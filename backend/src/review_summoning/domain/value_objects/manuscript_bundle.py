"""原稿 3 ブロック束ね VO (FUN §5.1 IN-DRAFT/MEMO/SLIDES、合計サイズ)。"""

from __future__ import annotations

from dataclasses import dataclass

from review_summoning.domain.exceptions import InvalidDomainInput
from review_summoning.domain.value_objects.theme import Theme

MANUSCRIPT_BLOCK_MAX_CHARS = 100_000
TOTAL_INPUT_MAX_CHARS = 200_000


@dataclass(frozen=True, slots=True)
class ManuscriptBundle:
    """トリム済み `draft_body` / `structure_memo` / `slides_summary`。

    少なくとも 1 ブロックが非空。各ブロックは最大 MANUSCRIPT_BLOCK_MAX_CHARS。
    `theme.scalar_length` と 3 ブロックの合計が TOTAL_INPUT_MAX_CHARS を超えないこと。
    """

    draft_body: str
    structure_memo: str
    slides_summary: str

    @classmethod
    def parse(
        cls,
        draft_body: str,
        structure_memo: str,
        slides_summary: str,
        *,
        theme: Theme,
    ) -> ManuscriptBundle:
        d = draft_body.strip()
        m = structure_memo.strip()
        s = slides_summary.strip()
        for label, part in (
            ("draft_body", d),
            ("structure_memo", m),
            ("slides_summary", s),
        ):
            if len(part) > MANUSCRIPT_BLOCK_MAX_CHARS:
                raise InvalidDomainInput(
                    f"{label} は {MANUSCRIPT_BLOCK_MAX_CHARS} 文字以下である必要があります。"
                )
        if not (d or m or s):
            raise InvalidDomainInput(
                "draft_body / structure_memo / slides_summary のうち、"
                "少なくとも 1 つは前後空白トリム後に非空である必要があります。"
            )
        total = theme.scalar_length + len(d) + len(m) + len(s)
        if total > TOTAL_INPUT_MAX_CHARS:
            raise InvalidDomainInput(
                f"テーマと原稿ブロックの合計が {TOTAL_INPUT_MAX_CHARS} 文字を超えています。"
            )
        return cls(draft_body=d, structure_memo=m, slides_summary=s)
