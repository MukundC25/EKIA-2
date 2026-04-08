"""
App Services — Agent Service
Orchestrates the full LangGraph pipeline for a single debug request.
"""
from app.models.schemas import DebugRequest, DebugResponse
from app.services.graph_service import graph_service
from app.services.evaluation import TraceContext
from agent.langgraph_flow import agent_graph


class AgentService:
    """Orchestrates the full EKIA debug agent pipeline."""

    async def run(self, request: DebugRequest) -> DebugResponse:
        """
        Run the 5-node LangGraph pipeline asynchronously.
        Wraps execution in a Langfuse trace for observability.
        """
        trace_input = {
            "error": request.error,
            "language": request.language.value if request.language else "other",
            "has_context": bool(request.context),
            "has_code": bool(request.code_snippet),
        }

        with TraceContext(
            name="ekia_debug_agent",
            input_data=trace_input,
            metadata={"language": request.language.value if request.language else "other"},
        ) as trace:

            # Pre-fetch graph context (runs outside agent for speed)
            graph_results = []
            if graph_service.is_connected:
                try:
                    graph_results = graph_service.search_errors(request.error)
                    trace.log_span("graph_retrieval", request.error, graph_results)
                except Exception as e:
                    print(f"[AgentService] Graph retrieval failed: {e}")

            # Build initial agent state
            initial_state = {
                "raw_input": request.error,
                "language": request.language.value if request.language else "other",
                "context": request.context or "",
                "code_snippet": request.code_snippet or "",
                "parsed_query": {},
                "vector_results": [],
                "graph_results": graph_results,
                "vector_context_str": "",
                "graph_context_str": "",
                "reasoning_output": {},
                "final_response": {},
                "error": None,
                "trace_id": trace.trace_id,
            }

            # Run the LangGraph pipeline
            final_state = agent_graph.invoke(initial_state)
            result = final_state.get("final_response", {})

            # Score in Langfuse
            trace.score_response(result)

            # Build Pydantic response
            return DebugResponse(
                error=result.get("error", request.error),
                root_cause=result.get("root_cause", ""),
                beginner_explanation=result.get("beginner_explanation", ""),
                technical_explanation=result.get("technical_explanation", ""),
                fix=result.get("fix", ""),
                related_concepts=result.get("related_concepts", []),
                practice_problems=result.get("practice_problems", []),
                confidence_score=result.get("confidence_score", 0.5),
                sources=result.get("sources", []),
                graph_context=result.get("graph_context"),
                trace_id=result.get("trace_id"),
            )


# Singleton instance
agent_service = AgentService()
