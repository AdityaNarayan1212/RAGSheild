# Phase 6: Frontend, Security Review, and Adversarial Testing

Phase 6 adds a local React/Vite interface to the existing FastAPI, Ollama, and Chroma application. The UI calls the existing API contracts through a loopback-only Vite proxy; it does not add a role-reporting endpoint, audit-log reader, file reader, or reindexing control.

## Pages and behavior

- **Document chat** calls `POST /documents/answer`, keeps conversation history in React memory, renders answer text as ordinary React text, and shows only the title, source name, and access level returned by the API. Duplicate citations are collapsed. No Markdown or HTML renderer is used.
- **Security lab** sends controlled requests to the running local API and records actual HTTP status, assertion outcome, and returned source names. It tests health, absent/invalid credentials, authenticated search, role-scoped search, synthetic fixture exclusion, answer response shape, and the retrieval scope of a direct prompt override. Model-dependent checks are marked blocked when the endpoint returns 503.
- **System status** checks only `GET /health`. Ollama readiness and index status remain unknown because the backend has no safe status contracts for them. A prior answer request's HTTP 503 is shown as an observed failure without claiming its cause.
- **Sign-in** accepts a locally configured bearer token and a display preference. The backend token determines authorization; the preference only chooses an assertion context and label. The token is held in React state, never written to browser storage, and is cleared on sign-out or refresh.

The frontend maps HTTP errors to safe user messages rather than showing backend stack traces or raw response bodies. It does not log credentials or document contents. The Vite development server and proxy bind to `127.0.0.1`; the backend remains responsible for authentication and role filtering. The documented Uvicorn command disables access logs because the default request line includes the `q=` query string for keyword search.

## API use and security test boundaries

The UI uses `GET /health`, `GET /documents/search?q=...`, and `POST /documents/answer`. It does not send a role parameter. The server's existing `/documents/index` route rebuilds the persistent Chroma collection, so the live security page does not invoke it. Backend tests verify that an employee token receives HTTP 403 from that route before indexing starts.

The synthetic canary and indirect-injection excerpt live in `data/source/security-tests/phase-6-fixtures.json`. The indexer reads only `.md` files under the `employee` and `hr` folders. The security fixture is not copied into either source folder or the production collection. The browser security page checks that ordinary keyword search returns no result for both fixture markers. `tests/test_generation.py` checks how an indirect-injection excerpt is serialized as untrusted data; this does not prove that a live language model will resist every attack. The live direct-injection probe checks source authorization and leaves model behavior for human review.

The frontend does not expose the local JSONL audit file. Audit events remain a local development artifact, omit user content and tokens, and are not tamper-proof. There is no frontend activity viewer. If access logs are enabled manually, Uvicorn may print keyword-search query strings to the terminal.

## Automated coverage

Backend pytest coverage includes missing and invalid bearer tokens, HR-only index authorization, role-filtered keyword/vector retrieval, request-supplied role override attempts, authorized answer sources, empty retrieval skipping generation, safe 503 behavior, audit privacy, and separation of security fixtures from indexable data. Ollama-dependent unit paths use mocks; ordinary tests do not download models.

Frontend Vitest coverage checks Authorization-header construction, malformed JSON handling, citation validation/deduplication, and that model-supplied HTML is escaped as text. `npm run build` checks that the Vite app compiles. These tests do not replace browser accessibility review, live-model evaluation, or a broader security assessment.

## Run locally on Windows

Use Node.js 22.12+ or 20.19+, Python 3.10+, and PowerShell. Open separate terminal windows from the repository root.

### 1. Set up Python dependencies

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If the environment already exists, activate it and install the current requirements:

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Set up local Ollama models

Install Ollama from its official installer. If the local service is not running, start it in a separate window with `ollama serve`. Download models explicitly; the app never installs them automatically:

```powershell
ollama pull nomic-embed-text
ollama pull qwen3:8b
ollama list
```

### 3. Start FastAPI

In a PowerShell window at the repository root, set two different temporary demo tokens and run the backend:

```powershell
$employeeToken = Read-Host 'Choose a local employee token and remember it for sign-in'
$hrToken = Read-Host 'Choose a different local HR token and remember it for sign-in'
$env:RAGSHIELD_EMPLOYEE_TOKEN = $employeeToken
$env:RAGSHIELD_HR_TOKEN = $hrToken
python -m uvicorn app.main:app --reload --host 127.0.0.1 --no-access-log
```

Keep this window open. The tokens are available only in this PowerShell process. Sign in to the frontend with either token; do not put token values in source files or commit them.

### 4. Index documents when needed

Semantic search and answer generation need an existing Chroma index. Rebuilding it replaces the current local collection, so use this command intentionally from a separate PowerShell window with the same HR token value set in that window:

```powershell
$hrToken = Read-Host 'Enter the same local HR token used in the backend window'
$env:RAGSHIELD_HR_TOKEN = $hrToken
$headers = @{ Authorization = "Bearer $env:RAGSHIELD_HR_TOKEN" }
Invoke-RestMethod -Method Post -Uri 'http://127.0.0.1:8000/documents/index' -Headers $headers
```

For local development, enter the same HR token value when prompted in the second window. The indexer includes only the employee and HR source folders.

### 5. Start the frontend

From the repository root in another PowerShell window:

```powershell
cd frontend
npm install
npm run dev
```

Open <http://127.0.0.1:5173>. Vite proxies `/api` to FastAPI at `http://127.0.0.1:8000`.

### 6. Validate dataset and run tests

From the repository root, with the Python environment active:

```powershell
python scripts/validate_dataset.py
python -m pytest -q
```

If `.venv\Scripts\Activate.ps1` is unavailable, run the same checks through the environment interpreter:

```powershell
.\.venv\Scripts\python.exe scripts\validate_dataset.py
.\.venv\Scripts\python.exe -m pytest -q
```

From `frontend/`:

```powershell
npm test
npm run build
```

The browser security page can run authentication and keyword-access probes without Ollama. The normal-answer and direct-injection probes require the embedding model, a populated Chroma index, and the chat model. If they return HTTP 503, check that Ollama is running and both models are installed; the UI records the real status and does not mark that run as passed.

## Known limitations

- Local demo bearer tokens are not a production identity system. They are configured by the backend operator and should not be reused as real credentials.
- The display preference is not a verified role label. A mismatch between preference and token permissions should make a role-specific probe fail.
- The backend's health endpoint says only that the API process responds. It does not test Ollama, model readiness, or index presence.
- The answer endpoint has no configurable retrieval relevance threshold. A query with no semantic matches cannot be reliably demonstrated through live answer behavior until such a contract exists; the no-retrieval branch is verified with mocked retrieval in pytest.
- The isolated indirect-injection fixture is not injected into the production index. An end-to-end fixture test would need a separate isolated test collection and explicit lifecycle controls.
- The UI does not display audit records. The JSONL file remains local, append-only by convention, and not tamper-proof.
- Prompt instructions and source-scope tests are defense-in-depth, not proof of model safety.
