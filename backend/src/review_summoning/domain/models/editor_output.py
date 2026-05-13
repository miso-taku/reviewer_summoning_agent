"""編集長の統合出力 (ドメイン表現)。"""

from __future__ import annotations

from dataclasses import dataclass

from review_summoning.domain.value_objects.identifiers import ReviewerId


@dataclass(frozen=True, slots=True)
class PriorityFix:
    """優先修正 1 件 (FUN §5.2.3 の論理構造)。"""

    rank: int
    summary: str
    related_reviewer_ids: tuple[ReviewerId, ...]


@dataclass(frozen=True, slots=True)
class EditorOutput:
    integrated_comment: str
    priority_fixes: tuple[PriorityFix, ...]
    deduplication_notes: str
