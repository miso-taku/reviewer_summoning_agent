"""1 名分の構造化レビュー (ドメイン表現)。"""

from __future__ import annotations

from dataclasses import dataclass

from review_summoning.domain.value_objects.identifiers import ReviewerId


@dataclass(frozen=True, slots=True)
class StructuredReview:
    """FUN §5.2.2 に対応するコアフィールド (配列は不変タプル)。"""

    reviewer_id: ReviewerId
    good_points: tuple[str, ...]
    issues: tuple[str, ...]
    concrete_fixes: tuple[str, ...]
