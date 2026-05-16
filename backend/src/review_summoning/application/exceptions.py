"""アプリケーション層例外 (presentation で HTTP / error.code に写像) (TEC §7.3)。"""


class ApplicationError(Exception):
    """アプリケーション層の例外の基底。"""


class ApplicationPipelineTimeoutError(ApplicationError):
    """パイプライン全体の wait_for バジェット超過 (504 REQUEST_TIMEOUT へ)。"""
