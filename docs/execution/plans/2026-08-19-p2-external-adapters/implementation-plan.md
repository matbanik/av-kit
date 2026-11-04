---
project: "2026-08-19-p2-external-adapters"
date: "2026-08-19"
source: "docs/build-plan/02-infrastructure.md"
meus: ["MEU-6", "MEU-7", "MEU-9"]
status: "complete"
template_version: "2.0"
---

# Implementation Plan: Phase 2 External Adapters

> **Project**: `2026-08-19-p2-external-adapters`
> **Build Plan Section(s)**: [02-infrastructure.md](../../../build-plan/02-infrastructure.md) §YouTube, §Transcript, §TTS, §Model manager
> **Status**: `in_progress`
> **Grouping**: [2026-08-18-build-plan-session-grouping.md](../../../../.agent/context/grouping/2026-08-18-build-plan-session-grouping.md) Session 3 — MEU-6 → MEU-7 → MEU-9

---

## Goal

Implement the remaining Phase 2 **network/ML** adapters behind frozen Phase 1 Protocols: `YouTubePort` (yt-dlp import, not shell-out), `TranscriptPort` (`youtube_transcript_api`), `TTSPort` (`KokoroAdapter`: PyTorch via `kokoro.KPipeline`/`KModel`, ONNX via `onnxruntime.InferenceSession`), and `ModelCatalogPort` (`huggingface_hub`). Do not mutate `avkit_core.ports`. Do not rewrite SQLite/UoW, filesystem, or FFmpeg. Default-suite tests mock those libraries; live YouTube/HF is forbidden.

av-kit remains a **job queue**. Adapters return domain DTOs and file pointers. They do not open a UoW, do not store transcript text / cookies / tokens, and do not write WAV/MP3 from Kokoro (`MediaPort` already owns encode).

## Context Tool Decision

```yaml
context_tool_decision:
  phase: execution
  eligible_tools: []
  decision: not_applicable
  eligibility_basis: "graphify-out/graph.json and graphify-out-research/graph.json absent; Headroom has no approved disposition. Execution uses frozen ports + approved plan."
  human_message_reference: null
```

Re-evaluate before execution. Same absence basis is expected unless a graph file appears on disk.

## Handoff Set

| Scope | Canonical handoff |
|---|---|
| MEU-6 | `.agent/context/handoffs/2026-08-19-p2-external-adapters-MEU-6-handoff.md` |
| MEU-7 | `.agent/context/handoffs/2026-08-19-p2-external-adapters-MEU-7-handoff.md` |
| MEU-9 | `.agent/context/handoffs/2026-08-19-p2-external-adapters-MEU-9-handoff.md` |

Rolling implementation review: `.agent/context/handoffs/2026-08-19-p2-external-adapters-implementation-critical-review.md`.

The product glob owner is named set `HANDOFF_GLOB` (expected count **3**). Do not restate the wildcard here.

## Work Packages and Context Lifecycle

`fresh_worker: none` → every non-`shared` row is `compact_continue`. Never emit `isolated`.

| ID | Work | depends_on | context_strategy | durable_outputs |
|---|---|---|---|---|
| WP-6a | MEU-6 Red: layout/deps/signatures | — | `shared` | `C:/Temp/av-kit/fail-to-pass-meu-6-scaffold.txt` |
| WP-6b | MEU-6 Green: `youtube/adapter.py` + `yt-dlp` dep | WP-6a | `compact_continue` | `avkit_infra/youtube/adapter.py`; compact then re-read `task.md` |
| WP-6c | MEU-6 Red: extract_info / ids / formats | WP-6b | `compact_continue` | `C:/Temp/av-kit/fail-to-pass-meu-6-extract.txt` |
| WP-6d | MEU-6 Green: extract/format mapping | WP-6c | `compact_continue` | `avkit_infra/youtube/adapter.py` |
| WP-6e | MEU-6 Red: download/cookies/SABR/cancel | WP-6d | `compact_continue` | `C:/Temp/av-kit/fail-to-pass-meu-6-download.txt` |
| WP-6f | MEU-6 Green: download + cookie test + SABR | WP-6e | `compact_continue` | `avkit_infra/youtube/adapter.py` |
| WP-7a | MEU-7 Red: transcript fetch/None/retryable | WP-6f | `compact_continue` | `C:/Temp/av-kit/fail-to-pass-meu-7.txt` |
| WP-7b | MEU-7 Green: `transcript/adapter.py` | WP-7a | `compact_continue` | `avkit_infra/transcript/adapter.py` |
| WP-9a | MEU-9 Red: voices/load/generate | WP-7b | `compact_continue` | `C:/Temp/av-kit/fail-to-pass-meu-9-tts.txt` |
| WP-9b | MEU-9 Green: `tts/adapter.py` + `tts/voices.py` | WP-9a | `compact_continue` | `avkit_infra/tts/` |
| WP-9c | MEU-9 Red: HF download/sideload/offline | WP-9b | `compact_continue` | `C:/Temp/av-kit/fail-to-pass-meu-9-models.txt` |
| WP-9d | MEU-9 Green: `model_manager/{catalog,manager}.py` | WP-9c | `compact_continue` | `avkit_infra/model_manager/` |

## User Review Required

None. Protocol vs Phase 2 prose forks are sourced in Implementation locks (frozen Protocols win). Voice catalog completed from official HF `VOICES.md`. SABR quality shrink belongs to MEU-10 (no SABR field on `DownloadOptions`).

**This section is content for the review loop, NOT a cue to stop now.**

Round-3 High findings were product-scope choices. **USER_EXPLICIT 2026-08-19** selected `ONNX_PREPROCESS` (hybrid) and `CHECK_EXEC_REVIEW` (Python frontmatter parser). Those locks are in this plan.

## Named sets (PR-9 — define once)

| Name | Value | Owner |
|------|-------|-------|
| `ADAPTER_LAYOUT` | `youtube/adapter.py`, `transcript/adapter.py`, `tts/adapter.py`, `tts/voices.py`, `model_manager/manager.py`, `model_manager/catalog.py` | this plan |
| `TTS_ADAPTER_CLASS` | `KokoroAdapter` | Spec layout `tts/adapter.py` comment; `02-infrastructure.md:38` |
| `FROZEN_LAYOUT` | Session 2 `database/`, `filesystem/`, `media/` — do not rewrite | grouping Session 2 |
| `YOUTUBE_PORT_METHODS` | `extract_info`, `extract_video_ids`, `download`, `get_formats`, `check_sabr_status`, `test_cookies`, `ytdlp_version` | frozen `ports/youtube.py` |
| `TRANSCRIPT_PORT_METHODS` | `get_transcript` | frozen `ports/transcript.py` |
| `TTS_PORT_METHODS` | `load_model`, `unload_model`, `generate`, `list_voices`, `get_model_status` | frozen `ports/tts.py` |
| `MODEL_CATALOG_PORT_METHODS` | `download`, `sideload` | frozen `ports/models.py` |
| `COOKIE_MODES` | `none`, `browser`, `file` | `06-gui.md` `downloader.cookie_mode`; `DownloadOptions.mode` |
| `QUALITY_HEIGHT` | `P2160=2160`, `P1440=1440`, `P1080=1080`, `P720=720`, `P480=480`, `P360=360`, `P240=240`, `P144=144` | Spec 359–362; `QualityPreset` |
| `QUALITY_SELECTOR_BEST` | `bestvideo+bestaudio/best` | Spec 360 |
| `QUALITY_SELECTOR_LOWEST` | `worstvideo+worstaudio/worst` | Spec 362 |
| `QUALITY_SELECTOR_HEIGHT` | `bestvideo[height<=N]+bestaudio/best[height<=N]` for each `QUALITY_HEIGHT` N | Spec 361 |
| `AUDIO_FORMAT_SELECTORS` | see Implementation locks (inspiration 994–1004 mapped to `AudioFormat` names) | Local Canon `youtube_downloader.py` |
| `COOKIE_AUDIO_SELECTOR` | `bestaudio[protocol=m3u8_native]/bestaudio[protocol=m3u8]/bestaudio/worst` | inspiration 988–991 |
| `SABR_LOG_NEEDLES` | `require a gvs po token`, `android client sabr formats require`, `ios client sabr formats require` | Spec 370 |
| `SABR_EXTRACTOR_ARGS` | `youtube.player_client=['android','tv','ios']` plus inspiration `player_skip`/`skip` HLS/DASH keys | inspiration 968–977 |
| `COOKIE_EXTRACTOR_ARGS` | `youtube.player_client=['tv','web_safari','web']` | inspiration 961–967 |
| `SABR_PROBE_URL` | `https://www.youtube.com/watch?v=dQw4w9WgXcQ` | inspiration `youtube_downloader.py:4152` |
| `AGE_GATE_NEEDLES` | casefold substrings `sign in to confirm your age`, `age-restricted` | yt-dlp age-gate messages; Research-backed |
| `PROGRESS_MIN_INTERVAL_S` | `0.25` | Spec “time-based throttle”; Research-backed flood cap |
| `SEED_VARIANT_IDS` | `kokoro-pt-fp32`, `kokoro-onnx-fp32`, `kokoro-onnx-fp16`, `kokoro-onnx-int8` | Spec 208–211; Session 2 seed |
| `ENGINE_BY_FORMAT` | `ModelFormat.PyTorch` → `kokoro.KPipeline`/`KModel`; `ModelFormat.ONNX` → `onnxruntime.InferenceSession` **plus** `ONNX_PREPROCESS` (not a second TTS library) | Spec 208–213; Human-approved 2026-08-19 hybrid |
| `ONNX_RUNTIME_DEP` | `onnxruntime>=1.16` (CPU wheel; tests mock). Do **not** add `onnxruntime-gpu` as a required dep. | Research-backed onnxruntime Execution Providers |
| `ONNX_PROVIDERS_AUTO` | CUDA → try `CUDAExecutionProvider` else `CPUExecutionProvider`; MPS/CPU → `CPUExecutionProvider` | onnxruntime EP list; no CoreML requirement |
| `ONNX_VOCAB_FILE` | `hexgrad/Kokoro-82M` `config.json` key `vocab` (phoneme char → int). Sidecar in HF cache — **not** a catalog id and **not** in `HF_FILE_MAP` | [KModel.forward](https://github.com/hexgrad/kokoro/blob/main/kokoro/model.py); v1.0 ONNX card |
| `ONNX_VOICE_FILENAME` | `voices/{voice_id}.pt` from `hexgrad/Kokoro-82M` via `KPipeline.load_single_voice` | [KPipeline.load_single_voice](https://github.com/hexgrad/kokoro/blob/main/kokoro/pipeline.py); Spec 447 |
| `ONNX_PREPROCESS` | see Implementation locks (quiet G2P → vocab ids → style at `len(phonemes)-1` → `session.run`) | Human-approved 2026-08-19; Finding 1 r3 |
| `CHECK_EXEC_REVIEW` | `tools/check_exec_review.py` — parse **first YAML frontmatter only** | Human-approved 2026-08-19; Finding 2 r3 |
| `EXEC_REVIEW_FILE` | `.agent/context/handoffs/2026-08-19-p2-external-adapters-implementation-critical-review.md` | this plan |
| `EXEC_REVIEW_TARGET` | `docs/execution/plans/2026-08-19-p2-external-adapters/implementation-plan.md` | `target_plan` exact match |
| `EXEC_REVIEW_MAX_ROUND` | `6` | execution-review cap |
| `CATALOG_METADATA` | adapter-owned four-row map: id → `{name, format, precision, catalog_size_bytes}` matching Session 2 seed names/sizes — **no DB import** | Spec 208–211; frozen `ModelVariant`; Session 2 `SEED_SIZE_BYTES` |
| `RETRYABLE_TRANSCRIPT_ERRORS` | `RequestBlocked`, `IpBlocked` (HTTP 429 is this library’s `RequestBlocked`, not a `TooManyRequests` class) | [youtube_transcript_api/_errors.py](https://github.com/jdepoix/youtube-transcript-api/blob/master/youtube_transcript_api/_errors.py) |
| `HF_FILE_MAP` | see Implementation locks | Spec 213; HF repos |
| `SIDELOAD_SUFFIXES` | `.pth`, `.onnx` | Spec 443 |
| `VOICE_COUNT` | `54` | Spec 409; HF VOICES.md |
| `KOKORO_VOICE_IDS` | Implementation locks tuple (54 IDs, document order) | [hexgrad/Kokoro-82M VOICES.md](https://huggingface.co/hexgrad/Kokoro-82M/blob/main/VOICES.md) |
| `LANG_BY_PREFIX` | `a=American English`, `b=British English`, `e=Spanish`, `f=French`, `h=Hindi`, `i=Italian`, `j=Japanese`, `p=Brazilian Portuguese`, `z=Mandarin Chinese` | inspiration §1 + HF Chinese section |
| `PLAN_FOLDER` | `docs/execution/plans/2026-08-19-p2-external-adapters` | MEU `execution_plan` (no trailing slash) |
| `PLAN_FOLDER_SLASH` | `docs/execution/plans/2026-08-19-p2-external-adapters/` | phase `"2"` `execution_plans` **additional** entry |
| `SESSION2_PLAN_SLASH` | `docs/execution/plans/2026-08-19-p2-persistence-io/` | must remain in phase `"2"` `execution_plans` |
| `HUB_NEXT_AFTER` | `/create-plan p3-services` | hub Next after this project’s H1-3 |
| `PHASE_ID` | `'2'` | `phases[].id` |
| `HUB_NEXT_FIELD` | the unique `Next: \`...\`` field in `docs/BUILD_PLAN.md` (exactly one match) | Codex r3 F1 pattern |
| `HANDOFF_GLOB` | `.agent/context/handoffs/2026-08-19-p2-external-adapters-MEU-*-handoff.md` | this plan |
| `SCAN_PLACEHOLDER_ARGS` | `rg -n -e TODO -e FIXME -e NotImplementedError -e assert packages/infrastructure/src` | Session 2 minus `SabrDetectedError` (flag-only this session) |
| `SCAN_SOUNDFILE_ARGS` | `rg -n -e soundfile packages/infrastructure/src` | Session 2 scan narrowed |
| `SCAN_CORE_INFRA_ARGS` | `rg -n -e sqlalchemy -e yt_dlp -e fastapi -e youtube_transcript_api -e huggingface_hub -e soundfile -e onnxruntime packages/core/src` | p1 reuse + Finding 1 |
| `SCAN_G36_ARGS` | `rg -n -e pytest.mark.skip -e pytest.mark.xfail -e pytest.skip tests/integration/test_youtube_adapter.py tests/integration/test_transcript_adapter.py tests/integration/test_tts_models.py` | G36 |
| `SCAN_ARCHIVE_ARGS` | `rg -n -e download-archive packages/infrastructure/src/avkit_infra/youtube` | Spec 353 |
| `REFLECTION_MARKERS` | `Friction Log`, `Execution Trace`, `Pattern Extraction`, `Patterns to KEEP`, `Next Session Design Rules`, `RULE-`, `Efficiency Metrics`, `Rule Adherence`, `Instruction Coverage`, `schema: v1`, `sections:`, `loaded:`, `decisive_rules:` | completion-preflight |
| `TEST_YOUTUBE` | `tests/integration/test_youtube_adapter.py` | Spec Testing 510 |
| `TEST_TRANSCRIPT` | `tests/integration/test_transcript_adapter.py` | Spec Testing 511 |
| `TEST_TTS_MODELS` | `tests/integration/test_tts_models.py` | Spec Testing 513 |
| `REGRESSION_TESTS` | `tests/unit/test_domain.py`, `tests/integration/test_sqlite_uow.py`, `tests/integration/test_filesystem_media.py` | Session 1–2 |

`KOKORO_VOICE_IDS` (define once):

```
af_heart, af_alloy, af_aoede, af_bella, af_jessica, af_kore, af_nicole, af_nova, af_river, af_sarah, af_sky,
am_adam, am_echo, am_eric, am_fenrir, am_liam, am_michael, am_onyx, am_puck, am_santa,
bf_alice, bf_emma, bf_isabella, bf_lily, bm_daniel, bm_fable, bm_george, bm_lewis,
jf_alpha, jf_gongitsune, jf_nezumi, jf_tebukuro, jm_kumo,
zf_xiaobei, zf_xiaoni, zf_xiaoxiao, zf_xiaoyi, zm_yunjian, zm_yunxi, zm_yunxia, zm_yunyang,
ef_dora, em_alex, em_santa, ff_siwis, hf_alpha, hf_beta, hm_omega, hm_psi, if_sara, im_nicola,
pf_dora, pm_alex, pm_santa
```

`AUDIO_FORMAT_SELECTORS` (define once; `AudioFormat` name → yt-dlp string):

| `AudioFormat` | Selector |
|---------------|----------|
| `Default` | `bestaudio/best[height<=480]/best` |
| `Lowest` | `worstaudio/bestaudio/best[height<=360]/best` |
| `Best` | `bestaudio/best[height<=720]/best` |
| `LowWebm` | `bestaudio[ext=webm]/bestaudio/best[height<=360]/best` |
| `MediumWebm` | `bestaudio[ext=webm]/bestaudio/best[height<=480]/best` |
| `StandardWebm` | `bestaudio[ext=webm]/bestaudio/best[height<=480]/best` |
| `StandardM4a` | `bestaudio[ext=m4a]/bestaudio/best[height<=480]/best` |
| `StandardMp3` | `bestaudio/best[height<=480]/best` |
| `HighM4a` | `bestaudio[ext=m4a]/bestaudio/best[height<=720]/best` |

When `options.mode` is `browser` or `file`, audio-only uses `COOKIE_AUDIO_SELECTOR` instead of that table (inspiration cookie/HLS lock).

`HF_FILE_MAP` (define once):

| `SEED_VARIANT_IDS` | repo | filename |
|--------------------|------|----------|
| `kokoro-pt-fp32` | `hexgrad/Kokoro-82M` | `kokoro-v1_0.pth` |
| `kokoro-onnx-fp32` | `onnx-community/Kokoro-82M-ONNX` | `onnx/model.onnx` |
| `kokoro-onnx-fp16` | `onnx-community/Kokoro-82M-ONNX` | `onnx/model_fp16.onnx` |
| `kokoro-onnx-int8` | `onnx-community/Kokoro-82M-ONNX` | `onnx/model_quantized.onnx` |

`CATALOG_METADATA` (define once; names/sizes match Session 2 seed; **not** a SQLite read):

| id | name | format | precision | catalog_size_bytes |
|----|------|--------|-----------|-------------------|
| `kokoro-pt-fp32` | PyTorch FP32 | `PyTorch` | `FP32` | `326*1024*1024` |
| `kokoro-onnx-fp32` | ONNX FP32 | `ONNX` | `FP32` | `326*1024*1024` |
| `kokoro-onnx-fp16` | ONNX FP16 | `ONNX` | `FP16` | `163*1024*1024` |
| `kokoro-onnx-int8` | ONNX INT8 | `ONNX` | `INT8` | `87*1024*1024` |

## Implementation locks (planning resolutions)

| Topic | Lock | Source |
|-------|------|--------|
| Frozen Protocols | Implement `YOUTUBE_PORT_METHODS` / `TRANSCRIPT_PORT_METHODS` / `TTS_PORT_METHODS` / `MODEL_CATALOG_PORT_METHODS` **as written**. Do not edit `avkit_core.ports`. | p1 freeze; grouping Session 3; p2 RULE carry-forward |
| `TTSPort.generate` progress | Frozen type is `Callable[[float], None]`. Phase 2 prose `(segment_index, segment_total)` **loses**. Map segment `i` of `n` to finite `i/n` in `[0, 1]`; empty yield → `1.0`. Never invoke with NaN/inf (p2 RULE-1). | frozen `tts.py`; Spec 408; p2 reflection RULE-1 |
| `ModelCatalogPort.download` | Returns `Path`. Does **not** open UoW. Does **not** call `mark_downloaded`. Spec 3-arg `mark_downloaded(id, path, size_bytes)` is superseded by frozen `(variant_id, path)` + Session 2 size-from-stat — **MEU-12** persists. | frozen `models.py`; Session 2 AC-5.18; Spec 442 vs 436 |
| `playlist_end` | Frozen `extract_video_ids(channel_url)` has no end arg. Ctor-inject `YouTubeAdapter(*, playlist_end: int = 0)`. `0` omits yt-dlp `playlistend`; `>0` sets it. Service later reads `transcript.playlist_end`. | Spec 340; frozen Protocol; hexagonal ctor like FFmpeg paths |
| Progress / stop on download | Frozen `download(url, options)` has no callbacks. Ctor-inject `on_progress: Callable[[int, int \| None, float \| None], None] \| None` (bytes, total, speed) and `should_stop: Callable[[], bool] \| None`. | Spec 350–351; frozen `DownloadOptions` |
| `yt_dlp_debug` | Ctor `yt_dlp_debug: bool = False`. When True, forward yt-dlp logger lines as structlog DEBUG module `yt-dlp`. | Spec 354 |
| SABR quality shrink | Adapter maps the `QualityPreset` it is given. Height ≤ 360 / audio-only `StandardMp3`/`HighM4a` under SABR Active is **MEU-10** (no SABR field on `DownloadOptions`). | Spec 348 vs frozen options; grouping Session 4 |
| SABR Passive | Custom logger watches `SABR_LOG_NEEDLES`. Set `DownloadResult.sabr_detected=True`. Do **not** raise `SABRDetectedError`. No DB row. | Spec 370 |
| Client fallback | Cookie `browser`/`file` → `COOKIE_EXTRACTOR_ARGS`; else `SABR_EXTRACTOR_ARGS`. | Spec 374; inspiration 952–977 |
| Cookies in yt-dlp opts | `none` → no cookie keys; `browser` → `cookiesfrombrowser=(browser, profile)`; `file` → `cookiefile=str(path)`. Never persist cookie bytes. Unknown `mode` → `ValidationError` (fail-closed). | Spec 352; `COOKIE_MODES` |
| `test_cookies` | Returns `CookieTestResult` only. Missing file / locked browser → `{ok: False, error_message}`. Do **not** raise `CookieTestError` here. | Spec 378 |
| Download-path cookie failure | Missing/unreadable cookie file during `download` → `CookieTestError` **from** `FileNotFoundError`/`OSError` (p2 RULE-2). | Spec 315; alias `CookieAccessError` |
| Age gate | yt-dlp `DownloadError` whose message casefold-contains an `AGE_GATE_NEEDLES` item → `AgeRestrictedError` from that exception. | Spec 312 |
| Cancel | `should_stop()` True in progress hook → `DownloadCancelledError`. | Spec 351 |
| Unmapped yt-dlp error | Other `DownloadError` → `DomainError` chained (`from e`). Never leak `yt_dlp.utils.DownloadError` across the port. | Spec 308; open-world fail-closed |
| `--download-archive` | Forbidden. Skip is SQLite `download_archive` in MEU-10. `SCAN_ARCHIVE` must be clean. | Spec 353, 475 |
| `get_formats` | Implement (on frozen Protocol; omitted from Phase 2 YouTube prose). Mock `extract_info` → `list[FormatInfo]`. | frozen Protocol; `01-domain-layer.md` |
| `extract_info` | `flat=True` → `PlaylistInfo` unique-preserve `video_ids`; `flat=False` single video → `VideoInfo`. | Spec 331–336 |
| Transcript `None` | `TranscriptsDisabled`, `NoTranscriptFound`, `VideoUnavailable` → `None`. Do **not** raise `TranscriptsDisabledError` / `NoTranscriptFoundError` from `get_transcript`. | Spec 323, 390 |
| Transcript retryable | Catch `RETRYABLE_TRANSCRIPT_ERRORS` only (`RequestBlocked`, `IpBlocked`). HTTP 429 is `RequestBlocked`. Unrecognized → `DomainError` from e. | Spec 391; Finding 6 |
| Transcript unknown | Unrecognized exception → `DomainError` from e (fail-closed; not `None`). | create-plan open-world corollary |
| Transcript title | Frozen `TranscriptResult.title` is non-empty. Phase 2 “title may be empty” **loses**. If fetch has no title, `title = video_id`. | frozen `transcript.py`; Spec 389 |
| Transcript text | Join segments with newlines. **Zero file writes**. No `time.sleep` inside `get_transcript`. | Spec 392, 396, 478 |
| Transcript API | Pin `youtube-transcript-api>=1.0`. Call `YouTubeTranscriptApi().fetch` / `.list` (v1 instance API). Version-floor tests parse `>=` major, never substring `"1"` (p2 RULE-3). | [PyPI 1.1.0](https://pypi.org/project/youtube-transcript-api/1.1.0/) |
| Device Auto | PyTorch: CUDA if `torch.cuda.is_available()` else MPS if `torch.backends.mps.is_available()` else CPU. ONNX: `ONNX_PROVIDERS_AUTO` (CUDA EP else CPU; MPS → CPU). Tests mock torch and onnxruntime. One loaded model; `load_model` another implies unload. | Spec 406; Finding 1 |
| `lang_code` | First character of `voice.voice_id`. Adapter derives it; callers do not pass a raw lang code. | Spec 408, 412 |
| WAV/MP3 | Not Kokoro. `generate` returns `np.ndarray` PCM only. | Spec 414 |
| Missing model file | `ModelLoadError` / `ModelDownloadError` **from** `FileNotFoundError`/`OSError` (p2 RULE-2). | Spec 320–321 |
| Offline download | If `variant.path` is an existing file, or `dest_dir / filename` exists, skip `hf_hub_download`. | Spec 444 |
| Sideload | Scan `models_dir` for `SIDELOAD_SUFFIXES`. Map `.pth` → `kokoro-pt-fp32`; `model.onnx`/`*fp32*.onnx` → `kokoro-onnx-fp32`; `*fp16*.onnx` → `kokoro-onnx-fp16`; `*quantized*.onnx`/`*int8*.onnx` → `kokoro-onnx-int8`. Unknown names skipped (do not invent catalog ids). Return `list[ModelVariant]` with `path` set and `is_downloaded=True` for the service to persist. | Spec 443 |
| Default dest | `~/.avkit/models/` is a service/settings default (MEU-12). Adapter uses the `dest_dir` argument. | Spec 447 |
| No UoW | YouTube/transcript/TTS/model adapters never import `SqlAlchemyUnitOfWork` or open a session. | Session 2 FFmpeg lock; Spec 436 |
| Live network | Default suite mocks `yt_dlp.YoutubeDL`, transcript API, `hf_hub_download`, `kokoro.KPipeline`, `load_single_voice`, and `onnxruntime.InferenceSession`. Do not hit live YouTube/HF. | Spec 515 |
| `uv sync` | After dep adds: `uv sync --all-packages`. Plain `uv sync` uninstalls member deps. | p2 Next Day Outline |
| Types | No `assert` for user-visible failures. | code-quality; Python `-O` |
| Production entrypoints (PR-8) | `YouTubeAdapter.download` / `extract_info` / `test_cookies` / `check_sabr_status`; `TranscriptAdapter.get_transcript`; `KokoroAdapter.generate` / `load_model` / `list_voices`; `ModelCatalogAdapter.download` / `sideload`. Controls are not test-only helpers. | Spec Goal |
| Engine split | `load_model` branches on `variant.format` via `ENGINE_BY_FORMAT`. PyTorch: local `KModel`/`KPipeline` from `variant.path`. ONNX: `onnxruntime.InferenceSession(path, providers=ONNX_PROVIDERS_AUTO)` and **must not** construct `KModel` (no `.pth` load). Every `SEED_VARIANT_IDS` member has a positive mocked load+generate oracle. | Finding 1; Spec 406 + catalog 208–213 |
| `ONNX_PREPROCESS` (generate after ONNX load) | **Human-approved hybrid (2026-08-19).** Do **not** add `kokoro-onnx` / `pykokoro`. Do **not** download onnx-community `voices/*.bin`. Pipeline: (1) quiet `KPipeline(lang_code=voice.voice_id[0], model=False, repo_id='hexgrad/Kokoro-82M')` yields `(graphemes, phonemes, None)` — G2P only, no audio. (2) Load `ONNX_VOCAB_FILE` `vocab` dict (mocked `hf_hub_download` / file read in tests). (3) `input_ids = [vocab[p] for p in phonemes if p in vocab]` (KModel.forward drop-unknown). `len(input_ids) <= 510` else `ValidationError`. Pad `tokens = [[0, *input_ids, 0]]` dtype `int64` shape `(1, <=512)`. (4) `pack = pipeline.load_single_voice(voice.voice_id)` → `ONNX_VOICE_FILENAME`; style = `pack[len(phonemes) - 1]` as `float32` shape `(1, 256)` — **KPipeline.infer** index `len(ps)-1`, not community README `voices[len(tokens)]`. (5) `speed_arr = np.array([speed], dtype=np.float32)` shape `(1,)`. (6) `session.run(None, dict(input_ids=tokens, style=style, speed=speed_arr))[0]` squeezed to 1-D finite PCM (RULE-1). Concatenate chunks. **Zero** WAV writes. Missing `config.json` or `voices/{id}.pt` → `ModelLoadError` from `FileNotFoundError`/`OSError` (RULE-2). Tests mock `KPipeline`, vocab file, `load_single_voice`, and `InferenceSession.run`; they **capture** the adapter-built `session.run` kwargs (must not inject fabricated `input_ids`/`style` inside the test double and skip the adapter). | Human-approved; [KModel.forward](https://github.com/hexgrad/kokoro/blob/main/kokoro/model.py); [KPipeline.infer](https://github.com/hexgrad/kokoro/blob/main/kokoro/pipeline.py); ONNX card `session.run` names; Spec 447 |
| Sideload metadata | `sideload` builds `ModelVariant` from `CATALOG_METADATA` + detected path; `size_bytes` = `path.stat().st_size` when the file exists, else `catalog_size_bytes`. Never import `avkit_infra.database`. | Finding 2; frozen `ModelVariant`; Session 2 size-from-stat |
| Transcript retryable names | Catch only `RETRYABLE_TRANSCRIPT_ERRORS`. Do not reference `TooManyRequests`. | Finding 6 |
| TTS class name | Public class is `TTS_ADAPTER_CLASS` (`KokoroAdapter`). | Finding 7; Spec 38 |
| SCAN_ADAPTER_LIBS | `yt_dlp` only under `youtube/`; `youtube_transcript_api` only under `transcript/`; `kokoro` and `onnxruntime` only under `tts/`; `huggingface_hub` only under `model_manager/`. `soundfile` nowhere in infra src. | Session 2 SCAN_SOUNDFILE split; Finding 1 |

### Control binding (PR-8)

Each control AC names: (1) observable (opts dict captured by mocked `YoutubeDL.__init__`, raised type + `__cause__`, returned DTO fields, callback value list, file-write count, `hf_hub_download` call count); (2) traceable chain from the production method above to that observable; (3) a negative oracle that the happy path cannot also satisfy (live network not required; mocked 429 → retryable; disabled captions → `None` and **zero** files; `--download-archive` key absent; NaN progress not invoked; missing model `__cause__` is `FileNotFoundError`).

Closed enums (`QualityPreset`, `AudioFormat`, `COOKIE_MODES`) are exhaustive at compile/test time — adding a preset without a selector breaks tests. Open-world library exceptions fail closed (`DomainError` / `TranscriptRetryableError` as locked). Adapters have no read-then-write persistence pair (no UoW); filesystem writes for downloads are yt-dlp’s job as observed via returned path.

## Proposed Changes

### MEU-6 `infra-youtube`

#### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---------|-------------|-------------------|-------------------|
| `download(url, DownloadOptions)` | Frozen `DownloadOptions` + adapter preconditions | `COOKIE_MODES`; `QualityPreset`; `AudioFormat`; `output_dir` Path; cookie **paths** only | Unexpected yt-dlp info keys ignored; unknown `mode` → `ValidationError` |
| `test_cookies(mode, browser, profile, cookie_file)` | Frozen signature | Same `COOKIE_MODES`; never cookie bytes in return | Extra kwargs forbidden by Protocol |
| `extract_info` / `extract_video_ids` / `get_formats` | Domain `VideoInfo` / `PlaylistInfo` / `FormatInfo` | Non-empty ids; unique-preserve playlist ids | Extra yt-dlp fields dropped |
| Ctor `playlist_end`, callbacks, `yt_dlp_debug` | Adapter ctor | `playlist_end >= 0`; callbacks optional | Unknown ctor kwargs → TypeError |

No REST/MCP/UI. Invalid mapped values raise existing `ValidationError` / domain errors (not HTTP 422).

#### Acceptance Criteria

| AC | Type | Description | Source | Negative Test |
|----|------|-------------|--------|---------------|
| AC-6.1 | integration | `ADAPTER_LAYOUT` youtube module importable; `avkit-infra` depends on `yt-dlp`; `uv sync --all-packages` used after the add | Spec 329; p2 uv lock | Import fails if dep missing; core still has no `yt_dlp` (`SCAN_CORE_INFRA`) |
| AC-6.2 | integration | Concrete `YouTubeAdapter` methods match `inspect.signature` of frozen `YouTubePort` for `YOUTUBE_PORT_METHODS` | frozen `youtube.py` | Extra Protocol methods or mutated core signatures fail |
| AC-6.3 | integration | Mocked `extract_info` single video → `VideoInfo`; playlist `flat=True` → `PlaylistInfo` with unique-preserve `video_ids` | Spec 331–336 | Duplicate ids collapsed; empty id rejected by domain |
| AC-6.4 | integration | `extract_video_ids` passes `flat_playlist=True`; ctor `playlist_end=0` omits `playlistend`; `playlist_end=3` sets `playlistend=3` | Spec 340 | Negative `playlist_end` rejected |
| AC-6.5 | integration | `get_formats` maps mocked format rows → `list[FormatInfo]` | frozen Protocol | Missing `format_id`/`ext` → `ValidationError` |
| AC-6.6 | integration | Video `QUALITY_SELECTOR_*` land in yt-dlp `format` opt; height presets use `QUALITY_HEIGHT` | Spec 359–362 | A `QualityPreset` without a selector fails the exhaustive table test |
| AC-6.7 | integration | Audio-only uses `AUDIO_FORMAT_SELECTORS`; cookie `browser`/`file` uses `COOKIE_AUDIO_SELECTOR` | inspiration 988–1004 | Cookie mode must not use the non-HLS table string |
| AC-6.8 | integration | Cookie opts: `none` omits cookie keys; `browser` sets `cookiesfrombrowser`; `file` sets `cookiefile` path string — never bytes | Spec 352 | Unknown mode → `ValidationError`; cookie bytes absent from opts and logs |
| AC-6.9 | integration | `should_stop()` True in hook → `DownloadCancelledError`; does not leak `DownloadError` | Spec 351, 308 | Continue-false path still returns `DownloadResult` |
| AC-6.10 | integration | Age-gate `DownloadError` matching `AGE_GATE_NEEDLES` → `AgeRestrictedError` with `__cause__` | Spec 312; RULE-2 | Non-age `DownloadError` is `DomainError`, not `AgeRestrictedError` |
| AC-6.11 | integration | Logger emitting any `SABR_LOG_NEEDLES` string sets `sabr_detected=True`; no `SABRDetectedError`; no DB insert | Spec 370 | Needle-free download has `sabr_detected=False` |
| AC-6.12 | integration | Captured opts contain **no** `download_archive` / `--download-archive` | Spec 353 | `SCAN_ARCHIVE` leftover hits fail |
| AC-6.13 | integration | `test_cookies` missing file / mocked locked browser → `{ok: False, error_message}`; never raises `CookieTestError`; no cookie material in result | Spec 378 | Success path `{ok: True, error_message: None}` |
| AC-6.14 | integration | `check_sabr_status` mocked extract of `SABR_PROBE_URL` → `SABRStatus` with `source=Detected` and `checked_at` set; needle hit → `Active` else `Inactive` | Spec 371 | Must not write SQLite |
| AC-6.15 | integration | `ytdlp_version()` returns mocked version string, or `None` if import/version missing | Spec 430 | Must not shell out to `yt-dlp` CLI |
| AC-6.16 | integration | Cookie mode → `COOKIE_EXTRACTOR_ARGS`; else `SABR_EXTRACTOR_ARGS` | Spec 374 | Android client must not appear when cookies active |
| AC-6.17 | integration | Progress hook skips ticks with non-finite speed; `PROGRESS_MIN_INTERVAL_S` throttle; never calls `on_progress` with NaN | RULE-1; Spec 350 | Unthrottled flood of identical timestamps is not required |
| AC-6.18 | integration | Adapter does not import/open UoW; download-path missing cookie file → `CookieTestError` from `FileNotFoundError` | Session 2; Spec 315; RULE-2 | `FFmpegAdapter` / SQLite files unchanged |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|----------|---------------|------------|
| Format selectors | Spec | Named `QUALITY_*` / `AUDIO_FORMAT_SELECTORS` |
| Cookie HLS audio | Local Canon | inspiration 988–991 → `COOKIE_AUDIO_SELECTOR` |
| `get_formats` omitted in Phase 2 prose | Local Canon | Frozen Protocol wins — implement |
| `playlist_end` / progress callbacks | Local Canon | Ctor injection (hexagonal, Session 2 FFmpeg pattern) |
| SABR quality shrink | Spec + sequencing | Deferred MEU-10 — no SABR field on options |
| Age-gate strings | Research-backed | `AGE_GATE_NEEDLES` |
| SABR probe video | Local Canon | `SABR_PROBE_URL` |
| Boundary | Spec | Paths/mode only; extra yt-dlp keys ignored |

#### Files Modified

| File | Action | Summary |
|------|--------|---------|
| `packages/infrastructure/pyproject.toml` | modify | Add `yt-dlp` (MEU-6); later transcript/kokoro/hf in MEU-7/9 |
| `packages/infrastructure/src/avkit_infra/youtube/__init__.py` | new | Package |
| `packages/infrastructure/src/avkit_infra/youtube/adapter.py` | new | `YouTubeAdapter` |
| `tests/integration/test_youtube_adapter.py` | new | Mocked yt-dlp ACs |

### MEU-7 `infra-transcript`

#### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---------|-------------|-------------------|-------------------|
| `get_transcript(video_id, languages)` | Frozen `TranscriptPort` + `TranscriptResult` | Non-empty `video_id`; `languages` list of str; title fallback `video_id` | Unexpected API keys ignored; extra kwargs forbidden |

#### Acceptance Criteria

| AC | Type | Description | Source | Negative Test |
|----|------|-------------|--------|---------------|
| AC-7.1 | integration | Transcript module importable; dep `youtube-transcript-api>=1.0`; version-floor test parses `>=` major (not `"1" in spec`) | Spec 384; RULE-3 | `>=0.9` must not pass a naive `"1" in spec` check |
| AC-7.2 | integration | `inspect.signature` matches frozen `get_transcript` | frozen `transcript.py` | Core mutation fails `SCAN_CORE_INFRA` / signature test |
| AC-7.3 | integration | Tries `languages` in order, then `en` if not already tried, then any available via `.list` | Spec 388; inspiration §2 | First matching language wins; later languages unused |
| AC-7.4 | integration | `TranscriptsDisabled` / `NoTranscriptFound` / `VideoUnavailable` → `None`; **zero** files written | Spec 323, 390, 392 | Must not raise `TranscriptsDisabledError` / `NoTranscriptFoundError` |
| AC-7.5 | integration | `RETRYABLE_TRANSCRIPT_ERRORS` (`RequestBlocked`, `IpBlocked`) → `TranscriptRetryableError` from the library exception | Spec 391; `_errors.py` | `None` is the wrong mapping for 429/`RequestBlocked` |
| AC-7.6 | integration | Success joins segment texts with newlines; `TranscriptResult.language` is the fetched language; missing title → `video_id` | Spec 389, 392; frozen title | Empty title must not reach the constructor |
| AC-7.7 | integration | No `time.sleep` / rate-limit delay inside `get_transcript`; unrecognized exception → `DomainError` from e | Spec 396; fail-closed | Sleep in adapter fails a source-grep / monkeypatch clock assertion |
| AC-7.8 | integration | No UoW; `youtube_transcript_api` import only under `transcript/` | Session 2; SCAN_ADAPTER_LIBS | Import in `youtube/` or `core` fails the scan |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|----------|---------------|------------|
| None vs typed skip errors | Spec | Frozen `None` wins over error-table raise |
| v1 `.fetch` API | Research-backed | youtube-transcript-api ≥1.0 |
| Title empty vs frozen | Local Canon | Frozen constructor — fallback `video_id` |
| Rate-limit sleep | Spec | Service MEU-11, not adapter |
| Boundary | Spec | video_id + language list only |

#### Files Modified

| File | Action | Summary |
|------|--------|---------|
| `packages/infrastructure/pyproject.toml` | modify | Add `youtube-transcript-api>=1.0` |
| `packages/infrastructure/src/avkit_infra/transcript/__init__.py` | new | Package |
| `packages/infrastructure/src/avkit_infra/transcript/adapter.py` | new | `TranscriptAdapter` |
| `tests/integration/test_transcript_adapter.py` | new | Mocked API ACs |

### MEU-9 `infra-tts-models`

#### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---------|-------------|-------------------|-------------------|
| `generate(text, voice, speed, on_progress)` | Frozen `TTSPort` + `VoiceConfig` + domain speed range | `on_progress` finite `[0,1]`; `lang_code[0]==voice_id[0]` | Extra Kokoro kwargs not forwarded unless named here |
| `load_model(variant, device)` | `ModelVariant` + `DeviceType` | Auto→CUDA/MPS/CPU; missing file chained | Unknown device enum cannot appear (closed `DeviceType`) |
| `download(variant, dest_dir, on_progress)` | Frozen `ModelCatalogPort` | `SEED_VARIANT_IDS` + `HF_FILE_MAP`; finite fraction | Unknown variant id → `ModelDownloadError`; no extra catalog ids |
| `sideload(models_dir)` | Adapter mapper | `SIDELOAD_SUFFIXES` only | Unknown filenames skipped, not inserted as new ids |

#### Acceptance Criteria

| AC | Type | Description | Source | Negative Test |
|----|------|-------------|--------|---------------|
| AC-9.1 | integration | `tts/` + `model_manager/` importable; deps `kokoro`, `huggingface_hub`, `ONNX_RUNTIME_DEP`; no `soundfile`; public TTS class is `KokoroAdapter` | Spec 38, 400, 440, 453 | `SCAN_SOUNDFILE` leftover hits fail; `TTSAdapter` name must not be the public class |
| AC-9.2 | integration | Signatures match frozen `TTS_PORT_METHODS` and `MODEL_CATALOG_PORT_METHODS` | frozen ports | Core mutation fails |
| AC-9.3 | integration | `list_voices()` length is `VOICE_COUNT`; ids exactly `KOKORO_VOICE_IDS`; each `VoiceConfig` satisfies prefix/`LANG_BY_PREFIX`; no DB | Spec 409; HF VOICES.md | 20-voice GUI sample must not be the catalog |
| AC-9.4 | integration | `load_model` uses `ENGINE_BY_FORMAT` for **every** `SEED_VARIANT_IDS` member: PyTorch constructs mocked `KPipeline`/`KModel`; each ONNX id constructs mocked `InferenceSession` with `ONNX_PROVIDERS_AUTO` and must **not** construct `KModel`. Quiet `KPipeline(model=False)` is allowed on the ONNX path for later `ONNX_PREPROCESS` only. `DeviceType.Auto` as locked. Second load unloads first. Missing **weight** file → `ModelLoadError` from `FileNotFoundError` | Spec 406; ENGINE_BY_FORMAT; RULE-2 | A suite that only mocks `KPipeline` while ONNX ids pass is a false pass; `__cause__ is None` fails |
| AC-9.5 | integration | `unload_model` → `get_model_status().is_loaded is False` | Spec 407 | Status must not persist device on `ModelVariant` |
| AC-9.6 | integration | `generate` after PyTorch load iterates mocked loud `KPipeline`; after ONNX load runs `ONNX_PREPROCESS` then mocked `session.run` → finite `ndarray`. Captured run feed **must** include `input_ids`/`style`/`speed` with the locked dtypes/shapes produced by the adapter from mocked phonemes+vocab+pack (example: phonemes `"ab"` and vocab `{a:1,b:2}` → `input_ids == [[0, 1, 2, 0]]`, style index `len("ab")-1`). `on_progress` only finite fractions in `[0,1]`; **zero** audio files written | Spec 408, 414; RULE-1; `ONNX_PREPROCESS` | NaN callback/PCM fails; ONNX generate must not call `KModel`; a test that returns audio from `session.run` without asserting adapter-built inputs is a false pass |
| AC-9.7 | integration | `lang_code` derived from `voice.voice_id[0]` when constructing/using the pipeline | Spec 408, 412 | Passing a mismatched `VoiceConfig` is already a domain error |
| AC-9.8 | integration | `download` calls mocked `hf_hub_download` with `HF_FILE_MAP` repo/filename into `dest_dir`; returns `Path`; `on_progress` finite including a final `1.0`; **does not** call `mark_downloaded` / open UoW | Spec 440–441; frozen port | Extra HF call when dest file exists fails AC-9.9 |
| AC-9.9 | integration | Offline: existing `variant.path` or dest file → skip network (`hf_hub_download` call count 0) | Spec 444 | Missing dest still calls download once |
| AC-9.10 | integration | `sideload` maps `SIDELOAD_SUFFIXES` to `SEED_VARIANT_IDS`; returns full frozen `ModelVariant` from `CATALOG_METADATA` + path + `is_downloaded=True`; `size_bytes` from `stat()` when the file exists else catalog size; unknown names omitted; **no** `avkit_infra.database` import | Spec 443; Finding 2 | A random `.txt` must not become a catalog id; inventing name/format/precision fails the parity test against `CATALOG_METADATA` |
| AC-9.11 | integration | HF/OS failure → `ModelDownloadError` from `OSError`/`FileNotFoundError` | Spec 321; RULE-2 | Bare raise with `__cause__ is None` fails |
| AC-9.12 | integration | `huggingface_hub` only under `model_manager/`; `kokoro` and `onnxruntime` only under `tts/`; Session 2 FFmpeg/SQLite tests still pass | SCAN_ADAPTER_LIBS; grouping | Import in core fails `SCAN_CORE_INFRA` |
| AC-9.13 | integration | Missing `ONNX_VOCAB_FILE` or `ONNX_VOICE_FILENAME` on ONNX generate → `ModelLoadError` from `FileNotFoundError`/`OSError`. `len(input_ids) > 510` → `ValidationError`. Do not fetch onnx-community `voices/*.bin`. Do not add `kokoro-onnx` | RULE-2; Spec 447; Human-approved hybrid | `__cause__ is None` fails; a `.bin` voice download in `HF_FILE_MAP` fails |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|----------|---------------|------------|
| 54 voice IDs | Research-backed | Official `VOICES.md` → `KOKORO_VOICE_IDS` (inspiration sample incomplete) |
| Progress type conflict | Local Canon | Frozen `Callable[[float], None]` wins |
| `mark_downloaded` 3-arg vs 2-arg | Local Canon | Frozen + Session 2; persist in MEU-12 |
| HF filenames | Spec + Research-backed | Spec repos + HF file names in `HF_FILE_MAP` |
| Chinese prefix `z` | Research-backed | HF Mandarin section; `LANG_BY_PREFIX` |
| ONNX vs `KPipeline` | Human-approved + Research-backed | `ONNX_PREPROCESS` hybrid: quiet kokoro G2P + hexgrad vocab/voices + `session.run` (Finding 1 r3) |
| Sideload DTO fields | Local Canon | `CATALOG_METADATA` + `stat()` size; no DB (Finding 2) |
| WAV encode | Spec | Out of this adapter — `MediaPort` |
| Boundary | Spec | `ModelVariant` + dest path; extra HF keys ignored |

#### Files Modified

| File | Action | Summary |
|------|--------|---------|
| `packages/infrastructure/pyproject.toml` | modify | Add `kokoro`, `huggingface_hub`, `onnxruntime>=1.16` |
| `packages/infrastructure/src/avkit_infra/tts/__init__.py` | new | Package |
| `packages/infrastructure/src/avkit_infra/tts/voices.py` | new | `KOKORO_VOICE_IDS` catalog |
| `packages/infrastructure/src/avkit_infra/tts/adapter.py` | new | `KokoroAdapter` implementing `TTSPort` |
| `packages/infrastructure/src/avkit_infra/model_manager/__init__.py` | new | Package |
| `packages/infrastructure/src/avkit_infra/model_manager/catalog.py` | new | `CATALOG_METADATA` (no DB) |
| `packages/infrastructure/src/avkit_infra/model_manager/manager.py` | new | `ModelCatalogAdapter` |
| `tests/integration/test_tts_models.py` | new | Mocked Kokoro + onnxruntime + HF ACs including `ONNX_PREPROCESS` kwargs |
| `tools/check_exec_review.py` | new | First-frontmatter execution-review gate (`CHECK_EXEC_REVIEW`) |

## Out of Scope

| Item | Kind | Deferred-to MEU | Basis |
|------|------|-----------------|-------|
| DownloadService / archive skip / SABR Force-Clear / quality shrink | deferred | MEU-10 | grouping Session 4; Spec 372 Force/Clear not adapter methods; SABR height cap needs session state |
| TranscriptService rate-limit sleeps, file write `raw/{id}.md`, zip | deferred | MEU-11 | Spec 394–396, 478 |
| TTSService / `mark_downloaded` / ModelDownloadRuntime | deferred | MEU-12 | Spec 436, 442; frozen 2-arg mark |
| Settings/health services | deferred | MEU-13 | grouping Session 4 |
| REST / OpenAPI | deferred | MEU-14–16 | `packages/api/` absent |
| MCP | deferred | MEU-17–18 | grouping Session 6 |
| GUI | deferred | MEU-19–23 | no `ui/`; create-plan 4A skip |
| Mutate `avkit_core.ports` | out-of-scope | — | p1 freeze; grouping “do not invent MEU IDs” / no domain-layout changes |
| Rewrite SQLite/UoW / filesystem / FFmpeg | out-of-scope | — | grouping Session 2 complete; this session is 6/7/9 only |
| Live YouTube / Hugging Face in default suite | out-of-scope | — | Spec 515 |
| `ConversionJob` / `ModelFetchJob` | out-of-scope | — | Spec 479 |
| yt-dlp `--download-archive` file SoT | out-of-scope | — | Spec 353, 475 |
| Store transcript text / cookies / tokens | out-of-scope | — | Spec 88, 477 |
| Raise `SABRDetectedError` from adapter | out-of-scope | — | Spec 370 flag-on-result preferred |
| GUI Step 4A | out-of-scope | — | No `ui/` files |
| `tools/validate_closeout_artifacts.py` port | out-of-scope | — | `commands.md` 16–17; marker receipts |
| MEU-13 in this plan (unblocked but not grouped) | out-of-scope | — | grouping Session 3 lock MEU-6,7,9 only |

## BUILD_PLAN.md Audit

This project does **not** rewrite Phase 2–7 contracts. Hub work at execution **task 15 + H1-3** (not a count-only grep):

1. `meu_status.py update MEU-6|MEU-7|MEU-9 <status> --plan PLAN_FOLDER`
2. **Add** `PLAN_FOLDER_SLASH` to phase `"2"` `execution_plans` **without removing** `SESSION2_PLAN_SLASH`
3. Rewrite hub `HUB_NEXT_FIELD` to `HUB_NEXT_AFTER`. Preserve Session 1 **and** Session 2 plan links in the same prose sentence
4. Prove with Verification Plan **§7** (`SSOT_PLAN_BOUND` / `SSOT_READY` / `SSOT_APPROVED`). A YAML substring count of `p2-external-adapters` is **not** a passing oracle

## Verification Plan

Classify every command through [`.agent/docs/output-evidence-policy.md`](../../../.agent/docs/output-evidence-policy.md). `rtk proxy` for these exact-evidence receipts.

### 1. Domain + Session 2 regression

```powershell
rtk proxy uv run pytest tests/unit/test_domain.py tests/integration/test_sqlite_uow.py tests/integration/test_filesystem_media.py -x --tb=short -v *> C:/Temp/av-kit/pytest-regression.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/pytest-regression.txt | Select-Object -Last 40; exit $code
```

### 2. Adapter integration tests

```powershell
rtk proxy uv run pytest tests/integration/test_youtube_adapter.py tests/integration/test_transcript_adapter.py tests/integration/test_tts_models.py -x --tb=short -v *> C:/Temp/av-kit/pytest-adapters.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/pytest-adapters.txt | Select-Object -Last 40; exit $code
```

### 3. Pyright + ruff infrastructure

```powershell
rtk proxy uv run pyright packages/infrastructure/ *> C:/Temp/av-kit/pyright-infra.txt; $code=$LASTEXITCODE; if ($code -ne 0) { Get-Content C:/Temp/av-kit/pyright-infra.txt | Select-Object -Last 40; exit $code }; rtk proxy uv run ruff check packages/infrastructure/ *> C:/Temp/av-kit/ruff-infra.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/ruff-infra.txt | Select-Object -Last 40; exit $code
```

### 4. Named scans (`SCAN_*` owners)

`rg` exit `0` = hits, `1` = no match, `>1` = tool failure. Clean scans treat `1` as PASS; fail on leftover hits or `$code -gt 1`.

```powershell
rtk proxy rg -n -e TODO -e FIXME -e NotImplementedError -e assert packages/infrastructure/src *> C:/Temp/av-kit/anti-placeholder-infra.txt; $code=$LASTEXITCODE; if ($code -gt 1) { Get-Content C:/Temp/av-kit/anti-placeholder-infra.txt; exit $code }; $hits=@(Get-Content C:/Temp/av-kit/anti-placeholder-infra.txt | Where-Object { $_ -and ($_ -notmatch '^\[rtk\]') }); if ($hits.Count -gt 0) { $hits; exit 1 }; 'PASS: SCAN_PLACEHOLDER clean'; exit 0
```

```powershell
rtk proxy rg -n -e soundfile packages/infrastructure/src *> C:/Temp/av-kit/anti-soundfile-infra.txt; $code=$LASTEXITCODE; if ($code -gt 1) { Get-Content C:/Temp/av-kit/anti-soundfile-infra.txt; exit $code }; $hits=@(Get-Content C:/Temp/av-kit/anti-soundfile-infra.txt | Where-Object { $_ -and ($_ -notmatch '^\[rtk\]') }); if ($hits.Count -gt 0) { $hits; exit 1 }; 'PASS: SCAN_SOUNDFILE clean'; exit 0
```

```powershell
rtk proxy rg -n -e sqlalchemy -e yt_dlp -e fastapi -e youtube_transcript_api -e huggingface_hub -e soundfile -e onnxruntime packages/core/src *> C:/Temp/av-kit/anti-infra-core.txt; $code=$LASTEXITCODE; if ($code -gt 1) { Get-Content C:/Temp/av-kit/anti-infra-core.txt; exit $code }; $hits=@(Get-Content C:/Temp/av-kit/anti-infra-core.txt | Where-Object { $_ -and ($_ -notmatch '^\[rtk\]') }); if ($hits.Count -gt 0) { $hits; exit 1 }; 'PASS: SCAN_CORE_INFRA clean'; exit 0
```

```powershell
rtk proxy rg -n -e pytest.mark.skip -e pytest.mark.xfail -e pytest.skip tests/integration/test_youtube_adapter.py tests/integration/test_transcript_adapter.py tests/integration/test_tts_models.py *> C:/Temp/av-kit/g36-skip-scan.txt; $code=$LASTEXITCODE; if ($code -gt 1) { Get-Content C:/Temp/av-kit/g36-skip-scan.txt; exit $code }; $hits=@(Get-Content C:/Temp/av-kit/g36-skip-scan.txt | Where-Object { $_ -and ($_ -notmatch '^\[rtk\]') }); if ($hits.Count -gt 0) { $hits; exit 1 }; 'PASS: SCAN_G36 clean'; exit 0
```

```powershell
rtk proxy rg -n -e download-archive packages/infrastructure/src/avkit_infra/youtube *> C:/Temp/av-kit/anti-archive-youtube.txt; $code=$LASTEXITCODE; if ($code -gt 1) { Get-Content C:/Temp/av-kit/anti-archive-youtube.txt; exit $code }; $hits=@(Get-Content C:/Temp/av-kit/anti-archive-youtube.txt | Where-Object { $_ -and ($_ -notmatch '^\[rtk\]') }); if ($hits.Count -gt 0) { $hits; exit 1 }; 'PASS: SCAN_ARCHIVE clean'; exit 0
```

`SCAN_ADAPTER_LIBS` (libs only in their adapter trees):

```powershell
rtk proxy pwsh -NoProfile -Command { $cases=@(@{pat='yt_dlp'; allow='youtube'}, @{pat='youtube_transcript_api'; allow='transcript'}, @{pat='huggingface_hub'; allow='model_manager'}, @{pat='kokoro'; allow='tts'}, @{pat='onnxruntime'; allow='tts'}); foreach ($c in $cases) { rtk proxy rg -n -e $c.pat packages/infrastructure/src *> C:/Temp/av-kit/scan-lib-$($c.pat).txt; $code=$LASTEXITCODE; if ($code -gt 1) { Get-Content C:/Temp/av-kit/scan-lib-$($c.pat).txt; exit $code }; $hits=@(Get-Content C:/Temp/av-kit/scan-lib-$($c.pat).txt | Where-Object { $_ -and ($_ -notmatch '^\[rtk\]') -and ($_ -notmatch [regex]::Escape($c.allow)) }); if ($hits.Count -gt 0) { $hits; exit 1 } }; 'PASS: SCAN_ADAPTER_LIBS' } *> C:/Temp/av-kit/scan-adapter-libs.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/scan-adapter-libs.txt; exit $code
```

### 5. MEU status render

```powershell
rtk proxy uv run python tools/meu_status.py render --check *> C:/Temp/av-kit/drift-check.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/drift-check.txt; exit $code
```

### 6. Closeout structural receipts (substitute for missing `validate_closeout_artifacts.py`)

Handoff markers (`HANDOFF_GLOB`; expected count 3):

```powershell
rtk proxy pwsh -NoProfile -Command { $files=@(Get-ChildItem -Path '.agent/context/handoffs' -Filter '2026-08-19-p2-external-adapters-MEU-*-handoff.md'); if ($files.Count -ne 3) { Write-Error ('expected 3 handoffs, got '+$files.Count); exit 1 }; foreach ($f in $files) { foreach ($pattern in @('Acceptance Criteria','CACHE BOUNDARY','FAIL_TO_PASS','Changed Files')) { if (-not (Select-String -Path $f.FullName -Pattern $pattern -Quiet)) { Write-Error ('missing '+$pattern+' in '+$f.Name); exit 1 } } }; 'PASS: handoff markers' } *> C:/Temp/av-kit/handoff-check.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/handoff-check.txt; exit $code
```

`PER_MEU_HANDOFF_AC` (Finding 5): each MEU file must contain that MEU’s plan AC-IDs (not a union across the glob).

```powershell
rtk proxy pwsh -NoProfile -Command { $plan='docs/execution/plans/2026-08-19-p2-external-adapters/implementation-plan.md'; $planText=Get-Content $plan -Raw; foreach ($n in @('6','7','9')) { $planAcs=@([regex]::Matches($planText, ('AC-'+$n+'\.[0-9]+')) | ForEach-Object { $_.Value } | Sort-Object -Unique); $file=Join-Path '.agent/context/handoffs' ('2026-08-19-p2-external-adapters-MEU-'+$n+'-handoff.md'); if (-not (Test-Path $file)) { Write-Error ('missing '+$file); exit 1 }; $fileAcs=@([regex]::Matches((Get-Content $file -Raw), ('AC-'+$n+'\.[0-9]+')) | ForEach-Object { $_.Value } | Sort-Object -Unique); $missing=@(Compare-Object $planAcs $fileAcs | Where-Object SideIndicator -eq '<='); if ($missing) { $missing; Write-Error ('MEU-'+$n+' missing ACs'); exit 1 } }; 'PASS: per-MEU AC set' } *> C:/Temp/av-kit/handoff-ac-check.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/handoff-ac-check.txt; exit $code
```

`LATEST_EXEC_VERDICT` (Finding 2 r3 / Human-approved parser): `CHECK_EXEC_REVIEW` reads **only the first YAML frontmatter** of `EXEC_REVIEW_FILE`. Require `review_mode == implementation`, `target_plan == EXEC_REVIEW_TARGET` (exact), `verdict == approved`, `findings_count == 0`, and `round` or `review_round` in `1..EXEC_REVIEW_MAX_ROUND` (if both keys exist they must be equal). Do **not** grep the body for the project slug. Do **not** use last-`^verdict:` / any-match `Select-String`. H1-7 and H2-4 must invoke this same command.

```powershell
rtk proxy uv run python tools/check_exec_review.py --self-test *> C:/Temp/av-kit/exec-review-selftest.txt; $code=$LASTEXITCODE; if ($code -ne 0) { Get-Content C:/Temp/av-kit/exec-review-selftest.txt; exit $code }; rtk proxy uv run python tools/check_exec_review.py --review-file .agent/context/handoffs/2026-08-19-p2-external-adapters-implementation-critical-review.md --expected-mode implementation --expected-target docs/execution/plans/2026-08-19-p2-external-adapters/implementation-plan.md --max-round 6 *> C:/Temp/av-kit/exec-review.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/exec-review-selftest.txt; Get-Content C:/Temp/av-kit/exec-review.txt; exit $code
```

`CHECK_EXEC_REVIEW_PROBES` is the `--self-test` half: wrong `target_plan` with slug only in the body, `approved`+`findings_count: 2`, `review_mode: plan`, and `changes_required` with a body `verdict: approved` must all exit 1. The happy fixture exits 0.

### 7. SSOT oracles (`cond and sys.exit(msg)` — never `raise SystemExit if cond else None`)

**SSOT_PLAN_BOUND** (task 15):

```powershell
rtk proxy uv run python -c "from pathlib import Path; import re; import sys; from tools.meu_status.model import load, get_meu; PLAN='docs/execution/plans/2026-08-19-p2-external-adapters'; SLASH=PLAN+'/'; OLD='docs/execution/plans/2026-08-19-p2-persistence-io/'; NEXT='/create-plan p3-services'; MEUS=('MEU-6','MEU-7','MEU-9'); data=load(); p2=next(p for p in data['phases'] if str(p['id'])=='2'); eps=list(p2.get('execution_plans') or []); SLASH not in eps and sys.exit('phase 2 missing PLAN_FOLDER_SLASH'); OLD not in eps and sys.exit('phase 2 missing SESSION2_PLAN_SLASH'); bad=next((p for p in data['phases'] if str(p['id'])!='2' and SLASH in list(p.get('execution_plans') or [])), None); bad is not None and sys.exit('PLAN_FOLDER_SLASH in phase '+str(bad['id'])); miss=next((k for k in MEUS if get_meu(data,k) is None), None); miss is not None and sys.exit('missing '+miss); wrong=next((k for k in MEUS if get_meu(data,k).get('execution_plan')!=PLAN), None); wrong is not None and sys.exit(wrong+' execution_plan='+str(get_meu(data,wrong).get('execution_plan'))); hub=Path('docs/BUILD_PLAN.md').read_text(encoding='utf-8'); hits=re.findall('Next:\\s+'+chr(96)+'([^'+chr(96)+']+)'+chr(96), hub); len(hits)!=1 and sys.exit('hub Next field count='+str(len(hits))); hits[0]!=NEXT and sys.exit('hub Next='+hits[0]); print('PASS: SSOT_PLAN_BOUND')" *> C:/Temp/av-kit/ssot-plan-bound.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/ssot-plan-bound.txt; exit $code
```

**SSOT_READY** (H1-3): same bound checks plus MEU-6/7/9 `status == ready_for_review`, then `render --check`.

```powershell
rtk proxy uv run python -c "from pathlib import Path; import re; import sys; from tools.meu_status.model import load, get_meu; PLAN='docs/execution/plans/2026-08-19-p2-external-adapters'; SLASH=PLAN+'/'; OLD='docs/execution/plans/2026-08-19-p2-persistence-io/'; NEXT='/create-plan p3-services'; MEUS=('MEU-6','MEU-7','MEU-9'); data=load(); p2=next(p for p in data['phases'] if str(p['id'])=='2'); eps=list(p2.get('execution_plans') or []); SLASH not in eps and sys.exit('phase 2 missing PLAN_FOLDER_SLASH'); OLD not in eps and sys.exit('phase 2 missing SESSION2_PLAN_SLASH'); bad=next((p for p in data['phases'] if str(p['id'])!='2' and SLASH in list(p.get('execution_plans') or [])), None); bad is not None and sys.exit('PLAN_FOLDER_SLASH in phase '+str(bad['id'])); miss=next((k for k in MEUS if get_meu(data,k) is None), None); miss is not None and sys.exit('missing '+miss); wrong=next((k for k in MEUS if get_meu(data,k).get('execution_plan')!=PLAN), None); wrong is not None and sys.exit(wrong+' execution_plan='+str(get_meu(data,wrong).get('execution_plan'))); st=next((k for k in MEUS if get_meu(data,k).get('status')!='ready_for_review'), None); st is not None and sys.exit(st+' status='+str(get_meu(data,st).get('status'))); hub=Path('docs/BUILD_PLAN.md').read_text(encoding='utf-8'); hits=re.findall('Next:\\s+'+chr(96)+'([^'+chr(96)+']+)'+chr(96), hub); len(hits)!=1 and sys.exit('hub Next field count='+str(len(hits))); hits[0]!=NEXT and sys.exit('hub Next='+hits[0]); print('PASS: SSOT_READY')" *> C:/Temp/av-kit/ssot-ready.txt; $code=$LASTEXITCODE; if ($code -ne 0) { Get-Content C:/Temp/av-kit/ssot-ready.txt; exit $code }; rtk proxy uv run python tools/meu_status.py render --check *> C:/Temp/av-kit/drift-check.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/ssot-ready.txt; Get-Content C:/Temp/av-kit/drift-check.txt; exit $code
```

**SSOT_APPROVED** (H2-2): MEU-6/7/9 `status == approved` and `execution_plan == PLAN`, then `meu_status.py render` and `render --check` (Finding 4 — YAML-only update is not enough).

```powershell
rtk proxy uv run python -c "import sys; from tools.meu_status.model import load, get_meu; PLAN='docs/execution/plans/2026-08-19-p2-external-adapters'; MEUS=('MEU-6','MEU-7','MEU-9'); data=load(); miss=next((k for k in MEUS if get_meu(data,k) is None), None); miss is not None and sys.exit('missing '+miss); wrong=next((k for k in MEUS if get_meu(data,k).get('execution_plan')!=PLAN or get_meu(data,k).get('status')!='approved'), None); wrong is not None and sys.exit(wrong+' status='+str(get_meu(data,wrong).get('status'))+' execution_plan='+str(get_meu(data,wrong).get('execution_plan'))); print('PASS: SSOT_APPROVED')" *> C:/Temp/av-kit/ssot-approved.txt; $code=$LASTEXITCODE; if ($code -ne 0) { Get-Content C:/Temp/av-kit/ssot-approved.txt; exit $code }; rtk proxy uv run python tools/meu_status.py render *> C:/Temp/av-kit/meu-render-approved.txt; $code=$LASTEXITCODE; if ($code -ne 0) { Get-Content C:/Temp/av-kit/meu-render-approved.txt; exit $code }; rtk proxy uv run python tools/meu_status.py render --check *> C:/Temp/av-kit/drift-check.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/ssot-approved.txt; Get-Content C:/Temp/av-kit/drift-check.txt; exit $code
```

`CLOSEOUT_GATE` (H2-4 / Finding 4): re-run handoff markers + `PER_MEU_HANDOFF_AC` + `LATEST_EXEC_VERDICT` (`CHECK_EXEC_REVIEW`, not a body grep) + reflection markers + metrics slug + `render --check`.

### N. OpenAPI Drift Check

**Skipped.** `packages/api/` is not created. Basis: Out of Scope → MEU-14–16.

## Open Questions

None remaining. Forks researched and promoted to Implementation locks / sufficiency tables. Round-3 High findings resolved by **USER_EXPLICIT 2026-08-19** choices: hybrid Kokoro ONNX preprocess; `tools/check_exec_review.py`.

| Question | Option | Source | Recommendation |
|----------|--------|--------|----------------|
| 54-voice list incomplete in inspiration | Use official HF `VOICES.md` Name column (54 IDs including Mandarin `z*`) | https://huggingface.co/hexgrad/Kokoro-82M/blob/main/VOICES.md | ✅ promoted to `KOKORO_VOICE_IDS` |
| Phase 2 progress `(i, n)` vs frozen `float` | Frozen `Callable[[float], None]` + finite `i/n` | frozen `tts.py`; p2 RULE-1 | ✅ |
| `mark_downloaded` inside manager | Return `Path`; MEU-12 persists | frozen `ModelCatalogPort`; Session 2 | ✅ |
| SABR height cap in adapter | Service MEU-10 | no SABR field on `DownloadOptions` | ✅ deferred |
| ONNX token/style resources | Hybrid: quiet `KPipeline` + `ONNX_VOCAB_FILE` + hexgrad `voices/*.pt` + `session.run`; no `kokoro-onnx`; no community `.bin` voices | USER_EXPLICIT 2026-08-19; hexgrad `KModel`/`KPipeline`; ONNX card input names | ✅ `ONNX_PREPROCESS` |
| Execution-review approval gate | Parse first YAML frontmatter only via `CHECK_EXEC_REVIEW`; exact `target_plan`; `findings_count==0`; `round`/`review_round` in 1..6 | USER_EXPLICIT 2026-08-19; Session 2 exec review uses `round:` | ✅ |

## Research References

- [yt-dlp Python API](https://github.com/yt-dlp/yt-dlp)
- [youtube-transcript-api v1 fetch](https://pypi.org/project/youtube-transcript-api/1.1.0/)
- [hexgrad/Kokoro-82M VOICES.md](https://huggingface.co/hexgrad/Kokoro-82M/blob/main/VOICES.md)
- [hexgrad/Kokoro-82M `kokoro-v1_0.pth`](https://huggingface.co/hexgrad/Kokoro-82M/blob/main/kokoro-v1_0.pth)
- [hexgrad kokoro `KPipeline` / `KModel` (PyTorch)](https://github.com/hexgrad/kokoro/blob/main/kokoro/pipeline.py)
- [hexgrad `KModel.forward` vocab map + pad-0](https://github.com/hexgrad/kokoro/blob/main/kokoro/model.py)
- [onnx-community/Kokoro-82M-ONNX `session.run` input names](https://huggingface.co/onnx-community/Kokoro-82M-ONNX)
- [onnx-community/Kokoro-82M-v1.0-ONNX (misaki + config.json vocab)](https://huggingface.co/onnx-community/Kokoro-82M-v1.0-ONNX)
- USER_EXPLICIT 2026-08-19: hybrid ONNX preprocess; `tools/check_exec_review.py`
- [onnxruntime Execution Providers](https://onnxruntime.ai/docs/execution-providers/)
- [huggingface_hub `hf_hub_download`](https://huggingface.co/docs/huggingface_hub/guides/download)
- Spec: `docs/build-plan/02-infrastructure.md` §YouTube/Transcript/TTS/Model manager
- Frozen: `packages/core/src/avkit_core/ports/{youtube,transcript,tts,models}.py`
- Local Canon: `_inspiration/_downloader_pseudo_logic.md`, `_inspiration/external_code/yt-dlp_GUI/youtube_downloader.py` 952–1004, `_inspiration/_kokoro_production_settings.md` §1
- Carry-forward: `docs/execution/reflections/2026-08-19-p2-persistence-io-reflection.md` RULE-1–3
- Grouping: Session 3 MEU-6 + MEU-7 + MEU-9 only
- Harness: `.agent/context/harness.local.md` (`plan_to_exec_gate: reviewer-auto`, `fresh_worker: none`)

## Explicit stop conditions

1. Plan-review round cap (3) without `approved` — HARD STOP (`create-plan` §5d).
2. Execution-review round cap (6) without `approved` — HARD STOP.
3. All independent-reviewer rungs unavailable — wait for Mat; never self-review.
4. Human approval required before any `git commit` / push / deploy.
5. Do **not** run product pytest/pyright/ruff **before** this plan is `approved` (GUARDRAILS SIGN 1). Static `Test-Path` / `rg` / `--help` only if a review loop fights about a missing tool.

## TDD / FAIL_TO_PASS

Tests first per slice (WP-6a/c/e, WP-7a, WP-9a/c). Save red receipts under `C:/Temp/av-kit/fail-to-pass-meu-{N}-*.txt`. Do not edit assertions to go green (G36). Red must fail for the AC reason (M5), not collection `ERROR`. Emerging standards in `task.md` row 13: M5, M6, G19, G36.
