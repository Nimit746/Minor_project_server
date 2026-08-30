import asyncio
from typing import Any, Dict, List
from Agentic_wf.agents.roadmap.states import Roadmap
from Agentic_wf.agents.roadmap.tools import search_resources_for_topics


def _classify_resource_type(title: str, url: str) -> str:
    """Classifies resource type based on URL and title semantics."""
    u = (url or "").lower()
    t = (title or "").lower()
    if "youtube.com" in u or "youtu.be" in u or "video" in t:
        return "video"
    elif "github.com" in u or "gitlab.com" in u:
        return "github"
    elif "udemy.com" in u or "coursera.org" in u or "edx.org" in u or "course" in t:
        return "course"
    elif "leetcode.com" in u or "hackerrank.com" in u or "practice" in t or "drills" in t:
        return "practice"
    elif "docs." in u or "developer." in u or "documentation" in t:
        return "doc"
    return "tutorial"


async def enrich_single_section(section: dict) -> tuple[dict, list[dict]]:
    """
    Executes web searches for a single section's search queries and structures top resources.
    Uses fast direct curation with semantic type classification to eliminate extra LLM rate limits.
    """
    search_queries = section.get("search_queries", [])
    section_title = section.get("title", "")
    
    if not search_queries:
        topics_str = " ".join(section.get("topics", [])[:2])
        search_queries = [f"{section_title} {topics_str} tutorial documentation"]

    raw_search_results: List[dict] = []
    for query in search_queries[:2]:
        try:
            results = await search_resources_for_topics(query, max_results=3)
            if results and isinstance(results, list):
                raw_search_results.extend(results)
        except Exception:
            pass

    seen_urls = set()
    curated_resources: List[dict] = []
    for r in raw_search_results:
        url = r.get("href") or r.get("url", "")
        if url and url not in seen_urls:
            seen_urls.add(url)
            title = r.get("title", "Recommended Learning Resource")
            body = (r.get("body", "") or "").strip()
            res_type = _classify_resource_type(title, url)
            
            curated_resources.append({
                "title": title,
                "url": url,
                "type": res_type,
                "description": body[:140] if body else f"Curated {res_type} for mastering {section_title}."
            })
            if len(curated_resources) >= 3:
                break

    enriched_section = dict(section)
    enriched_section["resources"] = curated_resources
    return enriched_section, curated_resources


async def create_sections_data(state: Roadmap) -> Dict[str, Any]:
    """
    Enriches each section with curated resources discovered via web search.
    Returns partial state update with updated sections and aggregated resources list.
    """
    sections = state.sections or []
    if not sections:
        return {"sections": [], "resources": []}

    try:
        tasks = [enrich_single_section(sec) for sec in sections]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        enriched_sections: List[dict] = []
        all_curated_resources: List[dict] = []

        for i, res in enumerate(results):
            if isinstance(res, Exception):
                fallback_sec = dict(sections[i])
                fallback_sec["resources"] = []
                enriched_sections.append(fallback_sec)
            else:
                sec, resources = res
                enriched_sections.append(sec)
                all_curated_resources.extend(resources)

        return {
            "sections": enriched_sections,
            "resources": all_curated_resources
        }
    except Exception as e:
        return {
            "sections": sections,
            "resources": [],
            "errors": [f"create_sections_data failed: {str(e)}"]
        }