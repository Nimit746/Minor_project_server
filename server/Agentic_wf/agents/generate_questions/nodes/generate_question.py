import uuid
from Agentic_wf.config import get_embeddings, Retriever as ConfigRetriever
from Agentic_wf.agents.generate_questions.states.schemas import SessionState, Question
from Agentic_wf.agents.generate_questions.nodes.cache_lookup import get_next_question_from_cache_or_generate
from Agentic_wf.agents.generate_questions.utils.router import get_next_question_type

# Map 1-5 difficulty scale to string representation - enhanced for better granularity
DIFFICULTY_MAP = {
    1: "easy",
    2: "easy",
    3: "medium",
    4: "hard",
    5: "expert"  # Added expert level for more difficulty variation
}


async def retrieve_relevant_chunks(topic: str, k: int = 3) -> list[str]:
    """Retrieve relevant chunks from vector DB for the given topic."""
    try:
        embeddings = get_embeddings()
        retriever = ConfigRetriever(embeddings, "default_collection")
        docs = await retriever.aretrieve(topic, k=k)
        if docs:
            return [doc.page_content for doc in docs]
        return []
    except Exception:
        return []


async def generate_question(state: SessionState) -> SessionState:
    """
    Generate a new question with cache optimization, grounded in
    the candidate's resume, company profile, and RAG knowledge.
    Now supports both MCQ and subjective (open-ended) questions with adaptive difficulty.
    """
    current_topic = state.current_topic or "Python programming basics"
    difficulty_int = state.current_difficulty or 2
    difficulty = DIFFICULTY_MAP.get(difficulty_int, "medium")
    # Dynamically select question type to maintain proper mix of MCQ and subjective
    question_type = get_next_question_type(state)

    # Retrieve relevant grounding chunks
    retrieved_chunks = await retrieve_relevant_chunks(current_topic)

    # Check cache / generate question with full context, now including question_type
    question = await get_next_question_from_cache_or_generate(
        topic=current_topic,
        difficulty=difficulty,
        retrieved_chunks=retrieved_chunks,
        company_name=state.company_name,
        target_role=state.target_role,
        candidate_skills=state.extracted_skills,
        question_type=question_type
    )

    # If cache lookup/generation failed, create a fallback question that supports both types
    if not question:
        if question_type == "mcq":
            fallback_question = Question(
                id=str(uuid.uuid4()),
                topic=current_topic,
                difficulty=difficulty,
                question_type="mcq",
                question_text=f"Which of the following best describes a core concept in {current_topic}?",
                options=[
                    "Correct understanding of architectural principles",
                    "Arbitrary hardcoded configuration",
                    "Unbounded memory allocation",
                    "Ignoring concurrency locks"
                ],
                correct_answer="Correct understanding of architectural principles",
                rubric=None
            )
        else:
            # Subjective/open-ended fallback question
            fallback_question = Question(
                id=str(uuid.uuid4()),
                topic=current_topic,
                difficulty=difficulty,
                question_type="open_ended",
                question_text=f"Explain the core principles and best practices of {current_topic}. Provide specific examples to illustrate your understanding.",
                options=None,
                correct_answer=None,
                rubric=f"Evaluation rubric for {current_topic}: 1) Correctness of core concepts (40%), 2) Depth of understanding (30%), 3) Quality of examples (20%), 4) Clarity of explanation (10%)"
            )
        question = fallback_question

    # Update state with the generated question
    state.question = question
    state.questions_asked += 1
    state.question_history.append(question)

    return state