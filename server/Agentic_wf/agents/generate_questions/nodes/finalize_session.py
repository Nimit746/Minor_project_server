
from Agentic_wf.agents.generate_questions.states import SessionState
from Agentic_wf.agents.generate_questions.utils import (
    recompute_weak_topics,
    calculate_detailed_metrics,
)


async def finalize_session(state: SessionState) -> dict:
    """
    Finalize the interview, calculate metrics, and update weak topics.
    """
    weak_topics = recompute_weak_topics(
        state.weak_topics,
        state.concept_gaps,
    )

    report = calculate_detailed_metrics(state)

    return {
        "weak_topics": weak_topics,
        "final_report": report,
        "session_complete": True,
    }
