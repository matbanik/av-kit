# Phase 0 — Overview

## Dependency Diagram

```
┌──────────────────────────────────────────────────────────────┐
│ Phase 6: GUI + Phase 8 Convert + Phase 9 Capture (tray/F2)   │
│ Phase 5: MCP + avkit_convert + avkit_capture                 │
├──────────────────────────────────────────────────────────────┤
│ Phase 4: REST API                                            │
├──────────────────────────────────────────────────────────────┤
│ Phase 3: Service Layer                                       │
├──────────────────────────────────────────────────────────────┤
│ Phase 2: Infrastructure (Adapters)                           │
├──────────────────────────────────────────────────────────────┤
│ Phase 1: Domain (Entities, Ports)                            │
└──────────────────────────────────────────────────────────────┘
```

## Build Order

1. **Domain first** — entities and ports define the vocabulary everything else uses
2. **Infrastructure second** — adapters implement ports, need domain types
3. **Services third** — orchestrate adapters through ports
4. **API fourth** — expose services via REST
5. **MCP and GUI in parallel** — both consume API
6. **Phase 8 conversion** — after the YouTube toolkit exists: domain addendum → FFmpeg encode/cut/extract → ConversionService → REST/MCP → Convert page under TTS. Canonical spec: [08-video-conversion.md](08-video-conversion.md).
7. **Phase 9 screenshot capture** — after Convert: domain addendum → capture adapter → CaptureService → REST/MCP → tray + F2 overlay + Capture page under Convert. Canonical spec: [09-screenshot-capture.md](09-screenshot-capture.md). Do not pack Session 8c (MEU-27).

## Golden Rules

1. Domain layer has ZERO dependencies on infrastructure
2. All IO goes through ports (protocol interfaces)
3. Every MEU has tests before implementation
4. Settings in SQLite, not JSON files
5. Same patterns as Zorivest (check before inventing) — command registry, HelpCards, independently verified orphan reap (**no attach**), testids

## Domain Model Reference

Canonical field lists, invariants, and “do not persist” rules: [01-domain-layer.md](01-domain-layer.md). This table is a summary only.

SQLite stores **job records and file pointers**, not transcript bodies or media bytes.

### Core Entities

| Entity | Module | Key Fields |
|--------|--------|------------|
| `DownloadJob` | Downloader | id, url, video_id, title, quality, audio_only, status, progress, file_path, queue_position |
| `DownloadArchiveEntry` | Downloader | extractor, video_id, recorded_at |
| `TranscriptJob` | Transcript | id, channel_url, channel_name, status, output_dir, video_count, word_count, zip_path |
| `TranscriptItem` | Transcript | job_id, video_id, title, path, status, word_count (child **record**, not a job) |
| `TTSJob` | TTS | id, source_kind, text_hash, text_preview, voice, speed, status, output_path |
| `ModelVariant` | TTS | id, name, format, precision, size_bytes, path, is_downloaded (not is_loaded) |
| `ConversionJob` | Convert (Phase 8) | id, kind, input_path, output_path, preset/cut/extract fields, status, progress |
| `CaptureShot` | Capture (Phase 9) | id, original_path, annotated_path, sidecar_path, width, height, source |
| `Setting` | Settings | namespace, key, value, updated_at |

### Enums

| Enum | Values |
|------|--------|
| `DownloadStatus` | Pending, Downloading, Done, Failed, Skipped, QualityBlocked, AgeRestricted, Cancelled |
| `TranscriptStatus` | Pending, Processing, Done, Failed, Paused, Cancelled |
| `TranscriptItemStatus` | Pending, Done, Skipped, Failed |
| `TTSStatus` | Pending, Generating, Done, Failed, Cancelled |
| `ConversionKind` | Compress, Cut, Extract (Phase 8) |
| `ConversionStatus` | Pending, Processing, Done, Failed, Cancelled, Skipped (Phase 8) |
| `CaptureSource` | Hotkey, Gui, McpFullscreen, McpRegion, McpInteractive, Scan, Import, Crop (Phase 9) |
| `CaptureRequestStatus` | Pending, Completed, Cancelled, Expired (Phase 9) |
| `MediaFormat` | MP4, WEBM, MP3, M4A, WAV, OPUS |
| `QualityPreset` | Best, P2160, P1440, P1080, P720, P480, P360, P240, P144, Lowest |
| `AudioFormat` | Default, Best, Lowest, LowWebm, MediumWebm, StandardWebm, StandardM4a, StandardMp3, HighM4a |
| `QueueProcessorState` | Idle, Processing, Paused (session only; not a job status) |
