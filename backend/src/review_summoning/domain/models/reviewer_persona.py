"""召喚されたレビュアー (ドメイン表現。Pydantic 非依存)。"""

from __future__ import annotations

from dataclasses import dataclass

from review_summoning.domain.value_objects.identifiers import ReviewerId


@dataclass(frozen=True, slots=True)
class ReviewerPersona:
    """レビュアー 1 名分 (FUN §5.2.1 の論理フィールドに対応)。"""

    id: ReviewerId
    display_name: str
    specialty_axis: str
    perspective: str
