def recompute_weak_topics(existing_weak_topics: list, concept_gaps: list) -> list:
    """
    Recompute weak topics by combining existing weak topics with new concept gaps from the session.
    Deduplicates and maintains a sorted list of unique weak topics.
    """
    combined = list(set((existing_weak_topics or []) + (concept_gaps or [])))
    return sorted(combined)