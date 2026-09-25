from Agentic_wf.agents.generate_questions.states import SessionState
from Agentic_wf.agents.generate_questions.utils import recompute_weak_topics, calculate_detailed_metrics

async def finalize_session(state: SessionState) -> SessionState:
    """
    Finalize the session by calculating metrics, updating weak topics, and preparing the final report.
    """
    # Recompute weak topics based on this session's performance
    state.weak_topics = recompute_weak_topics(state.weak_topics, state.concept_gaps)
    
    # Calculate detailed metrics for the final report
    state.final_report = calculate_detailed_metrics(state)
    
    # Mark the session as complete
    state.session_complete = True
    
    return {
        "weak_topics": state.weak_topics,
        "final_report": state.final_report,
        "session_complete": True,
    }