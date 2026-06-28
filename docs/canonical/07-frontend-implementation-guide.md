# Frontend Implementation Guide

## Purpose
Guide the Next.js 15 frontend implementation for dashboard, generation, job progress, playback, state management, ADHD-friendly UX, and tests.

## Owner Skills
- Primary: javascript-typescript
- Supporting: frontend-design, design-engineer, playwright, webapp-testing, accessibility review, test-driven-development

## Expected Output
A responsive, accessible, ADHD-friendly frontend that consumes the canonical API and plays HLS with toggleable captions.

## App Router Structure
```text
apps/web/app/
  (auth)/login/page.tsx
  (auth)/register/page.tsx
  (app)/dashboard/page.tsx
  (app)/generate/page.tsx
  (app)/jobs/[jobId]/page.tsx
  (app)/lessons/[lessonId]/page.tsx
  layout.tsx
  providers.tsx
apps/web/components/
  app-shell.tsx
  generate-form.tsx
  job-progress.tsx
  lesson-card.tsx
  lesson-player.tsx
  quiz-checkpoint.tsx
apps/web/lib/
  api-client.ts
  query-keys.ts
  stores/player-store.ts
```

## React Component Structure
- Page components compose feature components and load server-safe shell data only.
- Feature components own form interactions, player behavior, and status displays.
- Shared shadcn/ui components provide accessible primitives.
- Use `data-testid` on critical E2E targets: generate submit, progress stage, player, captions toggle, quiz checkpoint.

## Zustand Store Boundaries
Use Zustand only for local UI state:
- Draft lesson prompt before submit.
- Player preferences: captions enabled, playback speed, reduced motion preference.
- Dismissed non-critical hints.

Do not put server-owned job state, lesson lists, or auth session data in Zustand.

## React Query Usage
Use React Query for:
- `useMeQuery()`
- `useLessonsQuery()`
- `useCreateLessonMutation()`
- `useJobQuery(jobId, { refetchInterval })`
- `usePlaybackQuery(lessonId)`

Job polling stops when status is `succeeded`, `failed`, or `cancelled`.

Reasoning: React Query handles cache invalidation, polling, retries, and stale data better than custom stores.

## shadcn/ui and Tailwind Usage
- Use shadcn/ui for buttons, cards, dialogs, forms, progress, tabs, and toasts.
- Use Tailwind tokens for spacing, high contrast, focus rings, and reduced-motion variants.
- Keep the visual direction calm, focused, and warm: low visual clutter, clear hierarchy, gentle motion.

## Video Player Guidance
- Wrap video.js in a `LessonPlayer` component.
- Input props: `hlsUrl`, `captions`, `quizCheckpoints`, `durationSeconds`.
- Add caption tracks from playback metadata and set English default when present.
- Render quiz checkpoint markers on the timeline and show checkpoint UI when playback reaches the timestamp.
- Respect reduced-motion settings for overlays.

## Page Guidance
| Page | Guidance | Acceptance Criteria |
|---|---|---|
| Dashboard | Show recent lessons, statuses, retryable failures, create CTA | User sees only owned lessons. |
| Generate | Single focused prompt form, duration and level controls, expectation copy | Valid submit creates job and navigates to job page. |
| Job | Progress stage, percent, current explanation, safe failure state | Polling stops on terminal state. |
| Player | HLS playback, captions, quiz checkpoints, recap panel | Captions toggle and quiz metadata work. |

## Accessibility and ADHD UX Rules
- One primary action per screen region.
- Use short labels and progressive disclosure.
- Avoid autoplay audio before explicit user action.
- Provide captions by default when available.
- Use visible focus states and keyboard-accessible controls.
- Support reduced motion.
- Break lesson status into clear stages instead of vague loading spinners.
- Avoid dense dashboards; group lessons by actionable status.

## Frontend Test Guidance
- Vitest: API client behavior, pure utilities, store reducers.
- Component tests: generate form validation, progress display, quiz overlay state.
- Playwright: register/login, create lesson, poll mocked job, playback page loads HLS metadata and captions.
- Accessibility checks: keyboard navigation, focus order, caption track visibility.

## Acceptance Criteria
- Frontend uses Zustand only for local UI state and React Query for server state.
- HLS playback uses video.js and caption tracks are toggleable.
- Core pages are responsive on desktop and mobile.
- ADHD UX requirements are visible in layout and interaction decisions.

## Related Docs
- [Product Requirements](./03-product-requirements.md)
- [API and Data Contracts](./04-api-and-data-contracts.md)
- [Testing and Verification Guide](./09-testing-and-verification-guide.md)
