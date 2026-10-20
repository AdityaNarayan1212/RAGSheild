"""Simple local keyword search with role filtering before document reads."""

import re
from pathlib import Path
from typing import TypedDict

from app.config import Role

DOCUMENT_ROOT = Path(__file__).resolve().parents[1] / "data" / "source"


class SearchResult(TypedDict):
    title: str
    source: str
    snippet: str
    score: int


def search_documents(query: str, role: Role, limit: int) -> list[SearchResult]:
    """Search only the document categories the authenticated role may access."""
    categories = ("employee", "hr") if role == "hr" else ("employee",)
    terms = {term.casefold() for term in re.findall(r"\w+", query) if len(term) > 1}
    matches: list[SearchResult] = []

    for category in categories:
        category_path = DOCUMENT_ROOT / category
        if not category_path.is_dir():
            continue

        for path in sorted(category_path.glob("*.md")):
            content = path.read_text(encoding="utf-8")
            title = next(
                (line.lstrip("# ").strip() for line in content.splitlines() if line.startswith("# ")),
                path.stem.replace("-", " ").title(),
            )
            searchable_text = f"{title}\n{content}".casefold()
            score = sum(searchable_text.count(term) for term in terms)
            if score:
                matches.append(
                    {
                        "title": title,
                        "source": path.name,
                        "snippet": " ".join(content.split())[:320],
                        "score": score,
                    }
                )

    return sorted(matches, key=lambda result: (-result["score"], result["source"]))[:limit]
