"""ReviewerSummoningPort の PydanticAI 実装。"""

from __future__ import annotations

import uuid

from pydantic_ai import Agent

from review_summoning.application.exceptions import ApplicationLlmUpstreamError
from review_summoning.domain.models.reviewer_persona import ReviewerPersona
from review_summoning.domain.value_objects.identifiers import ReviewerId
from review_summoning.domain.value_objects.theme import Theme
from review_summoning.infrastructure.config import Settings
from review_summoning.infrastructure.llm.agent_runner import run_agent
from review_summoning.infrastructure.llm.schemas import SummoningLlmResult

_SUMMON_INSTRUCTIONS = """\
あなたは原稿レビューのための「レビュアー召喚」担当です。
与えられたテーマと原稿テキストに基づき、重複の少ない 3 名のレビュアーペルソナを設計してください。
各ペルソナは display_name（表示名）、specialty_axis（専門軸）、perspective（視点）を持ちます。
3 名は互いに異なる専門軸と視点を持つこと。日本語で回答してください。
"""


class PydanticAiReviewerSummoning:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._agent = Agent(
            settings.model_for_step("summon"),
            output_type=SummoningLlmResult,
            instructions=_SUMMON_INSTRUCTIONS,
            retries=1,
        )

    async def summon(
        self,
        theme: Theme,
        manuscript_text_for_llm: str,
    ) -> tuple[ReviewerPersona, ReviewerPersona, ReviewerPersona]:
        prompt = (
            f"## テーマ\n{theme.value}\n\n"
            f"## 原稿・メモ\n{manuscript_text_for_llm}\n\n"
            "上記に基づき、レビュアー 3 名を設計してください。"
        )
        result = await run_agent(
            self._agent,
            prompt,
            timeout_seconds=self._settings.llm_call_timeout_seconds,
            log_context="summon",
            manuscript_text_for_log=manuscript_text_for_llm,
            log_manuscript_plaintext=self._settings.log_manuscript_in_debug,
        )
        if len(result.reviewers) != 3:
            raise ApplicationLlmUpstreamError(
                "AI から 3 名のレビュアーを取得できませんでした。"
            )
        personas: list[ReviewerPersona] = []
        for item in result.reviewers:
            personas.append(
                ReviewerPersona(
                    id=ReviewerId.parse(str(uuid.uuid4())),
                    display_name=item.display_name.strip(),
                    specialty_axis=item.specialty_axis.strip(),
                    perspective=item.perspective.strip(),
                )
            )
        return (personas[0], personas[1], personas[2])
