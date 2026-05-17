"""Settings: API キー・モデル名・ログレベル (TEC §10)。"""

from __future__ import annotations

import logging
from functools import lru_cache
from typing import Literal

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from review_summoning.infrastructure.llm.constants import DEFAULT_LLM_CALL_TIMEOUT_SECONDS

LlmStep = Literal["summon", "review", "editor"]

_DEFAULT_OPENAI_MODEL = "openai:gpt-4o-mini"
_DEFAULT_ANTHROPIC_MODEL = "anthropic:claude-3-5-sonnet-latest"


class Settings(BaseSettings):
    """環境変数から読み込む実行時設定。"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    openai_api_key: str | None = Field(default=None, validation_alias="OPENAI_API_KEY")
    anthropic_api_key: str | None = Field(default=None, validation_alias="ANTHROPIC_API_KEY")
    llm_base_url: str | None = Field(default=None, validation_alias="LLM_BASE_URL")
    llm_model_summon: str | None = Field(default=None, validation_alias="LLM_MODEL_SUMMON")
    llm_model_review: str | None = Field(default=None, validation_alias="LLM_MODEL_REVIEW")
    llm_model_editor: str | None = Field(default=None, validation_alias="LLM_MODEL_EDITOR")
    log_level: str = Field(default="INFO", validation_alias="LOG_LEVEL")
    llm_call_timeout_seconds: float = Field(
        default=DEFAULT_LLM_CALL_TIMEOUT_SECONDS,
        validation_alias="LLM_CALL_TIMEOUT_SECONDS",
    )
    log_manuscript_in_debug: bool = Field(
        default=False,
        validation_alias="LOG_MANUSCRIPT_IN_DEBUG",
    )

    @model_validator(mode="after")
    def _require_api_key(self) -> Settings:
        if not self.openai_api_key and not self.anthropic_api_key:
            raise ValueError(
                "OPENAI_API_KEY または ANTHROPIC_API_KEY のいずれかを設定してください。"
            )
        return self

    @property
    def provider_prefix(self) -> str:
        if self.openai_api_key:
            return "openai"
        return "anthropic"

    def model_for_step(self, step: LlmStep) -> str:
        """ステップ別モデル名。`provider:model` 形式で返す。"""
        explicit = {
            "summon": self.llm_model_summon,
            "review": self.llm_model_review,
            "editor": self.llm_model_editor,
        }[step]
        if explicit:
            return explicit if ":" in explicit else f"{self.provider_prefix}:{explicit}"
        return _DEFAULT_OPENAI_MODEL if self.openai_api_key else _DEFAULT_ANTHROPIC_MODEL

    def configure_logging(self) -> None:
        level = getattr(logging, self.log_level.upper(), logging.INFO)
        logging.basicConfig(level=level, force=True)


@lru_cache
def get_settings() -> Settings:
    return Settings()


def reset_settings_cache() -> None:
    get_settings.cache_clear()
