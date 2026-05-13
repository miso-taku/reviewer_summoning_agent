"""召喚ポート (TEC §4.4.3)。"""

from __future__ import annotations

from typing import Protocol

from review_summoning.domain.models.reviewer_persona import ReviewerPersona
from review_summoning.domain.value_objects.theme import Theme


class ReviewerSummoningPort(Protocol):
    async def summon(
        self,
        theme: Theme,
        manuscript_text_for_llm: str,
    ) -> tuple[ReviewerPersona, ReviewerPersona, ReviewerPersona]:
        """3 名のペルソナを返す。"""
