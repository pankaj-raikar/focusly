# Focusly — Deployment and Infrastructure Architecture

## 1. Infrastructure Overview

```
┌──────────────────────────────────────────────────────────────────┐
│                        CLOUDFLARE                                 │
│  DNS · TLS · DDoS · WAF · CDN                                   │
│  focusly.app → Web service                                       │
│  api.focusly.app → API service                                   │
└─────────────────────────┬────────────────────────────────────────┘
                          │
┌─────────────────────────▼────────────────────────────────────────┐
│                        RAILWAY                                    │
│                                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐  ┌─────┐│
│  │ API      │  │ Worker   │  │ Web      │  │ Postgres│  │Redis││
│  │ FastAPI  │  │ ARQ      │  │ Next.js  │  │ Managed │  │Mgmt ││
│  │ gunicorn │  │ 1 inst.  │  │ Standalone│  │ 16     │  │ 7   ││
│  │ 4 workers│  │ max_jobs=5│  │          │  │         │  │     ││
│  └──────────┘  └──────────┘  └──────────┘  └────────┘  └─────┘│
│                                                                  │
│  Internal network: services communicate via Railway private DNS  │
└──────────────────────────────────────────────────────────────────┘
                          │
┌─────────────────────────▼────────────────────────────────────────┐
│                    CLOUDFLARE R2                                  │
│  Object storage (S3-compatible, free egress)                     │
│  Video storage · Audio storage · Asset storage · Backups         │
│  CDN-backed delivery                                             │
└──────────────────────────────────────────────────────────────────┘
```

---

## 2. Railway Service Configuration

### 2.1 API Service

```toml
# railway.toml (API)
[build]
builder = "dockerfile"
dockerfilePath = "docker/api.Dockerfile"

[deploy]
startCommand = "gunicorn src.focusly.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:${PORT} --timeout 120"
healthcheckPath = "/health"
healthcheckTimeout = 30
restartPolicyType = "on_failure"
restartPolicyMaxRetries = 3
numReplicas = 1
```

### 2.2 Worker Service

```toml
# railway.toml (Worker)
[build]
builder = "dockerfile"
dockerfilePath = "docker/api.Dockerfile"

[deploy]
startCommand = "arq src.focusly.workers.main.WorkerSettings"
restartPolicyType = "on_failure"
restartPolicyMaxRetries = 3
numReplicas = 1
```

### 2.3 Web Service

```toml
# railway.toml (Web)
[build]
builder = "dockerfile"
dockerfilePath = "docker/web.Dockerfile"

[deploy]
startCommand = "node server.js"
healthcheckPath = "/"
healthcheckTimeout = 10
restartPolicyType = "on_failure"
restartPolicyMaxRetries = 3
numReplicas = 1
```

---

## 3. CI/CD Pipeline

```
Push to main
    │
    ▼
GitHub Actions
    ├── Backend job
    │   ├── Lint (ruff)
    │   ├── Format check (ruff format)
    │   ├── Type check (mypy)
    │   ├── Migrate (alembic upgrade head)
    │   └── Test (pytest --cov=80%)
    │
    ├── Frontend job
    │   ├── Lint (eslint)
    │   ├── Type check (tsc --noEmit)
    │   ├── Unit test (vitest)
    │   └── Build (next build)
    │
    └── Deploy job (on green)
        ├── railway up --service api
        ├── railway up --service worker
        └── railway up --service web

Pull requests:
    ├── Same CI pipeline (lint, typecheck, test)
    └── No deployment
```

---

## 4. Domain and DNS

```
focusly.app
    ├── A record → Railway web service IP
    ├── CNAME api.focusly.app → Railway API service
    └── Cloudflare proxy enabled (orange cloud)

SSL: Cloudflare Universal SSL (automatic)
HTTP → HTTPS redirect: enforced via Cloudflare page rule
```

---

## 5. Observability Stack

```
┌──────────────────────────────────────────────────────────────┐
│                    Observability                              │
│                                                              │
│  Errors                                                      │
│  ├── Sentry (backend + frontend)                             │
│  │   ├── FastAPI integration                                 │
│  │   ├── SQLAlchemy integration                              │
│  │   ├── Next.js integration                                 │
│  │   └── Custom tags: agent_id, job_id, user_id             │
│  │                                                           │
│  Logging                                                     │
│  ├── structlog (JSON, structured)                            │
│  │   ├── Every log line: request_id, user_id                │
│  │   ├── Agent logs: agent_id, job_id, progress             │
│  │   └── Output: stdout → Railway log drain                 │
│  │                                                           │
│  Metrics                                                     │
│  ├── Chain runs table (tokens, latency, cost per agent)      │
│  ├── Agent execution logs (status, duration, errors)         │
│  ├── Job completion rate (completed / total)                 │
│  ├── Render success rate (successful / attempted)            │
│  └── Average generation time (submit → complete)             │
│                                                              │
│  Health                                                      │
│  ├── GET /health (DB, Redis, R2 connectivity)               │
│  ├── Railway built-in health checks                          │
│  └── Stuck job detection (ARQ cron, every 15 min)           │
└──────────────────────────────────────────────────────────────┘
```

### 5.1 Key Metrics to Track

| Metric | Source | Alert Threshold |
|--------|--------|----------------|
| Error rate | Sentry | >10 errors/minute |
| Job failure rate | PostgreSQL | >20% in 1 hour |
| Average generation time | PostgreSQL | >5 minutes |
| Queue depth | Redis | >10 jobs for >10 min |
| API latency p95 | structlog | >500ms |
| Render failure rate | agent_execution_logs | >30% |
| Claude API cost/day | chain_runs | >$10/day |
| ElevenLabs chars/day | chain_runs | >100k chars |

---

## 6. Database Backup

```bash
#!/bin/bash
# Cron: daily at 03:00 UTC (via Railway cron or ARQ cron)

DATE=$(date +%Y-%m-%d)
BACKUP_FILE="/tmp/focusly-backup-${DATE}.dump.gz"

# Dump
pg_dump -Fc "$DATABASE_URL" | gzip > "$BACKUP_FILE"

# Upload to R2
aws s3 cp "$BACKUP_FILE" "s3://${R2_BUCKET}/backups/${DATE}.dump.gz" \
    --endpoint-url "https://${R2_ACCOUNT_ID}.r2.cloudflarestorage.com"

# Cleanup local
rm "$BACKUP_FILE"

# Retention: delete backups older than 30 days
aws s3 ls "s3://${R2_BUCKET}/backups/" \
    --endpoint-url "https://${R2_ACCOUNT_ID}.r2.cloudflarestorage.com" \
    | while read -r line; do
        createDate=$(echo "$line" | awk '{print $1" "$2}')
        createDate=$(date -d "$createDate" +%s 2>/dev/null)
        olderThan=$(date -d "30 days ago" +%s)
        if [[ $createDate -lt $olderThan ]]; then
            fileName=$(echo "$line" | awk '{print $4}')
            aws s3 rm "s3://${R2_BUCKET}/backups/${fileName}" \
                --endpoint-url "https://${R2_ACCOUNT_ID}.r2.cloudflarestorage.com"
        fi
    done
```

---

## 7. Scaling Strategy

### Phase 1 (MVP): Vertical

| Resource | Current | Scale Up |
|----------|---------|----------|
| API workers | 4 (gunicorn) | 8 |
| Worker max_jobs | 5 | 10 |
| DB connections | 20 pool | 40 pool |
| Railway RAM | 1GB API, 2GB Worker | 2GB API, 4GB Worker |

### Phase 2: Horizontal

```
┌──────────────────────────────────────────────────────────────┐
│  Horizontal Scaling Architecture                              │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Cloudflare Load Balancer                           │    │
│  └────────┬────────────┬────────────┬──────────────────┘    │
│           │            │            │                        │
│     ┌─────▼────┐ ┌─────▼────┐ ┌─────▼────┐                 │
│     │  API #1  │ │  API #2  │ │  API #3  │                 │
│     └──────────┘ └──────────┘ └──────────┘                 │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Render Workers (dedicated Railway service)          │    │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐            │    │
│  │  │Render #1 │ │Render #2 │ │Render #3 │            │    │
│  │  └──────────┘ └──────────┘ └──────────┘            │    │
│  │  Higher CPU + RAM for Manim/Remotion/FFmpeg         │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
│  PostgreSQL: Read replica for GET /lessons, GET /lessons/:id│
│  Redis: Cluster mode if queue depth grows                   │
│  R2/CDN: Auto-scales (no change needed)                     │
└──────────────────────────────────────────────────────────────┘
```

---

## 8. Cost Projection

| Service | MVP (50 users) | Scale (500 users) |
|---------|----------------|-------------------|
| Railway (API + Worker + Web) | $20/month | $60/month |
| Railway Postgres | Included | $15/month |
| Railway Redis | Included | $5/month |
| Cloudflare R2 | $5/month (10GB free) | $20/month |
| Claude API | $15/month | $100/month |
| ElevenLabs | $22/month | $99/month |
| Sentry | Free tier | $26/month |
| Domain | $12/year | $12/year |
| **Total** | **~$62/month** | **~$325/month** |

---

## 9. Incident Response

### Severity Levels

| Level | Definition | Response Time | Example |
|-------|-----------|---------------|---------|
| SEV1 | Service completely down | <15 min | API returning 500 for all requests |
| SEV2 | Major feature broken | <30 min | Video generation failing for all users |
| SEV3 | Minor degradation | <2 hours | Slow generation times, single agent failures |
| SEV4 | Cosmetic/minor | Next business day | Dashboard loading slowly, typo in UI |

### Runbook Summary

| Incident | Steps |
|----------|-------|
| API down | Railway dashboard → check logs → restart → check Sentry → hotfix |
| Worker crash | Railway dashboard → check worker logs → check Redis → restart |
| Render failures | Check Manim Docker → check FFmpeg → check R2 connectivity |
| DB connection pool exhausted | Check active connections → increase pool size → restart API |
| High error rate | Sentry → identify new error → create fix → deploy |
| Cost spike | Check chain_runs table → identify expensive agent → reduce max_tokens or add caching |
