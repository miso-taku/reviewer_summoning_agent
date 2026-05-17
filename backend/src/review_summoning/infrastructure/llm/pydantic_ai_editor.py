"""EditorIntegrationPort の PydanticAI 実装。"""

from __future__ import annotations

from pydantic_ai import Agent

from review_summoning.domain.models.editor_output import EditorOutput, PriorityFix
from review_summoning.domain.models.structured_review import StructuredReview
from review_summoning.domain.value_objects.identifiers import ReviewerId
from review_summoning.domain.value_objects.theme import Theme
from review_summoning.infrastructure.config import Settings
from review_summoning.infrastructure.llm.agent_runner import run_agent
from review_summoning.infrastructure.llm.schemas import EditorLlmResult
from review_summoning.infrastructure.llm.trim import trim_priority_fixes

_EDITOR_INSTRUCTIONS = """\
あなたは編集長です。テーマ・原稿・3 名のレビュー結果を踏まえ、
integrated_comment（統合コメント）、priority_fixes（優先修正。rank 昇順の正整数、
summary、related_reviewer_ids は任意の UUID 文字列配列）、
deduplication_notes（重複整理メモ）を日本語で返してください。
priority_fixes は最大 20 件以内にしてください。
"""


def _format_reviews_for_prompt(reviews: tuple[StructuredReview, StructuredReview, StructuredReview]) -> str:
    blocks: list[str] = []
    for rv in reviews:
        blocks.append(
            f"### reviewer_id={rv.reviewer_id.value}\n"
            f"良い点: {list(rv.good_points)}\n"
            f"課題: {list(rv.issues)}\n"
            f"修正案: {list(rv.concrete_fixes)}\n"
        )
    return "\n".join(blocks)


class PydanticAiEditorIntegration:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._agent = Agent(
            settings.model_for_step("editor"),
            output_type=EditorLlmResult,
            instructions=_EDITOR_INSTRUCTIONS,
            retries=1,
        )

    async def integrate(
        self,
        theme: Theme,
        manuscript_text_for_llm: str,
        reviews: tuple[StructuredReview, StructuredReview, StructuredReview],
    ) -> EditorOutput:
        prompt = (
            f"## テーマ\n{theme.value}\n\n"
            f"## 原稿・メモ\n{manuscript_text_for_llm}\n\n"
            f"## 3 名のレビュー\n{_format_reviews_for_prompt(reviews)}\n\n"
            "編集長として統合コメントと優先修正を作成してください。"
        )
        result = await run_agent(
            self._agent,
            prompt,
            timeout_seconds=self._settings.llm_call_timeout_seconds,
            log_context="editor",
            manuscript_text_for_log=manuscript_text_for_llm,
            log_manuscript_plaintext=self._settings.log_manuscript_in_debug,
        )
        fixes_raw = trim_priority_fixes(result.priority_fixes)
        priority_fixes: list[PriorityFix] = []
        for item in fixes_raw:
            related = tuple(ReviewerId.parse(rid) for rid in item.related_reviewer_ids if rid.strip())
            priority_fixes.append(
                PriorityFix(
                    rank=item.rank,
                    summary=item.summary.strip(),
                    related_reviewer_ids=related,
                )
            )
        return EditorOutput(
            integrated_comment=result.integrated_comment.strip(),
            priority_fixes=tuple(priority_fixes),
            deduplication_notes=result.deduplication_notes.strip(),
        )
