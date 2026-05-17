"""SingleReviewPort の PydanticAI 実装。"""

from __future__ import annotations

from pydantic_ai import Agent

from review_summoning.domain.models.reviewer_persona import ReviewerPersona
from review_summoning.domain.models.structured_review import StructuredReview
from review_summoning.infrastructure.config import Settings
from review_summoning.infrastructure.llm.agent_runner import run_agent
from review_summoning.infrastructure.llm.schemas import StructuredReviewLlmOut
from review_summoning.infrastructure.llm.trim import trim_string_list

_REVIEW_INSTRUCTIONS = """\
あなたは原稿のレビュアーです。指定されたペルソナの視点で原稿を読み、
good_points（良い点）、issues（課題）、concrete_fixes（具体的な修正案）を
それぞれ箇条書きの文字列配列で返してください。日本語で回答してください。
各配列は最大 50 件までに収めてください。
"""


class PydanticAiSingleReview:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._agent = Agent(
            settings.model_for_step("review"),
            output_type=StructuredReviewLlmOut,
            instructions=_REVIEW_INSTRUCTIONS,
            retries=1,
        )

    async def review(
        self,
        persona: ReviewerPersona,
        manuscript_text_for_llm: str,
    ) -> StructuredReview:
        prompt = (
            f"## あなたのペルソナ\n"
            f"- 表示名: {persona.display_name}\n"
            f"- 専門軸: {persona.specialty_axis}\n"
            f"- 視点: {persona.perspective}\n\n"
            f"## 原稿・メモ\n{manuscript_text_for_llm}\n\n"
            "上記ペルソナの視点で原稿をレビューしてください。"
        )
        result = await run_agent(
            self._agent,
            prompt,
            timeout_seconds=self._settings.llm_call_timeout_seconds,
            log_context=f"review:{persona.id.value}",
            manuscript_text_for_log=manuscript_text_for_llm,
            log_manuscript_plaintext=self._settings.log_manuscript_in_debug,
        )
        return StructuredReview(
            reviewer_id=persona.id,
            good_points=trim_string_list(result.good_points, label="good_points"),
            issues=trim_string_list(result.issues, label="issues"),
            concrete_fixes=trim_string_list(result.concrete_fixes, label="concrete_fixes"),
        )
