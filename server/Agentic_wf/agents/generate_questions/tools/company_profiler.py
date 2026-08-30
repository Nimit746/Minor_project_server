import json
from typing import Dict, Any
from Agentic_wf.config.llm import LLM

# Well-known company profiles for fast fallback
KNOWN_COMPANY_PATTERNS: Dict[str, Dict[str, Any]] = {
    "google": {
        "focus_areas": ["Data structures and algorithms", "Graph algorithms", "Dynamic programming", "System design principles", "Distributed systems"],
        "question_style": "Algorithmic rigor, clean edge case handling, scalability",
        "difficulty_bias": "hard"
    },
    "amazon": {
        "focus_areas": ["Object-oriented design", "Data structures and algorithms", "Scalable APIs", "System design principles", "Database design"],
        "question_style": "Customer-focused trade-offs, concurrency, high availability",
        "difficulty_bias": "medium"
    },
    "meta": {
        "focus_areas": ["Data structures and algorithms", "Tree/Graph traversal", "API development", "System design principles", "Caching"],
        "question_style": "Speed of implementation, optimization, practical engineering",
        "difficulty_bias": "hard"
    },
    "microsoft": {
        "focus_areas": ["Data structures and algorithms", "API development", "Database design", "System design principles", "Testing & Debugging"],
        "question_style": "Clean code, maintainability, architectural design",
        "difficulty_bias": "medium"
    },
    "apple": {
        "focus_areas": ["Data structures and algorithms", "Memory management", "Operating system internals", "Low level design", "API development"],
        "question_style": "Performance optimization, hardware-software synergy",
        "difficulty_bias": "hard"
    },
    "netflix": {
        "focus_areas": ["System design principles", "Distributed systems", "Microservices", "Cloud computing", "Database design"],
        "question_style": "Resilience, high throughput, real-time telemetry",
        "difficulty_bias": "hard"
    }
}

COMPANY_PROFILING_PROMPT = """You are a technical recruiting expert.
For the company "{company_name}" and target role "{target_role}", describe the technical interview focus areas and pattern.

Return ONLY a valid JSON object matching:
{
  "focus_areas": ["topic1", "topic2", "topic3", "topic4"],
  "question_style": "description of interview flavor (e.g. heavy on system design, microservices, DSA, API design)",
  "difficulty_bias": "easy | medium | hard"
}
"""


async def get_company_profile(company_name: str, target_role: str = "Software Engineer") -> Dict[str, Any]:
    """Get technical focus areas and interview style for a target company."""
    if not company_name:
        return {
            "focus_areas": ["Data structures and algorithms", "System design principles", "Database design", "API development"],
            "question_style": "General industry standard technical interview",
            "difficulty_bias": "medium"
        }

    key = company_name.strip().lower()
    if key in KNOWN_COMPANY_PATTERNS:
        return KNOWN_COMPANY_PATTERNS[key]

    try:
        llm = LLM.get_llm("groq", temp=0.2)
        messages = [
            {"role": "user", "content": COMPANY_PROFILING_PROMPT.format(company_name=company_name, target_role=target_role)}
        ]
        response = await llm.ainvoke(messages)
        content = response.content.strip()

        if content.startswith("```json"):
            content = content[7:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()

        parsed = json.loads(content)
        return parsed
    except Exception:
        return {
            "focus_areas": ["Data structures and algorithms", "System design principles", "API development", "Database design"],
            "question_style": f"Standard technical questions for {company_name}",
            "difficulty_bias": "medium"
        }
