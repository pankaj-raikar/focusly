# Focusly — Project Setup

## 1. Monorepo Initialization

### 1.1 Directory Structure

```
focusly/
├── apps/
│   ├── api/                        # FastAPI backend (Python 3.12)
│   │   ├── src/
│   │   │   └── focusly/
│   │   │       ├── __init__.py
│   │   │       ├── main.py         # FastAPI app factory
│   │   │       ├── core/
│   │   │       │   ├── config.py       # Pydantic Settings
│   │   │       │   ├── database.py     # SQLAlchemy async engine
│   │   │       │   ├── redis.py        # Redis connection pool
│   │   │       │   ├── security.py     # JWT, bcrypt, tokens
│   │   │       │   ├── exceptions.py   # Custom exception hierarchy
│   │   │       │   └── logging.py      # Structlog config
│   │   │       ├── api/
│   │   │       │   ├── v1/
│   │   │       │   │   ├── auth.py
│   │   │       │   │   ├── lessons.py
│   │   │       │   │   ├── watch.py
│   │   │       │   │   ├── quiz.py
│   │   │       │   │   └── admin.py
│   │   │       │   ├── deps.py         # FastAPI dependencies
│   │   │       │   └── middleware.py
│   │   │       ├── domain/
│   │   │       │   ├── models/         # SQLAlchemy ORM models
│   │   │       │   ├── schemas/        # Pydantic request/response schemas
│   │   │       │   └── enums.py
│   │   │       ├── infrastructure/
│   │   │       │   ├── repositories/   # Data access layer
│   │   │       │   ├── services/       # External API clients
│   │   │       │   └── storage.py      # R2/S3 client
│   │   │       ├── agents/
│   │   │       │   ├── graph.py            # LangGraph StateGraph
│   │   │       │   ├── state.py            # PipelineState TypedDict
│   │   │       │   ├── nodes/              # One file per layer
│   │   │       │   │   ├── orchestration.py
│   │   │       │   │   ├── knowledge.py
│   │   │       │   │   ├── script.py
│   │   │       │   │   ├── visual.py
│   │   │       │   │   ├── codegen.py
│   │   │       │   │   ├── audio.py
│   │   │       │   │   ├── qa.py
│   │   │       │   │   └── render.py
│   │   │       │   ├── chains/             # LangChain chains per agent
│   │   │       │   │   ├── base.py
│   │   │       │   │   ├── knowledge_chains.py
│   │   │       │   │   ├── script_chains.py
│   │   │       │   │   ├── codegen_chains.py
│   │   │       │   │   ├── audio_chains.py
│   │   │       │   │   └── callbacks.py
│   │   │       │   ├── tools/              # LangChain tools
│   │   │       │   │   ├── unsplash_tool.py
│   │   │       │   │   ├── elevenlabs_tool.py
│   │   │       │   │   ├── pixabay_tool.py
│   │   │       │   │   ├── manim_tool.py
│   │   │       │   │   └── r2_storage_tool.py
│   │   │       │   ├── prompts/            # Prompt templates
│   │   │       │   │   ├── A02_audience.md
│   │   │       │   │   ├── A03_curriculum.md
│   │   │       │   │   └── ...
│   │   │       │   ├── memory/
│   │   │       │   │   ├── buffer.py
│   │   │       │   │   ├── entity.py
│   │   │       │   │   └── pg_memory.py
│   │   │       │   └── schemas/            # Per-agent Pydantic output schemas
│   │   │       │       ├── knowledge.py
│   │   │       │       ├── script.py
│   │   │       │       ├── visual.py
│   │   │       │       ├── codegen.py
│   │   │       │       └── audio.py
│   │   │       └── workers/
│   │   │           ├── main.py         # ARQ WorkerSettings
│   │   │           └── tasks.py        # Job task functions
│   │   ├── tests/
│   │   │   ├── conftest.py
│   │   │   ├── unit/
│   │   │   ├── integration/
│   │   │   └── fixtures/
│   │   ├── alembic/
│   │   │   ├── env.py
│   │   │   └── versions/
│   │   ├── alembic.ini
│   │   ├── pyproject.toml
│   │   └── Makefile
│   │
│   └── web/                        # Next.js 15 frontend
│       ├── app/
│       │   ├── (auth)/             # Route group: login, register
│       │   │   ├── login/page.tsx
│       │   │   └── register/page.tsx
│       │   ├── (dashboard)/        # Route group: protected pages
│       │   │   ├── layout.tsx
│       │   │   ├── dashboard/page.tsx
│       │   │   ├── generate/page.tsx
│       │   │   ├── jobs/[job_id]/page.tsx
│       │   │   ├── lessons/[id]/page.tsx
│       │   │   ├── lessons/[id]/quiz/page.tsx
│       │   │   └── settings/page.tsx
│       │   ├── layout.tsx          # Root layout
│       │   ├── page.tsx            # Landing page
│       │   └── globals.css
│       ├── components/
│       │   ├── ui/                 # shadcn/ui components
│       │   ├── video-player/       # Custom video player
│       │   ├── quiz/               # Quiz overlay
│       │   ├── dashboard/          # Dashboard cards
│       │   └── generate/           # Generation form
│       ├── hooks/
│       ├── lib/
│       │   ├── api.ts              # API client
│       │   ├── auth.ts             # Auth helpers
│       │   └── stores/             # Zustand stores
│       ├── public/
│       ├── next.config.ts
│       ├── tailwind.config.ts
│       ├── tsconfig.json
│       └── package.json
│
├── packages/
│   └── video-engine/               # Remotion compositions
│       ├── src/
│       │   ├── Root.tsx
│       │   ├── compositions/
│       │   │   ├── KineticText.tsx
│       │   │   ├── ImageOverlay.tsx
│       │   │   ├── BulletReveal.tsx
│       │   │   ├── ConceptMap.tsx
│       │   │   ├── AlgorithmStepThrough.tsx
│       │   │   ├── D3Chart.tsx
│       │   │   ├── QuizScene.tsx
│       │   │   ├── TransitionScene.tsx
│       │   │   ├── HookScene.tsx
│       │   │   ├── SummaryScene.tsx
│       │   │   └── ProgressMilestone.tsx
│       │   ├── lib/
│       │   │   ├── design-tokens.ts
│       │   │   ├── adhd-rules.ts
│       │   │   └── types.ts
│       │   └── render.ts           # CLI entrypoint
│       ├── remotion.config.ts
│       └── package.json
│
├── docker/
│   ├── api.Dockerfile
│   ├── web.Dockerfile
│   └── video-engine.Dockerfile
│
├── docker-compose.yml
├── docker-compose.prod.yml
├── Makefile
├── turbo.json
├── pnpm-workspace.yaml
├── .env.example
├── .gitignore
├── .github/
│   └── workflows/
│       └── ci.yml
└── CLAUDE.md
```

### 1.2 pnpm Workspace Configuration

```yaml
# pnpm-workspace.yaml
packages:
  - "apps/*"
  - "packages/*"
```

### 1.3 Turborepo Configuration

```json
// turbo.json
{
  "$schema": "https://turbo.build/schema.json",
  "tasks": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": [".next/**", "!.next/cache/**", "dist/**"]
    },
    "dev": {
      "cache": false,
      "persistent": true
    },
    "lint": {
      "dependsOn": ["^build"]
    },
    "typecheck": {
      "dependsOn": ["^build"]
    },
    "test": {
      "dependsOn": ["build"]
    }
  }
}
```

---

## 2. Docker Compose — Local Development

### 2.1 docker-compose.yml

```yaml
# docker-compose.yml
version: "3.9"

services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: focusly_dev
      POSTGRES_USER: focusly
      POSTGRES_PASSWORD: devpassword
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U focusly -d focusly_dev"]
      interval: 5s
      timeout: 3s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 5

  api:
    build:
      context: .
      dockerfile: docker/api.Dockerfile
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ./apps/api/src:/app/src    # hot reload
    ports:
      - "8000:8000"
    env_file:
      - .env
    environment:
      DATABASE_URL: postgresql+asyncpg://focusly:devpassword@postgres:5432/focusly_dev
      REDIS_URL: redis://redis:6379
      ENVIRONMENT: development
    command: uv run uvicorn src.focusly.main:app --reload --host 0.0.0.0 --port 8000

  worker:
    build:
      context: .
      dockerfile: docker/api.Dockerfile
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    env_file:
      - .env
    environment:
      DATABASE_URL: postgresql+asyncpg://focusly:devpassword@postgres:5432/focusly_dev
      REDIS_URL: redis://redis:6379
      ENVIRONMENT: development
    command: uv run arq src.focusly.workers.main.WorkerSettings

  video-engine:
    build:
      context: .
      dockerfile: docker/video-engine.Dockerfile
    volumes:
      - ./packages/video-engine/src:/app/src
    ports:
      - "3001:3001"
    environment:
      PORT: 3001

  web:
    build:
      context: .
      dockerfile: docker/web.Dockerfile
    depends_on:
      - api
    volumes:
      - ./apps/web:/app
      - /app/node_modules
      - /app/.next
    ports:
      - "3000:3000"
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:8000
      NODE_ENV: development

volumes:
  postgres_data:
  redis_data:
```

### 2.2 Makefile

```makefile
# Makefile
.PHONY: dev build test lint clean db-migrate db-upgrade

# ── Development ────────────────────────────────────────
dev:
	docker compose up --build

dev-api:
	cd apps/api && uv run uvicorn src.focusly.main:app --reload --port 8000

dev-web:
	cd apps/web && pnpm dev

dev-worker:
	cd apps/api && uv run arq src.focusly.workers.main.WorkerSettings

# ── Build ──────────────────────────────────────────────
build:
	pnpm turbo build

build-api:
	cd apps/api && uv build

build-web:
	cd apps/web && pnpm build

# ── Testing ────────────────────────────────────────────
test:
	pnpm turbo test

test-api:
	cd apps/api && uv run pytest -v --tb=short

test-api-cov:
	cd apps/api && uv run pytest --cov=src --cov-report=html --cov-fail-under=80

test-web:
	cd apps/web && pnpm test

test-e2e:
	cd apps/web && pnpm test:e2e

# ── Linting ────────────────────────────────────────────
lint:
	pnpm turbo lint

lint-api:
	cd apps/api && uv run ruff check src tests

lint-api-fix:
	cd apps/api && uv run ruff check --fix src tests

typecheck:
	pnpm turbo typecheck

typecheck-api:
	cd apps/api && uv run mypy src

typecheck-web:
	cd apps/web && pnpm tsc --noEmit

# ── Database ───────────────────────────────────────────
db-migrate:
	cd apps/api && uv run alembic revision --autogenerate -m "$(msg)"

db-upgrade:
	cd apps/api && uv run alembic upgrade head

db-downgrade:
	cd apps/api && uv run alembic downgrade -1

db-reset:
	docker compose down -v
	docker compose up postgres redis -d
	sleep 3
	cd apps/api && uv run alembic upgrade head

# ── Cleanup ────────────────────────────────────────────
clean:
	docker compose down -v
	rm -rf apps/web/.next apps/web/node_modules
	rm -rf apps/api/.mypy_cache apps/api/.pytest_cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

# ── Setup ──────────────────────────────────────────────
setup:
	pnpm install
	cd apps/api && uv sync --all-extras
	cp -n .env.example .env || true
	docker compose up postgres redis -d
	sleep 3
	cd apps/api && uv run alembic upgrade head
	@echo "✓ Setup complete. Run 'make dev' to start."
```

---

## 3. Environment Variables

### 3.1 .env.example

```bash
# ═══════════════════════════════════════════════════════
# FOCUSLY — Environment Variables
# Copy to .env and fill in values. NEVER commit .env.
# ═══════════════════════════════════════════════════════

# ── Application ────────────────────────────────────────
ENVIRONMENT=development           # development | staging | production
DEBUG=false
SECRET_KEY=                       # Generate: openssl genrsa 2048
CORS_ORIGINS=http://localhost:3000

# ── Database ───────────────────────────────────────────
DATABASE_URL=postgresql+asyncpg://focusly:devpassword@localhost:5432/focusly_dev

# ── Redis ──────────────────────────────────────────────
REDIS_URL=redis://localhost:6379

# ── External APIs ──────────────────────────────────────
ANTHROPIC_API_KEY=                # Claude API key
ELEVENLABS_API_KEY=               # TTS API key
ELEVENLABS_VOICE_ID=              # Selected voice ID

# ── Cloudflare R2 Storage ──────────────────────────────
CLOUDFLARE_R2_ACCOUNT_ID=
CLOUDFLARE_R2_ACCESS_KEY_ID=
CLOUDFLARE_R2_SECRET_ACCESS_KEY=
CLOUDFLARE_R2_BUCKET_NAME=
CLOUDFLARE_R2_PUBLIC_URL=

# ── Unsplash (AssetHunter) ─────────────────────────────
UNSPLASH_ACCESS_KEY=

# ── Pixabay (MusicSelection) ───────────────────────────
PIXABAY_API_KEY=

# ── Email (Phase 2 — leave empty for MVP) ─────────────
SMTP_HOST=
SMTP_PORT=
SMTP_USER=
SMTP_PASSWORD=

# ── Monitoring ─────────────────────────────────────────
SENTRY_DSN=

# ── Rate Limiting ──────────────────────────────────────
DAILY_GENERATION_LIMIT=10
CONCURRENT_RENDER_LIMIT=3
```

---

## 4. Git Hooks and Linting

### 4.1 Pre-commit Configuration

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: ruff-check
        name: ruff (Python linter)
        entry: uv run ruff check --fix
        language: system
        files: \.py$
        types: [python]

      - id: ruff-format
        name: ruff (Python formatter)
        entry: uv run ruff format
        language: system
        files: \.py$
        types: [python]

      - id: mypy
        name: mypy (Python type check)
        entry: uv run mypy
        language: system
        files: \.py$
        types: [python]
        pass_filenames: false
        args: [src]

      - id: eslint
        name: eslint (TypeScript linter)
        entry: pnpm -w exec eslint --fix
        language: system
        files: \.(ts|tsx)$

      - id: typecheck-web
        name: tsc (TypeScript type check)
        entry: sh -c 'cd apps/web && pnpm tsc --noEmit'
        language: system
        files: \.(ts|tsx)$
        pass_filenames: false
```

### 4.2 ruff.toml

```toml
# apps/api/ruff.toml
target-version = "py312"
line-length = 100

[lint]
select = [
    "E",    # pycodestyle errors
    "W",    # pycodestyle warnings
    "F",    # pyflakes
    "I",    # isort
    "N",    # pep8-naming
    "UP",   # pyupgrade
    "B",    # flake8-bugbear
    "A",    # flake8-builtins
    "S",    # flake8-bandit (security)
    "T20",  # flake8-print
    "SIM",  # flake8-simplify
    "TCH",  # type checking imports
]
ignore = ["S101"]  # allow assert in tests

[lint.per-file-ignores]
"tests/**" = ["S101", "T20"]

[format]
quote-style = "double"
indent-style = "space"
```

### 4.3 ESLint Configuration (apps/web)

```jsonc
// apps/web/.eslintrc.json
{
  "extends": [
    "next/core-web-vitals",
    "eslint:recommended",
    "@typescript-eslint/recommended"
  ],
  "rules": {
    "@typescript-eslint/no-unused-vars": ["error", { "argsIgnorePattern": "^_" }],
    "no-console": "error",
    "prefer-const": "error"
  }
}
```

### 4.4 TypeScript Configuration (apps/web)

```jsonc
// apps/web/tsconfig.json
{
  "compilerOptions": {
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "forceConsistentCasingInFileNames": true,
    "noEmit": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "target": "ES2022",
    "jsx": "preserve",
    "incremental": true,
    "plugins": [{ "name": "next" }],
    "paths": {
      "@/*": ["./app/*", "./*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
```

### 4.5 mypy Configuration (apps/api)

```toml
# apps/api/pyproject.toml — mypy section
[tool.mypy]
python_version = "3.12"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
plugins = ["pydantic.mypy", "sqlalchemy.ext.mypy.plugin"]

[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false
```

---

## 5. CI/CD Pipeline — GitHub Actions

### 5.1 ci.yml

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: true

jobs:
  backend:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_PASSWORD: test
          POSTGRES_DB: focusly_test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379

    env:
      DATABASE_URL: postgresql+asyncpg://postgres:test@localhost:5432/focusly_test
      REDIS_URL: redis://localhost:6379
      ENVIRONMENT: test
      ANTHROPIC_API_KEY: mock-key

    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v4
        with:
          version: "0.5"

      - name: Install dependencies
        run: cd apps/api && uv sync --all-extras

      - name: Lint
        run: cd apps/api && uv run ruff check src tests

      - name: Format check
        run: cd apps/api && uv run ruff format --check src tests

      - name: Type check
        run: cd apps/api && uv run mypy src

      - name: Run migrations
        run: cd apps/api && uv run alembic upgrade head

      - name: Run tests
        run: cd apps/api && uv run pytest -v --tb=short --cov=src --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          file: apps/api/coverage.xml
          flags: backend

  frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
        with:
          version: 9
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: pnpm

      - name: Install dependencies
        run: pnpm install

      - name: Lint
        run: cd apps/web && pnpm lint

      - name: Type check
        run: cd apps/web && pnpm tsc --noEmit

      - name: Unit tests
        run: cd apps/web && pnpm test

      - name: Build
        run: cd apps/web && pnpm build

  e2e:
    runs-on: ubuntu-latest
    needs: [backend, frontend]
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
        with:
          version: 9

      - name: Install dependencies
        run: pnpm install

      - name: Install Playwright
        run: cd apps/web && pnpm exec playwright install --with-deps chromium

      - name: Run E2E tests
        run: cd apps/web && pnpm test:e2e

  deploy-staging:
    needs: [backend, frontend, e2e]
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Deploy API to Railway
        run: railway up --service api
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
      - name: Deploy Web to Railway
        run: railway up --service web
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
      - name: Deploy Worker to Railway
        run: railway up --service worker
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
```

---

## 6. Railway Setup

### 6.1 Service Architecture

```
Railway project: focusly
├── Service: api          — FastAPI (gunicorn + uvicorn workers)
├── Service: worker       — ARQ job worker (1 instance)
├── Service: web          — Next.js (standalone build)
├── Plugin: postgres      — Managed PostgreSQL 16
└── Plugin: redis         — Managed Redis 7
```

### 6.2 Railway Configuration

Each service needs:
- **Environment variables** — imported from `.env.staging` / `.env.production`
- **Health check** — `/health` endpoint for api, process check for worker
- **Restart policy** — on failure, max 3 retries
- **Resource limits** — Hobby plan: 8GB RAM, 8 vCPU shared

---

## 7. CLAUDE.md — Project Instructions

```markdown
# Focusly

AI-driven animated learning platform for ADHD learners.
Monorepo: apps/api (FastAPI), apps/web (Next.js), packages/video-engine (Remotion).

## Quick Start
cp .env.example .env
make setup
make dev

## Architecture
- Backend: FastAPI + SQLAlchemy 2.0 async + ARQ queue
- Frontend: Next.js 15 App Router + Tailwind + shadcn/ui
- Video: Remotion (React scenes) + Manim (math animations) + FFmpeg
- AI: LangGraph (33-agent pipeline) + LangChain (LLM chains)
- Storage: Cloudflare R2
- Deploy: Railway

## Key Conventions
- Python: ruff, mypy strict, pytest, 80% coverage
- TypeScript: eslint strict, vitest, playwright
- Immutable data patterns everywhere
- All API responses: { data, error } envelope
- JWT in httpOnly cookies, never localStorage
- Max 7 words on screen (ADHD rule)

## Running Tests
make test-api          # Backend unit + integration
make test-api-cov      # With coverage report
make test-web          # Frontend unit tests
make test-e2e          # Playwright E2E

## Agent System
33 agents organized in 8 layers. Orchestrated by LangGraph StateGraph.
Each agent node wraps a LangChain chain (ChatAnthropic + parser + tools).
See docs/planner/06-langgraph-agents.md for full graph specification.
```

---

## 8. Task Checklist

- [M] Monorepo scaffolded with pnpm workspaces
- [M] Turborepo configured with build/dev/lint/test tasks
- [M] Docker Compose: Postgres 16, Redis 7, API, Worker, Web, Video Engine
- [M] .env.example with all variables documented
- [M] Pre-commit hooks: ruff, mypy, eslint, tsc
- [M] GitHub Actions CI: lint, typecheck, test for backend and frontend
- [M] Railway project created with staging services
- [M] CLAUDE.md with project instructions
- [S] Makefile with all dev commands
- [S] Docker Compose production overrides
- [C] Dependabot configuration for automated dependency updates
