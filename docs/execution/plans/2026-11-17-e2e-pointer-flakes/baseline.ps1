# E2E pointer flakes baseline (task row 0; implementation-plan.md §Verification Plan 1).
# The shape of docs/execution/plans/2026-11-17-test-run-reliability/baseline.ps1, with this
# plan's steps: 1. the tree state (baseline.sha, baseline-dirty.txt), the worktree list and the
# commits since ecfa3f3 that touched ui/tests/e2e or ui/src; 2. the path-scoped baseline:
# baseline-scope.json over §Files Modified, the "Read, never changed" files,
# ui/tests/e2e/main-diag-watch.cjs and meu-register.py, with the four new files and
# meu-register.py absent; baseline-dirty-hashes.json; the row-0 copies; baseline-eol.json;
# baseline-skip-hashes.json over packages/, mcp-server/, tools/ and ui/src/ (secret names and
# .agent/fleet/hub dropped before any stat or read, Session 83 RULE-2); the S2 binding: every
# epf91-probe.txt anchor at its line or at a moved line with the same text (a moved line is
# recorded, not failed: Session 51 RULE-3 and the brief's S2 rule), the three issues open,
# grouping row 91 proposed, the highest MEU recorded, D-1145 to D-1154 and D-1193 to D-1195
# unused outside this plan, no graphify graph, and the plan and task hashes as approved;
# 3. the host-load wait (Session 81 RULE-2; a load still above 50 % after the wait fails the
# row), then flake-run.py --list-check (epf-base-list.txt, epf-base-total.txt), the full
# Vitest run (epf-base-ui.txt, failures recorded, not fatal) and epf-red-source.txt;
# 4. assert-check.py --snapshot; the plan-local selftests, flake-run.py --kill-check (the task
# cell's --children 2, and the plan's --children 2 --churn), eol-check.py over the fresh copies,
# and ruff format --check and ruff check on the plan folder's Python (Session 82 RULE-1).
# uv sync is not run: no network (the brief), and the environment is used as installed.
# Every step but the full Vitest run is fail-fast. Run from the repository root in pwsh.
$ErrorActionPreference = 'Stop'
$root = (git rev-parse --show-toplevel).Trim()
Set-Location $root
$plan = 'docs/execution/plans/2026-11-17-e2e-pointer-flakes'
$receipts = 'C:/Temp/av-kit/e2e-pointer-flakes'
$env:ELECTRON_RUN_AS_NODE = $null
$env:PYTHONIOENCODING = 'utf-8'
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:RECEIPTS_DIR = 'C:/Temp/av-kit'
$tmp = 'C:\Temp\av-kit\e2e-pointer-flakes\tmp'
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
import ast, hashlib, json, pathlib, re, subprocess, sys

PLAN = pathlib.Path("docs/execution/plans/2026-11-17-e2e-pointer-flakes")
OUT = pathlib.Path("C:/Temp/av-kit/e2e-pointer-flakes")
COPIES = OUT / "baseline-copies"
PROBE = OUT / "epf91-probe.txt"
EXPECTED_HEAD = "9fce270bff07964d76da4dee163f83fddf31fe2e"
REGISTER = ".agent/context/known-issues.yaml"
GROUPING = ".agent/context/grouping/2026-11-17-value-triage-session-grouping.md"
HANDOFF = ".agent/context/handoffs/2026-11-17-e2e-pointer-flakes-handoff.md"
REFLECTION = "docs/execution/reflections/2026-11-17-e2e-pointer-flakes-reflection.md"
IMPL_REVIEW = ".agent/context/handoffs/2026-11-17-e2e-pointer-flakes-implementation-critical-review.md"
PLAN_REVIEW = ".agent/context/handoffs/2026-11-17-e2e-pointer-flakes-plan-critical-review.md"
MEU_REGISTER = f"{PLAN.as_posix()}/meu-register.py"
# §Files Modified, with each file's line-ending kind (implementation-plan.md §Files Modified).
# The conditional docs/build-plan/<area>.md has no name until row 7; the matrix is bound here.
MODIFIED = {
    "ui/tests/e2e/download-queue.test.ts": "LF",
    "ui/tests/e2e/convert-queue.test.ts": "LF",
    "ui/tests/e2e/capture-inbox.test.ts": "LF",
    "ui/tests/e2e/electron-app.ts": "LF",
    REGISTER: "LF",
    ".agent/context/known-issues.md": "LF",
    GROUPING: "LF",
    ".agent/context/meu-status.yaml": "LF",
    "docs/build-plan/build-priority-matrix.md": "CRLF",
    ".agent/context/meu-registry.md": "LF",
    "docs/BUILD_PLAN.md": "LF",
}
NEW = {
    "ui/tests/e2e/pointer-settle.ts": "LF",
    "ui/tests/e2e/e2e-diag.ts": "LF",
    "ui/tests/e2e/e2e-diag.test.ts": "LF",
    "ui/tests/unit/e2e-pointer.test.ts": "LF",
    MEU_REGISTER: "LF",
}
# Bound to its sha or absent; the plan does not write it (its role went to installMainDiag).
OPTIONAL = {"ui/tests/e2e/main-diag-watch.cjs": "LF"}
# §Project files "Read, never changed".
READ_ONLY = {
    "ui/tests/e2e/electron-env.ts": "LF",
    "ui/tests/e2e/main-error-watch.cjs": "LF",
    "ui/tests/e2e/electron-harness.test.ts": "LF",
    "ui/tests/e2e/main-rejection-watch.test.ts": "LF",
    "ui/tests/e2e/transcript-queue.test.ts": "LF",
    "ui/tests/unit/e2e-harness.test.ts": "LF",
    "ui/tests/unit/rejection-watch.test.ts": "LF",
    "ui/playwright.config.ts": "LF",
    "ui/package.json": "CRLF",
    "ui/src/renderer/src/components/queue/QueueList.tsx": None,
    "ui/src/renderer/src/components/queue/queue-dnd.ts": None,
}
# Shared state files: read first, own lines only; copied for eol-check.py (both CRLF).
SHARED = {"docs/execution/metrics.md": "CRLF", ".agent/context/current-focus.md": "CRLF"}
PLAN_FILES = {
    f"{PLAN.as_posix()}/{n}": "LF"
    for n in (
        "implementation-plan.md", "task.md", "flake-run.py", "assert-check.py", "red-check.py",
        "identity.py", "issue-resolve.py", "eol-check.py", "baseline.ps1",
    )
}
# The approved plan and task (the brief's reviewed versions; the plan moved after the round-3
# verdict only by its Status line).
PLAN_SHA = {
    f"{PLAN.as_posix()}/implementation-plan.md": "2ada9bf1f760816e6c86b66aea76636bb90e1dbbbe14c9f5718dc8527417518a",
    f"{PLAN.as_posix()}/task.md": "711ea4405afd2ea7ac9f7654f0c3fa446abecabbb6837c32aae73da017be5103",
}
ISSUES_OPEN = (
    "DOWNLOAD-QUEUE-DRAG-OVER-MISS",
    "CAPTURE-ZOOM-PAN-ORIGIN-FLAKE",
    "CAPTURE-E2E-LAUNCH-TEARDOWN-HANG",
)
GROUPING_ROW = "| 91 | `e2e-pointer-flakes` | \u2014 | P3 | proposed | \u2014 |"
DECISION_IDS = (*range(1145, 1155), 1193, 1194, 1195)
SCOPE_PREFIXES = (
    PLAN.as_posix() + "/",
    ".agent/context/handoffs/2026-11-17-e2e-pointer-flakes-",
    "docs/execution/reflections/2026-11-17-e2e-pointer-flakes-",
)
SKIP_ROOTS = ("packages", "mcp-server", "tools", "ui/src")
SECRET_BASES = (".mcp.json", "mcp-token.txt", ".claude.json", ".env")
problems = []
moved = []


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
if head != EXPECTED_HEAD:
    problems.append(f"HEAD is {head}, not the brief's {EXPECTED_HEAD} (stop and report)")
origin = subprocess.run(["git", "rev-parse", "origin/main"], capture_output=True).stdout.decode().strip()
print("origin/main as found", origin or "<none>")
branch = git("rev-parse", "--abbrev-ref", "HEAD").decode().strip()
print("branch", branch)
if branch != "main":
    problems.append(f"branch is {branch}, not main")
print("worktrees:")
for line in git("worktree", "list").decode("utf-8").splitlines():
    print("  " + line)
print("commits ecfa3f3..HEAD (all):")
for line in git("log", "--oneline", "ecfa3f3..HEAD").decode("utf-8").splitlines():
    print("  " + line)
print("commits ecfa3f3..HEAD -- ui/tests/e2e ui/src:")
for line in git("log", "--oneline", "ecfa3f3..HEAD", "--", "ui/tests/e2e", "ui/src").decode("utf-8").splitlines():
    print("  " + line)
print("files changed ecfa3f3..HEAD -- ui/tests/e2e ui/src:")
for line in git("diff", "--name-status", "ecfa3f3", "HEAD", "--", "ui/tests/e2e", "ui/src").decode("utf-8").splitlines():
    print("  " + line)
porcelain = git("status", "--porcelain", "--untracked-files=all").decode("utf-8")
(PLAN / "baseline-dirty.txt").write_bytes(porcelain.encode("utf-8"))
dirty = [line[3:].strip().strip('"') for line in porcelain.splitlines() if line.strip()]
print("baseline-dirty.txt", len(dirty), "paths")
for p in dirty:
    print("  dirty", p)

KINDS = {**MODIFIED, **NEW, **OPTIONAL}
scope = {p: sha(p) for p in (*KINDS, *READ_ONLY)}
for p in NEW:
    if scope[p] != "absent":
        problems.append(f"S2: new file already exists: {p}")
for p in (HANDOFF, REFLECTION, IMPL_REVIEW):
    if sha(p) != "absent":
        problems.append(f"S2: a closeout file already exists: {p}")
for p in (*MODIFIED, *READ_ONLY):
    if scope[p] in ("absent", "not-a-file"):
        problems.append(f"S2: scoped path missing: {p}")
print("optional", "ui/tests/e2e/main-diag-watch.cjs", scope["ui/tests/e2e/main-diag-watch.cjs"])
(PLAN / "baseline-scope.json").write_bytes((json.dumps(scope, indent=2) + "\n").encode())
print("baseline-scope.json", len(scope), "paths;", sum(v == "absent" for v in scope.values()), "absent")


def in_scope(p):
    return p in scope or p in SHARED or p.startswith(SCOPE_PREFIXES)


hashes = {p: (sha(p) if pathlib.Path(p).exists() else "deleted") for p in dirty if not in_scope(p) and not secret(p)}
(PLAN / "baseline-dirty-hashes.json").write_bytes((json.dumps(hashes, indent=2, sort_keys=True) + "\n").encode())
print("baseline-dirty-hashes.json", len(hashes), "paths outside this scope")
for p in sorted(hashes):
    print("  bound by hash", p, hashes[p][:16])
for p in SHARED:
    print("bound by content (read first, own lines only)", p, "dirty" if p in dirty else "clean at HEAD", sha(p)[:16])

# The row-0 content of every existing scoped, read-only, shared and plan file: eol-check.py's
# base, row 9's grouping base and the execution review's delta base.
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
# mcp-server/, tools/ and ui/src/, secret names dropped before any stat or read.
listed = git("ls-files", "--cached", "--others", "--exclude-standard", *SKIP_ROOTS)
skip_paths = [n for n in listed.decode("utf-8").splitlines() if n and not secret(n)]
skips = {p: sha(p) for p in skip_paths if pathlib.Path(p).is_file()}
(PLAN / "baseline-skip-hashes.json").write_bytes((json.dumps(skips, indent=2, sort_keys=True) + "\n").encode())
for r in SKIP_ROOTS:
    print("baseline-skip-hashes.json", r, sum(1 for p in skips if p.startswith(r + "/")), "files")
print("baseline-skip-hashes.json", len(skips), "files in all")

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

# S2: the probe's scope hashes against now (a change is recorded, never failed: bound to content).
probe = PROBE.read_bytes().decode("utf-8")
print("probe", PROBE.as_posix(), "sha256", hashlib.sha256(PROBE.read_bytes()).hexdigest()[:16])
for m in re.finditer(r"^(\S+): (LF|CRLF|MIXED|none) \d+ B \d+ lines ([0-9a-f]{16}) ", probe, re.M):
    rel, _, short = m.groups()
    now = sha(rel)[:16]
    state = "unchanged" if now == short else f"CHANGED {short} -> {now}"
    print("probe scope", rel, state)
    if now != short:
        moved.append(f"scope file changed since the probe: {rel} {short} -> {now}")

# S2: the anchors, each at its probe line or at one moved line holding the same text.
anchors = re.findall(r"^ok   (\S+?):(\d+) (.+)$", probe, re.M)
print("probe anchors", len(anchors))
if not anchors:
    problems.append("S2: no anchor read from the probe")
for rel, no, raw_needle in anchors:
    needle = ast.literal_eval(raw_needle)
    no = int(no)
    lines = pathlib.Path(rel).read_bytes().decode("utf-8").split("\n")
    at = [i + 1 for i, ln in enumerate(lines) if needle in ln]
    if no - 1 < len(lines) and needle in lines[no - 1]:
        print("anchor ok", f"{rel}:{no}", repr(needle), "occurrences", len(at))
    elif len(at) == 1:
        print("anchor MOVED", f"{rel}:{no} -> {at[0]}", repr(needle))
        moved.append(f"anchor moved: {rel}:{no} -> {at[0]} {needle!r}")
    else:
        print("anchor MISSING", f"{rel}:{no}", repr(needle), "found at", at)
        problems.append(f"S2: anchor {needle!r} not at {rel}:{no} and found at {at}")

register = pathlib.Path(REGISTER).read_bytes().decode("utf-8")
for issue in ISSUES_OPEN:
    m = re.search(r"^  - id: " + issue + r"\n(?:    .*\n)*?    status: (\S+)", register, re.M)
    state = m.group(1) if m else None
    print("issue", issue, "status", state)
    if state != "open":
        problems.append(f"S2: {issue} is {state}, not open")
glines = pathlib.Path(GROUPING).read_bytes().decode("utf-8").split("\n")
row = [(i + 1, ln) for i, ln in enumerate(glines) if ln.startswith("| 91 |")]
print("grouping row 91", row)
if [ln for _, ln in row] != [GROUPING_ROW]:
    problems.append("S2: grouping row 91 is not the one proposed row")
elif row[0][0] != 163:
    moved.append(f"grouping row 91 moved: :163 -> :{row[0][0]}")
for ln in glines:
    if re.match(r"^\| (74|92|93|94) \|", ln):
        print("grouping sibling", ln)

meu = git("grep", "-h", "-o", "-E", r"MEU-[0-9]+", "--", ".agent/context/meu-registry.md", ".agent/context/meu-status.yaml").decode()
nums = sorted({int(m[4:]) for m in meu.split()})
print("highest MEU in the registry and status:", f"MEU-{nums[-1]}" if nums else "none")
print("next free MEU id:", f"MEU-{nums[-1] + 1}" if nums else "unknown")
if nums and nums[-1] != 159:
    moved.append(f"highest MEU is MEU-{nums[-1]}: the plan names MEU-159 or a later id another session registered")

out = git("grep", "-h", "-o", "-E", r"D-1[0-9]{3}", "--", ".", ":(exclude).agent/fleet/hub").decode()
ids = sorted({int(m[2:]) for m in out.split()})
print("highest D-id in tracked files:", f"D-{ids[-1]}" if ids else "none")
untracked = [n for n in git("ls-files", "--others", "--exclude-standard").decode("utf-8").splitlines() if n and not secret(n)]
foreign = [n for n in untracked if not n.startswith(SCOPE_PREFIXES)]
print("untracked files outside this plan's scope:", foreign)
for d in DECISION_IDS:
    tracked = d in ids
    held = [n for n in foreign if pathlib.Path(n).is_file() and f"D-{d}".encode() in pathlib.Path(n).read_bytes()]
    print(f"D-{d}:", "IN USE" if tracked or held else "free", held)
    if tracked or held:
        problems.append(f"S2: D-{d} is in use outside this plan")

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

# The planning evidence left as it is: this session's receipt folder and the receipts root.
print("planning evidence in", OUT.as_posix())
for p in sorted(OUT.iterdir()):
    if p.name in ("baseline-copies", "tmp", "baseline-record.py"):
        continue
    print("  pre-existing", p.name + ("/" if p.is_dir() else ""))
root = OUT.parent
print("planning evidence in", root.as_posix())
for p in sorted(root.glob("epf-*.txt")) + sorted(root.glob("epf-plan-review-round-*.md")):
    print("  pre-existing", p.name)
for m in moved:
    print("S2-MOVED:", m)
for p in problems:
    print("PROBLEM:", p)
sys.exit(1 if problems else 0)
'@
New-Item -ItemType Directory -Force -Path $receipts | Out-Null
Set-Content -Path "$receipts/baseline-record.py" -Value $record -Encoding utf8
Invoke-Step 'record' @('uv', 'run', '--no-sync', 'python', "$receipts/baseline-record.py")

# 3. The host-load wait (Session 81 RULE-2), imported from flake-run.py; a load still above
# 50 % when its ten minutes end fails the row.
$hostLoad = @'
import importlib.util, sys
spec = importlib.util.spec_from_file_location(
    "flake_run", "docs/execution/plans/2026-11-17-e2e-pointer-flakes/flake-run.py"
)
mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mod  # flake-run.py's dataclasses resolve their module through it
spec.loader.exec_module(mod)
load = mod.host_load_wait(50.0)
sys.exit(0 if load <= 50.0 else 2)
'@
Set-Content -Path "$receipts/baseline-host-load.py" -Value $hostLoad -Encoding utf8
Invoke-Step 'host-load' @('uv', 'run', '--no-sync', 'python', "$receipts/baseline-host-load.py")

# The E2E list: the clipboard specs not listed, each watched fragment one test, the watched list
# eleven tests, and the full total for --expect-total.
& rtk proxy uv run --no-sync python "$plan/flake-run.py" --list-check --label base-list *> "$receipts/epf-base-list.txt"
$listCode = $LASTEXITCODE
Write-Output ("baseline step base-list exit={0} receipt={1}/epf-base-list.txt" -f $listCode, $receipts)
Get-Content "$receipts/epf-base-list.txt" -Tail 8
if ($listCode -ne 0) { exit $listCode }
$totals = @(Select-String -Path "$receipts/epf-base-list.txt" -Pattern '^expect-total ([0-9]+)$')
if ($totals.Count -ne 1) { Write-Output 'baseline step base-total: no single expect-total line'; exit 1 }
$total = $totals[0].Matches[0].Groups[1].Value
[System.IO.File]::WriteAllBytes("$receipts/epf-base-total.txt", [System.Text.Encoding]::ASCII.GetBytes("$total`n"))
Write-Output ("baseline step base-total exit=0 total={0}" -f $total)

# The base Vitest suite from pwsh in ui/ (memory: vitest-from-pwsh-not-bash); the gate's
# ui-tests excuse list reads it. Its failures are recorded, not fatal.
Push-Location 'P:\av-kit\ui'
& rtk proxy npm run test *> "$receipts/epf-base-ui.txt"
$uiCode = $LASTEXITCODE
Pop-Location
Write-Output ("base suite ui exit={0} receipt={1}/epf-base-ui.txt" -f $uiCode, $receipts)
Get-Content "$receipts/epf-base-ui.txt" | Select-String -Pattern 'Test Files|Tests |FAIL ' | Select-Object -Last 12

# The specs' blob ids at HEAD, so row 3 can show it ran on unfixed specs.
$src = foreach ($s in @('ui/tests/e2e/download-queue.test.ts', 'ui/tests/e2e/convert-queue.test.ts', 'ui/tests/e2e/capture-inbox.test.ts')) {
    $id = (git rev-parse "HEAD:$s").Trim()
    if ($LASTEXITCODE -ne 0) { Write-Output "baseline step red-source: no blob for $s"; exit 1 }
    "$s $id"
}
[System.IO.File]::WriteAllBytes("$receipts/epf-red-source.txt", [System.Text.Encoding]::ASCII.GetBytes((($src -join "`n") + "`n")))
Write-Output 'baseline step red-source exit=0'
Get-Content "$receipts/epf-red-source.txt"

# 4. The assertion snapshot, then the plan-local checkers (Session 82 RULE-1 on the plan
# folder's Python).
Invoke-Step 'assert-snapshot' @('uv', 'run', '--no-sync', 'python', "$plan/assert-check.py", '--snapshot')
$planPy = @(Get-ChildItem -Path $plan -Filter '*.py' | ForEach-Object { "$plan/$($_.Name)" })
Invoke-Step 'ruff-format-plan' (@('uv', 'run', '--no-sync', 'ruff', 'format', '--check') + $planPy)
Invoke-Step 'ruff-check-plan' (@('uv', 'run', '--no-sync', 'ruff', 'check') + $planPy)
Invoke-Step 'red-check-selftest' @('uv', 'run', '--no-sync', 'python', "$plan/red-check.py", '--selftest')
Invoke-Step 'identity-selftest' @('uv', 'run', '--no-sync', 'python', "$plan/identity.py", '--selftest')
Invoke-Step 'eol-check-selftest' @('uv', 'run', '--no-sync', 'python', "$plan/eol-check.py", '--selftest')
Invoke-Step 'flake-run-selftest' @('uv', 'run', '--no-sync', 'python', "$plan/flake-run.py", '--selftest')
Invoke-Step 'assert-check-selftest' @('uv', 'run', '--no-sync', 'python', "$plan/assert-check.py", '--selftest')
Invoke-Step 'kill-check' @('uv', 'run', '--no-sync', 'python', "$plan/flake-run.py", '--kill-check', '--children', '2')
Invoke-Step 'kill-check-churn' @('uv', 'run', '--no-sync', 'python', "$plan/flake-run.py", '--kill-check', '--children', '2', '--churn')
Invoke-Step 'assert-check-row0' @('uv', 'run', '--no-sync', 'python', "$plan/assert-check.py")
Invoke-Step 'eol-check-row0' @('uv', 'run', '--no-sync', 'python', "$plan/eol-check.py")
Write-Output 'baseline: all steps exit 0'
exit 0
