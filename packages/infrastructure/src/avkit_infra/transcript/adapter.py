"""TranscriptPort adapter backed by youtube-transcript-api >= 1.0."""

from __future__ import annotations

import structlog
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    AgeRestricted,
    FailedToCreateConsentCookie,
    InvalidVideoId,
    IpBlocked,
    NoTranscriptFound,
    PoTokenRequired,
    RequestBlocked,
    TranscriptsDisabled,
    VideoUnavailable,
    VideoUnplayable,
    YouTubeDataUnparsable,
    YouTubeRequestFailed,
)

from avkit_core.domain.errors import DomainError, TranscriptRetryableError, ValidationError
from avkit_core.domain.transcript import TranscriptFailureCause, TranscriptResult, TranscriptSkip

log = structlog.get_logger(module="transcript")

NO_CAPTIONS_ERRORS = (TranscriptsDisabled, NoTranscriptFound)
#: In youtube-transcript-api 1.2.4 an HTTP 429 raises IpBlocked, so a rate limit is a block.
RETRYABLE_ERRORS = (RequestBlocked, IpBlocked)
BLOCKED_TEXT = "caption request blocked"

#: The short reason each named library error gives. Any other error gives its class name; the
#: library's own text never crosses the port, because it can hold a URL with a query token.
LIBRARY_REASONS: dict[type[Exception], str] = {
    AgeRestricted: "the video is age-restricted",
    VideoUnplayable: "the video can't be played",
    PoTokenRequired: "YouTube asked for a PO token",
    InvalidVideoId: "the video ID isn't valid",
    YouTubeDataUnparsable: "YouTube's reply couldn't be read",
    YouTubeRequestFailed: "the request to YouTube failed",
    FailedToCreateConsentCookie: "YouTube's consent page couldn't be passed",
}


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
    """Instance-API transcript fetch. A video with no transcript returns a typed skip."""

    def get_transcript(
        self, video_id: str, languages: list[str]
    ) -> TranscriptResult | TranscriptSkip:
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
            listed = api.list(video_id)
            for transcript in listed:
                fetched = transcript.fetch()
                return _to_result(video_id, fetched)
            return TranscriptSkip(TranscriptFailureCause.no_captions)
        except RETRYABLE_ERRORS as exc:
            raise TranscriptRetryableError(BLOCKED_TEXT) from exc
        except NO_CAPTIONS_ERRORS:
            return TranscriptSkip(TranscriptFailureCause.no_captions)
        except VideoUnavailable:
            return TranscriptSkip(TranscriptFailureCause.unavailable)
        except DomainError:
            raise
        except Exception as exc:
            raise DomainError(LIBRARY_REASONS.get(type(exc), type(exc).__name__)) from exc
