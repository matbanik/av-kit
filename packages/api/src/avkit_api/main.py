"""FastAPI application factory, middleware, and lifespan."""

from __future__ import annotations

from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager
from uuid import uuid4

import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from avkit_api import __version__
from avkit_api.errors import (
    REQUEST_ID_HEADER,
    internal_error_response,
    log_unhandled_error,
    register_exception_handlers,
)
from avkit_api.routes.captures import router as captures_router
from avkit_api.routes.conversions import router as conversions_router
from avkit_api.routes.downloads import router as downloads_router
from avkit_api.routes.health import router as health_router
from avkit_api.routes.models import router as models_router
from avkit_api.routes.settings import router as settings_router
from avkit_api.routes.transcripts import router as transcripts_router
from avkit_api.routes.tts import router as tts_router
from avkit_api.wiring import AppServices, build_services

API_PREFIX = "/api/v1"
log = structlog.get_logger(module="api")
CORS_ORIGIN_REGEX = r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$"


def _validate_tokens(tokens: frozenset[str]) -> None:
    if not tokens:
        raise ValueError("tokens must be a non-empty frozenset")
    for token in tokens:
        if not isinstance(token, str) or token.strip() == "":
            raise ValueError("tokens must not contain blank members")


@asynccontextmanager
async def _lifespan(app: FastAPI) -> AsyncIterator[None]:
    services: AppServices = app.state.services
    services.transcript.recover_stale_processing()
    services.tts.recover_stale_processing()
    try:
        yield
    finally:
        services.download.cancel_processing()
        services.conversion.cancel_processing()
        services.transcript.stop_processing()
        idle = services.tts.stop_processing()
        if idle:
            services.models.unload()
            dispose = app.state.engine_dispose
            if dispose is not None:
                dispose()
        else:
            # A TTS worker is still synthesizing: keep its model and database.
            log.warning("api.shutdown_tts_busy")


def create_app(
    *,
    tokens: frozenset[str],
    services: AppServices | None = None,
    engine_dispose: Callable[[], None] | None = None,
) -> FastAPI:
    """Build the `/api/v1` application. Does not bind uvicorn."""
    _validate_tokens(tokens)
    dispose = engine_dispose
    if services is None:
        services, built_dispose = build_services()
        if dispose is None:
            dispose = built_dispose
    bound = services
    app = FastAPI(title="av-kit", version=__version__, lifespan=_lifespan)
    app.state.tokens = tokens
    app.state.services = bound
    app.state.engine_dispose = dispose

    @app.middleware("http")
    async def request_id_middleware(request: Request, call_next: Callable) -> object:
        incoming = request.headers.get(REQUEST_ID_HEADER)
        request_id = incoming if incoming else str(uuid4())
        request.state.request_id = request_id
        structlog.contextvars.bind_contextvars(request_id=request_id)
        try:
            response = await call_next(request)
        except Exception as exc:
            # CORS_SAFE_500: answered here, inside CORSMiddleware, so the 500 carries CORS.
            log_unhandled_error(request, exc)
            response = internal_error_response(request_id)
        finally:
            structlog.contextvars.unbind_contextvars("request_id")
        response.headers[REQUEST_ID_HEADER] = request_id
        return response

    app.add_middleware(
        CORSMiddleware,
        allow_origin_regex=CORS_ORIGIN_REGEX,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["Authorization", "Content-Type", REQUEST_ID_HEADER],
    )
    register_exception_handlers(app)
    app.include_router(health_router, prefix=API_PREFIX)
    app.include_router(downloads_router, prefix=API_PREFIX)
    app.include_router(conversions_router, prefix=API_PREFIX)
    app.include_router(captures_router, prefix=API_PREFIX)
    app.include_router(settings_router, prefix=API_PREFIX)
    app.include_router(transcripts_router, prefix=API_PREFIX)
    app.include_router(tts_router, prefix=API_PREFIX)
    app.include_router(models_router, prefix=API_PREFIX)
    return app
