import json
import logging
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from pydantic import ValidationError

from focusly_api.config import Settings
from focusly_api.openai_lesson import build_lesson_prompt, build_response_schema, generate_lesson
from focusly_api.schemas import LessonPackage


def lesson_data() -> dict:
    return {
        "title": "Binary Search",
        "hook": "Find an answer by removing half the possibilities.",
        "learningObjectives": ["Explain why sorted data matters"],
        "segments": [
            {
                "id": f"segment-{index}",
                "title": f"Step {index}",
                "narration": (
                    "Start with one concrete example, explain why the middle value matters, "
                    "and connect the comparison to removing an impossible half of the range. "
                    "Repeat the idea in plain language so the learner can follow the next step."
                ),
                "visualType": "bullets",
                "visualPayload": {
                    "eyebrow": None,
                    "items": ["One idea", "One example"],
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
                "question": "What does binary search remove?",
                "options": ["Half the range", "One random value"],
                "correctOptionIndex": 0,
                "explanation": "The comparison rules out one whole half.",
            }
        ],
        "recap": ["Sorted data", "Check the middle", "Remove half"],
        "reducedMotion": False,
    }


def test_lesson_package_rejects_invalid_duration() -> None:
    data = lesson_data()
    data["segments"][0]["targetSeconds"] = 10

    with pytest.raises(ValidationError, match="60 and 120 seconds"):
        LessonPackage.model_validate(data)


def test_lesson_package_rejects_html() -> None:
    data = lesson_data()
    data["segments"][1]["narration"] = "<script>bad</script>"

    with pytest.raises(ValidationError, match="HTML"):
        LessonPackage.model_validate(data)


def test_lesson_package_requires_a_quiz() -> None:
    data = lesson_data()
    data["quizzes"] = []

    with pytest.raises(ValidationError, match="quiz"):
        LessonPackage.model_validate(data)


def test_generate_lesson_uses_cerebras_chat_completions_and_records_usage(caplog) -> None:
    data = lesson_data()
    parsed = LessonPackage.model_validate(data)
    client = Mock()
    client.chat.completions.create.return_value = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content=json.dumps(data)))],
        usage=SimpleNamespace(prompt_tokens=100, completion_tokens=50, total_tokens=150),
    )

    with caplog.at_level(logging.INFO):
        result = generate_lesson(
            topic="Explain binary search",
            audience_level="beginner",
            duration_target_seconds=60,
            client=client,
            settings=Settings(cerebras_model="zai-glm-4.7"),
        )

    assert result == parsed
    call = client.chat.completions.create.call_args.kwargs
    assert call["model"] == "zai-glm-4.7"
    assert call["response_format"]["type"] == "json_schema"
    assert call["messages"][0]["role"] == "system"
    assert call["messages"][-1]["content"].endswith("Explain binary search")
    assert "input_tokens=100 output_tokens=50 total_tokens=150" in caplog.text


def test_generate_lesson_rejects_missing_content() -> None:
    client = Mock()
    client.chat.completions.create.return_value = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content=None))],
        usage=None,
    )

    with pytest.raises(RuntimeError, match="structured lesson"):
        generate_lesson(
            topic="Explain binary search",
            audience_level="beginner",
            duration_target_seconds=60,
            client=client,
            settings=Settings(),
        )


def test_generate_lesson_normalizes_segment_durations_to_requested_total() -> None:
    data = lesson_data()
    for segment in data["segments"]:
        segment["targetSeconds"] = 15
    client = Mock()
    client.chat.completions.create.return_value = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content=json.dumps(data)))],
        usage=None,
    )

    result = generate_lesson(
        topic="Explain binary search",
        audience_level="beginner",
        duration_target_seconds=60,
        client=client,
        settings=Settings(),
    )

    assert [segment.target_seconds for segment in result.segments] == [20, 20, 20]


def test_generate_lesson_rejects_script_too_short_for_requested_duration() -> None:
    data = lesson_data()
    for segment in data["segments"]:
        segment["narration"] = "Too short."
    parsed = LessonPackage.model_validate(data)
    client = Mock()
    client.chat.completions.create.return_value = SimpleNamespace(
        choices=[
            SimpleNamespace(message=SimpleNamespace(content=parsed.model_dump_json(by_alias=True)))
        ],
        usage=None,
    )

    with pytest.raises(RuntimeError, match="narration is too short"):
        generate_lesson(
            topic="Explain binary search",
            audience_level="beginner",
            duration_target_seconds=60,
            client=client,
            settings=Settings(),
        )


def test_prompt_keeps_stable_instructions_before_user_topic() -> None:
    prompt = build_lesson_prompt(
        topic="Explain recursion",
        audience_level="beginner",
        duration_target_seconds=90,
    )

    assert prompt[0]["role"] == "system"
    assert "ADHD-friendly" in prompt[0]["content"]
    assert prompt[-1]["content"].endswith("Explain recursion")


def test_response_schema_omits_constraints_unsupported_by_cerebras() -> None:
    schema = json.dumps(build_response_schema())

    unsupported = (
        "minLength",
        "maxLength",
        "pattern",
        "minimum",
        "maximum",
        "minItems",
        "maxItems",
    )
    for keyword in unsupported:
        assert keyword not in schema
