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
