# LangGraph Agent Pipeline

## Purpose
Define the canonical Path B 10-agent LangGraph MVP pipeline, node contracts, retry routing, checkpointing, progress reporting, and failure behavior.

## Owner Skills
- Primary: llm-application-dev
- Supporting: out-of-box-prompt, python-development, systematic-debugging, test-driven-development, verification-before-completion

## Expected Output
Future agents can implement the graph with deterministic stage names, typed state, structured Claude outputs, and testable retry behavior.

## Path B Graph
```text
R01 Orchestrator
  -> R02 Planner
  -> parallel: R03 Scriptwriter + R05 SceneDirector
  -> R04 QuizMaster
  -> parallel: R06 CodeGenerator + R07 AudioProducer
  -> R08 Animator
  -> R09 QAGate
  -> R10 Renderer
```

Reasoning: The MVP needs separation between pedagogy, script, visuals, code, audio, synchronization, QA, and rendering. Ten agents are enough because each node owns a clear artifact and parallelism is limited to places with low dependency conflict.

## Shared Node Input
Every node receives `PipelineState` with `job_id`, `lesson_id`, `thread_id`, user-safe generation parameters, current artifacts, errors, and retry counters.

## R01-R10 Contracts
| Node | Inputs | Outputs | Acceptance Criteria |
|---|---|---|---|
| R01 Orchestrator | Create request, user, lesson, job | Initialized `PipelineState`, stage events | State exists in PostgreSQL JSONB before downstream calls. |
| R02 Planner | Topic, audience preferences | `LessonContext` | 3-7 segments, objectives, misconceptions, ADHD supports. |
| R03 Scriptwriter | `LessonContext` | Narration script, pacing markers, hook, close | Script maps to segment IDs and duration targets. |
| R05 SceneDirector | `LessonContext` | Scene manifest, visual metaphors, layout rules, design tokens | One primary idea per scene and no external asset dependencies. |
| R04 QuizMaster | `LessonContext`, script | Quiz checkpoints | At least 2 checkpoints when duration exceeds 90 seconds. |
| R06 CodeGenerator | Script, scene manifest | Remotion TSX specs, Manim specs, syntax validation report | Generated assets validate syntactically before render. |
| R07 AudioProducer | Narration script | ElevenLabs audio keys, word timestamps | Audio stored in R2 and timestamps align to narration text. |
| R08 Animator | Code assets, audio timings, quiz | Timeline alignment, WebVTT/SRT captions | Captions are toggleable tracks and quiz timestamps are valid. |
| R09 QAGate | All artifacts | QA report, retry directives | Blocks render on critical sync, code, educational, or privacy failures. |
| R10 Renderer | Approved artifacts | HLS, final captions, manifest, playback metadata | HLS and caption URLs are persisted and lesson marked succeeded. |

## Node Output Schemas
Use Pydantic models for graph state fragments. Pseudocode shape:

```python
class AgentResult(BaseModel):
    stage: StageName
    status: Literal["ok", "retry", "failed"]
    output: dict
    issues: list[PipelineIssue] = []
    progress_percent: int
```

```python
class PipelineIssue(BaseModel):
    severity: Literal["info", "warning", "critical"]
    code: str
    message: str
    retry_target: StageName | None = None
```

## Retry Routing
| Failure | Retry Target | Max Attempts | Reasoning |
|---|---|---|---|
| Invalid structured Claude output | Same node | 2 | Parser repair is cheap and local. |
| Script/scene mismatch | R03 and R05 | 1 | Both artifacts may need re-alignment. |
| Code syntax failure | R06 | 2 | Code generation can self-repair with validation output. |
| TTS transient failure | R07 | 3 | External API failures are often transient. |
| Caption/audio drift | R08 | 2 | Alignment can be recalculated without regenerating lesson content. |
| QA critical pedagogy issue | R02 | 1 | Requires upstream lesson plan correction. |
| Render command failure | R10 then R06 if syntax-related | 2 | Some failures are render environment issues; syntax failures go back to code. |

## Checkpointing
- Compile the graph with a production Postgres checkpointer.
- Always invoke with `configurable.thread_id = "job:{job_id}"`.
- Persist a denormalized `pipeline_states.state_json` snapshot after every successful node.
- Do not use in-memory checkpointing outside tests.

Reasoning: LangGraph checkpointing supports resume and inspection. PostgreSQL JSONB makes the API and dashboard independent of LangGraph internals.

## Progress Reporting
| Stage | Progress |
|---|---:|
| R01 | 5 |
| R02 | 15 |
| R03/R05 | 30 |
| R04 | 40 |
| R06/R07 | 65 |
| R08 | 75 |
| R09 | 85 |
| R10 | 100 |

Progress updates must write both `generation_jobs` and `job_events`.

## Failure Handling
- Expected validation failures return `failed` with safe user-facing messages.
- Retryable failures use `waiting_retry` while scheduled.
- Critical failures persist internal details only in server logs or `job_events.metadata_json`, not user responses.
- Partial R2 artifacts remain under job-scoped keys for debugging but are not exposed through playback until success.

## Why LangGraph Is Required
LangGraph is required because Focusly has durable, branching, retryable, inspectable agent execution. A linear script would hide state transitions and make QA retry routing brittle.

## Why 10 Agents Are Enough for MVP
The 10-agent split maps to MVP artifact boundaries: orchestration, planning, writing, quiz, visual direction, code, audio, alignment, QA, render. More agents would add coordination overhead before product value is proven.

## Acceptance Criteria
- The graph topology matches Path B exactly.
- Every node has input, output, and retry contracts.
- Checkpointing uses PostgreSQL and stable `thread_id` values.
- Progress reporting maps user-visible stages to R01-R10.

## Related Docs
- [API and Data Contracts](./04-api-and-data-contracts.md)
- [Rendering, Audio, and Storage Guide](./08-rendering-audio-storage-guide.md)
- [Testing and Verification Guide](./09-testing-and-verification-guide.md)
