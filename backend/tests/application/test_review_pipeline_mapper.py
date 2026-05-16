"""map_completed_session_to_success_response の純粋マッピング。"""

import uuid

import pytest

from review_summoning.application.mappers.review_pipeline import (
    map_completed_session_to_success_response,
)
from review_summoning.domain.exceptions import UnexpectedDomainState
from review_summoning.domain.models.editor_output import EditorOutput, PriorityFix
from review_summoning.domain.models.review_session import ReviewSession
from review_summoning.domain.models.reviewer_persona import ReviewerPersona
from review_summoning.domain.models.structured_review import StructuredReview
from review_summoning.domain.value_objects.identifiers import RequestId, ReviewerId
from review_summoning.domain.value_objects.manuscript_bundle import ManuscriptBundle
from review_summoning.domain.value_objects.theme import Theme


def _complete_session() -> ReviewSession:
    theme = Theme.parse("t1")
    manuscript = ManuscriptBundle.parse("d", "m", "", theme=theme)
    session = ReviewSession(theme=theme, manuscript=manuscript)
    a, b, c = str(uuid.uuid4()), str(uuid.uuid4()), str(uuid.uuid4())
    triple = (
        ReviewerPersona(ReviewerId.parse(a), "A", "sa", "pa"),
        ReviewerPersona(ReviewerId.parse(b), "B", "sb", "pb"),
        ReviewerPersona(ReviewerId.parse(c), "C", "sc", "pc"),
    )
    session.assign_reviewers(triple)
    session.record_review(
        StructuredReview(ReviewerId.parse(a), ("ga",), ("ia",), ("fa",))
    )
    session.record_review(
        StructuredReview(ReviewerId.parse(b), ("gb",), ("ib",), ("fb",))
    )
    session.record_review(
        StructuredReview(ReviewerId.parse(c), ("gc",), ("ic",), ("fc",))
    )
    session.attach_editor(
        EditorOutput(
            integrated_comment="int",
            priority_fixes=(
                PriorityFix(1, "one", (ReviewerId.parse(a),)),
                PriorityFix(2, "two", (ReviewerId.parse(b), ReviewerId.parse(c))),
            ),
            deduplication_notes="notes",
        )
    )
    return session


def test_maps_three_reviewers_and_reviews_in_persona_order() -> None:
    session = _complete_session()
    req = RequestId.parse(str(uuid.uuid4()))
    dto = map_completed_session_to_success_response(
        session,
        request_id=req,
        completed_at="2026-05-12T12:00:00Z",
    )
    assert len(dto.reviewers) == 3
    assert len(dto.reviews) == 3
    assert {r.id for r in dto.reviewers} == {rv.reviewer_id for rv in dto.reviews}
    assert dto.editor.integrated_comment == "int"
    assert len(dto.editor.priority_fixes) == 2
    assert dto.editor.priority_fixes[0].related_reviewer_ids == (
        session.reviewers[0].id.value,
    )
    assert dto.meta.request_id == req.value
    assert dto.meta.completed_at == "2026-05-12T12:00:00Z"


def test_rejects_incomplete_session() -> None:
    theme = Theme.parse("t")
    manuscript = ManuscriptBundle.parse("b", "", "", theme=theme)
    session = ReviewSession(theme=theme, manuscript=manuscript)
    with pytest.raises(UnexpectedDomainState):
        map_completed_session_to_success_response(
            session,
            request_id=RequestId.parse(str(uuid.uuid4())),
            completed_at="2026-05-12T12:00:00Z",
        )
