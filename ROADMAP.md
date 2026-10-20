# RAGShield Roadmap

This page tracks the project in reviewable phases. Each completed phase has its own commit in the Git history and a short implementation note under `docs/`. No calendar dates are assigned yet; add a target date to a phase when it is scheduled.

## Completed

### Phase 1 — Project foundation

**Status:** Complete  
**Delivered:** FastAPI application, health endpoint, dependency setup, environment example, repository structure, and starter tests.

### Phase 2 — Role-aware document search

**Status:** Complete  
**Delivered:** Local employee and HR bearer-token roles, fictional Markdown documents, keyword search, and role-based source filtering.

### Phase 3 — Local audit logging

**Status:** Complete  
**Delivered:** JSON Lines audit events for searches and denied authentication attempts, without recording credentials, queries, or document contents.

### Phase 4 — Local semantic retrieval

**Status:** Complete  
**Delivered:** Ollama embeddings, persistent local Chroma storage, HR-only indexing, and role-filtered semantic search.

## Next

### Phase 5 — Local answer generation

**Status:** Planned  
**Target date:** Not scheduled  
**Planned work:** Generate answers from authorized retrieved passages using a manually installed local Ollama model, return source references, and add tests for role isolation and prompt-injection handling. The app will not download models automatically.

## Later

### Phase 6 — User interface and security review

**Status:** Planned  
**Target date:** Not scheduled  
**Planned work:** Build the local web interface and expand adversarial tests for document access, prompt injection, and audit behavior.

## Following progress

- Each phase is kept in its own commit so the GitHub commit history shows what changed at each step.
- Feature tasks can be tracked as GitHub Issues and grouped by phase with Milestones. Add due dates there when the schedule is known.
- Update this page when a phase starts, changes scope, or is completed.
