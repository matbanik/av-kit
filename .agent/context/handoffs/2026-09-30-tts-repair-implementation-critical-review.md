---
date: "2026-10-01"
review_mode: "execution"
target_plan: "docs/execution/plans/2026-09-30-tts-repair/implementation-plan.md"
round: 1
verdict: "approved"
findings_count: 6
template_version: "2.2"
requested_verbosity: "standard"
agent: "claude-fable-5-1-subagent"
---

# Critical Review: 2026-09-30-tts-repair (Session 27, MEU-62 / MEU-63 / MEU-64)

> **Review Mode**: `execution`
> **Verdict**: `approved`

Round 1 of 6. Independent reviewer dispatched in a separate context under the user-authorized same-vendor route (`human-review-decision.md`). The reviewer wrote no product, test, plan or handoff file; scratch receipts are under `/tmp/claude-review/`. Reviewed at branch `claude/vigilant-keller-tg7n45`, HEAD `950207f`, baseline `bea998a` (`baseline.sha`).

---

## Intent Anchor

The plan's goal: **"Make TTS produce audio again, and make its failures visible. Then fix the two TTS page usability findings from Mat's 2026-09-30 walkthrough."** Concretely: the Kokoro vocab/config and spaCy `en_core_web_sm` become managed, readiness-reported downloads; generation fails fast with a 409 that names the missing asset; every `Failed` job carries an `error_message` that reaches the Console and the run bar; the hidden "Manage" grid becomes a model picker with one state-driven Get / Load / Unload button; the text panel gains Apply cleanup, loses the raw preview, and replaces the tall voice list with a searchable combobox so Speed and Format fit the default window.

**intent_achieved: yes.** The delivered work achieves this. The decisive evidence is the authoritative Windows `TTS_LIVE` run on the reviewed code (`407db19`, GATED_PATHS byte-identical at HEAD): a fresh models directory goes `missing → ready` for both assets, `kokoro-onnx-int8` downloads with a valid vocab, `load` auto-starts the pinned spaCy wheel, and a generate with the GUI-default prepare steps (including `chunk`) ends `Done` with a 2.075 s / RMS 3619.9 WAV and `tts.generate` / `tts.generate_done` in the console ring. The fail-fast 409, the `error_message` catch-all, the picker/action state machine, the run-bar error, Apply cleanup, the APG combobox and the Space rule are each proven by assertion-level tests that I re-ran here (pytest, Vitest, MCP, and the Electron specs on a fresh build), plus my own adversarial probes of the wheel installer.

---

## Scope

**Target**: the full correlated Session 27 set — `docs/execution/plans/2026-09-30-tts-repair/{implementation-plan.md, task.md, walkthrough.md, human-gate-decision.md, local-requests.md, validate-task.sh, validate-task.ps1, tts_live_check.py, plan_checks.py, windows-gate-result.json, tts-live-result.json}`; handoffs `2026-09-30-tts-repair-MEU-62-handoff.md`, `-MEU-63-handoff.md`, `-MEU-64-handoff.md`; every file in `git diff bea998a..950207f` (84 files: `packages/`, `ui/`, `mcp-server/`, `tests/`, `openapi.committed.json`, `docs/build-plan/03,07,11`, `known-issues.yaml`, `meu-status.yaml`, `BUILD_PLAN.md`), including the user-decided carve-outs A-2 (adoption-record rebind, `8c14927`), A-3 (`ui/src/main/index.ts` reveal on `ready-to-show` + `startup-reveal.test.ts`), A-4 (`download-queue.test.ts` helper hardening), A-5 (`validate-task.ps1` serial Electron install), A-6 (`SettingsRail.tsx` click lock until scroll settles + `settings.test.ts` spec) and the A-7 acceptance.
**Review Type**: execution review (multi-MEU project; the newest handoff was only the seed)
**Checklist Applied**: IR (full) + DR (build-plan docs are claimed evidence at row 13)
**Correlation**: plan folder date/slug `2026-09-30-tts-repair` ↔ the three `2026-09-30-tts-repair-MEU-6x-handoff.md` files; `implementation-plan.md` §Handoff Set lists exactly these three.

---

## Findings

| # | Severity | Blocking | Kind | Finding | File:Line | Recommendation | Status |
|---|----------|----------|------|---------|-----------|----------------|--------|
| F1 | Medium | no | behavior | **Settings → Dependencies asset row never leaves "Downloading" on its own.** `postDownloadAsset` refetches `['health','dependencies']` once, right after the 202, so the row flips to `Downloading` (disabled Get). Nothing on the Settings page observes the download runtime or re-polls the rows afterwards: the only `Downloading → Idle/Failed` watcher that invalidates `QUERY_HEALTH_DEPENDENCIES` lives in `TTSPage` (`TTSPage.tsx:178-186`), and `queryClient` has no interval (`lib/query-client.ts:3-5`, `staleTime: 0` only). A user who clicks Get on Settings sees "Downloading" until a window-focus change or a remount, even after the 12 MB wheel installed seconds earlier. No AC states a completion refresh (AC-62.15 asks only for the POST and one refetch), so this is not a contract violation; it is a real gap in the delivered GUI flow. | `ui/src/renderer/src/features/settings/SettingsPage.tsx:233-236`, `ui/src/renderer/src/features/tts/tts-commands.ts:195-203`, `ui/src/renderer/src/features/tts/TTSPage.tsx:178-186` | On the Settings page, mount `useDownloadRuntime()` (1 s while `Downloading`) and invalidate `QUERY_HEALTH_DEPENDENCIES` on the `Downloading → *` transition, or give the dependencies query a `refetchInterval` while any asset row reads `downloading`. Add a Vitest spec that flips the seam from `downloading` to `ready` and asserts the row updates without a remount. | open |
| F2 | Medium | no | clerical | **The authoritative gate's own check still reports FAIL.** `validate-task.sh windows-gate-check` at HEAD exits 1: attempt 7 (`407db19`) ran 16 of 17 stages; `ui-electron` exited 1 with 1 unexpected (`download-queue.test.ts` AC-49.26 A16 drag-over wait), and stage 17 `source-audit` is absent. The user accepted this as `USER_EXPLICIT` A-7 (attributing the miss to his own interaction with the gate's app window); the implementer did not self-waive, and a waiver-aware change to the check was correctly not made. Reviewer closure of the gaps: (a) I ran the stage-17 pattern (`PREFIX_AUDIT` over `AUDIT_SRC`) at HEAD → no hits, and `git diff --quiet 407db19 HEAD -- <GATED_PATHS>` exits 0, so that audit binds to the Windows-tested code; (b) AC-49.26, its page, helpers and the drag path are outside the Session 27 diff, the container shows 0 misses in 150+ runs, and Mat's quiet repeats were 20/20. Everything else on Windows passed with zero tolerance: pytest 629/0, Vitest 702/702, e2e 117 passed / 0 flaky, `TTS_LIVE` 5/5. | `docs/execution/plans/2026-09-30-tts-repair/windows-gate-result.json:16-123`, `human-gate-decision.md` §A-7 | No change required for approval. For the record: the human-interaction attribution cannot be verified from the repository; it is the user's own statement and decision. If a later round touches `GATED_PATHS`, the re-run should be quiet-machine (A-7 option 1) so the check itself can pass once. Consider filing `DOWNLOAD-QUEUE-DRAG-OVER-MISS` with the A-4 diagnostic (A-7 option 1 proposed it; it was not filed). | accepted_risk |
| F3 | Low | no | behavior | **`activate_spacy_dir` prepends a user-writable directory to `sys.path`.** `sys.path.insert(0, entry)` gives `{models_directory}/spacy/en_core_web_sm-3.8.0/` import precedence over the stdlib and site-packages for every module name. Today the only content is the sha256-pinned wheel (`en_core_web_sm/` + `.dist-info`), extraction is zip-slip guarded (probed below), and the app is localhost-only on the user's own machine, so this sits inside the declared trust boundary. `append` would satisfy `SPACY_READY` identically with no shadowing exposure. | `packages/infrastructure/src/avkit_infra/tts/assets.py:119` | Use `sys.path.append(entry)` (readiness is by name; nothing else provides `en_core_web_sm`), or document why precedence is required. Hardening only. | open |
| F4 | Low | no | test-rigor | **One vacuous assertion in `test_ac_62_9`.** The `spacy.cli.download` spy (`cli_calls == []`) cannot fail: with `_patch_engines` installed, no production path imports or calls spaCy's CLI, so the spy guards nothing. The test is still 🟢 on its decisive assertions (409 naming `tts_spacy_model` for `am_eric` and for `jf_alpha`+`chunk`, zero `tts_jobs` rows, no output file, `FakeKPipeline` not constructed, `jf_alpha` without `chunk` → 201). | `tests/integration/test_tts_assets.py:559-562,575` | Either drop the spy or spy on `misaki`/`KPipeline` construction instead (already asserted via `FakeKPipeline.calls`). Clerical for the AC. | open |
| F5 | Low | no | clerical | Handoff line-range claims drift from file state: MEU-62 handoff says `assets.py` "1–275" (file is 291 lines) and `vocab.py` "1–44" (42 lines); the plan's Files Modified table lists `model_manager/manager.py` as *modify* but it is unchanged (the vocab fetch after the weights lives in `ModelService._run_download`, `services/models.py:236-240`, which the handoff describes correctly). An intelligent reader infers the right values. | `.agent/context/handoffs/2026-09-30-tts-repair-MEU-62-handoff.md` §Changed Files; `implementation-plan.md` §MEU-62 Files Modified | Correct the two ranges; mark `manager.py` "unchanged (behaviour moved to ModelService, D-20)". | open |
| F6 | Low | no | behavior | Two cosmetic runtime effects, both inside the letter of AC-62.8 / AC-63.1: (a) a variant download reuses one `on_progress` for the weights and then the vocab, so the bar and the picker suffix go `100% → 0% → 100%` when the weights already existed; (b) during a variant download the vocab row reads `missing` rather than `downloading`, because `runtime.asset` is `None` (AC-62.8 defines `downloading` as "runtime `asset` equals the row"). | `packages/core/src/avkit_core/services/models.py:233-240`, `packages/core/src/avkit_core/services/health.py:187-196` | Scale the vocab phase into the last ~5 % of the variant's progress, or expose a `phase`. Optional. | open |

> **`Blocking` is not `Severity`.** No finding above is blocking: F1 is a delivered-GUI usability gap outside every stated AC; F2 is an evidence/bookkeeping state the user decided and that the reviewer independently closed as far as the repository allows; F3–F6 are hardening, one weak assertion inside a strong test, and clerical drift.

### Out-of-Contract Observations (≤ 5, one line each)

1. `VoiceCombobox` closes only on Escape or an outside *mousedown* (`VoiceCombobox.tsx:55-66`, execution D-32); a keyboard user who Tabs from the input through the popup to the Speed slider leaves the open popup overlaying Speed/Format. AC-64.6 explicitly allows the open popup to cover them; a `focusout`-outside-root close would remove the wart without touching the AC-56.4 multi-activation behaviour.
2. A-4's `windowSettled` now needs 6 consecutive frames < 50 ms (`download-queue.test.ts:1125-1144`): a host running below ~20 fps fails the drag specs with `E2E_WINDOW_SHOWN` after 15 s. That is a clearer diagnostic than a silent miss, but it is a new load sensitivity for the authoritative gate; worth knowing before the next quiet-machine run.
3. `HealthService.dependencies()` (`health.py:175-185`) mutates `sys.path` on every poll through `spacy_ready → activate_spacy_dir` and calls `spacy_ready` twice (state + version). Idempotent and cheap after the first `import spacy`, but a read endpoint with a write side effect.

---

## Checklist Results

Decisive reviewer observations, as `evidence.v1`. Every command ran from `/home/user/av-kit` at HEAD `950207f` on a clean tree (`git status --porcelain` empty), `RECEIPTS_DIR=/tmp/claude-review`. The container is non-authoritative (no `rtk`/`pwsh`; 63 declared env-bound pytest failures; Vitest AC-51.6/AC-41.3 and the 4 capture-picker Electron specs env-bound); the authoritative evidence is the user's Windows attempt 7 at `407db19`, whose code identity I verified against HEAD.

```json
{"schema_version":"evidence.v1","check_id":"rv-identity","command":"git log --oneline -1; git diff --quiet 407db19 HEAD -- ui packages mcp-server tests tools pyproject.toml uv.lock openapi.committed.json docs/build-plan/11-page-layout.md docs/build-plan/gui-actions-index.md docs/execution/plans/2026-09-26-p11-layout-canon/implementation-plan.md .agent/context/grouping/2026-09-03-p11-page-layout-session-grouping.md .agent/model-registry.local.json .agent/model-registry.local.yaml docs/execution/plans/2026-09-30-tts-repair/validate-task.ps1 docs/execution/plans/2026-09-30-tts-repair/tts_live_check.py; git diff 407db19 HEAD --stat","cwd":"/home/user/av-kit","scope":"HEAD vs Windows-tested commit over GATED_PATHS","phase":"static","exit_code":0,"result":"pass","tested_state":"950207f clean","output":"950207f A-7 … | gated-diff exit=0 | post-407db19 diff: 6 files, all under docs/execution/plans/2026-09-30-tts-repair/ (human-gate-decision, local-requests, task, walkthrough, the two result JSONs)","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"rv-source-audit","command":"grep -nE 'TODO|FIXME|NotImplementedError|transition-all|bg-\\[#|console\\.log\\(|except Exception:\\s*pass|# type: ignore' <AUDIT_SRC: 12 files from validate-task.sh>","cwd":"/home/user/av-kit","scope":"Windows stage 17 pattern, reproduced by the reviewer (stage not run on Windows)","phase":"static","exit_code":1,"result":"pass","tested_state":"950207f = 407db19 over GATED_PATHS","output":"(no hits; grep exit 1 = clean)","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"rv-static","command":"uv run pyright packages/; uv run ruff check packages/ tests/; uv run python tools/export_openapi.py --check openapi.committed.json; python3 docs/execution/plans/2026-09-30-tts-repair/plan_checks.py static","cwd":"/home/user/av-kit","scope":"types, lint, OpenAPI drift, plan static verifier","phase":"static","exit_code":0,"result":"pass","tested_state":"950207f clean","output":"pyright: 0 errors, 0 warnings | ruff: All checks passed! | openapi --check exit=0 | PASS static: 24 task rows; scripts and plan cross-references agree","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"rv-pytest-62","command":"uv run pytest tests/integration/test_tts_assets.py tests/unit/test_tts_voice_fixture.py tests/unit/test_services.py tests/integration/test_tts_models.py tests/e2e/test_api_tts_models.py tests/e2e/test_api_health_settings.py tests/integration/test_api_wiring.py tests/e2e/test_api_openapi.py tests/unit/test_domain.py -q --tb=short -p no:cacheprovider -rfE","cwd":"/home/user/av-kit","scope":"PY62 + PYREG62 + VOICE_CATALOG_FIXTURE parity (18 AC-62 tests, full MEU-62 regression neighbours)","phase":"targeted","exit_code":1,"result":"pass","tested_state":"950207f clean","output":"1 failed, 232 passed in 103.56s — the single failure is tests/unit/test_domain.py::test_ac_2_2_download_status_has_no_paused, the declared ENV_BOUND_PY baseline member (Python 3.11 enum `in`); no other failure","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"rv-vitest","command":"npm --prefix ui run test -- tests/unit/settings-page.test.ts tests/unit/tts-page.behavior.test.ts tests/unit/tts-page.test.ts tests/unit/tts-run-bar.test.ts tests/unit/voice-combobox.test.tsx tests/unit/settings-rail.test.tsx tests/unit/layout-canon.test.ts tests/unit/e2e-wiring.test.ts tests/unit/gui-actions-audit.test.ts tests/unit/help-card.test.ts tests/unit/layout-primitives.test.ts tests/unit/queue-canon.test.ts","cwd":"/home/user/av-kit","scope":"UNIT62/63/64 + REGTTS + queue-canon","phase":"targeted","exit_code":1,"result":"pass","tested_state":"950207f clean","output":"Test Files 2 failed | 10 passed (12); Tests 2 failed | 134 passed (136) — the two failures are exactly the declared env-bound AC-51.6 (CRLF prefix hash) and AC-41.3 (P:/zorivest absent)","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"rv-mcp","command":"npm --prefix mcp-server run test","cwd":"/home/user/av-kit","scope":"full MCP suite incl. models-assets.test.ts (AC-62.13, 7 tests) and action-index TA-9","phase":"targeted","exit_code":0,"result":"pass","tested_state":"950207f clean","output":"Test Files 10 passed (10); Tests 222 passed (222)","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"rv-e2e","command":"npm --prefix ui run build && cd ui && ELECTRON_DISABLE_SANDBOX=1 xvfb-run -a npx playwright test tests/e2e/startup-reveal.test.ts tests/e2e/settings.test.ts tests/e2e/tts-generate.test.ts -g 'A-3|A-6|AC-62.15|AC-58.12|AC-63|AC-64|W2-5|AC-56.6' --reporter=line","cwd":"/home/user/av-kit/ui","scope":"fresh build; every new Session 27 Electron spec plus the carve-out specs (A-3 ×2, A-6, AC-62.15, AC-63.5/63.6, AC-64.4/64.6) and the TA-amended neighbours (W2-5, AC-56.6 ×4, AC-58.12 ×3)","phase":"targeted","exit_code":0,"result":"pass","tested_state":"950207f clean","output":"build exit=0 | Running 16 tests using 1 worker … 16 passed (35.5s)","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"rv-plan-checks","command":"bash validate-task.sh windows-gate-check; bash validate-task.sh tts-live-check; bash validate-task.sh handoff-ac; bash validate-task.sh task-state","cwd":"/home/user/av-kit","scope":"the plan's own result validators (paths under docs/execution/plans/2026-09-30-tts-repair/)","phase":"targeted","exit_code":1,"result":"partial","tested_state":"950207f clean","output":"windows-gate-check: FAIL: stages [16 ids] != [17 ids] (source-audit absent; ui-electron exit 1 is the next predicate) exit=1 | tts-live-check: PASS tts-live @ 407db19…: {'status': 'Done', 'error_message': None, 'steps': [...,'chunk','kokoro'], 'duration_s': 2.075, 'rms': 3619.9, 'bytes': 99644} exit=0 | handoff-ac: OK: all 9 plan AC(s) present ×3 (MEU-62/63/64) exit=0 | task-state: PASS implementation rows 0-13 exit=0","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"rv-zip-slip-probe","command":"uv run python - <<PY … install_spacy_wheel(whl, models, pin) for members {'/tmp/evil_abs.py','C:/evil_drive.py','en_core_web_sm\\\\..\\\\..\\\\evil_bs.py','en_core_web_sm/../../evil_mid.py','./././en_core_web_sm/ok.py', clean}, then sha256 '0'*64, then a non-zip payload PY","cwd":"/home/user/av-kit","scope":"adversarial probe of assets.install_spacy_wheel (AC-62.6 boundary rules)","phase":"targeted","exit_code":0,"result":"pass","tested_state":"950207f","output":"abs REFUSED: unsafe path in spaCy wheel: /tmp/evil_abs.py | spacy/=[] ; drive REFUSED … C:/evil_drive.py | spacy/=[] ; backslash-dotdot REFUSED | spacy/=[] ; mid-dotdot REFUSED | spacy/=[] ; dot installed -> spacy/en_core_web_sm-3.8.0 ; clean installed -> spacy/en_core_web_sm-3.8.0 ; badsha REFUSED: spaCy wheel sha256 mismatch … | spacy exists: False ; notzip REFUSED: spaCy wheel is not a valid zip archive | leftovers: [] — every refusal leaves no .tmp-* and no install dir; nothing written outside models/","fresh":true}
```

### Information Retrieval (IR)

| Check | Result | Command | Exit | Evidence |
|-------|--------|---------|------|----------|
| All AC have source labels | pass | `rg -n "^\| AC-6[234]\.\d+ \|" docs/execution/plans/2026-09-30-tts-repair/implementation-plan.md` (read) | 0 | Every AC-62.1–62.16, 63.1–63.6, 64.1–64.6 row carries Spec / Local Canon / Research-backed / Human-approved with a citation; each handoff AC table repeats the source |
| Validation cells are exact commands | pass | `python3 docs/execution/plans/2026-09-30-tts-repair/plan_checks.py static` | 0 | `PASS static: 24 task rows; scripts and plan cross-references agree` |
| BUILD_PLAN audit row present | pass | `git diff bea998a HEAD -- docs/build-plan/03-service-layer.md docs/build-plan/07-distribution.md docs/build-plan/11-page-layout.md` | 0 | 03 §TTS runtime assets rewritten with D-8…D-14 and AC-62.11 tags; 07 line 9 adds the spaCy wheel host and §Kokoro/models the packaged-runtime gap; 11 `:111` fixed to registry names + two migration pointers; mockup inventory untouched (layout-canon AC-50.4 passed in `rv-vitest`) |
| Post-MEU rows present (handoff, reflection, metrics) | partial | `bash validate-task.sh task-state` | 0 | Rows 0–13 and H1-1…H1-6 `[x]`; H1-7 (this review), H2-1…H2-3 (reflection, POST_REVIEW_STATE, closeout) correctly still `[ ]` — they follow approval |

### Design Review (DR)

| Check | Result | Command | Exit | Evidence |
|-------|--------|---------|------|----------|
| Naming convention followed | pass | `ls .agent/context/handoffs/2026-09-30-tts-repair-*` | 0 | Three `{date}-{slug}-MEU-6x-handoff.md` plus this one rolling review at the canonical path |
| Template version present | pass | `head -12 .agent/context/handoffs/2026-09-30-tts-repair-MEU-6{2,3,4}-handoff.md` | 0 | `template_version: "2.2"` in all three |
| YAML frontmatter well-formed | pass | `bash validate-task.sh handoff-ac` (parses each handoff) | 0 | `OK: all 9 plan AC(s) present in the handoff` ×3 |
| DR-1 claim-to-state | pass (F5 clerical) | file reads cited per finding | — | Every behavioural claim checked resolved to code (see IR-1/IR-3 below); only the two line ranges and the `manager.py` plan row drift |
| DR-2 residual old terms | pass | `rg -n "preview-raw" ui/src` → none; `rg -n "first PyTorch-variant load" docs/build-plan/03-service-layer.md` → none | 1 | `preview-raw` remains only in `test-ids.ts` (append-only registry, AC-51.6) and TA-1's negative assertion |
| DR-6 cross-reference | pass | `rg -n "MEU-68" .agent/context/meu-status.yaml` | 0 | The one deferral (MCP live audit) targets a registered MEU (`row_key: MEU-68`, line 1794) — not an orphan |

### Post-Implementation Review (PR)

| Check | Result | Command | Exit | Evidence |
|-------|--------|---------|------|----------|
| Evidence bundle complete | pass | reads of the three handoffs §Evidence + `walkthrough.md` + both result JSONs | — | Red/Green/gate `evidence.v1` blocks per MEU with decisive output; Windows attempt log 1–7 in `human-gate-decision.md`; the FAIL state of attempt 7 is stated plainly, not hidden (F2) |
| FAIL_TO_PASS table present | pass | `rg -n "### FAIL_TO_PASS" .agent/context/handoffs/2026-09-30-tts-repair-MEU-6*-handoff.md` | 0 | 3/3; each row names an assertion-level Red (e.g. `assert 500 == 409`, `expected 'output' to be 'error'`, `toBeLessThanOrEqual` via `require_failed_title`) |
| Commands independently runnable | pass | `rv-static`, `rv-pytest-62`, `rv-vitest`, `rv-mcp`, `rv-e2e`, `rv-plan-checks` above | mixed | Every claimed check reproduced; outcomes match the handoffs within the declared env-bound set |
| Anti-placeholder scan clean | pass | `rv-source-audit` | 1 (clean) | No TODO/FIXME/NotImplementedError/console.log/`# type: ignore` in `AUDIT_SRC` |

### Implementation Review Checklist

| # | Check | Result | Evidence |
|---|---|---|---|
| IR-1 | Live runtime evidence | **pass** | `tests/integration/test_tts_assets.py` builds the real graph (`build_services` → `create_app` → `TestClient`) and fakes only the engines and the two network fetches; the Windows `TTS_LIVE` run exercised real HF + GitHub + kokoro 0.9.4 end to end (`rv-plan-checks`: 2.075 s WAV). The two defects only a live run could find (output clipping, `KPipeline.Result` unpacking) were fixed test-first (`test_ac_62_16_model_overshoot_is_clipped_not_failed` asserts the decoded PCM `[32767, -32768, 16384]`; `…pipeline_result_objects…` asserts `input_ids == [[0, 7, 8, 0]]`). |
| IR-2 | Stub behavioural compliance | pass | `tests/tts_asset_fakes.py` `FakeAssets.download` flips its own `states[asset]` to READY and records the call; the test `Stack` fakes (`HubServer`, `WheelServer`) write real files that the production validators then read. |
| IR-3 | Error mapping completeness | pass | `ConflictError → 409` asserted with the envelope `code == "ConflictError"` and the asset name (AC-62.4/62.9); `ValueError`/pydantic → 422 for five bad bodies incl. `{"variant_id": ""}` and extra keys (AC-62.12); catch-all → 500 with the DB row `Failed` (AC-62.11); `SpacyModelNotFoundError → 503` on `/tts/prepare` left unchanged and exercised by the AC-64.1 failure test. `responses=` declares 409 on `/models/download`, `/models/load`, `/tts/generate` (`rv-static` OpenAPI check clean). |
| IR-4 | Fix generalization | pass | The attempt-3 per-file `isolated_home` fix was generalized at attempt 4 into `tests/conftest.py::_restore_import_path` (every test); the clipping fix sits in `_as_float32_pcm`, which both the PyTorch and ONNX paths share; `_chunk_part` is used by both branches. |
| IR-5 | Test rigor audit | pass (F4 one 🟡 assertion) | Table below. |
| IR-6 | Boundary validation coverage | pass | `ModelDownloadIn` exactly-one validator + `extra="forbid"`; MCP `.strict()` + `z.enum` (4 rejection cases, zero fetches); UI `assetDownloadSchema.strict()`; wheel: sha256, member-path rules, `resolve()`-inside-temp, atomic `os.replace`, temp cleanup — all probed adversarially (`rv-zip-slip-probe`). |
| IR-7 | Deferral & AC-coverage integrity | pass | (a) The single `deferred` row targets `MEU-68`, registered in `meu-status.yaml`; the six `out-of-scope` rows cite 03:414-422 / 07:214-223 and three were filed as known issues (`TTS-PACKAGED-RUNTIME-EXCLUDED`, `TTS-VOICE-PACK-LAZY-FETCH`, `TTS-NON-ENGLISH-G2P-DEPS`, all `status: open` at lines 786-807). (b) `handoff-ac` PASS ×3; every plan AC id appears in a handoff AC table with a test. (c) Every `integration` AC is backed by a route-level or Electron test, not a unit test (AC-62.x through `TestClient`; AC-63.1–63.3/63.5–63.6 and AC-64.1/64.2/64.4–64.6 by jsdom-with-fetch-ledger plus Electron). |

#### IR-5 test rigor grades

| File | Grade | Basis |
|---|---|---|
| `tests/integration/test_tts_assets.py` (18 tests) | 🟢 Strong | Exact values throughout: hub call ledger `== ["config.json"]`, runtime JSON equality, dependency rows compared as whole dicts, DB rows `== [("Failed", "RuntimeError: hf 503")]`, decoded WAV samples, `input_ids`. Negative paths: invalid vocab removed, sha mismatch, unpinned minor with zero fetches, zip-slip with no leftovers, 409 on ready, stale install replaced, deferred auto-download, 422 ×5, 409 concurrent. One vacuous spy (F4). |
| `tests/unit/test_tts_voice_fixture.py` | 🟢 | Parity of the 54-voice fixture against `list_voice_configs()` (fails on any divergence). |
| `tests/conftest.py` `_restore_import_path` | n/a (fixture) | Verified by the Windows 629/0 and the container's unchanged 63 env-bound set; function-scoped autouse runs after session/module fixtures, so legitimately persistent `sys.path` entries from higher scopes survive. |
| `mcp-server/tests/models-assets.test.ts` (7) | 🟢 | Asserts the exact body `{asset}`, method, path, single registry row at the appended position, and four rejections with `fetchImpl` called 0 times. |
| `ui/tests/unit/settings-page.test.ts` AC-62.15 (3) | 🟢 | Row order via `indexOf`, exact POST body, `depsCalls` increments, IPC spy not called, disabled state, older-backend absence. |
| `ui/tests/unit/tts-run-bar.test.ts` (4) | 🟢 | Every `RUN_BAR_ERROR` branch incl. empty/absent/stale/precedence. |
| `ui/tests/unit/tts-page.behavior.test.ts` (new AC-63/64 ×11, TA-2/3/5/6) | 🟢 | Option labels/values equality, selection fallbacks, exact POST ledgers (`toEqual([...])`), zero POSTs while disabled, chip containment in the model block, progress `aria-valuenow`, Apply: textarea value, one extra `/tts/prepare`, last `input_text` PUT; failed Apply: text unchanged and no new PUT after the debounce; combobox: groups, filter, Enter → exactly one PUT, Escape → unchanged. |
| `ui/tests/unit/voice-combobox.test.tsx` (7) | 🟢 | APG attributes, `aria-activedescendant` ids, Home/End, outside-press close, empty-state Enter sends nothing, AND of language + query, pure helper matrix. |
| `ui/tests/unit/tts-page.test.ts` AC-64.3, TA-1 | 🟡 Adequate | Source-text assertions (`variant="secondary"` inside the `<Button` tag; `not.toContain('preview-raw')`), as the plan specified for a `unit`/Local-Canon AC. |
| `ui/tests/e2e/tts-generate.test.ts` AC-63.5/63.6/64.4/64.6 | 🟢 | Geometry first (`toBeLessThanOrEqual(innerHeight)`, scroll tops 0) with the 54-voice fixture; ordered mutation ledger `['/models/download','/models/load','/models/unload']`; forced click on the disabled button adds nothing; exactly one voice PUT. AC-63.5's 15 s timeout matches the 5 s Failed-job poll. |
| `ui/tests/e2e/settings.test.ts` AC-62.15, A-6 | 🟢 | Ledger body keys `['asset']`; A-6 replays a deterministic 1.5 s smooth scroll and asserts `aria-current` after 2.5 s and exactly one current entry (Red proven per handoff; Green here). |
| `ui/tests/e2e/startup-reveal.test.ts` (2) | 🟢 | Asserts `BrowserWindow.isVisible()` from the main process after an immediate reload, and that the delayed backend URL (published by boot's last step) arrives. |
| `ui/tests/e2e/download-queue.test.ts` A-4 | n/a (helpers) | Same waits/timeouts; adds a frame-rate precondition and a diagnostic re-throw (Observation 2). |

### Carve-out review (A-2 … A-7)

- **A-2** (`8c14927`): two files, +5/−1, exactly `rule-preservation.md` `AGENTS.md.postimage_sha256` and one `protected_files` entry — within the authorization; outside GATED_PATHS. Correct.
- **A-3** (`ui/src/main/index.ts:490-509`): `revealMainWindow(window, process.argv, loginLaunchShouldHideWindow(...))` is registered on `window.once('ready-to-show')` before the load, with the call text unchanged (AC-61.15 pin holds); the initial `loadURL`/`loadFile` is wrapped in `try/catch` that logs through `appendStdoutLog`. `--start-minimized` and login-launch-hidden semantics are unchanged (`startup-mode.ts:revealMainWindow` is the same decision function with the same inputs; only the trigger moved from "load resolved" to "first paint"). `show: false` without `paintWhenInitiallyHidden: false`, so `ready-to-show` fires. Both A-3 specs pass here. Minimal and correct.
- **A-4**: helper-only, same assertions and timeouts; Observation 2.
- **A-5** (`validate-task.ps1` `npm-ci` argv): `npm ci` → serial `node ui/node_modules/electron/install.js` → `path.txt` guard; stage ids unchanged (`plan_checks.py static` PASS; attempt 7 `npm-ci` exit 0 with that argv).
- **A-6** (`SettingsRail.tsx:67-99,180-192`): the lock now ends `SCROLL_SETTLE_MS` (150 ms) after the scroller's last `scroll` event, capped at `CLICK_LOCK_MAX_MS` (3 s); with no scroll the original 800 ms applies (jsdom unchanged — `settings-rail.test.tsx` passed). `clickLockUntil` is set to `now + 3000` on click and zeroed on release, so the observer defers to the click for at most 3 s and `reconcile` runs once per click; `cancelHold` prevents a second click's release from firing the first's reconcile. Release semantics are correct. One consequence worth knowing: a manual wheel scroll during the hold extends it (up to 3 s), so the highlight follows a user's own scroll later than before — accepted by the A-6 option text ("3 s cap").
- **A-7**: see F2. The implementer recorded the FAIL state plainly and did not alter the check.

---

## Verdict

`approved` — The delivered work achieves the plan's intent: TTS produces audio again through the production graph on the authoritative Windows `TTS_LIVE` run, missing assets fail fast with a 409 that names the asset, every `Failed` job carries a reason that reaches the Console and the run bar, and the two walkthrough usability findings are fixed with geometry-proven layout. No evidence-backed High/Critical finding exists in runtime behaviour, contract correctness, test rigor, persistence or handoff truthfulness. The six findings are non-blocking: one delivered-GUI usability gap outside every AC (F1, recommended for a follow-up or a small correction), the user-decided gate-check state (F2, independently narrowed by the reviewer), one hardening note (F3), one vacuous assertion inside a strong test (F4), and clerical drift (F5, F6).

**Residual risk statement.** (1) The Windows gate check itself never reached PASS: one AC-49.26 drag-over miss on a non-quiet host, attributed by the user to his own input and outside this diff, and stage 17 not run on Windows (closed here by the reviewer at an identical gated tree). (2) The Settings-card "Downloading" row does not self-refresh (F1). (3) The packaged (PyInstaller) build still cannot synthesize (`TTS-PACKAGED-RUNTIME-EXCLUDED`, correctly out of scope and filed). (4) `activate_spacy_dir` prepends a user-writable path (F3).

**Follow-up actions (non-blocking, for H2 or a later session):** apply F1 as a small `/execution-corrections` item or file it as a known issue; correct F5's two line ranges; consider F3 (`append`) and F4; file `DOWNLOAD-QUEUE-DRAG-OVER-MISS` with the A-4 diagnostic so the next quiet-machine gate has a target.

> **The two verdicts have opposite requirements.** `approved` carries findings F1–F6 with `Blocking: no`; none defeats a control, so no `mechanism:` slug applies this round.
