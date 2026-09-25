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
    
    # Evaluate based on question type
    if state.question.question_type == "mcq":
        # Exact match for MCQ (free, no LLM cost)
        is_correct = state.candidate_answer.strip() == state.question.correct_answer.strip()
    elif state.question.question_type == "coding":
        # Run sandbox tests for coding questions (free, sandboxed execution)
        is_correct = await run_sandbox_tests(state.candidate_answer, state.question)
    elif state.question.question_type == "open_ended":
        # Use LLM judge only for open-ended questions (only LLM call in eval path)
        if state.question.rubric:
            is_correct = await groq_judge(state.candidate_answer, state.question.rubric)
        else:
            is_correct = False
    
    # Update state
    state.is_correct = is_correct
    
    # Update running score
    if is_correct:
        state.score_running += 1
        print(f"Answer marked as correct! Running score: {state.score_running}/{state.questions_asked}")
    else:
        print(f"Answer marked as incorrect. Running score: {state.score_running}/{state.questions_asked}")
        
    # Update correctness history - now that question_history is properly maintained, simple append
    state.answer_correctness_history.append(is_correct)
    
    print(f"Answer correctness history length: {len(state.answer_correctness_history)}, question history length: {len(state.question_history)}")
    return {
        "is_correct": is_correct,
        "score_running": state.score_running,
        "answer_correctness_history": state.answer_correctness_history,
    }