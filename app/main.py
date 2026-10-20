"""FastAPI entry point for the RAGShield backend."""

from typing import Annotated

from fastapi import Depends, FastAPI, Query

from app.audit import record_event
from app.auth import Role, require_role
from app.config import APP_TITLE, HEALTH_STATUS
from app.documents import SearchResult, search_documents

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
