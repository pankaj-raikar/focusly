# Focusly — LangGraph State Machine Architecture

## 1. Overview

The 33-agent pipeline is defined as a LangGraph `StateGraph`. Each agent is a node that reads from and writes to a shared `PipelineState`. Edges define execution order. Parallel branches execute concurrently. Conditional edges handle QA retry loops.

---

## 2. StateGraph Topology

```
START
  │
  ▼
┌──────────────────────────────────────────────────────────────────┐
│ LAYER 1: ORCHESTRATION                                           │
│ ┌─────────────┐                                                  │
│ │  A01 Init   │ (job_id, topic, audience_level → initialized)    │
│ └──────┬──────┘                                                  │
└────────┼───────────────��─────────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────────────────────────┐
│ LAYER 2: KNOWLEDGE (parallel where possible)                     │
│ ┌───────────┐    ┌──────────────────┐                           │
│ │ A02       │───►│  A03 Curriculum  │                           │
│ │ Audience  │    │  Architect       │                           │
│ └───────────┘    └───────┬──────────┘                           │
│         │                │          │                            │
│         │         ┌──────▼───┐  ┌───▼──────────┐               │
│         │         │   A04    │  │     A05      │  ← parallel   │
│         │         │ Misconce │  │  Objectives  │               │
│         │         └──────┬───┘  └───┬──────────┘               │
│ ┌───────▼─────────┐      │          │                           │
│ │ A13 Typography  │      │          │                           │
│ │ (from A02)      │      │          │                           │
│ └───────┬─────────┘      │          │                           │
│ ┌───────▼─────────┐      │          │                           │
│ │ A14 Accessibil  │      │          │                           │
│ └─────────────────┘      │          │                           │
└──────────────────────────┼──────────┼───────────────────────────┘
                           │          │
                           ▼          ▼
┌──────────────────────────────────────────────────────────────────┐
│ LAYER 3: SCRIPT                                                  │
│ ┌──────────────────────────────────────────────┐                │
│ │ A06 ScriptWriter (waits for A04 + A05)       │                │
│ └──────┬────────────┬────────────┬─────────────┘                │
│        │            │            │                               │
│  ┌─────▼────┐ ┌─────▼────┐ ┌────▼──────────┐  ← parallel      │
│  │ A07      │ │ A08      │ │ A09           │                   │
│  │ Pacing   │ │ Hook     │ │ Quiz          │                   │
│  └─────┬────┘ └──────────┘ └───────────────┘                   │
└────────┼────────────────────────────────────────────────────────┘
         │
         ├──► A10 SceneDirector
         ├──► A21 TTSNarration (starts in parallel with scenes)
         │
         ▼
┌──────────────────────────────────────────────────────────────────┐
│ LAYER 4: VISUAL (parallel branches)                              │
│ ┌──────────┐  ┌──────────┐  ┌──────────┐                       │
│ │  A10     │  │  A12     │  │  A13     │                       │
│ │ SceneDir │─►│ Assets   │  │ (done)   │                       │
│ │          │─►│          │  │          │                       │
│ └────┬─────┘  └──────────┘  └──────────┘                       │
│      │                                                          │
│ ┌────▼──────┐                                                   │
│ │  A11      │                                                   │
│ │ Metaphor  │                                                   │
│ └───────────┘                                                   │
└──────────────────────────────────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────────────────────────┐
│ LAYER 5: CODEGEN (per-scene parallel fan-out)                    │
│                                                                  │
│ ┌────────────────────────────────────────────────────────────┐   │
│ │ for each scene in scene_manifest:                         │   │
│ │   if type == "remotion": A15 RemotionCoder                │   │
│ │   if type == "manim":    A16 ManimCoder                   │   │
│ │   if type == "d3":       A17 D3ChartCoder                 │   │
│ │   if type == "threejs":  A18 ThreeJSCoder                 │   │
│ │                                                          │   │
│ │   Then: A19 AnimationTiming (waits for code + A21 audio)  │   │
│ └───────────────────────────────────────────────────────���────┘   │
│                                                                  │
│ ┌──────────┐  ┌──────────┐                                      │
│ │ A20 Capt │  │ A21 TTS  │ (already running)                    │
│ │ (from A21)│  │          │                                      │
│ └──────────┘  └──────────┘                                      │
└──────────────────────────────────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────────────────────────┐
│ LAYER 6: AUDIO (parallel)                                        │
│ ┌──────────┐  ┌──────────┐  ┌──────────┐                       │
│ │ A21 TTS  │  │ A22 Music│  │ A23 Sound│                       │
│ └────┬─────┘  └────┬─────┘  └────┬─────┘                       │
│      │             │             │                               │
│      └─────────────┼─────────────┘                               │
│                    ▼                                             │
│              ┌──────────┐                                       │
│              │ A24 Mix  │                                       │
│              └──────────┘                                       │
└──────────────────────────────────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────────────────────────┐
│ LAYER 7: QA (parallel checks → conditional routing)              │
│ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐       │
│ │ A25 Code │ │A26 Visual│ │ A27 Sync │ │ A28 Edu QA   │       │
│ └────┬─────┘ └────┬─────┘ └────┬─────┘ └──────┬───────┘       │
│      └────────────┼────────────┼───────────────┘               │
│                   ▼                                            │
│            ┌──────────────┐                                    │
│            │  route_qa    │ (conditional edge)                 │
│            │              │                                    │
│            │  "proceed" ──► render_scenes                      │
│            │  "retry_X" ─► back to failing agent (max 3x)     │
│            └──────────────┘                                    │
└──────────────────────────────────────────────────────────────────┘
         │
         ▼ (all QA passed or max retries exceeded)
┌──────────────────────────────────────────────────────────────────┐
│ LAYER 8: RENDER                                                  │
│ ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│ │A29 Render    │  │A30 FFmpeg    │  │A31 Evaluate  │          │
│ │Orchestrator  │─►│Stitch        │─►│Outcome       │          │
│ └──────────────┘  └──────────────┘  └──────┬───────┘          │
│                                            │                   │
│                                    ┌───────▼───────┐           │
│                                    │  A32 Memory   │           │
│                                    └───────┬───────┘           │
│                                            │                   │
│                                            ▼                   │
│                                           END                  │
└────────────────────────────────────��─────────────────────────────┘
```

---

## 3. Conditional Edge Logic

```python
def should_retry_or_proceed(state: PipelineState) -> str:
    """Route QA results: retry failing agents or proceed to render."""

    qa = state.get("qa_results", {})
    retries = state.get("retry_counts", {})

    # Priority-ordered checks (fail-fast)
    checks = [
        ("code_qa_passed",         "generate_scene_code", "retry_code"),
        ("visual_qa_passed",       "set_typography",      "retry_visual"),
        ("sync_qa_passed",         "align_animations",    "retry_sync"),
        ("educational_qa_passed",  "write_script",        "retry_educational"),
    ]

    for passed_key, target_node, route_name in checks:
        if not qa.get(passed_key, False):
            if retries.get(route_name, 0) < 3:
                return route_name
            # Max retries — log and proceed to render anyway
            logger.warning("qa_max_retries", check=passed_key)

    return "proceed"
```

---

## 4. Checkpointing

**Backend:** PostgreSQL via `langgraph-checkpoint-postgres`.

```python
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

checkpointer = AsyncPostgresSaver.from_conn_string(DATABASE_URL)
graph = build_pipeline_graph(checkpointer=checkpointer)
```

**Checkpoint table:** `langgraph_checkpoints(thread_id, checkpoint_ns, checkpoint_id, parent_id, checkpoint JSONB, metadata JSONB)`

**Recovery flow:**
1. ARQ retries the task
2. `graph.ainvoke(state, config={"configurable": {"thread_id": job_id}})` loads last checkpoint
3. Pipeline resumes from the last completed node
4. Only uncompleted nodes are re-executed

---

## 5. Node Function Pattern

Every node follows the same pattern:

```python
async def some_agent_node(state: PipelineState) -> dict:
    """Agent description."""

    # 1. Build chain (or reuse cached chain)
    chain = build_simple_chain("A##_name", OutputModel)

    # 2. Execute with retry on API errors
    async def call():
        return await chain.ainvoke({
            **relevant_state_fields,
            "format_instructions": get_parser(OutputModel).get_format_instructions(),
        })

    result = await execute_with_retry("A##", call)

    # 3. Return partial state update (merged by LangGraph)
    return {
        "some_field": result.model_dump(),
        "current_agent": "A##",
        "progress_percent": NN.N,
    }
```

---

## 6. Parallel Execution Details

LangGraph executes nodes in parallel when they have no dependency between them. The graph automatically detects:

| Parallel Group | Nodes | Why Parallel |
|---------------|-------|-------------|
| Knowledge 1 | A04, A05 | Both depend only on A03 output |
| Script | A07, A08, A09 | All depend only on A06 output |
| Visual | A11, A12 | Both depend on A10; A13 runs independently from A02 |
| Scenes + TTS | A15-A18 (per scene), A21 | Code gen and TTS are independent |
| QA | A25, A26, A27, A28 | All checks are independent |
| Music + Sound | A22, A23 | Both depend on different inputs |

---

## 7. Streaming Updates

LangGraph supports streaming node outputs. The backend exposes these via the job polling endpoint:

```python
async def get_job_status(job_id: str):
    # Read from LessonContext JSONB in lesson_jobs table
    context = job.context or {}
    return {
        "status": job.status,
        "progress_percent": context.get("progress_percent", 0),
        "current_agent": context.get("current_agent"),
        "agent_statuses": context.get("agent_statuses", {}),
    }
```

Each node writes `current_agent` and `progress_percent` to state. The ARQ worker periodically persists state to the database (on checkpoint) so the polling endpoint can read it.
