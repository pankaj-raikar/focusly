import subprocess
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import soundfile as sf

from .schemas import Segment

SAMPLE_RATE = 24_000
Pipeline = Callable[..., Iterable[tuple[Any, Any, np.ndarray]]]


@dataclass(frozen=True, slots=True)
class AudioTrack:
    segment_id: str
    path: Path
    duration: float


@dataclass(frozen=True, slots=True)
class Narration:
    path: Path
    tracks: list[AudioTrack]

    @property
    def durations(self) -> list[float]:
        return [track.duration for track in self.tracks]


def create_pipeline() -> Pipeline:
    from kokoro import KPipeline

    return KPipeline(lang_code="a", repo_id="hexgrad/Kokoro-82M")


def synthesize_segments(
    segments: list[Segment],
    *,
    output_dir: Path,
    voice: str = "af_heart",
    pipeline: Pipeline | None = None,
) -> Narration:
    output_dir.mkdir(parents=True, exist_ok=True)
    active_pipeline = pipeline or create_pipeline()
    tracks: list[AudioTrack] = []

    for segment in segments:
        chunks = [audio for _, _, audio in active_pipeline(segment.narration, voice=voice)]
        if not chunks:
            raise RuntimeError(f"Kokoro returned no audio for {segment.id}")
        audio = np.concatenate(chunks)
        duration = len(audio) / SAMPLE_RATE
        if duration != segment.target_seconds:
            chunks = [
                audio
                for _, _, audio in active_pipeline(
                    segment.narration,
                    voice=voice,
                    speed=duration / segment.target_seconds,
                )
            ]
            if not chunks:
                raise RuntimeError(f"Kokoro returned no audio for {segment.id}")
            audio = np.concatenate(chunks)
        missing_samples = round(segment.target_seconds * SAMPLE_RATE) - len(audio)
        if missing_samples > 0:
            audio = np.pad(audio, (0, missing_samples))

        path = output_dir / f"{segment.id}.wav"
        sf.write(path, audio, SAMPLE_RATE)
        tracks.append(
            AudioTrack(
                segment_id=segment.id,
                path=path,
                duration=sf.info(path).duration,
            )
        )

    narration_path = output_dir / "narration.wav"
    concat_file = output_dir / "segments.txt"
    concat_file.write_text(
        "".join(f"file '{track.path.resolve()}'\n" for track in tracks),
        encoding="utf-8",
    )
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(concat_file),
            "-c",
            "copy",
            str(narration_path),
        ],
        check=True,
        capture_output=True,
    )
    return Narration(path=narration_path, tracks=tracks)
