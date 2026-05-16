"""原稿 VO → LLM 投入用テキスト (TEC §4.4.3 備考: 連結方針は application で決定)。"""
from __future__ import annotations

from review_summoning.domain.value_objects.manuscript_bundle import ManuscriptBundle


def manuscript_bundle_to_llm_text(bundle: ManuscriptBundle) -> str:
    """非空ブロックのみラベル付きで連結する。"""
    sections: list[str] = []
    if bundle.draft_body:
        sections.append(f"【原稿本文】\n{bundle.draft_body}")
    if bundle.structure_memo:
        sections.append(f"【構成メモ】\n{bundle.structure_memo}")
    if bundle.slides_summary:
        sections.append(f"【スライド要約】\n{bundle.slides_summary}")
    return "\n\n".join(sections)
