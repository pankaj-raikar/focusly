# Focusly

Focusly turns a topic into a short animated lesson with captions, progress tracking, and quiz checkpoints.

## Stack

- FastAPI backend
- Next.js frontend
- Remotion video package
- pnpm workspace with uv-managed Python dependencies

## Setup

```bash
pnpm install
cp .env.example .env
```

Fill in `.env` with local API keys and settings. `.env` files are intentionally ignored by Git.

## Run

```bash
pnpm run dev
```

The API runs on `http://localhost:8000` and the web app runs on `http://localhost:3000`.

## Test

```bash
pnpm run test
```

## Outputs

Generated showcase assets live in `outputs/`, including screenshots, PDFs, slide decks, and videos.
