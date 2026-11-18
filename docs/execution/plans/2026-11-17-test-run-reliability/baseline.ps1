# Test run reliability baseline (task row 0; implementation-plan.md §Verification Plan 1).
# The shape of docs/execution/plans/2026-11-17-queue-convert-fixes/baseline.ps1, with this
# plan's steps: 1. the tree state (baseline.sha, baseline-dirty.txt); 2. the path-scoped
# baseline: baseline-scope.json over §Files Modified and the "Read, never changed" files, with
# the four new files absent; baseline-dirty-hashes.json, which binds every dirty path outside
# this scope by hash; the row-0 copies (wait-check.py's, eol-check.py's and AC-12's base) and
# baseline-eol.json; baseline-skip-hashes.json over packages/, mcp-server/ and tools/ (secret
# names dropped before any stat or read, Session 83 RULE-2); the S2 binding: the trr90-probe.txt
# anchors at their probe counts and lines, unhandledRejection absent from the watch, the three
# issues open, UI-PREVIEW-ELECTRON-RUN-AS-NODE-SILENT absent, grouping row 90 proposed, no
# graphify graph, and the plan and task hashes as approved (the plan's only post-review change
# is the Status line); 3. the host-load wait (Session 81 RULE-2), then the base receipts: the
# full Vitest run (trr-base-ui.txt) and the full Python suite with the D6 argv without -x
# (trr-base-py.txt), their failures recorded, not fatal; and the timed plain run of the three
# TIME_GUARD files (trr-base-two.txt, wall_s on its last line), which must pass; 4. the
# plan-local selftests, eol-check.py over the fresh copies, and ruff format --check and ruff
# check on the plan folder's Python (Session 82 RULE-1). Every other step is fail-fast. Run
# from the repository root in pwsh.
$ErrorActionPreference = 'Stop'
$root = (git rev-parse --show-toplevel).Trim()
Set-Location $root
$plan = 'docs/execution/plans/2026-11-17-test-run-reliability'
$receipts = 'C:/Temp/av-kit/test-run-reliability'
$env:ELECTRON_RUN_AS_NODE = $null
$env:PYTHONIOENCODING = 'utf-8'
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:RECEIPTS_DIR = 'C:/Temp/av-kit'
$tmp = 'C:\Temp\av-kit\test-run-reliability\tmp'
New-Item -ItemType Directory -Force -Path $tmp | Out-Null
$env:TMP = $tmp
$env:TEMP = $tmp

function Invoke-Step([string]$Id, [string[]]$Argv) {
    & rtk proxy @Argv
    $code = $LASTEXITCODE
    Write-Output ("baseline step {0} exit={1}" -f $Id, $code)
    if ($code -ne 0) { exit $code }
}

# 1-2. Tree state, path-scoped baseline and the S2 binding, in Python so every file is read and
# written as bytes.
$record = @'
import hashlib, json, pathlib, re, subprocess, sys

PLAN = pathlib.Path("docs/execution/plans/2026-11-17-test-run-reliability")
OUT = pathlib.Path("C:/Temp/av-kit/test-run-reliability")
COPIES = OUT / "baseline-copies"
TTS = "tests/integration/test_tts_assets.py"
YT = "tests/integration/test_youtube_adapter.py"
WATCH = "ui/tests/e2e/main-error-watch.cjs"
ENV = "ui/tests/e2e/electron-env.ts"
APP = "ui/tests/e2e/electron-app.ts"
PKG = "ui/package.json"
INBOX = "ui/tests/e2e/capture-inbox.test.ts"
COMMANDS = ".agent/docs/commands.md"
REGISTER = ".agent/context/known-issues.yaml"
GROUPING = ".agent/context/grouping/2026-11-17-post-session-88-triage-session-grouping.md"
HANDOFF = ".agent/context/handoffs/2026-11-17-test-run-reliability-handoff.md"
# §Files Modified, with each file's line-ending kind (implementation-plan.md §Files Modified).
MODIFIED = {
    TTS: "CRLF",
    YT: "CRLF",
    WATCH: "LF",
    ENV: "LF",
    APP: "LF",
    PKG: "CRLF",
    COMMANDS: "CRLF",
    REGISTER: "LF",
    ".agent/context/known-issues.md": "LF",
    GROUPING: "LF",
}
NEW = {
    "ui/scripts/electron-vite-dev.mjs": "LF",
    "ui/tests/unit/rejection-watch.test.ts": "LF",
    "ui/tests/unit/dev-script.test.ts": "LF",
    "ui/tests/e2e/main-rejection-watch.test.ts": "LF",
}
# §Project files "Read, never changed": bound by hash; their kind is recorded, not expected,
# except where the plan names it.
READ_ONLY = {
    INBOX: "LF",
    "ui/tests/unit/e2e-harness.test.ts": "LF",
    "ui/tests/e2e/electron-harness.test.ts": "LF",
    "ui/scripts/playwright-with-outputfile.mjs": "CRLF",
    "ui/tests/e2e/global-setup.ts": None,
    "tests/unit/test_services.py": "CRLF",
    "tests/conftest.py": "CRLF",
    "tests/integration/test_tts_voice_packs.py": "CRLF",
    "docs/execution/plans/2026-11-15-convert-settings-drafts/dev-app-procs.py": "LF",
    "ui/src/main/index.ts": None,
    "ui/electron.vite.config.ts": None,
}
# Shared state files: read first, own lines only; copied for eol-check.py (both CRLF).
SHARED = {"docs/execution/metrics.md": "CRLF", ".agent/context/current-focus.md": "CRLF"}
PLAN_FILES = {
    f"{PLAN.as_posix()}/{n}": "LF"
    for n in (
        "implementation-plan.md", "task.md", "red-check.py", "identity.py", "issue-resolve.py",
        "eol-check.py", "baseline.ps1", "wait-check.py", "slow_worker.py", "load-run.py",
        "dev-proof.py",
    )
}
# The approved plan and task (the plan's sha moved only by the Status line's execute words:
# 7299e6159b3a... as reviewed, 57a13aeb1251... with the approval line).
PLAN_SHA = {
    f"{PLAN.as_posix()}/implementation-plan.md": "57a13aeb125108d8c9dec22f61ebd9f8ad5c2c2d59eb836dadf21519bf98b21c",
    f"{PLAN.as_posix()}/task.md": "caf440eaa7765ec6887e218d168553df589b5b730be5fedaf823916d79b797d0",
}
PLAN_REVIEW = ".agent/context/handoffs/2026-11-17-test-run-reliability-plan-critical-review.md"
# The trr90-probe.txt anchors, each bound to the count and 1-based lines the probe recorded
# (S2: the eleven TTS waits and the YouTube join at their lines, the two anchor lines, the
# watch's uncaughtException handler, the close header, the dev and preview lines, W9-7's
# regex). Three needles are shared by several lines (two pairs of assertions in the two
# gated-generation tests, and the four Idle assertions); each is bound to all its lines.
ANCHORS = (
    (TTS, "            self.hold.wait(timeout=5)", (62,)),
    (TTS, "    def wait_idle(self, timeout: float = 5.0) -> dict[str, Any]:", (177,)),
    (TTS, "    stack.services.tts.wait_idle(5.0)  # type: ignore[attr-defined]", (227,)),
    (TTS, "        gate.wait(timeout=5)", (526,)),
    (TTS, "    client.app.state.services.tts.wait_idle(5.0)  # type: ignore[attr-defined]", (712,)),
    (TTS, "def _poll_tts(client: TestClient, job_id: str, wanted: str, timeout: float = 5.0) -> str:", (896,)),
    (TTS, "        self.released.append(self.release.wait(5.0))", (938,)),
    (TTS, "    assert gated.entered.wait(5.0)", (955, 977)),
    (TTS, "    assert tts.wait_idle(5.0) is True", (963, 984)),
    (TTS, 'VOCAB = {"vocab": {"a": 1, "b": 2}, "n_token": 3}', (30,)),
    (TTS, '    assert stack.wait_idle()["state"] == "Idle"', (260, 305, 414, 515)),
    (TTS, "    assert gated.released == [True]", (964,)),
    (YT, "            service._thread.join(timeout=5)", (939,)),
    (YT, "        assert service.get_job(job.id).status is TranscriptStatus.Done", (940,)),
    (YT, "REPO_ROOT = Path(__file__).resolve().parents[2]", (40,)),
    (YT, "PROGRESS_MIN_INTERVAL_S = 0.25", (105,)),
    (WATCH, "process.on('uncaughtException', (error) => {", (16,)),
    (APP, "'main-process uncaught exception(s):\\n'", (59,)),
    (PKG, '"dev": "electron-vite dev",', (16,)),
    (PKG, '"preview": "electron-vite preview",', (18,)),
    (INBOX, "expect(stderr).not.toMatch(/UnhandledPromiseRejectionWarning: Error: backend not ready/)", (403,)),
)
ISSUES_OPEN = (
    "PY-SUITE-5S-WAIT-FLAKE-UNDER-LOAD",
    "E2E-MAIN-PROCESS-REJECTIONS-UNWATCHED",
    "UI-DEV-ELECTRON-RUN-AS-NODE-SILENT",
)
ISSUE_ABSENT = "UI-PREVIEW-ELECTRON-RUN-AS-NODE-SILENT"
GROUPING_ROW = "| 90 | `test-run-reliability` | \u2014 | P3 | proposed | \u2014 |"
SCOPE_PREFIXES = (
    PLAN.as_posix() + "/",
    ".agent/context/handoffs/2026-11-17-test-run-reliability-",
    "docs/execution/reflections/2026-11-17-test-run-reliability-",
)
SKIP_ROOTS = ("packages", "mcp-server", "tools")
SECRET_BASES = (".mcp.json", "mcp-token.txt", ".claude.json", ".env")
problems = []


def secret(name):
    parts = name.split("/")
    base = parts[-1]
    return (
        base in SECRET_BASES
        or base.startswith(".env.")
        or (len(parts) >= 2 and parts[-2] == ".claude" and base == "settings.local.json")
        or name.startswith(".agent/fleet/hub/")
    )


def git(*args):
    return subprocess.run(["git", *args], capture_output=True, check=True).stdout


def sha(path):
    p = pathlib.Path(path)
    if p.is_file():
        return hashlib.sha256(p.read_bytes()).hexdigest()
    return "absent" if not p.exists() else "not-a-file"


def eol(raw):
    crlf = raw.count(b"\r\n")
    bare = raw.count(b"\n") - crlf
    if crlf and bare:
        return "MIXED", crlf, bare
    return ("CRLF" if crlf else ("LF" if bare else "none")), crlf, bare


head = git("rev-parse", "HEAD").decode().strip()
(PLAN / "baseline.sha").write_bytes((head + "\n").encode())
print("baseline.sha", head)
if head != "79e3fa58501db96e5cce4796c5146963a00748c2":
    problems.append(f"S2: HEAD is {head}, not the brief's 79e3fa5")
origin = subprocess.run(["git", "rev-parse", "origin/main"], capture_output=True).stdout.decode().strip()
print("origin/main as found", origin or "<none>")
porcelain = git("status", "--porcelain", "--untracked-files=all").decode("utf-8")
(PLAN / "baseline-dirty.txt").write_bytes(porcelain.encode("utf-8"))
dirty = [line[3:].strip().strip('"') for line in porcelain.splitlines() if line.strip()]
print("baseline-dirty.txt", len(dirty), "paths")
for p in dirty:
    print("  dirty", p)

KINDS = {**MODIFIED, **NEW}
scope = {p: sha(p) for p in (*KINDS, *READ_ONLY)}
for p in NEW:
    if scope[p] != "absent":
        problems.append(f"S2: new file already exists: {p}")
if sha(HANDOFF) != "absent":
    problems.append(f"S2: the handoff already exists: {HANDOFF}")
for p in (*MODIFIED, *READ_ONLY):
    if scope[p] in ("absent", "not-a-file"):
        problems.append(f"S2: scoped path missing: {p}")
(PLAN / "baseline-scope.json").write_bytes((json.dumps(scope, indent=2) + "\n").encode())
print("baseline-scope.json", len(scope), "paths;", sum(v == "absent" for v in scope.values()), "absent")
procs_sha = scope["docs/execution/plans/2026-11-15-convert-settings-drafts/dev-app-procs.py"]
print("dev-app-procs.py", procs_sha[:12])
if not procs_sha.startswith("03053bc97a32"):
    problems.append(f"S2: dev-app-procs.py sha256 {procs_sha[:12]}, not the plan's 03053bc97a32")


def in_scope(p):
    return p in scope or p in SHARED or p.startswith(SCOPE_PREFIXES)


hashes = {p: (sha(p) if pathlib.Path(p).exists() else "deleted") for p in dirty if not in_scope(p) and not secret(p)}
(PLAN / "baseline-dirty-hashes.json").write_bytes((json.dumps(hashes, indent=2, sort_keys=True) + "\n").encode())
print("baseline-dirty-hashes.json", len(hashes), "paths outside this scope")
for p in sorted(hashes):
    print("  bound by hash", p, hashes[p][:16])
for p in SHARED:
    print("bound by content (read first, own lines only)", p, "dirty" if p in dirty else "clean at HEAD", sha(p)[:16])

# The row-0 content of every existing scoped, read-only, shared and plan file: wait-check.py's,
# eol-check.py's and AC-12's base, and the execution review's delta base.
copied = 0
for p in (*KINDS, *READ_ONLY, *SHARED, *PLAN_FILES):
    if not pathlib.Path(p).is_file():
        continue
    dest = COPIES / p
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(pathlib.Path(p).read_bytes())
    copied += 1
print("baseline-copies", copied, "row-0 copies under", COPIES.as_posix())

# baseline-skip-hashes.json (H1-4): every tracked or untracked, not-ignored file under packages/,
# mcp-server/ and tools/, secret names dropped before any stat or read.
listed = git("ls-files", "--cached", "--others", "--exclude-standard", *SKIP_ROOTS)
skip_paths = [n for n in listed.decode("utf-8").splitlines() if n and not secret(n)]
skips = {p: sha(p) for p in skip_paths if pathlib.Path(p).is_file()}
(PLAN / "baseline-skip-hashes.json").write_bytes((json.dumps(skips, indent=2, sort_keys=True) + "\n").encode())
print("baseline-skip-hashes.json", len(skips), "files under packages/, mcp-server/ and tools/")

# Line endings, measured with Python bytes.
eols = {}
for p, want in {**KINDS, **READ_ONLY, **SHARED, **PLAN_FILES}.items():
    if not pathlib.Path(p).is_file():
        eols[p] = {"kind": "absent", "expected": want, "crlf": 0, "bare_lf": 0}
        print("eol absent", p)
        continue
    raw = pathlib.Path(p).read_bytes()
    kind, crlf, bare = eol(raw)
    eols[p] = {"kind": kind, "expected": want, "crlf": crlf, "bare_lf": bare, "bom": raw.startswith(b"\xef\xbb\xbf")}
    print("eol", kind, "crlf", crlf, "bare_lf", bare, "bom", eols[p]["bom"], p)
    if want is not None and kind != want and p not in NEW:
        problems.append(f"S2: {p} is {kind}, the plan says {want}")
(PLAN / "baseline-eol.json").write_bytes((json.dumps(eols, indent=2) + "\n").encode())
print("baseline-eol.json", len(eols), "paths")

# S2: the anchors, the watch, the registers, the grouping row, graphify, the approved plan.
for p, needle, want_lines in ANCHORS:
    lines = pathlib.Path(p).read_bytes().decode("utf-8").split("\n")
    at = tuple(i + 1 for i, ln in enumerate(lines) if needle in ln)
    print("anchor", p, "::", repr(needle), "->", len(at), "at", list(at))
    if at != want_lines:
        problems.append(f"S2: anchor {needle!r} in {p} at {list(at)}, the probe says {list(want_lines)}")
watch_text = pathlib.Path(WATCH).read_bytes().decode("utf-8")
n = watch_text.count("unhandledRejection")
print("watch unhandledRejection count", n)
if n:
    problems.append("S2: unhandledRejection is already in the watch")
register = pathlib.Path(REGISTER).read_bytes().decode("utf-8")
for issue in ISSUES_OPEN:
    m = re.search(r"^  - id: " + issue + r"\n(?:    .*\n)*?    status: (\S+)", register, re.M)
    state = m.group(1) if m else None
    print("issue", issue, "status", state)
    if state != "open":
        problems.append(f"S2: {issue} is {state}, not open")
k = register.count("id: " + ISSUE_ABSENT)
print("issue", ISSUE_ABSENT, "entries", k)
if k:
    problems.append(f"S2: {ISSUE_ABSENT} is already registered")
row = [ln for ln in pathlib.Path(GROUPING).read_bytes().decode("utf-8").split("\n") if ln.startswith("| 90 |")]
print("grouping row 90", row)
if row != [GROUPING_ROW]:
    problems.append("S2: grouping row 90 is not the one proposed row")
graphs = [g for g in ("graphify-out", "graphify-out-research") if pathlib.Path(g).exists()]
print("graphify graphs", graphs)
if graphs:
    problems.append(f"S1: a graphify graph exists: {graphs}")
for p, want in PLAN_SHA.items():
    got = sha(p)
    print("approved", p, got)
    if got != want:
        problems.append(f"S2: {p} sha256 {got}, not the approved {want}")
print("plan review", PLAN_REVIEW, sha(PLAN_REVIEW))
for p in PLAN_FILES:
    print("plan file", p, sha(p)[:16])
    if not pathlib.Path(p).is_file():
        problems.append(f"row 0: {p} is missing")
for p in problems:
    print("PROBLEM:", p)
sys.exit(1 if problems else 0)
'@
New-Item -ItemType Directory -Force -Path $receipts | Out-Null
Set-Content -Path "$receipts/baseline-record.py" -Value $record -Encoding utf8
Invoke-Step 'uv-sync' @('uv', 'sync', '--frozen', '--all-packages')
Invoke-Step 'record' @('uv', 'run', '--no-sync', 'python', "$receipts/baseline-record.py")

# 3. The host-load wait (Session 81 RULE-2), imported from load-run.py as the gate's host-load
# step and dev-proof.py do. It never fails the row; it records the load it ran at.
$hostLoad = @'
import importlib.util
spec = importlib.util.spec_from_file_location(
    "load_run", "docs/execution/plans/2026-11-17-test-run-reliability/load-run.py"
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
mod.host_load_wait()
'@
Set-Content -Path "$receipts/baseline-host-load.py" -Value $hostLoad -Encoding utf8
Invoke-Step 'host-load' @('uv', 'run', '--no-sync', 'python', "$receipts/baseline-host-load.py")

# The base Vitest suite from pwsh in ui/ (memory: vitest-from-pwsh-not-bash); the gate's
# ui-tests excuse list reads it. Its failures are recorded, not fatal.
Push-Location 'P:\av-kit\ui'
& rtk proxy npm run test *> "$receipts/trr-base-ui.txt"
$uiCode = $LASTEXITCODE
Pop-Location
Write-Output ("base suite ui exit={0} receipt={1}/trr-base-ui.txt" -f $uiCode, $receipts)
Get-Content "$receipts/trr-base-ui.txt" | Select-String -Pattern 'Test Files|Tests |FAIL ' | Select-Object -Last 12

# The full Python suite with the D6 argv (.agent/docs/commands.md, py-tests) without -x, so
# every base failure is recorded; the gate excuses only those ids. Not fatal.
& rtk proxy uv run --no-sync pytest tests/ --tb=short -q *> "$receipts/trr-base-py.txt"
$pyCode = $LASTEXITCODE
Write-Output ("base suite py exit={0} receipt={1}/trr-base-py.txt" -f $pyCode, $receipts)
Get-Content "$receipts/trr-base-py.txt" | Select-String -Pattern '^FAILED |^ERROR | in [0-9.]+s' | Select-Object -Last 20

# The timed plain run of the three TIME_GUARD files, through the same wrapper row 2 uses for
# trr-green-two.txt; wall_s is its last line. It must pass.
$two = @'
import subprocess, sys, time
t = time.monotonic()
r = subprocess.run([sys.executable, "-m", "pytest", "-q", "--tb=short", "-p", "no:cacheprovider",
                    "tests/integration/test_tts_assets.py", "tests/integration/test_youtube_adapter.py",
                    "tests/integration/test_tts_voice_packs.py"])
sys.stdout.flush()
print("wall_s:", round(time.monotonic() - t, 1))
sys.exit(r.returncode)
'@
Set-Content -Path "$receipts/baseline-two.py" -Value $two -Encoding utf8
& rtk proxy uv run --no-sync python "$receipts/baseline-two.py" *> "$receipts/trr-base-two.txt"
$twoCode = $LASTEXITCODE
Write-Output ("baseline step base-two exit={0} receipt={1}/trr-base-two.txt" -f $twoCode, $receipts)
Get-Content "$receipts/trr-base-two.txt" -Tail 3
if ($twoCode -ne 0) { exit $twoCode }

# 4. The plan-local checkers (Session 82 RULE-1 on the plan folder's Python).
$planPy = @(Get-ChildItem -Path $plan -Filter '*.py' | ForEach-Object { "$plan/$($_.Name)" })
Invoke-Step 'ruff-format-plan' (@('uv', 'run', '--no-sync', 'ruff', 'format', '--check') + $planPy)
Invoke-Step 'ruff-check-plan' (@('uv', 'run', '--no-sync', 'ruff', 'check') + $planPy)
Invoke-Step 'red-check-selftest' @('uv', 'run', '--no-sync', 'python', "$plan/red-check.py", '--selftest')
Invoke-Step 'identity-selftest' @('uv', 'run', '--no-sync', 'python', "$plan/identity.py", '--selftest')
Invoke-Step 'eol-check-selftest' @('uv', 'run', '--no-sync', 'python', "$plan/eol-check.py", '--selftest')
Invoke-Step 'wait-check-selftest' @('uv', 'run', '--no-sync', 'python', "$plan/wait-check.py", '--selftest')
Invoke-Step 'load-run-selftest' @('uv', 'run', '--no-sync', 'python', "$plan/load-run.py", '--selftest')
Invoke-Step 'dev-proof-selftest' @('uv', 'run', '--no-sync', 'python', "$plan/dev-proof.py", '--selftest')
Invoke-Step 'eol-check-row0' @('uv', 'run', '--no-sync', 'python', "$plan/eol-check.py")
Write-Output 'baseline: all steps exit 0'
exit 0
