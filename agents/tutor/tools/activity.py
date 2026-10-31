"""
agents/tutor/tools/activity.py
Next-activity tool — recommend the next learning activity based on evidence.
"""

from api.database import get_connection


def get_next_activity(learner_id: str, certification_code: str = "AI-103") -> dict:
    """
    Recommends the next learning activity from the learner's active plan.

    Selection logic (deterministic):
      1. Find the active plan for the certification.
      2. Return the first 'pending' or 'in_progress' activity by sequence_order.
      3. Prioritise activities whose concept has a due review (spaced repetition).
      4. If all activities are complete, congratulate the learner and suggest revision.

    Always explain to the learner why this activity comes next
    (e.g. "this concept is a prerequisite" or "you need to revise this area").

    Args:
        learner_id: UUID of the learner.
        certification_code: Target certification, e.g. "AI-103".

    Returns:
        The recommended activity dict, or a completion message.
    """
    from datetime import date

    today = date.today()

    with get_connection() as conn:
        # Find the active plan
        plan = conn.execute(
            """
            SELECT id FROM learning_plans
            WHERE learner_id = %s::uuid
              AND certification = %s
              AND status = 'active'
            ORDER BY created_at DESC
            LIMIT 1
            """,
            (learner_id, certification_code),
        ).fetchone()

        if plan is None:
            return {
                "status": "no_plan",
                "message": (
                    "No active learning plan found. "
                    "Call generate_learning_plan to create one."
                ),
            }

        plan_id = str(plan["id"])

        # Check for overdue review activities first
        overdue_review = conn.execute(
            """
            SELECT la.id, la.concept_id, la.activity_type, la.title,
                   la.sequence_order, c.slug AS concept_slug, c.name AS concept_name,
                   mr.status AS mastery_status, rs.due_date
            FROM review_schedules rs
            JOIN concepts c ON rs.concept_id = c.id
            JOIN learning_activities la
                ON la.concept_id = c.id AND la.plan_id = %s::uuid
            LEFT JOIN mastery_records mr
                ON mr.concept_id = c.id AND mr.learner_id = %s::uuid
            WHERE rs.learner_id = %s::uuid
              AND rs.due_date <= %s
              AND rs.completed_at IS NULL
              AND la.status IN ('pending', 'in_progress')
            ORDER BY rs.due_date ASC
            LIMIT 1
            """,
            (plan_id, learner_id, learner_id, today),
        ).fetchone()

        if overdue_review:
            return _format_activity(overdue_review, reason="review_due", due_date=str(overdue_review["due_date"]))

        # Otherwise return next pending activity by sequence
        next_activity = conn.execute(
            """
            SELECT la.id, la.concept_id, la.activity_type, la.title,
                   la.sequence_order, la.description,
                   c.slug AS concept_slug, c.name AS concept_name,
                   c.difficulty,
                   COALESCE(mr.status, 'not_assessed') AS mastery_status
            FROM learning_activities la
            JOIN concepts c ON la.concept_id = c.id
            LEFT JOIN mastery_records mr
                ON mr.concept_id = c.id AND mr.learner_id = %s::uuid
            WHERE la.plan_id = %s::uuid
              AND la.status IN ('pending', 'in_progress')
            ORDER BY la.sequence_order ASC
            LIMIT 1
            """,
            (learner_id, plan_id),
        ).fetchone()

        if next_activity is None:
            # Count completed activities
            completed = conn.execute(
                "SELECT COUNT(*) AS cnt FROM learning_activities WHERE plan_id = %s::uuid AND status = 'completed'",
                (plan_id,),
            ).fetchone()
            return {
                "status": "plan_complete",
                "completed_activities": completed["cnt"] if completed else 0,
                "message": (
                    "All activities in the current plan are complete. "
                    "Congratulate the learner and suggest a full revision "
                    "or attempting a practice exam."
                ),
            }

    return _format_activity(next_activity, reason="next_in_sequence")


def _format_activity(row, reason: str, due_date: str | None = None) -> dict:
    return {
        "status": "activity_found",
        "activity_id": str(row["id"]),
        "concept_slug": row["concept_slug"],
        "concept_name": row["concept_name"],
        "activity_type": row["activity_type"],
        "title": row["title"],
        "sequence_order": row["sequence_order"],
        "mastery_status": row.get("mastery_status", "not_assessed"),
        "reason": reason,
        "due_date": due_date,
        "message": (
            f"Next activity: '{row['title']}'. "
            f"Reason: {reason.replace('_', ' ')}. "
            "Explain why this activity is recommended before starting it."
        ),
    }

