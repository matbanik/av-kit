"""FastAPI getters that read frozen services from `app.state`."""

from __future__ import annotations

from starlette.requests import Request


def get_download_service(request: Request) -> object:
    """Return the download service bound on the app."""
    return request.app.state.services.download


def get_conversion_service(request: Request) -> object:
    """Return the conversion service bound on the app."""
    return request.app.state.services.conversion


def get_transcript_service(request: Request) -> object:
    """Return the transcript service bound on the app."""
    return request.app.state.services.transcript


def get_tts_service(request: Request) -> object:
    """Return the TTS service bound on the app."""
    return request.app.state.services.tts


def get_model_service(request: Request) -> object:
    """Return the model service bound on the app."""
    return request.app.state.services.models


def get_settings_service(request: Request) -> object:
    """Return the settings service bound on the app."""
    return request.app.state.services.settings


def get_health_service(request: Request) -> object:
    """Return the health service bound on the app."""
    return request.app.state.services.health


def get_capture_service(request: Request) -> object:
    """Return the capture service bound on the app."""
    return request.app.state.services.capture
