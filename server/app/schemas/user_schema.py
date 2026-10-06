from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

class UserCreate(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=2, max_length=100)
    password: str = Field(min_length=8, max_length=72)

    @field_validator('password')
    @classmethod
    def _bcyrpt_limit(cls, v: str) -> str:
        if len(v.encode('utf-8')) > 72:
            raise ValueError("Password must be at most 72 bytes")
        return v




class UserUpdate(BaseModel):
        """Only fields a user may change about themselves (no roles / is_active here)."""
        full_name: str | None = Field(default=None, min_length=2, max_length=100)



class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    uuid: str
    email: EmailStr
    full_name: str
    is_active: bool
    roles: list[str]
    created_at: datetime