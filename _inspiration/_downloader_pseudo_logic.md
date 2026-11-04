# YouTube Video Downloader — Pseudo Logic

> **Source**: `p:\av-kit\yt-dlp_GUI\youtube_downloader.py` (4,406 lines)
> **User Intent**: "I want to download YouTube videos and playlists with quality control, queue management, and SABR bypass."
> **This document captures functional intent and behavioral contracts — NOT code.**

---

## 1. URL Resolution Flow

**User action**: Paste a YouTube URL → Click "Add"

**Behavioral contract**:
1. Accept URL from input field
2. Detect URL type:
   - Single video (`/watch?v=...`, `/shorts/...`)
   - Playlist (`/playlist?list=...`, `&list=...` in video URL)
   - Channel (`/@handle`, `/c/name`, `/channel/id`)
3. For single videos → extract video ID, title, duration via yt-dlp info extraction
4. For playlists/channels → flat-extract all video IDs → add each as a separate queue entry
5. Extract metadata (title, duration, format availability) in background thread
6. Add to download queue with status "Pending"
7. Duplicate detection: if video ID already in queue, warn and skip

**Info caching**:
- Cache extracted metadata per video ID to avoid re-extraction
- Cache has expiry timer (~5 minutes between cleanups)
- Lock per-URL to prevent concurrent extractions of the same video
- Semaphore limits concurrent extractions to 5

---

## 2. Quality Negotiation

**Behavioral contract**:
1. User selects target quality from dropdown:
   - Options: Best, 2160p (4K), 1440p (2K), 1080p, 720p, 480p, 360p, 240p, 144p, Lowest
2. Quality applies to: selected items in queue AND newly added items
3. yt-dlp format selector mapping:
   - "Best" → `bestvideo+bestaudio/best`
   - "1080p" → `bestvideo[height<=1080]+bestaudio/best[height<=1080]`
   - etc.
4. Quality setting change triggers update of all selected queue items

**SABR interaction**:
- Under SABR restrictions, quality options shrink to ["360p"] only
- Audio options shrink to ["standard_mp3", "high_m4a"]
- Quality-blocked items get status "QualityBlocked" (orange color in UI)

---

## 3. SABR Bypass System

**What is SABR?**
YouTube's Server-Adaptive Bitrate streaming system that can block certain download clients from accessing high-quality formats. Detection happens at download time via yt-dlp warnings.

**Detection flow**:
1. **Passive detection**: yt-dlp logger watches for SABR indicator strings in real-time:
   - "require a gvs po token"
   - "android client sabr formats require"
   - "ios client sabr formats require"
2. **Manual check**: User clicks "Check SABR" button → runs test extraction on a known video
3. **Force mode**: User clicks "Force SABR" button → activates SABR mode without detection

**SABR mode activation**:
- Visual indicator appears in UI (frame with warning label)
- Quality dropdown restricted to SABR-compatible options only
- Audio format dropdown restricted similarly
- All items using incompatible quality get status updated to "QualityBlocked"
- Download logic switches to SABR-compatible format selectors

**Client fallback chain** (yt-dlp extractor_args):
- Normal mode: default yt-dlp client rotation
- SABR mode: specific client ordering that avoids SABR-blocked formats
- Cookie mode adjusts client selection further (cookie-compatible clients only)

---

## 4. Download Orchestration

**Queue data structure** (per item):
- Video ID, Title, Quality, Duration, Status
- Quality/Audio format applied at add-time or changed via selection

**Status state machine**:
```
Pending ──→ Downloading ──→ Done
                │              ↑
                ├──→ Failed ───┘ (via Reset)
                ├──→ Skipped (duplicate/archive)
                ├──→ QualityBlocked (SABR)
                └──→ AgeRestricted
```

**Status colors in UI**:
| Status | Color | Count displayed |
|--------|-------|-----------------|
| Total | Black | Always |
| Done | Green | Always |
| Pending | Black | Always |
| Failed | Red | Always |
| Skipped | Purple | Always |
| QualityBlocked | Orange | Always |
| AgeRestricted | Brown | Always |
| Downloading | Blue | Always |

**Queue operations**:
- Add (from URL input)
- Remove Selected / Clear All
- Move Up / Move Down / Move to Top / Move to Bottom
- Reset Selected (Failed → Pending for retry)
- Sort by any column (ID, Name, Quality, Duration, Status)

**Processing flow**:
1. "Start" button initiates download thread
2. Sequential processing: pick first "Pending" item
3. Build yt-dlp options dictionary with:
   - Format selector based on quality + SABR mode
   - Download path
   - Cookie options (if enabled)
   - Progress hook callback
   - Logger instance
4. Execute yt-dlp download
5. Update status based on result
6. Move to next "Pending" item
7. "Stop" button sets stop_event → current download raises DownloadCancelled
8. Stop detection is aggressive — checked in logger callbacks, progress hooks, and download loops

**Progress tracking**:
- yt-dlp progress hook reports: filename, downloaded bytes, total bytes, speed, ETA
- Throttled to prevent UI lag (time-based limiting on progress updates)
- Progress displayed in status bar area

---

## 5. Cookie Authentication

**Three modes**:
1. **None** — no cookie injection
2. **From Browser** — extract cookies from installed browser
   - Browser selection: chrome, firefox, edge, brave, opera, vivaldi, chromium, whale, safari
   - Optional browser profile specification
   - Warning: "Close browser first!" (browser lock prevents cookie access)
   - Test button to verify cookie extraction works
3. **From File** — load Netscape-format cookies.txt file
   - File browser dialog
   - Read-only display of selected path

**Cookie injection into yt-dlp**:
- `from_browser` mode: `cookiesfrombrowser: (browser_name, profile_path)`
- `from_file` mode: `cookiefile: path_to_cookies.txt`
- Cookie mode affects which yt-dlp clients are viable (some clients don't support cookies)

---

## 6. Audio Extraction

**Audio-only mode**:
- Checkbox toggles audio-only mode
- When enabled, audio format dropdown appears (hidden by default)
- Format options (9 choices):
  - default (Auto), best (Highest Quality), lowest (Smallest Size)
  - low_webm (~48kbps Opus), medium_webm (~70kbps Opus), standard_webm (~128kbps Opus)
  - standard_m4a (~128kbps AAC), standard_mp3 (~192kbps MP3), high_m4a (~160kbps AAC)

**FFmpeg dependency**:
- Audio extraction requires FFmpeg for format conversion
- App checks FFmpeg availability at startup
- If FFmpeg missing: warning shown, some audio formats unavailable

**SABR impact on audio**:
- Under SABR mode, audio options restricted to: standard_mp3, high_m4a

---

## 7. Archive Tracking

**Behavioral contract**:
- Download history tracked for duplicate detection
- When adding URL, check if video ID was previously downloaded
- Previously downloaded videos get status "Skipped"
- Archive is persistent across sessions

---

## 8. Settings Contract

**Persisted settings** (JSON file `settings.json`):

| Setting | Type | Default | Scope |
|---------|------|---------|-------|
| `download_path` | string | ~/Downloads | Download location |
| `quality` | string | "1080p" | Video quality preference |
| `audio_only` | bool | false | Audio extraction mode |
| `audio_format` | string | "default" | Audio format when audio_only |
| `console_visible` | bool | true | Console panel visibility |
| `log_level` | string | "INFO" | Console log level filter |
| `yt_dlp_debug` | bool | false | Show yt-dlp debug output |
| `cookie_mode` | string | "none" | Cookie authentication mode |
| `cookie_browser` | string | "chrome" | Browser for cookie extraction |
| `cookie_browser_profile` | string | "" | Browser profile name |
| `cookie_file_path` | string | "" | Path to cookies.txt |
| `window_geometry` | string | "800x700" | Window size and position |
| `queue_state` | array | [] | Saved queue items |

**Settings behavior**:
- Settings changes trigger debounced save (delayed write to prevent excessive IO)
- Quality and audio format changes apply to selected items immediately via trace callbacks
- Window geometry saved on close, restored on open

---

## 9. Console / Logging System

**Console features**:
- Scrolled text widget with log output
- Toggle visibility (checkbox)
- Log level filter: DEBUG, INFO, WARNING, ERROR, CRITICAL
- yt-dlp debug toggle (separate from app log level)
- Clear logs button
- Thread-safe message queue: background threads queue messages, GUI thread processes them
- yt-dlp messages prefixed with `[yt-dlp]` tag

**Message routing**:
- yt-dlp logger → message_queue → GUI thread processes → display in console
- App messages → direct log_message call → display in console
- Progress updates → progress_queue → GUI thread processes → update status bar

---

## 10. Dependency Management

**Runtime dependencies**:
- yt-dlp (Python library, imported directly)
- FFmpeg (external binary, detected via subprocess)
- No other external services required

**Check Dependencies button**:
- Verifies yt-dlp version
- Verifies FFmpeg availability and version
- Reports results in console
