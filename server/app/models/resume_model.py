from uuid import uuid4
from typing import Literal
from datetime import datetime
from pydantic import BaseModel, Field
from app.utils.datetime_utils import _now
ResumeStatus = Literal["pending", "processing", "ready", "failed"]



class ResumeModel(BaseModel):
    uuid: str = Field(default_factory=lambda: str(uuid4()))
    user_uuid : str
    filename: str
    content_type: str
    size_bytes: int
    file_path: str
    status: Literal['pending','processing','ready','failed'] = 'pending'
    error: str | None = None
    profile: dict | None = None
    created_at: datetime = Field(default_factory=_now)
    updated_at: datetime = Field(default_factory=_now)