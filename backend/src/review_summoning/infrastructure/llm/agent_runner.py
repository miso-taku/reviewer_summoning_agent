"""PydanticAI Agent 実行の共通ラッパ（個別タイムアウト・例外正規化）。"""

from __future__ import annotations

import asyncio
import logging
from typing import TypeVar

from pydantic_ai import Agent

from review_summoning.infrastructure.llm.llm_errors import map_llm_exception
from review_summoning.infrastructure.llm.logging_utils import mask_if_present

logger = logging.getLogger(__name__)

OutputT = TypeVar("OutputT")


async def run_agent(
    agent: Agent[None, OutputT],
    user_prompt: str,
    *,
    timeout_seconds: float,
    log_context: str,
    manuscript_text_for_log: str | None = None,
    log_manuscript_plaintext: bool = False,
) -> OutputT:
    """`agent.run` を wait_for で包み、例外をアプリケーション層向けに正規化する。"""
    safe_prompt = mask_if_present(
        user_prompt[:500] + ("…" if len(user_prompt) > 500 else ""),
        manuscript_text_for_log,
        allow_plaintext=log_manuscript_plaintext,
    )
    logger.debug("LLM 呼び出し開始 context=%s prompt_preview=%s", log_context, safe_prompt)
    try:
        result = await asyncio.wait_for(
            agent.run(user_prompt),
            timeout=timeout_seconds,
        )
    except Exception as exc:
        mapped = map_llm_exception(exc)
        logger.warning(
            "LLM 呼び出し失敗 context=%s error_type=%s",
            log_context,
            type(exc).__name__,
        )
        raise mapped from exc

    logger.debug("LLM 呼び出し完了 context=%s", log_context)
    return result.output
