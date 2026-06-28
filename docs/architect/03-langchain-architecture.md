# Focusly — LangChain Chain/Tool/Memory Architecture

## 1. Overview

LangChain serves as the abstraction layer between LangGraph agent nodes and the Claude API. Each agent node wraps one or more LangChain chains that handle prompt formatting, LLM invocation, structured output parsing, tool execution, and error recovery.

---

## 2. Chain Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                     LangGraph Node (e.g. A06 ScriptWriter)       │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │                   LangChain Chain                          │  │
│  │                                                            │  │
│  │  ┌──────────┐   ┌──────────┐   ┌──────────┐              │  │
│  │  │  Prompt   │──►│  LLM     │──►│  Parser  │──► Pydantic │  │
│  │  │ Template  │   │(ChatAnth)│   │(Pydantic)│    Output   │  │
│  │  └──────────┘   └──────────┘   └──────────┘              │  │
│  │       ▲               │                                    │  │
│  │       │               ▼                                    │  │
│  │  ┌──────────┐   ┌──────────┐                              │  │
│  │  │  Memory   │   │ Callback │ (CostTrackingCallback)      │  │
│  │  │ (buffer)  │   └──────────┘                              │  │
│  │  └──────────┘                                              │  │
│  └────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
```

---

## 3. Chain Patterns

### 3.1 Pattern Map

| Pattern | Used By | Description |
|---------|---------|-------------|
| SimpleChain | A02, A05, A07, A08, A13 | Single LLM call → parse structured output |
| SequentialChain | A04 | Two-step: outline generation → misconception analysis |
| ToolCallingChain | A12, A21, A22 | LLM decides which tool to call, executes tool, returns result |
| RetryChain | A15, A16, A17, A18 | LLM → validate output → retry with error context if invalid |
| CreativeChain | A06, A08 | Higher temperature LLM for script/hook generation |

### 3.2 SimpleChain (Most Common)

```
PromptTemplate ──► ChatAnthropic(temp=0.3) ──► PydanticOutputParser ──► BaseModel
```

Input variables: topic, audience_level, context, format_instructions
Output: Pydantic model matching the agent's schema

### 3.3 RetryChain (Code Generation)

```
                  ┌──────────────────────────────────────────────┐
                  │                                              │
PromptTemplate ─��► ChatAnthropic(temp=0) ──► PydanticParser ──► │
                  │                                              │
                  │                              ┌───────────┐   │
                  │                              │ Validator  │   │
                  │                              │ (AST parse │   │
                  │                              │  + class   │   │
                  │                              │  check)    │   │
                  │                              └─────┬─────┘   │
                  │                     valid ◄────────┤         │
                  │                              fail: │         │
                  │                       inject error context    │
                  │                       into next prompt ──────┘
                  │                       (max 3 attempts)
                  └──────────────────────────────────────────────┘
```

---

## 4. Tool Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    Tool Registry                              │
│                                                              │
│  ┌──────────────────┐  ┌──────────────────┐                 │
│  │ UnsplashSearch   │  │ ElevenLabsTTS    │                 │
│  │ (image search)   │  │ (text-to-speech) │                 │
│  │ HTTP: Unsplash   │  │ HTTP: ElevenLabs │                 │
│  │ API              │  │ API              │                 │
│  └──────────────────┘  └──────────────────┘                 │
│                                                              │
│  ┌──────────────────┐  ┌──────────────────┐                 │
│  │ PixabayMusic     │  │ R2Storage        │                 │
│  │ (royalty-free    │  │ (upload/download │                 │
│  │  music search)   │  │  signed URLs)    │                 │
│  │ HTTP: Pixabay    │  │ S3: Cloudflare   │                 │
│  │ API              │  │ R2               │                 │
│  └──────────────────┘  └──────────────────┘                 │
│                                                              │
│  ┌──────────────────┐                                       │
│  │ ManimRender      │                                       │
│  │ (validate +      │                                       │
│  │  preview render) │                                       │
│  │ Subprocess:      │                                       │
│  │ manim CLI        │                                       │
│  └──────────────────┘                                       │
└──────────────────────────────────────────────────────────────┘
```

Each tool is a `BaseTool` subclass with:
- `name` and `description` for LLM tool selection
- `args_schema` (Pydantic model) for input validation
- `_arun()` async implementation
- Error handling with retry for transient failures

---

## 5. Memory Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    Memory Layer                               │
│                                                              │
│  ┌──────────────────────────────────────────────────┐       │
│  │ ConversationBufferWindowMemory (per-agent)        │       │
│  │ Multi-turn refinement within a single pipeline    │       │
│  │ Window: last 10 messages                          │       │
│  │ Used by: A06 (script rewrite), A16 (code fix)     │       │
│  └──────────────────────────────────────────────────┘       │
│                                                              │
│  ┌──────────────────────────────────────────────────┐       │
│  │ EntityTracker (cross-agent, in-memory)             │       │
│  │ Tracks: concepts, techniques, metaphors            │       │
│  │ Updated by: A03, A06, A10, A11                     │       │
│  │ Read by: A06, A10, A11 (inject into prompts)       │       │
│  └──────────────────────────────────────────────────┘       │
│                                                              │
│  ┌──────────────────────────────────────────────────┐       │
│  │ PostgresMemoryStore (A32 MemoryAgent)              │       │
│  │ Persistent across lessons                          │       │
│  │ Table: agent_memory (JSONB)                        │       │
│  │ Stores: metaphors, pacing patterns, scene perf     │       │
│  │ Queried by: A03, A10, A11 before generating        │       │
│  │ Quality-scored: decays over time, boosts on reuse  │       │
│  └──────────────────────────────────────────────────┘       │
└───────────────────────────────────────────���──────────────────┘
```

---

## 6. Observability Pipeline

```
┌──────────────────────────────────────────────────────────────┐
│                Chain Run Observability                        │
│                                                              │
│  LangChain Callback ──► CostTrackingCallback                 │
│       │                                                      │
│       ▼                                                      │
│  ┌──────────────────────────────────────────┐               │
│  │ chain_runs table                          │               │
│  │  - job_id, agent_id, chain_name          │               │
│  │  - model, tokens_in, tokens_out          │               │
│  │  - latency_ms, cost_estimate             │               │
│  │  - cached (bool), error                  │               │
│  └──────────────────────────────────────────┘               │
│       │                                                      │
│       ▼                                                      │
│  PipelineTokenTracker (per-job aggregate)                    │
│  ��─► total_cost_usd, per-agent breakdown                    │
│  ──► cost_ceiling check ($0.50 max per job)                  │
└──────────────────────────────────────────────────────────────┘
```

---

## 7. Caching Strategy

```
┌──────────────────────────────────────────────────────────────┐
│                Redis LLM Cache                               │
│                                                              │
│  Key: sha256(llm_string + prompt)[:16]                      │
│  TTL: 7 days                                                 │
│  Scope: identical prompts across different jobs              │
│                                                              │
│  Cache hit: ──► Return cached Generation (no API call)       │
│  Cache miss: ──► Call Claude API ──► Store in cache          │
│                                                              │
│  Impact: Repeated topics (e.g., "binary search" from         │
│  different users) reuse planning agent outputs,              │
│  saving ~70% of token cost for identical prompts.            │
└──────────────────────────────────────────────────────────────┘
```

---

## 8. Error Propagation

```
API Error (RateLimit, Timeout, Connection)
    │
    ▼
execute_with_retry (max 3, exponential backoff)
    │
    ├── Success ──► Continue pipeline
    │
    └── All retries failed ──► PipelineError
            │
            ▼
        Log to agent_execution_logs table
            │
            ▼
        Mark job as failed
            │
            ▼
        Sentry alert (if error spike)
```

Validation Error (malformed LLM output):
```
LLM Output ──► PydanticParser
    │
    ├── Success ──► Continue
    │
    └── Parse Error ──► RetryChain
            │
            ├── Inject error context into next prompt
            ├── Re-invoke LLM (max 3 attempts)
            │
            └── All failed ──► PipelineError
```

---

## 9. Agent → Chain → Tool Mapping

| Agent | Chain Pattern | Tools | Memory | LLM Temp |
|-------|--------------|-------|--------|----------|
| A02 Audience | SimpleChain | — | — | 0.3 |
| A03 Curriculum | SimpleChain | — | EntityTracker(write) | 0.3 |
| A04 Misconception | SequentialChain | — | — | 0.3 |
| A05 Objectives | SimpleChain | — | — | 0.3 |
| A06 Script | CreativeChain | — | EntityTracker(read), BufferMemory | 0.7 |
| A07 Pacing | SimpleChain | — | — | 0.3 |
| A08 Hook | CreativeChain | — | — | 0.7 |
| A09 Quiz | SimpleChain | — | — | 0.3 |
| A10 SceneDir | SimpleChain | — | EntityTracker(read), PgMemory(read) | 0.3 |
| A11 Metaphor | SimpleChain | — | EntityTracker(read/write), PgMemory(read) | 0.3 |
| A12 Assets | ToolCallingChain | UnsplashSearch | — | 0.3 |
| A13 Typography | SimpleChain | — | — | 0.3 |
| A14 Accessibility | (Python code, no LLM) | — | — | — |
| A15 Remotion | RetryChain | — | — | 0.0 |
| A16 Manim | RetryChain | ManimRender(validate) | PgMemory(read) | 0.0 |
| A17 D3 | RetryChain | — | — | 0.0 |
| A18 ThreeJS | RetryChain | — | — | 0.0 |
| A19 Timing | (Python code, no LLM) | — | — | — |
| A20 Caption | (Python code, no LLM) | — | — | — |
| A21 TTS | ToolCallingChain | ElevenLabsTTS | — | 0.3 |
| A22 Music | ToolCallingChain | PixabayMusic | — | 0.3 |
| A23 Sound | (Rule-based, no LLM) | — | — | — |
| A24 Mix | (FFmpeg subprocess) | — | — | — |
| A25-A28 QA | (Python validators, no LLM except A28) | — | — | 0.3 |
| A29 Render | (Node.js subprocess) | — | — | — |
| A30 FFmpeg | (FFmpeg subprocess) | — | — | — |
| A31 Evaluate | SimpleChain | — | — | 0.3 |
| A32 Memory | (DB write, no LLM) | PgMemory(write) | — | — |

14 agents use LLM chains. 6 are pure Python/Node.js/FFmpeg subprocesses. 13 use LLM with specific chain patterns.
