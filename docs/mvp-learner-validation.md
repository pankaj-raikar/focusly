# Focusly MVP Learner Validation

## Goal

Test whether target learners can independently generate, watch, and answer a quiz for a short animated lesson.

## Participants

Recruit five learners who identify with attention or focus difficulties. Run sessions individually. Do not explain the interface unless the learner is unable to continue.

## Session script

1. Ask the learner to choose a topic they genuinely want to understand.
2. Give them the Focusly URL and say: “Create and watch a lesson about your topic.”
3. Observe without directing them.
4. After playback, ask:
   - What were the three main ideas?
   - Did the visuals help or distract?
   - Was the narration too fast, too slow, or comfortable?
   - Did captions help?
   - Would you use this for another topic?
5. Record the metrics below.

## Pass criteria

- All five learners create and start a lesson without developer intervention.
- At least three learners finish playback and answer the quiz.
- At least three learners correctly recall two lesson ideas.
- No learner is blocked by generation, playback, captions, or quiz controls.

## Evidence to retain

- One row per learner in `docs/mvp-learner-validation.csv`.
- API logs containing OpenAI token usage and stage timings.
- Any failed job ID and its logged failure stage.
- Concise notes for repeated usability issues; omit personal identifying details.

## Decision rules

- If fewer than three learners finish, fix the earliest shared abandonment point.
- If generation failures affect two sessions, improve that stage before adding features.
- If learners finish but cannot recall two ideas, revise lesson prompts and scene density.
- If the flow passes, the MVP validation gate is complete; defer infrastructure listed in the implementation plan.
