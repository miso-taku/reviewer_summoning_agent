"""エラーレスポンス (FUN §8.1)。"""

from __future__ import annotations

from pydantic import BaseModel


class ErrorDetail(BaseModel):
    field: str
    issue: str


class ErrorBody(BaseModel):
    code: str
    message: str
    details: list[ErrorDetail] | None = None


class ErrorEnvelope(BaseModel):
    error: ErrorBody
