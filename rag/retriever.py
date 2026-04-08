"""
RAG Layer — Hybrid Retriever
Combines FAISS semantic search + Neo4j graph context for comprehensive retrieval
"""
from typing import Optional
from langchain_community.vectorstores import FAISS
from rag.vector_store import load_vector_store


_vectorstore: Optional[FAISS] = None


def get_vectorstore() -> FAISS:
    """Lazy-load and cache the vector store."""
    global _vectorstore
    if _vectorstore is None:
        _vectorstore = load_vector_store()
    return _vectorstore


def retrieve_vector_context(query: str, k: int = 5) -> list[dict]:
    """
    Perform semantic similarity search on FAISS index.
    Returns top-k relevant error documents.
    """
    vs = get_vectorstore()
    results = vs.similarity_search_with_score(query, k=k)

    retrieval_results = []
    for doc, score in results:
        retrieval_results.append({
            "content": doc.page_content,
            "metadata": doc.metadata,
            "similarity_score": float(score),  # Lower = more similar in FAISS L2
        })

    return retrieval_results


def format_vector_context(results: list[dict]) -> str:
    """Format retrieval results into a readable context block for the LLM prompt."""
    if not results:
        return "No relevant documents found in knowledge base."

    parts = []
    for i, result in enumerate(results, 1):
        meta = result.get("metadata", {})
        parts.append(
            f"--- Source {i} (Similarity: {result['similarity_score']:.3f}) ---\n"
            f"{result['content']}\n"
        )

    return "\n".join(parts)


def invalidate_cache():
    """Force reload the vector store (e.g., after rebuilding the index)."""
    global _vectorstore
    _vectorstore = None
