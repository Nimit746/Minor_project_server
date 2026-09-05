from typing import Any, Dict
from Agentic_wf.agents.roadmap.states import Roadmap
from Agentic_wf.config import get_async_db
from Agentic_wf.tools import fetch_candidate_profile


async def get_candidate_data(state: Roadmap) -> Dict[str, Any]:
    """
    Retrieves the candidate's data from MongoDB (candidate profile and session history).
    If no candidate data or weak areas are found, flags state for universal roadmap generation.
    Returns partial state update dictionary.
    """
    candidate_id = state.candidate_id
    updates: Dict[str, Any] = {
        "performance_data": [],
        "weak_topics": [],
        "strengths": [],
        "is_universal": True
    }

    if not candidate_id:
        return updates

    try:
        # Fetch candidate profile
        profile = await fetch_candidate_profile(candidate_id)
        
        # Fetch session history if available
        sessions = []
        try:
            db = get_async_db()
            cursor = db.sessions.find({"candidate_id": candidate_id}).sort("timestamp", -1).limit(10)
            sessions = await cursor.to_list(length=10)
        except Exception:
            pass

        if profile:
            weak_topics = profile.get("weak_topics", []) or []
            strengths = profile.get("strengths", []) or []
            target_role = state.target_role or profile.get("target_role")
            
            # Check for concept gaps or weak areas from session history
            for s in sessions:
                if "weak_topics" in s and isinstance(s["weak_topics"], list):
                    for wt in s["weak_topics"]:
                        if wt not in weak_topics:
                            weak_topics.append(wt)
                if "concept_gaps" in s and isinstance(s["concept_gaps"], list):
                    for cg in s["concept_gaps"]:
                        if cg not in weak_topics:
                            weak_topics.append(cg)

            # Determine if we have specific weaknesses or need universal
            is_universal = len(weak_topics) == 0

            updates["performance_data"] = sessions
            updates["weak_topics"] = weak_topics
            updates["strengths"] = strengths
            updates["is_universal"] = is_universal
            if target_role and not state.target_role:
                updates["target_role"] = target_role
        else:
            updates["is_universal"] = True

    except Exception as e:
        updates["errors"] = [f"Failed to fetch candidate data: {str(e)}"]
        updates["is_universal"] = True

    return updates
