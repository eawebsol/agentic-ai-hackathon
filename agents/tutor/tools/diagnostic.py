"""
agents/tutor/tools/diagnostic.py
Diagnostic tool — select questions and record evidence from learner responses.
"""

import json
from uuid import uuid4
from datetime import datetime, timezone

from api.database import get_connection


def run_diagnostic(
    learner_id: str,
    concept_slug: str,
    learner_answer: str,
    question_stem: str,
    question_difficulty: str = "intermediate",
) -> dict:
    """
    Records a diagnostic question and the learner's answer as an assessment event.

    Use this during the onboarding diagnostic phase to probe the learner's
    understanding across AI-103 skill areas. Each call records one
    question-answer pair and returns a prompt for you to evaluate the response.

    Do NOT evaluate correctness yourself without evidence. Use evaluate_response
    after this tool to apply the rubric and record mastery evidence.

    Args:
        learner_id: UUID of the learner (string form).
        concept_slug: Slug of the concept being diagnosed (e.g. "rag-retrieval").
        learner_answer: The learner's answer text.
        question_stem: The question you posed to the learner.
        question_difficulty: "beginner", "intermediate", or "advanced".

    Returns:
        A dict with the saved response_id, assessment_id and a status message.
    """
    if question_difficulty not in ("beginner", "intermediate", "advanced"):
        question_difficulty = "intermediate"

    now = datetime.now(timezone.utc)

    with get_connection() as conn:
        # Look up concept
        concept = conn.execute(
            "SELECT id FROM concepts WHERE slug = %s",
            (concept_slug,),
        ).fetchone()
        concept_id = str(concept["id"]) if concept else None

        # Create or reuse today's diagnostic assessment for this learner
        assessment = conn.execute(
            """
            SELECT id FROM assessments
            WHERE learner_id = %s::uuid
              AND assessment_type = 'diagnostic'
              AND status = 'in_progress'
            ORDER BY started_at DESC
            LIMIT 1
            """,
            (learner_id,),
        ).fetchone()

        if assessment:
            assessment_id = str(assessment["id"])
        else:
            assessment_id = str(uuid4())
            conn.execute(
                """
                INSERT INTO assessments (id, learner_id, assessment_type,
                    certification, status, started_at, metadata)
                VALUES (%s::uuid, %s::uuid, 'diagnostic', 'AI-103',
                    'in_progress', %s, %s::jsonb)
                """,
                (
                    assessment_id,
                    learner_id,
                    now,
                    json.dumps({}),
                ),
            )

        # Save the original question
        question_id = str(uuid4())
        conn.execute(
            """
            INSERT INTO questions (id, concept_id, stem, question_type, difficulty,
                rubric, metadata)
            VALUES (%s::uuid, %s::uuid, %s, 'short_answer', %s,
                %s::jsonb, %s::jsonb)
            """,
            (
                question_id,
                concept_id,
                question_stem,
                question_difficulty,
                json.dumps({
                    "technical_correctness": 40,
                    "explanation_reasoning": 25,
                    "appropriate_use_case": 20,
                    "security_responsible_ai": 15,
                }),
                json.dumps({"source": "diagnostic", "concept_slug": concept_slug}),
            ),
        )

        # Save the learner's response (score/feedback populated by evaluate_response)
        response_id = str(uuid4())
        conn.execute(
            """
            INSERT INTO responses (id, assessment_id, question_id, learner_id,
                answer, evidence, answered_at)
            VALUES (%s::uuid, %s::uuid, %s::uuid, %s::uuid, %s, %s::jsonb, %s)
            """,
            (
                response_id,
                assessment_id,
                question_id,
                learner_id,
                learner_answer,
                json.dumps([]),
                now,
            ),
        )

        conn.commit()

    return {
        "status": "recorded",
        "response_id": response_id,
        "assessment_id": assessment_id,
        "question_id": question_id,
        "concept_slug": concept_slug,
        "message": (
            "Response recorded. Now call evaluate_response with this "
            "response_id to score and generate feedback."
        ),
    }

