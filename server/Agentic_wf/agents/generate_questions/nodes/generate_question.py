from Agentic_wf.agents.generate_questions.states import SessionState
from Agentic_wf.agents.generate_questions.utils import (
    get_next_question_from_cache_or_generate,
    get_next_question_type,
    retrieve_relevant_chunks,
)


async def generate_question(state: SessionState) -> SessionState:
    """
    Generate a question based on the current session state.
    """
    # Determine question type
    question_type = get_next_question_type(state)

    # Retrieve relevant chunks
    retrieved_chunks = await retrieve_relevant_chunks(state.current_topic)

    # Get the next question
    question = await get_next_question_from_cache_or_generate(
        topic=state.current_topic,
        difficulty=state.current_difficulty,
        retrieved_chunks=retrieved_chunks,
        company_name=state.company_name,
        target_role=state.target_role,
        candidate_skills=state.extracted_skills,
        question_type=question_type,
    )

    return {'question': question}