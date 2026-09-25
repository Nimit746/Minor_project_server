from langchain_core.prompts import ChatPromptTemplate

section_creation = ChatPromptTemplate([
    ('system',"""You are an expert Learning Path Designer.
Your task is to organize prioritized learning topics into chronological milestones/phases (sections) for the candidate's roadmap.

Guidelines:
1. Divide the roadmap into 3 to 5 structured sections/phases (e.g., Phase 1: Foundations & Remediation, Phase 2: Core Architecture & Hands-on, Phase 3: Advanced Systems & Production Readiness).
2. If weak topics exist, ensure initial phases directly remediate them with practical hands-on checkpoints and set focus_type="weak_point_remediation" and focus_tag="Remediation Focus".
3. For each section, provide:
   - 2 to 4 interactive, concrete checkpoints that the learner can mark as completed in the UI.
   - 1 to 2 focused web search queries for documentation and interactive tutorials.
   - Realistic estimated hours.

Return ONLY a valid JSON object with the following schema:
{{
  "sections": [
    {{
      "section_id": "section_1",
      "title": "Section Title",
      "phase": "Phase 1: Foundations & Weak Point Remediation",
      "focus_type": "weak_point_remediation" | "core_domain",
      "focus_tag": "Remediation Focus" | "Core Mastery" | "Advanced Architecture",
      "estimated_hours": number,
      "topics": ["Topic 1", "Topic 2"],
      "learning_objectives": ["Objective 1", "Objective 2"],
      "checkpoints": [
        {{
          "checkpoint_id": "chk_1_1",
          "task": "Concrete, actionable task or drill to complete",
          "is_completed": false,
          "estimated_minutes": 45
        }}
      ],
      "search_queries": ["concise search query 1", "concise search query 2"],
      "practical_exercises": ["Hands-on mini-project / code exercise"]
    }}
  ]
}}"""),
    ('human', 'Target Role / Domain: {target_role}\nDaily Commitment: {available_hours_per_day} hours/day\nLearning Profile: {learning_profile}\nPrioritized Topics: {prioritized_topics}\n\nOrganize these topics into structured, chronological learning path sections with actionable interactive checkpoints. Return JSON only.')
])


def section_creation_prompt(
    target_role: str,
    learning_profile: dict,
    prioritized_topics: list[dict],
    available_hours_per_day: float
):
    return section_creation.format(
        target_role=target_role,
        available_hours_per_day=available_hours_per_day,
        learning_profile=str(learning_profile),
        prioritized_topics=str(prioritized_topics)
    )