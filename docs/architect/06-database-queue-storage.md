# Focusly — Database, Queue, and Storage Architecture

## 1. PostgreSQL Architecture

### 1.1 Connection Management

```
┌──────────────────────────────────────────────────────────────┐
│                    Connection Pool                             │
│                                                              │
│  SQLAlchemy AsyncEngine                                      │
│  ├── pool_size=20 (persistent connections)                   │
│  ├── max_overflow=10 (burst capacity)                        │
│  ├── pool_pre_ping=True (detect stale connections)           │
│  └── echo=False in production (no SQL logging)               │
│                                                              │
│  Shared by: API (4 gunicorn workers × async sessions)        │
│            Worker (ARQ tasks × async sessions)                │
│            LangGraph checkpointer (async sessions)            │
└──────────────────────────────────────────────────────────────┘
```

### 1.2 Table Relationships

```
users (1) ──── (N) refresh_tokens
users (1) ──── (N) lesson_jobs
users (1) ──── (N) lessons
users (1) ──── (N) watch_sessions
users (1) ──── (N) quiz_attempts

lesson_jobs (1) ── (1) lessons
lessons (1) ──── (N) watch_sessions
lessons (1) ──── (N) quiz_attempts
lesson_jobs (1) ── (N) agent_execution_logs
lesson_jobs (1) ── (N) chain_runs

agent_memory (standalone, no FK)
langgraph_checkpoints (standalone, keyed by thread_id)
```

### 1.3 JSONB Strategy

The `lesson_jobs.context` column stores the full `LessonContext` as JSONB. This is the primary mechanism for inter-agent data sharing.

**Why JSONB over relational tables for agent state?**
- Agent output schemas change frequently during development
- Atomic updates (one write per agent completion)
- No join overhead when agents read state
- Checkpointing works natively with JSONB serialization
- Easy to serialize/deserialize Pydantic models

**Tradeoffs acknowledged:**
- No foreign key constraints within JSONB
- Query performance for filtering by nested fields is slower
- Schema validation happens in application layer (Pydantic), not database

### 1.4 Indexes

| Table | Index | Purpose |
|-------|-------|---------|
| users | email (unique) | Login lookup |
| refresh_tokens | user_id | Token cleanup per user |
| refresh_tokens | expires_at | Expired token cleanup cron |
| lesson_jobs | user_id | User's jobs list |
| lesson_jobs | status | Queue filtering |
| lesson_jobs | created_at DESC | Recent jobs first |
| lessons | user_id | User's lessons list |
| lessons | created_at DESC | Recent lessons first |
| watch_sessions | (user_id, lesson_id) unique | One session per user per lesson |
| quiz_attempts | (lesson_id, user_id) | Quiz results per lesson |
| agent_memory | memory_type | Type-based retrieval |
| agent_memory | topic_domain | Domain filtering |
| agent_memory | topic_tags (GIN) | Array overlap queries |
| agent_memory | quality_score DESC | Ranked retrieval |
| langgraph_checkpoints | thread_id | Checkpoint lookup |
| agent_execution_logs | job_id | Logs per job |
| chain_runs | job_id | Cost analysis per job |

---

## 2. ARQ Queue Architecture

### 2.1 Queue Design

```
┌──────────────────────────────────────────────────────────────┐
│                    Redis Queues                               │
│                                                              │
│  focusly:jobs          — Main lesson generation queue        │
│  focusly:rate_limit:*  — Sliding window rate limit counters  │
│  focusly:llm_cache:*   — Cached LLM responses               │
│                                                              │
│  Redis serves triple duty:                                   │
│  1. ARQ job queue broker                                     │
│  2. Rate limiting (sorted sets)                              │
│  3. LLM response cache                                       │
└──────────────────────────────────────────────────────────────┘
```

### 2.2 Job Lifecycle

```
POST /lessons/generate
    │
    ▼
Create LessonJob in PostgreSQL (status=queued)
    │
    ▼
ARQ: enqueue(generate_lesson_task, job_id)
    │
    ▼
Worker picks up task
    │
    ├── Update job: status=running, started_at=NOW()
    │
    ▼
Build LangGraph pipeline, execute
    │
    ├── Checkpoint after each layer
    │
    ├── Success:
    │   ├── Create Lesson record
    │   ├── Update job: status=completed, completed_at=NOW()
    │   └── Return
    │
    └── Failure:
        ├── Update job: status=failed, error_message=str(e)[:500]
        ├── Sentry capture
        └── ARQ will retry (max_tries=3)
```

### 2.3 Stuck Job Detection

```python
# Cron: every 15 minutes
async def check_stuck_jobs():
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=15)
    stuck = SELECT * FROM lesson_jobs
            WHERE status = 'running'
            AND started_at < cutoff
    for job in stuck:
        job.status = 'failed'
        job.error_message = 'timeout: stuck > 15 minutes'
```

---

## 3. Cloudflare R2 Storage Architecture

### 3.1 Bucket Structure

```
focusly-videos/
├── audio/
│   └── {job_id}/
│       ├── segment_0.mp3
│       ├── segment_1.mp3
│       └── mixed.mp3
├── scenes/
│   └── {job_id}/
│       ├── scene_0.mp4
│       ├── scene_1.mp4
│       └── ...
├── videos/
│   └── {job_id}/
│       ├── final.mp4
│       ├── master.m3u8
│       ├── segment_000.ts
│       ├── segment_001.ts
│       └── thumbnail.jpg
├── assets/
│   └── {job_id}/
│       ├── unsplash_0.jpg
│       └── ...
└── music/
    └── background_ambient.mp3
```

### 3.2 Access Patterns

| Operation | Method | Auth |
|-----------|--------|------|
| Agent uploads scene MP4 | boto3 put_object | Service credentials |
| Agent uploads audio | boto3 put_object | Service credentials |
| Agent uploads final video + HLS | boto3 put_object | Service credentials |
| User watches video | Signed URL (1h expiry) | User → API → R2 |
| User sees thumbnail | Signed URL (1h expiry) | User → API → R2 |
| Agent reads asset | boto3 get_object | Service credentials |

No public URLs for videos. All access goes through signed URLs generated by the API.

### 3.3 Cleanup Strategy

When a user deletes a lesson:
1. Delete all objects under `videos/{job_id}/`
2. Delete all objects under `audio/{job_id}/`
3. Delete all objects under `scenes/{job_id}/`
4. Delete all objects under `assets/{job_id}/`
5. Delete lesson record from PostgreSQL
6. Delete associated watch_sessions, quiz_attempts (CASCADE)

---

## 4. Data Flow Diagram — Complete Pipeline

```
User input: "Explain binary search"
    │
    ▼
API: Validate + Create LessonJob + Enqueue
    │
    ▼
Worker: Build LangGraph pipeline
    │
    ├─► A02-A05: Claude API → LearnerProfile, Outline, Misconceptions, Objectives
    │   (writes to LessonContext JSONB)
    │
    ├─► A06-A09: Claude API → Script, Pacing, Hook, Quiz
    │   (writes to LessonContext JSONB)
    │
    ├─► A10-A14: Claude API + Unsplash API → Scene Manifest, Assets, Design Tokens
    │   (downloads images to local temp, uploads to R2)
    │
    ├─► A15-A20: Claude API (code gen) → Remotion TSX + Manim Python + Captions
    │   (validates code, writes to LessonContext JSONB)
    │
    ├─► A21: ElevenLabs API → Audio segments + word timestamps
    │   (uploads MP3s to R2)
    │
    ├─► A22-A24: Pixabay API + FFmpeg → Background music + Sound cues + Mixed audio
    │   (uploads to R2)
    │
    ├─► A25-A28: QA checks (compile, visual, sync, educational)
    │   (conditional retry: route back to failing agent, max 3x)
    │
    ├─► A29: Remotion render (Node.js subprocess) → scene MP4s
    │   (uploads to R2)
    │
    ├─► A30: FFmpeg stitch → final MP4 + HLS + thumbnail
    │   (uploads to R2)
    │
    ├─► A31: Evaluate outcome → eval_score
    │
    └─► A32: Store memory → agent_memory table
    │
    ▼
Create Lesson record: video_path, hls_path, thumbnail_path
    │
    ▼
Mark job completed
    │
    ▼
Frontend: GET /lessons/:id → signed R2 URL → video.js plays HLS
```

---

## 5. Caching Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    Caching Layers                             │
│                                                              │
│  L1: React Query Cache (client)                              │
│  ├── Lessons: 5-minute stale time                            │
│  ├── Job status: no cache (always fresh)                     │
│  └── Quiz results: 1-hour stale time                         │
│                                                              │
│  L2: Redis LLM Cache (server)                                │
│  ├── Key: sha256(prompt + model)                             │
│  ├── TTL: 7 days                                             │
│  ├── Hit rate target: >30% for repeated topics               │
│  └── Saves ~$0.15 per cache hit (Claude API cost)            │
│                                                              │
│  L3: R2 CDN Cache (edge)                                     │
│  ├── HLS segments cached at edge                             │
│  ├── Thumbnails cached at edge                               │
│  └── No additional configuration needed (auto with R2)       │
│                                                              │
│  L4: PostgreSQL (persistent)                                 │
│  ├── LessonContext JSONB (agent state)                       │
│  ├── Agent memory (cross-lesson learning)                    │
│  └── LangGraph checkpoints (crash recovery)                  │
└──────────────────────────────────────────────────────────────┘
```
