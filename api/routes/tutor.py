"""
api/routes/tutor.py
-------------------
FastAPI routes exposing Educentriks Cognify agent capabilities:
- Learner profiles
- Personalized plans
- Next activity recommendations
- Privacy-preserving teacher/cohort insights (PS02)
"""

from uuid import UUID
from fastapi import APIRouter, HTTPException, Query

from agents.tutor.tools.profile import get_learner_profile
from agents.tutor.tools.activity import get_next_activity
from agents.tutor.tools.planning import generate_learning_plan
from agents.tutor.tools.events import get_teacher_dashboard
from agents.tutor.tools.curriculum import get_exam_objectives

router = APIRouter(prefix="/tutor", tags=["Tutor & Learning"])


@router.get("/profile/{learner_id}")
async def fetch_profile(learner_id: UUID):
    result = get_learner_profile(str(learner_id))
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@router.get("/objectives/{certification_code}")
async def fetch_objectives(certification_code: str = "AI-103"):
    result = get_exam_objectives(certification_code)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@router.post("/plan/{learner_id}")
async def create_or_refresh_plan(learner_id: UUID, certification: str = Query("AI-103")):
    return generate_learning_plan(str(learner_id), certification)


@router.get("/next-activity/{learner_id}")
async def fetch_next_activity(learner_id: UUID, certification: str = Query("AI-103")):
    return get_next_activity(str(learner_id), certification)


@router.get("/teacher/dashboard")
async def fetch_teacher_dashboard(certification: str = Query("AI-103")):
    return get_teacher_dashboard(certification)

