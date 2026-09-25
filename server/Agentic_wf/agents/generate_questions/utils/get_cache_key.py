def get_cache_key(topic: str, difficulty: str, company_name: str | None = None, question_type: str = "mcq") -> str:
    """Generate a unique cache key for topic, difficulty, company, and question type."""
    company_key = (company_name or "general").strip().lower()
    return f"{topic}:{difficulty}:{company_key}:{question_type}"