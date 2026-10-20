# Phase 3: Minimal Local Audit Logging

Phase 3 adds a local JSON Lines audit trail around protected document searches.

## Recorded fields

Each event records a UTC timestamp, action, role, outcome, and result count. Search terms, bearer tokens, source filenames, and document contents are intentionally excluded.

Events are appended to `logs/audit.jsonl` by default. Set `RAGSHIELD_AUDIT_LOG` to select another local path. The `logs/` directory is excluded from Git.

## Current limits

The log is a local development artifact, not a tamper-proof compliance record. It has no rotation or centralized collection. Audit write errors stop the affected request rather than returning an unlogged search result. These controls are a foundation for later review and security testing, not proof of complete security.
