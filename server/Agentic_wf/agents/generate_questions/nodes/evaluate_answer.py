from Agentic_wf.agents.generate_questions.states.schemas import SessionState
from Agentic_wf.agents.generate_questions.nodes.llm_judge import groq_judge, run_sandbox_tests
import logging

logger = logging.getLogger(__name__)

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
        return state
    
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
            logger.warning("No rubric provided for open-ended question - marking as incorrect")
            is_correct = False
    
    # Update state
    state.is_correct = is_correct
    
    # Update running score
    if is_correct:
        state.score_running += 1
        
    # Update correctness history
    state.answer_correctness_history.append(is_correct)
    
    logger.info(f"Answer {is_correct and 'correct' or 'incorrect'}!")
    logger.info(f"Current score: {state.score_running}/{state.questions_asked}")
    
    return state