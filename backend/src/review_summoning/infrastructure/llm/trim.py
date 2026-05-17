"""LLM 受信後の配列トリム (TEC §5.2)。"""

from __future__ import annotations

import logging
from typing import TypeVar

from review_summoning.infrastructure.llm.constants import MAX_PRIORITY_FIXES, MAX_REVIEW_ARRAY_ITEMS

T = TypeVar("T")

logger = logging.getLogger(__name__)


def trim_string_list(
    items: list[str],
    *,
    max_items: int = MAX_REVIEW_ARRAY_ITEMS,
    label: str = "items",
) -> tuple[str, ...]:
    """配列を上限まで切り詰め、超過時は警告ログを出す。"""
    if len(items) <= max_items:
        return tuple(items)
    logger.warning("%s が上限 %d を超過したため切り詰めます (受信 %d 件)", label, max_items, len(items))
    return tuple(items[:max_items])


def trim_priority_fixes(items: list[T], *, max_items: int = MAX_PRIORITY_FIXES) -> list[T]:
    if len(items) <= max_items:
        return items
    logger.warning(
        "priority_fixes が上限 %d を超過したため切り詰めます (受信 %d 件)",
        max_items,
        len(items),
    )
    return items[:max_items]
