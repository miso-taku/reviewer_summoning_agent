"""application DTO → presentation スキーマ (純粋マッピング)。"""

from __future__ import annotations

from review_summoning.application.dto import ReviewSuccessResponseDTO
from review_summoning.presentation.schemas.response import (
    EditorOut,
    MetaOut,
    PriorityFixOut,
    ReviewerOut,
    ReviewItemOut,
    ReviewSuccessResponse,
)


def map_success_dto_to_response(dto: ReviewSuccessResponseDTO) -> ReviewSuccessResponse:
    return ReviewSuccessResponse(
        reviewers=[
            ReviewerOut(
                id=r.id,
                display_name=r.display_name,
                specialty_axis=r.specialty_axis,
                perspective=r.perspective,
            )
            for r in dto.reviewers
        ],
        reviews=[
            ReviewItemOut(
                reviewer_id=r.reviewer_id,
                good_points=list(r.good_points),
                issues=list(r.issues),
                concrete_fixes=list(r.concrete_fixes),
            )
            for r in dto.reviews
        ],
        editor=EditorOut(
            integrated_comment=dto.editor.integrated_comment,
            priority_fixes=[
                PriorityFixOut(
                    rank=pf.rank,
                    summary=pf.summary,
                    related_reviewer_ids=list(pf.related_reviewer_ids),
                )
                for pf in dto.editor.priority_fixes
            ],
            deduplication_notes=dto.editor.deduplication_notes,
        ),
        meta=MetaOut(
            request_id=dto.meta.request_id,
            completed_at=dto.meta.completed_at,
        ),
    )
