# Framework small syncs baseline (task row 0; implementation-plan.md §Verification Plan 1).
# The shape of docs/execution/plans/2026-11-15-hdp-expert-pass/baseline.ps1, with this plan's steps:
# 1. the tree state (baseline.sha, baseline-dirty.txt); 2. the path-scoped baseline
# (baseline-scope.json with every new path absent, baseline-dirty-hashes.json, the four BASE copies
# in C:/Temp/av-kit/fs/base/); 3. the Session 85 binding (D-887, S2): SKILL_DIR/SKILL.md equals
# HEAD, and WORKFLOW differs from HEAD, and from 1e54433 (the HEAD this plan was written at, before
# Sessions 85 and 86 were committed), only in the Topic too broad row, which goes to topic-row.txt;
# 4. the upstream copies in C:/Temp/av-kit/fs/upstream/ with their blob ids (S5, port-check --files
# checks them again); 5. uv sync and the base Python suite (fs-base-py.txt; its own failures are
# recorded, not fatal: the session gate excuses only the ids this receipt shows failing);
# 6. the four plan-local selftests. Every other step is fail-fast. Run from the repository root.
$ErrorActionPreference = 'Stop'
$root = (git rev-parse --show-toplevel).Trim()
Set-Location $root
$plan = 'docs/execution/plans/2026-11-15-framework-small-syncs'
$receipts = 'C:/Temp/av-kit/fs'
$env:ELECTRON_RUN_AS_NODE = $null
$env:PYTHONIOENCODING = 'utf-8'
$env:RECEIPTS_DIR = 'C:/Temp/av-kit'
$env:AGENT_MODEL_REGISTRY_HOME = 'P:/.agent'
$userTmp = $env:TMP
$userTemp = $env:TEMP
$tmp = 'C:\Temp\av-kit\fs\tmp'
New-Item -ItemType Directory -Force -Path $tmp | Out-Null

function Invoke-Step([string]$Id, [string[]]$Argv) {
    & rtk proxy @Argv
    $code = $LASTEXITCODE
    Write-Output ("baseline step {0} exit={1}" -f $Id, $code)
    if ($code -ne 0) { exit $code }
}

# 1-3. Tree state, path-scoped baseline and the Session 85 binding, in Python so every file is
# read and written as bytes.
$record = @'
import hashlib, json, pathlib, re, subprocess, sys

PLAN = pathlib.Path("docs/execution/plans/2026-11-15-framework-small-syncs")
BASE = pathlib.Path("C:/Temp/av-kit/fs/base")
SKILL = ".agent/skills/deep-research-prompting/SKILL.md"
WORKFLOW = ".agent/workflows/inspiration-research.md"
GIT_SKILL = ".agent/skills/git-workflow/SKILL.md"
COMMIT_SCRIPT = ".agent/skills/git-workflow/scripts/agent-commit.ps1"
EXISTING = (SKILL, WORKFLOW, GIT_SKILL, COMMIT_SCRIPT)
NEW = (
    ".agent/skills/deep-research-prompting/scripts/strip_embedded_images.py",
    ".agent/skills/deep-research-prompting/templates/d1-chatgpt.md",
    ".agent/skills/deep-research-prompting/templates/d2-gemini.md",
    ".agent/skills/deep-research-prompting/templates/d3-claude.md",
    ".agent/skills/deep-research-prompting/templates/skeleton.md",
    ".agent/skills/deep-research-prompting/templates/snapshot.md",
    ".agent/skills/deep-research-prompting/templates/domain-overlays/content-seo.md",
    "tests/tooling/test_strip_embedded_images.py",
    "tools/check_commit_identity.py",
    "tests/tooling/test_check_commit_identity.py",
)
PLAN_WRITTEN_AT = "1e54433a797842f157e7af367ff5fec12f13f78b"
SCOPE_PREFIXES = (
    PLAN.as_posix() + "/",
    ".agent/context/handoffs/2026-11-15-framework-small-syncs-",
    "docs/execution/reflections/2026-11-15-framework-small-syncs-",
)
SHARED = ("docs/execution/metrics.md", ".agent/context/current-focus.md")
problems = []

def git(*args):
    return subprocess.run(["git", *args], capture_output=True, check=True).stdout

def sha(path):
    p = pathlib.Path(path)
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else ("absent" if not p.exists() else "not-a-file")

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

hashes = {p: (sha(p) if pathlib.Path(p).exists() else "deleted") for p in dirty if not in_scope(p)}
(PLAN / "baseline-dirty-hashes.json").write_bytes((json.dumps(hashes, indent=2, sort_keys=True) + "\n").encode())
print("baseline-dirty-hashes.json", len(hashes), "paths outside this scope")
for p in SHARED:
    print("shared", p, "dirty" if p in dirty else "clean at HEAD", sha(p))

for p in EXISTING:
    dest = BASE / p
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(pathlib.Path(p).read_bytes())
    print("BASE", p, "sha256", sha(dest))

# Session 85 binding (D-887, S2).
if pathlib.Path(SKILL).read_bytes() != git("cat-file", "--filters", f"HEAD:{SKILL}"):
    problems.append(f"S2: {SKILL} differs from HEAD")
else:
    print("S2", SKILL, "equals HEAD")
for label, args in (("HEAD", ("diff", "HEAD", "--", WORKFLOW)), (PLAN_WRITTEN_AT[:7], ("diff", PLAN_WRITTEN_AT, "--", WORKFLOW))):
    diff = git(*args).decode("utf-8").replace("\r", "")
    changed = [ln for ln in diff.splitlines() if ln[:1] in "+-" and not ln.startswith(("+++", "---"))]
    other = [ln for ln in changed if not ln[1:].startswith("| Topic too broad |")]
    print("S2", WORKFLOW, "vs", label, ":", len(changed), "changed line(s),", len(other), "outside the Topic too broad row")
    if other:
        problems.append(f"S2: {WORKFLOW} changed beyond the Topic too broad row since {label}")
rows = [ln for ln in pathlib.Path(WORKFLOW).read_bytes().decode("utf-8").replace("\r\n", "\n").split("\n") if ln.startswith("| Topic too broad |")]
if len(rows) != 1 or "human-decision-protocol.md" not in rows[0]:
    problems.append("S2: WORKFLOW does not hold exactly one Topic too broad row that cites human-decision-protocol.md")
else:
    (PLAN / "topic-row.txt").write_bytes((rows[0] + "\n").encode("utf-8"))
    print("topic-row.txt sha256", sha(PLAN / "topic-row.txt"))
text = pathlib.Path(GIT_SKILL).read_bytes().decode("utf-8")
for anchor in ("### What the Script Does", "2. ✅ Checks remote URL format", "### Exact-Scope Signed Commit Mode", "## Agent Workflow Checklist", "- [ ] Step 1: Check signing"):
    if anchor not in text:
        problems.append(f"S2: {GIT_SKILL} lacks the anchor {anchor!r}")
print("S2", GIT_SKILL, "anchors checked")
for p in problems:
    print("PROBLEM:", p)
sys.exit(1 if problems else 0)
'@
Set-Content -Path "$receipts/baseline-record.py" -Value $record -Encoding utf8
Invoke-Step 'record' @('uv', 'run', 'python', "$receipts/baseline-record.py")

# 4. Upstream: the exact blob bytes, written by Python so no shell re-encodes them; S5 on a
# blob id or byte count that differs from §Upstream blobs.
$fetch = @'
import hashlib, pathlib, subprocess, sys
OUT = pathlib.Path("C:/Temp/av-kit/fs/upstream")
SKILL = "0a8d5bc:core/.agent/skills/deep-research-prompting/"
BLOBS = (
    ("SKILL.md", "234d25a", 26816),
    ("scripts/strip_embedded_images.py", "4ef304e", 7898),
    ("templates/d1-chatgpt.md", "ef187b4", 1805),
    ("templates/d2-gemini.md", "e4c6c0d", 1843),
    ("templates/d3-claude.md", "24fff82", 1825),
    ("templates/domain-overlays/content-seo.md", "30d2dde", 7676),
    ("templates/skeleton.md", "cf92ba1", 2407),
    ("templates/snapshot.md", "eef9dbe", 1193),
    ("workflows/inspiration-research.md", "d9bf24f", 783),
)
bad = 0
for rel, prefix, size in BLOBS:
    spec = "0a8d5bc:core/.agent/" + rel if rel.startswith("workflows/") else SKILL + rel
    data = subprocess.run(["git", "-C", "P:/agentic-framework", "show", spec], capture_output=True, check=True).stdout
    dest = OUT / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)
    blob = subprocess.run(["git", "hash-object", str(dest)], capture_output=True, check=True, text=True).stdout.strip()
    ok = blob.startswith(prefix) and len(data) == size
    bad += not ok
    print("fetched", spec, "blob", blob[:7], "bytes", len(data), "ok" if ok else f"S5 expected {prefix} {size}")
sys.exit(1 if bad else 0)
'@
Set-Content -Path "$receipts/fetch-upstream.py" -Value $fetch -Encoding utf8
Invoke-Step 'upstream-fetch' @('uv', 'run', 'python', "$receipts/fetch-upstream.py")

# 5. Install from the lock; the base Python suite with TMP and TEMP outside the user profile.
Invoke-Step 'uv-sync' @('uv', 'sync', '--frozen', '--all-packages')
$env:TMP = $tmp
$env:TEMP = $tmp
& rtk proxy uv run pytest tests/ --tb=short -q -rfE *> "$receipts/fs-base-py.txt"
Write-Output ("base suite py exit={0} receipt={1}/fs-base-py.txt" -f $LASTEXITCODE, $receipts)
Get-Content "$receipts/fs-base-py.txt" | Select-String -Pattern '^FAILED |^ERROR |passed|failed' | Select-Object -Last 12
$env:TMP = $userTmp
$env:TEMP = $userTemp

# 6. The plan-local checkers (red-check.py and identity.py copied from
# 2026-11-05-closeout-register-grammar with this plan's PLAN and PROJECT_ARTIFACTS).
Invoke-Step 'red-check-selftest' @('uv', 'run', 'python', "$plan/red-check.py", '--selftest')
Invoke-Step 'identity-selftest' @('uv', 'run', 'python', "$plan/identity.py", '--selftest')
Invoke-Step 'port-check-selftest' @('uv', 'run', 'python', "$plan/port-check.py", '--selftest')
Invoke-Step 'script-check-selftest' @('uv', 'run', 'python', "$plan/script-check.py", '--selftest')
Write-Output 'baseline: all steps exit 0'
exit 0
