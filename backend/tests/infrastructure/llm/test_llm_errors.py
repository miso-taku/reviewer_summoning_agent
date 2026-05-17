"""LLM 例外正規化 (TEC §7.3 / §9)。"""

from __future__ import annotations

import httpx
from pydantic_ai.exceptions import ModelHTTPError, UnexpectedModelBehavior

from review_summoning.application.exceptions import (
    ApplicationLlmUnavailableError,
    ApplicationLlmUpstreamError,
)
from review_summoning.infrastructure.llm.llm_errors import map_llm_exception


def test_map_model_http_error_to_upstream() -> None:
    exc = ModelHTTPError(502, "openai:gpt-4o-mini", body={"error": "bad"})
    mapped = map_llm_exception(exc)
    assert isinstance(mapped, ApplicationLlmUpstreamError)


def test_map_connect_error_to_unavailable() -> None:
    mapped = map_llm_exception(httpx.ConnectError("connection refused"))
    assert isinstance(mapped, ApplicationLlmUnavailableError)


def test_map_timeout_error_to_upstream() -> None:
    mapped = map_llm_exception(TimeoutError())
    assert isinstance(mapped, ApplicationLlmUpstreamError)


def test_map_unexpected_model_behavior() -> None:
    mapped = map_llm_exception(UnexpectedModelBehavior("bad output"))
    assert isinstance(mapped, ApplicationLlmUpstreamError)
