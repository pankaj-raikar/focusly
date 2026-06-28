# Focusly MVP Runbook

## Requirements

- Node.js 22+ and pnpm 10
- Python 3.12 and uv
- FFmpeg and FFprobe
- An OpenAI API key

Kokoro runs locally. Its model and voice files download on the first narration run.

## Install

```bash
rtk pnpm install
cd apps/api
rtk proxy uv sync
cd ../..
cp .env.example .env
```

Set `OPENAI_API_KEY` in the root `.env`. The API loads this file automatically.

## Run

```bash
rtk pnpm dev
```

This starts the API at <http://localhost:8000> and web app at <http://localhost:3000>.
Enter a topic and keep the progress page open.

## Verify

```bash
rtk pnpm test
```

Run the real local media smoke test:

```bash
cd apps/api
RUN_MEDIA_SMOKE=1 rtk proxy uv run pytest tests/test_smoke_real_media.py -q
```

Run a real OpenAI generation only when `OPENAI_API_KEY` is set:

```bash
cd apps/api
RUN_OPENAI_INTEGRATION=1 rtk proxy uv run pytest tests/test_openai_real.py -q
```

## Failure checks

- Invalid topics return HTTP `422`.
- Missing jobs return HTTP `404`.
- Jobs with provider, TTS, or render errors end in `failed` with a safe message.
- Generated media is served only from the matching job directory.

## Cleanup

Generated jobs and the SQLite database are under `data/`:

```bash
rm -rf data
```

## Learner validation

Use [mvp-learner-validation.md](./mvp-learner-validation.md) for the five required sessions and record results in `mvp-learner-validation.csv`.
