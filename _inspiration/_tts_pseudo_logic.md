# Kokoro TTS Application — Pseudo Logic

> **Source**: `p:\av-kit\kokoro\kokoro_tts_app.py` (908 lines)
> **User Intent**: "I want to convert text to speech using local AI TTS models with voice selection and format options."
> **This document captures functional intent and behavioral contracts — NOT code.**

---

## 1. Text Input Flow

**User action**: Type/paste text into text area OR load from file

**Behavioral contract**:
1. Large text input area (main UI panel)
2. "Load File" button → file dialog → read text file → populate text area
3. Text statistics computed on every change:
   - Bytes (raw size)
   - Words (whitespace-split count)
   - Sentences (period/exclamation/question mark split)
   - Lines (newline count)
   - Estimated tokens (words × 1.3 approximation)
4. Statistics displayed in status area below text input
5. Empty text → generation button disabled

---

## 2. Voice & Speed Selection

**Voice presets**:
20 built-in voices across languages, each encoded with a language prefix:

| Prefix | Language | Example Voices |
|--------|----------|----------------|
| `af_` | American English (female) | af_heart, af_bella, af_nicole, af_sarah, af_sky |
| `am_` | American English (male) | am_adam, am_michael, am_eric |
| `bf_` | British English (female) | bf_emma, bf_isabella |
| `bm_` | British English (male) | bm_george, bm_lewis |
| `ef_` | Spanish (female) | ef_dora |
| `em_` | Spanish (male) | em_alex, em_santa |
| `ff_` | French (female) | ff_siwis |
| `hf_` | Hindi (female) | hf_alpha, hf_beta |
| `hm_` | Hindi (male) | hm_omega, hm_psi |
| `jf_` | Japanese (female) | jf_alpha |

**Language code derivation**:
- First character of voice name IS the language code
- `af_heart` → lang_code `a` (American English)
- `ef_dora` → lang_code `e` (Spanish)
- This mapping is critical: wrong lang_code produces garbled pronunciation

**Speed control**:
- Range: 0.5x to 2.0x
- Default: 1.0x
- Slider or spinner UI control
- Applied at generation time, not preview

---

## 3. Model Management (LM Studio-Inspired)

> **Design intent**: Replace the original app's lazy initialization with an explicit Discover → Download → Load → Unload lifecycle, inspired by LM Studio's UX patterns for local model management.

### 3A. Model Browser

**Available Kokoro variants from Hugging Face**:

| Variant | Format | Size | Source |
|---------|--------|------|--------|
| Kokoro-82M (PyTorch) | `.pth` + config | ~326 MB FP32 | `hexgrad/Kokoro-82M` |
| Kokoro-82M (ONNX FP32) | `.onnx` | ~326 MB | `onnx-community/Kokoro-82M-ONNX` |
| Kokoro-82M (ONNX FP16) | `.onnx` | ~163 MB | `onnx-community/Kokoro-82M-ONNX` |
| Kokoro-82M (ONNX INT8) | `.onnx` | ~92 MB | `onnx-community/Kokoro-82M-ONNX` |

**Browser behavior**:
- GUI panel listing available variants with format, size, and compatibility info
- Recommended variant highlighted based on detected hardware
- Refresh button to check for new versions

### 3B. Download Manager

**Download flow**:
1. User selects variant → clicks "Download"
2. Download via `huggingface_hub.hf_hub_download()`
3. Progress bar showing download percentage
4. Store in configurable local directory (default: `~/.avkit/models/`)
5. Downloaded models appear in "My Models" list

### 3C. Model Loader

**Load/Unload lifecycle**:
```
No Model ──→ Loading... ──→ Loaded (Ready)
                               │
                               └──→ Unloaded (back to No Model)
```

**Status indicator**: Always visible in UI header
- "No model loaded" (gray)
- "Loading Kokoro-82M (ONNX FP16)..." (yellow, with spinner)
- "Kokoro-82M (ONNX FP16) — GPU" (green, showing device)

**Device selection**:
- Auto-detect: CUDA GPU → MPS (Apple) → CPU
- Manual override via dropdown
- Show VRAM/RAM usage estimates before loading

### 3D. GPU Offload Controls

**For PyTorch variant**:
- Toggle or slider: CPU vs GPU inference
- Show estimated VRAM consumption
- Warning if model exceeds available VRAM

**For ONNX variant**:
- Execution provider selection: CUDA → DirectML → CPU
- No partial offloading (ONNX is all-or-nothing per provider)

### 3E. Sideloading

- Users can place compatible model files (`.pth`, `.onnx`) in the models directory
- App scans directory on startup and when "Refresh" clicked
- Sideloaded models appear alongside downloaded models

### 3F. Offline Mode

- Once model is cached locally, generation works without internet
- Set `HF_HUB_OFFLINE=1` environment variable when cached models exist
- No network calls during generation

### 3G. Voice Pack Management

- Voice embeddings (style vectors) are separate from base model
- Located in HuggingFace cache: `~/.cache/huggingface/hub/models--hexgrad--Kokoro-82M/snapshots/.../`
- 54 voices across 8 languages, pre-downloadable
- Voice packs can be managed independently of model variant

---

## 4. Generation Pipeline

**Original app behavior** (extracted for adaptation):
1. Load model lazily on first generation (original) → **New**: explicit load via Model Manager
2. Split text by paragraphs (`\n+` pattern) for long content
3. Generate audio segment-by-segment using KPipeline:
   - `pipe = KPipeline(lang_code='{code}')`
   - `generator = pipe(text, voice='{voice_id}', speed={speed}, split_pattern=r'\n+')`
   - Each segment yields: (graphemes, phonemes, audio_array)
4. Progress reporting: segment count, estimated completion
5. Cancellation support: check stop event between segments

**Critical parameters**:
- `lang_code`: MUST match voice prefix (first char of voice name)
- `split_pattern`: `r'\n+'` for paragraph-based chunking
- `speed`: float (0.5–2.0)
- Sample rate: 24000 Hz (fixed by Kokoro model)

**Error handling**:
- Model not loaded → prompt user to load first
- CUDA out of memory → fallback to CPU, notify user
- Empty text → silently skip
- Generation interrupted → clean up partial output

---

## 5. Audio Assembly

**Behavioral contract**:
1. Collect audio segments from generator (numpy arrays)
2. Concatenate all segments: `np.concatenate(segments)`
3. Save based on output format:

**WAV output**:
- Direct write via `soundfile.write()` at 24000 Hz

**MP3 output**:
- Write temp WAV first
- Convert via FFmpeg subprocess:
  - Bitrate: 80kbps (optimized for speech, not music)
  - Sample rate: 44100 Hz
  - Channels: mono
- Delete temp WAV after conversion
- Requires FFmpeg available in PATH or bundled

**Filename pattern**: `kokoro_{voice}_{segment_count}.{ext}`
- Example: `kokoro_af_heart_42.mp3`

---

## 6. Output Management

**Behavioral contract**:
1. Configurable output directory (file browser)
2. After successful generation:
   - Success dialog with file information
   - "Open File" action → opens audio file in system default player
   - "Open Folder" action → opens output directory in file explorer
3. File info displayed: size, duration, segment count

---

## 7. Settings Contract

**Persisted settings** (JSON file, debounced auto-save with 400ms delay):

| Setting | Type | Default | Purpose |
|---------|------|---------|---------|
| `voice` | string | "af_heart" | Selected voice preset |
| `speed` | float | 1.0 | Generation speed multiplier |
| `output_format` | string | "mp3" | Output format (wav/mp3) |
| `output_path` | string | ~/Documents | Output directory |
| `model_variant` | string | "" | Active model variant (new) |
| `device_preference` | string | "auto" | Device: auto/cuda/cpu (new) |
| `models_directory` | string | "~/.avkit/models" | Model storage location (new) |
| `input_text` | string | "" | Last entered text (for resume) |
| `window_geometry` | string | "" | Window size and position |

**Settings behavior**:
- Auto-save on every change with 400ms debounce (prevents excessive IO during typing)
- Settings restored on app launch
- Input text saved so user can resume work after restart

---

## 8. PyInstaller Considerations

The original app has extensive PyInstaller compatibility code:
- `multiprocessing.freeze_support()` for Windows
- `sys.stderr`/`sys.stdout` null guard for windowed mode
- spaCy model loading patches for bundled executables
- `_MEIPASS` path handling for bundled resources

**For av-kit**: These concerns move to the distribution phase (Phase 7 in build plan). The core service layer should be clean of these workarounds — they belong in the Electron packaging step.

---

## 9. Windows-Specific Behaviors

**From battle-tested matbanik.info production**:
- `conda run --no-capture-output` required (conda swallows errors on Windows)
- `python -c` with multiline strings fails silently in PowerShell
- KeyboardInterrupt contamination persists across terminal sessions
- Always write generation scripts to `.py` files, never inline
