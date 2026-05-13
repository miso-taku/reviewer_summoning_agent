"""ドメイン例外 (入力検証 vs 不変条件 vs 想定外)。

presentation 層で HTTP + error.code に写像する (FUN §8 / TEC §7.3)。
"""


class DomainError(Exception):
    """ドメイン層の例外の基底。"""


class InvalidDomainInput(DomainError):
    """ユーザー入力・意味的制約違反 (主に 422 VALIDATION_ERROR へ)。"""


class DomainInvariantViolation(DomainError):
    """集約の不変条件違反 (並列レビュー順序・編集長前提など)。"""


class UnexpectedDomainState(DomainError):
    """想定外の内部状態 (バグ相当。主に 500 INTERNAL_ERROR へ)。"""
