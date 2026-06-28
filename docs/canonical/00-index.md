# Focusly Canonical Documentation Index

## Purpose
This package is the canonical build blueprint for Focusly, an AI-driven animated learning platform for ADHD learners. It constrains future implementation to the approved stack and the Path B 10-agent LangGraph MVP.

## Owner Skills
- Primary: project-planner
- Supporting: llm-application-dev, backend-development, frontend-design, design-engineer, test-driven-development, code-review, verification-before-completion

## Expected Output
Future coding agents can build Focusly phase by phase without choosing new architecture, external services, or MVP agent topology.

## Canonical Decisions
| Decision | Canonical Choice | Reasoning |
|---|---|---|
| MVP agent path | Path B, 10-agent LangGraph graph | Small enough to verify, expressive enough for planning, script, quiz, media, QA, and render responsibilities. |
| Future agent path | Path A, 33-agent pipeline | Allowed only after MVP metrics prove bottlenecks that justify splitting responsibilities. |
| Runtime external services | Claude API, ElevenLabs, Cloudflare R2 only | Keeps MVP cost, privacy, failure modes, and integration testing bounded. |
| Orchestration | LangGraph | Required for deterministic node routing, checkpointing, retries, and progress reporting. |
| LLM chains | LangChain | Standardizes prompts, parsers, structured outputs, and provider calls. |
| Async jobs | ARQ + Redis | Lightweight Python-native queue for long media generation jobs. |
| Pipeline persistence | PostgreSQL JSONB | Durable, queryable state snapshots without over-modeling every agent artifact. |
| Auth | JWT RS256 in httpOnly cookies | Stateless auth with asymmetric key rotation and reduced XSS token exposure. |
| Playback | video.js + HLS + WebVTT/SRT tracks | Broad browser support, adaptive playback, and toggleable captions. |

## Reading Order
1. [Canonical Stack and Skill Routing](./01-canonical-stack-and-skill-routing.md)
2. [System Architecture](./02-system-architecture.md)
3. [Product Requirements](./03-product-requirements.md)
4. [API and Data Contracts](./04-api-and-data-contracts.md)
5. [LangGraph Agent Pipeline](./05-langgraph-agent-pipeline.md)
6. [Backend Implementation Guide](./06-backend-implementation-guide.md)
7. [Frontend Implementation Guide](./07-frontend-implementation-guide.md)
8. [Rendering, Audio, and Storage Guide](./08-rendering-audio-storage-guide.md)
9. [Testing and Verification Guide](./09-testing-and-verification-guide.md)
10. [Security and Reliability Guide](./10-security-and-reliability-guide.md)
11. [8-Week Implementation Plan](./11-8-week-implementation-plan.md)
12. [Future Agent Build Rules](./12-future-agent-build-rules.md)
13. [Post-MVP Evolution](./13-post-mvp-evolution.md)

## File Map
| File | Role |
|---|---|
| `00-index.md` | Entry point, canonical decisions, package scope. |
| `01-canonical-stack-and-skill-routing.md` | Approved tools and skill ownership. |
| `02-system-architecture.md` | Component boundaries, data flow, deployment shape. |
| `03-product-requirements.md` | MVP user stories, requirement IDs, traceability. |
| `04-api-and-data-contracts.md` | HTTP contracts, database entities, JSONB state contracts. |
| `05-langgraph-agent-pipeline.md` | Path B graph, node contracts, checkpointing, retries. |
| `06-backend-implementation-guide.md` | FastAPI, auth, workers, SQLAlchemy, testing guidance. |
| `07-frontend-implementation-guide.md` | Next.js app surfaces, state boundaries, ADHD UX, player. |
| `08-rendering-audio-storage-guide.md` | Remotion, Manim, FFmpeg, ElevenLabs, R2, captions. |
| `09-testing-and-verification-guide.md` | Test pyramid, mocks, E2E, acceptance tests. |
| `10-security-and-reliability-guide.md` | Auth, CSRF, isolation, sandboxing, runbooks. |
| `11-8-week-implementation-plan.md` | Phase plan, deliverables, exit criteria. |
| `12-future-agent-build-rules.md` | Mandatory rules for future coding agents. |
| `13-post-mvp-evolution.md` | Controlled evolution beyond MVP. |

## In Scope
- Topic-to-animated-lesson generation.
- ADHD-friendly pacing, short segments, quiz checkpoints, captions, and summaries.
- Authenticated dashboard, generation form, job polling, and video player.
- Path B LangGraph pipeline using Claude, ElevenLabs, Remotion, Manim, FFmpeg, R2.
- Test guidance for backend, frontend, agents, rendering, and pipeline acceptance.

## Out of Scope
- Unsplash, Pixabay, LottieFiles, Sentry, music APIs, or any extra MVP runtime API.
- Path A 33-agent implementation in MVP.
- Native mobile apps, educator portals, institution billing, PDF/PPTX upload, and observability SaaS.
- Burned-in captions as the primary player experience.

## Build Path Summary
Focusly starts as a monorepo with a Next.js frontend, FastAPI backend, PostgreSQL, Redis/ARQ worker, and a Path B LangGraph pipeline. Users submit a topic, the backend creates a job, ARQ executes the graph, agents persist artifacts and progress in PostgreSQL JSONB, media is rendered locally by worker processes, outputs are uploaded to private R2 keys, and the frontend polls job status before playing signed HLS with toggleable captions.

## Acceptance Criteria
- Every MVP subsystem maps to a canonical stack choice.
- Every build decision links to a detailed doc in this package.
- Path B is the only MVP pipeline.
- MVP external runtime services are limited to Claude API, ElevenLabs, and Cloudflare R2.
- Future agents can determine the next document to read without asking for architecture clarification.
