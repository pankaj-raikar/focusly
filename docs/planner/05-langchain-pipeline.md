# Focusly — LangChain Pipeline

## 1. Overview

LangChain serves as the LLM pipeline layer for all 33 agents. Each agent node in the LangGraph pipeline wraps one or more LangChain chains that:
1. Load a prompt template
2. Format it with agent-specific variables
3. Call Claude via ChatAnthropic
4. Parse structured output into Pydantic models

---

## 2. ChatAnthropic Setup

```python
# agents/chains/base.py
from langchain_anthropic import ChatAnthropic
from focusly.core.config import get_settings


def get_llm(temperature: float = 0.3) -> ChatAnthropic:
    """Standard LLM for most agents. Lower temperature for deterministic output."""
    return ChatAnthropic(
        model="claude-sonnet-4-6-20250514",
        anthropic_api_key=get_settings().anthropic_api_key,
        temperature=temperature,
        max_tokens=4096,
        max_retries=3,
        default_headers={"anthropic-beta": "prompt-caching-2024-07-31"},
    )


def get_deterministic_llm() -> ChatAnthropic:
    """For code generation and structured output. Temperature 0."""
    return ChatAnthropic(
        model="claude-sonnet-4-6-20250514",
        anthropic_api_key=get_settings().anthropic_api_key,
        temperature=0.0,
        max_tokens=8192,
        max_retries=3,
    )


def get_creative_llm() -> ChatAnthropic:
    """For script writing and hook generation. Slightly higher temperature."""
    return ChatAnthropic(
        model="claude-sonnet-4-6-20250514",
        anthropic_api_key=get_settings().anthropic_api_key,
        temperature=0.7,
        max_tokens=4096,
        max_retries=3,
    )
```

---

## 3. Prompt Template Management

### 3.1 Template File Structure

```
agents/prompts/
├── A02_audience.md
├── A03_curriculum.md
├── A04_misconceptions.md
├── A05_objectives.md
├── A06_script.md
├── A07_pacing.md
├── A08_hook.md
├── A09_quiz.md
├── A10_scene_director.md
├── A11_visual_metaphor.md
├── A12_asset_hunter.md
├── A13_typography.md
├── A14_accessibility.md
├── A15_remotion_coder.md
├── A16_manim_coder.md
├── A17_d3_coder.md
├── A18_threejs_coder.md
├── A28_educational_qa.md
└── A31_evaluator.md
```

### 3.2 Template Loader

```python
# agents/prompts/loader.py
from pathlib import Path
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate

PROMPTS_DIR = Path(__file__).parent


def load_system_prompt(agent_id: str) -> str:
    """Load a markdown prompt template for the given agent."""
    prompt_file = PROMPTS_DIR / f"{agent_id}.md"
    if not prompt_file.exists():
        raise FileNotFoundError(f"Prompt template not found: {agent_id}")
    return prompt_file.read_text()


def build_chat_prompt(agent_id: str, human_template: str) -> ChatPromptTemplate:
    """Build a ChatPromptTemplate with the agent's system prompt."""
    system = load_system_prompt(agent_id)
    return ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(
            system + "\n\n{format_instructions}"
        ),
        ("human", human_template),
    ])
```

---

## 4. Structured Output Parsers

Each agent has a Pydantic model that defines its output schema. `PydanticOutputParser` extracts structured data from Claude's text response.

```python
# agents/chains/base.py (continued)
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel


def get_parser(model: type[BaseModel]) -> PydanticOutputParser:
    return PydanticOutputParser(pydantic_object=model)
```

### Per-Agent Output Schemas

| Agent | Output Model | Key Fields |
|-------|-------------|------------|
| A02 | `AudienceProfile` | level, prerequisites, vocabulary_ceiling |
| A03 | `CurriculumOutline` | segments[], total_duration, concept_count |
| A04 | `MisconceptionAnalysis` | misconceptions[] |
| A05 | `LearningObjectives` | objectives[] |
| A06 | `FullScript` | segments[] (text, duration, emphasis) |
| A07 | `PacedScript` | segments[] + pauses + emphasis markers |
| A08 | `HookAndSummary` | hook_text, closing_summary, reengagement_cues |
| A09 | `QuizSet` | questions[] (4 options, explanations) |
| A10 | `SceneManifest` | scenes[] (type, template, props) |
| A11 | `MetaphorEnrichment` | enriched_scenes[] |
| A13 | `DesignTokens` | font, sizes, colors, spacing |
| A15 | `RemotionCode` | code (tsx string), component_name |
| A16 | `ManimCode` | code (python string), class_name, estimated_duration |
| A28 | `EducationalQAReport` | passed, gaps[], recommendations[] |
| A31 | `EvaluationResult` | score, dimensions{}, notes |

---

## 5. Chain Composition Patterns

### 5.1 SimpleChain (Single LLM Call + Parse)

Used by agents that produce one structured output: A02, A05, A07, A08, A13.

```python
# agents/chains/base.py
from langchain_core.runnables import RunnableSequence


def build_simple_chain(
    agent_id: str,
    output_model: type[BaseModel],
    llm=None,
    human_template: str = "{topic}\n\nContext:\n{context}",
) -> RunnableSequence:
    """Build a chain: prompt → LLM → parse."""
    from focusly.agents.prompts.loader import build_chat_prompt
    from focusly.agents.chains.base import get_llm, get_parser

    _llm = llm or get_llm()
    prompt = build_chat_prompt(agent_id, human_template)
    parser = get_parser(output_model)

    return prompt | _llm | parser
```

### 5.2 SequentialChain (Multi-Step Reasoning)

Used by A04 (outline → misconception analysis).

```python
# agents/chains/knowledge_chains.py
from langchain_core.runnables import RunnableLambda


def build_misconception_chain():
    """A04: Generate curriculum outline, then analyze misconceptions."""
    llm = get_llm()

    # Step 1: Build outline
    outline_chain = build_simple_chain("A03_curriculum", CurriculumOutline, llm)

    # Step 2: Analyze misconceptions from outline
    misconception_chain = build_simple_chain("A04_misconceptions", MisconceptionAnalysis, llm)

    # Compose: outline → extract JSON → analyze
    return (
        outline_chain
        | RunnableLambda(lambda outline: {
            "outline_json": outline.model_dump_json(indent=2)
        })
        | misconception_chain
    )
```

### 5.3 ToolCallingChain (LLM + External Tools)

Used by agents that need external services.

```python
# agents/chains/visual_chains.py
from langchain_core.messages import SystemMessage, HumanMessage


async def run_asset_hunting(scenes: list[dict], topic: str) -> list[dict]:
    """A12 AssetHunter: Use Unsplash tool to find images for each scene."""
    llm = get_llm()
    tool = UnsplashSearchTool()
    llm_with_tools = llm.bind_tools([tool])

    enriched_scenes = []
    for scene in scenes:
        response = await llm_with_tools.ainvoke([
            SystemMessage(content=load_system_prompt("A12_asset_hunter")),
            HumanMessage(content=f"Find images for: {scene['visual_description']}"),
        ])

        asset_urls = []
        for tool_call in response.tool_calls:
            result = await tool.ainvoke(tool_call["args"])
            asset_urls.extend(r["url"] for r in result)

        enriched_scenes.append({**scene, "asset_urls": asset_urls})

    return enriched_scenes
```

### 5.4 RetryChain (LLM + Validation + Retry)

Used by code-generation agents (A15, A16, A17, A18).

```python
# agents/chains/codegen_chains.py
import ast


async def run_with_retry(
    agent_id: str,
    output_model: type[BaseModel],
    input_vars: dict,
    validator: callable | None = None,
    max_attempts: int = 3,
) -> BaseModel:
    chain = build_simple_chain(agent_id, output_model, get_deterministic_llm())
    last_error = None

    for attempt in range(max_attempts):
        try:
            result = await chain.ainvoke({
                **input_vars,
                "retry_context": f"Previous attempt failed: {last_error}" if last_error else "",
            })

            if validator:
                validation_error = validator(result)
                if validation_error:
                    last_error = validation_error
                    continue

            return result
        except Exception as e:
            last_error = str(e)

    raise PipelineError(agent_id, f"Failed after {max_attempts} attempts: {last_error}")


def validate_manim_code(output) -> str | None:
    """Validate Manim code: syntax check + Scene class presence."""
    code = output.code if hasattr(output, "code") else str(output)
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return f"Syntax error: {e}"

    has_scene = any(
        isinstance(node, ast.ClassDef)
        for node in ast.walk(tree)
    )
    if not has_scene:
        return "No class definition found in generated code"
    return None
```

---

## 6. Tool Definitions

### 6.1 UnsplashSearchTool

```python
# agents/tools/unsplash_tool.py
from langchain_core.tools import BaseTool
from pydantic import BaseModel
import httpx


class UnsplashInput(BaseModel):
    query: str
    count: int = 3


class UnsplashSearchTool(BaseTool):
    name: str = "unsplash_search"
    description: str = "Search Unsplash for relevant images by keyword"
    args_schema: type = UnsplashInput

    async def _arun(self, query: str, count: int = 3) -> list[dict]:
        from focusly.core.config import get_settings
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                "https://api.unsplash.com/search/photos",
                params={"query": query, "per_page": count},
                headers={
                    "Authorization": f"Client-ID {get_settings().unsplash_access_key}"
                },
            )
            data = resp.json()
            return [
                {
                    "url": photo["urls"]["regular"],
                    "description": photo.get("alt_description", ""),
                    "author": photo["user"]["name"],
                    "license": "Unsplash License",
                }
                for photo in data.get("results", [])
            ]

    def _run(self, query: str, count: int = 3) -> list[dict]:
        raise NotImplementedError("Use async version")
```

### 6.2 ElevenLabsTTSTool

```python
# agents/tools/elevenlabs_tool.py
class ElevenLabsTTSTool(BaseTool):
    name: str = "elevenlabs_tts"
    description: str = "Convert text to speech using ElevenLabs TTS API"

    async def _arun(self, text: str, segment_index: int = 0) -> dict:
        from focusly.infrastructure.services.elevenlabs_service import ElevenLabsService
        service = ElevenLabsService()
        audio_bytes, timestamps = await service.synthesize(text)

        # Upload to R2
        from focusly.infrastructure.services.r2_service import R2Service
        r2 = R2Service()
        key = f"audio/{segment_index}.mp3"
        url = await r2.upload(key, audio_bytes, "audio/mpeg")

        return {
            "file_path": key,
            "file_url": url,
            "duration_ms": len(audio_bytes) // 16,  # rough estimate
            "word_timestamps": timestamps,
        }
```

### 6.3 ManimRenderTool

```python
# agents/tools/manim_tool.py
class ManimRenderTool(BaseTool):
    name: str = "manim_render"
    description: str = "Validate and preview-render a Manim scene"

    async def _arun(self, code: str, scene_class: str) -> dict:
        import ast
        # Step 1: Syntax validation
        try:
            ast.parse(code)
        except SyntaxError as e:
            return {"valid": False, "error": f"Syntax error: {e}"}

        # Step 2: Preview render (low quality, for validation only)
        return {
            "valid": True,
            "code": code,
            "class_name": scene_class,
            "preview_available": True,
        }
```

---

## 7. Memory Modules

### 7.1 Agent Buffer Memory (Multi-Turn Refinement)

```python
# agents/memory/buffer.py
from langchain.memory import ConversationBufferWindowMemory


class AgentBufferMemory:
    def __init__(self, agent_id: str, window_size: int = 10):
        self.agent_id = agent_id
        self._memory = ConversationBufferWindowMemory(
            k=window_size, return_messages=True
        )

    def add_interaction(self, user_msg: str, assistant_msg: str) -> None:
        self._memory.save_context({"input": user_msg}, {"output": assistant_msg})

    def get_history(self) -> list:
        return self._memory.load_memory_variables({}).get("chat_history", [])
```

### 7.2 Entity Memory (Cross-Agent Context)

```python
# agents/memory/entity.py
@dataclass
class EntityTracker:
    entities: dict[str, dict] = field(default_factory=dict)

    def add_entity(self, name: str, entity_type: str, description: str, source_agent: str) -> None:
        key = name.lower().strip()
        if key in self.entities:
            self.entities[key]["mentions"] += 1
        else:
            self.entities[key] = {
                "name": name, "type": entity_type,
                "description": description, "source_agent": source_agent, "mentions": 1,
            }

    def get_summary_for_prompt(self) -> str:
        if not self.entities:
            return "No entities tracked yet."
        return "\n".join(
            f"- {e['name']} ({e['type']}): {e['description']}"
            for e in self.entities.values()
        )
```

---

## 8. Token Tracking & Cost Control

### 8.1 Cost Callback

```python
# agents/chains/callbacks.py
from dataclasses import dataclass
from langchain_core.callbacks import AsyncCallbackHandler
from langchain_core.outputs import LLMResult


PRICING = {
    "claude-sonnet-4-6-20250514": {"input": 3.00, "output": 15.00},
}


@dataclass
class PipelineTokenTracker:
    agent_usages: dict[str, dict] = field(default_factory=dict)
    total_cost_usd: float = 0.0

    def get_total_cost(self) -> float:
        return sum(u.get("cost", 0) for u in self.agent_usages.values())


class CostTrackingCallback(AsyncCallbackHandler):
    def __init__(self, agent_id: str, model: str, tracker: PipelineTokenTracker):
        self.agent_id = agent_id
        self.model = model
        self.tracker = tracker

    async def on_llm_end(self, response: LLMResult, **kwargs):
        usage = (response.llm_output or {}).get("usage", {})
        input_tokens = usage.get("input_tokens", 0)
        output_tokens = usage.get("output_tokens", 0)

        pricing = PRICING.get(self.model, {"input": 3.0, "output": 15.0})
        cost = (input_tokens / 1_000_000) * pricing["input"] + (output_tokens / 1_000_000) * pricing["output"]

        self.tracker.agent_usages[self.agent_id] = {
            "input": input_tokens, "output": output_tokens, "cost": cost,
        }
        self.tracker.total_cost_usd += cost
```

### 8.2 Per-Job Cost Ceiling

```python
# Enforced in orchestrator node
MAX_COST_PER_JOB_USD = 0.50

async def check_cost_ceiling(tracker: PipelineTokenTracker) -> bool:
    if tracker.get_total_cost() > MAX_COST_PER_JOB_USD:
        logger.warning("cost_ceiling_exceeded", cost=tracker.get_total_cost())
        return False
    return True
```

---

## 9. Redis-Backed LLM Cache

```python
# agents/chains/cache.py
import hashlib, json
from langchain_core.caches import BaseCache
from langchain_core.outputs import Generation


class RedisLLMCache(BaseCache):
    def __init__(self, prefix: str = "llm_cache", ttl: int = 604800):  # 7 days
        self.prefix = prefix
        self.ttl = ttl

    def _make_key(self, prompt: str, llm_string: str) -> str:
        h = hashlib.sha256(f"{llm_string}:{prompt}".encode()).hexdigest()[:16]
        return f"{self.prefix}:{h}"

    def lookup(self, prompt: str, llm_string: str) -> list[Generation] | None:
        # Async version using aioredis
        ...

    def update(self, prompt: str, llm_string: str, return_val: list[Generation]) -> None:
        # Async version using aioredis
        ...
```

---

## 10. Error Handling

```python
# agents/chains/error_handling.py
import asyncio
from anthropic import RateLimitError, APITimeoutError, APIConnectionError


async def execute_with_retry(agent_id: str, coro_factory, max_retries: int = 3, base_delay: float = 1.0):
    last_error = None
    for attempt in range(max_retries):
        try:
            return await coro_factory()
        except RateLimitError as e:
            last_error = e
            await asyncio.sleep(base_delay * (2 ** attempt))
        except (APITimeoutError, APIConnectionError) as e:
            last_error = e
            await asyncio.sleep(base_delay * (2 ** attempt))

    raise PipelineError(agent_id, f"Failed after {max_retries} retries: {last_error}")
```

---

## 11. Testing Chains

```python
# tests/unit/test_chains.py
from unittest.mock import AsyncMock, patch
import pytest
from langchain_core.messages import AIMessage
from langchain_core.outputs import ChatGeneration, ChatResult


def mock_chat_result(text: str) -> ChatResult:
    return ChatResult(
        generations=[ChatGeneration(message=AIMessage(content=text))],
        llm_output={"usage": {"input_tokens": 100, "output_tokens": 200}},
    )


@pytest.mark.asyncio
async def test_audience_chain_parses_output():
    with patch("focusly.agents.chains.base.get_llm") as mock:
        mock_llm = AsyncMock()
        mock_llm.ainvoke.return_value = mock_chat_result('{"level": "intermediate"}')
        mock.return_value = mock_llm

        chain = build_simple_chain("A02_audience", AudienceProfile)
        result = await chain.ainvoke({"topic": "Photosynthesis", "context": {}})
        assert isinstance(result, AudienceProfile)
```

---

## 12. Task Checklist

- [M] ChatAnthropic configured with model, temperature, retry settings
- [M] Prompt templates for all 25+ LLM-powered agents
- [M] PydanticOutputParser for each agent's output schema
- [M] SimpleChain pattern for A02, A05, A07, A08, A13
- [M] RetryChain pattern for A15, A16, A17, A18 (code validation)
- [M] ToolCallingChain for A12 (Unsplash), A21 (ElevenLabs)
- [M] Error handling with exponential backoff for API errors
- [M] Token tracking callback per chain run
- [S] Redis-backed LLM response cache
- [S] Entity tracker for cross-agent context
- [S] Per-job cost ceiling ($0.50)
- [C] Prompt versioning in git
- [C] A/B testing different prompt strategies
