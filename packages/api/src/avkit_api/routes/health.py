"""Health liveness and dependency routes."""

from __future__ import annotations

from typing import Any, Literal

from fastapi import APIRouter, Depends, Response

from avkit_api.auth import require_bearer
from avkit_api.dependencies import get_health_service
from avkit_api.formatters import format_iso
from avkit_api.schemas.health import (
    ConsoleEventOut,
    ConsoleSnapshotOut,
    DependenciesOut,
    EspeakOut,
    FfmpegDependencyOut,
    JsRuntimeOut,
    LivenessOut,
    StartupMetricIn,
    TtsAssetOut,
    VersionAvailabilityOut,
)

router = APIRouter()


@router.get("/health", response_model=LivenessOut)
def health_liveness(health: Any = Depends(get_health_service)) -> LivenessOut:
    """Unauthenticated process-up probe."""
    live = health.liveness()
    if not live.ok:
        raise RuntimeError("health liveness is not ok")
    return LivenessOut(status="ok")


@router.get(
    "/health/dependencies",
    response_model=DependenciesOut,
    dependencies=[Depends(require_bearer)],
)
def health_dependencies(health: Any = Depends(get_health_service)) -> DependenciesOut:
    """Authenticated binary version probe."""
    deps = health.dependencies()
    ffmpeg_version = deps.ffmpeg_version
    ytdlp_version = deps.ytdlp_version
    return DependenciesOut(
        yt_dlp=VersionAvailabilityOut(version=ytdlp_version, available=ytdlp_version is not None),
        ffmpeg=FfmpegDependencyOut(
            version=ffmpeg_version,
            available=ffmpeg_version is not None,
            path=deps.ffmpeg_path,
            ffprobe_available=deps.ffprobe_available,
        ),
        tts_onnx_vocab=_asset_out(deps.tts_onnx_vocab, None),
        tts_spacy_model=_asset_out(deps.tts_spacy_model, deps.tts_spacy_version),
        tts_voice_packs=_asset_out(deps.tts_voice_packs, None),
        tts_espeak=_espeak_out(deps.tts_espeak),
        js_runtime=_js_runtime_out(deps.js_runtime),
    )


def _espeak_out(status: Any) -> EspeakOut:
    """Serialize `EspeakStatus`; `path` is the resolved executable as a native path string."""
    return EspeakOut(
        available=bool(status.available),
        version=status.version,
        path=None if status.path is None else str(status.path),
    )


_RUNTIME_SOURCES: dict[str, Literal["setting", "bundled", "path"]] = {
    "setting": "setting",
    "bundled": "bundled",
    "path": "path",
}


def _js_runtime_out(status: Any) -> JsRuntimeOut:
    """Serialize `JsRuntimeStatus` (`RUNTIME_WIRE`); an unknown source reads as None."""
    return JsRuntimeOut(
        available=bool(status.available),
        name=status.name,
        path=None if status.path is None else str(status.path),
        version=status.version,
        source=_RUNTIME_SOURCES.get(str(status.source)),
        solver=bool(status.solver),
    )


_ASSET_WIRES: dict[str, Literal["ready", "missing", "downloading"]] = {
    "ready": "ready",
    "missing": "missing",
    "downloading": "downloading",
}


def _asset_out(state: Any, version: str | None) -> TtsAssetOut:
    """Serialize one `AssetState`; an unknown state fails closed (KeyError → 500)."""
    wire = _ASSET_WIRES[str(state.value)]
    return TtsAssetOut(
        version=version if wire == "ready" else None,
        available=wire == "ready",
        state=wire,
    )


@router.get(
    "/health/console",
    response_model=ConsoleSnapshotOut,
    dependencies=[Depends(require_bearer)],
)
def health_console(
    after_seq: int = 0,
    health: Any = Depends(get_health_service),
) -> ConsoleSnapshotOut:
    """Return console events after `after_seq`. Not SSE."""
    events = health.console_snapshot(after_seq)
    items = [
        ConsoleEventOut(
            seq=event.seq,
            ts=format_iso(event.timestamp),
            level=event.level,
            module=event.module,
            message=event.message,
        )
        for event in events
    ]
    last_seq = max((item.seq for item in items), default=after_seq)
    return ConsoleSnapshotOut(items=items, last_seq=last_seq)


@router.post(
    "/health/startup-metrics",
    status_code=204,
    dependencies=[Depends(require_bearer)],
)
def health_startup_metrics(
    body: StartupMetricIn,
    health: Any = Depends(get_health_service),
) -> Response:
    """Record a startup metric. Log only."""
    health.record_startup_metric(body.key, body.value_ms)
    return Response(status_code=204)
