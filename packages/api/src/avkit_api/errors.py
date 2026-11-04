"""ErrorEnvelope handlers and domain-to-HTTP mapping."""

from __future__ import annotations

import structlog
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from avkit_core.domain.errors import (
    AgeRestrictedError,
    AnnotationValidationError,
    CaptureFailedError,
    CaptureNotSupportedError,
    ConflictError,
    CookieTestError,
    DomainError,
    ExtractError,
    FFmpegNotFoundError,
    InboxPathError,
    InvalidTimeRangeError,
    ModelLoadError,
    NotFoundError,
    SpacyModelNotFoundError,
    ValidationError,
)

DOMAIN_HTTP_MAP: dict[type[DomainError], int] = {
    ValidationError: 422,
    InvalidTimeRangeError: 422,
    CookieTestError: 422,
    AgeRestrictedError: 422,
    InboxPathError: 422,
    AnnotationValidationError: 422,
    ExtractError: 422,
    ModelLoadError: 422,
    NotFoundError: 404,
    ConflictError: 409,
    FFmpegNotFoundError: 503,
    SpacyModelNotFoundError: 503,
    CaptureFailedError: 503,
    CaptureNotSupportedError: 503,
}


def _envelope(code: str, message: str, details: dict[str, object] | None) -> dict[str, object]:
    return {"error": {"code": code, "message": message, "details": details}}


REQUEST_ID_HEADER = "X-Request-ID"

log = structlog.get_logger(module="api")


def _request_id(request: Request) -> str | None:
    return getattr(request.state, "request_id", None)


def _route(request: Request) -> str:
    """The matched route path template, else the raw URL path.

    An included router's route carries its template relative to the include prefix,
    so the prefix is the part of the URL path before the suffix the route matches.
    """
    path = request.url.path
    route = request.scope.get("route")
    template = getattr(route, "path_format", None)
    regex = getattr(route, "path_regex", None)
    if not isinstance(template, str) or regex is None:
        return path
    for start, char in enumerate(path):
        if char == "/" and regex.match(path[start:]):
            return path[:start] + template
    return path


def log_unhandled_error(request: Request, exc: BaseException) -> None:
    """ERROR_EVENT: one `api.unhandled_error` per failing request. Call inside `except`."""
    text = str(exc)
    name = type(exc).__name__
    log.error(
        "api.unhandled_error",
        request_id=_request_id(request),
        route=_route(request),
        method=request.method,
        error=f"{name}: {text}" if text else name,
        exc_info=True,
    )


def internal_error_response(request_id: str | None) -> JSONResponse:
    """The masked 500: no exception text, the request id in details and the header."""
    details: dict[str, object] | None = (
        {"request_id": request_id} if request_id is not None else None
    )
    headers = {REQUEST_ID_HEADER: request_id} if request_id is not None else None
    return JSONResponse(
        status_code=500,
        content=_envelope("internal_error", "Internal server error", details),
        headers=headers,
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Install ErrorEnvelope handlers on `app`."""

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        if exc.status_code == 401:
            code = "unauthorized"
            message = "Missing or invalid bearer token"
        else:
            code = "http_error"
            message = str(exc.detail)
        return JSONResponse(
            status_code=exc.status_code,
            content=_envelope(code, message, None),
            headers=dict(exc.headers or {}),
        )

    @app.exception_handler(RequestValidationError)
    async def request_validation_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        del request, exc
        return JSONResponse(
            status_code=422,
            content=_envelope("validation_error", "Request validation failed", None),
        )

    @app.exception_handler(DomainError)
    async def domain_error_handler(request: Request, exc: DomainError) -> JSONResponse:
        status = 500
        for error_type, mapped in DOMAIN_HTTP_MAP.items():
            if isinstance(exc, error_type):
                status = mapped
                break
        if status >= 500:
            request_id = _request_id(request)
            if status == 500:
                # ERROR_EVENT for an unmapped DomainError; a mapped 503 is not logged.
                log_unhandled_error(request, exc)
            details: dict[str, object] | None = (
                {"request_id": request_id} if request_id is not None else None
            )
            return JSONResponse(
                status_code=status,
                content=_envelope("internal_error", "Internal server error", details),
            )
        return JSONResponse(
            status_code=status,
            content=_envelope(type(exc).__name__, str(exc), None),
        )

    @app.exception_handler(Exception)
    async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
        # Backstop: request_id_middleware catches route exceptions, so this runs only
        # for one that never passed through it, and that one is logged here.
        log_unhandled_error(request, exc)
        return internal_error_response(_request_id(request))
