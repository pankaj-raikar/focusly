# Focusly — Frontend Implementation Plan

## 1. App Router Structure

```
apps/web/app/
├── layout.tsx                 # Root layout: fonts, theme, providers
├── page.tsx                   # Landing page (public)
├── globals.css                # Tailwind imports + CSS custom properties
├── (auth)/
│   ├── login/page.tsx         # Login page
│   └── register/page.tsx      # Registration page
├── (dashboard)/               # Protected route group
│   ├── layout.tsx             # Auth guard + sidebar + header
│   ├── dashboard/page.tsx     # Lesson list grid
│   ├── generate/page.tsx      # Topic input + level selector
│   ├── jobs/
│   │   └── [job_id]/page.tsx  # Job status polling page
│   ├── lessons/
│   │   ├── [id]/
│   │   │   ├── page.tsx       # Video watch page
│   │   │   └── quiz/page.tsx  # Quiz results
│   └── settings/page.tsx      # Account settings
└── api/                       # Next.js API routes (if needed for SSR)
```

---

## 2. Component Architecture

```
components/
├── ui/                        # shadcn/ui base (Button, Input, Card, etc.)
├── layout/
│   ├── AppShell.tsx           # Sidebar + header + main area
│   ├── Sidebar.tsx            # Navigation sidebar
│   └── Header.tsx             # Top bar with user menu
├── generate/
│   ├── GenerateForm.tsx       # Topic input form
│   └── LevelSelector.tsx      # Beginner / Intermediate / Advanced
├── dashboard/
│   ├── LessonGrid.tsx         # Grid of lesson cards
│   ├── LessonCard.tsx         # Single lesson card
│   └── EmptyState.tsx         # "No lessons yet" CTA
├── job/
│   ├── JobStatusPoller.tsx    # Polling + progress animation
│   └── ProgressStages.tsx     # Stage labels (Planning → Rendering)
├── video-player/
│   ├── VideoPlayer.tsx        # Main player component
│   ├── PlayerControls.tsx     # Custom controls (play, replay 10s, speed)
│   ├── ChapterMarkers.tsx     # Segment markers on progress bar
│   ├── CaptionOverlay.tsx     # Burned-in caption display
│   └── QuizOverlay.tsx        # Quiz checkpoint that pauses video
├── quiz/
│   ├── QuizCard.tsx           # Question + 4 options
│   ├── QuizResult.tsx         # Answer reveal + explanation
│   └── QuizSummary.tsx        # End-of-lesson quiz results
└── shared/
    ├── LoadingSkeleton.tsx
    ├── ErrorBoundary.tsx
    └── EmptyState.tsx
```

---

## 3. Key Component Specifications

### 3.1 GenerateForm

- Single text input for topic (max 200 chars, visible char counter)
- Level selector: 3 radio-style buttons (Beginner / Intermediate / Advanced)
- Submit button disabled while a job is already in progress
- On submit: POST `/api/v1/lessons/generate` → redirect to `/jobs/:job_id`
- Loading state during submission
- Error state with retry

### 3.2 JobStatusPoller

- Polls `GET /api/v1/lessons/jobs/:job_id` every 5 seconds
- Shows animated progress indicator with stage labels:
  - Planning your lesson... (0-10%)
  - Writing the script... (10-25%)
  - Designing scenes... (25-40%)
  - Generating animations... (40-60%)
  - Adding narration... (60-75%)
  - Quality checking... (75-85%)
  - Rendering video... (85-95%)
  - Almost there... (95-100%)
- On completion: auto-redirect to `/lessons/:lesson_id`
- On failure: show error message with retry button

### 3.3 VideoPlayer

- Built on `video.js` with `@videojs/http-streaming` for HLS
- Custom controls:
  - Play/pause
  - Replay last 10 seconds (critical for ADHD)
  - Chapter markers on progress bar (one per segment)
  - Speed selector: 0.75x, 1x, 1.25x, 1.5x
  - Caption toggle (on by default)
- Quiz overlay: pauses video at checkpoint timestamp, renders quiz question, resumes on answer
- Progress saved every 10 seconds via `PUT /watch/:id/progress`
- Keyboard shortcuts: space (play/pause), left arrow (-10s), right arrow (+10s)
- Remember watch position on return

---

## 4. State Management

### 4.1 Stores (Zustand)

```typescript
// lib/stores/auth-store.ts
interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  checkAuth: () => Promise<void>;
}

// lib/stores/player-store.ts
interface PlayerState {
  isPlaying: boolean;
  currentTime: number;
  duration: number;
  playbackRate: number;
  captionsEnabled: boolean;
  currentSegment: number;
  setPlaybackRate: (rate: number) => void;
  toggleCaptions: () => void;
}

// lib/stores/quiz-store.ts
interface QuizState {
  activeQuizIndex: number | null;
  selectedOption: number | null;
  isAnswerRevealed: boolean;
  answers: Record<number, { selected: number; correct: boolean }>;
  startQuiz: (index: number) => void;
  submitAnswer: (option: number) => void;
  dismissQuiz: () => void;
}
```

### 4.2 Server State (React Query)

```typescript
// lib/api.ts
const api = {
  // Lessons
  generateLesson: (topic: string, level?: string) =>
    fetcher.post("/api/v1/lessons/generate", { topic, level }),

  getJobStatus: (jobId: string) =>
    fetcher.get(`/api/v1/lessons/jobs/${jobId}`),

  getLessons: (page: number = 1, limit: number = 12) =>
    fetcher.get(`/api/v1/lessons?page=${page}&limit=${limit}`),

  getLesson: (id: string) =>
    fetcher.get(`/api/v1/lessons/${id}`),

  deleteLesson: (id: string) =>
    fetcher.delete(`/api/v1/lessons/${id}`),

  // Watch
  startWatch: (lessonId: string) =>
    fetcher.post(`/api/v1/watch/${lessonId}/start`),

  updateProgress: (lessonId: string, position: number, percentage: number) =>
    fetcher.put(`/api/v1/watch/${lessonId}/progress`, { position_seconds: position, percentage }),

  completeWatch: (lessonId: string) =>
    fetcher.post(`/api/v1/watch/${lessonId}/complete`),

  // Quiz
  submitQuizAnswer: (lessonId: string, questionIndex: number, selectedOption: number) =>
    fetcher.post(`/api/v1/quiz/${lessonId}/attempt`, { question_index: questionIndex, selected_option: selectedOption }),

  getQuizResults: (lessonId: string) =>
    fetcher.get(`/api/v1/quiz/${lessonId}/results`),
};
```

---

## 5. Auth Flow

- JWT stored in httpOnly cookie (set by backend on login)
- No JWT in localStorage (XSS protection)
- Next.js middleware checks auth for `(dashboard)` route group
- Client-side auth check on app load via `GET /api/v1/auth/me`
- Unauthenticated users redirected to `/login`

```typescript
// middleware.ts
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

const protectedPaths = ["/dashboard", "/generate", "/jobs", "/lessons", "/settings"];

export function middleware(request: NextRequest) {
  const path = request.nextUrl.pathname;
  const isProtected = protectedPaths.some((p) => path.startsWith(p));

  if (isProtected && !request.cookies.has("access_token")) {
    return NextResponse.redirect(new URL("/login", request.url));
  }
  return NextResponse.next();
}

export const config = { matcher: ["/((?!api|_next|favicon.ico).*)"] };
```

---

## 6. TailwindCSS Design Tokens

```css
/* globals.css */
@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  /* ADHD-friendly palette: high contrast, semantic colors */
  --color-surface: oklch(97% 0.005 260);
  --color-surface-elevated: oklch(100% 0 0);
  --color-text-primary: oklch(18% 0.005 260);
  --color-text-secondary: oklch(45% 0.01 260);
  --color-accent: oklch(62% 0.2 255);
  --color-accent-hover: oklch(55% 0.22 255);
  --color-success: oklch(65% 0.2 145);
  --color-warning: oklch(75% 0.18 85);
  --color-error: oklch(60% 0.22 25);

  /* Concept color mapping (same concept = same color everywhere) */
  --concept-1: oklch(65% 0.2 255);   /* blue */
  --concept-2: oklch(65% 0.2 145);   /* green */
  --concept-3: oklch(70% 0.18 85);   /* amber */
  --concept-4: oklch(60% 0.22 25);   /* red */
  --concept-5: oklch(60% 0.2 310);   /* purple */

  /* Typography */
  --text-display: clamp(2.5rem, 1rem + 5vw, 4.5rem);
  --text-heading: clamp(1.5rem, 1rem + 2vw, 2.5rem);
  --text-body: clamp(1rem, 0.95rem + 0.25vw, 1.125rem);
  --text-caption: 0.875rem;

  /* Spacing */
  --space-section: clamp(3rem, 2rem + 4vw, 6rem);

  /* Motion */
  --duration-fast: 150ms;
  --duration-normal: 300ms;
  --ease-out-expo: cubic-bezier(0.16, 1, 0.3, 1);
}

@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

## 7. Page Specifications

| Page | Route | Auth | Key Features |
|------|-------|------|-------------|
| Landing | `/` | No | Hero, CTA, feature cards, pricing |
| Login | `/login` | No | Email/password form, link to register |
| Register | `/register` | No | Email/password form, link to login |
| Dashboard | `/dashboard` | Yes | Lesson grid (12/page), empty state CTA |
| Generate | `/generate` | Yes | Topic input, level selector, submit |
| Job Status | `/jobs/:job_id` | Yes | Polling progress, auto-redirect on complete |
| Watch Lesson | `/lessons/:id` | Yes | Video player, quiz overlay, captions |
| Quiz Results | `/lessons/:id/quiz` | Yes | Score, question-by-question review |
| Settings | `/settings` | Yes | Account info, change password |

---

## 8. Loading and Error States

- Every data-fetching page has a loading skeleton (not spinner)
- API errors shown as toast notifications
- Video player has a loading state for HLS buffer
- Job failure shows error message + retry button
- Network error shows "connection lost" banner with auto-retry

---

## 9. Task Checklist

### Setup
- [M] Next.js 15 App Router scaffold with TypeScript strict
- [M] TailwindCSS + shadcn/ui initialized
- [M] Zustand + React Query providers in root layout
- [M] API client with auth token handling
- [M] Design tokens (CSS custom properties)

### Pages
- [M] Landing page
- [M] Login page with form validation
- [M] Register page with form validation
- [M] Dashboard with lesson grid
- [M] Generate page with topic form
- [M] Job status polling page
- [M] Lesson watch page with video player
- [M] Quiz results page
- [S] Settings page

### Components
- [M] VideoPlayer with HLS, custom controls, quiz overlay
- [M] JobStatusPoller with animated progress
- [M] GenerateForm with char counter and level selector
- [M] LessonCard with thumbnail, status badge, date
- [M] QuizOverlay that pauses video
- [S] ChapterMarkers on progress bar
- [S] CaptionOverlay (styled captions)
- [C] Picture-in-picture mode

### Quality
- [M] Responsive design (320px to 1920px)
- [M] Accessibility: keyboard nav, WCAG AA contrast, reduced motion
- [M] Loading skeletons for all data-fetching pages
- [M] Error boundaries
- [S] Keyboard shortcuts for video player
- [S] Watch position persistence
