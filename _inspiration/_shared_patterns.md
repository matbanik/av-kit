# Shared Behavioral Patterns

> **Purpose**: Common patterns found across all 3 source apps that should be unified in av-kit.
> These patterns become shared infrastructure components in the new architecture.

---

## 1. Console / Logging Pattern

**Found in**: Downloader, Transcript, TTS (all three)

**Common behavior**:
- Scrolled text widget displaying log output
- Log level filtering (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Thread-safe message passing (background thread → queue → GUI thread displays)
- Clear logs button
- Console visibility toggle (show/hide)

**Differences across apps**:
| Feature | Downloader | Transcript | TTS |
|---------|-----------|-----------|-----|
| yt-dlp debug toggle | ✅ | ❌ | ❌ |
| Color-coded levels | ❌ | ❌ | ❌ |
| Log to file | ❌ | ❌ | ❌ |

**Unified component design**:
- Shared console component with:
  - Level filtering dropdown
  - Color-coded output (green=info, yellow=warning, red=error)
  - Module prefix tags ([Downloader], [Transcript], [TTS])
  - Clear button
  - Toggle visibility
  - Copy to clipboard
  - Log to file option
  - Search/filter within logs
- Backend: structlog with contextvars correlation IDs (per Zorivest pattern)
- Frontend: React component with virtualized scrolling for performance

---

## 2. Background Processing Pattern

**Found in**: Downloader, Transcript, TTS (all three)

**Common behavior**:
- Long operations run on background threads
- GUI thread remains responsive during processing
- Start/Stop controls (all three)
- Pause/Resume (Transcript has this; Downloader and TTS do not but should)
- Progress reporting from background to GUI

**Differences across apps**:
| Feature | Downloader | Transcript | TTS |
|---------|-----------|-----------|-----|
| Threading model | Single thread + semaphore for extraction | Single thread | Single thread |
| Cancellation | Aggressive (checked in logger callbacks) | Event-based | Between segments |
| Pause/Resume | ❌ | ✅ (Event-based) | ❌ |
| Progress granularity | Per-byte (yt-dlp progress hook) | Per-video | Per-segment |

**Unified service-layer pattern**:
- Abstract `BackgroundJob` with:
  - `start()`, `stop()`, `pause()`, `resume()`
  - Progress callback: `(current, total, message) → void`
  - Cancellation token checked between work units
  - State machine: Idle → Running → Paused → Done/Failed/Cancelled
- FastAPI integration: jobs tracked in DB, status queryable via REST
- SSE or polling for real-time progress updates to GUI

---

## 3. Settings Persistence Pattern

**Found in**: Downloader, Transcript, TTS (all three)

**Common behavior**:
- All use JSON files for settings persistence
- Settings loaded at startup with defaults for missing keys
- Settings saved after changes

**Differences across apps**:
| Feature | Downloader | Transcript | TTS |
|---------|-----------|-----------|-----|
| File | settings.json | download_config.json | (inline in app) |
| Save trigger | Debounced (delayed write) | Immediate | Debounced (400ms) |
| Migration | ❌ | ✅ (string→object format) | ❌ |
| Window geometry | ✅ | ❌ | ✅ |

**Unified settings service**:
- SQLite-backed settings with per-module namespaces:
  - `downloader.quality`, `downloader.path`, `downloader.cookie_mode`
  - `transcript.requests_per_hour`, `transcript.delay_between_requests`
  - `tts.voice`, `tts.speed`, `tts.output_format`, `tts.models_directory`
  - `app.window_geometry`, `app.theme`, `app.log_level`
- Atomic writes (SQLite transactions vs JSON file corruption risk)
- Settings API: `GET /api/v1/settings/{namespace}`, `PUT /api/v1/settings/{namespace}`
- Frontend: Zustand store synced with backend via TanStack Query

---

## 4. FFmpeg Integration Pattern

**Found in**: Downloader, TTS

**Common behavior**:
- FFmpeg used for media format conversion
- Availability checked at startup
- Subprocess calls for conversion

**Differences across apps**:
| Feature | Downloader | TTS |
|---------|-----------|-----|
| Use case | Audio extraction, format conversion | WAV→MP3 conversion |
| Detection | `check_ffmpeg_availability()` | Implicit (fails on first use) |
| Settings | MP3 bitrate/format selection | Fixed: 80kbps, 44.1kHz, mono |

**Unified media service**:
- `MediaService` (infrastructure adapter implementing `MediaPort`):
  - `is_available()` → bool
  - `get_version()` → string
  - `convert(input_path, output_path, options)` → result
  - `probe(file_path)` → MediaInfo (duration, format, bitrate, etc.)
- Auto-detection at startup, cached result
- Configurable FFmpeg binary path (bundled or system)

---

## 5. yt-dlp Integration Pattern

**Found in**: Downloader, Transcript

**Common behavior**:
- yt-dlp used for YouTube data extraction
- Both import `yt_dlp` directly
- Both need video metadata extraction

**Differences across apps**:
| Feature | Downloader | Transcript |
|---------|-----------|-----------|
| Use case | Full video download | Flat playlist extraction (video IDs only) |
| Options complexity | High (format selectors, cookies, SABR) | Low (just `flat_playlist=True`) |
| Error handling | SABR detection, age restriction | Simple retry |

**Unified YouTube adapter**:
- `YouTubeAdapter` (infrastructure adapter implementing `YouTubePort`):
  - `extract_info(url, flat=False)` → VideoInfo | PlaylistInfo
  - `extract_video_ids(channel_url)` → list[str]
  - `download(url, options)` → DownloadResult
  - `get_formats(video_id)` → list[FormatInfo]
  - `check_sabr_status()` → SABRStatus
- Shared cookie management
- Shared SABR detection logic
- Connection error handling and retry policies

---

## 6. File Browser Pattern

**Found in**: Downloader, TTS (Transcript uses config, not browser)

**Common behavior**:
- Directory selection dialog for output path
- Selected path displayed in read-only entry
- Path persisted in settings

**Unified component**:
- Shared React component: `DirectoryPicker`
  - Current path display
  - "Change..." button → native Electron dialog (`dialog.showOpenDialog`)
  - Path validation (exists, writable)
  - Used by: Download path, TTS output path, Model storage path

---

## 7. Window State Pattern

**Found in**: Downloader, TTS

**Common behavior**:
- Window geometry (size + position) saved on close
- Restored on next open

**Unified approach**:
- Electron `electron-store` for window state (same as Zorivest)
- Per-feature panel sizes stored (e.g., console panel height, sidebar width)
- Responsive layout with drag-to-resize panels
