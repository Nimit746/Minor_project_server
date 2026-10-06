from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.models.roadmap_model import RoadmapStatus

class RoadmapCreate(BaseModel):
    session_uuid: str


class RoadmapRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    uuid : str
    session_uuid: str
    status: RoadmapStatus
    content: dict | None = None
    error: str | None = None
    created_at: datetime
    updated_at: datetime