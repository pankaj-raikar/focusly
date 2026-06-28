# Focusly — Milestones and Execution Order

## Phase Overview

| Phase | Weeks | Goal | Milestone |
|-------|-------|------|-----------|
| 0 | 1-2 | Foundation | Register, login, empty dashboard on staging |
| 1 | 3-4 | Agent Foundation | Topic → structured script in database |
| 2 | 5-7 | Video Engine | Topic → agents → scenes → MP4 in R2 → watchable |
| 3 | 8-9 | Audio + Full Pipeline | Topic → 3-min narrated animated lesson with quiz |
| 4 | 10 | QA + Polish | Self-correcting pipeline, eval scores stored |
| 5 | 11-12 | Production Launch | 10 real students watched at least one lesson |

---

## Phase 0 — Foundation (Weeks 1-2)

**Goal:** Working dev environment, database, authentication, basic frontend.

### Week 1: Backend Foundation

- [M] Monorepo scaffold (pnpm workspaces, Turborepo)
- [M] Docker Compose (Postgres 16, Redis 7, API, Worker, Web)
- [M] FastAPI boilerplate: config, database, logging, exception handlers
- [M] Alembic migrations setup, initial schema (users, refresh_tokens)
- [M] Auth endpoints: register, login, refresh, logout
- [M] JWT RS256 + httpOnly cookie auth
- [M] API middleware: CORS, request ID, structured logging

### Week 2: Frontend + CI

- [M] Next.js 15 App Router scaffold
- [M] TailwindCSS + shadcn/ui setup
- [M] Login and register pages connected to API
- [M] Zustand auth store + protected route middleware
- [M] GitHub Actions CI: lint, typecheck, test for backend and frontend
- [M] Railway staging deployment
- [S] Landing page

**Gate:** I can register, log in, and see an empty dashboard on staging.

---

## Phase 1 — Agent Foundation (Weeks 3-4)

**Goal:** LangChain/LangGraph setup, planning agents produce a structured lesson context.

### Week 3: Infrastructure + Knowledge Agents

- [M] LangChain ChatAnthropic setup with retry config
- [M] Prompt template system (markdown files + loader)
- [M] PydanticOutputParser for structured extraction
- [M] LessonContext data model + database schema (lesson_jobs JSONB)
- [M] ARQ job queue configured, worker running
- [M] LangGraph StateGraph skeleton (state definition, empty nodes)
- [M] A01 MasterOrchestrator (initialize job, track progress)
- [M] A02 AudienceCalibrationAgent (topic → LearnerProfile)
- [M] A03 CurriculumArchitectAgent (profile → lesson outline)
- [M] A04 MisconceptionModelingAgent (outline → misconception map)
- [M] A05 LearningObjectiveAgent (outline → objectives)

### Week 4: Script Agents + Integration

- [M] A06 ScriptWriterAgent (outline + misconceptions → script segments)
- [M] A07 PacingAgent (script → paced script with pauses/emphasis)
- [M] A08 HookAndRetentionAgent (topic → hook text + closing summary)
- [M] A09 QuizCheckpointAgent (script + objectives → quiz questions)
- [M] All agents tested with mocked Claude API (respx)
- [M] POST /lessons/generate → job queued → planning agents run → context saved
- [M] GET /lessons/jobs/:id → returns current agent status + progress
- [M] GenerateForm + JobStatusPoller frontend connected
- [S] Redis-backed LLM response cache

**Gate:** Submit "Explain binary search" → get a structured script with segments, hooks, quizzes in the database.

---

## Phase 2 — Video Engine (Weeks 5-7)

**Goal:** Remotion scene library built, Manim rendering working, scenes rendering to MP4.

### Week 5: Remotion Templates

- [M] Remotion project scaffolded in packages/video-engine
- [M] ADHD design rules hardcoded (max 30s segment, max 7 words, min 32px font)
- [M] Design tokens module (colors, fonts, spacing)
- [M] KineticText composition (animated word-by-word reveal)
- [M] ImageOverlay composition (full-bleed image + caption)
- [M] BulletReveal composition (sequential bullet reveal)
- [M] TransitionScene composition (between-segment breather)
- [M] A10 SceneDirectorAgent (script → scene manifest)
- [M] A11 VisualMetaphorAgent (abstract concepts → metaphor specs)

### Week 6: Manim + More Templates

- [M] Manim Docker setup (Cairo, Pango, LaTeX, FFmpeg)
- [M] ManimRenderService (subprocess with 90s timeout)
- [M] Manim code validation (syntax, Scene class, construct method)
- [M] BinarySearch example scene renders to MP4
- [M] Fallback: Manim failure → Remotion static diagram
- [M] A16 ManimCoderAgent (scene spec → Manim Python code)
- [M] A15 RemotionCoderAgent (scene spec → Remotion TSX code)
- [M] ConceptMap composition
- [M] A12 AssetHunterAgent (scene manifest → Unsplash images)
- [M] A13 TypographyAndLayoutAgent (design tokens)
- [M] A14 AccessibilityAgent (WCAG AA audit)

### Week 7: Rendering Pipeline

- [M] A29 RenderOrchestratorAgent (spawn Node.js child process for Remotion)
- [M] RenderResourceManager (max 3 concurrent renders)
- [M] FFmpeg conversion (codec alignment for Manim output)
- [M] Cloudflare R2 integration (upload rendered MP4s)
- [M] Signed URL generation for video access
- [M] GET /lessons/:id returns signed video URL
- [M] VideoPlayer component with video.js + HLS
- [M] QuizScene composition
- [M] HookScene + SummaryScene + ProgressMilestone compositions
- [M] A17 D3ChartCoderAgent, A18 ThreeJSCoderAgent
- [S] D3Chart composition
- [C] ThreeJS integration in Remotion

**Gate:** Submit topic → agents generate scenes → Remotion+Manim render → MP4 in R2 → watchable in browser.

---

## Phase 3 — Audio and Full Pipeline (Weeks 8-9)

**Goal:** Narrated video with captions, quiz checkpoints, HLS streaming.

### Week 8: Audio Production

- [M] A21 TTSNarrationAgent (ElevenLabs API + SSML pacing)
- [M] Word-level timestamp extraction from ElevenLabs response
- [M] A19 AnimationTimingAgent (sync visuals to audio timestamps)
- [M] A20 CaptionSubtitleAgent (SRT generation from word timestamps)
- [M] A22 MusicSelectionAgent (Pixabay royalty-free music)
- [M] A23 SoundDesignAgent (sound cue manifest)
- [M] A24 AudioMixAgent (ffmpeg: normalize → duck → mix → export)
- [M] Audio upload to R2

### Week 9: Stitching + Quiz + HLS

- [M] A30 FFmpegStitchAgent (concat scenes → mux audio → burn captions → HLS)
- [M] HLS segmentation (6s segments, master playlist)
- [M] VideoPlayer with chapter markers, speed control, caption toggle
- [M] QuizOverlay component (pause video at checkpoint, show question, resume on answer)
- [M] Quiz attempt API + results
- [M] Watch session tracking (progress saved every 10s)
- [M] Replay last 10 seconds button
- [M] Full pipeline end-to-end: topic → video with narration, captions, quiz
- [S] Keyboard shortcuts (space, arrows)
- [S] Watch position persistence

**Gate:** Full end-to-end working. Topic in, 3-minute narrated animated lesson with quiz checkpoints out.

---

## Phase 4 — QA and Polish (Week 10)

**Goal:** Self-correcting pipeline, production-ready quality.

- [M] A25 CodeQA (TypeScript/Python compilation check)
- [M] A26 VisualQA (frame preview analysis)
- [M] A27 SyncQA (audio-visual alignment check)
- [M] A28 EducationalQA (objective coverage check)
- [M] QA retry loops in LangGraph (conditional edges, max 3 retries)
- [M] A31 LearningOutcomeEvaluator (eval_score 0-1)
- [M] A32 MemoryAgent (store learnings to agent_memory table)
- [M] Error handling: all failure modes produce useful error messages
- [M] Rate limiting: 10 generations per user per day
- [M] Sentry integrated: all unhandled exceptions tracked
- [M] Daily generation count reset (ARQ cron job)
- [M] Stuck job detection and auto-fail
- [S] Token usage tracking and cost reporting
- [S] Chain run observability (latency, tokens, cost per agent)

**Gate:** System self-corrects on broken scenes. Eval scores stored. Ready for real users.

---

## Phase 5 — Production Launch (Weeks 11-12)

**Goal:** Stable, monitored, production deployment with real users.

### Week 11: Production Setup

- [M] Production Railway environment configured
- [M] Domain configured (focusly.app), HTTPS via Cloudflare
- [M] All environment variables set in production
- [M] Database backup cron to R2 (daily)
- [M] Health check endpoint
- [M] Sentry alerts configured
- [M] Load test: 50 concurrent users, 3 concurrent renders — no degradation
- [M] Runbook: how to restart services, check queue, diagnose failures

### Week 12: Beta Launch

- [M] 10 beta users invited (RVCE students)
- [M] A33 StudentFeedbackAgent reading real watch analytics
- [M] Watch analytics: drop-off points mapped to scene indices
- [M] Quiz pass rate tracking
- [M] Week 1 post-launch review: eval scores, quiz pass rates, drop-off points
- [S] Dashboard usage stats (total lessons, total watch time)
- [S] Settings page (change password)

**Gate:** 10 real students have watched at least one lesson each. Feedback collected.

---

## Dependencies Between Phases

```
Phase 0 ──► Phase 1 ──► Phase 2 ──► Phase 3 ──► Phase 4 ──► Phase 5
                                        │
                                        └──► Phase 3 can begin partial work
                                             on audio while Phase 2 finishes
                                             remaining templates
```

**Hard gates:** Do not start Phase 2 until Phase 1 milestone is confirmed. Do not start Phase 5 until Phase 4 milestone is confirmed.

---

## Solo Engineer Daily Schedule

| Time | Activity | Duration |
|------|----------|----------|
| Morning (9-11 AM) | Implementation — write new code | 2 hours |
| Afternoon (1-3 PM) | Testing + refactoring — fix what broke | 2 hours |
| Evening (4-5 PM) | Review + deploy + docs — commit, push, update docs | 1 hour |

Weekly target: 25 hours focused development time.

---

## Risk Gates

After each phase, review before proceeding:

1. Is the milestone met? If not, **do not proceed.** Fix first.
2. Are there >3 known bugs from this phase? Fix before moving on.
3. Is test coverage ≥80%? If not, write more tests.
4. Is the deployment stable? If not, stabilize before adding complexity.

---

## Task Summary by Priority

| Priority | Count | Description |
|----------|-------|-------------|
| M (Must) | 89 | Core features, MVP blockers |
| S (Should) | 24 | Quality-of-life, important but not blockers |
| C (Could) | 11 | Nice-to-have, Phase 2+ |

Total estimated effort: 12 weeks, 25 hours/week = 300 hours.
