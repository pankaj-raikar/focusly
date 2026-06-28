# Canonical Stack and Skill Routing

## Purpose
Define the only approved MVP technology stack and the skill-routing rules future agents must follow before changing a subsystem.

## Owner Skills
- Primary: project-planner
- Supporting: backend-development, python-development, database-design, javascript-typescript, frontend-design, design-engineer, llm-application-dev, playwright, webapp-testing, test-driven-development, systematic-debugging, code-review, verification-before-completion, out-of-box-prompt

## Expected Output
A coding agent can identify the correct toolchain, specialist workflow, output artifact, and acceptance criteria for each subsystem.

## Canonical Stack
| Layer | Canonical Tooling | MVP Use |
|---|---|---|
| Monorepo | pnpm, Turborepo, uv | Shared repo orchestration for web and Python services. |
| Frontend | Next.js 15, React, TypeScript | App Router dashboard, generate flow, job page, player page. |
| UI | TailwindCSS, shadcn/ui | Accessible, consistent ADHD-friendly UI components. |
| Client state | Zustand | Local UI state only: draft prompt, player preferences, lightweight wizard state. |
| Server state | React Query | Auth status, job polling, lesson lists, signed playback URLs. |
| Video player | video.js + HLS | Adaptive playback with WebVTT/SRT caption tracks. |
| Backend | Python 3.12, FastAPI | Auth, API contracts, job control, signed URL generation. |
| API models | Pydantic | Request, response, agent artifact, and error schemas. |
| Database | PostgreSQL 16 | Users, lessons, jobs, artifacts, JSONB pipeline state. |
| ORM / migrations | SQLAlchemy 2 async, Alembic | Async persistence and versioned schema changes. |
| Queue | Redis 7 + ARQ | Long-running generation and render jobs. |
| Agent orchestration | LangGraph | Path B graph execution, checkpointing, retries. |
| LLM chains | LangChain | Claude calls, prompts, parsers, structured output validation. |
| LLM provider | Claude API | Planning, writing, code generation, QA. |
| Rendering | Remotion, Manim, FFmpeg | TSX scenes, math/diagram animations, stitching, HLS. |
| Audio | ElevenLabs | TTS narration and timing metadata. |
| Storage | Cloudflare R2 | Private media, manifests, captions, render artifacts. |
| Auth | JWT RS256 in httpOnly cookies | Secure browser sessions without localStorage tokens. |
| Testing | pytest, pytest-asyncio, respx, Vitest, Playwright | Unit, async, mocked external services, frontend, E2E. |

## Skill Routing Matrix
| Subsystem | Canonical Tools / Frameworks | Primary Skill | Supporting Skills | Output Artifact | Acceptance Criteria |
|---|---|---|---|---|---|
| Product planning | Markdown, requirement IDs | project-planner | out-of-box-prompt | PRD, traceability matrix | Requirements are testable and linked to tasks. |
| Backend API | FastAPI, Pydantic | backend-development | python-development, security-review | Routers, schemas, service contracts | Endpoints match `04-api-and-data-contracts.md`. |
| Python services | Python 3.12, async IO | python-development | test-driven-development | Service modules and workers | Async boundaries are explicit; no blocking API calls in request handlers. |
| Database | PostgreSQL 16, SQLAlchemy 2 async, Alembic | database-design | database-migrations | Entity models, migrations | Migrations are versioned, reversible, and safe for existing data. |
| Agent pipeline | LangGraph, LangChain, Claude API | llm-application-dev | out-of-box-prompt, systematic-debugging | Graph nodes, state schemas, prompts | Path B contracts pass mocked-Claude tests. |
| Frontend app | Next.js 15, React, TypeScript | javascript-typescript | frontend-design, design-engineer | App Router pages, components | Pages are responsive, accessible, and use canonical state boundaries. |
| UI/UX | TailwindCSS, shadcn/ui | frontend-design | design-engineer | ADHD-friendly layouts and tokens | Short-focus layout, reduced distraction, captions and quizzes are prominent. |
| Player | video.js, HLS, WebVTT/SRT | javascript-typescript | webapp-testing, playwright | Player component | HLS loads, captions toggle, quiz markers are visible. |
| Rendering | Remotion, Manim, FFmpeg | llm-application-dev | python-development, systematic-debugging | Scene render contracts and command wrappers | Render smoke tests produce HLS output and captions. |
| Audio | ElevenLabs | backend-development | python-development | TTS service wrapper | Mock tests verify retries, timestamps, and storage. |
| Storage | Cloudflare R2 | backend-development | security-review | Object key policy and signed URLs | Private objects never expose raw bucket access. |
| Auth/security | JWT RS256 cookies | security-review | backend-development | Auth middleware, cookie policy | Tokens are httpOnly; CSRF and CORS rules are enforced. |
| Testing | pytest, Vitest, Playwright | test-driven-development | playwright, webapp-testing | Test suites and fixtures | Tests cover contracts, mocked services, E2E happy path. |
| Debugging | Logs, traces, job events | systematic-debugging | code-review | RCA notes, regression tests | Bugs are reproduced, isolated, fixed, and verified. |
| Review | Markdown docs, implementation diffs | code-review | verification-before-completion | Findings and signoff | Review checks contracts, security, regressions, tests. |

## Mandatory Future-Agent Rule
Before changing a subsystem, future agents must invoke the matching primary skill from the matrix. If the change crosses subsystems, invoke the process skill first, then each relevant implementation skill.

## Reasoning
- Skill routing prevents agents from inventing a second architecture.
- Canonical tooling keeps contracts stable across backend, frontend, worker, and rendering work.
- Explicit output artifacts let reviewers verify work against docs instead of subjective intent.

## Acceptance Criteria
- No MVP subsystem uses a non-canonical runtime dependency.
- Each subsystem has a primary skill, supporting skill, output artifact, and acceptance criteria.
- Future agents are explicitly instructed to invoke the correct skill before implementation.

## Related Docs
- [System Architecture](./02-system-architecture.md)
- [Future Agent Build Rules](./12-future-agent-build-rules.md)
