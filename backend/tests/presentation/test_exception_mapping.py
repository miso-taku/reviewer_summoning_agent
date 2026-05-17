"""例外 → HTTP ステータス・error.code (FUN §8.2 / TEC §7.3)。"""

from __future__ import annotations

import uuid
from typing import Any

import pytest
from fastapi.testclient import TestClient

from review_summoning.application.dto import (
    EditorOutDTO,
    MetaOutDTO,
    PriorityFixOutDTO,
    ReviewerOutDTO,
    ReviewItemOutDTO,
    ReviewSuccessResponseDTO,
)
from review_summoning.application.exceptions import (
    ApplicationLlmUnavailableError,
    ApplicationLlmUpstreamError,
    ApplicationPipelineTimeoutError,
)
from review_summoning.application.use_cases.run_review_pipeline import (
    RunReviewPipelineCommand,
    RunReviewPipelineUseCase,
)
from review_summoning.domain.exceptions import InvalidDomainInput
from review_summoning.presentation.dependencies import get_review_pipeline_use_case
from review_summoning.presentation.main import create_app

_VALID_JSON = {
    "theme": "テーマ",
    "draft_body": "本文",
    "structure_memo": None,
    "slides_summary": None,
}


def _client_with_use_case(use_case: RunReviewPipelineUseCase) -> TestClient:
    app = create_app()
    app.dependency_overrides[get_review_pipeline_use_case] = lambda: use_case
    return TestClient(app)


class _StubUseCase:
    def __init__(self, outcome: Any) -> None:
        self._outcome = outcome

    async def execute(self, command: RunReviewPipelineCommand, **kwargs: Any) -> Any:
        if isinstance(self._outcome, BaseException):
            raise self._outcome
        return self._outcome


def _success_dto() -> ReviewSuccessResponseDTO:
    rid = str(uuid.uuid4())
    return ReviewSuccessResponseDTO(
        reviewers=(
            ReviewerOutDTO(rid, "A", "sa", "pa"),
            ReviewerOutDTO(str(uuid.uuid4()), "B", "sb", "pb"),
            ReviewerOutDTO(str(uuid.uuid4()), "C", "sc", "pc"),
        ),
        reviews=(
            ReviewItemOutDTO(rid, ("g",), ("i",), ("c",)),
            ReviewItemOutDTO(str(uuid.uuid4()), (), (), ()),
            ReviewItemOutDTO(str(uuid.uuid4()), (), (), ()),
        ),
        editor=EditorOutDTO(
            integrated_comment="ic",
            priority_fixes=(PriorityFixOutDTO(1, "fix", (rid,)),),
            deduplication_notes="dn",
        ),
        meta=MetaOutDTO(request_id=str(uuid.uuid4()), completed_at="2026-05-12T12:00:00Z"),
    )


@pytest.mark.parametrize(
    ("exc", "status", "code"),
    [
        (InvalidDomainInput("テーマが空"), 422, "VALIDATION_ERROR"),
        (ApplicationLlmUpstreamError("LLM 5xx"), 502, "LLM_UPSTREAM_ERROR"),
        (ApplicationLlmUnavailableError("接続不可"), 503, "LLM_UNAVAILABLE"),
        (
            ApplicationPipelineTimeoutError("タイムアウト"),
            504,
            "REQUEST_TIMEOUT",
        ),
    ],
)
def test_maps_application_and_domain_exceptions(
    exc: BaseException,
    status: int,
    code: str,
) -> None:
    client = _client_with_use_case(_StubUseCase(exc))
    response = client.post("/api/v1/review", json=_VALID_JSON)
    assert response.status_code == status
    payload = response.json()
    assert payload["error"]["code"] == code


class _NeverCalledUseCase:
    async def execute(self, *args: Any, **kwargs: Any) -> Any:
        raise AssertionError("ユースケースは呼ばれない想定")


def test_maps_pydantic_validation_to_422() -> None:
    client = _client_with_use_case(_NeverCalledUseCase())
    response = client.post(
        "/api/v1/review",
        json={"theme": "", "draft_body": "", "structure_memo": "", "slides_summary": ""},
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_success_returns_200_with_reviewers_reviews_editor_meta() -> None:
    dto = _success_dto()
    client = _client_with_use_case(_StubUseCase(dto))
    response = client.post("/api/v1/review", json=_VALID_JSON)
    assert response.status_code == 200
    body = response.json()
    assert len(body["reviewers"]) == 3
    assert len(body["reviews"]) == 3
    assert "editor" in body
    assert "meta" in body
