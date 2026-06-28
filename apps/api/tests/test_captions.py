from pathlib import Path

import numpy as np
import soundfile as sf

from focusly_api.captions import build_webvtt
from focusly_api.kokoro_tts import SAMPLE_RATE, synthesize_segments
from focusly_api.schemas import Segment, VisualPayload


def segment(segment_id: str, narration: str) -> Segment:
    return Segment(
        id=segment_id,
        title=segment_id.title(),
        narration=narration,
        visual_type="bullets",
        visual_payload=VisualPayload(
            eyebrow=None,
            items=["One idea"],
            left_label=None,
            left_value=None,
            right_label=None,
            right_value=None,
            nodes=None,
        ),
        target_seconds=20,
    )


def test_build_webvtt_uses_audio_boundaries_and_sentence_proportions() -> None:
    segments = [
        segment("one", "First idea. Second idea is longer."),
        segment("two", "Final idea."),
    ]

    captions = build_webvtt(segments, [4.0, 2.0])

    assert captions == (
        "WEBVTT\n\n"
        "00:00:00.000 --> 00:00:01.333\nFirst idea.\n\n"
        "00:00:01.333 --> 00:00:04.000\nSecond idea is longer.\n\n"
        "00:00:04.000 --> 00:00:06.000\nFinal idea.\n"
    )


def test_synthesize_segments_writes_each_track_and_combined_wav(tmp_path: Path) -> None:
    segments = [
        segment("one", "First idea."),
        segment("two", "Second idea."),
    ]

    def fake_pipeline(text: str, *, voice: str, speed: float = 1):
        del speed
        amplitude = 0.1 if text.startswith("First") else 0.2
        yield "", "", np.full(SAMPLE_RATE * 20, amplitude, dtype=np.float32)

    result = synthesize_segments(
        segments,
        output_dir=tmp_path,
        voice="test-voice",
        pipeline=fake_pipeline,
    )

    assert [track.path.name for track in result.tracks] == ["one.wav", "two.wav"]
    assert result.path == tmp_path / "narration.wav"
    assert result.path.exists()
    assert result.durations == [20, 20]
    assert sf.info(result.path).duration == 40


def test_synthesize_segments_slows_short_audio_to_segment_target(tmp_path: Path) -> None:
    speeds: list[float] = []

    def fake_pipeline(text: str, *, voice: str, speed: float = 1):
        del text, voice
        speeds.append(speed)
        seconds = 12 if speed == 1 else 19.8
        yield "", "", np.zeros(round(SAMPLE_RATE * seconds), dtype=np.float32)

    result = synthesize_segments(
        [segment("one", "First idea.")],
        output_dir=tmp_path,
        pipeline=fake_pipeline,
    )

    assert speeds == [1, 0.6]
    assert result.durations == [20]
