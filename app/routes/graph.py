"""Graph endpoints — Knowledge graph visualization and search."""
from fastapi import APIRouter, Query, HTTPException
from app.services.graph_service import graph_service
from app.models.schemas import GraphQueryResponse, GraphNode, GraphEdge

router = APIRouter(prefix="/api/graph", tags=["graph"])


@router.get("/", summary="Get full knowledge graph for visualization")
async def get_full_graph(limit: int = Query(default=100, ge=10, le=500)):
    """Returns all nodes and edges for the force-directed graph visualization."""
    if not graph_service.is_connected:
        return {
            "nodes": _get_demo_nodes(),
            "edges": _get_demo_edges(),
            "demo_mode": True,
            "message": "Neo4j not connected — showing demo data.",
        }

    data = graph_service.get_full_graph(limit=limit)
    return {**data, "demo_mode": False}


@router.get("/search", summary="Search graph for a specific error")
async def search_graph(
    error: str = Query(..., description="Error name to search for", min_length=2),
    depth: int = Query(default=2, ge=1, le=5),
):
    """Search the knowledge graph for an error and return its neighborhood."""
    if not graph_service.is_connected:
        raise HTTPException(
            status_code=503,
            detail="Neo4j is not connected. Start Neo4j Desktop and ensure credentials in .env are correct.",
        )

    results = graph_service.search_errors(error, depth=depth)
    return {"results": results, "count": len(results), "query": error}


@router.get("/stats", summary="Graph database statistics")
async def get_graph_stats():
    """Returns node and relationship counts for the knowledge graph."""
    return graph_service.get_stats()


def _get_demo_nodes():
    return [
        {"id": "e1", "label": "NullPointerException", "type": "Error", "properties": {"language": "Java"}},
        {"id": "e2", "label": "KeyError", "type": "Error", "properties": {"language": "Python"}},
        {"id": "e3", "label": "StackOverflowError", "type": "Error", "properties": {"language": "Java"}},
        {"id": "e4", "label": "TypeError", "type": "Error", "properties": {"language": "JavaScript"}},
        {"id": "c1", "label": "Null Reference", "type": "Concept", "properties": {}},
        {"id": "c2", "label": "Recursion", "type": "Concept", "properties": {}},
        {"id": "c3", "label": "Type Safety", "type": "Concept", "properties": {}},
        {"id": "c4", "label": "Dictionary Access", "type": "Concept", "properties": {}},
        {"id": "f1", "label": "Use Optional<T>", "type": "Fix", "properties": {}},
        {"id": "f2", "label": "Add base case", "type": "Fix", "properties": {}},
        {"id": "p1", "label": "LeetCode: Reverse Linked List", "type": "Problem", "properties": {}},
        {"id": "p2", "label": "LeetCode: Two Sum", "type": "Problem", "properties": {}},
        {"id": "l1", "label": "Java", "type": "Language", "properties": {}},
        {"id": "l2", "label": "Python", "type": "Language", "properties": {}},
        {"id": "l3", "label": "JavaScript", "type": "Language", "properties": {}},
    ]


def _get_demo_edges():
    return [
        {"source": "e1", "target": "c1", "relationship": "CAUSED_BY"},
        {"source": "e3", "target": "c2", "relationship": "CAUSED_BY"},
        {"source": "e2", "target": "c4", "relationship": "CAUSED_BY"},
        {"source": "e4", "target": "c3", "relationship": "CAUSED_BY"},
        {"source": "e1", "target": "f1", "relationship": "FIXED_BY"},
        {"source": "e3", "target": "f2", "relationship": "FIXED_BY"},
        {"source": "c1", "target": "p1", "relationship": "PRACTICED_BY"},
        {"source": "c4", "target": "p2", "relationship": "PRACTICED_BY"},
        {"source": "e1", "target": "l1", "relationship": "IN_LANGUAGE"},
        {"source": "e3", "target": "l1", "relationship": "IN_LANGUAGE"},
        {"source": "e2", "target": "l2", "relationship": "IN_LANGUAGE"},
        {"source": "e4", "target": "l3", "relationship": "IN_LANGUAGE"},
    ]
