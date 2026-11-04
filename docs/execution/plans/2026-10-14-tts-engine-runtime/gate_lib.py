"""Gate library for 2026-10-14-tts-engine-runtime (Session 32), called only by validate-task.ps1.

Session 30's validate-task.sh kept these parsers as inline heredocs. This plan runs fully on Windows
(implementation-plan.md §Harness), so they live here as subcommands, run through
`rtk proxy uv run python`. Each subcommand prints `PASS ...` or `FAIL: ...` and exits 0 or 1.
`identity` prints the WORKTREE_IDENTITY hex digest and nothing else.

This file is in GATED_PATHS: any edit to it after the gate reopens the gate.
Only the standard library is used, plus PyYAML for the SSOT checks (it is a project dependency).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path

PLAN = "docs/execution/plans/2026-10-14-tts-engine-runtime"
TARGET = f"{PLAN}/implementation-plan.md"
# The windows-gate stage order (Sessions 30 and 31). plan_checks.py asserts it equals the ps1 $stages ids.
ORDER = ["npm-ci", "mcp-npm-ci", "py-types", "py-lint", "ui-types", "ui-lint", "mcp-types", "py-tests", "ui-tests",
         "ui-build", "ui-harness-build", "mcp-build", "mcp-tests", "openapi", "state-render", "ui-electron",
         "source-audit"]
# A failing test that raises one of these is an assertion-level Red (the test expected a different domain outcome).
DOMAIN_ERRORS = ("ValidationError", "ConflictError", "TtsRuntimeError", "ModelLoadError", "ModelDownloadError")
TEST_ROOTS = ("tests/", "ui/tests/", "mcp-server/tests/")
SCOPE_ROOTS = ["ui", "packages", "mcp-server", "tests", "tools", "packaging", "openapi.committed.json", "uv.lock"]
ISSUES_RESOLVED = ["TTS-VOICE-PACK-LAZY-FETCH", "SETTINGS-TTS-ASSET-ROW-STALE", "TTS-SPACY-SYSPATH-PREPEND",
                   "TTS-NON-ENGLISH-G2P-DEPS", "TTS-PACKAGED-RUNTIME-EXCLUDED"]
GROUPING = ".agent/context/grouping/2026-10-09-triage-residuals-session-grouping.md"
GROUPING_ROW = "| 32 | `tts-engine-runtime` | MEU-73, MEU-74, MEU-72 | P2 |"


def _fail(msg: str) -> int:
    print(f"FAIL: {msg}")
    return 1


def _git(*args: str) -> bytes:
    return subprocess.run(["git", *args], capture_output=True, check=True).stdout


def _read(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


# ---------------------------------------------------------------- plan parsing

def plan_acs(plan: str) -> dict[str, str]:
    """AC id -> the first backticked path in the AC row's Test cell (or '' when it names no file)."""
    out: dict[str, str] = {}
    for line in plan.splitlines():
        m = re.match(r"^\| (AC-\d+\.\d+) \|", line)
        if not m:
            continue
        cell = line.rstrip().rstrip("|").split("|")[-1]
        p = re.search(r"`([^`\s]+)`", cell)
        out[m.group(1)] = p.group(1) if p else ""
    return out


def plan_ta_ranges(plan: str) -> dict[str, list[tuple[int, int]] | None]:
    """TEST_AMENDMENTS file -> allowed baseline line ranges (None = the whole file is fenced in)."""
    out: dict[str, list[tuple[int, int]] | None] = {}
    for line in plan.splitlines():
        if not re.match(r"^\| TA-\d+[a-z]? \|", line):
            continue
        cell = line.split("|")[2]
        for item in re.findall(r"`([^`]+)`", cell):
            path, _, spec = item.partition(":")
            if not spec:
                out[path] = None
                continue
            ranges = []
            for part in spec.split(","):
                a, _, b = part.strip().partition("-")
                ranges.append((int(a), int(b or a)))
            prev = out.get(path, [])
            out[path] = None if prev is None and path in out else (prev or []) + ranges
    return out


def plan_files(plan: str) -> dict[str, set[str]]:
    """Files Modified path -> the set of actions it is listed with."""
    out: dict[str, set[str]] = {}
    for path, action in re.findall(r"^\| `([^`]+)` \| (new|modify \(append\)|modify) \|", plan, re.M):
        out.setdefault(path, set()).add(action)
    return out


def _tag_re(ac: str, style: str) -> re.Pattern[str]:
    meu, n = ac[3:].split(".")
    text = f"ac_{meu}_{n}" if style == "py" else f"AC-{meu}.{n}"
    return re.compile(re.escape(text) + r"(?!\d)", re.I)


# ---------------------------------------------------------------- identity

def worktree_identity(paths: list[str]) -> str:
    """WORKTREE_IDENTITY: HEAD, the binary diff over GATED_PATHS, and each untracked gated file's bytes."""
    h = hashlib.sha256()
    h.update(_git("rev-parse", "HEAD").strip() + b"\n")
    h.update(_git("diff", "HEAD", "--binary", "--", *paths))
    others = [p for p in _git("ls-files", "--others", "--exclude-standard", "-z", "--", *paths).split(b"\0") if p]
    for p in sorted(others):
        h.update(p + b"\0" + hashlib.sha256(Path(p.decode("utf-8")).read_bytes()).hexdigest().encode() + b"\n")
    return h.hexdigest()


def cmd_identity(a: argparse.Namespace) -> int:
    print(worktree_identity(a.paths))
    return 0


# ---------------------------------------------------------------- SSOT state

def _meu_rows() -> dict[str, str | None]:
    import yaml
    data = yaml.safe_load(open(".agent/context/meu-status.yaml", encoding="utf-8"))
    return {r["id"]: r.get("status") for r in data["meus"]}


def cmd_meu_state(a: argparse.Namespace) -> int:
    rows = _meu_rows()
    want = dict(w.split("=", 1) for w in a.want)
    bad = {k: rows.get(k) for k, v in want.items() if rows.get(k) != v}
    if bad:
        return _fail(f"MEU state {bad} (want {want}; Stop condition S1 if a prerequisite moved)")
    print(f"PASS MEU state {want}")
    return 0


# ---------------------------------------------------------------- pytest

def _pytest_failed(path: str) -> tuple[set[str], str]:
    text = Path(path).read_text(encoding="utf-8", errors="replace")
    if not re.search(r"\d+ (passed|failed)", text):
        raise SystemExit(f"FAIL: {path} has no pytest summary (collection/runner error)")
    return {ln.split(" - ")[0] for ln in text.splitlines() if ln.startswith(("FAILED ", "ERROR "))}, text


def _module_of(path: str) -> str:
    return path[:-3].replace("/", ".") if path.endswith(".py") else path


def cmd_pytest_red(a: argparse.Namespace) -> int:
    if a.rc == 0:
        return _fail(f"red-{a.meu}: pytest Red expected a failing run, got exit 0")
    if not Path(a.junit).exists():
        return _fail(f"red-{a.meu}: junit XML missing (exit {a.rc})")
    plan = _read(a.plan)
    symbols = [s for s in a.symbols.split(",") if s]
    ta_files = set(plan_ta_ranges(plan))
    decisive: list[str] = []
    tolerated: list[str] = []  # tests failing only because a declared new symbol does not exist yet
    ta_other: list[str] = []
    bad: list[str] = []
    for case in ET.parse(a.junit).getroot().iter("testcase"):
        cls, name = case.get("classname") or "", case.get("name") or ""
        full = f"{cls}::{name}"
        for kind in ("failure", "error"):
            for el in case.findall(kind):
                msg = (el.get("message") or "") + (el.text or "")
                if (re.search(r"ModuleNotFoundError|ImportError|AttributeError", msg)
                        and any(re.search(rf"\b{re.escape(s)}\b", msg) for s in symbols)):
                    tolerated.append(full)
                elif kind == "failure" and ("AssertionError" in msg or "assert " in msg or "DID NOT RAISE" in msg
                                            or any(e in msg for e in DOMAIN_ERRORS)):
                    if re.search(rf"ac_{a.meu}_\d+", name, re.I):
                        decisive.append(full)
                    elif any(cls.startswith(_module_of(f)) for f in ta_files):
                        ta_other.append(full)
                    else:
                        bad.append(f"untagged failure outside TEST_AMENDMENTS files: {full}")
                else:
                    bad.append(f"{kind}: {full}: {msg[:200]}")
    if bad:
        return _fail(f"red-{a.meu}: {bad[:6]}")
    run_set = {f.replace("\\", "/") for f in a.files}
    red = decisive + [t for t in tolerated if re.search(rf"ac_{a.meu}_\d+", t, re.I)]
    missing = [ac for ac, test in plan_acs(plan).items()
               if ac.startswith(f"AC-{a.meu}.") and test.endswith(".py") and test in run_set
               and not any(_tag_re(ac, "py").search(d) for d in red)]
    if missing:
        return _fail(f"red-{a.meu}: no failing test for {missing} (a test named ac_{a.meu}_n must fail on an "
                     f"assertion or on a declared new symbol)")
    print(f"PASS red-{a.meu} pytest: {len(decisive)} decisive AC assertions, {len(tolerated)} declared-symbol import "
          f"errors, TEST_AMENDMENTS-file failures (disposition in walkthrough): {ta_other}")
    return 0


def cmd_pytest_ok(a: argparse.Namespace) -> int:
    base, _ = _pytest_failed(a.baseline)
    head, text = _pytest_failed(a.receipt)
    new = sorted(head - base)
    if new:
        return _fail(f"{a.receipt}: new pytest failures versus the baseline: {new}")
    if a.rc != 0 and not head:
        return _fail(f"{a.receipt}: exit {a.rc} with no failed test (runner error)")
    m = re.search(r"(\d+) passed", text)
    print(f"PASS pytest {Path(a.receipt).stem}: {m.group(1) if m else '?'} passed; baseline failures tolerated: {sorted(head)}")
    return 0


# ---------------------------------------------------------------- vitest

def _vitest(path: str) -> tuple[dict, list[dict]]:
    if not Path(path).exists():
        raise SystemExit(f"FAIL: Vitest JSON missing: {path}")
    j = json.loads(Path(path).read_text(encoding="utf-8"))
    load = [s["name"] for s in j.get("testResults", []) if s.get("message")]
    if load:
        raise SystemExit(f"FAIL: suite load errors {load}")
    if j.get("numPendingTests", 0) or j.get("numTodoTests", 0):
        raise SystemExit("FAIL: pending/todo tests present")
    failed = [dict(t, file=s["name"].replace("\\", "/")) for s in j.get("testResults", [])
              for t in s.get("assertionResults", []) if t.get("status") == "failed"]
    return j, failed


def cmd_vitest_red(a: argparse.Namespace) -> int:
    if a.rc == 0:
        return _fail(f"red-{a.meu} {a.pkg}: Vitest Red expected a failing run, got exit 0")
    plan = _read(a.plan)
    j, failed = _vitest(a.json)
    ta_files = set(plan_ta_ranges(plan))
    symbols = [s for s in a.symbols.split(",") if s]
    decisive, ta_other, bad = [], [], []
    for t in failed:
        raw = " ".join(t.get("failureMessages", []))
        msgs = raw.lower()
        # A testing-library "Unable to find" is a missing element: the assertion-level Red of a GUI test.
        asserted = ("expected" in msgs or "assert" in msgs or "unable to find" in msgs
                    or any(s in raw and "is not a function" in raw for s in symbols))
        if asserted and re.search(rf"AC-{a.meu}\.\d+", t.get("fullName", "")):
            decisive.append(t["fullName"])
        elif asserted and any(t["file"].endswith(f) for f in ta_files):
            ta_other.append(t["fullName"][:80])
        else:
            bad.append(t["fullName"][:100])
    if bad:
        return _fail(f"red-{a.meu} {a.pkg}: failures that are not AC-{a.meu} assertions or TEST_AMENDMENTS pins: {bad[:6]}")
    run_set = {f"{a.pkg}/{f}".replace("\\", "/") for f in a.files}
    missing = [ac for ac, test in plan_acs(plan).items()
               if ac.startswith(f"AC-{a.meu}.") and test in run_set
               and not any(_tag_re(ac, "ts").search(d) for d in decisive)]
    if missing:
        return _fail(f"red-{a.meu} {a.pkg}: no failing assertion for {missing}")
    print(f"PASS red-{a.meu} {a.pkg} Vitest: {len(decisive)} decisive, {j.get('numPassedTests')} passing; "
          f"TEST_AMENDMENTS pins failing: {ta_other}")
    return 0


def cmd_vitest_ok(a: argparse.Namespace) -> int:
    j, failed = _vitest(a.json)
    base: set[str] = set()
    if a.baseline and Path(a.baseline).exists():
        base = {t["fullName"] for t in _vitest(a.baseline)[1]}
    real = [t["fullName"] for t in failed if t["fullName"] not in base]
    if real:
        return _fail(f"{Path(a.json).stem}: real failures: {real[:8]}")
    if a.rc != 0 and not failed:
        return _fail(f"{Path(a.json).stem}: exit {a.rc} with no failed assertion (runner error)")
    print(f"PASS {Path(a.json).stem}: {j.get('numPassedTests')} passed of {j.get('numTotalTests')}; "
          f"baseline failures tolerated: {len(failed)}")
    return 0


# ---------------------------------------------------------------- Playwright / Electron

def _specs(suite: dict):
    for s in suite.get("specs", []):
        yield suite.get("file", ""), s
    for child in suite.get("suites", []):
        yield from _specs(child)


def _playwright(path: str) -> dict:
    if not Path(path).exists():
        raise SystemExit(f"FAIL: Playwright JSON missing: {path}")
    j = json.loads(Path(path).read_text(encoding="utf-8"))
    if j.get("errors"):
        raise SystemExit(f"FAIL: top-level Playwright errors (collection/launch): {j['errors'][:1]}")
    return j


def cmd_electron_red(a: argparse.Namespace) -> int:
    if a.rc == 0:
        return _fail(f"{a.tag}: Electron Red expected a failing run, got exit 0")
    j = _playwright(a.json)
    decisive = []
    for top in j.get("suites", []):
        for _, spec in _specs(top):
            if a.tag not in spec.get("title", ""):
                continue
            for test in spec.get("tests", []):
                for res in test.get("results", []):
                    msgs = [e.get("message", "") for e in res.get("errors", [])] + [(res.get("error") or {}).get("message", "")]
                    if res.get("status") == "failed" and any("expect(" in m or "Expected" in m for m in msgs):
                        decisive.append(spec["title"])
    if not decisive:
        return _fail(f"{a.tag}: no failed {a.tag} spec with an expect() assertion error")
    print(f"PASS {a.tag} Electron Red: {len(decisive)} failing specs")
    return 0


def _electron_failures(j: dict) -> tuple[list[str], int]:
    real, passed = [], 0
    for top in j.get("suites", []):
        for file, spec in _specs(top):
            for test in spec.get("tests", []):
                results = test.get("results", [])
                last = results[-1].get("status") if results else "missing"
                if last in ("passed", "skipped") and test.get("status") not in ("unexpected", "flaky"):
                    passed += last == "passed"
                    continue
                real.append(f"{file}: {spec.get('title')} ({test.get('status')})")
    return real, passed


def cmd_electron_ok(a: argparse.Namespace) -> int:
    real, passed = _electron_failures(_playwright(a.json))
    base: set[str] = set()
    if a.baseline and Path(a.baseline).exists():
        base = set(_electron_failures(_playwright(a.baseline))[0])
    new = [r for r in real if r not in base]
    if new:
        return _fail(f"{Path(a.json).stem}: Electron failures (flaky counts as real): {new[:8]}")
    if a.rc != 0 and not real:
        return _fail(f"{Path(a.json).stem}: exit {a.rc} with no failed spec (runner error)")
    print(f"PASS {Path(a.json).stem}: {passed} passed; baseline failures tolerated: {len(real)}")
    return 0


# ---------------------------------------------------------------- scope fences

def _changed(base: str, roots: list[str]) -> set[str]:
    out = set(_git("diff", "--name-only", base, "--", *roots).decode().split())
    out |= {p for p in _git("ls-files", "--others", "--exclude-standard", "--", *roots).decode().splitlines() if p}
    return out


def _existed(base: str, path: str) -> bool:
    return subprocess.run(["git", "cat-file", "-e", f"{base}:{path}"], capture_output=True).returncode == 0


def _removed_lines(base: str, path: str) -> list[int]:
    diff = _git("diff", "-U0", base, "--", path).decode("utf-8", errors="replace")
    lines: list[int] = []
    for m in re.finditer(r"^@@ -(\d+)(?:,(\d+))? \+", diff, re.M):
        start, count = int(m.group(1)), int(m.group(2) if m.group(2) is not None else 1)
        lines.extend(range(start, start + count))
    return lines


def cmd_ta_check(a: argparse.Namespace) -> int:
    base = Path(a.baseline_sha).read_text(encoding="utf-8").strip()
    plan = _read(a.plan)
    ta = plan_ta_ranges(plan)
    files = plan_files(plan)
    errors = []
    for path in sorted(_changed(base, list(TEST_ROOTS))):
        if not path.startswith(TEST_ROOTS) or not _existed(base, path):
            continue
        removed = _removed_lines(base, path)
        if not removed:
            continue
        if path in ta:
            ranges = ta[path]
            if ranges is None:
                continue
            outside = [n for n in removed if not any(lo <= n <= hi for lo, hi in ranges)]
            if outside:
                errors.append(f"{path}: baseline lines {outside[:10]} changed outside its TEST_AMENDMENTS ranges {ranges}")
        elif "modify (append)" in files.get(path, set()):
            errors.append(f"{path}: 'modify (append)' file has removed or changed lines {removed[:10]}")
        else:
            errors.append(f"{path}: existing test file changed but is not in TEST_AMENDMENTS (lines {removed[:10]})")
    if errors:
        return _fail("; ".join(errors))
    ids = sorted({m for m in re.findall(r"^\| (TA-\d+[a-z]?) \|", plan, re.M)}, key=lambda t: (int(re.sub(r"\D", "", t)), t))
    print(f"PASS ta-check: existing test edits stay inside the {len(ids)} TEST_AMENDMENTS rows' ranges ({ids[0]}..{ids[-1]}); "
          f"append-only files only grew (base {base[:7]})")
    return 0


def cmd_api_scope(a: argparse.Namespace) -> int:
    base = Path(a.baseline_sha).read_text(encoding="utf-8").strip()
    plan = _read(a.plan)
    listed = set(plan_files(plan))
    changed = _changed(base, SCOPE_ROOTS)
    extra = sorted(changed - listed)
    if extra:
        return _fail(f"PRODUCT_SCOPE: changed files not in a Files Modified table: {extra}")
    print(f"PASS PRODUCT_SCOPE: {len(changed)} changed product files since {base[:7]}, all listed")
    return 0


# ---------------------------------------------------------------- task state and hub

def cmd_task_state(a: argparse.Namespace) -> int:
    lo, hi = (int(x) for x in a.rows.split("-"))
    rows = {}
    for line in _read(a.task).splitlines():
        m = re.match(r"^\| (\d+) \|", line)
        if m:
            rows[int(m.group(1))] = line
    if sorted(rows) != list(range(lo, hi + 1)):
        return _fail(f"expected rows {lo}-{hi}, got {sorted(rows)}")
    text = _read(a.task)
    for n, line in rows.items():
        status = line.rstrip().rstrip("|").split("|")[-1].strip().strip("`")
        if status == "[x]":
            continue
        if status == "[B]" and re.search(rf"^### B-{n}$", text, re.M) and "follow-up" in line:
            continue
        return _fail(f"row {n} is {status!r} (needs [x], or [B] with a ### B-{n} block and a follow-up)")
    print(f"PASS implementation rows {lo}-{hi}")
    return 0


def _section(text: str, heading: str) -> str:
    parts = text.split(heading, 1)
    if len(parts) < 2:
        return ""
    level = heading.split(" ", 1)[0]
    return re.split(rf"\n#{{1,{len(level)}}} ", parts[1], maxsplit=1)[0]


def cmd_hub(a: argparse.Namespace) -> int:
    bp = "docs/build-plan"
    errors = []
    b02 = _read(f"{bp}/02-infrastructure.md")
    if "onnx-community/Kokoro-82M-v1.0-ONNX" not in b02 or "`onnx-community/Kokoro-82M-ONNX`" in b02:
        errors.append("02-infrastructure.md still names the v0.19 ONNX repo or lacks Kokoro-82M-v1.0-ONNX")
    b03 = _read(f"{bp}/03-service-layer.md")
    for h in ("## TTS voice assets (residual)", "## TTS language runtime (residual)"):
        if "Delivered (Session 32)" not in _section(b03, h):
            errors.append(f"03 {h} lacks its 'Delivered (Session 32)' line")
    b07 = _section(_read(f"{bp}/07-distribution.md"), "### Packaged ONNX TTS runtime (residual)")
    if not all(k in b07 for k in ("Delivered (Session 32)", "tools/smoke_packaged_tts.py", "THIRD_PARTY_NOTICES")):
        errors.append("07 §Packaged ONNX lacks the Delivered line naming tools/smoke_packaged_tts.py and THIRD_PARTY_NOTICES")
    dep = [ln for ln in _read(f"{bp}/06-gui.md").splitlines() if ln.startswith("| Dependencies |")]
    if not dep or not any("eSpeak NG" in ln and "TTS assets" in ln for ln in dep):
        errors.append("06-gui.md Dependencies row lacks TTS assets and eSpeak NG")
    vp = [ln for ln in _read(f"{bp}/11-page-layout.md").splitlines() if ln.startswith("| Voice picker |")]
    if not vp or "unavailable" not in vp[0]:
        errors.append("11-page-layout.md Voice picker row does not describe unavailable voices")
    matrix = _read(f"{bp}/build-priority-matrix.md")
    for row in ("| 3.6 | MEU-73 |", "| 3.7 | MEU-74 |", "| 7.4 | MEU-72 |"):
        if row not in matrix:
            errors.append(f"build-priority-matrix.md lacks {row}")
    if errors:
        return _fail("; ".join(errors))
    print("PASS hub reconciliation (02, 03 x2, 06, 07, 11, matrix)")
    return 0


# ---------------------------------------------------------------- gate results

def _sha(path: str) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest().upper()


def _load(path: str) -> dict:
    try:
        return json.loads(Path(path).read_text(encoding="utf-8-sig"))
    except OSError as err:
        raise SystemExit(f"FAIL: {path} unreadable: {err}")


def cmd_gate_check(a: argparse.Namespace) -> int:
    ident = worktree_identity(a.gated)
    errors = []
    g = _load(f"{PLAN}/windows-gate-result.json")
    if g.get("schema") != "s32-windows-gate.v1":
        errors.append(f"windows-gate schema {g.get('schema')}")
    if g.get("identity") != ident or g.get("identity_end") != ident:
        errors.append(f"windows-gate identity {g.get('identity')}/{g.get('identity_end')} != current {ident}")
    for key, path in (("lockfile_sha256", "ui/package-lock.json"), ("mcp_lockfile_sha256", "mcp-server/package-lock.json"),
                      ("uv_lock_sha256", "uv.lock")):
        if (g.get(key) or "").upper() != _sha(path):
            errors.append(f"windows-gate {key} differs from {path}")
    pre = g.get("preflight") or {}
    if not pre.get("agentic_framework_head") or not pre.get("agent_registry_sha256") or pre.get("drift") is not False:
        errors.append(f"windows-gate preflight {pre}")
    got = [s.get("id") for s in g.get("stages", [])]
    if got != ORDER:
        errors.append(f"windows-gate stages {got} != {ORDER}")
    failed = [s.get("id") for s in g.get("stages", []) if s.get("exit") != 0]
    if failed:
        errors.append(f"windows-gate stages failed: {failed}")
    v, e, py = g.get("vitest") or {}, g.get("e2e") or {}, g.get("pytest") or {}
    if v.get("failed") != 0 or (v.get("total") or 0) < a.floor_vitest:
        errors.append(f"vitest {v} (COUNT_FLOORS total >= {a.floor_vitest}, failed 0)")
    if e.get("unexpected") != 0 or e.get("flaky") not in (0, None) or (e.get("expected") or 0) < a.floor_e2e:
        errors.append(f"e2e {e} (COUNT_FLOORS expected >= {a.floor_e2e}, unexpected 0, flaky 0)")
    if py.get("failed") != 0 or (py.get("passed") or 0) < a.floor_pytest:
        errors.append(f"pytest {py} (COUNT_FLOORS passed >= {a.floor_pytest}, failed 0)")
    s = _load(f"{PLAN}/package-smoke-result.json")
    if s.get("schema") != "s32-package-smoke.v2":
        errors.append(f"package-smoke schema {s.get('schema')}")
    if s.get("identity") != ident or s.get("identity_end") != ident:
        errors.append(f"package-smoke identity {s.get('identity')}/{s.get('identity_end')} != current {ident}")
    online = s.get("online") or {}
    if online.get("passed") is not True or online.get("forbidden_dirs") != []:
        errors.append(f"ONLINE_PROVISION {online}")
    inst = s.get("installer") or {}
    if (inst.get("dist_exit") != 0 or inst.get("nsis_assert_exit") != 0
            or inst.get("notices_staged") is not True or inst.get("ffmpeg_license_staged") is not True):
        errors.append(f"INSTALLER_STAGE {inst}")
    off = s.get("offline") or {}
    probe = off.get("negative_probe") or {}
    proxy = off.get("proxy") or {}
    root = Path.cwd().resolve()
    try:
        inside = Path(off.get("backend_dir") or ".").resolve().is_relative_to(root)
    except OSError:
        inside = True
    if (off.get("passed") is not True or (off.get("wav_samples") or 0) <= 8000 or probe.get("state") != "Failed"
            or not probe.get("error") or not off.get("backend_dir") or inside
            or any(proxy.get(k) != "http://127.0.0.1:9" for k in ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY"))):
        errors.append(f"OFFLINE_SMOKE {off} (needs passed, wav_samples > 8000, negative_probe Failed with an error, "
                      f"backend_dir outside {root}, dead proxies)")
    if (s.get("mcp_probe") or {}).get("result") not in ("started", "unreachable"):
        errors.append(f"MCP_ENTRY_PROBE not recorded: {s.get('mcp_probe')}")
    if errors:
        return _fail("; ".join(errors))
    print(f"PASS windows gate + package smoke @ {ident[:12]}: vitest {v} e2e {e} pytest {py}; "
          f"offline wav_samples {off.get('wav_samples')}, probe {probe.get('state')}; MCP probe {s['mcp_probe']['result']}")
    return 0


def cmd_mcp_probe(a: argparse.Namespace) -> int:
    """MCP_ENTRY_PROBE: recorded, never a pass condition, so it exits 0 once the record is written."""
    rec: dict = {"entry": a.entry, "result": "unreachable", "exit_code": None, "stderr_tail": "", "seconds": None}
    if not Path(a.entry).exists():
        rec["stderr_tail"] = "entry file missing"
    else:
        init = {"jsonrpc": "2.0", "id": 1, "method": "initialize",
                "params": {"protocolVersion": "2025-06-18", "capabilities": {},
                           "clientInfo": {"name": "s32-mcp-probe", "version": "1"}}}
        start = time.monotonic()
        proc = subprocess.Popen(["node", a.entry], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, text=True, encoding="utf-8")
        assert proc.stdin and proc.stdout
        proc.stdin.write(json.dumps(init) + "\n")
        proc.stdin.flush()
        import threading
        lines: list[str] = []
        reader = threading.Thread(target=lambda: lines.extend(iter(proc.stdout.readline, "")), daemon=True)
        reader.start()
        deadline = start + 10
        while time.monotonic() < deadline and proc.poll() is None:
            if any('"jsonrpc"' in ln for ln in lines):
                rec["result"] = "started"
                break
            time.sleep(0.1)
        rec["seconds"] = round(time.monotonic() - start, 2)
        proc.kill()
        _, err = proc.communicate(timeout=5)
        rec["exit_code"] = proc.returncode
        rec["stderr_tail"] = (err or "")[-800:]
        rec["first_stdout"] = lines[0][:300] if lines else ""
    Path(a.out).write_text(json.dumps(rec, indent=2), encoding="utf-8")
    print(f"PASS MCP_ENTRY_PROBE recorded: {rec['result']} (exit {rec['exit_code']})")
    return 0


# ---------------------------------------------------------------- review and SSOT closeout

ANTHROPIC = re.compile(r"claude|opus|sonnet|haiku|fable|anthropic", re.I)


def cmd_review_check(a: argparse.Namespace) -> int:
    t = _read(a.file)
    parts = t.split("---")
    if len(parts) < 3:
        return _fail(f"{a.file} has no YAML frontmatter")
    fm = dict(re.findall(r'^(\w+):\s*"?([^"\n]*)"?\s*$', parts[1], re.M))
    if fm.get("target_plan") != TARGET:
        return _fail(f"target_plan {fm.get('target_plan')}")
    if fm.get("review_mode") != a.mode:
        return _fail(f"review_mode {fm.get('review_mode')}")
    if int(fm.get("round", "0") or 0) > a.cap:
        return _fail(f"round {fm.get('round')} over cap {a.cap}")
    if fm.get("verdict") != "approved":
        return _fail(f"verdict {fm.get('verdict')}")
    agent = fm.get("agent", "")
    # The author is Anthropic; the reviewer must be the Codex route (vendor OpenAI), never same-vendor.
    if not agent or ANTHROPIC.search(agent):
        return _fail(f"agent {agent!r} is not the Codex reviewer route")
    print(f"PASS {a.mode} review approved round {fm['round']} by {agent}")
    return 0


def cmd_ssot(a: argparse.Namespace) -> int:
    import yaml
    rows = _meu_rows()
    want = "ready_for_review" if a.stage == "review" else "approved"
    bad = {m: rows.get(m) for m in ("MEU-73", "MEU-74", "MEU-72") if rows.get(m) != want}
    if bad:
        return _fail(f"MEU state {bad} (want {want})")
    grouping = _read(GROUPING)
    label = "in review" if a.stage == "review" else "approved"
    if f"{GROUPING_ROW} {label} |" not in grouping:
        return _fail(f"grouping Session 32 row is not '{label}'")
    if a.stage == "review":
        focus = _read(".agent/context/current-focus.md")
        if "tts-engine-runtime" not in focus or "ready_for_review" not in focus:
            return _fail("current-focus.md does not record Session 32 ready_for_review")
        print("PASS SSOT review state")
        return 0
    issues = {i["id"]: i for i in yaml.safe_load(open(".agent/context/known-issues.yaml", encoding="utf-8"))["issues"]}
    for iid in ISSUES_RESOLVED:
        it = issues.get(iid) or {}
        ev = (it.get("verification") or {}).get("evidence_file") or ""
        if it.get("status") != "resolved" or not ev.startswith(f"{PLAN}/"):
            return _fail(f"{iid} status {it.get('status')} evidence {ev!r}")
    if "TTS-JA-ZH-G2P-EXTRAS" not in issues:
        return _fail("follow-up issue TTS-JA-ZH-G2P-EXTRAS not filed (D-70)")
    probe = (_load(f"{PLAN}/package-smoke-result.json").get("mcp_probe") or {}).get("result")
    mcp = issues.get("MCP-PACKAGED-ENTRY-UNREACHABLE") or {}
    expect = {"unreachable": "open", "started": "resolved"}.get(probe or "")
    mev = (mcp.get("verification") or {}).get("evidence_file") or ""
    if mcp.get("status") != expect or not mev.startswith(f"{PLAN}/"):
        return _fail(f"MCP-PACKAGED-ENTRY-UNREACHABLE status {mcp.get('status')} evidence {mev!r}; the probe said "
                     f"{probe!r}, so it must be {expect!r} (AC-72.9)")
    if "2026-10-14-tts-engine-runtime" not in _read("docs/execution/metrics.md"):
        return _fail("metrics row missing")
    print(f"PASS POST_REVIEW_STATE (MCP probe {probe} -> {expect})")
    return 0


# ---------------------------------------------------------------- CLI

def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("identity"); s.add_argument("--paths", nargs="+", required=True); s.set_defaults(fn=cmd_identity)
    s = sub.add_parser("meu-state"); s.add_argument("--want", nargs="+", required=True); s.set_defaults(fn=cmd_meu_state)
    s = sub.add_parser("pytest-red")
    for k in ("--meu", "--junit", "--symbols", "--plan"):
        s.add_argument(k, required=True)
    s.add_argument("--rc", type=int, required=True); s.add_argument("--files", nargs="+", required=True)
    s.set_defaults(fn=cmd_pytest_red)
    s = sub.add_parser("pytest-ok")
    s.add_argument("--receipt", required=True); s.add_argument("--baseline", required=True)
    s.add_argument("--rc", type=int, required=True); s.set_defaults(fn=cmd_pytest_ok)
    s = sub.add_parser("vitest-red")
    for k in ("--meu", "--pkg", "--json", "--plan"):
        s.add_argument(k, required=True)
    s.add_argument("--symbols", default="")
    s.add_argument("--rc", type=int, required=True); s.add_argument("--files", nargs="+", required=True)
    s.set_defaults(fn=cmd_vitest_red)
    s = sub.add_parser("vitest-ok")
    s.add_argument("--json", required=True); s.add_argument("--rc", type=int, required=True)
    s.add_argument("--baseline", default=""); s.set_defaults(fn=cmd_vitest_ok)
    s = sub.add_parser("electron-red")
    s.add_argument("--tag", required=True); s.add_argument("--json", required=True)
    s.add_argument("--rc", type=int, required=True); s.set_defaults(fn=cmd_electron_red)
    s = sub.add_parser("electron-ok")
    s.add_argument("--json", required=True); s.add_argument("--rc", type=int, required=True)
    s.add_argument("--baseline", default=""); s.set_defaults(fn=cmd_electron_ok)
    for name, fn in (("ta-check", cmd_ta_check), ("api-scope", cmd_api_scope)):
        s = sub.add_parser(name)
        s.add_argument("--baseline-sha", required=True); s.add_argument("--plan", required=True); s.set_defaults(fn=fn)
    s = sub.add_parser("task-state")
    s.add_argument("--task", required=True); s.add_argument("--rows", required=True); s.set_defaults(fn=cmd_task_state)
    sub.add_parser("hub").set_defaults(fn=cmd_hub)
    s = sub.add_parser("gate-check")
    s.add_argument("--gated", nargs="+", required=True)
    for k in ("--floor-vitest", "--floor-e2e", "--floor-pytest"):
        s.add_argument(k, type=int, required=True)
    s.set_defaults(fn=cmd_gate_check)
    s = sub.add_parser("mcp-probe")
    s.add_argument("--entry", required=True); s.add_argument("--out", required=True); s.set_defaults(fn=cmd_mcp_probe)
    s = sub.add_parser("review-check")
    s.add_argument("--file", required=True); s.add_argument("--mode", required=True, choices=["plan", "implementation"])
    s.add_argument("--cap", type=int, required=True); s.set_defaults(fn=cmd_review_check)
    s = sub.add_parser("ssot"); s.add_argument("--stage", required=True, choices=["review", "post-review"])
    s.set_defaults(fn=cmd_ssot)
    a = p.parse_args()
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
