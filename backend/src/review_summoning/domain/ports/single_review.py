"""単一レビューポート (TEC §4.4.3)。"""

from __future__ import annotations

from typing import Protocol

from review_summoning.domain.models.reviewer_persona import ReviewerPersona
from review_summoning.domain.models.structured_review import StructuredReview


class SingleReviewPort(Protocol):
    async def review(
        self,
        persona: ReviewerPersona,
        manuscript_text_for_llm: str,
    ) -> StructuredReview:
        """1 名分の構造化レビューを返す。"""
