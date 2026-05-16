"""完了した ReviewSession → 成功レスポンス DTO (純粋関数)。"""
from __future__ import annotations

from review_summoning.application.dto import (
    EditorOutDTO,
    MetaOutDTO,
    PriorityFixOutDTO,
    ReviewerOutDTO,
    ReviewItemOutDTO,
    ReviewSuccessResponseDTO,
)
from review_summoning.domain.exceptions import UnexpectedDomainState
from review_summoning.domain.models.review_session import ReviewSession
from review_summoning.domain.value_objects.identifiers import RequestId


def map_completed_session_to_success_response(
    session: ReviewSession,
    *,
    request_id: RequestId,
    completed_at: str,
) -> ReviewSuccessResponseDTO:
    """不変条件を満たした集約のみ受け付ける。"""
    if session.reviewers is None:
        raise UnexpectedDomainState("レビュアーが未確定のままマッピングしようとしました。")
    if session.editor is None:
        raise UnexpectedDomainState("編集長出力が未設定のままマッピングしようとしました。")
    if len(session.reviews) != 3:
        raise UnexpectedDomainState("レビューが 3 件揃っていません。")

    review_by_id = {r.reviewer_id.value: r for r in session.reviews}

    reviewers_out = tuple(
        ReviewerOutDTO(
            id=p.id.value,
            display_name=p.display_name,
            specialty_axis=p.specialty_axis,
            perspective=p.perspective,
        )
        for p in session.reviewers
    )

    reviews_out: list[ReviewItemOutDTO] = []
    for p in session.reviewers:
        r = review_by_id.get(p.id.value)
        if r is None:
            raise UnexpectedDomainState("レビュアーごとのレビューが欠けています。")
        reviews_out.append(
            ReviewItemOutDTO(
                reviewer_id=r.reviewer_id.value,
                good_points=r.good_points,
                issues=r.issues,
                concrete_fixes=r.concrete_fixes,
            )
        )

    ed = session.editor
    editor_out = EditorOutDTO(
        integrated_comment=ed.integrated_comment,
        priority_fixes=tuple(
            PriorityFixOutDTO(
                rank=pf.rank,
                summary=pf.summary,
                related_reviewer_ids=tuple(r.value for r in pf.related_reviewer_ids),
            )
            for pf in ed.priority_fixes
        ),
        deduplication_notes=ed.deduplication_notes,
    )

    meta = MetaOutDTO(request_id=request_id.value, completed_at=completed_at)

    return ReviewSuccessResponseDTO(
        reviewers=reviewers_out,
        reviews=tuple(reviews_out),
        editor=editor_out,
        meta=meta,
    )
