# Round 1 corrections — blast-radius census (plan-corrections Step 5c)

This is the raw, unfiltered sweep output (`rg -F -n` over `implementation-plan.md`, `task.md`, `local-requests.md`, `validate-task.sh`, `validate-task.ps1` and `tts_live_check.py`), followed by one disposition per hit. `rg` exit 1 means no match. For an old value that is the desired outcome; for a new value it would mean the edit did not land.

**Summary.** Blast-radius census: 15 values changed (C1–C15); 29 sweeps (25 in Pass 1, 4 in the post-fix Pass 2); 57 hit lines (53 + 4). 5 sites were updated (plan:122, plan:132, the AC-64.6 wording, task:50, and the `gated` list at sh:622); the remaining hits are confirmed consistent, per the table below.

## Pass 1 (raw receipt)

```text
=== [C1-old] rg -F -n "REQUIRED_TTS_ASSETS(variant, voice)"
--- rg exit 1
=== [C1-new] rg -F -n "REQUIRED_TTS_ASSETS("
docs/execution/plans/2026-09-30-tts-repair/implementation-plan.md:119:| `REQUIRED_TTS_ASSETS(variant, voice, enabled_steps)` | `{ONNX_VOCAB}` for every variant (D-8), plus `SPACY_MODEL` when `voice.voice_id[0] in SPACY_LANG_CODES` **or** `enabled_steps ∩ SPACY_STEPS ≠ ∅` (D-10). `KOKORO_LANG_CODES` is defined in the core domain as the nine prefixes `a b e f h i j p z`. A pytest parity assertion ties it to the keys of `avkit_infra/tts/voices.py:68-78` `LANG_BY_PREFIX` (core cannot import infra). A lang code outside it raises `ValidationError`, so the function fails closed. | D-8, D-10 |
docs/execution/plans/2026-09-30-tts-repair/implementation-plan.md:193:| AC-62.9 | integration | `TTSService.generate`, after voice validation (`tts.py:129-132`) and **before** the job row is created (`:135`), raises `ASSET_MISSING_ERROR` for the first missing member of `REQUIRED_TTS_ASSETS(loaded variant, voice, enabled_steps)`, in `TtsAsset` declaration order. `POST /tts/generate` → 409 whose message names the asset. | Spec 03:419 | With `SPACY_MODEL` missing and an `am_*` voice: 409 naming `tts_spacy_model`; zero `tts_jobs` rows; no file under `tts.output_path`; `KPipeline` constructed 0 times; a spy on `spacy.cli.download` called 0 times. A `jf_*` (`j`) voice with `enabled_steps=["chunk"]` and spaCy missing → 409 naming `tts_spacy_model`, with zero rows (the default-GUI path; `prepare._chunk` is never reached). The same voice with `enabled_steps=[]` passes the check (no spaCy needed). |
--- rg exit 0
=== [C2-old] rg -F -n "en_core_web_sm"
docs/execution/plans/2026-09-30-tts-repair/implementation-plan.md:22:  - Two Kokoro runtime assets become managed downloads (D-22): the `config.json` vocab/config and spaCy `en_core_web_sm`.
docs/execution/plans/2026-09-30-tts-repair/implementation-plan.md:121:| `SPACY_MODEL_PIN` | `{"3.8": WheelPin(name=SPACY_MODEL, version="3.8.0", url="https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl", sha256="1932429db727d4bff3deed6b34cfc05df17794f4a52eeb26cf8928f7c1a0fb85")}`, keyed by the installed spaCy `major.minor`. `SPACY_MODEL` is the existing core constant `avkit_core.services.prepare.SPACY_MODEL` (`prepare.py:9`), never restated. The lock has spaCy 3.8.15 (`uv.lock:2399`); the wheel METADATA says `spaCy >=3.8.0,<3.9.0`. The sha256 was measured on 2026-09-30: a 12 806 118-byte download from that URL, 35 members, `en_core_web_sm-3.8.0.dist-info/` present. | Human-approved D-22 ("wheel URL pinned to the installed spaCy major.minor"); Research-backed (download + METADATA read at plan time) |
docs/execution/plans/2026-09-30-tts-repair/implementation-plan.md:122:| `SPACY_INSTALL_DIR` | `{tts.models_directory}/spacy/en_core_web_sm-3.8.0/`. This is the wheel's contents extracted as-is, including `.dist-info`, so `spacy.util.is_package` and `spacy.load("en_core_web_sm")` both resolve once the directory is on `sys.path`. | D-11 |
docs/execution/plans/2026-09-30-tts-repair/implementation-plan.md:536:    research: { engine: native, sources: ["kokoro 0.9.4 pipeline.py:106-113 — lang 'a'/'b' build misaki en.G2P", "misaki 0.9.4 en.py:497-503 — G2P loads en_core_web_sm and calls spacy.cli.download when absent"] }
docs/execution/plans/2026-09-30-tts-repair/implementation-plan.md:540:    question: "How does a managed en_core_web_sm become importable without pip at runtime?"
docs/execution/plans/2026-09-30-tts-repair/implementation-plan.md:546:    research: { engine: native, sources: ["https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl — downloaded 2026-09-30, sha256 1932429d…fb85, 35 members incl. .dist-info, METADATA spaCy >=3.8.0,<3.9.0", "misaki 0.9.4 en.py:500 — readiness = spacy.util.is_package, satisfied by .dist-info on sys.path"] }
docs/execution/plans/2026-09-30-tts-repair/implementation-plan.md:615:- spaCy model wheel: `https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl` (sha256 above; METADATA spaCy `>=3.8.0,<3.9.0`).
--- rg exit 0
=== [C2-new] rg -F -n "SPACY_MODEL"
docs/execution/plans/2026-09-30-tts-repair/implementation-plan.md:115:| `TTS_ASSETS` | Closed `StrEnum` `TtsAsset` in `avkit_core/domain/tts.py` with exactly `ONNX_VOCAB = "tts_onnx_vocab"` and `SPACY_MODEL = "tts_spacy_model"`. Every `match` over it is exhaustive (`assert_never`), so pyright fails the build when a member is added. | Spec 03:418 (row names) |
docs/execution/plans/2026-09-30-tts-repair/implementation-plan.md:119:| `REQUIRED_TTS_ASSETS(variant, voice, enabled_steps)` | `{ONNX_VOCAB}` for every variant (D-8), plus `SPACY_MODEL` when `voice.voice_id[0] in SPACY_LANG_CODES` **or** `enabled_steps ∩ SPACY_STEPS ≠ ∅` (D-10). `KOKORO_LANG_CODES` is defined in the core domain as the nine prefixes `a b e f h i j p z`. A pytest parity assertion ties it to the keys of `avkit_infra/tts/voices.py:68-78` `LANG_BY_PREFIX` (core cannot import infra). A lang code outside it raises `ValidationError`, so the function fails closed. | D-8, D-10 |
docs/execution/plans/2026-09-30-tts-repair/implementation-plan.md:121:| `SPACY_MODEL_PIN` | `{"3.8": WheelPin(name=SPACY_MODEL, version="3.8.0", url="https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl", sha256="1932429db727d4bff3deed6b34cfc05df17794f4a52eeb26cf8928f7c1a0fb85")}`, keyed by the installed spaCy `major.minor`. `SPACY_MODEL` is the existing core constant `avkit_core.services.prepare.SPACY_MODEL` (`prepare.py:9`), never restated. The lock has spaCy 3.8.15 (`uv.lock:2399`); the wheel METADATA says `spaCy >=3.8.0,<3.9.0`. The sha256 was measured on 2026-09-30: a 12 806 118-byte download from that URL, 35 members, `en_core_web_sm-3.8.0.dist-info/` present. | Human-approved D-22 ("wheel URL pinned to the installed spaCy major.minor"); Research-backed (download + METADATA read at plan time) |
docs/execution/plans/2026-09-30-tts-repair/implementation-plan.md:123:| `SPACY_READY` | `spacy.util.is_package(SPACY_MODEL)` is true after `activate_spacy_dir(settings)`. This is the same predicate misaki checks before it would run `spacy.cli.download` (misaki `en.py:500-501`). | Research-backed (misaki source) |
docs/execution/plans/2026-09-30-tts-repair/implementation-plan.md:173:| File import: spaCy wheel | `install_spacy_wheel` in `avkit_infra/tts/assets.py` | sha256 == `SPACY_MODEL_PIN.sha256`. Every zip member path must be relative, contain no `..` segment, not be absolute or drive-qualified, and resolve inside a temporary extraction dir. The dir is moved into place with `os.replace` only after full success. | Any violation → `ModelDownloadError`, no `SPACY_INSTALL_DIR` created (atomicity: extract to `…/spacy/.tmp-<uuid>`, then `os.replace`). **Existing destination (`SPACY_INSTALL_EXISTING`):** when `SPACY_READY` is already true, `download(asset=SPACY_MODEL)` raises `ConflictError("tts asset already ready: tts_spacy_model")` → 409 and fetches nothing. When `SPACY_INSTALL_DIR` exists but `SPACY_READY` is false (a corrupt install), the worker `shutil.rmtree`s the stale directory after sha256 verification and before `os.replace`. Both run inside the download worker that `ModelService._lock` admits one at a time. `assets.py` never imports `huggingface_hub` (AC-9.12, `tests/integration/test_tts_models.py:641-661`); the vocab fetch stays in `model_manager/manager.py`. |
docs/execution/plans/2026-09-30-tts-repair/implementation-plan.md:190:| AC-62.6 | integration | `ModelService.download(asset=SPACY_MODEL)` does the following: picks `SPACY_MODEL_PIN[spacy major.minor]`; streams the URL through an injected `fetch` (production: `urllib.request` with the process proxy environment); verifies sha256; extracts under the Boundary Inventory wheel rules; `os.replace`s into `SPACY_INSTALL_DIR`; calls `activate_spacy_dir`; ends with `SPACY_READY` true. Runtime `asset="tts_spacy_model"` and `state="Downloading"` while it runs, then `Idle`. | Human-approved D-22 (03:417); D-11 | Three negatives: (a) a sha256 mismatch ends `Failed` with an `error_message` containing `sha256`, and `SPACY_INSTALL_DIR` does not exist; (b) an unpinned spaCy minor (`"3.9"` patched in) gives `Failed` with `no pinned {SPACY_MODEL} for spaCy 3.9`, and `fetch` is never called; (c) a wheel member `../evil.py` gives `Failed`, nothing is written outside the temp dir, and the temp dir is removed; (d) `SPACY_INSTALL_EXISTING`: with `SPACY_READY` true, `POST /models/download {asset: "tts_spacy_model"}` → 409 and `fetch` call count 0; with a stale `SPACY_INSTALL_DIR` (dist-info present, package dir missing), a download replaces it and ends `SPACY_READY` true. |
docs/execution/plans/2026-09-30-tts-repair/implementation-plan.md:193:| AC-62.9 | integration | `TTSService.generate`, after voice validation (`tts.py:129-132`) and **before** the job row is created (`:135`), raises `ASSET_MISSING_ERROR` for the first missing member of `REQUIRED_TTS_ASSETS(loaded variant, voice, enabled_steps)`, in `TtsAsset` declaration order. `POST /tts/generate` → 409 whose message names the asset. | Spec 03:419 | With `SPACY_MODEL` missing and an `am_*` voice: 409 naming `tts_spacy_model`; zero `tts_jobs` rows; no file under `tts.output_path`; `KPipeline` constructed 0 times; a spy on `spacy.cli.download` called 0 times. A `jf_*` (`j`) voice with `enabled_steps=["chunk"]` and spaCy missing → 409 naming `tts_spacy_model`, with zero rows (the default-GUI path; `prepare._chunk` is never reached). The same voice with `enabled_steps=[]` passes the check (no spaCy needed). |
docs/execution/plans/2026-09-30-tts-repair/implementation-plan.md:227:| `packages/infrastructure/src/avkit_infra/tts/assets.py` | new | `resolve_vocab_path`, `validate_vocab_file`, `SPACY_MODEL_PIN`, `install_spacy_wheel`, `activate_spacy_dir`, `TtsAssetAdapter` |
docs/execution/plans/2026-09-30-tts-repair/implementation-plan.md:497:| S5 | `SPACY_MODEL_PIN` sha256 or URL no longer matches upstream during execution | Stop. This is a one-way-door re-pin decision for the human. |
--- rg exit 0
=== [C3-old] rg -F -n ".agent/model-registry.local.json docs/execution"
--- rg exit 1
=== [C3-new] rg -F -n "openapi.committed.json"
docs/execution/plans/2026-09-30-tts-repair/validate-task.sh:432:    run s27-openapi-final uv run python tools/export_openapi.py --check openapi.committed.json
docs/execution/plans/2026-09-30-tts-repair/validate-task.sh:444:    run s27-62-openapi uv run python tools/export_openapi.py --check openapi.committed.json
docs/execution/plans/2026-09-30-tts-repair/validate-task.sh:540:    run s27-gate-openapi uv run python tools/export_openapi.py --check openapi.committed.json
docs/execution/plans/2026-09-30-tts-repair/validate-task.sh:561:    run s27-api-openapi uv run python tools/export_openapi.py --check openapi.committed.json
docs/execution/plans/2026-09-30-tts-repair/validate-task.sh:622:gated = ["ui", "packages", "mcp-server", "tests", "tools", "pyproject.toml", "uv.lock", "openapi.committed.json",
docs/execution/plans/2026-09-30-tts-repair/validate-task.ps1:102:        @('openapi',          @('uv', 'run', 'python', 'tools/export_openapi.py', '--check', 'openapi.committed.json')),
docs/execution/plans/2026-09-30-tts-repair/task.md:42:| 5 | Implement the MEU-62 API, wiring, MCP and Settings card. Run the OpenAPI two-step: `--check` fails with the intended drift, then `-o`, then `--check` passes. | coder | API/MCP/UI source; `openapi.committed.json` | `bash docs/execution/plans/2026-09-30-tts-repair/validate-task.sh green62 > "${RECEIPTS_DIR}/s27-62-green.txt" 2>&1; code=$?; tail -n 25 "${RECEIPTS_DIR}/s27-62-green.txt"; exit $code` | 4 | shared | source files; `s27-openapi-*` receipts | `avkit_builder` | `[ ]` |
docs/execution/plans/2026-09-30-tts-repair/implementation-plan.md:132:| `GATED_PATHS` | The executable copy is `GATED` in `validate-task.sh` `windows-gate-check`, and `plan_checks.py static` asserts it equals this list: `ui packages mcp-server tests tools pyproject.toml uv.lock openapi.committed.json docs/BUILD_PLAN.md docs/build-plan .agent/model-registry.local.json .agent/model-registry.local.yaml .agent/context/meu-status.yaml .agent/context/grouping docs/execution/plans/2026-09-30-tts-repair/validate-task.ps1 docs/execution/plans/2026-09-30-tts-repair/tts_live_check.py`. That is the code, plus the files the gate stages read: `openapi` reads `openapi.committed.json`; `state-render` reads `meu-status.yaml` and `BUILD_PLAN.md`; Vitest reads `docs/build-plan/*.md` (e.g. `gui-actions-audit.test.ts:12`, `layout-canon.test.ts`); pytest reads the registry overlay and grouping. | cloud-local §3.3 item 2 |
docs/execution/plans/2026-09-30-tts-repair/implementation-plan.md:233:| `openapi.committed.json` | modify | regenerated only after `--check` reports drift (G8) |
docs/execution/plans/2026-09-30-tts-repair/implementation-plan.md:247:| UI → `POST /models/download` | `downloadBody` zod in `tts-commands.ts` (next to `loadBody`, `:44-49`) | `z.union([z.object({variant_id: z.string().min(1)}).strict(), z.object({asset: z.enum(TTS_ASSET_WIRES)}).strict()])`. `TTS_ASSET_WIRES` is a UI mirror, pinned to the MCP/Python values by a Vitest parity assertion that reads `openapi.committed.json`. | `.strict()`. The server still validates (422). |
docs/execution/plans/2026-09-30-tts-repair/implementation-plan.md:443:uv run python tools/export_openapi.py --check openapi.committed.json > "$RECEIPTS_DIR/s27-openapi-check.txt" 2>&1; echo "exit=$?"
docs/execution/plans/2026-09-30-tts-repair/implementation-plan.md:445:uv run python tools/export_openapi.py -o openapi.committed.json > "$RECEIPTS_DIR/s27-openapi-regen.txt" 2>&1; echo "exit=$?"
--- rg exit 0
=== [C4-old] rg -F -n "attempt 1"
--- rg exit 1
=== [C4-old2] rg -F -n "attempt-1"
--- rg exit 1
=== [C5-old] rg -F -n "MEU-56 → MEU-63/64"
--- rg exit 1
=== [C5-old2] rg -F -n "TT 3/9/12"
--- rg exit 1
=== [C5-new] rg -F -n "AC-50.4"
docs/execution/plans/2026-09-30-tts-repair/implementation-plan.md:389:   - The TT rows inside `<!-- BEGIN MOCKUP INVENTORY -->` … `<!-- END … -->` (`:156-318`) are **not** edited. They are the Phase 11 canon lock that `ui/tests/unit/layout-canon.test.ts` AC-50.4 (`:43-47,130-145`) parses: owner `^MEU-5[2-8]$`, label and disposition equal to mockup §05, and row count. Row 13 re-runs `layout-canon.test.ts` after the edit to prove it (Review R1 F2).
docs/execution/plans/2026-09-30-tts-repair/task.md:50:| 13 | Hub reconciliation (plan §BUILD_PLAN.md Audit items 1–3) and new known issues.<br>• Amend 03 §TTS runtime assets per D-8 to D-14 and AC-62.11.<br>• Amend 11: fix the `:111` registry names, and add prose pointers in the two §Residuals sections. The mockup-inventory TT rows are **not** edited (the AC-50.4 lock).<br>• Amend 07-distribution line 9 and §Kokoro / models.<br>• Add `TTS-PACKAGED-RUNTIME-EXCLUDED`, `TTS-VOICE-PACK-LAZY-FETCH` and `TTS-NON-ENGLISH-G2P-DEPS` through `tools/issue_triage.py add`, then render.<br>• Re-run the doc-reading Vitest (`layout-canon`, `queue-canon`). | orchestrator | hub edits; 3 new issues | `bash docs/execution/plans/2026-09-30-tts-repair/validate-task.sh hub > "${RECEIPTS_DIR}/s27-hub.txt" 2>&1; code=$?; tail -n 20 "${RECEIPTS_DIR}/s27-hub.txt"; exit $code` | 12 | shared | `docs/build-plan/03…`, `11…`, `07…`; `known-issues.yaml` / `.md` | `avkit_coordinator` | `[ ]` |
docs/execution/plans/2026-09-30-tts-repair/validate-task.sh:507:    # The mockup-inventory TT rows stay untouched (AC-50.4 lock); prove the doc-reading suites still pass.
--- rg exit 0
=== [C6-old] rg -F -n "console\.log|"
--- rg exit 1
=== [C6-new] rg -F -n "console\.log\("
docs/execution/plans/2026-09-30-tts-repair/validate-task.ps1:83:    $auditPattern = 'TODO|FIXME|NotImplementedError|transition-all|bg-\[#|console\.log\(|except Exception:\s*pass|# type: ignore'
docs/execution/plans/2026-09-30-tts-repair/validate-task.sh:315:PREFIX_AUDIT='TODO|FIXME|NotImplementedError|transition-all|bg-\[#|console\.log\(|except Exception:\s*pass|# type: ignore'
--- rg exit 0
=== [C7-old] rg -F -n "known-issues.yaml >"
--- rg exit 1
=== [C8-old] rg -F -n "enabled_steps=[]"
docs/execution/plans/2026-09-30-tts-repair/implementation-plan.md:193:| AC-62.9 | integration | `TTSService.generate`, after voice validation (`tts.py:129-132`) and **before** the job row is created (`:135`), raises `ASSET_MISSING_ERROR` for the first missing member of `REQUIRED_TTS_ASSETS(loaded variant, voice, enabled_steps)`, in `TtsAsset` declaration order. `POST /tts/generate` → 409 whose message names the asset. | Spec 03:419 | With `SPACY_MODEL` missing and an `am_*` voice: 409 naming `tts_spacy_model`; zero `tts_jobs` rows; no file under `tts.output_path`; `KPipeline` constructed 0 times; a spy on `spacy.cli.download` called 0 times. A `jf_*` (`j`) voice with `enabled_steps=["chunk"]` and spaCy missing → 409 naming `tts_spacy_model`, with zero rows (the default-GUI path; `prepare._chunk` is never reached). The same voice with `enabled_steps=[]` passes the check (no spaCy needed). |
--- rg exit 0
=== [C8-old2] rg -F -n ", [], TTSSourceKind"
--- rg exit 1
=== [C9-old] rg -F -n "2 new issues"
--- rg exit 1
=== [C9-new] rg -F -n "TTS-NON-ENGLISH-G2P-DEPS"
docs/execution/plans/2026-09-30-tts-repair/implementation-plan.md:366:| Non-English G2P runtime pieces: `e/f/h/i/p` voices use `misaki.espeak.EspeakG2P` (needs espeak-ng), and `j`/`z` need the `misaki[ja]` / `[zh]` extras (kokoro `pipeline.py:114-134`) | out-of-scope | — | 03:414-421 lists exactly two managed assets (D-22). Row 13 files `TTS-NON-ENGLISH-G2P-DEPS`. |
docs/execution/plans/2026-09-30-tts-repair/task.md:50:| 13 | Hub reconciliation (plan §BUILD_PLAN.md Audit items 1–3) and new known issues.<br>• Amend 03 §TTS runtime assets per D-8 to D-14 and AC-62.11.<br>• Amend 11: fix the `:111` registry names, and add prose pointers in the two §Residuals sections. The mockup-inventory TT rows are **not** edited (the AC-50.4 lock).<br>• Amend 07-distribution line 9 and §Kokoro / models.<br>• Add `TTS-PACKAGED-RUNTIME-EXCLUDED`, `TTS-VOICE-PACK-LAZY-FETCH` and `TTS-NON-ENGLISH-G2P-DEPS` through `tools/issue_triage.py add`, then render.<br>• Re-run the doc-reading Vitest (`layout-canon`, `queue-canon`). | orchestrator | hub edits; 3 new issues | `bash docs/execution/plans/2026-09-30-tts-repair/validate-task.sh hub > "${RECEIPTS_DIR}/s27-hub.txt" 2>&1; code=$?; tail -n 20 "${RECEIPTS_DIR}/s27-hub.txt"; exit $code` | 12 | shared | `docs/build-plan/03…`, `11…`, `07…`; `known-issues.yaml` / `.md` | `avkit_coordinator` | `[ ]` |
docs/execution/plans/2026-09-30-tts-repair/validate-task.sh:501:for i in ("TTS-PACKAGED-RUNTIME-EXCLUDED", "TTS-VOICE-PACK-LAZY-FETCH", "TTS-NON-ENGLISH-G2P-DEPS"):
--- rg exit 0
=== [C10-old] rg -F -n "only in `tests/integration/test_tts_assets.py`"
--- rg exit 1
=== [C11-old] rg -F -n "fails on the pre-change layout"
--- rg exit 1
=== [C11-new] rg -F -n "VOICE_CATALOG_FIXTURE"
docs/execution/plans/2026-09-30-tts-repair/implementation-plan.md:130:| `VOICE_CATALOG_FIXTURE` | `ui/tests/e2e/fixtures/tts-voices.json`: the full production voice list (54 voices, `VOICE_COUNT`, `avkit_infra/tts/voices.py:80`) in the `GET /tts/voices` item shape. It is generated once in row 10 from `list_voice_configs()`. A pytest parity test (`tests/unit/test_tts_voice_fixture.py`) fails if the file diverges from `list_voice_configs()`. `installTtsSeam` takes an optional `voices` argument, which the AC-64.6 spec (and only that spec) sets to this fixture. The one-voice default for the other specs is unchanged. | Review R1 F1; Spec 11:124 |
docs/execution/plans/2026-09-30-tts-repair/implementation-plan.md:322:| AC-64.6 | integration | At `DEFAULT_WINDOW`, with the combobox closed and the seam serving `VOICE_CATALOG_FIXTURE`, the bounding box of `speed-slider` and of `format-select` ends at or above `window.innerHeight`, with the page scroll containers at `scrollTop == 0`. The spec title contains `AC-64.6`. | Spec 11:124 | **Red on the pre-change layout:** `red64` runs `require_failed_title AC-64.6 toBeLessThanOrEqual`, so row 10 is not done unless the `AC-64.6` spec itself fails, on its bounding-box `expect`, against the unchanged layout. If it does not go Red with the production-size catalog, apply Stop condition S8. With the combobox **open**, Speed/Format need not be visible (the popup may overlay them). |
docs/execution/plans/2026-09-30-tts-repair/implementation-plan.md:356:| `ui/tests/e2e/fixtures/tts-voices.json` (new), `tests/unit/test_tts_voice_fixture.py` (new) | new | `VOICE_CATALOG_FIXTURE` and its parity test |
docs/execution/plans/2026-09-30-tts-repair/implementation-plan.md:500:| S8 | The `AC-64.6` spec does not go Red on the pre-change layout with `VOICE_CATALOG_FIXTURE` | Stop MEU-64. Record the measured bounding boxes and the `LOCAL_REPRO` R5 result, then present a Decision Brief (for example: the Space rule already holds at the default window, or the overflow needs a state the seam lacks). Never weaken the assertion. |
docs/execution/plans/2026-09-30-tts-repair/validate-task.sh:467:      || fail "VOICE_CATALOG_FIXTURE parity (write the fixture before the Red run)"
--- rg exit 0
=== [C12-old] rg -F -n "English voices"
docs/execution/plans/2026-09-30-tts-repair/implementation-plan.md:98:>    - D-10: spaCy needed on any variant, for English voices or whenever the default-on `chunk` step runs.
docs/execution/plans/2026-09-30-tts-repair/implementation-plan.md:379:   - D-10: spaCy is triggered on the first load of **any** variant, and generation needs it per `REQUIRED_TTS_ASSETS` (English voices, or any voice with the `chunk` step).
--- rg exit 0
=== [C12-new] rg -F -n "SPACY_STEPS"
docs/execution/plans/2026-09-30-tts-repair/implementation-plan.md:118:| `SPACY_STEPS` | `frozenset({"chunk"})`. These are the prepare steps whose implementation loads the spaCy model (`services/prepare.py:150-161` `_chunk`). `chunk` is in `PREPARE_DEFAULT_ON` (`prepare.py:24`; UI `tts-prepare.ts:17-19`), so the GUI default needs spaCy for **every** voice. | Local Canon `services/prepare.py:9,24,150-161,250-251` |
docs/execution/plans/2026-09-30-tts-repair/implementation-plan.md:119:| `REQUIRED_TTS_ASSETS(variant, voice, enabled_steps)` | `{ONNX_VOCAB}` for every variant (D-8), plus `SPACY_MODEL` when `voice.voice_id[0] in SPACY_LANG_CODES` **or** `enabled_steps ∩ SPACY_STEPS ≠ ∅` (D-10). `KOKORO_LANG_CODES` is defined in the core domain as the nine prefixes `a b e f h i j p z`. A pytest parity assertion ties it to the keys of `avkit_infra/tts/voices.py:68-78` `LANG_BY_PREFIX` (core cannot import infra). A lang code outside it raises `ValidationError`, so the function fails closed. | D-8, D-10 |
docs/execution/plans/2026-09-30-tts-repair/implementation-plan.md:533:    chosen: "Any variant's load triggers it (AC-62.7); generation requires it per REQUIRED_TTS_ASSETS — voices whose lang code is in SPACY_LANG_CODES, or any voice when enabled_steps include a SPACY_STEPS member (chunk, default-on)"
--- rg exit 0
=== [C13-old] rg -F -n "R1-R4"
--- rg exit 1
=== [C13-new] rg -F -n "R5"
docs/execution/plans/2026-09-30-tts-repair/implementation-plan.md:500:| S8 | The `AC-64.6` spec does not go Red on the pre-change layout with `VOICE_CATALOG_FIXTURE` | Stop MEU-64. Record the measured bounding boxes and the `LOCAL_REPRO` R5 result, then present a Decision Brief (for example: the Space rule already holds at the default window, or the overflow needs a state the seam lacks). Never weaken the assertion. |
docs/execution/plans/2026-09-30-tts-repair/local-requests.md:24:  R5 TTS-LANGUAGE-VOICE-PICKER-SPACE: TTS page at the default window, HelpCard in its default state, Language = All.
docs/execution/plans/2026-09-30-tts-repair/validate-task.sh:384:for r in ("R1", "R2", "R3", "R4", "R5"):
docs/execution/plans/2026-09-30-tts-repair/validate-task.sh:389:print("PASS LOCAL_REPRO recorded for R1-R5")
--- rg exit 0
```

## Pass 2 — after fixing the Pass 1 findings (raw receipt)

```text
=== [C3-post] rg -F -n "executable copy is"
docs/execution/plans/2026-09-30-tts-repair/implementation-plan.md:132:| `GATED_PATHS` | The executable copy is the `gated` list in `validate-task.sh` `windows-gate-check`, and `plan_checks.py static` asserts it equals this list: `ui packages mcp-server tests tools pyproject.toml uv.lock openapi.committed.json docs/BUILD_PLAN.md docs/build-plan .agent/model-registry.local.json .agent/model-registry.local.yaml .agent/context/meu-status.yaml .agent/context/grouping docs/execution/plans/2026-09-30-tts-repair/validate-task.ps1 docs/execution/plans/2026-09-30-tts-repair/tts_live_check.py`. That is the code, plus the files the gate stages read: `openapi` reads `openapi.committed.json`; `state-render` reads `meu-status.yaml` and `BUILD_PLAN.md`; Vitest reads `docs/build-plan/*.md` (e.g. `gui-actions-audit.test.ts:12`, `layout-canon.test.ts`); pytest reads the registry overlay and grouping. | cloud-local §3.3 item 2 |
--- rg exit 0
=== [C2-post] rg -F -n "spacy.load("en_core_web_sm")"
--- rg exit 1
=== [C14] rg -F -n "ends at or above"
--- rg exit 1
=== [C15] rg -F -n "queue-canon"
docs/execution/plans/2026-09-30-tts-repair/validate-task.sh:508:    vitest_env_ok s27-hub-doc-tests tests/unit/layout-canon.test.ts tests/unit/queue-canon.test.ts tests/unit/gui-actions-audit.test.ts
docs/execution/plans/2026-09-30-tts-repair/implementation-plan.md:156:| Vitest | AC-41.3 `ui/tests/unit/queue-canon.test.ts` | `P:/zorivest` is absent and `styles.css` is unchanged since `f7d3134`. |
docs/execution/plans/2026-09-30-tts-repair/task.md:50:| 13 | Hub reconciliation (plan §BUILD_PLAN.md Audit items 1–3) and new known issues.<br>• Amend 03 §TTS runtime assets per D-8 to D-14 and AC-62.11.<br>• Amend 11: fix the `:111` registry names, and add prose pointers in the two §Residuals sections. The mockup-inventory TT rows are **not** edited (the AC-50.4 lock).<br>• Amend 07-distribution line 9 and §Kokoro / models.<br>• Add `TTS-PACKAGED-RUNTIME-EXCLUDED`, `TTS-VOICE-PACK-LAZY-FETCH` and `TTS-NON-ENGLISH-G2P-DEPS` through `tools/issue_triage.py add`, then render.<br>• Re-run the doc-reading Vitest (`layout-canon`, `queue-canon`, `gui-actions-audit`). | orchestrator | hub edits; 3 new issues | `bash docs/execution/plans/2026-09-30-tts-repair/validate-task.sh hub > "${RECEIPTS_DIR}/s27-hub.txt" 2>&1; code=$?; tail -n 20 "${RECEIPTS_DIR}/s27-hub.txt"; exit $code` | 12 | shared | `docs/build-plan/03…`, `11…`, `07…`; `known-issues.yaml` / `.md` | `avkit_coordinator` | `[ ]` |
--- rg exit 0
```

## Dispositions

| Sweep | Hit (file:line) | Disposition |
|---|---|---|
| C1-old | — (exit 1) | confirmed-consistent: no two-argument `REQUIRED_TTS_ASSETS` remains |
| C1-new | plan:119, plan:193 | confirmed-consistent: definition and AC-62.9 both use `(…, enabled_steps)` |
| C2-old | plan:22 (Goal prose), plan:536 (upstream research quote), plan:540 (D-11 question text), plan:615 (reference URL) | confirmed-consistent: prose, quotes and the wheel URL, which must carry the literal name and version |
| C2-old | plan:121 (`SPACY_MODEL_PIN` URL and dist-info name) | confirmed-consistent: a literal inside the pinned URL / measured artifact |
| C2-old | plan:122 (`spacy.load("en_core_web_sm")`) | **updated** in the post-fix pass → `spacy.load(SPACY_MODEL)` (C2-post exit 1) |
| C2-new | plan:115 (`TtsAsset.SPACY_MODEL` member) | confirmed-consistent: this is the enum member, a different name in a different namespace from the `prepare.SPACY_MODEL` constant. The enum is qualified as `TtsAsset.SPACY_MODEL` in code. |
| C2-new | plan:119, :121, :123, :173, :190, :193, :227, :497 | confirmed-consistent |
| C3-old | — (exit 1) | confirmed-consistent: the old GATED list string is gone |
| C3-new | sh:432, :444, :540, :561; ps1:102; task:42; plan:233, :247, :443, :445 | confirmed-consistent: `--check` / regen command sites (unchanged by this correction) |
| C3-new | sh:622 (`gated` list), plan:132 (`GATED_PATHS`) | **updated**. The plan wording "`GATED`" was corrected to the `gated` list in the post-fix pass (C3-post). `plan_checks.py static` asserts the two lists are equal. |
| C4-old / C4-old2 | — (exit 1) | confirmed-consistent: "attempt 1" floor wording is gone |
| C5-old / C5-old2 | — (exit 1) | confirmed-consistent: no TT-row re-owning remains |
| C5-new | plan:389, task:50, sh:507 | confirmed-consistent |
| C6-old | — (exit 1) | confirmed-consistent |
| C6-new | ps1:83, sh:315 | confirmed-consistent (`plan_checks.py` asserts equality) |
| C7-old | — (exit 1) | confirmed-consistent: H2-1 no longer passes `known-issues.yaml` |
| C8-old | plan:193 | confirmed-consistent: the deliberate AC-62.9 negative (a `j` voice without `chunk` needs no spaCy) |
| C8-old2 | — (exit 1) | confirmed-consistent: the live check uses `PREPARE_DEFAULT_ON` |
| C9-old | — (exit 1) | confirmed-consistent |
| C9-new | plan:366, task:50, sh:501 | confirmed-consistent |
| C10-old | — (exit 1) | confirmed-consistent: the single Red-tolerance rule is `pytest_red` |
| C11-old | — (exit 1) | confirmed-consistent |
| C11-new | plan:130, :322, :356, :500; sh:467 | confirmed-consistent |
| C12-old | plan:98, plan:379 | confirmed-consistent: both state the widened rule (English voices **or** `chunk`) |
| C12-new | plan:118, :119, :533 | confirmed-consistent |
| C13-old | — (exit 1) | confirmed-consistent |
| C13-new | plan:500, local-requests:24, sh:384, :389 | confirmed-consistent |
| C14 (AC-64.6 "ends at or above") | — (exit 1 after the fix) | **updated** in the post-fix pass → "bottom edge … ≤ `window.innerHeight`" |
| C15 (doc-reading suite list) | sh:508, task:50, plan:156 | **updated**: task row 13 now names `gui-actions-audit`, matching sh:508. plan:156 is the env-bound census row, confirmed-consistent. |
