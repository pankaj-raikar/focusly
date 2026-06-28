# Post-MVP Evolution

## Purpose
Define controlled evolution paths after Focusly MVP, including Path B to Path A expansion, optional services, uploads, educator features, mobile, and institutional licensing.

## Owner Skills
- Primary: project-planner
- Supporting: llm-application-dev, backend-development, frontend-design, market-research, security-review, code-review

## Expected Output
Post-MVP ideas are captured without contaminating MVP architecture or runtime dependencies.

## Path B to Path A Evolution
Path A, the 33-agent pipeline, is a future evolution path only. It should be considered when MVP telemetry shows repeated bottlenecks in a Path B node.

Potential splits:
| Path B Node | Split When | Possible Path A Agents |
|---|---|---|
| R02 Planner | Planning quality varies by topic type | curriculum planner, misconception analyst, objective mapper. |
| R03 Scriptwriter | Script pacing or tone needs specialization | hook writer, segment writer, summary writer, ADHD pacing editor. |
| R05 SceneDirector | Visual design bottlenecks emerge | metaphor designer, layout designer, accessibility designer. |
| R06 CodeGenerator | Remotion and Manim failures differ | Remotion generator, Manim generator, syntax fixer, render preflight. |
| R09 QAGate | QA reports miss specialized issues | educational QA, sync QA, visual QA, code QA, safety QA. |

## When to Split Agents
Split only when:
- A single node has high retry rate or long latency.
- Failures are attributable to separable responsibilities.
- New contracts can be tested independently.
- The added coordination cost is lower than the quality or reliability gain.

## Post-MVP External Services
Allowed only after MVP:
- Observability SaaS such as Sentry.
- Asset APIs for licensed images or icons.
- Music or sound-effect APIs with licensing review.
- Document extraction services for PDF/PPTX upload.

Each addition requires security review, cost review, privacy review, fallback behavior, tests, and documentation updates.

## Asset APIs
Asset APIs may support richer visuals after MVP, but generated code and internal diagrams remain the default. Any asset integration must store license metadata with artifacts and avoid exposing learner prompts to unnecessary third parties.

## Sentry and Observability
Post-MVP observability may add error tracking, tracing, and performance dashboards. MVP runbooks and logs should be implemented first so SaaS observability enhances rather than replaces operational discipline.

## PDF/PPTX Upload
Future upload support may allow educators or learners to upload source material. This requires file validation, malware scanning strategy, extraction pipeline, data retention policy, and new requirements for source-grounded generation.

## Educator Portal
Potential features:
- Class lesson libraries.
- Assignment links.
- Review and approve generated lessons.
- Student progress insights.
- Shared templates for ADHD-friendly lesson structure.

## Mobile App
Mobile should follow after web engagement is validated. A mobile app should reuse backend contracts and HLS/caption assets rather than introducing a second generation pipeline.

## Institutional Licensing
Institutional licensing may add organizations, roles, SSO, audit logs, retention policies, and billing. This requires a separate product and security planning pass.

## Acceptance Criteria
- Path A is clearly post-MVP only.
- Future services are optional and gated by review.
- Post-MVP features do not alter MVP runtime service constraints.
- Evolution rules explain when specialization is justified.

## Related Docs
- [Canonical Stack and Skill Routing](./01-canonical-stack-and-skill-routing.md)
- [LangGraph Agent Pipeline](./05-langgraph-agent-pipeline.md)
- [Future Agent Build Rules](./12-future-agent-build-rules.md)
