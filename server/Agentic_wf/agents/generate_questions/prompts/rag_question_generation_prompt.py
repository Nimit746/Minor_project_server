from langchain_core.prompts import ChatPromptTemplate

# Chat prompt template for RAG-grounded question generation
rag_question_generation = ChatPromptTemplate([
    ('system',"""You are an expert technical interview question generator.
Create a high-quality interview question tailored to the target company, candidate background, topic, and difficulty.

You must return ONLY a valid JSON object, no markdown fences, no preamble, no extra text. The JSON must match this schema exactly:
{{
  "id": "unique_string_id",
  "topic": "the provided topic",
  "difficulty": "easy|medium|hard",
  "question_type": "mcq|coding|open_ended",
  "question_text": "the full question text",
  "options": ["option A", "option B", "option C", "option D"],
  "correct_answer": "the correct option text",
  "rubric": "evaluation rubric for open-ended/coding questions"
}}

Ensure the question is relevant, tests understanding of the topic, and is appropriate for the specified difficulty level and company interview standard."""),
    ('human', 'Context:\n{context}\n\nBase this question on the following reference material:\n{reference_material}\n\nGenerate a {difficulty} {question_type} question about: {topic}')
])


def build_rag_question_generation_prompt(
    topic: str,
    difficulty: str,
    retrieved_chunks: list[str],
    company_name: str | None = None,
    target_role: str | None = None,
    candidate_skills: list[str] | None = None,
    question_type: str = "mcq"
):
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
    return rag_question_generation.format_prompt(
        context=context_str,
        reference_material=chunks_text,
        difficulty=difficulty,
        question_type=question_type,
        topic=topic
    )