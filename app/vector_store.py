"""Persistent, local-only Chroma collection for precomputed vectors."""

import os
from functools import lru_cache
from pathlib import Path
from typing import Any

import chromadb
from chromadb.config import Settings

from app.config import PROJECT_ROOT

COLLECTION_NAME = "ragshield_documents"
DEFAULT_PATH = PROJECT_ROOT / "data" / "chroma"


def get_store_path() -> Path:
    configured_path = Path(os.getenv("CHROMA_PERSIST_DIRECTORY", str(DEFAULT_PATH)))
    if not configured_path.is_absolute():
        configured_path = PROJECT_ROOT / configured_path
    return configured_path.resolve()


@lru_cache(maxsize=4)
def get_collection(persist_path: str) -> Any:
    """Return a persistent collection with telemetry disabled."""
    client = chromadb.PersistentClient(
        path=persist_path,
        settings=Settings(anonymized_telemetry=False),
    )
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
        embedding_function=None,
    )


def collection_for_configured_path() -> Any:
    return get_collection(str(get_store_path()))
