"""Graph endpoints — Knowledge graph visualization and search (live Neo4j data only)."""
from fastapi import APIRouter, Query, HTTPException
from app.services.graph_service import graph_service

router = APIRouter(prefix="/api/graph", tags=["graph"])


def _offline_detail() -> dict:
    return {
        "message": f"Neo4j is not reachable at {graph_service.uri}.",
        "error": graph_service.last_error,
        "hint": "Start the Neo4j database, then load the knowledge base with: "
                "docker compose exec backend python -m graph.ingest_graph",
    }


@router.get("/", summary="Get full knowledge graph for visualization")
async def get_full_graph(limit: int = Query(default=100, ge=10, le=500)):
    """Returns all nodes and edges for the force-directed graph visualization."""
    if not graph_service.is_connected:
        return {"nodes": [], "edges": [], "connected": False, **_offline_detail()}

    data = graph_service.get_full_graph(limit=limit)
    return {**data, "connected": True}


@router.get("/search", summary="Search graph for a specific error")
async def search_graph(
    error: str = Query(..., description="Error name to search for", min_length=2),
    depth: int = Query(default=2, ge=1, le=5),
):
    """Search the knowledge graph for an error and return its neighborhood."""
    if not graph_service.is_connected:
        raise HTTPException(status_code=503, detail=_offline_detail())

    results = graph_service.search_errors(error, depth=depth)
    return {"results": results, "count": len(results), "query": error}


@router.get("/stats", summary="Graph database statistics")
async def get_graph_stats():
    """Returns node and relationship counts for the knowledge graph."""
    return graph_service.get_stats()
