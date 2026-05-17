"""application DTO → presentation レスポンスのマッピング。"""

from __future__ import annotations

import uuid

from review_summoning.application.dto import (
    EditorOutDTO,
    MetaOutDTO,
    PriorityFixOutDTO,
    ReviewerOutDTO,
    ReviewItemOutDTO,
    ReviewSuccessResponseDTO,
)
from review_summoning.presentation.mappers import map_success_dto_to_response


def test_maps_dto_to_pydantic_response() -> None:
    a, b, c = str(uuid.uuid4()), str(uuid.uuid4()), str(uuid.uuid4())
    dto = ReviewSuccessResponseDTO(
        reviewers=(
            ReviewerOutDTO(a, "A", "sa", "pa"),
            ReviewerOutDTO(b, "B", "sb", "pb"),
            ReviewerOutDTO(c, "C", "sc", "pc"),
        ),
        reviews=(
            ReviewItemOutDTO(a, ("g",), ("i",), ("f",)),
            ReviewItemOutDTO(b, (), (), ()),
            ReviewItemOutDTO(c, (), (), ()),
        ),
        editor=EditorOutDTO(
            integrated_comment="ic",
            priority_fixes=(PriorityFixOutDTO(1, "s", (a, b)),),
            deduplication_notes="dn",
        ),
        meta=MetaOutDTO(request_id=str(uuid.uuid4()), completed_at="2026-05-12T12:00:00Z"),
    )
    out = map_success_dto_to_response(dto)
    assert len(out.reviewers) == 3
    assert out.reviews[0].good_points == ["g"]
    assert out.editor.priority_fixes[0].rank == 1
    assert out.meta.completed_at == dto.meta.completed_at
