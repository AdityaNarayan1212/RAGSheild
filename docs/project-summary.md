# RAGShield Project Summary

## What the project is

RAGShield is a local learning project for a role-aware Retrieval-Augmented Generation (RAG) assistant. It answers questions from fictional NovaTech employee documents. Employee credentials can reach employee material; HR credentials can reach employee and HR material. The project demonstrates how authorization, retrieval, answer generation, citations, auditing, a browser UI, and adversarial checks fit together.

It is a development and learning system, not a production identity platform or proof that an AI model is safe.

## Phase history

| Phase | Delivered |
| --- | --- |
| 1. Project foundation | FastAPI app, health endpoint, dependency setup, environment example, repository structure, starter tests. |
| 2. Role-aware document search | Local employee and HR bearer tokens, fictional Markdown source files, keyword search filtered by role. |
| 3. Local audit logging | JSON Lines events for searches, answers, indexing, and denied authentication. Logs omit tokens, queries, and document content. |
| 4. Semantic retrieval | Ollama embeddings, persistent local Chroma index, document chunking, HR-only indexing, role-filtered vector search. |
| 5. Grounded answer generation | Local Ollama chat model receives authorized passages; API returns answer plus server-selected source references. Model installation is manual. |
| 6. Frontend and security review | React/Vite sign-in, chat, citations, status page, read-only security probes, isolated synthetic fixtures, dataset validator, backend and frontend regression suites. |
| 7. Retrieval relevance controls | Optional cosine-distance cutoff for semantic results and answer context, plus this project guide. Implementation is ready for review; verification is pending. |

Each phase has a separate commit in Git. [ROADMAP.md](../ROADMAP.md) records current status and links to phase notes.

## Architecture and data flow

1. **Frontend:** React and Vite run on loopback. The token stays in page memory and is sent as a bearer token to the API. Answer text renders as text; source references come from the API.
2. **Authentication:** FastAPI resolves the configured employee or HR token to a role. The UI's role preference is only a label and test assertion; it does not grant access.
3. **Sources:** Fictional employee and HR Markdown files live under `data/source/employee` and `data/source/hr`. Synthetic security fixtures are stored separately and are excluded from indexing.
4. **Retrieval:** HR can rebuild the persistent local Chroma index. Ollama embeds document chunks and questions. Chroma filters by allowed access level before returning chunks. The optional Phase 7 distance cutoff can further narrow those results.
5. **Generation:** The local Ollama chat model receives the question and authorized excerpts. System instructions treat excerpts as untrusted data. The API constructs citations separately from the model response.
6. **Audit:** The backend appends minimal events to a local JSONL file. It is not a tamper-proof audit system and the frontend does not expose it.

## Main API routes

- `GET /health` — confirms that the API process responds. It does not report model or index readiness.
- `GET /documents/search?q=...` — role-filtered keyword search.
- `POST /documents/index` — HR-only rebuild of the local vector collection.
- `GET /documents/semantic-search?q=...` — role-filtered semantic results, optionally narrowed by the Phase 7 cosine-distance cutoff.
- `POST /documents/answer` — retrieve authorized chunks, generate a local answer when matches remain, and return server-selected source metadata.

## Local technology

- Python, FastAPI, Uvicorn, pytest, and HTTPX for backend and API behavior.
- Ollama with `nomic-embed-text` embeddings and `qwen3:8b` answer generation by default.
- ChromaDB for local persistent vectors.
- React, Vite, JavaScript, CSS, and Vitest for the interface and frontend checks.
- No hosted inference service, paid API, or cloud database is required.

## Running it

Prerequisites are Python 3.10+, Node.js 20.19+ or 22.12+, Git, and Ollama. Install Python packages with `pip install -r requirements.txt`; install frontend packages from `frontend/` with `npm install`. Install the two Ollama models manually with `ollama pull nomic-embed-text` and `ollama pull qwen3:8b`.

Configure distinct local values for `RAGSHIELD_EMPLOYEE_TOKEN` and `RAGSHIELD_HR_TOKEN`, then start FastAPI on `127.0.0.1:8000`. From `frontend/`, run `npm run dev` and open `http://127.0.0.1:5173`. HR indexes the documents through `POST /documents/index` before semantic search or answers can use them. Full PowerShell commands are in [README.md](../README.md).

Optional `RAGSHIELD_MAX_COSINE_DISTANCE` accepts a number from `0` to `2`. Leave it blank until you compare distances for representative questions using the intended embedding model and source corpus. Lower values are stricter. This setting is a retrieval control, not a confidence score or a guarantee that the remaining passage supports the generated answer.

## Security boundaries

- Demo tokens are configured local credentials, not production authentication.
- Authorization is determined by the backend token. Request bodies and UI preferences cannot elevate a role.
- Role filtering occurs inside Chroma's query, before the relevance cutoff.
- The model does not choose its own citations; the backend supplies references from retrieved passages.
- Prompt instructions and adversarial tests reduce risk but cannot prove model behavior safe.
- The status page checks only `/health`; Ollama readiness and index state remain unknown.
- The local audit file omits user content but is not tamper-proof. Uvicorn access logs can expose keyword query strings if enabled; the documented run command disables them.
- The frontend security lab performs read-only requests and does not rebuild or mutate the index.

## Verification and remaining work

Before release, rerun the backend tests, dataset validator, frontend tests, and production build. The previous Phase 6 run passed 28 pytest tests, 10 Vitest tests, dataset validation, and the frontend production build. Those results predate Phase 7 and do not verify the new cutoff.

Phase 7 still needs regression coverage for configured and unset cutoffs, invalid values, and the answer path when all candidates are filtered. It also needs calibration with the actual local models. Other known gaps include browser accessibility review, model-dependent live adversarial evaluation, isolated end-to-end indirect-injection evaluation, production-grade identity, and durable/tamper-resistant auditing.
