from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class JobStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


@dataclass(frozen=True, slots=True)
class Job:
    id: str
    topic: str
    audience_level: str
    duration_target_seconds: int
    status: JobStatus
    stage: str
    progress_percent: int
    lesson_json: str | None
    video_path: str | None
    captions_path: str | None
    safe_error: str | None
    created_at: datetime
    updated_at: datetime
