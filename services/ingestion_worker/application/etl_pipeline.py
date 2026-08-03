"""RAG ingestion pipeline — ETL for knowledge base.

Extract → Transform → Chunk → Embed → Load (Chroma)
Run on demand + on schedule via Redis queue.
"""

from __future__ import annotations

import re
import uuid
from pathlib import Path
from typing import Any

try:
    # Availability probe only — the client itself comes from shared.infrastructure.chroma_client
    import chromadb  # noqa: F401

    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer

    ST_AVAILABLE = True
except ImportError:
    ST_AVAILABLE = False

from shared.infrastructure.chroma_client import get_or_create_collection
from shared.infrastructure.observability import log

# Trusted base path for KB ingestion — prevents path traversal via Redis job data_dir
KB_BASE_DIR = Path(__file__).resolve().parents[3] / "data" / "kb"

# --- Embedding model (loaded once) ---
_model = None


def _get_model():
    global _model
    if _model is None:
        if not ST_AVAILABLE:
            raise ImportError(
                "sentence-transformers not installed. "
                "Install with: pip install sentence-transformers"
            )
        _model = SentenceTransformer("BAAI/bge-m3")
    return _model


# --- Extract ---


def _resolve_kb_dir(data_dir: str) -> Path:
    """Resolve and validate KB directory stays within trusted base."""
    resolved = Path(data_dir).resolve()
    base = KB_BASE_DIR.resolve()
    if not str(resolved).startswith(str(base)):
        raise ValueError(f"data_dir must be within {base}")
    return resolved


def extract_kb_sources(data_dir: str = "data/kb") -> list[dict[str, Any]]:
    """Extract KB sources from markdown and CSV files."""
    sources = []
    kb_path = _resolve_kb_dir(data_dir)

    for file_path in kb_path.rglob("*"):
        if file_path.suffix == ".md":
            content = file_path.read_text(encoding="utf-8")
            sources.append(
                {
                    "source": str(file_path),
                    "content": content,
                    "type": "markdown",
                    "language": "pt/en",
                }
            )
        elif file_path.suffix == ".csv":
            content = file_path.read_text(encoding="utf-8")
            sources.append(
                {
                    "source": str(file_path),
                    "content": content,
                    "type": "csv",
                    "language": "pt/en",
                }
            )

    log.info("kb_extracted", sources=len(sources))
    return sources


# --- Transform + Chunk ---


def _chunk_markdown(content: str, source: str, chunk_size: int = 500) -> list[dict[str, Any]]:
    """Chunk markdown content by section headers."""
    chunks = []
    sections = re.split(r"\n(?=##\s)", content)

    for section in sections:
        if not section.strip():
            continue
        # Extract header
        header_match = re.match(r"##\s+(.+)", section)
        header = header_match.group(1).strip() if header_match else "General"

        # Chunk long sections
        if len(section) > chunk_size:
            paragraphs = section.split("\n\n")
            current_chunk = ""
            for para in paragraphs:
                if len(current_chunk) + len(para) > chunk_size and current_chunk:
                    chunks.append(
                        {
                            "id": str(uuid.uuid4()),
                            "content": current_chunk.strip(),
                            "metadata": {"source": source, "section": header, "type": "faq"},
                        }
                    )
                    current_chunk = para
                else:
                    current_chunk += "\n\n" + para if current_chunk else para
            if current_chunk.strip():
                chunks.append(
                    {
                        "id": str(uuid.uuid4()),
                        "content": current_chunk.strip(),
                        "metadata": {"source": source, "section": header, "type": "faq"},
                    }
                )
        else:
            chunks.append(
                {
                    "id": str(uuid.uuid4()),
                    "content": section.strip(),
                    "metadata": {"source": source, "section": header, "type": "faq"},
                }
            )

    return chunks


def _chunk_csv(content: str, source: str) -> list[dict[str, Any]]:
    """Chunk CSV content — each row becomes a document."""
    chunks = []
    lines = content.strip().split("\n")
    if len(lines) < 2:
        return chunks

    headers = [h.strip() for h in lines[0].split(",")]
    for line in lines[1:]:
        values = [v.strip() for v in line.split(",")]
        if len(values) == len(headers):
            doc = " | ".join(f"{h}: {v}" for h, v in zip(headers, values, strict=True))
            chunks.append(
                {
                    "id": str(uuid.uuid4()),
                    "content": doc,
                    "metadata": {"source": source, "type": "fee"},
                }
            )

    return chunks


def transform_and_chunk(sources: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Transform and chunk all KB sources."""
    all_chunks = []
    for src in sources:
        if src["type"] == "markdown":
            all_chunks.extend(_chunk_markdown(src["content"], src["source"]))
        elif src["type"] == "csv":
            all_chunks.extend(_chunk_csv(src["content"], src["source"]))

    log.info("kb_chunked", chunks=len(all_chunks))
    return all_chunks


# --- Embed + Load ---


def embed_and_load(chunks: list[dict[str, Any]]) -> int:
    """Embed chunks and upsert into Chroma."""
    if not chunks:
        return 0

    model = _get_model()
    collection = get_or_create_collection()

    # Batch embed
    contents = [c["content"] for c in chunks]
    embeddings = model.encode(contents, show_progress_bar=False).tolist()

    # Upsert into Chroma
    batch_size = 100
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i : i + batch_size]
        batch_embeddings = embeddings[i : i + batch_size]
        collection.upsert(
            ids=[c["id"] for c in batch],
            documents=[c["content"] for c in batch],
            embeddings=batch_embeddings,
            metadatas=[c["metadata"] for c in batch],
        )

    log.info("kb_loaded", chunks=len(chunks))
    return len(chunks)


# --- Main ETL entry point ---


def run_ingestion(data_dir: str = "data/kb") -> int:
    """Run the full ETL pipeline."""
    sources = extract_kb_sources(data_dir)
    chunks = transform_and_chunk(sources)
    count = embed_and_load(chunks)
    log.info("ingestion_complete", total_chunks=count)
    return count
