"""PydanticAI アダプタ (Agent.run をモック、実 LLM 非呼び出し)。"""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, patch

import pytest

from review_summoning.domain.models.reviewer_persona import ReviewerPersona
from review_summoning.domain.models.structured_review import StructuredReview
from review_summoning.domain.value_objects.identifiers import ReviewerId
from review_summoning.domain.value_objects.theme import Theme
from review_summoning.infrastructure.config import Settings
from review_summoning.infrastructure.llm.pydantic_ai_editor import PydanticAiEditorIntegration
from review_summoning.infrastructure.llm.pydantic_ai_review import PydanticAiSingleReview
from review_summoning.infrastructure.llm.pydantic_ai_summoning import PydanticAiReviewerSummoning
from review_summoning.infrastructure.llm.schemas import (
    EditorLlmResult,
    PriorityFixLlmOut,
    ReviewerPersonaLlmOut,
    StructuredReviewLlmOut,
    SummoningLlmResult,
)


@pytest.fixture
def settings(monkeypatch: pytest.MonkeyPatch) -> Settings:
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    return Settings()


@pytest.mark.asyncio
async def test_summoning_returns_three_personas(settings: Settings) -> None:
    llm_out = SummoningLlmResult(
        reviewers=[
            ReviewerPersonaLlmOut(
                display_name="A",
                specialty_axis="技術",
                perspective="実装",
            ),
            ReviewerPersonaLlmOut(
                display_name="B",
                specialty_axis="構成",
                perspective="読者",
            ),
            ReviewerPersonaLlmOut(
                display_name="C",
                specialty_axis="表現",
                perspective="文体",
            ),
        ]
    )
    adapter = PydanticAiReviewerSummoning(settings)
    with patch(
        "review_summoning.infrastructure.llm.pydantic_ai_summoning.run_agent",
        new=AsyncMock(return_value=llm_out),
    ):
        triple = await adapter.summon(Theme.parse("テーマ"), "原稿本文")

    assert len(triple) == 3
    for p in triple:
        ReviewerId.parse(p.id.value)


@pytest.mark.asyncio
async def test_review_trims_arrays(settings: Settings) -> None:
    rid = str(uuid.uuid4())
    persona = ReviewerPersona(
        id=ReviewerId.parse(rid),
        display_name="A",
        specialty_axis="x",
        perspective="y",
    )
    llm_out = StructuredReviewLlmOut(
        good_points=[f"g{i}" for i in range(60)],
        issues=["i1"],
        concrete_fixes=[],
    )
    adapter = PydanticAiSingleReview(settings)
    with patch(
        "review_summoning.infrastructure.llm.pydantic_ai_review.run_agent",
        new=AsyncMock(return_value=llm_out),
    ):
        review = await adapter.review(persona, "原稿")

    assert len(review.good_points) == 50
    assert review.reviewer_id.value == rid


@pytest.mark.asyncio
async def test_editor_trims_priority_fixes(settings: Settings) -> None:
    theme = Theme.parse("テーマ")
    rid = str(uuid.uuid4())
    reviews = (
        StructuredReview(
            reviewer_id=ReviewerId.parse(rid),
            good_points=(),
            issues=(),
            concrete_fixes=(),
        ),
        StructuredReview(
            reviewer_id=ReviewerId.parse(str(uuid.uuid4())),
            good_points=(),
            issues=(),
            concrete_fixes=(),
        ),
        StructuredReview(
            reviewer_id=ReviewerId.parse(str(uuid.uuid4())),
            good_points=(),
            issues=(),
            concrete_fixes=(),
        ),
    )
    fixes = [
        PriorityFixLlmOut(rank=i + 1, summary=f"s{i}", related_reviewer_ids=[rid])
        for i in range(25)
    ]
    llm_out = EditorLlmResult(
        integrated_comment="統合",
        priority_fixes=fixes,
        deduplication_notes="メモ",
    )
    adapter = PydanticAiEditorIntegration(settings)
    with patch(
        "review_summoning.infrastructure.llm.pydantic_ai_editor.run_agent",
        new=AsyncMock(return_value=llm_out),
    ):
        out = await adapter.integrate(theme, "原稿", reviews)

    assert len(out.priority_fixes) == 20
    assert out.integrated_comment == "統合"
