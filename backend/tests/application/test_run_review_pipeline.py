"""RunReviewPipelineUseCase: フェイクポート・並列・タイムアウト (test-plan §4.2 / TEC §6.2)。"""

from __future__ import annotations

import asyncio
import uuid
from typing import Any

import pytest

from review_summoning.application.exceptions import ApplicationPipelineTimeoutError
from review_summoning.application.use_cases.run_review_pipeline import (
    RunReviewPipelineCommand,
    RunReviewPipelineUseCase,
)
from review_summoning.domain.exceptions import InvalidDomainInput
from review_summoning.domain.models.editor_output import EditorOutput, PriorityFix
from review_summoning.domain.models.reviewer_persona import ReviewerPersona
from review_summoning.domain.models.structured_review import StructuredReview
from review_summoning.domain.value_objects.identifiers import RequestId, ReviewerId


def _rid() -> str:
    return str(uuid.uuid4())


def _persona(rid: str, name: str = "R") -> ReviewerPersona:
    return ReviewerPersona(
        id=ReviewerId.parse(rid),
        display_name=name,
        specialty_axis="axis",
        perspective="view",
    )


def _review(rid: str) -> StructuredReview:
    return StructuredReview(
        reviewer_id=ReviewerId.parse(rid),
        good_points=("g",),
        issues=("i",),
        concrete_fixes=("c",),
    )


def _editor_out() -> EditorOutput:
    r0 = _rid()
    return EditorOutput(
        integrated_comment="ic",
        priority_fixes=(
            PriorityFix(
                rank=1,
                summary="s",
                related_reviewer_ids=(ReviewerId.parse(r0),),
            ),
        ),
        deduplication_notes="dn",
    )


class FakeSummoning:
    def __init__(self, triple: tuple[ReviewerPersona, ReviewerPersona, ReviewerPersona]) -> None:
        self.triple = triple
        self.calls: list[str] = []

    async def summon(self, theme: Any, manuscript_text_for_llm: str) -> Any:
        self.calls.append("summon")
        return self.triple


class FakeSingleReview:
    def __init__(
        self,
        reviews_by_id: dict[str, StructuredReview | BaseException],
    ) -> None:
        self._by_id = reviews_by_id
        self.calls: list[str] = []
        self.touched_ids: list[str] = []

    async def review(self, persona: ReviewerPersona, manuscript_text_for_llm: str) -> StructuredReview:
        self.calls.append(f"review:{persona.id.value}")
        self.touched_ids.append(persona.id.value)
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


def _commands() -> tuple[RunReviewPipelineCommand, tuple[str, str, str]]:
    a, b, c = _rid(), _rid(), _rid()
    cmd = RunReviewPipelineCommand(
        theme="テーマ",
        draft_body="本文",
        structure_memo="",
        slides_summary="",
    )
    return cmd, (a, b, c)


@pytest.mark.asyncio
async def test_execute_invocation_order_summon_three_reviews_one_editor() -> None:
    cmd, (a, b, c) = _commands()
    triple = (_persona(a, "A"), _persona(b, "B"), _persona(c, "C"))
    summoning = FakeSummoning(triple)
    reviews = {a: _review(a), b: _review(b), c: _review(c)}
    single = FakeSingleReview(reviews)
    editor = FakeEditor(_editor_out())
    uc = RunReviewPipelineUseCase(summoning, single, editor)

    await uc.execute(cmd, request_id=RequestId.parse(_rid()))

    assert summoning.calls == ["summon"]
    assert set(single.calls) == {f"review:{a}", f"review:{b}", f"review:{c}"}
    assert len(single.calls) == 3
    assert editor.calls == ["integrate"]


@pytest.mark.asyncio
async def test_execute_raises_first_review_failure_in_slot_order() -> None:
    cmd, (a, b, c) = _commands()
    triple = (_persona(a), _persona(b), _persona(c))
    summoning = FakeSummoning(triple)
    err = ValueError("review failed on purpose")
    single = FakeSingleReview(
        {
            a: _review(a),
            b: err,
            c: _review(c),
        }
    )
    editor = FakeEditor(_editor_out())
    uc = RunReviewPipelineUseCase(summoning, single, editor)

    with pytest.raises(ValueError, match="review failed on purpose"):
        await uc.execute(cmd)

    assert editor.calls == []


@pytest.mark.asyncio
async def test_gather_waits_for_all_reviews_before_raising() -> None:
    """TEC §6.2 の「先頭例外マップ」+ gather: 失敗スロットが決まっても他タスクは完了まで走る。"""
    cmd, (a, b, c) = _commands()
    triple = (_persona(a), _persona(b), _persona(c))
    summoning = FakeSummoning(triple)

    async def slow_ok(rid: str) -> StructuredReview:
        await asyncio.sleep(0.05)
        return _review(rid)

    class OrderingFakeReview:
        def __init__(self) -> None:
            self.done: list[str] = []

        async def review(self, persona: ReviewerPersona, manuscript_text_for_llm: str) -> StructuredReview:
            if persona.id.value == b:
                raise ValueError("b fails")
            res = await slow_ok(persona.id.value)
            self.done.append(persona.id.value)
            return res

    single = OrderingFakeReview()
    editor = FakeEditor(_editor_out())
    uc = RunReviewPipelineUseCase(summoning, single, editor)

    with pytest.raises(ValueError, match="b fails"):
        await uc.execute(cmd)

    assert set(single.done) == {a, c}
    assert editor.calls == []


@pytest.mark.asyncio
async def test_pipeline_timeout_wraps_whole_run() -> None:
    cmd, (a, b, c) = _commands()
    triple = (_persona(a), _persona(b), _persona(c))

    class SlowSummon(FakeSummoning):
        async def summon(self, theme: Any, manuscript_text_for_llm: str) -> Any:
            await asyncio.sleep(1.0)
            return self.triple

    summoning = SlowSummon(triple)
    single = FakeSingleReview({a: _review(a), b: _review(b), c: _review(c)})
    editor = FakeEditor(_editor_out())
    uc = RunReviewPipelineUseCase(summoning, single, editor)

    with pytest.raises(ApplicationPipelineTimeoutError):
        await uc.execute(cmd, pipeline_timeout_seconds=0.05)

    assert single.calls == []


@pytest.mark.asyncio
async def test_invalid_theme_async() -> None:
    cmd = RunReviewPipelineCommand(theme="   ", draft_body="x")
    uc = RunReviewPipelineUseCase(
        FakeSummoning((_persona(_rid()), _persona(_rid()), _persona(_rid()))),
        FakeSingleReview({}),
        FakeEditor(_editor_out()),
    )
    with pytest.raises(InvalidDomainInput):
        await uc.execute(cmd)
