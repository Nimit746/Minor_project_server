def get_safe_batch_size(question_type: str) -> int:
    """
    Return safe batch sizes based on question type to avoid token limit issues:
    - open_ended/coding: 1 question (long-form with rubrics)
    - mcq: 2 questions (shorter format)
    Optimized for allam-2-7b's 4096 token context window
    """
    if question_type in ["open_ended", "coding"]:
        return 1
    return 2  # For MCQs, we can safely generate 2 at a time