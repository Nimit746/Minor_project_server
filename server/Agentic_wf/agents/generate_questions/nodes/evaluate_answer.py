from Agentic_wf.agents.generate_questions.states import SessionState
from Agentic_wf.agents.generate_questions.utils import groq_judge, run_sandbox_tests

async def evaluate_answer(state: SessionState) -> SessionState:
    """
    Evaluate the candidate's answer - Stage 6 implements type-based routing:
    - MCQ: free exact match
    - Coding: free sandbox execution
    - Open-ended: LLM judge (only LLM call in eval path)
    """
    if not state.question or not state.candidate_answer:
        state.is_correct = False
        state.answer_correctness_history.append(False)
        return {"is_correct": False, "answer_correctness_history": state.answer_correctness_history}
    
    is_correct = False
    numeric_score: float = 0.0
    feedback_text: str | None = None

    # Evaluate based on question type
    if state.question.question_type == "mcq":
        # Exact match for MCQ (free, no LLM cost)
        is_correct = state.candidate_answer.strip() == (state.question.correct_answer or "").strip()
        numeric_score = 10.0 if is_correct else 0.0
        feedback_text = "Correct" if is_correct else "Incorrect"
    elif state.question.question_type == "coding":
        # Run sandbox tests for coding questions (free, sandboxed execution)
        is_correct = await run_sandbox_tests(state.candidate_answer, state.question)
        numeric_score = 10.0 if is_correct else 0.0
        feedback_text = "Passed test cases" if is_correct else "Failed test cases"
    elif state.question.question_type == "open_ended":
        # Use LLM judge for open-ended questions - supports partial credit (0-10)
        try:
            question_context = state.question.question_text
            if state.question.rubric:
                question_context += f"\n\nRubric / Criteria:\n{state.question.rubric}"

            judge_result = await groq_judge(question=question_context, answer=state.candidate_answer)
            numeric_score = float(judge_result.score)
            feedback_text = getattr(judge_result, "critique", None)
            # An answer with >= 5/10 is considered competent for difficulty progression
            is_correct = numeric_score >= 5.0
        except Exception as e:
            print(f"Error evaluating open-ended answer with groq_judge: {e}")
            numeric_score = 0.0
            is_correct = False
            feedback_text = "Evaluation failed"

    # Update state
    state.is_correct = is_correct
    state.score_running += numeric_score
    state.score_history.append(numeric_score)
    state.answer_correctness_history.append(is_correct)

    print(
        f"Answer evaluated: score={numeric_score}/10, is_correct={is_correct}. "
        f"Running score: {state.score_running}/{(len(state.question_history) or 1) * 10}"
    )

    return {
        "is_correct": is_correct,
        "score_running": state.score_running,
        "score_history": state.score_history,
        "answer_correctness_history": state.answer_correctness_history,
        "last_evaluation": {
            "score": numeric_score,
            "max_score": 10.0,
            "is_correct": is_correct,
            "critique": feedback_text,
        },
    }