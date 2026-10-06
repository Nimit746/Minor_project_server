import json
import logging
from Agentic_wf.agents.generate_questions.states import SessionState, CandidateProfile
from Agentic_wf.config.database import get_async_db
from Agentic_wf.agents.generate_questions.tools import analyze_resume, get_company_profile

logger = logging.getLogger(__name__)

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

    # 2. Extract resume information if a URL is provided
    if state.resume_file_url:
        try:
            # The analyze_resume tool now takes a URL
            resume_analysis = await analyze_resume(state.resume_file_url)
            
            if "error" in resume_analysis:
                logger.error(f"Resume analysis failed: {resume_analysis['error']}")
            else:
                state.extracted_skills = resume_analysis.get("skills", [])
                profile.skills = state.extracted_skills
                
                # Merge recommended topics into strengths
                recommended_topics = resume_analysis.get("recommended_topics", [])
                state.strengths = list(set(state.strengths + recommended_topics))
                profile.strengths = state.strengths
                
                # Optionally, save the URL of the analyzed resume
                profile.resume_text = state.resume_file_url 
        except Exception as e:
            logger.warning(f"An exception occurred during resume analysis: {e}")

    # 3. Retrieve company interview trends and extract focus areas if target company is specified
    if state.company_name:
        try:
            # Call the updated function that returns JSON string
            comp_profile_json = await get_company_profile.ainvoke({
                "company_name": state.company_name,
                "target_role": state.target_role
            })
            comp_profile = json.loads(comp_profile_json)
            
            # Extract focus areas from search results
            focus_areas = []
            for result in comp_profile.get("results", []):
                snippet = result.get("snippet", "").lower()
                # Extract common technical focus areas from interview snippets
                if "coding" in snippet: focus_areas.append("Coding fundamentals")
                if "system design" in snippet: focus_areas.append("System Design")
                if "algorithms" in snippet: focus_areas.append("Algorithms")
                if "data structures" in snippet: focus_areas.append("Data Structures")
                if "api" in snippet: focus_areas.append("API Development")
                if "database" in snippet: focus_areas.append("Database Systems")
            
            # Remove duplicates and set company focus
            state.company_focus = list(dict.fromkeys(focus_areas))  # preserve order, remove duplicates
        except Exception as e:
            logger.warning(f"Failed to retrieve company trends: {e}")
            state.company_focus = []

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
            from Agentic_wf.agents.generate_questions.utils.get_available_topics_for_session import DEFAULT_TOPICS
            state.current_topic = DEFAULT_TOPICS[0]

    return {
        "historical_avg_score": state.historical_avg_score,
        "weak_topics": state.weak_topics,
        "strengths": state.strengths,
        "weaknesses": state.weaknesses,
        "sessions_completed": state.sessions_completed,
        "resume_text": state.resume_text,
        "company_name": state.company_name,
        "target_role": state.target_role,
        "extracted_skills": state.extracted_skills,
        "company_focus": state.company_focus,
        "current_difficulty": state.current_difficulty,
        "current_topic": state.current_topic,
    }