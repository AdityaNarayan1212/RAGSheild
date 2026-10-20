# RAGShield

RAGShield is a learning project for building and testing a locally run, access-controlled Retrieval-Augmented Generation (RAG) application. The planned NovaTech assistant will answer employee questions from company documents while keeping HR-only material restricted. Later phases will explore retrieval authorization, prompt injection in documents, audit logging, and security testing.

## Current status

Phase 1 provides a small FastAPI backend with a `GET /health` endpoint and a test for its JSON response. It does not yet load documents, enforce roles, connect to Ollama, store embeddings, or provide a frontend. A successful health check only confirms that the API responds; it does not prove application security.

## Planned architecture

- Python and FastAPI provide the backend API.
- Ollama will run the language model locally (`qwen3:8b`) and the embedding model (`nomic-embed-text`).
- ChromaDB will store local document embeddings.
- React, Vite, JavaScript, and CSS will provide the planned frontend.
- pytest will verify backend behavior and later security controls.

No paid API, hosted inference service, or cloud database is required.

## Prerequisites

Install these tools from their official sources:

- Python 3.10 or newer: <https://www.python.org/downloads/>
- Git: <https://git-scm.com/downloads>
- Node.js (includes npm): <https://nodejs.org/en/download>
- Ollama: <https://ollama.com/download>

Only Python is needed to run the Phase 1 backend. Node.js and Ollama are listed for later phases; this phase does not install or download any AI model.

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
- `httpx` provides the HTTP client used by FastAPI's test client.

If PowerShell blocks virtual environment activation, use Command Prompt without changing the machine's execution policy:

```bat
.venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
```

You can also avoid activation by calling `.venv\Scripts\python.exe` directly.

## Run the backend

With the virtual environment active, start the local development server:

```powershell
python -m uvicorn app.main:app --reload
```

Open <http://127.0.0.1:8000/health> to see `{"status":"ok"}`. Stop the server with **Ctrl+C** in its terminal.

## Run the tests

```powershell
python -m pytest
```

The health test checks the HTTP status, JSON content type, and expected status value.

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

This API is the starting point for later routes. Future phases can add document ingestion and embeddings, retrieve only passages authorized for the signed-in user's role, and send the allowed context to a local Ollama model. The current health endpoint exposes no secrets or machine-specific details, and none of those future capabilities are represented as implemented yet.

