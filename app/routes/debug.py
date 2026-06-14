"""Debug endpoint — POST /api/debug"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
import time

from app.models.schemas import DebugRequest, DebugResponse
from app.services.agent_service import agent_service

router = APIRouter(prefix="/api", tags=["debug"])


@router.post("/debug", response_model=DebugResponse, summary="Debug an error using AI")
async def debug_error(request: DebugRequest, background_tasks: BackgroundTasks):
    """Analyze an error using the full EKIA agent pipeline."""
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


@router.get("/debug/history", summary="Get recent debug sessions")
async def get_debug_history():
    """Returns debug session history."""
    return JSONResponse(content={
        "sessions": [],
        "message": "History persistence coming soon. Connect Langfuse for full trace history.",
    })
