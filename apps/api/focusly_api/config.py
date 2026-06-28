from dataclasses import dataclass, field
from os import environ
from pathlib import Path

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[3]


@dataclass(frozen=True, slots=True)
class Settings:
    cerebras_api_key: str = field(default_factory=lambda: environ.get("CEREBRAS_API_KEY", ""))
    cerebras_base_url: str = field(
        default_factory=lambda: environ.get("CEREBRAS_BASE_URL", "https://api.cerebras.ai/v1")
    )
    cerebras_model: str = field(
        default_factory=lambda: environ.get("CEREBRAS_MODEL", "zai-glm-4.7")
    )
    kokoro_voice: str = field(default_factory=lambda: environ.get("KOKORO_VOICE", "af_heart"))
    data_dir: Path = field(
        default_factory=lambda: Path(environ.get("FOCUSLY_DATA_DIR", REPO_ROOT / "data/jobs"))
    )
    database_path: Path = field(
        default_factory=lambda: Path(
            environ.get("FOCUSLY_DATABASE_PATH", REPO_ROOT / "data/focusly.db")
        )
    )
    video_package_dir: Path = field(
        default_factory=lambda: Path(
            environ.get("FOCUSLY_VIDEO_DIR", REPO_ROOT / "packages/video")
        )
    )
    cors_origin: str = field(
        default_factory=lambda: environ.get("FOCUSLY_CORS_ORIGIN", "http://localhost:3000")
    )


def load_settings(*, env_file: Path | None = None) -> Settings:
    load_dotenv(env_file or REPO_ROOT / ".env", override=False)
    return Settings()
