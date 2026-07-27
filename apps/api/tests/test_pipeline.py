import logging
from pathlib import Path

import numpy as np

from focusly_api.config import Settings
from focusly_api.db import Database
from focusly_api.jobs import JobStatus
from focusly_api.kokoro_tts import SAMPLE_RATE
from focusly_api.pipeline import run_generation_job
from focusly_api.schemas import LessonPackage


def lesson() -> LessonPackage:
    return LessonPackage.model_validate(
        {
            "title": "Binary Search",
            "hook": "Remove half the choices.",
            "learningObjectives": ["Explain binary search"],
            "segments": [
                {
                    "id": f"segment-{index}",
                    "title": f"Step {index}",
                    "narration": f"Narration {index}.",
                    "visualType": "bullets",
                    "visualPayload": {
                        "eyebrow": None,
                        "items": ["One idea"],
                        "leftLabel": None,
                        "leftValue": None,
                        "rightLabel": None,
                        "rightValue": None,
                        "nodes": None,
                    },
                    "targetSeconds": 20,
                }
                for index in range(1, 4)
            ],
            "quizzes": [
                {
                    "afterSegmentId": "segment-2",
                    "question": "What is removed?",
                    "options": ["Half", "Nothing"],
                    "correctOptionIndex": 0,
                    "explanation": "The impossible half is removed.",
                }
            ],
            "recap": ["Check the middle"],
            "reducedMotion": False,
        }
    )


def fake_pipeline(text: str, *, voice: str):
    del text, voice
    yield "", "", np.zeros(SAMPLE_RATE * 20, dtype=np.float32)


def test_generation_job_persists_progress_artifacts_and_timings(
    tmp_path: Path, caplog
) -> None:
    database = Database(tmp_path / "focusly.db")
    database.create_tables()
    job = database.create_job(
        topic="Explain binary search",
        audience_level="beginner",
        duration_target_seconds=60,
    )
    rendered: list[tuple[Path, Path]] = []

    def fake_render(lesson_path: Path, narration_path: Path, output_path: Path) -> Path:
        rendered.append((lesson_path, narration_path))
        output_path.write_bytes(b"video")
        return output_path

    with caplog.at_level(logging.INFO):
        run_generation_job(
            job.id,
            database=database,
            settings=Settings(data_dir=tmp_path / "jobs"),
            lesson_generator=lambda **_: lesson(),
            tts_pipeline=fake_pipeline,
            renderer=fake_render,
        )

    saved = database.get_job(job.id)
    assert saved is not None
    assert saved.status is JobStatus.SUCCEEDED
    assert saved.stage == "succeeded"
    assert saved.progress_percent == 100
    assert Path(saved.video_path or "").read_bytes() == b"video"
    assert Path(saved.captions_path or "").read_text().startswith("WEBVTT")
    assert saved.lesson_json is not None
    assert rendered[0][0].name == "lesson.json"
    assert rendered[0][1].name == "narration.wav"
    assert "stage=planning" in caplog.text
    assert "stage=narrating" in caplog.text
    assert "stage=rendering" in caplog.text
    assert "stage=total" in caplog.text


def test_generation_job_records_safe_failure_and_stage(tmp_path: Path, caplog) -> None:
    database = Database(tmp_path / "focusly.db")
    database.create_tables()
    job = database.create_job(
        topic="Explain binary search",
        audience_level="beginner",
        duration_target_seconds=60,
    )

    with caplog.at_level(logging.ERROR):
        run_generation_job(
            job.id,
            database=database,
            settings=Settings(data_dir=tmp_path / "jobs"),
            lesson_generator=lambda **_: (_ for _ in ()).throw(
                RuntimeError("secret provider error")
            ),
            tts_pipeline=fake_pipeline,
        )

    saved = database.get_job(job.id)
    assert saved is not None
    assert saved.status is JobStatus.FAILED
    assert saved.safe_error == "Lesson generation failed. Please try again."
    assert "secret" not in saved.safe_error
    assert "stage=planning" in caplog.text


def test_generation_job_fails_when_real_narration_is_shorter_than_target(
    tmp_path: Path,
) -> None:
    database = Database(tmp_path / "focusly.db")
    database.create_tables()
    job = database.create_job(
        topic="Explain binary search",
        audience_level="beginner",
        duration_target_seconds=60,
    )

    def short_audio(text: str, *, voice: str):
        del text, voice
        yield "", "", np.zeros(SAMPLE_RATE, dtype=np.float32)

    run_generation_job(
        job.id,
        database=database,
        settings=Settings(data_dir=tmp_path / "jobs"),
        lesson_generator=lambda **_: lesson(),
        tts_pipeline=short_audio,
    )

    saved = database.get_job(job.id)
    assert saved is not None
    assert saved.status is JobStatus.FAILED
    assert saved.safe_error == "Lesson generation failed. Please try again."


def test_two_minute_job_allows_narration_timing_drift(tmp_path: Path) -> None:
    database = Database(tmp_path / "focusly.db")
    database.create_tables()
    job = database.create_job(
        topic="Explain binary search",
        audience_level="beginner",
        duration_target_seconds=120,
    )
    lesson_data = lesson().model_dump(by_alias=True)
    for segment_data in lesson_data["segments"]:
        segment_data["targetSeconds"] = 40
    two_minute_lesson = LessonPackage.model_validate(lesson_data)

    def slightly_long_audio(text: str, *, voice: str, speed: float = 1):
        del text, voice, speed
        yield "", "", np.zeros(SAMPLE_RATE * 40 + 8_000, dtype=np.float32)

    def fake_render(lesson_path: Path, narration_path: Path, output_path: Path) -> Path:
        del lesson_path, narration_path
        output_path.write_bytes(b"video")
        return output_path

    run_generation_job(
        job.id,
        database=database,
        settings=Settings(data_dir=tmp_path / "jobs"),
        lesson_generator=lambda **_: two_minute_lesson,
        tts_pipeline=slightly_long_audio,
        renderer=fake_render,
    )

    saved = database.get_job(job.id)
    assert saved is not None
    assert saved.status is JobStatus.SUCCEEDED
