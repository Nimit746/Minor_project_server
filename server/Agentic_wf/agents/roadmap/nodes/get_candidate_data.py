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
    weak_topics = list(state.weak_topics or [])
    strengths = list(state.strengths or [])
    performance_data = list(state.performance_data or [])
    is_universal = state.is_universal

    updates: Dict[str, Any] = {
        "performance_data": performance_data,
        "weak_topics": weak_topics,
        "strengths": strengths,
        "is_universal": is_universal
    }

    if not candidate_id:
        return updates

    try:
        # Fetch candidate profile if available
        profile = await fetch_candidate_profile(candidate_id)

        session_weak: list = []
        session_doc = performance_data[0] if performance_data else None

        if not session_doc and state.session_id:
            try:
                db = get_async_db()
                session_doc = await db["interview_sessions"].find_one(
                    {"uuid": state.session_id},
                    {"weak_topics": 1, "summary": 1, "turns": 1},
                )
            except Exception:
                pass

        if session_doc:
            session_weak = list(session_doc.get("weak_topics", []) or [])
            if not session_weak and session_doc.get("turns"):
                session_weak = list({
                    t.get("topic") for t in session_doc["turns"]
                    if t.get("score") is not None and t["score"] < 7.0 and t.get("topic")
                })

        for wt in session_weak:
            if wt not in weak_topics:
                weak_topics.append(wt)

        if profile:
            for p_wt in (profile.get("weak_topics", []) or []):
                if p_wt not in weak_topics:
                    weak_topics.append(p_wt)
            for p_str in (profile.get("strengths", []) or []):
                if p_str not in strengths:
                    strengths.append(p_str)
            target_role = state.target_role or profile.get("target_role")
            if target_role and not state.target_role:
                updates["target_role"] = target_role

        # If we have weak topics, it's never universal
        is_universal = len(weak_topics) == 0

        updates["performance_data"] = [session_doc] if session_doc else performance_data
        updates["weak_topics"] = weak_topics
        updates["strengths"] = strengths
        updates["is_universal"] = is_universal

    except Exception as e:
        updates["errors"] = [f"Failed to fetch candidate data: {str(e)}"]
        updates["is_universal"] = True

    return updates
