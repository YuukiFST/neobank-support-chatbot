"""ChromaDB client wrapper."""

from __future__ import annotations

try:
    import chromadb

    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False

from shared.infrastructure.config import settings

chroma_client = None
KB_COLLECTION = "neobank_kb"


def _get_client():
    global chroma_client
    if chroma_client is None:
        if not CHROMA_AVAILABLE:
            raise ImportError("chromadb not installed. Install with: pip install chromadb")
        chroma_client = chromadb.HttpClient(host=settings.chroma_host, port=settings.chroma_port)
    return chroma_client


def get_or_create_collection():
    client = _get_client()
    return client.get_or_create_collection(
        name=KB_COLLECTION,
        metadata={"hnsw:space": "cosine"},
    )


def query_kb(query: str, n_results: int = 3) -> list[str]:
    """Query the knowledge base collection. Returns empty list if Chroma unavailable."""
    if not CHROMA_AVAILABLE:
        return []
    try:
        collection = get_or_create_collection()
        if collection.count() == 0:
            return []
        results = collection.query(
            query_texts=[query], n_results=min(n_results, collection.count())
        )
        return results.get("documents", [[]])[0]
    except Exception:
        return []
