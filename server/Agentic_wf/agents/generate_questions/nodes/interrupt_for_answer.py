from langgraph.types import interrupt
from Agentic_wf.agents.generate_questions.states import SessionState


async def interrupt_for_answer(state: SessionState) -> SessionState:
    """Interrupt the graph to wait for the candidate's answer."""
    if not state.question:
        return state
        
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