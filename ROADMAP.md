# RAGShield Roadmap

This page tracks the project in reviewable phases. Each completed phase has its own commit in the Git history and a short implementation note under `docs/`. Completion dates reflect the phase commit dates; future targets remain unscheduled until agreed.

## Completed

### Phase 1 — Project foundation

**Status:** Complete — 2026-10-21

**Delivered:** FastAPI application, health endpoint, dependency setup, environment example, repository structure, and starter tests.

### Phase 2 — Role-aware document search

**Status:** Complete — 2026-10-21

**Delivered:** Local employee and HR bearer-token roles, fictional Markdown documents, keyword search, and role-based source filtering.

### Phase 3 — Local audit logging

**Status:** Complete — 2026-10-21

**Delivered:** JSON Lines audit events for searches and denied authentication attempts, without recording credentials, queries, or document contents.

### Phase 4 — Local semantic retrieval

**Status:** Complete — 2026-10-21

**Delivered:** Ollama embeddings, persistent local Chroma storage, HR-only indexing, and role-filtered semantic search.

### Phase 5 — Local answer generation

**Status:** Complete — 2026-10-21

**Delivered:** Generate answers from authorized retrieved passages using a manually installed local Ollama model, return server-selected source references, and test role isolation and prompt-injection handling. The app does not download models automatically.

## Next

### Phase 6 — User interface and security review

**Status:** Planned
**Target date:** Not scheduled

**Planned work:** Build the local web interface and expand adversarial tests for document access, prompt injection, and audit behavior.

## Following progress

- Each phase is kept in its own commit so the GitHub commit history shows what changed at each step.
- Feature tasks can be tracked as GitHub Issues and grouped by phase with Milestones. Add due dates there when the schedule is known.
- Update this page when a phase starts, changes scope, or is completed.
