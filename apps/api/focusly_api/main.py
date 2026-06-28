import json
from collections.abc import Callable
from functools import partial
from pathlib import Path

from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from .config import Settings, load_settings
from .db import Database
from .jobs import Job
from .pipeline import run_generation_job
from .schemas import CreateJobRequest, JobResponse, LessonResponse

JobRunner = Callable[[str], None]


def job_response(job: Job) -> JobResponse:
    return JobResponse(
        job_id=job.id,
        topic=job.topic,
        audience_level=job.audience_level,
        duration_target_seconds=job.duration_target_seconds,
        status=job.status,
        stage=job.stage,
        progress_percent=job.progress_percent,
        is_retryable=job.status.value == "failed",
        safe_error=job.safe_error,
        created_at=job.created_at,
        updated_at=job.updated_at,
    )


def create_app(
    *,
    settings: Settings | None = None,
    database: Database | None = None,
    job_runner: JobRunner | None = None,
) -> FastAPI:
    active_settings = settings or load_settings()
    active_database = database or Database(active_settings.database_path)
    active_database.create_tables()
    active_runner = job_runner or partial(
        run_generation_job,
        database=active_database,
        settings=active_settings,
    )

    app = FastAPI(title="Focusly API")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[active_settings.cors_origin],
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
    )

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/api/jobs", response_model=JobResponse, status_code=202)
    def create_job(
        request: CreateJobRequest,
        background_tasks: BackgroundTasks,
    ) -> JobResponse:
        job = active_database.create_job(
            topic=request.topic,
            audience_level=request.audience_level,
            duration_target_seconds=request.duration_target_seconds,
        )
        background_tasks.add_task(active_runner, job.id)
        return job_response(job)

    @app.get("/api/jobs", response_model=list[JobResponse])
    def list_jobs() -> list[JobResponse]:
        return [job_response(job) for job in active_database.list_jobs()]

    @app.get("/api/jobs/{job_id}", response_model=JobResponse)
    def get_job(job_id: str) -> JobResponse:
        job = active_database.get_job(job_id)
        if job is None:
            raise HTTPException(status_code=404, detail="Job not found")
        return job_response(job)

    @app.post("/api/jobs/{job_id}/retry", response_model=JobResponse, status_code=202)
    def retry_job(job_id: str, background_tasks: BackgroundTasks) -> JobResponse:
        job = active_database.get_job(job_id)
        if job is None:
            raise HTTPException(status_code=404, detail="Job not found")
        if job.status.value != "failed":
            raise HTTPException(status_code=409, detail="Only failed jobs can be retried")
        retried = active_database.create_job(
            topic=job.topic,
            audience_level=job.audience_level,
            duration_target_seconds=job.duration_target_seconds,
        )
        background_tasks.add_task(active_runner, retried.id)
        return job_response(retried)

    @app.get("/api/jobs/{job_id}/lesson", response_model=LessonResponse)
    def get_lesson(job_id: str) -> LessonResponse:
        job = active_database.get_job(job_id)
        if job is None:
            raise HTTPException(status_code=404, detail="Job not found")
        if not job.lesson_json or not job.video_path or not job.captions_path:
            raise HTTPException(status_code=409, detail="Lesson is not ready")

        lesson = json.loads(job.lesson_json)
        segment_end: dict[str, int] = {}
        elapsed = 0
        for segment in lesson["segments"]:
            elapsed += segment["targetSeconds"]
            segment_end[segment["id"]] = elapsed
        quizzes = [
            {
                **quiz,
                "timestampSeconds": segment_end[quiz["afterSegmentId"]],
            }
            for quiz in lesson["quizzes"]
        ]
        return LessonResponse(
            job_id=job.id,
            lesson=lesson,
            video_url=f"/media/{job.id}/{Path(job.video_path).name}",
            captions_url=f"/media/{job.id}/{Path(job.captions_path).name}",
            quiz_checkpoints=quizzes,
        )

    @app.get("/media/{job_id}/{filename}")
    def get_media(job_id: str, filename: str) -> FileResponse:
        if filename != Path(filename).name:
            raise HTTPException(status_code=404, detail="Media not found")
        job = active_database.get_job(job_id)
        if job is None:
            raise HTTPException(status_code=404, detail="Media not found")
        job_dir = (active_settings.data_dir / job_id).resolve()
        path = (job_dir / filename).resolve()
        if path.parent != job_dir or not path.is_file():
            raise HTTPException(status_code=404, detail="Media not found")
        return FileResponse(path)

    return app


app = create_app()
