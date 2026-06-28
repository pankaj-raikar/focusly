# Graph Report - .  (2026-06-28)

## Corpus Check
- 199 files · ~290,080 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 378 nodes · 618 edges · 32 communities (27 shown, 5 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 33 edges (avg confidence: 0.72)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Backend Database|Backend Database]]
- [[_COMMUNITY_Config Lesson Generation|Config Lesson Generation]]
- [[_COMMUNITY_Web UI Components|Web UI Components]]
- [[_COMMUNITY_System Architecture|System Architecture]]
- [[_COMMUNITY_Video Lesson Model|Video Lesson Model]]
- [[_COMMUNITY_Web Package Dependencies|Web Package Dependencies]]
- [[_COMMUNITY_API Schemas|API Schemas]]
- [[_COMMUNITY_Remotion Package|Remotion Package]]
- [[_COMMUNITY_Audio Captions Pipeline|Audio Captions Pipeline]]
- [[_COMMUNITY_Web TypeScript Config|Web TypeScript Config]]
- [[_COMMUNITY_Rendering Queue Infrastructure|Rendering Queue Infrastructure]]
- [[_COMMUNITY_Workspace Scripts|Workspace Scripts]]
- [[_COMMUNITY_Showcase Capture|Showcase Capture]]
- [[_COMMUNITY_Video TypeScript Config|Video TypeScript Config]]
- [[_COMMUNITY_Secure Video Delivery|Secure Video Delivery]]
- [[_COMMUNITY_App Layout|App Layout]]
- [[_COMMUNITY_Showcase Manifest|Showcase Manifest]]
- [[_COMMUNITY_Showcase Manifest|Showcase Manifest]]
- [[_COMMUNITY_Showcase Manifest|Showcase Manifest]]
- [[_COMMUNITY_Authentication Security|Authentication Security]]
- [[_COMMUNITY_Manim Scene|Manim Scene]]
- [[_COMMUNITY_Serverless URL Shortener|Serverless URL Shortener]]
- [[_COMMUNITY_Job API Contracts|Job API Contracts]]
- [[_COMMUNITY_Next Config|Next Config]]
- [[_COMMUNITY_Playwright Config|Playwright Config]]
- [[_COMMUNITY_Frontend State|Frontend State]]
- [[_COMMUNITY_API Package|API Package]]

## God Nodes (most connected - your core abstractions)
1. `Settings` - 23 edges
2. `Database` - 21 edges
3. `generate_lesson()` - 16 edges
4. `run_generation_job()` - 15 edges
5. `compilerOptions` - 15 edges
6. `LessonPackage` - 14 edges
7. `make_client()` - 13 edges
8. `load_settings()` - 12 edges
9. `synthesize_segments()` - 11 edges
10. `reject_html()` - 9 edges

## Surprising Connections (you probably didn't know these)
- `Remotion Manim FFmpeg` --semantically_similar_to--> `Rendering Audio Storage Guide`  [INFERRED] [semantically similar]
  outputs/manual-20260519-focusly/presentations/focusly-phase-1-genai-v2/output/focusly-phase-1-genai-evaluation-v2.pdf → docs/canonical/08-rendering-audio-storage-guide.md
- `LangGraph and LangChain` --semantically_similar_to--> `Path B Graph`  [INFERRED] [semantically similar]
  outputs/manual-20260519-focusly/presentations/focusly-phase-1-genai-v2/output/focusly-phase-1-genai-evaluation-v2.pdf → docs/canonical/05-langgraph-agent-pipeline.md
- `Rendering Pipeline` --semantically_similar_to--> `Programmatic Video`  [INFERRED] [semantically similar]
  docs/architect/04-remotion-manim-rendering.md → Product Requirements Document.md
- `ARQ Queue Lifecycle` --semantically_similar_to--> `Async Job Queue`  [INFERRED] [semantically similar]
  docs/architect/06-database-queue-storage.md → Product Requirements Document.md
- `PostgreSQL Architecture` --semantically_similar_to--> `Single PostgreSQL Database`  [INFERRED] [semantically similar]
  docs/architect/06-database-queue-storage.md → Product Requirements Document.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Focusly MVP Architecture Alignment** — product_requirements_document_focusly, architect_01_high_level_system_design_system_architecture, canonical_04_api_and_data_contracts_pipeline_state_contract, canonical_05_langgraph_agent_pipeline_path_b_graph [INFERRED 0.85]
- **Media Delivery Chain** — canonical_08_rendering_audio_storage_guide_remotion_manim, canonical_08_rendering_audio_storage_guide_ffmpeg_hls, canonical_08_rendering_audio_storage_guide_webvtt_r2, canonical_07_frontend_implementation_guide_videojs_lesson_player [INFERRED 0.85]
- **Private MVP Simplification** — plans_2026_06_24_focusly_openai_kokoro_mvp_openai_responses_api, plans_2026_06_24_focusly_openai_kokoro_mvp_kokoro_tts, plans_2026_06_24_focusly_openai_kokoro_mvp_sequential_python_pipeline, plans_2026_06_24_focusly_openai_kokoro_mvp_native_mp4_video [EXTRACTED 1.00]

## Communities (32 total, 5 thin omitted)

### Community 0 - "Backend Database"
Cohesion: 0.11
Nodes (27): DeclarativeBase, Database, Job, JobStatus, Base, JobRecord, run_generation_job(), Job (+19 more)

### Community 1 - "Config Lesson Generation"
Cohesion: 0.13
Nodes (29): Any, load_settings(), Settings, build_lesson_prompt(), build_response_schema(), CerebrasClient, ChatApi, ChatCompletionsApi (+21 more)

### Community 2 - "Web UI Components"
Cohesion: 0.11
Nodes (19): GenerateForm(), JobCard(), JobProgress(), stageCopy, LessonPlayer(), findPendingQuiz(), QuizCard(), TimedQuiz (+11 more)

### Community 3 - "System Architecture"
Cohesion: 0.09
Nodes (25): FastAPI Gateway Layer, Next.js Client Layer, High-Level System Architecture, 33-Agent Pipeline, StateGraph Topology, LangChain Chain Architecture, Cost Tracking Callback, Frontend Component Hierarchy (+17 more)

### Community 4 - "Video Lesson Model"
Cohesion: 0.16
Nodes (17): getDurationInFrames(), getSceneStartFrames(), getSegmentDurationInFrames(), Lesson, lessonSchema, Segment, segmentSchema, visualPayloadSchema (+9 more)

### Community 5 - "Web Package Dependencies"
Cohesion: 0.08
Nodes (24): dependencies, next, react, react-dom, devDependencies, jsdom, @playwright/test, @testing-library/jest-dom (+16 more)

### Community 6 - "API Schemas"
Cohesion: 0.15
Nodes (12): BaseModel, FastAPI, create_app(), job_response(), ApiModel, CreateJobRequest, JobResponse, LessonResponse (+4 more)

### Community 7 - "Remotion Package"
Cohesion: 0.10
Nodes (20): dependencies, react, react-dom, remotion, @remotion/cli, @remotion/zod-types, zod, devDependencies (+12 more)

### Community 8 - "Audio Captions Pipeline"
Cohesion: 0.22
Nodes (13): build_webvtt(), format_timestamp(), AudioTrack, create_pipeline(), Narration, synthesize_segments(), Segment, Pipeline (+5 more)

### Community 9 - "Web TypeScript Config"
Cohesion: 0.11
Nodes (17): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+9 more)

### Community 10 - "Rendering Queue Infrastructure"
Cohesion: 0.12
Nodes (17): Manim Scenes, Remotion Scenes, Rendering Pipeline, ARQ Queue Lifecycle, PostgreSQL Architecture, Railway Infrastructure, ARQ Worker, Mocked External Services (+9 more)

### Community 11 - "Workspace Scripts"
Cohesion: 0.17
Nodes (11): name, packageManager, private, scripts, dev, dev:api, dev:web, test (+3 more)

### Community 12 - "Showcase Capture"
Cohesion: 0.18
Nodes (10): completed, failed, manifest, outDir, ROOT, safeName(), shotsDir, stamp (+2 more)

### Community 13 - "Video TypeScript Config"
Cohesion: 0.18
Nodes (10): compilerOptions, jsx, module, moduleResolution, noUncheckedIndexedAccess, skipLibCheck, strict, target (+2 more)

### Community 14 - "Secure Video Delivery"
Cohesion: 0.25
Nodes (8): R2 Storage Layout, httpOnly Cookie Auth, Signed R2 URLs, Threat Model, Cloudflare Edge, REQ-003 Watch Generated Lesson, HLS Access Model, video.js LessonPlayer

### Community 15 - "App Layout"
Cohesion: 0.40
Nodes (3): bodyFont, displayFont, metadata

### Community 16 - "Showcase Manifest"
Cohesion: 0.40
Nodes (4): apiUrl, artifacts, baseUrl, createdAt

### Community 17 - "Showcase Manifest"
Cohesion: 0.40
Nodes (4): apiUrl, artifacts, baseUrl, createdAt

### Community 18 - "Showcase Manifest"
Cohesion: 0.40
Nodes (4): apiUrl, artifacts, baseUrl, createdAt

### Community 19 - "Authentication Security"
Cohesion: 0.50
Nodes (4): REQ-001 Account Session, Auth Cookie Contract, RS256 Cookie Auth, CSRF and User Data Isolation

### Community 21 - "Serverless URL Shortener"
Cohesion: 0.50
Nodes (4): API Gateway, AWS Lambda, DynamoDB, Serverless URL Shortener

### Community 22 - "Job API Contracts"
Cohesion: 0.67
Nodes (3): REQ-002 Generate Lesson Prompt, API Endpoint List, Job Status States

## Knowledge Gaps
- **136 isolated node(s):** `focusly-api`, `bodyFont`, `displayFont`, `metadata`, `stageCopy` (+131 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **5 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Database` connect `Backend Database` to `Config Lesson Generation`, `API Schemas`?**
  _High betweenness centrality (0.015) - this node is a cross-community bridge._
- **Why does `Settings` connect `Config Lesson Generation` to `Backend Database`, `API Schemas`?**
  _High betweenness centrality (0.012) - this node is a cross-community bridge._
- **Why does `LessonPackage` connect `Config Lesson Generation` to `Backend Database`, `API Schemas`?**
  _High betweenness centrality (0.008) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `Settings` (e.g. with `CerebrasClient` and `ChatApi`) actually correct?**
  _`Settings` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `Database` (e.g. with `Job` and `JobStatus`) actually correct?**
  _`Database` has 4 INFERRED edges - model-reasoned connections that need verification._
- **What connects `focusly-api`, `bodyFont`, `displayFont` to the rest of the system?**
  _139 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Backend Database` be split into smaller, more focused modules?**
  _Cohesion score 0.11341463414634147 - nodes in this community are weakly interconnected._