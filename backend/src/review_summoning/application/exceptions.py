"""アプリケーション層例外 (presentation で HTTP / error.code に写像) (TEC §7.3)。"""


class ApplicationError(Exception):
    """アプリケーション層の例外の基底。"""


class ApplicationPipelineTimeoutError(ApplicationError):
    """パイプライン全体の wait_for バジェット超過 (504 REQUEST_TIMEOUT へ)。"""


class ApplicationLlmUpstreamError(ApplicationError):
    """LLM プロバイダ 4xx/5xx・パース不能 (502 LLM_UPSTREAM_ERROR へ)。"""


class ApplicationLlmUnavailableError(ApplicationError):
    """接続エラー・DNS 等 (503 LLM_UNAVAILABLE へ)。"""
