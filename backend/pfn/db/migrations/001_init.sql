-- Python Forge Nexus :: initial schema
PRAGMA foreign_keys = ON;

CREATE TABLE learners (
    id            TEXT PRIMARY KEY,
    display_name  TEXT NOT NULL DEFAULT 'Learner',
    locale        TEXT NOT NULL DEFAULT 'ar' CHECK (locale IN ('ar','en')),
    theme         TEXT NOT NULL DEFAULT 'dark' CHECK (theme IN ('dark','light')),
    goals_json    TEXT NOT NULL DEFAULT '[]',
    onboarded     INTEGER NOT NULL DEFAULT 0,
    created_at    TEXT NOT NULL,
    updated_at    TEXT NOT NULL
);

CREATE TABLE preferences (
    learner_id        TEXT PRIMARY KEY REFERENCES learners(id) ON DELETE CASCADE,
    assistance_mode   TEXT NOT NULL DEFAULT 'full_support',
    hints_enabled     INTEGER NOT NULL DEFAULT 1,
    trace_enabled     INTEGER NOT NULL DEFAULT 1,
    execution_mode    TEXT NOT NULL DEFAULT 'native',
    mentor_role       TEXT NOT NULL DEFAULT 'teacher',
    daily_goal_minutes INTEGER NOT NULL DEFAULT 30,
    updated_at        TEXT NOT NULL
);

CREATE TABLE skills (
    id                     TEXT PRIMARY KEY,
    domain                 TEXT NOT NULL,
    level                  INTEGER NOT NULL,
    title_ar               TEXT NOT NULL,
    title_en               TEXT NOT NULL,
    description_ar         TEXT NOT NULL DEFAULT '',
    description_en         TEXT NOT NULL DEFAULT '',
    prerequisites_json     TEXT NOT NULL DEFAULT '[]',
    related_json           TEXT NOT NULL DEFAULT '[]',
    evidence_required      INTEGER NOT NULL DEFAULT 2,
    updated_at             TEXT NOT NULL
);

CREATE TABLE skill_state (
    learner_id      TEXT NOT NULL REFERENCES learners(id) ON DELETE CASCADE,
    skill_id        TEXT NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
    state           TEXT NOT NULL DEFAULT 'not_assessed',
    confidence      REAL NOT NULL DEFAULT 0.0,
    evidence_count  INTEGER NOT NULL DEFAULT 0,
    independent_count INTEGER NOT NULL DEFAULT 0,
    assisted_count  INTEGER NOT NULL DEFAULT 0,
    last_evidence_at TEXT,
    last_verified_at TEXT,
    next_review_at  TEXT,
    review_interval_days REAL NOT NULL DEFAULT 1.0,
    updated_at      TEXT NOT NULL,
    PRIMARY KEY (learner_id, skill_id)
);

CREATE TABLE evidence (
    id            TEXT PRIMARY KEY,
    learner_id    TEXT NOT NULL REFERENCES learners(id) ON DELETE CASCADE,
    skill_id      TEXT,
    kind          TEXT NOT NULL,
    source_type   TEXT NOT NULL,
    source_id     TEXT,
    outcome       TEXT NOT NULL,
    independence  TEXT NOT NULL DEFAULT 'independent',
    weight        REAL NOT NULL DEFAULT 1.0,
    details_json  TEXT NOT NULL DEFAULT '{}',
    created_at    TEXT NOT NULL
);
CREATE INDEX idx_evidence_learner ON evidence(learner_id, created_at);
CREATE INDEX idx_evidence_skill ON evidence(learner_id, skill_id);

CREATE TABLE curriculum_modules (
    id            TEXT PRIMARY KEY,
    level         INTEGER NOT NULL,
    order_index   INTEGER NOT NULL,
    domain        TEXT NOT NULL,
    title_ar      TEXT NOT NULL,
    title_en      TEXT NOT NULL,
    summary_ar    TEXT NOT NULL DEFAULT '',
    summary_en    TEXT NOT NULL DEFAULT '',
    skills_json   TEXT NOT NULL DEFAULT '[]',
    synced_at     TEXT NOT NULL
);

CREATE TABLE module_progress (
    learner_id   TEXT NOT NULL REFERENCES learners(id) ON DELETE CASCADE,
    module_id    TEXT NOT NULL REFERENCES curriculum_modules(id) ON DELETE CASCADE,
    status       TEXT NOT NULL DEFAULT 'not_started',
    example_runs INTEGER NOT NULL DEFAULT 0,
    experiment_runs INTEGER NOT NULL DEFAULT 0,
    task_passed  INTEGER NOT NULL DEFAULT 0,
    assessment_passed INTEGER NOT NULL DEFAULT 0,
    transfer_passed INTEGER NOT NULL DEFAULT 0,
    updated_at   TEXT NOT NULL,
    PRIMARY KEY (learner_id, module_id)
);

CREATE TABLE missions (
    id           TEXT PRIMARY KEY,
    world        TEXT NOT NULL,
    order_index  INTEGER NOT NULL DEFAULT 0,
    difficulty   INTEGER NOT NULL DEFAULT 1,
    title_ar     TEXT NOT NULL,
    title_en     TEXT NOT NULL,
    brief_ar     TEXT NOT NULL DEFAULT '',
    brief_en     TEXT NOT NULL DEFAULT '',
    skills_json  TEXT NOT NULL DEFAULT '[]',
    synced_at    TEXT NOT NULL
);

CREATE TABLE mission_attempts (
    id           TEXT PRIMARY KEY,
    learner_id   TEXT NOT NULL REFERENCES learners(id) ON DELETE CASCADE,
    mission_id   TEXT,
    world        TEXT NOT NULL,
    code         TEXT NOT NULL,
    mode         TEXT NOT NULL DEFAULT 'native',
    ok           INTEGER NOT NULL DEFAULT 0,
    score        REAL NOT NULL DEFAULT 0.0,
    hints_used   INTEGER NOT NULL DEFAULT 0,
    assistance_level TEXT NOT NULL DEFAULT 'independent',
    duration_ms  INTEGER NOT NULL DEFAULT 0,
    result_json  TEXT NOT NULL DEFAULT '{}',
    created_at   TEXT NOT NULL
);
CREATE INDEX idx_attempts_learner ON mission_attempts(learner_id, created_at);

CREATE TABLE projects (
    id            TEXT PRIMARY KEY,
    learner_id    TEXT NOT NULL REFERENCES learners(id) ON DELETE CASCADE,
    slug          TEXT NOT NULL,
    title         TEXT NOT NULL,
    template      TEXT NOT NULL DEFAULT 'blank',
    description   TEXT NOT NULL DEFAULT '',
    current_version INTEGER NOT NULL DEFAULT 1,
    created_at    TEXT NOT NULL,
    updated_at    TEXT NOT NULL,
    UNIQUE (learner_id, slug)
);

CREATE TABLE project_files (
    project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    path       TEXT NOT NULL,
    content    TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    PRIMARY KEY (project_id, path)
);

CREATE TABLE project_versions (
    id          TEXT PRIMARY KEY,
    project_id  TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    version     INTEGER NOT NULL,
    message     TEXT NOT NULL DEFAULT '',
    snapshot_json TEXT NOT NULL,
    created_at  TEXT NOT NULL,
    UNIQUE (project_id, version)
);

CREATE TABLE simulation_runs (
    id           TEXT PRIMARY KEY,
    learner_id   TEXT,
    world        TEXT NOT NULL,
    mission_id   TEXT,
    config_json  TEXT NOT NULL DEFAULT '{}',
    events_json  TEXT NOT NULL DEFAULT '[]',
    final_state_json TEXT NOT NULL DEFAULT '{}',
    ok           INTEGER NOT NULL DEFAULT 0,
    created_at   TEXT NOT NULL
);

CREATE TABLE events (
    id          TEXT PRIMARY KEY,
    learner_id  TEXT,
    type        TEXT NOT NULL,
    payload_json TEXT NOT NULL DEFAULT '{}',
    created_at  TEXT NOT NULL
);
CREATE INDEX idx_events_learner ON events(learner_id, created_at);

CREATE TABLE ai_assistance (
    id          TEXT PRIMARY KEY,
    learner_id  TEXT,
    context_type TEXT NOT NULL,
    context_id  TEXT,
    role        TEXT NOT NULL,
    mode        TEXT NOT NULL,
    request_json TEXT NOT NULL DEFAULT '{}',
    response_json TEXT NOT NULL DEFAULT '{}',
    provider    TEXT NOT NULL DEFAULT 'local',
    created_at  TEXT NOT NULL
);

CREATE TABLE experiments (
    id          TEXT PRIMARY KEY,
    learner_id  TEXT,
    name        TEXT NOT NULL,
    hypothesis  TEXT NOT NULL DEFAULT '',
    design_json TEXT NOT NULL DEFAULT '{}',
    created_at  TEXT NOT NULL
);

CREATE TABLE experiment_runs (
    id          TEXT PRIMARY KEY,
    experiment_id TEXT NOT NULL REFERENCES experiments(id) ON DELETE CASCADE,
    params_json TEXT NOT NULL DEFAULT '{}',
    metrics_json TEXT NOT NULL DEFAULT '{}',
    seed        INTEGER,
    duration_ms INTEGER NOT NULL DEFAULT 0,
    notes       TEXT NOT NULL DEFAULT '',
    created_at  TEXT NOT NULL
);

CREATE TABLE portfolio_artifacts (
    id          TEXT PRIMARY KEY,
    learner_id  TEXT NOT NULL REFERENCES learners(id) ON DELETE CASCADE,
    kind        TEXT NOT NULL,
    title       TEXT NOT NULL,
    summary     TEXT NOT NULL DEFAULT '',
    payload_json TEXT NOT NULL DEFAULT '{}',
    independence TEXT NOT NULL DEFAULT 'independent',
    created_at  TEXT NOT NULL
);

CREATE TABLE career_tasks (
    id          TEXT PRIMARY KEY,
    company     TEXT NOT NULL,
    role        TEXT NOT NULL,
    difficulty  INTEGER NOT NULL DEFAULT 1,
    title_ar    TEXT NOT NULL,
    title_en    TEXT NOT NULL,
    brief_ar    TEXT NOT NULL DEFAULT '',
    brief_en    TEXT NOT NULL DEFAULT '',
    skills_json TEXT NOT NULL DEFAULT '[]',
    synced_at   TEXT NOT NULL
);

CREATE TABLE career_submissions (
    id          TEXT PRIMARY KEY,
    learner_id  TEXT NOT NULL REFERENCES learners(id) ON DELETE CASCADE,
    task_id     TEXT NOT NULL REFERENCES career_tasks(id) ON DELETE CASCADE,
    status      TEXT NOT NULL DEFAULT 'in_progress',
    workdir     TEXT NOT NULL DEFAULT '',
    tests_json  TEXT NOT NULL DEFAULT '{}',
    review_json TEXT NOT NULL DEFAULT '{}',
    created_at  TEXT NOT NULL,
    updated_at  TEXT NOT NULL
);

CREATE TABLE rescue_analyses (
    id          TEXT PRIMARY KEY,
    learner_id  TEXT,
    root_name   TEXT NOT NULL,
    summary_json TEXT NOT NULL,
    created_at  TEXT NOT NULL
);

CREATE TABLE library_runs (
    id          TEXT PRIMARY KEY,
    learner_id  TEXT,
    library_id  TEXT NOT NULL,
    example_index INTEGER NOT NULL DEFAULT 0,
    ok          INTEGER NOT NULL DEFAULT 0,
    output      TEXT NOT NULL DEFAULT '',
    created_at  TEXT NOT NULL
);
CREATE INDEX idx_library_runs ON library_runs(learner_id, library_id);
