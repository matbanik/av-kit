# Triage tool fixes baseline (task row 0; implementation-plan.md §Verification Plan 1).
# The shape of docs/execution/plans/2026-11-15-framework-small-syncs/baseline.ps1, with this plan's steps:
# 1. the tree state (baseline.sha, baseline-dirty.txt); 2. the path-scoped baseline
# (baseline-scope.json with the new test file absent, baseline-dirty-hashes.json, the BASE copies
# of every existing file in C:/Temp/av-kit/triage-tool-fixes/base/); 3. the bindings (S2): each of
# the four code files equals HEAD, and every doc-check.py anchor occurs exactly once in its BASE
# copy; 4. uv sync and the base Python suite (ttf-base-py.txt; its own failures are recorded, not
# fatal: the session gate excuses only the ids this receipt shows failing), and the four tools
# files' existing ruff findings (ttf-ruff-base.txt, not fatal); 5. the three plan-local
# selftests (issue-resolve.py has none; row 11 runs it bound to the row-0 register hash). Every other step is fail-fast. Run from the repository root.
$ErrorActionPreference = 'Stop'
$root = (git rev-parse --show-toplevel).Trim()
Set-Location $root
$plan = 'docs/execution/plans/2026-11-15-triage-tool-fixes'
$receipts = 'C:/Temp/av-kit/triage-tool-fixes'
$env:ELECTRON_RUN_AS_NODE = $null
$env:PYTHONIOENCODING = 'utf-8'
$env:RECEIPTS_DIR = 'C:/Temp/av-kit'
$env:AGENT_MODEL_REGISTRY_HOME = 'P:/.agent'
$userTmp = $env:TMP
$userTemp = $env:TEMP
$tmp = 'C:\Temp\av-kit\triage-tool-fixes\tmp'
New-Item -ItemType Directory -Force -Path $tmp | Out-Null

function Invoke-Step([string]$Id, [string[]]$Argv) {
    & rtk proxy @Argv
    $code = $LASTEXITCODE
    Write-Output ("baseline step {0} exit={1}" -f $Id, $code)
    if ($code -ne 0) { exit $code }
}

# 1-3. Tree state, path-scoped baseline and the bindings, in Python so every file is read and
# written as bytes.
$record = @'
import hashlib, importlib.util, json, pathlib, subprocess, sys

PLAN = pathlib.Path("docs/execution/plans/2026-11-15-triage-tool-fixes")
BASE = pathlib.Path("C:/Temp/av-kit/triage-tool-fixes/base")
CODE = (
    "tools/issue_triage.py",
    "tools/issue_triage/verify.py",
    "tools/issue_triage/discover.py",
    "tools/issue_triage/triage.py",
)
DOCS = (
    ".agent/workflows/issue-triage.md",
    ".agent/skills/issue-triage/SKILL.md",
    ".agent/docs/issue-lifecycle-guide.md",
    ".agent/docs/commands.md",
    ".agent/docs/cloud-local-collaboration.md",
)
REGISTERS = (
    ".agent/context/known-issues.yaml",
    ".agent/context/known-issues.md",
    ".agent/context/grouping/2026-11-15-post-rc3-triage-residuals-session-grouping.md",
)
EXISTING = CODE + DOCS + REGISTERS
NEW = ("tests/unit/test_issue_triage.py",)
SCOPE_PREFIXES = (
    PLAN.as_posix() + "/",
    ".agent/context/handoffs/2026-11-15-triage-tool-fixes-",
    "docs/execution/reflections/2026-11-15-triage-tool-fixes-",
)
SHARED = ("docs/execution/metrics.md", ".agent/context/current-focus.md")
problems = []

def git(*args):
    return subprocess.run(["git", *args], capture_output=True, check=True).stdout

def sha(path):
    p = pathlib.Path(path)
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else ("absent" if not p.exists() else "not-a-file")

def eol(path):
    b = pathlib.Path(path).read_bytes()
    crlf, lf = b.count(b"\r\n"), b.count(b"\n")
    return "CRLF" if crlf and crlf == lf else ("LF" if crlf == 0 else "mixed")

head = git("rev-parse", "HEAD").decode().strip()
(PLAN / "baseline.sha").write_bytes((head + "\n").encode())
print("baseline.sha", head)
porcelain = git("status", "--porcelain", "--untracked-files=all").decode("utf-8")
(PLAN / "baseline-dirty.txt").write_bytes(porcelain.encode("utf-8"))
dirty = [line[3:].strip().strip('"') for line in porcelain.splitlines() if line.strip()]
print("baseline-dirty.txt", len(dirty), "paths")

scope = {p: sha(p) for p in EXISTING + NEW}
for p in NEW:
    if scope[p] != "absent":
        problems.append(f"new path already exists: {p}")
for p in EXISTING:
    if scope[p] in ("absent", "not-a-file"):
        problems.append(f"existing path missing: {p}")
(PLAN / "baseline-scope.json").write_bytes((json.dumps(scope, indent=2) + "\n").encode())
print("baseline-scope.json", len(scope), "paths;", sum(v == "absent" for v in scope.values()), "absent")
if problems:
    for p in problems:
        print("PROBLEM:", p)
    sys.exit(1)

HEAD_PLANS = {n for n in git("ls-tree", "--name-only", "HEAD", "docs/execution/plans/").decode().splitlines() if n}

def other_plan(p):
    # A new plan folder another session's planner writes (coordinator, 2026-11-15; identity.py
    # OTHER_PLAN_PREFIX): not this scope, and not bound by hash either.
    folder = "/".join(p.split("/")[:4])
    return p.startswith("docs/execution/plans/2026-11-15-") and folder != p and folder not in HEAD_PLANS

def in_scope(p):
    return p in scope or p in SHARED or p.startswith(SCOPE_PREFIXES) or other_plan(p)

hashes = {p: (sha(p) if pathlib.Path(p).exists() else "deleted") for p in dirty if not in_scope(p)}
(PLAN / "baseline-dirty-hashes.json").write_bytes((json.dumps(hashes, indent=2, sort_keys=True) + "\n").encode())
print("baseline-dirty-hashes.json", len(hashes), "paths outside this scope")
for p in SHARED:
    print("shared", p, "dirty" if p in dirty else "clean at HEAD", sha(p))

for p in EXISTING:
    dest = BASE / p
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(pathlib.Path(p).read_bytes())
    print("BASE", p, eol(p), "sha256", sha(dest))

# S2: the code this plan edits is HEAD's code.
for p in CODE:
    # D-1040 (Session 79 row 0): system core.autocrlf=true makes --filters emit CRLF for an LF
    # blob, so the working bytes may equal the raw blob or the filtered one; git diff decides.
    work = pathlib.Path(p).read_bytes()
    same_bytes = work in (git("cat-file", "blob", f"HEAD:{p}"), git("cat-file", "--filters", f"HEAD:{p}"))
    if not same_bytes or subprocess.run(["git", "diff", "--quiet", "HEAD", "--", p]).returncode != 0:
        problems.append(f"S2: {p} differs from HEAD")
    else:
        print("S2", p, "equals HEAD")
# S2: every doc-check.py anchor occurs exactly once in its BASE copy (a doc that an earlier
# session changed is fine while the anchors hold).
spec = importlib.util.spec_from_file_location("doc_check", PLAN / "doc-check.py")
dc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dc)
for rel in dc.DOCS:
    try:
        dc.apply(rel, (BASE / rel).read_bytes())
        print("S2 anchors", rel, "each found once")
    except dc.AnchorError as exc:
        problems.append(f"S2: {exc}")
for p in problems:
    print("PROBLEM:", p)
sys.exit(1 if problems else 0)
'@
Set-Content -Path "$receipts/baseline-record.py" -Value $record -Encoding utf8
Invoke-Step 'record' @('uv', 'run', 'python', "$receipts/baseline-record.py")

# 4. Install from the lock; the base Python suite with TMP and TEMP outside the user profile.
Invoke-Step 'uv-sync' @('uv', 'sync', '--frozen', '--all-packages')
$env:TMP = $tmp
$env:TEMP = $tmp
& rtk proxy uv run pytest tests/ --tb=short -q -rfE *> "$receipts/ttf-base-py.txt"
Write-Output ("base suite py exit={0} receipt={1}/ttf-base-py.txt" -f $LASTEXITCODE, $receipts)
Get-Content "$receipts/ttf-base-py.txt" | Select-String -Pattern '^FAILED |^ERROR |passed|failed' | Select-Object -Last 12
$env:TMP = $userTmp
$env:TEMP = $userTemp

# 4b. The four tools files' existing ruff findings (3 at plan time; recorded, not fatal). The gate's
# tools-lint step allows no (path, code) pair that this receipt lacks.
& rtk proxy uv run --no-sync ruff check --output-format concise tools/issue_triage.py tools/issue_triage/verify.py tools/issue_triage/discover.py tools/issue_triage/triage.py *> "$receipts/ttf-ruff-base.txt"
Write-Output ("tools ruff base exit={0} receipt={1}/ttf-ruff-base.txt" -f $LASTEXITCODE, $receipts)

# 5. The plan-local checkers (red-check.py and identity.py copied from
# 2026-11-15-framework-small-syncs with this plan's PLAN; doc-check.py written for this plan).
Invoke-Step 'red-check-selftest' @('uv', 'run', 'python', "$plan/red-check.py", '--selftest')
Invoke-Step 'identity-selftest' @('uv', 'run', 'python', "$plan/identity.py", '--selftest')
Invoke-Step 'doc-check-selftest' @('uv', 'run', 'python', "$plan/doc-check.py", '--selftest')
Write-Output 'baseline: all steps exit 0'
exit 0
