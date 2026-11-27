"""RAG Retriever — FAISS semantic search interface."""
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
    """Perform semantic similarity search on FAISS index."""
    vs = get_vectorstore()
    results = vs.similarity_search_with_score(query, k=k)

    # FAISS IndexFlatL2 returns the squared L2 distance. Embeddings are unit-normalized,
    # so ||q - d||^2 = 2 - 2·cos(q, d)  →  cosine similarity = 1 - distance / 2.
    retrieval_results = []
    for doc, score in results:
        distance = float(score)
        retrieval_results.append({
            "content": doc.page_content,
            "metadata": doc.metadata,
            "similarity_score": round(1.0 - distance / 2.0, 4),
            "l2_distance": round(distance, 4),
        })

    return retrieval_results


def format_vector_context(results: list[dict]) -> str:
    """Format retrieval results into a readable context block for the LLM prompt."""
    if not results:
        return "No relevant documents found in knowledge base."

    parts = []
    for i, result in enumerate(results, 1):
        parts.append(
            f"--- Source {i} (Cosine similarity: {result['similarity_score']:.3f}) ---\n"
            f"{result['content']}\n"
        )

    return "\n".join(parts)


def invalidate_cache():
    """Force reload the vector store after rebuilding the index."""
    global _vectorstore
    _vectorstore = None
