# Focusly — High-Level System Architecture

## 1. System Overview

Focusly is a full-stack application that converts topic prompts into ADHD-optimized animated lesson videos through a 33-agent AI pipeline orchestrated by LangGraph, rendered by Remotion + Manim, narrated by ElevenLabs TTS, and delivered via HLS streaming.

```
┌──────────────────────────────────────────────────────────────────────────┐
│                              CLIENT LAYER                                │
│                   Next.js 15 (App Router + React 19)                     │
│              TypeScript · TailwindCSS · shadcn/ui · Zustand              │
│         video.js (HLS) · React Query · Zod validation                   │
└────────────────────────────┬────────────────���────────────────────────────┘
                             │ HTTPS (TLS 1.3)
                             ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                           API GATEWAY LAYER                              │
│                    FastAPI (Python 3.12 · Uvicorn)                       │
│            Auth middleware · Rate limiting · Request ID · CORS            │
└──────┬──────────────────┬──────────────────┬─────────────────────────────┘
       │                  │                  │
       ▼                  ▼                  ▼
┌─────────────┐  ┌──────────────┐  ┌──────────────────────────────────────┐
│  PostgreSQL │  │    Redis 7   │  │        AGENT ORCHESTRATION           │
│     16      │  │  (Queue +    │  │     LangGraph StateGraph             │
│ (primary DB)│  │   Cache +    │  │   ┌────────────────────────────┐     │
│             │  │   Rate limit)│  │   │  33 Agent Nodes (A01-A33)  │     │
└─────────────┘  └──────────────┘  │   │  Each wraps LangChain:     │     │
       │                           │   │  ChatAnthropic + Parser    │     │
       ▼                           │   │  + Tools + Memory          │     │
┌─────────────┐                    │   └────────────────────────────┘     │
│  Alembic    │                    └────────────┬─────────────────────────┘
│  Migrations │                                 │
└─────────────┘                    ┌────────────┼──────────────┐
                                   │            │              │
                                   ▼            ▼              ▼
                          ┌──────────────┐ ┌─────────┐ ┌──────────────┐
                          │ Remotion 4   │ │  Manim  │ │ ElevenLabs   │
                          │ (React→MP4)  │ │ (Py→MP4)│ │ TTS API      │
                          │ Node.js sub  │ │ Py sub  │ │              │
                          └──────┬───────┘ └────┬────┘ └──────┬───────┘
                                 │              │             │
                                 └──────────────┼─────────────┘
                                                ▼
                                    ┌────────────────────┐
                                    │    FFmpeg (stitch  │
                                    │    + mux + HLS)    │
                                    └─────────┬──────────┘
                                              ▼
                                    ┌────────────────────┐
                                    │  Cloudflare R2     │
                                    │  (S3-compatible    │
                                    │   object storage)  │
                                    │  + CDN (auto)      │
                                    └─────────┬──────────┘
                                              ▼
                                    ┌────────────────────┐
                                    │  HLS Stream →      │
                                    │  video.js player   │
                                    └────────────────────┘
```

---

## 2. Component Interaction Diagram

```
                    ┌─────────────────────────────────────────┐
                    │              NEXT.JS FRONTEND            │
                    │                                         │
                    │  ┌─────────┐  ┌──────────┐  ┌────────┐ │
                    │  │ Generate │  │ Dashboard│  │ Player │ │
                    │  │  Form   │  │  (cards) │  │ (HLS)  │ │
                    │  └────┬────┘  └────┬─────┘  └───┬────┘ │
                    │       │            │             │      │
                    │  ┌────▼────────────▼─────────────▼────┐ │
                    │  │       React Query + Zustand        │ │
                    │  │    (server state + client state)    │ │
                    │  └────────────────┬───────────────────┘ │
                    └───────────────────┼─────────────────────┘
                                        │ fetch (httpOnly cookie)
                    ┌───────────────────┼─────────────────────┐
                    │                   ▼                     │
                    │         FASTAPI BACKEND API             │
                    │                                         │
                    │  ┌──────────┐  ┌──────────────────────┐ │
                    │  │   Auth   │  │   Lesson Controller  │ │
                    │  │ (JWT RS  │  │  /generate → enqueue │ │
                    │  │  256)    │  │  /poll → read state  │ │
                    │  └──────────┘  └──────────┬───────────┘ │
                    │                           │              │
                    │  ┌────────────────────────▼───────────┐ │
                    │  │         ARQ Worker                  │ │
                    │  │  ┌──────────────────────────────┐  │ │
                    │  │  │  LangGraph Pipeline          │  │ │
                    │  │  │  ┌────┐ ┌────┐    ┌────┐    │  │ │
                    │  │  │  │A01│→│A02│→···→│A33│    │  │ │
                    │  │  │  └────┘ └────┘    └────┘    │  │ │
                    │  │  │  Each node:                 │  │ │
                    │  │  │  LangChain chain             │  │ │
                    │  │  │  (ChatAnthropic + tools)     │  │ │
                    │  │  └──────────────────────────────┘  │ │
                    │  └────────────────────────────────────┘ │
                    └─────────────────────────────────────────┘
```

---

## 3. Data Flow — Lesson Generation

```
User clicks "Generate"
         │
         ▼
    POST /lessons/generate ──► Create LessonJob (status=queued) in PostgreSQL
         │                          │
         ▼                          ▼
    Return job_id (202)        Enqueue ARQ task
                                      │
                                      ▼
                              ARQ Worker picks up task
                                      │
                                      ▼
                              Build LangGraph pipeline
                              Load/create checkpoint
                                      │
                                      ▼
                              ┌─── Layer 1: A01 Initialize ───┐
                              │                                │
                              ▼                                │
                         Layer 2: Knowledge (A02-A05)          │
                         LangChain chains → Pydantic output    │
                         Save to LessonContext JSONB           │
                              │                                │
                              ▼                                │
                         Layer 3: Script (A06-A09)             │
                         Write narration + quiz questions      │
                              │                                │
                              ▼                                │
                    ┌─── Layer 4: Visual (A10-A14) ───┐       │
                    │  Scene manifest + design tokens  │       │
                    │  + asset downloads (Unsplash)    │       │
                    └────────────┬────────────────────┘       │
                                 │                             │
                    ┌────────────┼────────────────────┐       │
                    ▼            ▼                    ▼       │
              Layer 5        Layer 6                 │       │
              Code Gen       Audio                   │       │
              (A15-A20)      (A21-A24)               │       │
              Remotion TSX   ElevenLabs TTS          │       │
              Manim Python   Music + Sound           │       │
              D3.js          FFmpeg mix              │       │
                    │            │                    │       │
                    └────────────┼────────────────────┘       │
                                 ▼                             │
                         Layer 7: QA (A25-A28)                │
                         Compile check, visual QA,            │
                         sync QA, educational QA              │
                         Conditional retry (max 3x)           │
                                 │                             │
                                 ▼                             │
                         Layer 8: Render (A29-A32)            │
                         Remotion render (Node.js sub)        │
                         Manim render (Python sub)            │
                         FFmpeg stitch + HLS                  │
                         Upload to R2                         │
                         Evaluate outcome                     │
                         Store memory                         │
                                 │                             │
                                 ▼                             │
                         Mark job completed                    │
                         Save Lesson record                    │
                                      │
                                      ▼
                              Frontend polls GET /jobs/:id
                              Progress updates from agent_statuses
                              On completion: redirect to /lessons/:id
```

---

## 4. Layered Architecture

| Layer | Technology | Responsibility |
|-------|-----------|---------------|
| Presentation | Next.js 15 + React | UI rendering, state management, video playback |
| API | FastAPI | Auth, request validation, routing, rate limiting |
| Queue | ARQ + Redis | Async job dispatch, retry, stuck job detection |
| Orchestration | LangGraph | Agent DAG, parallel execution, conditional routing, checkpointing |
| Intelligence | LangChain + Claude API | LLM chains, structured output, tool calling, memory |
| Rendering | Remotion + Manim + FFmpeg | Scene composition, animation, encoding, HLS segmentation |
| Storage | PostgreSQL + Cloudflare R2 | Persistent data + video/asset object storage |
| Observability | Sentry + structlog | Error tracking, structured logging, metrics |

---

## 5. Key Architectural Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Agent orchestration | LangGraph StateGraph | Native support for DAG execution, parallel branches, conditional edges, checkpointing |
| LLM pipeline | LangChain | Structured output parsing, tool calling, memory, caching, callback-based cost tracking |
| Video engine | Remotion (primary) + Manim (math) | Remotion handles general scenes with React; Manim provides superior math animation |
| Queue | ARQ (not Celery) | Async-native Python, Redis-backed, fewer moving parts for solo engineer |
| Auth tokens | httpOnly cookies (not localStorage) | XSS protection; no token exposure to JavaScript |
| Job status | Polling (not WebSockets) | Simpler to build, deploy, debug; 5s polling is acceptable UX |
| Database | Single PostgreSQL | Avoid operational complexity; JSONB for flexible agent state |
| Deployment | Railway (not AWS) | Managed Postgres + Redis, minimal ops surface for solo engineer |

---

## 6. Tech Stack Justification

### Why LangGraph over custom DAG engine?

LangGraph provides:
- **StateGraph** with typed state — each node reads/writes to a shared TypedDict
- **Parallel fan-out** — A04+A05 run concurrently after A03
- **Conditional edges** — QA retry loops route back to the failing agent
- **Checkpointing** — PostgreSQL-backed crash recovery
- **Streaming** — real-time agent status updates

Building this from scratch would take 2-3 weeks for a solo engineer. LangGraph does it out of the box.

### Why LangChain over raw Claude API calls?

LangChain provides:
- **PydanticOutputParser** — extract structured JSON from Claude's text response
- **Tool calling** — AssetHunter uses Unsplash, TTS uses ElevenLabs, all through a unified tool interface
- **Memory modules** — ConversationBufferMemory for multi-turn refinement, EntityMemory for cross-agent context
- **Callbacks** — CostTrackingCallback logs token usage per chain run
- **Caching** — Redis-backed LLM cache reduces costs for repeated topics

### Why Manim alongside Remotion?

Remotion excels at:
- Text animations, image overlays, bullet reveals, quiz scenes
- React-based component model (familiar for frontend developers)
- Programmatic control over every frame

Manim excels at:
- Mathematical equation rendering (LaTeX-quality)
- Algorithm step-throughs (binary search pointers, sorting animations)
- Data structure visualization (trees, graphs, linked lists)
- Geometric proofs and transformations

Using both gives the best visual quality for each content type.

---

## 7. Security Boundaries

```
Internet ──► Cloudflare (TLS, DDoS, WAF)
                │
                ▼
         Railway (API + Worker + Web)
         ┌──────────────────────┐
         │ API: Auth middleware  │──► Reject unauthenticated
         │ API: Rate limiting   │──► 10 gen/day/user
         │ API: Input sanitise  │──► Strip harmful content
         │ Worker: Sandboxed    │──► Manim in subprocess
         └──────────────────────┘
                │
                ▼
         PostgreSQL (encrypted at rest)
         Redis (no sensitive data, only queue + cache)
         R2 (signed URLs, 1h expiry, no public video URLs)
```

---

## 8. Scalability Considerations

| Component | MVP (50 users) | Scale Target (500 users) |
|-----------|----------------|--------------------------|
| API | 1 instance, 4 workers | 2+ instances behind Railway proxy |
| Worker | 1 instance, 3 concurrent renders | 3+ instances, dedicated render workers |
| PostgreSQL | Single instance, 20 connections | Read replica for heavy reads |
| Redis | Single instance | Redis Cluster (if queue depth grows) |
| R2/CDN | Auto-scales | No change needed |
| Video delivery | R2 CDN | No change needed (CDN handles it) |
