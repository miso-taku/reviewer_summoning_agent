"""テーマ VO (FUN §5.1 IN-THEME、TEC §4.4.2)。"""

from __future__ import annotations

from dataclasses import dataclass

from review_summoning.domain.exceptions import InvalidDomainInput

THEME_MAX_CHARS = 2000


@dataclass(frozen=True, slots=True)
class Theme:
    """前後空白トリム済み。1〜2000 Unicode スカラ (Python str のコードポイント長)。"""

    value: str

    @property
    def scalar_length(self) -> int:
        return len(self.value)

    @classmethod
    def parse(cls, raw: str) -> Theme:
        value = raw.strip()
        n = len(value)
        if n == 0:
            raise InvalidDomainInput("テーマは前後空白を除き 1 文字以上必要です。")
        if n > THEME_MAX_CHARS:
            raise InvalidDomainInput(
                f"テーマは {THEME_MAX_CHARS} 文字以下である必要があります (Unicode スカラ単位)。"
            )
        return cls(value)
