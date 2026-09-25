from Agentic_wf.agents.generate_questions.states import SessionState
from Agentic_wf.agents.generate_questions.utils import bump_difficulty, pick_next_topic

async def controller(state: SessionState) -> SessionState:
    """
    Controller node that adapts difficulty and topic based on candidate performance.
    """
    # Initialize with default topic if not set
    if not state.current_topic:
        state.current_topic = pick_next_topic(state)

    # Skip adaptation logic on initial run (no answers evaluated yet)
    if not state.answer_correctness_history:
        return {"current_topic": state.current_topic}

    # Get last answers to adjust difficulty
    last_answer_correct = state.answer_correctness_history[-1]
    last_two = state.answer_correctness_history[-2:] if len(state.answer_correctness_history) >= 2 else [last_answer_correct]

    # Adjust difficulty based on performance
    if last_two == [True, True]:
        state.current_difficulty = bump_difficulty(state.current_difficulty, 1)
    elif not last_answer_correct:
        state.current_difficulty = bump_difficulty(state.current_difficulty, -1)
        if state.question and state.question.topic not in state.concept_gaps:
            state.concept_gaps.append(state.question.topic)

    # Track difficulty progression for analytics
    state.difficulty_history.append(state.current_difficulty)
    
    # Pick the next topic
    state.current_topic = pick_next_topic(state)
    return {
        "current_difficulty": state.current_difficulty,
        "concept_gaps": state.concept_gaps,
        "difficulty_history": state.difficulty_history,
        "current_topic": state.current_topic,
    }