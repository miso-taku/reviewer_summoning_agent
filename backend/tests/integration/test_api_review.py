"""IT-API: POST /api/v1/review 結合テスト (test-plan §3.2 / TC-IT-01〜05)。"""

from __future__ import annotations

import uuid

import pytest

from review_summoning.application.exceptions import (
    ApplicationLlmUnavailableError,
    ApplicationLlmUpstreamError,
)
from review_summoning.application.use_cases.run_review_pipeline import RunReviewPipelineUseCase
from review_summoning.domain.models.editor_output import EditorOutput, PriorityFix
from review_summoning.domain.models.reviewer_persona import ReviewerPersona
from review_summoning.domain.models.structured_review import StructuredReview
from review_summoning.domain.value_objects.identifiers import ReviewerId
from review_summoning.domain.value_objects.manuscript_bundle import TOTAL_INPUT_MAX_CHARS
from review_summoning.domain.value_objects.theme import THEME_MAX_CHARS
from review_summoning.presentation.schemas.response import ReviewSuccessResponse
from tests.integration.conftest import UseCaseWithPipelineTimeout, api_client_for
from tests.support.port_fakes import (
    FakeEditor,
    FakeSingleReview,
    FakeSummoning,
    SlowFakeSummoning,
)

# テスト計画 §10: 最小有効リクエスト
_MIN_VALID_JSON = {
    "theme": "テーマ",
    "draft_body": "本文",
    "structure_memo": None,
    "slides_summary": None,
}


def _rid() -> str:
    return str(uuid.uuid4())


def _persona(rid: str, name: str) -> ReviewerPersona:
    return ReviewerPersona(
        id=ReviewerId.parse(rid),
        display_name=name,
        specialty_axis="専門軸",
        perspective="観点",
    )


def _review(rid: str) -> StructuredReview:
    return StructuredReview(
        reviewer_id=ReviewerId.parse(rid),
        good_points=("良い点",),
        issues=("指摘",),
        concrete_fixes=("修正案",),
    )


def _editor_out(related_id: str) -> EditorOutput:
    return EditorOutput(
        integrated_comment="統合コメント",
        priority_fixes=(
            PriorityFix(
                rank=1,
                summary="優先修正",
                related_reviewer_ids=(ReviewerId.parse(related_id),),
            ),
            PriorityFix(
                rank=2,
                summary="次点",
                related_reviewer_ids=(ReviewerId.parse(related_id),),
            ),
        ),
        deduplication_notes="重複整理",
    )


def _stubbed_use_case() -> RunReviewPipelineUseCase:
    a, b, c = _rid(), _rid(), _rid()
    triple = (_persona(a, "レビュアーA"), _persona(b, "レビュアーB"), _persona(c, "レビュアーC"))
    return RunReviewPipelineUseCase(
        summoning=FakeSummoning(triple),
        single_review=FakeSingleReview({a: _review(a), b: _review(b), c: _review(c)}),
        editor=FakeEditor(_editor_out(a)),
    )


def _assert_fun_612_integrity(body: dict) -> None:
    """FUN §6.1.2 整合性ルール。"""
    assert len(body["reviewers"]) == 3
    assert len(body["reviews"]) == 3
    reviewer_ids = {r["id"] for r in body["reviewers"]}
    for item in body["reviews"]:
        assert item["reviewer_id"] in reviewer_ids
    ranks = [pf["rank"] for pf in body["editor"]["priority_fixes"]]
    assert len(ranks) == len(set(ranks))
    assert all(isinstance(r, int) and r >= 1 for r in ranks)


@pytest.mark.asyncio
@pytest.mark.req("REQ-F-001")
async def test_it_api_01_post_review_success_with_stubbed_ports() -> None:
    """IT-API-01 / TC-IT-01: スタブポートで 200、reviewers/reviews/editor/meta。"""
    async with api_client_for(_stubbed_use_case()) as client:
        response = await client.post("/api/v1/review", json=_MIN_VALID_JSON)

    assert response.status_code == 200
    body = response.json()
    ReviewSuccessResponse.model_validate(body)
    _assert_fun_612_integrity(body)
    assert "editor" in body
    assert "meta" in body
    assert body["meta"]["request_id"]
    assert body["meta"]["completed_at"]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("payload", "description"),
    [
        (
            {"theme": "", "draft_body": "本文", "structure_memo": None, "slides_summary": None},
            "テーマ空",
        ),
        (
            {
                "theme": "テーマ",
                "draft_body": "",
                "structure_memo": "",
                "slides_summary": "",
            },
            "3 ブロック全非空違反",
        ),
        (
            {
                "theme": "x",
                "draft_body": "y" * TOTAL_INPUT_MAX_CHARS,
                "structure_memo": None,
                "slides_summary": None,
            },
            "合計 200000 超過",
        ),
    ],
    ids=["empty_theme", "all_blocks_empty", "total_chars_exceeded"],
)
async def test_it_api_02_validation_errors_return_422(
    payload: dict,
    description: str,
) -> None:
    """IT-API-02 / TC-IT-02: 422 + VALIDATION_ERROR。"""
    async with api_client_for(_stubbed_use_case()) as client:
        response = await client.post("/api/v1/review", json=payload)

    assert response.status_code == 422, description
    payload_body = response.json()
    assert payload_body["error"]["code"] == "VALIDATION_ERROR"


@pytest.mark.asyncio
async def test_it_api_02_domain_validation_empty_theme_whitespace_only() -> None:
    """Pydantic 通過後ドメイン第 2 段: 空白のみテーマ。"""
    async with api_client_for(_stubbed_use_case()) as client:
        response = await client.post(
            "/api/v1/review",
            json={
                "theme": "   ",
                "draft_body": "本文",
                "structure_memo": None,
                "slides_summary": None,
            },
        )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


@pytest.mark.asyncio
async def test_it_api_02_theme_max_length_boundary() -> None:
    """テーマ 2001 文字は 422。"""
    async with api_client_for(_stubbed_use_case()) as client:
        response = await client.post(
            "/api/v1/review",
            json={
                "theme": "あ" * (THEME_MAX_CHARS + 1),
                "draft_body": "本文",
                "structure_memo": None,
                "slides_summary": None,
            },
        )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


@pytest.mark.asyncio
@pytest.mark.req("REQ-NF-010")
async def test_it_api_03_pipeline_timeout_returns_504() -> None:
    """IT-API-03 / TC-IT-05: スタブ遅延 → 504 REQUEST_TIMEOUT。"""
    a, b, c = _rid(), _rid(), _rid()
    triple = (_persona(a, "A"), _persona(b, "B"), _persona(c, "C"))
    inner = RunReviewPipelineUseCase(
        summoning=SlowFakeSummoning(triple, delay_seconds=0.3),
        single_review=FakeSingleReview({a: _review(a), b: _review(b), c: _review(c)}),
        editor=FakeEditor(_editor_out(a)),
    )
    use_case = UseCaseWithPipelineTimeout(inner, pipeline_timeout_seconds=0.05)

    async with api_client_for(use_case) as client:
        response = await client.post("/api/v1/review", json=_MIN_VALID_JSON)

    assert response.status_code == 504
    assert response.json()["error"]["code"] == "REQUEST_TIMEOUT"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("exc", "status", "code"),
    [
        (ApplicationLlmUpstreamError("LLM プロバイダ 5xx"), 502, "LLM_UPSTREAM_ERROR"),
        (ApplicationLlmUnavailableError("接続不可"), 503, "LLM_UNAVAILABLE"),
    ],
)
async def test_it_api_04_llm_errors_map_to_http(
    exc: BaseException,
    status: int,
    code: str,
) -> None:
    """IT-API-04 / TC-IT-04: スタブ例外 → 502/503 + error.code。"""
    a, b, c = _rid(), _rid(), _rid()
    triple = (_persona(a, "A"), _persona(b, "B"), _persona(c, "C"))

    class FailingSummoning(FakeSummoning):
        async def summon(self, theme, manuscript_text_for_llm: str):
            raise exc

    use_case = RunReviewPipelineUseCase(
        summoning=FailingSummoning(triple),
        single_review=FakeSingleReview({}),
        editor=FakeEditor(_editor_out(a)),
    )

    async with api_client_for(use_case) as client:
        response = await client.post("/api/v1/review", json=_MIN_VALID_JSON)

    assert response.status_code == status
    assert response.json()["error"]["code"] == code


class _NeverCalledUseCase:
    async def execute(self, *args, **kwargs):
        raise AssertionError("ユースケースは呼ばれない想定")


@pytest.mark.asyncio
async def test_it_api_02_validation_does_not_invoke_use_case() -> None:
    """422 時にユースケースが実行されないこと。"""
    async with api_client_for(_NeverCalledUseCase()) as client:
        response = await client.post(
            "/api/v1/review",
            json={"theme": "", "draft_body": "x"},
        )
    assert response.status_code == 422
