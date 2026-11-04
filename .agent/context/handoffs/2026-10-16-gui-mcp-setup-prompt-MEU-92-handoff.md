---
date: "2026-10-17"
project: "gui-mcp-setup-prompt"
meu: "MEU-92"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.2"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/implementation-plan.md"
build_plan_section: "bp07"
agent: "claude-code-local (Claude Opus 5.5)"
reviewer: "Codex via local dispatch"
predecessor: ".agent/context/handoffs/2026-10-16-gui-mcp-setup-prompt-MEU-71-handoff.md"
---

# Handoff: 2026-10-16-gui-mcp-setup-prompt-MEU-92-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-92 — `dist-mcp-server-bundle`. The packaged app ships a self-contained MCP server, so the entry the setup prompt names (`resources/mcp-server/index.mjs`) starts from a built tree.
**Build Plan Section**: [07 §mcp-server-bundle-residual](../../../docs/build-plan/07-distribution.md#mcp-server-bundle-residual).
**Predecessor**: [MEU-71 handoff](2026-10-16-gui-mcp-setup-prompt-MEU-71-handoff.md) (`SERVER_ENTRY` already names `index.mjs` for the packaged path).

Before this MEU, the packaged app copied `mcp-server/dist` (tsc output) to `resources/mcp-server`, and it had no `node_modules`, so every packaged launch failed with `ERR_MODULE_NOT_FOUND` (`MCP-PACKAGED-ENTRY-UNREACHABLE`, Session 32).

- **Bundle (`BUNDLE_SCRIPT`).** `npm --prefix mcp-server run bundle` runs `mcp-server/scripts/bundle.ts` (tsx). esbuild 0.28.2 (exact pin) writes `mcp-server/bundle/index.mjs`: ESM, platform node, target node22, every dependency inlined, with a `createRequire` banner so CommonJS dependencies get a `require`.
- **Licences (`BUNDLE_LICENSES`).** `mcp-server/scripts/bundle-licenses.ts` `collectLicenses` reads the build's metafile and writes `bundle/LICENSES.txt`: one section per inlined `node_modules` package, sorted, with name, version, licence id and licence text. A package with no licence file fails the build.
- **Packaging (`PACKAGING_INPUTS`).** `ui/electron-builder.yml` copies `../mcp-server/bundle` (not `dist`) to `resources/mcp-server`; `ui/package.json` `dist:prep` ends with the bundle; `.gitignore` ignores `mcp-server/bundle/`.
- **Proof (`PKG_PROBE`, AC-92.4).** A fresh `electron-builder --win dir` build holds the byte-equal bundle and `LICENSES.txt`, and `av-kit.exe` with `ELECTRON_RUN_AS_NODE=1` starts both the in-place entry and a hermetic copy outside the repository.

**Plan:** [implementation-plan.md](../../../docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/implementation-plan.md) §MEU-92. **Grouping:** D-56 (Mat accepted MEU-92 into Session 31b; recorded at row 0). **Execution authorization:** `USER_EXPLICIT` 2026-10-17 "proceed" ([walkthrough.md](../../../docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/walkthrough.md) §Execution authorization).

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-92.1 | integration (process) | `mcp-server/bundle/index.mjs` exists after `bundle`; a copy of `bundle/` in a temp directory with no `node_modules` above it, run as `node <copy>/index.mjs`, answers `initialize` with `serverInfo.name` `av-kit` | `MCP-PACKAGED-ENTRY-UNREACHABLE`; D-83 | `mcp-server/tests/bundle.test.ts` `AC-92.1 …` | ✅ |
| AC-92.2 | unit | `collectLicenses` returns one sorted section per fixture `node_modules` package with name, version, licence id and text, scoped names included; a package without a licence file throws `no licence file for <name>`; the real `bundle/LICENSES.txt` names every package in the real build's metafile | D-85 | `mcp-server/tests/bundle-licenses.test.ts` `AC-92.2 …` (3) | ✅ |
| AC-92.3 | unit | `PACKAGING_INPUTS` and `BUNDLE_SCRIPT`: the yml copies `../mcp-server/bundle` to `mcp-server` and no longer names `dist`; `dist:prep` ends with the bundle; `.gitignore` has `mcp-server/bundle/`; the `bundle` script and `esbuild` exactly `0.28.2` | 07 `:253`; D-83 | `mcp-server/tests/bundle.test.ts` `AC-92.3 …` (4) | ✅ |
| AC-92.4 | runtime (packaged) | `PKG_PROBE`: a fresh `win-unpacked` build holds the byte-equal bundle and `LICENSES.txt`; `av-kit.exe` with `ELECTRON_RUN_AS_NODE` starts the in-place entry and the hermetic copy, each answering `initialize` as `av-kit` | p7 RULE-1; grouping D-56; D-84 | `validate-task.ps1 -Check pkg-probe` → `pkg-probe-result.json` | ✅ |
| AC-23 (cross-ref) | — | Owned by the MEU-71 handoff (TA-2 amends AC-23.19 and AC-23.20); MEU-92 changes no GUI action | plan `TEST_AMENDMENTS` | [MEU-71 handoff](2026-10-16-gui-mcp-setup-prompt-MEU-71-handoff.md) | see MEU-71 |
| AC-41 (cross-ref) | — | Owned by the MEU-71 handoff (amendment A-1, AC-41.3) | D-89, D-91 | [MEU-71 handoff](2026-10-16-gui-mcp-setup-prompt-MEU-71-handoff.md) | see MEU-71 |
| AC-71 (cross-ref) | regression | The MEU-71 unit set re-runs in `gate92`, because `SERVER_ENTRY` names the bundle's `index.mjs` | plan `gate92` | `ui/tests/unit/` MEU-71 set (`$ui71`) | ✅ |

<!-- CACHE BOUNDARY -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|--------------------------|--------------|-----------|
| AC-92.1 | `npm --prefix mcp-server run bundle: expected false to be true` (existence assertion; `red92` deleted `mcp-server/bundle` first) | pass | `mcp-server/tests/bundle.test.ts` `AC-92.1 …` |
| AC-92.2 | load failure: `Cannot find module '../scripts/bundle-licenses.js'` (the declared new-module file) | pass | `mcp-server/tests/bundle-licenses.test.ts` |
| AC-92.3 | 4 assertion failures, one per pin: the yml pair, `dist:prep` `npm run clean:out && npm run build && npm run build:picker`, no `mcp-server/bundle/` line, `scripts.bundle` `undefined` | pass | `mcp-server/tests/bundle.test.ts` `AC-92.3 …` |
| AC-92.4 | Session 32's recorded `ERR_MODULE_NOT_FOUND` (`known-issues.yaml` `MCP-PACKAGED-ENTRY-UNREACHABLE`); runtime only, outside the Vitest Red | `PASS pkg-probe` | `pkg-probe-result.json` |

Every receipt and its decisive lines are in [walkthrough.md](../../../docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/walkthrough.md) (§Red (row 6), §Green (row 7), §Packaged probe (row 8), §MEU-92 gate (row 9)).

### Commands Executed

```json
{"schema_version":"evidence.v1","check_id":"s31b-92-red","command":"rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/validate-task.ps1 -Check red92 *> C:/Temp/av-kit/s31b-run-red92.txt (task.md row 6, verbatim)","cwd":"P:/av-kit-wt/s31b-gui-mcp-setup-prompt","scope":"MEU-92 Red: delete mcp-server/bundle, mcp-server Vitest on bundle.test.ts and bundle-licenses.test.ts, vitest-red classification","phase":"red","exit_code":0,"result":"pass","tested_state":"HEAD 6097cf5 plus row 0a, the whole MEU-71 change and the row 6 tests","output":"mcp-server Vitest 2 files, 5 failed | PASS MEU-92 Vitest RED: 5 assertion failures, 0 missing-symbol, load-tolerated files ['bundle-licenses.test.ts'], TA pins failing [] | PASS red92","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s31b-92-green-run1","command":"rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/validate-task.ps1 -Check green92 *> C:/Temp/av-kit/s31b-run-green92.txt (task.md row 7, verbatim; receipt kept as s31b-run-green92-run1.txt)","cwd":"P:/av-kit-wt/s31b-gui-mcp-setup-prompt","scope":"MEU-92 Green run 1: mcp-types, mcp-bundle, mcp-server Vitest on the MEU-92 set","phase":"green","exit_code":1,"result":"fail","tested_state":"HEAD 6097cf5 plus row 0a, MEU-71 and the row 7 change before the AC-92.1 cleanup repair","output":"PASS mcp-types | PASS mcp-bundle | 1 failed, 7 passed | AC-92.1: every assertion passed, then the finally block's rmSync failed with EPERM while the killed child still held the temp directory as its cwd | FAIL: green92-mcp-vitest","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s31b-92-green","command":"rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/validate-task.ps1 -Check green92 *> C:/Temp/av-kit/s31b-run-green92.txt (task.md row 7, verbatim)","cwd":"P:/av-kit-wt/s31b-gui-mcp-setup-prompt","scope":"MEU-92 Green run 2: mcp-types, mcp-bundle, mcp-server Vitest on the MEU-92 set","phase":"green","exit_code":0,"result":"pass","tested_state":"HEAD 6097cf5 plus row 0a, MEU-71 and the row 7 change","output":"PASS mcp-types | PASS mcp-bundle | PASS green92-mcp-vitest: 8 passed of 8 | PASS green92","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s31b-92-pkg-probe-run1","command":"rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/validate-task.ps1 -Check pkg-probe *> C:/Temp/av-kit/s31b-run-pkg-probe.txt (task.md row 8, verbatim; receipt kept as s31b-run-pkg-probe-run1.txt)","cwd":"P:/av-kit-wt/s31b-gui-mcp-setup-prompt","scope":"PKG_PROBE run 1: packaging pins, dist:prep, electron-builder --win dir --x64, MCP_ENTRY_PROBE in place and on the hermetic copy, pkg-result","phase":"runtime","exit_code":1,"result":"fail","tested_state":"HEAD 6097cf5 plus row 0a, MEU-71 and MEU-92 before the D-97 probe-launch repair","output":"PASS packaging pins | PASS pkg-dist-prep | PASS pkg-builder | both mcp-probe stages: FileNotFoundError [WinError 2] at subprocess.Popen on the relative path ui/dist/win-unpacked/av-kit.exe | FAIL: report missing (pkg-result)","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s31b-92-pkg-probe","command":"rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/validate-task.ps1 -Check pkg-probe *> C:/Temp/av-kit/s31b-run-pkg-probe.txt (task.md row 8, verbatim)","cwd":"P:/av-kit-wt/s31b-gui-mcp-setup-prompt","scope":"PKG_PROBE run 2 (AC-92.4): packaging pins, dist:prep, electron-builder --win dir --x64, byte-equal bundle and LICENSES.txt, MCP_ENTRY_PROBE with av-kit.exe in place and on the hermetic copy","phase":"runtime","exit_code":0,"result":"pass","tested_state":"HEAD 6097cf5 plus row 0a, MEU-71, MEU-92 and D-97; pkg-probe-result.json identity binds av-kit.exe 34383e87, index.mjs 2ee9a90b, LICENSES.txt 24ee2931, electron-builder.yml 965321f3 and both package.json and package-lock.json pairs","output":"PASS packaging pins | PASS pkg-dist-prep | PASS pkg-builder | PASS MCP_ENTRY_PROBE started in 0.17 s (in place) | PASS MCP_ENTRY_PROBE started in 0.11 s (hermetic) | serverInfo name av-kit version 0.1.0 | PASS PKG_PROBE: bundle and LICENSES.txt byte-equal in win-unpacked (2ee9a90bc366), both probes started; proof bound to 10 files | PASS pkg-probe","fresh":true}
```

```json
{"schema_version":"evidence.v1","check_id":"s31b-92-gate","command":"rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/validate-task.ps1 -Check gate92 *> C:/Temp/av-kit/s31b-run-gate92.txt (task.md row 9, verbatim; product-file manifest C:/Temp/av-kit/s31b-gate92-manifest.txt)","cwd":"P:/av-kit-wt/s31b-gui-mcp-setup-prompt","scope":"MEU-92 gate: mcp-types, mcp-build, mcp-bundle, full mcp-server Vitest, the MEU-71 ui unit set, pkg-current (PKG_EVIDENCE)","phase":"targeted","exit_code":0,"result":"pass","tested_state":"HEAD 6097cf59adc7835fa6062c8bd3d55c679aef4543 plus 61 uncommitted product paths (git diff --name-only HEAD and untracked, excluding the plan folder and handoffs); sha256 of the per-file sha256sum manifest 1ee1a6d1012cf5f521bfb0596eb8bfc37cc0e479d5356a6ca182f0e220bd6e03","output":"PASS mcp-types | PASS mcp-build | PASS mcp-bundle | PASS gate92-mcp-vitest: 446 passed of 446 | PASS gate92-ui-vitest: 56 passed of 56 | PASS PKG_EVIDENCE: pkg-probe-result.json passed and all 10 bound files are unchanged | PASS gate92","fresh":true}
```

### Quality Gate Results

The MEU-92 gate is `validate-task.ps1 -Check gate92` (task.md row 9). It passed first time: the full mcp-server suite (446, the 438 of gate71 plus the 8 MEU-92 tests), the MEU-71 ui unit set, and `pkg-current`, which re-hashed the 10 files row 8 proved after the fresh bundle. The packaged proof is row 8's run 2. Run 1 built the tree, but the plan's probe harness could not launch a relative `/` exe path, repaired as D-97. The worktree has no `packaging/dist/avkit-backend` or `packaging/ffmpeg-win64` (gitignored outputs); electron-builder skipped both with a warning, and AC-92.4 reads neither. The fresh full D6 gate (`-Check gate`, H1-2) then passed: `gate-result.json` `passed: true`, including `gate-mcp-bundle` and `gate-pkg-current` after the fresh bundle, mcp-server 446/446 and `COUNT_FLOORS` pass. Mat's Claude Desktop run of the setup prompt (`RESULT: connected`) used the dev entry `mcp-server/dist/index.js`, not the packaged `index.mjs`; the packaged start is row 8's `MCP_ENTRY_PROBE`.

---

## Changed Files

| File | Action | Summary |
|------|--------|---------|
| `mcp-server/scripts/bundle.ts` | new | `BUNDLE_OPTIONS` (exported), `bundle()`; runs only as the main module |
| `mcp-server/scripts/bundle-licenses.ts` | new | `collectLicenses`, `renderLicenses` |
| `mcp-server/package.json`, `mcp-server/package-lock.json` | modified | `"bundle": "tsx scripts/bundle.ts"`; `"esbuild": "0.28.2"` (already in the lockfile through `tsx`, so two lockfile lines) |
| `ui/electron-builder.yml` | modified | `- from: ../mcp-server/bundle` |
| `ui/package.json` | modified | `dist:prep` ends with `&& npm --prefix ../mcp-server run bundle` |
| `.gitignore` | modified | `mcp-server/bundle/` |
| `mcp-server/tests/bundle.test.ts` | new | AC-92.1, AC-92.3 (node builtins and Vitest only) |
| `mcp-server/tests/bundle-licenses.test.ts` | new | AC-92.2 |

```diff
   - from: ../packaging/THIRD_PARTY_NOTICES.md
     to: THIRD_PARTY_NOTICES.md
-  - from: ../mcp-server/dist
+  - from: ../mcp-server/bundle
     to: mcp-server
```

Shared by both MEUs: the plan folder `docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/` (including the `plan_checks.py` probe-launch repair, D-97) and the hub files listed in the plan's §Shared table (row 10 and H1/H2).

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

None.

---

## Decision Log

```yaml
decision_log:
  - id: D-97
    stage: execution
    question: "pkg-probe run 1 built win-unpacked, but MCP_ENTRY_PROBE could not launch ui/dist/win-unpacked/av-kit.exe (FileNotFoundError, WinError 2) although the file exists. Is the probe harness repaired in place?"
    resolution: autonomous
    class: two-way
    chosen: "plan_checks.py mcp_probe launches the resolved absolute path of argv[0]; the existence check, the initialize request, the 10 s deadline and probe_passed are unchanged, and pkg-probe re-runs from the start"
    source_tag: Local Canon
    precedents: ["D-93 - a plan check that could not pass in this worktree was repaired as a two-way autonomous call and logged", "AGENTS.md:57 - setup may be repaired; assertions may not"]
    research: { engine: none, sources: [] }
    reasoning: "A direct check showed CreateProcess rejecting the relative forward-slash path while the absolute path runs av-kit.exe in node mode (exit 0, node 24.18.1). The fix changes how the probe starts the process, not what it requires, so it cannot turn a failing entry green."
  - id: D-98
    stage: execution
    question: "AC-92.2 requires LICENSES.txt to name every package in the real build's metafile, but the shipped bundle/ holds only index.mjs and LICENSES.txt; where does the test get the metafile?"
    resolution: autonomous
    class: two-way
    chosen: "bundle.ts exports BUNDLE_OPTIONS and runs only as the main module; the test rebuilds with those options and write: false, derives the package names from that metafile with its own regex, and checks LICENSES.txt for a heading per package"
    source_tag: Local Canon
    precedents: ["implementation-plan.md MEU-92 Boundary Inventory - resources/mcp-server holds only index.mjs and LICENSES.txt", "mcp-server/src/index.ts - the isMainModule guard keeps an import from starting the server"]
    research: { engine: none, sources: [] }
    reasoning: "Writing the metafile into bundle/ would ship it, and a second output folder adds an artifact to keep in step; rebuilding from the exported options reads the same inputs, and deriving names independently keeps collectLicenses from being its own oracle."
```

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-10-17 | claude-code-local (Claude Opus 5.5) | Initial MEU-92 handoff after gate92 |
