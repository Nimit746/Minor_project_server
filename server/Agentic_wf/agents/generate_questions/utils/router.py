from Agentic_wf.agents.generate_questions.states import SessionState
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
    Determines the type of the next question to maintain a 60/40 MCQ to open-ended ratio.
    """
    mcq_count = sum(1 for q in state.question_history if q.question_type == "mcq")
    total_questions = len(state.question_history)
    target_mcq_count = int((total_questions + 1) * 0.6)

    if mcq_count < target_mcq_count:
        return "mcq"
    return "open_ended"


def should_continue(state: SessionState) -> Literal["continue", "end"]:
    """
    Determines whether to continue the interview based on several conditions.
    """
    # End if the maximum number of questions is reached
    if len(state.question_history) >= MAX_QUESTIONS:
        return "end"

    # End if the candidate demonstrates mastery
    if state.current_difficulty >= MASTERY_DIFFICULTY_THRESHOLD and \
       state.answer_correctness_history[-MASTERY_CONSECUTIVE_CORRECT:] == [True] * MASTERY_CONSECUTIVE_CORRECT:
        return "end"

    # End if the last three questions were answered incorrectly
    if len(state.answer_correctness_history) >= 3 and \
       state.answer_correctness_history[-3:] == [False, False, False]:
        return "end"
        
    return "continue"


def bump_difficulty(current_difficulty: int, change: int) -> int:
    """
    Adjusts the difficulty level, keeping it within the 1-10 range.
    """
    return max(1, min(10, current_difficulty + change))


async def is_mastered(state: SessionState, topic: str) -> bool:
    """
    Checks if a topic is mastered based on the candidate's performance.
    (This is a placeholder for your mastery logic)
    """
    # Example logic: consider a topic mastered if 3 questions on it were answered correctly.
    correct_count = 0
    for i, q in enumerate(state.question_history):
        if q.topic == topic and state.answer_correctness_history[i]:
            correct_count += 1
    return correct_count >= 3


async def pick_next_topic(state: SessionState) -> str:
    """
    Selects the next topic for the interview, prioritizing concept gaps and avoiding mastered topics.
    """
    # Prioritize concept gaps first
    if state.concept_gaps:
        # Pick a concept gap that is not yet mastered
        for topic in state.concept_gaps:
            if not await is_mastered(state, topic):
                return topic

    # If no unmastered concept gaps, pick a new topic from the knowledge graph
    all_topics = set(state.knowledge_graph.nodes)
    
    # Create a set of topics that have already been asked
    asked_topics = {q.topic for q in state.question_history}
    
    # Exclude mastered and already asked topics
    mastered_topics = {topic for topic in all_topics if await is_mastered(state, topic)}
    
    available_topics = list(all_topics - mastered_topics - asked_topics)

    if available_topics:
        return random.choice(available_topics)
        
    # Fallback if all topics are covered/mastered
    return "General"