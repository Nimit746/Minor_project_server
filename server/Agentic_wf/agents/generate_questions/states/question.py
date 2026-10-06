from pydantic import BaseModel
from typing import Literal

class Question(BaseModel):
    id: str
    topic: str
    difficulty: str
    question_type: Literal["mcq", "coding", "open_ended"]
    question_text: str
    options: list[str] | None = None  # for MCQ
    correct_answer: str | None = None  # for MCQ
    rubric: str | None = None  # for open_ended/coding