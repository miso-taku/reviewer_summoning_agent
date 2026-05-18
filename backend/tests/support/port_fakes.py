"""結合・application テスト向けインメモリポートフェイク (test-plan §6.1)。"""

from __future__ import annotations

import asyncio
from typing import Any

from review_summoning.domain.models.editor_output import EditorOutput
from review_summoning.domain.models.reviewer_persona import ReviewerPersona
from review_summoning.domain.models.structured_review import StructuredReview


class FakeSummoning:
    def __init__(self, triple: tuple[ReviewerPersona, ReviewerPersona, ReviewerPersona]) -> None:
        self.triple = triple
        self.calls: list[str] = []

    async def summon(self, theme: Any, manuscript_text_for_llm: str) -> Any:
        self.calls.append("summon")
        return self.triple


class SlowFakeSummoning(FakeSummoning):
    def __init__(
        self,
        triple: tuple[ReviewerPersona, ReviewerPersona, ReviewerPersona],
        *,
        delay_seconds: float,
    ) -> None:
        super().__init__(triple)
        self._delay_seconds = delay_seconds

    async def summon(self, theme: Any, manuscript_text_for_llm: str) -> Any:
        await asyncio.sleep(self._delay_seconds)
        return await super().summon(theme, manuscript_text_for_llm)


class FakeSingleReview:
    def __init__(
        self,
        reviews_by_id: dict[str, StructuredReview | BaseException],
    ) -> None:
        self._by_id = reviews_by_id
        self.calls: list[str] = []

    async def review(self, persona: ReviewerPersona, manuscript_text_for_llm: str) -> StructuredReview:
        self.calls.append(f"review:{persona.id.value}")
        outcome = self._by_id[persona.id.value]
        if isinstance(outcome, BaseException):
            raise outcome
        await asyncio.sleep(0)
        return outcome


class FakeEditor:
    def __init__(self, output: EditorOutput) -> None:
        self.output = output
        self.calls: list[str] = []

    async def integrate(self, theme: Any, manuscript_text_for_llm: str, reviews: Any) -> EditorOutput:
        self.calls.append("integrate")
        return self.output
