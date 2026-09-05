from langchain_core.prompts import ChatPromptTemplate

section_enrichment = ChatPromptTemplate([
    ('system',"""You are an expert Technical Content Curator.
Given a roadmap section and live web search results, curate the top resources and practical guides for the learner.
Select up to 3 high-quality resources (Official Docs, reputable tutorials, GitHub repositories, free courses, or interactive practice).

Return ONLY a valid JSON object with the following schema:
{{
  "resources": [
    {{
      "title": "Resource title",
      "url": "URL if present in search result or trusted domain",
      "type": "doc" | "video" | "tutorial" | "course" | "practice" | "github",
      "description": "Brief explanation of why this resource is recommended"
    }}
  ]
}}"""),
    ('human', 'Section Title: {section_title}\nTopics: {topics}\nLearning Objectives: {learning_objectives}\nWeb Search Results: {search_results}\n\nCurate up to 3 best resources from the search results for this section. Return JSON only.')
])


def section_enrichment_prompt(
    section: dict,
    search_results: list[dict]
):
    # Summarize search results concisely to stay well within token limits
    compact_results = [
        {
            "title": r.get("title", ""),
            "url": r.get("href") or r.get("url", ""),
            "snippet": r.get("body", "")[:120]
        }
        for r in search_results[:4]
    ]
    return section_enrichment.format(
        section_title=section.get('title', ''),
        topics=str(section.get('topics', [])[:4]),
        learning_objectives=str(section.get('learning_objectives', [])[:2]),
        search_results=str(compact_results)
    )