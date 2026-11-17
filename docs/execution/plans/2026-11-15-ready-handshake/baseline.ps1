# Ready handshake baseline (task row 0; implementation-plan.md §Verification Plan 1).
# The shape of docs/execution/plans/2026-11-15-convert-settings-drafts/baseline.ps1 (itself from
# the framework-small-syncs one), with this plan's steps: 1. the tree state (baseline.sha,
# baseline-dirty.txt); 2. the path-scoped baseline (baseline-scope.json over §Files Modified, with
# the two new Vitest files absent; baseline-dirty-hashes.json, which binds every dirty path outside
# this scope by hash, Session 83's untracked plan folder and plan review included; the row-0
# copies and baseline-eol.json; baseline-packaged.json, read-only); the S2 binding: cli.py,
# python-manager.ts, index.ts and the two existing test files equal HEAD (Session 79 RULE-1: the raw
# or the filtered blob, and `git diff --quiet HEAD`), the diff of 04 and 06 against HEAD is printed
# and their home sections are unchanged, neither holds a Session 82 note, both issues are open,
# MEU-153 and MEU-154 pending, grouping row 82 proposed, no graphify graph; 3. uv sync, the base
# Python suite (rh-base-py.txt), the base Vitest suite (rh-base-ui.txt) and the Session 77 RULE-3
# base checks (ruff format --check, ui-lint); their own failures are recorded, not fatal; 4. the
# plan-local selftests. red-check.py, identity.py and issue-resolve.py are written before this runs
# (C:/Temp/av-kit/ready-handshake/make-copies.py); this script requires them. Every other step is
# fail-fast. Run from the repository root in pwsh.
$ErrorActionPreference = 'Stop'
$root = (git rev-parse --show-toplevel).Trim()
Set-Location $root
$plan = 'docs/execution/plans/2026-11-15-ready-handshake'
$receipts = 'C:/Temp/av-kit/ready-handshake'
$env:ELECTRON_RUN_AS_NODE = $null
$env:PYTHONIOENCODING = 'utf-8'
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:RECEIPTS_DIR = 'C:/Temp/av-kit'
$userTmp = $env:TMP
$userTemp = $env:TEMP
$tmp = 'C:\Temp\av-kit\ready-handshake\tmp'
New-Item -ItemType Directory -Force -Path $tmp | Out-Null

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

PLAN = pathlib.Path("docs/execution/plans/2026-11-15-ready-handshake")
OUT = pathlib.Path("C:/Temp/av-kit/ready-handshake")
COPIES = OUT / "baseline-copies"
CLI = "packages/api/src/avkit_api/cli.py"
CLI_TEST = "tests/unit/test_backend_cli.py"
SPAWN_TEST = "tests/integration/test_backend_spawn.py"
PM = "ui/src/main/python-manager.ts"
INDEX = "ui/src/main/index.ts"
API_DOC = "docs/build-plan/04-rest-api.md"
GUI_DOC = "docs/build-plan/06-gui.md"
GROUPING = ".agent/context/grouping/2026-11-15-post-rc3-triage-residuals-session-grouping.md"
PACKAGED = "packaging/dist/avkit-backend/avkit-backend.exe"
# §Files Modified, with each file's line-ending kind.
MODIFIED = {
    CLI: "LF",
    CLI_TEST: "CRLF",
    SPAWN_TEST: "LF",
    PM: "LF",
    INDEX: "CRLF",
    API_DOC: "CRLF",
    GUI_DOC: "CRLF",
    ".agent/context/known-issues.yaml": "LF",
    ".agent/context/known-issues.md": "LF",
    ".agent/context/meu-status.yaml": "LF",
    ".agent/context/meu-registry.md": "LF",
    "docs/BUILD_PLAN.md": "LF",
    GROUPING: "LF",
}
NEW = {
    "ui/tests/unit/ready-line-buffer.test.ts": "LF",
    "ui/tests/unit/ready-line-pipe.test.ts": "LF",
}
# The AC-154.9 pins, read and never changed; their kind is recorded, not expected.
PINS = ("ui/tests/unit/ready-probe-guard.test.ts", "ui/tests/e2e/backend-output-after-close.test.ts")
# The plan's own files (row 0 re-measures them; all LF).
PLAN_FILES = {
    f"{PLAN.as_posix()}/{n}": "LF"
    for n in ("implementation-plan.md", "task.md", "gap-tally.py", "ready-gap-probe.mjs", "red-check.py", "identity.py", "issue-resolve.py", "baseline.ps1")
}
KINDS = {**MODIFIED, **NEW}
HEAD_EQUAL = (CLI, CLI_TEST, SPAWN_TEST, PM, INDEX)
HOME = {API_DOC: "## READY after listen (residual)", GUI_DOC: "### READY line buffering (residual)"}
SCOPE_PREFIXES = (
    PLAN.as_posix() + "/",
    ".agent/context/handoffs/2026-11-15-ready-handshake-",
    "docs/execution/reflections/2026-11-15-ready-handshake-",
)
SHARED = ("docs/execution/metrics.md", ".agent/context/current-focus.md")
ISSUES = ("BACKEND-READY-BEFORE-LISTEN", "GUI-READY-CHUNK-BOUNDARY")
MEUS = ("MEU-153", "MEU-154")
problems = []

def git(*args):
    return subprocess.run(["git", *args], capture_output=True, check=True).stdout

def sha(path):
    p = pathlib.Path(path)
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else ("absent" if not p.exists() else "not-a-file")

def eol(raw):
    crlf = raw.count(b"\r\n")
    bare = raw.count(b"\n") - crlf
    kind = "CRLF" if crlf and not bare else ("LF" if bare and not crlf else ("MIXED" if crlf and bare else "none"))
    return kind, crlf, bare

head = git("rev-parse", "HEAD").decode().strip()
(PLAN / "baseline.sha").write_bytes((head + "\n").encode())
print("baseline.sha", head)
origin = subprocess.run(["git", "rev-parse", "origin/main"], capture_output=True).stdout.decode().strip()
print("origin/main as found", origin or "<none>")
porcelain = git("status", "--porcelain", "--untracked-files=all").decode("utf-8")
(PLAN / "baseline-dirty.txt").write_bytes(porcelain.encode("utf-8"))
dirty = [line[3:].strip().strip('"') for line in porcelain.splitlines() if line.strip()]
print("baseline-dirty.txt", len(dirty), "paths")
for p in dirty:
    print("  dirty", p)

scope = {p: sha(p) for p in KINDS}
for p in NEW:
    if scope[p] != "absent":
        problems.append(f"S2: new test file already exists: {p}")
for p in MODIFIED:
    if scope[p] in ("absent", "not-a-file"):
        problems.append(f"S2: scoped path missing: {p}")
(PLAN / "baseline-scope.json").write_bytes((json.dumps(scope, indent=2) + "\n").encode())
print("baseline-scope.json", len(scope), "paths;", sum(v == "absent" for v in scope.values()), "absent")

def in_scope(p):
    # Unlike the convert-settings-drafts copy, another session's new plan folder is not excused:
    # the start prompt binds Session 83's untracked folder and plan review by hash here.
    return p in scope or p in SHARED or p.startswith(SCOPE_PREFIXES)

hashes = {p: (sha(p) if pathlib.Path(p).exists() else "deleted") for p in dirty if not in_scope(p)}
(PLAN / "baseline-dirty-hashes.json").write_bytes((json.dumps(hashes, indent=2, sort_keys=True) + "\n").encode())
print("baseline-dirty-hashes.json", len(hashes), "paths outside this scope")
for p in sorted(hashes):
    print("  bound by hash", p, hashes[p][:16])
for p in SHARED:
    print("bound by content (read first, own lines only)", p, "dirty" if p in dirty else "clean at HEAD", sha(p)[:16])

# The row-0 content of every existing scoped file and pin: the execution review's delta base.
copied = 0
for p in (*KINDS, *PINS):
    if not pathlib.Path(p).is_file():
        continue
    dest = COPIES / p
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(pathlib.Path(p).read_bytes())
    copied += 1
print("baseline-copies", copied, "row-0 copies under", COPIES.as_posix())

# S2, Session 79 RULE-1: working bytes equal HEAD's raw or filtered blob, and git diff is quiet.
def head_state(p):
    work = pathlib.Path(p).read_bytes()
    raw = git("show", f"HEAD:{p}")
    filt = git("cat-file", "--filters", f"HEAD:{p}")
    quiet = subprocess.run(["git", "diff", "--quiet", "HEAD", "--", p]).returncode == 0
    return work in (raw, filt), quiet, raw, filt

for p in HEAD_EQUAL:
    same, quiet, _, _ = head_state(p)
    print("head-equal", p, "bytes", same, "diff-quiet", quiet)
    if not (same and quiet):
        problems.append(f"S2: {p} differs from HEAD")

def section(text, heading):
    lines = text.replace("\r\n", "\n").split("\n")
    level = len(heading) - len(heading.lstrip("#"))
    starts = [i for i, ln in enumerate(lines) if ln == heading]
    if len(starts) != 1:
        return None
    out = []
    for ln in lines[starts[0] + 1:]:
        m = re.match(r"^(#+) ", ln)
        if m and len(m.group(1)) <= level:
            break
        out.append(ln)
    return "\n".join(out)

for p, heading in HOME.items():
    same, quiet, raw, filt = head_state(p)
    diff = git("diff", "HEAD", "--", p).decode("utf-8", "replace")
    print("doc", p, "bytes equal HEAD", same, "diff-quiet", quiet, "diff bytes", len(diff))
    if diff:
        print(diff)
    work_sec = section(pathlib.Path(p).read_bytes().decode("utf-8"), heading)
    head_secs = {section(b.decode("utf-8"), heading) for b in (raw, filt)}
    print("home section", p, repr(heading), "found" if work_sec is not None else "MISSING", "unchanged" if work_sec in head_secs else "CHANGED")
    if work_sec is None or work_sec not in head_secs:
        problems.append(f"S2: the home section {heading!r} in {p} is missing or changed since HEAD")
    n = pathlib.Path(p).read_bytes().count(b"Delivered (Session 82)")
    print("home", p, "Delivered (Session 82) notes:", n)
    if n:
        problems.append(f"S2: {p} already holds a Session 82 Delivered note")

# Line endings, measured with Python bytes.
eols = {}
for p, want in {**KINDS, **{q: None for q in PINS}, **PLAN_FILES}.items():
    if not pathlib.Path(p).is_file():
        eols[p] = {"kind": "absent", "expected": want, "crlf": 0, "bare_lf": 0}
        print("eol absent", p)
        continue
    raw = pathlib.Path(p).read_bytes()
    kind, crlf, bare = eol(raw)
    eols[p] = {"kind": kind, "expected": want, "crlf": crlf, "bare_lf": bare, "bom": raw.startswith(b"\xef\xbb\xbf")}
    print("eol", kind, "crlf", crlf, "bare_lf", bare, "bom", eols[p]["bom"], p)
    if want is not None and kind != want:
        problems.append(f"S2: {p} is {kind}, the plan says {want}")
(PLAN / "baseline-eol.json").write_bytes((json.dumps(eols, indent=2) + "\n").encode())
print("baseline-eol.json", len(eols), "paths")

# The packaged exe, read-only: path, sha256 or absent, size, mtime.
exe = pathlib.Path(PACKAGED)
if exe.is_file():
    st = exe.stat()
    packaged = {"path": PACKAGED, "sha256": sha(PACKAGED), "size": st.st_size, "mtime": st.st_mtime}
else:
    packaged = {"path": PACKAGED, "sha256": "absent", "size": None, "mtime": None}
(PLAN / "baseline-packaged.json").write_bytes((json.dumps(packaged, indent=2) + "\n").encode())
print("baseline-packaged.json", packaged)

register = pathlib.Path(".agent/context/known-issues.yaml").read_bytes().decode("utf-8")
for issue in ISSUES:
    m = re.search(r"^  - id: " + re.escape(issue) + r"\n(?:    .*\n)*?    status: (\S+)", register, re.M)
    state = m.group(1) if m else None
    print("issue", issue, "status", state)
    if state != "open":
        problems.append(f"S2: {issue} is {state}, not open")
status = pathlib.Path(".agent/context/meu-status.yaml").read_bytes().decode("utf-8")
for meu in MEUS:
    m = re.search(r"^- row_key: " + meu + r"\n(?:  .*\n)*?  status: (\S+)", status, re.M)
    state = m.group(1) if m else None
    print("meu", meu, "status", state)
    if state != "pending":
        problems.append(f"S2: {meu} is {state}, not pending")
row = [ln for ln in pathlib.Path(GROUPING).read_bytes().decode("utf-8").split("\n") if ln.startswith("| 82 |")]
print("grouping row 82", row)
if len(row) != 1 or "| proposed |" not in row[0]:
    problems.append("S2: grouping §6 row 82 is not one proposed row")
graphs = [g for g in ("graphify-out", "graphify-out-research") if pathlib.Path(g).exists()]
print("graphify graphs", graphs)
if graphs:
    problems.append(f"S1: a graphify graph exists: {graphs}")
for n in ("red-check.py", "identity.py", "issue-resolve.py", "gap-tally.py"):
    p = PLAN / n
    print("plan script", p.as_posix(), sha(p)[:16])
    if not p.is_file():
        problems.append(f"row 0: {p.as_posix()} is missing")
for p in problems:
    print("PROBLEM:", p)
sys.exit(1 if problems else 0)
'@
New-Item -ItemType Directory -Force -Path $receipts | Out-Null
Set-Content -Path "$receipts/baseline-record.py" -Value $record -Encoding utf8
Invoke-Step 'record' @('uv', 'run', '--no-sync', 'python', "$receipts/baseline-record.py")

# 3. Install from the lock; the base suites with TMP and TEMP outside the user profile.
Invoke-Step 'uv-sync' @('uv', 'sync', '--frozen', '--all-packages')
$env:TMP = $tmp
$env:TEMP = $tmp
& rtk proxy uv run --no-sync pytest tests/ --tb=short -q -rfE *> "$receipts/rh-base-py.txt"
Write-Output ("base suite py exit={0} receipt={1}/rh-base-py.txt" -f $LASTEXITCODE, $receipts)
Get-Content "$receipts/rh-base-py.txt" | Select-String -Pattern '^FAILED |^ERROR |passed|failed' | Select-Object -Last 12
$env:TMP = $userTmp
$env:TEMP = $userTemp
# Vitest from pwsh in ui/ (memory: vitest-from-pwsh-not-bash); the gate's ui-tests excuse list reads it.
Push-Location 'P:\av-kit\ui'
& rtk proxy npm run test *> "$receipts/rh-base-ui.txt"
$uiCode = $LASTEXITCODE
Pop-Location
Write-Output ("base suite ui exit={0} receipt={1}/rh-base-ui.txt" -f $uiCode, $receipts)
Get-Content "$receipts/rh-base-ui.txt" | Select-String -Pattern 'Test Files|Tests ' | Select-Object -Last 4
# Session 77 RULE-3: the base tree's format and lint findings, recorded before any edit.
& rtk proxy uv run --no-sync ruff format --check packages/api/src/avkit_api/cli.py tests/unit/test_backend_cli.py tests/integration/test_backend_spawn.py "$plan/gap-tally.py" *> "$receipts/rh-base-ruff-format.txt"
Write-Output ("base ruff format --check exit={0} receipt={1}/rh-base-ruff-format.txt" -f $LASTEXITCODE, $receipts)
Get-Content "$receipts/rh-base-ruff-format.txt" | Select-Object -Last 6
& rtk proxy npm --prefix ui run lint *> "$receipts/rh-base-ui-lint.txt"
Write-Output ("base ui-lint exit={0} receipt={1}/rh-base-ui-lint.txt" -f $LASTEXITCODE, $receipts)
Get-Content "$receipts/rh-base-ui-lint.txt" | Select-Object -Last 6

# 4. The plan-local checkers.
Invoke-Step 'red-check-selftest' @('uv', 'run', '--no-sync', 'python', "$plan/red-check.py", '--selftest')
Invoke-Step 'identity-selftest' @('uv', 'run', '--no-sync', 'python', "$plan/identity.py", '--selftest')
Invoke-Step 'gap-tally-selftest' @('uv', 'run', '--no-sync', 'python', "$plan/gap-tally.py", '--selftest')
Write-Output 'baseline: all steps exit 0'
exit 0
