# Session 95 eval-describe-raw-bytes baseline (task row 0; implementation-plan.md §Verification
# Plan 1). The shape of docs/execution/plans/2026-11-17-mcp-audit-refresh/baseline.ps1, with this
# plan's steps: 1. uv sync --frozen --offline --all-packages (S7 on a held file); 2. the tree
# state (baseline.sha, baseline-dirty.txt with the foreign class marked, git worktree list); the
# sibling check (edr-since.txt: every commit since 3e61b5b, and none of them touching mcp-server,
# Session 64's or Session 92's plan folder, S2); the path-scoped baseline: baseline-scope.json
# over §Files Modified, the "Read, never changed" files and the foreign class, with the two new
# files and the handoff absent; baseline-dirty-hashes.json, which binds every dirty path outside
# this scope by hash; the row-0 copies (eol-check.py's and edr-check.py doc's base) and
# baseline-eol.json; baseline-skip-hashes.json over packages/, tools/, ui/, tests/ and
# mcp-server/{src,scripts,tests} (secret names dropped before any stat or read, Session 83
# RULE-2); the S2 binding: the anchors by line and text (a line that only moved is recorded for
# the handoff, Session 51 RULE-3), the issue open (yaml.safe_load, by key, Session 92 RULE-2),
# grouping row 95 proposed, the s95 roots absent, tsx's CLI and node present, no graphify graph,
# and the plan, task and plan-review hashes as approved; 3. the host load; 4. the home-path check
# before (edr-home-before.txt, S8); 5. edr-check.py records --record (baseline-records.json,
# written once, and the eval-rerun.py and eval-check.py selftests); 6. the red-check.py,
# identity.py, eol-check.py and edr-check.py selftests, eol-check.py over the fresh copies, and
# ruff format --check and ruff check on the plan folder's Python (Session 82 RULE-1). No build
# here (row 1 builds). Every step is fail-fast. Run from the repository root in pwsh.
$ErrorActionPreference = 'Stop'
$root = (git rev-parse --show-toplevel).Trim()
Set-Location $root
$plan = 'docs/execution/plans/2026-11-18-eval-describe-raw-bytes'
$receipts = 'C:/Temp/av-kit/eval-describe-raw-bytes'
$env:ELECTRON_RUN_AS_NODE = $null
$env:PYTHONIOENCODING = 'utf-8'
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:RECEIPTS_DIR = 'C:/Temp/av-kit'
$tmp = 'C:\Temp\av-kit\eval-describe-raw-bytes\tmp'
New-Item -ItemType Directory -Force -Path $tmp | Out-Null
$env:TMP = $tmp
$env:TEMP = $tmp

function Invoke-Step([string]$Id, [string[]]$Argv) {
    & rtk proxy @Argv
    $code = $LASTEXITCODE
    Write-Output ("baseline step {0} exit={1}" -f $Id, $code)
    if ($code -ne 0) { exit $code }
}

# 2. Tree state, the sibling check, the path-scoped baseline and the S2 binding, in Python so
# every file is read and written as bytes.
$record = @'
import hashlib, json, pathlib, shutil, subprocess, sys

import yaml

PLAN = pathlib.Path("docs/execution/plans/2026-11-18-eval-describe-raw-bytes")
OUT = pathlib.Path("C:/Temp/av-kit/eval-describe-raw-bytes")
COPIES = OUT / "baseline-copies"
EXPECTED_HEAD = "3e61b5ba074c9434ca7ea1bea9d809da80305560"
S64 = "docs/execution/plans/2026-11-11-capture-export-copy"
S92 = "docs/execution/plans/2026-11-17-mcp-audit-refresh"
EVAL_RUN = f"{S64}/eval-run.md"
HARNESS = f"{S64}/eval-harness.ts"
GUARD = f"{S92}/eval-rerun.py"
GROUPING = ".agent/context/grouping/2026-11-18-eval-describe-session-grouping.md"
REGISTER = ".agent/context/known-issues.yaml"
ISSUE = "EVAL-HARNESS-DESCRIBE-CP437-MOJIBAKE"
HANDOFF = ".agent/context/handoffs/2026-11-18-eval-describe-raw-bytes-handoff.md"
EVAL_BASE = pathlib.Path("C:/Temp/av-kit/s64/eval")
ROOTS = ("s95-old", "s95-old3", "s95-describe", "s95-direct")
TSX = pathlib.Path("mcp-server/node_modules/tsx/dist/cli.mjs")
# §Files Modified, with each file's line-ending kind (implementation-plan.md §Files Modified).
MODIFIED = {
    EVAL_RUN: "LF",
    REGISTER: "LF",
    ".agent/context/known-issues.md": "LF",
    GROUPING: "LF",
}
NEW = {
    f"{PLAN.as_posix()}/test_eval_describe.py": "LF",
    f"{S64}/eval-describe.py": "LF",
    HANDOFF: "LF",
}
# §Files Modified "Read, never changed": bound by hash; their kind is recorded, not expected.
# The Session 64 describe receipt sits outside the repository: hashed, never copied.
READ_ONLY = (
    GUARD,
    f"{S92}/capture-description.expected.txt",
    f"{S64}/eval-check.py",
    HARNESS,
    f"{S64}/eval-seed.py",
    f"{S64}/task.md",
    f"{S64}/implementation-plan.md",
    "mcp-server/scripts/audit/backend.ts",
    "C:/Temp/av-kit/s64-E1-describe.txt",
    "docs/BUILD_PLAN.md",
)
# The foreign class (Session 92 RULE-3): the coordinator's files, bound by hash; a change is
# recorded in the handoff, is not S4 and stays out of the commit paths.
FOREIGN_CLASS = (
    ".agent/model-registry.local.json",
    *sorted(p.as_posix() for p in pathlib.Path(".claude/agents").glob("*.md")),
    *sorted(p.as_posix() for p in pathlib.Path(".cursor/agents").glob("*.md")),
)
# Shared state files: read first, own lines only; copied for eol-check.py (both CRLF).
SHARED = {"docs/execution/metrics.md": "CRLF", ".agent/context/current-focus.md": "CRLF"}
PLAN_FILES = {
    f"{PLAN.as_posix()}/{n}": "LF"
    for n in (
        "implementation-plan.md", "task.md", "edr-check.py", "edr-old.ps1", "red-check.py",
        "identity.py", "issue-resolve.py", "eol-check.py", "baseline.ps1", "host-load.ps1",
    )
}
# The approved plan and task. The plan's sha moved only by the Status line's execute words
# (the coordinator, 2026-11-18), from 78d24c0b... (reviewed) to the value here; task.md and the
# plan review are unchanged. The plan review's hash is the one found before row 0 ran.
PLAN_SHA = {
    f"{PLAN.as_posix()}/implementation-plan.md": "83a3cdcd3407684740b5e8b522fb02c9f89795e558d934bfac7e544c2803f2b2",
    f"{PLAN.as_posix()}/task.md": "51c158bc2f62ef63c159aa537aedefceffb1c2db78b35bb1df7e0ccf5aa7ec48",
}
PLAN_REVIEW = ".agent/context/handoffs/2026-11-18-eval-describe-raw-bytes-plan-critical-review.md"
PLAN_REVIEW_SHA = "174c848615186c5bc9ed74a32a206603d67a6c776e7ace698c3d21c35a792c4e"
# The task row 0 anchors: (path, line, text, unique). A unique text must occur once in the
# file; if it is not on its line, the line moved and is recorded (Session 51 RULE-3).
ANCHORS = (
    (EVAL_RUN, 24, "3. **Describe.** From", True),
    (GUARD, 35, 'CUT = "<!-- CUT: the real surface ends above this line -->"', True),
    (GUARD, 43, "MOJIBAKE = re.compile(", True),
    (GUARD, 60, "def blocks(", True),
    (GUARD, 68, "def real_surface(", True),
    (GUARD, 94, "def build(", True),
    (HARNESS, 58, "function evalRoot(raw: string | undefined): string {", True),
    (GROUPING, 118, "| 95 | `eval-describe-raw-bytes` |", True),
)
SINCE_PATHS = ("mcp-server", S64, S92)
SCOPE_PREFIXES = (
    PLAN.as_posix() + "/",
    ".agent/context/handoffs/2026-11-18-eval-describe-raw-bytes-",
    "docs/execution/reflections/2026-11-18-eval-describe-raw-bytes-",
)
SKIP_DIRS = ("packages", "tools", "ui", "tests", "mcp-server/src", "mcp-server/scripts", "mcp-server/tests")
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


def foreign(p):
    return "coordinator, foreign class" if p in FOREIGN_CLASS else None


def text_lines(p):
    return pathlib.Path(p).read_bytes().decode("utf-8").replace("\r\n", "\n").split("\n")


OUT.mkdir(parents=True, exist_ok=True)
(OUT / "tmp").mkdir(parents=True, exist_ok=True)
head = git("rev-parse", "HEAD").decode().strip()
(PLAN / "baseline.sha").write_bytes((head + "\n").encode())
print("baseline.sha", head)
if head != EXPECTED_HEAD:
    problems.append(f"S2: HEAD is {head}, not the brief's {EXPECTED_HEAD[:7]}")
origin = subprocess.run(["git", "rev-parse", "origin/main"], capture_output=True).stdout.decode().strip()
print("origin/main as found", origin or "<none>")
worktrees = git("worktree", "list").decode("utf-8")
print("git worktree list:")
for line in worktrees.splitlines():
    print("  ", line)

# The sibling check: every commit since 3e61b5b, and none touching mcp-server or either eval folder.
since = git("log", "--oneline", "3e61b5b..HEAD").decode("utf-8")
touching = git("log", "--oneline", "3e61b5b..HEAD", "--", *SINCE_PATHS).decode("utf-8")
(OUT / "edr-since.txt").write_bytes(
    (
        "git log --oneline 3e61b5b..HEAD\n" + (since or "(empty)\n")
        + "\ngit log --oneline 3e61b5b..HEAD -- " + " ".join(SINCE_PATHS) + "\n"
        + (touching or "(empty)\n")
    ).encode("utf-8")
)
print("edr-since.txt: commits since 3e61b5b:", since.splitlines() or "none")
print("  commits touching mcp-server, Session 64's or Session 92's folder:", touching.splitlines() or "none")
if touching.strip():
    problems.append(f"S2: commits since 3e61b5b touch {SINCE_PATHS}: {touching.splitlines()}")

porcelain = git("status", "--porcelain", "--untracked-files=all").decode("utf-8")
dirty = [line[3:].strip().strip('"') for line in porcelain.splitlines() if line.strip()]
marks = [f"# foreign ({foreign(p)}): {p}" for p in dirty if foreign(p)]
(PLAN / "baseline-dirty.txt").write_bytes((porcelain + "".join(m + "\n" for m in marks)).encode("utf-8"))
print("baseline-dirty.txt", len(dirty), "paths,", len(marks), "foreign")
for p in dirty:
    print("  dirty", p, f"(foreign: {foreign(p)})" if foreign(p) else "")

KINDS = {**MODIFIED, **NEW}
scope = {p: sha(p) for p in (*KINDS, *READ_ONLY, *FOREIGN_CLASS)}
for p in NEW:
    if scope[p] != "absent":
        problems.append(f"S2: new file already exists: {p}")
for p in (*MODIFIED, *READ_ONLY):
    if scope[p] in ("absent", "not-a-file"):
        problems.append(f"S2: scoped path missing: {p}")
(PLAN / "baseline-scope.json").write_bytes((json.dumps(scope, indent=2) + "\n").encode())
print("baseline-scope.json", len(scope), "paths;", sum(v == "absent" for v in scope.values()), "absent;", len(FOREIGN_CLASS), "foreign class")
for p in FOREIGN_CLASS:
    print("  foreign class", p, scope[p][:16])


def in_scope(p):
    return p in scope or p in SHARED or p.startswith(SCOPE_PREFIXES)


hashes = {p: (sha(p) if pathlib.Path(p).exists() else "deleted") for p in dirty if not in_scope(p) and not secret(p)}
(PLAN / "baseline-dirty-hashes.json").write_bytes((json.dumps(hashes, indent=2, sort_keys=True) + "\n").encode())
print("baseline-dirty-hashes.json", len(hashes), "paths outside this scope")
for p in sorted(hashes):
    print("  bound by hash", p, hashes[p][:16])
for p in SHARED:
    print("bound by content (read first, own lines only)", p, "dirty" if p in dirty else "clean at HEAD", sha(p)[:16])

# The row-0 content of every existing repository scope, read-only, shared and plan file:
# eol-check.py's base, edr-check.py doc's base and the execution review's delta base.
copied = 0
for p in (*KINDS, *READ_ONLY, *SHARED, *PLAN_FILES, PLAN_REVIEW):
    src = pathlib.Path(p)
    if src.is_absolute() or not src.is_file():
        continue
    dest = COPIES / p
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(src.read_bytes())
    copied += 1
print("baseline-copies", copied, "row-0 copies under", COPIES.as_posix())

# baseline-skip-hashes.json (H1-4): every tracked or untracked, not-ignored file under the skip
# dirs, secret names dropped before any stat or read.
listed = git("ls-files", "--cached", "--others", "--exclude-standard", *SKIP_DIRS)
skip_paths = [n for n in listed.decode("utf-8").splitlines() if n and not secret(n)]
skips = {p: sha(p) for p in skip_paths if pathlib.Path(p).is_file()}
(PLAN / "baseline-skip-hashes.json").write_bytes((json.dumps(skips, indent=2, sort_keys=True) + "\n").encode())
per_dir = {d: sum(1 for p in skips if p.startswith(d + "/")) for d in SKIP_DIRS}
print("baseline-skip-hashes.json", len(skips), "files:", per_dir)

# Line endings, measured with Python bytes.
eols = {}
for p, want in {**KINDS, **{q: None for q in READ_ONLY}, **SHARED, **PLAN_FILES}.items():
    if not pathlib.Path(p).is_file():
        eols[p] = {"kind": "absent", "expected": want, "crlf": 0, "bare_lf": 0}
        print("eol absent", p)
        continue
    raw = pathlib.Path(p).read_bytes()
    kind, crlf, bare = eol(raw)
    eols[p] = {"kind": kind, "expected": want, "crlf": crlf, "bare_lf": bare, "bom": raw.startswith(b"\xef\xbb\xbf"), "bytes": len(raw)}
    print("eol", kind, "crlf", crlf, "bare_lf", bare, "bom", eols[p]["bom"], "bytes", len(raw), p)
    if want is not None and kind != want and p not in NEW:
        problems.append(f"S2: {p} is {kind}, the plan says {want}")
(PLAN / "baseline-eol.json").write_bytes((json.dumps(eols, indent=2) + "\n").encode())
print("baseline-eol.json", len(eols), "paths")

# S2: the anchors by line and text.
moved = []
for p, line, needle, unique in ANCHORS:
    text = pathlib.Path(p).read_bytes().decode("utf-8")
    lines = text.replace("\r\n", "\n").split("\n")
    here = lines[line - 1] if line <= len(lines) else None
    n = text.count(needle)
    hits = [i + 1 for i, ln in enumerate(lines) if needle in ln]
    at = here is not None and needle in here
    state = "at line" if at else (f"moved to {hits}" if len(hits) == 1 else "missing")
    print(f"anchor {p}:{line} {state} count={n} :: {needle[:100]!r}")
    if n != 1:
        problems.append(f"S2: anchor {needle[:80]!r} in {p} counted {n}, not 1")
    elif not at:
        moved.append(f"{p}:{line} -> {hits[0]}")
# The task row 0 text checks on those lines, wherever they now are.
run = text_lines(EVAL_RUN)
step3 = [i + 1 for i, ln in enumerate(run) if ln.startswith("3. **Describe.** From")]
step3_ok = len(step3) == 1 and "describe >" in run[step3[0] - 1]
print("eval-run.md step 3 line", step3, "starts '3. **Describe.** From' and holds 'describe >':", step3_ok)
if not step3_ok:
    problems.append("S2: eval-run.md step 3 is not one line holding 'describe >'")
line6 = run[5] if len(run) > 5 else ""
line6_ok = line6.endswith("the three `real-*` runs.")
print("eval-run.md:6 ends 'the three `real-*` runs.':", line6_ok, repr(line6[-60:]))
if not line6_ok:
    problems.append(f"S2: eval-run.md:6 is {line6!r}")
harness = text_lines(HARNESS)
eval_root = [i + 1 for i, ln in enumerate(harness) if "evalRoot" in ln]
range_ok = any(57 <= n <= 64 for n in eval_root)
print("eval-harness.ts evalRoot lines", eval_root, "one in 57-64:", range_ok)
if not range_ok:
    problems.append(f"S2: eval-harness.ts:57-64 holds no evalRoot (lines {eval_root})")
grouping = text_lines(GROUPING)
row95 = [(i + 1, ln) for i, ln in enumerate(grouping) if ln.startswith("| 95 |")]
row_ok = len(row95) == 1 and "| proposed |" in row95[0][1]
print("grouping row 95", row95, "one proposed row:", row_ok)
if not row_ok:
    problems.append("S2: grouping row 95 is not one proposed row")
elif row95[0][0] != 118:
    moved.append(f"{GROUPING}:118 -> {row95[0][0]} (row 95)")
print("anchor lines moved:", moved or "none")

# S2: the issue, read by key with yaml.safe_load (Session 92 RULE-2).
data = yaml.safe_load(pathlib.Path(REGISTER).read_bytes().decode("utf-8"))
matches = [i for i in data.get("issues", []) if isinstance(i, dict) and i.get("id") == ISSUE]
status = matches[0].get("status") if len(matches) == 1 else None
reg_line = next((i + 1 for i, ln in enumerate(text_lines(REGISTER)) if ln == f"  - id: {ISSUE}"), None)
print(f"issue {ISSUE}: entries {len(matches)}, status {status}, line {reg_line}")
if status != "open":
    problems.append(f"S2: {ISSUE} is {status}, not open")

# S2: the scratch roots absent, tsx's CLI and node present; S1: no graphify graph.
for r in ROOTS:
    exists = (EVAL_BASE / r).exists()
    print(f"root {(EVAL_BASE / r).as_posix()} exists: {exists}")
    if exists:
        problems.append(f"S2: the root {r} already exists")
print("tsx cli", TSX.as_posix(), "exists:", TSX.is_file())
if not TSX.is_file():
    problems.append("S2: tsx's CLI is missing")
node = shutil.which("node")
print("node on PATH:", bool(node))
if not node:
    problems.append("S2: node is not on PATH")
else:
    print("node --version", subprocess.run([node, "--version"], capture_output=True).stdout.decode().strip())
graphs = [g for g in ("graphify-out", "graphify-out-research") if pathlib.Path(g).exists()]
print("graphify graphs", graphs)
if graphs:
    problems.append(f"S1: a graphify graph exists: {graphs}")

# The approved plan, task and plan review.
for p, want in PLAN_SHA.items():
    got = sha(p)
    print("approved", p, got)
    if got != want:
        problems.append(f"S2: {p} sha256 {got}, not the approved {want}")
got = sha(PLAN_REVIEW)
print("plan review", PLAN_REVIEW, got)
if got != PLAN_REVIEW_SHA:
    problems.append(f"S2: the plan review's sha256 is {got}, not {PLAN_REVIEW_SHA}")
s92_cache = pathlib.Path(S92) / "__pycache__"
print("Session 92 __pycache__ (ignored, left in place):", sorted(p.name for p in s92_cache.glob("*")) if s92_cache.is_dir() else "none")
for n in ("red-check.py", "identity.py", "issue-resolve.py", "eol-check.py", "host-load.ps1", "edr-check.py", "edr-old.ps1"):
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

# 1. The environment (S7 on a held file).
Invoke-Step 'uv-sync' @('uv', 'sync', '--frozen', '--offline', '--all-packages')
# 2. The record.
Invoke-Step 'record' @('uv', 'run', '--no-sync', 'python', "$receipts/baseline-record.py")

# 3. The host load, recorded only: row 0 runs no build, suite or harness, so it does not wait.
# host-load.ps1 (the 50 % wait) runs before row 1's build and Red and in the H1-2 gate.
$samples = @()
for ($i = 0; $i -lt 5; $i++) {
    if ($i -gt 0) { Start-Sleep -Seconds 2 }
    $samples += [math]::Round([double](Get-CimInstance Win32_Processor | Measure-Object -Property LoadPercentage -Average).Average, 1)
}
$mean = [math]::Round((($samples | Measure-Object -Average).Average), 1)
Write-Output ("baseline host load recorded: samples [{0}] mean={1} % (not a wait; rows 1 and H1-2 wait at 50 %)" -f ($samples -join ', '), $mean)

# 4. The home-path check before (S8).
& rtk proxy uv run --no-sync python tools/check_home_path.py *> "$receipts/edr-home-before.txt"
$homeCode = $LASTEXITCODE
Get-Content "$receipts/edr-home-before.txt" | Select-Object -Last 4
Write-Output ("baseline step home-path exit={0} receipt={1}/edr-home-before.txt" -f $homeCode, $receipts)
if ($homeCode -ne 0) { exit $homeCode }

# 5. The records, written once (AC-11), with both legacy selftests. The edr-check selftest runs
# first (the brief: before its first real use).
Invoke-Step 'edr-check-selftest' @('uv', 'run', '--no-sync', 'python', "$plan/edr-check.py", '--selftest')
# A rerun of this script after a later step failed finds the file written: it then compares
# against it instead of writing it again (records --record refuses an existing file).
if (Test-Path -LiteralPath "$plan/baseline-records.json") {
    Write-Output 'baseline records: baseline-records.json exists from an earlier run of this row; comparing'
    Invoke-Step 'records-compare' @('uv', 'run', '--no-sync', 'python', "$plan/edr-check.py", 'records')
} else {
    Invoke-Step 'records-record' @('uv', 'run', '--no-sync', 'python', "$plan/edr-check.py", 'records', '--record')
}

# 6. The plan-local checkers (Session 82 RULE-1 on the plan folder's Python).
Invoke-Step 'red-check-selftest' @('uv', 'run', '--no-sync', 'python', "$plan/red-check.py", '--selftest')
Invoke-Step 'identity-selftest' @('uv', 'run', '--no-sync', 'python', "$plan/identity.py", '--selftest')
Invoke-Step 'eol-check-selftest' @('uv', 'run', '--no-sync', 'python', "$plan/eol-check.py", '--selftest')
Invoke-Step 'eol-check-row0' @('uv', 'run', '--no-sync', 'python', "$plan/eol-check.py")
$planPy = @(Get-ChildItem -Path $plan -Filter '*.py' | Sort-Object Name | ForEach-Object { "$plan/$($_.Name)" })
Write-Output ("baseline plan Python: {0}" -f ($planPy -join ', '))
Invoke-Step 'ruff-format-plan' (@('uv', 'run', '--no-sync', 'ruff', 'format', '--check') + $planPy)
Invoke-Step 'ruff-check-plan' (@('uv', 'run', '--no-sync', 'ruff', 'check') + $planPy)
Write-Output 'baseline: all steps exit 0'
exit 0
