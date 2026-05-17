"""Settings (TEC §10) の単体テスト。"""

from __future__ import annotations

import pytest

from review_summoning.infrastructure.config import Settings, reset_settings_cache


@pytest.fixture(autouse=True)
def _clear_settings_cache() -> None:
    reset_settings_cache()
    yield
    reset_settings_cache()


def test_settings_requires_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    with pytest.raises(ValueError, match="OPENAI_API_KEY"):
        Settings()


def test_model_for_step_openai_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.delenv("LLM_MODEL_SUMMON", raising=False)
    cfg = Settings()
    assert cfg.model_for_step("summon") == "openai:gpt-4o-mini"


def test_model_for_step_explicit_with_prefix(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setenv("LLM_MODEL_REVIEW", "gpt-4o")
    cfg = Settings()
    assert cfg.model_for_step("review") == "openai:gpt-4o"


def test_model_for_step_full_model_string(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("LLM_MODEL_EDITOR", "anthropic:claude-3-5-haiku-latest")
    cfg = Settings()
    assert cfg.model_for_step("editor") == "anthropic:claude-3-5-haiku-latest"
