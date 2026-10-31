"""
agents/tutor/tools/mastery.py
Mastery tools — update concept mastery, adapt question difficulty,
and schedule spaced-repetition reviews.
"""

import json
from datetime import date, datetime, timezone, timedelta

from api.database import get_connection


# Mastery transition rules — deterministic, not LLM-decided
_MASTERY_THRESHOLDS = {
    "proficient": 75.0,
    "developing": 50.0,
    "needs_revision": 0.0,
}


def update_mastery(
    learner_id: str,
    concept_slug: str,
    response_id: str,
    score: float,
    evidence_note: str,
) -> dict:
    """
    Updates the concept-level mastery record using assessment evidence.

    Mastery transitions follow deterministic score thresholds:
      - proficient:     composite score ≥ 75
      - developing:     composite score ≥ 50
      - needs_revision: composite score < 50

    Do NOT change mastery solely because the learner answered correctly
    without evaluating reasoning quality. Always base the call on a scored
    response (response_id required).

    Args:
        learner_id: UUID of the learner.
        concept_slug: Slug of the concept being updated.
        response_id: UUID of the scored response that provides evidence.
        score: Composite score from evaluate_response (0–100).
        evidence_note: Brief description of the evidence for this update.

    Returns:
        Updated mastery record dict.
    """
    # Determine new status from score
    if score >= _MASTERY_THRESHOLDS["proficient"]:
        new_status = "proficient"
    elif score >= _MASTERY_THRESHOLDS["developing"]:
        new_status = "developing"
    else:
        new_status = "needs_revision"

    confidence = round(score / 100.0, 2)
    now = datetime.now(timezone.utc)

    evidence_entry = {
        "response_id": response_id,
        "score": score,
        "note": evidence_note,
        "assessed_at": now.isoformat(),
    }

    with get_connection() as conn:
        concept = conn.execute(
            "SELECT id FROM concepts WHERE slug = %s", (concept_slug,)
        ).fetchone()

        if concept is None:
            return {"error": f"Concept '{concept_slug}' not found."}

        concept_id = str(concept["id"])

        # Upsert mastery record, appending new evidence
        row = conn.execute(
            """
            INSERT INTO mastery_records (
                learner_id, concept_id, status, evidence,
                confidence, last_assessed_at
            )
            VALUES (
                %s::uuid, %s::uuid, %s,
                %s::jsonb, %s, %s
            )
            ON CONFLICT (learner_id, concept_id) DO UPDATE SET
                status           = EXCLUDED.status,
                evidence         = mastery_records.evidence || EXCLUDED.evidence,
                confidence       = EXCLUDED.confidence,
                last_assessed_at = EXCLUDED.last_assessed_at,
                updated_at       = now()
            RETURNING id, status, confidence, last_assessed_at, updated_at
            """,
            (
                learner_id,
                concept_id,
                new_status,
                json.dumps([evidence_entry]),
                confidence,
                now,
            ),
        ).fetchone()
        conn.commit()

    return {
        "mastery_id": str(row["id"]),
        "learner_id": learner_id,
        "concept_slug": concept_slug,
        "new_status": row["status"],
        "confidence": float(row["confidence"]),
        "last_assessed_at": row["last_assessed_at"].isoformat(),
        "score_used": score,
        "message": (
            f"Mastery updated to '{new_status}' based on score {score:.1f}. "
            "Consider calling schedule_review if the concept needs reinforcement."
        ),
    }


def adapt_question_difficulty(
    learner_id: str,
    concept_slug: str,
) -> dict:
    """
    Selects the appropriate difficulty for the next practice question on a concept.

    The selection is deterministic, based on current mastery and prerequisite
    readiness — not chosen arbitrarily by the model. Explain the difficulty
    choice to the learner.

    Args:
        learner_id: UUID of the learner.
        concept_slug: Slug of the concept to practise next.

    Returns:
        A dict with recommended difficulty and the rationale.
    """
    with get_connection() as conn:
        mastery = conn.execute(
            """
            SELECT mr.status, mr.confidence
            FROM mastery_records mr
            JOIN concepts c ON mr.concept_id = c.id
            WHERE mr.learner_id = %s::uuid AND c.slug = %s
            """,
            (learner_id, concept_slug),
        ).fetchone()

        # Check prerequisite readiness
        unmet_prereqs = conn.execute(
            """
            SELECT COUNT(*) AS cnt
            FROM concept_prerequisites cp
            JOIN concepts prereq ON cp.prerequisite_id = prereq.id
            LEFT JOIN mastery_records mr
                ON mr.concept_id = cp.prerequisite_id
               AND mr.learner_id = %s::uuid
            WHERE cp.concept_id = (SELECT id FROM concepts WHERE slug = %s)
              AND (mr.status IS NULL OR mr.status IN ('not_assessed', 'needs_revision'))
            """,
            (learner_id, concept_slug),
        ).fetchone()

    unmet_count = unmet_prereqs["cnt"] if unmet_prereqs else 0

    if unmet_count > 0:
        difficulty = "beginner"
        rationale = (
            f"{unmet_count} prerequisite concept(s) are not yet mastered. "
            "Starting with beginner difficulty to build foundations first."
        )
    elif mastery is None or mastery["status"] == "not_assessed":
        difficulty = "beginner"
        rationale = "Concept not yet assessed — starting at beginner difficulty."
    elif mastery["status"] == "needs_revision":
        difficulty = "beginner"
        rationale = "Recent assessment shows the concept needs revision — using beginner difficulty."
    elif mastery["status"] == "developing":
        difficulty = "intermediate"
        rationale = "Learner is developing this concept — stepping up to intermediate difficulty."
    else:  # proficient
        difficulty = "advanced"
        rationale = "Learner has demonstrated proficiency — using advanced difficulty to challenge and consolidate."

    return {
        "concept_slug": concept_slug,
        "recommended_difficulty": difficulty,
        "rationale": rationale,
        "unmet_prerequisites": unmet_count,
    }


def schedule_review(
    learner_id: str,
    concept_slug: str,
    current_mastery_status: str,
) -> dict:
    """
    Creates or updates a spaced-repetition review activity for a concept.

    Use this after a mastery update when the concept needs reinforcement
    (status is 'needs_revision' or 'developing'). The review interval
    is determined by the mastery status using a simple deterministic policy.

    Interval policy:
      - needs_revision: review in 1 day
      - developing:     review in 3 days
      - proficient:     review in 7 days (consolidation)

    Args:
        learner_id: UUID of the learner.
        concept_slug: Slug of the concept to schedule.
        current_mastery_status: 'needs_revision', 'developing', or 'proficient'.

    Returns:
        The created or updated review schedule record.
    """
    interval_map = {
        "needs_revision": 1,
        "developing": 3,
        "proficient": 7,
    }
    interval_days = interval_map.get(current_mastery_status, 3)
    due_date = date.today() + timedelta(days=interval_days)

    with get_connection() as conn:
        concept = conn.execute(
            "SELECT id FROM concepts WHERE slug = %s", (concept_slug,)
        ).fetchone()

        if concept is None:
            return {"error": f"Concept '{concept_slug}' not found."}

        concept_id = str(concept["id"])

        row = conn.execute(
            """
            INSERT INTO review_schedules (learner_id, concept_id, due_date, interval_days)
            VALUES (%s::uuid, %s::uuid, %s, %s)
            RETURNING id, due_date, interval_days, created_at
            """,
            (learner_id, concept_id, due_date, interval_days),
        ).fetchone()
        conn.commit()

    return {
        "schedule_id": str(row["id"]),
        "concept_slug": concept_slug,
        "due_date": row["due_date"].isoformat(),
        "interval_days": row["interval_days"],
        "mastery_status": current_mastery_status,
        "message": (
            f"Review scheduled for {row['due_date'].isoformat()} "
            f"({interval_days} day(s) from today). "
            "This will appear in the learner's plan."
        ),
    }

