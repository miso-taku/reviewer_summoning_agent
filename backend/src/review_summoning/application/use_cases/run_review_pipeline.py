"""RunReviewPipelineUseCase: 召喚 → 3 名並列レビュー → 編集長 のパイプライン。

TEC §4.3 / §6.2 / §9.2 に準拠。
並列失敗時は asyncio.gather(return_exceptions=True) で全タスク完了を待ち、
スロット順で最初の例外を伝播する。TEC §6.2 の「先頭例外マップ」案に合わせる。
"""

from __future__ import annotations

import asyncio
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime

from review_summoning.application.dto import ReviewSuccessResponseDTO
from review_summoning.application.exceptions import ApplicationPipelineTimeoutError
from review_summoning.application.manuscript_text import manuscript_bundle_to_llm_text
from review_summoning.application.mappers.review_pipeline import (
    map_completed_session_to_success_response,
)
from review_summoning.domain.models.review_session import ReviewSession
from review_summoning.domain.models.structured_review import StructuredReview
from review_summoning.domain.ports.editor_integration import EditorIntegrationPort
from review_summoning.domain.ports.reviewer_summoning import ReviewerSummoningPort
from review_summoning.domain.ports.single_review import SingleReviewPort
from review_summoning.domain.value_objects.identifiers import RequestId
from review_summoning.domain.value_objects.manuscript_bundle import ManuscriptBundle
from review_summoning.domain.value_objects.theme import Theme

# TEC §9.1 / §9.2: サーバ全体バジェット (秒)
DEFAULT_PIPELINE_TIMEOUT_SECONDS = 170.0


@dataclass(frozen=True, slots=True)
class RunReviewPipelineCommand:
    """presentation / テストから渡すコマンド (手順 1: ドメイン VO 検証対象の素データ)。"""

    theme: str
    draft_body: str | None = None
    structure_memo: str | None = None
    slides_summary: str | None = None


def _utc_completed_at_iso_z() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


class RunReviewPipelineUseCase:
    """ReviewerSummoningPort → SingleReviewPort を3並列 → EditorIntegrationPort。"""

    def __init__(
        self,
        summoning: ReviewerSummoningPort,
        single_review: SingleReviewPort,
        editor: EditorIntegrationPort,
    ) -> None:
        self._summoning = summoning
        self._single_review = single_review
        self._editor = editor

    async def execute(
        self,
        command: RunReviewPipelineCommand,
        *,
        request_id: RequestId | None = None,
        pipeline_timeout_seconds: float = DEFAULT_PIPELINE_TIMEOUT_SECONDS,
    ) -> ReviewSuccessResponseDTO:
        theme_vo = Theme.parse(command.theme)
        manuscript_vo = ManuscriptBundle.parse(
            command.draft_body or "",
            command.structure_memo or "",
            command.slides_summary or "",
            theme=theme_vo,
        )
        req_id = request_id or RequestId.parse(str(uuid.uuid4()))
        manuscript_text = manuscript_bundle_to_llm_text(manuscript_vo)
        session = ReviewSession(theme=theme_vo, manuscript=manuscript_vo)

        try:
            await asyncio.wait_for(
                self._run_without_budget(session, manuscript_text),
                timeout=pipeline_timeout_seconds,
            )
        except TimeoutError as e:
            raise ApplicationPipelineTimeoutError(
                "レビューパイプラインがサーバ側時間制限を超過しました。"
            ) from e

        return map_completed_session_to_success_response(
            session,
            request_id=req_id,
            completed_at=_utc_completed_at_iso_z(),
        )

    async def _run_without_budget(
        self,
        session: ReviewSession,
        manuscript_text: str,
    ) -> None:
        personas = await self._summoning.summon(session.theme, manuscript_text)
        session.assign_reviewers(personas)

        results = await asyncio.gather(
            *[
                self._single_review.review(persona, manuscript_text)
                for persona in personas
            ],
            return_exceptions=True,
        )

        structured: list[StructuredReview] = []
        for item in results:
            if isinstance(item, BaseException):
                raise item
            structured.append(item)

        reviews_for_editor: tuple[StructuredReview, StructuredReview, StructuredReview] = (
            structured[0],
            structured[1],
            structured[2],
        )

        for rv in reviews_for_editor:
            session.record_review(rv)

        editor_out = await self._editor.integrate(
            session.theme,
            manuscript_text,
            reviews_for_editor,
        )
        session.attach_editor(editor_out)
