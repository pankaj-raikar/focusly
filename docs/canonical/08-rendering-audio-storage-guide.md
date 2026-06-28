# Rendering, Audio, and Storage Guide

## Purpose
Define how Focusly generates scenes, narration, captions, HLS outputs, and private storage artifacts using Remotion, Manim, FFmpeg, ElevenLabs, and Cloudflare R2.

## Owner Skills
- Primary: llm-application-dev
- Supporting: python-development, backend-development, systematic-debugging, security-review, webapp-testing

## Expected Output
Rendering agents can produce deterministic media artifacts without adding non-canonical asset or music services.

## Remotion Scene Strategy
- R06 generates typed Remotion scene specs and TSX components for layout-driven animation.
- Scene props come from `scene_manifest`, script segments, design tokens, and timings.
- Scenes must avoid remote image dependencies in MVP.
- Validate TSX syntax before render.
- Keep one primary concept per scene to support ADHD pacing.

## Manim Scene Strategy
- Use Manim for algorithm, math, graph, and coordinate-based explanations.
- R06 outputs Manim scene specs and Python scene files.
- Validate Python syntax and render a low-resolution smoke preview before full render.
- Keep Manim outputs as intermediate video clips for FFmpeg stitching.

## FFmpeg Stitching and HLS Segmentation
Pipeline steps:
1. Normalize Remotion and Manim clips to common resolution, FPS, pixel format, and audio settings.
2. Align narration audio with scene timeline from R08.
3. Concatenate clips and audio into a master MP4.
4. Generate HLS playlist and segments.
5. Preserve captions as external WebVTT/SRT tracks.

MVP output:
```text
master.mp4
hls/master.m3u8
hls/segment_000.ts
captions/captions.vtt
captions/captions.srt
render_manifest.json
```

## ElevenLabs TTS Strategy
- R07 sends narration script chunks to ElevenLabs.
- Store raw audio and normalized narration audio in R2.
- Capture or derive word timestamps when supported by the integration path.
- Retry transient TTS failures with bounded exponential backoff.
- Never call ElevenLabs from the browser.

## WebVTT/SRT Captions Strategy
- R08 generates captions from narration and word timings.
- WebVTT is the primary player caption format.
- SRT is generated for export and fallback.
- Captions must be short enough for readability and aligned to segment pacing.
- Burned-in captions are optional only for export or fallback renders.

## Cloudflare R2 Storage Strategy
- Store all artifacts under the key structure in `04-api-and-data-contracts.md`.
- Keep buckets private.
- Upload metadata rows to `lesson_artifacts` after successful upload.
- Use content types: `application/vnd.apple.mpegurl`, `video/mp2t`, `text/vtt`, `application/x-subrip`, `audio/mpeg`, `application/json`.

## Private Signed HLS Access Model
- Playback API verifies user owns the lesson.
- API returns short-lived signed URLs for manifest and captions.
- Segment access must be signed through rewritten manifests or an authenticated proxy.
- Signed URL TTL should be short and refreshable through the playback endpoint.

## Render Timeout and Fallback Behavior
| Stage | Timeout | Fallback |
|---|---:|---|
| Remotion render | per scene budget | Retry R10 once; route to R06 if syntax/render code issue. |
| Manim render | per scene budget | Retry lower quality preview; route to R06 if code issue. |
| FFmpeg stitch | total media budget | Retry command once with logged args redacted. |
| HLS upload | bounded storage timeout | Retry R2 upload; mark job failed if persistent. |

## MVP Rule: No External Asset or Music APIs
MVP must not use Unsplash, Pixabay, LottieFiles, external music APIs, or any additional runtime media API. Visuals must be generated from code, shapes, text, diagrams, and canonical rendering tools.

Reasoning: External asset APIs add licensing, moderation, availability, and privacy risks before MVP learning value is validated.

## Acceptance Criteria
- Final successful jobs produce HLS, WebVTT, SRT, render manifest, and artifact rows.
- Captions are external toggleable tracks.
- R2 objects are private and accessed through authorized signed playback metadata.
- No non-canonical media or asset APIs are used in MVP.

## Related Docs
- [API and Data Contracts](./04-api-and-data-contracts.md)
- [LangGraph Agent Pipeline](./05-langgraph-agent-pipeline.md)
- [Security and Reliability Guide](./10-security-and-reliability-guide.md)
