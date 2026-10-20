"""FastAPI entry point for the RAGShield backend."""

from fastapi import FastAPI

from app.config import APP_TITLE, HEALTH_STATUS

app = FastAPI(title=APP_TITLE)


@app.get("/health")
def health_check() -> dict[str, str]:
    """Report that the API process is responding without exposing host details."""
    return {"status": HEALTH_STATUS}
