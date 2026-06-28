# Focusly — Backend and Frontend Architecture

## 1. Backend Architecture

### 1.1 Layered Design

```
┌───────────────────────────────────────────────────────────────┐
│                      API Layer (FastAPI)                       │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐        │
│  │  Auth    │ │ Lessons  │ │  Watch   │ │  Quiz    │        │
│  │ Router   │ │ Router   │ │ Router   │ │ Router   │        │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘        │
│       │             │            │             │              │
│  ┌────▼─────────────▼────────────▼─────────────▼──────┐      │
│  │                 Dependencies                        │      │
│  │  get_db() · get_current_user() · get_redis()       │      │
│  └────────────────────┬───────────────────────────────┘      │
└───────────────────────┼───────────────────────────────────────┘
                        │
┌───────────────────────┼───────────────────────────────────────┐
│                Domain Layer                                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │  Models  │  │ Schemas  │  │  Enums   │  │ Services │    │
│  │ (ORM)    │  │ (Pydantic│  │          │  │ (domain  │    │
│  │          │  │  req/resp│  │          │  │  logic)  │    │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘    │
└───────────────────────────────────────────────────────────────┘
                        │
┌───────────────────────┼───────────────────────────────────────┐
│             Infrastructure Layer                               │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐             │
│  │ Repositories│  │  Services  │  │  Storage   │             │
│  │ (DB access) │  │ (Claude,   │  │ (R2/S3     │             │
│  │             │  │  ElevenLabs│  │  client)   │             │
│  │             │  │  httpx)    │  │            │             │
│  └────────────┘  └────────────┘  └────────────┘             │
└───────────────────────────────────────────────────────────────┘
                        │
┌───────────────────────┼───────────────────────────────────────┐
│                  Agent Layer                                   │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐             │
│  │  LangGraph │  │ LangChain  │  │   Tools    │             │
│  │  StateGraph│  │  Chains    │  │ (Unsplash, │             │
│  │  (33 nodes)│  │ (prompt→   │  │  ElevenLabs│             │
│  │            │  │  LLM→parse)│  │  Pixabay,  │             │
│  │            │  │            │  │  Manim, R2)│             │
│  └────────────┘  └────────────┘  └────────────┘             │
└───────────────────────────────────────────────────────────────┘
                        │
┌───────────────────────┼───────────────────────────────────────┐
│                  Worker Layer                                  │
│  ┌──────────────────────────────────────────┐                │
│  │  ARQ Worker                              │                │
│  │  - generate_lesson_task (main job)       │                │
│  │  - check_stuck_jobs (cron, every 15 min) │                │
│  │  - cleanup_expired_tokens (cron, daily)  │                │
│  └──────────────────────────────────────────┘                │
└───────────────────────────────────────────────────────────────┘
```

### 1.2 Dependency Injection

```python
# api/deps.py
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as redis

async def get_db() -> AsyncSession:
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise

async def get_redis() -> redis.Redis:
    return await get_redis_pool()

async def get_current_user(
    token: str = Depends(cookie_token),
    db: AsyncSession = Depends(get_db),
) -> User:
    payload = decode_token(token)
    user = await db.get(User, payload["sub"])
    if not user:
        raise AuthenticationError("User not found")
    return user

async def require_admin(user: User = Depends(get_current_user)) -> User:
    if not user.is_admin:
        raise AuthorizationError("Admin access required")
    return user
```

---

## 2. Frontend Architecture

### 2.1 Component Hierarchy

```
RootLayout (providers: QueryClient, Zustand)
├── PublicLayout
│   ├── LandingPage (/)
│   ├── LoginPage (/login)
│   └── RegisterPage (/register)
│
└── DashboardLayout (auth guard)
    ├── Sidebar (navigation)
    ├── Header (user menu, notifications)
    │
    ├── DashboardPage (/dashboard)
    │   └── LessonGrid → LessonCard[]
    │
    ├── GeneratePage (/generate)
    │   └── GenerateForm → LevelSelector
    │
    ├── JobStatusPage (/jobs/:job_id)
    │   └── JobStatusPoller → ProgressStages
    │
    ├── LessonPage (/lessons/:id)
    │   └── VideoPlayer
    │       ├── PlayerControls
    │       ├── ChapterMarkers
    │       ├── CaptionOverlay
    │       └── QuizOverlay → QuizCard
    │
    ├── QuizResultsPage (/lessons/:id/quiz)
    │   └── QuizSummary → QuizResult[]
    │
    └── SettingsPage (/settings)
```

### 2.2 State Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                     State Management                          │
│                                                              │
│  Server State (React Query)                                  │
│  ┌──────────────────────────────────────────┐               │
│  │ useQuery(["lessons"], api.getLessons)    │               │
│  │ useQuery(["job", jobId], api.getJob)     │               │
│  │ useQuery(["lesson", id], api.getLesson)  │               │
│  │ staleTime: 5 minutes                     │               │
│  │ refetchOnWindowFocus: true               │               │
│  └──────────────────────────────────────────┘               │
│                                                              │
│  Client State (Zustand)                                      │
│  ┌──────────────────┐  ┌──────────────────┐                │
│  │ useAuthStore     │  │ usePlayerStore   │                │
│  │ - user           │  │ - isPlaying      │                │
│  │ - isAuthenticated│  │ - currentTime    │                │
│  │ - login/logout   │  │ - playbackRate   │                │
│  └──────────────────┘  │ - captionsEnabled│                │
│                         └──────────────────┘                │
│  ┌──────────────────┐                                       │
│  │ useQuizStore     │                                       │
│  │ - activeQuizIndex│                                       │
│  │ - selectedOption │                                       │
│  │ - isRevealed     │                                       │
│  │ - answers        │                                       │
│  └──────────────────┘                                       │
│                                                              │
│  URL State                                                   │
│  ┌──────────────────┐                                       │
│  │ /dashboard?page=2│                                       │
│  │ /generate?level= │                                       │
│  └──────────────────┘                                       │
└──────────────────────────────────────────────────────────────┘
```

### 2.3 API Client

```typescript
// lib/api.ts
const BASE_URL = process.env.NEXT_PUBLIC_API_URL;

async function fetcher<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${BASE_URL}${endpoint}`, {
    ...options,
    credentials: "include", // send httpOnly cookies
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
  });

  if (!response.ok) {
    const error = await response.json();
    throw new ApiError(error.error.code, error.error.message, response.status);
  }

  return response.json();
}
```

### 2.4 Auth Flow

```
1. User submits login form
        │
        ▼
2. POST /api/v1/auth/login {email, password}
        │
        ▼
3. Backend validates credentials
   Sets httpOnly cookies:
   - access_token (15 min)
   - refresh_token (7 days)
        │
        ▼
4. Frontend stores user info in Zustand
   isAuthenticated = true
        │
        ▼
5. Subsequent requests: cookies auto-attached by browser
        │
        ▼
6. Access token expires (15 min)
        │
        ▼
7. React Query interceptor catches 401
   Calls POST /auth/refresh (uses refresh_token cookie)
        │
        ▼
8. New access_token set, request retried
        │
        ▼
9. Refresh token expired (7 days)
   Redirect to /login
```

---

## 3. Video Player Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    VideoPlayer Component                       │
│                                                              │
│  ┌──────────────────────────────────────────────┐           │
│  │             video.js instance                 │           │
│  │  HLS plugin → loads master.m3u8              │           │
│  │  CDN serves .ts segments                     │           │
│  └──────────────────────┬───────────────────────┘           │
│                         │                                    │
│  ┌──────────────────────▼───────────────────────┐           │
│  │             Custom Controls                   │           │
│  │  [Play] [Replay 10s] [Speed ▼] [CC] [PiP]   │           │
│  │  [──────────●─────────────────] chapter marks │           │
│  └──────────────────────┬───────────────────────┘           │
│                         │                                    │
│  ┌──────────────────────▼───────────────────────┐           │
│  │             Quiz Overlay                      │           │
│  │  Triggered at checkpoint timestamps           │           │
│  │  Pauses video → Shows question                │           │
│  │  User answers → Reveals explanation           │           │
│  │  Submit → Resume video                        │           │
│  └──────────────────────────────────────────────┘           │
│                                                              │
│  ┌──────────────────────────────────────────────┐           │
│  │             Progress Tracking                 │           │
│  │  Every 10s: PUT /watch/:id/progress          │           │
│  │  On complete: POST /watch/:id/complete       │           │
│  │  On return: seek to saved position           │           │
│  └──────────────────────────────────────────────┘           │
└──────────────────────────────────────────────────────────────┘
```

---

## 4. Error Handling Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    Error Flow                                  │
│                                                              │
│  Backend Error                                               │
│  │                                                           │
│  ├── FocuslyError (custom hierarchy)                        │
│  │   ├── AuthenticationError (401)                          │
│  │   ├── AuthorizationError (403)                           │
│  │   ├── NotFoundError (404)                                │
│  │   ├── ValidationError (422)                              │
│  │   ├── RateLimitError (429)                               │
│  │   ├── PipelineError (500)                                │
│  │   └── RenderError (500)                                  │
│  │                                                           │
│  ├── Global exception handler                               │
│  │   Returns: { data: null, error: { code, message } }      │
│  │                                                           │
│  └── Sentry capture (500 errors)                            │
│                                                              │
│  Frontend Error                                              │
│  │                                                           │
│  ├── ApiError class                                         │
│  │   .code: string                                          │
│  │   .message: string                                       │
│  │   .status: number                                        │
│  │                                                           │
│  ├── React Query onError callback                           │
│  │   → Toast notification                                   │
│  │   → 401 → redirect to login                              │
│  │   → 429 → "Too many requests" banner                    │
│  │                                                           │
│  └── ErrorBoundary component                                │
│      → Catches render errors                                │
│      → Shows fallback UI with retry button                  │
└──────────────────────────────────────────────────────────────┘
```
