"""Settings namespace request schemas."""

from __future__ import annotations

from pydantic import Field, StrictBool

from avkit_api.schemas.common import ApiModel

TTS_INPUT_TEXT_MAX = 1_000_000


class SettingsPutIn(ApiModel):
    """Partial leaf mapping for any settings namespace. Extra fields are forbidden."""

    path: str | None = None
    ffmpeg_path: str | None = None
    quality: str | None = None
    audio_only: bool | None = None
    audio_format: str | None = None
    cookie_mode: str | None = None
    cookie_browser: str | None = None
    cookie_browser_profile: str | None = None
    cookie_file_path: str | None = None
    archive_tracking: bool | None = None
    yt_dlp_debug: bool | None = None
    output_dir: str | None = None
    default_preset: str | None = None
    skip_existing: bool | None = None
    gpu_preference: str | None = None
    requests_per_hour: float | None = None
    delay_between_requests: float | None = None
    max_retries: float | None = None
    retry_delay: float | None = None
    batch_size: float | None = None
    pause_between_batches: float | None = None
    playlist_end: float | None = None
    max_words_per_document: float | None = None
    models_directory: str | None = None
    voice: str | None = None
    speed: float | None = None
    output_format: str | None = None
    output_path: str | None = None
    device: str | None = None
    chunk_max_chars: float | None = None
    input_text: str | None = Field(default=None, max_length=TTS_INPUT_TEXT_MAX)
    log_level: str | None = None
    log_to_file: bool | None = None
    console_visible: bool | None = None
    theme: str | None = None
    inbox_dir: str | None = None
    hotkey: str | None = None
    copy_to_clipboard: bool | None = None
    close_to_tray: bool | None = None
    # StrictBool: AC-67.11 requires "yes" -> 422, not lax coercion to True.
    flatten_backup: StrictBool | None = None
    backup_dir: str | None = None
    annotated_format: str | None = None
