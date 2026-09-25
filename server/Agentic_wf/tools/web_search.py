import asyncio
import logging

from langchain_core.tools import tool

from Agentic_wf.config.settings import get_settings

logger = logging.getLogger(__name__)

_MAX_ATTEMPTS = 3
_BASE_BACKOFF_SECONDS = 1.5
_SEARCH_TIMEOUT_SECONDS = 10

settings = get_settings()


# ---------------------------------------------------------------------------
# Tavily backend (primary)
# ---------------------------------------------------------------------------

def _search_tavily_sync(query: str, max_results: int) -> list[dict]:
    """Blocking Tavily call — run off the event loop via a thread."""
    from tavily import TavilyClient

    client = TavilyClient(api_key=settings.tavily_api_key)
    response = client.search(query=query, max_results=max_results)

    results = []
    for item in response.get("results", []):
        results.append({
            "title": item.get("title", ""),
            "href": item.get("url", ""),
            "body": item.get("content", ""),
        })
    return results


async def _try_tavily(query: str, max_results: int) -> list[dict] | None:
    """Attempt Tavily search with retry/backoff. Returns None on total failure
    (so the caller can fall back to DDGS), or a list (possibly empty) on success.
    """
    if not settings.tavily_api_key:
        logger.info("settings.tavily_api_key not set; skipping Tavily backend.")
        return None

    last_error: Exception | None = None

    for attempt in range(1, _MAX_ATTEMPTS + 1):
        try:
            results = await asyncio.wait_for(
                asyncio.to_thread(_search_tavily_sync, query, max_results),
                timeout=_SEARCH_TIMEOUT_SECONDS,
            )
            return results or []

        except asyncio.TimeoutError as e:
            last_error = e
            logger.warning(
                "Tavily search timed out (attempt %d/%d) for query '%s'",
                attempt, _MAX_ATTEMPTS, query,
            )

        except Exception as e:
            last_error = e
            logger.warning(
                "Tavily error (attempt %d/%d) for query '%s': %s",
                attempt, _MAX_ATTEMPTS, query, e,
            )
            if attempt < _MAX_ATTEMPTS:
                wait = _BASE_BACKOFF_SECONDS * (2 ** (attempt - 1))
                await asyncio.sleep(wait)

    logger.error(
        "Tavily exhausted %d attempts for query '%s': %s",
        _MAX_ATTEMPTS, query, last_error,
    )
    return None


# ---------------------------------------------------------------------------
# DDGS backend (free fallback)
# ---------------------------------------------------------------------------

def _search_ddgs_sync(query: str, max_results: int) -> list[dict]:
    """Blocking DDGS call — run off the event loop via a thread."""
    from ddgs import DDGS

    with DDGS() as ddgs:
        return ddgs.text(query, max_results=max_results, backend="lite")


async def _try_ddgs(query: str, max_results: int) -> list[dict]:
    """Attempt DDGS search with retry/backoff. Returns [] on total failure."""
    from ddgs.exceptions import DDGSException, RatelimitException

    last_error: Exception | None = None

    for attempt in range(1, _MAX_ATTEMPTS + 1):
        try:
            results = await asyncio.wait_for(
                asyncio.to_thread(_search_ddgs_sync, query, max_results),
                timeout=_SEARCH_TIMEOUT_SECONDS,
            )
            return results or []

        except RatelimitException as e:
            last_error = e
            wait = _BASE_BACKOFF_SECONDS * (2 ** (attempt - 1))
            logger.warning(
                "DDGS rate-limited (attempt %d/%d) for query '%s'; backing off %.1fs",
                attempt, _MAX_ATTEMPTS, query, wait,
            )
            if attempt < _MAX_ATTEMPTS:
                await asyncio.sleep(wait)

        except asyncio.TimeoutError as e:
            last_error = e
            logger.warning(
                "DDGS search timed out (attempt %d/%d) for query '%s'",
                attempt, _MAX_ATTEMPTS, query,
            )

        except DDGSException as e:
            last_error = e
            logger.warning(
                "DDGS error (attempt %d/%d) for query '%s': %s",
                attempt, _MAX_ATTEMPTS, query, e,
            )
            if attempt < _MAX_ATTEMPTS:
                await asyncio.sleep(_BASE_BACKOFF_SECONDS)

        except Exception as e:
            logger.error("Unexpected error in DDGS search for '%s': %s", query, e)
            return []

    logger.error(
        "DDGS exhausted %d attempts for query '%s': %s",
        _MAX_ATTEMPTS, query, last_error,
    )
    return []


# ---------------------------------------------------------------------------
# Public interface
# ---------------------------------------------------------------------------

async def web_search_impl(query: str, max_results: int = 7) -> list[dict]:
    """Search the web, preferring Tavily and falling back to DDGS.

    Safe to call directly from other tools or backend code — this is the
    one to import when you need search results programmatically, without
    going through LangChain's tool-invocation machinery.

    Args:
        query: The search query string.
        max_results: Maximum number of results to return (default 7).

    Returns:
        A list of result dicts with keys "title", "href", "body", or an
        empty list if the query was empty or both backends failed.
    """
    if not query or not query.strip():
        return []

    tavily_results = await _try_tavily(query, max_results)
    if tavily_results is not None:
        if tavily_results:
            return tavily_results
        logger.info("Tavily returned no results for '%s'; trying DDGS fallback.", query)
    else:
        logger.info("Tavily unavailable for '%s'; trying DDGS fallback.", query)

    return await _try_ddgs(query, max_results)


@tool
async def web_search(query: str, max_results: int = 7) -> list[dict]:
    """Performs a web search to find up-to-date information on a given query.
    Uses Tavily as the primary backend (if TAVILY_API_KEY is configured) and
    falls back to DuckDuckGo search (DDGS) if Tavily is unavailable or fails.
    Useful for researching companies, technical topics, or any other
    information that requires accessing the internet.

    Args:
        query: The search query string.
        max_results: Maximum number of results to return (default 7).

    Returns:
        A list of search result dicts, or an empty list if the search
        failed or returned nothing.
    """
    return await web_search_impl(query, max_results)