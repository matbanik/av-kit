"""TTS prepare, generate, voices, and job routes. Static paths first."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

from fastapi import APIRouter, Depends, Response

from avkit_api.auth import require_bearer
from avkit_api.dependencies import get_tts_service
from avkit_api.formatters import format_iso
from avkit_api.schemas.tts import (
    TTSGenerateIn,
    TTSJobOut,
    TTSPrepareIn,
    TTSPrepareOut,
    VoiceListOut,
    VoiceOut,
)
from avkit_core.domain.enums import MediaFormat, TTSSourceKind

router = APIRouter(prefix="/tts", dependencies=[Depends(require_bearer)])

# `VoiceUnavailableReason` value to its `VOICE_REASON` wire literal (MEU-74).
_REASON_WIRES: dict[str, Literal["espeak_missing", "language_unsupported"]] = {
    "espeak_missing": "espeak_missing",
    "language_unsupported": "language_unsupported",
}


def _job_out(job: Any) -> TTSJobOut:
    source_path = None if job.source_path is None else str(job.source_path)
    output_path = None if job.output_path is None else str(job.output_path)
    return TTSJobOut(
        id=job.id,
        source_kind=job.source_kind.value,
        source_path=source_path,
        text_hash=job.text_hash,
        text_preview=job.text_preview,
        voice=job.voice,
        speed=job.speed,
        format=job.format.value,
        status=job.status.value,
        output_path=output_path,
        segments_total=job.segments_total,
        segments_done=job.segments_done,
        error_message=job.error_message,
        created_at=format_iso(job.created_at),
    )


@router.post("/prepare", response_model=TTSPrepareOut)
def prepare_tts(body: TTSPrepareIn, tts: Any = Depends(get_tts_service)) -> TTSPrepareOut:
    """Run prepare steps. Unknown step → 422 from the service."""
    cleaned = tts.prepare(body.text, body.enabled_steps, body.chunk_max_chars)
    return TTSPrepareOut(cleaned_text=cleaned)


@router.post(
    "/generate",
    status_code=201,
    response_model=TTSJobOut,
    responses={
        409: {
            "description": "Conflict: no model loaded, a run in progress, or a TTS asset missing",
        },
    },
)
def generate_tts(body: TTSGenerateIn, tts: Any = Depends(get_tts_service)) -> TTSJobOut:
    """Start a generation in the background and return the job at once (`Generating`).

    Poll `GET /tts/{id}` until `Done`, `Failed` or `Cancelled`. Does not open `source_path`.
    """
    source_kind = TTSSourceKind.File if body.source_kind == "file" else TTSSourceKind.Inline
    source_path = None if body.source_path is None else Path(body.source_path)
    job = tts.generate(
        body.text,
        body.voice,
        body.speed,
        MediaFormat[body.format],
        body.enabled_steps,
        source_kind,
        source_path,
    )
    return _job_out(job)


@router.get("/voices", response_model=VoiceListOut)
def list_voices(tts: Any = Depends(get_tts_service)) -> VoiceListOut:
    """Public `TTSService.list_voices` facade: each voice with its availability (D-89)."""
    items = [
        VoiceOut(
            voice_id=voice.voice_id,
            language=voice.language,
            gender=voice.gender,
            style_description=voice.style_description,
            available=availability.available,
            reason=None
            if availability.reason is None
            else _REASON_WIRES[str(availability.reason.value)],
        )
        for voice, availability in tts.list_voices()
    ]
    return VoiceListOut(items=items)


@router.get("/{id}", response_model=TTSJobOut)
def get_tts(id: str, tts: Any = Depends(get_tts_service)) -> TTSJobOut:
    """Poll one TTS job."""
    return _job_out(tts.get_status(id))


@router.delete("/{id}", status_code=204)
def cancel_tts(id: str, tts: Any = Depends(get_tts_service)) -> Response:
    """Cancel the running TTS job; it ends `Cancelled` with no output file. Always 204."""
    tts.cancel(id)
    return Response(status_code=204)
