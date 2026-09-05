from langchain_core.prompts import ChatPromptTemplate

topic_analysis = ChatPromptTemplate([
    ('system',"""You are an expert Technical Curriculum Architect and Career Mentor.
Your task is to analyze the candidate's target role, target domain, background performance, and pain points/weak topics, or create a universal curriculum if candidate data is absent.

Guidelines:
1. If the candidate has weak topics or pain points, you MUST prioritize and emphasize these areas with dedicated remediation strategies, higher time allocation, and foundational drills before advanced concepts.
2. If this is a universal roadmap (no prior candidate weakness data), provide a comprehensive, industry-standard mastery curriculum from foundational concepts to advanced production architectures.
3. Organize prioritized topics logically with category, priority (High/Medium/Low), estimated hours, and reasoning.

Return ONLY a valid JSON object with the following schema:
{{
  "is_universal": boolean,
  "learning_profile": {{
    "summary": "Brief summary of candidate profile or universal domain path",
    "focus_areas": ["List of primary focus areas"],
    "total_estimated_weeks": number,
    "strategy": "Remediation-first OR Standard Mastery"
  }},
  "prioritized_topics": [
    {{
      "topic_name": "Name of topic",
      "priority": "High" | "Medium" | "Low",
      "is_weak_point": boolean,
      "estimated_hours": number,
      "learning_goal": "What the learner should achieve",
      "key_concepts": ["concept 1", "concept 2"]
    }}
  ]
}}"""),
    ('human', 'Target Role / Domain: {target_role}\nDaily Available Hours: {available_hours_per_day} hours/day\nTarget Completion Date: {target_date}\nUniversal Mode: {is_universal}\nIdentified Weak Topics / Pain Points: {weak_topics}\nIdentified Strengths: {strengths}\nCandidate Session/Performance History: {performance_data}\n\nAnalyze the requirements and generate the structured prioritized topics and learning profile in JSON.')
])


def topic_analysis_prompt(
    target_role: str,
    available_hours_per_day: float,
    target_date: str | None,
    weak_topics: list[str],
    strengths: list[str],
    performance_data: list[dict],
    is_universal: bool
):
    return topic_analysis.format(
        target_role=target_role,
        available_hours_per_day=available_hours_per_day,
        target_date=target_date or 'Flexible',
        is_universal=is_universal,
        weak_topics=str(weak_topics),
        strengths=str(strengths),
        performance_data=str(performance_data)
    )