from Agentic_wf.agents.generate_questions.states.schemas import SessionState, CandidateProfile
from Agentic_wf.config.database import get_async_db
from Agentic_wf.agents.generate_questions.tools import analyze_resume, get_company_profile


async def load_candidate_profile(state: SessionState) -> SessionState:
    """
    Load candidate profile from MongoDB and analyze resume/company context
    to personalize the starting state and topic list.
    """
    # 1. Load or fallback profile from MongoDB
    if state.candidate_id:
        try:
            db = get_async_db()
            candidates_collection = db.candidates
            profile_data = await candidates_collection.find_one({"candidate_id": state.candidate_id})

            if not profile_data:
                profile = CandidateProfile(
                    candidate_id=state.candidate_id,
                    resume_text=state.resume_text,
                    target_company=state.company_name,
                    target_role=state.target_role,
                    historical_avg_score=0.0,
                    weak_topics=[],
                    strengths=[],
                    weaknesses=[],
                    sessions_completed=0
                )
                await candidates_collection.insert_one(profile.model_dump())
            else:
                profile = CandidateProfile(**profile_data)
                state.historical_avg_score = profile.historical_avg_score
                state.weak_topics = profile.weak_topics
                state.strengths = profile.strengths
                state.weaknesses = profile.weaknesses
                state.sessions_completed = profile.sessions_completed
                
                # Inherit stored resume or company if not passed in current state
                if not state.resume_text and profile.resume_text:
                    state.resume_text = profile.resume_text
                if not state.company_name and profile.target_company:
                    state.company_name = profile.target_company
                if not state.target_role and profile.target_role:
                    state.target_role = profile.target_role

        except Exception:
            pass

    # 2. Extract resume information if available
    if state.resume_text:
        try:
            resume_analysis = await analyze_resume(state.resume_text)
            state.extracted_skills = resume_analysis.get("skills", [])
            if resume_analysis.get("recommended_topics"):
                state.strengths = list(set(state.strengths + resume_analysis.get("recommended_topics", [])))
        except Exception:
            pass

    # 3. Retrieve company profiling if target company is specified
    if state.company_name:
        try:
            comp_profile = await get_company_profile(state.company_name, state.target_role or "Software Engineer")
            state.company_focus = comp_profile.get("focus_areas", [])
        except Exception:
            pass

    # 4. Set initial difficulty based on candidate's historical score
    if state.historical_avg_score > 0.8:
        state.current_difficulty = 4
    elif state.historical_avg_score < 0.4 and state.sessions_completed > 0:
        state.current_difficulty = 1
    else:
        state.current_difficulty = 2

    # 5. Set initial topic: Prioritize weak topics -> Company focus -> Resume skills -> Default
    if state.weak_topics:
        state.current_topic = state.weak_topics[0]
    elif state.company_focus:
        state.current_topic = state.company_focus[0]
    elif state.extracted_skills:
        state.current_topic = state.extracted_skills[0]
    elif not state.current_topic:
        from Agentic_wf.agents.generate_questions.nodes.controller import AVAILABLE_TOPICS
        state.current_topic = AVAILABLE_TOPICS[0]

    return state
