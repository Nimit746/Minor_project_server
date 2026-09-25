from Agentic_wf.agents.generate_questions.states.schemas import SessionState
from Agentic_wf.config.database import get_async_db
from datetime import datetime
import json

# Map 1-5 difficulty scale to string representation - must match generate_question.py
DIFFICULTY_MAP = {
    1: "easy",
    2: "easy",
    3: "medium",
    4: "hard",
    5: "expert"
}

def recompute_weak_topics(existing_weak_topics: list, concept_gaps: list) -> list:
    """
    Recompute weak topics by combining existing weak topics with new concept gaps from the session.
    Deduplicates and maintains a sorted list of unique weak topics.
    """
    combined = list(set((existing_weak_topics or []) + (concept_gaps or [])))
    return sorted(combined)

def calculate_detailed_metrics(state: SessionState) -> dict:
    """
    Calculate detailed metrics for consolidated mock test results.
    Includes breakdown by question type, difficulty level, and topic performance.
    """
    # Calculate type-wise performance
    mcq_questions = [q for q in state.question_history if q.question_type == "mcq"]
    open_ended_questions = [q for q in state.question_history if q.question_type == "open_ended"]
    
    # Calculate correct answers with proper boundary checks to avoid index errors
    mcq_correct = 0
    open_ended_correct = 0
    
    # Iterate through both histories in sync to avoid indexing issues
    for q, is_correct in zip(state.question_history, state.answer_correctness_history):
        if q.question_type == "mcq" and is_correct:
            mcq_correct += 1
        elif q.question_type == "open_ended" and is_correct:
            open_ended_correct += 1
    
    # Calculate difficulty-wise performance
    difficulty_performance = {
        "easy": {"total": 0, "correct": 0},
        "medium": {"total": 0, "correct": 0},
        "hard": {"total": 0, "correct": 0},
        "expert": {"total": 0, "correct": 0}
    }
    
    # Calculate difficulty-wise performance with safe iteration
    for q, is_correct in zip(state.question_history, state.answer_correctness_history):
        if q.difficulty in difficulty_performance:
            difficulty_performance[q.difficulty]["total"] += 1
            if is_correct:
                difficulty_performance[q.difficulty]["correct"] += 1
    
    # For any remaining questions in question_history that don't have a matching answer
    # (in case histories are out of sync), still count them in total but not correct
    remaining_questions = len(state.question_history) - len(state.answer_correctness_history)
    if remaining_questions > 0:
        for q in state.question_history[-remaining_questions:]:
            if q.difficulty in difficulty_performance:
                difficulty_performance[q.difficulty]["total"] += 1
    
    # Calculate topic-wise performance
    topic_performance = {}
    # Calculate topic-wise performance with safe iteration
    for q, is_correct in zip(state.question_history, state.answer_correctness_history):
        if q.topic not in topic_performance:
            topic_performance[q.topic] = {"total": 0, "correct": 0}
        topic_performance[q.topic]["total"] += 1
        if is_correct:
            topic_performance[q.topic]["correct"] += 1
    
    # Add remaining questions without answers to topic totals
    if remaining_questions > 0:
        for q in state.question_history[-remaining_questions:]:
            if q.topic not in topic_performance:
                topic_performance[q.topic] = {"total": 0, "correct": 0}
            topic_performance[q.topic]["total"] += 1
    
    # Calculate overall pass/fail status and percentile estimate
    overall_score = state.score_running / state.questions_asked if state.questions_asked > 0 else 0.0
    passed = overall_score >= 0.7  # 70% passing threshold
    
    return {
        "overall": {
            "total_questions": state.questions_asked,
            "mcq_total": len(mcq_questions),
            "open_ended_total": len(open_ended_questions),
            "total_correct": state.score_running,
            "overall_score": overall_score,
            "passed": passed,
            "completion_timestamp": datetime.utcnow().isoformat()
        },
        "type_wise": {
            "mcq": {
                "total": len(mcq_questions),
                "correct": mcq_correct,
                "accuracy": mcq_correct / len(mcq_questions) if len(mcq_questions) > 0 else 0
            },
            "open_ended": {
                "total": len(open_ended_questions),
                "correct": open_ended_correct,
                "accuracy": open_ended_correct / len(open_ended_questions) if len(open_ended_questions) > 0 else 0
            }
        },
        "difficulty_wise": difficulty_performance,
        "topic_wise": topic_performance,
        "answer_correctness_history": state.answer_correctness_history,
        "concept_gaps_identified": state.concept_gaps
    }

async def finalize_session(state: SessionState) -> SessionState:
    """
    Final node in the workflow to persist session results and update candidate metrics in MongoDB.
    Enhanced to save consolidated mock test results as per requirements.
    """
    # 1. Calculate current session score and detailed metrics
    if state.questions_asked > 0:
        current_session_score = state.score_running / state.questions_asked
    else:
        current_session_score = 0.0

    # Calculate consolidated detailed metrics for the mock test
    consolidated_metrics = calculate_detailed_metrics(state)
    state.final_session_score = current_session_score
    state.consolidated_metrics = consolidated_metrics

    if not state.candidate_id:
        return state

    try:
        db = get_async_db()
        candidates_collection = db.candidates
        sessions_collection = db.sessions
        mock_tests_collection = db.mock_test_results  # New collection specifically for consolidated mock test results

        # Fetch existing candidate record
        candidate = await candidates_collection.find_one({"candidate_id": state.candidate_id})

        historical_avg = candidate.get("historical_avg_score", 0.0) if candidate else 0.0
        sessions_completed = candidate.get("sessions_completed", 0) if candidate else 0
        existing_weak_topics = candidate.get("weak_topics", []) if candidate else []
        
        # Get all previous mock test results to build truly consolidated data
        previous_mock_tests = await mock_tests_collection.find(
            {"candidate_id": state.candidate_id}
        ).to_list(length=None)

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
                    "target_role": state.target_role,
                    "last_mock_test_date": datetime.utcnow(),
                    "all_time_best_score": max(candidate.get("all_time_best_score", 0), current_session_score) if candidate else current_session_score
                }
            },
            upsert=True
        )

        # Log detailed session breakdown in sessions collection (existing functionality)
        await sessions_collection.insert_one({
            "candidate_id": state.candidate_id,
            "company_name": state.company_name,
            "target_role": state.target_role,
            "score": current_session_score,
            "questions_asked": state.questions_asked,
            "score_running": state.score_running,
            "concept_gaps": state.concept_gaps,
            "question_history": [q.model_dump() for q in state.question_history],
            "answer_history": state.answer_history,
            "created_at": datetime.utcnow()
        })

        # Save CONSOLIDATED mock test results as required - this is the enhanced functionality
        # This stores all consolidated metrics in a dedicated collection for easy reporting
        await mock_tests_collection.insert_one({
            "candidate_id": state.candidate_id,
            "mock_test_id": f"mock_test_{state.candidate_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            "company_name": state.company_name,
            "target_role": state.target_role,
            "test_date": datetime.utcnow(),
            "total_questions": 30,  # We now always generate 30 questions per requirements
            "consolidated_metrics": consolidated_metrics,
            "comprehensive_breakdown": {
                "all_questions": [q.model_dump() for q in state.question_history],
                "all_answers": state.answer_history,
                "answer_correctness": state.answer_correctness_history,
                "difficulty_progression": [DIFFICULTY_MAP.get(d, "medium") for d in state.difficulty_history] if hasattr(state, 'difficulty_history') else []
            },
            # Calculate improvement over previous tests
            "improvement_from_previous": current_session_score - historical_avg if previous_mock_tests else 0,
            "rankable_score": new_avg  # Weighted average for candidate ranking
        })

        state.updated_historical_avg = new_avg
        return state

    except Exception as e:
        print(f"Error in finalize_session: {e}")
        return state