from pathlib import Path

import pytest

from focusly_api.config import load_settings


def test_load_settings_reads_root_env_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    for name in (
        "CEREBRAS_API_KEY",
        "CEREBRAS_BASE_URL",
        "CEREBRAS_MODEL",
        "KOKORO_VOICE",
        "FOCUSLY_CORS_ORIGIN",
    ):
        monkeypatch.delenv(name, raising=False)
    env_file = tmp_path / ".env"
    env_file.write_text(
        "\n".join(
            [
                "CEREBRAS_API_KEY=test-key",
                "CEREBRAS_BASE_URL=https://example.com/v1",
                "CEREBRAS_MODEL=test-model",
                "KOKORO_VOICE=test-voice",
                "FOCUSLY_CORS_ORIGIN=http://127.0.0.1:3000",
            ]
        ),
        encoding="utf-8",
    )

    settings = load_settings(env_file=env_file)

    assert settings.cerebras_api_key == "test-key"
    assert settings.cerebras_base_url == "https://example.com/v1"
    assert settings.cerebras_model == "test-model"
    assert settings.kokoro_voice == "test-voice"
    assert settings.cors_origin == "http://127.0.0.1:3000"
