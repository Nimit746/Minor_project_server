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
