# av-kit — Application Purpose

> **What is this document?** A guided questionnaire defining the application's purpose, audience, and scope. This is the starting point for all planning and design work. Modeled after Zorivest's APPLICATION_PURPOSE.md.

---

## 1. What does av-kit do?

av-kit is a **unified YouTube media toolkit** — a single desktop application that combines three previously separate tools:

1. **YouTube Video Downloader** — Download videos and playlists with quality control, queue management, and SABR bypass
2. **YouTube Transcript Downloader** — Batch-download all transcripts from YouTube channels and compile them into Markdown documents
3. **Text-to-Speech (TTS)** — Convert text to speech using local AI models (Kokoro-82M) with voice selection, speed control, and format options

The application also provides **AI agent access** via an MCP server, enabling AI coding assistants to trigger downloads, extract transcripts, and generate audio programmatically.

---

## 2. Who is the user?

| User Type | Description | Primary Module |
|-----------|-------------|----------------|
| **Content Creator** | Downloads videos for reference, generates transcripts for research, creates audio narrations | All three |
| **Researcher** | Batch-downloads transcripts from channels for analysis, compiles into searchable documents | Transcript + TTS |
| **Developer** | Uses MCP tools to automate media workflows, integrates with AI coding assistants | MCP Server |
| **Podcaster** | Converts written content to speech for audio versions of articles | TTS |
| **Archivist** | Downloads and catalogs YouTube content with metadata tracking | Downloader |

---

## 3. Core Problem

**Fragmentation.** Users currently need three separate applications, each with its own settings, UI paradigm, and dependencies. All three share underlying dependencies (yt-dlp, FFmpeg) but manage them independently.

**What we solve:**
- One installation, one UI, shared settings
- Unified queue and progress management
- Single MCP server for AI agent access to all capabilities
- Shared dependency management (yt-dlp, FFmpeg, Kokoro model)

---

## 4. Feature Areas

### 4A. Video Downloader
- URL paste → auto-detect type (video / playlist / channel / shorts)
- Quality selection with SABR bypass fallback chain
- Download queue with reorder, pause, resume, cancel
- Cookie authentication (browser extraction or file)
- Audio-only extraction with format selection
- Archive tracking (skip previously downloaded)
- Progress reporting per item and overall

### 4B. Transcript Downloader
- Channel URL → resolve all video IDs
- Batch transcript download with rate limiting
- Individual .md files with YAML frontmatter (title, channel, date, video ID, URL)
- Compiled per-channel Markdown with TOC and heading hierarchy
- Multi-volume splitting at configurable word count
- Resume capability with progress files
- Multi-channel queue with completion indicators

### 4C. Text-to-Speech
- Text input (paste or file load) with statistics
- LM Studio-inspired model management (Discover / Download / Load / Unload)
- Kokoro-82M support (PyTorch + ONNX variants: FP32, FP16, INT8)
- Voice selection across languages with speed control
- GPU offload controls with VRAM/RAM usage estimates
- WAV and MP3 output with FFmpeg conversion
- Battle-tested text preparation (number spelling, acronym spacing, sentence length limits)

### 4D. Settings
- Per-module settings with unified persistence
- Download path, quality preferences, audio format
- Rate limiting configuration
- Model directory, device preference
- Window geometry and layout preferences

### 4E. MCP Server
- Download tools (trigger download, check status, list queue)
- Transcript tools (extract transcript, batch channel download)
- TTS tools (generate audio, list voices, check model status)
- Settings tools (read/write configuration)

---

## 5. Data Sources & Integrations

| Source | Protocol | Used By |
|--------|----------|---------|
| YouTube | yt-dlp (HTTP) | Downloader, Transcript |
| YouTube Transcript API | REST | Transcript |
| Hugging Face Hub | REST / huggingface_hub | TTS (model download) |
| Kokoro-82M | Local inference (PyTorch / ONNX) | TTS |
| FFmpeg | Local subprocess | Downloader, TTS |
| SQLite | Local file | Settings, job queue, history |

---

## 6. Non-Functional Requirements

| Requirement | Target |
|-------------|--------|
| **Startup time** | < 3 seconds to usable UI (splash screen during backend startup) |
| **Download performance** | Match yt-dlp CLI speed (no overhead from GUI layer) |
| **TTS generation** | Real-time factor < 1.0x on GPU, < 3.0x on CPU |
| **Model loading** | < 10 seconds for Kokoro ONNX INT8 on modern hardware |
| **Offline capable** | All features except YouTube API calls work offline after initial setup |
| **Disk footprint** | < 500MB without models; models managed separately |
| **Platform** | Windows 10/11 primary; macOS/Linux secondary |
| **Architecture** | Same as Zorivest: Electron + React + FastAPI + MCP + TDD |

---

## 7. Questions for Deep Research Phase

These questions will be directed to the deep research workflow when ready:

1. What is the current state of SABR bypass in yt-dlp (2026)?
2. How do other Electron apps handle bundling Python ML models?
3. What are the latest Kokoro-82M quantization options and performance benchmarks?
4. How should the MCP server handle long-running operations (downloads, TTS generation)?
5. What rate limiting strategies avoid YouTube transcript API bans?
6. How do modern desktop apps handle GPU detection and fallback for ML inference?
