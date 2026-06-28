import re

from .schemas import Segment

SENTENCE_PATTERN = re.compile(r"(?<=[.!?])\s+")


def format_timestamp(seconds: float) -> str:
    milliseconds = round(seconds * 1000)
    hours, remainder = divmod(milliseconds, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    whole_seconds, milliseconds = divmod(remainder, 1000)
    return f"{hours:02}:{minutes:02}:{whole_seconds:02}.{milliseconds:03}"


def build_webvtt(segments: list[Segment], durations: list[float]) -> str:
    if len(segments) != len(durations):
        raise ValueError("each segment needs an audio duration")

    cues: list[str] = []
    segment_start = 0.0

    for segment, duration in zip(segments, durations, strict=True):
        sentences = [
            sentence.strip()
            for sentence in SENTENCE_PATTERN.split(segment.narration.strip())
            if sentence.strip()
        ]
        weights = [len(sentence) for sentence in sentences]
        total_weight = sum(weights)
        cue_start = segment_start

        for index, (sentence, weight) in enumerate(zip(sentences, weights, strict=True)):
            cue_end = (
                segment_start + duration
                if index == len(sentences) - 1
                else cue_start + duration * weight / total_weight
            )
            cues.append(
                f"{format_timestamp(cue_start)} --> {format_timestamp(cue_end)}\n{sentence}"
            )
            cue_start = cue_end

        segment_start += duration

    return "WEBVTT\n\n" + "\n\n".join(cues) + "\n"
