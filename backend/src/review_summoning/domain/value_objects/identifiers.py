"""識別子 VO (TEC §4.4.2)。"""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from review_summoning.domain.exceptions import InvalidDomainInput


def _parse_uuid(raw: str, label: str) -> str:
    text = raw.strip()
    try:
        u = uuid.UUID(text)
    except ValueError as e:
        msg = f"{label} は有効な UUID 形式である必要があります。"
        raise InvalidDomainInput(msg) from e
    return str(u)


@dataclass(frozen=True, slots=True)
class ReviewerId:
    """レビュアー ID (UUID 文字列)。"""

    value: str

    @classmethod
    def parse(cls, raw: str) -> ReviewerId:
        return cls(_parse_uuid(raw, "ReviewerId"))


@dataclass(frozen=True, slots=True)
class RequestId:
    """リクエスト相関 ID (UUID 文字列)。"""

    value: str

    @classmethod
    def parse(cls, raw: str) -> RequestId:
        return cls(_parse_uuid(raw, "RequestId"))
