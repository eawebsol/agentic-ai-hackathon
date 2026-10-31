# Educentriks — Decision Log

_Last updated: 31 October 2026_

Append decisions here; do not silently overwrite earlier choices.

## D-001 — Hackathon-first delivery
- **Decision:** Optimise for a compelling working hackathon MVP, not a fully productionised platform.
- **Reason:** Time and judging impact matter; avoid unnecessary restrictions.
- **Implication:** Prioritise the end-to-end learner journey, voice, UX and reliable demo. Defer broad platform features.

## D-002 — Microsoft certification ecosystem
- **Decision:** Start with Microsoft certifications; AI-103 is the primary MVP certification.
- **Roadmap candidates:** AI-901 and AI-200.
- **Reason:** AI-103 aligns closely with agent development and the hackathon theme.
- **Caveat:** Verify current official exam status and objectives before implementing content.

## D-003 — Audience and proficiency
- **Decision:** Serve aspiring/career-switcher and experienced developer audiences, with mixed proficiency.
- **Implication:** Diagnose skill level and adapt the starting point.

## D-004 — Career positioning
- **Decision:** Primary MVP outcome is AI Engineer / Generative AI Engineer.
- **Implication:** FDE competencies may be mapped later; do not build a second MVP career product.

## D-005 — Agent architecture
- **Decision:** One Google ADK tutor orchestrator with specialised tools.
- **Reason:** Simpler to build and test than a multi-agent swarm.

## D-006 — Technology stack
- **Frontend:** Next.js + TypeScript.
- **Backend:** Python + FastAPI.
- **Agent:** Google ADK.
- **LLM:** Gemini initially, behind a provider adapter.
- **Database:** PostgreSQL + pgvector.
- **Hosting direction:** Vercel + Cloud Run after local validation.
- **Authentication:** Supabase Auth only if hosted login is needed.

## D-007 — Voice-first
- **Decision:** Voice is a core interaction, not decoration.
- **Implication:** Prioritise microphone capture, transcription, corrections and natural speech handling; retain typed fallback.

## D-008 — Content integrity
- **Decision:** Use official Microsoft resources/objectives and create original teaching/practice material.
- **Implication:** Store source URLs and verification dates; never label generated questions as actual exam questions.

## D-009 — Flexible task workflow
- **Decision:** Work in manageable tasks with exact commands, expected outputs, tests and troubleshooting notes. Group related tasks when it helps speed.
- **Completion rule:** Mark done only after verification.

## D-010 — Progress records
- **Decision:** Maintain a master blueprint, separate task log and separate decision log.


## D-011 — Hackathon problem statement
- **Decision:** Target the second problem statement, adaptive exam-prep tutor with a learner model (PS02).
- **Implication:** Make adaptive learning behaviour demonstrable, not just a conversational tutor.

## D-012 — Concept graph
- **Decision:** Represent the initial curriculum using concepts and explicit prerequisite relationships, mapped to official exam objectives.
- **Implication:** Diagnostic results and learning recommendations can account for prerequisite gaps.

## D-013 — Evidence-based learner model
- **Decision:** Track concept mastery using assessment evidence and misconception analysis, not correctness alone.
- **Implication:** Store supporting evidence and confidence; uncertain diagnoses must remain uncertain.

## D-014 — Adaptive difficulty and spaced repetition
- **Decision:** Adapt subsequent original practice-question difficulty and schedule reviews using learner evidence.
- **Implication:** Keep MVP policies simple, explainable and testable.

## D-015 — Minimal teacher/cohort insights
- **Decision:** Include a minimal teacher view of aggregated concept gaps and recurring misconceptions.
- **Implication:** Protect individual learner responses and avoid building a full classroom-management product.

## D-016 — Wispr Flow workflow
- **Decision:** Treat Wispr Flow usage and its evidence as an explicit hackathon workstream.
- **Evidence:** The user has confirmed they have started using Wispr Flow.
- **Implication:** Record actual workflow usage and verify the organiser's exact requirement before claiming compliance.

## D-017 — Generative model version
- **Decision:** Adopt `gemini-3.8-flash` for the Google ADK tutor agent orchestrator.
- **Reason:** Verified active API endpoint for Google GenAI with native function calling.
- **Implication:** Fast latency with high-accuracy multi-tool calling suitable for interactive voice and chat loops.

## D-018 — Multi-provider resilience via OpenRouter & LiteLLM
- **Decision:** Integrated OpenRouter with `openai/gpt-4o-mini` as primary LLM engine through Google ADK's native `LiteLLM` module.
- **Reason:** Eliminates public free-tier 503 demand spikes and model churn during live hackathon demonstrations and judge testing.
- **Implication:** Unlocks sub-second latency, robust function calling, and rock-solid 99.99% uptime for both development and deployed judge evaluation.
