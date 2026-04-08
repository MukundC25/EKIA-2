"""
Tests — RAG Layer
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from rag.embeddings import get_embeddings
from rag.vector_store import load_vector_store
from rag.retriever import retrieve_vector_context, format_vector_context


def test_embeddings_load():
    """HuggingFace embeddings model should load successfully."""
    embeddings = get_embeddings()
    assert embeddings is not None


def test_embeddings_encode():
    """Embedding model should produce valid vectors."""
    embeddings = get_embeddings()
    result = embeddings.embed_query("NullPointerException in Java")
    assert isinstance(result, list)
    assert len(result) == 384  # all-MiniLM-L6-v2 produces 384-d vectors
    assert all(isinstance(v, float) for v in result)


def test_vector_store_loads():
    """Vector store should load or build from knowledge base."""
    vs = load_vector_store()
    assert vs is not None


def test_vector_retrieval_returns_results():
    """Retriever should return results for a common error query."""
    results = retrieve_vector_context("NullPointerException Java", k=3)
    assert isinstance(results, list)
    assert len(results) > 0

    first = results[0]
    assert "content" in first
    assert "metadata" in first
    assert "similarity_score" in first


def test_vector_retrieval_python_error():
    """Retriever should find Python KeyError in knowledge base."""
    results = retrieve_vector_context("Python dictionary KeyError", k=3)
    assert len(results) > 0
    contents = " ".join(r["content"] for r in results)
    assert "Python" in contents or "KeyError" in contents


def test_format_context():
    """Context formatter should produce a non-empty string."""
    results = retrieve_vector_context("StackOverflowError recursion", k=2)
    formatted = format_vector_context(results)
    assert isinstance(formatted, str)
    assert len(formatted) > 10
    assert "Source" in formatted
