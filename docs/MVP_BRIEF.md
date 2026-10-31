# Educentriks Cognify — MVP Brief

_Product by Educentriks_

_Last updated: 31 October 2026_

## 1. Product summary

Educentriks Cognify is a voice-first, adaptive AI certification learning coach.
It helps technical learners prepare for Microsoft AI-103 by understanding
their current knowledge, identifying skill gaps, teaching concepts using
reliable learning sources, evaluating practical understanding and adapting
the learner's next activity.

## 2. Target learner

The primary user is an individual preparing for a technical certification.

Initial learner profiles:

- Aspiring AI engineers and career switchers with foundational programming
  knowledge.
- Software, cloud and AI practitioners who already have technical experience
  but need to identify and close specific knowledge gaps.

The diagnostic determines the learner's starting level. The product must not
assume that every learner is a beginner.

## 3. Problem

A conventional study plan often treats every learner the same. Learners may
spend too much time revising familiar topics while overlooking prerequisites,
misconceptions and practical weaknesses.

They need a coach that can determine what they understand, explain what they
do not, and adjust the learning path as new evidence becomes available.

## 4. Product promise

Tell Cognify your certification goal and what you already know. It will help
you understand where you stand, what to learn next and whether your
understanding is improving.

## 5. Core learner journey

1. **Onboard:** The learner describes their background, goal and study
   availability by voice or text.
2. **Diagnose:** Cognify asks targeted questions across the selected
   certification's mapped skill areas.
3. **Understand gaps:** Cognify identifies strengths, weaknesses,
   misconceptions and areas not yet assessed.
4. **Plan:** Cognify creates a prioritised learning path based on prerequisites,
   learner evidence and available study time.
5. **Learn:** The learner asks questions and receives explanations grounded
   in curated learning resources, with source links.
6. **Practise:** The learner answers original questions or practical scenarios.
7. **Evaluate:** Cognify evaluates reasoning against an explicit rubric,
   identifies misconceptions and explains the feedback.
8. **Adapt:** The system updates mastery only when supported by assessment
   evidence and recommends the next activity.
9. **Track:** The learner sees progress and outstanding skill gaps.

## 6. Hackathon MVP capabilities

- Voice-first onboarding with typed fallback.
- Persistent learner profile.
- Adaptive diagnostic.
- Certification objective-to-skill mapping.
- Learner mastery model with evidence.
- Personalised learning plan.
- Retrieval-grounded tutor with source links.
- Original practice questions and scenario evaluation.
- Misconception-aware feedback.
- Evidence-based mastery updates.
- Next-activity recommendation.
- Progress dashboard with persisted state.

A minimal class-level learning-gap dashboard is included to address the
problem statement's teacher-dashboard requirement. It uses seeded demo
learners and highlights cohort-level mastery and common weak concepts.
It does not become a full classroom-management system or displace the
individual learner journey.

## 7. Agent behaviour

Cognify uses one orchestrating agent with specialised tools for profile
management, diagnostics, curriculum retrieval, resource search, planning,
assessment, mastery updates and next-activity selection.

The agent must:

- Ask only necessary follow-up questions.
- Confirm ambiguous or consequential profile changes.
- Ground certification explanations in traceable sources.
- Distinguish official material from generated explanations and practice.
- Never present generated questions as actual certification exam questions.
- Explain uncertainty and avoid unsupported mastery claims.

## 8. Initial certification scope

Primary MVP: Microsoft AI-103.

Before publishing certification-specific content, verify the current exam
title, code, status, objectives and weightings against official Microsoft
sources. Record source URLs and verification dates.

## 9. Non-goals

- Multi-certification catalogue.
- Job marketplace or placement platform.
- Payments or exam registration.
- Full cloud coding-lab infrastructure.
- Enterprise administration and classroom management.
- Fine-tuning or hosting large language models locally.
- Multi-agent swarm architecture.

## 10. MVP success criteria

A new learner can complete the full journey from onboarding to an adapted
next activity in a repeatable demo session.

The demo must show:

- Two learners with different backgrounds receiving meaningfully different
  diagnostics or plans.
- A grounded explanation with visible source links.
- Practice feedback that explains the learner's reasoning.
- A mastery change supported by assessment evidence.
- A next activity that responds to that change.
- Progress that remains available after a page refresh.

## 11. Product identity

- Parent organisation: **Educentriks**
- Product: **Educentriks Cognify**
- Product category: Adaptive AI certification learning coach
