QUESTION_GENERATION_SYSTEM_PROMPT = """You are an expert technical interview question generator.
Create a high-quality interview question tailored to the target company, candidate background, topic, and difficulty.

You must return ONLY a valid JSON object, no markdown fences, no preamble, no extra text. The JSON must match this schema exactly:
{
  "id": "unique_string_id",
  "topic": "the provided topic",
  "difficulty": "easy|medium|hard",
  "question_type": "mcq|coding|open_ended",
  "question_text": "the full question text",
  "options": ["option A", "option B", "option C", "option D"],
  "correct_answer": "the correct option text",
  "rubric": "evaluation rubric for open-ended/coding questions"
}

Ensure the question is relevant, tests understanding of the topic, and is appropriate for the specified difficulty level and company interview standard."""


def build_question_generation_prompt(
    topic: str,
    difficulty: str,
    company_name: str | None = None,
    target_role: str | None = None,
    candidate_skills: list[str] | None = None,
    question_type: str = "mcq"
) -> str:
    """Build the user prompt for question generation incorporating company & candidate context."""
    context_lines = []
    if company_name:
        context_lines.append(f"Target Company: {company_name}")
    if target_role:
        context_lines.append(f"Target Role: {target_role}")
    if candidate_skills:
        context_lines.append(f"Candidate Skills Background: {', '.join(candidate_skills[:6])}")

    context_str = "\n".join(context_lines)
    if context_str:
        context_str = f"Context:\n{context_str}\n\n"

    return f"""{context_str}Generate a {difficulty} {question_type} question about: {topic}"""


def build_rag_prompt(
    topic: str,
    difficulty: str,
    retrieved_chunks: list[str],
    company_name: str | None = None,
    target_role: str | None = None,
    candidate_skills: list[str] | None = None,
    question_type: str = "mcq"
) -> str:
    """Build the user prompt with RAG grounding context, company and candidate context."""
    chunks_text = "\n\n---\n\n".join(retrieved_chunks)
    context_lines = []
    if company_name:
        context_lines.append(f"Target Company: {company_name}")
    if target_role:
        context_lines.append(f"Target Role: {target_role}")
    if candidate_skills:
        context_lines.append(f"Candidate Skills Background: {', '.join(candidate_skills[:6])}")

    context_str = "\n".join(context_lines)
    if context_str:
        context_str = f"Context:\n{context_str}\n\n"

    return f"""{context_str}Base this question on the following reference material:\n{chunks_text}

Generate a {difficulty} {question_type} question about: {topic}"""