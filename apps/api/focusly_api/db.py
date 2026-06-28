from pathlib import Path
from uuid import uuid4

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from .jobs import Job, JobStatus
from .models import Base, JobRecord


class Database:
    def __init__(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.engine = create_engine(f"sqlite:///{path}", connect_args={"check_same_thread": False})
        self.sessions = sessionmaker(self.engine, expire_on_commit=False)

    def create_tables(self) -> None:
        Base.metadata.create_all(self.engine)

    @staticmethod
    def _job(record: JobRecord) -> Job:
        return Job(
            id=record.id,
            topic=record.topic,
            audience_level=record.audience_level,
            duration_target_seconds=record.duration_target_seconds,
            status=JobStatus(record.status),
            stage=record.stage,
            progress_percent=record.progress_percent,
            lesson_json=record.lesson_json,
            video_path=record.video_path,
            captions_path=record.captions_path,
            safe_error=record.safe_error,
            created_at=record.created_at,
            updated_at=record.updated_at,
        )

    def create_job(
        self,
        *,
        topic: str,
        audience_level: str,
        duration_target_seconds: int,
    ) -> Job:
        record = JobRecord(
            id=str(uuid4()),
            topic=topic,
            audience_level=audience_level,
            duration_target_seconds=duration_target_seconds,
            status=JobStatus.QUEUED,
            stage="queued",
            progress_percent=0,
        )
        with self.sessions() as session:
            session.add(record)
            session.commit()
        return self._job(record)

    def get_job(self, job_id: str) -> Job | None:
        with self.sessions() as session:
            record = session.scalar(select(JobRecord).where(JobRecord.id == job_id))
            return self._job(record) if record else None

    def list_jobs(self) -> list[Job]:
        with self.sessions() as session:
            records = session.scalars(
                select(JobRecord).order_by(JobRecord.created_at.desc(), JobRecord.id.desc())
            )
            return [self._job(record) for record in records]

    def update_job(self, job_id: str, **values: object) -> Job:
        with self.sessions() as session:
            record = session.get(JobRecord, job_id)
            if record is None:
                raise KeyError(job_id)
            for key, value in values.items():
                setattr(record, key, value.value if isinstance(value, JobStatus) else value)
            session.commit()
            session.refresh(record)
            return self._job(record)
