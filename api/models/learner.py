from datetime import datetime, timezone
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class LearnerCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    current_role: str | None = None
    experience_level: str = "beginner"
    target_certification: str = "AI-103"
    learning_preferences: list[str] = Field(default_factory=list)


class Learner(LearnerCreate):
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
