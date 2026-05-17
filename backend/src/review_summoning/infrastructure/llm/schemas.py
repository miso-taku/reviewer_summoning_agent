"""PydanticAI 構造化出力用スキーマ (infrastructure 内に閉じる)。"""

from __future__ import annotations

from pydantic import BaseModel, Field

class ReviewerPersonaLlmOut(BaseModel):
    display_name: str = Field(..., min_length=1)
    specialty_axis: str = Field(..., min_length=1)
    perspective: str = Field(..., min_length=1)


class SummoningLlmResult(BaseModel):
    reviewers: list[ReviewerPersonaLlmOut] = Field(..., min_length=3, max_length=3)


class StructuredReviewLlmOut(BaseModel):
    good_points: list[str] = Field(default_factory=list)
    issues: list[str] = Field(default_factory=list)
    concrete_fixes: list[str] = Field(default_factory=list)


class PriorityFixLlmOut(BaseModel):
    rank: int = Field(..., ge=1)
    summary: str = Field(..., min_length=1)
    related_reviewer_ids: list[str] = Field(default_factory=list)


class EditorLlmResult(BaseModel):
    integrated_comment: str = Field(..., min_length=1)
    priority_fixes: list[PriorityFixLlmOut] = Field(default_factory=list)
    deduplication_notes: str = Field(..., min_length=1)
