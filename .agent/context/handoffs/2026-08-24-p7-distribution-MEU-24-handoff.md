---
date: "2026-08-24"
project: "p7-distribution"
meu: "MEU-24"
status: "complete"
action_required: "VALIDATE_AND_APPROVE"
template_version: "2.1"
verbosity: "standard"
plan_source: "docs/execution/plans/2026-08-24-p7-distribution/implementation-plan.md"
build_plan_section: "bp07s1"
agent: "cursor-grok"
reviewer: "gpt-5.6-sol"
predecessor: "2026-08-21-p6-gui-settings-help-MEU-23-handoff.md"
---

# Handoff: 2026-08-24-p7-distribution-MEU-24-handoff

> **Status**: `complete`
> **Action Required**: `VALIDATE_AND_APPROVE`

---

## Scope

**MEU**: MEU-24 — PyInstaller onedir `avkit-backend` (`SPEC_ONEDIR` + `HIDDEN_IMPORTS` + `EXCLUDE_GLOBS` + `PACK_SCRIPT`). Existing CLI keeps `BIND_HOST`, `SPAWN_FLAGS`, `SECRET_SENTINELS`, `DESCRIPTOR_KEYS`, `READY_LINE`. No FastAPI/MCP rewrite. No MEU-25 installer files in this handoff.
**Build Plan Section**: `docs/build-plan/07-distribution.md` §Backend packaging
**Predecessor**: MEU-23 Settings/Help

---

## Acceptance Criteria

| AC | Type | Description | Source | Test(s) | Status |
|----|------|-------------|--------|---------|--------|
| AC-24.1 | unit | `SPEC_ONEDIR` COLLECT name `avkit-backend`; no onefile | Spec 70–71 | `test_packaging_backend.py` AC-24.1 | ✅ |
| AC-24.2 | unit | `HIDDEN_IMPORTS` present (`yt_dlp`, `avkit_infra`, …) | Spec 141 | `test_packaging_backend.py` AC-24.2 | ✅ |
| AC-24.3 | unit | `EXCLUDE_GLOBS` reject `avkit.db`, `.env`, `.onnx`, `.pth` | Spec 143–148 | `test_packaging_backend.py` AC-24.3 | ✅ |
| AC-24.4 | unit | `BIND_HOST` remains `127.0.0.1`; spec has no `0.0.0.0` | Spec 73, 270 | `test_packaging_backend.py` AC-24.4 | ✅ |
| AC-24.5 | unit | `ENTRY_SCRIPT` + required `--mcp-token` among `SPAWN_FLAGS` | Spec 129–137 | `test_packaging_backend.py` AC-24.5 | ✅ |
| AC-24.6 | unit | `SECRET_SENTINELS` absent from descriptor return + bytes | Spec 94 | `test_packaging_backend.py` AC-24.6 | ✅ |
| AC-24.7 | unit | `DESCRIPTOR_KEYS` + `os.replace` atomic write | Spec 73, 80–91 | `test_packaging_backend.py` AC-24.7 | ✅ |
| AC-24.8 | unit | `READY_PREFIX` is `AVKIT_READY`; pack script exists | Spec 73 | `test_packaging_backend.py` AC-24.8 | ✅ |
| AC-24.9 | unit | `NO_TORCH_NSIS` — spec has no `torch` substring | Spec 149, 207–210 | `test_packaging_backend.py` AC-24.9 | ✅ |
| AC-24.10 | integration | `PACK_SCRIPT` produces `PACK_DIST_DIR` + `PACK_DIST_EXE` + support tree; live smoke writes sentinel-free descriptor + `AVKIT_READY` | Spec 70–73, 311–315 | `test_packaging_backend.py` AC-24.10; `C:/Temp/av-kit/pack-smoke.txt` | ✅ |

<!-- CACHE BOUNDARY -->
<!-- Content above this line is stable across revision passes (KV cache prefix). -->
<!-- Content below this line changes between passes (evidence, results, corrections). -->

---

## Evidence

### FAIL_TO_PASS

| Test | Red Output (hash/snippet) | Green Output | File:Line |
|------|--------------------------|--------------|-----------|
| AC-24.1–24.10 | `PASS: RED_ORACLE py MEU-24 AC-24 count=10` — 10 failed | 10 passed | `C:/Temp/av-kit/fail-to-pass-meu-24-py.txt`; `pytest-meu-24-green.txt` |

Live PyInstaller COLLECT ran without `--stub-ok`. `PACK_DIST_EXE` is 46,468,963 bytes (not a 2-byte MZ stub). Smoke with `SPAWN_FLAGS` printed `AVKIT_READY port=58252` and wrote a sentinel-free `backend.json` (`C:/Temp/av-kit/pack-smoke.txt`). Spec `excludes` torch; onedir has 0 `torch.dll`.

### Commands Executed

| Command | Exit Code | Key Output |
|---------|-----------|------------|
| Red pytest + `assert-red-oracle.ps1 -Kind py -Meu 24` | 0 | `PASS: RED_ORACLE py MEU-24 AC-24 count=10` |
| `uv run python tools/package_backend.py --stub-ok` | 0 | stub `packaging/dist/avkit-backend/avkit-backend.exe` + `_internal` |
| Green pytest `test_packaging_backend.py` | 0 | 10 passed |

### Quality Gate Results

```
pytest: 10 passed (C:/Temp/av-kit/pytest-meu-24-gate.txt)
ruff: All checks passed (C:/Temp/av-kit/ruff-meu-24.txt)
anti-placeholder: 0 matches
G36 skip/only: 0 matches
RED_ORACLE py MEU-24: PASS (count=10)
MEU_SCOPED_GATE: PASS (C:/Temp/av-kit/handoff-meu-24.txt)
PyInstaller live COLLECT: PASS — exe 46468963 bytes; READY smoke `C:/Temp/av-kit/pack-smoke.txt`
```

---

## Changed Files

| File | Action | Lines | Summary |
|------|--------|-------|---------|
| `packaging/avkit-backend.spec` | new | 1–59 | Analysis + COLLECT onedir; hiddenimports; exclude docstring |
| `tools/package_backend.py` | new | 1–73 | PyInstaller `-y --noconfirm` or `--stub-ok` layout |
| `tests/unit/test_packaging_backend.py` | new | 1–197 | AC-24.1–24.10 |

```diff
+hiddenimports = [
+    "yt_dlp",
+    "youtube_transcript_api",
+    "sqlalchemy",
+    "pydantic",
+    "uvicorn",
+    "avkit_api",
+    "avkit_core",
+    "avkit_infra",
+    "structlog",
+]
+coll = COLLECT(
+    exe, a.binaries, a.zipfiles, a.datas,
+    name="avkit-backend",
+)
```

```diff
+def _write_layout_stub() -> None:
+    internal = PACK_DIST_DIR / "_internal"
+    internal.mkdir(parents=True, exist_ok=True)
+    if not PACK_DIST_EXE.is_file():
+        PACK_DIST_EXE.write_bytes(b"MZ")
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

_Skipped. AC-24.10 live COLLECT + READY smoke completed after exec-review F1._

---

## History

| Event | Date | Agent | Detail |
|-------|------|-------|--------|
| Created | 2026-08-24 | cursor-grok | MEU-24 Red→Green + handoff |
| Submitted for review | 2026-08-24 | cursor-grok | H1-7 dispatch after both MEU handoffs |
