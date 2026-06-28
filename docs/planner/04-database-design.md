# Focusly — Database Design

## 1. Schema Overview

Single PostgreSQL 16 database. All tables use UUID primary keys, `created_at`/`updated_at` timestamps, and foreign key cascades.

---

## 2. Table Definitions

### 2.1 Users

```sql
CREATE TABLE users (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email           TEXT UNIQUE NOT NULL,
    password_hash   TEXT NOT NULL,
    is_verified     BOOLEAN DEFAULT FALSE,
    is_admin        BOOLEAN DEFAULT FALSE,
    daily_generation_count  INTEGER DEFAULT 0,
    daily_reset_at  TIMESTAMPTZ DEFAULT NOW(),
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE UNIQUE INDEX idx_users_email ON users(email);
```

### 2.2 Refresh Tokens

```sql
CREATE TABLE refresh_tokens (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash  TEXT UNIQUE NOT NULL,
    expires_at  TIMESTAMPTZ NOT NULL,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_refresh_tokens_user_id ON refresh_tokens(user_id);
CREATE INDEX idx_refresh_tokens_expires ON refresh_tokens(expires_at);
```

### 2.3 Lesson Jobs

```sql
CREATE TYPE job_status AS ENUM ('queued', 'running', 'completed', 'failed');

CREATE TABLE lesson_jobs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    topic           TEXT NOT NULL,
    status          job_status NOT NULL DEFAULT 'queued',
    context         JSONB,                    -- full LessonContext snapshot
    error_message   TEXT,
    started_at      TIMESTAMPTZ,
    completed_at    TIMESTAMPTZ,
    retry_count     INTEGER DEFAULT 0,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_lesson_jobs_user_id ON lesson_jobs(user_id);
CREATE INDEX idx_lesson_jobs_status ON lesson_jobs(status);
CREATE INDEX idx_lesson_jobs_created ON lesson_jobs(created_at DESC);
```

### 2.4 Lessons (Completed)

```sql
CREATE TABLE lessons (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id          UUID NOT NULL REFERENCES lesson_jobs(id) ON DELETE CASCADE,
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    topic           TEXT NOT NULL,
    video_path      TEXT NOT NULL,            -- R2 object key
    hls_path        TEXT NOT NULL,            -- R2 HLS playlist key
    thumbnail_path  TEXT,
    duration_seconds INTEGER,
    segment_count   INTEGER,
    eval_score      FLOAT,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_lessons_user_id ON lessons(user_id);
CREATE INDEX idx_lessons_created ON lessons(created_at DESC);
```

### 2.5 Watch Sessions

```sql
CREATE TABLE watch_sessions (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lesson_id           UUID NOT NULL REFERENCES lessons(id) ON DELETE CASCADE,
    user_id             UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    watch_percentage    FLOAT DEFAULT 0,
    last_position_seconds INTEGER DEFAULT 0,
    completed           BOOLEAN DEFAULT FALSE,
    started_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE UNIQUE INDEX idx_watch_session_user_lesson
    ON watch_sessions(user_id, lesson_id);
```

### 2.6 Quiz Attempts

```sql
CREATE TABLE quiz_attempts (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lesson_id       UUID NOT NULL REFERENCES lessons(id) ON DELETE CASCADE,
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    question_index  INTEGER NOT NULL,
    selected_option INTEGER NOT NULL,
    is_correct      BOOLEAN NOT NULL,
    attempted_at    TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_quiz_attempts_lesson ON quiz_attempts(lesson_id, user_id);
```

### 2.7 Agent Memory

```sql
CREATE TABLE agent_memory (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    memory_type     TEXT NOT NULL,
    -- metaphor | scene_performance | pacing | explanation
    topic_domain    TEXT,                     -- cs | math | biology | general
    topic_tags      TEXT[] DEFAULT '{}',      -- for tag-based retrieval
    content         JSONB NOT NULL,
    quality_score   FLOAT DEFAULT 0.5,
    usage_count     INTEGER DEFAULT 0,
    source_job_id   UUID,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_agent_memory_type ON agent_memory(memory_type);
CREATE INDEX idx_agent_memory_domain ON agent_memory(topic_domain);
CREATE INDEX idx_agent_memory_tags ON agent_memory USING GIN(topic_tags);
CREATE INDEX idx_agent_memory_quality ON agent_memory(quality_score DESC);
```

### 2.8 LangGraph Checkpoints

```sql
CREATE TABLE langgraph_checkpoints (
    thread_id       TEXT NOT NULL,
    checkpoint_ns   TEXT NOT NULL DEFAULT '',
    checkpoint_id   TEXT NOT NULL,
    parent_id       TEXT,
    checkpoint      JSONB NOT NULL,           -- serialized pipeline state
    metadata        JSONB DEFAULT '{}',
    created_at      TIMESTAMPTZ DEFAULT NOW(),

    PRIMARY KEY (thread_id, checkpoint_ns, checkpoint_id)
);

CREATE INDEX idx_lg_checkpoints_thread ON langgraph_checkpoints(thread_id);
```

### 2.9 Agent Execution Logs

```sql
CREATE TABLE agent_execution_logs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id          UUID NOT NULL REFERENCES lesson_jobs(id) ON DELETE CASCADE,
    agent_id        TEXT NOT NULL,            -- e.g. "A01", "A16"
    status          TEXT NOT NULL,            -- pending | running | done | failed
    started_at      TIMESTAMPTZ,
    completed_at    TIMESTAMPTZ,
    error           TEXT,
    retry_count     INTEGER DEFAULT 0,
    input_snapshot  JSONB,
    output_snapshot JSONB,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_agent_logs_job ON agent_execution_logs(job_id);
CREATE INDEX idx_agent_logs_agent ON agent_execution_logs(agent_id);
```

### 2.10 Chain Runs (LangChain Observability)

```sql
CREATE TABLE chain_runs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id          UUID NOT NULL REFERENCES lesson_jobs(id) ON DELETE CASCADE,
    agent_id        TEXT NOT NULL,
    chain_name      TEXT NOT NULL,
    model           TEXT NOT NULL,
    tokens_in       INTEGER DEFAULT 0,
    tokens_out      INTEGER DEFAULT 0,
    cache_creation_tokens INTEGER DEFAULT 0,
    cache_read_tokens     INTEGER DEFAULT 0,
    latency_ms      INTEGER DEFAULT 0,
    cost_estimate   FLOAT DEFAULT 0,
    cached          BOOLEAN DEFAULT FALSE,
    error           TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_chain_runs_job ON chain_runs(job_id);
CREATE INDEX idx_chain_runs_agent ON chain_runs(agent_id);
CREATE INDEX idx_chain_runs_model ON chain_runs(model);
```

---

## 3. LessonContext JSONB Schema

The `lesson_jobs.context` column stores the full `LessonContext` Pydantic model as JSONB. This is the shared state that all agents read from and write to.

```json
{
    "job_id": "uuid",
    "user_id": "uuid",
    "topic": "binary search",
    "audience_level": "intermediate",

    "learner_profile": {
        "level": "intermediate",
        "assumed_prerequisites": ["arrays", "looping"],
        "vocabulary_ceiling": "undergraduate CS",
        "adhd_accommodation": true
    },
    "lesson_outline": ["concept 1", "concept 2", "..."],
    "misconception_map": [
        {
            "concept": "binary search base case",
            "wrong_belief": "binary search works on unsorted arrays",
            "corrective_framing": "..."
        }
    ],
    "learning_objectives": ["Given a sorted array, trace binary search steps"],

    "script_segments": [
        {
            "index": 0,
            "text": "narration text...",
            "duration_seconds": 12.5,
            "emphasis_words": ["sorted", "middle"],
            "pause_before_ms": 0,
            "pause_after_ms": 1500
        }
    ],
    "hook_text": "Did you know your phone book uses binary search?",
    "closing_summary": "Key takeaways...",
    "quiz_questions": [
        {
            "after_segment_index": 2,
            "question": "What happens if the array is not sorted?",
            "options": ["A", "B", "C", "D"],
            "correct_index": 1,
            "wrong_answer_explanations": ["...", "...", "...", "..."]
        }
    ],

    "scene_manifest": [
        {
            "index": 0,
            "scene_type": "remotion",
            "template_name": "KineticText",
            "duration_frames": 375,
            "script_segment_index": 0,
            "props": {},
            "asset_paths": [],
            "generated_code": null
        }
    ],
    "asset_manifest": ["r2://assets/scene0/img.png"],
    "design_tokens": {
        "primary_font": "Inter",
        "min_font_size_px": 32,
        "concept_colors": {"binary search": "#4F46E5"},
        "max_words_per_text": 7
    },

    "audio_assets": [
        {
            "segment_index": 0,
            "file_path": "r2://audio/job123/seg0.mp3",
            "duration_ms": 12500,
            "word_timestamps": [{"word": "binary", "start": 0.0, "end": 0.4}]
        }
    ],
    "final_audio_path": "r2://audio/job123/mixed.mp3",

    "rendered_scene_paths": ["r2://scenes/job123/scene0.mp4"],
    "final_video_path": "r2://videos/job123/final.mp4",
    "hls_playlist_path": "r2://videos/job123/master.m3u8",

    "eval_score": 0.82,
    "eval_notes": "Good pacing, strong metaphor usage",

    "qa_results": {
        "code_qa_passed": true,
        "visual_qa_passed": true,
        "sync_qa_passed": true,
        "educational_qa_passed": true
    }
}
```

---

## 4. Alembic Migration Strategy

```
alembic/
├── env.py
├── script.py.mako
└── versions/
    ├── 001_initial_schema.py
    ├── 002_add_agent_memory.py
    └── ...
```

- One migration per feature addition
- Never modify committed migrations — always add new ones
- Test migrations against a copy of production data before deploying
- `alembic upgrade head` in CI to verify schema consistency

---

## 5. Seed Data

```python
# infrastructure/seeds.py
async def seed_admin_user(session: AsyncSession) -> None:
    from focusly.domain.models.user import User
    from focusly.core.security import hash_password

    admin = User(
        email="admin@focusly.app",
        password_hash=hash_password("temporary-password"),
        is_verified=True,
        is_admin=True,
    )
    session.add(admin)
    await session.commit()
```

---

## 6. Backup Strategy

- Daily automated `pg_dump` to Cloudflare R2 (cron in Railway or worker)
- 30-day retention
- Restore tested monthly
- Backup command: `pg_dump -Fc $DATABASE_URL | gzip > backup.dump.gz`

---

## 7. Task Checklist

- [M] All tables created via Alembic migrations
- [M] Indexes on foreign keys and frequent query columns
- [M] JSONB schema for LessonContext validated against Pydantic model
- [M] LangGraph checkpoint table for crash recovery
- [M] Agent execution logging table
- [M] Chain run observability table
- [M] Agent memory table with GIN index on tags
- [S] Seed data for admin user
- [S] Daily backup cron to R2
- [C] Connection pooling monitoring (pgBouncer if needed)
