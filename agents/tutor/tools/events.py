"""
agents/tutor/tools/events.py
Learning event recorder — immutable audit log of all learner interactions.
"""

import json
from datetime import datetime, timezone

from api.database import get_connection


def record_learning_event(
    learner_id: str,
    event_type: str,
    payload: dict | None = None,
) -> dict:
    """
    Records a learning event to the immutable audit log.

    Call this after significant interactions to maintain a traceable
    history of the learner's journey.

    Common event types:
      - lesson_viewed
      - diagnostic_started
      - diagnostic_completed
      - answer_submitted
      - feedback_received
      - plan_created
      - plan_revised
      - mastery_updated
      - review_scheduled
      - session_started
      - session_ended

    Args:
        learner_id: UUID of the learner.
        event_type: One of the event types listed above, or a descriptive string.
        payload: Optional dict of additional event data to persist.

    Returns:
        The saved event record with its ID and timestamp.
    """
    payload = payload or {}
    now = datetime.now(timezone.utc)

    with get_connection() as conn:
        row = conn.execute(
            """
            INSERT INTO learning_events (learner_id, event_type, payload, occurred_at)
            VALUES (%s::uuid, %s, %s::jsonb, %s)
            RETURNING id, event_type, occurred_at
            """,
            (learner_id, event_type, json.dumps(payload), now),
        ).fetchone()
        conn.commit()

    return {
        "event_id": str(row["id"]),
        "learner_id": learner_id,
        "event_type": row["event_type"],
        "occurred_at": row["occurred_at"].isoformat(),
    }


def get_teacher_dashboard(
    certification_code: str = "AI-103",
    cohort_id: str | None = None,
) -> dict:
    """
    Returns privacy-preserving aggregated learning gaps for a cohort or
    all learners on a certification.

    This view shows concept-level mastery distribution across learners.
    Individual learner responses and answers are NEVER exposed here.
    Only aggregate counts are returned.

    Args:
        certification_code: Certification to aggregate, e.g. "AI-103".
        cohort_id: Optional UUID to scope to a specific cohort.
                   If None, aggregates across all learners.

    Returns:
        A dict with concept gap distribution and recurring misconception counts.
    """
    with get_connection() as conn:
        if cohort_id:
            learner_filter = """
                JOIN cohort_memberships cm ON mr.learner_id = cm.learner_id
                WHERE cm.cohort_id = %s::uuid AND c.certification = %s
            """
            params = [cohort_id, certification_code]
        else:
            learner_filter = "WHERE c.certification = %s"
            params = [certification_code]

        concept_gaps = conn.execute(
            f"""
            SELECT c.slug, c.name, c.domain, c.difficulty,
                   COUNT(mr.id) AS assessed_count,
                   SUM(CASE WHEN mr.status = 'needs_revision' THEN 1 ELSE 0 END) AS needs_revision_count,
                   SUM(CASE WHEN mr.status = 'developing'     THEN 1 ELSE 0 END) AS developing_count,
                   SUM(CASE WHEN mr.status = 'proficient'     THEN 1 ELSE 0 END) AS proficient_count
            FROM concepts c
            LEFT JOIN mastery_records mr ON mr.concept_id = c.id
            {learner_filter}
            GROUP BY c.id, c.slug, c.name, c.domain, c.difficulty
            ORDER BY needs_revision_count DESC, developing_count DESC
            """,  # noqa: S608
            params,
        ).fetchall()

        # Top misconceptions — counts only, no individual data
        misc_params = [certification_code]
        if cohort_id:
            misc_filter = """
                JOIN cohort_memberships cm ON lm.learner_id = cm.learner_id
                WHERE cm.cohort_id = %s::uuid AND c.certification = %s
            """
            misc_params = [cohort_id, certification_code]
        else:
            misc_filter = "WHERE c.certification = %s"

        misconceptions = conn.execute(
            f"""
            SELECT c.slug, c.name,
                   COUNT(lm.id) AS occurrence_count,
                   lm.description AS misconception_description
            FROM learner_misconceptions lm
            JOIN concepts c ON lm.concept_id = c.id
            {misc_filter}
              AND lm.status IN ('suspected', 'confirmed')
            GROUP BY c.slug, c.name, lm.description
            ORDER BY occurrence_count DESC
            LIMIT 10
            """,  # noqa: S608
            misc_params,
        ).fetchall()

    return {
        "certification": certification_code,
        "cohort_id": cohort_id,
        "note": "Individual learner responses are not included. Aggregate counts only.",
        "concept_gaps": [
            {
                "concept_slug": row["slug"],
                "concept_name": row["name"],
                "domain": row["domain"],
                "difficulty": row["difficulty"],
                "assessed_count": row["assessed_count"],
                "needs_revision_count": row["needs_revision_count"],
                "developing_count": row["developing_count"],
                "proficient_count": row["proficient_count"],
            }
            for row in concept_gaps
        ],
        "top_misconceptions": [
            {
                "concept_slug": row["slug"],
                "concept_name": row["name"],
                "description": row["misconception_description"],
                "occurrence_count": row["occurrence_count"],
            }
            for row in misconceptions
        ],
    }

