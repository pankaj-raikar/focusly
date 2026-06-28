# Focusly — Deployment and Monitoring

## 1. Railway Deployment

### 1.1 Services

| Service | Type | Resources | Instances |
|---------|------|-----------|-----------|
| api | FastAPI (gunicorn + uvicorn workers) | 1 vCPU, 1GB RAM | 1 |
| worker | ARQ job worker | 2 vCPU, 2GB RAM | 1 |
| web | Next.js (standalone build) | 0.5 vCPU, 512MB RAM | 1 |
| postgres | Managed PostgreSQL 16 | Included | 1 |
| redis | Managed Redis 7 | Included | 1 |

### 1.2 Service Configuration

Each Railway service needs:
- **Environment variables** — imported from production .env
- **Health check** — `/health` for api, process check for worker
- **Restart policy** — on-failure, max 3 retries, 10s delay
- **Deploy trigger** — push to `main` branch

---

## 2. Docker Production Builds

### 2.1 api.Dockerfile

```dockerfile
FROM python:3.12-slim AS builder

WORKDIR /build
COPY pyproject.toml uv.lock ./
RUN pip install uv && uv sync --no-dev --frozen

FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY --from=builder /build/.venv /app/.venv
COPY src ./src

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app"

EXPOSE 8000
CMD ["gunicorn", "src.focusly.main:app", \
     "-w", "4", \
     "-k", "uvicorn.workers.UvicornWorker", \
     "-b", "0.0.0.0:8000", \
     "--timeout", "120", \
     "--graceful-timeout", "30"]
```

### 2.2 web.Dockerfile

```dockerfile
FROM node:20-slim AS builder

WORKDIR /app
COPY package.json pnpm-lock.yaml ./
RUN npm install -g pnpm && pnpm install --frozen-lockfile

COPY . .
RUN pnpm build

FROM node:20-slim

WORKDIR /app
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public

EXPOSE 3000
CMD ["node", "server.js"]
```

### 2.3 video-engine.Dockerfile

```dockerfile
FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libcairo2-dev \
    libpango1.0-dev \
    texlive-latex-base \
    texlive-latex-extra \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

RUN pip install manim==0.18.1

FROM node:20-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg chromium libcairo2 libpango-1.0-0 \
    texlive-latex-base texlive-latex-extra \
    fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY packages/video-engine/package.json ./
RUN npm install
COPY packages/video-engine/src ./src

EXPOSE 3001
CMD ["npm", "start"]
```

---

## 3. Environment Management

### 3.1 Variables by Environment

| Variable | Development | Staging | Production |
|----------|------------|---------|------------|
| ENVIRONMENT | development | staging | production |
| DEBUG | true | false | false |
| DATABASE_URL | local Docker | Railway managed | Railway managed |
| REDIS_URL | local Docker | Railway managed | Railway managed |
| CORS_ORIGINS | localhost:3000 | staging.focusly.app | focusly.app |
| SENTRY_DSN | (empty) | staging DSN | production DSN |

### 3.2 Secret Rotation

- API keys: rotate quarterly via Anthropic/ElevenLabs dashboards
- JWT secret: rotate via env var update + Railway redeploy
- R2 credentials: rotate via Cloudflare dashboard
- Database password: rotate via Railway plugin settings

---

## 4. Domain and HTTPS

```
focusly.app          → web service (Next.js)
api.focusly.app      → api service (FastAPI)
```

- Cloudflare DNS: A/CNAME records pointing to Railway
- SSL: Cloudflare Universal SSL (automatic)
- HTTP → HTTPS redirect: enforced via Cloudflare

---

## 5. Sentry Integration

### 5.1 Backend

```python
# main.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from focusly.core.config import get_settings

if get_settings().sentry_dsn:
    sentry_sdk.init(
        dsn=get_settings().sentry_dsn,
        environment=get_settings().environment,
        integrations=[
            FastApiIntegration(),
            SqlalchemyIntegration(),
        ],
        traces_sample_rate=0.1,
        profiles_sample_rate=0.1,
    )
```

### 5.2 Frontend

```typescript
// apps/web/sentry.client.config.ts
import * as Sentry from '@sentry/nextjs'

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  environment: process.env.NODE_ENV,
  tracesSampleRate: 0.1,
})
```

### 5.3 Alert Rules

| Alert | Condition | Severity |
|-------|-----------|----------|
| Error spike | >10 errors/minute | Critical |
| New error type | First occurrence of new error fingerprint | Warning |
| Render failure rate | >20% of renders fail in 1 hour | Critical |
| Queue depth | >10 jobs queued for >10 minutes | Warning |
| API latency | p95 >500ms for 5 minutes | Warning |

---

## 6. Structured Logging

```python
# core/logging.py
import structlog

def setup_logging():
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer() if not DEBUG else structlog.dev.ConsoleRenderer(),
        ],
    )

# Usage in API middleware
@structlog.contextvars.bind_contextvars(request_id=request_id, user_id=user_id)
```

Log format in production:
```json
{"event":"lesson_generation_started","level":"info","timestamp":"2026-05-18T10:30:00Z","request_id":"req-abc123","user_id":"user-xyz","job_id":"job-789","topic":"binary search"}
```

---

## 7. Health Checks

```python
# api/v1/health.py
@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db), redis=Depends(get_redis)):
    checks = {}

    # Database
    try:
        await db.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception as e:
        checks["database"] = f"error: {str(e)}"

    # Redis
    try:
        await redis.ping()
        checks["redis"] = "ok"
    except Exception as e:
        checks["redis"] = f"error: {str(e)}"

    # R2
    try:
        R2Service().client.head_bucket(Bucket=R2Service().bucket)
        checks["r2"] = "ok"
    except Exception as e:
        checks["r2"] = f"error: {str(e)}"

    healthy = all(v == "ok" for v in checks.values())
    return {"status": "healthy" if healthy else "degraded", "checks": checks}
```

---

## 8. Database Backup

```bash
# Cron job (runs daily at 3 AM UTC via Railway cron or worker)
#!/bin/bash
DATE=$(date +%Y-%m-%d)
pg_dump -Fc "$DATABASE_URL" | gzip > "/tmp/backup-${DATE}.dump.gz"
aws s3 cp "/tmp/backup-${DATE}.dump.gz" "s3://${R2_BUCKET}/backups/${DATE}.dump.gz" \
    --endpoint-url "https://${R2_ACCOUNT_ID}.r2.cloudflarestorage.com"
rm "/tmp/backup-${DATE}.dump.gz"
# Retention: delete backups older than 30 days
```

---

## 9. Scaling Strategy

### 9.1 Vertical (MVP — current)

- Increase Railway service RAM/CPU
- Increase gunicorn workers
- Increase ARQ max_jobs

### 9.2 Horizontal (Phase 2)

- Separate render workers (dedicated Railway service)
- Load balancer for API (Railway handles this)
- Queue partitioning (separate queues for planning vs rendering)
- R2 CDN handles video delivery scaling automatically
- PostgreSQL read replicas for heavy read endpoints

---

## 10. Incident Response Runbook

| Incident | Response |
|----------|----------|
| API down | Railway dashboard → check logs → restart service → check Sentry |
| Render failures spike | Check worker logs → check Manim Docker → check R2 connectivity |
| Queue stuck | Check Redis connectivity → check stuck job detection → manual retry |
| Database issues | Check connections → check disk → restore from backup |
| High error rate | Sentry → identify new error → hotfix → deploy |

---

## 11. Task Checklist

- [M] Railway services configured (api, worker, web, postgres, redis)
- [M] Docker production builds for all services
- [M] Environment variables set for staging and production
- [M] Domain + HTTPS via Cloudflare
- [M] Sentry integration (backend + frontend)
- [M] Structured logging (structlog JSON)
- [M] Health check endpoint
- [M] Database backup cron to R2
- [S] Alert rules in Sentry
- [S] Queue monitoring dashboard
- [S] Cost monitoring (API usage tracking)
- [C] Load testing with Locust
- [C] Incident response runbook document
