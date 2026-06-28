import json
from pathlib import Path
from unittest.mock import Mock

from focusly_api.config import Settings
from focusly_api.render import render_lesson


def test_render_lesson_uses_manim_only_for_diagram_segments(tmp_path: Path) -> None:
    lesson_path = tmp_path / "lesson.json"
    lesson_path.write_text(
        json.dumps(
            {
                "title": "Binary Search",
                "hook": "Remove half.",
                "learningObjectives": ["Explain binary search"],
                "segments": [
                    {
                        "id": "intro",
                        "title": "Start",
                        "narration": "Start here.",
                        "visualType": "title",
                        "visualPayload": {
                            "eyebrow": "Search",
                            "items": None,
                            "leftLabel": None,
                            "leftValue": None,
                            "rightLabel": None,
                            "rightValue": None,
                            "nodes": None,
                        },
                        "targetSeconds": 10,
                    },
                    {
                        "id": "halves",
                        "title": "Discard half",
                        "narration": "Compare the midpoint.",
                        "visualType": "diagram",
                        "visualPayload": {
                            "eyebrow": None,
                            "items": None,
                            "leftLabel": None,
                            "leftValue": None,
                            "rightLabel": None,
                            "rightValue": None,
                            "nodes": ["Low", "Middle", "High"],
                        },
                        "targetSeconds": 20,
                    },
                ],
                "quizzes": [],
                "recap": ["Discard half"],
                "reducedMotion": False,
            }
        ),
        encoding="utf-8",
    )
    narration_path = tmp_path / "narration.wav"
    narration_path.write_bytes(b"audio")
    output_path = tmp_path / "lesson.mp4"
    run = Mock()

    render_lesson(
        lesson_path,
        narration_path,
        output_path,
        settings=Settings(video_package_dir=tmp_path / "video"),
        run=run,
    )

    commands = [call.args[0] for call in run.call_args_list]
    manim_commands = [command for command in commands if command[0] == "manim"]
    assert len(manim_commands) == 2
    assert any("py_compile" in command for command in commands)
    final_ffmpeg = commands[-1]
    assert "overlay=eof_action=pass" in " ".join(final_ffmpeg)
    assert "PTS+10/TB" in " ".join(final_ffmpeg)
