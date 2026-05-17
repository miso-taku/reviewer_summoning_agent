"""配列トリム (TEC §5.2)。"""

from __future__ import annotations

from review_summoning.infrastructure.llm.trim import trim_priority_fixes, trim_string_list


def test_trim_string_list_within_limit() -> None:
    assert trim_string_list(["a", "b"]) == ("a", "b")


def test_trim_string_list_truncates() -> None:
    items = [str(i) for i in range(60)]
    trimmed = trim_string_list(items, max_items=50)
    assert len(trimmed) == 50
    assert trimmed[0] == "0"
    assert trimmed[-1] == "49"


def test_trim_priority_fixes_truncates() -> None:
    raw = list(range(25))
    assert len(trim_priority_fixes(raw, max_items=20)) == 20
