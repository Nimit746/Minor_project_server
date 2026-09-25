import uuid
from typing import Dict, List
from Agentic_wf.agents.generate_questions.states import Question
from Agentic_wf.agents.generate_questions.utils.get_cache_key import get_cache_key
from Agentic_wf.agents.generate_questions.utils.generate_batch_questions import generate_batch_questions

# In-memory cache for local dev - keyed by topic, difficulty, company, and question_type
question_cache: Dict[str, List[Question]] = {}

async def get_next_question_from_cache_or_generate(
    topic: str,
    difficulty: str,
    retrieved_chunks: list[str] = None,
    company_name: str | None = None,
    target_role: str | None = None,
    candidate_skills: list[str] | None = None,
    question_type: str = "mcq"
) -> Question | None:
    """
    Check cache for (topic, difficulty, company, question_type).
    If hit, pop and return one. If miss, generate a batch, cache them, return one.
    Now with improved cache key generation and error handling.
    """
    # Generate proper cache key with all dimensions
    cache_key = get_cache_key(topic, difficulty, company_name, question_type)

    # Check if we have questions in cache
    if cache_key in question_cache and question_cache[cache_key]:
        print(f"Cache hit! Returning question from cache for {cache_key}")
        return question_cache[cache_key].pop(0)

    # Cache miss - generate a new batch with safe defaults
    print(f"Cache miss! Generating new batch for {cache_key}")
    new_questions = await generate_batch_questions(
        topic,
        difficulty,
        retrieved_chunks,
        company_name=company_name,
        target_role=target_role,
        candidate_skills=candidate_skills,
        question_type=question_type
    )

    if new_questions:
        # Cache all questions except the first one we return
        question_cache[cache_key] = new_questions[1:]
        print(f"Cached {len(question_cache[cache_key])} questions for future use")
        return new_questions[0]

    # If all else fails, return None - caller will handle fallback
    print(f"Failed to generate any questions for {cache_key}")
    return None