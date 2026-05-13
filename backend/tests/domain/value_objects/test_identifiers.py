"""ReviewerId / RequestId VO (TEC §4.4.2)。"""

import uuid

import pytest

from review_summoning.domain.exceptions import InvalidDomainInput
from review_summoning.domain.value_objects.identifiers import RequestId, ReviewerId


def test_reviewer_id_accepts_uuid_string() -> None:
    u = str(uuid.uuid4())
    rid = ReviewerId.parse(u)
    assert rid.value == u


def test_reviewer_id_rejects_invalid() -> None:
    with pytest.raises(InvalidDomainInput):
        ReviewerId.parse("not-a-uuid")


def test_request_id_same_rules() -> None:
    u = str(uuid.uuid4())
    assert RequestId.parse(u).value == u
