from uuid import uuid4
from click import style
from typing import Literal
from datetime import datetime
from pydantic import BaseModel, Field
from app.utils.datetime_utils import _now

SessionStatus = Literal["active", "completed", "abandoned", "failed"]

class Turn(BaseModel):
    seq: int
    question_uuid: str = Field(default_factory=lambda: str(uuid4()))
    topic: str
    qtype: Literal['mcq','coding','theory']
    difficulty: str
    prompt: str
    asked_at: datetime = Field(default_factory=_now)
    answered_at: datetime | None = None
    score: float | None = None
    feedback: dict | None = None
    answer: str | None = None
    options: list[str] | None = None
    meta: dict | None = None



class InterviewSessionModel(BaseModel):
    uuid: str = Field(default_factory=lambda : str(uuid4()))
    user_uuid: str
    resume_uuid: str
    role: str
    target_company: str | None = None
    difficulty: str = 'medium'
    status: Literal['active','completed','abandoned','failed'] = 'active'
    turns: list[Turn] = Field(default_factory=list)
    summary: dict | None = None
    created_at: datetime = Field(default_factory=_now)
    updated_at: datetime = Field(default_factory=_now)
