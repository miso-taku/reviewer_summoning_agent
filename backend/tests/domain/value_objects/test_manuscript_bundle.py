"""TC-U-VO-02 / TC-U-VO-03: ManuscriptBundle (FUN §5.1 IN-DRAFT/MEMO/SLIDES + 合計)。"""

import pytest

from review_summoning.domain.exceptions import InvalidDomainInput
from review_summoning.domain.value_objects.manuscript_bundle import (
    MANUSCRIPT_BLOCK_MAX_CHARS,
    TOTAL_INPUT_MAX_CHARS,
    ManuscriptBundle,
)
from review_summoning.domain.value_objects.theme import Theme


def _theme(n: int = 1) -> Theme:
    return Theme.parse("t" * n)


def test_at_least_one_block_non_empty_after_trim() -> None:
    with pytest.raises(InvalidDomainInput):
        ManuscriptBundle.parse("  ", "", "\n", theme=_theme())


def test_each_block_respects_upper_bound() -> None:
    body = "a" * MANUSCRIPT_BLOCK_MAX_CHARS
    with pytest.raises(InvalidDomainInput):
        ManuscriptBundle.parse(body + "x", "", "", theme=_theme())


def test_combined_theme_and_blocks_over_200000_rejected() -> None:
    theme = _theme(2000)
    # 200000 - 2000 = 198000 for three blocks; split 66000 each → OK boundary
    part = "b" * 66000
    ManuscriptBundle.parse(part, part, part, theme=theme)
    # one more char in any block → total 200001
    with pytest.raises(InvalidDomainInput):
        ManuscriptBundle.parse(part + "x", part, part, theme=theme)


def test_total_exactly_200000_ok() -> None:
    theme = Theme.parse("t" * 2000)
    rest = TOTAL_INPUT_MAX_CHARS - theme.scalar_length  # 198000
    a, b, c = rest // 3, rest // 3, rest - 2 * (rest // 3)
    m = ManuscriptBundle.parse("a" * a, "b" * b, "c" * c, theme=theme)
    assert len(m.draft_body) + len(m.structure_memo) + len(m.slides_summary) == rest


def test_trims_blocks() -> None:
    m = ManuscriptBundle.parse("  x  ", "y", " ", theme=_theme())
    assert m.draft_body == "x"
    assert m.structure_memo == "y"
    assert m.slides_summary == ""
