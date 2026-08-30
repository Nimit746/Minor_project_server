from Agentic_wf.agents.generate_questions.states.schemas import SessionState
from Agentic_wf.config.database import get_async_db


def recompute_weak_topics(existing_weak_topics: list, concept_gaps: list) -> list:
    """
    Recompute weak topics by combining existing weak topics with new concept gaps from the session.
    Deduplicates and maintains a sorted list of unique weak topics.
    """
    combined = list(set((existing_weak_topics or []) + (concept_gaps or [])))
    return sorted(combined)


async def finalize_session(state: SessionState) -> SessionState:
    """
    Final node in the workflow to persist session results and update candidate metrics in MongoDB.
    """
    # 1. Calculate current session score
    if state.questions_asked > 0:
        current_session_score = state.score_running / state.questions_asked
    else:
        current_session_score = 0.0

    state.final_session_score = current_session_score

    if not state.candidate_id:
        return state

    try:
        db = get_async_db()
        candidates_collection = db.candidates
        sessions_collection = db.sessions

        # Fetch existing candidate record
        candidate = await candidates_collection.find_one({"candidate_id": state.candidate_id})

        historical_avg = candidate.get("historical_avg_score", 0.0) if candidate else 0.0
        sessions_completed = candidate.get("sessions_completed", 0) if candidate else 0
        existing_weak_topics = candidate.get("weak_topics", []) if candidate else []

        # Calculate new weighted average score (0.7 * current + 0.3 * historical)
        if sessions_completed > 0:
            new_avg = 0.7 * current_session_score + 0.3 * historical_avg
        else:
            new_avg = current_session_score

        new_weak_topics = recompute_weak_topics(existing_weak_topics, state.concept_gaps)
        new_sessions_count = sessions_completed + 1

        # Update candidate profile
        await candidates_collection.update_one(
            {"candidate_id": state.candidate_id},
            {
                "$set": {
                    "historical_avg_score": new_avg,
                    "weak_topics": new_weak_topics,
                    "sessions_completed": new_sessions_count,
                    "target_company": state.company_name,
                    "target_role": state.target_role
                }
            },
            upsert=True
        )

        # Log detailed session breakdown in sessions collection
        await sessions_collection.insert_one({
            "candidate_id": state.candidate_id,
            "company_name": state.company_name,
            "target_role": state.target_role,
            "score": current_session_score,
            "questions_asked": state.questions_asked,
            "score_running": state.score_running,
            "concept_gaps": state.concept_gaps,
            "question_history": [q.model_dump() for q in state.question_history],
            "answer_history": state.answer_history
        })

        state.updated_historical_avg = new_avg
        return state

    except Exception:
        return state