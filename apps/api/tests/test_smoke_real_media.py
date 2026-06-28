import os
import subprocess
from pathlib import Path

import pytest

from focusly_api.config import Settings
from focusly_api.db import Database
from focusly_api.jobs import JobStatus
from focusly_api.pipeline import run_generation_job
from focusly_api.schemas import LessonPackage

pytestmark = pytest.mark.skipif(
    os.environ.get("RUN_MEDIA_SMOKE") != "1",
    reason="set RUN_MEDIA_SMOKE=1 to run local Kokoro and Remotion",
)


def fixture_lesson() -> LessonPackage:
    return LessonPackage.model_validate(
        {
            "title": "Binary Search",
            "hook": "Find an answer without checking every item.",
            "learningObjectives": ["Explain how binary search removes half the range"],
            "segments": [
                {
                    "id": "sorted",
                    "title": "Start sorted",
                    "narration": (
                        "Binary search begins with values arranged from smallest to largest. "
                        "That order is the rule that makes the shortcut possible. Imagine a "
                        "dictionary: words before the page you opened come earlier, and words "
                        "after it come later. Without that predictable order, checking the "
                        "middle would tell us nothing about where to search next."
                    ),
                    "visualType": "bullets",
                    "visualPayload": {
                        "eyebrow": None,
                        "items": ["Sorted values", "Known direction"],
                        "leftLabel": None,
                        "leftValue": None,
                        "rightLabel": None,
                        "rightValue": None,
                        "nodes": None,
                    },
                    "targetSeconds": 20,
                },
                {
                    "id": "middle",
                    "title": "Check the middle",
                    "narration": (
                        "Now compare the target with the value in the middle. If the target is "
                        "larger, every smaller value on the left becomes impossible. If the "
                        "target is smaller, every larger value on the right becomes impossible. "
                        "One comparison therefore removes an entire half, while a normal "
                        "line-by-line search removes only one choice."
                    ),
                    "visualType": "comparison",
                    "visualPayload": {
                        "eyebrow": None,
                        "items": None,
                        "leftLabel": "Discard",
                        "leftValue": "1  3  5",
                        "rightLabel": "Keep",
                        "rightValue": "9  11  13",
                        "nodes": None,
                    },
                    "targetSeconds": 20,
                },
                {
                    "id": "repeat",
                    "title": "Halve again",
                    "narration": (
                        "Repeat the same move inside the half that remains. Choose its middle, "
                        "compare again, and discard another impossible half. Sixteen choices "
                        "become eight, then four, then two, and finally one. That repeated "
                        "halving is why binary search stays fast even when the original list "
                        "contains thousands or millions of sorted values."
                    ),
                    "visualType": "diagram",
                    "visualPayload": {
                        "eyebrow": None,
                        "items": None,
                        "leftLabel": None,
                        "leftValue": None,
                        "rightLabel": None,
                        "rightValue": None,
                        "nodes": ["16", "8", "4", "2", "1"],
                    },
                    "targetSeconds": 20,
                },
            ],
            "quizzes": [
                {
                    "afterSegmentId": "middle",
                    "question": "What can one comparison remove?",
                    "options": ["Half the range", "Only the middle value"],
                    "correctOptionIndex": 0,
                    "explanation": "Sorted order lets us rule out one complete half.",
                }
            ],
            "recap": ["Sort first", "Check the middle", "Discard half"],
            "reducedMotion": False,
        }
    )


def test_real_kokoro_remotion_and_manim_pipeline(tmp_path: Path) -> None:
    database = Database(tmp_path / "focusly.db")
    database.create_tables()
    job = database.create_job(
        topic="Explain binary search",
        audience_level="beginner",
        duration_target_seconds=60,
    )

    run_generation_job(
        job.id,
        database=database,
        settings=Settings(data_dir=tmp_path / "jobs"),
        lesson_generator=lambda **_: fixture_lesson(),
    )

    saved = database.get_job(job.id)
    assert saved is not None
    assert saved.status is JobStatus.SUCCEEDED
    assert saved.video_path is not None
    assert saved.captions_path is not None
    duration = float(
        subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                saved.video_path,
            ],
            check=True,
            capture_output=True,
            text=True,
        ).stdout
    )
    assert 60 <= duration <= 120
    assert Path(saved.captions_path).read_text(encoding="utf-8").startswith("WEBVTT")
