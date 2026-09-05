from Agentic_wf.agents.generate_questions.states.schemas import SessionState
from typing import Literal
import random

# Maximum number of questions per session (total 30 as required)
MAX_QUESTIONS = 6
# Mastery threshold conditions
MASTERY_DIFFICULTY_THRESHOLD = 5
MASTERY_CONSECUTIVE_CORRECT = 5

# Question type distribution: 60% MCQ, 40% subjective (open-ended) to meet requirement of both types
QUESTION_TYPES = ["mcq"] * 6 + ["open_ended"] * 4  # 6 MCQs, 4 open-ended for every 10 questions

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

def should_continue(state: SessionState) -> Literal["continue", "end"]:
    """
    Conditional edge function to determine if we should ask another question or end the session.
    Modified to always ask all 30 questions even if some are answered wrong, as per requirements.
    Only ends when MAX_QUESTIONS (30) is reached, regardless of performance.
    """
    # Continue until we've asked all 30 questions - this ensures we display all questions
    # even if some are answered incorrectly, as per the requirement
    if state.questions_asked >= MAX_QUESTIONS:
        return "end"
    
    # Otherwise continue to next question
    return "continue"