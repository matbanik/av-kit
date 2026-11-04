---
project: "2026-10-14-tts-engine-runtime"
meus: ["MEU-73", "MEU-74", "MEU-72"]
status: "draft"
template_version: "2.2"
---

# Implementation Plan: TTS engine runtime (Session 32)

> **Project**: `2026-10-14-tts-engine-runtime`
> **Build Plan Section(s)**: [03 §TTS voice assets (residual)](../../../build-plan/03-service-layer.md#tts-voice-assets-residual) (MEU-73), [03 §TTS language runtime (residual)](../../../build-plan/03-service-layer.md#tts-language-runtime-residual) (MEU-74), [07 §Packaged ONNX TTS runtime (residual)](../../../build-plan/07-distribution.md#packaged-onnx-tts-runtime-residual) (MEU-72)
> **Grouping**: [.agent/context/grouping/2026-10-09-triage-residuals-session-grouping.md](../../../../.agent/context/grouping/2026-10-09-triage-residuals-session-grouping.md) §Session 32 (lines 94-101): order MEU-73 → MEU-74 → MEU-72; split flag "yes, candidate".
> **Status**: `draft`
> **Worktree / branch**: `P:/av-kit-wt/tts-engine-runtime`, `claude/s32-tts-engine-runtime`, from `main` @ `7861020`.

## Goal

Make TTS generation work offline, outside a repo checkout, and for every language the app lists, with no GPL code in the TTS runtime:

<!-- goal-anchor -->
> **Goal anchor:** `TTS generates offline in the installed app for every listed language it can honestly support, with no GPL code in the TTS runtime`

`plan_checks.py static` checks that `review-prompt-plan.md` quotes the anchor verbatim, and the review ledger is opened with it (`--goal-anchor`).

**Scope of "no GPL" (D-87, Human-approved 2026-10-14).** The anchor covers the TTS runtime: the frozen backend's Python code and everything it loads in process. The installer also carries FFmpeg (`ffmpeg.exe`/`ffprobe.exe`, P7, used by Convert and downloads). It is a pinned BtbN **GPL** build, because Convert's software fallback uses `libx264`/`libx265`. This plan does not change that build. It makes the distribution honest: `NOTICES` names FFmpeg as a separately shipped GPL-3.0 program with its source location, and the installer carries the build's own `LICENSE.txt` (`INSTALLER_STAGE`). The choice between an LGPL build and Convert's software encoders becomes the follow-up issue `FFMPEG-GPL-BUILD` (Out of Scope).


1. **MEU-73.** Voice packs become a managed asset (`tts_voice_packs`), fetched with the model or by Get, never mid-job. A missing pack is a 409 before any job row. The Settings Dependencies card refreshes when a download settles, and the managed spaCy directory is appended to `sys.path` instead of prepended.
2. **MEU-74.** espeak-ng is detected on the user's machine and reported as a readiness row (`tts_espeak`). `/tts/voices` marks each voice `available` with a `reason`. The TTS page shows unavailable voices disabled with that reason. Generate with an unavailable voice is a 409 before any job row. Japanese and Mandarin stay unavailable (D-70).
3. **MEU-72.** The ONNX path runs av-kit's own G2P and chunker plus onnxruntime, with no `kokoro.KPipeline`, `KModel` or torch import. The frozen backend bundles the G2P stack. A local packaged smoke builds the backend, generates a short WAV through the frozen API, builds the installer, and records whether the shipped MCP entry starts.

Planning found two defects that the grouping did not know about. Both are fixed here because MEU-72's smoke cannot pass without them:

- **Vocabulary/model mismatch on the ONNX path.**
  - The ONNX catalog downloads `onnx-community/Kokoro-82M-ONNX`, which is Kokoro **v0.19**.
  - The vocab comes from `hexgrad/Kokoro-82M` `config.json`, which is **v1.0**, and the voice packs are v1.0 too.
  - The v0.19 tokenizer gives 83 of the 114 v1.0 symbols a different id or none at all. The v1.0 ONNX export matches the v1.0 vocab on every symbol. Receipt: `C:/Temp/av-kit/s32-onnx-vocab-compare.txt`.
  - D-73 switches the ONNX catalog to `onnx-community/Kokoro-82M-v1.0-ONNX` at a pinned revision.
- **GPL code in the default English path.**
  - `misaki.espeak` (used by `KPipeline` for English out-of-dictionary fallback and every non-English voice) imports `phonemizer` (phonemizer-fork, **GPL-3.0-or-later**) and `espeakng_loader`, which loads the espeak-ng DLL (GPL-3.0) in process.
  - D-61 approved "never ship espeak-ng". The same principle excludes phonemizer and the in-process DLL binding (D-71).

## Context Tool Decision

```yaml
context_tool_decision:
  phase: planning
  eligible_tools: []
  decision: not_applicable
  eligibility_basis: "graphify-out/ and graphify-out-research/ absent in the worktree; no headroom on PATH (2026-10-14). Row 0 re-checks before execution (validate-task.ps1 prereq refuses if a graph appears)."
  human_message_reference: null
```

## Harness, driver and reviewer route

- **Driver:** Claude Code (VS Code extension) on Mat's Windows 11 machine, which is local (`.agent/docs/harness-profiles.md`; `.agent/context/harness.local.md` §Claude Code).
  - `native_shell: pwsh`. The Bash tool is Git Bash and is used only for read-only inspection.
  - `fresh_worker`: Agent tool.
  - `plan_to_exec_gate: human`. After the plan review returns `approved`, execution waits for Mat's explicit "proceed" (GUARDRAILS SIGN 1).
- **Cloud/local split does not apply.** The driver OS is the target OS. `cloud-local-collaboration.md` §1 applies the contract only "whenever the driver OS differs from the target OS".
  - Every stage, including `WINDOWS_GATE` and `package-smoke`, runs here, through `validate-task.ps1` and `rtk proxy`, with receipts in `C:/Temp/av-kit/` (AGENTS §RTK).
  - There is no `validate-task.sh`. Session 24, which also ran fully on Windows, is the precedent.
- **Commits:** the agent never commits or pushes on its own (PROFILE; standing user rule).
  - The gate binds to `WORKTREE_IDENTITY` (§Single-statement contracts): `HEAD` plus a hash of the working-tree diff over `GATED_PATHS`. It does not need a commit.
  - Mat commits the reviewed tree from the H2-3 commit draft.
- **Reviewer:** Codex CLI, class `avkit_independent_reviewer` (vendor OpenAI, distinct from the author's vendor, Anthropic), effort `high`.
  - The model comes from the project overlay; no snapshot pin is passed (AGENTS §Dual-Agent Workflow). Session 31's `gpt-6.1-sol` pin was scoped to that plan's loops only (`2026-10-10-gui-polish-residuals/human-review-decision.md:29`).
  - Dispatch: `tools/Invoke-CodexDispatch.ps1 -LoopId … -AuthorVendor anthropic`, with the prompt [review-prompt-plan.md](review-prompt-plan.md).
  - Caps: plan 3 rounds, execution 6 (PROFILE B5).
  - Codex usage is treated as metered unless `codex login status` proves a ChatGPT-plan login (PROFILE B2).
  - If Codex is unauthenticated, review falls to Mat. The author never self-reviews.

## Handoff Set

| MEU | Handoff | Written at |
|-----|---------|-----------|
| MEU-73 | `.agent/context/handoffs/2026-10-14-tts-engine-runtime-MEU-73-handoff.md` | row 4 |
| MEU-74 | `.agent/context/handoffs/2026-10-14-tts-engine-runtime-MEU-74-handoff.md` | row 8 |
| MEU-72 | `.agent/context/handoffs/2026-10-14-tts-engine-runtime-MEU-72-handoff.md` | row 12 |
| plan review | `.agent/context/handoffs/2026-10-14-tts-engine-runtime-plan-critical-review.md` | Codex (verbatim copy) |
| execution review | `.agent/context/handoffs/2026-10-14-tts-engine-runtime-implementation-critical-review.md` | Codex (verbatim copy) |

Each MEU handoff carries its own `evidence.v1` block. The execution review reads all three plus `walkthrough.md`.

## Work Packages and Context Lifecycle

| WP | Rows | MEU | Strategy | Durable output read before the next WP |
|----|------|-----|----------|----------------------------------------|
| WP-0 | 0–1 | — | shared | `walkthrough.md` §Baseline, §Census |
| WP-1 | 2–4 | MEU-73 | shared, then `compact_continue` at row 4 | MEU-73 handoff |
| WP-2 | 5–8 | MEU-74 | shared, then `compact_continue` at row 8 | MEU-74 handoff |
| WP-3 | 9–12 | MEU-72 | shared, then `compact_continue` at row 12 | MEU-72 handoff |
| WP-4 | 13, H1-*, review, H2-* | all | shared / isolated (review) | handoffs, walkthrough, review file |

**Split flag (grouping line 101, D-82).** At row 8 the coordinator records its context use in `walkthrough.md` §Split. If it is above about 50%, WP-3 onward runs as **Session 32b** in a fresh session. That session reads `task.md`, this plan and the MEU-73/74 handoffs first. Nothing else changes: the same plan, task table, gate and review loop. A 32b split is not a new plan.

## User Review Required

> [!IMPORTANT]
> These are the decisions Mat sees at the human execution gate. They are content for the review loop, not a stop.

1. **D-71: no GPL code in process.**
   - Non-English G2P (Spanish, French, Hindi, Italian, Brazilian Portuguese) calls the user-installed `espeak-ng` **command-line program** as a subprocess. It does not load the espeak-ng DLL through `phonemizer`/`espeakng_loader` the way kokoro/misaki do.
   - The shipped app never imports `phonemizer`, `espeakng_loader` or `misaki.espeak`, and PyInstaller excludes them.
   - This is stricter than D-61, which flagged the in-process binding as a grey area. The cost is two ported mapping tables (`ESPEAK_MAP`: `MULTI_E2M` from misaki's `EspeakG2P` for the non-English languages, and `EN_E2M` from `EspeakFallback` for the English fallback, Apache-2.0, attributed) and a subprocess per segment.
2. **D-76: num2words (LGPL-2.1) ships in the bundle.**
   - misaki's English G2P imports it to spell numbers.
   - It is collected as plain `.py` source (PyInstaller `module_collection_mode`), so a user can replace it, and it is listed in a new `packaging/THIRD_PARTY_NOTICES.md`.
   - The alternative is to strip number expansion, which reads "42" as nothing.
3. **D-73: the ONNX catalog switches to Kokoro v1.0.**
   - Previously downloaded ONNX files under `{models_dir}/onnx/` (v0.19) are ignored, not deleted. That holds everywhere a path can come from: the directory scan, the database row a v0.19 download persisted, `POST /models/load`, and the download fast path (`LEGACY_ONNX_PATH`). Users download the ONNX variant once more (87–326 MB); until they do, the variant shows as not downloaded and a load is refused with a re-download message.
   - This fixes wrong pronunciation on every ONNX run (the 83-symbol vocab mismatch).
4. **D-70: Japanese and Mandarin voices stay listed but unavailable** (Human-approved 2026-10-14). A follow-up issue tracks the `misaki[ja]`/`[zh]` extras.
5. **LOCAL-ESPEAK is optional.**
   - espeak-ng is **not installed** on this machine (2026-10-14: not on PATH, no `C:\Program Files\eSpeak NG`).
   - Unit tests prove the CLI contract with a fake runner. One live check (a Spanish WAV through the real `espeak-ng`) runs only if Mat installs espeak-ng 1.52 before row 13.
   - If he does not, the MEU-74 handoff and the reflection record the live CLI path as unverified, and a follow-up issue is opened (Stop condition S5 governs a live mismatch).
6. **D-87: FFmpeg stays a GPL build in this session** (Human-approved 2026-10-14, "Scope anchor + notice"). The goal anchor is scoped to the TTS runtime. FFmpeg is disclosed in `NOTICES` with its licence text and source location, and `FFMPEG-GPL-BUILD` is filed for the LGPL-or-encoders decision.
7. **The offline smoke denies network through the process environment, not the OS firewall** (D-88). `OFFLINE_SMOKE` points every proxy variable at a dead local port and proves the denial with `NEGATIVE_PROBE`. It covers every HTTP client in the frozen stack that honours proxy variables (requests, httpx, urllib, pip). A raw-socket client would not be covered; none is known in the bundle. A firewall rule would need an elevated shell on every gate run.

## Single-statement contracts

Each name below is defined once, here. Rows, ACs and scripts refer to it by name.

| Name | Contract | Source |
|------|----------|--------|
| `ONNX_REPO` | `onnx-community/Kokoro-82M-v1.0-ONNX` at `ONNX_REVISION` = `1939ad2a8e416c0acfeecc08a694d14ef25f2231`. Files: `onnx/model.onnx` (fp32), `onnx/model_fp16.onnx`, `onnx/model_quantized.onnx` (int8). | D-73; receipts `s32-hf-onnx10.json`, `s32-onnx-vocab-compare.txt` |
| `ONNX_LOCAL_DIR` | `{tts.models_directory}/kokoro-v1.0-onnx/`, the Hugging Face `local_dir` for the ONNX weights and voice packs. | D-73 |
| `LEGACY_ONNX_DIR` | `{tts.models_directory}/onnx/`, where MEU-24/62 stored v0.19 weights. Sideload skips `*.onnx` directly under it and logs `model.legacy_onnx_ignored` once per scan. It never deletes. | D-73 |
| `LEGACY_ONNX_PATH` | A persisted path is legacy when `is_legacy_onnx_path(path, models_dir)` (pure, in `avkit_core.domain.tts`) is true: the suffix is `.onnx` and the parent is exactly `LEGACY_ONNX_DIR`. It is applied at every place a v0.19 path can re-enter:<br>• `ModelService.list_available` reports such a row as `is_downloaded=False`; the database `path` is unchanged.<br>• `ModelService.load` refuses it before the TTS port is called: `ConflictError("model variant <id> needs a re-download (v0.19 file)")`, HTTP 409 (`LEGACY_MODEL_409`). No load is attempted and the loaded state does not change.<br>• `ModelCatalogAdapter.download` skips its `variant.path` fast path for a legacy path and fetches into `ONNX_LOCAL_DIR` at `ONNX_REVISION`. The existing `_run_download` → `mark_downloaded(variant.id, path)` then replaces the row's path.<br>• The legacy file is never opened for writing, moved or deleted. Its bytes are unchanged after list, load and download.<br>Every ONNX local path comes from one helper, `variant_local_path(variant_id, models_dir)` in `avkit_infra.tts.voices`. | D-73; round-1 F2 |
| `VOICE_PACK` | `{ONNX_LOCAL_DIR}/voices/<voice_id>.bin`: raw little-endian float32 of exactly `510*256*4 = 522 240` bytes, read as a `(510, 256)` array. | D-74; README of `ONNX_REPO`; receipt `s32-hf-onnx10.json` (55 `voices/*.bin`) |
| `VOICE_PACKS_READY` | Every voice in the catalog (`VOICE_COUNT` = 54) has a `VOICE_PACK` of exactly 522 240 bytes. Otherwise `missing`. | D-74 |
| `VOICE_PACK_DOWNLOAD` | For each catalog voice whose pack is not exactly 522 240 bytes: `hf_hub_download(ONNX_REPO, "voices/<id>.bin", revision=ONNX_REVISION, local_dir=ONNX_LOCAL_DIR)`, then a size check. A wrong size deletes the file and raises `ModelDownloadError` naming the voice. Progress is `done/total` over the voices it fetches, and it is monotonic. Only `model_manager` imports `huggingface_hub` (AC-9.12); `TtsAssetAdapter` receives the fetch by injection. | 03 §TTS voice assets "Voice packs managed"; D-74 |
| `MODEL_CHAINS_PACKS` | After a variant download succeeds, `ModelService` downloads `tts_voice_packs` in the same runtime when it is missing. The runtime stays `Downloading` with `asset = tts_voice_packs`. If the pack download fails, the variant stays downloaded and the runtime goes to `Failed` with an error naming the asset. | 03 §TTS voice assets ("or with the model"); D-74 |
| `ASSET_409_ORDER` | `TtsService.generate` checks in this order: input validation → model loaded (existing 409) → voice known (existing 422) → `VOICE_AVAILABLE_409` → the `required_tts_assets` 409 (`tts asset missing: <wire>`) → job row. No job row exists after any 409. | 03 §TTS voice assets, §TTS language runtime; MEU-62 `ASSET_MISSING_ERROR` |
| `VOICE_AVAILABLE_409` | `ConflictError("voice unavailable: <voice_id> (<reason>)")`, where `<reason>` is a `VOICE_REASON`. | 03 §TTS language runtime "Voice availability" |
| `VOICE_REASON` | A closed set of two values: `espeak_missing` for lang codes e/f/h/i/p when `ESPEAK_DETECT` reports unavailable, and `language_unsupported` for lang codes j/z always (D-70). a/b are always available. The wire is `Literal["espeak_missing","language_unsupported"] \| None`. | D-70, D-81 |
| `ESPEAK_DETECT` | `EspeakCliAdapter.status()` re-probes on every call, in order: `shutil.which("espeak-ng")`, then `%ProgramFiles%\eSpeak NG\espeak-ng.exe`, then `%ProgramFiles(x86)%\eSpeak NG\espeak-ng.exe`. The version is the first stdout line of `<exe> --version` (timeout 5 s), cached per `(path, mtime_ns)`. A failing `--version` means `available=False`. It returns `EspeakStatus(available, version, path)`. There is no setting for a custom path (Out of Scope). | 03 §TTS language runtime "Detect"; D-77; FFmpeg precedent `media/adapter.py:211-223` (minus the latch) |
| `ESPEAK_G2P` | `EspeakCliAdapter.phonemize(text, lang_code)`. The voice is chosen by `ESPEAK_VOICE` = `{e: "es", f: "fr-fr", h: "hi", i: "it", p: "pt-br", a: "en-us", b: "en-gb"}`. The text is split into segments at punctuation `;:,.!?¡¿—…"«»“”()` and each segment runs `[exe, "-q", "--ipa", "--tie=^", "-v", <voice>, "--stdin"]` with the text on **stdin** (never argv), UTF-8, a 30 s timeout and `CREATE_NO_WINDOW`. Language-switch flags `(xx)` are stripped. Each segment's output then goes through the `ESPEAK_MAP` mapping for its language: `MULTI_E2M` for `e/f/h/i/p`, `EN_E2M` only for the English fallback. The punctuation is then re-joined, with `«` `»` re-joined as `“` `”`, as upstream does (`espeak.py:89`). A nonzero exit or timeout raises `TtsRuntimeError("espeak-ng failed: …")`. | D-71; misaki `espeak.py` (Apache-2.0); espeak-ng(1) `--ipa`, `--tie`, `--stdin` |
| `ESPEAK_MAP` | Two mappings ported from misaki 0.9.4 `espeak.py` (Apache-2.0, attributed). They are never mixed, and each keeps its upstream post-processing at misaki's `version=None`, which is what kokoro 0.9.4 passes (`kokoro/pipeline.py:108,134`):<br>• `MULTI_E2M`, for `e/f/h/i/p`, is `EspeakG2P`'s default `e2m` (`espeak.py:71-85`): `a^ɪ`→`I`, `a^ʊ`→`W`, `d^z`→`ʣ`, `d^ʒ`→`ʤ`, `e^ɪ`→`A`, `o^ʊ`→`O`, `ə^ʊ`→`Q`, `s^s`→`S`, `t^s`→`ʦ`, `t^ʃ`→`ʧ`, `ɔ^ɪ`→`Y`, applied in sorted key order. Then `^` and `-` are removed (`espeak.py:96-104`). Plain `e`, `r`, `x` and the combining nasal tilde U+0303 are left unchanged. The `version == '2.0'` nasal-vowel table is not ported.<br>• `EN_E2M`, for the English fallback only, is `EspeakFallback.E2M` (`espeak.py:14-29`), applied longest key first. Then come the steps in `espeak.py:49-58`:<br>&nbsp;&nbsp;– `(\S)U+0329` → `ᵊ\1`, and any remaining U+0329 is removed;<br>&nbsp;&nbsp;– US: `o^ʊ`→`O`, `ɜːɹ`→`ɜɹ`, `ɜː`→`ɜɹ`, `ɪə`→`iə`, and `ː` is removed;<br>&nbsp;&nbsp;– British: `e^ə`→`ɛː`, `iə`→`ɪə`, `ə^ʊ`→`Q`;<br>&nbsp;&nbsp;– then `o`→`ɔ`, `ɾ`→`T`, `ʔ`→`t`, and `^` is removed.<br>• `ESPEAK_EN_FALLBACK(british)` is the callable handed to `misaki.en.G2P(fallback=…)`. It runs `ESPEAK_G2P` with `en-us` or `en-gb` and `EN_E2M`, and returns `(ps, 2)`, or `(None, None)` when the output is empty, as `EspeakFallback.__call__` does.<br>• `ESPEAK_MAP_PARITY`: a unit test reads the installed `misaki/espeak.py` as text and never imports it. It locates the file through `importlib.util.find_spec("misaki").submodule_search_locations` and parses it with `ast`. It asserts that `MULTI_E2M` equals the default `self.e2m` dict literal in `EspeakG2P.__init__`, and that `EN_E2M` equals the `E2M` dict literal in `EspeakFallback`. | D-71; misaki 0.9.4 `espeak.py:14-58,71-107`; kokoro 0.9.4 `pipeline.py:108,134` |
| `G2P_ROUTE` | `KokoroG2p.phonemize(text, lang_code)`:<br>• a/b go to `misaki.en.G2P(trf=False, british=(lang_code=="b"), fallback=<ESPEAK_G2P for a/b when available, else None>, unk="")`, built lazily and cached per `british` flag through an injectable `misaki_factory` (default: the real class).<br>• Before the first construction it checks `spacy.util.is_package("en_core_web_sm")`. If that is false, it raises `ConflictError("tts asset missing: tts_spacy_model")`, so misaki's own `spacy.cli.download` (a network install, `misaki/en.py` 0.9.4 `G2P.__init__`) is never reached.<br>• e/f/h/i/p go to `ESPEAK_G2P`.<br>• j/z raise `ValidationError` (unreachable behind `VOICE_AVAILABLE_409`). | D-71, D-72 |
| `G2P_SEAM` | Every Python test that drives `KokoroAdapter.generate` reaches phonemes through one fixture, `tts_g2p_seam`, in `tests/tts_g2p_fakes.py` (new). Until row 10 it patches `avkit_infra.tts.adapter.KPipeline` with the existing `FakeKPipeline`; from row 10 it injects a `FakeG2p` through `KokoroAdapter(g2p=…)`. Test bodies written in rows 2 and 5 do not change when the fixture switches. | TA-2, TA-3b |
| `CHUNK_RULE` | `split_phonemes(ps, limit=510)` returns non-empty chunks of at most 510 symbols each, in order, whose concatenation (minus trimmed boundary spaces) equals `ps`. It cuts at the last sentence end `.!?` before the limit, else the last clause mark `,;:—…`, else the last space, else hard at 510. Text is first split into sentences so each G2P call stays short. The existing `MAX_ONNX_INPUT_IDS` guard in `_onnx_chunk` stays as a defence. | Local Canon `adapter.py:228-229` (`MAX_ONNX_INPUT_IDS` = 510, the model's limit); kokoro `KPipeline` waterfall (Apache-2.0) as the behaviour reference; D-78 |
| `ONNX_FEEDS` | `input_ids` int64 `[[0, *ids, 0]]` (ids from the vocab, unknown symbols dropped); `style` float32 `(1, 256)` = `pack[min(len(ids), 510) - 1]` (row 0 when ids is empty); `speed` float32 `[speed]`. | Existing `_onnx_chunk` (adapter.py:217-249); README of `ONNX_REPO` |
| `TORCH_PATH` | The PyTorch variant uses the same `G2P_ROUTE`, `CHUNK_RULE` and `VOICE_PACK`. It imports `KModel` lazily inside `load_model` and calls `kmodel(ps, torch.from_numpy(pack[len(ps)-1]).unsqueeze(0).to(device), speed)`. `KPipeline` is never imported. The style index differs from `ONNX_FEEDS` on purpose, because each path copies its upstream reference: kokoro `KPipeline` indexes by phoneme-string length, and the `ONNX_REPO` README by token count after unknown symbols are dropped. The two agree whenever every symbol is in the vocab. The MEU-72 handoff records the difference. | D-75 |
| `IMPORT_HYGIENE` | In a fresh interpreter with `sys.modules["torch"]`, `["kokoro"]`, `["phonemizer"]` and `["espeakng_loader"]` set to `None`, so any import attempt fails loudly, the test imports `avkit_infra.tts.adapter` and the **real** `misaki.en` module. It then runs an English and a Spanish ONNX generate through `KokoroG2p`, with the `misaki_factory` faked (no spaCy model needed), a fake session and a fake espeak runner. Afterwards `torch`, `kokoro`, `phonemizer`, `espeakng_loader` and `misaki.espeak` are absent from `sys.modules` (or still `None`). | D-71; 07 §Packaged ONNX "No torch", "ONNX without torch" |
| `SPEC_BUNDLE` | `packaging/avkit-backend.spec`:<br>• `excludes` ⊇ `torch, torchvision, torchaudio, kokoro, phonemizer, espeakng_loader, misaki.espeak`.<br>• hiddenimports ⊇ `misaki.en, misaki.token, num2words, spacy, onnxruntime, avkit_infra.tts.g2p, avkit_infra.tts.espeak`, plus `collect_submodules("num2words")`.<br>• datas ⊇ `collect_data_files("misaki")`.<br>• `module_collection_mode={"num2words": "py"}`.<br>• No Kokoro weights, voice packs, spaCy model, CUDA or espeak-ng in the bundle. | 07 §Packaged ONNX "Bundle"; 07:312; D-61; D-76 |
| `NOTICES` | `packaging/THIRD_PARTY_NOTICES.md` lists six components, each with its licence and upstream URL:<br>• misaki (Apache-2.0, including the two ported `ESPEAK_MAP` tables).<br>• num2words (LGPL-2.1), with how to replace the collected `.py` source and the full LGPL-2.1 text copied from the package's `COPYING`.<br>• spaCy (MIT).<br>• onnxruntime (MIT).<br>• The kokoro model weights (Apache-2.0, downloaded, not shipped).<br>• FFmpeg: a separately shipped GPL-3.0 program (`resources/ffmpeg/ffmpeg.exe`, `ffprobe.exe`), the BtbN build `n8.1.2-44-g7c533d0f86` that `tools/fetch_ffmpeg_windows.ps1` pins, run as a subprocess and never linked. The entry gives the source location (`https://github.com/FFmpeg/FFmpeg/tree/n8.1.2` and the build scripts at `https://github.com/BtbN/FFmpeg-Builds`) and points at the `resources/ffmpeg/LICENSE.txt` that ships next to the binaries (D-87).<br>It states that espeak-ng is not shipped. `ui/electron-builder.yml` `extraResources` copies it to `resources/THIRD_PARTY_NOTICES.md`. | D-76, D-87 |
| `PACKAGE_SMOKE` | `validate-task.ps1 -Check package-smoke` runs three steps in this order:<br>(A) `ONLINE_PROVISION`.<br>(B) `INSTALLER_STAGE`.<br>(C) `OFFLINE_SMOKE`, against the backend copied out of the staged installer tree.<br>It merges their results, with `WORKTREE_IDENTITY` at start and end, into `package-smoke-result.json`. The check passes only if all three pass. `tools/smoke_packaged_tts.py` implements (A) as `--phase online` and (C) as `--phase offline`. The script itself runs through `uv run python`, but the backend it drives is the frozen exe. | 07 §Packaged ONNX "Smoke"; D-79; round-1 F3 |
| `ONLINE_PROVISION` | `smoke_packaged_tts.py --phase online --models-dir C:/Temp/av-kit/s32-smoke-models --out C:/Temp/av-kit/s32-smoke-online.json`. Network is allowed; this phase only fills the model cache.<br>(1) Build the backend with `tools/package_backend.py`, never with `--stub-ok`. The smoke refuses an `avkit-backend.exe` under 1 MB.<br>(2) Assert `packaging/dist/avkit-backend/_internal` has no `torch`, `kokoro`, `phonemizer` or `espeakng_loader` directory (`forbidden_dirs`).<br>(3) Start `avkit-backend.exe --port 0 --app-data <tmp>` and read `AVKIT_READY`.<br>(4) Point `tts.models_directory` at `SMOKE_MODELS` = `C:/Temp/av-kit/s32-smoke-models`, which is cached across attempts.<br>(5) Download `kokoro-onnx-int8`, `tts_onnx_vocab`, `tts_spacy_model` and `tts_voice_packs` through the frozen API.<br>(6) Stop the backend. No generate runs in this phase. | 07 §Packaged ONNX "Smoke"; round-1 F3 |
| `OFFLINE_SMOKE` | `smoke_packaged_tts.py --phase offline --backend-dir C:/Temp/av-kit/s32-smoke-run/avkit-backend --models-dir C:/Temp/av-kit/s32-smoke-models --out C:/Temp/av-kit/s32-smoke-offline.json`.<br>• **Copy.** `validate-task.ps1` first deletes `C:/Temp/av-kit/s32-smoke-run/` and copies `ui/dist/win-unpacked/resources/avkit-backend` there. The binary under test is the one the installer packs, outside the checkout.<br>• **Fresh process.** It starts a new process with cwd `C:/Temp/av-kit/s32-smoke-run`, a fresh empty `--app-data`, and fresh empty `HF_HOME` and `XDG_CACHE_HOME` directories under it.<br>• **Network denied.** `HTTP_PROXY`, `HTTPS_PROXY`, `ALL_PROXY` and their lower-case forms are set to `http://127.0.0.1:9`, and `NO_PROXY`/`no_proxy` to `127.0.0.1,localhost`. `HF_HUB_OFFLINE` is **not** set, so the denial is tested rather than assumed.<br>• **Generate.** It points `tts.models_directory` at `SMOKE_MODELS`, loads `kokoro-onnx-int8` on CPU, generates "Hello from av-kit." with `af_heart` at speed 1.0, polls to `Completed`, and requires a WAV with more than 8 000 samples.<br>• **Probe.** It then runs `NEGATIVE_PROBE` and stops the backend.<br>• **Result.** It records `offline: {passed, wav_samples, negative_probe: {state, error}, backend_dir, cwd, proxy}`. | 07 §Packaged ONNX "Smoke"; D-88; round-1 F3 |
| `NEGATIVE_PROBE` | In the same offline process, after the generate: set `tts.models_directory` to a fresh empty `C:/Temp/av-kit/s32-smoke-run/probe-models`, `POST /models/download {"asset":"tts_voice_packs"}`, and poll `GET /models/download-runtime` (60 s cap). It passes only when the runtime reaches `Failed` with a non-empty error. If the runtime ends `Idle` with packs ready, traffic got out and the smoke fails. Settings are restored to `SMOKE_MODELS` afterwards. | D-88; round-1 F3 |
| `INSTALLER_STAGE` | After `ONLINE_PROVISION` passes, the same check runs `tools/fetch_ffmpeg_windows.ps1` when any of `packaging/ffmpeg-win64/ffmpeg.exe`, `ffprobe.exe` or `LICENSE.txt` is missing. The fetch copies the archive's `LICENSE.txt` and exits 6 if the archive has none. The check then runs `npm --prefix mcp-server run build`, `npm --prefix ui run dist` (its receipt is the build receipt), and `docs/execution/plans/2026-08-24-p7-distribution/assert-nsis-pack.ps1 -BuildReceipt <that receipt>` (the 500 MB `SIZE_CAP_BYTES`). It asserts two staged files, and `windows-gate-check` requires both results `true`:<br>• `ui/dist/win-unpacked/resources/THIRD_PARTY_NOTICES.md` exists and names FFmpeg and GPL-3.0 (`installer.notices_staged`).<br>• `ui/dist/win-unpacked/resources/ffmpeg/LICENSE.txt` exists and is non-empty (`installer.ffmpeg_license_staged`).<br>It then records `MCP_ENTRY_PROBE`: `node ui/dist/win-unpacked/resources/mcp-server/index.js` gets one MCP `initialize` JSON-RPC line on stdin; the result is `started` if a JSON-RPC reply arrives within 10 s, else `unreachable` with the exit code and stderr tail. **`MCP_ENTRY_PROBE` is recorded, not a pass condition.** | 07 §Packaged ONNX "Smoke"; `MCP-PACKAGED-ENTRY-UNREACHABLE` (candidate); D-87 |
| `WORKTREE_IDENTITY` | sha256 over, in order: `git rev-parse HEAD`; `git diff HEAD --binary -- <GATED_PATHS>`; for each path in `git ls-files --others --exclude-standard -- <GATED_PATHS>` sorted, `path` + sha256 of its bytes. `windows-gate`, `package-smoke` and `windows-gate-check` compute it the same way: one implementation, `gate_lib.py identity`, called by `Get-WorktreeIdentity` in `validate-task.ps1`. | D-79; cloud-local §3 code identity, adapted to no-commit |
| `GATED_PATHS` | The executable copy is `$gated` in `validate-task.ps1`, and `plan_checks.py static` asserts it equals this list: `ui packages mcp-server tests tools packaging pyproject.toml uv.lock openapi.committed.json docs/build-plan docs/proposals .agent/docs .agent/schemas .agent/roles .agent/templates .agent/skills .agent/workflows .agent/model-registry.local.json .agent/model-registry.local.yaml docs/execution/plans/2026-10-14-tts-engine-runtime/validate-task.ps1 docs/execution/plans/2026-10-14-tts-engine-runtime/gate_lib.py`. This is Session 30's list (`2026-10-02-capture-flatten-backup/implementation-plan.md:174`) plus `packaging` and the runner's parser `gate_lib.py`, widened to all of `docs/build-plan` (the hub row edits it before the gate). **Excluded:** `.agent/context/**`, `docs/BUILD_PLAN.md`, `docs/execution/metrics.md` and this plan's markdown. These are SSOT or closeout records; `post-review-state` re-runs the doc-reading suites after its edits. | cloud-local §3.4 |
| `COUNT_FLOORS` | Amended under Stop condition S1 (walkthrough §Execution amendments): the branch was fast-forwarded to `c72fc44`, which merges Session 31 (gate `2026-10-10-gui-polish-residuals/windows-gate-result.json`, tested `0cfa40a`: 775 / 131 / 629, measured before Session 30 merged) onto Session 30 (`2026-10-02-capture-flatten-backup`, `81fdda7`: 773 / 133 / 655). Floors are the larger of those and the merged tree measured at `c72fc44` before any MEU-73 product change: Vitest `numTotalTests` ≥ 800 with `numFailedTests` 0; Playwright `stats.expected` ≥ 137 with `unexpected` 0 and `flaky` 0; pytest passed ≥ 655 with failed 0. The executable copies are literals in `validate-task.ps1` `windows-gate-check`, and `plan_checks.py static` asserts they equal 800 / 137 / 655. | cloud-local §3.3 |
| `PRODUCT_SCOPE` | Every changed or untracked file under `ui`, `packages`, `mcp-server`, `tests`, `tools`, `packaging`, `openapi.committed.json` or `uv.lock` (from `git diff <baseline.sha> --name-only` plus `git ls-files --others --exclude-standard`, so a commit Mat makes mid-session does not hide a file) appears by exact path in a Files Modified table of this plan. Each Files Modified row names exactly one path, with no brace or glob patterns, and `plan_checks.py static` refuses a row that does. `validate-task.ps1 -Check api-scope` enforces it. | Local Canon (scope fence) |
| `NEW_TESTIDS` | `tts-espeak-row`, `tts-espeak-guidance`, `voice-unavailable-reason`. They are registered in `ui/tests/e2e/test-ids.ts`. | 06-gui; AGENTS §GUI test ids |

### TEST_AMENDMENTS

These are existing assertions whose expectation this plan changes. Each change is source-backed and minimal, and `ta-check` fences it to the named file:line ranges. Row 1's census confirms or extends this list. A hit not listed here is either `unaffected` (with the reason) or a `new-contradiction`, which triggers S2.

"Applied at row" is the Red row that edits the assertion. Each amendment lands together with the new tests of the same MEU, so the Green row that follows makes both pass.

| TA | File:lines | Today | After | Applied at row | Basis |
|----|-----------|-------|-------|----------------|-------|
| TA-1 | `tests/integration/test_tts_models.py:64-69` | `HF_FILE_MAP_EXPECTED` ONNX rows point at `onnx-community/Kokoro-82M-ONNX` | `ONNX_REPO` paths, plus `ONNX_REVISION` and `ONNX_LOCAL_DIR` asserted on the download call. The catalog sizes (lines 43-61) stay the same: they are display-only (`manager.py:23`), and the v1.0 files are within about 1% of them (receipt `s32-hf-onnx10-sizes.json`). | 2 | D-73 |
| TA-2 | `tests/integration/test_tts_models.py:226-285, 495-505, 525-540, 670-691` | `FakeKPipeline` patched over `avkit_infra.tts.adapter.KPipeline`; asserts its kwargs (`lang_code`, `model=False`, `repo_id`), `.pt` voice errors through `raise_voice`, and the 511-symbol limit | Same AC ids (AC-9.x) and the same observables, reached through `G2P_SEAM`. The kwargs test becomes "the G2P receives `lang_code` `b` for `bf_alice`". The voice error case deletes the tmp `VOICE_PACK` instead of setting `raise_voice` and still expects `ModelLoadError` caused by `FileNotFoundError`. The 511-symbol case expects `CHUNK_RULE` (two chunks, two `session.run` calls) instead of `ValidationError`, because the new chunker cuts what `KPipeline` used to hand over in one piece. | 9 (voice error case at row 2) | D-75; `KPipeline` removed under the 07 rule "ONNX without torch"; D-78 |
| TA-3a | `tests/integration/test_tts_assets.py:597-611` | The failed-job console case forces failure with `FakeKPipeline.raise_voice = FileNotFoundError("voices/am_eric.pt")` (a lazy fetch) | Failure is forced by a `FakeSession.run` that raises `RuntimeError`. A missing pack is now AC-73.4's 409, so it cannot produce a failed job row. | 2 | TTS-VOICE-PACK-LAZY-FETCH; AC-73.4 |
| TA-3b | `tests/integration/test_tts_assets.py:25, 556-582, 770-839` | Imports `FakeKPipeline`; counts `FakeKPipeline.calls`; `test_ac_62_16_pipeline_result_objects_carry_phonemes_and_audio` checks the `KPipeline.Result` shape | Call counts on the `G2P_SEAM` fake. The Result-shape test is deleted because its subject, `_chunk_part`, is deleted with `KPipeline`; the MEU-72 handoff lists the deletion. Its intent (the model receives real phoneme ids, not pad tokens only) moves to AC-72.4 `ONNX_FEEDS`. | 9 | D-75 |
| TA-4 | `tests/e2e/test_api_health_settings.py:49-50`, `tests/e2e/test_api_auth.py:63-64`, `tests/e2e/api_fakes.py` | `DependencyHealth(...)` with two asset fields | Gains `tts_voice_packs` (row 2) and `tts_espeak` (row 5) | 2, 5 | AC-73.7, AC-74.5 |
| TA-5 | `ui/tests/unit/settings-page.test.ts:763-764, 836-837` | Two asset rows in the fixture | The fixture gains `tts_voice_packs` (row 2) and `tts_espeak` (row 5). The absent-rows case also asserts that `tts-asset-row-tts_voice_packs` is absent. | 2, 5 | AC-73.11, AC-74.7 |
| TA-6 | `mcp-server/tests/models-assets.test.ts:30` | `it.each` over two wires | Three wires | 2 | AC-73.13 |
| TA-7 | `tests/unit/test_tts_voice_fixture.py`, `ui/tests/e2e/fixtures/tts-voices.json` | Fixture rows equal catalog rows (4 fields) | Rows gain `available`/`reason` (the catalog default is `true`/`null`) | 5 | AC-74.3 |
| TA-8 | `tests/integration/test_tts_assets.py:669-691` | `sys.path.count(...) == 1` after activation; the position is not asserted | The count assertion is unchanged; AC-73.12 adds the position assertion in a new test | 2 | TTS-SPACY-SYSPATH-PREPEND |
| TA-9 | `tests/integration/test_tts_assets.py:568-582` | `test_ac_62_9` uses `jf_alpha` as the "no spaCy needed" voice and expects its generate without `chunk` to return 201 | The voice becomes `ef_dora`, a non-English voice that is still available when espeak is present. The test body monkeypatches `EspeakCliAdapter.status` (imported inside the test) to report available. The 409 and 201 expectations are unchanged. A `j` voice can no longer pass, because `VOICE_AVAILABLE_409` refuses it first. | 5 | D-70; `ASSET_409_ORDER` |
| TA-10 | `tests/integration/test_tts_models.py:590-595` | `test_ac_9_9` expects the offline fast path to find an ONNX file at `{models_dir}/onnx/model.onnx` | The file is placed at `variant_local_path("kokoro-onnx-fp32", tmp_path)` (under `ONNX_LOCAL_DIR`), and the "no `hf_hub_download` call" assertion is unchanged. A file at the old place is now `LEGACY_ONNX_PATH` and must not short-circuit. | 2 | D-73 |
| TA-11 | `tests/integration/test_tts_assets.py:244-255` | `TtsAsset` has exactly two values, and `required_tts_assets` returns `(ONNX_VOCAB, SPACY_MODEL)` or `(ONNX_VOCAB,)` | The value list gains `tts_voice_packs` last (`tts_onnx_vocab`, `tts_spacy_model`, `tts_voice_packs`). Each expected tuple adds `VOICE_PACKS` in declaration order: `(ONNX_VOCAB, SPACY_MODEL, VOICE_PACKS)` and `(ONNX_VOCAB, VOICE_PACKS)`. The validation case at 256-257 is unchanged. | 2 | AC-73.1 |
| TA-12 | `tests/integration/test_tts_assets.py:163-171` | The `Stack.put_weights` helper writes ONNX weights to `{models_dir}/<HF filename>`, which is `LEGACY_ONNX_DIR` for ONNX ids | The path comes from `variant_local_path(variant_id, self.models_dir)`, so the helper seeds the place a real download writes. The `mark_downloaded` setup is unchanged. | 2 | D-73 |
| TA-13 | `tests/integration/test_tts_models.py:604-608` | `test_ac_9_10` sideloads the three ONNX files from `{tmp}/onnx/` | The three files go under `{tmp}/kokoro-v1.0-onnx/onnx/`. Every assertion is unchanged; AC-73.9 covers the files left in `{tmp}/onnx/`. | 2 | D-73 |
| TA-14 | `tests/e2e/test_api_tts_models.py:156-161` | `test_ac_16_7` asserts the first `/tts/voices` row equals exactly `{voice_id, language, gender, style_description}` | The expected dict gains `"available": True, "reason": None` (`am_eric` is lang `a`, always available). The facade call count, the `lang_code` ban and the route source scans are unchanged. | 5 | D-95; AC-74.3 |

`tests/integration/test_tts_models.py:692-693` scans `model_manager/catalog.py` for `voices/` and `.bin`. It is unaffected because `VOICE_PACK_DOWNLOAD` lives in the new `model_manager/voice_packs.py` and `catalog.py` is not modified. Row 1 records this as `unaffected`.

`tests/integration/test_sqlite_uow.py:828-840` persists ONNX paths straight under `tmp_path`, below the repository layer, which `LEGACY_ONNX_PATH` does not touch. It is unaffected.

Five renderer and MCP tests build voice rows without `available` or `reason`: `ui/tests/unit/voice-combobox.test.tsx:20-30`, `ui/tests/unit/tts-page.behavior.test.ts:43-45`, `ui/tests/unit/tts-page.test.ts:245-251`, `ui/tests/e2e/tts-generate.test.ts:167` and `mcp-server/tests/tools-parity.test.ts:126` (receipt `census-s32-voice-rows.txt`). They are unaffected because the renderer `VoiceOut` declares both fields optional, and an absent field means available (MEU-74 Files Modified, `tts-voices.ts`). AC-74.3 still requires the API to send both fields on every row.

`ta-check` fences only lines an amendment removes or changes; added lines are allowed. A new helper call such as `_load_ready_variant` also writing `VOICE_PACK` files is therefore an addition, not an amendment. The Red row's handoff lists every added helper line.

### Environment-bound census

| Item | Bound to | Handling |
|------|----------|----------|
| `ONLINE_PROVISION` downloads (about 87 + 28 + 12 MB) | network to huggingface.co and github.com | It is cached in `SMOKE_MODELS`. A network failure is a `[B]` external blocker with its receipt, never a pass. |
| `OFFLINE_SMOKE` | no network, by construction (dead proxy, `NEGATIVE_PROBE`) | Runs every attempt. A proxy-ignoring raw socket would escape the denial (D-88); the handoff states this residual. |
| `LOCAL-ESPEAK` | espeak-ng installed on Mat's machine | Optional (User Review item 5). Absent means the handoff records it as unverified. |
| Real-model ONNX regression | a downloaded `kokoro-onnx-int8` | Covered only by `PACKAGE_SMOKE`. pytest uses fake sessions, so the suite stays offline. |
| Electron E2E | Mat's desktop session | It runs in `windows-gate` with `ELECTRON_RUN_AS_NODE` cleared (memory: electron-run-as-node). |

## Proposed Changes

### MEU-73 — TTS voice assets

#### Boundary Inventory

| Boundary | Change | Wire / schema | Contract test |
|----------|--------|---------------|---------------|
| `POST /models/download` | accepts `{asset: "tts_voice_packs"}` | `TtsAssetWire` gains `"tts_voice_packs"` | AC-73.7 |
| `GET /health/dependencies` | new row | `tts_voice_packs: TtsAssetOut` (`available`, `version: null`, `state`) | AC-73.7 |
| `POST /tts/generate` | 409 `tts asset missing: tts_voice_packs` before any job row | existing error envelope | AC-73.4 |
| `GET /models/download-runtime` | `asset` may be `tts_voice_packs` during `MODEL_CHAINS_PACKS` | existing field, new value | AC-73.6 |
| MCP `avkit_models.download_asset` | enum gains `tts_voice_packs` | `TTS_ASSET_WIRES` | AC-73.13 |
| Hugging Face | weights and packs from `ONNX_REPO` at `ONNX_REVISION` | — | AC-73.8 |
| `sys.path` | managed spaCy dir appended | — | AC-73.12 |

#### Acceptance Criteria

| AC | Description | Source | Type | Test |
|----|-------------|--------|------|------|
| AC-73.1 | `TtsAsset.VOICE_PACKS = "tts_voice_packs"`, declared last (after `SPACY_MODEL`). `required_tts_assets` returns it for both formats and every lang code, in declaration order: `(ONNX_VOCAB, SPACY_MODEL, VOICE_PACKS)` when spaCy is needed, `(ONNX_VOCAB, VOICE_PACKS)` otherwise (TA-11). | Spec 03 "Voice packs managed" | unit | `tests/unit/test_tts_voice_packs_service.py` |
| AC-73.2 | `TtsAssetAdapter.state(VOICE_PACKS)` follows `VOICE_PACKS_READY`. All 54 packs at 522 240 bytes → `ready`. One missing, or one at 522 239 bytes → `missing`. | Spec 03; D-74 | integration | `tests/integration/test_tts_voice_packs.py` |
| AC-73.3 | `download(VOICE_PACKS)` follows `VOICE_PACK_DOWNLOAD`. It fetches only the packs that are missing or the wrong size, passes `revision=ONNX_REVISION`, reports monotonic progress ending at 1.0, and on a wrong-size file deletes it and raises `ModelDownloadError` naming the voice. A fake fetch is injected and `huggingface_hub` is never imported by `avkit_infra.tts`. | Spec 03; AC-9.12 | integration | `tests/integration/test_tts_voice_packs.py` |
| AC-73.4 | `generate` with a missing pack raises `ConflictError("tts asset missing: tts_voice_packs")` (HTTP 409) and leaves no job row (`ASSET_409_ORDER`). | Spec 03 "Voice packs managed"; MEU-62 | unit | `tests/unit/test_tts_voice_packs_service.py` |
| AC-73.5 | The adapter reads the style row from `VOICE_PACK` (`ONNX_FEEDS`). With `huggingface_hub.hf_hub_download` patched to raise, generate still yields finite samples (no mid-run fetch). | Spec 03; TTS-VOICE-PACK-LAZY-FETCH | integration | `tests/integration/test_tts_voice_packs.py` |
| AC-73.6 | `MODEL_CHAINS_PACKS`. A variant download with packs missing makes the runtime report `asset=tts_voice_packs` while `Downloading` and ends `Idle` with packs ready. With packs present, no pack fetch happens. A pack failure leaves the variant downloaded and the runtime `Failed` with an error naming `tts_voice_packs`. | Spec 03 ("or with the model"); D-74 | unit | `tests/unit/test_tts_voice_packs_service.py` |
| AC-73.7 | The API contract: `POST /models/download {"asset":"tts_voice_packs"}` → 202; `GET /health/dependencies` has `tts_voice_packs` with `state` ∈ {ready, missing, downloading}; an unknown asset → 422. | Spec 03; Boundary Input Contract | integration | `tests/e2e/test_api_tts_runtime.py` |
| AC-73.8 | `HF_FILE_MAP` ONNX rows use `ONNX_REPO` and the download passes `revision=ONNX_REVISION` with `local_dir=ONNX_LOCAL_DIR`. The PyTorch row is unchanged. | D-73 | unit | `tests/integration/test_tts_models.py` (TA-1) |
| AC-73.9 | Sideload ignores `LEGACY_ONNX_DIR/*.onnx` and logs `model.legacy_onnx_ignored`. It finds `ONNX_LOCAL_DIR/onnx/model_quantized.onnx` as `kokoro-onnx-int8`, and a user-sideloaded `D:/x/model_fp16.onnx` elsewhere under the models dir still maps. | D-73 | integration | `tests/integration/test_tts_voice_packs.py` |
| AC-73.10 | Settings refresh: when the download runtime goes from `Downloading` to anything else, `SettingsPage` invalidates `['health','dependencies']` exactly once, through a shared hook `useRefreshDependenciesOnSettle` in `useTtsJob.ts`. It does not refetch on steady `Idle`. | Spec 03 "Settings refresh"; D-43; D-28 | integration | `ui/tests/unit/settings-tts-runtime.test.ts` |
| AC-73.11 | The Settings Dependencies card shows `tts-asset-row-tts_voice_packs` labelled "Voice packs" with the Get button when it is missing; Get posts `{asset:"tts_voice_packs"}`. | Spec 03; MEU-62 asset row precedent | integration | `ui/tests/unit/settings-tts-runtime.test.ts` |
| AC-73.12 | `activate_spacy_dir` **appends**: after activation the install dir is `sys.path[-1]`, entries already present keep their order, and a second call is a no-op. | Spec 03 "spaCy path" | unit | `tests/integration/test_tts_assets.py` (new test) |
| AC-73.13 | MCP `TTS_ASSET_WIRES` includes `tts_voice_packs`, and the `download_asset` schema accepts it and still rejects an unknown wire. | Spec 03 (parity); D-84 | unit | `mcp-server/tests/models-assets.test.ts` (TA-6) |
| AC-73.14 | `openapi.committed.json` regenerated; `export_openapi.py --check` passes. | G8 | integration | gate stage `openapi` |
| AC-73.15 | `LEGACY_ONNX_PATH` on an upgraded database. A real SQLite file is created through the normal migrations, and `kokoro-onnx-int8` is marked downloaded at `{models_dir}/onnx/model_quantized.onnx`, the way v0.19 left it. Then:<br>• `GET /models` shows that variant `is_downloaded: false`.<br>• `POST /models/load` returns 409 `model variant kokoro-onnx-int8 needs a re-download (v0.19 file)`, and the fake TTS port records no `load_model` call.<br>• The legacy file's sha256 is unchanged.<br>`is_legacy_onnx_path` is also table-tested: legacy dir `.onnx` is true; `ONNX_LOCAL_DIR/onnx/*.onnx`, a `.pth` and a sideload elsewhere are false. | D-73; round-1 F2 | integration | `tests/integration/test_tts_voice_packs.py` |
| AC-73.16 | Re-download over a legacy row. With the AC-73.15 database and `hf_hub_download` faked, `POST /models/download {"variant_id":"kokoro-onnx-int8"}` calls the fetch once with `repo_id=ONNX_REPO`, `revision=ONNX_REVISION` and `local_dir=ONNX_LOCAL_DIR` (no fast-path return). Afterwards the row's path is `variant_local_path("kokoro-onnx-int8", models_dir)`, `GET /models` shows `is_downloaded: true`, a load passes the legacy check, and the legacy file's sha256 is unchanged. | D-73; round-1 F2 | integration | `tests/integration/test_tts_voice_packs.py` |

#### Spec Sufficiency

| Question | Answer | Source |
|----------|--------|--------|
| Which file is a "voice pack"? | `voices/<id>.bin` from `ONNX_REPO` (raw float32 of 510×256), the same data as hexgrad's `.pt` without torch | D-74; README |
| Per voice or all at once? | All 54 at once (about 28 MB), with the model or by Get | D-74 |
| Where is it stored? | `ONNX_LOCAL_DIR/voices/` | D-73 |

#### Files Modified (MEU-73)

| File | Action | What |
|------|--------|------|
| `packages/core/src/avkit_core/domain/tts.py` | modify | `TtsAsset.VOICE_PACKS`; `required_tts_assets`; `is_legacy_onnx_path` (`LEGACY_ONNX_PATH`) |
| `packages/core/src/avkit_core/domain/health.py` | modify | `DependencyHealth.tts_voice_packs` |
| `packages/core/src/avkit_core/services/models.py` | modify | `MODEL_CHAINS_PACKS`; `LEGACY_ONNX_PATH` in `list_available` and `load` |
| `packages/core/src/avkit_core/services/health.py` | modify | pack state |
| `packages/infrastructure/src/avkit_infra/tts/assets.py` | modify | pack state and download; the append fix |
| `packages/infrastructure/src/avkit_infra/tts/voices.py` | modify | `ONNX_REPO`, `ONNX_REVISION`, `ONNX_LOCAL_DIR`, `HF_FILE_MAP`, `variant_local_path` |
| `packages/infrastructure/src/avkit_infra/tts/adapter.py` | modify | `VOICE_PACK` style only: `_onnx_chunk` reads the `.bin` pack instead of `pipeline.load_single_voice`, and the PyTorch call passes the pack to `KPipeline` as a `(510, 1, 256)` tensor `voice`. `KPipeline` stays until row 10. |
| `packages/infrastructure/src/avkit_infra/model_manager/manager.py` | modify | revision, local dir, legacy sideload skip, the legacy fast-path skip (`LEGACY_ONNX_PATH`) |
| `packages/infrastructure/src/avkit_infra/model_manager/voice_packs.py` | new | `fetch_voice_pack` (`VOICE_PACK_DOWNLOAD`) |
| `packages/api/src/avkit_api/schemas/models.py` | modify | `TtsAssetWire` value |
| `packages/api/src/avkit_api/schemas/health.py` | modify | `tts_voice_packs` row |
| `packages/api/src/avkit_api/routes/health.py` | modify | row mapping |
| `packages/api/src/avkit_api/wiring.py` | modify | inject the fetch into `TtsAssetAdapter` |
| `openapi.committed.json` | modify | regenerated (AC-73.14) |
| `ui/src/renderer/src/features/tts/tts-assets.ts` | modify | wire, label |
| `ui/src/renderer/src/features/tts/useTtsJob.ts` | modify | `useRefreshDependenciesOnSettle` |
| `ui/src/renderer/src/features/settings/SettingsPage.tsx` | modify | uses the hook; the voice packs row |
| `mcp-server/src/toolsets/models.ts` | modify | `TTS_ASSET_WIRES` |
| `tests/tts_g2p_fakes.py` | new | `G2P_SEAM` fixture (the `FakeKPipeline` phase) |
| `tests/unit/test_tts_voice_packs_service.py` | new | AC-73.1, AC-73.4, AC-73.6 |
| `tests/integration/test_tts_voice_packs.py` | new | AC-73.2, AC-73.3, AC-73.5, AC-73.9, AC-73.15, AC-73.16 |
| `tests/e2e/test_api_tts_runtime.py` | new | AC-73.7 |
| `ui/tests/unit/settings-tts-runtime.test.ts` | new | AC-73.10, AC-73.11 |
| `tests/integration/test_tts_models.py` | modify | TA-1; the TA-2 voice error case; TA-10; TA-13 |
| `tests/integration/test_tts_assets.py` | modify | TA-3a, TA-8, TA-11, TA-12; AC-73.12 |
| `tests/e2e/test_api_health_settings.py` | modify | TA-4 |
| `tests/e2e/test_api_auth.py` | modify | TA-4 |
| `tests/e2e/api_fakes.py` | modify | TA-4 |
| `ui/tests/unit/settings-page.test.ts` | modify | TA-5 |
| `mcp-server/tests/models-assets.test.ts` | modify | TA-6 |

`packages/infrastructure/src/avkit_infra/model_manager/catalog.py` is not modified (see the note under TEST_AMENDMENTS).

### MEU-74 — TTS language runtime

MEU-74 delivers detection, availability and the espeak-ng CLI adapter. The G2P router that *uses* the adapter, and the removal of `KPipeline`, belong to MEU-72, because 07 §Packaged ONNX "ONNX without torch" assigns that rewrite there (D-86).

#### Boundary Inventory

| Boundary | Change | Wire / schema | Contract test |
|----------|--------|---------------|---------------|
| `GET /tts/voices` | each row gains `available: bool` and `reason: VOICE_REASON \| null` | `VoiceOut` | AC-74.3 |
| `POST /tts/generate` | `VOICE_AVAILABLE_409` before the asset check and the job row | existing error envelope | AC-74.4 |
| `GET /health/dependencies` | `tts_espeak: {available, version, path}` | new `EspeakOut` | AC-74.5 |
| `espeak-ng` subprocess | argv and stdin per `ESPEAK_G2P` | — | AC-74.6 |
| GUI | the Settings espeak row; disabled combobox options | `NEW_TESTIDS` | AC-74.7, AC-74.8, AC-74.9 |

#### Acceptance Criteria

| AC | Description | Source | Type | Test |
|----|-------------|--------|------|------|
| AC-74.1 | `voice_availability(lang_code, espeak_available)` follows `VOICE_REASON` over all 9 lang codes × 2 espeak states (a table test). An unknown lang code raises `ValidationError`. | Spec 03 "Voice availability"; D-70 | unit | `tests/unit/test_tts_voice_availability.py` |
| AC-74.2 | `ESPEAK_DETECT` with a fake `which`, env and runner covers five cases. (1) Found on PATH. (2) Found only under `%ProgramFiles%`. (3) Found nowhere: `available=False, version=None, path=None`. (4) `--version` exits nonzero: unavailable. (5) The version is cached per `(path, mtime_ns)`, and a fresh install is seen on the next call (no latch). | Spec 03 "Detect"; D-77 | unit | `tests/unit/test_espeak_adapter.py` |
| AC-74.3 | `GET /tts/voices` returns `available`/`reason` per row. With espeak absent: `ef_dora` is `false/"espeak_missing"`, `jf_alpha` is `false/"language_unsupported"`, and `af_heart` is `true/null`. With espeak present: `ef_dora` is `true/null`, and `jf_alpha` stays unavailable. | Spec 03; Boundary Input Contract | integration | `tests/e2e/test_api_tts_runtime.py` |
| AC-74.4 | `generate` with `ef_dora` while espeak is absent returns 409 `voice unavailable: ef_dora (espeak_missing)`. No job row exists, and the asset check is never reached: the fake asset port records no call. `j`/`z` voices give the same with `language_unsupported`. | Spec 03 "Voice availability"; `ASSET_409_ORDER` | integration | `tests/e2e/test_api_tts_runtime.py` |
| AC-74.5 | `GET /health/dependencies` `tts_espeak` mirrors `ESPEAK_DETECT`. With a fake port, present gives the version and path, and absent gives nulls. | Spec 03 "Detect" | integration | `tests/e2e/test_api_tts_runtime.py` |
| AC-74.6 | `ESPEAK_G2P` with a fake runner. The argv is exactly `[exe,"-q","--ipa","--tie=^","-v","es","--stdin"]`. The text arrives on stdin and never in argv. Punctuation is preserved in order, `(en)` flags are stripped, and `«` `»` come back as `“` `”`. A nonzero exit or a timeout raises `TtsRuntimeError`.<br>`ESPEAK_MAP` is tested with samples that tell the two tables apart:<br>• Spanish fake output `ˈeste` stays `ˈeste`.<br>• `t^s` and `d^z` become `ʦ` and `ʣ`.<br>• French `bɔ̃` keeps U+0303, and `-` is removed.<br>• There is one sample per `MULTI_E2M` rule.<br>• A multilingual call applies no `EN_E2M`-only rule: `e`, `r`, `x` and U+0303 survive.<br>• `ESPEAK_EN_FALLBACK` maps `e` → `A`, `ɚ` → `əɹ` and `ɾ` → `T`; US `o^ʊ` → `O`; British `ə^ʊ` → `Q`. It has one sample per `EN_E2M` rule and returns rating 2.<br>• `ESPEAK_MAP_PARITY` passes. | D-71; misaki `espeak.py` | unit | `tests/unit/test_espeak_adapter.py` |
| AC-74.7 | The Settings Dependencies card shows `tts-espeak-row`. When espeak is available, the row reads "Detected" plus the version. When it is absent, the row reads "Not installed" and shows `tts-espeak-guidance`: Spanish, French, Hindi, Italian and Portuguese voices need eSpeak NG, with the URL `https://github.com/espeak-ng/espeak-ng/releases` as text and a "Copy link" button that writes it through the existing `window.api.writeClipboardText` (D-96). The row has no Get button. | Spec 03 "Detect" | integration | `ui/tests/unit/settings-tts-runtime.test.ts` (appended) |
| AC-74.8 | `VoiceCombobox`: unavailable voices render `role="option"` with `aria-disabled="true"`. Click and Enter do not select them. Each shows the `voice-unavailable-reason` text ("Needs eSpeak NG" / "Language not supported yet"). Available voices behave as before. When the current selection is unavailable, the selected chip shows the reason. | Spec 03 "Voice availability" | integration | `ui/tests/unit/voice-combobox.test.tsx` (appended) |
| AC-74.9 | Electron: with the seam serving `jf_alpha` unavailable, its option is `aria-disabled="true"` and the reason is visible. | Spec 03; 06-gui | integration | `ui/tests/e2e/tts-generate.test.ts` (appended) |
| AC-74.10 | `openapi.committed.json` is regenerated, and `--check` passes. | G8 | integration | gate stage `openapi` |
| AC-74.11 | LOCAL-ESPEAK (optional, manual, after row 10): with espeak-ng 1.52 installed, the dev backend generates a Spanish WAV for `ef_dora` and a French WAV for `ff_siwis`. `ESPEAK_G2P` on the real CLI keeps `e` in Spanish `este` and U+0303 in French `bon`, and `tts_espeak` shows the version. | D-71 | integration | `walkthrough.md` §LOCAL-ESPEAK |

#### Spec Sufficiency

| Question | Answer | Source |
|----------|--------|--------|
| How is espeak-ng invoked without shipping GPL code? | A subprocess call to the user's CLI (D-71) | D-61 principle; phonemizer-fork GPL-3.0+ |
| ja/zh licence and size assessment ("assessed in the plan") | Assessed in D-70. `misaki[ja]` pulls `fugashi` and `unidic` (about 500 MB of dictionary); `misaki[zh]` pulls `jieba`, `pypinyin` and `cn2an`. Both stay unavailable and get a follow-up issue. | Spec 03 "ja / zh extras"; Human-approved 2026-10-14 |
| Where do reasons render? | In the combobox option and the chip; the 409 message carries the code | Spec 03 |
| Does MEU-74 make Spanish generate work? | It makes Spanish *honestly available*: listed, detected, and refused with a reason when espeak is absent. A Spanish WAV needs the MEU-72 G2P router (row 10), which calls `ESPEAK_G2P`. Until row 10, `KPipeline` still serves non-English voices when espeak exists. | 07 "ONNX without torch"; D-86 |

#### Files Modified (MEU-74)

| File | Action | What |
|------|--------|------|
| `packages/core/src/avkit_core/domain/tts.py` | modify | `VoiceUnavailableReason`, `EspeakStatus`, `voice_availability`, and a frozen `VoiceAvailability(available: bool, reason: VoiceUnavailableReason \| None)`. `VoiceConfig` keeps its five fields (spec 01-domain-layer.md:364; `test_domain.py` AC-2.10/AC-2.12). `TtsService.list_voices` pairs each voice with its availability (D-89). |
| `packages/core/src/avkit_core/ports/tts.py` | modify | `EspeakPort` |
| `packages/core/src/avkit_core/services/tts.py` | modify | `list_voices` availability; `VOICE_AVAILABLE_409` |
| `packages/core/src/avkit_core/domain/health.py` | modify | `tts_espeak` |
| `packages/core/src/avkit_core/services/health.py` | modify | `tts_espeak` |
| `packages/infrastructure/src/avkit_infra/tts/espeak.py` | new | `EspeakCliAdapter` (`ESPEAK_DETECT`, `ESPEAK_G2P`) and `ESPEAK_MAP` (`MULTI_E2M`, `EN_E2M`, `ESPEAK_EN_FALLBACK`) |
| `packages/api/src/avkit_api/schemas/tts.py` | modify | `VoiceOut.available/reason` |
| `packages/api/src/avkit_api/routes/tts.py` | modify | map availability |
| `packages/api/src/avkit_api/schemas/health.py` | modify | `EspeakOut` |
| `packages/api/src/avkit_api/routes/health.py` | modify | espeak row |
| `packages/api/src/avkit_api/wiring.py` | modify | `EspeakCliAdapter` injection |
| `openapi.committed.json` | modify | regenerated (AC-74.10) |
| `ui/src/renderer/src/features/tts/VoiceCombobox.tsx` | modify | disabled options, reason |
| `ui/src/renderer/src/features/tts/tts-voices.ts` | modify | `available?: boolean` / `reason?: VoiceUnavailableReason \| null` types (absent means available) and the reason text. They are optional so the voice rows that existing tests build without them stay valid and unchanged: `voice-combobox.test.tsx:20-30`, `tts-page.behavior.test.ts:43-45`, `tts-page.test.ts:245-251`, `tts-generate.test.ts:167` and `mcp-server/tests/tools-parity.test.ts:126` (receipt `census-s32-voice-rows.txt`). The API always sends both fields. |
| `ui/src/renderer/src/features/settings/SettingsPage.tsx` | modify | espeak row |
| `ui/src/renderer/src/features/tts/useTtsJob.ts` | modify | `useVoices` rows typed `VoiceOut[]` (D-99) |
| `ui/tests/e2e/test-ids.ts` | modify | `NEW_TESTIDS` |
| `ui/tests/e2e/fixtures/tts-voices.json` | modify | TA-7 |
| `tests/unit/test_tts_voice_fixture.py` | modify | TA-7 |
| `tests/unit/test_tts_voice_availability.py` | new | AC-74.1 |
| `tests/unit/test_espeak_adapter.py` | new | AC-74.2, AC-74.6 |
| `tests/e2e/test_api_tts_runtime.py` | modify (append) | AC-74.3, AC-74.4, AC-74.5 |
| `tests/e2e/test_api_tts_models.py` | modify | TA-14 (D-95) |
| `ui/tests/unit/settings-tts-runtime.test.ts` | modify (append) | AC-74.7 |
| `ui/tests/unit/voice-combobox.test.tsx` | modify (append) | AC-74.8 |
| `ui/tests/e2e/tts-generate.test.ts` | modify (append) | AC-74.9 |
| `tests/e2e/test_api_health_settings.py` | modify | TA-4 (`tts_espeak`) |
| `tests/e2e/test_api_auth.py` | modify | TA-4 (`tts_espeak`) |
| `tests/e2e/api_fakes.py` | modify | TA-4 (`tts_espeak`) |
| `ui/tests/unit/settings-page.test.ts` | modify | TA-5 (`tts_espeak`) |
| `tests/integration/test_tts_assets.py` | modify | TA-9 |

`tests/e2e/test_api_tts_runtime.py` and `ui/tests/unit/settings-tts-runtime.test.ts` are created at row 2. `plan_checks.py` accepts `modify (append)` for a path that a `new` row of this plan creates.

### MEU-72 — Packaged ONNX TTS runtime

#### Boundary Inventory

| Boundary | Change | Contract test |
|----------|--------|---------------|
| Python imports | `IMPORT_HYGIENE` | AC-72.1 |
| `KokoroG2p` | `G2P_ROUTE` (misaki English, `ESPEAK_G2P` for e/f/h/i/p, the spaCy guard) | AC-72.2 |
| `KokoroAdapter` constructor | gains `g2p` injection; `KPipeline` removed; `KModel` imported lazily | AC-72.4, AC-72.5 |
| ONNX session feeds | `ONNX_FEEDS` | AC-72.4 |
| Frozen bundle | `SPEC_BUNDLE`, `NOTICES` | AC-72.6, AC-72.7 |
| Frozen API | `PACKAGE_SMOKE` | AC-72.8 |
| Installer / MCP entry | `INSTALLER_STAGE` | AC-72.9 |

#### Acceptance Criteria

| AC | Description | Source | Type | Test |
|----|-------------|--------|------|------|
| AC-72.1 | `IMPORT_HYGIENE`. `avkit_infra.tts.adapter` and the real `misaki.en` import with torch, kokoro, phonemizer and espeakng_loader blocked. The English and Spanish ONNX generates (faked `misaki_factory`, fake session, fake espeak runner, tmp `VOICE_PACK`) each yield finite float32 samples clipped to [-1, 1], with progress ending at 1.0. | Spec 07 "ONNX without torch", "Tests"; D-71 | integration | `tests/integration/test_tts_no_torch.py` |
| AC-72.2 | `G2P_ROUTE`, in four cases. (1) English passes `ESPEAK_EN_FALLBACK` (`EN_E2M`) as the misaki fallback only when espeak is available (fake). (2) `e/f/h/i/p` call `ESPEAK_G2P` with the `ESPEAK_VOICE` code and `MULTI_E2M`, never `EN_E2M`. (3) `j/z` raise `ValidationError`. (4) With `spacy.util.is_package` faked to false, the first English call raises `ConflictError("tts asset missing: tts_spacy_model")` and the factory is never called, so `spacy.cli.download` is never reached. The misaki G2P is constructed once per `british` flag. | D-71, D-72 | unit | `tests/unit/test_tts_g2p.py` |
| AC-72.3 | `CHUNK_RULE` properties. Every chunk is non-empty and ≤ 510, and concatenation preserves order. The cut prefers sentence over clause over space. A 2 000-symbol run with no breaks splits hard at 510. Empty input yields no chunks, and generate then returns empty audio with progress 1.0. | Local Canon `adapter.py:228-229`; D-78 | unit | `tests/unit/test_tts_g2p.py` |
| AC-72.4 | `ONNX_FEEDS`, asserted on a recording fake session: the dtypes and shapes, `[[0,*ids,0]]`, the style row `len(ids)-1` (clamped), unknown symbols dropped, and one `session.run` per chunk. Real phoneme ids reach the model, not pad tokens only. That was the intent of the deleted AC-62.16 test (TA-3b). | Existing adapter contract | unit | `tests/integration/test_tts_models.py` (rebased, TA-2) |
| AC-72.5 | `TORCH_PATH` with a fake `KModel`. It is called once per chunk with the phoneme string and a `(1,256)` style tensor. `KPipeline` is never imported: after a run with a stub `kokoro` package that defines only `KModel`, `"kokoro.pipeline" not in sys.modules`. | D-75 | unit | `tests/integration/test_tts_models.py` (rebased, TA-2) |
| AC-72.6 | `SPEC_BUNDLE`, parsed from the spec AST: the excludes, hiddenimports, datas call and `module_collection_mode` are present. None of `kokoro-v1_0.pth`, `*.onnx`, `voices`, `en_core_web_sm` or `espeak` appears in datas. | Spec 07 "Bundle", 07:312 | unit | `tests/unit/test_packaging_backend.py` (appended) |
| AC-72.7 | `NOTICES`: the file exists, lists the six components with their licences, carries the LGPL-2.1 text, names FFmpeg as a separately shipped GPL-3.0 program with its source URL and `resources/ffmpeg/LICENSE.txt`, and states that espeak-ng is not shipped. `electron-builder.yml` copies it. `fetch_ffmpeg_windows.ps1 -ExtractOnly`, given a fabricated zip whose SHA the test computes and with two fake binaries over 1 KB, exits 6 when the zip has no `LICENSE.txt`, and copies `LICENSE.txt` into `-OutDir` when it does. | D-76, D-87 | unit | `tests/unit/test_packaging_installer.py` (appended) |
| AC-72.8 | `PACKAGE_SMOKE` passes. `package-smoke-result.json` has:<br>• `online.passed` and `forbidden_dirs: []`.<br>• `offline.passed`, `offline.wav_samples > 8000`, and `offline.negative_probe.state == "Failed"`.<br>• An `offline.backend_dir` outside the worktree, and the proxy values set.<br>• A `WORKTREE_IDENTITY` equal to the gate's, and timings.<br>`windows-gate-check` refuses the result if any of these is missing. | Spec 07 "Smoke", "Tests"; round-1 F3 | integration | `validate-task.ps1 -Check package-smoke` |
| AC-72.9 | `INSTALLER_STAGE`: `npm run dist` exits 0, `assert-nsis-pack.ps1` passes (size cap), and `installer.notices_staged` and `installer.ffmpeg_license_staged` are both `true`. `MCP_ENTRY_PROBE` is recorded as `started` or `unreachable` with its evidence. At H2-2 the result is copied into the `verification` of `MCP-PACKAGED-ENTRY-UNREACHABLE`, and the status changes only per the evidence: `unreachable` → `open`; `started` → `resolved` with "not reproduced". | Spec 07 "Smoke"; triage D-41 note | integration | `validate-task.ps1 -Check package-smoke` |

#### Files Modified (MEU-72)

| File | Action | What |
|------|--------|------|
| `packages/infrastructure/src/avkit_infra/tts/g2p.py` | new | `KokoroG2p` (`G2P_ROUTE`), `split_phonemes` (`CHUNK_RULE`) |
| `packages/infrastructure/src/avkit_infra/tts/adapter.py` | modify | drop `KPipeline` and `_chunk_part`; lazy `KModel`; G2P + chunker + pack |
| `packages/infrastructure/pyproject.toml` | modify | add `misaki[en]` (pinned to the version `uv.lock` already resolves, 0.9.4) and `num2words` (0.5.14) as direct deps; `kokoro` stays for the dev PyTorch path |
| `uv.lock` | modify | only if the direct-dep change re-locks (no new resolution expected) |
| `packaging/avkit-backend.spec` | modify | `SPEC_BUNDLE` |
| `packaging/THIRD_PARTY_NOTICES.md` | new | `NOTICES` |
| `ui/electron-builder.yml` | modify | `extraResources` notice |
| `tools/smoke_packaged_tts.py` | new | `ONLINE_PROVISION` (`--phase online`), `OFFLINE_SMOKE` and `NEGATIVE_PROBE` (`--phase offline`) |
| `tools/fetch_ffmpeg_windows.ps1` | modify | copy the archive's `LICENSE.txt` into `-OutDir`; exit 6 if there is none (D-87). The pin, the SHA check and the stub-size refusal are unchanged. |
| `tests/tts_g2p_fakes.py` | modify | `G2P_SEAM` switches to `FakeG2p` |
| `tests/unit/test_tts_g2p.py` | new | AC-72.2, AC-72.3 |
| `tests/integration/test_tts_no_torch.py` | new | AC-72.1 |
| `tests/integration/test_tts_models.py` | modify | TA-2; AC-72.4, AC-72.5 |
| `tests/integration/test_tts_assets.py` | modify | TA-3b |
| `tests/unit/test_packaging_backend.py` | modify (append) | AC-72.6 |
| `tests/unit/test_packaging_installer.py` | modify (append) | AC-72.7 (the notices and the fetch `LICENSE.txt` cases) |

## Out of Scope

| Item | Kind | Deferred-to MEU | Basis |
|------|------|-----------------|-------|
| TTS page run bar, voice panel and device rows | deferred | MEU-75, MEU-77, MEU-78 | Grouping §Session 33/35 and D-5 (lines 103-110, 219) |
| `misaki[ja]`/`[zh]` extras | out of scope | — | Human-approved D-70 (USER_EXPLICIT 2026-10-14); a follow-up issue `TTS-JA-ZH-G2P-EXTRAS` is filed at H2-2 |
| A custom espeak-ng path setting | out of scope | — | 03 §TTS language runtime lines 449-455 specify detection and guidance only; D-77 |
| An MCP audit step that downloads voice packs | out of scope | — | 03 §TTS voice assets lines 434-439 list no MCP audit change; `coverage.test.ts:16` counts actions, not enum values (D-84) |
| Fixing `MCP-PACKAGED-ENTRY-UNREACHABLE` | out of scope | — | 07 §Packaged ONNX "Smoke" (line 244) asks only to *record* it; it stays a candidate until evidence exists |
| Deleting legacy v0.19 ONNX files | out of scope | — | D-73: never delete user files (av-kit invariant, 09 "files on disk are not deleted"); the files are ignored and logged |
| Bundling voice packs, spaCy, Kokoro weights or CUDA | out of scope | — | 07:312; Human-approved D-22 |
| Replacing the GPL FFmpeg build (an LGPL build, or Convert without `libx264`/`libx265`) | out of scope | — | Human-approved D-87 (USER_EXPLICIT 2026-10-14); the follow-up issue `FFMPEG-GPL-BUILD` is filed at H2-2 |
| Re-pinning the hexgrad `config.json` vocab revision | out of scope | — | MEU-62 `VOCAB_LOCATION` contract (03 §TTS runtime assets) is unchanged; the receipt shows it matches v1.0-ONNX on every symbol |

## BUILD_PLAN.md Audit

Row 13 does the hub reconciliation (`validate-task.ps1 -Check hub`):

1. `docs/build-plan/02-infrastructure.md:217`: "`onnx-community/Kokoro-82M-ONNX` (ONNX)" → "`onnx-community/Kokoro-82M-v1.0-ONNX` @ `ONNX_REVISION` (ONNX weights and `voices/*.bin`)".
2. `03-service-layer.md` §TTS voice assets and §TTS language runtime: one "Delivered (Session 32)" line each, naming D-74 (`.bin`, all at once, chained with the model) and D-71 (CLI subprocess). The rule tables are unchanged.
3. `07-distribution.md` §Packaged ONNX: one "Delivered" line naming `tools/smoke_packaged_tts.py` and `NOTICES`.
4. `06-gui.md:1156` Dependencies row: "yt-dlp + FFmpeg version/path, TTS assets (Get), eSpeak NG (detected/guidance)". `11-page-layout.md:129`: the voice picker lists unavailable voices disabled with a reason.
5. `build-priority-matrix.md`: add rows 3.6 (MEU-73), 3.7 (MEU-74), 7.4 (MEU-72) only, per `meu-status.yaml` order numbers (lines 1913/1939/1963). Grouping D-1's wait for Session 30 has ended (Session 30 is approved). The other missing rows stay with their sessions; Session 31 may be editing nearby, so conflicts are resolved at Mat's merge.
6. `BUILD_PLAN.md` and the registry are generated: H1-3 and H2-2 run `meu_status.py update` and `render --check`; nothing is hand-edited.

## Verification Plan

All checks run as `pwsh -NoProfile -File docs/execution/plans/2026-10-14-tts-engine-runtime/validate-task.ps1 -Check <id>`. Every tool runs inside it through `rtk proxy`, with the raw receipt at `C:/Temp/av-kit/s32-<id>*.txt` (AGENTS §RTK; `output-evidence-policy.md`).

| # | Check | Scope | Blocking | Expected |
|---|-------|-------|----------|----------|
| 0 | `prereq`, `baseline` | context-tool gate, MEU states, `baseline.sha` | yes | `walkthrough.md` §Execution authorization records USER_EXPLICIT; plan review `approved`; MEU-73/74/72 `pending`; MEU-24/62/64 `approved`; no graph dirs |
| 1 | `census` | `TEST_AMENDMENTS` grep | yes | every hit dispositioned |
| 2 | `red-73` / `red-74` / `red-72` | new tests (`red-74` also runs the `ui` Vitest Red and the `AC-74.9` Electron Red) | yes | assertion failures only; only declared new symbols may fail to import |
| 3 | `green-73` / `green-74` / `green-72` | targeted pytest, Vitest, MCP Vitest | yes | pass |
| 4 | `gate73` / `gate74` / `gate72` | pyright, ruff, targeted suites, OpenAPI two-step, `ta-check` | yes | pass |
| 5 | `hub` | doc-reading Vitest (`layout-canon`, `gui-actions-audit`) and `render --check` | yes | pass |
| 6 | `plan-static` | `plan_checks.py static` + `selftest`; `lint_task_contract.py` | yes | pass |
| 7 | `windows-gate` | full PROFILE D6 set, 17 stages (Session 30 order) | yes | all exit 0; `COUNT_FLOORS` |
| 8 | `package-smoke` | `ONLINE_PROVISION` → `INSTALLER_STAGE` → `OFFLINE_SMOKE` (`PACKAGE_SMOKE`) | yes (MCP probe recorded only) | pass; offline generate and `NEGATIVE_PROBE` `Failed` |
| 9 | `windows-gate-check` | both result JSONs vs `WORKTREE_IDENTITY`, floors, stage list | yes | pass |
| 10 | `api-scope` | `PRODUCT_SCOPE` | yes | pass |
| 11 | OpenAPI | `uv run python tools/export_openapi.py --check openapi.committed.json`, then `-o` only on drift | yes | pass after regeneration in gate73/74 |
| 12 | `task-state`, `ssot-review`, `handoff-ac` | rows 0–13 closed; MEU states `ready_for_review`; AC coverage of the three handoffs | yes | pass |
| 13 | `review-check -Arg plan` / `-Arg implementation` | the canonical review file: frontmatter, target, mode, round within cap (3 / 6), `approved`, a non-Anthropic agent | yes | pass |
| 14 | `reflection` | `validate_closeout_artifacts.py` with this plan and the grouping as decision sources | yes | pass |
| 15 | `post-review-state` | MEUs `approved`, issues resolved with evidence under this plan, `render --check`, `issue_triage.py render --check`, doc-reading suites | yes | pass |

**Verifier negative cases (V4)**, run by `plan_checks.py selftest` on in-memory copies. Each must be reported:

- a duplicate row id;
- an unknown `-Check` name in `task.md`;
- a `COUNT_FLOORS` literal changed in the `.ps1`;
- a `GATED_PATHS` entry dropped;
- an undefined `AC-73.99`;
- a `D-99` reference;
- a `modify` row for a missing file;
- a `new` row for an existing file.

## GUI Element Compliance Check (create-plan Step 4A)

| Element | Action / state | Test id | Endpoint | Covered by |
|---------|----------------|---------|----------|-----------|
| Voice packs asset row + Get | download asset | `tts-asset-row-tts_voice_packs`, `tts-asset-get-btn-tts_voice_packs` | `POST /models/download` | AC-73.11 |
| Dependencies refresh on settle | invalidation | — | `GET /health/dependencies` | AC-73.10 |
| eSpeak NG row + guidance link | read-only + copy link (D-96) | `tts-espeak-row`, `tts-espeak-guidance` | `GET /health/dependencies` | AC-74.7 |
| Disabled voice option + reason | not selectable | `voice-unavailable-reason` | `GET /tts/voices` | AC-74.8, AC-74.9 |

The Get button pattern and the copy-link button (`writeClipboardText`, as Settings' "Copy log path" uses) reuse existing controls. No new `gui-actions-index.md` action is introduced: the asset Get was never indexed and stays an MEU-62 control; the voice picker's actions are unchanged.

## Stop Conditions

| ID | Condition | Action |
|----|-----------|--------|
| S1 | `main` moved past `7861020` with Session 31 merged before row 0 | Rebase the worktree, re-derive `COUNT_FLOORS` from Session 31's gate result, and record an amendment; do not execute against stale floors |
| S2 | The census finds a `new-contradiction` | Stop and brief (human-decision-protocol) |
| S3 | `misaki.en` imports `misaki.espeak`, `phonemizer` or torch at import time, so AC-72.1 cannot go Green without vendoring misaki. The planning probe (`C:/Temp/av-kit/s32-misaki-import-probe.txt`) shows misaki 0.9.4 does not; S3 guards a lock change. | Stop; Decision Brief (vendor `misaki.en` under Apache-2.0, or accept a lazy shim) |
| S4 | The frozen backend cannot load spaCy or misaki data in `PACKAGE_SMOKE` after two spec corrections | Stop and report the receipts; Decision Brief |
| S5 | LOCAL-ESPEAK shows that the real CLI rejects or differs from `ESPEAK_G2P` flags | Correct the adapter under an amendment, or record it as unverified plus an issue if espeak-ng is unavailable |
| S6 | The installer exceeds the size cap | Stop; report the bundle size breakdown |
| S7 | The `ONNX_REVISION` download fails with 404 (revision gone) | Stop; Decision Brief to re-pin |
| S8 | The pinned FFmpeg archive has no `LICENSE.txt` (fetch exit 6), or `NEGATIVE_PROBE` reaches the network | Stop; Decision Brief (another licence source for D-87, or a stronger denial for D-88) |

## Decision Log

Carried from the grouping (stage `grouping`): **D-1**, **D-3**, **D-4**, **D-6** (`.agent/context/grouping/2026-10-09-triage-residuals-session-grouping.md:215-221`). Triage decisions D-22, D-41, D-42, D-43 and D-61 are cited from `known-issues.yaml` and are not re-decided. This plan's ids start at D-70.

```yaml
decision_log:
  - id: D-70
    stage: planning
    question: "Japanese (j) and Mandarin (z) voices: add the misaki[ja]/[zh] extras now or mark them unavailable?"
    resolution: human
    class: product-preference
    chosen: "Mark unavailable: listed with reason language_unsupported, disabled in the GUI, 409 on generate; follow-up issue TTS-JA-ZH-G2P-EXTRAS"
    source_tag: Human-approved
    precedents: ["03-service-layer.md:453 — 'until then j/z voices follow the availability rule'"]
    research: { engine: native, sources: ["https://github.com/hexgrad/misaki pyproject extras — ja: fugashi, unidic (≈500 MB dictionary download), jaconv, mojimoji, pyopenjtalk; zh: jieba, ordered-set, pypinyin, cn2an, pypinyin-dict"] }
    reasoning: "Extras add hundreds of MB and new licence review; the availability rule gives an honest UI now."
    human_message_reference: "USER_EXPLICIT 2026-10-14 'Mark unavailable (Recommended)'"
  - id: D-71
    stage: planning
    question: "How do non-English voices get phonemes without shipping GPL code?"
    resolution: autonomous
    class: two-way
    chosen: "av-kit EspeakCliAdapter calls the user-installed espeak-ng CLI as a subprocess (text on stdin), with misaki's Apache-2.0 mappings ported and attributed (ESPEAK_MAP: EspeakG2P.e2m as MULTI_E2M for the non-English languages, EspeakFallback.E2M as EN_E2M for the English fallback only, parity-checked against the installed source without importing it); phonemizer, espeakng_loader and misaki.espeak are never imported and are excluded from the bundle"
    source_tag: Local Canon
    precedents: ["known-issues.yaml D-61 (Human-approved 2026-10-09) — never ship espeak-ng; no GPL code in the shipped app", "09 §ShareX source map — no GPL code"]
    research: { engine: native, sources: ["https://pypi.org/project/phonemizer-fork/ — License: GPL-3.0-or-later", "https://github.com/hexgrad/misaki/blob/main/misaki/espeak.py — EspeakG2P wraps phonemizer EspeakBackend (tie '^', remove-flags) and applies its own e2m table; EspeakFallback applies a different E2M table for English", "https://github.com/espeak-ng/espeak-ng/blob/master/src/espeak-ng.1.ronn — --ipa, --tie=CHAR, --stdin, -q, -v"] }
    reasoning: "In-process loading of a GPL library is the grey area D-61 flagged; phonemizer itself is GPL source we would ship. A separate program invoked at arm's length keeps the TTS runtime GPL-free and matches D-61's detect-and-guide model (FFmpeg, also a separate GPL program, is D-87). Alternative (bundle phonemizer, load the user's DLL) ships GPL Python code and loses."
  - id: D-72
    stage: planning
    question: "What is the English out-of-dictionary fallback?"
    resolution: autonomous
    class: two-way
    chosen: "ESPEAK_EN_FALLBACK (ESPEAK_G2P with en-us/en-gb and EN_E2M) when espeak-ng is detected; otherwise None (misaki emits unk='' and the word is skipped)"
    source_tag: Local Canon
    precedents: ["kokoro KPipeline uses EspeakFallback for a/b — same behaviour when espeak exists"]
    research: { engine: none, sources: [] }
    reasoning: "English stays available without espeak (most words are in misaki's lexicons); rare words are silent instead of failing the job. Recorded as a known quality trade-off in the MEU-72 handoff. The spaCy guard in G2P_ROUTE belongs to this decision: misaki 0.9.4 G2P.__init__ calls spacy.cli.download when the model is missing, which would be a network install mid-job; the guard turns that into the existing MEU-62 409."
  - id: D-73
    stage: planning
    question: "Which ONNX export does the catalog download?"
    resolution: autonomous
    class: two-way
    chosen: "onnx-community/Kokoro-82M-v1.0-ONNX at revision 1939ad2a8e416c0acfeecc08a694d14ef25f2231 into ONNX_LOCAL_DIR; LEGACY_ONNX_DIR ignored (logged, never deleted) in the scan, and LEGACY_ONNX_PATH applied to persisted rows in list, load and download; 02-infrastructure.md:217 amended"
    source_tag: Research-backed
    precedents: ["voices.py:82-87 — current map", "02-infrastructure.md:217 — names the v0.19 repo"]
    research: { engine: native, sources: ["https://huggingface.co/onnx-community/Kokoro-82M-ONNX — README marks new_version: onnx-community/Kokoro-82M-v1.0-ONNX (v0.19 export)", "C:/Temp/av-kit/s32-onnx-vocab-compare.txt — v0.19 tokenizer differs from v1.0 vocab on 83 symbols; v1.0-ONNX matches on all 114 (+'$')"] }
    reasoning: "The shipped vocab and packs are v1.0; feeding them to a v0.19 graph mispronounces. Pinning the revision makes downloads reproducible. A revision-scoped local dir is the only way to stop the rglob sideload from reusing the old file. The round-1 review showed that the scan is not the only entry: a v0.19 download persisted its path in the models table, and both load and the download fast path read that row. LEGACY_ONNX_PATH closes those entries with one pure predicate, so an upgraded user sees 'not downloaded' and a load is refused with a re-download message instead of running the mismatched graph."
  - id: D-74
    stage: planning
    question: "Voice pack format and granularity"
    resolution: autonomous
    class: two-way
    chosen: "One managed asset tts_voice_packs = all 54 voices/VOICE_ID.bin (~28 MB) from ONNX_REPO; downloaded chained after any model download and by Get; used by both formats"
    source_tag: Local Canon
    precedents: ["03-service-layer.md:436 — 'fetched on first selection of a voice (or with the model)'", "MEU-62 TtsAsset pattern (assets.py:217-258)"]
    research: { engine: native, sources: ["C:/Temp/av-kit/s32-hf-onnx10.json — 55 voices/*.bin at the pinned revision"] }
    reasoning: "Per-voice assets would need a parameterised asset port, wire and health row; 28 MB at once keeps the MEU-62 shape and makes every voice offline-ready. .bin avoids torch for packs."
  - id: D-75
    stage: planning
    question: "Does the PyTorch path keep KPipeline?"
    resolution: autonomous
    class: two-way
    chosen: "No: both formats share G2P_ROUTE, CHUNK_RULE and VOICE_PACK; PyTorch calls KModel directly (TORCH_PATH)"
    source_tag: Local Canon
    precedents: ["07-distribution.md §Packaged ONNX — 'the PyTorch path keeps using kokoro when torch is present' (KModel is kokoro)"]
    research: { engine: none, sources: [] }
    reasoning: "KPipeline would reintroduce misaki.espeak (GPL import) and lazy .pt fetches; one G2P keeps availability identical across formats."
  - id: D-76
    stage: planning
    question: "num2words (LGPL-2.1) in the frozen bundle?"
    resolution: autonomous
    class: two-way
    chosen: "Bundle it as replaceable .py source (module_collection_mode) and list it in THIRD_PARTY_NOTICES.md"
    source_tag: Research-backed
    precedents: ["D-61 targets GPL, not LGPL"]
    research: { engine: native, sources: ["https://pypi.org/project/num2words/ — LGPL-2.1", "https://pyinstaller.org/en/stable/spec-files.html — Analysis(module_collection_mode={'pkg': 'py'}) collects source files outside the PYZ"] }
    reasoning: "misaki.en imports num2words for number reading; LGPL permits distribution with notice and replaceability, which source collection provides. Flagged in User Review Required."
  - id: D-77
    stage: planning
    question: "How is espeak-ng detected?"
    resolution: autonomous
    class: two-way
    chosen: "ESPEAK_DETECT: which, then the two standard install dirs; re-probe per call; version cached per path+mtime; no custom-path setting"
    source_tag: Local Canon
    precedents: ["media/adapter.py:211-223 — FFmpeg probe (latched; MEU-78 calls the latch a divergence)"]
    research: { engine: native, sources: ["https://github.com/espeak-ng/espeak-ng/releases — the Windows MSI installs to Program Files\\eSpeak NG"] }
    reasoning: "No latch, so 'Check dependencies' sees a fresh install without restart; caching only the version keeps calls cheap."
  - id: D-78
    stage: planning
    question: "Chunking without KPipeline"
    resolution: autonomous
    class: two-way
    chosen: "CHUNK_RULE in avkit_infra.tts.g2p"
    source_tag: Local Canon
    precedents: ["adapter.py:228-229 — 510 limit", "kokoro KPipeline waterfall — behaviour reference"]
    research: { engine: none, sources: [] }
    reasoning: "The model limit is 510 tokens; natural boundaries keep prosody."
  - id: D-79
    stage: planning
    question: "How are the gate and packaged smoke run and bound when the driver is local and commits are the user's?"
    resolution: autonomous
    class: two-way
    chosen: "The driver runs windows-gate and package-smoke itself; both bind to WORKTREE_IDENTITY; Mat commits after review"
    source_tag: Local Canon
    precedents: ["cloud-local-collaboration.md §1 — contract applies when driver OS ≠ target OS", "Session 24 native run"]
    research: { engine: none, sources: [] }
    reasoning: "Same evidence strength as a commit sha without auto-committing."
  - id: D-80
    stage: planning
    question: "Reviewer route"
    resolution: autonomous
    class: two-way
    chosen: "Codex CLI avkit_independent_reviewer via Invoke-CodexDispatch, overlay model, effort high; plan cap 3, execution cap 6"
    source_tag: Local Canon
    precedents: ["harness.local.md §Claude Code", "AGENTS §Dual-Agent Workflow — no snapshot pins"]
    research: { engine: none, sources: [] }
    reasoning: "Vendor-distinct from the author; Session 31's model pin was scoped to its loops."
  - id: D-81
    stage: planning
    question: "Free-text reason or closed code?"
    resolution: autonomous
    class: two-way
    chosen: "Closed VOICE_REASON enum on the wire; the UI owns the wording"
    source_tag: Local Canon
    precedents: ["AssetState closed Literal on the wire (schemas/health.py:31-34)"]
    research: { engine: none, sources: [] }
    reasoning: "Closed sets fail closed and let the GUI and MCP clients branch."
  - id: D-82
    stage: planning
    question: "When does Session 32 split?"
    resolution: autonomous
    class: two-way
    chosen: "At row 8 if coordinator context > ~50%: rows 9 onward as Session 32b on the same plan"
    source_tag: Local Canon
    precedents: ["grouping line 101 — split flag candidate"]
    research: { engine: none, sources: [] }
    reasoning: "MEU-72 needs only MEU-74's EspeakCliAdapter (row 6) and the MEU-73/74 handoffs; its rows read no in-context state from rows 2-8."
  - id: D-83
    stage: planning
    question: "COUNT_FLOORS source"
    resolution: autonomous
    class: two-way
    chosen: "Session 30's authoritative gate on main (773 / 133 / 655); S1 if Session 31 merges first"
    source_tag: Local Canon
    precedents: ["2026-10-02-capture-flatten-backup/windows-gate-result.json"]
    research: { engine: none, sources: [] }
    reasoning: "The worktree is based on main @ 7861020, which contains Session 30, not 31."
  - id: D-84
    stage: planning
    question: "MCP surface for the new asset"
    resolution: autonomous
    class: two-way
    chosen: "Add tts_voice_packs to TTS_ASSET_WIRES; no new audit step"
    source_tag: Local Canon
    precedents: ["mcp-server/src/toolsets/models.ts:5", "coverage.test.ts:16 — counts actions"]
    research: { engine: none, sources: [] }
    reasoning: "Parity with the API enum; the audit census is unchanged because no action is added."
  - id: D-85
    stage: planning
    question: "How far does the hub reconciliation reach?"
    resolution: autonomous
    class: two-way
    chosen: "Only the lines this session's contracts change: 02-infrastructure.md:217, one Delivered line each in 03 §TTS voice assets, 03 §TTS language runtime and 07 §Packaged ONNX, 06-gui.md:1156, 11-page-layout.md:129, and build-priority-matrix rows 3.6/3.7/7.4"
    source_tag: Local Canon
    precedents: ["grouping D-1 (.agent/context/grouping/2026-10-09-triage-residuals-session-grouping.md:215) — the gated build-plan edits, matrix rows included, wait until Session 30 is approved (it is)"]
    research: { engine: none, sources: [] }
    reasoning: "Other missing matrix rows belong to sessions not yet run; editing them here would collide with Session 31's open branch and claim work this session did not do. The Delivered lines are new (no build-plan file has one yet); they are one line each so a reader of the residual section sees it is done without the rule tables changing."
  - id: D-86
    stage: planning
    question: "Which MEU owns the G2P router and the KPipeline removal?"
    resolution: autonomous
    class: two-way
    chosen: "MEU-72 (row 10). MEU-73 changes only the voice-pack style source; MEU-74 delivers detection, availability and the EspeakCliAdapter. The grouping order MEU-73 → MEU-74 → MEU-72 is kept."
    source_tag: Local Canon
    precedents: ["07-distribution.md:242 — 'The ONNX path runs the G2P directly and onnxruntime, with no dependency on kokoro.KPipeline/KModel' (MEU-72 rule table)", "03-service-layer.md §TTS language runtime — detect, availability, guidance (MEU-74 rule table)"]
    research: { engine: none, sources: [] }
    reasoning: "Putting the G2P rewrite in MEU-74 would make MEU-74's ACs depend on MEU-72's spec rule and leave MEU-72 with packaging only; each MEU's ACs now trace to its own spec section. The G2P_SEAM fixture keeps rows 2 and 5 tests stable across the row-10 rewrite."
  - id: D-87
    stage: planning
    question: "The installer ships a BtbN GPL FFmpeg build (P7, used by Convert's libx264/libx265 fallback). Does 'no GPL code' cover it, and what does this session do about it?"
    resolution: human
    class: product-preference
    chosen: "Scope the goal anchor to the TTS runtime ('no GPL code in the TTS runtime'); keep the FFmpeg build; disclose it in NOTICES as a separately shipped GPL-3.0 program with its source location, and ship the build's LICENSE.txt next to the binaries; file FFMPEG-GPL-BUILD for the choice between an LGPL build and Convert's software encoders"
    source_tag: Human-approved
    precedents: ["tools/fetch_ffmpeg_windows.ps1 — pinned BtbN win64-gpl-8.1 archive", "ui/electron-builder.yml extraResources — ../packaging/ffmpeg-win64 to ffmpeg", "media/adapter.py:496-507 and conversion.py:405-407 — libx265/libx264 software encoders"]
    research: { engine: native, sources: ["https://github.com/BtbN/FFmpeg-Builds — gpl and lgpl variants; gpl includes x264/x265", "https://www.ffmpeg.org/legal.html — GPL builds must ship the licence and offer source"] }
    reasoning: "Swapping the FFmpeg build changes Convert's encoders, which is outside this TTS session and needs its own tests. FFmpeg runs as a separate program, so disclosure plus licence text plus source location is the honest minimum now. The round-1 review (F1) found the original anchor 'no GPL code shipped' false for the installer as a whole, so the anchor was narrowed by the user rather than silently."
    human_message_reference: "USER_EXPLICIT 2026-10-14 'Scope anchor + notice (Recommended)'"
  - id: D-88
    stage: planning
    question: "How does the packaged smoke prove generation works with no network?"
    resolution: autonomous
    class: two-way
    chosen: "Provision online, then run OFFLINE_SMOKE as a fresh frozen process copied out of the staged installer tree, cwd and caches outside the checkout, every proxy variable pointed at http://127.0.0.1:9, HF_HUB_OFFLINE unset, and a NEGATIVE_PROBE download that must end Failed"
    source_tag: Local Canon
    precedents: ["07-distribution.md §Packaged ONNX 'Smoke'", "round-1 review F3 — an online run cannot certify offline generation"]
    research: { engine: native, sources: ["https://requests.readthedocs.io/en/latest/user/advanced/#proxies — HTTP(S)_PROXY / ALL_PROXY / NO_PROXY honoured", "https://huggingface.co/docs/huggingface_hub/package_reference/environment_variables — HF_HUB_OFFLINE, HF_HOME"] }
    reasoning: "A firewall rule needs an elevated shell on every gate run, and the gate runs unelevated. The dead proxy denies every proxy-honouring client, and NEGATIVE_PROBE proves the denial worked for the very client the app uses (huggingface_hub over requests/httpx). A raw-socket client would escape; none is known in the bundle, and the handoff states the residual."
  - id: D-89
    stage: execution
    question: "Row 1 census S2: MEU-74 planned VoiceConfig.available/reason, but test_domain.py AC-2.10/AC-2.12 and spec 01-domain-layer.md:364 fix VoiceConfig at five fields, and neither is in TEST_AMENDMENTS. How does MEU-74 carry voice availability?"
    resolution: human
    class: two-way
    chosen: "VoiceConfig keeps its five fields. domain/tts.py adds a frozen VoiceAvailability(available, reason); TtsService.list_voices returns each VoiceConfig paired with its VoiceAvailability, and the /tts/voices route maps the pair to VoiceOut available/reason. No test amendment, no spec-01 change; the MEU-74 file set and ACs are unchanged."
    source_tag: Human-approved
    precedents: ["tests/unit/test_domain.py:324,553-554,607-610 — exact VoiceConfig field inventory", "docs/build-plan/01-domain-layer.md:364 — VoiceConfig fields"]
    research: { engine: none, sources: [] }
    reasoning: "Availability depends on the runtime (espeak present or not), while VoiceConfig is the static catalog row the spec fixes. A separate value keeps the domain inventory test and spec 01 true, and needs no new TEST_AMENDMENTS entry."
    human_message_reference: "USER_EXPLICIT 2026-10-15 'Separate value (Recommended)' (AskUserQuestion, census S2)"
  - id: D-90
    stage: execution
    question: "Row 2: TA-3a names test_tts_assets.py:597-610, but line 611 asserts the message of the failure TA-3a replaces. Widen the range or leave 611 failing?"
    resolution: autonomous
    class: two-way
    chosen: "Widen TA-3a to 597-611. The forced FakeSession.run failure is a non-domain 500, sent through raise_server_exceptions=False, and the failed job id is read from tts_jobs."
    source_tag: Local Canon
    precedents: ["docs/execution/plans/2026-10-14-tts-engine-runtime/walkthrough.md §Execution amendments Row 2 — TA-3a range"]
    research: { engine: none, sources: [] }
    reasoning: "Line 611 checks the error text of the exact failure being replaced, so it must change with 603-610. The plan's range stopped one line short. No AC or new TA id changes, and ta-check enforces the new range."
  - id: D-91
    stage: execution
    question: "Stop condition S1 fired during row 2: the branch was fast-forwarded to c72fc44, the Session 31 merge. How do the baseline and COUNT_FLOORS follow?"
    resolution: autonomous
    class: two-way
    chosen: "Re-point baseline.sha to c72fc44, re-derive COUNT_FLOORS as 800 / 137 / 655, and move the prereq S1 guard to c72fc44."
    source_tag: Local Canon
    precedents: ["docs/execution/plans/2026-10-14-tts-engine-runtime/walkthrough.md §Execution amendments Row 2 S1 — measurements and receipts"]
    research: { engine: none, sources: [] }
    reasoning: "No MEU-73 product file had changed yet, so ta-check and api-scope must diff against the tree MEU-73 builds on. The floors are the larger of Session 31's gate and a measurement of the merged tree."
  - id: D-92
    stage: execution
    question: "AC-73.10 Downloading tests flaked because a refetch issued while the first fetch is in flight is deduped into it. Is a setup change allowed?"
    resolution: autonomous
    class: two-way
    chosen: "Add the setup helper waitForRuntimeDownloading() before the state flip. No assertion or expected value changes."
    source_tag: Local Canon
    precedents: ["AGENTS.md — assertions immutable in Green; fixture repairs may fix setup"]
    research: { engine: none, sources: [] }
    reasoning: "The flipped state otherwise arrives at the next 1 s poll, just past vi.waitFor's 1 s default. Only the setup is synchronised, and the assertions are untouched."
  - id: D-93
    stage: execution
    question: "The useEffect-keyed settle hook missed Downloading to Failed in about 3 of 5 runs. Keep it or change the mechanism?"
    resolution: autonomous
    class: two-way
    chosen: "useRefreshDependenciesOnSettle subscribes to QueryCache 'updated' events for the runtime query and invalidates on a Downloading exit."
    source_tag: Local Canon
    precedents: ["ui/src/renderer/src/features/tts/useTtsJob.ts — useRefreshDependenciesOnSettle"]
    research: { engine: none, sources: [] }
    reasoning: "When React batches two runtime results into one render, Downloading is never rendered. That is a real product race, so the cache event stream is the reliable source. The test passed 6/6 consecutive runs after the change."
  - id: D-94
    stage: execution
    question: "pyright rejects a torch tensor for KPipeline's voice parameter, which is annotated str | None. How should the PyTorch voice be typed?"
    resolution: autonomous
    class: two-way
    chosen: "Type the (510, 1, 256) tensor Any at the call site, with a comment citing kokoro load_voice."
    source_tag: Research-backed
    precedents: ["kokoro pipeline.py:157-158 — load_voice returns a FloatTensor argument unchanged"]
    research: { engine: none, sources: [] }
    reasoning: "The runtime accepts the tensor; only the annotation is narrow. A cast at the one call site keeps pyright at 0 errors without a suppression comment. KPipeline is removed in MEU-72 anyway."
  - id: D-95
    stage: execution
    question: "Row 5 census S2 (missed at row 1): tests/e2e/test_api_tts_models.py:156-161 (AC-16.7) asserts the exact /tts/voices row as four keys, but AC-74.3 and spec 03 add available/reason to every row, and the file is not in TEST_AMENDMENTS. How does MEU-74 handle it?"
    resolution: human
    class: two-way
    chosen: "Add TA-14: the AC-16.7 expected dict gains \"available\": True, \"reason\": None. Additive only; the VOICES_FACADE call count, the lang_code ban and the route source scans are unchanged. The file joins the MEU-74 Files Modified table."
    source_tag: Human-approved
    precedents: ["tests/e2e/test_api_tts_models.py:150-167 — AC-16.7 VOICES_FACADE", "docs/build-plan/03-service-layer.md:451 — every /tts/voices row carries available/reason", "D-89"]
    research: { engine: none, sources: [] }
    reasoning: "AC-16.7's control is the facade (public list_voices called, no lang_code); the exact-dict equality is incidental. Omitting the fields on available rows would contradict AC-74.3 'both fields on every row'."
    human_message_reference: "USER_EXPLICIT 2026-10-15 'Add TA-14 (Recommended)' (AskUserQuestion, census S2b)"
  - id: D-96
    stage: execution
    question: "Row 5: AC-74.7 says the eSpeak NG releases link 'opens through the existing external-link path', but the app has none (main denies window.open and navigation; the preload exposes openPath, showItemInFolder and clipboard IPC only). How does the guidance link work?"
    resolution: human
    class: two-way
    chosen: "Show the releases URL as selectable text plus a 'Copy link' button that calls the existing window.api.writeClipboardText. Renderer-only (SettingsPage.tsx); no new IPC channel or main-process surface. AC-74.7 is reworded from 'opens' to 'copies'."
    source_tag: Human-approved
    precedents: ["ui/src/main/index.ts:484-489 — setWindowOpenHandler deny and will-navigate block", "ui/src/main/preload.ts:51-53 — openPath, showItemInFolder, writeClipboardText", "ui/src/renderer/src/features/settings/SettingsPage.tsx:948 — 'Copy log path' uses writeClipboardText"]
    research: { engine: none, sources: [] }
    reasoning: "An openExternal channel would add three files outside the MEU-74 Files Modified table and a new main-process surface for one link. Copying uses a control Settings already has."
    human_message_reference: "USER_EXPLICIT 2026-10-15 'URL + Copy link (Recommended)' (AskUserQuestion, eSpeak link)"
  - id: D-97
    stage: execution
    question: "Row 6: ESPEAK_G2P raises TtsRuntimeError, and the red-74 tests import it with the adapter, but no TtsRuntimeError exists and packages/core/src/avkit_core/domain/errors.py is not in the MEU-74 Files Modified table. Where is it defined?"
    resolution: autonomous
    class: two-way
    chosen: "avkit_infra/tts/espeak.py defines class TtsRuntimeError(DomainError). It is a DomainError subclass, so the API's existing DomainError handling covers it, and errors.py is not touched."
    source_tag: Local Canon
    precedents: ["implementation-plan.md ESPEAK_G2P and AC-74.6 — 'raises TtsRuntimeError(\"espeak-ng failed: …\")'", "packages/core/src/avkit_core/domain/errors.py — DomainError base"]
    research: { engine: none, sources: [] }
    reasoning: "The contract names the error but not its module. Defining it beside its only raiser stays inside the Files Modified fence. MEU-72 may move it to domain/errors.py if the ONNX path raises it too, which its own Files Modified table governs."
  - id: D-98
    stage: execution
    question: "Row 6: the ESPEAK_MAP_PARITY test ends with assert 'misaki.espeak' not in sys.modules. Importing avkit_infra.tts.espeak runs the avkit_infra.tts package init, which imports KokoroAdapter, then kokoro, whose pipeline.py does 'from misaki import en, espeak'. The assertion can never pass in this process. How is it corrected?"
    resolution: human
    class: two-way
    chosen: "Replace the sys.modules line with an AST scan of avkit_infra/tts/espeak.py: no Import or ImportFrom of misaki, phonemizer or espeakng_loader. The two table-parity assertions are unchanged. The runtime sys.modules check stays with MEU-72 IMPORT_HYGIENE, which runs in a fresh interpreter after the adapter stops importing kokoro."
    source_tag: Human-approved
    precedents: [".venv/Lib/site-packages/kokoro/pipeline.py:5 — 'from misaki import en, espeak'", "packages/infrastructure/src/avkit_infra/tts/__init__.py:3 — imports KokoroAdapter", "AGENTS.md:57 — a proven wrong expectation needs human authorization", "implementation-plan.md IMPORT_HYGIENE"]
    research: { engine: none, sources: [] }
    reasoning: "D-71's control is that av-kit's adapter never imports misaki.espeak. A process-wide sys.modules check measures whatever else the pytest process imported, so it fails for reasons outside espeak.py. The import scan tests the adapter's own source directly."
    human_message_reference: "USER_EXPLICIT 2026-10-15 'AST import scan (Recommended)' (AskUserQuestion, parity fix)"
  - id: D-99
    stage: execution
    question: "Row 7: VoiceOut gains the optional boolean available, and ui typecheck then fails at TTSPage.tsx:126. That line casts useVoices() rows, typed Array<Record<string, string>> in useTtsJob.ts, to VoiceOut[], and a string record no longer overlaps a type with a boolean field. TTSPage.tsx and useTtsJob.ts are not in the MEU-74 Files Modified table. How is it fixed?"
    resolution: autonomous
    class: two-way
    chosen: "useTtsJob.ts useVoices types the /tts/voices rows as VoiceOut[] (type-only import from tts-voices.ts). TTSPage.tsx is unchanged; its cast becomes a no-op. useTtsJob.ts is already a plan file (MEU-73) and joins the MEU-74 Files Modified table."
    source_tag: Local Canon
    precedents: ["implementation-plan.md MEU-74 Files Modified — tts-voices.ts 'available?: boolean / reason?: … types'", "ui/src/renderer/src/features/tts/TTSPage.tsx:126 — the VoiceOut[] cast", "D-95 — a file added to the MEU-74 Files Modified table"]
    research: { engine: none, sources: [] }
    reasoning: "The plan fixes the VoiceOut field types, so the compile break is a direct consequence of the plan, not a design choice. Typing the query at its source is a one-line, type-only change with no runtime effect. The alternative, editing TTSPage.tsx, touches a file no plan table lists."
  - id: D-100
    stage: execution
    question: "Row 13: the eSpeak NG guidance 'Copy link' button (D-96) has no data-testid, and the plan's NEW_TESTIDS lists only tts-espeak-row, tts-espeak-guidance and voice-unavailable-reason. The GUI canon requires a test id on every interactive element and an index row for every user-visible action. Is it added?"
    resolution: autonomous
    class: two-way
    chosen: "Add data-testid=\"tts-espeak-copy-link-btn\" to the button in SettingsPage.tsx, and register TTS_ESPEAK_COPY_LINK_BTN in ui/tests/e2e/test-ids.ts after the MEU-74 block. No behaviour or assertion changes; both files are already in the MEU-74 Files Modified table. No gui-actions-index row is added: the AC-23.20 audit resolves every settings row's IPC cell through gui-actions-audit.test.ts:66-77, which maps no writeClipboardText cell, so a settings:copy_espeak_link row fails it. Extending that resolver is a test edit outside TEST_AMENDMENTS. The existing Settings 'Copy log path' button has no index row either, for the same reason. Both go to closeout as one follow-up."
    source_tag: Local Canon
    precedents: ["docs/build-plan/06-gui.md:1259 and :1275 — every interactive element uses a test-ids.ts constant", "docs/build-plan/gui-actions-index.md:111 — a page is incomplete if a button has no testid", "ui/tests/unit/gui-actions-audit.test.ts:66-77 — resolveIpcChannel has no writeClipboardText mapping", "D-96"]
    research: { engine: none, sources: [] }
    reasoning: "D-96 added the button after NEW_TESTIDS was fixed, so the list missed it. The canon rule is explicit, the change is one attribute plus one registry line, and the AC-74.7 test still finds the button by role and name. Leaving it would ship a control the GUI audit rules call incomplete. The index row is the one part that needs a test change, so it is deferred rather than forced."
```

## Research References

- `C:/Temp/av-kit/s32-hf-onnx.json`, `s32-hf-onnx10.json`: Hugging Face API listings for both ONNX repos (2026-10-14).
- `C:/Temp/av-kit/s32-onnx-vocab-compare.txt`: the vocab comparison with sha256 of each source.
- `C:/Temp/av-kit/s32-meu-stats.txt`: `meu_status.py stats` (91 MEUs, 67 approved, 1 closed, 23 pending).
- URLs as cited in the decision log.

## Planning receipts

| Receipt | What |
|---------|------|
| `C:/Temp/av-kit/s32-meu-stats.txt` | Step 1 discovery |
| `C:/Temp/av-kit/s32-grouping.md` | the grouping excerpt read |
| `C:/Temp/av-kit/s32-onnx-vocab-compare.txt` | D-73 evidence |
| `C:/Temp/av-kit/s32-plan-static.txt` | `plan_checks.py static` + `selftest` before dispatch |
| `C:/Temp/av-kit/s32-plan-dispatch-r1.txt` | round-1 Codex dispatch; the ledger refused its verdict (no round recorded) |
| `C:/Temp/av-kit/census-s32-*.txt` | round-1 correction census: stale strings (0 hits apart from the D-87 quote), `legacy-onnx-tests` (TA-10..TA-13), `jz-voices` / `espeak-voices` (TA-9), `voice-rows` (unaffected renderer and MCP fixtures), `gpl-buildplan` |

## Validation stage contract

Checks bind to PROFILE D6 through `validate-task.ps1`:

- **Static:** `py-types`, `py-lint`, `ui-types`, `ui-lint`, `mcp-types`, `plan-static`.
- **Targeted:** `red-*`, `green-*`, `gate73`, `gate74`, `gate72`.
- **One fresh full gate** (`windows-gate`, 17 stages) **and the runtime smoke** (`package-smoke`) before the execution review.

Input identity is `WORKTREE_IDENTITY` plus the `ui`/`mcp-server` lockfile and `uv.lock` hashes, the Electron version and the Node version recorded in each result JSON. `windows-gate-check` refuses a mismatch, so any edit under `GATED_PATHS` after the gate reopens it. Partial or cached output does not satisfy the gate, and nothing is reused between attempts (receipts are deleted at stage start).

Evidence is `evidence.v1` in each MEU handoff and in `walkthrough.md`. D9 = yes: MEU state updates happen at H1-3 and H2-2.
