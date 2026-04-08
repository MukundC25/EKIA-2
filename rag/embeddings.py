"""
RAG Layer — Embedding model factory
Uses HuggingFace sentence-transformers (all-MiniLM-L6-v2) — fully local, no API key needed
"""
import os
from functools import lru_cache
from langchain_huggingface import HuggingFaceEmbeddings


MODEL_NAME = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")


@lru_cache(maxsize=1)
def get_embeddings() -> HuggingFaceEmbeddings:
    """
    Returns a cached singleton HuggingFaceEmbeddings instance.
    First call downloads/loads the model; subsequent calls are instant.
    """
    print(f"[Embeddings] Loading model: {MODEL_NAME}")
    return HuggingFaceEmbeddings(
        model_name=MODEL_NAME,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )
