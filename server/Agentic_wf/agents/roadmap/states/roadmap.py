from operator import add
from typing import Annotated
from pydantic import BaseModel, Field


class SectionResource(BaseModel):
    title: str
    url: str | None = None
    type: str = "doc"  # doc, article, video, course, practice, github
    description: str | None = None


class InteractiveCheckpoint(BaseModel):
    checkpoint_id: str
    task: str
    is_completed: bool = False
    estimated_minutes: int = 45


class RoadmapSection(BaseModel):
    section_id: str
    title: str
    phase: str  # e.g., "Phase 1: Foundations & Weak Point Remediation"
    estimated_hours: float = 0.0
    focus_type: str = "core_domain"  # "weak_point_remediation" or "core_domain"
    focus_tag: str = "Core Domain"  # UI badge: "Weak Point Remediation", "Core Mastery", "Advanced"
    topics: list[str] = []
    learning_objectives: list[str] = []
    checkpoints: list[dict] = []
    search_queries: list[str] = []
    resources: list[dict] = []
    practical_exercises: list[str] = []


class Roadmap(BaseModel):
    # Candidate context inputs
    candidate_id: str = ""
    target_role: str | None = None
    available_hours_per_day: float = 2.0
    target_date: str | None = None

    # Candidate profile retrieved from MongoDB
    performance_data: list[dict] = Field(default_factory=list)
    weak_topics: list[str] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)
    is_universal: bool = False

    # Agent analysis
    learning_profile: dict = Field(default_factory=dict)
    prioritized_topics: list[dict] = Field(default_factory=list)

    # Generated sections & resources
    sections: list[dict] = Field(default_factory=list)
    resources: Annotated[list[dict], add] = Field(default_factory=list)

    # Final generated roadmap
    roadmap: dict | None = None

    # Workflow monitoring / error accumulator
    errors: Annotated[list[str], add] = Field(default_factory=list)
