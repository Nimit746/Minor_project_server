from pydantic import BaseModel, Field

class ResumeAnalysis(BaseModel):
    """Structured information extracted from a candidate resume."""
    skills: list[str] = Field(default_factory=list)
    primary_language: str | None = None
    experience_level: str | None = None
    project_domains: list[str] = Field(default_factory=list)
    recommended_topics: list[str] = Field(default_factory=list)