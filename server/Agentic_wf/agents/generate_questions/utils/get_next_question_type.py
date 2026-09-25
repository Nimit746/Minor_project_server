import random
from Agentic_wf.agents.generate_questions.states import SessionState



QUESTION_TYPES = ["mcq"] * 3 + ["open_ended"] * 7  # 3 MCQs, 7 open-ended for every 10 questions

def get_next_question_type(state: SessionState) -> str:
    """
    Get the next question type based on session progress to maintain proper distribution.
    This ensures we have a mix of MCQ and subjective questions throughout the 30 questions.
    """
    # Count how many of each type we've asked so far
    mcq_count = sum(1 for q in state.question_history if q.question_type == "mcq")
    open_ended_count = len(state.question_history) - mcq_count
    
    # Target distribution: 18 MCQs (60%), 12 open-ended (40%) out of 30 total
    target_mcq = int((state.questions_asked + 1) * 0.6)
    target_open_ended = (state.questions_asked + 1) - target_mcq
    
    if mcq_count < target_mcq:
        return "mcq"
    elif open_ended_count < target_open_ended:
        return "open_ended"
    else:
        # Fallback to random selection from the distribution list
        return random.choice(QUESTION_TYPES)