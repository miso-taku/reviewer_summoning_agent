"""ReviewSession 集約 (TEC §4.4.1)。"""

from __future__ import annotations

from dataclasses import dataclass, field

from review_summoning.domain.exceptions import DomainInvariantViolation, InvalidDomainInput
from review_summoning.domain.models.editor_output import EditorOutput
from review_summoning.domain.models.reviewer_persona import ReviewerPersona
from review_summoning.domain.models.structured_review import StructuredReview
from review_summoning.domain.value_objects.manuscript_bundle import ManuscriptBundle
from review_summoning.domain.value_objects.theme import Theme


@dataclass
class ReviewSession:
    """1 リクエスト単位: 召喚 → 3 レビュー → 編集長の順序制約を守る。"""

    theme: Theme
    manuscript: ManuscriptBundle
    _reviewers: tuple[ReviewerPersona, ...] | None = field(default=None, repr=False)
    _reviews: dict[str, StructuredReview] = field(default_factory=dict, repr=False)
    _editor: EditorOutput | None = field(default=None, repr=False)

    @property
    def reviewers(self) -> tuple[ReviewerPersona, ...] | None:
        return self._reviewers

    @property
    def reviews(self) -> tuple[StructuredReview, ...]:
        return tuple(self._reviews.values())

    @property
    def editor(self) -> EditorOutput | None:
        return self._editor

    def assign_reviewers(self, personas: tuple[ReviewerPersona, ...]) -> None:
        if self._reviewers is not None:
            raise DomainInvariantViolation("レビュアーは既に確定済みです。")
        if len(personas) != 3:
            raise InvalidDomainInput("レビュアーはちょうど 3 名である必要があります。")
        self._reviewers = personas

    def record_review(self, review: StructuredReview) -> None:
        if self._reviewers is None:
            raise DomainInvariantViolation(
                "レビュアーが 3 名確定する前にレビューを記録できません。"
            )
        allowed = {p.id.value for p in self._reviewers}
        rid = review.reviewer_id.value
        if rid not in allowed:
            raise InvalidDomainInput("レビューの reviewer_id が召喚済みレビュアーと一致しません。")
        if rid in self._reviews:
            raise DomainInvariantViolation("同一レビュアーに対するレビューは既に記録済みです。")
        self._reviews[rid] = review

    def attach_editor(self, output: EditorOutput) -> None:
        if len(self._reviews) != 3:
            raise DomainInvariantViolation(
                "3 件のレビューが揃う前に編集長出力を設定できません。"
            )
        if self._editor is not None:
            raise DomainInvariantViolation("編集長出力は既に設定済みです。")
        self._editor = output
