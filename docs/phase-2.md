# Phase 2: Role-Aware Local Document Search

Phase 2 adds a small local search path that demonstrates one key RAG security rule: determine the caller's role and filter allowed document sources before reading or ranking their contents.

## What is implemented

- `RAGSHIELD_EMPLOYEE_TOKEN` and `RAGSHIELD_HR_TOKEN` select the employee and HR demo roles.
- `/documents/search?q=...` requires a bearer token and searches local Markdown documents.
- Employees can search only `data/source/employee`; HR can search employee and HR sources.
- `data/source/security-tests` is excluded from ordinary search.
- The fixture documents contain fictional process descriptions, not real employee records.

## Local setup

Set distinct token values in the PowerShell window used to start the server:

```powershell
$env:RAGSHIELD_EMPLOYEE_TOKEN = [guid]::NewGuid().ToString('N')
$env:RAGSHIELD_HR_TOKEN = [guid]::NewGuid().ToString('N')
python -m uvicorn app.main:app --reload
```

The endpoint returns `503` if either token is missing or both tokens are equal. It returns `401` for missing or invalid bearer credentials.

## Design limits

These tokens are a local demonstration mechanism, not a production login system. Keyword search is used to keep the phase dependency-free; there is no embedding model, vector database, prompt construction, or LLM call yet. The authorization tests cover expected role filtering but do not establish that the application is secure against all attacks.
