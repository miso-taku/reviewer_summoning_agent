"""成功レスポンス DTO (FUN §6.1.2)。"""

from __future__ import annotations

from pydantic import BaseModel, Field


class ReviewerOut(BaseModel):
    id: str
    display_name: str
    specialty_axis: str
    perspective: str


class ReviewItemOut(BaseModel):
    reviewer_id: str
    good_points: list[str]
    issues: list[str]
    concrete_fixes: list[str]


class PriorityFixOut(BaseModel):
    rank: int = Field(..., ge=1)
    summary: str
    related_reviewer_ids: list[str]


class EditorOut(BaseModel):
    integrated_comment: str
    priority_fixes: list[PriorityFixOut]
    deduplication_notes: str


class MetaOut(BaseModel):
    request_id: str
    completed_at: str


class ReviewSuccessResponse(BaseModel):
    reviewers: list[ReviewerOut]
    reviews: list[ReviewItemOut]
    editor: EditorOut
    meta: MetaOut
