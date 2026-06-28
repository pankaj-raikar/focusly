# Product Requirements Document

## AI-Driven Animated Learning Platform for ADHD Learners

### Spec-Driven Architecture · Solo Engineer Edition

---

**Document version:** 1.0.0 **Author:** Solo Engineer **Status:** Active — Specification Phase **Last updated:** May 2026 **Classification:** Internal working document

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Problem Statement](#2-problem-statement)
3. [Goals and Success Metrics](#3-goals-and-success-metrics)
4. [User Personas](#4-user-personas)
5. [Scope and Boundaries](#5-scope-and-boundaries)
6. [Functional Requirements](#6-functional-requirements)
7. [Non-Functional Requirements](#7-non-functional-requirements)
8. [System Architecture](#8-system-architecture)
9. [Multi-Agent System Specification](#9-multi-agent-system-specification)
10. [Video Production Engine Specification](#10-video-production-engine-specification)
11. [Data Models](#11-data-models)
12. [API Specification](#12-api-specification)
13. [Frontend Specification](#13-frontend-specification)
14. [Infrastructure and DevOps](#14-infrastructure-and-devops)
15. [Testing Strategy](#15-testing-strategy)
16. [Build Phases and Milestones](#16-build-phases-and-milestones)
17. [Risk Register](#17-risk-register)
18. [Decisions Log](#18-decisions-log)

---

## 1\. Executive Summary

### 1.1 Product name

**Focusly** — AI-Driven Animated Learning Platform for ADHD Learners.

### 1.2 One-sentence description

Focusly converts lecture notes, syllabi, and topic prompts into programmatically generated, ADHD-optimised animated lesson videos, entirely through a multi-agent AI orchestration system, with no human editor in the loop.

### 1.3 The core proposition

A student types "Explain binary search" and within minutes receives a precisely paced, visually animated, course-specific lesson video — broken into 30-second segments, color-coded by concept, narrated, with quiz checkpoints — built entirely from code, not from pre-recorded humans or AI video generation APIs.

### 1.4 Solo engineer context

This product is designed to be built, deployed, and maintained by one software engineer. Every architectural decision in this document is made with that constraint in mind. Complexity is traded for reliability at every decision point. No feature is included unless it can be owned end-to-end by one person.

---

## 2\. Problem Statement

### 2.1 The learner problem

College students with ADHD — particularly in engineering and technical disciplines — experience a consistent broken learning loop:

1. They attend a lecture and lose focus at a complex concept
2. They review slides and remain confused — text-heavy, no visual movement
3. They search YouTube and find generic 30-minute videos misaligned with their syllabus
4. They ask peers or TAs and face scheduling friction and embarrassment
5. They give up or cram the night before the exam
6. The comprehension gap persists and compounds

The root failure is the absence of **on-demand, course-specific, visually animated, appropriately paced** explanations targeted at the exact misconception the student holds.

### 2.2 The market gap

| Existing solution | Strengths | Fatal gap |
| --- | --- | --- |
| Khan Academy | Visual, on-demand | Not course-specific, too long |
| Lecture recordings | Course-specific | Not visual, same attention problem |
| YouTube tutorials | On-demand | Generic, too long, inconsistent quality |
| Byju's / PhysicsWallah | Indian market | Pre-recorded, not adaptive, not ADHD-specific |

No existing product combines: course-specific + visual-animated + on-demand + ADHD-paced + programmatically generated.

### 2.3 The technical gap

Existing "AI video" products use one of two approaches: pre-recorded human educators, or AI video generation APIs (Runway, Sora, Kling). Both fail the programmatic control requirement. Neither allows deterministic, parameterised control over every frame of educational content.

---

## 3\. Goals and Success Metrics

### 3.1 Primary goals

| Goal | Metric | Target |
| --- | --- | --- |
| Generate a complete lesson video | End-to-end pipeline success rate | ≥ 90% of requests produce a valid MP4 |
| Produce ADHD-appropriate pacing | Max segment duration | 100% of segments ≤ 30 seconds |
| Match educational depth | Learning objective coverage | ≥ 85% of objectives addressed per video |
| Deliver fast enough to be useful | Time from prompt to video ready | ≤ 5 minutes for a 3-minute lesson |
| Achieve real retention | Quiz pass rate on first attempt | ≥ 70% of students pass checkpoint quizzes |

### 3.2 Solo engineer success metrics

| Constraint | Target |
| --- | --- |
| Weekly dev hours to maintain | ≤ 10 hours after MVP launch |
| Incident response time | ≤ 30 minutes to identify root cause |
| Deploy frequency | At least once per week, zero-downtime |
| Test coverage | ≥ 80% on critical path (agents, render pipeline, API) |

### 3.3 Phase 1 MVP definition

A user can input a topic, the system generates a complete animated lesson video with narration and quiz checkpoints, and the video is streamed back to the user within 5 minutes. Everything else is post-MVP.

---

## 4\. User Personas

### 4.1 Primary — Arjun Mehta (the ADHD learner)

* **Background:** 2nd-year B.E. Computer Science, RV College of Engineering, Bangalore
* **ADHD profile:** Diagnosed, takes medication, tech-savvy, uses Notion and forest app
* **Learning behaviour:** Understands big-picture concepts quickly, loses detail in sequential steps
* **Pain point:** "I get the concept but I miss the steps in between. Lecture notes just confuse me more."
* **Device:** Phone-first (OnePlus), occasionally laptop
* **Session pattern:** Studies in 15–20 minute bursts, highest focus 9–11pm
* **Willingness to pay:** ₹299–499/month if it genuinely helps exam prep

### 4.2 Secondary — Meera Iyer (the self-aware struggler)

* **Background:** 3rd-year B.E. Electronics, no formal ADHD diagnosis but exhibits strong attention difficulties
* **Behaviour:** Relies heavily on YouTube, frustrated by irrelevant content
* **Pain point:** "The YouTube video is on quicksort but it uses a completely different approach than my professor."
* **Value:** Course-specific content tailored to her exact syllabus

### 4.3 Tertiary — Professor Ramesh (the content source)

* **Background:** Associate Professor, teaches Data Structures and Algorithms
* **Concern:** His lecture notes getting processed by an AI system he doesn't control
* **Win condition:** He sees the output and it correctly represents his teaching approach
* **Involvement:** Passive — his notes are the input, he is not actively using the platform

---

## 5\. Scope and Boundaries

### 5.1 In scope — MVP

* User authentication (email + password, no OAuth for MVP)
* Topic prompt input and lesson video generation
* Multi-agent pipeline: script → scene → code → audio → render → deliver
* Programmatic video: Remotion (general scenes) + Manim (math scenes)
* TTS narration with pacing control
* Quiz checkpoints embedded in video segments
* Video streaming via HLS to a custom player
* Basic student dashboard (lessons generated, watch history)
* Job queue with status polling
* PostgreSQL data persistence
* Docker-based local development
* Railway or Render deployment (not AWS — too complex for solo MVP)

### 5.2 In scope — Phase 2 (post-MVP)

* File upload: PDF/PPTX lecture notes as input
* Misconception-targeted explanations (requires real student feedback data)
* Spaced repetition scheduling
* Student analytics dashboard
* Educator portal for content verification
* Multi-language narration (Hindi, Kannada)
* Mobile app (React Native)
* Institutional licensing

### 5.3 Explicitly out of scope — forever for solo

* Real-time collaborative features
* Live lecture processing
* Custom avatar/character animation (Cartoon-style talking heads)
* Content marketplace (user-uploaded lessons)
* Social/community features
* Native mobile app before web MVP is stable
* On-premise deployment for institutions

### 5.4 Solo engineer constraints

These constraints are hard limits, not preferences. Any feature that violates them is deferred regardless of user demand:

* **No feature requiring more than one database** until Phase 3 (PostgreSQL only — no Mongo, no separate vector DB until search is needed)
* **No microservices** — monorepo, one deployable backend, one deployable frontend
* **No real-time features** (WebSockets) in MVP — polling is sufficient and simpler to operate
* **No ML training pipelines** — inference only, via external APIs
* **Maximum 3 external service dependencies** in MVP: Claude API, ElevenLabs API, Cloudflare R2

---

## 6\. Functional Requirements

Requirements use MoSCoW priority: **M**ust, **S**hould, **C**ould, **W**on't.

### 6.1 Authentication and accounts

| ID | Priority | Requirement |
| --- | --- | --- |
| AUTH-01 | M | User can register with email and password |
| AUTH-02 | M | Password stored as bcrypt hash, never plaintext |
| AUTH-03 | M | JWT access token (15 min expiry) + refresh token (7 days) |
| AUTH-04 | M | User can log out, invalidating refresh token |
| AUTH-05 | S | Email verification on registration |
| AUTH-06 | S | Password reset via email link |
| AUTH-07 | C | Google OAuth |
| AUTH-08 | W | SSO / SAML for institutions (Phase 2) |

### 6.2 Lesson generation — the core flow

| ID | Priority | Requirement |
| --- | --- | --- |
| GEN-01 | M | User inputs a topic as free text (1–200 characters) |
| GEN-02 | M | System validates input: non-empty, not harmful content |
| GEN-03 | M | System creates a lesson job and returns a job ID immediately (async — do not block) |
| GEN-04 | M | User can poll job status via job ID |
| GEN-05 | M | System runs the full multi-agent pipeline for every job |
| GEN-06 | M | Pipeline produces a valid MP4 ≤ 5 minutes long |
| GEN-07 | M | Every segment is ≤ 30 seconds |
| GEN-08 | M | Video includes narration audio |
| GEN-09 | M | Video includes burned-in captions |
| GEN-10 | M | Video includes at least one quiz checkpoint |
| GEN-11 | M | Completed video is stored and associated with the user's account |
| GEN-12 | M | Failed jobs are marked as failed with an error reason |
| GEN-13 | M | Failed jobs do not bill the user |
| GEN-14 | S | User receives a notification (in-app) when video is ready |
| GEN-15 | S | User can regenerate a failed lesson at no extra cost |
| GEN-16 | C | User can specify target audience level (beginner / intermediate / advanced) |
| GEN-17 | C | User can upload a PDF or PPTX as context |
| GEN-18 | W | Real-time generation progress stream |

### 6.3 Video player

| ID | Priority | Requirement |
| --- | --- | --- |
| VID-01 | M | Video plays in browser via HLS streaming |
| VID-02 | M | Player shows overall progress bar |
| VID-03 | M | Player shows chapter markers for each segment |
| VID-04 | M | Captions are visible by default, can be toggled off |
| VID-05 | M | Playback speed control: 0.75x, 1x, 1.25x, 1.5x |
| VID-06 | M | "Replay last 10 seconds" button — critical for ADHD |
| VID-07 | M | Quiz checkpoints pause the video and prompt the user |
| VID-08 | M | Quiz answer submitted before video resumes |
| VID-09 | S | Keyboard shortcuts: space (play/pause), left arrow (−10s), right arrow (+10s) |
| VID-10 | S | Player remembers watch position if user leaves and returns |
| VID-11 | C | Picture-in-picture mode |
| VID-12 | W | Download MP4 (Phase 2, requires watermarking first) |

### 6.4 Student dashboard

| ID | Priority | Requirement |
| --- | --- | --- |
| DASH-01 | M | User can see all lessons they have generated |
| DASH-02 | M | Each lesson shows: topic, status (processing / ready / failed), date |
| DASH-03 | M | User can open and watch any completed lesson |
| DASH-04 | M | User can delete a lesson |
| DASH-05 | S | User can see quiz scores per lesson |
| DASH-06 | S | User can see watch completion percentage per lesson |
| DASH-07 | C | Basic usage stats: total lessons generated, total watch time |

### 6.5 Job queue and pipeline

| ID | Priority | Requirement |
| --- | --- | --- |
| QUEUE-01 | M | Jobs are processed asynchronously via a persistent queue |
| QUEUE-02 | M | Maximum 3 concurrent render jobs to prevent resource exhaustion |
| QUEUE-03 | M | Jobs have a timeout of 10 minutes — if exceeded, marked as failed |
| QUEUE-04 | M | Transient failures are retried up to 3 times with exponential backoff |
| QUEUE-05 | M | Job state transitions are logged with timestamps |
| QUEUE-06 | S | Queue depth is visible in admin panel |
| QUEUE-07 | S | Stuck jobs are automatically detected and requeued after 15 minutes |

---

## 7\. Non-Functional Requirements

### 7.1 Performance

| Requirement | Target |
| --- | --- |
| API response time (p95) for non-generation endpoints | ≤ 200ms |
| Job submission response time | ≤ 500ms |
| Time from job submission to video ready (3-minute lesson) | ≤ 5 minutes |
| Video first-frame load time (HLS) | ≤ 2 seconds |
| Concurrent users supported (MVP) | 50 simultaneous users |
| Concurrent render jobs | 3 (solo infrastructure constraint) |

### 7.2 Reliability

| Requirement | Target |
| --- | --- |
| API uptime | ≥ 99% (allows \~7h downtime/month) |
| Video delivery uptime | ≥ 99.5% (CDN-backed) |
| Data loss tolerance | Zero — all user data must survive a server restart |
| Backup frequency | Daily automated DB backup to R2 |
| Backup retention | 30 days |

### 7.3 Security

| Requirement | Specification |
| --- | --- |
| All traffic | HTTPS only, redirect HTTP to HTTPS |
| Passwords | bcrypt with cost factor 12 |
| Tokens | JWT signed with RS256, stored in httpOnly cookie |
| API keys | Never exposed to frontend, stored in environment variables only |
| User data isolation | Every DB query scoped to authenticated user ID |
| Video access | Signed URLs with 1-hour expiry — no public video URLs |
| Rate limiting | 10 lesson generations per user per day (MVP) |
| Input sanitisation | All user inputs sanitised before passing to AI agents |

### 7.4 Maintainability (solo engineer critical)

| Requirement | Specification |
| --- | --- |
| Code coverage | ≥ 80% on agent pipeline, API routes, and data layer |
| Type safety | mypy strict mode on Python backend, TypeScript strict on frontend |
| Linting | ruff (Python), eslint (TypeScript) — zero warnings in CI |
| Documentation | Every agent, every API route, every data model has a docstring |
| Error messages | Every error includes a machine-readable code and human-readable message |
| Logging | Structured JSON logs (structlog) with request ID on every log line |
| Observability | Sentry for errors, basic metrics via Prometheus + Grafana (Phase 2) |

### 7.5 Scalability (solo constraints acknowledged)

The MVP architecture supports vertical scaling only. Horizontal scaling is architecturally possible but not a Phase 1 requirement. The system must handle 50 concurrent users without degradation. Beyond that, a waitlist is acceptable until Phase 2.

---

## 8\. System Architecture

### 8.1 High-level architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        CLIENT                                │
│              Next.js 15 (App Router)                         │
│         React · TypeScript · TailwindCSS                     │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTPS
┌────────────────────▼────────────────────────────────────────┐
│                    BACKEND API                               │
│              FastAPI (Python 3.12)                           │
│         Pydantic · SQLAlchemy · JWT Auth                     │
└───────┬────────────────────────────────┬────────────────────┘
        │                                │
┌───────▼────────┐              ┌────────▼───────────────────┐
│   PostgreSQL   │              │       ARQ Job Queue         │
│  (primary DB)  │              │  (Redis-backed, async)      │
└────────────────┘              └────────┬───────────────────┘
                                         │
                        ┌────────────────▼──────────────────┐
                        │     Multi-Agent Orchestrator       │
                        │  (Python · Claude API · 33 agents) │
                        └────────────────┬──────────────────┘
                                         │
              ┌──────────────────────────┼───────────────────┐
              │                          │                    │
   ┌──────────▼───────┐      ┌──────────▼──────┐  ┌─────────▼──────┐
   │  Remotion Render │      │  Manim Render   │  │ ElevenLabs TTS │
   │  (Node.js child) │      │ (Python subprocess)│  │     API        │
   └──────────┬───────┘      └──────────┬──────┘  └─────────┬──────┘
              │                          │                    │
              └──────────────────────────┼───────────────────┘
                                         │
                              ┌──────────▼──────────┐
                              │   FFmpeg (encode)    │
                              │   stitch + mux       │
                              └──────────┬──────────┘
                                         │
                              ┌──────────▼──────────┐
                              │   Cloudflare R2      │
                              │   (video storage)    │
                              └──────────┬──────────┘
                                         │
                              ┌──────────▼──────────┐
                              │   HLS Stream         │
                              │   → video.js player  │
                              └─────────────────────┘
```

### 8.2 Monorepo structure

```
focusly/
├── apps/
│   ├── web/                    # Next.js 15 frontend
│   │   ├── app/                # App Router pages
│   │   ├── components/
│   │   ├── lib/
│   │   └── package.json
│   │
│   └── api/                    # FastAPI backend
│       ├── src/
│       │   └── focusly/
│       │       ├── main.py
│       │       ├── core/
│       │       ├── api/
│       │       ├── domain/
│       │       ├── infrastructure/
│       │       ├── agents/     # all 33 agents
│       │       └── workers/    # ARQ job workers
│       ├── tests/
│       └── pyproject.toml
│
├── packages/
│   └── video-engine/           # Remotion compositions (Node.js)
│       ├── src/
│       │   ├── compositions/   # scene React components
│       │   ├── scenes/         # scene type library
│       │   └── render.ts       # CLI render entrypoint
│       └── package.json
│
├── docker/
│   ├── api.Dockerfile
│   ├── web.Dockerfile
│   └── video-engine.Dockerfile
│
├── docker-compose.yml          # local dev — all services
├── docker-compose.prod.yml     # production overrides
├── Makefile                    # all dev commands
└── .github/
    └── workflows/
        └── ci.yml
```

### 8.3 Technology decisions — final

| Layer | Technology | Rationale |
| --- | --- | --- |
| Frontend framework | Next.js 15 (App Router) | Known stack, RSC for performance |
| Styling | TailwindCSS + shadcn/ui | Fast to build, consistent |
| State management | Zustand + React Query | Minimal, no Redux complexity |
| Backend framework | FastAPI | Async-native, Pydantic integration, automatic OpenAPI docs |
| Language (backend) | Python 3.12 | Agent ecosystem, Manim compatibility |
| ORM | SQLAlchemy 2.0 async | Industry standard, type-safe |
| Migrations | Alembic | Pairs with SQLAlchemy |
| Database | PostgreSQL 16 | Single database, proven reliability |
| Job queue | ARQ (async Redis queue) | Simpler than Celery for async Python, fewer moving parts |
| Queue broker | Redis 7 | Required by ARQ, also used for rate limiting |
| Video composition | Remotion 4 | React-based, programmatic, image inserts, Lottie, Three.js |
| Math animation | Manim Community | Algorithm and equation animations |
| TTS | ElevenLabs API | Best quality, SSML pacing control |
| LLM (agents) | Claude API (claude-sonnet-4-6) | Script generation, scene decisions |
| Video encoding | FFmpeg | Industry standard, free |
| Object storage | Cloudflare R2 | S3-compatible, free egress |
| CDN | Cloudflare (auto with R2) | No additional config |
| Deployment | Railway | Simplest solo deployment, managed Postgres + Redis |
| Package manager (Python) | uv | Speed, lockfile, workspace support |
| Package manager (Node) | pnpm | Monorepo workspace support |
| Linting/formatting (Python) | ruff | Single tool, fast |
| Type checking (Python) | mypy strict | Catches runtime errors at build time |
| Testing (Python) | pytest + pytest-asyncio | Async-native testing |
| Testing (frontend) | Vitest + Playwright | Unit + E2E |
| Error tracking | Sentry | Free tier sufficient for MVP |
| CI/CD | GitHub Actions | Free for solo, integrates with Railway |

---

## 9\. Multi-Agent System Specification

### 9.1 Architecture pattern

The system uses the **orchestrator-worker pattern** with shared context state. All agents read from and write to a single `LessonContext` object stored in PostgreSQL (as JSONB) and updated atomically. No agent-to-agent direct messaging. The orchestrator is the only agent with write access to agent scheduling decisions.

### 9.2 Shared context schema

```python
# src/focusly/domain/models.py

```

`from pydantic import BaseModel, Field`  

`from typing import Any`

`class Misconception(BaseModel):`  

`concept: str`  

`wrong_belief: str`  

`corrective_framing: str`

`class LearnerProfile(BaseModel):`  

`level: str                    # beginner | intermediate | advanced`  

`assumed_prerequisites: list[str]`  

`vocabulary_ceiling: str`  

`adhd_accommodation: bool = True`

`class ScriptSegment(BaseModel):`  

`index: int`  

`text: str                     # narration text`  

`duration_seconds: float       # target duration`  

`emphasis_words: list[str]     # words to stress in TTS`  

`pause_before_ms: int = 0      # SSML pause before segment`  

`pause_after_ms: int = 0`

`class Scene(BaseModel):`  

`index: int`  

`scene_type: str               # remotion | manim | d3 | threejs`  

`template_name: str            # which Remotion composition to use`  

`duration_frames: int          # at 30fps`  

`script_segment_index: int     # links to script`  

`props: dict[str, Any]         # passed to Remotion component`  

`asset_paths: list[str]        # S3 paths of required assets`  

`generated_code: str | None    # Manim python or D3 script if applicable`

`class AudioAsset(BaseModel):`  

`segment_index: int`  

`file_path: str                # R2 path`  

`duration_ms: int`  

`word_timestamps: list[dict]   # word-level timing from ElevenLabs`

`class QuizQuestion(BaseModel):`  

`after_segment_index: int`  

`question: str`  

`options: list[str]            # 4 options always`  

`correct_index: int`  

`wrong_answer_explanations: list[str]  # why each wrong option is wrong`

`class AgentStatus(BaseModel):`  

`agent_id: str`  

`status: str                   # pending | running | done | failed`  

`started_at: str | None`  

`completed_at: str | None`  

`error: str | None`  

`retry_count: int = 0`

`class LessonContext(BaseModel):`  

`# Identity`  

`job_id: str`  

`user_id: str`  

`topic: str`

```
# Layer 2 outputs
learner_profile: LearnerProfile | None = None
lesson_outline: list\[str\] | None = None
misconception_map: list\[Misconception\] | None = None
learning_objectives: list\[str\] | None = None

# Layer 3 outputs
script: list\[ScriptSegment\] | None = None
hook_text: str | None = None
closing_summary: str | None = None
quiz_questions: list\[QuizQuestion\] | None = None

# Layer 4 outputs
scene_manifest: list\[Scene\] | None = None
asset_manifest: list\[str\] | None = None
design_tokens: dict | None = None
accessibility_audit_passed: bool = False

# Layer 5 outputs — code
generated_scenes: list\[Scene\] | None = None
caption_srt: str | None = None

# Layer 6 outputs — audio
audio_assets: list\[AudioAsset\] | None = None
final_audio_path: str | None = None

# Layer 7 outputs — QA
code_qa_passed: bool = False
visual_qa_passed: bool = False
sync_qa_passed: bool = False
educational_qa_passed: bool = False

# Layer 8 outputs — render
rendered_scene_paths: list\[str\] | None = None
final_video_path: str | None = None
hls_playlist_path: str | None = None
eval_score: float | None = None
eval_notes: str | None = None

# Agent tracking
agent_statuses: dict\[str, AgentStatus\] = Field(default_factory=dict)
```

### 9.3 Complete agent registry

Layer 1 — Orchestration

**A01 · MasterOrchestrator**

* Reads: initial job request
* Writes: task graph, agent schedule
* Spawns: all agents in dependency order
* Handles: agent failures (retry up to 3 times, then mark job failed)
* Model: claude-sonnet-4-6
* Timeout: monitors entire pipeline, 10-minute total limit

Layer 2 — Knowledge and Curriculum Planning

**A02 · AudienceCalibrationAgent**

* Input: topic, user's stated level preference
* Output: `learner_profile` in LessonContext
* Determines: vocabulary ceiling, assumed prerequisites, cognitive profile
* Model: claude-sonnet-4-6
* Timeout: 30 seconds

**A03 · CurriculumArchitectAgent**

* Input: topic, learner_profile
* Output: `lesson_outline` — ordered concept list with target durations
* Enforces: total duration ≤ 5 minutes, each segment ≤ 30 seconds
* Model: claude-sonnet-4-6
* Timeout: 45 seconds

**A04 · MisconceptionModelingAgent**

* Input: lesson_outline, learner_profile
* Output: `misconception_map` — per concept: wrong belief + corrective framing
* Critical: this is what separates accurate explanation from insight-generating explanation
* Model: claude-sonnet-4-6
* Timeout: 60 seconds

**A05 · LearningObjectiveAgent**

* Input: lesson_outline
* Output: `learning_objectives` — testable, measurable, one per concept
* These become acceptance criteria for A31 (Evaluator)
* Model: claude-sonnet-4-6
* Timeout: 30 seconds

Layer 3 — Script and Narrative

**A06 · ScriptWriterAgent**

* Input: lesson_outline, misconception_map, learner_profile
* Output: `script` — list of ScriptSegments with narration text
* Constraint: one concept per segment, max 7 words on screen at once
* Must produce: insight-generating explanation, not accurate-but-hollow description
* Model: claude-sonnet-4-6
* Timeout: 90 seconds

**A07 · PacingAgent**

* Input: script
* Output: updated script with pause_before_ms, pause_after_ms, emphasis_words, duration_seconds
* Injects: 1–2 second silence after hard concepts, emphasis markers before conceptual jumps
* Flags: any segment where information density exceeds ADHD safe threshold (> 2 new concepts in 30s)
* Model: claude-sonnet-4-6
* Timeout: 30 seconds

**A08 · HookAndRetentionAgent**

* Input: topic, script
* Output: `hook_text` (first 8 seconds), re-engagement cues at minute 1 and 2, `closing_summary`
* The hook must answer "why does this matter to me right now?" before any content
* Model: claude-sonnet-4-6
* Timeout: 30 seconds

**A09 · QuizCheckpointAgent**

* Input: script, misconception_map, learning_objectives
* Output: `quiz_questions` — one per major concept, targeting the misconception
* Format: 4-option MCQ with explanation for each wrong option
* Never: surface recall ("what is the name of...") — always: application or misconception correction
* Model: claude-sonnet-4-6
* Timeout: 60 seconds

Layer 4 — Visual Direction and Assets

**A10 · SceneDirectorAgent**

* Input: script, learner_profile
* Output: `scene_manifest` — each segment gets: scene_type, template_name, props
* Decision tree: mathematical → manim, data → d3, text/concept → remotion, 3D structure → threejs
* Model: claude-sonnet-4-6
* Timeout: 60 seconds

**A11 · VisualMetaphorAgent**

* Input: scene_manifest (for abstract concept scenes)
* Output: updated scene props with metaphor specifications
* Constraint: metaphor must be isomorphic to concept logic, not merely illustrative
* Examples: binary search → phone book page tearing, recursion → mirror facing mirror
* Model: claude-sonnet-4-6
* Timeout: 45 seconds

**A12 · AssetHunterAgent**

* Input: scene_manifest (asset requirements)
* Output: `asset_manifest` — file paths in R2 for each required asset
* Sources: Unsplash API (photos), LottieFiles public (animations), Iconify (icons)
* Validates: license compatibility before storing
* Language: Python with httpx
* Timeout: 120 seconds

**A13 · TypographyAndLayoutAgent**

* Input: lesson topic, learner_profile
* Output: `design_tokens` — font, sizes, palette, spacing rules
* Enforces: max 7 words per text element, minimum font size 32px at 1080p
* Manages: color-concept consistency map (same concept → same color across all scenes)
* Model: claude-sonnet-4-6
* Timeout: 20 seconds

**A14 · AccessibilityAgent**

* Input: design_tokens, scene_manifest
* Output: accessibility audit report, corrected design_tokens
* Checks: WCAG AA contrast (4.5:1 minimum), no flashing > 3Hz, caption readability
* Language: Python with Pillow for contrast calculation
* Timeout: 30 seconds

Layer 5 — Code Generation (parallel per scene)

**A15 · RemotionCoderAgent**

* Input: scene (type: remotion), design_tokens, asset_manifest, audio timing
* Output: complete `.tsx` Remotion scene component
* Templates available: KineticText, ImageOverlay, BulletReveal, ConceptMap, QuizScene, TransitionScene
* Validates: TypeScript compilation before marking done
* Model: claude-sonnet-4-6
* Timeout: 60 seconds per scene

**A16 · ManimCoderAgent**

* Input: scene (type: manim), design_tokens, narration segment text
* Output: complete Python Manim scene class file
* Only called for: equations, algorithm step-throughs, geometric proofs, data structure visualisations
* Validates: Python syntax check before marking done
* Model: claude-sonnet-4-6
* Timeout: 90 seconds per scene

**A17 · D3ChartCoderAgent**

* Input: scene (type: d3), data from asset_manifest, design_tokens
* Output: complete D3.js chart embedded in a Remotion `.tsx` component
* Scene types: bar charts, line graphs, scatter plots, network graphs
* Model: claude-sonnet-4-6
* Timeout: 60 seconds per scene

**A18 · ThreeJSCoderAgent**

* Input: scene (type: threejs), design_tokens
* Output: Three.js scene embedded in a Remotion `.tsx` component using Canvas
* Only called for: 3D molecular structures, architectural models, abstract 3D metaphors
* Used sparingly — only when 3D adds genuine understanding
* Model: claude-sonnet-4-6
* Timeout: 90 seconds per scene

**A19 · AnimationTimingAgent**

* Input: all generated scene code, audio_assets (word timestamps)
* Output: updated scene code with `interpolate()` calls aligned to exact frame numbers
* Precision target: visual change within ±2 frames of narration mention
* Language: Python — modifies generated code, does not generate new scenes
* Timeout: 30 seconds per scene

**A20 · CaptionAndSubtitleAgent**

* Input: script, audio_assets (word timestamps)
* Output: `caption_srt` — word-level timed SRT file
* Produces: styled caption component for Remotion (large text, high contrast)
* Language: Python
* Timeout: 20 seconds

Layer 6 — Audio Production

**A21 · TTSNarrationAgent**

* Input: paced script (with SSML markup)
* Output: `audio_assets` — per-segment MP3s with word-level timestamps
* API: ElevenLabs with SSML pacing control
* Handles: pause injection, emphasis, speaking rate variation per segment
* Language: Python with httpx
* Timeout: 60 seconds per segment, 5 minutes total

**A22 · MusicSelectionAgent**

* Input: lesson topic, target duration
* Output: background music file path in R2 with duck automation spec
* Source: Pixabay royalty-free music API
* Music requirements: BPM 70–90 (not too energetic), no lyrics, no high-frequency spikes
* Language: Python
* Timeout: 30 seconds

**A23 · SoundDesignAgent**

* Input: scene_manifest, audio_assets
* Output: sound cue manifest — event type + frame number for each cue
* Cue types: concept-reveal chime, highlight-click, quiz-reward, segment-transition
* Source: pre-curated sound library stored in R2
* Language: Python
* Timeout: 20 seconds

**A24 · AudioMixAgent**

* Input: audio_assets, music file, sound cue manifest
* Output: `final_audio_path` — single mixed MP3
* Process: ffmpeg normalise → duck music under narration → mix sound cues → export
* Language: Python with fluent-ffmpeg bindings
* Timeout: 60 seconds

Layer 7 — QA and Self-Correction

All QA agents operate in a retry loop: fail → send error context to originating agent → originating agent rewrites → QA reruns. Maximum 3 retries before escalating to orchestrator.

**A25 · CodeQAAgent**

* Runs: TypeScript compiler check on Remotion scenes, Python syntax on Manim scenes
* Checks: no missing imports, no undefined asset paths, no type errors
* On fail: sends full compiler error to A15/A16/A17/A18 for rewrite
* Timeout: 30 seconds per scene

**A26 · VisualQAAgent**

* Runs: preview render of first and last frame of each scene
* Checks: text overflow, contrast violations, elements outside safe zone, font size
* Uses: Pillow for image analysis of rendered frames
* On fail: sends specific frame issues to A13/A15 for correction
* Timeout: 60 seconds per scene

**A27 · SyncQAAgent**

* Checks: every visual keyframe is within ±2 frames of corresponding audio word timestamp
* Checks: scene transitions align with sentence boundaries
* On fail: sends drift measurements to A19 for timing correction
* Timeout: 30 seconds per scene

**A28 · EducationalQAAgent**

* Checks: every misconception in misconception_map is addressed in the script
* Checks: every learning objective in learning_objectives is covered by at least one scene
* Checks: no segment has more than 2 new concepts
* On fail: sends specific gap report to A06 for script revision
* Model: claude-sonnet-4-6
* Timeout: 45 seconds

Layer 8 — Render, Evaluation, and Memory

**A29 · RenderOrchestratorAgent**

* Triggers: full Remotion render for each approved scene
* Method: spawns Node.js child process running `@remotion/renderer`
* Collects: rendered MP4 per scene, uploads to R2
* Parallel: renders up to 3 scenes simultaneously
* Timeout: 3 minutes per scene render

**A30 · FFmpegStitchAgent**

* Input: all rendered scene MP4 paths, final_audio_path, caption_srt
* Process: concat scenes → mux audio → burn captions → inject chapter markers → HLS segment
* Output: `final_video_path`, `hls_playlist_path`, thumbnail sprite
* Language: Python with subprocess ffmpeg
* Timeout: 3 minutes

**A31 · LearningOutcomeEvaluatorAgent**

* Input: finished video metadata, script, learning_objectives, misconception_map
* Output: `eval_score` (0.0–1.0), `eval_notes` with specific improvement areas
* Scoring dimensions: explanation clarity, pacing, visual-narration coherence, objective coverage
* Threshold: score < 0.6 → flag for human review, do not fail the job
* Model: claude-sonnet-4-6
* Timeout: 60 seconds

**A32 · MemoryAgent**

* Input: completed LessonContext, eval_score
* Writes to: PostgreSQL `agent_memory` table (structured JSONB)
* Stores: metaphors that worked per concept type, scene types that scored highest, pacing patterns
* Future runs: A03, A10, A11 query this table before generating new lessons on similar topics
* Language: Python with SQLAlchemy
* Timeout: 20 seconds

**A33 · StudentFeedbackAgent**

* Triggered by: student completing a video (not during generation)
* Reads: watch-time analytics, quiz results, explicit rating
* Maps: drop-off points → specific scene indices
* Writes: scene quality scores to `agent_memory`, triggers regeneration for scenes scoring < 0.5
* Language: Python
* Timeout: 30 seconds (async, runs in background after video watched)

### 9.4 Agent execution flow

```
Job created
│
▼
A01 MasterOrchestrator — builds task graph
│
├─► A02 AudienceCalibration ──────────────────────────────┐
├─► A03 CurriculumArchitect (waits for A02)               │
├─► A04 MisconceptionModeling (waits for A03)             │ parallel
└─► A05 LearningObjective (waits for A03)                 │
│
├─► A06 ScriptWriter (waits for A04, A05) ────────────────┤
├─► A07 PacingAgent (waits for A06)                       │
├─► A08 HookAndRetention (waits for A06)                  │ parallel
└─► A09 QuizCheckpoint (waits for A04, A05, A06)          │
│
├─► A10 SceneDirector (waits for A07) ────────────────────┤
├─► A11 VisualMetaphor (waits for A10)                    │
├─► A12 AssetHunter (waits for A10)                       │ parallel
├─► A13 TypographyAndLayout (waits for A02)               │
└─► A14 Accessibility (waits for A13)                     │
│
\[for each scene — parallel\]                               │
├─► A15/A16/A17/A18 CodeGen (waits for A10–A14) ─────────┤
├─► A21 TTSNarration (waits for A07) — runs in parallel   │
└─► A19 AnimationTiming (waits for A15–A18 + A21)        │
│
├─► A20 CaptionSubtitle (waits for A21) ─────────────────┤
├─► A22 MusicSelection (waits for A03)                    │
├─► A23 SoundDesign (waits for A10, A21)                  │
└─► A24 AudioMix (waits for A21, A22, A23)               │
│
\[QA loop — all must pass\]                                 │
├─► A25 CodeQA                                            │
├─► A26 VisualQA                                          │
├─► A27 SyncQA                                            │
└─► A28 EducationalQA                                     │
│
├─► A29 RenderOrchestrator (waits for all QA pass) ───────┤
└─► A30 FFmpegStitch (waits for A29 + A24)               │
│
├─► A31 LearningOutcomeEvaluator ────────────────────────-┤
└─► A32 MemoryAgent                                       │
▼
Video ready
```

---

## 10\. Video Production Engine Specification

### 10.1 Remotion scene library

The following scene templates must be built as Remotion compositions before any agent code generation can work. These are not generated by AI — they are hand-built, tested, and parameterised templates that the AI agents populate with props.

| Template name | Description | Key props |
| --- | --- | --- |
| `KineticText` | Animated word-by-word text reveal | text, emphasis_words, duration, color |
| `ImageOverlay` | Full-bleed image with animated caption | src, caption, entry_animation |
| `BulletReveal` | Sequential bullet point reveal | items\[\], color, duration_per_item |
| `ConceptMap` | Animated node-connection diagram | nodes\[\], edges\[\], highlight_sequence |
| `AlgorithmStepThrough` | Embeds Manim output as Video | manim_src, caption, duration |
| `D3Chart` | Animated data visualisation | chart_type, data, duration |
| `QuizScene` | Pause + question + 4 options + answer reveal | question, options\[\], correct_index, explanations\[\] |
| `TransitionScene` | Between-segment breather | text, color, duration |
| `HookScene` | Opening attention capture | hook_text, topic, duration |
| `SummaryScene` | Closing concept recap | key_points\[\], duration |
| `ProgressMilestone` | Micro-reward at segment end | segment_number, total_segments |

### 10.2 ADHD design rules — hardcoded, not configurable

These rules are enforced programmatically in the render pipeline and cannot be overridden by any agent:

```python
ADHD_RULES = {
"max_segment_duration_seconds": 30,
"max_words_per_text_element": 7,
"min_font_size_px_at_1080p": 32,
"min_contrast_ratio": 4.5,           # WCAG AA
"max_concepts_per_segment": 2,
"progress_bar_always_visible": True,
"pause_after_hard_concept_ms": 2000,
"micro_reward_every_n_segments": 3,
"max_information_density_score": 0.7, # computed metric
}
```

### 10.3 Video output specification

| Property | Value |
| --- | --- |
| Resolution | 1920×1080 (1080p) |
| Frame rate | 30fps |
| Video codec | H.264 (libx264) |
| Audio codec | AAC 128kbps |
| Max file size | 150MB per lesson |
| HLS segment duration | 6 seconds |
| Thumbnail | Auto-generated at 50% mark |
| Captions | Burned into video + separate SRT file |

---

## 11\. Data Models

### 11.1 Database schema

```sql
-- Users
CREATE TABLE users (
id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
email       TEXT UNIQUE NOT NULL,
password_hash TEXT NOT NULL,
created_at  TIMESTAMPTZ DEFAULT NOW(),
updated_at  TIMESTAMPTZ DEFAULT NOW(),
is_verified BOOLEAN DEFAULT FALSE,
daily_generation_count INTEGER DEFAULT 0,
daily_reset_at TIMESTAMPTZ DEFAULT NOW()
);
```

`-- Refresh tokens`  

`CREATE TABLE refresh_tokens (`  

`id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),`  

`user_id     UUID REFERENCES users(id) ON DELETE CASCADE,`  

`token_hash  TEXT UNIQUE NOT NULL,`  

`expires_at  TIMESTAMPTZ NOT NULL,`  

`created_at  TIMESTAMPTZ DEFAULT NOW()`  

`);`

`-- Lesson jobs`  

`CREATE TABLE lesson_jobs (`  

`id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),`  

`user_id         UUID REFERENCES users(id) ON DELETE CASCADE,`  

`topic           TEXT NOT NULL,`  

`status          TEXT NOT NULL DEFAULT 'queued',`  

`-- queued | running | completed | failed`  

`context         JSONB,                    -- full LessonContext`  

`error_message   TEXT,`  

`created_at      TIMESTAMPTZ DEFAULT NOW(),`  

`started_at      TIMESTAMPTZ,`  

`completed_at    TIMESTAMPTZ,`  

`retry_count     INTEGER DEFAULT 0`  

`);`  

`CREATE INDEX idx_lesson_jobs_user_id ON lesson_jobs(user_id);`  

`CREATE INDEX idx_lesson_jobs_status ON lesson_jobs(status);`

`-- Completed lessons`  

`CREATE TABLE lessons (`  

`id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),`  

`job_id          UUID REFERENCES lesson_jobs(id),`  

`user_id         UUID REFERENCES users(id) ON DELETE CASCADE,`  

`topic           TEXT NOT NULL,`  

`video_path      TEXT NOT NULL,            -- R2 path`  

`hls_path        TEXT NOT NULL,`  

`thumbnail_path  TEXT,`  

`duration_seconds INTEGER,`  

`segment_count   INTEGER,`  

`eval_score      FLOAT,`  

`created_at      TIMESTAMPTZ DEFAULT NOW()`  

`);`  

`CREATE INDEX idx_lessons_user_id ON lessons(user_id);`

`-- Watch sessions`  

`CREATE TABLE watch_sessions (`  

`id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),`  

`lesson_id       UUID REFERENCES lessons(id) ON DELETE CASCADE,`  

`user_id         UUID REFERENCES users(id) ON DELETE CASCADE,`  

`watch_percentage FLOAT DEFAULT 0,`  

`last_position_seconds INTEGER DEFAULT 0,`  

`completed       BOOLEAN DEFAULT FALSE,`  

`started_at      TIMESTAMPTZ DEFAULT NOW(),`  

`updated_at      TIMESTAMPTZ DEFAULT NOW()`  

`);`

`-- Quiz attempts`  

`CREATE TABLE quiz_attempts (`  

`id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),`  

`lesson_id       UUID REFERENCES lessons(id) ON DELETE CASCADE,`  

`user_id         UUID REFERENCES users(id) ON DELETE CASCADE,`  

`question_index  INTEGER NOT NULL,`  

`selected_option INTEGER NOT NULL,`  

`is_correct      BOOLEAN NOT NULL,`  

`attempted_at    TIMESTAMPTZ DEFAULT NOW()`  

`);`

`-- Agent memory (long-term learning store)`  

`CREATE TABLE agent_memory (`  

`id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),`  

`memory_type     TEXT NOT NULL,`  

`-- metaphor | scene_performance | pacing | explanation`  

`topic_domain    TEXT,                     -- cs | math | biology | general`  

`content         JSONB NOT NULL,`  

`quality_score   FLOAT,`  

`usage_count     INTEGER DEFAULT 0,`  

`created_at      TIMESTAMPTZ DEFAULT NOW(),`  

`updated_at      TIMESTAMPTZ DEFAULT NOW()`  

`);`  

`CREATE INDEX idx_agent_memory_type ON agent_memory(memory_type);`  

`CREATE INDEX idx_agent_memory_domain ON agent_memory(topic_domain);`  

---

## 12\. API Specification

Base URL: `https://api.focusly.app/api/v1`

All authenticated endpoints require: `Authorization: Bearer <access_token>`

All responses follow: `{ "data": {...}, "error": null }` or `{ "data": null, "error": { "code": "...", "message": "..." } }`

### 12.1 Auth endpoints

```
POST   /auth/register          Register new user
POST   /auth/login             Login, returns access + refresh token
POST   /auth/refresh           Refresh access token
POST   /auth/logout            Invalidate refresh token
POST   /auth/verify-email      Verify email with token
POST   /auth/forgot-password   Request password reset
POST   /auth/reset-password    Reset password with token
```

### 12.2 Lesson generation endpoints

```
POST   /lessons/generate       Submit a new lesson generation job
Body: { topic: string, level?: "beginner"|"intermediate"|"advanced" }
Returns: { job_id: uuid, status: "queued" }
```

`GET    /lessons/jobs/:job_id   Poll job status`  

`Returns: { status, progress_percent, error_message? }`

`GET    /lessons               List user's completed lessons (paginated)`  

`Query: page, limit`  

`Returns: { lessons: [...], total, page }`

`GET    /lessons/:lesson_id    Get lesson details + signed video URL`  

`Returns: { lesson, video_url, hls_url, expires_at }`

`DELETE /lessons/:lesson_id    Delete a lesson and its video`  

### 12.3 Watch session endpoints

```
POST   /watch/:lesson_id/start         Start a watch session
PUT    /watch/:lesson_id/progress      Update watch position
Body: { position_seconds, percentage }
POST   /watch/:lesson_id/complete      Mark lesson as completed
```

### 12.4 Quiz endpoints

```
POST   /quiz/:lesson_id/attempt        Submit a quiz answer
Body: { question_index: int, selected_option: int }
Returns: { is_correct, explanation }
```

`GET    /quiz/:lesson_id/results        Get all quiz results for a lesson`  

### 12.5 Admin endpoints (no auth bypass — requires is_admin flag)

```
GET    /admin/jobs/queue           Current queue depth and running jobs
GET    /admin/jobs/stuck           Jobs running > 10 minutes
POST   /admin/jobs/:job_id/retry   Manually retry a failed job
GET    /admin/metrics              Basic system metrics
```

---

## 13\. Frontend Specification

### 13.1 Page map

```
/                       Landing page (public)
/login                  Login page
/register               Registration page
/dashboard              Student dashboard (authenticated)
/generate               New lesson generation page
/jobs/:job_id           Job status polling page (redirects to lesson when done)
/lessons/:lesson_id     Lesson watch page with custom player
/lessons/:lesson_id/quiz  Quiz results page
/settings               Account settings
```

### 13.2 Key component specifications

**GenerateForm** (`/generate`)

* Single text input for topic (max 200 chars, char counter visible)
* Level selector: Beginner / Intermediate / Advanced (defaults to Intermediate)
* Submit button disabled while a job is already in progress
* On submit: POST to `/lessons/generate`, redirect to `/jobs/:job_id`

**JobStatusPoller** (`/jobs/:job_id`)

* Polls `GET /lessons/jobs/:job_id` every 5 seconds
* Shows animated progress indicator with stage labels:
  * Planning your lesson...
  * Writing the script...
  * Designing scenes...
  * Generating animations...
  * Adding narration...
  * Quality checking...
  * Rendering video...
  * Almost there...
* On completion: auto-redirect to `/lessons/:lesson_id`
* On failure: show error message with retry button

**VideoPlayer** (`/lessons/:lesson_id`)

* Built on `video.js` with HLS plugin
* Custom controls: replay 10s button, chapter markers, speed selector
* Caption toggle (on by default)
* Quiz overlay: pauses video at checkpoint, renders quiz, resumes on answer
* Progress saved every 10 seconds via `PUT /watch/:lesson_id/progress`

**Dashboard** (`/dashboard`)

* Grid of lesson cards: topic, thumbnail, status badge, date, duration
* Empty state with CTA to generate first lesson
* Pagination (12 per page)
* No infinite scroll — simpler to implement and maintain

### 13.3 State management

* **Server state** (lessons, jobs, quiz results): React Query with 5-minute cache
* **UI state** (player position, quiz answers): Zustand local store
* **Auth state**: Zustand + httpOnly cookie (no JWT in localStorage)
* **No Redux** — over-engineered for this scale

---

## 14\. Infrastructure and DevOps

### 14.1 Local development

```yaml
# docker-compose.yml — everything needed to run locally
services:
postgres:
image: postgres:16-alpine
environment:
POSTGRES_DB: focusly_dev
POSTGRES_PASSWORD: devpassword
ports: \["5432:5432"\]
volumes: \["postgres_data:/var/lib/postgresql/data"\]
```

`redis:`  

`image: redis:7-alpine`  

`ports: ["6379:6379"]`

`api:`  

`build: ./apps/api`  

`depends_on: [postgres, redis]`  

`volumes: ["./apps/api:/app"]   # hot reload`  

`environment:`  

`DATABASE_URL: postgresql+asyncpg://postgres:devpassword@postgres/focusly_dev`  

`REDIS_URL: redis://redis:6379`  

`ports: ["8000:8000"]`  

`command: uv run uvicorn src.focusly.main:app --reload --host 0.0.0.0`

`worker:`  

`build: ./apps/api`  

`depends_on: [postgres, redis]`  

`environment:`  

`DATABASE_URL: postgresql+asyncpg://postgres:devpassword@postgres/focusly_dev`  

`REDIS_URL: redis://redis:6379`  

`command: uv run arq src.focusly.workers.main.WorkerSettings`

`video-engine:`  

`build: ./packages/video-engine`  

`volumes: ["./packages/video-engine:/app"]`  

`ports: ["3001:3001"]`

`web:`  

`build: ./apps/web`  

`volumes: ["./apps/web:/app"]`  

`ports: ["3000:3000"]`  

`environment:`  

`NEXT_PUBLIC_API_URL: http://localhost:8000`  

### 14.2 Environment variables

```bash
# .env.example — all required variables documented
```

# `Never commit .env — only .env.example`

# `App`

`ENVIRONMENT=development          # development | staging | production`  

`SECRET_KEY=                      # RS256 private key (generate with openssl)`  

`DEBUG=false`

# `Database`

`DATABASE_URL=                    # postgresql+asyncpg://...`

# `Redis`

`REDIS_URL=                       # redis://...`

# `External APIs`

`ANTHROPIC_API_KEY=               # Claude API`  

`ELEVENLABS_API_KEY=              # TTS`  

`ELEVENLABS_VOICE_ID=             # chosen voice`

# `Storage`

`CLOUDFLARE_R2_ACCOUNT_ID=`  

`CLOUDFLARE_R2_ACCESS_KEY_ID=`  

`CLOUDFLARE_R2_SECRET_ACCESS_KEY=`  

`CLOUDFLARE_R2_BUCKET_NAME=`  

`CLOUDFLARE_R2_PUBLIC_URL=`

# `Email (Phase 2 — leave empty for MVP to skip email verification)`

`SMTP_HOST=`  

`SMTP_PORT=`  

`SMTP_USER=`  

`SMTP_PASSWORD=`

# `Monitoring`

`SENTRY_DSN=`  

### 14.3 CI/CD pipeline

```yaml
# .github/workflows/ci.yml
name: CI
```

`on:`  

`push:`  

`branches: [main]`  

`pull_request:`  

`branches: [main]`

`jobs:`  

`backend:`  

`runs-on: ubuntu-latest`  

`services:`  

`postgres:`  

`image: postgres:16`  

`env: { POSTGRES_PASSWORD: test, POSTGRES_DB: focusly_test }`  

`options: --health-cmd pg_isready --health-interval 10s`  

`redis:`  

`image: redis:7`  

`options: --health-cmd "redis-cli ping" --health-interval 10s`  

`steps:`  

`- uses: actions/checkout@v4`  

`- uses: astral-sh/setup-uv@v4`  

`- run: cd apps/api && uv sync --all-extras`  

`- run: cd apps/api && uv run ruff check src tests`  

`- run: cd apps/api && uv run mypy src`  

`- run: cd apps/api && uv run pytest`  

`env:`  

`DATABASE_URL: postgresql+asyncpg://postgres:test@localhost/focusly_test`  

`REDIS_URL: redis://localhost:6379`

`frontend:`  

`runs-on: ubuntu-latest`  

`steps:`  

`- uses: actions/checkout@v4`  

`- uses: pnpm/action-setup@v4`  

`- run: cd apps/web && pnpm install`  

`- run: cd apps/web && pnpm lint`  

`- run: cd apps/web && pnpm typecheck`  

`- run: cd apps/web && pnpm test`

`deploy:`  

`needs: [backend, frontend]`  

`if: github.ref == 'refs/heads/main'`  

`runs-on: ubuntu-latest`  

`steps:`  

`- uses: actions/checkout@v4`  

`- name: Deploy to Railway`  

`run: railway up --service api`  

`env: { RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }} }`  

### 14.4 Deployment architecture (Railway — solo standard)

```
Railway project: focusly
├── Service: api          (FastAPI — gunicorn + uvicorn workers)
├── Service: worker       (ARQ job worker — 1 instance)
├── Service: web          (Next.js — Railway static build)
├── Plugin: postgres      (managed PostgreSQL 16)
└── Plugin: redis         (managed Redis 7)
```

`External:`  

`├── Cloudflare R2         (video and asset storage)`  

`└── Cloudflare DNS        (custom domain)`  

Estimated monthly cost at MVP scale (50 users):

* Railway Hobby plan: \~$20/month
* Cloudflare R2: \~$5/month (first 10GB free)
* ElevenLabs: \~$22/month (starter plan, 100k chars)
* Claude API: \~$15/month (estimated 50 generations/day)
* Sentry: free tier
* **Total: \~$62/month**

---

## 15\. Testing Strategy

### 15.1 Test pyramid

```
E2E tests (Playwright)         — 10% — critical user journeys only
Integration tests (pytest)     — 30% — agent pipeline, API routes, DB
Unit tests (pytest + Vitest)   — 60% — pure functions, agents, components
```

### 15.2 Critical path tests — must pass before any deploy

```python
# The 10 tests that must never fail
```

# `1. Full pipeline integration — topic in, job status out`

`def test_lesson_generation_job_created(client, db_session):`  

`response = client.post("/api/v1/lessons/generate",`  

`json={"topic": "binary search"})`  

`assert response.status_code == 202`  

`assert "job_id" in response.json()["data"]`

# `2. Agent context serialisation — no data loss between agents`

`def test_lesson_context_serialisation_roundtrip():`  

`ctx = LessonContext(job_id="test", user_id="u1", topic="recursion")`  

`ctx.learner_profile = LearnerProfile(level="intermediate", ...)`  

`serialised = ctx.model_dump_json()`  

`restored = LessonContext.model_validate_json(serialised)`  

`assert restored.learner_profile.level == "intermediate"`

# `3. ADHD rules enforced — no segment longer than 30 seconds`

`def test_adhd_rules_max_segment_duration(mock_script):`  

`paced = PacingAgent().run(mock_script, learner_profile=...)`  

`assert all(s.duration_seconds <= 30 for s in paced)`

# `4. Auth — unauthenticated request rejected`

`def test_unauthenticated_generate_rejected(client):`  

`response = client.post("/api/v1/lessons/generate",`  

`json={"topic": "test"})`  

`assert response.status_code == 401`

# `5. Rate limit — 11th generation in a day rejected`

`def test_daily_rate_limit_enforced(client, authenticated_user):`  

`# set daily_generation_count to 10`  

`for _ in range(11):`  

`response = client.post("/api/v1/lessons/generate", ...)`  

`assert response.status_code == 429`

# `6. Video URL signed — unsigned URL rejected by R2`

`def test_video_url_is_signed(client, completed_lesson):`  

`response = client.get(f"/api/v1/lessons/{completed_lesson.id}")`  

`url = response.json()["data"]["video_url"]`  

`assert "X-Amz-Signature" in url   # signed URL indicator`

# `7. QA retry loop — broken code triggers rewrite`

`def test_code_qa_triggers_rewrite_on_failure(mock_broken_scene):`  

`result = CodeQAAgent().run(mock_broken_scene)`  

`assert result.retry_count > 0`  

`assert result.status == "done"`

# `8. User isolation — user cannot access another user's lesson`

`def test_lesson_user_isolation(client, user_a_lesson, user_b_token):`  

`response = client.get(f"/api/v1/lessons/{user_a_lesson.id}",`  

`headers={"Authorization": f"Bearer {user_b_token}"})`  

`assert response.status_code == 404`

# `9. Job timeout — stuck job marked failed after 10 minutes`

`def test_stuck_job_marked_failed(worker, old_running_job):`  

`worker.check_stuck_jobs()`  

`assert old_running_job.status == "failed"`  

`assert old_running_job.error_message == "timeout"`

# `10. ADHD design tokens enforced — font size minimum`

`def test_design_tokens_enforce_min_font_size(mock_scene):`  

`tokens = TypographyAndLayoutAgent().run(topic="test", ...)`  

`assert tokens["min_font_size_px"] >= 32`  

### 15.3 Agent mocking strategy

In tests, external API calls (Claude, ElevenLabs) are always mocked. Real API calls only happen in the production pipeline. This keeps tests fast, deterministic, and free.

```python
# conftest.py
@pytest.fixture
def mock_claude_api(respx_mock):
respx_mock.post("https://api.anthropic.com/v1/messages").mock(
return_value=httpx.Response(200, json={
"content": \[{"type": "text", "text": '{"segments": \[...\]}'}\]
})
)
yield respx_mock
```

`@pytest.fixture`  

`def mock_elevenlabs_api(respx_mock):`  

`respx_mock.post("https://api.elevenlabs.io/v1/text-to-speech/...").mock(`  

`return_value=httpx.Response(200, content=b"fake_mp3_bytes")`  

`)`  

`yield respx_mock`  

---

## 16\. Build Phases and Milestones

### Phase 0 — Foundation (Weeks 1–2)

Goal: working development environment, database, authentication

* [ ] Monorepo scaffolded (apps/api, apps/web, packages/video-engine)



* [ ] Docker Compose working locally (postgres, redis, api, worker, web)



* [ ] FastAPI boilerplate: config, logging, database, migrations



* [ ] Auth endpoints: register, login, refresh, logout



* [ ] Next.js: login and register pages connected to API



* [ ] CI pipeline: lint + typecheck + test on every PR



* [ ] Railway deployment: staging environment live




**Milestone:** I can register, log in, and see an empty dashboard on staging.

### Phase 1 — Agent Foundation (Weeks 3–4)

Goal: orchestrator + planning agents working, producing a lesson context

* [ ] LessonContext data model + database schema complete



* [ ] ARQ job queue configured, worker running



* [ ] A01 MasterOrchestrator: task graph + agent scheduling



* [ ] A02 AudienceCalibration, A03 CurriculumArchitect, A04 MisconceptionModeling, A05 LearningObjective



* [ ] A06 ScriptWriter, A07 PacingAgent



* [ ] All agents tested with mocked Claude API



* [ ] POST /lessons/generate → job queued → planning agents run → context saved



* [ ] GET /lessons/jobs/:id → returns current agent status




**Milestone:** Submit "Explain binary search" → get a structured script back in the database.

### Phase 2 — Video Engine (Weeks 5–7)

Goal: Remotion scene library built, scenes rendering to MP4

* [ ] Remotion project scaffolded in packages/video-engine



* [ ] All 11 scene templates built and visually tested



* [ ] ADHD design rules hardcoded into templates



* [ ] KineticText and ImageOverlay working end-to-end



* [ ] Manim installed in Docker, BinarySearch example renders



* [ ] A10 SceneDirector, A11 VisualMetaphor, A13 TypographyAndLayout



* [ ] A15 RemotionCoder, A16 ManimCoder generating scene code



* [ ] A29 RenderOrchestrator: Node.js child process render



* [ ] Rendered MP4 uploaded to R2



* [ ] Signed URL returned from GET /lessons/:id




**Milestone:** Submit topic → agents generate scenes → Remotion renders → MP4 in R2 → watchable in browser.

### Phase 3 — Audio and Full Pipeline (Weeks 8–9)

Goal: narrated video with captions, quiz checkpoints

* [ ] A21 TTSNarrationAgent: ElevenLabs integration with SSML



* [ ] A19 AnimationTimingAgent: sync audio to frame



* [ ] A20 CaptionSubtitleAgent: SRT generation



* [ ] A22 MusicSelection, A23 SoundDesign, A24 AudioMix



* [ ] A30 FFmpegStitchAgent: concat + mux + burn captions



* [ ] A09 QuizCheckpointAgent + QuizScene template



* [ ] HLS segmentation working, video.js player with HLS



* [ ] Full pipeline: topic → video with narration, captions, quiz




**Milestone:** Full end-to-end working. Topic in, 3-minute narrated animated lesson out.

### Phase 4 — QA Agents and Polish (Week 10)

Goal: self-correcting pipeline, production-ready quality

* [ ] A25 CodeQA, A26 VisualQA, A27 SyncQA, A28 EducationalQA



* [ ] Retry loops working: broken scene → rewrite → recheck



* [ ] A31 LearningOutcomeEvaluator



* [ ] A32 MemoryAgent + agent_memory table



* [ ] Error handling: all failure modes produce useful error messages



* [ ] Rate limiting: 10 generations per user per day



* [ ] Sentry integrated: all unhandled exceptions tracked




**Milestone:** System self-corrects on broken scenes. Eval score stored. Ready for real users.

### Phase 5 — Production Launch (Week 11–12)

Goal: stable, monitored, production deployment with real users

* [ ] Production Railway environment configured



* [ ] Domain configured, HTTPS via Cloudflare



* [ ] All environment variables set in production



* [ ] Load test: 50 concurrent users, 3 concurrent renders — no degradation



* [ ] Runbook written: how to restart services, check queue, diagnose failures



* [ ] 10 beta users invited (RVCE students — Arjun's cohort)



* [ ] Watch analytics working: A33 StudentFeedbackAgent reading real data



* [ ] Week 1 post-launch review: eval scores, quiz pass rates, drop-off points




**Milestone:** 10 real students have watched at least one lesson each. Feedback collected.

---

## 17\. Risk Register

| Risk | Likelihood | Impact | Mitigation |
| --- | --- | --- | --- |
| Claude API generates syntactically broken Remotion code | High | High | CodeQA agent + 3 retry loops |
| Manim render takes too long (> 3 min per scene) | Medium | High | Timeout + fallback to Remotion static diagram |
| ElevenLabs API down | Low | Medium | Cache last successful audio; queue retry |
| FFmpeg stitch fails silently | Medium | High | Validate MP4 output file size > 0 and duration > 0 |
| R2 upload fails | Low | High | Retry with exponential backoff; alert via Sentry |
| Agent produces NSFW or harmful content | Low | High | Input validation + output content check before render |
| Railway service crash during render | Low | High | ARQ job persists in Redis; resumes on restart |
| Solo burnout on complex architecture | Medium | Critical | Phase gates — do not start Phase 2 until Phase 1 milestone is confirmed |
| Claude API cost runaway | Medium | Medium | Hard daily spend limit in Anthropic console; rate limit per user |
| Remotion Lambda cold start too slow | Medium | Medium | Use local renderer for MVP; Lambda only if scaling needed |

---

## 18\. Decisions Log

Record every architectural decision here. This prevents revisiting settled decisions and explains why things are the way they are.

| Date | Decision | Rationale | Alternatives rejected |
| --- | --- | --- | --- |
| May 2026 | ARQ over Celery for job queue | ARQ is async-native Python, fewer moving parts, Redis already required | Celery: requires separate result backend, more config |
| May 2026 | Railway over AWS | Solo engineer — Railway managed Postgres + Redis reduces ops surface area | AWS: powerful but overkill for MVP solo |
| May 2026 | Single PostgreSQL database | Avoid operational complexity of multiple datastores in MVP | Redis as primary: no ACID; Mongo: no relational queries |
| May 2026 | Remotion as primary engine, Manim as subprocess | Remotion handles all general scenes; Manim only for mathematical content | Manim for everything: too slow, wrong aesthetic for non-math |
| May 2026 | Polling not WebSockets for job status | Simpler to build, deploy, and debug for solo; polling every 5s is acceptable UX | WebSockets: additional complexity, stateful connections |
| May 2026 | No OAuth for MVP | Email/password is sufficient for 50 beta users; saves 1 week of build time | Google OAuth: adds dependency, more attack surface |
| May 2026 | Signed URLs for video access (1h expiry) | Security: no unauthenticated video access; CDN handles delivery | Public URLs: easier but no access control |
| May 2026 | httpOnly cookie for JWT | Protects against XSS token theft | localStorage: standard but vulnerable to XSS |

---

*End of document — version 1.0.0*

*Next review: after Phase 1 milestone is confirmed. Update decisions log and risk register as the build progresses.*