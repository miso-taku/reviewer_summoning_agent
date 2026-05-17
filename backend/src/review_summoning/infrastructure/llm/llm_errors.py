"""LLM / PydanticAI 例外をアプリケーション例外へ正規化 (TEC §7.3 / §9)。"""

from __future__ import annotations

import httpx
from pydantic_ai.exceptions import AgentRunError, ModelHTTPError, UnexpectedModelBehavior
from pydantic_core import ValidationError as PydanticCoreValidationError

from review_summoning.application.exceptions import (
    ApplicationError,
    ApplicationLlmUnavailableError,
    ApplicationLlmUpstreamError,
)


def map_llm_exception(exc: BaseException) -> ApplicationError:
    """プロバイダ 4xx/5xx・パース失敗・接続エラーを写像する。"""
    if isinstance(exc, ApplicationError):
        return exc

    if isinstance(exc, TimeoutError):
        return ApplicationLlmUpstreamError(
            "AI 呼び出しが時間制限を超過しました。時間をおいて再試行してください。"
        )

    if isinstance(exc, ModelHTTPError):
        return ApplicationLlmUpstreamError(
            "AI 側でエラーが発生しました。時間をおいて再試行してください。"
        )

    if isinstance(exc, (UnexpectedModelBehavior, PydanticCoreValidationError)):
        return ApplicationLlmUpstreamError(
            "AI からの応答を解釈できませんでした。時間をおいて再試行してください。"
        )

    if isinstance(exc, AgentRunError):
        return ApplicationLlmUpstreamError(
            "AI 側でエラーが発生しました。時間をおいて再試行してください。"
        )

    if isinstance(exc, httpx.TimeoutException):
        return ApplicationLlmUpstreamError(
            "AI 呼び出しが時間制限を超過しました。時間をおいて再試行してください。"
        )

    if isinstance(exc, (httpx.ConnectError, httpx.NetworkError, ConnectionError, OSError)):
        return ApplicationLlmUnavailableError(
            "一時的に AI サービスへ接続できません。時間をおいて再試行してください。"
        )

    return ApplicationLlmUpstreamError(
        "AI 側でエラーが発生しました。時間をおいて再試行してください。"
    )
