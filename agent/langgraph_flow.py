"""LangGraph Agent Pipeline — 5-node StateGraph: parse → retrieve → reason → validate → respond"""
import json
import re
from typing import TypedDict, Optional, Any
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from langchain.schema import HumanMessage, SystemMessage

from agent.prompts import (
    SYSTEM_PROMPT,
    OUTPUT_FORMAT_PROMPT,
    QUERY_REWRITE_PROMPT,
    REASONING_PROMPT,
)
from rag.retriever import retrieve_vector_context, format_vector_context


class AgentState(TypedDict):
    raw_input: str
    language: str
    context: str
    code_snippet: str
    parsed_query: dict
    vector_results: list
    graph_results: list
    vector_context_str: str
    graph_context_str: str
    reasoning_output: dict
    final_response: dict
    error: Optional[str]
    trace_id: Optional[str]


def get_llm() -> ChatGroq:
    """Initialize the Groq LLM (Llama 3)."""
    return ChatGroq(
        model="openai/gpt-oss-20b",
        temperature=0.0
    )


def extract_json(text: str) -> dict:
    """Robustly extract JSON from LLM response text."""
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    json_match = re.search(r'\{.*\}', text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass

    return {
        "error": "Parse Error",
        "root_cause": text[:500] if text else "LLM returned non-JSON response",
        "beginner_explanation": "The AI response could not be parsed.",
        "technical_explanation": text[:1000] if text else "",
        "fix": "Please try again with more specific error information.",
        "related_concepts": [],
        "practice_problems": [],
        "confidence_score": 0.1,
    }


def parse_query_node(state: AgentState) -> AgentState:
    """Rewrite and structure the raw user query."""
    try:
        llm = get_llm()
        prompt = QUERY_REWRITE_PROMPT.format(raw_query=state["raw_input"])
        response = llm.invoke([HumanMessage(content=prompt)])
        parsed = extract_json(response.content)

        if state.get("language") and state["language"] != "other":
            parsed["language"] = state["language"]
        if state.get("context"):
            parsed["context"] = state["context"]

        state["parsed_query"] = parsed
        print(f"[Agent] Parsed query: {parsed.get('error_type')} ({parsed.get('language')})")
    except Exception as e:
        print(f"[Agent] parse_query error: {e}")
        state["parsed_query"] = {
            "error_type": state["raw_input"][:100],
            "language": state.get("language", "unknown"),
            "context": state.get("context", ""),
            "rewritten_query": state["raw_input"],
        }
    return state


def retrieve_node(state: AgentState) -> AgentState:
    """Retrieve relevant context from FAISS vector store and Neo4j graph."""
    parsed = state.get("parsed_query", {})
    search_query = parsed.get("rewritten_query", state["raw_input"])

    try:
        vector_results = retrieve_vector_context(search_query, k=5)
        state["vector_results"] = vector_results
        state["vector_context_str"] = format_vector_context(vector_results)
        print(f"[Agent] Retrieved {len(vector_results)} vector documents")
    except Exception as e:
        print(f"[Agent] Vector retrieval error: {e}")
        state["vector_results"] = []
        state["vector_context_str"] = "Vector retrieval unavailable."

    graph_results = state.get("graph_results", [])
    if graph_results:
        graph_str = json.dumps(graph_results, indent=2)
    else:
        graph_str = "No graph context available."
    state["graph_context_str"] = graph_str

    return state


def reason_node(state: AgentState) -> AgentState:
    """Call Groq/Llama3 to analyze the error using retrieved context."""
    parsed = state.get("parsed_query", {})

    prompt = REASONING_PROMPT.format(
        error=parsed.get("error_type", state["raw_input"]),
        language=parsed.get("language", "unknown"),
        context=parsed.get("context", state.get("context", "No additional context")),
        code_snippet=state.get("code_snippet", "No code snippet provided"),
        vector_context=state.get("vector_context_str", ""),
        graph_context=state.get("graph_context_str", ""),
        output_format=OUTPUT_FORMAT_PROMPT,
        system_rules=SYSTEM_PROMPT,
    )

    try:
        llm = get_llm()
        response = llm.invoke([HumanMessage(content=prompt)])
        reasoning = extract_json(response.content)
        state["reasoning_output"] = reasoning
        print(f"[Agent] Reasoning complete — confidence: {reasoning.get('confidence_score', '?')}")
    except Exception as e:
        print(f"[Agent] Reasoning error: {e}")
        state["reasoning_output"] = {
            "error": parsed.get("error_type", "Unknown Error"),
            "root_cause": f"Analysis failed: {str(e)}",
            "beginner_explanation": f"LLM error: {str(e)}",
            "technical_explanation": "Failed to connect to the LLM. Verify your GROQ_API_KEY.",
            "fix": "Please check your GROQ_API_KEY in the .env file.",
            "related_concepts": [],
            "practice_problems": [],
            "confidence_score": 0.0,
        }
    return state


def validate_node(state: AgentState) -> AgentState:
    """Validate and sanitize the reasoning output structure."""
    reasoning = state.get("reasoning_output", {})

    required_fields = {
        "error": state.get("parsed_query", {}).get("error_type", "Unknown"),
        "root_cause": "Unable to determine root cause.",
        "beginner_explanation": "Please provide more details.",
        "technical_explanation": "Insufficient context for technical analysis.",
        "fix": "Review documentation for this error type.",
        "related_concepts": [],
        "practice_problems": [],
        "confidence_score": 0.5,
    }

    validated = {**required_fields, **reasoning}
    validated["confidence_score"] = max(0.0, min(1.0, float(validated.get("confidence_score", 0.5))))

    if not isinstance(validated["related_concepts"], list):
        validated["related_concepts"] = []
    if not isinstance(validated["practice_problems"], list):
        validated["practice_problems"] = []

    sources = []
    for result in state.get("vector_results", [])[:3]:
        meta = result.get("metadata", {})
        if meta.get("error_type"):
            sources.append(f"{meta['error_type']} ({meta.get('language', '?')})")
    validated["sources"] = sources

    state["reasoning_output"] = validated
    print("[Agent] Validation passed.")
    return state


def respond_node(state: AgentState) -> AgentState:
    """Package the final response."""
    reasoning = state.get("reasoning_output", {})
    state["final_response"] = {
        **reasoning,
        "trace_id": state.get("trace_id"),
        "graph_context": state.get("graph_results") if state.get("graph_results") else None,
    }
    print(f"[Agent] Final response ready for: {reasoning.get('error', '?')}")
    return state


def build_agent_graph():
    """Build and compile the LangGraph StateGraph."""
    workflow = StateGraph(AgentState)

    workflow.add_node("parse_query", parse_query_node)
    workflow.add_node("retrieve", retrieve_node)
    workflow.add_node("reason", reason_node)
    workflow.add_node("validate", validate_node)
    workflow.add_node("respond", respond_node)

    workflow.set_entry_point("parse_query")
    workflow.add_edge("parse_query", "retrieve")
    workflow.add_edge("retrieve", "reason")
    workflow.add_edge("reason", "validate")
    workflow.add_edge("validate", "respond")
    workflow.add_edge("respond", END)

    return workflow.compile()


agent_graph = build_agent_graph()
