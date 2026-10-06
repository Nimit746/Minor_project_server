from uuid import uuid4
from datetime import datetime
from app.utils.datetime_utils import _now
from pydantic import BaseModel, Field, EmailStr

class UserModel(BaseModel):
    """Mirrors exactly what is stored in the 'users' collection."""
    uuid: str = Field(default_factory=lambda: str(uuid4()))
    email: EmailStr
    full_name: str
    hashed_password: str
    is_active: bool = True
    is_verified: bool = False
    roles: list[str] = Field(default_factory=lambda: ['user'])
    created_at: datetime = Field(default_factory=_now)
    updated_at: datetime = Field(default_factory=_now)