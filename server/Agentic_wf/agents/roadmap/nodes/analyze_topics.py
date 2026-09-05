from typing import Any, Dict, List
from Agentic_wf.agents.roadmap.states import Roadmap
from Agentic_wf.config import LLM
from Agentic_wf.agents.roadmap.prompts import (
    topic_analysis,
    topic_analysis_prompt,
)
from Agentic_wf.agents.roadmap.utils import parse_json_safely


async def analyze_topics(state: Roadmap) -> Dict[str, Any]:
    """
    Analyzes the target role, candidate background, and pain points/weak topics.
    Prioritizes topics needing urgent remediation vs core domain mastery.
    Returns partial state update dictionary.
    """
    target_role = state.target_role or "Software Engineer"
    available_hours = state.available_hours_per_day or 2.0
    target_date = state.target_date
    weak_topics = state.weak_topics or []
    strengths = state.strengths or []
    performance_data = state.performance_data or []
    is_universal = state.is_universal

    prompt = topic_analysis_prompt(
        target_role=target_role,
        available_hours_per_day=available_hours,
        target_date=target_date,
        weak_topics=weak_topics,
        strengths=strengths,
        performance_data=performance_data,
        is_universal=is_universal,
    )

    messages = topic_analysis.format_messages(
        target_role=target_role,
        available_hours_per_day=available_hours,
        target_date=target_date or 'Flexible',
        is_universal=is_universal,
        weak_topics=str(weak_topics),
        strengths=str(strengths),
        performance_data=str(performance_data)
    )

    try:
        llm = LLM.get_llm("groq")
        response = await llm.ainvoke(messages)
        parsed = parse_json_safely(response.content, default={})

        return {
            "learning_profile": parsed.get("learning_profile", {}),
            "prioritized_topics": parsed.get("prioritized_topics", []),
            "is_universal": parsed.get("is_universal", is_universal),
        }
    except Exception as e:
        fallback_profile = {
            "summary": f"Comprehensive roadmap for {target_role}",
            "focus_areas": weak_topics if weak_topics else [f"{target_role} Core Fundamentals"],
            "total_estimated_weeks": 8,
            "strategy": "Remediation-first" if weak_topics else "Standard Mastery",
        }
        fallback_topics = [
            {
                "topic_name": topic,
                "priority": "High",
                "is_weak_point": True,
                "estimated_hours": 10.0,
                "learning_goal": f"Master core concepts and solve gaps in {topic}",
                "key_concepts": [topic]
            }
            for topic in weak_topics
        ] or [
            {
                "topic_name": f"{target_role} Core Competencies",
                "priority": "High",
                "is_weak_point": False,
                "estimated_hours": 20.0,
                "learning_goal": f"Gain mastery of foundational skills for {target_role}",
                "key_concepts": ["Core Fundamentals", "Best Practices", "System Design"]
            }
        ]
        return {
            "learning_profile": fallback_profile,
            "prioritized_topics": fallback_topics,
            "errors": [f"analyze_topics fallback used: {str(e)}"]
        }