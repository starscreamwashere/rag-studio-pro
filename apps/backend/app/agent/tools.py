"""Agent tools.

Internal retrieval tools (vector/graph/hybrid) reuse app.rag.* directly inside
the agent graph. This module holds the external Web Search tool (DuckDuckGo,
no API key) — the one "sensitive" action gated by human approval.
"""

from app.core.config import settings


def web_search(query: str) -> list[dict]:
    """Best-effort web search. Returns [] on any failure (never breaks the agent)."""
    try:
        from ddgs import DDGS

        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=settings.web_search_max_results)
        return [
            {
                "title": r.get("title", ""),
                "snippet": r.get("body", ""),
                "url": r.get("href", ""),
            }
            for r in results
        ]
    except Exception:  # noqa: BLE001 — web search is optional/best-effort
        return []
