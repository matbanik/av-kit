# Video Conversion & Media Processing — Pseudo Logic

> **Source**: `p:\av-kit\_inspiration\shutter-encoder-master\` (Java, ~350KB of source) + `P:\ffmpeg\.agent\docs\shutter-encoder-guide.md`
> **User Intent**: Bulk video compression with GPU acceleration, video cutting at specific times, and audio extraction from video files.
> **This document captures functional intent, FFmpeg command patterns, and GPU acceleration strategies — NOT code.**

---

## Feature Set Overview

| Feature | Priority | Description |
|---------|----------|-------------|
| **Bulk video compression** | Core | Queue of video files → H.265 NVENC → reduced file size |
| **GPU-accelerated encoding** | Core | Auto-detect NVIDIA/AMD/Intel → use hardware encoder |
| **CQ mode** (constant quality) | Core | Quality-based encoding vs bitrate-based |
| **Video cutting** | Core | Trim at specific in/out points with frame accuracy |
| **Audio extraction** | Core | Extract audio tracks from video without re-encoding |
| **2-pass encoding** | Secondary | Better quality at target bitrate (used with VBR) |
| **File size targeting** | Secondary | Specify desired output size → auto-calculate bitrate |
| **Resolution scaling** | Secondary | Downscale (e.g., 1080p → 720p) during encoding |

---

## 1. Bulk Video Conversion Pipeline

### Queue Processing Pattern (from Shutter Encoder)

```
File List (drag-and-drop or browse)
    ↓
For each file in queue:
    1. FFPROBE: analyze → get codec, resolution, fps, duration, audio streams
    2. Build FFmpeg command string from settings
    3. Execute FFmpeg as subprocess
    4. Monitor progress (parse stderr for frame count / speed)
    5. On complete: move to next file
    6. On error: log, continue or stop based on policy
    ↓
All files processed → summary report
```

**Key behavioral contracts**:
- Files processed **sequentially** (not parallel — GPU encoder is single-instance)
- Each file gets its own FFPROBE analysis before encoding
- Progress per file: `frame=X time=HH:MM:SS.ms speed=N.Nx` parsed from FFmpeg stderr
- Cancellation supported between files and mid-encode (send `q` to FFmpeg stdin)
- Duplicate output filenames: auto-increment suffix (`_1`, `_2`)
- Skip existing files option

### File Information Extraction (FFPROBE)

Before encoding, probe each file for:

| Property | FFprobe Flag | Use |
|----------|-------------|-----|
| Video codec | `-show_entries stream=codec_name` | Determine GPU decode compatibility |
| Resolution | `-show_entries stream=width,height` | Display in queue, scaling decisions |
| Frame rate | `-show_entries stream=r_frame_rate` | Progress calculation, conforming |
| Duration | `-show_entries format=duration` | Progress bar, ETA calculation |
| Audio streams | `-show_entries stream=codec_type` | Audio extraction, stream mapping |
| Audio codec | `-show_entries stream=codec_name` | Determine output container for extraction |
| Bit depth | `-show_entries stream=bits_per_raw_sample` | 8-bit vs 10-bit GPU filter selection |
| Interlacing | `-show_entries stream=field_order` | Deinterlace decision |

---

## 2. GPU-Accelerated Encoding

### Hardware Detection Strategy (from Shutter Encoder FFMPEG.java)

**Startup detection sequence**:

1. **Enumerate GPU hardware** (Windows: parse `wmic path win32_VideoController`, Mac: `system_profiler`)
   - Set flags: `hasNvidiaGPU`, `hasAMDGPU`, `hasIntelGPU`
   
2. **Verify actual GPU encode/decode capability** via probe command:
   - Run a 1-frame encode test: `ffmpeg -hwaccel cuda -i test.mp4 -frames:v 1 -f null -`
   - If succeeds → mark as available
   - If fails → fall back to next GPU type or software

3. **GPU filter compatibility test** (used for deinterlacing, scaling):
   - CUDA: `scale_cuda=640:360,hwdownload,format=nv12`
   - AMF: `vpp_amf=640:360,hwdownload,format=nv12`
   - QSV: `scale_qsv=640:360,hwdownload,format=nv12`
   - Vulkan: `scale_vulkan=640:360,hwdownload,format=nv12`

### Encoder Selection Logic

| GPU Type | Encoder Name | FFmpeg Codec | Detect Via |
|----------|-------------|--------------|-----------|
| **NVIDIA** | NVENC | `hevc_nvenc` / `h264_nvenc` / `av1_nvenc` | CUDA probe |
| **AMD** | AMF | `hevc_amf` / `h264_amf` / `av1_amf` | D3D11VA probe |
| **Intel** | QSV | `hevc_qsv` / `h264_qsv` / `av1_qsv` | QSV probe |
| **Any** | Vulkan | `hevc_vulkan` / `h264_vulkan` | Vulkan probe |
| **None** | Software | `libx265` / `libx264` / `libaom-av1` | Default fallback |

### NVENC-Specific Settings (from guide + source)

**Presets** (NVENC uses `p1`–`p7`, not `ultrafast`–`veryslow`):

| Preset | Speed | Quality | Use Case |
|--------|-------|---------|----------|
| `p1` | Fastest | Lowest | Real-time streaming |
| `p4` | Balanced | Good | Default batch encoding |
| `p7` | Slowest | Best | "Max Quality" checkbox |

**Tune modes**:
- H.264 NVENC: `-tune hq`
- H.265 NVENC: `-tune uhq` (ultra high quality)
- AV1 NVENC: `-tune uhq`

### GPU Decode + Encode Pipeline (Zero-Copy)

When both decode and encode are GPU-accelerated:

```
# Full GPU pipeline (fastest — no CPU-GPU transfer)
ffmpeg -hwaccel cuda -hwaccel_output_format cuda -i input.mp4 \
  -c:v hevc_nvenc -preset p4 -cq 25 output.mp4

# GPU decode → CPU filter → GPU encode (when filters needed)
ffmpeg -hwaccel cuda -hwaccel_output_format cuda -i input.mp4 \
  -vf "scale_cuda=1280:720,hwdownload,format=nv12" \
  -c:v hevc_nvenc -preset p4 -cq 25 output.mp4
```

**10-bit handling**: Replace `format=nv12` with `format=p010`.

---

## 3. Rate Control Modes

### CQ Mode (Constant Quality) — Recommended Default

| CQ Value | Quality | ~Compression Ratio | Use Case |
|:---:|---|---|---|
| **18–20** | Near-lossless | ~2:1 | Archival |
| **22** | Excellent | ~3:1 | Personal library |
| **25** | Balanced ⭐ | ~4:1 | Best quality-to-size ratio |
| **28** | Good | ~5:1 | Streaming/sharing |
| **30–32** | Acceptable | ~7:1 | Mobile/web upload |

**FFmpeg flag**: `-cq 25 -qmin 0 -qmax 51` (for NVENC)
**For software x265**: `-crf 25`

### VBR Mode (Variable Bitrate)

```
ffmpeg -i input.mp4 -c:v hevc_nvenc -b:v 5000k output.mp4
```

### File Size Target Mode

1. Calculate required bitrate from target:
   ```
   target_bitrate = (target_size_MB * 8192) / duration_seconds - audio_bitrate
   ```
2. Use 2-pass encoding for best results:
   ```
   ffmpeg -i input.mp4 -c:v libx265 -b:v {calculated}k -pass 1 -f null /dev/null
   ffmpeg -i input.mp4 -c:v libx265 -b:v {calculated}k -pass 2 output.mp4
   ```

### 2-Pass Encoding

```
# Pass 1: Analysis (fast — output discarded)
ffmpeg -i input.mp4 -c:v hevc_nvenc -b:v 5000k -pass 1 -passlogfile out -f null /dev/null

# Pass 2: Encoding (uses analysis data)
ffmpeg -i input.mp4 -c:v hevc_nvenc -b:v 5000k -pass 2 -passlogfile out output.mp4
```

---

## 4. Video Cutting (In/Out Points)

### Frame-Accurate Cutting (from Shutter Encoder InputAndOutput.java)

**Behavioral contract**:
- User sets In Point (HH:MM:SS.FF) and Out Point via video player
- Timecodes converted to milliseconds for FFmpeg `-ss` and `-t` flags
- NTSC drop-frame timecodes handled (29.97, 59.94 fps)

**FFmpeg patterns**:

```bash
# Fast seek (input-level) + duration
ffmpeg -ss 00:01:30.000 -i input.mp4 -t 00:02:00.000 -c copy output.mp4

# Frame-count based (more accurate for specific frame counts)
ffmpeg -ss 00:01:30.000 -i input.mp4 -frames:v 1500 -c copy output.mp4

# Re-encode for frame accuracy (when -c copy has keyframe alignment issues)
ffmpeg -ss 00:01:30.000 -i input.mp4 -t 00:02:00.000 -c:v hevc_nvenc -cq 25 output.mp4
```

**Apply cut to all** (batch cutting): Same in/out points applied to every file in queue.

### Split Mode

Split video into equal segments:

```bash
ffmpeg -i input.mp4 -force_key_frames "expr:gte(t,n_forced*300)" \
  -f segment -segment_time 300 -reset_timestamps 1 \
  output_%03d.mp4
```

---

## 5. Audio Extraction

### Extract Audio Without Re-Encoding (from Shutter Encoder Extract.java)

**Stream mapping strategy**:
```bash
# Extract audio stream (copy, no re-encode)
ffmpeg -i input.mp4 -vn -sn -c:a copy -map a:0 output.m4a

# Extract specific audio stream (multi-audio files)
ffmpeg -i input.mp4 -vn -sn -c:a copy -map a:1 output_audio_2.m4a

# Extract video stream only
ffmpeg -i input.mp4 -an -sn -c:v copy -map v:0 output_video.mp4

# Extract all streams separately
# Video → output_video_1.mp4
# Audio → output_audio_1.m4a (per stream)
# Subtitles → output_subtitles_1.srt (per stream)
```

**Container auto-selection** (based on detected audio codec):

| Audio Codec | Output Container |
|-------------|-----------------|
| PCM (pcm_*) | `.wav` |
| AAC | `.m4a` |
| AC3 / EAC3 | `.ac3` / `.eac3` |
| Opus | `.opus` |
| Vorbis | `.oga` |
| MP3 | `.mp3` |
| MP2 | `.mp2` |
| WMA | `.wma` |

**Metadata preservation**:
```bash
# Preserve audio metadata
ffmpeg -i input.mp4 -vn -c:a copy -map a:0 -map_metadata:s:a 0:s:a output.m4a

# Preserve video metadata
ffmpeg -i input.mp4 -an -c:v copy -map v:0 -map_metadata 0 -movflags use_metadata_tags output.mp4
```

---

## 6. Audio Settings for Video Encoding

| Setting | FFmpeg Flag | Recommendation |
|---------|-------------|---------------|
| Copy (no re-encode) | `-c:a copy` | Best when audio doesn't need changes |
| AAC 128kbps | `-c:a aac -b:a 128k` | Good for most content |
| AAC 192kbps | `-c:a aac -b:a 192k` | Music videos |
| Stereo downmix | `-ac 2` | Reduce 5.1 → stereo |

---

## 7. Resolution Scaling

```bash
# Scale to specific resolution (maintain aspect ratio)
ffmpeg -i input.mp4 -vf "scale=1280:720" -c:v hevc_nvenc output.mp4

# Scale by percentage
ffmpeg -i input.mp4 -vf "scale=iw/2:ih/2" -c:v hevc_nvenc output.mp4

# GPU-accelerated scaling (NVIDIA)
ffmpeg -hwaccel cuda -hwaccel_output_format cuda -i input.mp4 \
  -vf "scale_cuda=1280:720" -c:v hevc_nvenc output.mp4

# Ensure even dimensions (required by most codecs)
ffmpeg -i input.mp4 -vf "scale=1280:-2" -c:v hevc_nvenc output.mp4
```

---

## 8. Advanced Features

### Deinterlacing (GPU-Accelerated)

| GPU | FFmpeg Filter |
|-----|--------------|
| NVIDIA | `bwdif_cuda=0:{field}:0,hwdownload,format=nv12` |
| Intel QSV | `vpp_qsv=deinterlace=1,hwdownload,format=nv12` |
| Vulkan | `bwdif_vulkan=0:{field}:0,hwdownload,format=nv12` |
| Software | `yadif=0:{field}:0` or `bwdif=0:{field}:0` |

### Profile/Level Selection

**H.264**: Default `high`, level `5.1` for up to 1080p. Auto-level for 4K+.
**H.265**: Default `main`. Use `main10` for 10-bit content.
**NVENC H.265 max quality**: `-preset p7 -tune uhq -profile:v main`

### GOP (Group of Pictures)

```bash
# Custom GOP size (keyframe interval)
ffmpeg -i input.mp4 -c:v hevc_nvenc -g 250 output.mp4
```

---

## Implementation Approach for av-kit

### Domain Entities

```
ConversionJob:
  id, input_path, output_path, codec, rate_control_mode,
  quality_value, audio_bitrate, status, progress,
  gpu_encoder, preset, created_at

ConversionPreset:
  name, codec, rate_control, quality, audio_bitrate,
  resolution, max_quality, description

CutJob:
  id, input_path, output_path, in_point_ms, out_point_ms,
  copy_mode, status

ExtractionJob:
  id, input_path, output_path, stream_type (video/audio/subtitle),
  stream_index, status
```

### Service Layer

```
ConversionService:
  - add_to_queue(file_path, preset) → ConversionJob
  - start_batch_processing()
  - stop_processing()
  - get_queue() → list[ConversionJob]
  - detect_gpu() → GPUCapabilities
  - estimate_output_size(file_path, preset) → size_bytes

CutService:
  - cut_video(file_path, in_ms, out_ms, copy_mode) → CutJob
  - split_video(file_path, segment_duration_sec) → list[CutJob]

ExtractionService:
  - extract_audio(file_path, stream_index) → ExtractionJob
  - extract_video(file_path) → ExtractionJob
  - extract_all(file_path) → list[ExtractionJob]
  - list_streams(file_path) → list[StreamInfo]
```

### Infrastructure Adapter: FFmpegAdapter

```
FFmpegAdapter (implements MediaPort):
  - probe(file_path) → MediaInfo
  - encode(file, options, on_progress) → result
  - extract_stream(file, stream_type, stream_index, output) → result
  - cut(file, in_ms, out_ms, copy, output) → result
  - detect_gpu() → GPUCapabilities
  - is_available() → bool
  - get_version() → str
```

### GPU Detection Sequence (on app startup)

```
1. Run: ffmpeg -encoders | grep nvenc → check for hevc_nvenc
2. If found: run 1-frame GPU encode test
3. If test passes: GPU encoding available
4. Repeat for amf, qsv, vulkan
5. Store result in GPUCapabilities:
   - nvidia_nvenc: bool
   - amd_amf: bool
   - intel_qsv: bool
   - vulkan: bool
   - recommended_encoder: str
```

### GUI Components

```
features/converter/
  ├── FileQueue.tsx          — Drag-and-drop file list with probe info
  ├── PresetSelector.tsx     — Preset cards (Archival, Balanced, Fast)
  ├── QualityControls.tsx    — CQ slider, bitrate, file size target
  ├── AudioControls.tsx      — Audio codec, bitrate, copy toggle
  ├── GPUStatus.tsx          — Detected GPU, encoder in use
  ├── BatchProgress.tsx      — Per-file and overall progress
  └── AdvancedPanel.tsx      — Resolution, 2-pass, GOP, preset override

features/cutter/
  ├── VideoTimeline.tsx      — Visual timeline with in/out markers
  ├── TimeInput.tsx          — HH:MM:SS.FF input fields
  ├── SplitControls.tsx      — Segment duration for split mode
  └── CutPreview.tsx         — Preview frames at cut points

features/extractor/
  ├── StreamList.tsx         — List of video/audio/subtitle streams
  ├── StreamDetails.tsx      — Codec, bitrate, language per stream
  └── ExtractControls.tsx    — Extract selected / extract all
```

### Presets (Built-In)

| Preset Name | Codec | CQ | Audio | Preset | Description |
|-------------|-------|----|-------|--------|-------------|
| Archival | H.265 | 18 | Copy | p7 (max) | Maximum quality, larger files |
| High Quality | H.265 | 22 | 128k | p4 | Personal library |
| Balanced ⭐ | H.265 | 25 | 128k | p4 | Best quality-to-size ratio |
| Sharing | H.265 | 28 | 128k | p4 | Good for streaming/upload |
| Mobile | H.265 | 30 | 96k | p4 | Small files, 720p downscale |

### Integration with Existing av-kit Features

- **Downloader → Converter**: After downloading, offer to compress the video
- **Converter → TTS**: Extract audio → generate transcript → TTS
- **Extractor → Transcript**: Extract audio → feed to transcript pipeline
- **Settings unified**: Conversion presets stored in same SQLite settings service
