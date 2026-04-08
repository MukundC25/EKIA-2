"""
FastAPI Routes — Debug endpoint
POST /api/debug — Main debug pipeline entry point
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
import time

from app.models.schemas import DebugRequest, DebugResponse
from app.services.agent_service import agent_service

router = APIRouter(prefix="/api", tags=["debug"])


@router.post("/debug", response_model=DebugResponse, summary="Debug an error using AI")
async def debug_error(request: DebugRequest, background_tasks: BackgroundTasks):
    """
    Analyze an error using the full EKIA pipeline:
    - Query parsing & language detection
    - FAISS semantic retrieval
    - Neo4j GraphRAG context
    - Llama3 reasoning via Ollama
    - Response validation
    - Langfuse tracing & scoring

    Returns a structured JSON with root cause, fix, concepts, and practice problems.
    """
    start = time.time()

    try:
        response = await agent_service.run(request)
        elapsed = round(time.time() - start, 2)
        print(f"[API] /debug completed in {elapsed}s — confidence: {response.confidence_score:.2f}")
        return response

    except Exception as e:
        print(f"[API] /debug error: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "message": "Agent pipeline failed",
                "error": str(e),
                "hint": "Check that Ollama is running: `ollama serve` and `ollama pull llama3`",
            },
        )


@router.get("/debug/history", summary="Get recent debug sessions (placeholder)")
async def get_debug_history():
    """Returns mock history — integrate with a real DB for production."""
    return JSONResponse(content={
        "sessions": [],
        "message": "History persistence coming soon. Connect Langfuse for full trace history.",
    })
