"""Small local-only client for Ollama's embeddings endpoint."""

import os
from urllib.parse import urlsplit

import httpx

DEFAULT_BASE_URL = "http://127.0.0.1:11434"
DEFAULT_EMBEDDING_MODEL = "nomic-embed-text"
ALLOWED_HOSTS = {"localhost", "127.0.0.1", "::1"}


class OllamaUnavailable(RuntimeError):
    """Raised when the configured local Ollama service cannot embed text."""


def embed_texts(texts: list[str], client: httpx.Client | None = None) -> list[list[float]]:
    """Request vectors from a loopback Ollama server without using proxies."""
    if not texts:
        return []

    base_url = os.getenv("OLLAMA_BASE_URL", DEFAULT_BASE_URL).rstrip("/")
    parsed_url = urlsplit(base_url)
    if parsed_url.scheme != "http" or parsed_url.hostname not in ALLOWED_HOSTS:
        raise OllamaUnavailable("Ollama must use a local HTTP address.")

    model = os.getenv("EMBEDDING_MODEL", DEFAULT_EMBEDDING_MODEL)
    owns_client = client is None
    session = client or httpx.Client(timeout=60.0, trust_env=False)

    try:
        response = session.post(
            f"{base_url}/api/embed",
            json={"model": model, "input": texts},
        )
        response.raise_for_status()
        vectors = response.json().get("embeddings")
    except (httpx.HTTPError, ValueError, TypeError) as error:
        raise OllamaUnavailable("The local Ollama embedding request failed.") from error
    finally:
        if owns_client:
            session.close()

    if not isinstance(vectors, list) or len(vectors) != len(texts):
        raise OllamaUnavailable("Ollama returned an unexpected number of embeddings.")

    validated_vectors: list[list[float]] = []
    dimensions: int | None = None
    for vector in vectors:
        if not isinstance(vector, list) or not vector:
            raise OllamaUnavailable("Ollama returned an invalid embedding.")
        if any(not isinstance(value, (float, int)) for value in vector):
            raise OllamaUnavailable("Ollama returned an invalid embedding.")
        if dimensions is not None and len(vector) != dimensions:
            raise OllamaUnavailable("Ollama returned embeddings with inconsistent sizes.")
        dimensions = len(vector)
        validated_vectors.append([float(value) for value in vector])

    return validated_vectors
