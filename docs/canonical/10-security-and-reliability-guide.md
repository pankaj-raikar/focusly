# Security and Reliability Guide

## Purpose
Define MVP security controls, reliability policies, timeout/retry behavior, R2 privacy, secret handling, and operational runbooks.

## Owner Skills
- Primary: security-review
- Supporting: backend-development, database-design, systematic-debugging, code-review, verification-before-completion

## Expected Output
Implementation agents can build auth, authorization, input safety, render isolation, and reliability behavior without making ad hoc security decisions.

## JWT RS256 httpOnly Cookie Auth
- Sign access JWTs with RS256 private key from environment.
- Verify with configured public key.
- Store JWT only in `focusly_session` httpOnly cookie.
- Include `sub`, `iat`, `exp`, `iss`, `aud`, `jti`.
- Use short expiration and explicit logout cookie clearing.

## SameSite and Secure Cookie Rules
- Production cookies: `Secure`, `HttpOnly` for session, `SameSite=Lax`, path `/`.
- Development may omit `Secure` only for local HTTP.
- CSRF cookie is readable by JS for double-submit but contains no auth credential.

## CSRF and CORS Strategy
- Require `X-CSRF-Token` on state-changing requests.
- Validate header against `focusly_csrf` cookie.
- CORS allowlist must include only deployed frontend origins.
- Do not allow wildcard credentials.

## User Data Isolation
- Every lesson, job, pipeline state, artifact, and event access must join back to `user_id`.
- Playback signed URLs require ownership checks.
- R2 object keys include `user_id` and are not security boundaries by themselves.

## Input Sanitization
- Validate topic length, allowed preferences, and duration bounds.
- Treat all generated code as untrusted until validated and sandboxed.
- Do not render user-provided HTML.
- Redact prompts, provider payloads, signed URLs, and secrets from user-visible errors.

## Rate Limits
| Surface | Limit Strategy |
|---|---|
| Auth endpoints | IP-based low threshold and lockout delay. |
| Lesson generation | Per-user daily and rolling-window limits. |
| Job polling | Higher limit but bounded to prevent abuse. |
| Playback signing | Per-user limit; short TTL refresh allowed. |

## Render Sandboxing
- Run render jobs in a controlled worker workspace.
- Use per-job temporary directories.
- Disallow network access from generated scene code where feasible.
- Enforce process timeouts and max output sizes.
- Delete temp directories after artifact upload or failed cleanup grace period.

## Timeout Policy
| Operation | Policy |
|---|---|
| Claude node call | Per-call timeout and structured output repair retry. |
| ElevenLabs call | Per-request timeout and transient retry. |
| Remotion/Manim render | Per-scene timeout. |
| FFmpeg | Command timeout based on target duration. |
| ARQ job | Total generation timeout. |

## Retry Policy
- Retry transient provider and storage failures with bounded exponential backoff.
- Retry invalid structured outputs through parser repair before regenerating full node output.
- Do not retry authorization, validation, or forbidden external-service errors.
- Persist retry attempts in job state.

## R2 Privacy
- Buckets are private.
- No public-read media objects in MVP.
- Signed URLs are short-lived.
- Artifact rows track content type, size, and owning lesson.

## Secret Management
- Store Claude, ElevenLabs, R2 credentials, JWT keys, database URLs, and Redis URLs in environment variables.
- Never commit `.env` files.
- Do not log secrets or signed URLs.
- Key rotation requires invalidating old JWT `jti` values when necessary.

## Reliability Runbook
| Symptom | First Checks | Recovery |
|---|---|---|
| Job stuck `queued` | ARQ worker health, Redis connectivity | Restart worker, requeue eligible job. |
| Job stuck `running` | Last `job_events`, worker logs, timeout marker | Mark failed if timeout exceeded; allow retry. |
| Render failed | R10 logs, syntax validation report, temp artifacts | Route to R06 if code-related; otherwise retry R10 once. |
| Playback 403 | Ownership check, signed URL TTL | Refresh playback metadata after auth verification. |
| Captions missing | R08 output, artifact rows, R2 keys | Regenerate R08/R10 if source audio exists. |

## Acceptance Criteria
- Auth never uses localStorage tokens.
- State-changing requests have CSRF protection.
- Users cannot access other users' jobs, lessons, artifacts, or playback URLs.
- Render execution is bounded by workspace, timeout, and size controls.
- Reliability runbooks exist for stuck jobs, render failures, and playback failures.

## Related Docs
- [API and Data Contracts](./04-api-and-data-contracts.md)
- [Backend Implementation Guide](./06-backend-implementation-guide.md)
- [Testing and Verification Guide](./09-testing-and-verification-guide.md)
