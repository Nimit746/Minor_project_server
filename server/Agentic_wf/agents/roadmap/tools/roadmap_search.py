import asyncio
from typing import List, Dict, Any
from ddgs import DDGS

# In-memory search cache to avoid duplicate queries and rate limits
_SEARCH_CACHE: Dict[str, List[Dict[str, Any]]] = {}


async def search_resources_for_topics(
    query: str,
    max_results: int = 4,
    cache: bool = True
) -> List[Dict[str, Any]]:
    """
    Optimized web search tool for the roadmap agent.
    Features:
    - In-memory caching for identical or repeated queries.
    - Runs blocking DDGS in an async executor thread.
    - Limits payload size and sanitizes snippets to save tokens downstream.
    """
    cache_key = query.strip().lower()
    if cache and cache_key in _SEARCH_CACHE:
        return _SEARCH_CACHE[cache_key]

    def _sync_ddgs_call() -> List[Dict[str, Any]]:
        try:
            results = DDGS().text(
                query,
                max_results=max_results,
                max_retries=2
            )
            compact = []
            for r in (results or []):
                compact.append({
                    "title": r.get("title", ""),
                    "href": r.get("href", ""),
                    "url": r.get("href", ""),
                    "body": (r.get("body", "") or "")[:200]
                })
            return compact
        except Exception:
            return []

    try:
        loop = asyncio.get_running_loop()
        results = await loop.run_in_executor(None, _sync_ddgs_call)
        if cache and results:
            _SEARCH_CACHE[cache_key] = results
        return results
    except Exception:
        return []
