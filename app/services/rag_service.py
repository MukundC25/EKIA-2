"""
App Services — RAG Service
Manages vector store lifecycle and provides retrieval interface.
"""
from rag.vector_store import build_vector_store, load_vector_store
from rag.retriever import retrieve_vector_context, format_vector_context, invalidate_cache
from langchain_community.vectorstores import FAISS
from typing import Optional


class RAGService:
    """Service layer wrapping FAISS vector store operations."""

    def __init__(self):
        self._vectorstore: Optional[FAISS] = None

    def initialize(self):
        """Load or build the FAISS index on startup."""
        print("[RAGService] Initializing vector store...")
        self._vectorstore = load_vector_store()
        print("[RAGService] Vector store ready.")

    def rebuild_index(self):
        """Force-rebuild the FAISS index (e.g., after adding new errors)."""
        print("[RAGService] Rebuilding FAISS index...")
        self._vectorstore = build_vector_store()
        invalidate_cache()
        print("[RAGService] Rebuild complete.")

    def retrieve(self, query: str, k: int = 5) -> tuple[list[dict], str]:
        """
        Retrieve relevant documents for the given query.
        Returns (results_list, formatted_context_string)
        """
        results = retrieve_vector_context(query, k=k)
        context_str = format_vector_context(results)
        return results, context_str

    @property
    def is_ready(self) -> bool:
        return self._vectorstore is not None


# Singleton instance
rag_service = RAGService()
