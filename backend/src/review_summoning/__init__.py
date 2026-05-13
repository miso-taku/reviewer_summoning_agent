"""review_summoning パッケージ。

レイヤ構成（依存方向は domain ← application ← presentation / infrastructure）:
    - domain: 値オブジェクト・集約・ポート（外部 I/O なし）
    - application: ユースケース・マッパー（domain のみに依存）
    - infrastructure: PydanticAI 等の外部アダプタ・設定
    - presentation: FastAPI ルータ・DTO
"""

__version__ = "0.1.0"
