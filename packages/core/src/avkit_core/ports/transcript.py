"""Transcript fetch port protocol."""

from __future__ import annotations

from typing import Protocol

from avkit_core.domain.transcript import TranscriptResult, TranscriptSkip


class TranscriptPort(Protocol):
    """Caption fetch. A video with no transcript returns a TranscriptSkip carrying its cause."""

    def get_transcript(
        self, video_id: str, languages: list[str]
    ) -> TranscriptResult | TranscriptSkip: ...
