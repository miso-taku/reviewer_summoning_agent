"""ReviewRequestBody の Pydantic 第 1 段バリデーション (FUN §5.1)。"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from review_summoning.domain.value_objects.manuscript_bundle import (
    MANUSCRIPT_BLOCK_MAX_CHARS,
    TOTAL_INPUT_MAX_CHARS,
)
from review_summoning.domain.value_objects.theme import THEME_MAX_CHARS
from review_summoning.presentation.schemas.request import ReviewRequestBody


def test_accepts_minimal_valid_request() -> None:
    body = ReviewRequestBody(theme="テーマ", draft_body="本文")
    assert body.theme == "テーマ"
    assert body.draft_body == "本文"


def test_trims_theme_and_blocks() -> None:
    body = ReviewRequestBody(
        theme="  テーマ  ",
        draft_body="  本文  ",
        structure_memo="",
        slides_summary=None,
    )
    assert body.theme == "テーマ"
    assert body.draft_body == "本文"


def test_rejects_empty_theme_after_trim() -> None:
    with pytest.raises(ValidationError):
        ReviewRequestBody(theme="   ", draft_body="x")


def test_rejects_theme_over_max() -> None:
    with pytest.raises(ValidationError):
        ReviewRequestBody(theme="a" * (THEME_MAX_CHARS + 1), draft_body="x")


def test_rejects_all_blocks_empty() -> None:
    with pytest.raises(ValidationError):
        ReviewRequestBody(theme="t", draft_body="", structure_memo="", slides_summary="")


def test_rejects_block_over_max() -> None:
    with pytest.raises(ValidationError):
        ReviewRequestBody(
            theme="t",
            draft_body="x" * (MANUSCRIPT_BLOCK_MAX_CHARS + 1),
        )


def test_rejects_total_input_over_max() -> None:
    theme = "t"
    remaining = TOTAL_INPUT_MAX_CHARS - len(theme) + 1
    with pytest.raises(ValidationError):
        ReviewRequestBody(theme=theme, draft_body="a" * remaining)
