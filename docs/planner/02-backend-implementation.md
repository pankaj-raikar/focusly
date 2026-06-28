# Focusly — Backend Implementation Plan

## 1. Application Structure

```
apps/api/src/focusly/
├── __init__.py
├── main.py                    # FastAPI app factory, lifespan, middleware
├── core/
│   ├── config.py              # Pydantic Settings (all env vars)
│   ├── database.py            # Async SQLAlchemy engine + session factory
│   ├── redis.py               # Redis connection pool + helpers
│   ├── security.py            # JWT RS256, bcrypt, token creation/validation
│   ├── exceptions.py          # Custom exception hierarchy
│   └── logging.py             # Structlog JSON config
├── api/
│   ├── v1/
│   │   ├── auth.py            # Register, login, refresh, logout, verify
│   │   ├── lessons.py         # Generate, poll, list, get, delete
│   │   ├── watch.py           # Start, progress, complete
│   │   ├── quiz.py            # Attempt, results
│   │   └── admin.py           # Queue, stuck, retry, metrics
│   ├── deps.py                # get_db, get_current_user, get_redis
│   └── middleware.py          # CORS, request ID, logging, rate limit
├── domain/
│   ├── models/
│   │   ├── user.py            # User, RefreshToken
│   │   ├── lesson.py          # LessonJob, Lesson
│   │   ├── watch.py           # WatchSession
│   │   ├── quiz.py            # QuizAttempt
│   │   ├── agent_memory.py    # AgentMemory
│   │   └── langgraph.py       # LangGraphCheckpoint, AgentExecutionLog, ChainRun
│   ├── schemas/
│   │   ├── auth.py            # RegisterRequest, LoginRequest, TokenResponse
│   │   ├── lesson.py          # GenerateRequest, JobStatus, LessonResponse
│   │   ├── quiz.py            # QuizAttemptRequest, QuizResult
│   │   └── common.py          # ApiResponse, PaginatedResponse, ErrorResponse
│   └── enums.py               # JobStatus, AgentStatus, SceneType, MemoryType
├── infrastructure/
│   ├── repositories/
│   │   ├── user_repo.py
│   │   ├── lesson_repo.py
│   │   └── memory_repo.py
│   ├── services/
│   │   ├── claude_service.py  # Direct Claude API (non-LangChain fallback)
│   │   ├── elevenlabs_service.py
│   │   └── r2_service.py      # Cloudflare R2 client
│   └── storage.py             # S3/R2 generic client wrapper
├── agents/                    # See 06-langgraph-agents.md
│   ├── graph.py
│   ├── state.py
│   ├── nodes/
│   ├── chains/
│   ├── tools/
│   ├── prompts/
│   ├── memory/
│   └── schemas/
└── workers/
    ├── main.py                # ARQ WorkerSettings
    └── tasks.py               # generate_lesson_task, retry_job_task
```

---

## 2. Core Modules

### 2.1 Configuration (core/config.py)

```python
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # App
    environment: str = "development"
    debug: bool = False
    cors_origins: str = "http://localhost:3000"

    # Database
    database_url: str = "postgresql+asyncpg://focusly:devpassword@localhost:5432/focusly_dev"

    # Redis
    redis_url: str = "redis://localhost:6379"

    # Security
    secret_key: str = ""  # RS256 private key
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7
    bcrypt_cost: int = 12

    # External APIs
    anthropic_api_key: str = ""
    elevenlabs_api_key: str = ""
    elevenlabs_voice_id: str = ""
    unsplash_access_key: str = ""
    pixabay_api_key: str = ""

    # R2 Storage
    cloudflare_r2_account_id: str = ""
    cloudflare_r2_access_key_id: str = ""
    cloudflare_r2_secret_access_key: str = ""
    cloudflare_r2_bucket_name: str = ""
    cloudflare_r2_public_url: str = ""

    # Rate limiting
    daily_generation_limit: int = 10
    concurrent_render_limit: int = 3

    # Sentry
    sentry_dsn: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache
def get_settings() -> Settings:
    return Settings()
```

### 2.2 Database (core/database.py)

```python
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase
from focusly.core.config import get_settings

engine = create_async_engine(
    get_settings().database_url,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
    echo=get_settings().debug,
)

async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncSession:
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
```

### 2.3 Redis (core/redis.py)

```python
import redis.asyncio as redis
from focusly.core.config import get_settings

_pool: redis.Redis | None = None


async def get_redis() -> redis.Redis:
    global _pool
    if _pool is None:
        _pool = redis.from_url(
            get_settings().redis_url,
            encoding="utf-8",
            decode_responses=True,
        )
    return _pool


async def close_redis() -> None:
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None
```

### 2.4 Security (core/security.py)

```python
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import bcrypt
import jwt
from focusly.core.config import get_settings


def hash_password(password: str) -> str:
    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt(rounds=get_settings().bcrypt_cost),
    ).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


def create_access_token(user_id: str) -> str:
    settings = get_settings()
    payload = {
        "sub": user_id,
        "type": "access",
        "exp": datetime.now(timezone.utc)
        + timedelta(minutes=settings.access_token_expire_minutes),
        "iat": datetime.now(timezone.utc),
        "jti": str(uuid4()),
    }
    return jwt.encode(payload, settings.secret_key, algorithm="RS256")


def create_refresh_token() -> str:
    return str(uuid4())


def decode_token(token: str) -> dict:
    return jwt.decode(
        token,
        get_settings().secret_key,
        algorithms=["RS256"],
    )
```

### 2.5 Exceptions (core/exceptions.py)

```python
from typing import Any


class FocuslyError(Exception):
    code: str = "INTERNAL_ERROR"
    status_code: int = 500

    def __init__(self, message: str, detail: Any = None):
        self.message = message
        self.detail = detail
        super().__init__(message)


class AuthenticationError(FocuslyError):
    code = "AUTHENTICATION_ERROR"
    status_code = 401


class AuthorizationError(FocuslyError):
    code = "AUTHORIZATION_ERROR"
    status_code = 403


class NotFoundError(FocuslyError):
    code = "NOT_FOUND"
    status_code = 404


class ValidationError(FocuslyError):
    code = "VALIDATION_ERROR"
    status_code = 422


class RateLimitError(FocuslyError):
    code = "RATE_LIMIT_EXCEEDED"
    status_code = 429


class PipelineError(FocuslyError):
    code = "PIPELINE_ERROR"
    status_code = 500

    def __init__(self, agent_id: str, message: str):
        self.agent_id = agent_id
        super().__init__(f"[{agent_id}] {message}")


class RenderError(FocuslyError):
    code = "RENDER_ERROR"
    status_code = 500
```

### 2.6 Logging (core/logging.py)

```python
import structlog
import sys
from focusly.core.config import get_settings


def setup_logging() -> None:
    settings = get_settings()

    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
    ]

    if settings.environment == "development":
        processors.append(structlog.dev.ConsoleRenderer())
    else:
        processors.append(structlog.processors.JSONRenderer())

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
        cache_logger_on_first_use=True,
    )
```

---

## 3. API Response Format

```python
# domain/schemas/common.py
from pydantic import BaseModel
from typing import Any, Generic, TypeVar

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    data: T | None = None
    error: ErrorDetail | None = None


class ErrorDetail(BaseModel):
    code: str
    message: str
    detail: Any = None


class PaginatedResponse(BaseModel, Generic[T]):
    data: list[T]
    total: int
    page: int
    limit: int
    error: None = None
```

---

## 4. Auth Module (api/v1/auth.py)

### Endpoints

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| POST | /api/v1/auth/register | Create account | No |
| POST | /api/v1/auth/login | Login, get tokens | No |
| POST | /api/v1/auth/refresh | Refresh access token | No (uses refresh token) |
| POST | /api/v1/auth/logout | Invalidate refresh token | Yes |
| POST | /api/v1/auth/verify-email | Verify email with token | No |
| POST | /api/v1/auth/forgot-password | Request reset email | No |
| POST | /api/v1/auth/reset-password | Reset password with token | No |

### Key implementation details

- Password stored as bcrypt hash (cost factor 12)
- JWT access token: RS256, 15-min expiry, stored in httpOnly cookie
- Refresh token: UUID stored in `refresh_tokens` table, 7-day expiry, httpOnly cookie
- Token refresh: rotate refresh token on each refresh (invalidate old, create new)
- Rate limiting on login: 5 attempts per IP per 15 minutes
- Input validation: email format, password min 8 chars, no empty fields

---

## 5. Lesson Module (api/v1/lessons.py)

### Endpoints

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| POST | /api/v1/lessons/generate | Submit generation job | Yes |
| GET | /api/v1/lessons/jobs/:job_id | Poll job status | Yes |
| GET | /api/v1/lessons | List user's lessons (paginated) | Yes |
| GET | /api/v1/lessons/:lesson_id | Get lesson + signed video URL | Yes |
| DELETE | /api/v1/lessons/:lesson_id | Delete lesson + video | Yes |

### Generate flow

1. Validate input (topic 1-200 chars, not harmful)
2. Check rate limit (daily_generation_count < 10)
3. Create LessonJob (status=queued) in PostgreSQL
4. Enqueue ARQ task `generate_lesson_task` with job_id
5. Return job_id immediately (202 Accepted)

### Job status polling

- Returns: status (queued/running/completed/failed), progress_percent, current_agent, error_message
- progress_percent derived from which agents have completed (0-100 scale)

---

## 6. LangGraph + LangChain Integration

See dedicated files:
- `05-langchain-pipeline.md` — LangChain chains, tools, memory, caching
- `06-langgraph-agents.md` — LangGraph StateGraph, nodes, edges, checkpointing

---

## 7. ARQ Worker Configuration

```python
# workers/main.py
from arq import cron
from focusly.workers.tasks import (
    generate_lesson_task,
    check_stuck_jobs,
    cleanup_expired_tokens,
)


class WorkerSettings:
    functions = [generate_lesson_task]
    cron_jobs = [
        cron(check_stuck_jobs, minute={0, 15, 30, 45}),
        cron(cleanup_expired_tokens, hour={3}),
    ]
    max_jobs = 5
    job_timeout = 600  # 10 minutes max per job
    max_tries = 3
    retry_delay = 30  # seconds between retries
    queue_name = "focusly:jobs"
```

```python
# workers/tasks.py
import structlog
from uuid import UUID

from focusly.core.database import async_session
from focusly.agents.graph import build_pipeline_graph, PipelineState
from focusly.domain.models.lesson import LessonJob, Lesson
from focusly.infrastructure.services.r2_service import R2Service

logger = structlog.get_logger("worker")


async def generate_lesson_task(ctx: dict, job_id: str) -> dict:
    """Main ARQ task: runs the full LangGraph pipeline for a lesson."""
    async with async_session() as db:
        # Load job
        job = await db.get(LessonJob, UUID(job_id))
        if job is None:
            return {"status": "error", "message": "Job not found"}

        job.status = "running"
        job.started_at = datetime.now(timezone.utc)
        await db.commit()

        try:
            # Build and run the LangGraph pipeline
            graph = build_pipeline_graph()
            initial_state = PipelineState(
                job_id=str(job.id),
                user_id=str(job.user_id),
                topic=job.topic,
                audience_level=job.context.get("level", "intermediate"),
                context=job.context or {},
                errors=[],
            )

            # Run with checkpointing
            final_state = await graph.ainvoke(
                initial_state,
                config={"configurable": {"thread_id": job_id}},
            )

            # Create Lesson record from completed pipeline
            lesson = Lesson(
                job_id=job.id,
                user_id=job.user_id,
                topic=job.topic,
                video_path=final_state["final_video_path"],
                hls_path=final_state["hls_playlist_path"],
                thumbnail_path=final_state.get("thumbnail_path"),
                duration_seconds=final_state.get("total_duration_seconds"),
                segment_count=len(final_state.get("script_segments", [])),
                eval_score=final_state.get("eval_score"),
            )
            db.add(lesson)

            job.status = "completed"
            job.completed_at = datetime.now(timezone.utc)
            await db.commit()

            return {"status": "completed", "lesson_id": str(lesson.id)}

        except Exception as e:
            job.status = "failed"
            job.error_message = str(e)[:500]
            job.completed_at = datetime.now(timezone.utc)
            await db.commit()
            logger.error("lesson_generation_failed", job_id=job_id, error=str(e))
            raise


async def check_stuck_jobs(ctx: dict) -> None:
    """Detect and fail jobs stuck in 'running' for > 15 minutes."""
    async with async_session() as db:
        cutoff = datetime.now(timezone.utc) - timedelta(minutes=15)
        result = await db.execute(
            select(LessonJob)
            .where(LessonJob.status == "running")
            .where(LessonJob.started_at < cutoff)
        )
        stuck_jobs = result.scalars().all()
        for job in stuck_jobs:
            job.status = "failed"
            job.error_message = "timeout: stuck in running state for > 15 minutes"
            job.completed_at = datetime.now(timezone.utc)
            logger.warning("stuck_job_failed", job_id=str(job.id))
        await db.commit()
```

---

## 8. Manim and Remotion Rendering

See dedicated files:
- `07-manim-pipeline.md` — Manim scene generation, Docker, subprocess execution
- The Remotion rendering is handled by A29 RenderOrchestratorAgent (see LangGraph nodes)

---

## 9. External Service Integrations

### 9.1 Cloudflare R2 (infrastructure/services/r2_service.py)

```python
import boto3
from botocore.config import Config
from focusly.core.config import get_settings


class R2Service:
    def __init__(self):
        settings = get_settings()
        self.client = boto3.client(
            "s3",
            endpoint_url=f"https://{settings.cloudflare_r2_account_id}.r2.cloudflarestorage.com",
            aws_access_key_id=settings.cloudflare_r2_access_key_id,
            aws_secret_access_key=settings.cloudflare_r2_secret_access_key,
            config=Config(signature_version="s3v4"),
        )
        self.bucket = settings.cloudflare_r2_bucket_name
        self.public_url = settings.cloudflare_r2_public_url

    async def upload(self, key: str, data: bytes, content_type: str) -> str:
        self.client.put_object(
            Bucket=self.bucket, Key=key, Body=data, ContentType=content_type
        )
        return f"{self.public_url}/{key}"

    def get_signed_url(self, key: str, expires_in: int = 3600) -> str:
        return self.client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket, "Key": key},
            ExpiresIn=expires_in,
        )

    async def delete(self, key: str) -> None:
        self.client.delete_object(Bucket=self.bucket, Key=key)
```

### 9.2 ElevenLabs TTS

```python
# infrastructure/services/elevenlabs_service.py
import httpx
from focusly.core.config import get_settings


class ElevenLabsService:
    BASE_URL = "https://api.elevenlabs.io/v1"

    def __init__(self):
        settings = get_settings()
        self.api_key = settings.elevenlabs_api_key
        self.voice_id = settings.elevenlabs_voice_id

    async def synthesize(
        self, text: str, ssml: bool = True, output_format: str = "mp3_44100_128"
    ) -> tuple[bytes, list[dict]]:
        """Returns (audio_bytes, word_timestamps)."""
        headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json",
        }
        payload = {
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75,
                "style": 0.3,
                "use_speaker_boost": True,
            },
            "output_format": output_format,
        }

        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                f"{self.BASE_URL}/text-to-speech/{self.voice_id}/with-timestamps",
                headers=headers,
                json=payload,
            )
            resp.raise_for_status()

            audio = resp.content
            # Parse word timestamps from response headers or JSON
            timestamps = []  # Parse from response
            return audio, timestamps
```

---

## 10. Rate Limiting

```python
# api/middleware.py
import time
from focusly.core.redis import get_redis


async def check_rate_limit(user_id: str, limit: int = 10) -> bool:
    """Sliding window rate limit: max `limit` generations per day per user."""
    redis = await get_redis()
    key = f"rate_limit:generate:{user_id}"
    now = time.time()
    window_start = now - 86400  # 24 hours

    pipe = redis.pipeline()
    pipe.zremrangebyscore(key, 0, window_start)
    pipe.zadd(key, {str(now): now})
    pipe.zcard(key)
    pipe.expire(key, 86400)
    results = await pipe.execute()

    count = results[2]
    return count <= limit
```

---

## 11. Task Checklist

### Core Infrastructure
- [M] FastAPI app factory with lifespan (startup: DB, Redis; shutdown: cleanup)
- [M] Pydantic Settings with all env vars
- [M] Async SQLAlchemy engine + session factory
- [M] Redis connection pool
- [M] JWT RS256 token creation and validation
- [M] Structured logging with structlog
- [M] Custom exception hierarchy with error codes
- [M] API middleware: CORS, request ID, logging, rate limiting

### Auth Module
- [M] POST /auth/register (validation, bcrypt hash, create user)
- [M] POST /auth/login (verify password, create tokens, set httpOnly cookies)
- [M] POST /auth/refresh (rotate refresh token)
- [M] POST /auth/logout (invalidate refresh token)
- [S] POST /auth/verify-email
- [S] POST /auth/forgot-password

### Lesson Module
- [M] POST /lessons/generate (validate, rate limit, create job, enqueue)
- [M] GET /lessons/jobs/:id (status, progress, error)
- [M] GET /lessons (paginated list)
- [M] GET /lessons/:id (details + signed video URL)
- [M] DELETE /lessons/:id (delete video from R2, delete record)

### Watch and Quiz Modules
- [M] POST /watch/:id/start
- [M] PUT /watch/:id/progress
- [M] POST /watch/:id/complete
- [M] POST /quiz/:id/attempt
- [M] GET /quiz/:id/results

### Worker
- [M] ARQ WorkerSettings with generate_lesson_task
- [M] Stuck job detection (15-min cron)
- [M] Exponential backoff retry (3 attempts)

### External Services
- [M] R2 upload, signed URLs, delete
- [M] ElevenLabs TTS with word timestamps
- [M] Rate limiting (Redis sliding window, 10/day/user)
