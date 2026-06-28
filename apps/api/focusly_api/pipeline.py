import json
import logging
from collections.abc import Callable
from pathlib import Path
from threading import Lock
from time import perf_counter

from .captions import build_webvtt
from .config import Settings, load_settings
from .db import Database
from .jobs import JobStatus
from .kokoro_tts import Pipeline, synthesize_segments
from .openai_lesson import generate_lesson
from .render import render_lesson
from .schemas import LessonPackage

logger = logging.getLogger(__name__)

# ponytail: one process and one render at a time is enough for the private MVP;
# replace this with a durable queue before running multiple API instances.
RENDER_LOCK = Lock()
LessonGenerator = Callable[..., LessonPackage]
Renderer = Callable[[Path, Path, Path], Path]


def run_generation_job(
    job_id: str,
    *,
    database: Database,
    settings: Settings | None = None,
    lesson_generator: LessonGenerator = generate_lesson,
    tts_pipeline: Pipeline | None = None,
    renderer: Renderer | None = None,
) -> None:
    active_settings = settings or load_settings()
    job = database.get_job(job_id)
    if job is None:
        raise KeyError(job_id)

    job_dir = (active_settings.data_dir / job_id).resolve()
    job_dir.mkdir(parents=True, exist_ok=True)
    total_started = perf_counter()
    stage = "planning"
    stage_started = total_started

    try:
        database.update_job(
            job_id,
            status=JobStatus.RUNNING,
            stage="planning",
            progress_percent=15,
        )
        lesson = lesson_generator(
            topic=job.topic,
            audience_level=job.audience_level,
            duration_target_seconds=job.duration_target_seconds,
        )
        logger.info(
            "job_id=%s stage=%s duration_seconds=%.3f",
            job_id,
            stage,
            perf_counter() - stage_started,
        )

        stage = "narrating"
        stage_started = perf_counter()
        database.update_job(job_id, stage="narrating", progress_percent=45)
        narration = synthesize_segments(
            lesson.segments,
            output_dir=job_dir / "audio",
            voice=active_settings.kokoro_voice,
            pipeline=tts_pipeline,
        )
        actual_duration = sum(narration.durations)
        if not job.duration_target_seconds <= actual_duration <= 120:
            raise RuntimeError(
                "Narration duration "
                f"{actual_duration:.1f}s is outside "
                f"{job.duration_target_seconds}–120s"
            )
        captions_path = job_dir / "captions.vtt"
        captions_path.write_text(
            build_webvtt(lesson.segments, narration.durations),
            encoding="utf-8",
        )
        logger.info(
            "job_id=%s stage=%s duration_seconds=%.3f",
            job_id,
            stage,
            perf_counter() - stage_started,
        )

        render_data = lesson.model_dump(by_alias=True)
        for segment, duration in zip(
            render_data["segments"], narration.durations, strict=True
        ):
            segment["targetSeconds"] = round(duration, 3)
        lesson_path = job_dir / "lesson.json"
        lesson_path.write_text(json.dumps(render_data, indent=2), encoding="utf-8")

        stage = "rendering"
        stage_started = perf_counter()
        database.update_job(
            job_id,
            stage="rendering",
            progress_percent=75,
            lesson_json=json.dumps(render_data),
            captions_path=str(captions_path),
        )
        output_path = job_dir / "lesson.mp4"
        active_renderer = renderer or (
            lambda lesson_file, narration_file, output_file: render_lesson(
                lesson_file,
                narration_file,
                output_file,
                settings=active_settings,
            )
        )
        with RENDER_LOCK:
            active_renderer(lesson_path, narration.path, output_path)
        logger.info(
            "job_id=%s stage=%s duration_seconds=%.3f",
            job_id,
            stage,
            perf_counter() - stage_started,
        )

        database.update_job(
            job_id,
            status=JobStatus.SUCCEEDED,
            stage="succeeded",
            progress_percent=100,
            video_path=str(output_path),
        )
        logger.info(
            "job_id=%s stage=total duration_seconds=%.3f",
            job_id,
            perf_counter() - total_started,
        )
    except Exception:
        logger.exception("Generation job %s failed stage=%s", job_id, stage)
        database.update_job(
            job_id,
            status=JobStatus.FAILED,
            stage="failed",
            safe_error="Lesson generation failed. Please try again.",
        )
