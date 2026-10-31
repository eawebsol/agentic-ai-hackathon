"""
agents/tutor/tools/planning.py
Learning plan tool — generate and persist a personalised learning plan.
"""

import json
from uuid import uuid4
from datetime import datetime, timezone

from api.database import get_connection


def generate_learning_plan(
    learner_id: str,
    certification_code: str = "AI-103",
    ordered_concept_slugs: list[str] | None = None,
) -> dict:
    """
    Creates a personalised learning plan and its ordered activities,
    based on the learner's diagnostic results and concept gap analysis.

    Call this after the diagnostic is complete and mastery records have been
    updated. The plan's activity order should reflect:
      1. Prerequisite concepts first
      2. Weakest concepts (needs_revision) before developing ones
      3. Proficient concepts last (for consolidation, if time allows)

    If ordered_concept_slugs is not provided, the tool will derive an order
    from mastery status automatically.

    Args:
        learner_id: UUID of the learner.
        certification_code: Target certification, e.g. "AI-103".
        ordered_concept_slugs: Optional explicit ordered list of concept slugs
            to include as activities. If None, auto-ordered by mastery gap.

    Returns:
        The created plan with its list of activities.
    """
    with get_connection() as conn:
        # Deactivate any existing active plan for this cert
        conn.execute(
            """
            UPDATE learning_plans
            SET status = 'paused', updated_at = now()
            WHERE learner_id = %s::uuid
              AND certification = %s
              AND status = 'active'
            """,
            (learner_id, certification_code),
        )

        # Create new plan
        plan_id = str(uuid4())
        now = datetime.now(timezone.utc)
        conn.execute(
            """
            INSERT INTO learning_plans (id, learner_id, certification, status, created_at, updated_at)
            VALUES (%s::uuid, %s::uuid, %s, 'active', %s, %s)
            """,
            (plan_id, learner_id, certification_code, now, now),
        )

        # Determine concept order
        if ordered_concept_slugs:
            slugs = ordered_concept_slugs
        else:
            # Auto-order: needs_revision → developing → not_assessed → proficient
            status_order = {
                "needs_revision": 0,
                "not_assessed": 1,
                "developing": 2,
                "proficient": 3,
            }
            rows = conn.execute(
                """
                SELECT c.slug, c.name, c.difficulty,
                       COALESCE(mr.status, 'not_assessed') AS mastery_status
                FROM concepts c
                LEFT JOIN mastery_records mr
                    ON mr.concept_id = c.id AND mr.learner_id = %s::uuid
                WHERE c.certification = %s
                ORDER BY c.slug
                """,
                (learner_id, certification_code),
            ).fetchall()

            sorted_rows = sorted(
                rows,
                key=lambda r: (
                    status_order.get(r["mastery_status"], 1),
                    r["difficulty"],
                ),
            )
            slugs = [r["slug"] for r in sorted_rows]

        # Create learning activities
        activities_created = []
        for order, slug in enumerate(slugs, start=1):
            concept = conn.execute(
                "SELECT id, name, difficulty FROM concepts WHERE slug = %s",
                (slug,),
            ).fetchone()

            if concept is None:
                continue  # Skip unknown slugs

            mastery = conn.execute(
                """
                SELECT status FROM mastery_records
                WHERE learner_id = %s::uuid AND concept_id = %s::uuid
                """,
                (learner_id, str(concept["id"])),
            ).fetchone()

            mastery_status = mastery["status"] if mastery else "not_assessed"
            activity_type = "review" if mastery_status == "needs_revision" else "lesson"

            activity_id = str(uuid4())
            conn.execute(
                """
                INSERT INTO learning_activities (
                    id, plan_id, concept_id, activity_type,
                    title, description, sequence_order, status, metadata, created_at
                )
                VALUES (
                    %s::uuid, %s::uuid, %s::uuid, %s,
                    %s, %s, %s, 'pending', %s::jsonb, %s
                )
                """,
                (
                    activity_id,
                    plan_id,
                    str(concept["id"]),
                    activity_type,
                    f"{activity_type.capitalize()}: {concept['name']}",
                    f"Study and practise {concept['name']} (difficulty: {concept['difficulty']})",
                    order,
                    json.dumps({"mastery_at_creation": mastery_status}),
                    now,
                ),
            )
            activities_created.append({
                "activity_id": activity_id,
                "concept_slug": slug,
                "concept_name": concept["name"],
                "activity_type": activity_type,
                "sequence_order": order,
                "mastery_status": mastery_status,
            })

        conn.commit()

    return {
        "plan_id": plan_id,
        "learner_id": learner_id,
        "certification": certification_code,
        "status": "active",
        "total_activities": len(activities_created),
        "activities": activities_created,
        "message": (
            "Learning plan created. Share the plan summary with the learner "
            "and ask if they would like to start the first activity."
        ),
    }

