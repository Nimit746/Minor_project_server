from Agentic_wf.agents.generate_questions.states.schemas import SessionState
import logging

logger = logging.getLogger(__name__)

# List of default topics for fallback rotation
DEFAULT_TOPICS = [
    "Python programming basics",
    "Data structures and algorithms",
    "Machine learning fundamentals",
    "System design principles",
    "Database design",
    "Cloud computing",
    "API development",
    "Cybersecurity basics"
]


def bump_difficulty(current: int, delta: int) -> int:
    """Bump difficulty up or down, keeping it within 1-5 bounds."""
    return max(1, min(5, current + delta))


def get_available_topics_for_session(state: SessionState) -> list[str]:
    """Dynamically assemble pool of topics based on company focus, resume skills, and defaults."""
    topic_pool: list[str] = []

    # Add company focus areas first
    if state.company_focus:
        topic_pool.extend(state.company_focus)

    # Add extracted skills from resume
    if state.extracted_skills:
        topic_pool.extend(state.extracted_skills)

    # Add default topics to ensure sufficient variety
    for t in DEFAULT_TOPICS:
        if t not in topic_pool:
            topic_pool.append(t)

    return topic_pool


def pick_next_topic(state: SessionState) -> str:
    """
    Pick the next topic to ask a question about.
    Priority:
    1. Concept gaps (failed questions in current session)
    2. Weak topics from candidate profile
    3. Rotation across company focus / resume skills / default topics
    """
    # 1. Prioritize current session concept gaps
    if state.concept_gaps:
        return state.concept_gaps[-1]

    # 2. Next prioritize candidate historical weak topics
    recent_topics = [q.topic for q in state.question_history[-3:]]
    for wt in state.weak_topics:
        if wt not in recent_topics:
            return wt

    # 3. Rotate through session topics
    available_topics = get_available_topics_for_session(state)
    fresh_topics = [t for t in available_topics if t not in recent_topics]

    if fresh_topics:
        return fresh_topics[0]

    return available_topics[0]


async def controller(state: SessionState) -> SessionState:
    """
    Controller node that adapts difficulty and topic based on candidate performance.
    """
    # Initialize with default topic if not set
    if not state.current_topic:
        state.current_topic = pick_next_topic(state)

    # Skip adaptation logic on initial run (no answers evaluated yet)
    if not state.answer_correctness_history:
        return state

    # Get last answers to adjust difficulty
    last_answer_correct = state.answer_correctness_history[-1]
    last_two = state.answer_correctness_history[-2:] if len(state.answer_correctness_history) >= 2 else [last_answer_correct]

    # Adjust difficulty based on performance
    if last_two == [True, True]:
        state.current_difficulty = bump_difficulty(state.current_difficulty, 1)
        logger.info(f"Increasing difficulty to {state.current_difficulty} (2 consecutive correct answers)")
    elif not last_answer_correct:
        state.current_difficulty = bump_difficulty(state.current_difficulty, -1)
        logger.info(f"Decreasing difficulty to {state.current_difficulty} (last answer incorrect)")
        if state.question and state.question.topic not in state.concept_gaps:
            state.concept_gaps.append(state.question.topic)
            logger.info(f"Added {state.question.topic} to concept gaps")

    # Pick the next topic
    state.current_topic = pick_next_topic(state)
    logger.info(f"Next topic: {state.current_topic}, current difficulty: {state.current_difficulty}")

    return state