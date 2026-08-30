import json

TOPIC_ANALYSIS_SYSTEM_PROMPT = """You are an expert Technical Curriculum Architect and Career Mentor.
Your task is to analyze the candidate's target role, target domain, background performance, and pain points/weak topics, or create a universal curriculum if candidate data is absent.

Guidelines:
1. If the candidate has weak topics or pain points, you MUST prioritize and emphasize these areas with dedicated remediation strategies, higher time allocation, and foundational drills before advanced concepts.
2. If this is a universal roadmap (no prior candidate weakness data), provide a comprehensive, industry-standard mastery curriculum from foundational concepts to advanced production architectures.
3. Organize prioritized topics logically with category, priority (High/Medium/Low), estimated hours, and reasoning.

Return ONLY a valid JSON object with the following schema:
{
  "is_universal": boolean,
  "learning_profile": {
    "summary": "Brief summary of candidate profile or universal domain path",
    "focus_areas": ["List of primary focus areas"],
    "total_estimated_weeks": number,
    "strategy": "Remediation-first OR Standard Mastery"
  },
  "prioritized_topics": [
    {
      "topic_name": "Name of topic",
      "priority": "High" | "Medium" | "Low",
      "is_weak_point": boolean,
      "estimated_hours": number,
      "learning_goal": "What the learner should achieve",
      "key_concepts": ["concept 1", "concept 2"]
    }
  ]
}
"""

def build_topic_analysis_prompt(
    target_role: str,
    available_hours_per_day: float,
    target_date: str | None,
    weak_topics: list[str],
    strengths: list[str],
    performance_data: list[dict],
    is_universal: bool
) -> str:
    return f"""Target Role / Domain: {target_role}
Daily Available Hours: {available_hours_per_day} hours/day
Target Completion Date: {target_date or 'Flexible'}
Universal Mode: {is_universal}
Identified Weak Topics / Pain Points: {json.dumps(weak_topics)}
Identified Strengths: {json.dumps(strengths)}
Candidate Session/Performance History: {json.dumps(performance_data)}

Analyze the requirements and generate the structured prioritized topics and learning profile in JSON."""


SECTION_CREATION_SYSTEM_PROMPT = """You are an expert Learning Path Designer.
Your task is to organize prioritized learning topics into chronological milestones/phases (sections) for the candidate's roadmap.

Guidelines:
1. Divide the roadmap into 3 to 6 structured sections/phases (e.g., Phase 1: Core Remediation, Phase 2: Core Domain Fundamentals, Phase 3: Advanced Architectures & Hands-on Projects, Phase 4: Interview & Practical Readiness).
2. If weak topics exist, ensure the initial phases directly remediate them with practical hands-on checkpoints.
3. For each section, provide specific web search queries (2-4 queries) that will be used to discover the best modern resources, documentation, interactive tutorials, and practice problems on the internet.

Return ONLY a valid JSON object with the following schema:
{
  "sections": [
    {
      "section_id": "section_1",
      "title": "Section Title",
      "phase": "Phase 1: Foundations & Weak Point Remediation",
      "focus_type": "weak_point_remediation" | "core_domain",
      "estimated_hours": number,
      "topics": ["Topic 1", "Topic 2"],
      "learning_objectives": ["Objective 1", "Objective 2"],
      "search_queries": ["specific search query 1", "specific search query 2"],
      "practical_exercises": ["Hands-on exercise / mini-project 1"]
    }
  ]
}
"""

def build_section_creation_prompt(
    target_role: str,
    learning_profile: dict,
    prioritized_topics: list[dict],
    available_hours_per_day: float
) -> str:
    return f"""Target Role / Domain: {target_role}
Daily Commitment: {available_hours_per_day} hours/day
Learning Profile: {json.dumps(learning_profile)}
Prioritized Topics: {json.dumps(prioritized_topics)}

Organize these topics into structured, chronological learning path sections with targeted web search queries. Return JSON only."""


SECTION_ENRICHMENT_SYSTEM_PROMPT = """You are an expert Technical Content Curator.
Given a roadmap section and live web search results, curate the top resources and practical guides for the learner.
Select high-quality resources (Official Docs, reputable tutorials, GitHub repositories, free courses, or interactive practice).

Return ONLY a valid JSON object with the following schema:
{
  "resources": [
    {
      "title": "Resource title",
      "url": "URL if present in search result or trusted domain",
      "type": "doc" | "video" | "tutorial" | "course" | "practice" | "github",
      "description": "Why this resource is recommended"
    }
  ]
}
"""

def build_section_enrichment_prompt(
    section: dict,
    search_results: list[dict]
) -> str:
    return f"""Section Title: {section.get('title')}
Topics: {json.dumps(section.get('topics', []))}
Learning Objectives: {json.dumps(section.get('learning_objectives', []))}
Live Web Search Results: {json.dumps(search_results)}

Curate the best resources from the search results for this section. Return JSON only."""
