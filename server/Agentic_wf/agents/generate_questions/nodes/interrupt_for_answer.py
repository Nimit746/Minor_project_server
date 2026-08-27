from langgraph.types import interrupt
from Agentic_wf.agents.generate_questions.states import SessionState
import logging

logger = logging.getLogger(__name__)

async def interrupt_for_answer(state: SessionState) -> SessionState:
    """Interrupt the graph to wait for the candidate's answer."""
    if not state.question:
        logger.error("No question generated before waiting for answer!")
        return state
        
    logger.info(f"Waiting for answer to question: {state.question.question_text}")
    
    # Use LangGraph's interrupt to pause execution and wait for resume value
    candidate_answer = interrupt({
        "question_id": state.question.id,
        "question_text": state.question.question_text,
        "options": state.question.options,
        "question_type": state.question.question_type
    })
    
    # Update state with the received answer
    state.candidate_answer = candidate_answer
    state.answer_history.append(candidate_answer)
    
    return state