from Agentic_wf.agents.generate_questions.states import SessionState

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