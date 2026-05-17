"""ドメイン/アプリケーション例外 -> HTTP + error.code (FUN §8 / TEC §7.3)。"""

from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from review_summoning.application.exceptions import (
    ApplicationError,
    ApplicationLlmUnavailableError,
    ApplicationLlmUpstreamError,
    ApplicationPipelineTimeoutError,
)
from review_summoning.domain.exceptions import (
    DomainError,
    DomainInvariantViolation,
    InvalidDomainInput,
    UnexpectedDomainState,
)
from review_summoning.presentation.schemas.error import ErrorBody, ErrorDetail, ErrorEnvelope

logger = logging.getLogger(__name__)


def _error_response(
    status_code: int,
    *,
    code: str,
    message: str,
    details: list[ErrorDetail] | None = None,
) -> JSONResponse:
    body = ErrorEnvelope(
        error=ErrorBody(code=code, message=message, details=details),
    )
    return JSONResponse(status_code=status_code, content=body.model_dump(exclude_none=True))


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(InvalidDomainInput)
    async def invalid_domain_input_handler(
        _request: Request,
        exc: InvalidDomainInput,
    ) -> JSONResponse:
        return _error_response(
            422,
            code="VALIDATION_ERROR",
            message=str(exc),
        )

    @app.exception_handler(RequestValidationError)
    async def request_validation_handler(
        _request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        details: list[ErrorDetail] = []
        for err in exc.errors():
            loc = err.get("loc", ())
            field = ".".join(str(part) for part in loc if part != "body")
            issue = err.get("type", "invalid")
            msg = err.get("msg", "")
            if msg:
                issue = msg
            details.append(ErrorDetail(field=field or "body", issue=issue))
        message = "入力内容に誤りがあります。"
        if details:
            message = details[0].issue
        return _error_response(
            422,
            code="VALIDATION_ERROR",
            message=message,
            details=details or None,
        )

    @app.exception_handler(ApplicationPipelineTimeoutError)
    async def pipeline_timeout_handler(
        _request: Request,
        exc: ApplicationPipelineTimeoutError,
    ) -> JSONResponse:
        return _error_response(
            504,
            code="REQUEST_TIMEOUT",
            message=str(exc),
        )

    @app.exception_handler(ApplicationLlmUpstreamError)
    async def llm_upstream_handler(
        _request: Request,
        exc: ApplicationLlmUpstreamError,
    ) -> JSONResponse:
        return _error_response(
            502,
            code="LLM_UPSTREAM_ERROR",
            message=str(exc),
        )

    @app.exception_handler(ApplicationLlmUnavailableError)
    async def llm_unavailable_handler(
        _request: Request,
        exc: ApplicationLlmUnavailableError,
    ) -> JSONResponse:
        return _error_response(
            503,
            code="LLM_UNAVAILABLE",
            message=str(exc),
        )

    @app.exception_handler(DomainInvariantViolation)
    async def domain_invariant_handler(
        _request: Request,
        exc: DomainInvariantViolation,
    ) -> JSONResponse:
        logger.exception("Domain invariant violation", exc_info=exc)
        return _error_response(
            500,
            code="INTERNAL_ERROR",
            message="内部エラーが発生しました。",
        )

    @app.exception_handler(UnexpectedDomainState)
    async def unexpected_domain_state_handler(
        _request: Request,
        exc: UnexpectedDomainState,
    ) -> JSONResponse:
        logger.exception("Unexpected domain state", exc_info=exc)
        return _error_response(
            500,
            code="INTERNAL_ERROR",
            message="内部エラーが発生しました。",
        )

    @app.exception_handler(DomainError)
    async def domain_error_handler(_request: Request, exc: DomainError) -> JSONResponse:
        logger.exception("Unhandled domain error", exc_info=exc)
        return _error_response(
            500,
            code="INTERNAL_ERROR",
            message="内部エラーが発生しました。",
        )

    @app.exception_handler(ApplicationError)
    async def application_error_handler(
        _request: Request,
        exc: ApplicationError,
    ) -> JSONResponse:
        logger.exception("Unhandled application error", exc_info=exc)
        return _error_response(
            500,
            code="INTERNAL_ERROR",
            message="内部エラーが発生しました。",
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        _request: Request,
        exc: StarletteHTTPException,
    ) -> JSONResponse:
        if exc.status_code == 415:
            return _error_response(
                422,
                code="UNSUPPORTED_MEDIA_TYPE",
                message="Content-Type は application/json で送信してください。",
            )
        return _error_response(
            exc.status_code,
            code="INTERNAL_ERROR",
            message=str(exc.detail),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(_request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled exception", exc_info=exc)
        return _error_response(
            500,
            code="INTERNAL_ERROR",
            message="内部エラーが発生しました。",
        )
