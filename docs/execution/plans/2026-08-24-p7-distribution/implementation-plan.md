---
project: "2026-08-24-p7-distribution"
date: "2026-08-24"
source: "docs/build-plan/07-distribution.md"
meus: ["MEU-24", "MEU-25"]
status: "approved"
template_version: "2.0"
---

# Implementation Plan: Phase 7 Distribution

> **Project**: `2026-08-24-p7-distribution`
> **Build Plan Section(s)**: [07-distribution.md](../../../build-plan/07-distribution.md) §Backend packaging + §Electron packaging + §FFmpeg + §MCP on a shipped machine
> **Status**: `draft`
> **Grouping**: [2026-08-18-build-plan-session-grouping.md](../../../../.agent/context/grouping/2026-08-18-build-plan-session-grouping.md) Session 12 — MEU-24 then MEU-25

---

## Goal

Ship the Windows distribution gate: a PyInstaller **onedir** `avkit-backend` that binds `127.0.0.1`, writes a secret-free `backend.json`, and prints `AVKIT_READY`; then an electron-builder **NSIS** installer whose `extraResources` carry that backend, bundled FFmpeg/ffprobe, and `mcp-server/dist`. Do not invent MEU IDs. Do not rewrite FastAPI routers or MCP tools. Do not rewind MEU-26 chrome or MEU-23 Settings/Help.

---

## Context Tool Decision

```yaml
context_tool_decision:
  phase: planning_and_execution
  eligible_tools: []
  decision: not_applicable
  eligibility_basis: "graphify-out/graph.json and graphify-out-research/graph.json are absent (Glob 0). Headroom has no approved disposition. Planning and execution use file reads + P0 exact-evidence receipts (bypass class)."
  human_message_reference: null
```

Re-evaluate before Step 6. If graphs remain absent and Headroom still has no approved disposition, reuse this record.

---

## Handoff Set

| Scope | Canonical handoff |
|---|---|
| MEU-24 | `.agent/context/handoffs/2026-08-24-p7-distribution-MEU-24-handoff.md` |
| MEU-25 | `.agent/context/handoffs/2026-08-24-p7-distribution-MEU-25-handoff.md` |

Rolling implementation review: `.agent/context/handoffs/2026-08-24-p7-distribution-implementation-critical-review.md`.

Product glob owner: `HANDOFF_GLOB`. Expected count: `HANDOFF_COUNT` = `2`.

---

## Work Packages and Context Lifecycle

`fresh_worker: none` → every non-`shared` row is `compact_continue`. Never emit `isolated`.

| ID | Work | depends_on | context_strategy | durable_outputs |
|---|---|---|---|---|
| WP-24a | MEU-24 Red: write `RED_AC_IDS_24` pytest (`RED_TEST_TITLE` + `RED_JSON_24`) and pass `RED_ORACLE_CHECK -Meu 24`. Do not add `SPEC_FILE` yet. | — | `compact_continue` | `C:/Temp/av-kit/fail-to-pass-meu-24-py.txt`; `RED_JSON_24`; compact then re-read `task.md` |
| WP-24b | Green: `SPEC_FILE` onedir + `HIDDEN_IMPORTS` + `EXCLUDE_GLOBS` + `PACK_SCRIPT`; smoke packaged exe with `SPAWN_FLAGS`. Do not rewrite routers. | WP-24a | `compact_continue` | `packaging/avkit-backend.spec`; `tools/package_backend.py`; compact then re-read `task.md` |
| WP-24c | `MEU_SCOPED_GATE` + MEU-24 handoff (`HANDOFF_MARKER_CHECK` + AC-24.*) | WP-24b | `compact_continue` | `HANDOFF_24` |
| WP-25a | MEU-25 Red: `RED_AC_IDS_25` + `RED_JSON_25` + `RED_ORACLE_CHECK -Meu 25`. Do not add electron-builder config yet. | WP-24c | `compact_continue` | `C:/Temp/av-kit/fail-to-pass-meu-25.txt`; `RED_JSON_25` |
| WP-25b | Green: `BUILD_CONFIG` NSIS + `EXTRA_RESOURCES` (`from: PACK_DIST_DIR`) + `BUNDLE_RESOLVER` + `BUNDLE_WIRE` + `MCP_SNIPPET` + `VITEST_MEU25`. Do not rewind chrome. | WP-25a | `compact_continue` | `ui/electron-builder.yml`; `tools/fetch_ffmpeg_windows.ps1`; `docs/distribution/mcp.json.example` |
| WP-25c | Run `NSIS_BUILD_CMD` then `NSIS_PACK_CHECK`. Missing artifact is FAIL. `[B]` only with external-error receipt + `NSIS_PACK_FOLLOWUP`. `CLEAN_VM` install is a separate later `[B]`. | WP-25b | `compact_continue` | `C:/Temp/av-kit/nsis-build.txt`; `C:/Temp/av-kit/nsis-size.txt` |
| WP-25d | MEU-25 gate + handoff; hub bind MEU-24/25; `HUB_NEXT_AFTER`. Grouping Session 12 ✅ is **H2 after exec `approved`**. | WP-25c | `shared` | `HANDOFF_25`; `.agent/context/meu-status.yaml`; `docs/BUILD_PLAN.md` |

---

## User Review Required

None that block planning. Sourced conflicts are locked below (reviewer confirms):

1. **Harness gate:** `.agent/context/harness.local.md` `plan_to_exec_gate: reviewer-auto` wins over Cursor default `human`. After Codex `approved`, auto-continue to execution.
2. **`resources/extra/` vs `ours.exe`:** Spec layout diagram nests payloads under `resources/extra/`, but the same file’s `ours.exe` line and Local Canon `packagedBackendPath()` use `{process.resourcesPath}/avkit-backend/avkit-backend.exe`. **Lock `RESOURCES_BACKEND` / `RESOURCES_FFMPEG` / `RESOURCES_MCP`** at the resources root (`to:` = those folder names). Diagram `extra/` is the extraResources *concept*, not a required path segment. Source: Spec 102 + 44–51; `ui/src/main/python-manager.ts` 56–58; [electron-builder extraResources](https://www.electron.build/docs/contents/).
3. **Onedir, not onefile:** official PyInstaller docs: onefile extracts `_MEIxxxxxx` every launch (startup tax). Spec already forbids onefile as default. **Lock `SPEC_ONEDIR`.** Source: https://pyinstaller.org/en/stable/operating-mode.html
4. **Local NSIS pack is attempted; clean-VM install is separate.** `NSIS_BUILD_CMD` must run. A missing `ui/dist/*.exe` after that command is FAIL (`NSIS_PACK_CHECK`), never PASS. `[B]` + `NSIS_PACK_FOLLOWUP` only when the build receipt shows an external/environment error. **`CLEAN_VM`** (install/launch on a clean Windows image) remains a separate `[B]` + CI escape and does not replace the local pack attempt.
5. **FFmpeg vendor:** Windows essentials build fetched by `FETCH_FFMPEG` with a pinned SHA256 (filled on first successful download during execution). Do not commit a floating “latest” URL without a hash.
6. **spaCy:** do **not** bundle `en_core_web_sm`. Chunk-prepare degrades (503-style dependency error) — do not fail splash. Spec 151–152.
7. **Copy MCP omit `AVKIT_API_BASE`:** already shipped in MEU-23. MEU-25 **proves** it and adds `MCP_SNIPPET`; does not rewrite `ipc.ts` unless a regression is found.
8. **4A:** no new renderer `<button>`/`<input>` in this project → skip GUI element indexes.

**This section is content for the review loop, NOT a cue to stop now.**

---

## Named sets (PR-9 — define once)

| Name | Value | Owner |
|------|-------|-------|
| `SPEC_FILE` | `packaging/avkit-backend.spec` | Spec 70–73; AC-24.1 |
| `SPEC_ONEDIR` | Analysis + COLLECT onedir named `avkit-backend`; no `EXE(..., onefile=True)` / `--onefile` | Spec 70–71; PyInstaller operating-mode |
| `HIDDEN_IMPORTS` | `yt_dlp`, `youtube_transcript_api`, `sqlalchemy`, `pydantic`, `uvicorn`, `avkit_api`, `avkit_core`, `avkit_infra`, `structlog` | Spec 141 |
| `EXCLUDE_GLOBS` | `**/.avkit/models/**`, `**/avkit.db`, `**/.env`, `**/*.onnx`, `**/*.pth`, `**/cuda/**`, `**/cudnn/**` | Spec 143–148, 266–267 |
| `ENTRY_SCRIPT` | `packages/api/src/avkit_api/__main__.py` → `cli.main` | Spec 73; Local Canon cli.py |
| `BIND_HOST` | `127.0.0.1` only | Spec 73; cli.py `BIND_HOST` |
| `SPAWN_FLAGS` | `--token`, `--mcp-token`, `--port 0`, `--app-data` | Spec 129–137 |
| `READY_LINE` | `AVKIT_READY port={n} instance={id}` with `n > 0` | Spec 73 |
| `DESCRIPTOR_KEYS` | `schema_version`, `pid`, `instance_id`, `executable_path`, `host`, `port`, `bind`, `api_base`, `app_data`, `started_at` | Spec 80–91 |
| `SECRET_KEYS` | `token`, `mcp_token`, `AVKIT_API_TOKEN`, `--token`, `--mcp-token` — must not appear as **keys** in `backend.json` | Spec 94 |
| `SECRET_SENTINELS` | two unique runtime values passed as `token=` and `mcp_token=` into `write_descriptor`; both must be absent from return JSON and file bytes | Spec 94; r1 F4 |
| `PACK_SCRIPT` | `tools/package_backend.py` invokes PyInstaller `-y --noconfirm` on `SPEC_FILE` | this plan |
| `NAMED_SETS_FILE` | `docs/execution/plans/2026-08-24-p7-distribution/named-sets.json` — executable owner of counts, handoff names, `HUB_NEXT_AFTER`, `PACK_DIST_*`, `SIZE_CAP_BYTES` | PR-9; r1 F6 |
| `PACK_DIST_DIR` | `packaging/dist/avkit-backend` (onedir folder: exe + `_internal` / support tree) | Spec 70–73; r1 F1 |
| `PACK_DIST_EXE` | `packaging/dist/avkit-backend/avkit-backend.exe` | Spec 44–45; r1 F1 |
| `RESOURCES_BACKEND` | `join(process.resourcesPath, 'avkit-backend', 'avkit-backend.exe')` | Spec 102; python-manager.ts |
| `RESOURCES_FFMPEG` | `join(process.resourcesPath, 'ffmpeg', 'ffmpeg.exe')` (+ sibling `ffprobe.exe`) | Spec 157; lock 2 |
| `RESOURCES_MCP` | `join(process.resourcesPath, 'mcp-server')` | Spec 220 |
| `BUILD_CONFIG` | `ui/electron-builder.yml` (or `ui/package.json` `build` key — one owner only: the yml) | Spec 173–181 |
| `NSIS_TARGET` | `win.target = nsis`, arch x64 | Spec 177, 245 |
| `EXTRA_RESOURCES` | FileSets `{from: PACK_DIST_DIR, to: avkit-backend}`, `{from: FFMPEG_VENDOR, to: ffmpeg}`, `{from: mcp-server/dist, to: mcp-server}`. `from` is the **directory**, never `PACK_DIST_EXE` alone. | Spec 178; r1 F1 |
| `FFMPEG_VENDOR` | `packaging/ffmpeg-win64/` containing `ffmpeg.exe` + `ffprobe.exe` | Spec 157 |
| `FETCH_FFMPEG` | `tools/fetch_ffmpeg_windows.ps1` — URL + SHA256 pin; writes `FFMPEG_VENDOR` | Research-backed |
| `BUNDLE_RESOLVER` | `bundled_ffmpeg()` in `wiring.py`: if `getattr(sys, "frozen", False)` then `Path(sys.executable).resolve().parent.parent / "ffmpeg" / "ffmpeg.exe"` else `None`. No env-var-only bridge. | Spec 159–163; r1 F3 |
| `BUNDLE_WIRE` | `cli.main` → `build_services` → `FFmpegAdapter(..., bundle_path=bundled_ffmpeg())` | Spec 159–163; adapter.py |
| `PROBE_ORDER` | setting file exists → `bundle_path` file exists → `PATH` | Spec 159–163 |
| `NSIS_KEEP_APPDATA` | `nsis.deleteAppDataOnUninstall` is `false` | Spec 258 |
| `MCP_SNIPPET` | `docs/distribution/mcp.json.example` — keys `AVKIT_API_TOKEN`, `AVKIT_APP_DATA` only | Spec 223–234 |
| `MCP_COPY_DEFAULT` | `copy-mcp-config` without pin omits `AVKIT_API_BASE` | Spec 230–234; ipc.ts |
| `SIZE_CAP` | NSIS `*.exe` under `ui/dist` `< SIZE_CAP_BYTES` (`524288000`) | Spec 33, 284 |
| `NSIS_BUILD_CMD` | in `ui/`: `npm run build`; then `npx electron-builder --win nsis --x64`. Receipt `C:/Temp/av-kit/nsis-build.txt`. | Spec 173–181; r1 F2 |
| `NSIS_PACK_CHECK` | `assert-nsis-pack.ps1 -BuildReceipt C:/Temp/av-kit/nsis-build.txt` — missing artifact is FAIL (never PASS) | r1 F2 |
| `NSIS_PACK_FOLLOWUP` | known-issue id `NSIS-SANDBOX-PACK` + CI `windows-latest electron-builder --win nsis --x64` | r1 F2 |
| `CLEAN_VM` | clean-Windows **install/launch** after a local artifact exists → `[B]` + CI if no VM; **not** a substitute for `NSIS_BUILD_CMD` | Spec 279–290 |
| `NO_TORCH_NSIS` | extraResources + spec excludes do not include torch/CUDA wheels or Kokoro weights | Spec 207–210 |
| `SPACY_DEGRADE` | do not collect `en_core_web_sm`; chunk prepare may 503 | Spec 151–152 |
| `RED_AC_IDS_24` | AC-24.1–AC-24.10 | this plan |
| `RED_AC_IDS_25` | AC-25.1–AC-25.10 | this plan |
| `RED_TEST_TITLE` | every AC-N test title contains exactly one `AC-24.N` or `AC-25.N` | FIC |
| `RED_JSON_24` | `C:/Temp/av-kit/fail-to-pass-meu-24-py.json` | pytest/json or enumerated receipt |
| `RED_JSON_25` | `C:/Temp/av-kit/fail-to-pass-meu-25.json` | this plan |
| `RED_ORACLE_CHECK` | `assert-red-oracle.ps1 -Kind py -Meu 24` or `-Meu 25` (prefix/count from `NAMED_SETS_FILE`) | PR-9; r1 F6 |
| `BUILDER_PIN` | `—` while `fresh_worker: none` | harness.local.md |
| `GROUPING_FILE` | `.agent/context/grouping/2026-08-18-build-plan-session-grouping.md` | grouping |
| `GROUPING_DONE_MARK` | Progress row `\| 12 \| \`p7-distribution\` \| ✅ complete \|` and Session 12 heading `✅ complete` | grouping Progress |
| `PLAN_FOLDER` | `docs/execution/plans/2026-08-24-p7-distribution` | MEU `execution_plan` |
| `PLAN_FOLDER_SLASH` | `docs/execution/plans/2026-08-24-p7-distribution/` | phase `"7"` |
| `HUB_NEXT_AFTER` | `NAMED_SETS_FILE` key `HUB_NEXT_AFTER` — SSOT commands load it; do not restate the string | grouping open decision #8 |
| `HUB_NEXT_FIELD` | unique `Next: \`...\`` in `docs/BUILD_PLAN.md` | hub |
| `EXEC_REVIEW_FILE` | `.agent/context/handoffs/2026-08-24-p7-distribution-implementation-critical-review.md` | this plan |
| `EXEC_REVIEW_TARGET` | `docs/execution/plans/2026-08-24-p7-distribution/implementation-plan.md` | exact `target_plan` |
| `EXEC_REVIEW_MAX_ROUND` | `6` | execution-review cap |
| `CHECK_EXEC_REVIEW` | `tools/check_exec_review.py` first YAML; `--expected-mode implementation` | p2 Human-approved |
| `HANDOFF_TEMPLATE` | `.agent/context/handoffs/TEMPLATE.md` | closeout |
| `HANDOFF_SOURCE_READ` | `C:/Temp/av-kit/handoff-source-read-meu-24.txt` then `…-meu-25.txt` written **before** each handoff | p4 F4 |
| `HANDOFF_BUNDLE_MARKERS` | `Acceptance Criteria`, `CACHE BOUNDARY`, `FAIL_TO_PASS`, `Changed Files`, `Quality Gate Results`, `Commands Executed`, `## Evidence` | TEMPLATE |
| `HANDOFF_COUNT` | integer in `NAMED_SETS_FILE` | `HANDOFF_GLOB` |
| `HANDOFF_GLOB` | filter + names in `NAMED_SETS_FILE` | this plan |
| `HANDOFF_24` | `.agent/context/handoffs/2026-08-24-p7-distribution-MEU-24-handoff.md` | this plan |
| `HANDOFF_25` | `.agent/context/handoffs/2026-08-24-p7-distribution-MEU-25-handoff.md` | this plan |
| `HANDOFF_MARKER_CHECK` | `rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-08-24-p7-distribution/assert-handoff-markers.ps1` | PR-9 |
| `REFLECTION_MARKERS` | `Friction Log`, `Execution Trace`, `Pattern Extraction`, `Patterns to KEEP`, `Next Session Design Rules`, `RULE-`, `Efficiency Metrics`, `Rule Adherence`, `Instruction Coverage`, `schema: v1`, `sections:`, `loaded:`, `decisive_rules:` | p6 |
| `MEU24_TOUCHED` | `SPEC_FILE`, `PACK_SCRIPT`, `tests/unit/test_packaging_backend.py` | MEU-24 |
| `MEU25_TOUCHED` | `BUILD_CONFIG`, `FETCH_FFMPEG`, `MCP_SNIPPET`, `wiring.py` `BUNDLE_RESOLVER`, `tests/unit/test_packaging_installer.py`, `tests/unit/test_ffmpeg_bundle_wire.py`, `ui/tests/unit/dev-spawn.test.ts`, `ui/tests/unit/copy-mcp-config.test.ts` | MEU-25 |
| `VITEST_MEU25` | in `ui/`: `npx vitest run` on `NAMED_SETS_FILE.VITEST_MEU25_FILES` `--allowOnly=false` | r1 F5 |
| `MEU_SCOPED_GATE_24` | `uv run pytest tests/unit/test_packaging_backend.py` + pyright/ruff on packaging/tools + `SCAN_PLACEHOLDER` + `SCAN_G36` | AGENTS MEU gate |
| `MEU_SCOPED_GATE_25` | pytest installer/wire tests + `VITEST_MEU25` + `npx tsc --noEmit` in `ui/` if TS touched + eslint if TS touched | AGENTS MEU gate |
| `OPENAPI_CHECK` | `packages/api/` routes **not** modified → `--check` no-drift. `-o` forbidden unless FAIL. | G8 |
| `CHROME_RULES` | RULE-1 `AVKIT_APP_DATA`; do not rewind chrome | chrome reflection |
| `SETTINGS_RULES` | RULE-1 queue toggle; RULE-2 no `require()` sqlite; RULE-3 Electron smoke after main extract | MEU-23 reflection |

---

## G29 wiring checklist

| Layer | Ready? | Evidence |
|-------|--------|----------|
| FastAPI CLI + descriptor + READY | YES | MEU-19 `cli.py` — do not rewrite routers |
| Electron spawn `SPAWN_FLAGS` + `RESOURCES_BACKEND` | YES | `python-manager.ts` |
| FFmpeg adapter `PROBE_ORDER` | YES adapter / NO bundle wire | adapter.py has `bundle_path`; `build_services` omits it → **MEU-25** |
| PyInstaller onedir | NO → **MEU-24** | grouping Session 12 |
| NSIS + extraResources | NO → **MEU-25** | grouping Session 12 |
| MCP tools | YES — do not rewrite | MEU-17/18 `approved` |

---

## create-plan §4A — GUI Element Compliance

**Not triggered.** This project does not create or migrate renderer `<button>`, `<input>`, `<select>`, or status controls. MCP copy/pin already exist (MEU-23). Docs-only `MCP_SNIPPET`.

---

## MEU-24 — `dist-backend`

### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy | Invalid-input | Create/Update parity | Source |
|---------|-------------|-------------------|--------------------|---------------|----------------------|--------|
| CLI argv | `parse_args` argparse | `SPAWN_FLAGS`; port ≥ 0; tokens non-blank | extra flags → argparse error (exit ≠ 0) | blank token / negative port | same parser packaged vs `python -m` | Spec 129–137; cli.py |
| `backend.json` | `write_descriptor` dict | `DESCRIPTOR_KEYS` only | extra keys not written | secrets in file → fail AC | overwrite atomic `os.replace` | Spec 75–94 |
| PyInstaller spec | `SPEC_FILE` text/AST | `SPEC_ONEDIR`; `HIDDEN_IMPORTS`; `EXCLUDE_GLOBS` | unknown collect dirs forbidden if they match excludes | `--onefile` present → fail | n/a | Spec 70–148 |

### Acceptance Criteria

| AC | Type | Description | Source | Negative Test |
|----|------|-------------|--------|---------------|
| AC-24.1 | unit | **Control `SPEC_ONEDIR`.** Observable: `SPEC_FILE` exists and contains COLLECT onedir name `avkit-backend`. Chain: `PACK_SCRIPT` → PyInstaller → `SPEC_FILE`. Negative: `--onefile` or `exe = EXE(..., exclude_binaries=False)` onefile form present → fail. | Spec 70–71; https://pyinstaller.org/en/stable/operating-mode.html | onefile default |
| AC-24.2 | unit | **Control `HIDDEN_IMPORTS`.** Observable: every name in the set appears in `hiddenimports` (or equivalent). Chain: `SPEC_FILE` Analysis. Negative: omit `yt_dlp` or `avkit_infra` → fail. | Spec 141 | missing hidden import |
| AC-24.3 | unit | **Control `EXCLUDE_GLOBS`.** Observable: spec/excludes reject models, `avkit.db`, `.env`, `*.onnx`, `*.pth`. Chain: `SPEC_FILE` + `PACK_SCRIPT` filter helper. Negative: datas include a path ending `avkit.db` → fail. | Spec 143–148 | leak db/weights |
| AC-24.4 | unit | **Control `BIND_HOST`.** Observable: packaged entry still uses `BIND_HOST == 127.0.0.1`; spec/runtime hook does not pass `0.0.0.0`. Chain: `cli.main` → uvicorn.Config. Negative: host `0.0.0.0` in spec or hook → fail. | Spec 73, 270 | bind all interfaces |
| AC-24.5 | unit | **Control `ENTRY_SCRIPT` + `SPAWN_FLAGS`.** Observable: spec script is `ENTRY_SCRIPT`; argv parser still requires all four flags. Chain: Analysis `scripts` → `parse_args`. Negative: drop `--mcp-token` from required set → fail. | Spec 129–137 | missing flag |
| AC-24.6 | unit | **Control `SECRET_SENTINELS` + `SECRET_KEYS`.** Observable: call `write_descriptor(..., token=<sentinel_a>, mcp_token=<sentinel_b>)`; neither sentinel appears in the returned dict serialization or exact `backend.json` bytes; none of `SECRET_KEYS` appear as keys. Chain: `cli.write_descriptor`. Negative: mutate payload so an allowed `DESCRIPTOR_KEYS` field equals `sentinel_a` → fail. | Spec 94 | secret value under allowed key |
| AC-24.7 | unit | **Control `DESCRIPTOR_KEYS` + atomic replace.** Observable: written JSON keys == the set; temp `.{pid}.tmp` then `os.replace`. Chain: `write_descriptor`. Negative: non-atomic truncate-in-place only → fail. | Spec 73, 80–91 | torn write |
| AC-24.8 | unit | **Control `READY_LINE`.** Observable: after bind, stdout matches prefix and port > 0. Chain: `cli.main` print. Negative: `port=0` in READY → fail. | Spec 73 | zero port |
| AC-24.9 | unit | **Control `NO_TORCH_NSIS` on the spec side.** Observable: spec does not collect `torch` / `cuda` / Kokoro weight dirs. Chain: `SPEC_FILE` excludes. Negative: `hiddenimports` contains `torch` → fail. | Spec 149, 207–210 | torch in backend |
| AC-24.10 | integration | **Control packaged smoke.** Observable: `PACK_SCRIPT` produces `PACK_DIST_DIR` containing `PACK_DIST_EXE` plus the onedir support tree; running `PACK_DIST_EXE` with `SPAWN_FLAGS` against a temp `app-data` writes a sentinel-free descriptor + `READY_LINE` then exits on test harness timeout/SIGTERM. Chain: `package_backend.py` → exe → `cli.main`. Negative: onefile-only `dist/avkit-backend.exe` without `PACK_DIST_DIR` support files → fail. If PyInstaller/binary build cannot run in the sandbox, mark **the run** `[B]` with receipt — spec + unit ACs still green. | Spec 70–73, 311–315 | missing onedir tree |

### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|----------|---------------|------------|
| onedir vs onefile | Spec + Research-backed | Spec 70–71; PyInstaller operating-mode (onefile extracts every launch) |
| Hidden imports list | Spec | Spec 141 — closed set |
| No secrets in descriptor | Spec + Local Canon | Spec 94; `cli.write_descriptor` already discards tokens |
| Live-identity orphan table | Spec + Local Canon | Already MEU-19; consume, do not rewind |
| spaCy model | Spec | Degrade; do not bundle |

### Files Modified

| File | Action | Summary |
|------|--------|---------|
| `packaging/avkit-backend.spec` | new | `SPEC_ONEDIR` + imports + excludes |
| `tools/package_backend.py` | new | invoke PyInstaller on `SPEC_FILE` |
| `tests/unit/test_packaging_backend.py` | new | AC-24.1–24.10 |
| `docs/execution/plans/2026-08-24-p7-distribution/assert-red-oracle.ps1` | new | oracle |
| `packages/api/src/avkit_api/cli.py` | modify only if smoke proves a packaged-entry bug | no route rewrite |

---

## MEU-25 — `dist-installer`

### Boundary Inventory

| Surface | Schema Owner | Field Constraints | Extra-Field Policy | Invalid-input | Create/Update parity | Source |
|---------|-------------|-------------------|--------------------|---------------|----------------------|--------|
| electron-builder yml | `BUILD_CONFIG` schema (documented keys) | `NSIS_TARGET`; `EXTRA_RESOURCES` `to` ∈ {avkit-backend, ffmpeg, mcp-server} | unknown extraResources `to` that ships weights → fail | `to: extra/avkit-backend` (breaks `ours.exe`) → fail | n/a | Spec 173–181; lock 2 |
| `FETCH_FFMPEG` | script args + SHA256 | writes only `ffmpeg.exe`/`ffprobe.exe` | extra files in vendor dir ignored by extraResources filter | hash mismatch → nonzero exit | replace vendor dir | Research-backed |
| `build_services` bundle | constructor `bundle_path: Path \| None` | file must exist to count | extra kwargs unchanged | missing bundle falls through to PATH | create-only wire | Spec 159–163 |
| MCP snippet file | JSON object | `MCP_SNIPPET` keys only | extra `AVKIT_API_BASE` forbidden in default example | pin belongs in docs note, not default file | n/a | Spec 223–234 |
| Uninstall | NSIS flag | `NSIS_KEEP_APPDATA` | n/a | `deleteAppDataOnUninstall: true` → fail | n/a | Spec 258 |

### Acceptance Criteria

| AC | Type | Description | Source | Negative Test |
|----|------|-------------|--------|---------------|
| AC-25.1 | unit | **Control `NSIS_TARGET`.** Observable: `BUILD_CONFIG` win target is nsis x64. Chain: electron-builder load. Negative: only portable/squirrel target → fail. | Spec 177, 245 | non-NSIS ship target |
| AC-25.2 | unit | **Control `EXTRA_RESOURCES` from+to.** Observable: three FileSets `to` exactly `avkit-backend`, `ffmpeg`, `mcp-server` and backend `from` equals `PACK_DIST_DIR` (the onedir folder, so the installed `RESOURCES_BACKEND` sits beside `_internal`/support files). Chain: `BUILD_CONFIG` → electron-builder extraResources → `process.resourcesPath`. Negative: `from: PACK_DIST_EXE` (exe only) or `to: extra/avkit-backend` → fail. | Spec 102, 178; https://www.electron.build/docs/contents/ | exe-only copy |
| AC-25.3 | unit | **Control `RESOURCES_BACKEND` parity (Vitest).** Observable: `packagedBackendPath(resourcesPath)` equals `join(resourcesPath,'avkit-backend','avkit-backend.exe')`. Chain: `boot` → `packagedBackendPath` → `spawnOwned`. Scheduled in `VITEST_MEU25` (`dev-spawn.test.ts`). Negative: implementation resolves under `extra/` → fail. | Spec 102; Local Canon | extra/ prefix |
| AC-25.4 | unit | **Control `BUNDLE_RESOLVER` + `BUNDLE_WIRE`.** Observable: when `sys.frozen` is true and `sys.executable` is `{resources}/avkit-backend/avkit-backend.exe`, `bundled_ffmpeg()` returns `{resources}/ffmpeg/ffmpeg.exe` and `build_services` passes that path as `bundle_path`. Chain: `cli.main` → `build_services` → `bundled_ffmpeg()` → `FFmpegAdapter`. Negative: `sys.frozen` true but resolver returns `None` or an env-only path that ignores the sibling `ffmpeg/` layout → fail. Do not select `AVKIT_FFMPEG_BUNDLE` as the production bridge. | Spec 159–163 | frozen sibling miss |
| AC-25.5 | unit | **Control `PROBE_ORDER`.** Observable: existing file setting wins; else `bundle_path` file; else PATH; none → `FFmpegNotFoundError`. Chain: `FFmpegAdapter._resolve_ffmpeg`. Negative: a PATH decoy `ffmpeg` is used when the bundled file exists → fail. | Spec 159–163 | PATH decoy wins |
| AC-25.6 | unit | **Control `NSIS_KEEP_APPDATA`.** Observable: `deleteAppDataOnUninstall` is false. Chain: `BUILD_CONFIG` nsis. Negative: true → fail. | Spec 258 | wipe queue on uninstall |
| AC-25.7 | unit | **Control `MCP_SNIPPET`.** Observable: example JSON has `AVKIT_API_TOKEN` + `AVKIT_APP_DATA` only. Chain: repo doc path. Negative: default includes `AVKIT_API_BASE` → fail. | Spec 223–234 | stale pin in default |
| AC-25.8 | unit | **Control `MCP_COPY_DEFAULT` (Vitest).** Observable: existing `copy-mcp-config.test.ts` — `handleIpc('copy-mcp-config', { pinEndpoint: false })` clipboard JSON omits `AVKIT_API_BASE`. Chain: renderer IPC → `handleIpc` → clipboard. Scheduled in `VITEST_MEU25`. Negative: default copy includes `AVKIT_API_BASE` → fail. Do not rewrite `ipc.ts` unless this test regresses. | Spec 230–234 | pin-by-default |
| AC-25.9 | unit | **Control `NO_TORCH_NSIS` + `EXCLUDE_GLOBS` on installer.** Observable: extraResources filters do not include `*.onnx`, `*.pth`, torch/cuda dirs. Chain: `BUILD_CONFIG`. Negative: from `~/.avkit/models` → fail. | Spec 207–210, 266 | weights in NSIS |
| AC-25.10 | integration | **Control `NSIS_BUILD_CMD` + `SIZE_CAP`.** Observable: `NSIS_BUILD_CMD` runs (receipt required); on success `NSIS_PACK_CHECK` proves `ui/dist/*.exe` `< SIZE_CAP_BYTES`. Chain: `ui` build → electron-builder → `ui/dist`. Negative: missing artifact after the command, or size ≥ cap → fail (never PASS). `[B]` + `NSIS_PACK_FOLLOWUP` only when the build receipt shows an external/environment error. `CLEAN_VM` install/launch is a separate `[B]` after an artifact exists. | Spec 33, 284–290 | missing artifact PASS |

### Spec Sufficiency Table

| Behavior | Classification | Resolution |
|----------|---------------|------------|
| extraResources destination | Spec + Research-backed + Local Canon | ours.exe + electron-builder `to` relative to `resources/` |
| FFmpeg probe order | Spec + Local Canon | adapter already implements; wire `bundle_path` |
| Default MCP env | Spec | omit `AVKIT_API_BASE` |
| Uninstall data | Spec | do not auto-delete `{app_data}` |
| Auto-update / signing | Spec | optional; not a ship gate |
| FFmpeg Windows build source | Research-backed | pinned SHA256 fetch script (Gyan/BtbN essentials) filled at Green |

### Files Modified

| File | Action | Summary |
|------|--------|---------|
| `ui/electron-builder.yml` | new | NSIS + `EXTRA_RESOURCES` |
| `ui/package.json` | modify | `electron-builder` dep + `dist` script only |
| `tools/fetch_ffmpeg_windows.ps1` | new | pinned vendor fetch |
| `packages/api/src/avkit_api/wiring.py` | modify | `BUNDLE_RESOLVER` + `BUNDLE_WIRE` |
| `ui/tests/unit/dev-spawn.test.ts` | modify | `RESOURCES_BACKEND` + `extra/` negative (AC-25.3) |
| `ui/tests/unit/copy-mcp-config.test.ts` | prove | existing AC-25.8; edit only on regression |
| `docs/distribution/mcp.json.example` | new | `MCP_SNIPPET` |
| `tests/unit/test_packaging_installer.py` | new | AC-25.1–25.10 |
| `tests/unit/test_ffmpeg_bundle_wire.py` | new | probe + wiring |

---

## Out of Scope

| Item | Kind | Deferred-to MEU | Basis |
|------|------|-----------------|-------|
| macOS / Linux ship gate | out-of-scope | — | `07-distribution.md` lines 243–250: Windows is the Phase 7 gate; others secondary |
| electron-updater / code signing as exit | out-of-scope | — | Spec 180–181, 273: optional; not a domain change |
| Kokoro weights / CUDA / torch in installer | out-of-scope | — | Spec 25–32, 266–267 forbid bundling |
| FastAPI route / OpenAPI rewrite | out-of-scope | — | grouping Session 12 + MEU-16 `approved` |
| MCP tool rewrite | out-of-scope | — | grouping; MEU-17/18 `approved` |
| Rewind MEU-26 chrome / MEU-23 Settings | out-of-scope | — | grouping Session 12 notes; MEU-23 reflection RULE-3 |
| SSE, OCR Part 1, multi-file TTS, MCP Guard, ConversionJob GUI | out-of-scope | — | grouping “Named deferrals are not MEUs”; Spec 238 |
| Session 8c `p6-gui-console-polish` | out-of-scope | — | grouping Progress row 8c (Human-approved insert; not in `07-distribution.md`); not MEU-24/25 |
| Live YouTube download on clean VM | out-of-scope | — | Spec 290: optional dedicated job, not the install smoke |

---

## BUILD_PLAN.md Audit

This project **does** bind phase `"7"` `execution_plans` to `PLAN_FOLDER_SLASH` and rewrites `HUB_NEXT_FIELD` to `HUB_NEXT_AFTER`. Do not hand-edit AUTOGEN tables.

```powershell
rtk proxy uv run python -c "from pathlib import Path; import json, re, sys; from tools.meu_status.model import load, get_meu; PLAN='docs/execution/plans/2026-08-24-p7-distribution'; SLASH=PLAN+'/'; NEXT=json.loads(Path(PLAN+'/named-sets.json').read_text(encoding='utf-8'))['HUB_NEXT_AFTER']; MEUS=('MEU-24','MEU-25'); data=load(); p7=next(p for p in data['phases'] if str(p['id'])=='7'); eps=list(p7.get('execution_plans') or []); SLASH not in eps and sys.exit('phase 7 missing PLAN_FOLDER_SLASH'); miss=next((k for k in MEUS if get_meu(data,k) is None), None); miss is not None and sys.exit('missing '+miss); wrong=next((k for k in MEUS if get_meu(data,k).get('execution_plan')!=PLAN), None); wrong is not None and sys.exit(wrong+' execution_plan='+str(get_meu(data,wrong).get('execution_plan'))); hub=Path('docs/BUILD_PLAN.md').read_text(encoding='utf-8'); hits=re.findall('Next:\\s+'+chr(96)+'([^'+chr(96)+']+)'+chr(96), hub); len(hits)!=1 and sys.exit('hub Next field count='+str(len(hits))); hits[0]!=NEXT and sys.exit('hub Next='+hits[0]); print('PASS: SSOT_PLAN_BOUND')" *> C:/Temp/av-kit/ssot-plan-bound.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/ssot-plan-bound.txt; exit $code
```

---

## Verification Plan

### 1. MEU-24 Red oracle
```powershell
rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-08-24-p7-distribution/assert-red-oracle.ps1 -Kind py -Meu 24 -Receipt C:/Temp/av-kit/fail-to-pass-meu-24-py.txt *> C:/Temp/av-kit/red-oracle-24.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/red-oracle-24.txt; exit $code
```

### 2. MEU-24 / MEU-25 targeted pytest + `VITEST_MEU25`
```powershell
rtk proxy uv run pytest tests/unit/test_packaging_backend.py tests/unit/test_packaging_installer.py tests/unit/test_ffmpeg_bundle_wire.py -x --tb=short -v *> C:/Temp/av-kit/pytest-p7-packaging.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/pytest-p7-packaging.txt | Select-Object -Last 40; exit $code
```

```powershell
rtk proxy pwsh -NoProfile -Command { Push-Location ui; npx vitest run tests/unit/dev-spawn.test.ts tests/unit/copy-mcp-config.test.ts --allowOnly=false; exit $LASTEXITCODE } *> C:/Temp/av-kit/vitest-meu-25.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/vitest-meu-25.txt | Select-Object -Last 40; exit $code
```

### 2b. NSIS pack (after `NSIS_BUILD_CMD` receipt)
```powershell
rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-08-24-p7-distribution/assert-nsis-pack.ps1 -BuildReceipt C:/Temp/av-kit/nsis-build.txt *> C:/Temp/av-kit/nsis-size-run.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/nsis-size-run.txt; exit $code
```

### 3. OpenAPI no-drift
```powershell
rtk proxy uv run python tools/export_openapi.py --check openapi.committed.json *> C:/Temp/av-kit/openapi-check.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/openapi-check.txt; exit $code
```

### 4. Exec review
```powershell
rtk proxy uv run python tools/check_exec_review.py --review-file .agent/context/handoffs/2026-08-24-p7-distribution-implementation-critical-review.md --expected-mode implementation --expected-target docs/execution/plans/2026-08-24-p7-distribution/implementation-plan.md --max-round 6 *> C:/Temp/av-kit/exec-review.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/exec-review.txt; exit $code
```

---

## Open Questions

Resolved in-plan (not human-gated):

| Question | Option | Source | Pros | Cons | Recommendation |
|----------|--------|--------|------|------|----------------|
| extraResources path `extra/` vs resources root | A: `to: avkit-backend` | Spec 102; python-manager; electron-builder docs | Matches `ours.exe` + existing spawn | Diagram shows `extra/` | ✅ |
| | B: `to: extra/avkit-backend` | Spec diagram 44–51 | Matches ASCII tree | Breaks live-identity `ours.exe` | ❌ |
| onedir vs onefile | A: onedir | Spec 70; PyInstaller operating-mode | No per-launch extract; <3s budget | Folder, not single exe | ✅ |
| | B: onefile | PyInstaller usage `--onefile` | Single file | Extracts `_MEI*` every start | ❌ |
| Clean-VM **install** as blocking | A: `[B]` + CI if no VM **after** local `NSIS_BUILD_CMD` | Spec 279; E2E-SANDBOX policy | Unblocks sandbox | Ship checklist waits on CI | ✅ |
| | B: HARD STOP until VM | none | Stronger ship proof | Invents a human gate the spec does not | ❌ |
| FFmpeg installed-layout bridge | A: frozen sibling `BUNDLE_RESOLVER` | Spec 159–163; `cli.main` already calls `build_services` | No Electron env dependency | Requires `sys.frozen` in packaged exe | ✅ |
| | B: Electron sets `AVKIT_FFMPEG_BUNDLE` | `index.ts` spawnOwned env | Explicit | Dead if spawn forgets the var (r1 F3) | ❌ |

---

## Explicit Stop Conditions

| Condition | Action |
|-----------|--------|
| Plan-review round cap (3) without `approved` | HARD STOP; present TL;DR; wait for `USER_EXPLICIT` |
| Exec-review round cap (6) without `approved` | HARD STOP; present TL;DR; wait for `USER_EXPLICIT` |
| All reviewer rungs unavailable | HARD STOP; never self-review |
| Commit / merge / deploy | wait for `USER_EXPLICIT` |
| `NSIS_BUILD_CMD` fails with an external/environment error | `[B]` `NSIS_PACK_FOLLOWUP` + CI — **not** a HARD STOP; config + Vitest oracles still block |
| Missing clean-Windows VM for **install/launch** after an artifact exists | `[B]` `CLEAN_VM` + CI — **not** a HARD STOP and **not** a substitute for `NSIS_BUILD_CMD` |
| Urge to start Session 8c or invent a MEU-ID | refuse; stay on MEU-24 then MEU-25 |

---

## Research References

- https://pyinstaller.org/en/stable/operating-mode.html — onefile extracts every launch
- https://www.electron.build/docs/contents/ — `extraResources.to` is relative to `resources/`
- [07-distribution.md](../../../build-plan/07-distribution.md)
- [APPLICATION_PURPOSE.md §6](../../../_inspiration/APPLICATION_PURPOSE.md) — <500MB, <3s UI
- MEU-23 reflection RULE-1/2/3 (carry-forward if Electron main is extracted)
