from typing import Literal
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from app.models.interview_model import SessionStatus

class InterviewCreate(BaseModel):
    resume_uuid : str
    role: str = Field(min_length=2, max_length=120)
    target_company: str | None = Field(default= None, max_length=120)
    difficulty: Literal['easy','medium','hard'] = 'medium'



class AnswerSubmit(BaseModel):
    seq: int = Field(ge=1, description='Sequence number of the question being answered')
    answer: str = Field(min_length=1, max_length=20000)




class TurnRead(BaseModel):
    """Client-facing view of a turn. `meta` is intentionally absent."""
    model_config = ConfigDict(from_attributes=True)
    seq: int
    question_uuid: str
    topic: str
    qtype: str
    difficulty: str
    prompt: str
    options: list[str] | None = None
    asked_at: datetime
    answer: str | None = None
    answered_at: datetime | None = None
    score: float | None = None
    feedback: dict | None = None



class InterviewSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    uuid: str
    resume_uuid: str
    role: str
    target_company: str | None = None
    difficulty: str
    status: SessionStatus
    created_at: datetime
    updated_at: datetime


class InterviewRead(InterviewSummary):
    turns: list[TurnRead] = []
    summary: dict | None = None


class InterviewTurnResponse(BaseModel):
    """Returned after starting an interview or submitting an answer."""

    session_uuid: str
    status: SessionStatus
    turn: TurnRead | None = None  # the NEXT question (None when the interview finished)
    summary: dict | None = None  # final report once status == "completed"
