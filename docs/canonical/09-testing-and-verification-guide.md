# Testing and Verification Guide

## Purpose
Define the MVP test pyramid, mocked integration tests, rendering smoke tests, E2E flows, and final verification checklist.

## Owner Skills
- Primary: test-driven-development
- Supporting: playwright, webapp-testing, systematic-debugging, code-review, verification-before-completion

## Expected Output
Future implementation work has an explicit verification path before completion is claimed.

## Test Pyramid
```text
Many: unit tests for schemas, services, reducers, prompts, parsers
Some: integration tests for API + DB, worker + mocked graph, player metadata
Few: Playwright E2E for happy path, failure path, playback path
Smoke: rendering pipeline produces short HLS and captions
```

## pytest Tests
- Pydantic request/response validation.
- Auth token creation, validation, expiry, and cookie flags.
- Lesson/job service authorization and ownership.
- Error response formatting.
- R2 object key generation.

## pytest-asyncio Tests
- Async SQLAlchemy repositories.
- FastAPI async test client endpoint behavior.
- ARQ worker job status transitions.
- Pipeline state JSONB save/load.

## respx Mocks
- Mock Claude API responses for structured outputs.
- Mock ElevenLabs audio and timestamp responses.
- Mock R2-compatible HTTP interactions if using HTTP client paths.
- Assert no tests call real external services by default.

## Vitest Tests
- API client methods and error normalization.
- React Query key factories.
- Zustand player preference store.
- Caption and quiz timestamp utilities.

## Playwright E2E Tests
Core flows:
- Register/login and dashboard loads.
- Create lesson from prompt and navigate to job page.
- Mock job polling transitions from `queued` to `running` to `succeeded`.
- Playback page loads signed metadata, HLS player shell, captions toggle, and quiz checkpoint marker.
- Failed job displays safe error and retry button when retryable.

Use Page Object Model for dashboard, generate, job, and player pages.

## Agent Tests with Mocked Claude
- R02 planner returns valid `LessonContext`.
- R03 script and R05 scene manifest share segment IDs.
- R04 quiz timestamps fit segment timeline.
- R06 code validation failures route to retry.
- R09 blocks critical educational or sync failures.
- Graph-level test verifies Path B topology and progress updates.

## ElevenLabs Mock Tests
- Successful TTS stores audio metadata.
- Transient errors retry within limits.
- Permanent errors create safe failure messages.
- Word timestamp gaps produce R08 alignment warnings.

## R2 Mock Tests
- Object keys include user, lesson, and job IDs.
- Upload metadata persists to `lesson_artifacts`.
- Playback endpoint refuses another user's lesson.
- Signed URLs have bounded TTL.

## Rendering Smoke Tests
- Render a 5-10 second synthetic lesson using local Remotion/Manim fixtures.
- Run FFmpeg HLS segmentation.
- Verify `master.m3u8`, at least one segment, WebVTT, SRT, and manifest exist.
- Do not require real Claude or ElevenLabs.

## Full Pipeline Acceptance Tests
Use mocked Claude and ElevenLabs plus local render smoke mode:
- Submit a test topic.
- Execute ARQ job synchronously in test mode.
- Verify job reaches `succeeded`.
- Verify final playback metadata includes HLS, captions, quiz checkpoints, duration.
- Verify all artifacts are owned by the authenticated user.

## Verification Checklist Before Completion
- All changed backend tests pass.
- All changed frontend tests pass.
- E2E happy path passes or has a documented blocker.
- Rendering smoke test passes for media-related changes.
- No real external runtime service is called in automated tests unless explicitly marked integration.
- Security-sensitive changes receive code review against `10-security-and-reliability-guide.md`.
- Documentation updates are included when contracts change.

## Acceptance Criteria
- Testing covers API, DB, worker, agent graph, media mocks, frontend state, and E2E flows.
- Mocked external services are mandatory for routine tests.
- Completion cannot be claimed without listing verification commands and results.

## Related Docs
- [Product Requirements](./03-product-requirements.md)
- [LangGraph Agent Pipeline](./05-langgraph-agent-pipeline.md)
- [Future Agent Build Rules](./12-future-agent-build-rules.md)
