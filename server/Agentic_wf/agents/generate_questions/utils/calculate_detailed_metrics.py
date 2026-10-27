
from Agentic_wf.agents.generate_questions.states import SessionState
from datetime import datetime, timezone


def calculate_detailed_metrics(state: SessionState) -> dict:
    """
    Calculate consolidated mock interview metrics, including:
    - Overall performance
    - Question-type performance
    - Difficulty-wise performance
    - Topic-wise performance
    """

    questions = state.question_history
    answers = state.answer_correctness_history

    mcq_questions = [
        q for q in questions if q.question_type == "mcq"
    ]
    open_ended_questions = [
        q for q in questions if q.question_type == "open_ended"
    ]

    # Pair each question with its corresponding correctness result.
    paired_count = min(len(questions), len(answers))
    paired_results = zip(
        questions[:paired_count],
        answers[:paired_count],
    )

    mcq_correct = 0
    open_ended_correct = 0

    difficulty_performance = {
        "easy": {"total": 0, "correct": 0},
        "medium": {"total": 0, "correct": 0},
        "hard": {"total": 0, "correct": 0},
        "expert": {"total": 0, "correct": 0},
    }

    topic_performance = {}

    # Count every question, including unanswered questions.
    for index, question in enumerate(questions):
        has_answer = index < paired_count
        is_correct = bool(answers[index]) if has_answer else False

        if question.question_type == "mcq" and is_correct:
            mcq_correct += 1
        elif question.question_type == "open_ended" and is_correct:
            open_ended_correct += 1

        # Difficulty-wise metrics
        difficulty = question.difficulty
        if difficulty in difficulty_performance:
            difficulty_performance[difficulty]["total"] += 1
            if is_correct:
                difficulty_performance[difficulty]["correct"] += 1

        # Topic-wise metrics
        topic = question.topic
        if topic not in topic_performance:
            topic_performance[topic] = {
                "total": 0,
                "correct": 0,
            }

        topic_performance[topic]["total"] += 1
        if is_correct:
            topic_performance[topic]["correct"] += 1

    # Use the actual number of recorded questions for the denominator.
    total_questions = len(questions)
    total_correct = sum(
        1 for result in answers[:total_questions] if result
    )

    overall_score = (
        total_correct / total_questions
        if total_questions > 0
        else 0.0
    )

    passed = overall_score >= 0.7

    return {
        "overall": {
            "total_questions": total_questions,
            "mcq_total": len(mcq_questions),
            "open_ended_total": len(open_ended_questions),
            "total_correct": total_correct,
            "overall_score": overall_score,
            "passed": passed,
            "completion_timestamp": datetime.now(
                timezone.utc
            ).isoformat(),
        },
        "type_wise": {
            "mcq": {
                "total": len(mcq_questions),
                "correct": mcq_correct,
            },
            "open_ended": {
                "total": len(open_ended_questions),
                "correct": open_ended_correct,
            },
        },
        "difficulty_wise": difficulty_performance,
        "topic_wise": topic_performance,
    }
