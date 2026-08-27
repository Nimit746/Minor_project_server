from Agentic_wf.agents.generate_questions.states.schemas import SessionState
from typing import Literal

# Maximum number of questions per session
MAX_QUESTIONS = 5
# Mastery threshold conditions
MASTERY_DIFFICULTY_THRESHOLD = 4
MASTERY_CONSECUTIVE_CORRECT = 3

def should_continue(state: SessionState) -> Literal["continue", "end"]:
    """
    Conditional edge function to determine if we should ask another question or end the session.
    Stage 8: End if either MAX_QUESTIONS is reached OR mastery threshold is hit.
    """
    # End if we've asked max questions
    if state.questions_asked >= MAX_QUESTIONS:
        return "end"
    
    # Check for mastery condition: current difficulty >=4 and last 3 answers correct
    if (state.current_difficulty >= MASTERY_DIFFICULTY_THRESHOLD and 
        len(state.answer_correctness_history) >= MASTERY_CONSECUTIVE_CORRECT):
        last_3 = state.answer_correctness_history[-MASTERY_CONSECUTIVE_CORRECT:]
        if all(last_3):
            return "end"
    
    # Otherwise continue to next question
    return "continue"