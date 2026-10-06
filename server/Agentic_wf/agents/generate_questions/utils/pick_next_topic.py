from Agentic_wf.agents.generate_questions.states import SessionState
from Agentic_wf.agents.generate_questions.utils.get_available_topics_for_session import get_available_topics_for_session

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