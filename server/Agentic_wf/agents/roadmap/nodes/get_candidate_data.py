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

        # Fix 3 (Option B): read weak_topics directly from the specific triggering
        # session document in the correct collection ("interview_sessions"), scoped
        # to the session that caused this roadmap to be generated.
        # This replaces the broken scan of the non-existent "sessions" collection.
        db = get_async_db()
        session_weak: list = []
        session_doc = None
        if state.session_id:
            try:
                session_doc = await db["interview_sessions"].find_one(
                    {"uuid": state.session_id},
                    {"weak_topics": 1, "summary": 1, "turns": 1},
                )
                if session_doc:
                    session_weak = session_doc.get("weak_topics", []) or []
                    # Fallback: if session weak_topics is empty, extract topics with score < 7.0 from turns
                    if not session_weak and session_doc.get("turns"):
                        session_weak = list({
                            t.get("topic") for t in session_doc["turns"]
                            if t.get("score") is not None and t["score"] < 7.0 and t.get("topic")
                        })
            except Exception:
                pass

        if profile:
            weak_topics = profile.get("weak_topics", []) or []
            strengths = profile.get("strengths", []) or []
            target_role = state.target_role or profile.get("target_role")

            # Merge weak topics from the triggering session (Fix 3 Option B)
            for wt in session_weak:
                if wt not in weak_topics:
                    weak_topics.append(wt)

            # Determine if we have specific weaknesses or need universal
            is_universal = len(weak_topics) == 0

            updates["performance_data"] = [session_doc] if session_doc else []
            updates["weak_topics"] = weak_topics
            updates["strengths"] = strengths
            updates["is_universal"] = is_universal
            if target_role and not state.target_role:
                updates["target_role"] = target_role
        else:
            # No candidate profile yet — still try to use session weak topics
            is_universal = len(session_weak) == 0
            updates["weak_topics"] = session_weak
            updates["is_universal"] = is_universal

    except Exception as e:
        updates["errors"] = [f"Failed to fetch candidate data: {str(e)}"]
        updates["is_universal"] = True

    return updates
