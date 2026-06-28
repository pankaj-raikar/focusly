# Product Requirements

## Purpose
Define MVP user stories, acceptance criteria, non-functional requirements, and traceability for Focusly.

## Owner Skills
- Primary: project-planner
- Supporting: frontend-design, design-engineer, llm-application-dev, backend-development, playwright, verification-before-completion

## Expected Output
Requirement IDs that implementation agents can trace to APIs, data models, pipeline nodes, UI pages, tests, and rollout phases.

## MVP User Stories and Acceptance Criteria

### REQ-001: Account Session
User Story: As a learner, I want to sign in securely so that my generated lessons remain private.

Acceptance Criteria:
- The system SHALL authenticate using JWT RS256 in httpOnly cookies.
- The system SHALL never store access tokens in localStorage.
- The dashboard SHALL show only lessons owned by the authenticated user.

### REQ-002: Generate Lesson Prompt
User Story: As a learner, I want to enter a topic prompt so that Focusly can generate an animated lesson.

Acceptance Criteria:
- The generate page SHALL accept a topic from 3 to 300 characters.
- The request SHALL include optional `audience_level`, `tone`, and `duration_target_seconds` within allowed values.
- Invalid requests SHALL return contract-compliant validation errors.

### REQ-003: ADHD-Optimized Lesson Structure
User Story: As an ADHD learner, I want short, segmented lessons so that I can stay engaged.

Acceptance Criteria:
- The planner SHALL produce 3 to 7 segments for MVP lessons.
- Each segment SHOULD target 20 to 60 seconds.
- The script SHALL include a hook, pacing markers, recap beats, and a closing summary.
- Visual density SHALL be limited to one primary idea per scene.

### REQ-004: Quiz Checkpoints
User Story: As a learner, I want quick quiz checkpoints so that I can confirm understanding.

Acceptance Criteria:
- Each lesson SHALL include at least 2 quiz checkpoints for lessons longer than 90 seconds.
- Each quiz SHALL include a question, 2 to 4 options, a correct answer, explanation, and timestamp target.
- Quiz checkpoints SHALL appear in frontend playback metadata.

### REQ-005: Captions
User Story: As a learner, I want toggleable captions so that I can read along or reduce audio dependence.

Acceptance Criteria:
- The pipeline SHALL generate WebVTT and SRT captions.
- The player SHALL expose captions as toggleable tracks.
- Burned-in captions MAY be generated only for export or fallback, not as the primary MVP caption experience.

### REQ-006: Job Polling and Progress
User Story: As a learner, I want to see progress while my lesson is generated.

Acceptance Criteria:
- The API SHALL expose job status and progress percentage.
- The frontend SHALL poll job status with React Query until `succeeded`, `failed`, or `cancelled`.
- Progress SHALL include current pipeline stage labels mapped to R01-R10.

### REQ-007: HLS Playback
User Story: As a learner, I want reliable video playback so that generated lessons stream smoothly.

Acceptance Criteria:
- The final render SHALL provide an HLS master or media playlist.
- The player SHALL use video.js to load HLS.
- Playback metadata SHALL include caption tracks and quiz checkpoint timestamps.

### REQ-008: Dashboard
User Story: As a learner, I want a dashboard so that I can view current and past lessons.

Acceptance Criteria:
- The dashboard SHALL list lessons by status, title, created time, and duration when available.
- Failed jobs SHALL display a safe error summary and retry option if retryable.
- Lesson links SHALL enforce user ownership.

### REQ-009: MVP External Service Limit
User Story: As the product owner, I want a bounded integration surface so that MVP reliability is manageable.

Acceptance Criteria:
- MVP runtime integrations SHALL be limited to Claude API, ElevenLabs, and Cloudflare R2.
- The product SHALL NOT use Unsplash, Pixabay, LottieFiles, Sentry, music APIs, or extra runtime APIs in MVP.

### REQ-010: Path B Pipeline
User Story: As the build team, I want a fixed agent graph so that implementation remains testable.

Acceptance Criteria:
- MVP SHALL implement only the 10-agent Path B graph.
- Path A SHALL appear only in post-MVP documentation.
- R01-R10 outputs SHALL conform to `05-langgraph-agent-pipeline.md`.

## Non-Functional Requirements
| ID | Requirement | Target |
|---|---|---|
| NFR-001 | API validation | Invalid requests return structured `400` or `422` errors. |
| NFR-002 | Auth isolation | Users cannot access another user's lessons, jobs, or signed playback URLs. |
| NFR-003 | Job durability | Job state survives process restart through PostgreSQL and LangGraph checkpointing. |
| NFR-004 | Render timeout | MVP render job has per-stage and total timeouts with failure status. |
| NFR-005 | Accessibility | Core pages support keyboard navigation, visible focus, captions, and reduced-motion mode. |
| NFR-006 | Testability | Claude, ElevenLabs, and R2 are mockable in automated tests. |

## Traceability Matrix
| Requirement | Implementation Docs | Test Docs |
|---|---|---|
| REQ-001 | `04`, `06`, `10` | `09` auth and security tests |
| REQ-002 | `04`, `06`, `07` | `09` API and frontend tests |
| REQ-003 | `05`, `07`, `08` | `09` agent and visual smoke tests |
| REQ-004 | `04`, `05`, `07` | `09` agent and E2E tests |
| REQ-005 | `04`, `07`, `08` | `09` player and caption tests |
| REQ-006 | `04`, `06`, `07` | `09` polling E2E tests |
| REQ-007 | `04`, `07`, `08` | `09` playback tests |
| REQ-008 | `04`, `06`, `07` | `09` dashboard tests |
| REQ-009 | `01`, `02`, `08`, `12` | `09` integration guard tests |
| REQ-010 | `05`, `11`, `12`, `13` | `09` graph contract tests |

## Acceptance Criteria
- Every MVP requirement has a stable ID and testable criteria.
- ADHD pacing, captions, quiz checkpoints, HLS playback, auth, job polling, and dashboard are explicit requirements.
- Each requirement maps to implementation and testing documents.

## Related Docs
- [API and Data Contracts](./04-api-and-data-contracts.md)
- [LangGraph Agent Pipeline](./05-langgraph-agent-pipeline.md)
- [8-Week Implementation Plan](./11-8-week-implementation-plan.md)
