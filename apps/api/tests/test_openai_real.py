import os

import pytest

from focusly_api.openai_lesson import generate_lesson

pytestmark = pytest.mark.skipif(
    os.environ.get("RUN_CEREBRAS_INTEGRATION") != "1"
    or not os.environ.get("CEREBRAS_API_KEY"),
    reason="set RUN_CEREBRAS_INTEGRATION=1 and CEREBRAS_API_KEY to call Cerebras",
)


def test_real_cerebras_structured_lesson() -> None:
    lesson = generate_lesson(
        topic="Explain binary search",
        audience_level="beginner",
        duration_target_seconds=60,
    )

    assert 3 <= len(lesson.segments) <= 5
    assert 60 <= sum(segment.target_seconds for segment in lesson.segments) <= 120
    assert lesson.quizzes
