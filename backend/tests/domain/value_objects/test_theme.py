"""TC-U-VO-01: Theme VO (FUN §5.1 IN-THEME)。"""

import pytest

from review_summoning.domain.exceptions import InvalidDomainInput
from review_summoning.domain.value_objects.theme import Theme


def test_theme_trims_whitespace() -> None:
    t = Theme.parse("  hello  ")
    assert t.value == "hello"


def test_theme_rejects_empty_after_trim() -> None:
    with pytest.raises(InvalidDomainInput):
        Theme.parse("   \n\t  ")


def test_theme_accepts_length_1() -> None:
    t = Theme.parse("a")
    assert t.value == "a"
    assert t.scalar_length == 1


def test_theme_accepts_length_2000() -> None:
    s = "あ" * 2000
    t = Theme.parse(s)
    assert t.scalar_length == 2000


def test_theme_rejects_over_2000_unicode_scalars() -> None:
    s = "x" * 2001
    with pytest.raises(InvalidDomainInput):
        Theme.parse(s)


def test_theme_counts_codepoints_not_utf8_bytes() -> None:
    t = Theme.parse("あ")  # 3 bytes in UTF-8, one Unicode scalar
    assert t.scalar_length == 1
