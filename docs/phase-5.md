# Phase 5: Local Answer Generation

Phase 5 adds a role-protected answer endpoint on top of Phase 4 retrieval. The API searches the local Chroma index with the authenticated role, sends only those retrieved excerpts to the local Ollama chat endpoint, and returns source references selected from the retrieved metadata.

## Request and response

`POST /documents/answer` accepts a JSON body containing a `query` string. The response contains an `answer` and a `sources` list. Sources are selected by the API from retrieved results; the model does not control the source list. If retrieval returns no results, the API returns a fixed no-results answer without calling the generation model.

## Local requirements

Install Ollama and explicitly download both models:

```powershell
ollama pull nomic-embed-text
ollama pull qwen3:8b
```

The app makes non-streaming requests to the local `/api/chat` endpoint. It does not call hosted inference or pull models automatically.

## Prompt-injection handling and limits

Retrieved excerpts are serialized as JSON data in a user message. A system message instructs the model to treat excerpts as untrusted reference text, ignore commands embedded in them, and answer only from supported facts. The authenticated role is applied during retrieval before generation, so HR-only passages are not added to an employee prompt. Source references are built from the same authorized retrieval results.

These prompt instructions and tests are defense-in-depth, not a guarantee that a language model will resist every prompt injection. Review generated answers and keep adversarial tests as controls evolve.
