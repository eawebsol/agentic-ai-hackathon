-- Migration 001 — Initial schema for Educentriks Cognify
-- Covers all entities from blueprint Sections 7 (core) and 17 (PS02 extensions)

-- Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";

-- ============================================================
-- CORE TABLES (Section 7)
-- ============================================================

-- Learners
-- Already created by api/init_db.py; kept here with IF NOT EXISTS
-- and extended with study availability.
CREATE TABLE IF NOT EXISTS learners (
    id                      UUID        PRIMARY KEY DEFAULT uuid_generate_v4(),
    name                    VARCHAR(100) NOT NULL,
    "current_role"          TEXT,
    experience_level        VARCHAR(50)  NOT NULL DEFAULT 'beginner',
    target_certification    VARCHAR(50)  NOT NULL DEFAULT 'AI-103',
    learning_preferences    JSONB        NOT NULL DEFAULT '[]'::jsonb,
    available_study_hours   INTEGER,                          -- hours per week
    created_at              TIMESTAMPTZ  NOT NULL DEFAULT now(),
    updated_at              TIMESTAMPTZ  NOT NULL DEFAULT now()
);

-- Add available_study_hours if the table was created by the old init_db.py
ALTER TABLE learners ADD COLUMN IF NOT EXISTS available_study_hours INTEGER;
ALTER TABLE learners ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ NOT NULL DEFAULT now();

-- Certifications
CREATE TABLE IF NOT EXISTS certifications (
    id          UUID        PRIMARY KEY DEFAULT uuid_generate_v4(),
    provider    VARCHAR(100) NOT NULL,
    code        VARCHAR(50)  NOT NULL UNIQUE,   -- e.g. AI-103
    title       VARCHAR(200) NOT NULL,
    status      VARCHAR(50)  NOT NULL DEFAULT 'active',   -- active | retired | beta
    version     VARCHAR(50),
    source_url  TEXT,
    verified_at TIMESTAMPTZ,
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT now()
);

-- Exam objectives
CREATE TABLE IF NOT EXISTS exam_objectives (
    id               UUID        PRIMARY KEY DEFAULT uuid_generate_v4(),
    certification_id UUID        NOT NULL REFERENCES certifications(id) ON DELETE CASCADE,
    objective_id     VARCHAR(50) NOT NULL,   -- e.g. "1.1", "2.3"
    description      TEXT        NOT NULL,
    domain           VARCHAR(200),
    weighting_pct    NUMERIC(5,2),
    source_url       TEXT,
    verified_at      TIMESTAMPTZ,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (certification_id, objective_id)
);

-- Skills (Python, RAG, agent orchestration, security, evaluation…)
CREATE TABLE IF NOT EXISTS skills (
    id          UUID        PRIMARY KEY DEFAULT uuid_generate_v4(),
    slug        VARCHAR(100) NOT NULL UNIQUE,
    name        VARCHAR(150) NOT NULL,
    description TEXT,
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT now()
);

-- Objective → skill mapping
CREATE TABLE IF NOT EXISTS objective_skills (
    objective_id UUID NOT NULL REFERENCES exam_objectives(id) ON DELETE CASCADE,
    skill_id     UUID NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
    PRIMARY KEY (objective_id, skill_id)
);

-- Official learning resources (Microsoft Learn pages, study guides…)
CREATE TABLE IF NOT EXISTS learning_resources (
    id               UUID        PRIMARY KEY DEFAULT uuid_generate_v4(),
    certification_id UUID        REFERENCES certifications(id),
    title            TEXT        NOT NULL,
    url              TEXT        NOT NULL,
    resource_type    VARCHAR(50) NOT NULL DEFAULT 'article',  -- article | video | lab | guide
    metadata         JSONB       NOT NULL DEFAULT '{}'::jsonb,
    last_verified_at TIMESTAMPTZ,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- RAG chunks (text + vector embedding)
-- Embedding dimension 768 matches Gemini text-embedding-004 default output.
CREATE TABLE IF NOT EXISTS resource_chunks (
    id           UUID     PRIMARY KEY DEFAULT uuid_generate_v4(),
    resource_id  UUID     NOT NULL REFERENCES learning_resources(id) ON DELETE CASCADE,
    chunk_index  INTEGER  NOT NULL,
    content      TEXT     NOT NULL,
    metadata     JSONB    NOT NULL DEFAULT '{}'::jsonb,
    embedding    vector(768),
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (resource_id, chunk_index)
);

-- Assessments (diagnostic / practice / review attempts)
CREATE TABLE IF NOT EXISTS assessments (
    id              UUID        PRIMARY KEY DEFAULT uuid_generate_v4(),
    learner_id      UUID        NOT NULL REFERENCES learners(id) ON DELETE CASCADE,
    assessment_type VARCHAR(50) NOT NULL DEFAULT 'diagnostic',  -- diagnostic | practice | review
    certification   VARCHAR(50) NOT NULL DEFAULT 'AI-103',
    status          VARCHAR(50) NOT NULL DEFAULT 'in_progress',  -- in_progress | completed | abandoned
    started_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    completed_at    TIMESTAMPTZ,
    metadata        JSONB       NOT NULL DEFAULT '{}'::jsonb
);

-- Original practice questions (never actual exam questions)
CREATE TABLE IF NOT EXISTS questions (
    id            UUID        PRIMARY KEY DEFAULT uuid_generate_v4(),
    objective_id  UUID        REFERENCES exam_objectives(id),
    concept_id    UUID,                                          -- FK added after concepts table
    stem          TEXT        NOT NULL,
    question_type VARCHAR(50) NOT NULL DEFAULT 'scenario',       -- scenario | multiple_choice | short_answer
    difficulty    VARCHAR(20) NOT NULL DEFAULT 'intermediate'
                              CHECK (difficulty IN ('beginner','intermediate','advanced')),
    rubric        JSONB       NOT NULL DEFAULT '{}'::jsonb,
    model_answer  TEXT,
    metadata      JSONB       NOT NULL DEFAULT '{}'::jsonb,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Learner responses (answers, scores, feedback, evidence)
CREATE TABLE IF NOT EXISTS responses (
    id            UUID        PRIMARY KEY DEFAULT uuid_generate_v4(),
    assessment_id UUID        NOT NULL REFERENCES assessments(id) ON DELETE CASCADE,
    question_id   UUID        REFERENCES questions(id),
    learner_id    UUID        NOT NULL REFERENCES learners(id) ON DELETE CASCADE,
    answer        TEXT        NOT NULL,
    score         NUMERIC(5,2),
    rubric_scores JSONB       NOT NULL DEFAULT '{}'::jsonb,
    feedback      TEXT,
    evidence      JSONB       NOT NULL DEFAULT '[]'::jsonb,
    answered_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Mastery records (per learner, per concept — updated only on evidence)
CREATE TABLE IF NOT EXISTS mastery_records (
    id               UUID        PRIMARY KEY DEFAULT uuid_generate_v4(),
    learner_id       UUID        NOT NULL REFERENCES learners(id) ON DELETE CASCADE,
    concept_id       UUID        NOT NULL,                       -- FK added after concepts table
    status           VARCHAR(50) NOT NULL DEFAULT 'not_assessed'
                                 CHECK (status IN ('not_assessed','needs_revision','developing','proficient')),
    evidence         JSONB       NOT NULL DEFAULT '[]'::jsonb,
    confidence       NUMERIC(3,2) DEFAULT 0.0
                                 CHECK (confidence >= 0.0 AND confidence <= 1.0),
    last_assessed_at TIMESTAMPTZ,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (learner_id, concept_id)
);

-- Learning plans
CREATE TABLE IF NOT EXISTS learning_plans (
    id            UUID        PRIMARY KEY DEFAULT uuid_generate_v4(),
    learner_id    UUID        NOT NULL REFERENCES learners(id) ON DELETE CASCADE,
    certification VARCHAR(50) NOT NULL DEFAULT 'AI-103',
    status        VARCHAR(50) NOT NULL DEFAULT 'active'
                              CHECK (status IN ('active','completed','paused')),
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Learning activities (ordered steps inside a plan)
CREATE TABLE IF NOT EXISTS learning_activities (
    id             UUID        PRIMARY KEY DEFAULT uuid_generate_v4(),
    plan_id        UUID        NOT NULL REFERENCES learning_plans(id) ON DELETE CASCADE,
    concept_id     UUID,                                         -- FK added after concepts table
    activity_type  VARCHAR(50) NOT NULL DEFAULT 'lesson',        -- lesson | practice | review | diagnostic
    title          TEXT        NOT NULL,
    description    TEXT,
    sequence_order INTEGER     NOT NULL DEFAULT 0,
    status         VARCHAR(50) NOT NULL DEFAULT 'pending'
                               CHECK (status IN ('pending','in_progress','completed','skipped')),
    scheduled_for  DATE,
    completed_at   TIMESTAMPTZ,
    metadata       JSONB       NOT NULL DEFAULT '{}'::jsonb,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Learning events (immutable audit log)
CREATE TABLE IF NOT EXISTS learning_events (
    id          UUID        PRIMARY KEY DEFAULT uuid_generate_v4(),
    learner_id  UUID        NOT NULL REFERENCES learners(id) ON DELETE CASCADE,
    event_type  VARCHAR(100) NOT NULL,   -- lesson_viewed | answer_submitted | plan_revised | …
    payload     JSONB       NOT NULL DEFAULT '{}'::jsonb,
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ============================================================
-- PS02 EXTENSIONS (Section 17)
-- ============================================================

-- Concepts (nodes in the concept graph)
CREATE TABLE IF NOT EXISTS concepts (
    id                   UUID        PRIMARY KEY DEFAULT uuid_generate_v4(),
    slug                 VARCHAR(100) NOT NULL UNIQUE,
    name                 VARCHAR(150) NOT NULL,
    description          TEXT         NOT NULL,
    certification        VARCHAR(50)  NOT NULL DEFAULT 'AI-103',
    domain               VARCHAR(100) NOT NULL,
    difficulty           VARCHAR(20)  NOT NULL DEFAULT 'beginner'
                                      CHECK (difficulty IN ('beginner','intermediate','advanced')),
    learning_objectives  JSONB        NOT NULL DEFAULT '[]'::jsonb,
    created_at           TIMESTAMPTZ  NOT NULL DEFAULT now()
);

-- Concept prerequisite graph (directed edges)
CREATE TABLE IF NOT EXISTS concept_prerequisites (
    concept_id      UUID NOT NULL REFERENCES concepts(id) ON DELETE CASCADE,
    prerequisite_id UUID NOT NULL REFERENCES concepts(id) ON DELETE CASCADE,
    PRIMARY KEY (concept_id, prerequisite_id),
    CHECK (concept_id <> prerequisite_id)
);

-- Exam objective → concept mapping
CREATE TABLE IF NOT EXISTS objective_concepts (
    objective_id UUID NOT NULL REFERENCES exam_objectives(id) ON DELETE CASCADE,
    concept_id   UUID NOT NULL REFERENCES concepts(id) ON DELETE CASCADE,
    PRIMARY KEY (objective_id, concept_id)
);

-- Now add deferred FKs that reference concepts
ALTER TABLE questions          ADD COLUMN IF NOT EXISTS concept_id UUID REFERENCES concepts(id);
ALTER TABLE mastery_records    ADD COLUMN IF NOT EXISTS concept_id UUID REFERENCES concepts(id);
ALTER TABLE learning_activities ADD COLUMN IF NOT EXISTS concept_id UUID REFERENCES concepts(id);

-- Learner misconceptions (PS02 — evidence-based, not just wrong answers)
CREATE TABLE IF NOT EXISTS learner_misconceptions (
    id                   UUID        PRIMARY KEY DEFAULT uuid_generate_v4(),
    learner_id           UUID        NOT NULL REFERENCES learners(id) ON DELETE CASCADE,
    concept_id           UUID        NOT NULL REFERENCES concepts(id) ON DELETE CASCADE,
    description          TEXT        NOT NULL,
    evidence_response_id UUID        REFERENCES responses(id),
    confidence           NUMERIC(3,2) DEFAULT 0.5
                                      CHECK (confidence >= 0.0 AND confidence <= 1.0),
    status               VARCHAR(50) NOT NULL DEFAULT 'suspected'
                                     CHECK (status IN ('suspected','confirmed','resolved')),
    detected_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    resolved_at          TIMESTAMPTZ
);

-- Spaced-repetition review schedule (PS02)
CREATE TABLE IF NOT EXISTS review_schedules (
    id           UUID    PRIMARY KEY DEFAULT uuid_generate_v4(),
    learner_id   UUID    NOT NULL REFERENCES learners(id) ON DELETE CASCADE,
    concept_id   UUID    NOT NULL REFERENCES concepts(id) ON DELETE CASCADE,
    due_date     DATE    NOT NULL,
    interval_days INTEGER NOT NULL DEFAULT 1,
    completed_at TIMESTAMPTZ,
    outcome      VARCHAR(50) CHECK (outcome IN ('passed','failed','skipped')),
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Cohorts (PS02 — teacher/class grouping)
CREATE TABLE IF NOT EXISTS cohorts (
    id            UUID        PRIMARY KEY DEFAULT uuid_generate_v4(),
    name          VARCHAR(200) NOT NULL,
    description   TEXT,
    certification VARCHAR(50) NOT NULL DEFAULT 'AI-103',
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Cohort memberships (PS02)
CREATE TABLE IF NOT EXISTS cohort_memberships (
    cohort_id  UUID NOT NULL REFERENCES cohorts(id) ON DELETE CASCADE,
    learner_id UUID NOT NULL REFERENCES learners(id) ON DELETE CASCADE,
    joined_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (cohort_id, learner_id)
);

-- ============================================================
-- INDEXES (common query patterns)
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_mastery_learner       ON mastery_records(learner_id);
CREATE INDEX IF NOT EXISTS idx_mastery_concept       ON mastery_records(concept_id);
CREATE INDEX IF NOT EXISTS idx_responses_learner     ON responses(learner_id);
CREATE INDEX IF NOT EXISTS idx_responses_assessment  ON responses(assessment_id);
CREATE INDEX IF NOT EXISTS idx_activities_plan       ON learning_activities(plan_id);
CREATE INDEX IF NOT EXISTS idx_events_learner        ON learning_events(learner_id);
CREATE INDEX IF NOT EXISTS idx_review_learner_due    ON review_schedules(learner_id, due_date);
CREATE INDEX IF NOT EXISTS idx_misconceptions_learner ON learner_misconceptions(learner_id);
CREATE INDEX IF NOT EXISTS idx_chunks_resource       ON resource_chunks(resource_id);
CREATE INDEX IF NOT EXISTS idx_objectives_cert       ON exam_objectives(certification_id);

-- IVFFlat index for cosine similarity search on embeddings
-- lists = 100 is a sensible default for up to ~1 million rows.
-- Rebuild with a higher value if the corpus grows significantly.
CREATE INDEX IF NOT EXISTS idx_chunks_embedding
    ON resource_chunks USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

