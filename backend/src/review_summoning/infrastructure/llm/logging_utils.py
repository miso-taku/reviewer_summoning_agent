"""原稿本文をログに出さないユーティリティ (TEC §8.3 / REQ-NF-022)。"""

from __future__ import annotations

MANUSCRIPT_MASK = "[原稿本文はログに出力しません]"


def mask_manuscript(text: str | None, *, allow_plaintext: bool = False) -> str:
    """デバッグ許可時のみ平文。それ以外はマスク。"""
    if allow_plaintext or not text:
        return text or ""
    return MANUSCRIPT_MASK


def mask_if_present(message: str, manuscript_text: str | None, *, allow_plaintext: bool = False) -> str:
    if allow_plaintext or not manuscript_text or manuscript_text not in message:
        return message
    return message.replace(manuscript_text, MANUSCRIPT_MASK)
