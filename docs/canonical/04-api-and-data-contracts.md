# API and Data Contracts

## Purpose
Define Focusly's MVP HTTP API, auth cookie behavior, database entities, JSONB contracts, job statuses, R2 keys, and HLS access model.

## Owner Skills
- Primary: backend-development
- Supporting: python-development, database-design, security-review, javascript-typescript, llm-application-dev

## Expected Output
Backend and frontend agents can implement compatible contracts without inventing endpoint shapes or database state fields.

## API Endpoint List
| Method | Path | Auth | Purpose |
|---|---|---|---|
| `POST` | `/api/auth/register` | No | Create user and set session cookie. |
| `POST` | `/api/auth/login` | No | Validate credentials and set session cookie. |
| `POST` | `/api/auth/logout` | Yes | Clear session cookie. |
| `GET` | `/api/me` | Yes | Return current user. |
| `POST` | `/api/lessons` | Yes | Create lesson generation job. |
| `GET` | `/api/lessons` | Yes | List authenticated user's lessons. |
| `GET` | `/api/lessons/{lesson_id}` | Yes | Get lesson detail and latest job summary. |
| `GET` | `/api/jobs/{job_id}` | Yes | Poll job status and progress. |
| `POST` | `/api/jobs/{job_id}/retry` | Yes | Retry failed retryable job. |
| `GET` | `/api/lessons/{lesson_id}/playback` | Yes | Return signed HLS and captions metadata. |

## Request and Response Shapes

### Create Lesson
```json
POST /api/lessons
{
  "topic": "Explain binary search",
  "audience_level": "beginner",
  "tone": "encouraging",
  "duration_target_seconds": 180
}
```

```json
202 Accepted
{
  "lesson_id": "uuid",
  "job_id": "uuid",
  "status": "queued",
  "poll_url": "/api/jobs/uuid"
}
```

### Job Status
```json
GET /api/jobs/{job_id}
{
  "job_id": "uuid",
  "lesson_id": "uuid",
  "status": "running",
  "stage": "R07_AUDIO_PRODUCER",
  "progress_percent": 62,
  "is_retryable": false,
  "safe_error": null,
  "created_at": "2026-05-21T12:00:00Z",
  "updated_at": "2026-05-21T12:03:00Z"
}
```

### Playback Metadata
```json
GET /api/lessons/{lesson_id}/playback
{
  "lesson_id": "uuid",
  "title": "Binary Search",
  "duration_seconds": 184,
  "hls_url": "https://signed.example/master.m3u8",
  "captions": [
    { "kind": "subtitles", "srclang": "en", "label": "English", "format": "vtt", "url": "https://signed.example/captions.vtt", "default": true }
  ],
  "quiz_checkpoints": [
    { "id": "q1", "timestamp_seconds": 57, "question": "What gets discarded each step?", "options": ["Half the search range", "The answer"], "correct_option_index": 0, "explanation": "Binary search compares the middle and removes the impossible half." }
  ]
}
```

## Error Response Format
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed.",
    "details": [
      { "field": "topic", "reason": "Must be between 3 and 300 characters." }
    ],
    "request_id": "uuid"
  }
}
```

## Auth Cookie Contract
| Cookie | Properties | Purpose |
|---|---|---|
| `focusly_session` | `HttpOnly`, `Secure` in production, `SameSite=Lax`, path `/`, short TTL | RS256 access JWT. |
| `focusly_csrf` | `Secure` in production, `SameSite=Lax`, readable by JS | Double-submit CSRF token for state-changing requests. |

JWT claims: `sub`, `email`, `iat`, `exp`, `iss`, `aud`, `jti`.

Reasoning: RS256 allows private signing keys to stay server-side and public verification keys to rotate safely. httpOnly cookies reduce token theft through XSS.

## Core Database Entities
| Entity | Key Fields | Notes |
|---|---|---|
| `users` | `id`, `email`, `password_hash`, `created_at` | Email unique, password hash only. |
| `lessons` | `id`, `user_id`, `title`, `topic`, `status`, `duration_seconds`, `created_at` | User-owned lesson shell and final metadata. |
| `generation_jobs` | `id`, `lesson_id`, `status`, `stage`, `progress_percent`, `attempt_count`, `safe_error`, `created_at`, `updated_at` | Polling source of truth. |
| `pipeline_states` | `id`, `job_id`, `thread_id`, `state_json`, `version`, `updated_at` | JSONB graph state snapshot. |
| `lesson_artifacts` | `id`, `lesson_id`, `kind`, `r2_key`, `content_type`, `size_bytes`, `metadata_json` | HLS, captions, audio, manifests, QA reports. |
| `job_events` | `id`, `job_id`, `stage`, `level`, `message`, `metadata_json`, `created_at` | Progress and debug audit trail. |

## LessonContext JSONB Contract
```json
{
  "topic": "Explain binary search",
  "audience_profile": { "level": "beginner", "adhd_supports": ["short_segments", "recap_beats"] },
  "learning_objectives": ["Explain sorted input", "Compare midpoint", "Discard half"],
  "misconceptions": ["Binary search works on unsorted lists"],
  "segments": [
    { "id": "seg_01", "title": "The Guessing Game", "target_seconds": 35, "objective_ids": ["lo_01"] }
  ],
  "design_tokens": { "pace": "brisk", "visual_density": "low", "caption_style": "high_contrast" }
}
```

## PipelineState Contract
```json
{
  "job_id": "uuid",
  "lesson_id": "uuid",
  "thread_id": "job:uuid",
  "status": "running",
  "current_stage": "R06_CODE_GENERATOR",
  "lesson_context": {},
  "script": { "segments": [], "narration": [] },
  "quiz": { "checkpoints": [] },
  "scene_manifest": { "scenes": [] },
  "generated_code": { "remotion": [], "manim": [], "validation": {} },
  "audio": { "tracks": [], "word_timestamps": [] },
  "captions": { "webvtt_key": null, "srt_key": null },
  "qa": { "status": "pending", "issues": [] },
  "render": { "hls_key": null, "duration_seconds": null },
  "errors": [],
  "updated_at": "ISO-8601"
}
```

## Job Status States
Allowed states: `queued`, `running`, `waiting_retry`, `succeeded`, `failed`, `cancelled`.

Allowed stage labels: `R01_ORCHESTRATOR`, `R02_PLANNER`, `R03_SCRIPTWRITER`, `R04_QUIZMASTER`, `R05_SCENE_DIRECTOR`, `R06_CODE_GENERATOR`, `R07_AUDIO_PRODUCER`, `R08_ANIMATOR`, `R09_QA_GATE`, `R10_RENDERER`.

## R2 Object Key Structure
```text
users/{user_id}/lessons/{lesson_id}/jobs/{job_id}/source/lesson_context.json
users/{user_id}/lessons/{lesson_id}/jobs/{job_id}/audio/narration.mp3
users/{user_id}/lessons/{lesson_id}/jobs/{job_id}/captions/captions.vtt
users/{user_id}/lessons/{lesson_id}/jobs/{job_id}/captions/captions.srt
users/{user_id}/lessons/{lesson_id}/jobs/{job_id}/video/hls/master.m3u8
users/{user_id}/lessons/{lesson_id}/jobs/{job_id}/video/hls/segment_000.ts
users/{user_id}/lessons/{lesson_id}/jobs/{job_id}/qa/report.json
```

## HLS Access Model
R2 objects are private. The playback endpoint authorizes lesson ownership, then returns short-lived signed URLs for the HLS manifest and caption tracks. Segment URLs should be signed through manifest rewriting or a signed proxy strategy, chosen during implementation but kept private-by-default.

## Acceptance Criteria
- All API responses use Pydantic-compatible shapes.
- Auth cookies follow RS256/httpOnly requirements.
- Pipeline and lesson state have explicit JSONB contracts.
- R2 keys include `user_id`, `lesson_id`, and `job_id` for isolation and traceability.

## Related Docs
- [Backend Implementation Guide](./06-backend-implementation-guide.md)
- [Frontend Implementation Guide](./07-frontend-implementation-guide.md)
- [Security and Reliability Guide](./10-security-and-reliability-guide.md)
