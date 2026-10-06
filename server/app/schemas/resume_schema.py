from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.models.resume_model import ResumeStatus

class ResumeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    uuid: str
    filename: str
    content_type: str
    size_bytes: int
    error: str | None = None
    created_at: datetime
    updated_at: datetime