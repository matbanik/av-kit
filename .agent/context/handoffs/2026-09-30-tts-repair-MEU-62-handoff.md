---
date: "2026-09-30"
project: "tts-repair"
meu: "MEU-62"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.2"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-09-30-tts-repair/implementation-plan.md"
build_plan_section: "bp03s3.5"
agent: "claude-code-web (Claude Opus 5.5)"
reviewer: "claude-fable-5-1-subagent (user-authorized, human-review-decision.md)"
predecessor: "none"
---

# Handoff: 2026-09-30-tts-repair-MEU-62-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-62 — `svc-tts-runtime-assets`. It makes Kokoro TTS produce audio by turning the vocab/config file and the spaCy English model into managed downloads with readiness rows. Generation now fails fast with a 409 naming the missing asset, every `Failed` job carries an `error_message`, and `tts.generate*` events reach the Console.
**Build Plan Section**: `docs/build-plan/03-service-layer.md` §TTS runtime assets (residual) (matrix 3.5)
**Predecessor**: none (first MEU of Session 27)

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-62.1 | unit | `TtsAsset`, `AssetState`, `REQUIRED_TTS_ASSETS` with the `SPACY_STEPS` rule; exhaustive match; fail-closed lang code; parity with `LANG_BY_PREFIX` | Spec 03:418; D-8, D-10 | `tests/integration/test_tts_assets.py::test_ac_62_1_required_assets_rule_and_closed_enums` | ✅ |
| AC-62.2 | integration | Variant download also fetches a valid `VOCAB_LOCATION`, even when the weights exist; an invalid vocab fails and is removed | Human-approved D-22 (03:416); D-8, D-9 | `test_ac_62_2_variant_download_fetches_vocab_even_when_weights_exist`, `test_ac_62_2_invalid_vocab_fails_and_is_removed` | ✅ |
| AC-62.3 | integration | A variant is `is_downloaded` only with weights **and** a valid vocab (REST body) | Spec 03:416 | `test_ac_62_3_variant_needs_weights_and_vocab_to_be_downloaded` | ✅ |
| AC-62.4 | integration | `POST /models/load` without the vocab → 409 naming `tts_onnx_vocab`; the port is never called | Spec 03:416, 03:419 | `test_ac_62_4_load_refuses_without_vocab` | ✅ |
| AC-62.5 | integration | PyTorch `KModel(repo_id, config=local path)`; the ONNX vocab resolver is evaluated per call | D-8, D-9; Research-backed | `test_ac_62_5_pytorch_load_passes_local_config_and_onnx_reads_resolver` | ✅ |
| AC-62.6 | integration | Pinned spaCy wheel: sha256 check, zip-slip guard, atomic install, `SPACY_READY`; the unpinned minor, a ready install (409) and a stale install | Human-approved D-22 (03:417); D-11 | `test_ac_62_6_spacy_download_installs_pinned_wheel`, `test_ac_62_6_sha_mismatch_unpinned_and_zip_slip_fail_closed`, `test_ac_62_6_existing_install_ready_is_409_and_stale_is_replaced` | ✅ |
| AC-62.7 | integration | Load of any variant starts the spaCy download (runtime `Downloading` before `load` returns); deferred while another download runs | Human-approved D-22; D-10 | `test_ac_62_7_load_starts_spacy_download_unless_busy`, `test_ac_62_7_load_defers_spacy_while_variant_download_runs` | ✅ |
| AC-62.8 | integration | `GET /health/dependencies` rows `tts_onnx_vocab` and `tts_spacy_model` with `ready`/`missing`/`downloading`, independent of each other | Spec 03:418 | `test_ac_62_8_dependency_rows_are_independent` | ✅ |
| AC-62.9 | integration | Generate fails fast (409, zero rows, no WAV, no `KPipeline`, no `spacy.cli.download`); the `jf_*` + `chunk` case is covered | Spec 03:419 | `test_ac_62_9_generate_fails_fast_on_missing_spacy` | ✅ |
| AC-62.10 | integration | `TTS_LOG_EVENTS` with fields; the console line carries `job_id=` / `error=`; redaction applies | Spec 03:420; D-13 | `test_ac_62_10_generate_events_and_console_fields`; `tests/unit/test_services.py::test_ac_13_6_ring_and_after_seq` (unchanged) | ✅ |
| AC-62.11 | integration | Every `Failed` job has an `error_message`, including on unexpected exceptions; `_current_id` is reset | Spec 03:421; AGENTS §Code Quality | `test_ac_62_11_every_failed_job_has_error_message` | ✅ |
| AC-62.12 | integration | `POST /models/download` takes exactly one of `variant_id` / `asset`; four bad bodies → 422 with no worker; concurrent → 409; runtime reports `asset` | Spec 03:422; D-12 | `test_ac_62_12_download_body_is_exactly_one_target` | ✅ |
| AC-62.13 | integration | MCP `avkit_models.download_asset` → `POST /models/download {asset}`; bad input rejected before fetch | Local Canon 03:451; D-12 | `mcp-server/tests/models-assets.test.ts` (7 tests) | ✅ |
| AC-62.14 | integration | `build_services` wires the resolver and assets and activates an existing install; activation is idempotent | Spec 03:416; D-11 | `test_ac_62_14_startup_activation_is_idempotent` | ✅ |
| AC-62.15 | integration | Settings Dependencies card renders the two asset rows after yt-dlp/FFmpeg; Get → `POST /models/download {asset}` and refetch; no IPC | Spec 03:418 | `ui/tests/unit/settings-page.test.ts` (3 × AC-62.15); `ui/tests/e2e/settings.test.ts` `AC-62.15 Dependencies card …` | ✅ |
| AC-62.16 | integration | ONNX generate with a valid vocab yields samples (Done, no error) | Spec 03:424 | `test_ac_62_16_onnx_generate_with_vocab_yields_samples`, `test_ac_62_16_model_overshoot_is_clipped_not_failed`, `test_ac_62_16_pipeline_result_objects_carry_phonemes_and_audio`; existing `test_ac_9_13`; real-network `tts-live-pre` (2.075 s WAV) | ✅ |

### Other plan AC references (not owned by MEU-62)

The plan also names these AC families. Each is listed here so no AC is silently dropped (C4):

| AC | Owner | Status in MEU-62 |
|----|-------|------------------|
| AC-63.x | MEU-63 handoff | ⏳ not in this MEU (rows 7–9) |
| AC-64.x | MEU-64 handoff | ⏳ not in this MEU (rows 10–12) |
| AC-2.x | existing domain tests | `ModelDownloadRuntime` constructions gain `asset=None` (FIXTURE_REPAIRS); TA-9 at `test_domain.py:321`, `:522-523`, `:602` (AC-2.9/2.12 pins); assertions otherwise unchanged. `test_ac_2_2` is the declared env-bound baseline failure. |
| AC-41.x | existing UI queue canon | untouched; AC-41.3 is a declared env-bound Vitest member (`P:/zorivest` absent). TA-8 was not needed: census found no assertion pinning the Dependencies row count (walkthrough §Census). |
| AC-50.x | existing hub-status parser (AC-50.4) | untouched by MEU-62; exercised at row 13 / H1 |
| AC-56.x | existing TTS page tests | untouched by MEU-62; TA-3 lands with MEU-63 |

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|--------------------------|--------------|-----------|
| pytest `ac_62` (18) | `PASS ac_62 pytest RED: 15 decisive, 3 missing-symbol`; e.g. `assert 500 == 409` (AC-62.4), `assert [] == ['config.json']` (AC-62.2), `assert 422 == 202` (AC-62.6/62.12) | `18 passed` | `tests/integration/test_tts_assets.py` |
| MCP AC-62.13 | three positive tests fail (`expected [] to deeply equal [...]`, `expected true not to be true`); the four rejection tests already pass because the action does not exist yet | `222 passed` (MCP suite) | `mcp-server/tests/models-assets.test.ts` |
| Vitest AC-62.15 | 1 decisive assertion; 2 element-not-found (the rows do not exist yet) | `69 passed of 70` (env-bound AC-51.6) | `ui/tests/unit/settings-page.test.ts` |
| Electron AC-62.15 | **Retroactive** (see note): on a worktree at `baseline.sha` `bea998a` plus only the new spec, `toContainText … element(s) not found` for `tts-asset-row-tts_onnx_vocab` | `8 passed` + `repeat-each=20` pass | `ui/tests/e2e/settings.test.ts` |

**Note on the Electron Red.** When the spec was written, the baseline job held the Electron runner. So its Red was proven afterwards, on a clean worktree of the pre-change commit carrying only the new spec: exit 1 on the AC-62.15 `expect`, with no top-level errors. The product code on that worktree is exactly the baseline.

### Commands Executed

```json
{"schema_version":"evidence.v1","check_id":"s27-62-red-pytest","command":"pytest_red ac_62 (validate-task.sh helper) over PY62","cwd":"/home/user/av-kit","scope":"MEU-62 pytest files","phase":"targeted","exit_code":0,"result":"pass","tested_state":"bea998a + MEU-62 tests only (no production edit)","output":"PASS ac_62 pytest RED: 15 decisive, 3 missing-symbol","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s27-62-red-e2e","command":"xvfb-run -a npm --prefix ui run test:e2e -- tests/e2e/settings.test.ts -g AC-62.15 (worktree of bea998a + new spec)","cwd":"/tmp/av-kit/wt-62red","scope":"Electron settings AC-62.15","phase":"targeted","exit_code":1,"result":"pass","tested_state":"bea998a product + MEU-62 settings spec","output":"AC-62.15 … | failed | expect(locator).toContainText(expected) failed Locator: getByTestId('tts-asset-row-tts_onnx_vocab') … element(s) not found","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s27-62-green","command":"bash docs/execution/plans/2026-09-30-tts-repair/validate-task.sh green62","cwd":"/home/user/av-kit","scope":"PY62+PYREG62 pytest, MCP typecheck/build/test, Settings Vitest + REGTTS, OpenAPI --check","phase":"targeted","exit_code":0,"result":"pass","tested_state":"bea998a + MEU-62 working tree","output":"PASS s27-62-green-pytest-all: 229 passed; env-bound baseline failures tolerated: ['FAILED tests/unit/test_domain.py::test_ac_2_2_download_status_has_no_paused'] | PASS s27-62-mcp-typecheck | PASS s27-62-mcp-build | PASS s27-62-mcp-test | PASS s27-62-green-vitest: 69 passed of 70, env-bound tolerated: AC-51.6 | PASS s27-openapi-final","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s27-62-gate","command":"bash docs/execution/plans/2026-09-30-tts-repair/validate-task.sh gate62","cwd":"/home/user/av-kit","scope":"pyright, ruff, targeted pytest, MCP, ui typecheck/lint/Vitest, OpenAPI --check, ui build, Electron settings + repeat-each=20","phase":"targeted","exit_code":0,"result":"pass","tested_state":"bea998a + MEU-62 working tree","output":"PASS s27-62-pyright | PASS s27-62-ruff | PASS s27-62-pytest: 229 passed (env-bound test_ac_2_2) | PASS mcp typecheck/build/test | PASS s27-62-typecheck | PASS s27-62-lint | PASS s27-62-vitest: 69 of 70 (AC-51.6) | PASS s27-62-openapi | PASS s27-62-build | PASS s27-62-e2e: 8 passed | PASS repeat-each=20 62-settings","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s27-openapi-two-step","command":"uv run python tools/export_openapi.py --check openapi.committed.json; … -o openapi.committed.json; … --check","cwd":"/home/user/av-kit","scope":"OpenAPI G8","phase":"targeted","exit_code":0,"result":"pass","tested_state":"MEU-62 schemas","output":"check exit=1 'OpenAPI drift: openapi.committed.json' → regen exit=0 → final exit=0; 409 declared on /models/download, /models/load, /tts/generate; ROUTE_INDEX stays 71","fresh":true}
```

### Post-gate defects found by the real-network live run (H1-2 prep)

`tts-live-pre` exercises real Hugging Face, GitHub and kokoro 0.9.4 through the container proxy. It found two product defects that the faked suites could not see. Each was fixed test-first after gate62:

1. **Output overshoot.** Real Kokoro audio peaks past ±1.0. `FilesystemAdapter.write_audio_wav` (AC-8.4) rejects that with `ValidationError: float samples must be within [-1.0, 1.0]`, so every real generate still failed, now with a visible reason. Red: `test_ac_62_16_model_overshoot_is_clipped_not_failed` (`assert 422 == 201`). Fix: `_as_float32_pcm` clips to [-1, 1], as a 16-bit PCM write does in the Kokoro reference example.
2. **`KPipeline.Result` chunks.** kokoro 0.9.4 yields `Result` objects, which are sequence-like but not tuples. The tuple-only unpacking dropped the phonemes: ONNX received `[[0, 0]]` and produced 0.325 s of noise (live: `duration_s 0.325`), and the PyTorch branch had the same flaw. Red: `test_ac_62_16_pipeline_result_objects_carry_phonemes_and_audio` (`assert [[0, 0]] == [[0, 7, 8, 0]]`). Fix: `_chunk_part` reads `Result` fields or tuple positions, and torch tensors move to CPU before conversion.

```json
{"schema_version":"evidence.v1","check_id":"s27-tts-live-pre","command":"bash docs/execution/plans/2026-09-30-tts-repair/validate-task.sh tts-live-pre","cwd":"/home/user/av-kit","scope":"real HF + GitHub through the proxy: fresh rows, variant download, spaCy auto-load, generate WAV (GUI default prepare steps), console events","phase":"targeted","exit_code":0,"result":"pass","tested_state":"43017a5 clean tree","output":"PASS fresh-rows {missing, missing} | PASS variant-download {Idle, vocab_valid, listed} | PASS spacy-autoload {missing -> ready} | PASS generate-wav {Done, error_message None, duration_s 2.075, rms 3615.01} | PASS console-events {tts.generate, tts.generate_done}","fresh":true}
```

The plan-time harness `tts_live_check.py` also needed one fix: it read `.state` from the domain row, but the domain row is the `AssetState` itself. That was a harness bug, not a product bug.

**Container pre-gate (H1-2), attempt 3 on `d793f1f`, clean tree:** PASS. Results: pytest 566 passed (no new failures versus the baseline), Vitest 700/702, Electron 111, `tts-live-pre` 2.075 s, and a clean source audit. Attempt 1 found two sites the census missed, both inside approved categories:
- `test_api_auth` health fake → `FIXTURE_REPAIRS`;
- `test_api_downloads` `ACTION_INDEX_AFTER` 67 → 68 → TA-9.

Both are recorded in walkthrough §Pre-gate attempt 1.

**WINDOWS_GATE attempt 3: a MEU-62 hermeticity defect (fixed).** `build_services` activates the default `~/.avkit/models` at startup, before a test or the live harness sets its own directory. `activate_spacy_dir` adds to the process-wide `sys.path`, so a real user install on Mat's host (created by an interactive app session) made spaCy read `ready` everywhere: 12 `test_tts_assets.py` failures, and TTS_LIVE attempt 3's `fresh-rows` / `spacy-autoload` saw `ready → ready`.

- Reproduced here with a fake home install: 12 failed, matching Windows.
- Fix: the autouse `isolated_home` fixture points `HOME` and `USERPROFILE` at an empty dir. `tts_live_check.py` redirects `~` to a throwaway dir before the services start, and now requires spaCy `missing` at `fresh-rows` and `missing → ready` at `spacy-autoload`, unless spaCy is importable from the interpreter itself (`site_spacy`, which its docstring always allowed).
- With the same fake home, both pass: 20/20, and live `missing → ready`, 2.075 s. The old harness reproduces the leak.

The product behaviour is unchanged: process-wide readiness is the truth for misaki's `spacy.load`.

**WINDOWS_GATE attempt 4: the attempt-3 fix was incomplete (now fixed at the root).** `isolated_home` isolated `~` only inside `test_tts_assets.py`. An earlier file in the same pytest process (`test_api_captures.py`, AC-37.15) calls `build_services`, which activated the real `~/.avkit/models` and left it on `sys.path`. The attempt-3 fix had been proven on the file alone, which was the gap.

- Root fix: an autouse `_restore_import_path` fixture in `tests/conftest.py` restores `sys.path` and drops new `en_core_web_sm` modules after **every** test. `HOME` is left alone, so the `rtk` tooling tests are unaffected.
- Evidence with a fake home spaCy install: the captures + assets pair goes from 12 failed to 0. The full suite goes from **75 failed to 63 failed**, and 63 is exactly the env-bound baseline count; no `test_tts_assets` failures remain. A normal-home run fails on the identical 63.
- TTS_LIVE attempt 4 (Windows) passed `missing → ready`, with `site_spacy` false and 2.075 s.

The authoritative fresh full gate is `WINDOWS_GATE` + `TTS_LIVE` (H1-6). The container pre-gate, including the real-network `tts-live-pre`, is recorded at H1-2.

### Quality Gate Results

```
pyright (uv run pyright packages/): 0 errors, 0 warnings
ruff check packages/ tests/: 0 violations
pytest (PY62 + PYREG62): 229 passed; 1 env-bound baseline failure (test_ac_2_2, Python 3.11 enum `in`)
MCP: 222 passed; ui typecheck 0; ui lint 0 (--max-warnings 0); Vitest 69/70 (AC-51.6 env-bound)
Electron settings: 8 passed; repeat-each=20: 160/160
anti-placeholder: 0 matches (source-audit runs at H1-2)
```

---

## Changed Files

| File | Action | Lines | Summary |
|------|--------|-------|---------|
| `packages/core/src/avkit_core/domain/tts.py` | modified | +68 | `TtsAsset`, `AssetState`, `SPACY_MODEL`, `KOKORO_LANG_CODES`, `SPACY_LANG_CODES`, `SPACY_STEPS`, `required_tts_assets`; `ModelDownloadRuntime.asset` |
| `packages/core/src/avkit_core/domain/health.py` | modified | +4 | `DependencyHealth` asset states and the spaCy version |
| `packages/core/src/avkit_core/ports/tts.py` | modified | +24 | `TtsAssetPort` (`state`, `version`, `download`, `activate`) |
| `packages/core/src/avkit_core/services/models.py` | modified | rewrite (+214/−) | vocab-aware list/load, `download_asset`, spaCy auto-trigger under `_lock`, `models_directory`, `asset_missing` |
| `packages/core/src/avkit_core/services/tts.py` | modified | +50 | pre-job `_require_assets`, `TTS_LOG_EVENTS`, catch-all `_fail` |
| `packages/core/src/avkit_core/services/health.py` | modified | +32 | `CONSOLE_FIELDS`, asset rows, `download_runtime` reader |
| `packages/core/src/avkit_core/services/prepare.py` | modified | ±2 | imports `SPACY_MODEL` from the domain (D-21) |
| `packages/infrastructure/src/avkit_infra/tts/assets.py` | new | 1–291 | `TtsAssetAdapter`, `SPACY_MODEL_PIN`, `install_spacy_wheel`, `activate_spacy_dir`, `spacy_ready`, `resolve_vocab_path`, `vocab_is_valid` |
| `packages/infrastructure/src/avkit_infra/model_manager/vocab.py` | new | 1–42 | `fetch_vocab` (Hugging Face, AC-9.12 confinement) |
| `packages/infrastructure/src/avkit_infra/tts/adapter.py` | modified | +37 | `vocab_path` resolver, `KModel(repo_id, config, model)`, constants moved to `assets.py` |
| `packages/api/src/avkit_api/{wiring.py,schemas/models.py,schemas/health.py,routes/models.py,routes/health.py,routes/tts.py}` | modified | +104 | composition, `ModelDownloadIn` validator, `TtsAssetOut`, asset branch, declared 409s |
| `openapi.committed.json` | modified | +123/−12 | regenerated after `--check` reported drift |
| `mcp-server/src/toolsets/{models.ts,registry.ts}` | modified | +15 | `download_asset` action, appended |
| `ui/src/renderer/src/features/tts/tts-assets.ts` | new | 1–58 | shared asset wires, labels, chip, `presentAssetRows` |
| `ui/src/renderer/src/features/tts/tts-commands.ts` | modified | +22 | `assetDownloadSchema`, `postDownloadAsset` |
| `ui/src/renderer/src/features/settings/SettingsPage.tsx` | modified | +40 | Dependencies card asset rows and Get |
| tests (`test_tts_assets.py` new, `tts_asset_fakes.py` new, `models-assets.test.ts` new, `settings-page.test.ts`, `settings.test.ts`, `test-ids.ts`) | new/modified | — | AC-62.x |
| tests (`test_domain.py:321` TA-9; `action-index/convert/capture/m7-resource.test.ts` TA-9) | modified | — | TA-9 only |
| tests (`test_services.py`, `test_uow_commit_log.py`, `test_console_level.py`, `api_fakes.py`, `test_api_health_settings.py`, `test_domain.py` constructions) | modified | — | `FIXTURE_REPAIRS` (setup only; assertions unchanged) |

```diff
@@ services/tts.py generate — before the job row exists
         if config is None:
             raise ValidationError("voice is not available")
+        variant_id = status.variant_id
+        self._require_assets(variant_id, voice, enabled_steps)
@@
         except DomainError as exc:
-            return self._mark(job.id, TTSStatus.Failed, str(exc))
+            return self._fail(job.id, str(exc))
+        except Exception as exc:
+            # Never leave a job in Generating: record the reason, then re-raise (500).
+            detail = str(exc)
+            self._fail(job.id, f"{type(exc).__name__}: {detail}" if detail else type(exc).__name__)
+            raise
```

```diff
@@ services/health.py _process (CONSOLE_FIELDS)
             raw = str(event_dict.get("event", method_name))
-            message = redact_message(raw)
+            fields = "".join(
+                f" {key}={event_dict[key]}" for key in CONSOLE_FIELDS if key in event_dict
+            )
+            message = redact_message(raw + fields)
```

```diff
@@ tts/adapter.py load_model (PyTorch)
-            loaded = KModel(model=str(path))
+            config = self._vocab_file()
+            # A local config keeps kokoro from fetching config.json from Hugging Face at load.
+            loaded = KModel(
+                repo_id=ONNX_VOCAB_REPO,
+                config=str(config) if config is not None and config.is_file() else None,
+                model=str(path),
+            )
```

---

## Codex Validation Report

_Left blank for reviewer agent. Reviewer fills this section during `/validation-review`._

### Recheck Protocol

1. Read Scope + AC table
2. Verify each AC against Evidence section (file:line, not memory)
3. Independently probe the claimed behavior and compare decisive output
4. Verify the full gate is fresh and matches current D6 inputs; rerun if changed or unproven
5. Record findings below

### Findings

| # | Severity | Finding | File:Line | Recommendation | Status |
|---|----------|---------|-----------|----------------|--------|

### Verdict

_pending_

---

## Deferred Items

None within MEU-62. Filed as known issues at row 13 (out of scope per the plan's §Out of Scope): packaged-app TTS runtime, lazy voice-pack fetch, non-English G2P dependencies.

---

## Decision Log

```yaml
decision_log:
  - id: D-20
    stage: execution
    question: "Where does the vocab fetch live, given tests/unit/test_domain.py:1324 pins ModelCatalogPort to exactly ('download','sideload')?"
    resolution: autonomous
    class: two-way
    chosen: "Behind the new TtsAssetPort: model_manager/vocab.fetch_vocab (the only infra package allowed to import huggingface_hub) is injected into TtsAssetAdapter; ModelService calls assets.download(ONNX_VOCAB) after the weights"
    source_tag: Local Canon
    precedents: ["tests/unit/test_domain.py:1324 — ModelCatalogPort method pin", "tests/integration/test_tts_models.py:641-661 — AC-9.12 huggingface_hub confinement"]
    research: { engine: none, sources: [] }
    reasoning: "Adding a port method would change a pinned expectation outside TEST_AMENDMENTS (Stop condition S3). The injected fetch keeps both pins intact and the port count unchanged."
  - id: D-21
    stage: execution
    question: "How does infra reference the spaCy model name without importing avkit_core.services?"
    resolution: autonomous
    class: two-way
    chosen: "Define SPACY_MODEL once in avkit_core.domain.tts; services/prepare.py imports it, so prepare.SPACY_MODEL still resolves"
    source_tag: Local Canon
    precedents: ["packages/infrastructure/src — no module imports avkit_core.services (rg, 2026-09-30)", "implementation-plan.md SPACY_MODEL_PIN — never restate the name"]
    research: { engine: none, sources: [] }
    reasoning: "Keeps the infra → domain/ports dependency direction and the single definition. The plan said the constant lives in prepare.py; it is now defined in the domain and re-exported there by import."
  - id: D-23
    stage: execution
    question: "Service and response shape for asset downloads"
    resolution: autonomous
    class: two-way
    chosen: "ModelService.download_asset(asset) next to download(variant_id); 202 body {variant: null, asset}; the already-ready 409 applies to both assets"
    source_tag: Local Canon
    precedents: ["packages/api/src/avkit_api/routes/models.py — ModelDownloadAcceptedOut", "implementation-plan.md AC-62.6 (d) SPACY_INSTALL_EXISTING"]
    research: { engine: none, sources: [] }
    reasoning: "A separate method keeps download(variant_id) byte-compatible for every existing caller and fake. The plan's 'download(asset=…)' names the same behaviour. Applying the ready → 409 rule to the vocab too avoids a silent re-fetch and matches the spaCy rule."
  - id: D-24
    stage: execution
    question: "Targeted container pytest runs include test_domain.py, which has a baseline env-bound failure"
    resolution: autonomous
    class: two-way
    chosen: "validate-task.sh pytest_paths_ok: targeted runs use the declared ENV_BOUND_PY rule (failed set ⊆ baseline failed set), like pytest_env_ok"
    source_tag: Local Canon
    precedents: ["implementation-plan.md §Environment-bound census, pytest row", "walkthrough.md §Baseline — test_ac_2_2 fails at bea998a"]
    research: { engine: none, sources: [] }
    reasoning: "No new tolerance: the same declared, signature-proved rule, applied to a subset of paths. WINDOWS_GATE still runs the full suite with zero tolerance."
  - id: D-25
    stage: execution
    question: "UI body for asset downloads: one union schema, or two strict schemas?"
    resolution: autonomous
    class: two-way
    chosen: "A separate strict assetDownloadSchema / buildAssetDownloadBody next to the unchanged downloadSchema"
    source_tag: Local Canon
    precedents: ["ui/src/renderer/src/features/tts/tts-commands.ts:50-55,107-109 — buildDownloadBody used by existing tests"]
    research: { engine: none, sources: [] }
    reasoning: "The same wire contract as the plan's union (exactly one key, strict) without changing buildDownloadBody's signature for existing callers and tests."
  - id: D-26
    stage: execution
    question: "Asset row wording and backward compatibility on the Dependencies card"
    resolution: autonomous
    class: two-way
    chosen: "Chips read Ready / Missing / Downloading; rows render only when the payload carries them (presentAssetRows)"
    source_tag: Local Canon
    precedents: ["ui/tests/unit/settings-rail.test.tsx:478 — success-tone count pinned for a two-row payload", "docs/build-plan/11-page-layout.md ST7 — never fabricate a state"]
    research: { engine: none, sources: [] }
    reasoning: "Keeps existing two-row fixtures unaffected and never shows a state the backend did not report."
  - id: D-33
    stage: execution
    question: "Real Kokoro output exceeds [-1, 1], and the AC-8.4 WAV writer rejects it. Where is it fixed?"
    resolution: autonomous
    class: two-way
    chosen: "The adapter's PCM normalization clips to [-1, 1]; the writer's range contract stays strict"
    source_tag: Research-backed
    precedents: ["tests/integration/test_filesystem_media.py AC-8.4 — the writer contract", "hexgrad/Kokoro-82M README — writes the float output as 16-bit PCM, which clips"]
    research: { engine: none, sources: ["kokoro 0.9.4 package source (installed)"] }
    reasoning: "The producer owns its output range. Clipping matches the reference 16-bit write, whereas peak normalization would change loudness per job. The writer keeps rejecting genuinely bad input."
  - id: D-34
    stage: execution
    question: "How are KPipeline chunks read, given kokoro 0.9.4 yields Result objects?"
    resolution: autonomous
    class: two-way
    chosen: "_chunk_part reads the named Result field (phonemes/audio), or the tuple position for plain tuples"
    source_tag: Research-backed
    precedents: ["kokoro/pipeline.py KPipeline.Result (0.9.4) — graphemes, phonemes, audio; __iter__/__getitem__/__len__"]
    research: { engine: none, sources: ["kokoro 0.9.4 package source (installed)"] }
    reasoning: "Handles both the pinned release and the tuple shape the existing fakes and older releases use, without widening the test fakes."
```

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-09-30 | claude-code-web | Initial handoff after gate62 |
| Updated | 2026-09-30 | claude-code-web | Two live-run defects fixed test-first (D-33, D-34); tts-live-pre PASS |
