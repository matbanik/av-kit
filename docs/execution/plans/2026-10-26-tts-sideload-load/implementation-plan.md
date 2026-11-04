---
project: "2026-10-26-tts-sideload-load"
date: "2026-10-26"
source: "docs/build-plan/03-service-layer.md#tts-sideload-load-residual"
meus: ["MEU-98"]
status: "draft"
template_version: "2.2"
---

# Implementation Plan: TTS sideload load, spaCy directory swap and the eSpeak evidence stage (Session 42)

> **Project:** `2026-10-26-tts-sideload-load`
> **Build plan:**
> - `docs/build-plan/03-service-layer.md` §TTS sideload load (residual) (`:507-516`, MEU-98; matrix row 3.11, `build-priority-matrix.md:40`). Spec 02 §Model manager "Sideload" (`02-infrastructure.md:447`, "detect a dropped `.pth`/`.onnx` and mark it downloaded") is the behaviour it restores.
> - Rider `TTS-SPACY-SYSPATH-STALE-DIR` (`known-issues.yaml:2556`, TECH-DEBT P4): 03 §TTS asset fetch "spaCy path" row (`03-service-layer.md:442`) is its Local Canon neighbour. Row 1 adds its rule row to §TTS sideload load (D-128).
> - Local evidence stage for `TTS-ESPEAK-LIVE-PATH-UNVERIFIED` (`known-issues.yaml:2455`, MEU-EXPAND of approved MEU-74): the AC-74.11 procedure in `docs/execution/plans/2026-10-14-tts-engine-runtime/implementation-plan.md:312`.
>
> **Grouping:** `.agent/context/grouping/2026-10-17-gui-shell-and-tts-sideload-session-grouping.md`, Session 42 (`:101-112`), decisions D-94, D-95, D-103 and D-98, D-99, D-100 (`:160-169`).
> **Known issues:** `MODEL-SIDELOAD-LOAD-500` (`known-issues.yaml:2511`, triage D-86, `meu_links: [MEU-98]`), `TTS-SPACY-SYSPATH-STALE-DIR` (`:2556`, `meu_links: []`), `TTS-ESPEAK-LIVE-PATH-UNVERIFIED` (`:2455`).
> **Status:** `draft`. Under `plan_to_exec_gate: human`, execution starts only on the user's explicit chat message after plan-review approval.
>
> Line anchors are from `7b29fcd` (the 2026-10-24 squashed root commit). Session 40's commit on `main` (`b6b288e`) touches none of the files below except the shared grouping file (`PREREQS`, D-120).

## Goal

A model file dropped into `tts.models_directory` is listed as downloaded but cannot be loaded. `ModelService.list_available` overlays every row from `catalog.sideload(models_dir)` onto the repository rows (`services/models.py:117-118`), but nothing records the scanned path. `load` reads only the repository row (`:141-150`) and hands it, with `path=None`, to the adapter. The adapter's `_require_weight_path` (`tts/adapter.py:133-142`) then raises `ModelLoadError("model weight file is missing")`, which answers 422 (`errors.py:36`). Nothing is logged: the call (`adapter.py:247`) sits before the `try` blocks that log `tts.load_failed` (`:123-124`). The rider is a second readiness defect on the same directory: `activate_spacy_dir` (`tts/assets.py:120-133`) only appends, so after `tts.models_directory` changes, the old folder's spaCy install stays on `sys.path` and Dependencies keeps reporting it ready.

1. **MEU-98 — `svc-tts-sideload-load`.**
   - `ModelService` records every scanned sideload file that has a catalog row, through the existing `mark_downloaded`, before it lists or loads (`SIDELOAD_RECORD`, `RECORD_RULE`). A listed variant can then be loaded.
   - Every failing `KokoroAdapter.load_model` logs exactly one `tts.load_failed` before it raises, the missing weight file included (`LOAD_FAILURE_PATHS`, `LOG_CAUSE`).
   - A contract test drives `GET /models/downloaded`, then `POST /models/load`, through the production composition root.
2. **Rider — `TTS-SPACY-SYSPATH-STALE-DIR`.** `activate_spacy_dir` swaps the entries it added for the current directory's entries (`SPACY_PATH_SWAP`).
3. **Evidence stage — `TTS-ESPEAK-LIVE-PATH-UNVERIFIED`.** If eSpeak NG is installed on this machine, Mat runs the AC-74.11 procedure and the result is recorded. If it is absent (it is today: `where.exe espeak-ng` finds nothing and no `Program Files/eSpeak NG` exists), the row is `[B]` (b) with the evidence, the issue stays open with a fresh `verification`, and the session still closes (`ESPEAK_STAGE`, grouping D-100).

Order: `SIDELOAD_RECORD` first (the contract test needs it), then `LOAD_FAILURE_PATHS`, then the rider, then the evidence stage. Each change is one Red/Green pair in one tree. Row 0 records the baseline in `baseline.sha`. Treat the live files as the baseline and reset nothing.

## Context Tool Decision

```yaml
context_tool_decision:
  phase: planning
  eligible_tools: []
  decision: not_applicable
  eligibility_basis: "graphify-out/ and graphify-out-research/ are absent from P:/av-kit-wt/s42-tts-sideload-load and P:/av-kit (ls: No such file or directory, 2026-10-26); no headroom MCP or binary. Scope is three source files (core services/models.py, infrastructure tts/adapter.py and tts/assets.py) and four test files, read directly, which .agent/docs/context-tool-decision-gate.md routes to direct file/search."
  human_message_reference: null
```

Task row 0 re-evaluates this before execution (create-plan §5f). It stops (S1) if a graph directory has appeared.

## Harness, driver and reviewer route

- **Driver:** Claude Code in the VSCode extension on Mat's Windows host (`.agent/docs/harness-profiles.md` §Claude Code; `.agent/context/harness.local.md` §Claude Code).
  - `native_shell: pwsh`. Every validation goes through `rtk proxy` with the receipt pattern `*> C:/Temp/av-kit/<receipt>.txt; $code=$LASTEXITCODE; Get-Content …; exit $code`.
  - `plan_to_exec_gate: human`. A reviewer `approved` does not start execution; the user's explicit chat message does.
  - `fresh_worker` is the Agent tool with `.claude/agents/` (`av-kit-builder`, `av-kit-verifier`). Every non-`shared` row keeps `compact_continue` as its fallback.
- **Cloud/local split: not used.** Mat's Windows host is both the driver and the target. The grouping allows Python in the container, but the eSpeak stage is local, and one host keeps one identity. There is no `validate-task.sh`/`.ps1` and no `local-requests.md`. Commands are the PROFILE D6 Python argv (`.agent/docs/commands.md:190-210`) plus targeted file lists.
- **Working directory:** `P:/av-kit` on `main` (D-120). No branches or worktrees (AGENTS.md §Commits). Row 0 runs `uv sync --frozen --all-packages --python 3.12` (D-121).
- **Reviewer:** Codex CLI through `tools/Invoke-CodexDispatch.ps1` (`avkit_independent_reviewer`; `.agent/skills/cli-dispatch/SKILL.md`), with `AGENT_MODEL_REGISTRY_HOME=P:/.agent`. Claude wrote the plan, so the reviewer is a different vendor. Caps: plan 3 rounds, execution 6. If Codex is unavailable, Mat is the fallback (PROFILE B3/B4). Self-review is never allowed.
- **Never:** commit, push, upload, publish, or write to YouTube; author an `approved` verdict; send secrets to a provider.

## Handoff Set

| Scope | Canonical handoff |
|---|---|
| `MEU-98` (with the rider and the evidence stage) | `.agent/context/handoffs/2026-10-26-tts-sideload-load-MEU-98-handoff.md` |

Plan-local tooling (project artifacts, not product):

- [session-gate.ps1](session-gate.ps1) (rows 8 and H1-2)
- [identity.py](identity.py) (input identity, H1-6b)
- [red-check.py](red-check.py) (Red proof, rows 2, 4 and 6)

Rolling reviews:

- `.agent/context/handoffs/2026-10-26-tts-sideload-load-plan-critical-review.md`
- `.agent/context/handoffs/2026-10-26-tts-sideload-load-implementation-critical-review.md`

## Work Packages and Context Lifecycle

| ID | Work | depends_on | context_strategy | durable_outputs |
|---|---|---|---|---|
| WP-0 | Prerequisites, baseline, `TEST_AMENDMENTS` census, the 03 canon edits (task rows 0–1) | — | `shared` | `walkthrough.md` §Execution message, §Baseline, §Census; `baseline.sha`; 03 edits |
| WP-1 | `SIDELOAD_RECORD` TDD (rows 2–3) | WP-0 | `shared` | tests + `services/models.py`; Red/Green receipts; `walkthrough.md` §Sideload record |
| WP-2 | `LOAD_FAILURE_PATHS` TDD with the contract test (rows 4–5) | WP-1 | `shared` | tests + `tts/adapter.py`; `walkthrough.md` §Load failures |
| WP-3 | `SPACY_PATH_SWAP` TDD (rows 6–7) | WP-2 | `compact_continue` | tests + `tts/assets.py`; `walkthrough.md` §spaCy swap; compact, then re-read `task.md` and the walkthrough |
| WP-4 | Session gate, hub, eSpeak stage (rows 8–10) | WP-3 | `shared` | gate receipts; `meu-status.yaml`, rendered `BUILD_PLAN.md`; `walkthrough.md` §eSpeak |
| WP-5 | H1 closeout, execution review, H2 | WP-4 | `compact_continue` | handoff, rolling review, reflection, metrics row |

---

## User Review Required

> [!IMPORTANT]
> These items are for the review loop and for the user's execution message. They are not a pause point.
>
> 1. **Listing models now writes the database on first sight of a sideload (`SIDELOAD_RECORD`, D-123).** `GET /models` and `GET /models/downloaded` (and MCP `avkit_models` list) call `list_available`. The first call after a file is dropped records its path with one `mark_downloaded` per file and one explicit `uow.commit()` call; later calls make no `mark_downloaded` call and no explicit commit (`RECORD_RULE`). The unit of work's own commit on every clean exit (`unit_of_work.py:60`) is unchanged. `POST /models/load` records the same way first, so a load never depends on a list having happened.
> 2. **A sideload with no catalog row is still display-only.** A scanned id with no repository row (AC-12.8) is listed and never recorded; loading it stays 404. Today all four sideload ids (`voices.py:159-172`) have seeded rows (`engine.py:23`); AC-98.7 keeps it that way.
> 3. **A removed file is not un-marked (`REMOVED_FILE`, D-126).** The row stays recorded; `load` answers 422 "model weight file is missing" and logs `tts.load_failed` once. Un-marking on a later scan is out of scope.
> 4. **Load failures are logged once each (`LOAD_FAILURE_PATHS`, D-127).** New `tts.load_failed` lines: missing, unset or unreadable weight file (device `cpu`), PyTorch runtime not bundled, kokoro import failure, unsupported format. The `error` field names the cause (`LOG_CAUSE`), for example `FileNotFoundError`. The 422 bodies are unchanged.
> 5. **The spaCy path swaps on the next readiness check (`SPACY_PATH_SWAP`, D-128).** After `tts.models_directory` changes, the next spaCy readiness or activation call (`GET /api/v1/health/dependencies`, or a successful model load) removes the old folder's spaCy entries that av-kit itself added and adds the new folder's. An already-imported spaCy model stays imported in the running process; readiness reads False because `spacy.util.is_package` looks up distribution metadata on `sys.path` (R-b).
> 6. **eSpeak NG is absent on this machine.** Row 10 will be `[B]` (b) unless Mat installs eSpeak NG 1.52 before row 10. That is non-blocking for the session (grouping D-100).
> 7. **The Session 40 dependency (D-120).** Session 40 is committed on `main` (`b6b288e`); its grouping edit resolves D-103. Row 0 confirms it and stops (S1) otherwise.

---

## Proposed Changes

### Single-statement contracts

Each name below is defined once, here. ACs, task rows and tests refer to these names and never restate the values.

| Name | Definition | Source |
|---|---|---|
| `PREREQS` | Before any edit: the cwd is the repository root `P:/av-kit` on branch `main`; no `graphify-out*/`; the grouping row `\| D-103 \|` is not `open`; in `meu-status.yaml`, MEU-9, MEU-12, MEU-62, MEU-73, MEU-74 and MEU-75 are `approved` and MEU-98 is `pending`; `services/models.py` contains `for row in self._catalog.sideload(models_dir):`, `tts/adapter.py` contains `path = _require_weight_path(variant)`, and `tts/assets.py` contains `def activate_spacy_dir` (the code this plan changes). | grouping `:101-112`, D-103 (`:169`); `meu-status.yaml:2562` |
| `SIDELOAD_RECORD` | `ModelService` gains one private step, `_record_sideload(uow, models_dir) -> None`. It calls `self._catalog.sideload(models_dir)` once and, for each scanned row whose id has a repository row (`uow.models.get(id) is not None`) and matches `RECORD_RULE`, calls `uow.models.mark_downloaded(id, scanned.path)`. If it wrote anything it calls `uow.commit()` once. `list_available` calls it inside its existing unit of work, before `list_catalog()`; the overlay of scanned rows that follows (`:117-118`) is unchanged, so an id with no repository row is still listed. `load` calls it inside its unit of work, before `uow.models.get(variant_id)`. Core does no filesystem I/O: the scan is the port's (`ModelCatalogPort.sideload`, `ports/models.py:22`), and `models.py` gains no `is_file`, `exists`, `stat` or `avkit_infra` import. | 03 "Mark downloaded", "Load resolves"; 02 "Sideload" (`:447`); D-123 |
| `RECORD_RULE` | A scanned row is recorded iff its repository row is not downloaded, or the repository path differs from the scanned path. So a never-recorded file, a row whose path is the v0.19 legacy file (the scan never returns a legacy file, `manager.py:97-113`), and a managed file replaced by a dropped one at another path are recorded; a row already recorded at that path is not written. A second call with no file change makes no `mark_downloaded` call and no explicit `uow.commit()` call. "Commit" in this plan's ACs means that explicit call, counted by the fake unit of work's `commits` (`tests/unit/test_services.py:296`); the automatic commit `SqlAlchemyUnitOfWork.__exit__` makes on every clean exit (`unit_of_work.py:60`) is unchanged and out of scope. | D-124 |
| `MARK_SIGNATURE` | `mark_downloaded(variant_id, path)` keeps its two-argument signature (`ports/storage.py:99-106`). The repository sets `size_bytes` from the file when it exists (`repositories.py:365-373`). Row 1 amends the 03 "Mark downloaded" row to read `mark_downloaded(id, path)` and say the repository records the size. | D-125 |
| `REMOVED_FILE` | A recorded file deleted later stays recorded. `load` passes the row to the adapter, which raises the existing `ModelLoadError("model weight file is missing")` (422) and logs one `tts.load_failed` (`LOAD_FAILURE_PATHS`). | 03 "Tests" ("a file removed after the scan returns the 422 and the log line"); D-126 |
| `LOAD_FAILURE_PATHS` | Every call of `KokoroAdapter.load_model` that raises logs exactly one `tts.load_failed` event (through `_log_load_failed`) before the exception leaves the adapter; a call that returns logs none. The branches that log today keep their device values. Newly logged: the three `_require_weight_path` failures (path unset, file missing, file unreadable), with device `"cpu"`, as the probe-failure branch logs (`:249-252`); `torch is None` and the kokoro `ImportError` in `_load_pytorch`, with device = the resolved target; and the unsupported-format `ValidationError`, with device = the resolved target. The exception types and messages are unchanged. | 03 "Logged failure"; grouping D-98; D-127 |
| `LOG_CAUSE` | The `error` field of a `tts.load_failed` event is the type name of the cause: for a `ModelLoadError` with a `__cause__`, the cause's type (`FileNotFoundError` for an unset or missing file, the `OSError` subclass for an unreadable one, `ImportError`/`ModuleNotFoundError` for kokoro); otherwise the raised exception's own type (`ModelLoadError` for `torch is None`, `ValidationError` for the format). The branches that already log pass the raw failure, so their values are unchanged. | 03 "Logged failure" ("with the variant and cause"); D-127 |
| `SPACY_PATH_SWAP` | `tts/assets.py` keeps a module-level `_ACTIVE_SPACY_ENTRIES: set[str]` guarded by a module-level `threading.Lock`. Each `activate_spacy_dir(models_dir)` call, under the lock: computes the current entries (`str(spacy_install_dir(models_dir, pin))` for every pin whose directory exists); removes from `sys.path` every tracked entry that is not current and is in `sys.path`, and drops it from the set; appends every current entry not in `sys.path` and tracks it (append, never insert, so AC-73.12 holds); and calls `importlib.invalidate_caches()` iff it changed `sys.path`. An entry it did not add is never removed. A current entry already on `sys.path` that it did not add is left alone and not tracked. | known issue fix "swap the tracked entry"; 03 "spaCy path" (`:442`); R-a, R-b; D-128 |
| `CONTRACT_STACK` | AC-98.6 and AC-98.9 use `tests/integration/test_tts_assets.py` `Stack` (`:128-225`): the production `build_services` plus `create_app`, with only the engines faked (`_patch_engines`, `FakeSession`/`FakeKModel`). No new e2e test file. | 03 "Tests" (contract test); D-129 |
| `ESPEAK_STAGE` | Row 10 calls the production detection, `EspeakCliAdapter().status()` (`espeak.py:146-175`: `PATH`, then the `ProgramFiles`/`ProgramFiles(x86)` install locations, then `--version`), and prints the resolved path and version. **Absent** (`available` False): the row is `[B]` (b) missing dependency, with a `### B-10` `evidence.v1` block (command, exit 3, the `<absent>` line); `TTS-ESPEAK-LIVE-PATH-UNVERIFIED` stays `open` and its `verification` gets `last_checked` = that day, `method` "row 10 `EspeakCliAdapter().status()` probe", `result` "espeak-ng unavailable". **Present:** Mat runs the AC-74.11 procedure (`2026-10-14-tts-engine-runtime/implementation-plan.md:312`) in the dev app and the pasted outcome goes in `walkthrough.md` §eSpeak and the handoff. Pass resolves the issue at H2-2. A failure opens a new issue against MEU-74 (grouping D-100) and does not widen MEU-98. | grouping D-100; D-130 |
| `RED_TREE` | Each Red row refuses a product edit made before its tests run: row 2 refuses any change under `packages/` since `baseline.sha` (tracked or untracked); row 4 refuses a change to `tts/adapter.py` or `tts/assets.py`; row 6 refuses a change to `tts/assets.py`. | D-131 |
| `TEST_AMENDMENTS` | **TA-1** `tests/integration/test_tts_device_resolution.py` `test_ac_75_9_unreadable_weight_file_is_model_load_error_neg` (`:657`): it adds a `capture_logs` block around the load and asserts exactly one `tts.load_failed` event with `variant_id` the variant's id, `device == "cpu"` and `error == "PermissionError"`. Every existing line of that test stays. | Local Canon |
| `CENSUS_PATTERNS` | Row 1 greps `tests` and `mcp-server/tests` for `list_available`, `list_downloaded`, `mark_downloaded`, `sideload`, `sideload_rows`, `_require_weight_path`, `tts.load_failed`, `model weight file is missing`, `PyTorch runtime is not bundled`, `unsupported model format`, `activate_spacy_dir`, `spacy_ready`, `sys.path`, `models/downloaded`, `models/load`, `model.marked_downloaded` and `.commits`, and names `tests/unit/test_uow_commit_log.py` explicitly. A test that counts commits or repository writes around `list_available`/`load` is `unaffected` only when its catalog fake scans no file with a repository row; one that asserts `tts.load_failed` counts is `unaffected` only when the branch it drives already logged. Each hit gets a disposition: `TA-n`, `unaffected` with the reason, or `new-contradiction`, which triggers S2. | Local Canon (Session 35/40 census) |
| `PRODUCT_SCOPE` | The files this plan may change are exactly the Files Modified and Hub and state rows below; `session-gate.ps1` `scope-paths` holds the same allow-list. No `packages/api/`, `ui/` or `mcp-server/` file changes. | grouping `:103-108` |

### MEU-98 — `svc-tts-sideload-load`

#### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---|---|---|---|
| REST `GET /api/v1/models`, `GET /api/v1/models/downloaded` | existing `ModelVariant` response (unchanged) | unchanged; a recorded sideload reads `is_downloaded: true` with its `path` | unchanged |
| REST `POST /api/v1/models/load` | existing body `{variant_id, device}` (unchanged) | unchanged; errors 404 / 409 / 422 unchanged | unchanged (existing `extra="forbid"`) |
| `ModelRepository.mark_downloaded(variant_id, path)` | `ports/storage.py:99-106` (unchanged) | `NotFoundError` for an unknown id (never reached: `SIDELOAD_RECORD` checks the row first) | n/a |
| `ModelCatalogPort.sideload(models_dir)` | `ports/models.py:22` (unchanged) | first match per id, legacy files skipped (`manager.py:97-113`) | n/a |
| structlog `tts.load_failed` | `adapter.py:123-124` (unchanged keys) | `variant_id`, `device`, `error` (`LOG_CAUSE`) | no new keys |
| `sys.path` spaCy entries | `SPACY_PATH_SWAP` | only entries av-kit appended | entries it did not add are untouched |
| OpenAPI, IPC, MCP schemas | unchanged | no change | no change |

#### Acceptance Criteria

Test names start `test_ac_98_<n>_`. The full names are in Verification Plan §2, and `red-check.py --require` uses those names, as the task rows do. AC-98.6, AC-98.8 and AC-98.9 use the existing `test_tts_assets.py` fixtures `stack` and `isolated_path` (`:117`). The fixture restores `sys.path`; each of these tests also resets `assets._ACTIVE_SPACY_ENTRIES` through `monkeypatch`, so the tracked set never leaks between tests.

| AC | Type | Description | Source | Negative Test |
|---|---|---|---|---|
| AC-98.1 | unit | `SIDELOAD_RECORD` on list (`test_services.py`, `_tts_stack`, `FakeCatalog.sideload_rows`): with a scanned `kokoro-pt-fp32` row at `models_dir/kokoro.pth` (seeded not downloaded) and a scanned `side` row with no repository row, `list_available()` returns both as downloaded; afterwards the repository row `kokoro-pt-fp32` is downloaded with that path and the fake's `uow.commits` (explicit `uow.commit()` calls, `RECORD_RULE`) rose by exactly 1; a second `list_available()` leaves `commits` unchanged and makes no `mark_downloaded` call; `side` has no repository row. `list_downloaded()` records the same way. Source (`test_ac_98_1_core_does_no_file_io`): `services/models.py` contains no `.is_file(`, `.exists(`, `.stat(` or `avkit_infra`. | 03 "Mark downloaded"; AC-12.8 | `side` is never passed to `mark_downloaded` (the fake would raise `KeyError`) |
| AC-98.2 | unit | `SIDELOAD_RECORD` on load: with the same scan and no prior list, `load("kokoro-pt-fp32", CPU)` records the row and the fake `TTSPort` receives a variant whose `path` is the scanned path; the vocab 409 and the unknown-id 404 are unchanged (a `side`-only id is 404). A row whose persisted path is the legacy file, with a scanned file at the current path, is re-recorded and loads instead of the legacy 409; the same legacy row with no scanned file still answers the legacy 409. | 03 "Load resolves" ("legacy and vocab checks are unchanged") | With no scanned file, the seeded row reaches the port with `path is None` and the existing behaviour holds |
| AC-98.3 | unit | `RECORD_RULE`: a downloaded row at path P with a scanned file at Q ≠ P is re-recorded at Q (one commit); a downloaded row at P with a scanned file at P is not written (`commits` unchanged, no `mark_downloaded` call). | `RECORD_RULE` | The idempotent case commits nothing |
| AC-98.4 | integration | `LOAD_FAILURE_PATHS` for the weight file (`test_tts_device_resolution.py`, `_adapter`, `capture_logs`, `_events`), parametrized `path=None` and a nonexistent file: `load_model` raises `ModelLoadError("model weight file is missing")`, exactly one `tts.load_failed` is captured with `variant_id` the id, `device == "cpu"`, `error == "FileNotFoundError"`; no engine constructor ran and the adapter reports nothing loaded. TA-1 covers the unreadable case. | 03 "Logged failure"; known issue | A successful load in the same test module logs no `tts.load_failed` (`test_ac_98_5_success_logs_none`) |
| AC-98.5 | integration | `LOAD_FAILURE_PATHS` for the runtime and the format: (a) `torch` patched to `None` with a `.pth` variant: one event, `error == "ModelLoadError"`; (b) kokoro import raising `ImportError`: one event, `error` an `ImportError` type name; (c) the defensive unsupported-format branch (`adapter.py:260-261`). No constructible `ModelVariant` reaches it: `__post_init__` validates `format` with `require_enum` (`domain/tts.py:327`), so `dataclasses.replace(..., format="TFLite")` raises in construction. The test therefore builds a valid ONNX variant whose weight file exists and then forces the field on that one frozen instance, `object.__setattr__(variant, "format", "TFLite")`. The domain invariant is untouched. With the probe `lambda fmt: frozenset()` and `DeviceType.CPU` (`_resolve` only passes the format to the probe, `adapter.py:268-279`), `load_model` raises `ValidationError` matching "unsupported model format", and exactly one event is captured with `error == "ValidationError"` and `device == "cpu"`. At row 4 the raise already happens but nothing is logged, so the event-count assertion fails (an `AssertionError`); the row 5 adapter edit turns it Green. Each event carries the resolved target device. (d) A successful CPU load logs none. | `LOAD_FAILURE_PATHS`, `LOG_CAUSE` | The already-logged branches (AC-75.9 engine-init and session failures) still log exactly one event |
| AC-98.6 | integration | Contract (`test_tts_assets.py`, `CONTRACT_STACK`): `put_vocab`, `stack.wheel.hold` set (the spaCy auto-download stays pending), and a dropped `models_dir/kokoro-v1.0-onnx/onnx/model.onnx` that nothing marked. `GET /api/v1/models/downloaded` lists `kokoro-onnx-fp32`. `POST /api/v1/models/load {"variant_id":"kokoro-onnx-fp32","device":"cpu"}` answers 200, the `FakeSession` was built from that file, and the database row has that path and a `size_bytes` equal to the file size. The file is then deleted: the same `POST` answers 422 with `model weight file is missing` and exactly one `tts.load_failed` is captured. | 03 "Tests" (contract; removed file) | The pre-fix 422 on the first load is the defect |
| AC-98.7 | integration | Invariant (`test_tts_models.py`): `set(CATALOG_METADATA) == {v[0] for v in SEED_VARIANTS}`, so every id the scan can return has a seeded repository row. It passes at Red; it is a guard, not a Red proof. | `SIDELOAD_RECORD` (records only ids with a row) | A new scan id without a seed fails this test |
| AC-98.8 | integration | `SPACY_PATH_SWAP` (`test_tts_assets.py`, `isolated_path`): with spaCy install dirs under folders A and B, `activate_spacy_dir(A)` then `activate_spacy_dir(B)` leaves A's entry out of `sys.path` and B's entry last; `activate_spacy_dir(C)` (no install) leaves neither and `spacy_ready(C)` is False. An entry appended by the test itself that equals no current dir survives every call. Repeating `activate_spacy_dir(B)` changes nothing. | known issue; AC-73.12 | `insert(0, …)` is never used (AC-73.12 order) |
| AC-98.9 | integration | `SPACY_PATH_SWAP` through `CONTRACT_STACK`: `_install_spacy(stack)` makes `deps()["tts_spacy_model"]["state"]` `ready`; `stack.services.settings.set("tts", "models_directory", B)` with an empty B makes it `missing`, and A's install dir is not in `sys.path`. | known issue blast radius (Dependencies readiness) | Setting it back to A reads `ready` again |
| AC-98.10 | manual | `ESPEAK_STAGE`: row 10's probe receipt and either the `[B]` (b) block or Mat's AC-74.11 outcome, pasted in `walkthrough.md` §eSpeak and the handoff. | grouping D-100 | Absence never blocks the session |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|---|---|---|
| Record the sideload | Spec | 03 "Mark downloaded"; 02 "Sideload" (`SIDELOAD_RECORD`) |
| When to record | Local Canon | `RECORD_RULE` (D-124): the smallest rule that makes "load resolves" hold and stays idempotent |
| Size recorded | Spec / Local Canon | `MARK_SIGNATURE`: the repository already stats the file; row 1 corrects the 03 wording (D-125) |
| Load resolves | Spec | 03 "Load resolves" (`SIDELOAD_RECORD` in `load`) |
| Removed file | Spec | 03 "Tests" (`REMOVED_FILE`) |
| Logged failure and its cause | Spec / Local Canon | 03 "Logged failure"; grouping D-98 (error level, existing event) (`LOAD_FAILURE_PATHS`, `LOG_CAUSE`) |
| spaCy path after a directory change | Local Canon / Research-backed | known-issue fix line; `is_package` and `find_spec` behaviour (R-a, R-b) (`SPACY_PATH_SWAP`) |
| eSpeak live path | Local Canon | grouping D-100 (`ESPEAK_STAGE`) |

#### Files Modified

| File | Action | Summary |
|---|---|---|
| `packages/core/src/avkit_core/services/models.py` | modify | `_record_sideload`; called by `list_available` and `load` (`SIDELOAD_RECORD`, `RECORD_RULE`) |
| `packages/infrastructure/src/avkit_infra/tts/adapter.py` | modify | `LOAD_FAILURE_PATHS`, `LOG_CAUSE` |
| `packages/infrastructure/src/avkit_infra/tts/assets.py` | modify | `SPACY_PATH_SWAP` |
| `tests/unit/test_services.py` | modify | AC-98.1–98.3 |
| `tests/integration/test_tts_device_resolution.py` | modify | AC-98.4, AC-98.5; TA-1 |
| `tests/integration/test_tts_assets.py` | modify | AC-98.6, AC-98.8, AC-98.9 |
| `tests/integration/test_tts_models.py` | modify | AC-98.7 |

### Hub and state files (rows 1, 9, H1-3, H2)

| File | Action | Summary |
|---|---|---|
| `docs/build-plan/03-service-layer.md` | modify (row 1, row 9) | Row 1, §TTS sideload load: "Mark downloaded" reads `mark_downloaded(id, path)` and "the repository records the file size" (D-125); new rule rows **Record on scan** (`list_available` and `load` record a scanned file with a catalog row; no write when already recorded at that path; an id with no row stays display-only) and **spaCy directory change** (the entries av-kit appended for the old `models_directory` are removed on the next readiness check; others are never touched); the "Tests" row adds the spaCy swap. Row 9: a `> **Delivered (Session 42).**` note after the table naming this plan |
| `.agent/context/meu-status.yaml` | modify (row 9, H2-2) | MEU-98 `execution_plan` and `ready_for_review` (row 9, before the H1-2 gate binds this file); `approved` after review (H2-2) |
| `docs/BUILD_PLAN.md` | generated | AUTOGEN regions written only by `meu_status.py render` |
| `.agent/context/meu-registry.md` | generated | written by `meu_status.py render`; never hand-edited |
| `.agent/context/current-focus.md` | modify | the current focus names Session 42 (H1-3) |
| `.agent/context/known-issues.yaml` | modify | row 10 `verification` of `TTS-ESPEAK-LIVE-PATH-UNVERIFIED`; after H1-7b approval (H2-2): `MODEL-SIDELOAD-LOAD-500` and `TTS-SPACY-SYSPATH-STALE-DIR` → `resolved` with the handoff link, the rider's `meu_links` gains MEU-98; the eSpeak issue per `ESPEAK_STAGE` |
| `.agent/context/known-issues.md` | generated | written by `issue_triage.py render` (H2-2); never hand-edited |
| `.agent/context/grouping/2026-10-17-gui-shell-and-tts-sideload-session-grouping.md` | modify (H2-2) | Session 42 marked delivered |
| `docs/execution/metrics.md` | modify | the Session 42 row (H2-3) |

No `build-priority-matrix.md` edit: row 3.11 already exists and the matrix has no status column. No `02-infrastructure.md` edit: its "Sideload" line already says "mark it downloaded".

---

## Out of Scope

| Item | Kind | Deferred-to MEU | Basis |
|---|---|---|---|
| Un-marking a recorded file that was deleted | out-of-scope | — | 03 "Tests" asks only for the 422 and the log line (`REMOVED_FILE`) |
| Recording inside `ModelManager.sideload` | rejected | — | AC-9.8: the manager holds no unit of work; core owns the write (D-123) |
| A settings-change hook for `tts.models_directory` | rejected | — | widens scope to `wiring.py` and `SettingsService`; the next readiness check already swaps (D-128) |
| Unloading an already-imported spaCy model | out-of-scope | — | readiness is metadata-based (R-b); the process keeps what it imported until restart |
| Any REST, OpenAPI, IPC, GUI or MCP change | out-of-scope | — | 03 §TTS sideload load changes service behaviour only; `openapi --check` proves it |
| A fix for a failing AC-74.11 live run | deferred | new issue against MEU-74 | grouping D-100 (`ESPEAK_STAGE`) |
| Installing eSpeak NG | out-of-scope | — | a machine dependency, not product code; Mat's choice |

## BUILD_PLAN.md Audit

This project edits the D3 hub only through `meu_status.py` in row 9 (§Hub and state files). The validation is exact:

```powershell
rtk proxy uv run python tools/meu_status.py render --check *> C:/Temp/av-kit/s42-state-render.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/s42-state-render.txt; exit $code
```

```powershell
rtk proxy rg -n -e "MEU-98" -e "tts-sideload-load" -e "Delivered \(Session 42\)" docs/BUILD_PLAN.md docs/build-plan/03-service-layer.md .agent/context/meu-status.yaml *> C:/Temp/av-kit/s42-hub-rg.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/s42-hub-rg.txt; exit $code
```

Row 9's deliverable is that the `rg` receipt shows the 03 Delivered note, MEU-98 with `execution_plan` set to this plan, and the rendered `BUILD_PLAN.md` line; and that `render --check` exits 0.

## Verification Plan

All commands run from the repository root `P:/av-kit` in `pwsh`. Receipts go to `C:/Temp/av-kit/s42-*.txt`. The ids are PROFILE D6's (`.agent/docs/commands.md:190-210`); targeted runs are those argv with a file list. No Electron, Vitest or MCP id runs (`PRODUCT_SCOPE`).

### 1. Prerequisites and baseline (row 0)

- `uv sync --frozen --all-packages --python 3.12` (D-121), then `npm --prefix ui ci` for `state-canon`.
- `PREREQS` (S1).
- `git rev-parse HEAD > docs/execution/plans/2026-10-26-tts-sideload-load/baseline.sha`.
- The baseline receipts are `s42-base-py.txt`, from `py-tests` over the whole suite, and `s42-base-canon.txt`, from the two `state-canon` suites. The failed set is recorded in `walkthrough.md` §Baseline. A test failing at baseline is never counted as a regression; a test passing at baseline that fails later is one. The gate's baseline rule excuses only the three environmental packaging ids (AC-24.10, AC-25.10, AC-25.7; Sessions 35–40), and only when this receipt shows them `FAILED`.

### 2. Red (rows 2, 4 and 6)

Each change's new and amended tests are written first, on a tree that `RED_TREE` proves unchanged where it matters. They must fail by assertion. `red-check.py` declares no new name (`DECLARED_NEW = ()`), because every Red test drives an existing public surface.

- **A call that raises at baseline is wrapped:** a Red test whose call raises a documented domain error before the fix (for example the legacy 409 in AC-98.2) catches only that error type around the call, then asserts the outcome. So the failure is an `E assert` line, which `red-check.py` accepts, never a bare exception, which it refuses.
- **Log assertions use `capture_logs`** and count events by name (`_events`), so a missing log line is an assertion failure.
- **Row 2 (`SIDELOAD_RECORD`):** `pytest tests/unit/test_services.py tests/integration/test_tts_models.py -k "ac_98"` on a tree with no `packages/` change. `test_ac_98_1_list_available_records_sideload`, `test_ac_98_2_load_records_and_passes_path`, `test_ac_98_2_legacy_row_with_new_file_loads` and `test_ac_98_3_changed_path_rerecorded` must fail by assertion (`--require`). These may pass: `test_ac_98_1_core_does_no_file_io`, `test_ac_98_2_side_only_id_is_not_found`, `test_ac_98_2_vocab_conflict_unchanged`, `test_ac_98_2_legacy_row_without_file_still_conflicts`, `test_ac_98_3_same_path_not_written` and `test_ac_98_7_catalog_metadata_matches_seed`.
- **Row 4 (`LOAD_FAILURE_PATHS`):** `pytest tests/integration/test_tts_device_resolution.py tests/integration/test_tts_assets.py -k "ac_98_4 or ac_98_5 or ac_98_6 or ac_75_9_unreadable"` with `adapter.py` and `assets.py` unchanged. `test_ac_98_4_missing_weight_logs_load_failed` (both parameters), `test_ac_98_5_torch_absent_logs`, `test_ac_98_5_kokoro_import_logs`, `test_ac_98_5_unsupported_format_logs`, `test_ac_98_6_sideload_contract_list_then_load` (it reaches its 200 on the row 3 tree, then fails on the log count) and TA-1's `test_ac_75_9_unreadable_weight_file_is_model_load_error_neg` must fail by assertion. `test_ac_98_5_success_logs_none` may pass.
- **Row 6 (`SPACY_PATH_SWAP`):** `pytest tests/integration/test_tts_assets.py -k "ac_98_8 or ac_98_9"` with `assets.py` unchanged. `test_ac_98_8_activate_swaps_tracked_entry` and `test_ac_98_9_models_directory_change_reports_spacy_missing` must fail by assertion. `test_ac_98_8_untracked_entry_survives` may pass.

`RED_PROOF`: [red-check.py](red-check.py) decides each Red. Each Red command writes its child exit code to `<receipt>.exit` straight after `$code=$LASTEXITCODE`. The checker requires:

- a non-zero exit and exactly one pytest failing-run summary;
- no setup failure anywhere in the receipt, a collection error included;
- **every failure block is attributed:** one block per failed test (pytest `____ name ____` sections), the block count equal to the summary's failed count, at least one diagnostic per block, and every diagnostic an assertion (`E AssertionError`, `E assert`, `E Failed: DID NOT RAISE`);
- **`--require TITLE`:** each named stem has a failure block whose diagnostics are all assertions; the match is exact up to a non-digit (`test_ac_98_1` never matches `test_ac_98_10`).

`red-check.py --selftest` runs 37 receipt fixtures (11 positive, 26 negative), including one proving that a declared-name receipt is refused under the live, empty set (R-2).

### 3. Targeted Green (rows 3, 5 and 7)

Each Green row runs the files its change can reach, whole:

```powershell
rtk proxy uv run pytest tests/unit/test_services.py tests/unit/test_uow_commit_log.py tests/integration/test_tts_models.py tests/integration/test_tts_assets.py tests/integration/test_tts_voice_packs.py tests/integration/test_sqlite_uow.py tests/e2e/test_api_tts_models.py --tb=short -q -rfE *> C:/Temp/av-kit/s42-sl-green.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/s42-sl-green.txt -Tail 25; exit $code
```

```powershell
rtk proxy uv run pytest tests/integration/test_tts_device_resolution.py tests/integration/test_tts_models.py tests/integration/test_tts_assets.py tests/integration/test_tts_voice_packs.py tests/e2e/test_api_tts_models.py tests/e2e/test_api_error_surface.py --tb=short -q -rfE *> C:/Temp/av-kit/s42-lf-green.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/s42-lf-green.txt -Tail 25; exit $code
```

```powershell
rtk proxy uv run pytest tests/integration/test_tts_assets.py tests/integration/test_tts_voice_packs.py tests/integration/test_tts_models.py --tb=short -q -rfE *> C:/Temp/av-kit/s42-sp-green.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/s42-sp-green.txt -Tail 25; exit $code
```

Each Green row also runs `uv run pyright packages/` and `uv run ruff check packages/ tests/`. The task rows hold the exact commands.

### 4. Session gate (rows 8, H1-2): `session-gate.ps1`

The plan-local [session-gate.ps1](session-gate.ps1) runs in `pwsh` from the repository root. It writes one receipt per step (`C:/Temp/av-kit/s42-D6-<id>.txt`) and prints `<id> stage=<stage> exit=<n>` and the receipt tail. It is fail-fast in stage order: after the first non-zero step, every later step is printed as `not_run`. The steps, in order:

1. `identity-before`: `INPUT_IDENTITY` (§Validation stage contract).
2. **Static:** `py-types`, `py-lint`, `task-contract`, then `scope-paths` (`SCOPE_CHECK`, §5).
3. **Full:**
   - `py-tests`: the whole suite, `--tb=short -q -rfE`, with the baseline rule. An environmental packaging id is excused only if it appears as `FAILED <id>` in `s42-base-py.txt`, and a missing receipt excuses nothing. Any `ERROR` fails the step. The gate prints the excused ids.
   - `openapi`.
   - `state-render`.
   - `state-canon`: `npm --prefix ui run test -- tests/unit/layout-canon.test.ts tests/unit/queue-canon.test.ts`. These are the two suites that read `meu-status.yaml` and `docs/BUILD_PLAN.md` (D-122).
4. `identity-after`. The gate fails when `tested_state` differs between `identity-before` and `identity-after`.

The row's command is `rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-10-26-tts-sideload-load/session-gate.ps1`, with the receipt pattern (task row 8). The other UI ids, Electron and MCP D6 ids are not gate steps: no file under `ui/` or `mcp-server/` changes, and no API schema changes (`openapi`).

### 5. `SCOPE_CHECK` (row 8)

- **`scope-paths`:** every path in `git diff --no-renames --name-only -z <baseline>` plus `git ls-files --others --exclude-standard -z` is a Files Modified or Hub and state row, or one of this project's artifacts (this plan folder, the `2026-10-26-tts-sideload-load-*` handoffs, the reflection). With `--no-renames`, a rename shows its source deletion as well as its destination. `-z` keeps paths with spaces or non-ASCII names whole (R-4). The allow-list in the script is the union of those tables; changing either means changing both.

### 6. OpenAPI drift (G8)

No `packages/api/` file changes. `openapi.committed.json` is not regenerated, and the `openapi` D6 check (`--check`) must pass in the gate. H1-4 proves the committed file adds, removes and changes no schema since `baseline.sha` (any change is S5).

### 7. Closeout (H1, H2)

These are the template commands with this project's paths:

- `validate_closeout_artifacts.py` for the handoff, run twice: with `--handoff` + `--plan`, then with `--ac-coverage-only`;
- `durable_evidence.py --require-full`;
- the review-state parsers;
- the reflection validator, with `--decision-source` for the plan, the handoff, the 2026-10-17 grouping and `.agent/context/known-issues.yaml`, and `--decision-issue` for `MODEL-SIDELOAD-LOAD-500`, `TTS-SPACY-SYSPATH-STALE-DIR` and `TTS-ESPEAK-LIVE-PATH-UNVERIFIED`;
- `lint_task_contract.py`.

The handoff's AC table carries one cross-reference row per AC family it does not own (`AC-9`, `AC-12`, `AC-24`, `AC-25`, `AC-73`, `AC-74`, `AC-75`; the AC-24 and AC-25 rows cite the gate's baseline rule): the regression test (or gate rule) that keeps that family green.

## Stop Conditions

| ID | Condition | Action |
|---|---|---|
| S1 | Row 0 finds a graph directory, a cwd other than `P:/av-kit` or a branch other than `main`, D-103 still `open`, or a `PREREQS` status or symbol not as stated | Stop. Ask Mat, or re-run the context-tool gate. |
| S2 | The census finds an existing expectation this design contradicts outside `TEST_AMENDMENTS` (for example a commit count around `list_available`, or a `tts.load_failed` count on a newly logged branch) | Stop for the human with a Decision Brief naming the test and the smallest amendment. No test edit. |
| S3 | `red-check.py` refuses a Red receipt (`RED_PROOF`, §2), or `RED_TREE` refuses the tree | Fix the test setup only (or revert the early product edit), then re-prove Red. |
| S4 | AC-98.9 cannot read `missing` after the swap because `is_package` still resolves the old distribution (R-b does not hold on this runtime) | Stop for a Decision Brief with the measurement. Option B is a readiness check against the current directory's install dir. |
| S5 | `SCOPE_CHECK` finds a path outside `PRODUCT_SCOPE`, or `openapi.committed.json` changes | Revert that change or stop with a Decision Brief. |
| S6 | A test that passed at baseline fails in the gate | Fix the product change; never relax or skip the test. If the old behaviour was the contract, stop with a brief. |
| S7 | Review cap (plan 3, execution 6) or the reviewer is unavailable | HARD STOP with a TL;DR (create-plan §5d). Mat is the fallback reviewer. |

## Decision Log

Research engine for this plan: `native` (Claude Code reading of the av-kit source, the installed spaCy 3.8.15 source and the Python and structlog documentation, 2026-10-26). Grouping §8 D-94, D-95, D-103, D-98, D-99 and D-100 carry forward unchanged into the reflection (stage `grouping`). "Triage D-86" is the 2026-10-17 triage decision in `known-issues.yaml` (`:2540`) that the spec cites. This plan's ids start at D-120.

```yaml
decision_log:
  - id: D-120
    stage: planning
    question: "Where is the plan written and executed?"
    resolution: autonomous
    class: two-way
    chosen: "P:/av-kit on main; no branch or worktree"
    source_tag: Human-approved
    precedents: ["Mat 2026-10-26: no branches, everything on main and pushed (AGENTS.md section Commits)", "Session 40 committed on main as b6b288e; its grouping edit resolves D-103"]
    research: { engine: none, sources: [] }
    reasoning: "The plan was drafted in a worktree while Session 40's files were uncommitted in P:/av-kit. Mat then ruled out branches and worktrees, and Session 40 has committed, so the plan lives and executes on main. PREREQS still checks that D-103 is resolved before any product edit."
  - id: D-121
    stage: planning
    question: "Which interpreter does the environment use?"
    resolution: autonomous
    class: two-way
    chosen: "uv sync --frozen --all-packages --python 3.12 in row 0"
    source_tag: Local Canon
    precedents: ["P:/av-kit/.venv is CPython 3.12"]
    research: { engine: none, sources: [] }
    reasoning: "The gate's identity hashes the interpreter and its distribution set; 3.12 matches the main tree and the pinned wheels. An explicit --python keeps uv from picking another interpreter."
  - id: D-122
    stage: planning
    question: "Which D6 ids does the gate run?"
    resolution: autonomous
    class: two-way
    chosen: "The Python ids (py-types, py-lint, task-contract, scope-paths, py-tests, openapi, state-render), plus state-canon (the Vitest layout-canon and queue-canon suites), with the input identity before and after"
    source_tag: Local Canon
    precedents: ["Session 40 gate (Electron/UI/MCP ids for a renderer change)", "PRODUCT_SCOPE has no ui/ or mcp-server/ file", "ui/tests/unit/layout-canon.test.ts:18-19 and queue-canon.test.ts:18-19 read meu-status.yaml and docs/BUILD_PLAN.md"]
    research: { engine: none, sources: [] }
    reasoning: "No renderer, IPC or MCP file changes and no schema changes, which openapi --check proves. Running the Electron suite would add about 10 minutes and load other sessions on this machine without testing anything this plan changes. Row 9 and H2-2 do write the two state files that the two Vitest canon suites read, so those suites run in the gate and again in H2-2, as in Session 40."
  - id: D-123
    stage: planning
    question: "Where is a sideloaded file recorded, and when?"
    resolution: autonomous
    class: two-way
    chosen: "SIDELOAD_RECORD: a private ModelService step that scans once and calls mark_downloaded for each scanned id with a repository row that RECORD_RULE selects, in one unit of work with one explicit commit call when it wrote anything, at the start of list_available and of load"
    source_tag: Spec
    precedents: ["03 'Mark downloaded' and 'Load resolves'", "02-infrastructure.md:447 'detect a dropped .pth/.onnx and mark it downloaded'", "AC-9.8 (the manager holds no unit of work)", "AC-12.8 (a sideload-only id is listed)"]
    research: { engine: none, sources: [] }
    reasoning: "Core owns the unit of work and the scan already flows through ModelCatalogPort, so the service is the one place that can persist without new I/O in core. Recording in load as well means a POST /models/load right after a drop works without a prior list. A load-only lookup that never persists was rejected: it keeps the database wrong for every other reader (list, MCP, status). Recording in ModelManager.sideload was rejected by AC-9.8."
  - id: D-124
    stage: planning
    question: "Which scanned rows are written?"
    resolution: autonomous
    class: two-way
    chosen: "RECORD_RULE: not downloaded, or a different path"
    source_tag: Local Canon
    precedents: ["manager.py:97-113 (the scan skips legacy files)", "repositories.py:365-373 (mark_downloaded is a plain update)"]
    research: { engine: none, sources: [] }
    reasoning: "Writing only on a difference makes repeated GET /models free of commits. Comparing paths also repairs a legacy row and a managed file replaced by a dropped one. Comparing sizes was rejected: it would need a stat in core."
  - id: D-125
    stage: planning
    question: "03 cites mark_downloaded(id, path, size_bytes); does the port change?"
    resolution: autonomous
    class: two-way
    chosen: "No. Keep mark_downloaded(variant_id, path); row 1 corrects the 03 wording"
    source_tag: Local Canon
    precedents: ["ports/storage.py:99-106", "repositories.py:365-373 sets size_bytes from the file"]
    research: { engine: none, sources: [] }
    reasoning: "The repository already records the size, so a third argument would duplicate it and force core to stat the file. The spec row describes the outcome; its signature is corrected to match the port."
  - id: D-126
    stage: planning
    question: "What happens when a recorded file is removed?"
    resolution: autonomous
    class: two-way
    chosen: "REMOVED_FILE: the row stays recorded; load answers 422 and logs once"
    source_tag: Spec
    precedents: ["03 'Tests': a file removed after the scan returns the 422 and the log line"]
    research: { engine: none, sources: [] }
    reasoning: "The spec names this outcome. Un-marking on scan would need a second rule for managed downloads and is not asked for."
  - id: D-127
    stage: planning
    question: "Which load failures log, with which device and cause?"
    resolution: autonomous
    class: two-way
    chosen: "LOAD_FAILURE_PATHS and LOG_CAUSE: every failing load_model logs exactly one tts.load_failed; weight-path failures log device cpu; error names the cause"
    source_tag: Spec
    precedents: ["03 'Logged failure' ('every load failure, including a missing weight file … with the variant and cause')", "grouping D-98 (error level, the existing event)", "adapter.py:249-252 logs device cpu when no device was tried"]
    research: { engine: native, sources: ["https://www.structlog.org/en/stable/testing.html"] }
    reasoning: "One event per failure keeps the log query simple and matches the existing branches. ModelLoadError alone would not say why, so the cause's type is logged where there is one. Device cpu for a failure before resolution follows the probe-failure branch: nothing was tried and the adapter is left unloaded on cpu."
  - id: D-128
    stage: planning
    question: "How does readiness stop seeing the old spaCy folder?"
    resolution: autonomous
    class: two-way
    chosen: "SPACY_PATH_SWAP: activate_spacy_dir tracks the entries it added and swaps them for the current directory's on every call"
    source_tag: Research-backed
    precedents: ["known-issue fix 'swap the tracked entry when models_directory changes'", "03 'spaCy path' (append, AC-73.12)", "TtsAssetAdapter.state and spacy_ready call activate on every readiness check (assets.py:136, :247)"]
    research: { engine: native, sources: ["https://docs.python.org/3/library/importlib.html#importlib.util.find_spec", "spacy/util.py is_package (spaCy 3.8.15, importlib_metadata.distribution)"] }
    reasoning: "Every readiness path already calls activate with the current directory, so the swap needs no settings hook and no wiring change. Tracking only what av-kit added keeps user or site entries safe. is_package resolves distribution metadata on sys.path, so readiness reads False after the swap even when the module stays in sys.modules (find_spec alone would still succeed). A settings hook was rejected as wider than the rider; a check against the current dir only was rejected because the stale entry would still shadow imports."
  - id: D-129
    stage: planning
    question: "Where does the contract test live?"
    resolution: autonomous
    class: two-way
    chosen: "CONTRACT_STACK in tests/integration/test_tts_assets.py; no new e2e file"
    source_tag: Local Canon
    precedents: ["test_tts_assets.py Stack (:128-225) runs the production build_services and create_app", "tests/e2e/api_fakes.py fakes the services, so an e2e test there would not reach ModelService"]
    research: { engine: none, sources: [] }
    reasoning: "The spec's contract test must cross the real service and repository. The Stack already does, with only the engines faked, and has the vocab, spaCy and wait helpers the test needs."
  - id: D-130
    stage: planning
    question: "How does the eSpeak stage close when eSpeak NG is absent?"
    resolution: autonomous
    class: two-way
    chosen: "ESPEAK_STAGE: probe; absent → [B] (b) with evidence and a fresh verification; present → Mat runs AC-74.11"
    source_tag: Local Canon
    precedents: ["grouping D-100", "grouping Session 42 'If it is absent, the issue stays open and the session still closes'"]
    research: { engine: none, sources: [] }
    reasoning: "The stage is evidence, not code. A missing dependency is a valid [B] reason with a pasted probe. The probe is the production EspeakCliAdapter.status(), not shutil.which alone, so an installation outside PATH under Program Files counts as present (plan review round 1 F2). Installing eSpeak NG is Mat's machine choice, so the agent never installs it."
  - id: D-131
    stage: planning
    question: "How does a Red row prove it ran before its fix?"
    resolution: autonomous
    class: two-way
    chosen: "RED_TREE: each Red command refuses a change to the product files its Green row edits"
    source_tag: Local Canon
    precedents: ["Session 40 rows 2 and 4 (baseline renderer and row 3 snapshot)"]
    research: { engine: none, sources: [] }
    reasoning: "Each Green row edits one product file, so a per-file diff against baseline.sha is enough; a hash snapshot like Session 40's row3-ui-src.json is not needed."
```

## Research References

- Python `importlib.util.find_spec` (returns `sys.modules[name].__spec__` when the module is already imported): https://docs.python.org/3/library/importlib.html#importlib.util.find_spec (R-a)
- spaCy `spacy.util.is_package` (3.8.15: `importlib_metadata.distribution(name)`, a metadata lookup over `sys.path`): installed source `P:/av-kit/.venv/Lib/site-packages/spacy/util.py:993-1003` (R-b)
- structlog testing (`structlog.testing.capture_logs`): https://www.structlog.org/en/stable/testing.html
- Python `sys.path` and `importlib.invalidate_caches`: https://docs.python.org/3/library/importlib.html#importlib.invalidate_caches

The plan relies on two facts. After an entry leaves `sys.path` and caches are invalidated, `importlib.metadata` no longer finds the distributions under it, so `is_package` is False. `find_spec` alone would keep answering for an imported module, which is why readiness needs both (the existing `spacy_ready` already checks both).

## Planning receipts

- **R-0 (2026-10-26).** Discovery: `meu_status.py stats` (`C:/Temp/av-kit/s42-plan-stats.txt`), exit 0: 98 MEUs, 91 approved, 1 closed, 6 pending. MEU-98 is pending (band P2, matrix 3.11).
- **R-1 (2026-10-26).** `identity.py --selftest`, exit 0, 0 failures (`C:/Temp/av-kit/s42-plan-R-identity.txt`). Each bound path, an untracked test file and the runtime keys (`python`, `espeak_ng`, `node`, the distribution-set hash) change `tested_state` and make `durable_evidence.evidence_problems` refuse the earlier full record. Edits to the closeout artifacts leave it unchanged.
- **R-2 (2026-10-26).** `red-check.py --selftest`, exit 0, 37 fixtures, 0 wrong (`C:/Temp/av-kit/s42-plan-R-redcheck.txt`).
- **R-3 (2026-10-26).** `session-gate.ps1` parses with 0 PowerShell parse errors (`C:/Temp/av-kit/s42-plan-R-gate-parse.txt`). It was not run during planning, because it needs the execution baseline.
- **R-4 (2026-10-24, carried).** Session 40's `scope-paths` probe (rename source, spaces, non-ASCII); the Python body is unchanged here apart from the allow-list.
- **R-5 (2026-10-26).** `lint_task_contract.py --allowed-builder-classes avkit_builder,avkit_coordinator,avkit_verifier` over `task.md`, exit 0: "27 row(s) … 25 row(s) fully checked … 2 row(s) exempt (view_file): H1-5, H2-1" (`C:/Temp/av-kit/s42-plan-R-task-lint.txt`).
- **R-6 (2026-10-26).** eSpeak probe: `where.exe espeak-ng` finds nothing and `C:/Program Files/eSpeak NG` is absent.
- **R-7 (2026-10-26).** Plan review round 1 (`.agent/context/handoffs/2026-10-26-tts-sideload-load-plan-critical-review.md`, `changes_required`) was corrected in place:
  - F1: AC-98.5(c) now forces `format` on a built variant, because `replace` fails domain validation before the adapter runs.
  - F2: `ESPEAK_STAGE`, row 10 and `identity.py` use `EspeakCliAdapter().status()`.
  - F3: "commit" means the explicit `uow.commit()` call (`RECORD_RULE`).
  - F4: the swap trigger is spaCy readiness or a successful load, not a model list.
  - Residual: `identity.py` records `node --version` for `state-canon`.
  - Re-checks: `identity.py --selftest` exit 0, 0 failures (R-1 receipt); `ruff check --ignore E501` on `identity.py` clean (the E501 long lines carry over from Session 40's copy and are outside the gate's `packages/ tests/` scope); task lint exit 0 (R-5 receipt). Live probe: `_espeak_identity()` = `<absent>`, `node` = `v24.19.0`.
- **R-8 (2026-10-26).** Mat ruled out branches and worktrees. The plan moved to `main` in `P:/av-kit`: D-120 and D-121, `PREREQS`, row 0's check (the repository root and `main`, in place of the worktree, branch and merge-base checks), S1 and the working-directory lines. No AC, contract or test changed.
- **R-a / R-b (2026-10-26, native).** The Python `find_spec` reference and the installed spaCy `is_package` source (§Research References).

## Validation stage contract

- **Static:** `py-types`, `py-lint`, `task-contract`, `scope-paths` (§4).
- **Targeted:** §3 after each production edit (blocking for its row).
- **Fresh full:** §4 in one pass after the last input edit, from the repository root, `pwsh`. Row 8 runs it after the product edits. Row 9 then changes bound inputs (`meu-status.yaml`, the rendered `BUILD_PLAN.md`, the 03 note), so H1-2's run is the fresh full record the handoff carries. It must pass; no partial, cached or reused receipt counts. Re-run all of §4 if any input changes after it (H1-6b).
- **Runtime (manual):** the eSpeak stage (row 10), recorded, non-blocking.
- **Input identity (`INPUT_IDENTITY`):** [identity.py](identity.py) prints the runtime identity and `tested_state`, which is HEAD plus one SHA-256. The hash covers:
  - **The work tree:** the tracked diff and the untracked (not ignored) files of the whole work tree. It excludes only this session's own closeout outputs, which no suite or gate step reads: this plan folder's `*.md`, this session's handoffs and reflection, `docs/execution/metrics.md`, `.agent/context/current-focus.md` and `known-issues.yaml`/`.md`. So `uv.lock`, `openapi.committed.json`, this plan's scripts, `docs/build-plan/`, `docs/BUILD_PLAN.md`, `meu-status.yaml`, `meu-registry.md` and the grouping files are bound.
  - **The runtime identity, observed live:** the Python running it, the SHA-256 of its installed distribution set, the versions of `onnxruntime`, `kokoro`, `torch` and `spacy`, the `espeak-ng` path and version that `EspeakCliAdapter().status()` resolves (`<absent>` when unavailable), because eSpeak detection changes which voices the TTS suites report, and `node --version`, because `state-canon` runs Vitest.

  `--state-only` computes the same value. The gate records the state before and after it runs (§4), and the handoff's final full `evidence.v1` record carries it. H1-6b re-derives it live with `identity.py --state-only`, so any bound change refuses the old record and forces H1-2 again.
- **Evidence:** each receipt's exit code and decisive lines, pasted as `evidence.v1` in the handoff.

## Execution Correction Notes

These are recorded during execution so that no plan-level contract changes silently. The execution review sees each item.

| Item | Change | Evidence |
|---|---|---|
| ECN-1 baseline re-record | Row 0 first ran at HEAD `d30f62b`. Its four `test_framework_adoption.py` failures were a stale `AGENTS.md` rule-map pin after `bb481ec`. Mat chose "Update pin, commit+push" (AskUserQuestion, 2026-10-27), which became `c34866b`. Row 0 was re-run there, and `baseline.sha` records `c34866b`. The baseline failed set is the one environmental id `test_mcp_snippet_keys[AC-25.7]`. | `walkthrough.md` §Baseline; `s42-base-py.txt` |
| ECN-2 B-10 location | The plan puts row 10's `### B-10` `evidence.v1` block in `walkthrough.md`. The blocked-row predicate that `lint_task_contract.py` and `durable_evidence.blocked_evidence_problems` share reads the task file itself, so the block lives in `task.md`. Row 10's task cell cites `B-10` and links the follow-up `TTS-ESPEAK-LIVE-PATH-UNVERIFIED` (`known-issues.yaml`). `walkthrough.md` §eSpeak mirrors the outcome. The `[B]` (b) outcome itself is unchanged. | `task.md` §B-10; `s42-b10-lint.txt` (`OK: 27 row(s)`), `s42-b10-evidence.txt` (`OK`) |
| ECN-3 receipts root | The scratch row runner sets `$env:RECEIPTS_DIR='C:/Temp/av-kit'` before each row command. `lint_task_contract.py` needs it on this instantiated tree, and the plan's commands keep writing under `C:/Temp/av-kit`. No command changed. | row 8 `task-contract` exit 0 |
