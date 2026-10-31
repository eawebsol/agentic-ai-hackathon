"""
agents/tutor/tools/assessment.py
Assessment tools — evaluate learner responses against rubrics and
detect possible misconceptions from reasoning.
"""

import json
from datetime import datetime, timezone

from api.database import get_connection


def evaluate_response(
    response_id: str,
    technical_correctness_score: float,
    explanation_reasoning_score: float,
    appropriate_use_case_score: float,
    security_responsible_ai_score: float,
    feedback: str,
    evidence_notes: str,
) -> dict:
    """
    Evaluates a learner's recorded response against the standard rubric and
    persists the score and feedback.

    Rubric weights (must sum to 100 when multiplied):
      - Technical correctness:     40 %
      - Explanation and reasoning: 25 %
      - Appropriate use case:      20 %
      - Security / responsible AI: 15 %

    Each score argument is a value from 0.0 to 1.0 (proportion of that
    dimension earned). The composite score is computed automatically.

    Do NOT portray these scores as scientifically validated measurements.
    Always explain the evidence behind the score in the feedback.

    Args:
        response_id: UUID of the response row to update.
        technical_correctness_score: 0.0–1.0
        explanation_reasoning_score: 0.0–1.0
        appropriate_use_case_score:  0.0–1.0
        security_responsible_ai_score: 0.0–1.0
        feedback: Written feedback to return to the learner.
        evidence_notes: Brief note on what evidence drove this evaluation.

    Returns:
        Updated response dict with composite score.
    """
    # Composite weighted score (0–100)
    composite = (
        technical_correctness_score * 40
        + explanation_reasoning_score * 25
        + appropriate_use_case_score * 20
        + security_responsible_ai_score * 15
    )

    rubric_scores = {
        "technical_correctness": round(technical_correctness_score, 2),
        "explanation_reasoning": round(explanation_reasoning_score, 2),
        "appropriate_use_case": round(appropriate_use_case_score, 2),
        "security_responsible_ai": round(security_responsible_ai_score, 2),
    }

    evidence = [
        {
            "type": "rubric_evaluation",
            "notes": evidence_notes,
            "evaluated_at": datetime.now(timezone.utc).isoformat(),
        }
    ]

    with get_connection() as conn:
        row = conn.execute(
            """
            UPDATE responses
            SET score = %s,
                rubric_scores = %s::jsonb,
                feedback = %s,
                evidence = %s::jsonb
            WHERE id = %s::uuid
            RETURNING id, assessment_id, learner_id, score, feedback
            """,
            (
                round(composite, 2),
                json.dumps(rubric_scores),
                feedback,
                json.dumps(evidence),
                response_id,
            ),
        ).fetchone()
        conn.commit()

    if row is None:
        return {"error": f"Response {response_id} not found."}

    return {
        "response_id": str(row["id"]),
        "assessment_id": str(row["assessment_id"]),
        "learner_id": str(row["learner_id"]),
        "composite_score": float(row["score"]),
        "rubric_scores": rubric_scores,
        "feedback": row["feedback"],
        "message": "Score and feedback recorded. Call update_mastery if evidence supports a mastery change.",
    }


def detect_misconceptions(
    learner_id: str,
    concept_slug: str,
    response_id: str,
    misconception_description: str,
    confidence: float,
) -> dict:
    """
    Records a possible misconception identified from the learner's reasoning.

    Only call this when the learner's explanation or reasoning reveals a
    probable misunderstanding — not simply because an answer was incorrect.
    A wrong answer without explanatory reasoning is not sufficient evidence.

    Confidence must reflect your certainty (0.0 = unsure, 1.0 = certain).
    Uncertain diagnoses must remain 'suspected', not 'confirmed'.

    Args:
        learner_id: UUID of the learner.
        concept_slug: Slug of the concept the misconception relates to.
        response_id: UUID of the response that contains the evidence.
        misconception_description: Clear description of the suspected misconception.
        confidence: Your confidence that this is a genuine misconception (0.0–1.0).

    Returns:
        The saved misconception record, or {"error": "..."}.
    """
    confidence = max(0.0, min(1.0, confidence))
    status = "confirmed" if confidence >= 0.8 else "suspected"

    with get_connection() as conn:
        concept = conn.execute(
            "SELECT id FROM concepts WHERE slug = %s",
            (concept_slug,),
        ).fetchone()

        if concept is None:
            return {"error": f"Concept '{concept_slug}' not found. Cannot record misconception."}

        concept_id = str(concept["id"])

        row = conn.execute(
            """
            INSERT INTO learner_misconceptions (
                learner_id, concept_id, description,
                evidence_response_id, confidence, status, detected_at
            )
            VALUES (
                %s::uuid, %s::uuid, %s, %s::uuid, %s, %s, now()
            )
            RETURNING id, status, confidence, detected_at
            """,
            (
                learner_id,
                concept_id,
                misconception_description,
                response_id,
                confidence,
                status,
            ),
        ).fetchone()
        conn.commit()

    return {
        "misconception_id": str(row["id"]),
        "concept_slug": concept_slug,
        "description": misconception_description,
        "status": row["status"],
        "confidence": float(row["confidence"]),
        "detected_at": row["detected_at"].isoformat(),
        "message": (
            f"Misconception recorded as '{status}'. "
            "Explain this diagnosis to the learner with the evidence you observed."
        ),
    }

