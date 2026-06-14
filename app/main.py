"""EKIA-2 FastAPI Application Entry Point"""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize all services on startup."""
    print("\n" + "=" * 60)
    print("  EKIA-2 — AI Debugging Assistant")
    print("=" * 60)

    from app.services.rag_service import rag_service
    rag_service.initialize()

    from app.services.graph_service import graph_service
    graph_service.connect()

    print("=" * 60)
    print("  EKIA-2 ready. API docs: http://localhost:8000/docs")
    print("=" * 60 + "\n")

    yield

    graph_service.close()
    print("[App] Shutdown complete.")


app = FastAPI(
    title="EKIA-2 AI Debugging Assistant",
    description=(
        "An intelligent debugging assistant powered by LangGraph, Ollama/Llama3, "
        "FAISS vector search, and Neo4j GraphRAG. Analyzes errors and provides "
        "structured root-cause analysis, fixes, and learning resources."
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

from app.routes.debug import router as debug_router
from app.routes.graph import router as graph_router

app.include_router(debug_router)
app.include_router(graph_router)


@app.get("/health", tags=["health"])
async def health_check():
    from app.services.rag_service import rag_service
    from app.services.graph_service import graph_service

    return {
        "status": "healthy",
        "version": "1.0.0",
        "services": {
            "rag": "ready" if rag_service.is_ready else "initializing",
            "graph": "connected" if graph_service.is_connected else "disconnected",
            "llm": "ollama (local)",
            "embeddings": "HuggingFace all-MiniLM-L6-v2",
        },
    }


@app.get("/", tags=["root"])
async def root():
    return {
        "message": "Welcome to EKIA-2 — AI Debugging Assistant",
        "docs": "/docs",
        "health": "/health",
        "debug": "POST /api/debug",
        "graph": "GET /api/graph",
    }
