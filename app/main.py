"""EKIA-2 FastAPI Application Entry Point"""
import os
import time
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

LLM_CHECK_TTL = 60
_llm_check = {"status": "unknown", "checked_at": 0.0, "detail": None}


async def check_llm(force: bool = False) -> dict:
    """Live check that the Groq API key is valid and the configured model is available (cached)."""
    from agent.langgraph_flow import LLM_MODEL

    if not force and time.time() - _llm_check["checked_at"] < LLM_CHECK_TTL:
        return _llm_check

    key = os.getenv("GROQ_API_KEY", "")
    if not key:
        _llm_check.update(status="not_configured", detail="GROQ_API_KEY is not set", checked_at=time.time())
        return _llm_check

    try:
        async with httpx.AsyncClient(timeout=8) as client:
            r = await client.get(
                f"https://api.groq.com/openai/v1/models/{LLM_MODEL}",
                headers={"Authorization": f"Bearer {key}"},
            )
        if r.status_code == 200:
            _llm_check.update(status="ready", detail=None)
        elif r.status_code in (401, 403):
            _llm_check.update(status="auth_failed", detail="Groq rejected the API key")
        elif r.status_code == 404:
            _llm_check.update(status="model_not_found", detail=f"Model {LLM_MODEL} not available on Groq")
        else:
            _llm_check.update(status="unreachable", detail=f"Groq returned HTTP {r.status_code}")
    except Exception as e:
        _llm_check.update(status="unreachable", detail=str(e))
    _llm_check["checked_at"] = time.time()
    return _llm_check


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize all services on startup."""
    print("\n" + "=" * 60)
    print("  EKIA-2 — AI Debugging Assistant")
    print("=" * 60)

    from app.database import engine, Base
    import app.models.history  # noqa: F401  (registers the table)
    Base.metadata.create_all(bind=engine)

    from app.services.rag_service import rag_service
    rag_service.initialize()

    from app.services.graph_service import graph_service
    graph_service.connect()

    from app.services.evaluation import langfuse_status
    print(f"[Langfuse] Status: {langfuse_status()}")

    llm = await check_llm(force=True)
    print(f"[LLM] Groq status: {llm['status']}" + (f" — {llm['detail']}" if llm["detail"] else ""))

    print("=" * 60)
    print("  EKIA-2 ready. API docs at /docs")
    print("=" * 60 + "\n")

    yield

    from app.services.evaluation import flush
    flush()
    graph_service.close()
    print("[App] Shutdown complete.")


app = FastAPI(
    title="EKIA-2 AI Debugging Assistant",
    description=(
        "An intelligent debugging assistant powered by a LangGraph agent, a Groq-hosted LLM, "
        "FAISS vector search over MiniLM embeddings, and Neo4j GraphRAG. Analyzes errors and "
        "provides structured root-cause analysis, fixes, and learning resources."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

cors_origins = os.getenv(
    "CORS_ORIGINS", "http://localhost:5173,http://localhost:3000"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in cors_origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.routes.debug import router as debug_router  # noqa: E402
from app.routes.graph import router as graph_router  # noqa: E402

app.include_router(debug_router)
app.include_router(graph_router)


@app.get("/health", tags=["health"])
async def health_check():
    """Live status of every component — nothing here is hardcoded."""
    from app.services.rag_service import rag_service
    from app.services.graph_service import graph_service
    from app.services.evaluation import langfuse_status, dashboard_url
    from agent.langgraph_flow import LLM_MODEL
    from rag.embeddings import MODEL_NAME as EMBEDDING_MODEL

    llm = await check_llm()
    graph_connected = graph_service.is_connected

    return {
        "status": "healthy",
        "version": "1.0.0",
        "services": {
            "rag": "ready" if rag_service.is_ready else "initializing",
            "graph": "connected" if graph_connected else "disconnected",
            "llm": llm["status"],
            "langfuse": langfuse_status(),
        },
        "details": {
            "llm_model": LLM_MODEL,
            "llm_provider": "Groq",
            "llm_error": llm["detail"],
            "embedding_model": EMBEDDING_MODEL.split("/")[-1],
            "vector_store": "FAISS (IndexFlatL2)",
            "knowledge_documents": rag_service.document_count,
            "neo4j_uri": graph_service.uri,
            "neo4j_error": None if graph_connected else graph_service.last_error,
            "langfuse_url": dashboard_url(),
        },
    }


STATIC_DIR = os.getenv("STATIC_DIR")

if STATIC_DIR and os.path.isdir(STATIC_DIR):
    # Single-container mode (Hugging Face Spaces): FastAPI also serves the built React app.
    from fastapi import HTTPException
    from fastapi.responses import FileResponse

    _static_root = os.path.realpath(STATIC_DIR)

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_frontend(full_path: str):
        if full_path.startswith(("api/", "docs", "redoc", "openapi.json")):
            raise HTTPException(status_code=404)
        candidate = os.path.realpath(os.path.join(_static_root, full_path))
        if full_path and candidate.startswith(_static_root + os.sep) and os.path.isfile(candidate):
            return FileResponse(candidate)
        return FileResponse(os.path.join(_static_root, "index.html"))  # SPA routes: /graph, /history
else:
    @app.get("/", tags=["root"])
    async def root():
        return {
            "message": "Welcome to EKIA-2 — AI Debugging Assistant",
            "docs": "/docs",
            "health": "/health",
            "debug": "POST /api/debug",
            "graph": "GET /api/graph",
        }
