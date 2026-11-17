# Docs path hygiene baseline (task row 0; implementation-plan.md §Verification Plan 1).
# The shape of docs/execution/plans/2026-11-15-framework-small-syncs/baseline.ps1, with this plan's
# steps: 1. the tree state (baseline.sha, baseline-dirty.txt); 2. the path-scoped baseline
# (baseline-scope.json with the three new files absent, baseline-dirty-hashes.json, the BASE copies
# in C:/Temp/av-kit/dph/base/); 3. line endings by Python bytes against §Live fixes (S5), and the
# plan files measured again; 4. inventory.py --baseline (S2, S7; inventory-0.json); 5. the anchors
# of §Live fixes, §The layout block, §The register and the task-contract row (edit-check.py
# --anchors, S5); 6. uv sync, the base Python suite (dph-base-py.txt; its own failures are
# recorded, not fatal: the session gate excuses only the ids it shows failing), the two vitest
# files (dph-base-ui.txt; a failure is S6) and the full Vitest suite (dph-base-ui-full.txt,
# recorded for the gate's ui-tests excuse list); 7. the plan-local selftests. Every other step is
# fail-fast. Run from the repository root. Nothing here names the home folder.
$ErrorActionPreference = 'Stop'
$root = (git rev-parse --show-toplevel).Trim()
Set-Location $root
$plan = 'docs/execution/plans/2026-11-15-docs-path-hygiene'
$receipts = 'C:/Temp/av-kit/dph'
$env:ELECTRON_RUN_AS_NODE = $null
$env:PYTHONIOENCODING = 'utf-8'
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:RECEIPTS_DIR = 'C:/Temp/av-kit'
$env:AGENT_MODEL_REGISTRY_HOME = 'P:/.agent'
$userTmp = $env:TMP
$userTemp = $env:TEMP
# keep pytest's temp dirs away from the home folder
$tmp = 'C:\Temp\av-kit\dph\tmp'
New-Item -ItemType Directory -Force -Path $tmp | Out-Null
New-Item -ItemType Directory -Force -Path "$receipts/base" | Out-Null

function Invoke-Step([string]$Id, [string[]]$Argv) {
    & rtk proxy @Argv
    $code = $LASTEXITCODE
    Write-Output ("baseline step {0} exit={1}" -f $Id, $code)
    if ($code -ne 0) { exit $code }
}

# 1-3. Tree state, path-scoped baseline and line endings, in Python so every file is read and
# written as bytes.
$record = @'
import hashlib, json, pathlib, subprocess, sys

PLAN = pathlib.Path("docs/execution/plans/2026-11-15-docs-path-hygiene")
BASE = pathlib.Path("C:/Temp/av-kit/dph/base")
EOL = {
    ".agent/skills/git-workflow/SKILL.md": "CRLF",
    "_inspiration/capture-crop/design.md": "LF",
    "docs/build-plan/06-gui.md": "CRLF",
    "docs/build-plan/07-distribution.md": "CRLF",
    "README.md": "LF",
    "ui/tests/unit/capture-interactive.test.ts": "LF",
    "ui/tests/unit/dev-spawn.test.ts": "LF",
    ".agent/context/known-issues.yaml": "LF",
    ".agent/docs/commands.md": "CRLF",
}
EXISTING = tuple(EOL) + (".agent/context/known-issues.md",)
NEW = (
    "tools/check_home_path.py",
    "tools/home_path_allowlist.txt",
    "tests/tooling/test_check_home_path.py",
)
SCOPE_PREFIXES = (
    PLAN.as_posix() + "/",
    ".agent/context/handoffs/2026-11-15-docs-path-hygiene-",
    "docs/execution/reflections/2026-11-15-docs-path-hygiene-",
)
SHARED = ("docs/execution/metrics.md", ".agent/context/current-focus.md")
HUB = ".agent/fleet/hub/"
problems = []


def secret(p):
    # Execution decision D-1081: the secret files are never opened, hashed or copied.
    name = p.rsplit("/", 1)[-1].lower()
    return (
        p.startswith(HUB)
        or name in (".mcp.json", "mcp-token.txt", ".claude.json", ".env")
        or name.startswith(".env.")
        or p.lower().endswith(".claude/settings.local.json")
    )


def git(*args):
    return subprocess.run(["git", *args], capture_output=True, check=True).stdout


def sha(path):
    p = pathlib.Path(path)
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else ("absent" if not p.exists() else "not-a-file")


def eol(raw):
    crlf = raw.count(b"\r\n")
    bare = raw.count(b"\n") - crlf
    lone = raw.count(b"\r") - crlf
    kind = "CRLF" if crlf and not bare and not lone else "LF" if bare and not crlf and not lone else "mixed"
    return kind, crlf, bare, lone


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

HEAD_PLANS = {n for n in git("ls-tree", "--name-only", "HEAD", "docs/execution/plans/").decode().splitlines() if n}


def other_plan(p):
    # A new plan folder another session's planner writes (coordinator, 2026-11-15; identity.py
    # OTHER_PLAN_PREFIX): not this scope, and not bound by hash either.
    folder = "/".join(p.split("/")[:4])
    return p.startswith("docs/execution/plans/2026-11-15-") and folder != p and folder not in HEAD_PLANS


def in_scope(p):
    return p in scope or p in SHARED or p.startswith(SCOPE_PREFIXES) or other_plan(p)


hashes = {}
for p in dirty:
    if in_scope(p):
        continue
    if secret(p):
        hashes[p] = "skipped-secret"
        continue
    hashes[p] = sha(p) if pathlib.Path(p).exists() else "deleted"
(PLAN / "baseline-dirty-hashes.json").write_bytes((json.dumps(hashes, indent=2, sort_keys=True) + "\n").encode())
print("baseline-dirty-hashes.json", len(hashes), "paths outside this scope")
for p in SHARED:
    print("shared", p, "dirty" if p in dirty else "clean at HEAD", sha(p), "eol", eol(pathlib.Path(p).read_bytes())[0])

for p in EXISTING:
    dest = BASE / p
    if dest.exists() and dest.read_bytes() != pathlib.Path(p).read_bytes():
        problems.append(f"a BASE copy from an earlier run differs from the file: {p}")
        continue
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(pathlib.Path(p).read_bytes())
    print("BASE", p, "sha256", sha(dest))

# 3. Line endings by Python bytes (S5).
for p, want in EOL.items():
    kind, crlf, bare, lone = eol(pathlib.Path(p).read_bytes())
    print("eol", kind, "expected", want, "crlf", crlf, "bare_lf", bare, "lone_cr", lone, p)
    if kind != want:
        problems.append(f"S5: {p} line endings are {kind}, §Live fixes says {want}")
for p in (PLAN / "implementation-plan.md", PLAN / "task.md", pathlib.Path(".agent/context/handoffs/2026-11-15-docs-path-hygiene-plan-critical-review.md")):
    raw = p.read_bytes()
    kind, crlf, bare, lone = eol(raw)
    print("plan file", p.as_posix(), "sha256", hashlib.sha256(raw).hexdigest(), "eol", kind, "lines", raw.count(b"\n"))
for p in problems:
    print("PROBLEM:", p)
sys.exit(1 if problems else 0)
'@
Set-Content -Path "$receipts/baseline-record.py" -Value $record -Encoding utf8
Invoke-Step 'record' @('uv', 'run', '--no-sync', 'python', "$receipts/baseline-record.py")

# 4. The inventory (S2 on a live test, source, config or script beyond the six; S7 on an own hit).
Invoke-Step 'inventory-baseline' @('uv', 'run', '--no-sync', 'python', "$plan/inventory.py", '--baseline')

# 5. Anchors (S5).
Invoke-Step 'anchors' @('uv', 'run', '--no-sync', 'python', "$plan/edit-check.py", '--anchors')

# 6. Install from the lock; the base Python suite with TMP and TEMP at the dph tmp folder.
Invoke-Step 'uv-sync' @('uv', 'sync', '--frozen', '--all-packages')
$env:TMP = $tmp
$env:TEMP = $tmp
& rtk proxy uv run --no-sync pytest tests/ --tb=short -q -rfE *> "$receipts/dph-base-py.txt"
Write-Output ("base suite py exit={0} receipt={1}/dph-base-py.txt" -f $LASTEXITCODE, $receipts)
Get-Content "$receipts/dph-base-py.txt" | Select-String -Pattern '^FAILED |^ERROR |passed|failed' | Select-Object -Last 12
$env:TMP = $userTmp
$env:TEMP = $userTemp
# Vitest from pwsh in ui/ (memory: vitest-from-pwsh-not-bash). The two files must pass (S6).
Push-Location 'P:\av-kit\ui'
& rtk proxy npm run test -- tests/unit/dev-spawn.test.ts tests/unit/capture-interactive.test.ts *> "$receipts/dph-base-ui.txt"
$uiCode = $LASTEXITCODE
Pop-Location
Write-Output ("base ui two files exit={0} receipt={1}/dph-base-ui.txt" -f $uiCode, $receipts)
Get-Content "$receipts/dph-base-ui.txt" | Select-String -Pattern 'Test Files|Tests |skipped' | Select-Object -Last 4
if ($uiCode -ne 0) { Write-Output 'S6: a vitest file fails at base'; exit $uiCode }
# The full Vitest suite, recorded for the gate's ui-tests excuse list (not fatal).
Push-Location 'P:\av-kit\ui'
& rtk proxy npm run test *> "$receipts/dph-base-ui-full.txt"
$uiFullCode = $LASTEXITCODE
Pop-Location
Write-Output ("base suite ui exit={0} receipt={1}/dph-base-ui-full.txt" -f $uiFullCode, $receipts)
Get-Content "$receipts/dph-base-ui-full.txt" | Select-String -Pattern 'Test Files|Tests ' | Select-Object -Last 4

# 7. The plan-local checkers, with their temp folders in the dph tmp folder too.
$env:TMP = $tmp
$env:TEMP = $tmp
Invoke-Step 'red-check-selftest' @('uv', 'run', '--no-sync', 'python', "$plan/red-check.py", '--selftest')
Invoke-Step 'inventory-selftest' @('uv', 'run', '--no-sync', 'python', "$plan/inventory.py", '--selftest')
Invoke-Step 'edit-check-selftest' @('uv', 'run', '--no-sync', 'python', "$plan/edit-check.py", '--selftest')
Invoke-Step 'identity-selftest' @('uv', 'run', '--no-sync', 'python', "$plan/identity.py", '--selftest')
Write-Output 'baseline: all steps exit 0'
exit 0
