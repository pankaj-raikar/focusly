# Future Agent Build Rules

## Purpose
Set mandatory rules for future coding agents building Focusly so implementation stays aligned with the canonical MVP architecture.

## Owner Skills
- Primary: project-planner
- Supporting: code-review, verification-before-completion, test-driven-development, systematic-debugging, security-review

## Expected Output
Future agents know which skills to invoke, which MVP changes are forbidden, how docs must be updated, and what verification is required.

## Skill Invocation Rules
| Change Type | Invoke Before Work |
|---|---|
| Requirements, roadmap, task planning | project-planner |
| API endpoint, FastAPI service, worker | backend-development, python-development |
| Database model or migration | database-design, database-migrations |
| LangGraph, LangChain, prompts, parsers | llm-application-dev, out-of-box-prompt |
| Frontend page or component | javascript-typescript, frontend-design |
| Visual polish or design system | design-engineer, frontend-design |
| Auth, cookies, secrets, ownership | security-review |
| E2E flow | playwright, webapp-testing |
| New feature or bug fix | test-driven-development |
| Bug investigation | systematic-debugging |
| Pre-merge review | code-review |
| Completion claim | verification-before-completion |

## Forbidden MVP Changes
- Do not replace Path B with Path A before MVP completion.
- Do not add Unsplash, Pixabay, LottieFiles, Sentry, music APIs, or extra runtime APIs.
- Do not use auth tokens in localStorage.
- Do not use burned-in captions as the primary caption experience.
- Do not run long generation or rendering work inside FastAPI request handlers.
- Do not store binary media in PostgreSQL.
- Do not bypass PostgreSQL JSONB pipeline state persistence.
- Do not use a non-LangGraph orchestrator for the MVP pipeline.
- Do not use a non-LangChain prompt/chains/parser layer for MVP LLM calls.

## Documentation Update Rules
- If an API shape changes, update `04-api-and-data-contracts.md` and affected tests.
- If a requirement changes, update `03-product-requirements.md` and `11-8-week-implementation-plan.md`.
- If graph topology or node output changes, update `05-langgraph-agent-pipeline.md`.
- If storage keys or playback behavior changes, update `08-rendering-audio-storage-guide.md`.
- If auth, rate limits, or privacy behavior changes, update `10-security-and-reliability-guide.md`.

## Testing Requirements
- Backend changes require pytest or pytest-asyncio coverage.
- Frontend changes require Vitest or Playwright coverage depending on scope.
- Agent changes require mocked-Claude contract tests.
- Audio changes require mocked ElevenLabs tests.
- Storage changes require R2 mock tests.
- Media changes require rendering smoke tests.

## Review Requirements
- Review must prioritize bugs, regressions, security, contract drift, missing tests, and non-canonical dependencies.
- Any external service addition is a blocking finding during MVP.
- Any auth token localStorage usage is a blocking finding.
- Any missing ownership check on lesson/job/artifact access is a blocking finding.

## Verification Requirements
Before claiming completion, the agent must report:
- Files changed.
- Tests or checks run.
- Tests not run and why.
- Contract docs updated or confirmation that no contract changed.
- Known residual risks.

## Acceptance Criteria
- Future agents have explicit skill routing before each type of change.
- Forbidden MVP changes are unambiguous.
- Documentation, testing, review, and verification requirements are enforceable.

## Related Docs
- [Canonical Stack and Skill Routing](./01-canonical-stack-and-skill-routing.md)
- [Testing and Verification Guide](./09-testing-and-verification-guide.md)
- [Security and Reliability Guide](./10-security-and-reliability-guide.md)
