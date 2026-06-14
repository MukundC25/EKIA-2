"""FAISS Vector Store — Build, persist, and load the index from the error knowledge base."""
import os
import json
from pathlib import Path
from typing import Optional

from langchain_community.vectorstores import FAISS
from langchain.schema import Document

from rag.embeddings import get_embeddings

FAISS_INDEX_PATH = os.getenv("FAISS_INDEX_PATH", "data/faiss_index")
KNOWLEDGE_BASE_PATH = os.getenv(
    "KNOWLEDGE_BASE_PATH", "data/error_knowledge_base/errors.json"
)


def _load_knowledge_base_as_documents() -> list[Document]:
    """Convert error knowledge base JSON into LangChain Documents for embedding."""
    kb_path = Path(KNOWLEDGE_BASE_PATH)
    if not kb_path.exists():
        raise FileNotFoundError(f"Knowledge base not found at {kb_path}")

    with open(kb_path, "r") as f:
        errors = json.load(f)

    documents = []
    for error in errors:
        content = (
            f"Error: {error['error_type']}\n"
            f"Language: {error['language']}\n"
            f"Concept: {error['concept']}\n"
            f"Description: {error['description']}\n"
            f"Common Causes: {', '.join(error.get('common_causes', []))}\n"
            f"Fix: {error['fix']}\n"
            f"Code Example: {error.get('code_example', '')}\n"
            f"Fix Code: {error.get('fix_code', '')}\n"
            f"Related Concepts: {', '.join(error.get('related_concepts', []))}\n"
            f"Tags: {', '.join(error.get('tags', []))}"
        )
        documents.append(
            Document(
                page_content=content,
                metadata={
                    "id": error["id"],
                    "error_type": error["error_type"],
                    "language": error["language"],
                    "concept": error["concept"],
                    "practice_problems": ", ".join(error.get("practice_problems", [])),
                    "related_concepts": ", ".join(error.get("related_concepts", [])),
                    "fix": error["fix"],
                    "fix_code": error.get("fix_code", ""),
                    "tags": ", ".join(error.get("tags", [])),
                },
            )
        )

    print(f"[VectorStore] Loaded {len(documents)} documents from knowledge base")
    return documents


def build_vector_store() -> FAISS:
    """Build FAISS index from scratch and persist to disk."""
    documents = _load_knowledge_base_as_documents()
    embeddings = get_embeddings()

    print("[VectorStore] Building FAISS index...")
    vectorstore = FAISS.from_documents(documents, embeddings)

    Path(FAISS_INDEX_PATH).mkdir(parents=True, exist_ok=True)
    vectorstore.save_local(FAISS_INDEX_PATH)
    print(f"[VectorStore] Index saved to {FAISS_INDEX_PATH}")

    return vectorstore


def load_vector_store() -> Optional[FAISS]:
    """Load existing FAISS index from disk, or build a new one if missing."""
    embeddings = get_embeddings()
    index_path = Path(FAISS_INDEX_PATH)

    if index_path.exists() and any(index_path.iterdir()):
        print(f"[VectorStore] Loading existing FAISS index from {FAISS_INDEX_PATH}")
        return FAISS.load_local(
            FAISS_INDEX_PATH,
            embeddings,
            allow_dangerous_deserialization=True,
        )

    print("[VectorStore] No existing index found — building from scratch")
    return build_vector_store()
