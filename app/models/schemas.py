"""
EKIA-2 Pydantic Schemas — Request/Response models for all API endpoints
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Any
from enum import Enum


class SupportedLanguage(str, Enum):
    java = "java"
    python = "python"
    javascript = "javascript"
    typescript = "typescript"
    react = "react"
    cpp = "c++"
    c = "c"
    sql = "sql"
    docker = "docker"
    kubernetes = "kubernetes"
    go = "go"
    rust = "rust"
    other = "other"


# ---------------------------------------------------------------------------
# Debug Request / Response
# ---------------------------------------------------------------------------

class DebugRequest(BaseModel):
    error: str = Field(
        ...,
        description="The error message or type (e.g. NullPointerException, KeyError)",
        min_length=2,
        max_length=2000,
        examples=["NullPointerException at UserService.java:42"]
    )
    language: Optional[SupportedLanguage] = Field(
        default=SupportedLanguage.other,
        description="Programming language of the error"
    )
    context: Optional[str] = Field(
        default=None,
        description="Additional context, stack trace, or description of what you were doing",
        max_length=5000
    )
    code_snippet: Optional[str] = Field(
        default=None,
        description="Relevant code snippet where the error occurred",
        max_length=5000
    )

    class Config:
        json_schema_extra = {
            "example": {
                "error": "NullPointerException",
                "language": "java",
                "context": "Calling getUserById() in a REST controller — the user might not exist in DB",
                "code_snippet": "User user = userRepo.findById(id);\nSystem.out.println(user.getName());"
            }
        }


class DebugResponse(BaseModel):
    error: str = Field(description="Original error message")
    root_cause: str = Field(description="Technical root cause of the error")
    beginner_explanation: str = Field(description="Simple, beginner-friendly explanation")
    technical_explanation: str = Field(description="In-depth technical analysis")
    fix: str = Field(description="Concrete fix with code example")
    related_concepts: List[str] = Field(default=[], description="Related programming concepts to learn")
    practice_problems: List[str] = Field(default=[], description="Practice problems to reinforce understanding")
    confidence_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Model's confidence in the answer (0.0 to 1.0)"
    )
    sources: List[str] = Field(default=[], description="Knowledge base sources used")
    graph_context: Optional[List[dict]] = Field(default=None, description="Related graph relationships found")
    trace_id: Optional[str] = Field(default=None, description="Langfuse trace ID for observability")
    trace_url: Optional[str] = Field(default=None, description="Link to this trace in the Langfuse UI")


# ---------------------------------------------------------------------------
# Graph Query
# ---------------------------------------------------------------------------

class GraphQueryRequest(BaseModel):
    error_name: Optional[str] = Field(default=None)
    language: Optional[str] = Field(default=None)
    concept: Optional[str] = Field(default=None)
    depth: int = Field(default=2, ge=1, le=5, description="Graph traversal depth")


class GraphNode(BaseModel):
    id: str
    label: str
    type: str  # Error, Concept, Fix, Problem
    properties: dict = {}


class GraphEdge(BaseModel):
    source: str
    target: str
    relationship: str


class GraphQueryResponse(BaseModel):
    nodes: List[GraphNode] = []
    edges: List[GraphEdge] = []
    query: str
    total_nodes: int = 0
    total_edges: int = 0


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

class HealthResponse(BaseModel):
    status: str
    version: str
    services: dict


# ---------------------------------------------------------------------------
# Internal Agent State (used within LangGraph)
# ---------------------------------------------------------------------------

class ParsedQuery(BaseModel):
    error_type: str
    language: str
    context: str
    code_snippet: Optional[str] = None
    rewritten_query: str


class ReasoningOutput(BaseModel):
    error: str
    root_cause: str
    beginner_explanation: str
    technical_explanation: str
    fix: str
    related_concepts: List[str] = []
    practice_problems: List[str] = []
    confidence_score: float = 0.0
