# Build Priority Matrix — av-kit

> **Spec source:** `docs/BUILD_PLAN.md` and `docs/build-plan/00-overview.md`–`11-page-layout.md`.
> MEU IDs registered 2026-08-18 via `/session-grouping`. Phase 8 MEU-28–33: 2026-08-24. Phase 9 MEU-34–39: 2026-08-26.
> Phase 10 MEU-41–49: 2026-08-28. Phase 11 MEU-50–58: 2026-09-03. Phase 6 residual MEU-61: 2026-09-20. 2026-09-30 GUI-walkthrough residuals MEU-62–70 (Phases 3/5/6/9/11). 2026-10-09 triage residuals MEU-71–91 (Phases 3/4/7/9/11). 2026-10-17 triage residuals MEU-93–98 (Phases 3/6). 2026-11-03 release candidate residuals MEU-108–112 (Phases 6/7/8/9). 2026-11-04 rc.2 triage residuals MEU-113–126 (Phases 3/6/7/8).
> YAML SSOT: `.agent/context/meu-status.yaml`.
> Each MEU maps to exactly one row below.

## Priority bands

| Band | MEUs | Rule |
|------|------|------|
| P0 | MEU-1–4 | Domain first. No infrastructure until ports exist. |
| P1 | MEU-5–13 | Adapters then services. Never import infra from domain. |
| P2 | MEU-14–125 | API before MCP/GUI. Distribution after GUI shell. Conversion (MEU-28–33) after the YouTube toolkit exists. Capture (MEU-34–40) after Convert. Capture annotation geometry (MEU-59) after the Capture page and native picker. Capture edit-until-Save (MEU-60) after MEU-59. Queue cards (MEU-41–49) after every page exists. Page layout (MEU-50–58) after the queue cards it composes around. Login item (MEU-61) after Settings (MEU-23) and the NSIS installer (MEU-25). 2026-09-30 residuals: TTS runtime assets (MEU-62) before the TTS page residuals (MEU-63/64) and the MCP live audit (MEU-68); Capture toolbar (MEU-65) before zoom (MEU-66); flatten-with-backup (MEU-67) after MEU-60; header toggles (MEU-69) and Settings emphasis (MEU-70) last. 2026-10-17 residuals: shortcut binding (MEU-95) before palette curation (MEU-96) before common shortcuts (MEU-97); path fields (MEU-93) and theme-reactive selects (MEU-94) stand alone; TTS sideload load (MEU-98) after the device fallback (MEU-75). |

## MEU order

| Order | MEU | Slug | Spec section | Depends on |
|:-----:|-----|------|--------------|------------|
| 1.1 | MEU-1 | `domain-scaffold` | [01 §Package layout](01-domain-layer.md#package-layout) | — |
| 1.2 | MEU-2 | `domain-enums-vos` | [01 §Enums](01-domain-layer.md#enums-domainenumspy) + VOs | MEU-1 |
| 1.3 | MEU-3 | `domain-entities` | [01 §Persistable entities](01-domain-layer.md#persistable-entities) | MEU-2 |
| 1.4 | MEU-4 | `domain-ports-errors` | [01 §Ports](01-domain-layer.md#port-protocols) + [errors](01-domain-layer.md#domain-errors-domainerrorspy) | MEU-2, MEU-3 |
| 2.1 | MEU-5 | `infra-sqlite-uow` | [02 §Database](02-infrastructure.md#database) + ORM | MEU-4 |
| 2.2 | MEU-6 | `infra-youtube` | [02 §YouTube adapter](02-infrastructure.md#youtube-adapter-youtubeadapterpy) | MEU-4 |
| 2.3 | MEU-7 | `infra-transcript` | [02 §Transcript adapter](02-infrastructure.md#transcript-adapter-transcriptadapterpy) | MEU-4 |
| 2.4 | MEU-8 | `infra-filesystem-media` | [02 §Filesystem](02-infrastructure.md#filesystem-adapter-filesystemwriterpy) + Media | MEU-4 |
| 2.5 | MEU-9 | `infra-tts-models` | [02 §TTS](02-infrastructure.md#tts-adapter-ttsadapterpy) + Model manager | MEU-4 |
| 3.1 | MEU-10 | `svc-download` | [03 §DownloadService](03-service-layer.md#downloadservice) | MEU-5, MEU-6, MEU-8 |
| 3.2 | MEU-11 | `svc-transcript` | [03 §TranscriptService](03-service-layer.md#transcriptservice) | MEU-5, MEU-6, MEU-7, MEU-8 |
| 3.3 | MEU-12 | `svc-tts-models` | [03 §TTSService](03-service-layer.md#ttsservice) + Prepare + Models | MEU-5, MEU-8, MEU-9 |
| 3.4 | MEU-13 | `svc-settings-health` | [03 §Settings](03-service-layer.md#settingsservice) + Health | MEU-5, MEU-8 |
| 3.5 | MEU-62 | `svc-tts-runtime-assets` | [03 §TTS runtime assets (residual)](03-service-layer.md#tts-runtime-assets-residual) | MEU-16, MEU-22 |
| 3.6 | MEU-73 | `svc-tts-voice-assets` | [03 §TTS voice assets (residual)](03-service-layer.md#tts-voice-assets-residual) | MEU-62 |
| 3.7 | MEU-74 | `svc-tts-language-runtime` | [03 §TTS language runtime (residual)](03-service-layer.md#tts-language-runtime-residual) | MEU-73, MEU-64 |
| 3.8 | MEU-75 | `svc-tts-device-fallback` | [03 §TTS device resolution (residual)](03-service-layer.md#tts-device-resolution-residual) | MEU-62, MEU-63 |
| 3.9 | MEU-77 | `svc-tts-async-generate` | [03 §TTS async generation (residual)](03-service-layer.md#tts-async-generation-residual) | MEU-62, MEU-63, MEU-68, MEU-76 |
| 3.10 | MEU-78 | `svc-ffmpeg-resolver` | [03 §FFmpeg resolution (residual)](03-service-layer.md#ffmpeg-resolution-residual) | MEU-13, MEU-29 |
| 3.11 | MEU-98 | `svc-tts-sideload-load` | [03 §TTS sideload load (residual)](03-service-layer.md#tts-sideload-load-residual) | MEU-12, MEU-75 |
| 3.12 | MEU-115 | `svc-transcript-failure-reason` | [03 §Transcript failure reason (residual)](03-service-layer.md#transcript-failure-reason-residual) | MEU-11, MEU-13, MEU-16, MEU-21, MEU-27 |
| 3.13 | MEU-116 | `svc-transcript-block-stop` | [03 §Transcript block stop (residual)](03-service-layer.md#transcript-block-stop-residual) | MEU-11, MEU-115 |
| 3.14 | MEU-117 | `svc-tts-build-capability` | [03 §TTS build capability (residual)](03-service-layer.md#tts-build-capability-residual) | MEU-72, MEU-75, MEU-98 |
| 3.15 | MEU-119 | `svc-tts-load-keeps-model` | [03 §TTS load keeps the current model (residual)](03-service-layer.md#tts-load-keeps-model-residual) | MEU-62, MEU-75, MEU-98 |
| 3.16 | MEU-121 | `svc-tts-fp16-nonfinite` | [03 §TTS ONNX FP16 audio (residual)](03-service-layer.md#tts-onnx-fp16-audio-residual) | MEU-62, MEU-72, MEU-117 |
| 3.17 | MEU-122 | `svc-transcript-metadata` | [03 §Transcript source metadata (residual)](03-service-layer.md#transcript-source-metadata-residual) | MEU-7, MEU-11 |
| 4.1 | MEU-14 | `api-app-auth` | [04 §App factory](04-rest-api.md#app-factory-and-lifespan) + Auth | MEU-10–13 |
| 4.2 | MEU-15 | `api-downloads-health-settings` | [04 §Downloads](04-rest-api.md#routes--downloads) + Health + Settings | MEU-14 |
| 4.3 | MEU-16 | `api-transcripts-tts-models` | [04 §Transcripts](04-rest-api.md#routes--transcripts) + TTS + Models | MEU-14 |
| 4.4 | MEU-76 | `api-error-surface` | [04 §Unhandled errors (residual)](04-rest-api.md#unhandled-errors-residual) | MEU-14 |
| 5.1 | MEU-17 | `mcp-runtime` | [05 §Runtime](05-mcp-server.md#runtime) | MEU-14 |
| 5.2 | MEU-18 | `mcp-tools` | [05 §Compound tools](05-mcp-server.md#compound-tools) | MEU-17, MEU-15, MEU-16 |
| 5.3 | MEU-68 | `mcp-live-audit` | [05 §MCP live audit (residual)](05-mcp-server.md#mcp-live-audit-residual) | MEU-18, MEU-62 |
| 6.1 | MEU-19 | `gui-shell` | [06 §Startup](06-gui.md#loading--startup-performance-tracked) + IPC | MEU-14 |
| 6.2 | MEU-20 | `gui-downloader` | [06 §Downloader](06-gui.md#downloader-page---default-route) | MEU-19, MEU-15 |
| 6.2a | MEU-26 | `gui-chrome-zorivest` | [06 §Main window](06-gui.md#main-window-layout) + console chrome | MEU-19, MEU-20 |
| 6.2b | MEU-27 | `gui-console-polish` | [06 §Console](06-gui.md#console-panel-right-side-sheet) polish | MEU-26 |
| 6.3 | MEU-21 | `gui-transcript` | [06 §Transcript](06-gui.md#transcript-page-transcript) | MEU-19, MEU-16 |
| 6.4 | MEU-22 | `gui-tts-models` | [06 §TTS](06-gui.md#tts-page-tts) | MEU-19, MEU-16 |
| 6.5 | MEU-23 | `gui-settings-help` | [06 §Settings](06-gui.md#settings-page-settings) + Help + audit | MEU-19–22 |
| 6.6 | MEU-61 | `gui-login-item` | [06 §Startup (login item)](06-gui.md#startup-login-item) | MEU-23, MEU-25 |
| 6.7 | MEU-69 | `gui-header-toggle-state` | [06 §Header toggles (residual)](06-gui.md#header-toggles-residual) | MEU-19, MEU-26 |
| 6.8 | MEU-93 | `gui-path-fields` | [06 §Path fields (residual)](06-gui.md#path-fields-residual) | MEU-33, MEU-22 |
| 6.9 | MEU-94 | `gui-theme-reactive-selects` | [06 §Theme-reactive selects (residual)](06-gui.md#theme-reactive-selects-residual) | MEU-19, MEU-23 |
| 6.10 | MEU-95 | `gui-shortcut-binding` | [06 §Shortcut binding (residual)](06-gui.md#shortcut-binding-residual) | MEU-19, MEU-69 |
| 6.11 | MEU-96 | `gui-command-palette-curation` | [06 §Command palette curation (residual)](06-gui.md#command-palette-curation-residual) | MEU-95, MEU-23 |
| 6.12 | MEU-97 | `gui-common-shortcuts` | [06 §Common shortcuts (residual)](06-gui.md#common-shortcuts-residual) | MEU-95, MEU-96 |
| 6.13 | MEU-108 | `gui-ready-probe-guard` | [06 §Ready probe (residual)](06-gui.md#ready-probe-residual) | MEU-19 |
| 6.14 | MEU-118 | `gui-tts-device-options` | [06 §TTS device options (residual)](06-gui.md#tts-device-options-residual) | MEU-23, MEU-75, MEU-117 |
| 6.15 | MEU-120 | `gui-models-dir-probe` | [06 §Models folder probe (residual)](06-gui.md#models-folder-probe-residual) | MEU-23 |
| 6.16 | MEU-124 | `download-received-quality` | [06 §Downloader received quality (residual)](06-gui.md#download-received-quality-residual) | MEU-10, MEU-20 |
| 6.17 | MEU-126 | `gui-light-accent-contrast` | [06 §Light accent contrast (residual)](06-gui.md#light-accent-contrast-residual) | MEU-26 |
| 7.1 | MEU-24 | `dist-backend` | [07 §Backend packaging](07-distribution.md#backend-packaging-pyinstaller) | MEU-14, MEU-19 |
| 7.2 | MEU-25 | `dist-installer` | [07 §Electron packaging](07-distribution.md#electron-packaging-electron-builder) | MEU-24, MEU-17 |
| 7.3 | MEU-71 | `gui-mcp-setup-prompt` | [07 §MCP setup prompt (residual)](07-distribution.md#mcp-setup-prompt-residual) | MEU-23, MEU-25 |
| 7.4 | MEU-72 | `dist-tts-onnx-runtime` | [07 §Packaged ONNX TTS runtime (residual)](07-distribution.md#packaged-onnx-tts-runtime-residual) | MEU-24, MEU-62 |
| 7.5 | MEU-92 | `dist-mcp-server-bundle` | [07 §MCP server bundle (residual)](07-distribution.md#mcp-server-bundle-residual) | MEU-25, MEU-71 |
| 7.6 | MEU-110 | `dist-release-candidate` | [07 §Release candidate packaging (residual)](07-distribution.md#release-candidate-packaging-residual) | MEU-25, MEU-92 |
| 7.7 | MEU-113 | `dist-fetch-exit-codes` | [07 §Fetch script exit codes (residual)](07-distribution.md#fetch-exit-codes-residual) | MEU-25, MEU-110 |
| 7.8 | MEU-114 | `dist-uninstall-installer-copy` | [07 §Uninstall removes the installer copy (residual)](07-distribution.md#uninstall-installer-copy-residual) | MEU-25 |
| 7.9 | MEU-125 | `dist-release-candidate-2` | [07 §Second release candidate (residual)](07-distribution.md#second-release-candidate-residual) | MEU-110, MEU-113, MEU-114, MEU-115, MEU-116, MEU-117, MEU-118, MEU-119, MEU-120, MEU-121 |
| 8.1 | MEU-28 | `domain-conversion` | [08 §Domain](08-video-conversion.md#domain) | MEU-4 |
| 8.2 | MEU-29 | `infra-conversion` | [08 §Infrastructure](08-video-conversion.md#infrastructure) | MEU-28, MEU-5, MEU-8 |
| 8.3 | MEU-30 | `svc-conversion` | [08 §Service layer](08-video-conversion.md#service-layer) | MEU-29 |
| 8.4 | MEU-31 | `api-conversion` | [08 §REST API](08-video-conversion.md#rest-api) | MEU-30, MEU-14 |
| 8.5 | MEU-32 | `mcp-convert` | [08 §MCP](08-video-conversion.md#mcp) | MEU-31, MEU-17 |
| 8.6 | MEU-33 | `gui-convert` | [08 §Convert Page](08-video-conversion.md#convert-page-convert) | MEU-31, MEU-19, MEU-26 |
| 8.7 | MEU-109 | `convert-output-folder` | [08 §Output folder (residual)](08-video-conversion.md#output-folder-residual) | MEU-29 |
| 8.8 | MEU-112 | `convert-job-gpu-preference` | [08 §Encoder choice per job (residual)](08-video-conversion.md#job-encoder-choice-residual) | MEU-30, MEU-33 |
| 8.9 | MEU-123 | `convert-extract-stream-index` | [08 §Extract stream index (residual)](08-video-conversion.md#extract-stream-index-residual) | MEU-29, MEU-30 |
| 9.1 | MEU-34 | `domain-capture` | [09 §Domain](09-screenshot-capture.md#domain) | MEU-4 |
| 9.2 | MEU-35 | `infra-capture` | [09 §Infrastructure](09-screenshot-capture.md#infrastructure) | MEU-34, MEU-5 |
| 9.3 | MEU-36 | `svc-capture` | [09 §Service layer](09-screenshot-capture.md#service-layer) | MEU-35 |
| 9.4 | MEU-37 | `api-capture` | [09 §REST API](09-screenshot-capture.md#rest-api) | MEU-36, MEU-14 |
| 9.5 | MEU-38 | `mcp-capture` | [09 §MCP](09-screenshot-capture.md#mcp) | MEU-37, MEU-17 |
| 9.6 | MEU-39 | `gui-capture` | [09 §Capture Page](09-screenshot-capture.md#capture-page-capture) | MEU-37, MEU-19, MEU-26 |
| 9.7 | MEU-40 | `native-region-picker` | [09 §Native region picker](09-screenshot-capture.md#native-region-picker-helper-process) | MEU-39 |
| 9.8 | MEU-59 | `gui-capture-annotate-arrow-text` | [09 §Annotation geometry (arrow + text)](09-screenshot-capture.md#annotation-geometry-arrow-text) | MEU-39, MEU-40 |
| 9.9 | MEU-60 | `gui-capture-annotate-edit-until-save` | [09 §Annotation edit until Save](09-screenshot-capture.md#annotation-edit-until-save) | MEU-59 |
| 9.10 | MEU-65 | `gui-capture-toolbar-icons` | [09 §Viewport toolbar icons and Options](09-screenshot-capture.md#viewport-toolbar-icons-and-options) | MEU-57, MEU-60 |
| 9.11 | MEU-66 | `gui-capture-zoom` | [09 §Viewport zoom](09-screenshot-capture.md#viewport-zoom) | MEU-59, MEU-65 |
| 9.12 | MEU-67 | `capture-flatten-backup` | [09 §Flatten with backup](09-screenshot-capture.md#flatten-with-backup) | MEU-38, MEU-60 |
| 9.13 | MEU-80 | `gui-icon-button-hints` | [09 §Icon-button hints](09-screenshot-capture.md#icon-button-hints) | MEU-65, MEU-67 |
| 9.14 | MEU-81 | `gui-capture-action-row` | [09 §Capture action row](09-screenshot-capture.md#capture-action-row) | MEU-80, MEU-67 |
| 9.15 | MEU-82 | `capture-text-baseline` | [09 §Text preview baseline](09-screenshot-capture.md#text-preview-baseline) | MEU-59 |
| 9.16 | MEU-83 | `capture-arrow-geometry` | [09 §Arrow bake geometry](09-screenshot-capture.md#arrow-bake-geometry) | MEU-59, MEU-67 |
| 9.17 | MEU-84 | `capture-file-variant-sync` | [09 §Annotated file sync and Open file](09-screenshot-capture.md#annotated-file-sync-and-open-file) | MEU-39, MEU-67 |
| 9.18 | MEU-85 | `gui-capture-size-scrub` | [09 §Size scrubbing](09-screenshot-capture.md#size-scrubbing) | MEU-65 |
| 9.19 | MEU-86 | `gui-capture-color-swatches` | [09 §Named colour swatches](09-screenshot-capture.md#named-colour-swatches) | MEU-65 |
| 9.20 | MEU-87 | `gui-capture-tool-lock` | [09 §Tool lock](09-screenshot-capture.md#tool-lock) | MEU-60, MEU-65 |
| 9.21 | MEU-88 | `gui-capture-filmstrip-menu` | [09 §Filmstrip context menu](09-screenshot-capture.md#filmstrip-context-menu) | MEU-57 |
| 9.22 | MEU-89 | `gui-capture-filmstrip-multiselect` | [09 §Filmstrip multi-select](09-screenshot-capture.md#filmstrip-multi-select) | MEU-88 |
| 9.23 | MEU-90 | `capture-pixelate-mark` | [09 §Pixelate mark](09-screenshot-capture.md#pixelate-mark) | MEU-59, MEU-67 |
| 9.24 | MEU-91 | `capture-eraser-mark` | [09 §Eraser mark](09-screenshot-capture.md#eraser-mark) | MEU-90 |
| 9.25 | MEU-99 | `gui-capture-history-chords` | [09 §Canvas history chords](09-screenshot-capture.md#canvas-history-chords) | MEU-60, MEU-97 |
| 9.26 | MEU-100 | `gui-capture-resize-handles` | [09 §Resize handles](09-screenshot-capture.md#resize-handles) | MEU-60, MEU-91 |
| 9.27 | MEU-101 | `gui-capture-text-reedit` | [09 §Text re-edit and scaling](09-screenshot-capture.md#text-re-edit-and-scaling) | MEU-82, MEU-100 |
| 9.28 | MEU-102 | `capture-text-multiline` | [09 §Multi-line text](09-screenshot-capture.md#multi-line-text) | MEU-101 |
| 9.29 | MEU-103 | `capture-redact-mark` | [09 §Redact mark](09-screenshot-capture.md#redact-mark) | MEU-91, MEU-100 |
| 9.30 | MEU-104 | `capture-copy-image-actions` | [09 §Copy image and action names](09-screenshot-capture.md#copy-image-and-action-names) | MEU-81, MEU-99 |
| 9.31 | MEU-105 | `gui-capture-style-tool-flow` | [09 §Style and tool flow](09-screenshot-capture.md#style-and-tool-flow) | MEU-87, MEU-99, MEU-100 |
| 9.32 | MEU-106 | `capture-line-ellipse-shapes` | [09 §Line and ellipse](09-screenshot-capture.md#line-and-ellipse) | MEU-100, MEU-105 |
| 9.33 | MEU-107 | `capture-step-mark` | [09 §Step mark](09-screenshot-capture.md#step-mark) | MEU-105 |
| 9.34 | MEU-111 | `mcp-image-fits-stdio` | [05 §Image size limit (residual)](05-mcp-server.md#image-size-limit-residual) | MEU-38 |
| 10.1 | MEU-41 | `canon-queue-cards` | [10 §Scope and non-goals](10-queue-card-ui.md#scope-and-non-goals) | MEU-39 |
| 10.2 | MEU-42 | `svc-requeue-widening` | [10 §Re-queue contract](10-queue-card-ui.md#re-queue-contract) | MEU-41 |
| 10.3 | MEU-43 | `gui-queue-primitives` | [10 §Status token table](10-queue-card-ui.md#status-token-table) | MEU-41 |
| 10.4 | MEU-44 | `gui-queue-card` | [10 §QueueCard anatomy](10-queue-card-ui.md#queuecard-anatomy) | MEU-43 |
| 10.5 | MEU-45 | `gui-convert-queue` | [10 §Toolbar reduction](10-queue-card-ui.md#toolbar-reduction) | MEU-42, MEU-44 |
| 10.6 | MEU-46 | `gui-downloader-queue` | [10 §Primary action model](10-queue-card-ui.md#primary-action-model) | MEU-45 |
| 10.7 | MEU-47 | `gui-queue-bulk` | [10 §Selection and bulk model](10-queue-card-ui.md#selection-and-bulk-model) | MEU-46 |
| 10.8 | MEU-48 | `gui-queue-convergence` | [10 §Supersession of 06-gui.md](10-queue-card-ui.md#supersession-of-06-guimd) | MEU-47 |
| 10.9 | MEU-49 | `gui-queue-dnd` | [10 §Reorder model](10-queue-card-ui.md#reorder-model) | MEU-47 |
| 11.1 | MEU-50 | `canon-page-layout` | [11 §Scope and non-goals](11-page-layout.md#scope-and-non-goals) | MEU-49 |
| 11.2 | MEU-51 | `gui-layout-primitives` | [11 §Shared layout primitives](11-page-layout.md#shared-layout-primitives) | MEU-50 |
| 11.3 | MEU-52 | `gui-queue-header-row` | [11 §Queue header row](11-page-layout.md#queue-header-row) | MEU-51 |
| 11.4 | MEU-53 | `gui-downloader-layout` | [11 §Downloader page layout](11-page-layout.md#downloader-page-layout) | MEU-52 |
| 11.5 | MEU-54 | `gui-convert-layout` | [11 §Convert page layout](11-page-layout.md#convert-page-layout) | MEU-53 |
| 11.6 | MEU-55 | `gui-transcript-layout` | [11 §Transcript page layout](11-page-layout.md#transcript-page-layout) | MEU-52, MEU-49 |
| 11.7 | MEU-56 | `gui-tts-layout` | [11 §TTS page layout](11-page-layout.md#tts-page-layout) | MEU-51 |
| 11.8 | MEU-57 | `gui-capture-layout` | [11 §Capture page layout](11-page-layout.md#capture-page-layout) | MEU-51 |
| 11.9 | MEU-58 | `gui-settings-layout` | [11 §Settings page layout](11-page-layout.md#settings-page-layout) | MEU-51 |
| 11.10 | MEU-63 | `gui-tts-model-manager` | [11 §TTS model manager (residual)](11-page-layout.md#tts-model-manager-residual) | MEU-56, MEU-62 |
| 11.11 | MEU-64 | `gui-tts-text-panel` | [11 §TTS text panel (residual)](11-page-layout.md#tts-text-panel-residual) | MEU-56 |
| 11.12 | MEU-70 | `gui-settings-section-emphasis` | [11 §Settings section emphasis (residual)](11-page-layout.md#settings-section-emphasis-residual) | MEU-58 |
| 11.13 | MEU-79 | `gui-tts-voice-panel-layout` | [11 §TTS voice panel alignment (residual)](11-page-layout.md#tts-voice-panel-alignment-residual) | MEU-63, MEU-75 |

Phase 0 ([00-overview.md](00-overview.md)) is a summary only — no MEU.

**Closed:** MEU-48 `gui-queue-convergence` (10.8) — superseded 2026-09-03 by MEU-55 + MEU-56;
its ACs are inherited there. See
[Phase 11 grouping](../../.agent/context/grouping/2026-09-03-p11-page-layout-session-grouping.md).

Deferred (not rows): SSE, OCR Part 1, multi-file TTS, MCP Guard, Convert timeline / 2-pass / size-target / Downloader→Convert handoff ([08-video-conversion.md](08-video-conversion.md)), Capture window/GIF/upload/macOS ([09-screenshot-capture.md](09-screenshot-capture.md)).

## Companion docs

- Domain entities: [01-domain-layer.md](01-domain-layer.md)
- Architecture: `.agent/docs/architecture.md`
- Testing: `.agent/docs/testing-strategy.md`
- Grouping: `.agent/context/grouping/2026-08-18-build-plan-session-grouping.md`
- Phase 10 grouping: `.agent/context/grouping/2026-08-28-p10-queue-card-ui-session-grouping.md`
- Phase 11 grouping: `.agent/context/grouping/2026-09-03-p11-page-layout-session-grouping.md`
