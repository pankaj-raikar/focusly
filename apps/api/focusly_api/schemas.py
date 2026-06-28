import re
from datetime import datetime
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)
from pydantic.alias_generators import to_camel

HTML_PATTERN = re.compile(r"<[^>]+>")


def reject_html(value: str) -> str:
    if HTML_PATTERN.search(value):
        raise ValueError("HTML is not allowed")
    return value


class ApiModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        extra="forbid",
    )


class VisualPayload(ApiModel):
    eyebrow: str | None
    items: list[str] | None
    left_label: str | None
    left_value: str | None
    right_label: str | None
    right_value: str | None
    nodes: list[str] | None

    @field_validator(
        "eyebrow",
        "left_label",
        "left_value",
        "right_label",
        "right_value",
    )
    @classmethod
    def validate_optional_text(cls, value: str | None) -> str | None:
        return reject_html(value) if value is not None else None

    @field_validator("items", "nodes")
    @classmethod
    def validate_text_list(cls, value: list[str] | None) -> list[str] | None:
        return [reject_html(item) for item in value] if value is not None else None


class Segment(ApiModel):
    id: str = Field(min_length=1, pattern=r"^[a-z0-9][a-z0-9_-]*$")
    title: str = Field(min_length=1)
    narration: str = Field(min_length=1)
    visual_type: Literal["title", "bullets", "comparison", "steps", "diagram"]
    visual_payload: VisualPayload
    target_seconds: int = Field(ge=10, le=60)

    @field_validator("id", "title", "narration")
    @classmethod
    def validate_text(cls, value: str) -> str:
        return reject_html(value)

    @model_validator(mode="after")
    def validate_payload_for_visual_type(self) -> "Segment":
        payload = self.visual_payload
        required = {
            "title": payload.eyebrow is not None,
            "bullets": bool(payload.items),
            "comparison": all(
                (
                    payload.left_label,
                    payload.left_value,
                    payload.right_label,
                    payload.right_value,
                )
            ),
            "steps": bool(payload.items),
            "diagram": bool(payload.nodes),
        }
        if not required[self.visual_type]:
            raise ValueError(f"visualPayload does not match {self.visual_type}")
        return self


class QuizCheckpoint(ApiModel):
    after_segment_id: str = Field(min_length=1)
    question: str = Field(min_length=1)
    options: list[str] = Field(min_length=2, max_length=4)
    correct_option_index: int = Field(ge=0)
    explanation: str = Field(min_length=1)

    @field_validator("after_segment_id", "question", "explanation")
    @classmethod
    def validate_text(cls, value: str) -> str:
        return reject_html(value)

    @field_validator("options")
    @classmethod
    def validate_options(cls, value: list[str]) -> list[str]:
        return [reject_html(option) for option in value]

    @model_validator(mode="after")
    def validate_correct_option(self) -> "QuizCheckpoint":
        if self.correct_option_index >= len(self.options):
            raise ValueError("correctOptionIndex must point to an option")
        return self


class LessonPackage(ApiModel):
    title: str = Field(min_length=1)
    hook: str = Field(min_length=1)
    learning_objectives: list[str] = Field(min_length=1, max_length=4)
    segments: list[Segment] = Field(min_length=3, max_length=5)
    quizzes: list[QuizCheckpoint] = Field(min_length=1)
    recap: list[str] = Field(min_length=1, max_length=5)
    reduced_motion: bool = False

    @field_validator("title", "hook")
    @classmethod
    def validate_text(cls, value: str) -> str:
        return reject_html(value)

    @field_validator("learning_objectives", "recap")
    @classmethod
    def validate_text_list(cls, value: list[str]) -> list[str]:
        return [reject_html(item) for item in value]

    @model_validator(mode="after")
    def validate_lesson(self) -> "LessonPackage":
        duration = sum(segment.target_seconds for segment in self.segments)
        if not 60 <= duration <= 120:
            raise ValueError("lesson duration must be between 60 and 120 seconds")

        segment_ids = [segment.id for segment in self.segments]
        if len(segment_ids) != len(set(segment_ids)):
            raise ValueError("segment IDs must be unique")

        unknown_ids = {
            quiz.after_segment_id
            for quiz in self.quizzes
            if quiz.after_segment_id not in segment_ids
        }
        if unknown_ids:
            raise ValueError("quiz afterSegmentId must reference a lesson segment")

        return self


class CreateJobRequest(ApiModel):
    topic: str = Field(min_length=3, max_length=300)
    audience_level: Literal["beginner", "intermediate", "advanced"] = "beginner"
    duration_target_seconds: int = Field(ge=60, le=120)

    @field_validator("topic", mode="before")
    @classmethod
    def validate_topic(cls, value: object) -> str:
        if not isinstance(value, str):
            raise ValueError("topic must be text")
        return reject_html(value.strip())


class JobResponse(ApiModel):
    job_id: str
    topic: str
    audience_level: str
    duration_target_seconds: int
    status: Literal["queued", "running", "succeeded", "failed"]
    stage: str
    progress_percent: int
    is_retryable: bool
    safe_error: str | None
    created_at: datetime
    updated_at: datetime


class LessonResponse(ApiModel):
    job_id: str
    lesson: dict[str, object]
    video_url: str
    captions_url: str
    quiz_checkpoints: list[dict[str, object]]
