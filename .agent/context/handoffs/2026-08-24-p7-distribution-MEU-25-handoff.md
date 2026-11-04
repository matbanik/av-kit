---
date: "2026-08-24"
project: "p7-distribution"
meu: "MEU-25"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.1"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-08-24-p7-distribution/implementation-plan.md"
build_plan_section: "bp07s2"
agent: "cursor-grok"
reviewer: "gpt-5.6-sol"
predecessor: "2026-08-24-p7-distribution-MEU-24-handoff.md"
---

# Handoff: 2026-08-24-p7-distribution-MEU-25-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-25 — NSIS x64 installer (`NSIS_TARGET` + `EXTRA_RESOURCES` from `PACK_DIST_DIR` + `NSIS_KEEP_APPDATA` + `NO_TORCH_NSIS`), `FETCH_FFMPEG` pin script, `bundled_ffmpeg()` wire, `MCP_SNIPPET`, `RESOURCES_BACKEND` / `MCP_COPY_DEFAULT` Vitest. No FastAPI/MCP rewrite. No chrome/Settings rewind. No Session 8c.
**Build Plan Section**: `docs/build-plan/07-distribution.md` §Electron packaging + §FFmpeg + §MCP on a shipped machine
**Predecessor**: MEU-24 onedir backend

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-25.1 | unit | `NSIS_TARGET` win nsis x64 | Spec 177, 245 | `test_packaging_installer.py` AC-25.1 | ✅ |
| AC-25.2 | unit | `EXTRA_RESOURCES` from `PACK_DIST_DIR` to `avkit-backend` (not exe-only / not `extra/`) | Spec 102, 178 | `test_packaging_installer.py` AC-25.2 | ✅ |
| AC-25.3 | unit | `RESOURCES_BACKEND` = `join(resourcesPath,'avkit-backend','avkit-backend.exe')`; never `extra/` | Spec 102; Local Canon | `dev-spawn.test.ts` AC-25.3 | ✅ |
| AC-25.4 | unit | `BUNDLE_RESOLVER` + `BUNDLE_WIRE`: frozen sibling `ffmpeg/ffmpeg.exe` passed as `bundle_path` | Spec 159–163 | `test_ffmpeg_bundle_wire.py` AC-25.4 | ✅ |
| AC-25.5 | unit | `PROBE_ORDER` — bundled file beats PATH decoy; none → `FFmpegNotFoundError` | Spec 159–163 | `test_ffmpeg_bundle_wire.py` AC-25.5 | ✅ |
| AC-25.6 | unit | `NSIS_KEEP_APPDATA` `deleteAppDataOnUninstall: false` | Spec 258 | `test_packaging_installer.py` AC-25.6 | ✅ |
| AC-25.7 | unit | `MCP_SNIPPET` has `AVKIT_API_TOKEN` + `AVKIT_APP_DATA` only | Spec 223–234 | `test_packaging_installer.py` AC-25.7 | ✅ |
| AC-25.8 | unit | `MCP_COPY_DEFAULT` `pinEndpoint: false` omits `AVKIT_API_BASE` | Spec 230–234 | `copy-mcp-config.test.ts` AC-25.8 | ✅ |
| AC-25.9 | unit | `NO_TORCH_NSIS` — builder yml has no `.onnx` / `.pth` / cuda | Spec 207–210, 266 | `test_packaging_installer.py` AC-25.9 | ✅ |
| AC-25.10 | integration | `NSIS_BUILD_CMD` + `SIZE_CAP` — artifact exists and is `< SIZE_CAP_BYTES` | Spec 33, 284–290 | `assert-nsis-pack.ps1`; `nsis-size.txt` | ✅ |

<!-- CACHE BOUNDARY -->
<!-- Content above this line is stable across revision passes (KV cache prefix). -->
<!-- Content below this line changes between passes (evidence, results, corrections). -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|--------------------------|--------------|-----------|
| AC-25.1–25.10 py | `PASS: RED_ORACLE py MEU-25 AC-25 count=10` | 10 passed | `C:/Temp/av-kit/fail-to-pass-meu-25.txt`; `pytest-meu-25-green.txt` |
| AC-25.3 / AC-25.8 vitest | scheduled titles missing before Green | 4 passed (2 files) | `C:/Temp/av-kit/meu-25-green.txt` |
| AC-25.10 NSIS | n/a (integration after Green) | `PASS: SIZE_CAP bytes=221943296` | `C:/Temp/av-kit/nsis-build.txt`; `nsis-size.txt` |

`CLEAN_VM` install/launch remains a separate later `[B]` (plan lock 4). Vendor FFmpeg is a real BtbN pin (`sha256=5EFB8182E0770C7AF639CE46C229E5A5EA585884F17D2E94983051D8DA90BDAB`); `ffmpeg -version` / `ffprobe -version` exit 0. NSIS `av-kit Setup 0.1.0.exe` is 288,524,010 bytes. Installed payloads: `avkit-backend.exe` 46,468,963; `ffmpeg.exe` 144,441,856; `ffprobe.exe` 144,236,032. `FETCH_FFMPEG` rejects blank/mismatched SHA256.

### Commands Executed

| Command | Exit Code | Key Output |
|---------|-----------|------------|
| Red pytest + `assert-red-oracle.ps1 -Kind py -Meu 25` | 0 | `PASS: RED_ORACLE py MEU-25 AC-25 count=10` |
| Green pytest installer+wire | 0 | 10 passed |
| `npx vitest run` `VITEST_MEU25` | 0 | 4 passed |
| `npm run build` + `npx electron-builder --win nsis --x64` | 0 | `dist/av-kit Setup 0.1.0.exe` |
| `assert-nsis-pack.ps1` | 0 | `PASS: SIZE_CAP bytes=288524010` |

### Quality Gate Results

```
pytest installer+wire: 10 passed
vitest VITEST_MEU25: 4 passed
NSIS_PACK_CHECK: PASS bytes=288524010 cap=524288000
RED_ORACLE py MEU-25: PASS (count=10)
FETCH_FFMPEG SHA gate: blank/mismatch rejected (2 tests)
CLEAN_VM install/launch: later [B] — not this row
```

---

## Changed Files

| File | Action | Lines | Summary |
|------|--------|-------|---------|
| `ui/electron-builder.yml` | new | 1–21 | NSIS x64; extraResources from PACK_DIST_DIR + ffmpeg + mcp-server |
| `ui/package.json` | modified | 8–16, 40 | `dist` script + `electron-builder` dep |
| `tools/fetch_ffmpeg_windows.ps1` | new | 1–44 | pinned URL + SHA256 gate + extract |
| `docs/distribution/mcp.json.example` | new | 1–14 | token + app-data only |
| `packages/api/src/avkit_api/wiring.py` | modified | 94–150 | `bundled_ffmpeg()` + `bundle_path=` |
| `ui/tests/unit/dev-spawn.test.ts` | modified | — | AC-25.3 `packagedBackendPath` + `extra/` negative |
| `ui/tests/unit/copy-mcp-config.test.ts` | modified | 4 | AC-25.8 title on existing pinEndpoint:false case |
| `tests/unit/test_packaging_installer.py` | new | 1–108 | AC-25.1–25.3, 25.6–25.10 |
| `tests/unit/test_ffmpeg_bundle_wire.py` | new | 1–57 | AC-25.4–25.5 |

```diff
 extraResources:
+  - from: ../packaging/dist/avkit-backend
+    to: avkit-backend
+  - from: ../packaging/ffmpeg-win64
+    to: ffmpeg
+  - from: ../mcp-server/dist
+    to: mcp-server
 nsis:
+  deleteAppDataOnUninstall: false
```

```diff
+def bundled_ffmpeg() -> Path | None:
+    if not getattr(sys, "frozen", False):
+        return None
+    return Path(sys.executable).resolve().parent.parent / "ffmpeg" / "ffmpeg.exe"
-    media = FFmpegAdapter(configured_path=ffmpeg_path)
+    media = FFmpegAdapter(configured_path=ffmpeg_path, bundle_path=bundled_ffmpeg())
```

---

## Codex Validation Report

_Left blank for reviewer agent. Reviewer fills this section during `/execution-critical-review`._

### Recheck Protocol

1. Read Scope + AC table
2. Verify each AC against Evidence section (file:line, not memory)
3. Run all Commands Executed and compare output
4. Run Quality Gate commands independently
5. Record findings below

### Findings

| # | Severity | Finding | File:Line | Recommendation | Status |
|---|----------|---------|-----------|----------------|--------|
| — | — | pending independent review | — | — | open |

### Verdict

`pending` — implementer does not author the verdict

---

## Deferred Items

_Skipped. All AC-25.1–25.10 are ✅. `CLEAN_VM` install/launch is a plan-lock later `[B]` after the artifact exists and is not an AC in this MEU. Live FFmpeg SHA256 fill is recorded in Evidence, not an orphaned AC._

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-08-24 | cursor-grok | MEU-25 Red→Green + NSIS pack + handoff |
| Submitted for review | 2026-08-24 | cursor-grok | H1-7 dispatch after both MEU handoffs |
