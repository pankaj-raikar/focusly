import json
import os
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

from .config import Settings, load_settings

Runner = Callable[..., subprocess.CompletedProcess[Any]]


def render_lesson(
    lesson_path: Path,
    narration_path: Path,
    output_path: Path,
    *,
    settings: Settings | None = None,
    run: Runner = subprocess.run,
) -> Path:
    active_settings = settings or load_settings()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    silent_path = output_path.with_name("silent.mp4")
    run(
        [
            "pnpm",
            "--dir",
            str(active_settings.video_package_dir),
            "exec",
            "remotion",
            "render",
            "src/index.ts",
            "Lesson",
            str(silent_path),
            f"--props={lesson_path}",
            "--codec=h264",
            "--muted",
        ],
        check=True,
        capture_output=True,
    )

    lesson = json.loads(lesson_path.read_text(encoding="utf-8"))
    manim_script = Path(__file__).with_name("manim_scene.py")
    diagram_clips: list[tuple[float, Path]] = []
    elapsed = 0.0
    for segment in lesson["segments"]:
        duration = float(segment["targetSeconds"])
        if segment["visualType"] == "diagram":
            spec_path = output_path.with_name(f"{segment['id']}-manim.json")
            spec_path.write_text(
                json.dumps(
                    {
                        "title": segment["title"],
                        "nodes": segment["visualPayload"]["nodes"],
                        "duration": duration,
                    }
                ),
                encoding="utf-8",
            )
            media_dir = output_path.parent / f"{segment['id']}-manim"
            env = {**os.environ, "FOCUSLY_MANIM_SPEC": str(spec_path)}
            run(
                [sys.executable, "-m", "py_compile", str(manim_script)],
                check=True,
                capture_output=True,
            )
            for quality, name in (("l", "smoke"), ("m", "full")):
                run(
                    [
                        "manim",
                        "render",
                        f"-q{quality}",
                        "--fps",
                        "30",
                        "--media_dir",
                        str(media_dir),
                        "-o",
                        f"{segment['id']}-{name}",
                        str(manim_script),
                        "FocuslyDiagram",
                    ],
                    check=True,
                    capture_output=True,
                    env=env,
                )
            clip = next(
                media_dir.rglob(f"{segment['id']}-full.mp4"),
                media_dir / f"{segment['id']}-full.mp4",
            )
            diagram_clips.append((elapsed, clip))
        elapsed += duration

    command = ["ffmpeg", "-y", "-i", str(silent_path)]
    for _, clip in diagram_clips:
        command.extend(["-i", str(clip)])
    command.extend(["-i", str(narration_path)])
    if diagram_clips:
        filters = []
        base = "0:v"
        for index, (start, _) in enumerate(diagram_clips):
            filters.append(
                f"[{index + 1}:v]scale=1920:1080,fps=30,setpts=PTS+{start:g}/TB[manim{index}]"
            )
            filters.append(f"[{base}][manim{index}]overlay=eof_action=pass[video{index}]")
            base = f"video{index}"
        command.extend(["-filter_complex", ";".join(filters), "-map", f"[{base}]"])
    else:
        command.extend(["-map", "0:v:0", "-c:v", "copy"])
    command.extend(
        [
            "-map",
            f"{len(diagram_clips) + 1}:a:0",
            "-c:a",
            "aac",
            "-shortest",
            str(output_path),
        ]
    )
    run(
        command,
        check=True,
        capture_output=True,
    )
    silent_path.unlink(missing_ok=True)
    return output_path
