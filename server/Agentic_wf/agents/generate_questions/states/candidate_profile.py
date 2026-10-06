from pydantic import BaseModel

class CandidateProfile(BaseModel):
    candidate_id: str
    resume_file_url: str | None = None  # URL to the resume file
    resume_text: str | None = None
    skills: list[str] = []
    target_company: str | None = None
    target_role: str | None = None
    historical_avg_score: float = 0.0
    weak_topics: list[str] = []
    strengths: list[str] = []
    weaknesses: list[str] = []
    sessions_completed: int = 0