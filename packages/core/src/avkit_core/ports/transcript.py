"""Transcript fetch port protocol."""

from __future__ import annotations

from typing import Protocol

from avkit_core.domain.transcript import TranscriptResult


class TranscriptPort(Protocol):
    """Caption fetch. None means no transcript (item Skipped)."""

    def get_transcript(self, video_id: str, languages: list[str]) -> TranscriptResult | None: ...
