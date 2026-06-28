# Focusly — Security Architecture

## 1. Threat Model

| Threat | Vector | Mitigation |
|--------|--------|------------|
| Credential theft | XSS stealing JWT | httpOnly cookies (JWT never in JS) |
| Unauthorized access | Direct API calls | JWT RS256 validation on every request |
| Data leakage | User A sees User B's lesson | Every DB query scoped to authenticated user_id |
| Video piracy | Sharing video URLs | Signed R2 URLs with 1h expiry |
| Rate abuse | Excessive generation requests | Redis sliding window: 10/day/user |
| Prompt injection | Harmful content in topic input | Input sanitization before passing to AI agents |
| AI-generated NSFW | Agent produces harmful content | Output content check before render |
| Secret exposure | API keys in code/logs | Environment variables only, never logged |
| SQL injection | Malicious DB queries | SQLAlchemy ORM + parameterized queries |
| CSRF | Cross-site request forgery | SameSite=Strict on cookies, CORS whitelist |
| DoS | Flood the queue | Rate limiting + concurrent render limit (3) |
| Supply chain | Compromised dependency | Lockfile (uv.lock, pnpm-lock.yaml), Dependabot |

---

## 2. Authentication Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    Auth Flow                                  │
│                                                              │
│  Register                                                    │
│  ┌──────────┐    POST /auth/register                        │
│  │ email    │───► Validate email format                      │
│  │ password │───► bcrypt hash (cost=12)                      │
│  └──────────┘───► Create user in PostgreSQL                 │
│                                                              │
│  Login                                                       │
│  ┌──────────┐    POST /auth/login                           │
│  │ email    │───► Find user by email                        │
│  │ password │───► bcrypt.verify(password, hash)             │
│  └──────────┘───► Create JWT RS256 (15 min)                 │
│              ───► Create refresh token UUID (7 days)         │
│              ───► Set httpOnly cookies:                      │
│                   access_token=...; HttpOnly; SameSite=Strict│
│                   refresh_token=...; HttpOnly; SameSite=Strict│
│                                                              │
│  Refresh                                                     │
│  POST /auth/refresh                                         │
│  ├── Read refresh_token from cookie                          │
│  ├── Validate: exists in DB, not expired                     │
│  ├── Rotate: delete old, create new refresh token            │
│  └── Issue new access_token                                  │
│                                                              │
│  Protected Route                                             │
│  Any authenticated endpoint                                  │
│  ├── Read access_token from cookie                           │
│  ├── Decode JWT RS256 (verify signature)                     │
│  ├── Extract user_id from "sub" claim                        │
│  └── Load user from DB, attach to request                    │
└──────────────────────────────────────────────────────────────┘
```

### 2.1 Token Specifications

| Property | Access Token | Refresh Token |
|----------|-------------|---------------|
| Format | JWT RS256 | UUID v4 |
| Expiry | 15 minutes | 7 days |
| Storage | httpOnly cookie | httpOnly cookie |
| SameSite | Strict | Strict |
| Secure | true (production) | true (production) |
| Rotation | On refresh | On each refresh |
| Revocation | Expiry-based | Delete from DB |

### 2.2 Password Policy

- Minimum 8 characters
- Stored as bcrypt hash, cost factor 12
- Never logged, never returned in API responses
- Password reset via time-limited token (Phase 2)

---

## 3. Authorization Architecture

```
Every API endpoint enforces:
1. Authentication (valid JWT)
2. Ownership (user_id match)
3. Rate limiting (per-user limits)

GET /lessons/:id
    ├── Auth: valid JWT → user_id
    ├── Query: SELECT * FROM lessons WHERE id=:id AND user_id=:user_id
    ├── Not found → 404 (don't reveal existence)
    └── Found → return lesson with signed video URL

DELETE /lessons/:id
    ├── Auth: valid JWT → user_id
    ├── Query: DELETE FROM lessons WHERE id=:id AND user_id=:user_id
    ├── Also: delete video from R2
    └── Not found → 404

/admin/* endpoints
    ├── Auth: valid JWT → user_id
    ├── Additional: user.is_admin == True
    └── Non-admin → 403 Forbidden
```

---

## 4. Input Sanitization

```python
# All user inputs sanitized before passing to AI agents

def sanitize_topic(topic: str) -> str:
    """Strip harmful content, limit length, validate characters."""
    topic = topic.strip()
    if not topic:
        raise ValidationError("Topic cannot be empty")
    if len(topic) > 200:
        raise ValidationError("Topic too long (max 200 characters)")
    # Block known harmful patterns
    blocked_patterns = ["ignore previous", "system prompt", "act as"]
    for pattern in blocked_patterns:
        if pattern.lower() in topic.lower():
            raise ValidationError("Invalid topic content")
    return topic
```

---

## 5. Video Access Control

```
User requests GET /lessons/:id
    │
    ├── Verify: user owns this lesson
    │
    ├── Generate signed R2 URL
    │   ├── Expires: 1 hour
    │   ├── Resource: videos/{job_id}/master.m3u8
    │   └── Signature: HMAC-SHA256
    │
    └── Return { hls_url: "https://r2...?X-Amz-Signature=..." }
            │
            ▼
    video.js loads HLS from signed URL
            │
            ▼
    R2 CDN serves segments (signature validated per request)
            │
            ▼
    After 1 hour: URL expires, user must request new one
```

No public video URLs exist. All video access requires an authenticated API call that generates a time-limited signed URL.

---

## 6. Network Security

```
Internet
    │
    ▼
Cloudflare (TLS termination, DDoS protection, WAF)
    │
    ▼
Railway (internal network)
    ├── API service (port 8000, internal only)
    ├── Worker service (no external port)
    ├── Web service (port 3000, proxied through Cloudflare)
    ├── PostgreSQL (internal only, port 5432)
    └── Redis (internal only, port 6379)
```

### Security Headers (enforced via Cloudflare)

```
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: camera=(), microphone=(), geolocation=()
```

---

## 7. Secret Management

| Secret | Storage | Access |
|--------|---------|--------|
| ANTHROPIC_API_KEY | Railway env vars | API + Worker only |
| ELEVENLABS_API_KEY | Railway env vars | Worker only |
| JWT private key | Railway env vars | API only |
| DB password | Railway managed plugin | Automatic |
| R2 credentials | Railway env vars | Worker only |
| Sentry DSN | Railway env vars | API + Worker + Web |

Rules:
- Never in source code, never in logs, never in error messages
- Rotated quarterly or on suspected exposure
- Different keys for staging vs production

---

## 8. Content Safety

```
Input → sanitize_topic() → block harmful patterns
    │
    ▼
Agent output → content check before render
    │
    ├── Check: no NSFW text in script
    ├── Check: no harmful imagery in assets
    ├── Check: quiz questions are educational
    │
    └── Fail → mark job as failed, alert admin
```

---

## 9. Security Checklist

- [M] JWT RS256 in httpOnly cookies (not localStorage)
- [M] bcrypt password hashing (cost=12)
- [M] User isolation on every DB query
- [M] Signed R2 URLs (1h expiry)
- [M] Rate limiting (10 generations/day/user)
- [M] Input sanitization before AI processing
- [M] HTTPS only (Cloudflare TLS)
- [M] Security headers (HSTS, nosniff, DENY)
- [M] SameSite=Strict on all cookies
- [M] Secrets in environment variables only
- [M] SQL injection prevention (SQLAlchemy ORM)
- [M] CORS whitelist (staging/production origins only)
- [S] Content safety checks on AI output
- [S] Dependabot for dependency vulnerabilities
- [S] Security audit after MVP launch
