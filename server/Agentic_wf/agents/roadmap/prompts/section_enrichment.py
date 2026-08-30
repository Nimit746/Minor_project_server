import json

SECTION_ENRICHMENT_SYSTEM_PROMPT = """You are an expert Technical Content Curator.
Given a roadmap section and live web search results, curate the top resources and practical guides for the learner.
Select up to 3 high-quality resources (Official Docs, reputable tutorials, GitHub repositories, free courses, or interactive practice).

Return ONLY a valid JSON object with the following schema:
{
  "resources": [
    {
      "title": "Resource title",
      "url": "URL if present in search result or trusted domain",
      "type": "doc" | "video" | "tutorial" | "course" | "practice" | "github",
      "description": "Brief explanation of why this resource is recommended"
    }
  ]
}
"""

def build_section_enrichment_prompt(
    section: dict,
    search_results: list[dict]
) -> str:
    # Summarize search results concisely to stay well within token limits
    compact_results = [
        {
            "title": r.get("title", ""),
            "url": r.get("href") or r.get("url", ""),
            "snippet": r.get("body", "")[:120]
        }
        for r in search_results[:4]
    ]
    return f"""Section Title: {section.get('title')}
Topics: {json.dumps(section.get('topics', [])[:4])}
Learning Objectives: {json.dumps(section.get('learning_objectives', [])[:2])}
Web Search Results: {json.dumps(compact_results)}

Curate up to 3 best resources from the search results for this section. Return JSON only."""
