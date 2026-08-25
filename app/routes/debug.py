"""Debug endpoint — POST /api/debug"""
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import time
from datetime import datetime

from app.models.schemas import DebugRequest, DebugResponse
from app.services.agent_service import agent_service
from app.database import get_db
from app.models.history import DebugSession

router = APIRouter(prefix="/api", tags=["debug"])


@router.post("/debug", response_model=DebugResponse, summary="Debug an error using AI")
async def debug_error(request: DebugRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Analyze an error using the full EKIA agent pipeline."""
    start = time.time()

    try:
        response = await agent_service.run(request)
        elapsed = round(time.time() - start, 2)
        print(f"[API] /debug completed in {elapsed}s — confidence: {response.confidence_score:.2f}")
        
        # Save to database
        db_session = DebugSession(
            error=response.error,
            language=request.language.value if request.language else "unknown",
            confidence=response.confidence_score,
            trace_id=response.trace_id
        )
        db.add(db_session)
        db.commit()

        return response

    except Exception as e:
        err_msg = str(e)
        print(f"[API] /debug error: {err_msg}")
        raise HTTPException(
            status_code=500,
            detail={
                "message": "Agent pipeline failed",
                "error": err_msg,
                "hint": "Check your GROQ_API_KEY in the .env file and ensure you have internet access." if "groq" in err_msg.lower() or "connection" in err_msg.lower() or "401" in err_msg.lower() else "Check that your AI provider is reachable.",
            },
        )


@router.get("/debug/history", summary="Get recent debug sessions")
async def get_debug_history(db: Session = Depends(get_db)):
    """Returns debug session history."""
    sessions = db.query(DebugSession).order_by(DebugSession.timestamp.desc()).limit(20).all()
    
    session_list = []
    for s in sessions:
        # format timestamp to 'X minutes ago' or just use string
        diff = (datetime.utcnow() - s.timestamp).total_seconds()
        if diff < 60:
            ts_str = "Just now"
        elif diff < 3600:
            ts_str = f"{int(diff/60)} minutes ago"
        elif diff < 86400:
            ts_str = f"{int(diff/3600)} hours ago"
        else:
            ts_str = f"{int(diff/86400)} days ago"
            
        session_list.append({
            "id": s.id,
            "error": s.error,
            "language": s.language,
            "confidence": s.confidence,
            "trace_id": s.trace_id,
            "timestamp": ts_str
        })
        
    return JSONResponse(content={
        "sessions": session_list,
        "message": "Real history loaded from SQLite database."
    })
