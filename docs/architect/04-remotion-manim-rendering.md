# Focusly — Remotion + Manim Rendering Service Architecture

## 1. Rendering Pipeline Overview

```
Scene Manifest (from A10)
    │
    ├─► Remotion scenes ──► A15 generates .tsx ──► Node.js renders ──► scene.mp4
    │
    ├─► Manim scenes ──► A16 generates .py ──► Python renders ──► scene.mp4
    │
    └─► D3/ThreeJS ──► A17/A18 generates ──► Embedded in Remotion ──► scene.mp4

All scene.mp4s ──► FFmpeg concat + mux audio + burn captions ──► final.mp4 ──► HLS ──► R2
```

---

## 2. Remotion Architecture

```
packages/video-engine/
├── src/
│   ├── Root.tsx                       # Remotion root (registers all compositions)
│   ├── compositions/
│   │   ├── KineticText.tsx            # Word-by-word animated text
│   │   ├── ImageOverlay.tsx           # Full-bleed image + animated caption
│   │   ├── BulletReveal.tsx           # Sequential bullet point reveal
│   │   ├── ConceptMap.tsx             # Node-connection animated diagram
│   │   ├── AlgorithmStepThrough.tsx   # Embeds Manim output as <Video>
│   │   ├── D3Chart.tsx                # D3 chart in Remotion canvas
│   │   ├── QuizScene.tsx              # Pause + question + options + reveal
│   │   ├── TransitionScene.tsx        # Between-segment breather
│   │   ├── HookScene.tsx              # Opening attention capture
│   │   ├── SummaryScene.tsx           # Closing concept recap
│   │   └── ProgressMilestone.tsx      # Micro-reward at segment end
│   ├── lib/
│   │   ├── design-tokens.ts           # Shared colors, fonts, spacing
│   │   ├── adhd-rules.ts              # Hardcoded ADHD constraints
│   │   └── types.ts                   # Scene prop type definitions
│   └── render.ts                      # CLI entrypoint for Node.js subprocess
├── remotion.config.ts
└── package.json
```

### 2.1 Composition Props Interface

```typescript
// lib/types.ts
interface KineticTextProps {
  text: string;
  emphasisWords: string[];
  color: string;
  fontSize: number;           // min 32px
  durationFrames: number;     // at 30fps
  backgroundColor: string;
}

interface ImageOverlayProps {
  imageSrc: string;           // R2 URL or local path
  caption: string;
  captionColor: string;
  entryAnimation: "fade" | "slide" | "zoom";
  durationFrames: number;
}

interface QuizSceneProps {
  question: string;
  options: [string, string, string, string];
  correctIndex: number;
  explanations: [string, string, string, string];
  conceptColor: string;
  durationFrames: number;
}
```

### 2.2 ADHD Rules Enforcement

```typescript
// lib/adhd-rules.ts
export const ADHD_RULES = {
  maxSegmentDurationSeconds: 30,
  maxWordsPerTextElement: 7,
  minFontSizePxAt1080p: 32,
  minContrastRatio: 4.5,            // WCAG AA
  maxConceptsPerSegment: 2,
  progressBarAlwaysVisible: true,
  pauseAfterHardConceptMs: 2000,
  microRewardEveryNSegments: 3,
  maxInformationDensityScore: 0.7,
} as const;

// Enforced in every composition:
export function validateSceneProps(props: Record<string, unknown>): boolean {
  // Check font sizes, word counts, duration limits
  // Throw or warn on violation — never silently allow
}
```

### 2.3 Rendering Process

```
A29 RenderOrchestratorAgent
    │
    ├── For each scene (max 3 concurrent):
    │       │
    │       ▼
    │   Spawn Node.js child process:
    │   npx remotion render src/render.ts <composition> <output.mp4> --props=<JSON>
    │       │
    │       ├── Chromium headless browser
    │       ├── React renders each frame
    │       ├── FFmpeg encodes to MP4
    │       └── Output: scene_N.mp4
    │
    ├── Upload each scene_N.mp4 to R2
    └── Store R2 paths in state.rendered_scene_paths
```

---

## 3. Manim Architecture

### 3.1 Render Flow

```
A16 ManimCoderAgent
    │
    ├── Generate Python code (Scene subclass)
    ├── Validate: AST parse + class check + construct method
    │
    ▼
ManimRenderService
    │
    ├── Write code to temp file
    ├── Spawn subprocess: manim -qh scene.py ClassName
    ├── Timeout: 90 seconds
    │
    ├── Success ──► scene.mp4
    │       │
    │       ▼
    │   FFmpeg convert (match Remotion specs):
    │   - Scale to 1920x1080
    │   - 30fps
    │   - H.264 libx264
    │   - AAC 128kbps
    │   - yuv420p pixel format
    │
    ├── Failure ──► Fallback to Remotion ConceptMap
    │
    └── Upload converted mp4 to R2
```

### 3.2 Resource Limits

| Resource | Limit | Reason |
|----------|-------|--------|
| Concurrent Manim renders | 2 | CPU-intensive (Cairo + LaTeX) |
| Timeout per render | 90s | Prevent runaway processes |
| Max scene complexity | 50 play/wait calls | Prevent 10-minute renders |
| Memory per process | 2GB | LaTeX can spike memory |

---

## 4. FFmpeg Stitching (A30)

```
A30 FFmpegStitchAgent
    │
    ├── Input: rendered_scene_paths[], final_audio_path, caption_srt
    │
    ├── Step 1: Concat scenes
    │   ffmpeg -f concat -safe 0 -i filelist.txt -c copy scenes_combined.mp4
    │
    ├── Step 2: Mux audio
    │   ffmpeg -i scenes_combined.mp4 -i mixed_audio.mp3 -c:v copy -c:a aac -shortest output.mp4
    │
    ├── Step 3: Burn captions
    │   ffmpeg -i output.mp4 -vf "subtitles=captions.srt:force_style='FontSize=24'" final.mp4
    │
    ├── Step 4: HLS segmentation
    │   ffmpeg -i final.mp4 -profile:v baseline -level 3.0 \
    │     -start_number 0 -hls_time 6 -hls_list_size 0 \
    │     -f hls master.m3u8
    │
    ├── Step 5: Generate thumbnail
    │   ffmpeg -i final.mp4 -ss 50% -vframes 1 thumbnail.jpg
    │
    ├── Upload all to R2
    │   videos/{job_id}/master.m3u8
    │   videos/{job_id}/segment_000.ts
    │   videos/{job_id}/thumbnail.jpg
    │
    └── Return: final_video_path, hls_playlist_path, thumbnail_path
```

---

## 5. Video Delivery

```
User requests lesson
    │
    ▼
GET /lessons/:id
    │
    ├── Load lesson record from PostgreSQL
    ├── Generate signed R2 URL (1h expiry)
    │
    └── Return: { video_url, hls_url, thumbnail_url, expires_at }
            │
            ▼
    VideoPlayer component
        │
        ├── video.js with HLS plugin
        ├── Load master.m3u8 from signed URL
        ├── Cloudflare CDN serves .ts segments
        └── Custom controls: replay 10s, speed, captions, quiz overlay
```

---

## 6. Task Checklist

### Remotion
- [M] Remotion project scaffolded with 11 compositions
- [M] ADHD rules hardcoded in every composition
- [M] Design tokens shared across compositions
- [M] CLI render entrypoint (Node.js subprocess)
- [M] A29 RenderOrchestrator spawns child processes
- [M] Max 3 concurrent Remotion renders

### Manim
- [M] Docker image with Cairo, Pango, LaTeX, FFmpeg
- [M] ManimRenderService with 90s timeout
- [M] Code validation (AST + class + construct)
- [M] FFmpeg conversion to match Remotion specs
- [M] Fallback: Manim failure → Remotion static diagram

### FFmpeg
- [M] Scene concatenation
- [M] Audio muxing
- [M] Caption burning
- [M] HLS segmentation (6s segments)
- [M] Thumbnail generation

### Delivery
- [M] R2 upload for all video assets
- [M] Signed URL generation (1h expiry)
- [M] video.js player with HLS
- [S] Chapter markers on progress bar
- [S] Keyboard shortcuts
