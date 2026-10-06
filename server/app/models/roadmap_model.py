from uuid import uuid4
from typing import Literal
from datetime import datetime
from pydantic import BaseModel, Field
from app.utils.datetime_utils import _now

RoadmapStatus = Literal["pending", "processing", "ready", "failed"]

class RoadmapModel(BaseModel):
    uuid: str = Field(default_factory=lambda: str(uuid4()))
    user_uuid: str
    session_uuid: str
    status: Literal['pending','processing','ready','failed'] = 'pending'
    content: dict | None = None
    error: str | None = None
    error: str | None = None
    created_at: datetime = Field(default_factory=_now)
    updated_at: datetime = Field(default_factory=_now)