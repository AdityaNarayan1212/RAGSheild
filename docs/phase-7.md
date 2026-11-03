# Phase 7: Retrieval Relevance Controls and Project Guide

## Goal

Give operators a way to reject weak semantic matches before they are shown to a user or passed to the answer model. Keep existing behavior when no cutoff has been calibrated. Add one project-wide guide that explains the complete build and its limits.

## Feature

The Chroma collection uses cosine distance. `RAGSHIELD_MAX_COSINE_DISTANCE` is an optional environment setting from `0` to `2`; lower values require closer embedding matches. When set, semantic results whose distance is greater than the configured value are removed. This affects both `GET /documents/semantic-search` and the retrieved context for `POST /documents/answer`.

Leave the setting blank to preserve the existing top-k behavior. There is no universal default because the useful cutoff depends on the embedding model, document corpus, and query set. Calibrate it against representative in-scope and out-of-scope questions before enabling it. Invalid values produce a clear HTTP 500 configuration error and are not silently ignored.

The role filter remains part of the Chroma query. Relevance filtering happens only after Chroma has selected matches within the authenticated role's allowed categories, so it cannot expand access.

## Project guide

See [project-summary.md](project-summary.md) for the system overview, phase history, setup path, security boundaries, and remaining work.

## Review status

Implementation is prepared for review. Automated tests and live model checks have not been run for this phase. Re-run the backend suite, dataset validator, frontend suite, and production build before treating this phase as verified. Model cutoff calibration requires the intended local Ollama embedding model and representative queries.
