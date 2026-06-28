# Focusly — AI-Driven Animated Learning Platform

> **For Every Learner · ADHD-Optimized by Default**
> **Spec-Driven Architecture · Solo Engineer Edition**
> Generated: 2026-05-18 | Updated: 2026-05-19 | Status: ACTIVE

---

## Problem Statement

College students — particularly those with ADHD or attention difficulties — experience a persistent broken learning loop: they attend lectures, lose focus at complex concepts, review text-heavy slides, find generic YouTube videos misaligned with their syllabus, face scheduling friction with peers/TAs, and ultimately cram before exams. The comprehension gap compounds each semester, affecting grades, confidence, and career readiness.

This problem is most acute for ADHD learners, but the underlying failure is universal: the absence of on-demand, course-specific, visually animated, appropriately-paced explanations targeted at the exact misconception the student holds. Every learner benefits from well-paced, visually clear, concise content — ADHD accommodations simply make the content better for everyone.

**Design philosophy:** Focusly is built for all learners, with ADHD-optimization as the default quality bar. Short segments, visual clarity, minimal cognitive load, and embedded active recall aren't "accommodations" — they're just good teaching.

## Evidence

- **User quote (persona):** "I get the concept but I miss the steps in between. Lecture notes just confuse me more." — Arjun Mehta, 2nd-year B.E. CS, RVCE Bangalore
- **Market gap:** No existing product combines course-specific + visual-animated + on-demand + ADHD-paced + programmatically generated content
- **Universal design insight:** Research in cognitive load theory (Sweller) and multimedia learning (Mayer) shows that ALL learners benefit from short segments, dual coding (visual + verbal), and active retrieval practice — the same principles that help ADHD learners

## Proposed Solution

Focusly converts lecture notes, syllabi, and topic prompts into programmatically generated animated lesson videos — optimized for focus and retention by default — through a multi-agent AI orchestration system (LangGraph + LangChain + multi-provider LLMs), rendered by Remotion (React-based compositions) and Manim (mathematical animations), narrated by ElevenLabs TTS, and delivered via HLS streaming — with no human editor in the loop.

## Key Hypothesis

We believe programmatically generated, focus-optimized animated lessons will improve comprehension and retention for all engineering students compared to generic YouTube videos and text-heavy lecture notes. We'll know we're right when quiz pass rates reach ≥70% on first attempt and ≥60% of beta users report the platform helps them learn concepts they previously struggled with.

## What We're NOT Building

- Real-time collaborative features — solo engineer constraint, no WebSockets
- Live lecture processing — requires institutional integration, Phase 3+
- Custom avatar/character animation — complex 3D pipeline, out of scope for solo
- Content marketplace (user-uploaded lessons) — content moderation burden
- Social/community features — not core to the learning loop
- Native mobile app before web MVP is stable — React Native deferred
- On-premise deployment for institutions — ops complexity exceeds solo capacity
- Full LMS (gradebook, assignments, course management) — Focusly is a supplementary tool, not a replacement

## Success Metrics

| Metric | Target | How Measured |
|--------|--------|--------------|
| Pipeline success rate | ≥90% produce valid MP4 | Job status tracking in PostgreSQL |
| ADHD pacing compliance | 100% segments ≤30s | Automated QA check in A27 SyncQA |
| Learning objective coverage | ≥85% per video | A28 EducationalQA scoring |
| Time to video ready | ≤5 minutes for 3-min lesson | Job created_at → completed_at |
| Quiz pass rate (1st attempt) | ≥70% | Quiz attempts table |
| Beta user satisfaction | ≥60% report improvement | Post-launch survey (Week 12) |
| Weekly maintenance hours | ≤10 hours post-launch | Self-tracked |

## Open Questions

- [ ] What is the break-even point at ₹299-499/month pricing?
- [ ] Is 5 minutes realistic for a pipeline involving 33 LLM calls, Manim rendering, TTS, and FFmpeg? (Answer: depends on topic depth — simple topics fast, deep topics slower)

## Decisions Made (2026-05-19)

1. **Platform is for ALL users, not just ADHD.** ADHD-optimization is the default quality bar (short segments, visual clarity, embedded recall). Every learner benefits.
2. **Keep full 33-agent plan AND create a reduced 8-12 agent plan.** The 33-agent plan represents high-thoughtfulness output quality. The 8-12 agent plan is for faster iteration and MVP validation. Both are valid paths.
3. **Copyrighted materials — not a concern now.** Deferred. Will address when building the PDF/PPTX upload feature (Phase 2+).
4. **GDPR compliance — not a concern now.** Deferred. Will address when scaling beyond beta users.
5. **Multi-model strategy for cost optimization.** Easy/routine agents use small, cheap models (Haiku 4.5, Gemini Flash, GPT-4o-mini). High-reasoning agents use premium models (Claude Opus/Sonnet). Model assignment is per-agent, configurable via LangChain.
6. **Generation time is variable by design.** Simple topics: fast. Deep topics: slower. User can select depth level (quick overview / standard / deep dive), which affects agent count and render time. No hard 5-minute cap — instead, show realistic time estimates before generation starts.

---

## Users & Context

### Primary User — Arjun Mehta (the ADHD learner)

- **Who:** 2nd-year B.E. Computer Science, RV College of Engineering, Bangalore. Diagnosed ADHD, takes medication, tech-savvy.
- **Current behavior:** Understands big-picture concepts quickly, loses detail in sequential steps. Studies in 15-20 minute bursts, highest focus 9-11pm. Uses Notion and Forest app.
- **Trigger:** Attends a lecture, loses focus at a complex concept. Reviews slides, remains confused. Searches YouTube, finds generic 30-minute videos misaligned with his syllabus.
- **Success state:** Types "Explain binary search," receives a precisely paced, visually animated, course-specific lesson video within minutes, passes the embedded quiz checkpoint.

### Secondary User — Meera Iyer (the self-aware struggler)

- **Who:** 3rd-year B.E. Electronics, no formal ADHD diagnosis but exhibits strong attention difficulties. Relies heavily on YouTube.
- **Trigger:** YouTube video on quicksort uses a completely different approach than her professor.
- **Success state:** Gets course-specific content tailored to her exact syllabus and teaching approach.

### Tertiary User — Professor Ramesh (content source, passive)

- **Who:** Associate Professor, Data Structures and Algorithms. Concerned about his lecture notes being processed by AI.
- **Win condition:** Sees the output and it correctly represents his teaching approach.

### Job to Be Done

When I'm studying a concept from my engineering syllabus and the lecture/textbook doesn't make sense to me, I want to get a short, visually animated explanation that matches my course's approach, so I can understand the concept and pass my exam without spending hours searching YouTube.

### Non-Users

- K-12 students — different learning needs, different content depth
- Graduate researchers — need academic rigor, not ADHD-paced simplification
- Corporate training — different content structure, different pricing model
- Self-taught programmers — no syllabus to match against

---

## Solution Detail

### Core Capabilities (MoSCoW)

| Priority | Capability | Rationale |
|----------|------------|-----------|
| Must | User authentication (email + password) | Account management, progress tracking |
| Must | Topic prompt input and lesson generation | Core value proposition |
| Must | Multi-agent pipeline: script → scene → code → audio → render → deliver | The entire product |
| Must | Programmatic video: Remotion (general) + Manim (math) | Visual animation engine |
| Must | TTS narration with pacing control | ADHD-paced audio delivery |
| Must | Quiz checkpoints embedded in video segments | Active recall, retention testing |
| Must | Video streaming via HLS to custom player | Delivery mechanism |
| Must | Basic student dashboard | Lesson history, status tracking |
| Must | Job queue with status polling | Async processing UX |
| Must | PostgreSQL data persistence | State management |
| Should | Email verification on registration | Account security |
| Should | Password reset via email link | User self-service |
| Should | In-app notification when video is ready | Reduce polling anxiety |
| Should | User can regenerate failed lesson at no cost | Fair error handling |
| Should | Playback speed control (0.75x, 1.25x, 1.5x) | Personal preference |
| Should | Keyboard shortcuts (space, arrows) | Power user efficiency |
| Should | Watch position persistence | Return to where you left off |
| Could | Google OAuth | Convenience, lower friction |
| Could | User can specify audience level (beginner/intermediate/advanced) | Personalization |
| Could | User can upload PDF/PPTX as context | Course-specific content |
| Could | Picture-in-picture mode | Multitasking learners |
| Could | Basic usage stats (total lessons, total watch time) | Engagement awareness |
| Won't | SSO/SAML for institutions | Phase 2+ |
| Won't | Real-time generation progress stream | Polling is sufficient for MVP |
| Won't | Download MP4 | Requires watermarking first |
| Won't | Multi-language narration | Phase 2+ |
| Won't | Spaced repetition scheduling | Phase 2+ |

### MVP Scope

A user can input a topic, the system generates a complete animated lesson video with narration and quiz checkpoints, and the video is streamed back to the user within 5 minutes. Everything else is post-MVP.

### User Flow

1. User registers with email/password → lands on dashboard (empty state)
2. User clicks "Generate" → types topic "binary search" → selects "Intermediate"
3. System returns job ID → redirects to polling page with animated progress
4. Pipeline runs: planning → scripting → scene design → code generation → narration → QA → render → stitch
5. User auto-redirects to lesson page → video plays with HLS streaming
6. Quiz checkpoint pauses video → user answers → sees explanation → video resumes
7. Video completes → user returns to dashboard → lesson appears with status "completed"

---

## Technical Approach

**Feasibility:** MEDIUM-HIGH

Two execution paths exist (see Implementation Phases below):
- **Path A — Full 33-Agent Pipeline:** Maximum output quality. Every concern (pacing, metaphors, accessibility, sync, educational coverage) gets its own specialized agent. 12-week build.
- **Path B — Reduced 10-Agent Pipeline:** Faster to build, faster to iterate. Merges related agents into composite nodes. 8-week build. Can evolve into Path A over time.

Both use the same infrastructure (LangGraph, LangChain, Remotion, Manim, FFmpeg). The difference is agent granularity, not architecture.

### Multi-Model Strategy

Not every agent needs the most expensive model. LangChain allows per-agent model configuration:

| Agent Tier | Models | Examples | Cost/1M tokens (approx) |
|-----------|--------|----------|------------------------|
| Heavy reasoning | Claude Opus 4.6, o3 | A03 Curriculum, A04 Misconceptions, A31 Evaluator | $15-30 |
| Standard intelligence | Claude Sonnet 4.6 | A06 Script, A10 SceneDirector, A15-A18 CodeGen | $3-15 |
| Lightweight / routine | Haiku 4.5, GPT-4o-mini, Gemini Flash | A07 Pacing, A13 Typography, A20 Captions | $0.25-1 |
| Non-LLM | (no model) | A14 Accessibility (Python), A19 Timing (Python), A24 Mix (FFmpeg), A25-A27 QA (validators) | $0 |

**Estimated cost per lesson (3-min, standard depth):**
- Heavy reasoning agents (2 calls): ~$0.08
- Standard agents (8 calls): ~$0.12
- Lightweight agents (6 calls): ~$0.02
- Non-LLM agents: $0.00
- ElevenLabs TTS: ~$0.10
- **Total: ~$0.32/lesson**

### Variable Generation Time

Generation time scales with topic complexity and user-selected depth:

| Depth Level | Agents Used | Estimated Time | Description |
|-------------|------------|----------------|-------------|
| Quick Overview | 8 agents | 2-3 min | 1-2 min video, basic visuals, no deep metaphors |
| Standard (default) | 15-20 agents | 4-6 min | 3 min video, full visuals, quiz checkpoints |
| Deep Dive | 25-33 agents | 8-12 min | 5 min video, rich metaphors, multiple quiz points, music |

The UI shows a time estimate before generation starts. Users choose their depth level.

### Technology Stack

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| Frontend | Next.js 15 (App Router), React, TypeScript, TailwindCSS, shadcn/ui | Known stack, RSC performance |
| State | Zustand + React Query | Minimal, no Redux complexity |
| Backend | FastAPI (Python 3.12), Pydantic, SQLAlchemy 2.0 async | Async-native, type-safe, auto OpenAPI |
| ORM | SQLAlchemy 2.0 async | Industry standard |
| Migrations | Alembic | Pairs with SQLAlchemy |
| Database | PostgreSQL 16 | Single DB, JSONB for agent state, proven reliability |
| Job queue | ARQ (async Redis queue) | Simpler than Celery, fewer moving parts |
| Broker | Redis 7 | Required by ARQ, also rate limiting + cache |
| Agent orchestration | LangGraph | StateGraph for DAG execution, checkpointing, conditional edges |
| LLM pipeline | LangChain | Structured output, tools, memory, caching, callbacks |
| LLM (primary) | Claude Sonnet 4.6 via LangChain | Script, scene decisions, code gen |
| LLM (lightweight) | Haiku 4.5, GPT-4o-mini, Gemini Flash | Simple agents: pacing, typography, captions |
| LLM (reasoning) | Claude Opus 4.6, o3 | Complex agents: curriculum, misconceptions, evaluation |
| LLM routing | LangChain model config per agent | Model selection based on task complexity |
| Video composition | Remotion 4 | React-based, programmatic, templates |
| Math animation | Manim Community | LaTeX-quality equations, algorithm step-throughs |
| TTS | ElevenLabs API | Best quality, SSML pacing control |
| Video encoding | FFmpeg | Industry standard, free |
| Object storage | Cloudflare R2 | S3-compatible, free egress |
| CDN | Cloudflare (auto with R2) | No additional config |
| Deployment | Railway | Simplest solo deployment, managed Postgres + Redis |
| Package manager (Python) | uv | Speed, lockfile |
| Package manager (Node) | pnpm | Monorepo workspace support |
| Linting | ruff (Python), eslint (TypeScript) | Fast, comprehensive |
| Type checking | mypy strict (Python), tsc strict (TypeScript) | Catch errors at build time |
| Testing | pytest + pytest-asyncio, Vitest, Playwright | Unit + integration + E2E |
| Monitoring | Sentry, structlog | Error tracking + structured logging |
| CI/CD | GitHub Actions | Free for solo, integrates with Railway |

### Technical Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Claude API generates broken Remotion/Manim code | High | High | CodeQA agent + 3 retry loops + validation before render |
| Manim render takes too long (>3 min/scene) | Medium | High | 90s timeout + fallback to Remotion static diagram |
| 5-minute generation target unrealistic | Medium | Medium | Parallel agents + TTS in parallel with code gen |
| ElevenLabs API down or cost scaling | Low-Medium | Medium | Cache successful audio; queue retry; track chars/day |
| FFmpeg stitch fails silently | Medium | High | Validate MP4 size > 0 and duration > 0 |
| Claude API model deprecation or pricing change | Low | High | Abstract behind LangChain; swap model via config |
| Railway limitations at render scale | Medium | Medium | Vertical scaling first; dedicated render workers for Phase 2 |
| Solo burnout from 33-agent complexity | Medium | Critical | Phase gates — reduce to 8-12 agents for MVP if needed |
| Processing copyrighted lecture materials | Medium | High | User must own content; ToS disclaimer; educator consent model |
| GDPR compliance for student watch analytics | Medium | Medium | Data retention policy, right to deletion, privacy notice |

---

## Implementation Phases

| # | Phase | Description | Status | Parallel | Depends | PRP Plan |
|---|-------|-------------|--------|----------|---------|----------|
| 1 | Foundation | Monorepo, Docker, FastAPI, Auth, CI/CD, Railway staging | pending | - | - | docs/planner/01, 02 |
| 2 | Agent Foundation | LangChain/LangGraph setup, planning agents, script generation | pending | - | 1 | docs/planner/05, 06 |
| 3 | Video Engine | Remotion templates, Manim setup, scene rendering | pending | with 4 | 2 | docs/planner/07 |
| 4 | Audio Pipeline | ElevenLabs TTS, music, sound, audio mixing | pending | with 3 | 2 | docs/planner/05 |
| 5 | Full Pipeline | FFmpeg stitching, HLS, quiz, video player | pending | - | 3, 4 | docs/planner/02 |
| 6 | QA & Polish | QA agents, retry loops, evaluator, memory, error handling | pending | - | 5 | docs/planner/06, 08 |
| 7 | Production Launch | Railway production, monitoring, beta users | pending | - | 6 | docs/planner/09 |

### Phase 1: Foundation (Weeks 1-2)

**Goal:** Working development environment, database, authentication, basic frontend.

**Scope:**
- Monorepo scaffold (pnpm workspaces + Turborepo)
- Docker Compose (Postgres 16, Redis 7, API, Worker, Web, Video Engine)
- FastAPI boilerplate: config, database, migrations, logging, exceptions
- Auth endpoints: register, login, refresh, logout
- Next.js scaffold: login, register, dashboard pages
- CI pipeline: lint + typecheck + test on every PR
- Railway staging deployment

**Success signal:** I can register, log in, and see an empty dashboard on staging.

**Reference docs:**
- `docs/planner/01-project-setup.md`
- `docs/planner/02-backend-implementation.md` (sections 2-4)
- `docs/architect/05-backend-frontend-architecture.md` (backend section)

### Phase 2: Agent Foundation (Weeks 3-4)

**Goal:** LangChain/LangGraph setup, planning and script agents producing structured lesson context.

**Scope:**
- LangChain ChatAnthropic setup, prompt templates, structured parsers
- LangGraph StateGraph skeleton with state definition
- LessonContext data model + JSONB schema
- ARQ job queue configured
- A01-A09 agents (orchestration + knowledge + script)
- POST /lessons/generate → job queued → agents run → context saved
- GenerateForm + JobStatusPoller frontend

**Success signal:** Submit "Explain binary search" → get structured script with segments, hooks, quizzes in the database.

**MVP Agent Reduction Note:** For MVP, consider merging A07 (Pacing) into A06 (ScriptWriter) and making A23 (SoundDesign) rule-based without LLM involvement. This reduces the active agent count from 33 to ~28 for initial build.

**Reference docs:**
- `docs/planner/05-langchain-pipeline.md`
- `docs/planner/06-langgraph-agents.md`
- `docs/architect/02-langgraph-state-machine.md`
- `docs/architect/03-langchain-architecture.md`

### Phase 3: Video Engine (Weeks 5-7, parallel with Phase 4)

**Goal:** Remotion scene library built, Manim rendering working, scenes rendering to MP4.

**Scope:**
- 11 Remotion scene templates with ADHD rules hardcoded
- Manim Docker setup, subprocess rendering with 90s timeout
- A10-A18 agents (visual direction + code generation)
- A29 RenderOrchestrator (Node.js child process)
- FFmpeg conversion for Manim output
- R2 integration, signed URLs
- VideoPlayer component with HLS

**Success signal:** Topic → agents generate scenes → Remotion+Manim render → MP4 in R2 → watchable in browser.

**Reference docs:**
- `docs/planner/07-manim-pipeline.md`
- `docs/architect/04-remotion-manim-rendering.md`

### Phase 4: Audio Pipeline (Weeks 5-7, parallel with Phase 3)

**Goal:** Narrated audio with timing data.

**Scope:**
- A21 TTSNarrationAgent (ElevenLabs API + SSML)
- Word-level timestamp extraction
- A19 AnimationTimingAgent (sync visuals to audio)
- A20 CaptionSubtitleAgent (SRT generation)
- A22 MusicSelectionAgent, A24 AudioMixAgent
- Mixed audio uploaded to R2

**Success signal:** Script segments → audio with word timestamps → mixed audio file in R2.

### Phase 5: Full Pipeline (Weeks 8-9)

**Goal:** End-to-end video with narration, captions, quiz checkpoints.

**Scope:**
- A30 FFmpegStitchAgent (concat + mux + burn captions + HLS)
- QuizScene template + quiz overlay component
- Watch session tracking + progress persistence
- Replay 10s, speed control, caption toggle
- Full pipeline end-to-end

**Success signal:** Full end-to-end working. Topic in, 3-minute narrated animated lesson with quiz out.

### Phase 6: QA & Polish (Week 10)

**Goal:** Self-correcting pipeline, production-ready quality.

**Scope:**
- A25-A28 QA agents with retry loops
- A31 LearningOutcomeEvaluator
- A32 MemoryAgent
- Error handling, rate limiting, Sentry integration
- Cost tracking per pipeline run

**Success signal:** System self-corrects on broken scenes. Eval scores stored. Ready for real users.

### Phase 7: Production Launch (Weeks 11-12)

**Goal:** Stable, monitored, production deployment with real users.

**Scope:**
- Production Railway environment
- Domain + HTTPS via Cloudflare
- Load test (50 concurrent users)
- 10 beta users invited
- A33 StudentFeedbackAgent reading real analytics
- Post-launch review

**Success signal:** 10 real students have watched at least one lesson each.

### Parallelism Notes

Phases 3 and 4 can run in parallel because video rendering and audio production are independent — scenes don't need audio to render, and TTS doesn't need rendered scenes. They merge in Phase 5 when FFmpeg stitches them together.

---

## Business Model

**Note:** This section was missing from the original PRD. It needs validation through pricing research.

### Proposed Pricing (Indian Market)

| Tier | Price | Limits | Target |
|------|-------|--------|--------|
| Free | ₹0 | 2 lessons/month, 2-min max | Trial users |
| Student | ₹299/month | 30 lessons/month, 5-min max | Primary persona (Arjun) |
| Pro | ₹499/month | 100 lessons/month, 5-min max, PDF upload | Power users, exam prep |

### Unit Economics (Estimated)

| Cost Component | Per Lesson (3-min) |
|---------------|-------------------|
| Claude API (14 LLM agents) | ~$0.15 |
| ElevenLabs TTS | ~$0.10 |
| Remotion/Manim compute | ~$0.05 |
| R2 storage + delivery | ~$0.01 |
| **Total cost per lesson** | **~$0.31** |

At ₹299/month ($3.50), a user generating 10 lessons costs $3.10 in API costs — leaving ~$0.40 margin before infrastructure. This needs validation: the margin is thin and requires either higher pricing or API cost optimization.

### Break-Even Analysis

At 50 paying users × ₹399/month average = ₹19,950/month (~$238). Infrastructure + API costs at this scale: ~$62/month (PRD estimate) + ~$31/month (50 users × 10 lessons × $0.31 × 10% usage) = ~$93/month. Profitable at current estimates, but scales linearly with usage.

---

## Decisions Log

| Decision | Choice | Alternatives Considered | Rationale |
|----------|--------|------------------------|-----------|
| Agent orchestration | LangGraph | Custom DAG engine, Celery graphs | Native StateGraph, checkpointing, conditional edges |
| LLM pipeline | LangChain | Raw Claude API calls | Structured output, tools, memory, caching, callbacks |
| Video engine | Remotion (primary) + Manim (math) | Manim only, Synthesia, D-ID | Programmatic control, no pre-recorded humans |
| Job queue | ARQ | Celery, Dramatiq | Async-native, fewer moving parts, solo-friendly |
| Auth tokens | httpOnly cookies | localStorage JWT | XSS protection |
| Job status | Polling (5s) | WebSockets, SSE | Simpler to build/deploy/debug |
| Database | Single PostgreSQL | PG + Mongo + vector DB | Avoid operational complexity |
| Deployment | Railway | AWS, Render, Fly.io | Managed Postgres + Redis, minimal ops |
| LLM caching | Redis-backed | In-memory, no caching | Cost savings for repeated topics |
| QA approach | LangGraph conditional edges | Simple retry loops | Clean routing back to specific failing agent |
| Multi-model strategy | Per-agent model selection | Single model for all | Cost optimization: cheap models for simple tasks |
| Platform scope | All learners, ADHD-optimized default | ADHD-only | Universal design: good pacing benefits everyone |
| Agent granularity | Both 33-agent and 10-agent plans | 33-agent only | Path A (quality) and Path B (speed) both valid |
| Generation time | Variable by depth level | Hard 5-min cap | Quick/Standard/Deep Dive options with time estimates |

---

## Documentation Map

All planning and architecture documents are organized under `docs/`:

### Planning Documents (`docs/planner/`)

| File | Content |
|------|---------|
| `01-project-setup.md` | Monorepo, Docker, CI/CD, Railway, Makefile |
| `02-backend-implementation.md` | FastAPI structure, all endpoints, middleware |
| `03-frontend-implementation.md` | Next.js pages, components, state management |
| `04-database-design.md` | 10 tables, SQL schema, JSONB, indexes |
| `05-langchain-pipeline.md` | Chains, tools, memory, caching, cost control |
| `06-langgraph-agents.md` | StateGraph, 33 nodes, edges, retry loops |
| `07-manim-pipeline.md` | Docker, subprocess, validation, fallback |
| `08-testing-strategy.md` | pytest, Vitest, Playwright, mocked LLM |
| `09-deployment-monitoring.md` | Railway config, Sentry, logging, backups |
| `10-milestones-execution-order.md` | 5 phases, 89 Must tasks, risk gates |

### Architecture Documents (`docs/architect/`)

| File | Content |
|------|---------|
| `01-high-level-system-design.md` | System diagram, tech stack, decisions |
| `02-langgraph-state-machine.md` | StateGraph topology, parallel execution |
| `03-langchain-architecture.md` | Chain patterns, tools, memory, observability |
| `04-remotion-manim-rendering.md` | 11 compositions, Manim pipeline, FFmpeg |
| `05-backend-frontend-architecture.md` | Layered backend, component hierarchy |
| `06-database-queue-storage.md` | Connections, queue lifecycle, R2 structure |
| `07-security-architecture.md` | Threat model, auth, signed URLs |
| `08-deployment-infrastructure.md` | Railway, CI/CD, scaling, cost projection |

---

## Risk Register (Expanded)

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| LLM generates broken Remotion/Manim code | High | High | CodeQA + 3 retries + syntax validation before render. Multi-model: use best code-gen model per task |
| Manim render takes >3 min per scene | Medium | High | 90s timeout + fallback to Remotion static diagram |
| Generation time varies unpredictably | Medium | Medium | Show time estimate before generation starts; depth level selector |
| Solo burnout on 33-agent architecture | Medium | Critical | Start with Path B (10 agents); evolve to Path A (33 agents) |
| ElevenLabs API down | Low | Medium | Cache last successful audio; queue retry |
| ElevenLabs cost scaling beyond budget | Medium | Medium | Track chars/day; consider cheaper TTS for non-critical segments |
| FFmpeg stitch fails silently | Medium | High | Validate MP4 file size > 0 and duration > 0 |
| R2 upload fails | Low | High | Retry with exponential backoff; alert via Sentry |
| Agent produces NSFW/harmful content | Low | High | Input validation + output content check before render |
| Railway service crash during render | Low | High | ARQ job persists in Redis; resumes on restart |
| Single LLM provider dependency | Medium | High | Multi-model strategy: LangChain abstracts provider, swap models via config |
| Railway limitations at render scale | Medium | Medium | Vertical scaling first; dedicated render workers for Phase 2 |
| Multi-model cost tracking complexity | Low | Medium | PipelineTokenTracker logs model + cost per agent; per-job cost ceiling |
| LLM provider rate limits (multi-provider) | Medium | Medium | Fallback chain: primary model → secondary model → cached response |

---

*Generated: 2026-05-18 | Updated: 2026-05-19*
*Status: ACTIVE — decisions made, two execution paths defined*
*Source PRD: Product Requirements Document.md (v1.0.0)*
*Supporting docs: 10 planner files + 8 architect files under docs/*
*Reduced agent plan: docs/planner/11-reduced-agent-plan.md*
