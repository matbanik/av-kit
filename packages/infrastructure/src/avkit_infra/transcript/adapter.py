"""TranscriptPort adapter backed by youtube-transcript-api >= 1.0."""

from __future__ import annotations

import structlog
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    IpBlocked,
    NoTranscriptFound,
    RequestBlocked,
    TranscriptsDisabled,
    VideoUnavailable,
)

from avkit_core.domain.errors import DomainError, TranscriptRetryableError, ValidationError
from avkit_core.domain.transcript import TranscriptResult

log = structlog.get_logger(module="transcript")

NONE_ERRORS = (TranscriptsDisabled, VideoUnavailable)
RETRYABLE_ERRORS = (RequestBlocked, IpBlocked)


def _snippet_text(item: object) -> str:
    if isinstance(item, dict):
        text = item.get("text")
        return text if isinstance(text, str) else ""
    text = getattr(item, "text", "")
    return text if isinstance(text, str) else ""


def _to_result(video_id: str, fetched: object) -> TranscriptResult:
    snippets = getattr(fetched, "snippets", None)
    if snippets is None and isinstance(fetched, list):
        snippets = fetched
    if snippets is None:
        snippets = []
    text = "\n".join(_snippet_text(item) for item in snippets)
    language = getattr(fetched, "language_code", None) or getattr(fetched, "language", None)
    if not isinstance(language, str) or language == "":
        raise ValidationError("fetched transcript language is required")
    title = getattr(fetched, "title", None)
    if not isinstance(title, str) or title == "":
        title = video_id
    return TranscriptResult(video_id=video_id, title=title, text=text, language=language)


class TranscriptAdapter:
    """Instance-API transcript fetch. Returns None for disabled/missing captions."""

    def get_transcript(self, video_id: str, languages: list[str]) -> TranscriptResult | None:
        if not isinstance(video_id, str) or video_id == "":
            raise ValidationError("video_id must be a non-empty str")
        if not isinstance(languages, list) or not all(isinstance(item, str) for item in languages):
            raise ValidationError("languages must be a list of str")
        ordered: list[str] = []
        for language in languages:
            if language not in ordered:
                ordered.append(language)
        if "en" not in ordered:
            ordered.append("en")
        api = YouTubeTranscriptApi()
        try:
            for language in ordered:
                try:
                    fetched = api.fetch(video_id, languages=[language])
                    return _to_result(video_id, fetched)
                except NoTranscriptFound:
                    continue
                except NONE_ERRORS:
                    return None
            listed = api.list(video_id)
            for transcript in listed:
                fetched = transcript.fetch()
                return _to_result(video_id, fetched)
            return None
        except RETRYABLE_ERRORS as exc:
            raise TranscriptRetryableError(str(exc) or "transcript request blocked") from exc
        except NONE_ERRORS:
            return None
        except NoTranscriptFound:
            return None
        except TranscriptRetryableError:
            raise
        except DomainError:
            raise
        except Exception as exc:
            raise DomainError(str(exc) or "transcript fetch failed") from exc
