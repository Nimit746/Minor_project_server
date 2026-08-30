import uuid
import json
from typing import Dict, List
from Agentic_wf.config import LLM
from Agentic_wf.agents.generate_questions.states.schemas import Question
from Agentic_wf.agents.generate_questions.prompts.question_generation import (
    QUESTION_GENERATION_SYSTEM_PROMPT,
    build_rag_prompt,
    build_question_generation_prompt
)

# In-memory cache for local dev - keyed by topic, difficulty, and company
question_cache: Dict[str, List[Question]] = {}


def get_cache_key(topic: str, difficulty: str, company_name: str | None = None) -> str:
    """Generate a unique cache key for topic, difficulty, and company."""
    company_key = (company_name or "general").strip().lower()
    return f"{topic}:{difficulty}:{company_key}"


async def generate_batch_questions(
    topic: str,
    difficulty: str,
    retrieved_chunks: list[str] = None,
    company_name: str | None = None,
    target_role: str | None = None,
    candidate_skills: list[str] | None = None,
    batch_size: int = 5
) -> List[Question]:
    """
    Generate multiple questions in a single LLM call to optimize token usage.
    Caches all generated questions for future use.
    """
    llm = LLM.get_llm("groq")

    # Modify system prompt to request a JSON array of questions
    batch_system_prompt = QUESTION_GENERATION_SYSTEM_PROMPT.replace(
        "You must return ONLY a valid JSON object",
        f"You must return ONLY a valid JSON array of {batch_size} JSON objects"
    )

    # Build user prompt
    if retrieved_chunks:
        user_prompt = build_rag_prompt(
            topic,
            difficulty,
            retrieved_chunks,
            company_name=company_name,
            target_role=target_role,
            candidate_skills=candidate_skills
        )
    else:
        user_prompt = build_question_generation_prompt(
            topic,
            difficulty,
            company_name=company_name,
            target_role=target_role,
            candidate_skills=candidate_skills
        )

    # Add instruction to generate multiple unique questions
    user_prompt += f"\n\nGenerate exactly {batch_size} unique, distinct questions. Return them as a JSON array."

    messages = [
        {"role": "system", "content": batch_system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    # Call LLM with retry logic
    max_retries = 2
    for attempt in range(max_retries):
        try:
            response = await llm.ainvoke(messages)
            response_text = response.content.strip()

            # Clean up any markdown fences
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()

            # Parse JSON array
            questions_data = json.loads(response_text)

            # If model returns a single dict instead of a list
            if isinstance(questions_data, dict):
                questions_data = [questions_data]

            # Validate and convert to Question objects
            questions = []
            for q_data in questions_data:
                if not q_data.get("id"):
                    q_data["id"] = str(uuid.uuid4())
                questions.append(Question(**q_data))

            return questions

        except Exception as e:
            if attempt == max_retries - 1:
                print(f"Failed to generate batch questions: {e}")
                return []
            import asyncio
            await asyncio.sleep(1)


async def get_next_question_from_cache_or_generate(
    topic: str,
    difficulty: str,
    retrieved_chunks: list[str] = None,
    company_name: str | None = None,
    target_role: str | None = None,
    candidate_skills: list[str] | None = None
) -> Question | None:
    """
    Check cache for (topic, difficulty, company).
    If hit, pop and return one. If miss, generate a batch, cache them, return one.
    """
    cache_key = get_cache_key(topic, difficulty, company_name)

    # Check if we have questions in cache
    if cache_key in question_cache and question_cache[cache_key]:
        return question_cache[cache_key].pop(0)

    # Cache miss - generate a new batch
    new_questions = await generate_batch_questions(
        topic,
        difficulty,
        retrieved_chunks,
        company_name=company_name,
        target_role=target_role,
        candidate_skills=candidate_skills
    )

    if new_questions:
        question_cache[cache_key] = new_questions[1:]
        return new_questions[0]

    return None
