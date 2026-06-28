# System Architecture

## Purpose
Describe the end-to-end Focusly architecture, component boundaries, data flow, and deployment shape using only the canonical stack.

## Owner Skills
- Primary: project-planner
- Supporting: backend-development, python-development, database-design, frontend-design, llm-application-dev, security-review

## Expected Output
An implementation-ready architecture narrative that future agents can follow without selecting new infrastructure or service boundaries.

## Architecture Narrative
Focusly is a monorepo application with a Next.js frontend, a FastAPI backend, a PostgreSQL database, Redis-backed ARQ workers, and a LangGraph generation pipeline. The user submits a topic prompt. FastAPI validates input, authenticates the user through RS256 JWT cookies, creates a lesson job, persists initial pipeline state, and enqueues the job in ARQ. The worker executes the Path B LangGraph graph, calls Claude through LangChain chains, calls ElevenLabs for narration, renders scenes with Remotion and Manim, stitches HLS through FFmpeg, uploads assets to private R2 object keys, and updates job progress. The frontend polls job state with React Query and plays the final HLS stream with video.js and toggleable caption tracks.

## ASCII Architecture Diagram
```text
Browser
  | Next.js 15 App Router, React Query, Zustand, video.js
  v
FastAPI API
  | auth, validation, job creation, signed playback URLs
  +----------------------+
  |                      |
  v                      v
PostgreSQL 16         Redis 7
users, lessons,       ARQ queue
jobs, artifacts,
pipeline_state JSONB
                         |
                         v
                    ARQ Worker
                         |
                         v
                 LangGraph Path B
     R01 -> R02 -> R03/R05 -> R04 -> R06/R07 -> R08 -> R09 -> R10
        |       |       |       |       |       |       |       |
        +-------+-------+-------+-------+-------+-------+-------+
                         |
        Claude API via LangChain, ElevenLabs, Remotion, Manim, FFmpeg
                         |
                         v
                  Cloudflare R2 private objects
                  HLS, captions, audio, manifests
```

## Component Boundaries
| Component | Owns | Does Not Own |
|---|---|---|
| Next.js frontend | UI, form validation hints, polling, playback, accessibility | Direct R2 writes, direct Claude/ElevenLabs calls, auth token storage in localStorage. |
| FastAPI backend | Auth, API contracts, authorization, job lifecycle, signed URLs | Long-running render execution in request handlers. |
| ARQ worker | Long-running pipeline execution and rendering | Browser sessions and interactive UI state. |
| LangGraph pipeline | Agent state transitions, retry routing, checkpointing | HTTP transport or database migrations. |
| LangChain chains | Prompt templates, structured output parsing, Claude calls | Graph topology or job scheduling. |
| PostgreSQL | Durable users, lessons, jobs, JSONB state, artifact metadata | Binary media storage. |
| Redis | Queue and transient job locks | Durable source of truth. |
| R2 | Private media objects and render artifacts | User/session records or pipeline decisions. |

## Primary Data Flow
1. User submits `topic`, `audience_level`, and optional preferences from `/generate`.
2. FastAPI authenticates cookie, validates request with Pydantic, creates `lessons` and `generation_jobs` rows.
3. FastAPI enqueues `run_generation_job(job_id)` in ARQ and returns `202 Accepted`.
4. ARQ worker loads job, invokes LangGraph with `thread_id=job_id`, and persists node outputs to `pipeline_state` JSONB.
5. R02-R09 produce lesson context, script, quiz, scene manifest, code assets, audio, captions, QA reports.
6. R10 renders HLS and uploads media under private R2 keys.
7. Worker marks job `succeeded` or `failed`, writes final playback metadata.
8. Frontend polls `/api/jobs/{job_id}` until terminal state, then requests signed playback metadata.
9. video.js loads HLS manifest and caption tracks; quizzes appear at checkpoint timestamps.

## Deployment Shape
| Runtime | Process | Notes |
|---|---|---|
| Web | Next.js server | Serves app shell and frontend routes. |
| API | FastAPI ASGI process | Stateless except database and Redis connections. |
| Worker | ARQ worker process | Requires render toolchain and controlled filesystem workspace. |
| Database | PostgreSQL 16 | Durable relational and JSONB state. |
| Queue | Redis 7 | Queue, locks, and rate-limit counters. |
| Object storage | Cloudflare R2 | Private assets accessed through signed URLs or signed proxy. |

## Major Decision Reasoning
- Monorepo with pnpm, Turborepo, and uv: keeps web, API, worker, shared contracts, and docs versioned together while allowing language-specific package management.
- FastAPI: async Python integrates cleanly with LangGraph, LangChain, SQLAlchemy async, and ARQ.
- LangGraph: explicit graph topology, checkpointing, retry routes, and state inspection are required for multi-step agent jobs.
- LangChain: keeps prompts, parsers, and Claude calls reusable and testable outside graph topology.
- ARQ + Redis: long-running render jobs must not block FastAPI; ARQ is Python-native and simpler than heavier distributed queues for MVP.
- PostgreSQL JSONB: pipeline artifacts evolve quickly; JSONB preserves structured state while still supporting relational job ownership and indexes.
- Cloudflare R2: stores large media outside Postgres with S3-compatible access and private keys.
- Remotion: best fit for React/TSX scene generation and deterministic animated lesson videos.
- Manim: best fit for precise math, algorithm, graph, and diagram animations.
- FFmpeg: canonical tool for stitching, transcoding, HLS segmentation, and caption muxing.
- video.js: mature HLS playback and caption-track support across browsers.

## Acceptance Criteria
- The architecture contains no MVP runtime service beyond Claude API, ElevenLabs, and R2.
- Long-running work runs in ARQ workers, not request handlers.
- PostgreSQL is the durable source of truth for job and pipeline state.
- Captions are player-toggleable tracks, not only burned into video.
- Component boundaries are explicit enough to prevent duplicated responsibilities.

## Related Docs
- [API and Data Contracts](./04-api-and-data-contracts.md)
- [LangGraph Agent Pipeline](./05-langgraph-agent-pipeline.md)
- [Rendering, Audio, and Storage Guide](./08-rendering-audio-storage-guide.md)
