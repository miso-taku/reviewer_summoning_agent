"""POST /api/v1/review ルータ (FUN §6.1 / TEC §7.1)。"""

from __future__ import annotations

from fastapi import APIRouter, status

from review_summoning.application.use_cases.run_review_pipeline import (
    RunReviewPipelineCommand,
)
from review_summoning.presentation.dependencies import ReviewPipelineUseCaseDep
from review_summoning.presentation.mappers import map_success_dto_to_response
from review_summoning.presentation.schemas.request import ReviewRequestBody
from review_summoning.presentation.schemas.response import ReviewSuccessResponse

router = APIRouter(tags=["review"])


@router.post(
    "/review",
    response_model=ReviewSuccessResponse,
    status_code=status.HTTP_200_OK,
    summary="レビューパイプライン実行",
)
async def post_review(
    body: ReviewRequestBody,
    use_case: ReviewPipelineUseCaseDep,
) -> ReviewSuccessResponse:
    """Pydantic 第 1 段検証後、ユースケース内でドメイン VO 第 2 段検証を通す。"""
    command = RunReviewPipelineCommand(
        theme=body.theme,
        draft_body=body.draft_body,
        structure_memo=body.structure_memo,
        slides_summary=body.slides_summary,
    )
    result = await use_case.execute(command)
    return map_success_dto_to_response(result)
