# YouTube Transcript Downloader — Pseudo Logic

> **Source**: `p:\av-kit\YouTube-Transcript-Downloader\myc_gui.py` (627 lines)
> **User Intent**: "I want to batch-download all transcripts from YouTube channels and compile them into Markdown documents."
> **This document captures functional intent and behavioral contracts — NOT code.**

---

## 1. Channel Resolution Flow

**User action**: Paste a YouTube channel URL → Click "Add Channel"

**Behavioral contract**:
1. Accept channel URL in various formats:
   - `/@handle` (e.g., `https://www.youtube.com/@drekberg`)
   - `/c/name` (e.g., `https://www.youtube.com/c/paulsaladinomd`)
   - `/channel/UCxxxxxxx` (channel ID format)
   - `/user/username` (legacy format)
2. Use yt-dlp flat extraction to resolve all video IDs for the channel
   - `flat_playlist=True` — only extract IDs, not full metadata
   - `playlist_end` setting limits extraction depth (0 = no limit)
3. Return list of video IDs
4. Channel appears in queue list with URL and completion status

**Channel queue management**:
- Queue is a list of channel objects: `{url, completed}`
- Channels can be added, removed, reordered
- Config file persists queue between sessions
- Migration: old format (plain string URLs) → new format (objects with completion flag)

---

## 2. Transcript Acquisition

**For each video ID in a channel**:
1. Attempt `YouTubeTranscriptApi.get_transcript(video_id)` with language preference
2. Try language fallback chain: requested language → English → any available
3. Handle specific errors:
   - `TranscriptsDisabled` → log and skip
   - `NoTranscriptFound` → log and skip
   - Generic exceptions → retry with backoff
4. On success: save transcript as individual file with video metadata

**Output format** (adapted from original .txt to .md with YAML frontmatter):
```
---
video_id: dQw4w9WgXcQ
title: "Video Title"
channel: "Channel Name"
url: https://www.youtube.com/watch?v=dQw4w9WgXcQ
date: 2026-05-26
---

# Video Title

Transcript text content here, one line per transcript segment...
```

---

## 3. Rate Limiting Strategy

**Why rate limiting exists**: YouTube throttles or blocks IPs that make too many API requests. The transcript API is particularly sensitive.

**Configuration contract**:

| Setting | Type | Default | Purpose |
|---------|------|---------|---------|
| `requests_per_hour` | int | 300 | Target request rate cap |
| `delay_between_requests` | int | 6 | Seconds between individual requests |
| `max_retries` | int | 3 | Retry count per failed transcript |
| `retry_delay` | int | 30 | Seconds before retry after failure |
| `batch_size` | int | 50 | Videos processed before batch pause |
| `pause_between_batches` | int | 300 | Seconds (5 min) pause between batches |

**Rate limiting flow**:
1. Process videos in batches of `batch_size`
2. Between each video: wait `delay_between_requests` seconds
3. After each batch: pause for `pause_between_batches` seconds
4. On failure: wait `retry_delay` seconds, then retry up to `max_retries` times
5. Delay can be fixed or randomized (configurable range, e.g., 1–77 seconds)

---

## 4. Markdown Compilation

**Behavioral contract** (adapted from original PDF to Markdown):
1. Collect all individual transcript files for a channel
2. Compile into per-channel Markdown document:
   - H1 heading: Channel name
   - Table of contents with links to each video section
   - H2 heading per video: Video title
   - Full transcript text under each heading
3. Word count tracking per document
4. Multi-volume splitting:
   - Configurable `max_words_per_document` (default: 490,000 words)
   - When word count exceeds limit, start new volume file
   - Volume naming: `channel_name_vol1.md`, `channel_name_vol2.md`
5. Output as `.md` files (no PDF/ReportLab dependency)

---

## 5. Progress & State Machine

**Per-channel progress tracking**:
- Progress file per channel (JSON): tracks which video IDs have been processed
- Resume capability: on restart, skip already-processed videos
- Channel completion marking: when all videos processed, mark channel as "completed"

**Channel status indicators**:
- Incomplete: normal display in queue
- Completed: `✅ [DONE]` prefix + green background in queue list
- `COMPLETED_PREFIX = "✅ [DONE] "` prepended to URL display

**Post-completion actions**:
- ZIP archive of raw transcript files created automatically
- Channel marked as completed in config (persisted)

---

## 6. Queue Processing

**Processing flow**:
1. User clicks "Start" → processing thread begins
2. For each non-completed channel in queue (top to bottom):
   a. Resolve all video IDs via yt-dlp
   b. Load progress file (resume from where we left off)
   c. Process unfinished video IDs with rate limiting
   d. Update progress file after each video
   e. On completion: ZIP raw files, compile Markdown, mark done
3. User can Pause → processing thread blocks on pause event
4. User can Stop → processing thread exits loop

**Pause/Resume/Stop**:
- `is_paused` event: when set, processing loop blocks (waits)
- `is_running` event: when cleared, processing loop exits
- Thread-safe events coordinate between GUI and processing thread

---

## 7. Configuration Contract

**Persisted settings** (JSON file `download_config.json`):

| Setting | Type | Default | Purpose |
|---------|------|---------|---------|
| `channels` | array | [] | Queue of `{url, completed}` objects |
| `requests_per_hour` | int | 300 | Rate limit cap |
| `delay_between_requests` | int | 6 | Inter-request delay |
| `max_retries` | int | 3 | Retry count |
| `retry_delay` | int | 30 | Retry delay (seconds) |
| `batch_size` | int | 50 | Batch size |
| `playlist_end` | int | 0 | Max videos per channel (0=all) |
| `pause_between_batches` | int | 300 | Batch pause (seconds) |
| `max_words_per_document` | int | 490000 | Max words per compiled doc |

**Config behavior**:
- Loaded at startup, defaults applied for missing keys
- Saved after any change
- Migration logic handles old format → new format automatically

---

## 8. Output Directory Structure

```
transcripts/
├── {channel_name}/
│   ├── raw/
│   │   ├── {video_id}.md          # Individual transcript with YAML frontmatter
│   │   ├── {video_id}.md
│   │   └── ...
│   ├── compiled/
│   │   ├── {channel_name}_vol1.md # Compiled Markdown with TOC
│   │   └── {channel_name}_vol2.md # (if multi-volume)
│   ├── progress.json              # Resume state
│   └── {channel_name}_raw.zip     # Archive of raw files
└── ...
```

---

## 9. Console / Logging

**Logging features**:
- Scrolled text widget showing processing progress
- Thread-safe: backend thread queues messages, GUI thread displays
- Log callback pattern: processor receives a `log_callback` function
- Messages include: video being processed, transcript found/not found, errors, completion status
- Per-video status updates during batch processing
