"""Agent Service — Orchestrates the full LangGraph pipeline for a debug request."""
import asyncio
from app.models.schemas import DebugRequest, DebugResponse
from app.services.graph_service import graph_service
from app.services.evaluation import observation, score_response, trace_url
from agent.langgraph_flow import agent_graph, LLM_MODEL


class AgentService:
    """Orchestrates the full EKIA debug agent pipeline."""

    async def run(self, request: DebugRequest) -> DebugResponse:
        """Run the 5-node LangGraph pipeline inside one Langfuse trace."""
        language = request.language.value if request.language else "other"
        trace_input = {
            "error": request.error,
            "language": language,
            "context": request.context or "",
            "has_code": bool(request.code_snippet),
        }

        with observation(
            "ekia_debug_agent",
            as_type="agent",
            input=trace_input,
            metadata={"language": language, "llm": LLM_MODEL},
        ) as root:

            graph_results = []
            if graph_service.is_connected:
                with observation("graph_retrieval", as_type="retriever", input={"error": request.error}) as span:
                    try:
                        graph_results = await asyncio.to_thread(graph_service.search_errors, request.error)
                    except Exception as e:
                        print(f"[AgentService] Graph retrieval failed: {e}")
                        span.update(level="ERROR", status_message=str(e))
                    span.update(output={"matches": len(graph_results), "results": graph_results})

            initial_state = {
                "raw_input": request.error,
                "language": language,
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
                "trace_id": root.trace_id,
            }

            final_state = await asyncio.to_thread(agent_graph.invoke, initial_state)
            result = final_state.get("final_response", {})

            score_response(root, result)
            root.update(
                output={
                    "error": result.get("error"),
                    "root_cause": result.get("root_cause"),
                    "fix": result.get("fix"),
                    "confidence_score": result.get("confidence_score"),
                    "sources": result.get("sources"),
                }
            )

        if graph_service.is_connected:
            asyncio.create_task(
                asyncio.to_thread(
                    graph_service.ingest_debug_result,
                    error_name=result.get("error", request.error),
                    language=language,
                    root_cause=result.get("root_cause", ""),
                    fix=result.get("fix", ""),
                    related_concepts=result.get("related_concepts", []),
                )
            )

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
            trace_url=trace_url(result.get("trace_id")),
        )


agent_service = AgentService()
