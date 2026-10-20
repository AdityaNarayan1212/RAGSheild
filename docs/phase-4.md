# Phase 4: Local Semantic Retrieval

Phase 4 connects source documents to a local embedding runtime and a persistent vector index. The API calls Ollama's local `/api/embed` endpoint and stores the returned vectors in a local Chroma `PersistentClient` collection. It does not call a cloud inference service or download a model.

## Workflow

1. An HR role calls `POST /documents/index`.
2. The server reads Markdown files from only the employee and HR source folders, splits text into overlapping chunks, and requests embeddings from local Ollama.
3. Chroma persists chunks, vectors, and access-level metadata under `data/chroma`.
4. An authenticated user calls `GET /documents/semantic-search?q=...`.
5. The query embedding is generated locally, and Chroma applies an access-level metadata filter before results are returned.

Employees can retrieve employee chunks. HR can retrieve employee and HR chunks. The security-test folder is not indexed.

## Local requirements

Install Ollama from <https://ollama.com/download>, start it, and explicitly download the embedding model:

```powershell
ollama pull nomic-embed-text
```

The model download is a separate manual step. The backend does not pull models on startup or during requests. Chroma is an embedded local database; its telemetry is disabled in the client settings.

## Limits

This phase implements indexing and retrieval only. It does not generate answers, sanitize malicious document instructions, or provide an audit-grade security guarantee. The vector directory contains document data and is excluded from Git.
