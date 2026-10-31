# Educentriks — Agentic AI Hackathon Project Blueprint

_Last updated: 31 October 2026_

> **North star:** Build a compelling, reliable hackathon MVP first. This is a flexible working blueprint, not a rigid production specification. Complete and test a coherent learner journey before expanding the product.

## 1. Product direction

Educentriks is a **voice-first adaptive certification learning coach**. A learner explains their background and goal; Educentriks diagnoses their current ability, creates a personalised learning plan, teaches using grounded sources, assesses practical understanding, updates a learner model and recommends the next activity.

### Initial audience
- Aspiring AI engineers and career switchers.
- Existing software/cloud developers and experienced engineers.
- Mixed proficiency: use a diagnostic to choose an appropriate starting point.

### Certification focus
- **Primary MVP:** Microsoft AI-103 — Azure AI Apps and Agents Developer Associate.
- **Later roadmap:** AI-901 and AI-200, subject to checking their current official status and exam objectives.
- Verify exam title, code, objectives, weightings, availability and retirement status from current Microsoft sources before publishing content. Keep source URLs and verification dates.

### Career positioning
The MVP primarily supports the AI Engineer / Generative AI Engineer pathway. FDE competencies can be included in a future skills map, but do not build a second career product for the hackathon.

## 2. Hackathon-first principles

1. Prioritise a working end-to-end demo over broad feature coverage.
2. Make voice a prominent, meaningful input; retain typed fallback.
3. Demonstrate actual agent tool use, retrieval, assessment and learner-state updates—not just chat.
4. Polish the onboarding, diagnostic, learning plan and progress experience.
5. Ground certification claims in official Microsoft sources.
6. Use one orchestrating agent with tools; avoid an unnecessary multi-agent swarm.
7. Keep costs and infrastructure low. Use hosted inference; do not attempt large local models on the current laptop.
8. Keep a repeatable demo path working throughout development.

The event's Wispr Flow requirement, judging weights, deadline and submission rules must be rechecked against organiser material before final submission.

## 3. MVP scope

### Must-have
- [ ] Voice-first onboarding; capture background, goal, experience and available study time.
- [ ] Persistent learner profile with correction support.
- [ ] Adaptive diagnostic across several AI-103 skill areas.
- [ ] Skill-gap summary, including not-yet-assessed areas.
- [ ] Personalised learning plan.
- [ ] Tutor grounded in Microsoft Learn resources, with source links.
- [ ] Original practice questions and practical scenarios.
- [ ] Rubric-based feedback and evidence-backed mastery updates.
- [ ] Next-activity recommendation based on learner evidence.
- [ ] Progress dashboard and persistence across refresh/session.

### Nice-to-have, only if time permits
- [ ] Spoken tutor responses / text-to-speech.
- [ ] Small guided coding or architecture lab.
- [ ] Revision mode for weak areas.
- [ ] Sample learner/demo mode and shareable learning plan.

### Out of scope for hackathon MVP
- Full multi-provider certification catalogue.
- Job board, placement marketplace or recruiter portal.
- Community, leaderboard or mentor-booking features.
- Exam registration and payments.
- Full cloud code-execution lab platform.
- Fine-tuning or local large-model hosting.
- Multi-agent swarm and enterprise admin analytics.

## 4. Primary demo journey

1. Learner speaks: “I’m a Python developer. I know APIs, but I’m new to AI agents. I want to prepare for AI-103.”
2. Educentriks extracts profile details and asks only necessary follow-ups.
3. Learner completes a short diagnostic.
4. Educentriks identifies gaps and creates a tailored plan.
5. Learner asks a voice question about RAG, tools or agent orchestration.
6. Tutor retrieves relevant Microsoft learning material and answers with sources.
7. Learner completes an original scenario question or mini-exercise.
8. Tutor evaluates the response against a rubric and updates mastery.
9. Dashboard changes and recommends the next activity.

**Demo acceptance:** this journey works from a clean browser session with prepared demo data. Typed input is available if microphone or speech services fail.

## 5. Architecture

Use a **modular monolith** with one tutor orchestrator and specialised tools.

```text
Browser — Next.js / React / TypeScript
  ├── Voice capture + transcription adapter
  ├── Onboarding / diagnostic / tutor / plan / progress UI
  └── FastAPI backend
       ├── Learner and session services
       ├── Google ADK tutor orchestrator
       │    ├── Profile tools
       │    ├── Diagnostic tool
       │    ├── Curriculum/objectives tool
       │    ├── Resource retrieval (RAG)
       │    ├── Learning-plan tool
       │    ├── Assessment/evaluation tool
       │    └── Mastery/progress tool
       ├── LLM provider adapter (Gemini initially)
       └── PostgreSQL + pgvector
            ├── Learner and progress data
            ├── Certifications, objectives and skills
            └── Resource metadata, chunks and embeddings
```

### Technology decisions

| Layer | Initial choice | Reason / constraint |
|---|---|---|
| Frontend | Next.js, React, TypeScript | Fast polished web UI |
| Styling | Tailwind CSS | Fast iteration |
| Backend | Python + FastAPI | Reuses existing Python setup |
| Agent orchestration | Google ADK | Already installed |
| LLM | Gemini API initially | Keep model/provider configurable |
| Database | PostgreSQL + pgvector | Already running locally |
| Voice | Browser microphone + replaceable speech-to-text adapter | Test target browser; typed fallback |
| Authentication | Supabase Auth if hosted login is needed | Avoid custom auth |
| Frontend hosting | Vercel | Deploy after local flow works |
| Backend hosting | Google Cloud Run | Scale-to-zero where appropriate; monitor cost |
| Source control | GitHub | Existing private repo |

Microsoft is the certification/content ecosystem; Educentriks does not need to be hosted on Azure. Do not add cloud services solely for branding.

### Architecture guardrails
- Never commit `.env`, API keys, passwords or tokens.
- Keep LLM keys server-side.
- Validate tool inputs and outputs.
- Persist learner state in the database, not only chat history.
- Version certification objectives and store source/verification metadata.
- Use deterministic application logic for scoring and state transitions where practical.
- Let the model interpret and explain; do not let it invent official exam data.
- Keep voice and LLM providers replaceable.
- Do not expose privileged database credentials to the browser.

## 6. Agent tools

Start with one root tutor agent and narrowly scoped tools.

| Tool | Responsibility |
|---|---|
| `get_learner_profile` | Read structured learner profile |
| `update_learner_profile` | Apply learner-confirmed corrections |
| `get_exam_objectives` | Return versioned AI-103 objectives |
| `run_diagnostic` | Select diagnostic items and record evidence |
| `search_learning_resources` | Retrieve relevant official resources |
| `generate_learning_plan` | Create ordered activities from gaps |
| `evaluate_response` | Evaluate against an explicit rubric |
| `update_mastery` | Update skill status from assessment evidence |
| `get_next_activity` | Recommend the next learning activity |
| `record_learning_event` | Record completion and interaction events |

### Agent behaviour
- Understand natural speech, filler words, digressions and self-corrections.
- Ask clarifying questions only when needed.
- Confirm ambiguous, consequential profile changes.
- Cite retrieved sources for certification explanations.
- Distinguish official material from Educentriks explanations and practice.
- Never claim generated questions are actual Microsoft exam questions.
- Never guarantee exam success.
- Disclose when retrieval lacks reliable evidence.
- Update mastery only when assessment evidence supports it.

### Example technical-answer rubric
- Technical correctness: 40%.
- Explanation and reasoning: 25%.
- Appropriate use case: 20%.
- Security and responsible AI: 15%.

Keep the rubric adjustable and store evidence. Do not portray an LLM score as a scientifically validated measurement.

## 7. Data model

Implement only what the first vertical slice needs.

| Entity/table | Purpose |
|---|---|
| `learners` | Background, goal, experience, availability |
| `certifications` | Provider, code, title, version/status |
| `exam_objectives` | IDs, descriptions, weightings, source and verification date |
| `skills` | Python, RAG, agents, security, evaluation, etc. |
| `objective_skills` | Map objectives to skills |
| `learning_resources` | Official title, URL, metadata and version |
| `resource_chunks` | Text chunks, metadata and embeddings |
| `assessments` | Diagnostic/practice attempt metadata |
| `questions` | Original questions, objective mapping and rubric |
| `responses` | Answers, feedback, scores and evidence |
| `mastery_records` | Skill, status, evidence and last assessed date |
| `learning_plans` | Learner plan and target certification |
| `learning_activities` | Ordered activities and completion state |
| `learning_events` | Lesson viewed, answer submitted, lab completed, plan revised |

Official exam weighting and learner mastery are separate measures. Initial mastery states: `not_assessed`, `needs_revision`, `developing`, `proficient`.

## 8. Certification content and RAG

- Prefer official Microsoft Learn pages, official study guides and certification pages.
- Store source URL, title, certification code, objective mapping and `last_verified_at`.
- Respect source terms and copyright. Index only content permitted for such use; otherwise store metadata and link to the official source.
- Write original explanations, examples and practice questions.
- Never reproduce proprietary exam questions.
- Retrieval flow: identify topic/objective → retrieve relevant chunks → pass source metadata to model → generate level-appropriate explanation → return source links.
- If retrieval is weak, disclose the limitation rather than inventing a citation.

### RAG acceptance tests
- Relevant question retrieves relevant source.
- Answer links to the actual retrieved source.
- Unrelated question does not receive a fabricated Microsoft citation.
- Source URL and verification date are traceable.
- Updated resource metadata does not leave stale objective mappings.

## 9. Voice requirements and tests

### Behaviour
- Start/stop microphone capture.
- Show listening, processing, error and fallback states.
- Handle natural speech and corrections.
- Preserve the user's message on provider/network failure.
- Keep typed input available.

### Tests
- Clear speech produces a usable transcript.
- A self-correction is interpreted correctly.
- A digression does not overwrite the learner goal.
- Microphone denial gives a helpful typed fallback.
- Network/provider failure does not lose the message.
- The selected implementation works in the actual demo browser/laptop.

Browser speech support varies; verify it on the presentation machine rather than assuming uniform support.

## 10. Security and reliability

- Keep secrets out of Git and browser bundles.
- Use least-privilege database credentials.
- Validate user input and tool arguments.
- Add basic rate limits to public endpoints if deployed.
- Avoid logging secrets or unnecessary raw voice data.
- Use synthetic demo learner data unless real users consent.
- Handle LLM timeouts, rate limits and provider outages gracefully.
- Prepare a repeatable demo and typed fallback.
- Configure budget alerts before enabling paid cloud services. Alerts are not hard spending caps; inspect actual usage.

## 11. Repository structure

Create folders when needed; do not create empty scaffolding just for appearance.

```text
agentic-ai/
├── frontend/
│   ├── app/
│   ├── components/
│   └── lib/
├── backend/
│   ├── api/
│   ├── agents/
│   │   ├── tutor/
│   │   └── tools/
│   ├── services/
│   ├── models/
│   └── tests/
├── curriculum/
│   └── microsoft/
│       └── ai-103/
├── infrastructure/
│   └── postgres/
├── docs/
│   ├── EDUCENTRIKS_PROJECT_BLUEPRINT.md
│   ├── TASK_LOG.md
│   ├── DECISION_LOG.md
│   ├── product-requirements.md
│   ├── architecture.md
│   └── demo-script.md
└── README.md
```

## 12. Step-by-step task plan

### Workflow for each task
1. Explain the goal and why it matters.
2. Give exact commands or edits in manageable steps.
3. State expected output/behaviour.
4. Run a test or ask the user to verify.
5. Record evidence in `TASK_LOG.md`.
6. Mark `[x]` only after the acceptance check passes.
7. If blocked, mark `[!]`, record the issue and troubleshoot before depending on it.

Group related low-risk tasks when it improves speed. Keep the workflow flexible, but do not treat untested work as complete.

### Phase 0 — Existing setup and project records
- [x] **0.1 Development workspace:** WSL2 Ubuntu 24.04, Python 3.12, venv, Git, Node.js and Docker installed/verified.
- [x] **0.2 Agent framework:** Google ADK installed; starter agent generated.
- [x] **0.3 Local database:** PostgreSQL + pgvector running in Docker; vector extension verified.
- [x] **0.4 Source control:** private GitHub repo configured; initial commit pushed to `main`.
- [ ] **0.5 Add blueprint and logs to repository.** Acceptance: files committed/pushed; no secrets included.
- [ ] **0.6 Verify event rules.** Acceptance: deadline, demo duration, required tools, submission format and judging criteria recorded with source/date.

### Phase 1 — Product and demo definition
- [ ] **1.1 MVP brief.** Acceptance: target learner, problem, promise, scope and non-goals documented.
- [ ] **1.2 Learner journey.** Acceptance: onboarding → diagnostic → plan → tutor → practice → mastery → next activity documented.
- [ ] **1.3 Judge demo script.** Acceptance: short repeatable demo with sample profile and fallback.
- [ ] **1.4 AI-103 objective/skill map.** Acceptance: objective IDs map to skills and official source URLs.

### Phase 2 — Curriculum and data
- [ ] **2.1 Verify official AI-103 blueprint.** Acceptance: title/code/status/objectives/weightings checked against Microsoft.
- [ ] **2.2 Structured curriculum data.** Acceptance: backend can load objectives without prompt hardcoding.
- [ ] **2.3 Minimum database schema.** Acceptance: migrations support learner, objectives, assessments, mastery and plans.
- [ ] **2.4 Seed demo data.** Acceptance: sample learner and curriculum are queryable.
- [ ] **2.5 Resource metadata.** Acceptance: URLs work and include objective mapping/verification date.

### Phase 3 — Backend and agent vertical slice
- [ ] **3.1 FastAPI app + health endpoint.** Acceptance: local server starts and health returns success.
- [ ] **3.2 Configuration/secrets.** Acceptance: environment-based config; secrets absent from source.
- [ ] **3.3 Database connection.** Acceptance: backend query reads seeded data.
- [ ] **3.4 ADK tutor integration.** Acceptance: local request reaches agent and returns valid response.
- [ ] **3.5 Profile tools.** Acceptance: profile read and confirmed correction persist.
- [ ] **3.6 Curriculum tool.** Acceptance: agent retrieves objective data from DB.
- [ ] **3.7 RAG retrieval.** Acceptance: relevant question returns source-backed answer.
- [ ] **3.8 Diagnostic/assessment.** Acceptance: responses persist and are evaluated with rubric.
- [ ] **3.9 Plan generation.** Acceptance: plan reflects diagnostic gaps and persists.
- [ ] **3.10 Mastery/next activity.** Acceptance: evidence changes mastery and next recommendation.
- [ ] **3.11 Tests/failure handling.** Acceptance: core tests pass; invalid input/provider failure return useful errors.

### Phase 4 — Frontend and voice
- [ ] **4.1 Next.js foundation.** Acceptance: app runs locally and uses Educentriks brand assets where available.
- [ ] **4.2 Onboarding/profile UI.** Acceptance: learner can enter/edit persisted profile.
- [ ] **4.3 Diagnostic UI.** Acceptance: diagnostic completes and results display.
- [ ] **4.4 Learning-plan UI.** Acceptance: activities and status visible.
- [ ] **4.5 Tutor UI.** Acceptance: grounded answer and source links visible.
- [ ] **4.6 Voice capture/transcription.** Acceptance: works in target browser; typed fallback works.
- [ ] **4.7 Progress dashboard.** Acceptance: saved mastery and activity state display.
- [ ] **4.8 UX states.** Acceptance: loading, empty, error and mobile states do not block demo.

### Phase 5 — End-to-end test and hackathon polish
- [ ] **5.1 Clean-session demo journey.** Acceptance: complete without manual DB edits.
- [ ] **5.2 Beginner and experienced profiles.** Acceptance: plans differ meaningfully.
- [ ] **5.3 Voice corrections/fallback.** Acceptance: correction works; failure still allows progress.
- [ ] **5.4 Verify citations/certification claims.** Acceptance: demo claims have traceable sources.
- [ ] **5.5 Persistence.** Acceptance: progress survives reload/new session.
- [ ] **5.6 Demo reset.** Acceptance: known starting state can be restored quickly.
- [ ] **5.7 Backup recording.** Acceptance: short backup demo exists.
- [ ] **5.8 Pitch/submission.** Acceptance: problem, solution, agent workflow, differentiation and demo are clear.

### Phase 6 — Deployment, only after local MVP is stable
- [ ] **6.1 Hosting/cost plan.** Acceptance: services, region, secrets, expected cost and shutdown plan documented.
- [ ] **6.2 Frontend deployment.** Acceptance: public URL loads and reaches backend.
- [ ] **6.3 Backend deployment.** Acceptance: health and agent flow work remotely.
- [ ] **6.4 Hosted database/security.** Acceptance: secure connection; no public DB exposure.
- [ ] **6.5 Hosted smoke/cost checks.** Acceptance: core journey works; logs and billing reviewed.

## 13. Task verification template

Use in `TASK_LOG.md` for meaningful work:

```markdown
## Task X.Y — Task name
- Status: Not started / In progress / Blocked / Done
- Date:
- Goal:
- Changes made:
- Commands run:
- Expected result:
- Actual result:
- Test evidence:
- Issues and resolution:
- Commit:
```

A task is Done only when the change exists, its check passes and evidence is recorded. A blocked task is not a failure; record the blocker and next action.

## 14. MVP definition of done

- Learner can onboard by voice or typed fallback.
- Diagnostic identifies gaps across AI-103 skill areas.
- Personalised plan is generated and persisted.
- Tutor retrieves learning resources and cites them.
- Learner completes original practice.
- Evidence updates mastery.
- Next activity adapts to that evidence.
- Dashboard reflects updated progress.
- Demo can be repeated reliably.
- Secrets are protected and run instructions are documented.

Do not delay the demo for optional features. Once this loop works, focus on stability, UX and storytelling.

## 15. Existing environment — recorded baseline

Previously completed and verified; do not repeat unless something has changed:
- Windows 11 Enterprise; Intel Core i7-13700H; 16 GB RAM; integrated graphics; approximately 230 GB free storage at setup.
- WSL2 Ubuntu 24.04 LTS.
- Python 3.12 and venv at `~/agentic-ai/.venv`.
- Google ADK installed and starter agent generated.
- Node.js installed through NVM.
- Docker Engine running in WSL2.
- PostgreSQL + pgvector running through `infrastructure/postgres/compose.yaml`, bound to localhost port 5432.
- Private GitHub repository: `https://github.com/eawebsol/agentic-ai-hackathon`; initial commit pushed to `main`.
- Gemini API key exists in a local `.env`; never share or commit it.
- A previous Gemini request returned provider-side 503 overload. Keep provider/model configurable and distinguish provider outages from local setup errors.
- An untracked local calculator experiment exists at `hello_agent/tools/`; it was intentionally excluded from the initial commit. Do not delete or commit it without checking.

## 16. Immediate next actions

1. Add this blueprint, `TASK_LOG.md` and `DECISION_LOG.md` to the repository.
2. Verify current hackathon requirements and submission deadline.
3. Create the one-page MVP brief and judge demo script.
4. Verify the current AI-103 blueprint and build the objective-to-skill map.
5. Start the backend vertical slice after the curriculum shape is agreed.

**Current checkpoint:** development environment and GitHub foundation are ready. Educentriks application features are not yet complete. Focus next on a small, working hackathon journey.
