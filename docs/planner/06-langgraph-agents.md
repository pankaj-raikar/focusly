# Focusly — LangGraph Agent Orchestration

## 1. Overview

LangGraph defines the execution DAG for all 33 agents. Each agent is a node that wraps a LangChain chain. Edges define execution order, with parallel fan-out where dependencies allow. Conditional edges handle QA retry loops. PostgreSQL-backed checkpointing enables crash recovery.

---

## 2. State Definition

```python
# agents/state.py
from typing import TypedDict, Any, Annotated
from operator import add


class PipelineState(TypedDict, total=False):
    # Identity
    job_id: str
    user_id: str
    topic: str
    audience_level: str

    # Layer 2 — Knowledge
    learner_profile: dict
    lesson_outline: list[str]
    misconception_map: list[dict]
    learning_objectives: list[str]

    # Layer 3 — Script
    script_segments: list[dict]
    hook_text: str
    closing_summary: str
    quiz_questions: list[dict]

    # Layer 4 — Visual
    scene_manifest: list[dict]
    asset_manifest: list[str]
    design_tokens: dict

    # Layer 5 — Code Gen
    generated_scenes: list[dict]          # Annotated[list, add] for parallel append
    caption_srt: str

    # Layer 6 — Audio
    audio_assets: list[dict]
    final_audio_path: str

    # Layer 7 — QA
    qa_results: dict                      # { "code_qa_passed": bool, ... }
    qa_errors: list[dict]                 # errors for retry context

    # Layer 8 — Render
    rendered_scene_paths: list[str]
    final_video_path: str
    hls_playlist_path: str
    thumbnail_path: str
    eval_score: float
    eval_notes: str

    # Tracking
    current_agent: str
    progress_percent: float
    errors: list[str]
    retry_counts: dict[str, int]          # agent_id → count
    total_duration_seconds: int
```

---

## 3. Graph Construction

```python
# agents/graph.py
from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from focusly.agents.state import PipelineState
from focusly.agents.nodes.orchestration import initialize_job
from focusly.agents.nodes.knowledge import (
    calibrate_audience, build_curriculum, model_misconceptions, define_objectives,
)
from focusly.agents.nodes.script import (
    write_script, add_pacing, create_hook, generate_quizzes,
)
from focusly.agents.nodes.visual import (
    direct_scenes, enrich_metaphors, hunt_assets, set_typography, audit_accessibility,
)
from focusly.agents.nodes.codegen import (
    generate_scene_code, generate_captions, align_animations,
)
from focusly.agents.nodes.audio import (
    generate_narration, select_music, design_sounds, mix_audio,
)
from focusly.agents.nodes.qa import (
    check_code, check_visuals, check_sync, check_educational,
    route_qa_result,
)
from focusly.agents.nodes.render import (
    render_scenes, stitch_video, evaluate_outcome, store_memory,
)


def build_pipeline_graph(checkpointer=None) -> StateGraph:
    graph = StateGraph(PipelineState)

    # ── Layer 1: Orchestration ──
    graph.add_node("initialize", initialize_job)

    # ── Layer 2: Knowledge ──
    graph.add_node("calibrate_audience", calibrate_audience)
    graph.add_node("build_curriculum", build_curriculum)
    graph.add_node("model_misconceptions", model_misconceptions)
    graph.add_node("define_objectives", define_objectives)

    # ── Layer 3: Script ──
    graph.add_node("write_script", write_script)
    graph.add_node("add_pacing", add_pacing)
    graph.add_node("create_hook", create_hook)
    graph.add_node("generate_quizzes", generate_quizzes)

    # ── Layer 4: Visual ──
    graph.add_node("direct_scenes", direct_scenes)
    graph.add_node("enrich_metaphors", enrich_metaphors)
    graph.add_node("hunt_assets", hunt_assets)
    graph.add_node("set_typography", set_typography)
    graph.add_node("audit_accessibility", audit_accessibility)

    # ── Layer 5: Code Gen ──
    graph.add_node("generate_scene_code", generate_scene_code)
    graph.add_node("generate_captions", generate_captions)
    graph.add_node("align_animations", align_animations)

    # ── Layer 6: Audio ──
    graph.add_node("generate_narration", generate_narration)
    graph.add_node("select_music", select_music)
    graph.add_node("design_sounds", design_sounds)
    graph.add_node("mix_audio", mix_audio)

    # ── Layer 7: QA ──
    graph.add_node("check_code", check_code)
    graph.add_node("check_visuals", check_visuals)
    graph.add_node("check_sync", check_sync)
    graph.add_node("check_educational", check_educational)
    graph.add_node("route_qa", route_qa_result)

    # ── Layer 8: Render ──
    graph.add_node("render_scenes", render_scenes)
    graph.add_node("stitch_video", stitch_video)
    graph.add_node("evaluate_outcome", evaluate_outcome)
    graph.add_node("store_memory", store_memory)

    # ══════════════════════════════════════════════════════
    # EDGES
    # ══════════════════════════════════════════════════════

    # START → Layer 1
    graph.add_edge(START, "initialize")

    # Layer 1 → Layer 2
    graph.add_edge("initialize", "calibrate_audience")
    graph.add_edge("calibrate_audience", "build_curriculum")

    # Layer 2 parallel: misconceptions + objectives after curriculum
    graph.add_edge("build_curriculum", "model_misconceptions")
    graph.add_edge("build_curriculum", "define_objectives")

    # Layer 2 → Layer 3
    graph.add_edge("model_misconceptions", "write_script")
    graph.add_edge("define_objectives", "write_script")

    # Layer 3: pacing, hook, quiz parallel after script
    graph.add_edge("write_script", "add_pacing")
    graph.add_edge("write_script", "create_hook")
    graph.add_edge("write_script", "generate_quizzes")

    # Layer 3 → Layer 4 (typography starts early from audience)
    graph.add_edge("calibrate_audience", "set_typography")
    graph.add_edge("set_typography", "audit_accessibility")

    # Layer 3 → Layer 4 (scene direction after pacing)
    graph.add_edge("add_pacing", "direct_scenes")
    graph.add_edge("direct_scenes", "enrich_metaphors")
    graph.add_edge("direct_scenes", "hunt_assets")

    # Layer 3 → Layer 6 (TTS starts after pacing)
    graph.add_edge("add_pacing", "generate_narration")

    # Layer 4 → Layer 5 (code gen waits for all visual + narration)
    graph.add_edge("enrich_metaphors", "generate_scene_code")
    graph.add_edge("hunt_assets", "generate_scene_code")
    graph.add_edge("audit_accessibility", "generate_scene_code")

    # Layer 5: parallel sub-graph per scene
    graph.add_edge("generate_scene_code", "align_animations")
    graph.add_edge("generate_narration", "generate_captions")

    # Layer 6: music + sound design parallel, then mix
    graph.add_edge("build_curriculum", "select_music")
    graph.add_edge("direct_scenes", "design_sounds")
    graph.add_edge("generate_narration", "mix_audio")
    graph.add_edge("select_music", "mix_audio")
    graph.add_edge("design_sounds", "mix_audio")

    # Layer 5+6 → Layer 7 (QA after all code gen + audio)
    graph.add_edge("align_animations", "check_code")
    graph.add_edge("align_animations", "check_visuals")
    graph.add_edge("align_animations", "check_sync")
    graph.add_edge("generate_quizzes", "check_educational")

    # QA → conditional routing
    graph.add_edge("check_code", "route_qa")
    graph.add_edge("check_visuals", "route_qa")
    graph.add_edge("check_sync", "route_qa")
    graph.add_edge("check_educational", "route_qa")

    # Route QA → either retry or proceed
    graph.add_conditional_edges(
        "route_qa",
        should_retry_or_proceed,
        {
            "retry_code": "generate_scene_code",
            "retry_visual": "set_typography",
            "retry_sync": "align_animations",
            "retry_educational": "write_script",
            "proceed": "render_scenes",
        },
    )

    # Layer 8: render → stitch → evaluate → memory → END
    graph.add_edge("render_scenes", "stitch_video")
    graph.add_edge("mix_audio", "stitch_video")
    graph.add_edge("generate_captions", "stitch_video")
    graph.add_edge("stitch_video", "evaluate_outcome")
    graph.add_edge("evaluate_outcome", "store_memory")
    graph.add_edge("store_memory", END)

    return graph.compile(checkpointer=checkpointer)
```

---

## 4. QA Conditional Routing

```python
# agents/nodes/qa.py
MAX_RETRIES = 3


def should_retry_or_proceed(state: PipelineState) -> str:
    """Decide whether to retry a failed QA check or proceed to render."""
    qa = state.get("qa_results", {})
    retries = state.get("retry_counts", {})
    errors = state.get("qa_errors", [])

    # Find the first failing check that hasn't exceeded retries
    checks = [
        ("code_qa_passed", "check_code", "retry_code"),
        ("visual_qa_passed", "check_visuals", "retry_visual"),
        ("sync_qa_passed", "check_sync", "retry_sync"),
        ("educational_qa_passed", "check_educational", "retry_educational"),
    ]

    for passed_key, agent_id, retry_route in checks:
        if not qa.get(passed_key, False):
            count = retries.get(agent_id, 0)
            if count < MAX_RETRIES:
                return retry_route
            else:
                # Max retries exceeded — log and proceed anyway
                errors.append(f"QA check {agent_id} failed after {MAX_RETRIES} retries")

    return "proceed"
```

---

## 5. Node Functions (Key Examples)

### 5.1 Initialize Job (A01)

```python
# agents/nodes/orchestration.py
from focusly.agents.state import PipelineState
import structlog

logger = structlog.get_logger("agents")


async def initialize_job(state: PipelineState) -> dict:
    """A01 MasterOrchestrator: Initialize pipeline state."""
    logger.info("pipeline_started", job_id=state["job_id"], topic=state["topic"])
    return {
        "current_agent": "A01",
        "progress_percent": 1.0,
        "errors": [],
        "retry_counts": {},
    }
```

### 5.2 Calibrate Audience (A02)

```python
# agents/nodes/knowledge.py
from focusly.agents.chains.base import build_simple_chain
from focusly.agents.chains.error_handling import execute_with_retry
from focusly.agents.schemas.knowledge import AudienceProfile
from focusly.agents.state import PipelineState


async def calibrate_audience(state: PipelineState) -> dict:
    """A02: Analyze topic + audience level to produce a learner profile."""
    chain = build_simple_chain("A02_audience", AudienceProfile)

    async def call():
        return await chain.ainvoke({
            "topic": state["topic"],
            "audience_level": state.get("audience_level", "intermediate"),
            "format_instructions": "",
        })

    profile = await execute_with_retry("A02", call)
    return {
        "learner_profile": profile.model_dump(),
        "current_agent": "A02",
        "progress_percent": 5.0,
    }
```

### 5.3 Code QA with Retry (A25)

```python
# agents/nodes/qa.py
async def check_code(state: PipelineState) -> dict:
    """A25: TypeScript/Python compilation check on generated scenes."""
    scenes = state.get("generated_scenes", [])
    qa = dict(state.get("qa_results", {}))
    errors = list(state.get("qa_errors", []))

    all_passed = True
    for scene in scenes:
        code = scene.get("generated_code", "")
        scene_type = scene.get("scene_type", "")

        if scene_type == "remotion":
            # TypeScript compilation check
            passed = await validate_typescript(code)
        elif scene_type == "manim":
            # Python AST + Scene class check
            passed = validate_manim_syntax(code)
        else:
            passed = True

        if not passed:
            all_passed = False
            errors.append({
                "agent": "A25",
                "scene_index": scene.get("index"),
                "error": f"Code validation failed for scene {scene.get('index')}",
            })

    qa["code_qa_passed"] = all_passed
    return {"qa_results": qa, "qa_errors": errors}
```

---

## 6. Checkpointing

```python
# In main.py or graph construction
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

async def get_checkpointer():
    return AsyncPostgresSaver.from_conn_string(get_settings().database_url)

# Graph is compiled with checkpointer
graph = build_pipeline_graph(checkpointer=checkpointer)
```

Checkpoint saves state after every node. On crash recovery:
1. ARQ retries the task
2. Graph loads last checkpoint for the thread_id
3. Resumes from the last completed node

---

## 7. Frontend Polling Integration

The frontend polls `GET /lessons/jobs/:job_id`. The response is derived from the pipeline state:

```python
# api/v1/lessons.py
async def get_job_status(job_id: str, db: AsyncSession = Depends(get_db)):
    job = await db.get(LessonJob, UUID(job_id))
    if not job:
        raise NotFoundError("Job not found")

    # Derive progress from agent_statuses in context
    context = job.context or {}
    total_agents = 33
    completed = sum(
        1 for s in context.get("agent_statuses", {}).values()
        if s.get("status") == "done"
    )
    progress = round((completed / total_agents) * 100) if total_agents else 0

    return ApiResponse(data={
        "status": job.status,
        "progress_percent": progress,
        "current_agent": context.get("current_agent"),
        "error_message": job.error_message,
    })
```

---

## 8. Execution Flow Diagram

```
START
  │
  ▼
A01 initialize ──────────────────────────────────────────────────────────────────┐
  │                                                                              │
  ▼                                                                              │
A02 calibrate_audience ──────────────────────────────────────────────────┐       │
  │                                              │                        │       │
  ▼                                              ▼                        │       │
A03 build_curriculum                    A13 set_typography                │       │
  │          │                                  │                          │       │
  ▼          ▼                                  ▼                          │       │
A04 miscons  A05 objectives            A14 audit_accessibility            │       │
  │          │                                                                  │
  ▼          ▼                                                                  │
A06 write_script ───────────────────────────────────────────────────────────────┘
  │          │          │
  ▼          ▼          ▼
A07 pacing  A08 hook   A09 quiz        (parallel)
  │          │          │
  ▼          │          │
A10 direct_scenes ────────────────────────────────────────────────────────────────┐
  │          │                                                                    │
  ▼          ▼                                                                    │
A11 metaphors  A12 assets               (parallel)                               │
  │          │                                                                    │
  ▼          ▼                                                                    │
A15-A18 generate_scene_code ─────────────────────────────────────────────────────┐│
  │                                                                              ││
  ▼                             A21 TTS ──┐                                      ││
A19 align_animations                      │                                      ││
  │                                       ▼                                      ││
  │                              A20 captions                                    ││
  │                                       │                                      ││
  │                              A22 music ──┐                                   ││
  │                              A23 sounds ──┤                                  ││
  │                                           ▼                                  ││
  │                              A24 mix_audio                                   ││
  │                                                                              ││
  ▼                                                                              ││
A25 code_qa ─┐                                                                   ││
A26 visual_qa┤ (parallel)                                                        ││
A27 sync_qa  ─┤                                                                  ││
A28 edu_qa  ──┘                                                                  ││
  │                                                                              ││
  ▼                                                                              ││
route_qa ──── retry? ──► back to failing agent (max 3x)                          ││
  │                                                                              ││
  ▼ (all pass)                                                                   ││
A29 render_scenes ◄──────────────────────────────────────────────────────────────┘│
  │                                                                              │
  ▼                                                                              │
A30 stitch_video ◄───────────────────────────────────────────────────────────────┘
  │
  ▼
A31 evaluate
  │
  ▼
A32 memory
  │
  ▼
 END
```

---

## 9. Task Checklist

- [M] PipelineState TypedDict defined with all fields
- [M] StateGraph built with all 33 nodes
- [M] Sequential edges for Layer 1→2→3
- [M] Parallel edges for A04+A05, A07+A08+A09, A11+A12, A25+A26+A27+A28
- [M] Conditional edges for QA retry routing (route_qa → 5 possible targets)
- [M] Max 3 retries per QA check
- [M] PostgreSQL-backed checkpointing
- [M] Each node function wraps a LangChain chain with execute_with_retry
- [M] Progress tracking (current_agent, progress_percent) updated per node
- [S] Scene rendering sub-graph (parallel fan-out per scene)
- [S] Cost ceiling check between layers
- [S] Streaming execution updates for frontend
- [C] Human-in-the-loop for A31 evaluator (score < 0.6)
