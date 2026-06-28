# Focusly — Reduced Agent Plan (Path B: 10 Agents)

## 1. Overview

This document defines **Path B** — a reduced 10-agent pipeline that delivers high-quality output with faster build time and lower complexity. It is an alternative to the full 33-agent pipeline (**Path A**), not a replacement. Both paths use the same infrastructure (LangGraph, LangChain, Remotion, Manim, FFmpeg).

**When to use Path B:**
- MVP validation with real users (Weeks 1-8)
- Solo engineer building alone
- Need fast iteration on prompt quality
- Budget-conscious early stage

**When to evolve to Path A:**
- After MVP validation confirms product-market fit
- When output quality plateaus and specialized agents would help
- When you have budget for higher per-lesson cost
- When you want per-concern QA (accessibility, sync, educational coverage)

---

## 2. Agent Mapping: 33 → 10

| Reduced Agent | Merges From | Model | Rationale |
|--------------|-------------|-------|-----------|
| **R01 Orchestrator** | A01 | Sonnet 4.6 | Task graph, state management, progress tracking |
| **R02 Planner** | A02 + A03 + A04 + A05 | Opus 4.6 | One call produces: audience profile, curriculum outline, misconceptions, and objectives. Heavy reasoning needed. |
| **R03 Scriptwriter** | A06 + A07 + A08 | Sonnet 4.6 | One call produces: full script with pacing markers, hook, closing summary. Pacing rules injected into the prompt rather than a separate agent. |
| **R04 QuizMaster** | A09 | Sonnet 4.6 | Quiz generation from script + misconceptions. Same as Path A — already focused. |
| **R05 SceneDirector** | A10 + A11 + A12 + A13 + A14 | Sonnet 4.6 | One call produces: scene manifest with metaphors, asset requirements, design tokens, and accessibility check. The accessibility check is embedded in the prompt constraints rather than a separate audit. |
| **R06 CodeGenerator** | A15 + A16 + A17 + A18 | Sonnet 4.6 (temp=0) | Generates code for ALL scene types (Remotion TSX, Manim Python, D3). Uses RetryChain with syntax validation. Single agent, iterates over scenes sequentially. |
| **R07 AudioProducer** | A21 + A22 + A23 + A24 | Haiku 4.5 (orchestration only) | Calls ElevenLabs for TTS, Pixabay for music, applies sound cues (rule-based), mixes audio via FFmpeg. No LLM needed for most steps — the agent is a coordinator. |
| **R08 Animator** | A19 + A20 | None (Python) | Pure Python: aligns animation timing to audio word timestamps, generates SRT captions. No LLM involved. |
| **R09 QAGate** | A25 + A26 + A27 + A28 | Haiku 4.5 | Single QA pass: code compilation, visual check, sync check, educational coverage. Consolidated report with pass/fail per concern. If any fails, routes back to the relevant agent (R03, R05, or R06). |
| **R10 Renderer** | A29 + A30 + A31 + A32 | Haiku 4.5 (eval only) | Renders scenes (Remotion + Manim), stitches with FFmpeg, evaluates outcome, stores memory. Most work is subprocess execution, not LLM. |

---

## 3. LangGraph StateGraph (Reduced)

```python
# agents/graph_reduced.py

START
  │
  ▼
R01 Orchestrator (initialize)
  │
  ▼
R02 Planner (audience + curriculum + misconceptions + objectives)
  │
  ├──► R03 Scriptwriter (script + pacing + hook)
  │
  ├──► R05 SceneDirector (scene manifest + metaphors + assets + design)
  │         (parallel with R03)
  │
  ▼
R04 QuizMaster (quiz questions from script)
  │
  ├──► R06 CodeGenerator (generate scene code, sequential per scene)
  │         (waits for R03 + R05)
  │
  ├──► R07 AudioProducer (TTS + music + sound + mix)
  │         (starts after R03, parallel with R06)
  │
  ▼
R08 Animator (timing alignment + captions)
  │         (waits for R06 + R07)
  │
  ▼
R09 QAGate (code + visual + sync + educational check)
  │
  ├── PASS ──► R10 Renderer
  │
  └── FAIL ──► Route to failing agent (R03/R05/R06), max 3 retries
               │
               ▼
              R09 QAGate (re-check)
               │
               └──► R10 Renderer (after max retries or pass)
  │
  ▼
R10 Renderer (render + stitch + evaluate + memory)
  │
  ▼
 END
```

### Parallel Execution

| Parallel Group | Agents | Why |
|---------------|--------|-----|
| Script + Scenes | R03, R05 | Script writes narration, SceneDirector designs visuals — independent |
| Code + Audio | R06, R07 | Scene code gen and TTS are independent |
| QA checks | Internal to R09 | All 4 checks run in a single agent call with consolidated output |

### Conditional Edges

```python
def route_qa(state: PipelineState) -> str:
    qa = state.get("qa_results", {})
    retries = state.get("retry_counts", {})

    if not qa.get("code_qa_passed", False) and retries.get("R06", 0) < 3:
        return "retry_code"        # → R06
    if not qa.get("visual_qa_passed", False) and retries.get("R05", 0) < 3:
        return "retry_visual"      # → R05
    if not qa.get("sync_qa_passed", False) and retries.get("R08", 0) < 3:
        return "retry_sync"        # → R08
    if not qa.get("educational_qa_passed", False) and retries.get("R03", 0) < 3:
        return "retry_educational" # → R03

    return "proceed"               # → R10
```

---

## 4. Model Assignment (Multi-Model Strategy)

| Agent | Primary Model | Fallback Model | Why |
|-------|--------------|----------------|-----|
| R01 Orchestrator | Sonnet 4.6 | — | State management, needs reliability |
| R02 Planner | Opus 4.6 | Sonnet 4.6 | Heavy reasoning: curriculum + misconceptions + objectives in one call |
| R03 Scriptwriter | Sonnet 4.6 | — | Creative writing with constraints |
| R04 QuizMaster | Sonnet 4.6 | — | Educational assessment design |
| R05 SceneDirector | Sonnet 4.6 | — | Visual direction + metaphor + layout |
| R06 CodeGenerator | Sonnet 4.6 (temp=0) | — | Deterministic code generation |
| R07 AudioProducer | Haiku 4.5 | GPT-4o-mini | Mostly coordination, minimal LLM |
| R08 Animator | None | — | Pure Python, no LLM needed |
| R09 QAGate | Haiku 4.5 | GPT-4o-mini | Checklist evaluation, lightweight |
| R10 Renderer | Haiku 4.5 | — | Evaluation only, rest is subprocess |

### Cost Estimate per Lesson (Reduced Pipeline)

| Agent Tier | Calls | Model | Est. Cost |
|-----------|-------|-------|-----------|
| Heavy reasoning (R02) | 1 | Opus 4.6 | $0.08 |
| Standard (R01, R03, R04, R05, R06) | 5 | Sonnet 4.6 | $0.10 |
| Lightweight (R07, R09, R10) | 3 | Haiku 4.5 | $0.01 |
| Non-LLM (R08) | 0 | — | $0.00 |
| ElevenLabs TTS | — | — | $0.10 |
| **Total** | **9 LLM calls** | | **~$0.29/lesson** |

---

## 5. Build Timeline (Path B)

### Week 1-2: Foundation
Same as Path A Phase 0: monorepo, Docker, FastAPI, auth, CI/CD, Railway.

### Week 3: Core Pipeline Skeleton
- LangGraph StateGraph with 10 nodes
- LangChain ChatAnthropic with multi-model config
- R01 Orchestrator + R02 Planner (Opus 4.6)
- LessonContext JSONB schema
- ARQ job queue

**Milestone:** Submit topic → get curriculum outline + misconceptions in database.

### Week 4: Script + Scenes + Quiz
- R03 Scriptwriter (script + pacing + hook)
- R05 SceneDirector (scene manifest + metaphors + assets + design tokens)
- R04 QuizMaster (quiz questions)
- POST /lessons/generate → full planning pipeline → context saved

**Milestone:** Submit "binary search" → get complete script, scene manifest, quiz in database.

### Week 5-6: Code Generation + Audio + Rendering
- R06 CodeGenerator (Remotion TSX + Manim Python, with RetryChain)
- R07 AudioProducer (ElevenLabs + music + sound + mix)
- R08 Animator (timing + captions)
- R10 Renderer (Remotion render + Manim render + FFmpeg stitch + HLS)
- VideoPlayer component with HLS

**Milestone:** Topic → full video with narration in R2 → watchable.

### Week 7: QA + Polish
- R09 QAGate (consolidated QA with retry routing)
- Error handling, rate limiting, Sentry
- Cost tracking (PipelineTokenTracker)
- Watch session tracking + quiz attempts

**Milestone:** Self-correcting pipeline. Eval scores stored.

### Week 8: Launch
Same as Path A Phase 5: production Railway, domain, beta users.

**Total: 8 weeks** (vs 12 weeks for Path A)

---

## 6. Prompt Design (Key Difference from Path A)

In Path B, prompt engineering is more critical because fewer agents handle more concerns. Each agent's prompt must be more detailed and include constraints that Path A delegates to specialized agents.

### R02 Planner Prompt (Example)

```markdown
You are a curriculum designer AND learning scientist. Given a topic and audience level, produce ALL of the following in a single JSON response:

1. **audience_profile**: Vocabulary ceiling, assumed prerequisites, cognitive load considerations
2. **curriculum_outline**: Ordered concept list with target durations (each ≤30 seconds)
3. **misconceptions**: For each concept, the most common wrong belief and a corrective framing
4. **learning_objectives**: One testable, measurable objective per concept

CONSTRAINTS:
- Total lesson duration: 3-5 minutes
- Each segment: ≤30 seconds
- Maximum 2 new concepts per segment
- Target audience: {level} engineering students
- ADHD-optimized pacing: short segments, visual hooks, active recall

TOPIC: {topic}
AUDIENCE LEVEL: {audience_level}
```

### R03 Scriptwriter Prompt (Example)

```markdown
You are a scriptwriter AND pacing director AND engagement specialist. Write the complete narration script for this lesson.

For each segment, include:
- narration text (conversational, not academic)
- emphasis_words (words to stress in TTS)
- pause_before_ms and pause_after_ms (inject 1-2s silence after hard concepts)
- duration_seconds target

Also produce:
- hook_text: The first 8 seconds. Must answer "why does this matter to me right now?" before any content.
- closing_summary: Key takeaways in 2-3 sentences.

SCRIPT RULES:
- One concept per segment
- Maximum 7 words displayed on screen at once
- Never more than 2 new concepts in 30 seconds
- Use analogies and metaphors — don't just describe, explain WHY
- Target: insight-generating explanation, not accurate-but-hollow description
```

---

## 7. Evolution Path: B → A

When to evolve and how:

| Trigger | Action |
|---------|--------|
| Output quality plateaus | Split R02 into A02+A03+A04+A05 for better prompts |
| Accessibility issues in videos | Extract A14 AccessibilityAgent from R05 |
| Audio-visual sync complaints | Extract A19 AnimationTimingAgent from R08 |
| Quiz pass rates below 70% | Extract A28 EducationalQA from R09 |
| Need better metaphors | Extract A11 VisualMetaphor from R05 |
| Need music/sound quality | Extract A22+A23 from R07 |
| Need cross-lesson learning | Extract A32 MemoryAgent from R10 |

The evolution is incremental: split one agent at a time, validate the improvement, then split the next. The LangGraph architecture supports this naturally — you just add more nodes and edges.

---

## 8. Comparison: Path A vs Path B

| Dimension | Path A (33 Agents) | Path B (10 Agents) |
|-----------|-------------------|-------------------|
| Build time | 12 weeks | 8 weeks |
| Agent count | 33 | 10 |
| LLM calls per lesson | ~14 | ~9 |
| Cost per lesson | ~$0.32 | ~$0.29 |
| Prompt complexity | Low (focused prompts) | High (multi-concern prompts) |
| QA granularity | Per-concern (code, visual, sync, educational) | Consolidated (single QA pass) |
| Output quality ceiling | Higher (specialized agents) | Good (generalist agents) |
| Iteration speed | Slower (more agents to tune) | Faster (fewer prompts to iterate) |
| Maintenance burden | Higher | Lower |
| Evolution flexibility | Start here | Can evolve to Path A incrementally |

**Recommendation:** Start with Path B. Validate the product with real users. Evolve to Path A when specific quality concerns emerge that justify the additional complexity.
