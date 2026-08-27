from pydantic import BaseModel
from typing import Literal, Optional


class Question(BaseModel):
    id: str
    topic: str
    difficulty: str
    question_type: Literal["mcq", "coding", "open_ended"]
    question_text: str
    options: list[str] | None = None  # for MCQ
    correct_answer: str | None = None  # for MCQ
    rubric: str | None = None  # for open_ended/coding


class SessionState(BaseModel):
    # Candidate & Session Inputs
    candidate_id: str | None = None
    resume_text: str | None = None
    company_name: str | None = None
    target_role: str | None = None
    extracted_skills: list[str] = []
    company_focus: list[str] = []

    # Stage 1-2 fields
    question: Question | None = None
    candidate_answer: str | None = None
    is_correct: bool | None = None
    
    # Stage 3 fields
    question_history: list[Question] = []
    answer_history: list[str] = []
    score_running: int = 0
    questions_asked: int = 0
    
    # Stage 4 fields
    current_difficulty: int = 2  # 1-5 scale
    current_topic: str = ""
    answer_correctness_history: list[bool] = []
    concept_gaps: list[str] = []
    
    # Stage 7 fields
    historical_avg_score: float = 0.0
    weak_topics: list[str] = []
    strengths: list[str] = []
    weaknesses: list[str] = []
    sessions_completed: int = 0
    
    # Stage 8 fields (finalization)
    final_session_score: float | None = None
    updated_historical_avg: float | None = None


class CandidateProfile(BaseModel):
    candidate_id: str
    resume_text: str | None = None
    skills: list[str] = []
    target_company: str | None = None
    target_role: str | None = None
    historical_avg_score: float = 0.0
    weak_topics: list[str] = []
    strengths: list[str] = []
    weaknesses: list[str] = []
    sessions_completed: int = 0