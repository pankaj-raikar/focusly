# Backend Implementation Guide

## Purpose
Guide implementation of the FastAPI backend, auth, ARQ worker integration, SQLAlchemy/Alembic persistence, Pydantic schemas, rate limits, errors, and backend tests.

## Owner Skills
- Primary: backend-development
- Supporting: python-development, database-design, security-review, test-driven-development, systematic-debugging

## Expected Output
A maintainable Python backend that exposes the contracts in `04-api-and-data-contracts.md` and safely coordinates long-running generation jobs.

## FastAPI Module Structure
```text
apps/api/focusly_api/
  main.py
  core/config.py
  core/security.py
  core/errors.py
  db/session.py
  db/models.py
  db/migrations/
  schemas/auth.py
  schemas/lessons.py
  schemas/jobs.py
  routers/auth.py
  routers/me.py
  routers/lessons.py
  routers/jobs.py
  services/auth_service.py
  services/lesson_service.py
  services/job_service.py
  services/playback_service.py
  workers/arq_settings.py
  workers/jobs.py
  agents/graph.py
  agents/state.py
  integrations/claude.py
  integrations/elevenlabs.py
  integrations/r2.py
```

Reasoning: Keep HTTP routers thin, services testable, integrations mockable, and agent graph code separate from request handling.

## API Routing Strategy
- Routers own request parsing, dependencies, and response schemas.
- Services own authorization checks and database writes.
- No router should call Claude, ElevenLabs, Remotion, Manim, or FFmpeg directly.
- `POST /api/lessons` creates rows and enqueues ARQ, then returns `202`.

## Auth Implementation Strategy
- Use RS256 JWT signed with private key from environment.
- Set JWT in `focusly_session` httpOnly cookie.
- Validate JWT in FastAPI dependencies.
- Use `focusly_csrf` double-submit token for state-changing requests.
- Store password hashes with a modern password hashing algorithm.

Reasoning: Asymmetric JWT supports key rotation and httpOnly cookies reduce browser token exposure.

## ARQ Worker Strategy
- Define a single job entrypoint: `run_generation_job(ctx, job_id: str)`.
- Worker loads job and verifies it is `queued` or retryable before running.
- Worker updates stage and progress before and after every graph node.
- Worker uses per-stage timeouts and total job timeout.
- Worker writes terminal `succeeded` or `failed` status exactly once.

## SQLAlchemy and Alembic Strategy
- Use SQLAlchemy 2 async sessions with explicit transaction boundaries.
- Use Alembic for every schema change.
- Keep JSONB state in `pipeline_states.state_json` but index relational ownership and status fields.
- Separate schema migrations from data backfills.

Minimal table relationships:
```text
users 1--N lessons 1--N generation_jobs
lessons 1--N lesson_artifacts
generation_jobs 1--1 pipeline_states
generation_jobs 1--N job_events
```

## Pydantic Schema Strategy
- Define request and response models separately from ORM models.
- Use enum models for job statuses and stage labels.
- Validate all agent structured outputs before merging into `PipelineState`.
- Use explicit safe error schemas for user-facing failures.

## Rate Limiting Strategy
- Store rate-limit counters in Redis.
- Apply stricter limits to `POST /api/lessons` than read endpoints.
- Enforce per-user limits after authentication and IP limits before authentication.
- Return `429` with the standard error format.

## Error Handling Strategy
- Convert validation errors to the standard error response shape.
- Return `401` for unauthenticated, `403` for wrong owner, `404` for inaccessible lesson/job.
- Do not expose stack traces, provider prompts, raw Claude output, or secret-bearing URLs in errors.
- Include `request_id` in every error.

## Backend Test Guidance
- pytest: service functions, schema validation, auth helpers.
- pytest-asyncio: async database repositories and API clients.
- respx: mock Claude, ElevenLabs, and signed URL HTTP interactions where applicable.
- Contract tests: assert every endpoint matches `04-api-and-data-contracts.md`.
- Worker tests: enqueue fake job, run mocked graph, assert DB status transitions.

## Acceptance Criteria
- FastAPI routes match documented endpoint paths and shapes.
- Request handlers do not perform long-running generation or rendering.
- Auth uses RS256 JWT httpOnly cookies and CSRF for state-changing requests.
- SQLAlchemy models and Alembic migrations preserve the documented entity model.
- Backend tests cover auth, contracts, job lifecycle, and error responses.

## Related Docs
- [API and Data Contracts](./04-api-and-data-contracts.md)
- [LangGraph Agent Pipeline](./05-langgraph-agent-pipeline.md)
- [Security and Reliability Guide](./10-security-and-reliability-guide.md)
