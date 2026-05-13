"""編集長統合ポート (TEC §4.4.3)。"""

from __future__ import annotations

from typing import Protocol

from review_summoning.domain.models.editor_output import EditorOutput
from review_summoning.domain.models.structured_review import StructuredReview
from review_summoning.domain.value_objects.theme import Theme


class EditorIntegrationPort(Protocol):
    async def integrate(
        self,
        theme: Theme,
        manuscript_text_for_llm: str,
        reviews: tuple[StructuredReview, StructuredReview, StructuredReview],
    ) -> EditorOutput:
        """3 レビュー完了後に 1 回だけ呼ばれる想定。"""
