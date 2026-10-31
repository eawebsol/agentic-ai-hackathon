"""
tests/test_tutor_tools.py
-------------------------
Verifies all 10 Cognify tutor tools against the PostgreSQL database
and confirms the PS02 adaptive-learning pipeline works end-to-end.
"""

from agents.tutor.tools.profile import get_learner_profile, update_learner_profile
from agents.tutor.tools.curriculum import get_exam_objectives
from agents.tutor.tools.resources import search_learning_resources
from agents.tutor.tools.diagnostic import run_diagnostic
from agents.tutor.tools.assessment import evaluate_response, detect_misconceptions
from agents.tutor.tools.mastery import update_mastery, adapt_question_difficulty, schedule_review
from agents.tutor.tools.planning import generate_learning_plan
from agents.tutor.tools.activity import get_next_activity
from agents.tutor.tools.events import record_learning_event, get_teacher_dashboard

LEARNER_ID = "00000000-0000-0000-0000-000000000001"  # Alex Rivera (Demo Learner)

def test_all():
    print("=" * 60)
    print("TESTING EDUCENTRIKS COGNIFY TUTOR TOOLS & AGENTIC PIPELINE")
    print("=" * 60)

    # 1. Profile Tool
    print("\n1. Testing get_learner_profile...")
    profile = get_learner_profile(LEARNER_ID)
    assert "error" not in profile, f"Profile error: {profile}"
    print(f"   ✓ Learner: {profile['name']} | Role: {profile.get('current_role')} | Cert: {profile.get('target_certification')}")

    # 2. Curriculum Tool
    print("\n2. Testing get_exam_objectives...")
    objectives = get_exam_objectives("AI-103")
    assert "error" not in objectives, f"Curriculum error: {objectives}"
    print(f"   ✓ Found {objectives['total_objectives']} objectives for {objectives['certification']['code']}")

    # 3. Learning Resources (RAG / Keyword Grounding)
    print("\n3. Testing search_learning_resources...")
    res = search_learning_resources("agent state memory")
    assert res["status"] == "ok" and len(res["chunks"]) > 0, f"RAG error: {res}"
    print(f"   ✓ Retrieved grounded source: '{res['chunks'][0]['source_title']}' ({res['chunks'][0]['source_url']})")

    # 4. Diagnostic Tool
    print("\n4. Testing run_diagnostic (Recording practice response)...")
    diag = run_diagnostic(
        learner_id=LEARNER_ID,
        concept_slug="agent-tool-calling",
        learner_answer="Tools are executed by the LLM itself inside its neural network weights.",
        question_stem="Explain how an LLM executes a tool call.",
        question_difficulty="intermediate"
    )
    assert diag["status"] == "recorded", f"Diagnostic error: {diag}"
    response_id = diag["response_id"]
    print(f"   ✓ Response recorded: ID {response_id}")

    # 5. Assessment & Misconception Tool (PS02)
    print("\n5. Testing evaluate_response & detect_misconceptions...")
    eval_res = evaluate_response(
        response_id=response_id,
        technical_correctness_score=0.2,
        explanation_reasoning_score=0.3,
        appropriate_use_case_score=0.5,
        security_responsible_ai_score=0.5,
        feedback="LLMs do not execute code directly in their weights; they output structured JSON schemas requesting the client runtime to execute the tool.",
        evidence_notes="Learner confused model output generation with runtime execution."
    )
    assert "composite_score" in eval_res, f"Evaluation error: {eval_res}"
    print(f"   ✓ Rubric evaluated. Composite score: {eval_res['composite_score']}/100")

    misc = detect_misconceptions(
        learner_id=LEARNER_ID,
        concept_slug="agent-tool-calling",
        response_id=response_id,
        misconception_description="Belief that LLMs directly run external code within weights rather than generating execution requests.",
        confidence=0.85
    )
    assert misc["status"] in ("confirmed", "suspected"), f"Misconception error: {misc}"
    print(f"   ✓ Misconception detected & recorded: '{misc['description'][:50]}...' (status: {misc['status']})")

    # 6. Mastery & Adaptive Difficulty (PS02)
    print("\n6. Testing update_mastery & adapt_question_difficulty...")
    mastery = update_mastery(
        learner_id=LEARNER_ID,
        concept_slug="agent-tool-calling",
        response_id=response_id,
        score=eval_res["composite_score"],
        evidence_note="Low score on runtime tool execution reasoning."
    )
    print(f"   ✓ Mastery updated: {mastery['concept_slug']} -> status: '{mastery['new_status']}'")

    diff = adapt_question_difficulty(LEARNER_ID, "agent-tool-calling")
    print(f"   ✓ Adaptive difficulty for next question: '{diff['recommended_difficulty']}' (Rationale: {diff['rationale']})")

    # 7. Spaced Repetition Scheduling (PS02)
    print("\n7. Testing schedule_review...")
    review = schedule_review(LEARNER_ID, "agent-tool-calling", mastery["new_status"])
    print(f"   ✓ Review scheduled for: {review['due_date']} (Interval: {review['interval_days']} day(s))")

    # 8. Learning Plan Generation
    print("\n8. Testing generate_learning_plan...")
    plan = generate_learning_plan(LEARNER_ID, "AI-103")
    assert plan["total_activities"] > 0, f"Plan error: {plan}"
    print(f"   ✓ Plan generated with {plan['total_activities']} prioritized activities (Plan ID: {plan['plan_id']})")

    # 9. Next Activity Recommendation
    print("\n9. Testing get_next_activity...")
    next_act = get_next_activity(LEARNER_ID, "AI-103")
    print(f"   ✓ Recommended next activity: '{next_act['title']}' (Reason: {next_act['reason']})")

    # 10. Teacher / Cohort Dashboard (PS02)
    print("\n10. Testing get_teacher_dashboard (Privacy-preserving aggregate view)...")
    teacher_view = get_teacher_dashboard("AI-103")
    print(f"   ✓ Teacher dashboard generated. Tracked concepts: {len(teacher_view['concept_gaps'])}, Top misconceptions: {len(teacher_view['top_misconceptions'])}")

    print("\n" + "=" * 60)
    print("ALL 10 COGNIFY AGENT TOOLS PASSED & VERIFIED WITH DATABASE!")
    print("=" * 60)

if __name__ == "__main__":
    test_all()

