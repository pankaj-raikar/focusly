# 8-Week Implementation Plan

## Purpose
Provide a phased MVP build plan with required skills, deliverables, tests, exit criteria, phase gates, and requirement traceability.

## Owner Skills
- Primary: project-planner
- Supporting: test-driven-development, backend-development, frontend-design, llm-application-dev, database-design, playwright, code-review, verification-before-completion

## Expected Output
Future agents can execute Focusly MVP in order with clear weekly outcomes and no major architecture decisions left open.

## Week-by-Week Plan
| Week | Skills to Use | Deliverables | Tests | Exit Criteria | Requirements |
|---|---|---|---|---|---|
| 1 | project-planner, database-design, backend-development | Monorepo scaffold, FastAPI app, DB models, Alembic baseline, config | pytest schema and DB smoke tests | API starts, DB migrates, docs linked | REQ-001, REQ-009 |
| 2 | security-review, backend-development, javascript-typescript | Auth endpoints, cookies, CSRF, app shell, login/register | Auth unit/API tests, basic Playwright auth | User can register/login/logout securely | REQ-001 |
| 3 | backend-development, database-design, frontend-design | Lesson create/list/job polling APIs, dashboard, generate page | API contract tests, Vitest, Playwright generate mock | Create request returns queued job and dashboard lists it | REQ-002, REQ-006, REQ-008 |
| 4 | llm-application-dev, python-development | R01-R05 graph, LessonContext, script, quiz, scene manifest | Mocked Claude agent tests | Planner/script/quiz/scene outputs validate | REQ-003, REQ-004, REQ-010 |
| 5 | llm-application-dev, python-development | R06-R08 graph, code specs, audio integration wrapper, captions | Mocked ElevenLabs, code validation, caption tests | Captions and timing artifacts produced | REQ-005, REQ-010 |
| 6 | llm-application-dev, systematic-debugging | R09-R10, Remotion/Manim smoke render, FFmpeg HLS, R2 upload | Rendering smoke, R2 mock, full mocked pipeline | Pipeline produces playback metadata | REQ-005, REQ-007, REQ-010 |
| 7 | javascript-typescript, frontend-design, playwright | Player page, video.js HLS, captions toggle, quiz checkpoints | Playwright playback flow, accessibility tests | User can play successful lesson with captions and quizzes | REQ-004, REQ-005, REQ-007 |
| 8 | code-review, verification-before-completion, systematic-debugging | Hardening, rate limits, retries, runbooks, final docs updates | Full suite, E2E, security review checklist | MVP passes final verification gate | All MVP requirements |

## Phase Gates
| Gate | Required Evidence |
|---|---|
| Foundation Gate | Monorepo, DB migration, API health, config validation. |
| Auth Gate | RS256 cookie auth, CSRF, ownership tests. |
| Job Gate | Lesson creation, queueing, polling, dashboard visibility. |
| Agent Gate | R01-R08 contract tests with mocked Claude/ElevenLabs. |
| Media Gate | HLS, captions, R2 artifact metadata from smoke render. |
| Product Gate | Playwright generate-to-playback happy path. |
| Release Gate | Security checklist, runbook, docs updated, final verification results. |

## Task Breakdown Principles
- Write tests before or alongside each subsystem.
- Keep API contracts stable once frontend integration begins.
- Do not introduce post-MVP services to unblock MVP gaps.
- Prefer mocked external providers until manual integration testing.

## Requirement Traceability
- Weeks 1-2: REQ-001, NFR-001, NFR-002.
- Week 3: REQ-002, REQ-006, REQ-008.
- Weeks 4-5: REQ-003, REQ-004, REQ-005, REQ-010.
- Week 6: REQ-007, REQ-009, NFR-003, NFR-004.
- Week 7: REQ-004, REQ-005, REQ-007, NFR-005.
- Week 8: all requirements and NFRs.

## Acceptance Criteria
- Every week identifies skills, deliverables, tests, exit criteria, and requirement links.
- Phase gates prevent frontend polish from hiding missing backend/pipeline contracts.
- The plan keeps Path B and canonical external services intact.

## Related Docs
- [Product Requirements](./03-product-requirements.md)
- [Testing and Verification Guide](./09-testing-and-verification-guide.md)
- [Future Agent Build Rules](./12-future-agent-build-rules.md)
