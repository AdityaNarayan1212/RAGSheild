"""FastAPI entry point for the RAGShield backend."""

from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query

from app.audit import record_event
from app.auth import Role, require_hr, require_role
from app.config import APP_TITLE, HEALTH_STATUS
from app.documents import SearchResult, search_documents
from app.ollama import OllamaUnavailable
from app.rag import SemanticResult, rebuild_index, semantic_search

app = FastAPI(title=APP_TITLE)


@app.get("/health")
def health_check() -> dict[str, str]:
    """Report that the API process is responding without exposing host details."""
    return {"status": HEALTH_STATUS}


@app.get("/documents/search")
def search_local_documents(
    query: Annotated[str, Query(alias="q", min_length=1, max_length=200)],
    role: Annotated[Role, Depends(require_role)],
    limit: Annotated[int, Query(ge=1, le=20)] = 10,
) -> dict[str, list[SearchResult]]:
    """Return matching local documents visible to the authenticated role."""
    results = search_documents(query.strip(), role, limit)
    record_event(
        "document_search",
        role,
        "success" if results else "empty",
        result_count=len(results),
    )
    return {"results": results}


@app.post("/documents/index")
def index_local_documents(
    role: Annotated[Role, Depends(require_hr)],
) -> dict[str, int]:
    """Rebuild the local vector index from the employee and HR source folders."""
    try:
        result = rebuild_index()
    except OllamaUnavailable as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    record_event("document_index", role, "success", result_count=result["chunk_count"])
    return result


@app.get("/documents/semantic-search")
def search_semantic_documents(
    query: Annotated[str, Query(alias="q", min_length=1, max_length=200)],
    role: Annotated[Role, Depends(require_role)],
    limit: Annotated[int, Query(ge=1, le=20)] = 5,
) -> dict[str, list[SemanticResult]]:
    """Return role-filtered vector matches from the local Chroma collection."""
    try:
        results = semantic_search(query.strip(), role, limit)
    except OllamaUnavailable as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    record_event(
        "document_search",
        role,
        "success" if results else "empty",
        result_count=len(results),
    )
    return {"results": results}
