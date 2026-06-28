import json
from pathlib import Path
from unittest.mock import Mock

from fastapi.testclient import TestClient

from focusly_api.config import Settings
from focusly_api.db import Database
from focusly_api.main import create_app


def make_client(tmp_path: Path) -> tuple[TestClient, Database, Mock]:
    database = Database(tmp_path / "focusly.db")
    runner = Mock()
    app = create_app(
        settings=Settings(data_dir=tmp_path / "jobs", cors_origin="http://localhost:3000"),
        database=database,
        job_runner=runner,
    )
    return TestClient(app), database, runner


def test_create_and_get_job(tmp_path: Path) -> None:
    client, database, runner = make_client(tmp_path)

    response = client.post(
        "/api/jobs",
        json={
            "topic": "Explain binary search",
            "audienceLevel": "beginner",
            "durationTargetSeconds": 60,
        },
    )

    assert response.status_code == 202
    body = response.json()
    assert body["status"] == "queued"
    assert database.get_job(body["jobId"]) is not None
    runner.assert_called_once_with(body["jobId"])

    poll = client.get(f"/api/jobs/{body['jobId']}")
    assert poll.status_code == 200
    assert poll.json()["progressPercent"] == 0


def test_list_jobs_returns_empty_then_newest_first(tmp_path: Path) -> None:
    client, database, _ = make_client(tmp_path)

    assert client.get("/api/jobs").json() == []

    first = database.create_job(
        topic="First topic",
        audience_level="beginner",
        duration_target_seconds=60,
    )
    second = database.create_job(
        topic="Second topic",
        audience_level="advanced",
        duration_target_seconds=120,
    )

    response = client.get("/api/jobs")

    assert response.status_code == 200
    assert [job["jobId"] for job in response.json()] == [second.id, first.id]
    assert response.json()[0]["topic"] == "Second topic"
    assert response.json()[0]["audienceLevel"] == "advanced"
    assert response.json()[0]["durationTargetSeconds"] == 120


def test_retry_failed_job_creates_new_job_and_preserves_original(tmp_path: Path) -> None:
    client, database, runner = make_client(tmp_path)
    original = database.create_job(
        topic="Explain binary search",
        audience_level="intermediate",
        duration_target_seconds=90,
    )
    database.update_job(
        original.id,
        status="failed",
        stage="failed",
        safe_error="Lesson generation failed. Please try again.",
    )

    response = client.post(f"/api/jobs/{original.id}/retry")

    assert response.status_code == 202
    retried = response.json()
    assert retried["jobId"] != original.id
    assert retried["status"] == "queued"
    assert retried["topic"] == original.topic
    assert retried["audienceLevel"] == original.audience_level
    assert retried["durationTargetSeconds"] == original.duration_target_seconds
    runner.assert_called_once_with(retried["jobId"])
    assert database.get_job(original.id).status.value == "failed"


def test_retry_rejects_missing_or_active_job(tmp_path: Path) -> None:
    client, database, runner = make_client(tmp_path)
    active = database.create_job(
        topic="Explain binary search",
        audience_level="beginner",
        duration_target_seconds=60,
    )

    assert client.post("/api/jobs/missing/retry").status_code == 404
    assert client.post(f"/api/jobs/{active.id}/retry").status_code == 409
    runner.assert_not_called()


def test_create_job_validates_topic(tmp_path: Path) -> None:
    client, _, runner = make_client(tmp_path)

    response = client.post(
        "/api/jobs",
        json={
            "topic": "x",
            "audienceLevel": "beginner",
            "durationTargetSeconds": 60,
        },
    )

    assert response.status_code == 422
    runner.assert_not_called()

    whitespace = client.post(
        "/api/jobs",
        json={
            "topic": "   ",
            "audienceLevel": "beginner",
            "durationTargetSeconds": 60,
        },
    )
    assert whitespace.status_code == 422


def test_lesson_and_media_endpoints_reject_missing_or_unsafe_paths(tmp_path: Path) -> None:
    client, database, _ = make_client(tmp_path)
    job = database.create_job(
        topic="Explain binary search",
        audience_level="beginner",
        duration_target_seconds=60,
    )

    assert client.get(f"/api/jobs/{job.id}/lesson").status_code == 409
    assert client.get(f"/media/{job.id}/../focusly.db").status_code in {404, 422}
    assert client.get("/api/jobs/missing").status_code == 404


def test_serves_successful_lesson_metadata_and_job_scoped_media(tmp_path: Path) -> None:
    client, database, _ = make_client(tmp_path)
    job = database.create_job(
        topic="Explain binary search",
        audience_level="beginner",
        duration_target_seconds=60,
    )
    job_dir = tmp_path / "jobs" / job.id
    job_dir.mkdir(parents=True)
    video = job_dir / "lesson.mp4"
    captions = job_dir / "captions.vtt"
    video.write_bytes(b"video")
    captions.write_text("WEBVTT\n", encoding="utf-8")
    database.update_job(
        job.id,
        status="succeeded",
        stage="succeeded",
        progress_percent=100,
        video_path=str(video),
        captions_path=str(captions),
        lesson_json=json.dumps(
            {
                "title": "Binary Search",
                "hook": "Remove half.",
                "learningObjectives": ["Explain binary search"],
                "segments": [
                    {"id": "one", "targetSeconds": 10},
                    {"id": "two", "targetSeconds": 12},
                ],
                "quizzes": [
                    {
                        "afterSegmentId": "two",
                        "question": "What is removed?",
                        "options": ["Half", "Nothing"],
                        "correctOptionIndex": 0,
                        "explanation": "The impossible half.",
                    }
                ],
                "recap": ["Remove half"],
            }
        ),
    )

    response = client.get(f"/api/jobs/{job.id}/lesson")

    assert response.status_code == 200
    assert response.json()["quizCheckpoints"][0]["timestampSeconds"] == 22
    assert client.get(response.json()["videoUrl"]).content == b"video"
