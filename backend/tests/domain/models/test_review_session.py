"""TC-U-RS-01: ReviewSession 集約の不変条件 (TEC §4.4.1)。"""

import uuid

import pytest

from review_summoning.domain.exceptions import DomainInvariantViolation, InvalidDomainInput
from review_summoning.domain.models.editor_output import EditorOutput
from review_summoning.domain.models.review_session import ReviewSession
from review_summoning.domain.models.reviewer_persona import ReviewerPersona
from review_summoning.domain.models.structured_review import StructuredReview
from review_summoning.domain.value_objects.identifiers import ReviewerId
from review_summoning.domain.value_objects.manuscript_bundle import ManuscriptBundle
from review_summoning.domain.value_objects.theme import Theme


def _ids() -> tuple[str, str, str]:
    return str(uuid.uuid4()), str(uuid.uuid4()), str(uuid.uuid4())


def _session() -> ReviewSession:
    theme = Theme.parse("topic")
    manuscript = ManuscriptBundle.parse("body", "", "", theme=theme)
    return ReviewSession(theme=theme, manuscript=manuscript)


def _persona(rid: str, name: str = "R") -> ReviewerPersona:
    return ReviewerPersona(
        id=ReviewerId.parse(rid),
        display_name=name,
        specialty_axis="s",
        perspective="p",
    )


def test_cannot_record_review_before_reviewers_assigned() -> None:
    s = _session()
    rid, _, _ = _ids()
    review = StructuredReview(
        reviewer_id=ReviewerId.parse(rid),
        good_points=(),
        issues=(),
        concrete_fixes=(),
    )
    with pytest.raises(DomainInvariantViolation):
        s.record_review(review)


def test_assign_reviewers_must_be_exactly_three() -> None:
    s = _session()
    a, b, _ = _ids()
    with pytest.raises(InvalidDomainInput):
        s.assign_reviewers((_persona(a), _persona(b)))


def test_cannot_assign_reviewers_twice() -> None:
    s = _session()
    a, b, c = _ids()
    triple = (_persona(a), _persona(b), _persona(c))
    s.assign_reviewers(triple)
    with pytest.raises(DomainInvariantViolation):
        s.assign_reviewers(triple)


def test_review_reviewer_id_must_match_summoned() -> None:
    s = _session()
    a, b, c = _ids()
    s.assign_reviewers((_persona(a), _persona(b), _persona(c)))
    foreign = str(uuid.uuid4())
    review = StructuredReview(
        reviewer_id=ReviewerId.parse(foreign),
        good_points=(),
        issues=(),
        concrete_fixes=(),
    )
    with pytest.raises(InvalidDomainInput):
        s.record_review(review)


def test_editor_only_after_three_reviews() -> None:
    s = _session()
    a, b, c = _ids()
    s.assign_reviewers((_persona(a), _persona(b), _persona(c)))
    editor = EditorOutput(
        integrated_comment="x",
        priority_fixes=(),
        deduplication_notes="",
    )
    with pytest.raises(DomainInvariantViolation):
        s.attach_editor(editor)


def test_happy_path_three_reviews_then_editor() -> None:
    s = _session()
    a, b, c = _ids()
    s.assign_reviewers((_persona(a), _persona(b), _persona(c)))
    for rid in (a, b, c):
        s.record_review(
            StructuredReview(
                reviewer_id=ReviewerId.parse(rid),
                good_points=("g",),
                issues=(),
                concrete_fixes=(),
            )
        )
    editor = EditorOutput(
        integrated_comment="integrated",
        priority_fixes=(),
        deduplication_notes="",
    )
    s.attach_editor(editor)
    assert s.editor is editor
    assert len(s.reviews) == 3
