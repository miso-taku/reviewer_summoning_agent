"""原稿マスク (REQ-NF-022)。"""

from __future__ import annotations

from review_summoning.infrastructure.llm.logging_utils import MANUSCRIPT_MASK, mask_if_present, mask_manuscript


def test_mask_manuscript_default() -> None:
    assert mask_manuscript("secret draft") == MANUSCRIPT_MASK


def test_mask_manuscript_debug_allowed() -> None:
    assert mask_manuscript("secret draft", allow_plaintext=True) == "secret draft"


def test_mask_if_present_in_message() -> None:
    text = "hello secret world"
    assert "secret" not in mask_if_present(text, "secret")
