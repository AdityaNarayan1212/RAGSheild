import httpx

from app.ollama import OllamaUnavailable, embed_texts
from app.rag import chunk_text


def test_embedding_client_sends_batch_to_local_ollama(monkeypatch) -> None:
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
    captured = {}

    def handle(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        captured["body"] = request.read()
        return httpx.Response(200, json={"embeddings": [[0.1, 0.2], [0.3, 0.4]]})

    client = httpx.Client(transport=httpx.MockTransport(handle))
    try:
        result = embed_texts(["first", "second"], client)
    finally:
        client.close()

    assert captured["url"] == "http://127.0.0.1:11434/api/embed"
    assert b'"model":"nomic-embed-text"' in captured["body"]
    assert result == [[0.1, 0.2], [0.3, 0.4]]


def test_embedding_client_rejects_nonlocal_runtime(monkeypatch) -> None:
    monkeypatch.setenv("OLLAMA_BASE_URL", "https://example.com")

    try:
        embed_texts(["text"])
    except OllamaUnavailable as error:
        assert "local HTTP" in str(error)
    else:
        raise AssertionError("A non-local Ollama URL should be rejected.")


def test_chunk_text_respects_size_and_overlap() -> None:
    text = "word " * 260

    chunks = chunk_text(text)

    assert len(chunks) > 1
    assert all(len(chunk) <= 800 for chunk in chunks)
    assert set(chunks[0].split()) & set(chunks[1].split())
