from datetime import datetime, timezone
from typing import Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class ConceptCreate(BaseModel):
    slug: str = Field(min_length=2, max_length=100)
    name: str = Field(min_length=2, max_length=150)
    description: str = Field(min_length=10)
    certification: str = Field(default="AI-103", max_length=50)
    domain: str = Field(min_length=2, max_length=100)
    difficulty: Literal["beginner", "intermediate", "advanced"] = "beginner"
    learning_objectives: list[str] = Field(default_factory=list)
    prerequisite_concept_ids: list[UUID] = Field(default_factory=list)


class Concept(ConceptCreate):
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
