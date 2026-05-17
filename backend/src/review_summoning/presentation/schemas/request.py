"""リクエスト DTO — Pydantic 第 1 段バリデーション (FUN §5.1 / TEC §5.3)。"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator

from review_summoning.domain.value_objects.manuscript_bundle import (
    MANUSCRIPT_BLOCK_MAX_CHARS,
    TOTAL_INPUT_MAX_CHARS,
)
from review_summoning.domain.value_objects.theme import THEME_MAX_CHARS


def _normalize_optional_block(value: str | None) -> str:
    if value is None:
        return ""
    return value.strip()


class ReviewRequestBody(BaseModel):
    theme: str = Field(..., description="テーマ (IN-THEME)")
    draft_body: str | None = None
    structure_memo: str | None = None
    slides_summary: str | None = None

    @field_validator("theme", mode="before")
    @classmethod
    def strip_theme(cls, value: Any) -> str:
        if not isinstance(value, str):
            return value
        return value.strip()

    @field_validator("draft_body", "structure_memo", "slides_summary", mode="before")
    @classmethod
    def normalize_blocks(cls, value: Any) -> str | None:
        if value is None:
            return None
        if not isinstance(value, str):
            return value
        return value.strip()

    @model_validator(mode="after")
    def validate_ranges_and_combination(self) -> ReviewRequestBody:
        if len(self.theme) == 0:
            raise ValueError("テーマは前後空白を除き 1 文字以上必要です。")
        if len(self.theme) > THEME_MAX_CHARS:
            raise ValueError(
                f"テーマは {THEME_MAX_CHARS} 文字以下である必要があります (Unicode スカラ単位)。"
            )

        d = _normalize_optional_block(self.draft_body)
        m = _normalize_optional_block(self.structure_memo)
        s = _normalize_optional_block(self.slides_summary)

        for label, part in (
            ("draft_body", d),
            ("structure_memo", m),
            ("slides_summary", s),
        ):
            if len(part) > MANUSCRIPT_BLOCK_MAX_CHARS:
                raise ValueError(
                    f"{label} は {MANUSCRIPT_BLOCK_MAX_CHARS} 文字以下である必要があります。"
                )

        if not (d or m or s):
            raise ValueError(
                "draft_body / structure_memo / slides_summary のうち、"
                "少なくとも 1 つは前後空白トリム後に非空である必要があります。"
            )

        total = len(self.theme) + len(d) + len(m) + len(s)
        if total > TOTAL_INPUT_MAX_CHARS:
            raise ValueError(
                f"テーマと原稿ブロックの合計が {TOTAL_INPUT_MAX_CHARS} 文字を超えています。"
            )

        return self
