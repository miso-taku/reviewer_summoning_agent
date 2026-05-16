"""ユースケース出力用 DTO (Pydantic 非依存。presentation 層へ渡す前提データ)。"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ReviewerOutDTO:
    id: str
    display_name: str
    specialty_axis: str
    perspective: str


@dataclass(frozen=True, slots=True)
class ReviewItemOutDTO:
    reviewer_id: str
    good_points: tuple[str, ...]
    issues: tuple[str, ...]
    concrete_fixes: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class PriorityFixOutDTO:
    rank: int
    summary: str
    related_reviewer_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class EditorOutDTO:
    integrated_comment: str
    priority_fixes: tuple[PriorityFixOutDTO, ...]
    deduplication_notes: str


@dataclass(frozen=True, slots=True)
class MetaOutDTO:
    request_id: str
    completed_at: str


@dataclass(frozen=True, slots=True)
class ReviewSuccessResponseDTO:
    reviewers: tuple[ReviewerOutDTO, ...]
    reviews: tuple[ReviewItemOutDTO, ...]
    editor: EditorOutDTO
    meta: MetaOutDTO
