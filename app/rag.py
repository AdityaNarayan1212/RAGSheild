"""Chunk local source documents and retrieve them with role-aware vector search."""

import hashlib
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import TypedDict

from app.config import Role
from app.documents import DOCUMENT_ROOT
from app.ollama import embed_texts
from app.vector_store import collection_for_configured_path

MAX_CHUNK_CHARACTERS = 800
CHUNK_OVERLAP_CHARACTERS = 100
EMBEDDING_BATCH_SIZE = 32
_index_lock = threading.Lock()


@dataclass(frozen=True)
class SourceDocument:
    title: str
    source: str
    access_level: Role
    content: str


class SemanticResult(TypedDict):
    title: str
    source: str
    access_level: Role
    snippet: str
    distance: float


def load_indexable_documents() -> list[SourceDocument]:
    """Load only the employee and HR source folders; security tests stay separate."""
    documents: list[SourceDocument] = []
    for category in ("employee", "hr"):
        category_path = DOCUMENT_ROOT / category
        if not category_path.is_dir():
            continue
        for path in sorted(category_path.glob("*.md")):
            content = path.read_text(encoding="utf-8")
            title = next(
                (line[2:].strip() for line in content.splitlines() if line.startswith("# ")),
                path.stem.replace("-", " ").title(),
            )
            documents.append(
                SourceDocument(
                    title=title,
                    source=path.name,
                    access_level=category,
                    content=content,
                )
            )
    return documents


def chunk_text(text: str) -> list[str]:
    """Split text into overlapping, bounded chunks without losing word boundaries."""
    normalized = " ".join(text.split())
    if not normalized:
        return []

    chunks: list[str] = []
    start = 0
    while start < len(normalized):
        end = min(start + MAX_CHUNK_CHARACTERS, len(normalized))
        if end < len(normalized):
            boundary = normalized.rfind(" ", start + MAX_CHUNK_CHARACTERS // 2, end)
            if boundary > start:
                end = boundary
        chunk = normalized[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= len(normalized):
            break
        start = max(start + 1, end - CHUNK_OVERLAP_CHARACTERS)
    return chunks


def _document_chunks() -> list[tuple[SourceDocument, int, str]]:
    result: list[tuple[SourceDocument, int, str]] = []
    for document in load_indexable_documents():
        for index, chunk in enumerate(chunk_text(document.content)):
            result.append((document, index, chunk))
    return result


def rebuild_index() -> dict[str, int]:
    """Embed allowed local sources, then replace the dedicated Chroma collection."""
    with _index_lock:
        chunks = _document_chunks()
        embeddings: list[list[float]] = []
        for batch_start in range(0, len(chunks), EMBEDDING_BATCH_SIZE):
            batch = chunks[batch_start : batch_start + EMBEDDING_BATCH_SIZE]
            embeddings.extend(embed_texts([chunk for _, _, chunk in batch]))

        collection = collection_for_configured_path()
        existing = collection.get(include=["metadatas"])
        if existing["ids"]:
            collection.delete(ids=existing["ids"])

        if chunks:
            ids = [
                hashlib.sha256(
                    f"{document.access_level}:{document.source}:{index}".encode("utf-8")
                ).hexdigest()
                for document, index, _ in chunks
            ]
            collection.upsert(
                ids=ids,
                embeddings=embeddings,
                documents=[chunk for _, _, chunk in chunks],
                metadatas=[
                    {
                        "title": document.title,
                        "source": document.source,
                        "access_level": document.access_level,
                        "chunk_index": index,
                    }
                    for document, index, _ in chunks
                ],
            )

        return {
            "document_count": len(
                {(document.access_level, document.source) for document, _, _ in chunks}
            ),
            "chunk_count": len(chunks),
        }


def semantic_search(query: str, role: Role, limit: int) -> list[SemanticResult]:
    """Filter by authorized source category inside Chroma before returning matches."""
    query_embedding = embed_texts([query])[0]
    allowed_levels = ["employee"] if role == "employee" else ["employee", "hr"]
    result = collection_for_configured_path().query(
        query_embeddings=[query_embedding],
        n_results=limit,
        where={"access_level": {"$in": allowed_levels}},
        include=["documents", "metadatas", "distances"],
    )

    documents = result["documents"][0]
    metadatas = result["metadatas"][0]
    distances = result["distances"][0]
    matches: list[SemanticResult] = []
    for document, metadata, distance in zip(documents, metadatas, distances):
        level = metadata.get("access_level")
        if level not in allowed_levels:
            continue
        matches.append(
            {
                "title": str(metadata.get("title", "Document")),
                "source": Path(str(metadata.get("source", "unknown"))).name,
                "access_level": level,
                "snippet": str(document)[:320],
                "distance": float(distance),
            }
        )
    return matches
