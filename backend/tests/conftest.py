"""pytest 共通フィクスチャ置き場（フェーズ 1 以降で実装）。

- LLM 実呼び出しの除外は pyproject.toml の addopts (`-m "not llm_live"`) で既定化済み。
- フェーズ 2 以降でフェイクポート、フェーズ 3 以降で TestClient のフィクスチャを追加する。
"""
