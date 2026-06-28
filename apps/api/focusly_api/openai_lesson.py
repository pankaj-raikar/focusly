import json
import logging
from time import perf_counter
from typing import Any, Protocol, cast

from openai import OpenAI

from .config import Settings, load_settings
from .schemas import LessonPackage

logger = logging.getLogger(__name__)

STABLE_LESSON_INSTRUCTIONS = """Create one concise, accurate, ADHD-friendly animated lesson.
Return 3 to 5 segments totaling the requested duration.
Each segment teaches one idea and uses one supported visual type.
Write narration at roughly 110 to 140 spoken words per minute.
The narration must fill the requested duration.
Use concrete examples, a clear hook, and a short recap.
Use only these visual types: title, bullets, comparison, steps, diagram.
For every visualPayload, include all schema fields and use null for fields that do not apply.
Include at least one quiz checkpoint.
Do not output HTML or executable code."""

UNSUPPORTED_SCHEMA_KEYS = {
    "default",
    "maxItems",
    "maxLength",
    "maximum",
    "minItems",
    "minLength",
    "minimum",
    "pattern",
}


class ChatCompletionsApi(Protocol):
    def create(self, **kwargs: Any) -> Any: ...


class ChatApi(Protocol):
    completions: ChatCompletionsApi


class CerebrasClient(Protocol):
    chat: ChatApi


def build_response_schema() -> dict[str, Any]:
    def clean(value: Any) -> Any:
        if isinstance(value, list):
            return [clean(item) for item in value]
        if not isinstance(value, dict):
            return value
        cleaned = {
            key: clean(item) for key, item in value.items() if key not in UNSUPPORTED_SCHEMA_KEYS
        }
        if cleaned.get("type") == "object" and "properties" in cleaned:
            cleaned["required"] = list(cleaned["properties"])
        return cleaned

    return clean(LessonPackage.model_json_schema(by_alias=True))


def validate_script_length(lesson: LessonPackage, duration_target_seconds: int) -> None:
    words = sum(len(segment.narration.split()) for segment in lesson.segments)
    minimum_words = round(duration_target_seconds * 1.6)
    maximum_words = round(duration_target_seconds * 2.8)
    if words < minimum_words:
        raise RuntimeError(f"OpenAI narration is too short for {duration_target_seconds} seconds")
    if words > maximum_words:
        raise RuntimeError(f"OpenAI narration is too long for {duration_target_seconds} seconds")


def normalize_segment_durations(lesson_data: dict[str, Any], duration_target_seconds: int) -> None:
    segments = lesson_data.get("segments")
    if not isinstance(segments, list) or not segments:
        return

    seconds_per_segment, remainder = divmod(duration_target_seconds, len(segments))
    for index, segment in enumerate(segments):
        if isinstance(segment, dict):
            segment["targetSeconds"] = seconds_per_segment + (index < remainder)


def build_lesson_prompt(
    *,
    topic: str,
    audience_level: str,
    duration_target_seconds: int,
) -> list[dict[str, str]]:
    return [
        {"role": "system", "content": STABLE_LESSON_INSTRUCTIONS},
        {
            "role": "user",
            "content": (
                f"Audience level: {audience_level}\n"
                f"Target duration: {duration_target_seconds} seconds\n"
                f"Topic: {topic}"
            ),
        },
    ]


def generate_lesson(
    *,
    topic: str,
    audience_level: str,
    duration_target_seconds: int,
    client: CerebrasClient | None = None,
    settings: Settings | None = None,
) -> LessonPackage:
    active_settings = settings or load_settings()
    active_client = client or cast(
        CerebrasClient,
        OpenAI(
            api_key=active_settings.cerebras_api_key,
            base_url=active_settings.cerebras_base_url,
        ),
    )
    started = perf_counter()
    response = active_client.chat.completions.create(
        model=active_settings.cerebras_model,
        messages=build_lesson_prompt(
            topic=topic,
            audience_level=audience_level,
            duration_target_seconds=duration_target_seconds,
        ),
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "lesson_package",
                "strict": True,
                "schema": build_response_schema(),
            },
        },
    )
    usage = getattr(response, "usage", None)
    logger.info(
        "cerebras_model=%s duration_seconds=%.3f input_tokens=%s output_tokens=%s total_tokens=%s",
        active_settings.cerebras_model,
        perf_counter() - started,
        getattr(usage, "prompt_tokens", None),
        getattr(usage, "completion_tokens", None),
        getattr(usage, "total_tokens", None),
    )
    content = response.choices[0].message.content
    if not content:
        raise RuntimeError("Cerebras did not return a structured lesson")
    lesson_data = json.loads(content)
    normalize_segment_durations(lesson_data, duration_target_seconds)
    validated = LessonPackage.model_validate(lesson_data)
    validate_script_length(validated, duration_target_seconds)
    return validated
