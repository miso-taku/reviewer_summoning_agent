"""agent_runner: 個別タイムアウトと例外写像。"""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest
from pydantic_ai.exceptions import ModelHTTPError

from review_summoning.application.exceptions import ApplicationLlmUpstreamError
from review_summoning.infrastructure.llm.agent_runner import run_agent


@pytest.mark.asyncio
async def test_run_agent_returns_output() -> None:
    agent = MagicMock()
    result = MagicMock()
    result.output = "ok"
    agent.run = AsyncMock(return_value=result)

    out = await run_agent(
        agent,
        "prompt",
        timeout_seconds=1.0,
        log_context="test",
    )
    assert out == "ok"
    agent.run.assert_awaited_once_with("prompt")


@pytest.mark.asyncio
async def test_run_agent_timeout_maps_to_upstream() -> None:
    agent = MagicMock()

    async def slow_run(_prompt: str) -> MagicMock:
        await asyncio.sleep(2.0)
        return MagicMock(output="x")

    agent.run = slow_run

    with pytest.raises(ApplicationLlmUpstreamError, match="時間制限"):
        await run_agent(
            agent,
            "prompt",
            timeout_seconds=0.01,
            log_context="test",
        )


@pytest.mark.asyncio
async def test_run_agent_model_http_error_maps() -> None:
    agent = MagicMock()
    agent.run = AsyncMock(
        side_effect=ModelHTTPError(503, "openai:gpt-4o-mini", body=None),
    )

    with pytest.raises(ApplicationLlmUpstreamError):
        await run_agent(
            agent,
            "prompt",
            timeout_seconds=1.0,
            log_context="test",
        )
