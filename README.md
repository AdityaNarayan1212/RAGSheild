# RAGShield

RAGShield is a learning project for building and testing a locally run, access-controlled Retrieval-Augmented Generation (RAG) application. The planned NovaTech assistant will answer employee questions from company documents while keeping HR-only material restricted. Later phases will explore retrieval authorization, prompt injection in documents, audit logging, and security testing.

## Current status

Phase 1 provides the FastAPI foundation. Phase 2 adds local bearer-token roles and keyword search over fictional employee and HR Markdown files. Phase 3 writes local JSON Lines audit events for searches and denied authentication attempts. Phase 4 adds local Ollama embeddings and a persistent Chroma vector index with role-filtered semantic retrieval. There is no answer-generating LLM route or frontend yet. A successful health check only confirms that the API responds; it does not prove application security.

See [ROADMAP.md](ROADMAP.md) for delivered features and planned phases.

## Planned architecture

- Python and FastAPI provide the backend API.
- Ollama will run the language model locally (`qwen3:8b`) and the embedding model (`nomic-embed-text`).
- ChromaDB will store local document embeddings.
- React, Vite, JavaScript, and CSS will provide the planned frontend.
- pytest will verify backend behavior and later security controls.
- Local bearer tokens select the demo employee or HR role for protected routes.
- The audit log records event type, role, outcome, and result count without credentials or document content.
- Ollama creates embeddings locally; Chroma persists vectors under `data/chroma`.

No paid API, hosted inference service, or cloud database is required.

## Prerequisites

Install these tools from their official sources:

- Python 3.10 or newer: <https://www.python.org/downloads/>
- Git: <https://git-scm.com/downloads>
- Node.js (includes npm): <https://nodejs.org/en/download>
- Ollama: <https://ollama.com/download>

Python is needed for the backend. Install Ollama to use Phase 4 semantic indexing and search. Node.js is listed for the later frontend phase. Installing the Python dependencies does not download an Ollama model.

After installation, open a new PowerShell window and check the tools:

```powershell
python --version
python -m pip --version
git --version
node --version
npm --version
ollama --version
```

## Set up on Windows

Run these commands from the project folder in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

The requirements are limited to this phase:

- `fastapi` builds the API and its route.
- `uvicorn` runs the development server.
- `pytest` runs automated tests.
- `httpx` provides the HTTP client used by the API and test client.
- `chromadb` stores local embeddings and document metadata.

If PowerShell blocks virtual environment activation, use Command Prompt without changing the machine's execution policy:

```bat
.venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
```

You can also avoid activation by calling `.venv\Scripts\python.exe` directly.

## Run the backend

With the virtual environment active, configure two different local demo tokens and start the server in the same PowerShell window:

```powershell
$env:RAGSHIELD_EMPLOYEE_TOKEN = [guid]::NewGuid().ToString('N')
$env:RAGSHIELD_HR_TOKEN = [guid]::NewGuid().ToString('N')
python -m uvicorn app.main:app --reload
```

Open <http://127.0.0.1:8000/health> to see `{"status":"ok"}`. Stop the server with **Ctrl+C** in its terminal.

Search local documents by passing one of those tokens in an Authorization header. The employee token can search only `data/source/employee`; the HR token can search both employee and HR files. The `data/source/security-tests` folder is never searched.

```powershell
$headers = @{ Authorization = "Bearer $env:RAGSHIELD_EMPLOYEE_TOKEN" }
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/documents/search?q=leave' -Headers $headers
```

The tokens are local development credentials, not a production identity system. Keep any real values out of Git, and do not use the sample token values from tests outside testing.

Audit events are appended to `logs/audit.jsonl` by default. Set `RAGSHIELD_AUDIT_LOG` to choose another local path. The `logs/` directory is excluded from Git.

To enable semantic search, install Ollama from <https://ollama.com/download>, then download the configured embedding model yourself:

```powershell
ollama pull nomic-embed-text
```

The application never downloads models automatically. With Ollama running and the role tokens configured, the HR role can index the fictional source documents:

```powershell
$hrHeaders = @{ Authorization = "Bearer $env:RAGSHIELD_HR_TOKEN" }
Invoke-RestMethod -Method Post -Uri 'http://127.0.0.1:8000/documents/index' -Headers $hrHeaders
```

Use either token to search the index. Employee results are filtered to employee metadata inside Chroma; HR can retrieve employee and HR results.

```powershell
$headers = @{ Authorization = "Bearer $env:RAGSHIELD_EMPLOYEE_TOKEN" }
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/documents/semantic-search?q=leave' -Headers $headers
```

## Run the tests

```powershell
python -m pytest
```

The tests check the health response, token validation, keyword and vector-search role isolation, HR indexing permission, local embedding requests, chunking, and that audit entries omit tokens and search text.

## Troubleshooting

- **`python` is not recognized:** install Python from the official link above, enable its PATH option in the installer if offered, then open a new terminal. Do not change system PATH automatically as part of this project.
- **`pip` is not found:** use `python -m pip` to run pip through the selected Python installation.
- **PowerShell refuses activation:** use the Command Prompt activation commands above, or call `.venv\Scripts\python.exe` directly. No machine-wide policy change is needed.
- **`No module named fastapi`:** activate `.venv` and run `pip install -r requirements.txt` from this folder.
- **Port 8000 is busy:** start Uvicorn with `--port 8001` and open `http://127.0.0.1:8001/health`.

## Git safety

The `.gitignore` excludes virtual environments, secrets, local ChromaDB data, logs, generated sensitive security-test data, and frontend build artifacts. It keeps `.env.example` available as documentation.

Git is initialized on the `main` branch in this workspace. For future changes, stage, commit, and push them with:

```powershell
git add .
git commit -m "Describe your change"
git push origin main
```

## How this connects to the future RAG pipeline

This API now filters local source documents by a role selected from distinct bearer tokens, records minimal local audit events, and can retrieve authorized passages using local embeddings. Later phases can send approved passages to a local generation model and build a frontend. The current tests do not prove security against every attack.

