from Agentic_wf.agents.generate_questions.states import SessionState
from datetime import datetime

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
            },
            "open_ended": {
                "total": len(open_ended_questions),
                "correct": open_ended_correct,
            }
        },
        "difficulty_wise": difficulty_performance,
        "topic_wise": topic_performance
    }