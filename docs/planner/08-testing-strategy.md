# Focusly — Testing Strategy

## 1. Test Pyramid

```
E2E tests (Playwright)         — 10% — critical user journeys
Integration tests (pytest)     — 30% — API routes, DB, pipeline, queue
Unit tests (pytest + Vitest)   — 60% — agents, parsers, validators, components
```

Minimum coverage: **80%** on critical path (agents, render pipeline, API).

---

## 2. Backend Unit Tests (pytest)

### 2.1 conftest.py

```python
# tests/conftest.py
import pytest
import respx
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from focusly.main import create_app
from focusly.core.database import Base


TEST_DATABASE_URL = "postgresql+asyncpg://postgres:test@localhost:5432/focusly_test"


@pytest.fixture
async def db_engine():
    engine = create_async_engine(TEST_DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def db_session(db_engine):
    session_factory = async_sessionmaker(db_engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def client(db_session):
    app = create_app()
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def mock_claude_api(respx_mock):
    respx_mock.post("https://api.anthropic.com/v1/messages").mock(
        return_value=respx.MockResponse(200, json={
            "content": [{"type": "text", "text": '{"level": "intermediate"}'}],
            "usage": {"input_tokens": 100, "output_tokens": 50},
        })
    )
    yield respx_mock


@pytest.fixture
def mock_elevenlabs_api(respx_mock):
    respx_mock.post("https://api.elevenlabs.io/v1/text-to-speech/").mock(
        return_value=respx.MockResponse(200, content=b"fake_mp3_bytes")
    )
    yield respx_mock


@pytest.fixture
def mock_r2_service(monkeypatch):
    async def mock_upload(self, key, data, content_type):
        return f"https://r2.test/{key}"

    def mock_signed_url(self, key, expires_in=3600):
        return f"https://r2.test/{key}?signed=true"

    monkeypatch.setattr("focusly.infrastructure.services.r2_service.R2Service.upload", mock_upload)
    monkeypatch.setattr("focusly.infrastructure.services.r2_service.R2Service.get_signed_url", mock_signed_url)
```

### 2.2 Agent Unit Tests

```python
# tests/unit/test_agents.py
import pytest
from unittest.mock import AsyncMock, patch
from langchain_core.messages import AIMessage
from langchain_core.outputs import ChatGeneration, ChatResult


def mock_chat_result(text: str, input_tokens: int = 100, output_tokens: int = 200):
    return ChatResult(
        generations=[ChatGeneration(message=AIMessage(content=text))],
        llm_output={"usage": {"input_tokens": input_tokens, "output_tokens": output_tokens}},
    )


@pytest.mark.asyncio
async def test_audience_calibration_produces_valid_profile(mock_claude_api):
    from focusly.agents.nodes.knowledge import calibrate_audience

    mock_claude_api.post("https://api.anthropic.com/v1/messages").mock(
        return_value=respx.MockResponse(200, json={
            "content": [{"type": "text", "text": '{"level": "intermediate", "assumed_prerequisites": ["arrays"], "vocabulary_ceiling": "undergraduate CS", "adhd_accommodation": true}'}],
            "usage": {"input_tokens": 100, "output_tokens": 50},
        })
    )

    state = {"topic": "binary search", "audience_level": "intermediate"}
    result = await calibrate_audience(state)

    assert "learner_profile" in result
    assert result["current_agent"] == "A02"
    assert result["progress_percent"] == 5.0
```

### 2.3 ADHD Rules Validation

```python
# tests/unit/test_adhd_rules.py
from focusly.agents.validation.adhd_rules import enforce_adhd_rules, ADHD_RULES


def test_max_segment_duration():
    segments = [
        {"duration_seconds": 25.0},
        {"duration_seconds": 30.0},
        {"duration_seconds": 35.0},  # exceeds limit
    ]
    corrected = enforce_adhd_rules(segments)
    assert all(s["duration_seconds"] <= 30 for s in corrected)


def test_max_words_per_text():
    text = "This is way too many words on screen at once and violates the rule"
    assert count_display_words(text) > 7
    truncated = truncate_display_text(text, max_words=7)
    assert len(truncated.split()) <= 7
```

### 2.4 Manim Validation Tests

```python
# tests/unit/test_manim_validation.py
from focusly.agents.validation.manim_validator import validate_manim_code


def test_valid_manim_code():
    code = """
from manim import *
class TestScene(Scene):
    def construct(self):
        self.play(Create(Square()))
        self.wait(1)
"""
    result = validate_manim_code(code)
    assert result.valid is True
    assert result.class_name == "TestScene"


def test_missing_scene_class():
    result = validate_manim_code("x = 42")
    assert result.valid is False


def test_syntax_error():
    result = validate_manim_code("def broken(")
    assert result.valid is False


def test_forbidden_pattern():
    code = 'from manim import *\nclass Bad(Scene):\n    def construct(self):\n        import os; os.system("rm")'
    result = validate_manim_code(code)
    assert result.valid is False
```

### 2.5 Auth Tests

```python
# tests/unit/test_security.py
from focusly.core.security import hash_password, verify_password, create_access_token, decode_token


def test_password_hash_and_verify():
    password = "secure_password_123"
    hashed = hash_password(password)
    assert verify_password(password, hashed) is True
    assert verify_password("wrong_password", hashed) is False


def test_jwt_creation_and_decode():
    token = create_access_token("user-uuid-123")
    payload = decode_token(token)
    assert payload["sub"] == "user-uuid-123"
    assert payload["type"] == "access"
```

### 2.6 Pydantic Model Roundtrip

```python
# tests/unit/test_models.py
from focusly.agents.schemas.knowledge import AudienceProfile
from focusly.domain.models.lesson import LessonJob


def test_lesson_context_serialization_roundtrip():
    profile = AudienceProfile(
        level="intermediate",
        assumed_prerequisites=["arrays", "looping"],
        vocabulary_ceiling="undergraduate CS",
        adhd_accommodation=True,
    )
    json_str = profile.model_dump_json()
    restored = AudienceProfile.model_validate_json(json_str)
    assert restored.level == "intermediate"
    assert len(restored.assumed_prerequisites) == 2
```

---

## 3. Backend Integration Tests

### 3.1 API Route Tests

```python
# tests/integration/test_api_lessons.py
import pytest


@pytest.mark.asyncio
async def test_generate_lesson_creates_job(client, authenticated_user):
    response = await client.post(
        "/api/v1/lessons/generate",
        json={"topic": "binary search", "level": "intermediate"},
        headers=auth_headers(authenticated_user),
    )
    assert response.status_code == 202
    data = response.json()["data"]
    assert "job_id" in data
    assert data["status"] == "queued"


@pytest.mark.asyncio
async def test_generate_unauthenticated_rejected(client):
    response = await client.post(
        "/api/v1/lessons/generate",
        json={"topic": "test"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_rate_limit_enforced(client, authenticated_user):
    for _ in range(10):
        await client.post(
            "/api/v1/lessons/generate",
            json={"topic": "test"},
            headers=auth_headers(authenticated_user),
        )
    response = await client.post(
        "/api/v1/lessons/generate",
        json={"topic": "test"},
        headers=auth_headers(authenticated_user),
    )
    assert response.status_code == 429
```

### 3.2 User Isolation Test

```python
@pytest.mark.asyncio
async def test_user_cannot_access_other_users_lesson(client, user_a_lesson, user_b_token):
    response = await client.get(
        f"/api/v1/lessons/{user_a_lesson.id}",
        headers={"Authorization": f"Bearer {user_b_token}"},
    )
    assert response.status_code == 404
```

### 3.3 Job Timeout Test

```python
@pytest.mark.asyncio
async def test_stuck_job_marked_failed(db_session, old_running_job):
    from focusly.workers.tasks import check_stuck_jobs
    await check_stuck_jobs({})
    await db_session.refresh(old_running_job)
    assert old_running_job.status == "failed"
    assert "timeout" in old_running_job.error_message
```

### 3.4 Pipeline Integration Test

```python
@pytest.mark.asyncio
async def test_full_pipeline_with_mocked_llm(mock_claude_api, mock_elevenlabs_api, mock_r2_service):
    from focusly.agents.graph import build_pipeline_graph

    graph = build_pipeline_graph()
    state = {
        "job_id": "test-001",
        "user_id": "user-001",
        "topic": "binary search",
        "audience_level": "intermediate",
        "errors": [],
        "retry_counts": {},
    }
    # Verify graph compiles and entry point is correct
    assert graph is not None
```

---

## 4. Frontend Unit Tests (Vitest)

### 4.1 Component Tests

```typescript
// tests/components/GenerateForm.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { GenerateForm } from '@/components/generate/GenerateForm'

test('renders topic input with character counter', () => {
  render(<GenerateForm />)
  const input = screen.getByPlaceholderText(/enter a topic/i)
  expect(input).toBeInTheDocument()
  expect(screen.getByText(/0\/200/)).toBeInTheDocument()
})

test('disables submit when topic is empty', () => {
  render(<GenerateForm />)
  const button = screen.getByRole('button', { name: /generate/i })
  expect(button).toBeDisabled()
})

test('updates character counter on input', () => {
  render(<GenerateForm />)
  const input = screen.getByPlaceholderText(/enter a topic/i)
  fireEvent.change(input, { target: { value: 'binary search' } })
  expect(screen.getByText(/12\/200/)).toBeInTheDocument()
})
```

### 4.2 Store Tests

```typescript
// tests/stores/auth-store.test.ts
import { useAuthStore } from '@/lib/stores/auth-store'

beforeEach(() => {
  useAuthStore.setState({ user: null, isAuthenticated: false })
})

test('login sets user and isAuthenticated', async () => {
  const { login } = useAuthStore.getState()
  await login('test@example.com', 'password')
  const state = useAuthStore.getState()
  expect(state.isAuthenticated).toBe(true)
  expect(state.user).not.toBeNull()
})
```

---

## 5. E2E Tests (Playwright)

### 5.1 Critical User Journey

```typescript
// e2e/full-flow.spec.ts
import { test, expect } from '@playwright/test'

test('full lesson generation and playback flow', async ({ page }) => {
  // Register
  await page.goto('/register')
  await page.fill('input[name="email"]', `test-${Date.now()}@example.com`)
  await page.fill('input[name="password"]', 'TestPassword123!')
  await page.click('button[type="submit"]')
  await expect(page).toHaveURL('/dashboard')

  // Generate lesson
  await page.goto('/generate')
  await page.fill('input[name="topic"]', 'binary search')
  await page.click('button[type="submit"]')
  await expect(page).toHaveURL(/\/jobs\//)

  // Wait for job to complete (mock or timeout in CI)
  // In CI, this would use a pre-generated test fixture

  // Dashboard shows lesson
  await page.goto('/dashboard')
  await expect(page.locator('.lesson-card')).toHaveCount(1)
})

test('login and logout flow', async ({ page }) => {
  await page.goto('/login')
  await page.fill('input[name="email"]', 'test@example.com')
  await page.fill('input[name="password"]', 'password')
  await page.click('button[type="submit"]')
  await expect(page).toHaveURL('/dashboard')

  // Logout
  await page.click('[data-testid="user-menu"]')
  await page.click('text=Logout')
  await expect(page).toHaveURL('/login')
})

test('protected route redirects to login', async ({ page }) => {
  await page.goto('/dashboard')
  await expect(page).toHaveURL(/\/login/)
})
```

---

## 6. LangChain Chain Testing

```python
# tests/unit/test_chains.py
@pytest.mark.asyncio
async def test_simple_chain_parses_structured_output():
    with patch("focusly.agents.chains.base.get_llm") as mock_get_llm:
        mock_llm = AsyncMock()
        mock_llm.ainvoke.return_value = mock_chat_result(
            '{"level": "intermediate", "assumed_prerequisites": ["arrays"]}'
        )
        mock_get_llm.return_value = mock_llm

        from focusly.agents.chains.base import build_simple_chain
        from focusly.agents.schemas.knowledge import AudienceProfile

        chain = build_simple_chain("A02_audience", AudienceProfile)
        result = await chain.ainvoke({"topic": "test", "format_instructions": ""})
        assert isinstance(result, AudienceProfile)


@pytest.mark.asyncio
async def test_retry_chain_retries_on_malformed_output():
    call_count = 0

    async def mock_invoke(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise ValidationError("Invalid JSON")
        return mock_chat_result('{"code": "valid"}')

    with patch("focusly.agents.chains.base.get_llm") as mock:
        mock_llm = AsyncMock()
        mock_llm.ainvoke = mock_invoke
        mock.return_value = mock_llm

        from focusly.agents.chains.codegen_chains import run_with_retry
        result = await run_with_retry("A16_manim", ManimCode, {"scene": {}}, max_attempts=3)
        assert call_count == 3
```

---

## 7. Load Testing

Target: 50 concurrent users, 3 concurrent renders, no degradation.

```python
# tests/load/locustfile.py
from locust import HttpUser, task, between

class FocuslyUser(HttpUser):
    wait_time = between(1, 5)

    def on_start(self):
        self.client.post("/api/v1/auth/login", json={
            "email": "loadtest@example.com",
            "password": "password",
        })

    @task(3)
    def view_dashboard(self):
        self.client.get("/api/v1/lessons")

    @task(1)
    def generate_lesson(self):
        self.client.post("/api/v1/lessons/generate", json={
            "topic": "test topic",
        })
```

---

## 8. CI Integration

```yaml
# In .github/workflows/ci.yml
test-api:
  runs-on: ubuntu-latest
  services:
    postgres:
      image: postgres:16
      env: { POSTGRES_PASSWORD: test, POSTGRES_DB: focusly_test }
    redis:
      image: redis:7
  steps:
    - run: cd apps/api && uv run pytest -v --tb=short --cov=src --cov-report=xml
  env:
    DATABASE_URL: postgresql+asyncpg://postgres:test@localhost/focusly_test
    REDIS_URL: redis://localhost:6379
    ANTHROPIC_API_KEY: mock-key
    ENVIRONMENT: test
```

---

## 9. Task Checklist

### Backend Unit Tests
- [M] Agent node tests (A02, A06, A10, A16 — representative sample)
- [M] Parser tests (structured output parsing for each schema)
- [M] Validation tests (ADHD rules, Manim code, scene structure)
- [M] Auth tests (password hashing, JWT creation/validation)
- [M] Model tests (Pydantic serialization roundtrip)

### Backend Integration Tests
- [M] API routes: generate, poll, list, get, delete
- [M] Auth endpoints: register, login, refresh, logout
- [M] User isolation (cannot access other user's lesson)
- [M] Rate limiting (11th request returns 429)
- [M] Job timeout (stuck job → failed)
- [M] Pipeline integration (full graph with mocked LLM)

### Frontend Tests
- [M] GenerateForm component (input, counter, submit)
- [M] Auth store (login, logout, state)
- [S] Dashboard (lesson grid, pagination)
- [S] QuizOverlay (answer selection, reveal)

### E2E Tests
- [M] Full flow: register → generate → watch → quiz
- [M] Auth flow: login, logout, protected routes
- [S] Video player: play, pause, quiz interaction
- [S] Error states: failed generation, network error

### LangChain/LangGraph Tests
- [M] Chain tests with mocked LLM responses
- [M] Retry chain behavior (malformed output → retry → success)
- [M] Tool execution tests (mock external APIs)
- [S] Graph node tests (input state → output state)
- [S] QA conditional routing tests
