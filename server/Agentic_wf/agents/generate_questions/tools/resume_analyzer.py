import re
import json
from typing import List, Dict, Any
from Agentic_wf.config.llm import LLM

RESUME_EXTRACTION_PROMPT = """You are a technical resume parser and evaluator.
Analyze the following resume text and extract key technical attributes.

Return ONLY a valid JSON object with the following schema:
{
  "skills": ["skill1", "skill2", "skill3"],
  "primary_language": "Python | Java | C++ | JavaScript | Go | etc",
  "experience_level": "entry | mid | senior",
  "project_domains": ["e.g. Web Development", "Machine Learning", "Distributed Systems"],
  "recommended_topics": ["topic1", "topic2", "topic3", "topic4"]
}

Resume Text:
{resume_text}
"""


def extract_skills_heuristic(resume_text: str) -> List[str]:
    """Fallback keyword matching for common programming languages and tools."""
    common_skills = [
        "python", "javascript", "typescript", "java", "c++", "c#", "golang", "rust",
        "react", "node.js", "fastapi", "django", "flask", "docker", "kubernetes",
        "aws", "gcp", "azure", "mongodb", "postgresql", "mysql", "redis",
        "data structures", "algorithms", "system design", "machine learning", "deep learning",
        "rest api", "graphql", "microservices", "sql", "git"
    ]
    text_lower = resume_text.lower()
    found = [s.title() for s in common_skills if re.search(r'\b' + re.escape(s) + r'\b', text_lower)]
    return found


async def analyze_resume(resume_text: str) -> Dict[str, Any]:
    """Extract candidate skills, experience level, and recommended interview topics from resume."""
    if not resume_text or len(resume_text.strip()) < 20:
        return {
            "skills": ["Python", "Data Structures", "Algorithms"],
            "primary_language": "Python",
            "experience_level": "entry",
            "project_domains": ["General Software Engineering"],
            "recommended_topics": ["Python programming basics", "Data structures and algorithms"]
        }

    try:
        llm = LLM.get_llm("groq", temp=0.1)
        messages = [
            {"role": "user", "content": RESUME_EXTRACTION_PROMPT.format(resume_text=resume_text[:3000])}
        ]
        response = await llm.ainvoke(messages)
        content = response.content.strip()

        # Extract JSON substring if surrounded by markdown or explanatory text
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            content = json_match.group(0)

        parsed = json.loads(content)
        return parsed
    except Exception:
        skills = extract_skills_heuristic(resume_text)
        return {
            "skills": skills or ["Python", "Data Structures"],
            "primary_language": "Python",
            "experience_level": "entry",
            "project_domains": ["Software Development"],
            "recommended_topics": skills[:4] if skills else ["Python programming basics", "Data structures and algorithms"]
        }
