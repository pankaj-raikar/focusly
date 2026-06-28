# Focusly OpenAI + Kokoro MVP Implementation Plan

> **For Codex:** Use `executing-plans` to implement this plan task by task. Use the phase-specific skills listed below before editing each subsystem.

**Goal:** Prove that a learner will submit a topic and use a short, ADHD-friendly animated lesson with narration, captions, and quiz checkpoints.

**Architecture:** A Next.js web app calls a FastAPI service. The API runs one small sequential generation pipeline: OpenAI produces one validated lesson package, Kokoro creates local narration, Remotion renders scenes, and FFmpeg combines the result into an MP4. SQLite stores jobs and metadata; generated files stay on local disk.

**Tech Stack:** Next.js, TypeScript, Tailwind CSS, FastAPI, Pydantic, SQLite, SQLAlchemy, OpenAI Responses API, Kokoro, Remotion, FFmpeg, Vitest, pytest, Playwright.

---

## 1. Canonical-document analysis

The canonical docs describe a reasonable post-validation platform, not a fast MVP. They require ten LangGraph agents, LangChain, PostgreSQL, Redis/ARQ, R2, HLS, video.js, Remotion, Manim, Claude, and ElevenLabs before the first lesson can be tested with a learner.

The core product hypothesis needs only this path:

```text
topic
  -> structured lesson package
  -> narration audio
  -> rendered MP4 + WebVTT
  -> browser playback + quiz checkpoints
```

### Keep now

- Topic input with audience level and target duration.
- Three to five short lesson segments.
- Hook, recap, summary, low visual density, and quiz checkpoints.
- Job status and progress.
- Remotion, FFmpeg, captions, and accessible playback.
- Typed contracts and one end-to-end smoke test.

### Replace

| Canonical choice | MVP choice | Reason |
|---|---|---|
| Claude API | OpenAI Responses API with Structured Outputs | Direct Pydantic-compatible output; one provider call can create the complete lesson package. |
| ElevenLabs | Local Kokoro 82M | Apache-2.0 model, no runtime API account, simple Python integration. |
| Ten LangGraph agents | One four-stage Python pipeline | No graph is needed before retries, branches, and resume behavior become real problems. |
| LangChain | OpenAI Python SDK | A wrapper adds no value for one provider and one structured call. |
| PostgreSQL + Redis + ARQ | SQLite + one in-process background job | Enough for a single-instance private MVP. |
| Cloudflare R2 | Local `data/jobs/` storage | Avoid storage integration before deployment. |
| HLS + video.js | MP4 + native `<video>` | Browser-native playback and WebVTT already cover the MVP. |
| Remotion + Manim | Remotion only | Shapes, text, code, and simple diagrams cover initial lessons. |
| Full account system | No auth in the private MVP | Authentication does not test lesson usefulness. |

### Explicit MVP limits

- English narration only.
- One fixed Kokoro voice, configurable by environment variable.
- Lessons target 60–120 seconds and three to five segments.
- One API process and one generation job at a time.
- No arbitrary model-generated TSX or Python execution. OpenAI returns scene data; trusted templates render it.
- No uploads, external images, music, collaboration, billing, analytics SaaS, or mobile app.

## 2. MVP contracts

### Lesson package

OpenAI must return one strict structured object:

```python
class Segment(BaseModel):
    id: str
    title: str
    narration: str
    visual_type: Literal["title", "bullets", "comparison", "steps", "diagram"]
    visual_payload: dict[str, object]
    target_seconds: int


class QuizCheckpoint(BaseModel):
    after_segment_id: str
    question: str
    options: list[str]
    correct_option_index: int
    explanation: str


class LessonPackage(BaseModel):
    title: str
    hook: str
    learning_objectives: list[str]
    segments: list[Segment]
    quizzes: list[QuizCheckpoint]
    recap: list[str]
```

Validation rules:

- Three to five segments.
- One visual idea per segment.
- Two to four quiz options.
- At least one quiz for lessons over 60 seconds.
- Total target duration between 60 and 120 seconds.
- Narration and visible text must not contain raw HTML.

### Job states

```text
queued -> planning -> narrating -> rendering -> succeeded
                                            -> failed
```

The API exposes:

```text
POST /api/jobs
GET  /api/jobs/{job_id}
GET  /api/jobs/{job_id}/lesson
GET  /media/{job_id}/{filename}
```

## 3. Target repository

```text
apps/
  api/
    focusly_api/
      main.py
      config.py
      db.py
      models.py
      schemas.py
      jobs.py
      pipeline.py
      openai_lesson.py
      kokoro_tts.py
      captions.py
      render.py
    tests/
  web/
    app/
      page.tsx
      jobs/[jobId]/page.tsx
      lessons/[jobId]/page.tsx
    components/
      generate-form.tsx
      job-progress.tsx
      lesson-player.tsx
      quiz-card.tsx
    lib/
      api.ts
    tests/
packages/
  video/
    src/
      Root.tsx
      LessonComposition.tsx
      scenes.tsx
data/
  jobs/
```

Do not add Turborepo until more than the web and video packages need shared orchestration.

## 4. Implementation phases

### Phase 1: Prove media generation from a fixture

**Skills:** `brainstorming`, `javascript-typescript`, `remotion-best-practices`, `test-driven-development`

**Files:**

- Create `packages/video/src/Root.tsx`
- Create `packages/video/src/LessonComposition.tsx`
- Create `packages/video/src/scenes.tsx`
- Create `packages/video/fixtures/binary-search.json`
- Create `packages/video/package.json`

**Work:**

1. Define a JSON fixture matching `LessonPackage`.
2. Build five trusted scene templates: title, bullets, comparison, steps, diagram.
3. Render scenes from data only; do not execute generated code.
4. Render a 20-second fixture MP4 through Remotion.
5. Add reduced-motion behavior and readable contrast.

**Verification:**

```bash
rtk pnpm --dir packages/video test
rtk pnpm --dir packages/video render:fixture
rtk proxy ffprobe data/jobs/fixture/lesson.mp4
```

**Exit:** A deterministic local fixture produces a playable MP4.

### Phase 2: Generate a lesson package with OpenAI

**Skills:** `openai-docs`, `llm-application-dev`, `python-development`, `test-driven-development`

**Files:**

- Create `apps/api/focusly_api/config.py`
- Create `apps/api/focusly_api/schemas.py`
- Create `apps/api/focusly_api/openai_lesson.py`
- Create `apps/api/tests/test_openai_lesson.py`
- Create `apps/api/pyproject.toml`

**Work:**

1. Add the official `openai` Python SDK.
2. Default `OPENAI_MODEL` to `gpt-5.5`, but read it from the environment.
3. Make one Responses API call using strict Structured Outputs and `LessonPackage`.
4. Put stable ADHD-learning instructions first and the user's topic last for prompt caching.
5. Reject invalid segment count, quiz options, duration, or unsupported visual type.
6. Mock the OpenAI call in tests; automated tests must not spend API credits.

**Verification:**

```bash
rtk pytest apps/api/tests/test_openai_lesson.py
```

**Exit:** A mocked OpenAI response validates into `LessonPackage`; one manually approved integration run creates a real package.

### Phase 3: Add local narration and captions

**Skills:** `python-development`, `test-driven-development`

**Files:**

- Create `apps/api/focusly_api/kokoro_tts.py`
- Create `apps/api/focusly_api/captions.py`
- Create `apps/api/tests/test_captions.py`

**Work:**

1. Install `kokoro`, `soundfile`, and the system `espeak-ng` package.
2. Generate one WAV file per segment with a fixed voice such as `af_heart`.
3. Read each WAV duration and concatenate them with FFmpeg.
4. Build WebVTT cues from segment boundaries and sentence proportions.
5. Do not add forced-alignment infrastructure. Segment-level captions are sufficient for the MVP.

**Verification:**

```bash
rtk pytest apps/api/tests/test_captions.py
rtk proxy ffprobe data/jobs/fixture/narration.wav
```

**Exit:** Fixture narration and valid WebVTT are produced without an external TTS service.

### Phase 4: Build the sequential job pipeline

**Skills:** `backend-development`, `python-development`, `database-design`, `test-driven-development`

**Files:**

- Create `apps/api/focusly_api/db.py`
- Create `apps/api/focusly_api/models.py`
- Create `apps/api/focusly_api/jobs.py`
- Create `apps/api/focusly_api/render.py`
- Create `apps/api/focusly_api/pipeline.py`
- Create `apps/api/tests/test_pipeline.py`

**Work:**

1. Add SQLite tables for `jobs` and generated artifact paths.
2. Implement the four stages: planning, narrating, rendering, succeeded.
3. Run the pipeline through one `BackgroundTasks` job.
4. Use a process-local lock to allow one render at a time.
5. Persist the safe failure message and keep detailed errors in server logs.
6. Pass `LessonPackage` JSON to Remotion and combine video, narration, and captions with FFmpeg.

```python
# ponytail: single-process lock is enough for the private MVP;
# replace with a durable queue before running multiple API instances.
```

**Verification:**

```bash
rtk pytest apps/api/tests/test_pipeline.py
```

**Exit:** A mocked topic-to-video job reaches `succeeded`, and failures reach `failed`.

### Phase 5: Expose the FastAPI endpoints

**Skills:** `backend-development`, `python-development`, `test-driven-development`

**Files:**

- Create `apps/api/focusly_api/main.py`
- Create `apps/api/tests/test_api.py`

**Work:**

1. Validate topic length from 3 to 300 characters.
2. Accept `audience_level` and `duration_target_seconds`.
3. Return `202` with a job ID.
4. Return job progress and safe errors.
5. Serve only files under the matching job directory; reject path traversal.
6. Add a development-only CORS origin from configuration.

**Verification:**

```bash
rtk pytest apps/api/tests/test_api.py
```

**Exit:** The complete API contract works with mocked generation.

### Phase 6: Build the learner flow

**Skills:** `frontend-design`, `javascript-typescript`, `test-driven-development`, `playwright`

**Files:**

- Create `apps/web/app/page.tsx`
- Create `apps/web/app/jobs/[jobId]/page.tsx`
- Create `apps/web/app/lessons/[jobId]/page.tsx`
- Create `apps/web/components/generate-form.tsx`
- Create `apps/web/components/job-progress.tsx`
- Create `apps/web/components/lesson-player.tsx`
- Create `apps/web/components/quiz-card.tsx`
- Create `apps/web/lib/api.ts`

**Work:**

1. Build one focused topic form.
2. Poll job state with `fetch` and `setInterval`; do not add React Query for three endpoints.
3. Use native `<video controls>` with a WebVTT `<track>`.
4. Show quiz cards when playback crosses each segment boundary.
5. Support keyboard controls, visible focus, captions, and reduced motion.

**Verification:**

```bash
rtk pnpm --dir apps/web test
rtk pnpm --dir apps/web test:e2e
```

**Exit:** A learner can submit a topic, see progress, play the result, enable captions, and answer a quiz.

### Phase 7: Run the real vertical slice

**Skills:** `webapp-testing`, `systematic-debugging`, `verification-before-completion`, `code-review`

**Files:**

- Create `apps/api/tests/test_smoke_real_media.py`
- Create `docs/mvp-runbook.md`
- Create `.env.example`

**Work:**

1. Generate one 60–90 second lesson about binary search.
2. Verify narration, scene timing, captions, and quiz behavior manually.
3. Record generation time, OpenAI token usage, render time, and failure stage.
4. Test an invalid topic, an OpenAI failure, a TTS failure, and a render failure.
5. Document local startup and cleanup commands.

**Verification:**

```bash
rtk pytest apps/api/tests
rtk pnpm --dir apps/web test
rtk pnpm --dir apps/web test:e2e
rtk pnpm --dir packages/video test
```

**Exit:** Five people can generate and watch a lesson without developer intervention, and at least three complete the video and quiz.

## 5. Build order and schedule

| Day | Outcome |
|---|---|
| 1–2 | Fixture renders to MP4. |
| 3 | OpenAI produces validated lesson JSON. |
| 4 | Kokoro produces narration and captions. |
| 5–6 | FastAPI job pipeline produces a complete lesson. |
| 7–8 | Web generation, progress, playback, and quiz flow. |
| 9 | End-to-end tests and failure handling. |
| 10 | Five-user MVP test and fixes. |

## 6. Promotion gates

Add deferred infrastructure only when the stated condition occurs:

| Add later | Trigger |
|---|---|
| Authentication | The MVP is exposed beyond invited testers. |
| PostgreSQL | Multiple users or a deployed persistent instance is required. |
| Redis/ARQ | Jobs must survive API restarts or run concurrently. |
| R2/S3 storage | Media must survive machine replacement or be shared across instances. |
| HLS/video.js | MP4 startup or seeking is measurably poor for target lesson length. |
| LangGraph | The pipeline needs branching retries or resume from a specific stage. |
| Manim | Remotion templates cannot explain tested math/graph topics adequately. |
| Word-level alignment | Segment-level captions produce measurable comprehension or accessibility problems. |
| Multiple specialized model calls | A single lesson-package call fails quality evaluation by artifact type. |

## 7. Source decisions

- OpenAI's current model guide identifies `gpt-5.5` and recommends Structured Outputs instead of embedding schemas in prompts: <https://developers.openai.com/api/docs/guides/latest-model.md>
- OpenAI Structured Outputs supports Python Pydantic schemas: <https://developers.openai.com/api/docs/guides/structured-outputs>
- Kokoro is an Apache-2.0, 82M-parameter open-weight TTS model with a Python package and local inference instructions: <https://github.com/hexgrad/kokoro>
- Kokoro model card and license: <https://huggingface.co/hexgrad/Kokoro-82M>

## 8. MVP completion definition

The MVP is done when:

- A user enters a topic and receives a 60–120 second lesson.
- The lesson contains three to five short segments, narration, captions, and at least one quiz.
- The browser plays the MP4 with keyboard-accessible controls and toggleable captions.
- Automated tests use mocked OpenAI and local fixture media.
- One documented real integration test succeeds.
- Five target learners can use the flow without assistance.

Anything beyond this list is post-MVP.
