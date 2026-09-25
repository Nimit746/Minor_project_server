import asyncio
import json
import logging
from collections import defaultdict
from datetime import datetime, timezone
from langchain_core.tools import tool
from Agentic_wf.tools.web_search import web_search_impl as web_search

logger = logging.getLogger(__name__)

# Domains ranked by reliability for interview-experience content.
# Used only to sort/tag results, never to drop them outright.
_HIGH_SIGNAL_DOMAINS = {
    "leetcode.com": "question_bank",
    "glassdoor.com": "process_report",
    "geeksforgeeks.org": "question_bank",
    "teamblind.com": "process_report",
    "1point3acres.com": "process_report",
    "reddit.com": "process_report",
}

_CACHE_TTL_SECONDS = 60 * 60 * 24  # 24h; company interview patterns don't churn hourly
_cache: dict[str, tuple[float, dict]] = {}


def _domain_of(url: str) -> str:
    try:
        return url.split("/")[2].replace("www.", "")
    except IndexError:
        return ""


def _build_queries(company_name: str, target_role: str) -> list[tuple[str, str]]:
    """Returns (query, category) pairs. Categories let us bucket results
    instead of returning one undifferentiated list."""
    return [
        (f"{company_name} {target_role} interview process rounds 2026", "process"),
        (f"{company_name} {target_role} interview questions site:leetcode.com OR site:geeksforgeeks.org", "questions"),
        (f"{company_name} {target_role} interview experience 2025 2026", "experience"),
        (f"{company_name} {target_role} system design interview round", "system_design"),
        (f"{company_name} {target_role} coding round difficulty pattern", "difficulty"),
    ]


async def _run_query(query: str, category: str) -> tuple[str, list[dict]]:
    try:
        hits = await web_search(query)
        return category, hits or []
    except Exception as e:
        logger.warning("Search failed for query '%s': %s", query, e)
        return category, []

@tool
async def get_company_profile(company_name: str, target_role: str = "Software Engineer") -> str:
    """Fetch current, real-world data on a company's technical interview
    patterns — process/rounds, recent question types, system-design focus,
    and difficulty signals — so prep can be grounded in that company's
    actual interview style rather than generic DSA advice.

    Args:
        company_name: Name of the company (e.g. "Google", "Stripe", "Razorpay").
        target_role: The role being interviewed for. Defaults to "Software Engineer".

    Returns:
        JSON string with keys: company, target_role, generated_at, rounds_summary
        (best-effort extracted round structure if evident from results),
        by_category (dict of category -> list of {title, url, domain,
        signal_type, snippet}), and note (present only if nothing was found).
    """
    company_name = (company_name or "").strip()
    target_role = (target_role).strip()

    if not company_name:
        return json.dumps({"error": "No company name provided."})

    cache_key = f"{company_name.lower()}::{target_role.lower()}"
    now = datetime.now(timezone.utc).timestamp()
    if cache_key in _cache:
        cached_at, cached_payload = _cache[cache_key]
        if now - cached_at < _CACHE_TTL_SECONDS:
            return json.dumps(cached_payload)

    queries = _build_queries(company_name, target_role)

    # Run all queries concurrently instead of sequentially.
    query_results = await asyncio.gather(
        *(_run_query(q, cat) for q, cat in queries)
    )

    by_category: dict[str, list[dict]] = defaultdict(list)
    seen_urls: set[str] = set()

    for category, hits in query_results:
        for r in hits:
            url = r.get("url", "")
            if not url or url in seen_urls:
                continue
            seen_urls.add(url)
            domain = _domain_of(url)
            by_category[category].append({
                "title": r.get("title", ""),
                "url": url,
                "domain": domain,
                "signal_type": _HIGH_SIGNAL_DOMAINS.get(domain, "general"),
                "snippet": r.get("snippet") or r.get("content", ""),
            })
        # Cap each category so one noisy query doesn't dominate the payload
        by_category[category] = by_category[category][:6]

    total_results = sum(len(v) for v in by_category.values())

    payload = {
        "company": company_name,
        "target_role": target_role,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "by_category": dict(by_category),
    }

    if total_results == 0:
        payload["note"] = (
            f"No recent search results found for {company_name} / {target_role}. "
            "Fall back to general patterns for the company's industry/tier."
        )
    else:
        _cache[cache_key] = (now, payload)

    return json.dumps(payload)