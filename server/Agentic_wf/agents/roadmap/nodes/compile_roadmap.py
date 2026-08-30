from typing import Any, Dict
from datetime import datetime
from Agentic_wf.agents.roadmap.states import Roadmap
from Agentic_wf.config.database import get_async_db


async def compile_roadmap(state: Roadmap) -> Dict[str, Any]:
    """
    Compiles the final cohesive roadmap JSON structure including metadata,
    learning profile, sections, curated resources, and action plan.
    Saves the final roadmap to MongoDB (roadmaps collection / candidate profile).
    Returns partial state update dictionary.
    """
    target_role = state.target_role or "Software Engineer"
    candidate_id = state.candidate_id or "anonymous"
    available_hours = state.available_hours_per_day or 2.0
    sections = state.sections or []
    learning_profile = state.learning_profile or {}
    prioritized_topics = state.prioritized_topics or []
    is_universal = state.is_universal
    weak_topics = state.weak_topics or []

    # Calculate estimated total duration
    total_hours = sum(s.get("estimated_hours", 10.0) for s in sections)
    estimated_days = round(total_hours / available_hours) if available_hours > 0 else 30
    estimated_weeks = max(1, round(estimated_days / 7))

    final_roadmap_data = {
        "candidate_id": candidate_id,
        "target_role": target_role,
        "is_universal": is_universal,
        "created_at": datetime.utcnow().isoformat(),
        "timeline": {
            "available_hours_per_day": available_hours,
            "target_date": state.target_date,
            "total_estimated_hours": total_hours,
            "total_estimated_days": estimated_days,
            "total_estimated_weeks": estimated_weeks,
        },
        "learning_profile": learning_profile,
        "weak_points_targeted": weak_topics,
        "prioritized_topics": prioritized_topics,
        "sections": sections,
        "action_plan": [
            f"Dedicate {available_hours} hours/day consistently.",
            "Complete practical mini-projects and exercises after each section.",
            "Review weak-point remediation checkpoints before advancing." if weak_topics else "Build end-to-end milestone projects for your portfolio."
        ]
    }

    # Attempt to persist in MongoDB
    try:
        db = get_async_db()
        await db.roadmaps.update_one(
            {"candidate_id": candidate_id, "target_role": target_role},
            {"$set": final_roadmap_data},
            upsert=True
        )
        if candidate_id and candidate_id != "anonymous":
            await db.candidates.update_one(
                {"candidate_id": candidate_id},
                {"$set": {"latest_roadmap_id": f"{candidate_id}_{target_role}", "latest_roadmap_role": target_role}},
                upsert=True
            )
    except Exception:
        pass

    return {
        "roadmap": final_roadmap_data
    }
