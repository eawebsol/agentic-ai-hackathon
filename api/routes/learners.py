from uuid import UUID, uuid4
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, status
from psycopg.types.json import Jsonb

from api.database import get_connection
from api.models.learner import Learner, LearnerCreate

router = APIRouter(prefix="/learners", tags=["Learners"])


@router.post(
    "",
    response_model=Learner,
    status_code=status.HTTP_201_CREATED,
)
async def create_learner(payload: LearnerCreate):
    learner = Learner(
        id=uuid4(),
        **payload.model_dump(),
        created_at=datetime.now(timezone.utc),
    )

    query = """
        INSERT INTO learners (
            id, name, "current_role", experience_level,
            target_certification, learning_preferences, created_at
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING *
    """

    with get_connection() as conn:
        row = conn.execute(
            query,
            (
                learner.id,
                learner.name,
                learner.current_role,
                learner.experience_level,
                learner.target_certification,
                Jsonb(learner.learning_preferences),
                learner.created_at,
            ),
        ).fetchone()

    return Learner(**row)


@router.get("", response_model=list[Learner])
async def list_learners():
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM learners ORDER BY created_at DESC"
        ).fetchall()

    return [Learner(**row) for row in rows]


@router.get("/{learner_id}", response_model=Learner)
async def get_learner(learner_id: UUID):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM learners WHERE id = %s",
            (learner_id,),
        ).fetchone()

    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Learner not found",
        )

    return Learner(**row)
