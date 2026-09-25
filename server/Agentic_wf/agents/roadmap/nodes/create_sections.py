from typing import Any, Dict
from Agentic_wf.agents.roadmap.states import Roadmap
from Agentic_wf.config import LLM
from Agentic_wf.agents.roadmap.prompts import (
    section_creation,
    section_creation_prompt,
)
from Agentic_wf.agents.roadmap.utils import parse_json_safely


async def create_sections(state: Roadmap) -> Dict[str, Any]:
    """
    Organizes prioritized topics into structured chronological roadmap sections/phases.
    Generates targeted search queries and interactive checkpoints for each section.
    Returns partial state update dictionary.
    """
    target_role = state.target_role or "Software Engineer"
    learning_profile = state.learning_profile or {}
    prioritized_topics = state.prioritized_topics or []
    available_hours = state.available_hours_per_day or 2.0

    prompt = section_creation_prompt(
        target_role=target_role,
        learning_profile=learning_profile,
        prioritized_topics=prioritized_topics,
        available_hours_per_day=available_hours,
    )

    messages = section_creation.format_messages(
        target_role=target_role,
        available_hours_per_day=available_hours,
        learning_profile=str(learning_profile),
        prioritized_topics=str(prioritized_topics)
    )

    try:
        llm = LLM.get_llm("groq")
        response = await llm.ainvoke(messages)
        parsed = parse_json_safely(response.content, default={})

        sections = parsed.get("sections", [])
        for sec in sections:
            if "checkpoints" not in sec:
                sec["checkpoints"] = [
                    {"checkpoint_id": f"{sec.get('section_id', 'sec')}_1", "task": f"Complete foundational study on {sec.get('title')}", "is_completed": False, "estimated_minutes": 60}
                ]
            if "focus_tag" not in sec:
                sec["focus_tag"] = "Remediation Focus" if sec.get("focus_type") == "weak_point_remediation" else "Core Mastery"

        return {
            "sections": sections
        }
    except Exception as e:
        fallback_sections = [
            {
                "section_id": "section_1",
                "title": "Phase 1: Remediation & Foundations",
                "phase": "Phase 1",
                "focus_type": "weak_point_remediation" if state.weak_topics else "core_domain",
                "focus_tag": "Remediation Focus" if state.weak_topics else "Core Mastery",
                "estimated_hours": 15.0,
                "topics": [t.get("topic_name", "") for t in prioritized_topics[:2]],
                "learning_objectives": [f"Understand core principles of {target_role}"],
                "checkpoints": [
                    {"checkpoint_id": "chk_1_1", "task": f"Review fundamentals of {target_role}", "is_completed": False, "estimated_minutes": 45},
                    {"checkpoint_id": "chk_1_2", "task": "Implement practice drills for identified weak points", "is_completed": False, "estimated_minutes": 60}
                ],
                "search_queries": [f"{target_role} roadmap tutorial documentation", f"{target_role} best practices"],
                "practical_exercises": ["Build a small baseline project implementing core concepts"]
            },
            {
                "section_id": "section_2",
                "title": "Phase 2: Advanced Topics & Hands-on Projects",
                "phase": "Phase 2",
                "focus_type": "core_domain",
                "focus_tag": "Advanced Architecture",
                "estimated_hours": 20.0,
                "topics": [t.get("topic_name", "") for t in prioritized_topics[2:]] or [f"Advanced {target_role}"],
                "learning_objectives": [f"Master production-grade architectures for {target_role}"],
                "checkpoints": [
                    {"checkpoint_id": "chk_2_1", "task": f"Design system architecture for {target_role} project", "is_completed": False, "estimated_minutes": 90},
                    {"checkpoint_id": "chk_2_2", "task": "Deploy project to cloud environment", "is_completed": False, "estimated_minutes": 120}
                ],
                "search_queries": [f"Advanced {target_role} project tutorials", f"{target_role} interview questions"],
                "practical_exercises": ["Design and build an end-to-end portfolio project"]
            }
        ]
        return {
            "sections": fallback_sections,
            "errors": [f"create_sections fallback used: {str(e)}"]
        }