---
project: "2026-09-30-tts-repair"
date: "2026-09-30"
source: "docs/build-plan/03-service-layer.md#tts-runtime-assets-residual; docs/build-plan/11-page-layout.md#tts-model-manager-residual; docs/build-plan/11-page-layout.md#tts-text-panel-residual"
meus: ["MEU-62", "MEU-63", "MEU-64"]
status: "approved"
template_version: "2.2"
---

# Implementation Plan: TTS repair (Session 27)

> **Project:** `2026-09-30-tts-repair`
> **Build plan:** `docs/build-plan/03-service-layer.md` §TTS runtime assets (residual) (`:410-424`, matrix 3.5). `docs/build-plan/11-page-layout.md` §TTS model manager (residual) (`:101-111`, matrix 11.10) and §TTS text panel (residual) (`:115-125`, matrix 11.11). §Test-ID migration TT 1–28 (`:231-258`).
> **Grouping:** `.agent/context/grouping/2026-09-30-gui-walkthrough-residuals-session-grouping.md`, Session 27 (`:57-66`), with decisions D-1 to D-7 (`:156-166`).
> **Status:** `approved` by the independent plan review in Round 2 (user-directed Fable 5.1 subagent; `.agent/context/handoffs/2026-09-30-tts-repair-plan-critical-review.md`), with 8 non-blocking correction notes folded in (§Round 2 Correction Notes). Execution needs a direct user message (`plan_to_exec_gate: human`), recorded in [human-gate-decision.md](human-gate-decision.md) §Execution authorization.

## Goal

Make TTS produce audio again, and make its failures visible. Then fix the two TTS page usability findings from Mat's 2026-09-30 walkthrough.

- **MEU-62 `svc-tts-runtime-assets`** (core, infra, API, MCP, and the Settings Dependencies card):
  - Two Kokoro runtime assets become managed downloads (D-22): the `config.json` vocab/config and spaCy `en_core_web_sm`.
  - Both assets get readiness rows.
  - Generation fails fast with a 409 that names the missing asset.
  - Every `Failed` job carries an `error_message`, and `tts.generate*` events reach the console.
- **MEU-63 `gui-tts-model-manager`:** replaces the hidden "Manage" disclosure with a model picker and one state-driven Get / Load / Unload button. It shows the asset readiness chips next to the picker, and renders `job.error_message` in the run bar.
- **MEU-64 `gui-tts-text-panel`:**
  - Adds **Apply cleanup**.
  - Removes the redundant raw preview.
  - Replaces the full-width language select and the 236 px voice list with a searchable voice combobox, so Speed and Format fit the default window.

Order: MEU-62 → MEU-63 → MEU-64 (grouping `:61`). MEU-63 uses MEU-62's readiness rows and error text. MEU-64 shares `TTSPage.tsx` and its test files.

The worktree baseline is the branch HEAD when execution starts; row 0 records it in `baseline.sha`. Planning started from `175680c`. Treat the live files as the baseline and reset nothing.

## Context Tool Decision

```yaml
context_tool_decision:
  phase: planning
  eligible_tools: []
  decision: not_applicable
  eligibility_basis: "graphify-out/ and graphify-out-research/ are absent (ls: No such file or directory, 2026-09-30); no headroom on PATH (`which headroom` empty). Scope is Python service/adapter code plus one TSX page; direct file/search per .agent/docs/context-tool-decision-gate.md."
  human_message_reference: null
```

Task row 0 re-evaluates this before execution (create-plan §5f). The `prereq` check refuses if a graph directory has appeared.

## Harness, driver and reviewer route

- **Driver:** Claude Code in the claude.ai/code container. That means `native_shell: bash`, no `rtk`, no `pwsh`, no Codex CLI, and `plan_to_exec_gate: human` (`.agent/context/harness.local.md` §Claude Code; `.agent/docs/harness-profiles.md:120-123`). `fresh_worker` is the Agent tool with `.claude/agents/`. Rows keep `compact_continue` as the fallback.
- **Reviewer:** a Fable 5.1 subagent, same vendor, authorized by the user in [human-review-decision.md](human-review-decision.md). Plan cap 3, execution cap 6.
- **Gate location:** the Sessions 25/26 split ([human-gate-decision.md](human-gate-decision.md) A-1):
  - The container pre-gate is non-authoritative.
  - `WINDOWS_GATE` and `TTS_LIVE` run on Mat's machine and are authoritative.
  - Container commands call tools raw, which is the unfiltered equivalent of `rtk proxy`. `validate-task.ps1` runs every stage through `rtk proxy` (output-evidence-policy; Session 26 amendment A2).
- **Receipts:** `$RECEIPTS_DIR` in the container (default `/tmp/av-kit`), `C:/Temp/av-kit/` on Windows (`.agent/docs/macos-setup.md` §`RECEIPTS_DIR`).

## Handoff Set

| Scope | Canonical handoff |
|---|---|
| `MEU-62` | `.agent/context/handoffs/2026-09-30-tts-repair-MEU-62-handoff.md` |
| `MEU-63` | `.agent/context/handoffs/2026-09-30-tts-repair-MEU-63-handoff.md` |
| `MEU-64` | `.agent/context/handoffs/2026-09-30-tts-repair-MEU-64-handoff.md` |

Rolling reviews:

- `.agent/context/handoffs/2026-09-30-tts-repair-plan-critical-review.md`
- `.agent/context/handoffs/2026-09-30-tts-repair-implementation-critical-review.md`

## Work Packages and Context Lifecycle

| ID | Work | depends_on | context_strategy | durable_outputs |
|---|---|---|---|---|
| WP-0 | Prerequisites, baseline, `TEST_AMENDMENTS` census (task rows 0, 2) | — | `shared` | `walkthrough.md` §Baseline, §Census; `baseline.sha` |
| WP-1 | Record `LOCAL_REPRO` (row 1; gates MEU-63/64 Red only) | — | `shared` | `walkthrough.md` §LOCAL_REPRO; `known-issues.yaml` verification blocks |
| WP-2 | MEU-62 TDD and handoff (rows 3–6) | WP-0 | `compact_continue` | MEU-62 handoff; compact, then re-read `task.md` and the handoff |
| WP-3 | MEU-63 TDD and handoff (rows 7–9) | WP-2, WP-1 | `compact_continue` | MEU-63 handoff; compact, then re-read |
| WP-4 | MEU-64 TDD and handoff (rows 10–12) | WP-3 | `compact_continue` | MEU-64 handoff; compact, then re-read |
| WP-5 | Hub reconciliation and new known issues (row 13) | WP-4 | `shared` | `docs/build-plan/03…`, `11…`, `known-issues.yaml` |
| WP-6 | H1 closeout, `WINDOWS_GATE` + `TTS_LIVE`, execution review, H2 | WP-5 | `compact_continue` | handoffs, gate result JSONs, rolling review, reflection |

**Split flag (grouping `:65`, D-3).** Suppose the MEU-62 handoff (row 6) lands with the session past about 50 % of its context. Then the session compacts at that boundary and continues as "27b" from `task.md` and the MEU-62 handoff. Nothing is re-planned: rows 7–H2 stay as written. Every artifact the split needs is already durable, so the split is a compaction, not a new plan.

---

## User Review Required

> [!IMPORTANT]
> These items are for the plan-review loop and for the user's execution message. They are not a pause point before review.
>
> 1. **Execution authorization** (`plan_to_exec_gate: human`). After the reviewer approves, execution starts only on a direct user message. It is recorded in [human-gate-decision.md](human-gate-decision.md) §Execution authorization.
> 2. **`TEST_AMENDMENTS` TA-1 to TA-9** (§Single-statement contracts). These are the only pre-approved changes to existing test expectations. Each one follows a Spec or Human-approved rule change, cited per row. The execution message (or an explicit carve-out in it) approves them. Row 2's census stops execution for any contradiction outside this list (Stop condition S3).
> 3. **Decisions D-8 to D-17** (§Decision Log) are resolved autonomously and logged. Five of them adjust the build-plan text of 03 §TTS runtime assets / 11 §TTS residuals, and row 13 carries those edits into the spec:
>    - D-8: vocab needed by every variant.
>    - D-9: one shared vocab location.
>    - D-10: spaCy needed on any variant, for English voices or whenever the default-on `chunk` step runs.
>    - D-12: asset downloads go through `POST /models/download`.
>    - D-15: registry test IDs.
>
>    The user may veto any of them in the execution message.
> 4. **New egress host.** The spaCy wheel comes from `github.com/explosion/spacy-models` releases, a new outbound host next to Hugging Face (D-22 fixed "wheel URL pinned", and the model is hosted only there). `docs/build-plan/07-distribution.md:9` says "everything except YouTube / Hugging Face calls works offline". Row 13 adds the GitHub release host to that sentence.

---

## Proposed Changes

### Single-statement contracts

Each name below is defined once here. ACs, task rows and scripts refer to these names and never restate the values (PR-9).

| Name | Definition | Source |
|---|---|---|
| `TTS_ASSETS` | Closed `StrEnum` `TtsAsset` in `avkit_core/domain/tts.py` with exactly `ONNX_VOCAB = "tts_onnx_vocab"` and `SPACY_MODEL = "tts_spacy_model"`. Every `match` over it is exhaustive (`assert_never`), so pyright fails the build when a member is added. | Spec 03:418 (row names) |
| `ASSET_STATES` | Closed `StrEnum` `AssetState` with `ready`, `missing`, `downloading`. | Spec 03:418 |
| `SPACY_LANG_CODES` | `frozenset({"a", "b"})`. These are the Kokoro lang codes whose `KPipeline` builds `misaki.en.G2P`, which loads the spaCy model. | Research-backed: kokoro 0.9.4 `pipeline.py:106-113`; misaki 0.9.4 `en.py:497-503` |
| `SPACY_STEPS` | `frozenset({"chunk"})`. These are the prepare steps whose implementation loads the spaCy model (`services/prepare.py:150-161` `_chunk`). `chunk` is in `PREPARE_DEFAULT_ON` (`prepare.py:24`; UI `tts-prepare.ts:17-19`), so the GUI default needs spaCy for **every** voice. | Local Canon `services/prepare.py:9,24,150-161,250-251` |
| `REQUIRED_TTS_ASSETS(variant, voice, enabled_steps)` | `{ONNX_VOCAB}` for every variant (D-8), plus `SPACY_MODEL` when `voice.voice_id[0] in SPACY_LANG_CODES` **or** `enabled_steps ∩ SPACY_STEPS ≠ ∅` (D-10). `KOKORO_LANG_CODES` is defined in the core domain as the nine prefixes `a b e f h i j p z`. A pytest parity assertion ties it to the keys of `avkit_infra/tts/voices.py:68-78` `LANG_BY_PREFIX` (core cannot import infra). A lang code outside it raises `ValidationError`, so the function fails closed. | D-8, D-10 |
| `VOCAB_LOCATION` | `{tts.models_directory}/config.json`. It is resolved at call time from settings by one function, `resolve_vocab_path(settings)` in `avkit_infra/tts/assets.py`. It is fetched from `ONNX_VOCAB_REPO` / `ONNX_VOCAB_FILE` (`adapter.py:31-32`). **Valid** means it parses as JSON with a dict `vocab` (the rule `_load_onnx_vocab` already enforces, `adapter.py:150-166`). | D-9; Local Canon `adapter.py:31-32` |
| `SPACY_MODEL_PIN` | `{"3.8": WheelPin(name=SPACY_MODEL, version="3.8.0", url="https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl", sha256="1932429db727d4bff3deed6b34cfc05df17794f4a52eeb26cf8928f7c1a0fb85")}`, keyed by the installed spaCy `major.minor`. `SPACY_MODEL` is the existing core constant `avkit_core.services.prepare.SPACY_MODEL` (`prepare.py:9`), never restated. In this plan, a bare `SPACY_MODEL` in prose, a pin or a predicate means that constant. The enum member is always written `TtsAsset.SPACY_MODEL` (wire value `tts_spacy_model`) (Review R2-6). The lock has spaCy 3.8.15 (`uv.lock:2399`); the wheel METADATA says `spaCy >=3.8.0,<3.9.0`. The sha256 was measured on 2026-09-30: a 12 806 118-byte download from that URL, 35 members, `en_core_web_sm-3.8.0.dist-info/` present. | Human-approved D-22 ("wheel URL pinned to the installed spaCy major.minor"); Research-backed (download + METADATA read at plan time) |
| `SPACY_INSTALL_DIR` | `{tts.models_directory}/spacy/en_core_web_sm-3.8.0/`. This is the wheel's contents extracted as-is, including `.dist-info`, so `spacy.util.is_package(SPACY_MODEL)` and `spacy.load(SPACY_MODEL)` both resolve once the directory is on `sys.path`. | D-11 |
| `SPACY_READY` | After `activate_spacy_dir(settings)`: `spacy.util.is_package(SPACY_MODEL)` **and** `importlib.util.find_spec(SPACY_MODEL) is not None`. The first conjunct is the predicate misaki checks before it would run `spacy.cli.download` (misaki `en.py:500-501`). It is metadata-only (`importlib_metadata.distribution`, spaCy `util.py:993-1003`), so the second conjunct makes a corrupt install (dist-info present, package directory missing) read `missing`. That keeps `SPACY_INSTALL_EXISTING`'s stale branch reachable (Review R2-2). | Research-backed (misaki and spaCy source) |
| `ASSET_MISSING_ERROR` | `ConflictError(f"tts asset missing: {asset.value}")`. It maps to HTTP 409 with envelope `error.code == "ConflictError"` (`api/errors.py:25-42`). It is the outcome of `load` and `generate`. `POST /tts/prepare` (Preview, Apply) keeps its existing contract: `SpacyModelNotFoundError` → 503 (`errors.py:35`), unchanged by this plan. Both spellings mean "spaCy missing" on different routes, and each route has exactly one. | Spec 03:419; Local Canon `errors.py:35` |
| `TTS_LOG_EVENTS` | `tts.generate` (job_id, voice, variant), `tts.generate_done` (job_id, output), `tts.generate_failed` (job_id, error), all on the existing `structlog.get_logger(module="tts")` in `services/tts.py:48`. The same list is used for the console check. | Spec 03:420 |
| `CONSOLE_FIELDS` | `("job_id", "error")`. When an event carries one of these keys, `HealthService._process` appends ` key=value` to the console message in this order, and runs `redact_message` over the whole string. Other keys are unchanged. | D-13 |
| `MODEL_ACTION` | For the selected variant: `get` when it is not downloaded, `load` when it is downloaded and not loaded, `unload` when it is the loaded variant. The button's `data-testid` follows the action: `model-get-btn` / `model-load-btn` / `unload-btn`. It is computed by one pure function, `resolveModelAction` in `tts-controls.ts`, from the existing `getEnabled` / `loadEnabled` predicates. | Human-approved (11:107-108); D-15 |
| `RUN_BAR_ERROR` | `error` (client) if it is non-empty. Otherwise `job.error_message` when `job.status === "Failed"` and it is non-empty. Otherwise none. `resolveRunBarSlot` returns `'error'` exactly when `RUN_BAR_ERROR` is not none. | Spec 11:110 |
| `DEFAULT_WINDOW` | 1280 × 800 (`ui/src/main/index.ts:138`). Electron settles to about 1280 × 773 (`download-queue.test.ts:1112`). "Visible without scrolling" means the element's bounding box bottom is ≤ `window.innerHeight` with `document.scrollingElement.scrollTop == 0` and the TTS page scroll container at `scrollTop == 0`. | Spec 11:124 |
| `VOICE_CATALOG_FIXTURE` | `ui/tests/e2e/fixtures/tts-voices.json`: the full production voice list (54 voices, `VOICE_COUNT`, `avkit_infra/tts/voices.py:80`) in the `GET /tts/voices` item shape. It is generated once in row 10 from `list_voice_configs()`. A pytest parity test (`tests/unit/test_tts_voice_fixture.py`) fails if the file diverges from `list_voice_configs()`. `installTtsSeam` takes an optional `voices` argument, which the AC-64.6 spec (and only that spec) sets to this fixture. The one-voice default for the other specs is unchanged. | Review R1 F1; Spec 11:124 |
| `TEST_AMENDMENTS` | TA-1 to TA-9 below: the only approved changes to existing test expectations. | AGENTS §Testing & TDD |
| `GATED_PATHS` | The executable copy is the `gated` list in `validate-task.sh` `windows-gate-check`, and `plan_checks.py static` asserts it equals this list: `ui packages mcp-server tests tools pyproject.toml uv.lock openapi.committed.json docs/build-plan/11-page-layout.md docs/build-plan/gui-actions-index.md docs/execution/plans/2026-09-26-p11-layout-canon/implementation-plan.md .agent/context/grouping/2026-09-03-p11-page-layout-session-grouping.md .agent/model-registry.local.json .agent/model-registry.local.yaml docs/execution/plans/2026-09-30-tts-repair/validate-task.ps1 docs/execution/plans/2026-09-30-tts-repair/tts_live_check.py`. That is the code plus exactly the non-code files the gate stages read: `openapi` reads `openapi.committed.json`; `layout-canon.test.ts:14-17` reads `11-page-layout.md`, the p11 layout-canon plan and the p11 grouping; `gui-actions-audit.test.ts:12` reads `gui-actions-index.md`; `test_framework_adoption.py:472` reads the registry overlay. **Excluded, stated as a rule:** `.agent/context/meu-status.yaml` and `docs/BUILD_PLAN.md` (read by `state-render` and `layout-canon.test.ts:17-18`) are SSOT. They change only at H1-3 (before the gate) and at H2-2 (after approval), and cloud-local §3.4 treats such doc-only closeout edits as not reopening the gate. H2-2 (`post-review-state`) re-runs `state-render` and the doc-reading Vitest to prove the post-gate SSOT edits keep them green (Review R2-3). | cloud-local §3.3 item 2, §3.4 |
| `COUNT_FLOORS` | Vitest total ≥ 675 and Electron expected ≥ 110, the last authoritative gate (Session 26 attempt 7, `2026-09-28-p11-capture-settings/windows-gate-result.json:116-121`). pytest reports failed == 0 and its passed count is recorded. Every later attempt must have pytest passed ≥ the first attempt that produced a pytest count. The `.ps1` carries that value forward as `pytest_floor`. The executable copies are the literals in `validate-task.sh` `windows-gate-check`; `plan_checks.py static` asserts they equal 675 / 110. | cloud-local §3.3 |

**`TEST_AMENDMENTS`.** Each row changes only what its rule changes. Other assertions in the same test stay as they are.

| TA | Test (file:line) | Current expectation | Amended expectation | Rule |
|---|---|---|---|---|
| TA-1 | `ui/tests/unit/tts-page.test.ts:55`, `:167` | `preview-raw` in the Wave 2 id list and in the page source | Removed from the list. A new assertion checks that the source does **not** contain `preview-raw`. | Spec 11:122, 11:125 ("`preview-raw` removed with its assertions amended") |
| TA-2 | `ui/tests/unit/tts-page.behavior.test.ts:227` (AC-56.2) | `preview-raw` and `preview-cleaned` share a parent | `preview-cleaned` is absent before Preview and present after it. `preview-raw` is absent. | Spec 11:122 |
| TA-3 | `tts-page.behavior.test.ts:236-242` (AC-56.3) | Open `model-manage-toggle`, then `model-row` rows, each with `model-get-btn` | `model-select` lists the variants. For a not-downloaded selection the action button has `data-testid="model-get-btn"`. `model-row` is the single picker row. | Human-approved 11:107-108; D-15 |
| TA-4 | `ui/tests/e2e/tts-generate.test.ts:258`, `:342-346`, `:443-446` | Click `model-manage-toggle`, then per-row Get/Load, then `unload-btn` | Select a variant in `model-select`, then click the state-driven button (`model-get-btn` → `model-load-btn` → `unload-btn`). The IPC/REST ledger assertions are unchanged. | Human-approved 11:107-108 |
| TA-5 | `tts-page.behavior.test.ts:169`, inside the shared `renderPage()` setup helper (`:163-175`) | The setup waits until `voice-card` count equals `VOICES.length` | The setup waits until `voice-selected-chip` shows the persisted voice. This is setup only, so every test's starting state (combobox closed) is unchanged. The `VOICES.length` count moves into the AC-64.4 test, after the combobox is opened. | Research-backed 11:123 (popup listbox) |
| TA-6 | `tts-page.behavior.test.ts:262`, `:329` | `voice-grid` queried directly | Open the combobox first, then the same assertions | Research-backed 11:123 |
| TA-7 | `tts-generate.test.ts:260`, `:346`, `:349`, `:458` | `voice-grid` / `voice-card` / `language-select` visible without interaction | Open `voice-combobox` first. `language-select` is visible inside the open popup. | Research-backed 11:123; D-16 |
| TA-8 | Settings suites that pin the Dependencies card to exactly two rows (census names the lines) | exactly yt-dlp and FFmpeg rows | These two rows keep their text and order. Two rows follow them: `tts-asset-row-tts_onnx_vocab` and `tts-asset-row-tts_spacy_model`. | Spec 03:418 |
| TA-9 | `tests/unit/test_domain.py:321` (`SPEC_MODEL_DOWNLOAD_RUNTIME_FIELDS`, asserted at `:517-523` AC-2.9 and `:595-605` AC-2.12); `mcp-server/tests/action-index.test.ts:38` (`ACTION_INDEX` `toHaveLength(67)`); any other test the census finds pinning the `DependenciesOut` / `DependencyHealth` key set | exact old sets and counts | superset: +2 dependency keys; +1 runtime field `asset` (so the domain tuple becomes `("variant_id","asset","state","fraction","error_message")`. `asset` is a required dataclass field, with no default. Every existing `ModelDownloadRuntime(...)` construction in `packages/` and `tests/` passes `asset=None` explicitly: a `FIXTURE_REPAIRS`-class setup edit in tests, and a production edit in `services/models.py` (Review R2-5)); +1 MCP action `download_asset` (so `toHaveLength(68)`). Every old key and value is unchanged. | Spec 03:418, 03:422; D-12 |

**`FIXTURE_REPAIRS`.** `assets: TtsAssetPort` is a **required keyword-only** collaborator of `HealthService`, `TTSService` and `ModelService`, with no default. A missing wiring must fail at construction, not silently use a stub. Adding `assets=<fake>` to existing test constructions is setup-only fixture repair, allowed by AGENTS §Testing ("fixture repairs may fix setup"): about 18 constructions across `tests/unit/test_services.py`, `tests/integration/*`, `tests/e2e/api_fakes.py:497-525`. It changes no assertion and is not a TA row; the handoff lists every touched construction.

**Environment-bound census** (cloud-local §4). The container pre-gate tolerates only these failures. `WINDOWS_GATE` tolerates none.

| Tier | Member | Signature / handling |
|---|---|---|
| Vitest | AC-51.6 `ui/tests/unit/layout-primitives.test.ts` | The CRLF prefix hash recomputes to `819760B9…` (`vitest_env_ok`, copied from Session 26). |
| Vitest | AC-41.3 `ui/tests/unit/queue-canon.test.ts` | `P:/zorivest` is absent and `styles.css` is unchanged since `f7d3134`. |
| Electron | capture-picker specs in `ui/tests/e2e/capture-picker.test.ts` | Not on Windows, the stub `.exe` is absent, and the failure is exactly the stub-missing error (`electron_env_ok`). |
| pytest | the Windows-bound tooling tests (`tests/tooling/*`; 61 at Session 26) | `pytest_env_ok`: the container's failed set must be a subset of the failed set at `baseline.sha`, collected by the same command in a worktree (Session 26 A9/A10-R pattern). Any new failure is real. |
| External inputs | `P:/agentic-framework` HEAD; `P:/.agent/model-registry.json` hash | `validate-task.ps1` records both before stage 1. On attempt ≥ 2 a mismatch with the previous attempt stops before stage 1 (cloud-local §3.2). |

### MEU-62 — `svc-tts-runtime-assets`

#### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---|---|---|---|
| REST `POST /api/v1/models/download` body | `ModelDownloadIn` (`api/schemas/models.py:12`) | Exactly one of `variant_id: str (min_length=1)` or `asset: Literal["tts_onnx_vocab","tts_spacy_model"]` (`TTS_ASSETS` wire values). A `model_validator(mode="after")` rejects both-present and neither-present. | `extra="forbid"` (`ApiModel`, `schemas/common.py:8-11`). Invalid input → 422. |
| REST `GET /api/v1/models/download-runtime` response | `ModelDownloadRuntimeOut` (`:53`) | adds `asset: Literal[…] \| None`. At most one of `variant_id` / `asset` is non-null. | response model, `extra="forbid"` |
| REST `GET /api/v1/health/dependencies` response | `DependenciesOut` (`api/schemas/health.py:31`) | adds `tts_onnx_vocab: TtsAssetOut`, `tts_spacy_model: TtsAssetOut`. `TtsAssetOut{available: bool, version: str \| None, state: Literal["ready","missing","downloading"]}` is a superset of `VersionAvailabilityOut{version, available}` (D-14). `available == (state == "ready")`. | response model, `extra="forbid"` |
| REST `POST /api/v1/models/load` / `POST /api/v1/tts/generate` | unchanged bodies | new 409 outcomes only (`ASSET_MISSING_ERROR`). OpenAPI declares `409` in `responses=` for `/models/load`, `/models/download` and `/tts/generate`. | unchanged |
| MCP `avkit_models` action `download_asset` | `modelsSchema` zod member (`mcp-server/src/toolsets/models.ts:28-45`) | `{action: "download_asset", asset: z.enum(TTS_ASSET_WIRES)}` `.strict()` → `POST /models/download {asset}`. `TTS_ASSET_WIRES` is exported once from `models.ts`. | `.strict()`. Unknown enum or extra key is rejected before fetch (`TOOL_ERROR`). |
| File import: downloaded `config.json` | `validate_vocab_file` in `avkit_infra/tts/assets.py` | JSON object with a dict `vocab` (the same rule as `adapter.py:150-166`) | Invalid file → `ModelDownloadError`; the file is removed so `VOCAB_LOCATION` is never left half-valid. |
| File import: spaCy wheel | `install_spacy_wheel` in `avkit_infra/tts/assets.py` | sha256 == `SPACY_MODEL_PIN.sha256`. Every zip member path must be relative, contain no `..` segment, not be absolute or drive-qualified, and resolve inside a temporary extraction dir. The dir is moved into place with `os.replace` only after full success. | Any violation → `ModelDownloadError`, no `SPACY_INSTALL_DIR` created (atomicity: extract to `…/spacy/.tmp-<uuid>`, then `os.replace`). **Existing destination (`SPACY_INSTALL_EXISTING`):** when `SPACY_READY` is already true, `download(asset=TtsAsset.SPACY_MODEL)` raises `ConflictError("tts asset already ready: tts_spacy_model")` → 409 and fetches nothing. When `SPACY_INSTALL_DIR` exists but `SPACY_READY` is false (a corrupt install), the worker `shutil.rmtree`s the stale directory after sha256 verification and before `os.replace`. Both run inside the download worker that `ModelService._lock` admits one at a time. `assets.py` never imports `huggingface_hub` (AC-9.12, `tests/integration/test_tts_models.py:641-661`); the vocab fetch stays in `model_manager/manager.py`. |
| Settings | `tts.models_directory` (`services/settings.py:66-75`) | existing key; no new key | unchanged |

#### Acceptance Criteria

The call chain for every integration AC starts at a named production entrypoint:

- `build_services` (`api/wiring.py:116`) → the route (`routes/models.py`, `routes/tts.py`, `routes/health.py`) → the service method → the adapter.
- MCP: `modelsSchema` → `registry.ts` → HTTP client → the same route.

| AC | Type | Description | Source | Negative Test |
|---|---|---|---|---|
| AC-62.1 | unit | `TtsAsset`, `AssetState` and `REQUIRED_TTS_ASSETS` exist as defined. The `match` over `TtsAsset` is exhaustive (pyright `reportMatchNotExhaustive` stays clean). | Spec 03:418; D-8, D-10 | A lang code outside `KOKORO_LANG_CODES` (`"x"`) raises `ValidationError` instead of returning a set. A `j`/`z`/`e` voice with `enabled_steps` that exclude `chunk` returns `{ONNX_VOCAB}` only. The same voice with `["chunk"]` returns both assets. An `a` voice with `[]` returns both. A parity test fails if `KOKORO_LANG_CODES` and `LANG_BY_PREFIX` keys diverge. |
| AC-62.2 | integration | `ModelService.download(variant_id)` for **any** variant also fetches `VOCAB_LOCATION` via `hf_hub_download(repo_id=ONNX_VOCAB_REPO, filename=ONNX_VOCAB_FILE, local_dir=models_dir)` and validates it. A weight file that is already present no longer short-circuits a missing vocab (`manager.py:48-79`). Observable: files on disk plus the `hf_hub_download` call ledger. | Human-approved D-22 (03:416); D-8, D-9 | With the weight present and the vocab absent, exactly one `hf_hub_download` call is made (`config.json`) and zero for the weight file. An invalid `config.json` (no `vocab` dict) ends `Failed` with a non-empty runtime `error_message`, and no `config.json` is left on disk. |
| AC-62.3 | integration | `list_available` / `list_downloaded`: a variant is `is_downloaded: true` only when its weight **and** a valid `VOCAB_LOCATION` exist. `GET /models/available` reflects this. | Spec 03:416 ("not loadable") | Weight present, vocab missing → `is_downloaded: false` in the REST body. |
| AC-62.4 | integration | `ModelService.load` refuses with `ASSET_MISSING_ERROR(ONNX_VOCAB)` before calling the port → `POST /models/load` returns 409 `ConflictError` naming `tts_onnx_vocab`. | Spec 03:416, 03:419 | Vocab missing → the fake adapter's `load_model` call count is 0, and the status stays "not loaded". |
| AC-62.5 | integration | `KokoroAdapter` reads the vocab from a `vocab_path: Callable[[], Path]` resolver that `build_services` passes as `resolve_vocab_path(settings)` (`wiring.py:167`). ONNX chunks use it (`adapter.py:150-176`). The PyTorch load passes `KModel(repo_id=ONNX_VOCAB_REPO, config=str(path), model=…)`, so kokoro never calls `hf_hub_download` for `config.json` (kokoro `model.py:43-48`). The `onnx_vocab_path: Path` keyword stays as an override for tests. | D-8, D-9; Research-backed (kokoro 0.9.4 `KModel.__init__`) | `FakeKModel` records `config` and `repo_id`. A PyTorch load with the vocab absent never reaches `KModel`, because AC-62.4 refuses first. Changing `tts.models_directory` after startup makes the next ONNX chunk read the new location (the resolver is evaluated per call). |
| AC-62.6 | integration | `ModelService.download(asset=TtsAsset.SPACY_MODEL)` does the following: picks `SPACY_MODEL_PIN[spacy major.minor]`; streams the URL through an injected `fetch` (production: `urllib.request` with the process proxy environment); verifies sha256; extracts under the Boundary Inventory wheel rules; `os.replace`s into `SPACY_INSTALL_DIR`; calls `activate_spacy_dir`; ends with `SPACY_READY` true. Runtime `asset="tts_spacy_model"` and `state="Downloading"` while it runs, then `Idle`. | Human-approved D-22 (03:417); D-11 | Three negatives: (a) a sha256 mismatch ends `Failed` with an `error_message` containing `sha256`, and `SPACY_INSTALL_DIR` does not exist; (b) an unpinned spaCy minor (`"3.9"` patched in) gives `Failed` with `no pinned {SPACY_MODEL} for spaCy 3.9`, and `fetch` is never called; (c) a wheel member `../evil.py` gives `Failed`, nothing is written outside the temp dir, and the temp dir is removed; (d) `SPACY_INSTALL_EXISTING`: with `SPACY_READY` true, `POST /models/download {asset: "tts_spacy_model"}` → 409 and `fetch` call count 0; with a stale `SPACY_INSTALL_DIR` (dist-info present, package dir missing), a download replaces it and ends `SPACY_READY` true. |
| AC-62.7 | integration | `ModelService.load` of any variant, when `SPACY_READY` is false and the runtime is not `Downloading`, starts the spaCy download (AC-62.6 path) and logs `model.asset_download_started asset=tts_spacy_model`. When the runtime is `Downloading`, it does not start and logs `model.asset_download_deferred`. The check-then-start is atomic under `ModelService._lock` (the existing lock, `models.py:86-108`). The runtime is `Downloading` with `asset=tts_spacy_model` **before `load` returns**, so a caller that polls afterwards (for example `tts_live_check.py`) cannot race it. | Human-approved D-22 (03:417 "triggered on first … load"); D-10 widens it from PyTorch-only to any variant | While a variant download is running, load starts no second thread (the thread count stays 1) and the runtime still names the variant. |
| AC-62.8 | integration | `HealthService.dependencies()` returns rows `tts_onnx_vocab` and `tts_spacy_model` per `ASSET_STATES`. `downloading` is used when the runtime's `asset` equals that row. `ready` means valid `VOCAB_LOCATION` / `SPACY_READY`. Otherwise `missing`. `GET /health/dependencies` serializes them as `TtsAssetOut`. `HealthService` receives an `assets: TtsAssetPort` (new core port `ports/tts.py`, adapter in `avkit_infra/tts/assets.py`) from `build_services`. | Spec 03:418 | Fresh models directory → both rows `missing` with `available: false`. With a runtime fixed at `Downloading` + `asset=tts_spacy_model`, the spaCy row is `downloading` and the vocab row stays `missing` (the states are independent). |
| AC-62.9 | integration | `TTSService.generate`, after voice validation (`tts.py:129-132`) and **before** the job row is created (`:135`), raises `ASSET_MISSING_ERROR` for the first missing member of `REQUIRED_TTS_ASSETS(loaded variant, voice, enabled_steps)`, in `TtsAsset` declaration order. `POST /tts/generate` → 409 whose message names the asset. | Spec 03:419 | With `TtsAsset.SPACY_MODEL` missing and an `am_*` voice: 409 naming `tts_spacy_model`; zero `tts_jobs` rows; no file under `tts.output_path`; `KPipeline` constructed 0 times; a spy on `spacy.cli.download` called 0 times. A `jf_*` (`j`) voice with `enabled_steps=["chunk"]` and spaCy missing → 409 naming `tts_spacy_model`, with zero rows (the default-GUI path; `prepare._chunk` is never reached). The same voice with `enabled_steps=[]` passes the check (no spaCy needed). |
| AC-62.10 | integration | `TTS_LOG_EVENTS` are emitted, with their fields, on the success path and on each failure path (verified with `structlog.testing.capture_logs`). With `CONSOLE_FIELDS` the console ring message reads `tts.generate_failed job_id=<id> error=<message>`. | Spec 03:420; D-13 | An event without `CONSOLE_FIELDS` keys keeps its exact message (`test_ac_13_6` unchanged). An `error` value containing a `REDACT_NEEDLES` token is redacted in the ring message (existing `redact_message` fail-closed rule). |
| AC-62.11 | integration | Every `Failed` job has a non-empty `error_message`, on all three paths: `ValidationError` (re-raised → 422), `DomainError` (returned, 201), and **any other exception**. The last path marks the job `Failed` with `f"{type(exc).__name__}: {exc}"` (or the type name alone when the message is empty), logs `tts.generate_failed`, and re-raises (500 `internal_error`). | Spec 03:421; Local Canon AGENTS §Code Quality | Fake adapter raising `RuntimeError("hf 503")` from `generate` → the DB row is `Failed` (not `Generating`) with `error_message == "RuntimeError: hf 503"`, and `_current_id` is reset (a second generate is not a 409 overlap). |
| AC-62.12 | integration | `POST /models/download` accepts `{variant_id}` (unchanged) or `{asset}` → 202. A concurrent download → 409. The runtime endpoint reports `asset`. | Spec 03:422; D-12 | `{}`, `{variant_id, asset}`, `{asset: "tts_bogus"}`, `{asset: "tts_spacy_model", x: 1}` → 422 each, and no download thread starts. |
| AC-62.13 | integration | MCP `avkit_models` `download_asset` action → `POST /models/download` with body `{asset}` (MCP contract test with the fixture HTTP ledger). The description names the action. `registry.ts` has one new row for the same path. | Local Canon 03:451 ("5 MCP: Same methods"); D-12 | `{action:"download_asset", asset:"x"}` and `{action:"download_asset", asset:"tts_spacy_model", extra:1}` → `TOOL_ERROR` with zero fetches. |
| AC-62.14 | integration | `build_services` passes the vocab resolver to `KokoroAdapter` and `assets` to `HealthService` / `TTSService` / `ModelService`, and calls `activate_spacy_dir(settings)` once, so an installed model is importable after a restart. | Spec 03:416; D-11 | With `SPACY_INSTALL_DIR` absent, activation leaves `sys.path` unchanged (no dangling entry). With it present, `SPACY_READY` becomes true (fixture wheel built in `tmp_path`). `activate_spacy_dir` is idempotent: calling it twice leaves exactly one `sys.path` entry for the directory. |
| AC-62.15 | integration | The Settings → Dependencies card (`SettingsPage.tsx:924-953`) renders the two asset rows after yt-dlp and FFmpeg. Each row has a `StatusChip` (Ready / Missing / Downloading). A missing row has a `tts-asset-get-btn-<asset>` button that sends `POST /models/download {asset}` and then refetches `['health','dependencies']`. No new IPC. | Spec 03:418 ("GUI card renders them without new IPC") | A `ready` row has no Get button. A `downloading` row's Get button is disabled. The fetch ledger shows no `window.api` call for this action. |
| AC-62.16 | integration | Regression: an ONNX load with a valid vocab present yields samples (`test_ac_9_*` fakes, `test_tts_models.py:209-286`). | Spec 03:424 | Vocab present but without a `vocab` dict → `ValidationError` (existing rule, kept). |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|---|---|---|
| The two assets and managed downloads | Human-approved | D-22 (grouping D-1; `known-issues.yaml` TTS-GENERATE-FAILED-SILENT enrichment) |
| Vocab needed by PyTorch too | Research-backed | D-8: kokoro `KModel` downloads `config.json` from HF when `config` is None |
| One shared vocab location, resolved per call | Local Canon | D-9: `manager.py` layout; `models_directory` is a runtime setting |
| spaCy needed by ONNX too | Research-backed | D-10: `adapter.py:245-249` builds `KPipeline(model=False)` → `en.G2P` |
| spaCy install mechanism | Research-backed | D-11: wheel = zip with `.dist-info`; `spacy.util.is_package` uses package metadata |
| Asset Get transport (no new route) | Local Canon | D-12: extend `ModelDownloadIn` |
| Console visibility of the failure reason | Local Canon | D-13 |
| Row shape "same as existing rows" | Local Canon | D-14: superset of `VersionAvailabilityOut` |
| Unexpected exceptions during generate | Local Canon | AGENTS §Code Quality; AC-62.11 |
| Where the fail-fast check sits | Spec | 03:419 "before synthesis"; placed before job creation so no row or WAV exists |

#### Files Modified

| File | Action | Summary |
|---|---|---|
| `packages/core/src/avkit_core/domain/tts.py` | modify | `TtsAsset`, `AssetState`, `SPACY_LANG_CODES`, `KOKORO_LANG_CODES`, `required_tts_assets`; `ModelDownloadRuntime.asset` |
| `packages/core/src/avkit_core/ports/tts.py` | modify | `TtsAssetPort` protocol: `state(asset)`, `download(asset, on_progress)`, `activate()` |
| `packages/core/src/avkit_core/services/models.py` | modify | vocab-aware download/list/load, asset download, spaCy auto-trigger |
| `packages/core/src/avkit_core/services/tts.py` | modify | fail-fast, `TTS_LOG_EVENTS`, catch-all failure marking |
| `packages/core/src/avkit_core/services/health.py` | modify | asset rows; `CONSOLE_FIELDS` in `_process` |
| `packages/core/src/avkit_core/domain/health.py` | modify | `DependencyHealth` asset fields |
| `packages/infrastructure/src/avkit_infra/tts/assets.py` | new | `resolve_vocab_path`, `validate_vocab_file`, `SPACY_MODEL_PIN`, `install_spacy_wheel`, `activate_spacy_dir`, `TtsAssetAdapter` |
| `packages/infrastructure/src/avkit_infra/tts/adapter.py` | modify | vocab resolver; `KModel(config=…)` |
| `packages/infrastructure/src/avkit_infra/model_manager/manager.py` | unchanged | planned as modify; the vocab fetch after the weights landed in `ModelService._run_download` instead (D-20, review F5) |
| `packages/api/src/avkit_api/wiring.py` | modify | resolver, assets port, startup activation |
| `packages/api/src/avkit_api/schemas/models.py`, `schemas/health.py` | modify | `ModelDownloadIn` validator, runtime `asset`, `TtsAssetOut` |
| `packages/api/src/avkit_api/routes/models.py`, `routes/tts.py`, `routes/health.py` | modify | asset branch; `409` in `responses=` |
| `openapi.committed.json` | modify | regenerated only after `--check` reports drift (G8) |
| `mcp-server/src/toolsets/models.ts`, `mcp-server/src/toolsets/registry.ts` | modify | `download_asset` action |
| `ui/src/renderer/src/features/settings/SettingsPage.tsx` | modify | two Dependencies rows + Get |
| `ui/tests/e2e/test-ids.ts` | modify | MEU-62 block: `tts-asset-row-tts_onnx_vocab`, `tts-asset-row-tts_spacy_model`, `tts-asset-get-btn-tts_onnx_vocab`, `tts-asset-get-btn-tts_spacy_model` |
| `tests/unit/test_services.py`, `tests/integration/test_tts_models.py`, `tests/integration/test_tts_assets.py` (new), `tests/e2e/test_api_tts_models.py`, `tests/e2e/test_api_health_settings.py`, `tests/e2e/api_fakes.py`, `tests/integration/test_api_wiring.py` | modify/new | AC-62.1–62.16 |
| `mcp-server/tests/models-assets.test.ts` (new) | new | AC-62.13 |
| `ui/tests/unit/settings-page.test.ts`, `ui/tests/e2e/settings.test.ts` | modify | AC-62.15 (+TA-8) |

### MEU-63 — `gui-tts-model-manager`

#### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---|---|---|---|
| UI → `POST /models/download` | `downloadBody` zod in `tts-commands.ts` (next to `loadBody`, `:44-49`) | `z.union([z.object({variant_id: z.string().min(1)}).strict(), z.object({asset: z.enum(TTS_ASSET_WIRES)}).strict()])`. `TTS_ASSET_WIRES` is a UI mirror, pinned to the MCP/Python values by a Vitest parity assertion that reads `openapi.committed.json`. | `.strict()`. The server still validates (422). |
| UI → `POST /models/load` | `loadBody` (`tts-commands.ts:44-49`) | unchanged: device `auto\|cuda\|cpu\|mps` | unchanged |
| UI model picker value | `SelectInput` options from `GET /models/available` | value is a catalog `id`. A stale id not in the catalog resets to the loaded or first variant. | not user text |

#### Acceptance Criteria

Call chain: `TTSPage` (route `/tts`) → `useModelsAvailable` / `useModelStatus` / `useDownloadRuntime` / `['health','dependencies']` → `tts-commands.ts` mutations → REST.

| AC | Type | Description | Source | Negative Test |
|---|---|---|---|---|
| AC-63.1 | integration | The Voice section shows a `model-select` `SelectInput` listing every catalog variant with a state suffix: `— not downloaded`, `— downloading N%`, `— downloaded`, `— loaded`. Its default selection is the loaded variant, else the first downloaded one, else the first in the catalog. `device-select` sits in the same row (`model-row`). | Human-approved 11:107; Local Canon G30 | A catalog without the previously selected id falls back without throwing. The suffix never says `loaded` for a variant that is not `status.variant_id`. |
| AC-63.2 | integration | One primary `Button` whose label and `data-testid` follow `MODEL_ACTION`: **Get** → `POST /models/download {variant_id}`, **Load** → `POST /models/load {variant_id, device}`, **Unload** → `POST /models/unload`. While the selected variant is downloading, it reads "Getting…" and is disabled. | Human-approved 11:108 | For a not-downloaded selection the fetch ledger has zero `/models/load` calls after clicking. For the loaded selection the label is never Get or Load. The button is disabled while `runtime.state === 'Downloading'`, for any target. |
| AC-63.3 | integration | Next to the picker, two readiness chips come from `GET /health/dependencies` (`tts-asset-chip-tts_onnx_vocab`, `tts-asset-chip-tts_spacy_model`). A `missing` chip has its Get (`tts-asset-get-btn-<asset>` inside the TTS page scope) → `POST /models/download {asset}`. `download-progress` / `download-progress-bar` render under the picker row for variant or asset downloads. | Spec 11:109 | A `ready` chip has no Get. While `downloading`, Get is disabled and the progress bar shows `runtime.fraction`. |
| AC-63.4 | unit | `resolveRunBarSlot({error, status, jobError})` returns `'error'` exactly when `RUN_BAR_ERROR` is not none. The error banner renders `RUN_BAR_ERROR`'s text. | Spec 11:110 | A `Failed` job with an empty `error_message` and no client error → `'output'`. A `Done` job with a stale non-empty `error_message` → not `'error'`. A client error wins over a job error. |
| AC-63.5 | integration | The run bar shows `job.error_message` for a `Failed` job, in `error-banner` (jsdom behavior test with the fetch ledger, and Electron seam). | Spec 11:110; Local Canon G25 | The same page with a `Done` job shows no `error-banner`. |
| AC-63.6 | integration | Test-ID migration is recorded below. The Electron flow (seam) runs: select a not-downloaded variant → Get → progress → Load → Unload. The REST ledger shows each call once, in order. | Spec 11:111 | Clicking the action button while it is disabled adds no ledger entry. |

**Test-ID migration (MEU-63).** Registry values are the canonical strings. The spec's `get-btn` / `load-btn` (11:111) are the registered `model-get-btn` / `model-load-btn` (`test-ids.ts:137-139`); D-15.

| Existing ID | Migration | Detail |
|---|---|---|
| `model-manager` | keep | Voice-section model block container |
| `model-manage-toggle` | change | Becomes a "Model details" disclosure that holds `loaded-model-details`. It no longer hides the picker or actions. |
| `loaded-model` | keep | `StatusChip` in the Voice header |
| `loaded-model-details` | move | inside the "Model details" disclosure |
| `model-row` | change | the single picker row (select + device + action), not one row per variant |
| `model-get-btn` / `model-load-btn` / `unload-btn` | change | one button; `data-testid` follows `MODEL_ACTION` |
| `device-select` | move | into `model-row`, beside the picker |
| `download-progress` / `download-progress-bar` | move | under `model-row` |
| `error-banner` | keep | now also fed by `job.error_message` |
| new: `model-select`, `tts-asset-chip-tts_onnx_vocab`, `tts-asset-chip-tts_spacy_model` | add | MEU-63 block in `test-ids.ts` |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|---|---|---|
| Picker + one action | Human-approved | 11:107-108; triage D-1/D-2 |
| State suffix text | Local Canon | the triage D-2 option text ("not downloaded / downloaded / loaded"), plus "downloading N%" from `useDownloadRuntime` |
| Default selection | Local Canon | D-17: loaded, then first downloaded, then first |
| Where the Manage toggle goes | Spec | 11:111 keep/move/change; PRESERVED_TESTIDS (11:152) forbids silent removal → D-15 |
| Error surface | Spec | 11:110 |

#### Files Modified

| File | Action | Summary |
|---|---|---|
| `ui/src/renderer/src/features/tts/TTSPage.tsx` | modify | Voice model block recomposed (`:401-522`); run-bar error source (`:250`, `:697-701`) |
| `ui/src/renderer/src/features/tts/tts-controls.ts` | modify | `resolveModelAction` |
| `ui/src/renderer/src/features/tts/tts-run-bar.ts` | modify | `jobError` input |
| `ui/src/renderer/src/features/tts/tts-commands.ts` | modify | `downloadBody` union, `postDownloadAsset` |
| `ui/src/renderer/src/features/tts/useTtsJob.ts` | modify | runtime `asset`; dependencies query hook shared with Settings |
| `ui/tests/e2e/test-ids.ts` | modify | MEU-63 block |
| `ui/tests/unit/tts-page.behavior.test.ts`, `ui/tests/unit/tts-page.test.ts`, `ui/tests/unit/tts-run-bar.test.ts` (new if absent), `ui/tests/e2e/tts-generate.test.ts` | modify/new | AC-63.1–63.6, TA-3/TA-4 |

### MEU-64 — `gui-tts-text-panel`

#### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy |
|---|---|---|---|
| UI → `POST /tts/prepare` | `prepareBody` zod (`tts-commands.ts:24-30`) | unchanged (text, enabled steps from `PREPARE_STEPS`, `chunk_max_chars`) | `.strict()` unchanged |
| UI → `PUT /settings/tts` (`input_text`, `voice`) | existing `putSettings` (`tts-commands.ts:195-204`) | unchanged. Apply goes through the existing 300 ms debounced `scheduleInputText` (`TTSPage.tsx:183-191`). | unchanged |
| Voice combobox query | local state | free text, trimmed, case-insensitive substring match on `voice_id`, `name`, `language` | not sent anywhere |

#### Acceptance Criteria

Call chain: `TTSPage` → `postPrepare` / `scheduleInputText` / `chooseVoice` → REST.

| AC | Type | Description | Source | Negative Test |
|---|---|---|---|---|
| AC-64.1 | integration | `apply-cleanup-btn` (secondary `Button`, beside Preview) calls `POST /tts/prepare` with the current text, enabled steps and `chunk_max_chars`. On success it sets the textarea to `cleaned_text`, marks `input_text` touched, schedules the debounced `PUT /settings/tts {input_text}`, and clears the cleaned preview. | Human-approved 11:121 | Empty or whitespace text → disabled, no fetch. A prepare failure → the textarea is unchanged, no PUT, and `error-banner` shows the message. |
| AC-64.2 | integration | `preview-raw` is gone. `preview-cleaned` mounts only after a successful Preview and unmounts when the text changes or Apply runs. | Human-approved 11:122 | Before any Preview, `queryByTestId('preview-cleaned')` is null. After editing the text, it is null again. |
| AC-64.3 | unit | `preview-cleanup-btn` uses the `secondary` button variant, the same as Apply, so it reads as a button (TTS-CLEANUP-PREVIEW-REDUNDANT resolution path). | Local Canon G30; `known-issues.yaml` resolution path | The source assertion fails if the `ghost` variant comes back. |
| AC-64.4 | integration | `VoiceCombobox` (`features/tts/VoiceCombobox.tsx`) follows the WAI-ARIA APG combobox pattern: an input `voice-combobox` with `role="combobox"`, `aria-expanded`, `aria-controls`, `aria-activedescendant`. The popup listbox `voice-grid` (`role="listbox"`) mounts when open and holds `role="group"` sections per language with `voice-card` options (`role="option"`, `aria-selected`). Typing filters by `voice_id` / `name` / `language`. ArrowDown/Up move, Home/End jump, Enter selects (→ `chooseVoice` PUT), Escape closes without changing the voice. The current voice shows as `voice-selected-chip`. | Research-backed 11:123 (APG combobox); Human-approved delegation (triage D-8/D-9) | A query with no match shows "No voices match", and Enter sends no PUT. Escape after arrowing to a different option sends no PUT, and the chip is unchanged. |
| AC-64.5 | integration | `language-select` is a compact select in the open popup's header. It ANDs with the typed query and keeps the "All" option. | D-16; Human-approved "retain the functionality" (triage D-8) | Language `French` + query `am_` → zero options and the empty-state text. |
| AC-64.6 | integration | At `DEFAULT_WINDOW`, with the combobox closed and the seam serving `VOICE_CATALOG_FIXTURE`, the bottom edge of the bounding box of `speed-slider` and of `format-select` is ≤ `window.innerHeight`, with the page scroll containers at `scrollTop == 0`. The spec title contains `AC-64.6`. The spec's **first** `expect` calls are the two bounding-box assertions, made before any `voice-combobox` / `voice-selected-chip` interaction, so on the pre-change layout it fails on the geometry and not on a missing new element (Playwright stops at the first failed `expect`; Review R2-4). | Spec 11:124 | **Red on the pre-change layout:** `red64` runs `require_failed_title AC-64.6 toBeLessThanOrEqual`, so row 10 is not done unless the `AC-64.6` spec itself fails, on its bounding-box `expect`, against the unchanged layout. If it does not go Red with the production-size catalog, apply Stop condition S8. With the combobox **open**, Speed/Format need not be visible (the popup may overlay them). |

**Test-ID migration (MEU-64).**

| Existing ID | Migration | Detail |
|---|---|---|
| `preview-cleanup-btn` | change | secondary variant |
| `preview-cleaned` | change | conditional mount after Preview |
| `preview-raw` | removed | Spec 11:122/125; TA-1/TA-2 |
| `voice-grid` | change | popup listbox, mounted when open |
| `voice-card` | change | options inside the popup, grouped by language |
| `language-select` | change | compact select inside the popup header (D-16) |
| `speed-slider`, `format-select`, speed presets | keep | position rises; ids unchanged |
| new: `apply-cleanup-btn`, `voice-combobox`, `voice-selected-chip` | add | MEU-64 block in `test-ids.ts` |

#### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|---|---|---|
| Apply semantics | Human-approved | 11:121 |
| Preview collapse | Human-approved | 11:122; unmount on text edit is D-17's companion rule (a preview of stale text would mislead) |
| Combobox pattern and keyboard | Research-backed | WAI-ARIA APG combobox (listbox popup) |
| Language filter kept | Human-approved + Local Canon | triage D-8 "retain the functionality"; D-16 |
| Space | Spec | 11:124; `DEFAULT_WINDOW` |

#### Files Modified

| File | Action | Summary |
|---|---|---|
| `ui/src/renderer/src/features/tts/TTSPage.tsx` | modify | Cleanup block (`:340-398`), Voice picker (`:523-569`) |
| `ui/src/renderer/src/features/tts/VoiceCombobox.tsx` | new | combobox + popup listbox; reuses `filterVoices` / `uniqueLanguages` (`tts-voices.ts`) |
| `ui/src/renderer/src/features/tts/tts-voices.ts` | modify | query filter and grouping helpers |
| `ui/tests/e2e/test-ids.ts` | modify | MEU-64 block |
| `ui/tests/unit/tts-page.test.ts`, `ui/tests/unit/tts-page.behavior.test.ts`, `ui/tests/unit/voice-combobox.test.tsx` (new), `ui/tests/e2e/tts-generate.test.ts` (`installTtsSeam` gains an optional `voices` argument) | modify/new | AC-64.1–64.6, TA-1/2/5/6/7 |
| `ui/tests/e2e/fixtures/tts-voices.json` (new), `tests/unit/test_tts_voice_fixture.py` (new) | new | `VOICE_CATALOG_FIXTURE` and its parity test |

---

## Out of Scope

| Item | Kind | Deferred-to MEU | Basis |
|---|---|---|---|
| Packaged (PyInstaller) TTS: `packaging/avkit-backend.spec:35` excludes torch, and kokoro imports torch, so `KPipeline` is `None` in the frozen app (`adapter.py:15-22`, `:238-239`). There is also no hiddenimports entry for kokoro/misaki/spacy (`:14-24`). | out-of-scope | — | 03:422 limits MEU-62 to assets, readiness, fail-fast and logging. Packaging belongs to Phase 7 (`07-distribution.md:214-223` §Kokoro / models). Row 13 files known issue `TTS-PACKAGED-RUNTIME-EXCLUDED` so triage can schedule it. |
| Voice packs (`voices/<id>.pt`) fetched lazily from HF during generate (`adapter.py:183-185`) | out-of-scope | — | 03:414-421 lists exactly two managed assets (D-22). With AC-62.11, a fetch failure is no longer silent. Row 13 files `TTS-VOICE-PACK-LAZY-FETCH`. |
| Non-English G2P runtime pieces: `e/f/h/i/p` voices use `misaki.espeak.EspeakG2P` (needs espeak-ng), and `j`/`z` need the `misaki[ja]` / `[zh]` extras (kokoro `pipeline.py:114-134`) | out-of-scope | — | 03:414-421 lists exactly two managed assets (D-22). Row 13 files `TTS-NON-ENGLISH-G2P-DEPS`. |
| FFmpeg resolution divergence and an MP3 readiness hint | out-of-scope | — | 03:422: "ffmpeg divergence … is a separate issue, not this MEU". Still unfiled, pending the user (`current-focus.md`, Next steps 1). |
| Voice-select layout jump, model-flow gaps, Capture "Open file" | out-of-scope | — | Not in any MEU-62–64 row (grouping `:21-41` traceability table); `current-focus.md` lists them as "Still unfiled, pending the user". |
| Setup Readiness card (`readinessCount`, IPC `getSetupReadiness`) | out-of-scope | — | 03:418: the rows go on the Dependencies card, "without new IPC". |
| MCP live audit of the repaired `tts.generate` | deferred | MEU-68 | Grouping D-4: Session 28 follows this session so its baseline records a working generate. |

## BUILD_PLAN.md Audit

The D3 hub is `docs/BUILD_PLAN.md` + `docs/build-plan/`. Task row 13 makes these hub edits, with exact validation:

1. `03-service-layer.md` §TTS runtime assets (residual), `:416-422`, is amended to the decided contract:
   - D-8: the vocab is fetched with every variant.
   - D-9: one `VOCAB_LOCATION`, resolved per call; replaces "wiring passes `onnx_vocab_path`".
   - D-10: spaCy is triggered on the first load of **any** variant, and generation needs it per `REQUIRED_TTS_ASSETS` (English voices, or any voice with the `chunk` step).
   - D-12: assets go through `POST /models/download {asset}`.
   - D-13: `CONSOLE_FIELDS`.
   - D-14: row shape.
   - AC-62.11: the catch-all path.

   Each change is tagged with its D-id.
2. `11-page-layout.md`:
   - The §TTS model manager Test IDs row (`:111`) is corrected to the registry names (D-15).
   - The two §Residuals sections (TTS model manager, TTS text panel) gain one prose line each, pointing to this plan's §MEU-63 / §MEU-64 Test-ID migration tables.
   - The TT rows inside `<!-- BEGIN MOCKUP INVENTORY -->` … `<!-- END … -->` (`:156-318`) are **not** edited. They are the Phase 11 canon lock that `ui/tests/unit/layout-canon.test.ts` AC-50.4 (`:43-47,130-145`) parses: owner `^MEU-5[2-8]$`, label and disposition equal to mockup §05, and row count. Row 13 re-runs `layout-canon.test.ts` after the edit to prove it (Review R1 F2).
3. `07-distribution.md`:
   - Line 9 gains the spaCy wheel host.
   - §Kokoro / models (`:214-223`) gains one line saying that in the frozen app `KPipeline` is `None` because torch is excluded. That contradicts "ONNX variants load with bundled onnxruntime", and the line points to `TTS-PACKAGED-RUNTIME-EXCLUDED`.
4. `docs/BUILD_PLAN.md` AUTOGEN status regions are re-rendered by `tools/meu_status.py render` (H1-3 / H2-2) and checked with `render --check`.

## Verification Plan

Every command is registered in `validate-task.sh` (container) and `validate-task.ps1` (Windows), from one stage list. The stage ids match exactly (`windows-gate-check` asserts the order).

### 0. Plan-local static verifier (planning time; re-run in `pregate`)

`python3 docs/execution/plans/2026-09-30-tts-repair/plan_checks.py static` is stdlib-only, read-only and runs no product code (GUARDRAILS SIGN 1 carve-out). It checks five things:

- the task table's structure and its dependency graph;
- that every `validate-task.sh` check invoked from `task.md` exists;
- that the `.sh` `windows-gate-check` order equals the `.ps1` stage ids;
- that `AUDIT_SRC` and the audit pattern are identical in both scripts;
- that every `TA-n` and `D-n` in `task.md` is defined here.

Planning receipt, 2026-09-30:

- `PASS static: 24 task rows; scripts and plan cross-references agree` (exit 0).
- **Negative case**, run on mutated copies in the scratchpad:
  - A renamed `.ps1` stage plus a swapped audit file → `FAIL: stage order differs…` and `FAIL: AUDIT_SRC differs…` (exit 1).
  - A dangling dependency (`99`), a self-cycle and an unknown check label → three FAIL lines (exit 1).

### 1. Prerequisites and baseline (row 0)

`bash docs/execution/plans/2026-09-30-tts-repair/validate-task.sh prereq`, then `electron-setup` and `baseline`. `baseline` writes `baseline.sha` (HEAD before any product edit) and collects the baseline pytest failed-set, Vitest and Electron receipts.

### 2. Red (per MEU)

- `red62` has three parts:
  - A pytest Red via `pytest_red ac_62`. The rule is defined once, in `validate-task.sh` `pytest_red`:
    - at least one `ac_62` test must fail on an assertion;
    - an ImportError / ModuleNotFoundError is tolerated only when it names a not-yet-written MEU-62 symbol (`MEU62_SYMBOLS`), in any file;
    - every other failure or error rejects the Red.
  - An MCP Vitest Red (`AC-62.13`).
  - A Settings Vitest Red (`AC-62.15`).
- `red63` / `red64`: Vitest assertion Red, then an Electron Red after a fresh build (`electron_red`, the Session 26 helper).
- `AC-64.6`'s Red must come from the `AC-64.6` spec itself, failing on its bounding-box `expect` against the current layout (`require_failed_title`, Review R1 F1).

### 3. Targeted Green (after each production edit)

`green62` / `green63` / `green64`: the targeted suites plus the regression neighbours named in `validate-task.sh`.

### 4. Targeted MEU gates (rows 6, 9, 12)

`gate62`: pyright, ruff, targeted pytest, MCP typecheck/build/test, UI typecheck/lint, Settings Vitest, the OpenAPI two-step (below) and the Settings Electron spec. `gate63` / `gate64`: UI typecheck/lint/Vitest/build and `tts-generate.test.ts` under Electron, plus `--repeat-each=20` for every touched Electron spec into `$RECEIPTS_DIR/s27-repeat-*` (cloud-local §3.1 item 2).

### 5. OpenAPI drift (G8, rows 5 and H1-4)

```bash
uv run python tools/export_openapi.py --check openapi.committed.json > "$RECEIPTS_DIR/s27-openapi-check.txt" 2>&1; echo "exit=$?"
# only when the check reports drift caused by this MEU's schema changes:
uv run python tools/export_openapi.py -o openapi.committed.json > "$RECEIPTS_DIR/s27-openapi-regen.txt" 2>&1; echo "exit=$?"
```

Row 5 must show `--check` failing first (the intended schema change), then regenerating, then `--check` passing. `ROUTE_INDEX` stays 71 (`tests/e2e/test_api_openapi.py:111`; no new route).

### 6. Container pre-gate (H1-2, non-authoritative)

`validate-task.sh pregate` runs the D6 stages that can run here:

- input identity;
- `py-types`, `py-lint`, `ui-types`, `ui-lint`, `mcp-types`, `task-contract`;
- `pytest_env_ok`;
- `vitest_env_ok`;
- `ui-build`, `ui-harness-build`, `mcp-build`, `mcp-tests`, `openapi`, `state-render`;
- `electron_env_ok`;
- `tts-live-pre`: the container runs `tts_live_check.py` with real HF + GitHub downloads through the proxy (non-authoritative; HF and GitHub were both reachable at plan time, HTTP 200). Windows `TTS_LIVE` then confirms rather than discovers;
- `source-audit` over `AUDIT_SRC`.

### 7. `WINDOWS_GATE` + `TTS_LIVE` (H1-6, authoritative, local)

`validate-task.ps1 -Check windows-gate` runs the 17 D6 stages. The canonical order is the `order` list in `validate-task.sh` `windows-gate-check`; `plan_checks.py static` asserts that the `.ps1` `$stages` ids equal it.

It adds the preflight fields (cloud-local §5.2 schema bump → `s27-windows-gate.v1`).

`validate-task.ps1 -Check tts-live` runs `tts_live_check.py` against a throwaway models directory (`C:/Temp/av-kit/s27-live/models`) and a throwaway app-data directory, never Mat's `~/.avkit`. The steps (`TTS_LIVE_STEPS`) are defined once, in the `tts_live_check.py` module docstring and its `STEP_IDS` tuple; `plan_checks.py static` asserts that `validate-task.sh` uses the same ids. The generate step uses the GUI defaults (`PREPARE_DEFAULT_ON`, so `chunk` is on), so it exercises the path users run (Review R1 F3).

`validate-task.sh windows-gate-check` and `tts-live-check` validate both JSONs:

- schema, clean tree, stage order and exits, `COUNT_FLOORS`, flaky;
- code identity over `GATED_PATHS`.

### 8. Closeout (H1-5, H1-7, H2)

`validate_closeout_artifacts.py --ac-coverage-only` per handoff; `review-check`; reflection validator with `--decision-source` for the plan, handoffs, grouping and `known-issues.yaml`; `lint_task_contract.py`.

## GUI Element Compliance Check

The §4A reference files are not shipped: `docs/gui-element-reference.md`, `docs/gui-button-index.md`, `docs/gui-input-field-index.md`, `docs/gui-output-index.md` and `.agent/docs/gui-standards-enforcement.md` are absent. Recorded as `gui-refs-not-shipped` (create-plan §4A note). The applicable canon is used instead:

- `11-page-layout.md` §Test-ID migration (the tables above);
- `emerging-standards.md` G30 (native select), G32/G33 (tokens, no `transition-all`, no raw hex; enforced by `source-audit`) and E2 (written and wired E2E).

Every new interactive element has a registered test id and an Electron assertion (AC-63.6, AC-64.4–64.6, AC-62.15).

## Stop Conditions

| ID | Condition | Action |
|---|---|---|
| S1 | `prereq` refuses: a graph directory appeared, or a dependency MEU (16, 22, 56) is not `approved` | Stop. Re-run the context-tool gate with the human, or report. |
| S2 | `LOCAL_REPRO` contradicts a MEU-63/64 premise (for example, `error_message` already renders on the target) | MEU-62 continues. MEU-63/64 rows stop for a Decision Brief. |
| S3 | Census finds an expectation contradiction outside `TEST_AMENDMENTS` | Stop for the human with a Decision Brief. No test edit. |
| S4 | Red is not an assertion failure (collection or import error outside the declared new module) | Fix the test setup only, then re-prove Red. |
| S5 | `SPACY_MODEL_PIN` sha256 or URL no longer matches upstream during execution | Stop. This is a one-way-door re-pin decision for the human. |
| S6 | A gate failure that is not a product defect | Handle per cloud-local §3.5: a Decision Brief and an A-n row in `human-gate-decision.md`. No self-authorized test change. |
| S7 | Review cap (plan 3, execution 6), or the reviewer is unavailable | HARD STOP with TL;DR (create-plan §5d). |
| S8 | The `AC-64.6` spec does not go Red on the pre-change layout with `VOICE_CATALOG_FIXTURE` | Stop MEU-64. Record the measured bounding boxes and the `LOCAL_REPRO` R5 result, then present a Decision Brief (for example: the Space rule already holds at the default window, or the overflow needs a state the seam lacks). Never weaken the assertion. |

## Decision Log

Carried from the grouping (stage `grouping`, reflection carry-forward). Session 27's own are **D-1** (asset provisioning = managed downloads; `USER_EXPLICIT 2026-09-30 'D-22: follow you recommendation'`), **D-2** (original phases), **D-3** (one session, split flag) and **D-5** (tech-debt rows are not MEUs). The H2-1 reflection nevertheless carries **every** grouping §8 row, D-1 to D-7, with stage `grouping`, because `validate_closeout_artifacts.py:1387-1427` requires the whole §8 table when the grouping is a decision source (Review R2-1). Planning decisions:

```yaml
decision_log:
  - id: D-8
    stage: planning
    question: "Is config.json needed by the PyTorch variant too, or only ONNX?"
    resolution: autonomous
    class: two-way
    chosen: "Every variant requires VOCAB_LOCATION; the PyTorch load passes it as KModel(config=...)"
    source_tag: Research-backed
    precedents: ["packages/infrastructure/src/avkit_infra/tts/adapter.py:129 — KModel(model=...) passes no config", "docs/build-plan/03-service-layer.md:416 — vocab rule written for ONNX"]
    research: { engine: native, sources: ["kokoro 0.9.4 kokoro/model.py:43-48 (PyPI wheel, read 2026-09-30) — config None ⇒ hf_hub_download('config.json')"] }
    reasoning: "The same file is the PyTorch model's config; leaving it unset hides a network fetch in load. One asset row covers both. The alternative (ONNX only) keeps a silent HF dependency, which is the failure class this MEU removes."
  - id: D-9
    stage: planning
    question: "Where does the vocab live, and how does the adapter find it?"
    resolution: autonomous
    class: two-way
    chosen: "One file at tts.models_directory/config.json, resolved per call through resolve_vocab_path(settings) that wiring passes to KokoroAdapter"
    source_tag: Local Canon
    precedents: ["packages/infrastructure/src/avkit_infra/model_manager/manager.py:48-79 — weights under models_directory (root and onnx/)", "packages/core/src/avkit_core/services/settings.py:66-75 — models_directory is a runtime setting"]
    research: { engine: none, sources: [] }
    reasoning: "03:416 says 'into the variant's model directory' and 'wiring passes the resolved path'. A static path breaks when models_directory changes, and per-variant copies would need one readiness row per variant. A single shared file under a resolver keeps one row and one Get. Two-way."
  - id: D-10
    stage: planning
    question: "Which loads trigger the spaCy download, and which generations need spaCy?"
    resolution: autonomous
    class: two-way
    chosen: "Any variant's load triggers it (AC-62.7); generation requires it per REQUIRED_TTS_ASSETS — voices whose lang code is in SPACY_LANG_CODES, or any voice when enabled_steps include a SPACY_STEPS member (chunk, default-on)"
    source_tag: Research-backed
    precedents: ["packages/infrastructure/src/avkit_infra/tts/adapter.py:245-249 — ONNX path builds KPipeline(model=False)", "packages/core/src/avkit_core/services/prepare.py:150-161,250-251 — _chunk loads the spaCy model for every voice when chunk is enabled (default-on, :24)", "docs/build-plan/03-service-layer.md:417 — 'first PyTorch-variant load'"]
    research: { engine: native, sources: ["kokoro 0.9.4 pipeline.py:106-113 — lang 'a'/'b' build misaki en.G2P", "misaki 0.9.4 en.py:497-503 — G2P loads en_core_web_sm and calls spacy.cli.download when absent"] }
    reasoning: "The spec's PyTorch-only trigger comes from a triage that did not see the ONNX pipeline also runs English G2P. Keeping it would leave the default ONNX user without spaCy. Widening only the trigger (not the provisioning decision D-22) is two-way."
  - id: D-11
    stage: planning
    question: "How does a managed en_core_web_sm become importable without pip at runtime?"
    resolution: autonomous
    class: two-way
    chosen: "Verify the pinned wheel's sha256, extract it (zip-slip guarded, atomic os.replace) to SPACY_INSTALL_DIR, prepend that dir to sys.path at startup and after download"
    source_tag: Research-backed
    precedents: ["docs/build-plan/03-service-layer.md:417 — 'never pip at runtime outside that single pinned wheel'"]
    research: { engine: native, sources: ["https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl — downloaded 2026-09-30, sha256 1932429d…fb85, 35 members incl. .dist-info, METADATA spaCy >=3.8.0,<3.9.0", "misaki 0.9.4 en.py:500 — readiness = spacy.util.is_package, satisfied by .dist-info on sys.path"] }
    reasoning: "A wheel is a zip. Extracting it with its dist-info satisfies both spacy.util.is_package and spacy.load by name, which is what misaki calls. Running pip in-process would fail in a frozen app and violates 03:417. The checksum pin makes the one download reproducible."
  - id: D-12
    stage: planning
    question: "Which endpoint does 'Get' for an asset use, given 'No new REST route'?"
    resolution: autonomous
    class: two-way
    chosen: "POST /models/download accepts exactly one of a variant_id body or an asset body; the runtime reports asset; MCP gets a download_asset action on the same path"
    source_tag: Local Canon
    precedents: ["docs/build-plan/03-service-layer.md:422 — no new REST route", "docs/build-plan/03-service-layer.md:451 — MCP uses the same methods", "packages/core/src/avkit_core/services/models.py:86-108 — one download runtime and lock"]
    research: { engine: none, sources: [] }
    reasoning: "The existing route and single runtime already serialize downloads under one lock. A pseudo-variant in the catalog would put assets in the model picker, and a new route violates 03:422. Although it changes a request-body shape, this is two-way here: the API is localhost-only; both consumers (the Electron renderer and mcp-server) are in this repo and change in the same session; and the change is an additive superset — variant_id body bodies keep working byte-for-byte."
  - id: D-13
    stage: planning
    question: "How does the failure reason reach the Console, which shows only the event string?"
    resolution: autonomous
    class: two-way
    chosen: "CONSOLE_FIELDS (job_id, error) are appended to the console message and redacted; other events are unchanged"
    source_tag: Local Canon
    precedents: ["packages/core/src/avkit_core/services/health.py:108-144 — _process keeps only event", ".agent/context/known-issues.yaml TTS-GENERATE-FAILED-SILENT — 'nothing in the console'; triage D-3 log with job_id and error"]
    research: { engine: none, sources: [] }
    reasoning: "Logging the event alone would satisfy 03:420 in name while the Console still shows no reason. A two-key allowlist keeps every other console line byte-identical (test_ac_13_6), and redact_message still runs over the whole line."
  - id: D-14
    stage: planning
    question: "What is 'the same shape as existing dependency rows' when those rows have no state?"
    resolution: autonomous
    class: two-way
    chosen: "TtsAssetOut{available, version, state} — a superset of VersionAvailabilityOut"
    source_tag: Local Canon
    precedents: ["packages/api/src/avkit_api/schemas/health.py:18-35", "ui/src/renderer/src/features/settings/SettingsPage.tsx:66-69 — checkChip reads available"]
    research: { engine: none, sources: [] }
    reasoning: "Keeps the existing chip helper working unchanged and adds the three-state field the spec requires."
  - id: D-15
    stage: planning
    question: "Test ids for the single model action, and what becomes of model-manage-toggle?"
    resolution: autonomous
    class: two-way
    chosen: "One button whose data-testid follows MODEL_ACTION (model-get-btn / model-load-btn / unload-btn); model-manage-toggle becomes a 'Model details' disclosure"
    source_tag: Local Canon
    precedents: ["docs/build-plan/11-page-layout.md:152 — PRESERVED_TESTIDS; change never silently removes", "ui/tests/e2e/test-ids.ts:135-139,335 — registered values"]
    research: { engine: none, sources: [] }
    reasoning: "Keeps every registered string and the existing E2E click semantics (clicking model-get-btn still downloads). The spec's get-btn/load-btn at 11:111 are shorthand for the registered values."
  - id: D-16
    stage: planning
    question: "Where does language-select go once the combobox replaces the full-width select?"
    resolution: autonomous
    class: two-way
    chosen: "A compact select in the open popup's header, ANDed with the typed query"
    source_tag: Local Canon
    precedents: [".agent/context/known-issues.yaml TTS-LANGUAGE-VOICE-PICKER-SPACE D-8 — 'retain the functionality'", "docs/build-plan/11-page-layout.md:125 — language-select keep/move/change, not removed"]
    research: { engine: native, sources: ["https://www.w3.org/WAI/ARIA/apg/patterns/combobox/ — listbox popup may carry its own controls"] }
    reasoning: "It removes the full-width select from the resting layout (the space complaint), keeps the id and the language-only browse, and costs nothing when the popup is closed."
  - id: D-17
    stage: planning
    question: "Default model selection, and when the cleaned preview clears"
    resolution: autonomous
    class: two-way
    chosen: "Select the loaded variant, else the first downloaded, else the first. The cleaned preview unmounts on text edit or Apply."
    source_tag: Local Canon
    precedents: ["ui/src/renderer/src/features/tts/TTSPage.tsx:238 — loaded variant already derived", "docs/build-plan/11-page-layout.md:122 — preview collapses otherwise"]
    research: { engine: none, sources: [] }
    reasoning: "Shows the actionable state first. A preview of text that has since changed would misrepresent what Apply writes."
```

No planning question needs the human. The execution message may veto any autonomous row (User Review Required item 3).

### D-18 — MEU-63 scope after `LOCAL_REPRO` R2 did not reproduce the "Get buttons look alike" premise (Stop condition S2)

**Recommendation:** A — keep MEU-63 as scoped (picker plus one state-driven Get / Load / Unload button, readiness chips, and the run-bar error). The redesign rests on your explicit product decision, not on the Get-styling symptom. R2 confirmed the "Manage reads as plain text" half. MEU-62 will also make the ONNX variants on your machine read `downloaded: false` until `config.json` is fetched (AC-62.3), which brings back the enabled/disabled Get mix the target could not show today. **Reversibility:** two-way (a UI recomposition; `PRESERVED_TESTIDS` keeps every id). **Default if unanswered:** A. **Resolved:** A, `USER_EXPLICIT 2026-09-30 'proceed, D-18 A'` ([human-gate-decision.md](human-gate-decision.md) §Execution authorization).

**Precedents:**

- `.agent/context/known-issues.yaml` TTS-MODEL-MANAGE-AFFORDANCE D-1: `USER_EXPLICIT 2026-09-30 'this should be selection of a model after which Get Load or Unload button will appear depending on the state of the model'`.
- `docs/build-plan/11-page-layout.md:107-108` (Human-approved picker and one action).
- [walkthrough.md](walkthrough.md) §LOCAL_REPRO R2.

**Research:** none new. The triage D-2 sources (voicebox model-management states) still apply.

| Option | Source | Pros (vs. rec.) | Cons (vs. rec.) | Verdict |
|---|---|---|---|---|
| A. Keep MEU-63 as scoped (recommended) | triage D-1 (`USER_EXPLICIT`); 11:107-111 | — | — | ✅ |
| B. Narrow MEU-63 to the failure surface (AC-63.4/63.5), plus restyling the Manage toggle as a button | R2 result (walkthrough §LOCAL_REPRO) | Smaller diff; keeps the existing four-row grid that works on your machine | Contradicts your explicit picker decision. Leaves four Get + four Load buttons, which read as eight choices once ONNX variants show `downloaded: false` after MEU-62. 11:107-108 would need a spec amendment. | ⚠️ |
| C. Defer the picker to a later session; ship only MEU-62 and MEU-64 now | grouping D-3 split flag | Fastest path to working audio | Session 27 reopens `TTSPage.tsx` twice. No MEU-ID is scheduled for the deferral (a PR-7 violation, unless a new MEU is registered). | ❌ |

Answering in the execution message is enough. `task.md` row 7 does not start until D-18 is resolved (S2).

## Round 1 Review Corrections

Plan review Round 1 (`.agent/context/handoffs/2026-09-30-tts-repair-plan-critical-review.md`, Fable 5.1 subagent) returned `changes_required`: 3 High, 4 Medium, 3 Low. All ten findings were applied as document corrections; no code changed. The blast-radius census receipt, with a disposition per hit, is [review-r1-census.md](review-r1-census.md).

| Finding | Correction |
|---|---|
| F1 High (AC-64.6 vacuous oracle) | New `VOICE_CATALOG_FIXTURE` (54 production voices, parity-tested) is served to the AC-64.6 spec only. `red64` now requires the **`AC-64.6` spec itself** to fail on its bounding-box `expect` (`require_failed_title`). New Stop condition S8 applies if it cannot go Red. New `LOCAL_REPRO` item R5 gives target evidence. |
| F2 High (row 13 vs AC-50.4 lock) | The mockup-inventory TT rows are no longer edited. 11 gets only the `:111` registry-name fix plus prose pointers in the §Residuals sections. `hub` re-runs `layout-canon` / `queue-canon` / `gui-actions-audit`. |
| F3 High (`REQUIRED_TTS_ASSETS` misses `prepare._chunk`) | New `SPACY_STEPS`, and `REQUIRED_TTS_ASSETS(variant, voice, enabled_steps)` now covers it. AC-62.1 and AC-62.9 negatives are rewritten, with the `jf_*` + `chunk` → 409 case. The 409 (load/generate) vs 503 (`/tts/prepare`) split is stated once under `ASSET_MISSING_ERROR`. D-10 cites `prepare.py`. `tts_live_check.py` generates with `PREPARE_DEFAULT_ON`. |
| F4 Medium (census reach) | Census patterns now also cover `MODEL_DOWNLOAD_RUNTIME_FIELDS`, `ModelDownloadRuntime`, `DependencyHealth`, the service constructors, `ACTION_INDEX` and `toHaveLength(67)`. TA-9 names `test_domain.py:321/517-523/595-605` and `action-index.test.ts:38`. TA-5 keeps `renderPage()`'s start state and waits on `voice-selected-chip`. |
| F5 Medium (H2-1 cannot exit 0) | `known-issues.yaml` is removed from H2-1's `--decision-source`. Triage decisions are cited in prose. |
| F6 Medium (`GATED_PATHS` gap) | `GATED_PATHS` now adds `openapi.committed.json`, `docs/BUILD_PLAN.md`, `docs/build-plan`, `.agent/model-registry.local.yaml`, `.agent/context/meu-status.yaml` and `.agent/context/grouping`. `plan_checks.py` asserts that the plan and `.sh` lists are equal. |
| F7 Low (install into an existing dir) | `SPACY_INSTALL_EXISTING`: when already ready → 409 with no fetch; a stale directory is removed before `os.replace`. `activate_spacy_dir` is idempotent. Negatives are added to AC-62.6 and AC-62.14. |
| F8 Low (restated clusters) | The stage order is canonical in the `.sh`, and `TTS_LIVE_STEPS` in `tts_live_check.STEP_IDS` (imported by the `.sh`). `COUNT_FLOORS` and `GATED_PATHS` are machine-checked by `plan_checks.py`. `SPACY_MODEL` references `prepare.SPACY_MODEL`. The Red-tolerance rule points at `pytest_red`. |
| F9 Low (clerical) | The `test-ids.ts:135-139,335` ref is fixed. The floor now carries the first counted attempt's value forward (`.ps1`), with the wording aligned. D-12 records why it is two-way. |
| F10 Medium (`source-audit` hits `health.py:149`) | The audit term is now `console\.log\(` in both scripts. Receipt, 2026-09-30: the old pattern hit `health.py:149` (exit 0); the new pattern returns exit 1 over the existing `AUDIT_SRC`; and a sample call still matches. |
| Observations 1–5 | 1: new out-of-scope row + known issue `TTS-NON-ENGLISH-G2P-DEPS`. 2: 07 §Kokoro/models note. 3: `FIXTURE_REPAIRS` rule. 4: AC-62.7 "Downloading before `load` returns". 5: Boundary Inventory states the AC-9.12 `huggingface_hub` confinement. |

`plan_checks.py static` after corrections: `PASS static: 24 task rows; scripts and plan cross-references agree`. Its new checks have their own negative case: a mutated `gated` entry plus a lowered Vitest floor → two FAIL lines, exit 1.

## Round 2 Correction Notes (post-approval, non-blocking)

Round 2 returned `approved`: 0 High/Critical, 3 Medium, 5 Low, none blocking. The PR-6 census gate passed, and all ten Round 1 corrections were verified against live sources. The notes were folded in as document corrections before execution. Census: [review-r2-census.md](review-r2-census.md).

| Note | Correction |
|---|---|
| R2-1 Medium | H2-1's reflection carries every grouping §8 row, D-1 to D-7, because the validator requires the whole table (§Decision Log preamble; `task.md` H2-1). |
| R2-2 Medium | `SPACY_READY` = `is_package` ∧ `find_spec`, so the corrupt-install branch of `SPACY_INSTALL_EXISTING` is reachable. |
| R2-3 Medium | `GATED_PATHS` is narrowed to exactly the non-code files the stages read. It **supersedes Round 1 F6's widening**. The `meu-status.yaml` / `BUILD_PLAN.md` exclusion is stated as a rule, and `post-review-state` re-runs the doc-reading Vitest after the H2-2 SSOT edits. |
| R2-4 Low | AC-64.6's bounding-box `expect` calls come first in the spec. |
| R2-5 Low | `ModelDownloadRuntime.asset` is required; existing constructions pass `asset=None` explicitly. |
| R2-6 Low | `SPACY_MODEL` = the `prepare` constant; the enum member is always `TtsAsset.SPACY_MODEL`. |
| R2-7 Low | R5 is re-sent with the approved-plan message (task row 1). |
| R2-8 Low | `tts-live-pre` uses `STEP_IDS.index(...)`. |

**Post-approval author notes (2026-09-30, `LOCAL_REPRO` received).**

- The results are recorded in [walkthrough.md](walkthrough.md) §LOCAL_REPRO, with the screenshots in `local-evidence/`, and as verification blocks on the five issues in `known-issues.yaml`.
- R1 confirms the Round 1 F3 correction: the target's `error_message` is `prepare._chunk`'s `SpacyModelNotFoundError` text.
- R2 did not reproduce, so Stop condition S2 applies, and Decision Brief D-18 gates row 7.
- R5 (addendum, [screen 6](local-evidence/s27-repro-screen-6-r5.png)) reproduced at the default window: Speed and Format are fully below the fold. That confirms AC-64.6 can go Red, so S8 is not expected. The run bar is below the fold too, which is outside 11:124 and recorded as an observation.
- Running `repro-check` exposed a defect in this plan's own script, now fixed. It split on the first `## LOCAL_REPRO` text, which was a prose mention, instead of the heading line. It now anchors on the heading (`re.split(..., flags=re.M)`).
  - Positive: `PASS LOCAL_REPRO recorded for R1-R5`, exit 0.
  - Negative (R3 changed to `pending` in a scratch copy): `FAIL: R3 has no recorded result`, exit 1.
- No product file changed.

## Research References

- kokoro 0.9.4 and misaki 0.9.4 wheels (PyPI, `pip download --no-deps`, read 2026-09-30): `kokoro/model.py:31-50`, `kokoro/pipeline.py:22-36,106-135`, `misaki/en.py:497-503`.
- spaCy model wheel: `https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl` (sha256 above; METADATA spaCy `>=3.8.0,<3.9.0`).
- WAI-ARIA Authoring Practices, Combobox pattern: `https://www.w3.org/WAI/ARIA/apg/patterns/combobox/`.
- Triage research for the picker and combobox: `.agent/context/known-issues.yaml` (TTS-MODEL-MANAGE-AFFORDANCE D-2, TTS-LANGUAGE-VOICE-PICKER-SPACE D-9 sources).
- `.agent/docs/cloud-local-collaboration.md` §3–§5, §7, §9; Session 26 `validate-task.sh` / `.ps1` as templates (§10).

## Validation stage contract

The plan binds to PROFILE D6 (`.agent/docs/commands.md` §D6), in stages:

1. **Static:** py-types, py-lint, ui-types, ui-lint, mcp-types, task-contract.
2. **Targeted:** the per-MEU Red/Green/gate checks.
3. **Fresh full:** the container pre-gate first (non-authoritative), then `WINDOWS_GATE` (authoritative).
4. **Runtime:** `TTS_LIVE`.

For each stage, `validate-task.sh` / `.ps1` hold the argv, cwd (repo root), scope and blocking status (all blocking). Expected results are exit 0 (with the stated `rg` exception), and receipts go under `$RECEIPTS_DIR` / `C:/Temp/av-kit`.

**Input identity** is recorded independently at pre-gate and at each Windows attempt:

- HEAD, a hash of `git status --porcelain`, and both lockfile hashes;
- the Node and Electron versions;
- `P:/agentic-framework` HEAD and the `P:/.agent` registry hash (Windows).

**Reuse is disabled:**

- Any commit touching `GATED_PATHS` after the tested SHA reopens the gate (cloud-local §3.4).
- A cached, partial or container-only result never certifies the full gate.
