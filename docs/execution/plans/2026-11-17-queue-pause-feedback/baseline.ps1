# Queue pause feedback baseline (task row 0; implementation-plan.md §Verification Plan 1).
# The shape of docs/execution/plans/2026-11-15-convert-settings-drafts/baseline.ps1, through the
# ready-handshake copy, with this plan's steps: 1. the tree state (baseline.sha,
# baseline-dirty.txt); 2. the path-scoped baseline: baseline-scope.json over §Files Modified and
# the "Read, never changed" files, with the four new files absent; baseline-dirty-hashes.json,
# which binds every dirty path outside this scope by hash; the row-0 copies (the eol-check.py
# base) and baseline-eol.json; baseline-skip-hashes.json over packages/, mcp-server/, tests/ and
# tools/ (secret names dropped before any read, Session 83 RULE-2); the S2 binding: the
# qp88-probe.txt anchors each counted once, MEU-155 absent, QUEUE-PAUSE-NO-FEEDBACK open, grouping
# row 88 proposed, no queue-pause-feedback-residual anchor in 10, no graphify graph, and the plan
# and task hashes as approved (the plan's only post-review change is the Status line); 3. uv sync,
# the base Python suite (qp-base-py.txt), the base Vitest suite (qp-base-ui.txt) and the base
# format and lint checks; their own failures are recorded, not fatal; 4. the plan-local selftests,
# eol-check.py over the fresh copies, and ruff format --check and ruff check on the plan folder's
# Python (Session 82 RULE-1). Every other step is fail-fast. Run from the repository root in pwsh.
$ErrorActionPreference = 'Stop'
$root = (git rev-parse --show-toplevel).Trim()
Set-Location $root
$plan = 'docs/execution/plans/2026-11-17-queue-pause-feedback'
$receipts = 'C:/Temp/av-kit/queue-pause-feedback'
$env:ELECTRON_RUN_AS_NODE = $null
$env:PYTHONIOENCODING = 'utf-8'
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:RECEIPTS_DIR = 'C:/Temp/av-kit'
$tmp = 'C:\Temp\av-kit\queue-pause-feedback\tmp'
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

PLAN = pathlib.Path("docs/execution/plans/2026-11-17-queue-pause-feedback")
OUT = pathlib.Path("C:/Temp/av-kit/queue-pause-feedback")
COPIES = OUT / "baseline-copies"
GROUPING = ".agent/context/grouping/2026-11-15-post-rc3-triage-residuals-session-grouping.md"
TOOLBAR = "ui/src/renderer/src/components/queue/QueueToolbar.tsx"
CONVERT_CMDS = "ui/src/renderer/src/features/converter/convert-commands.ts"
DOWNLOAD_CMDS = "ui/src/renderer/src/features/downloader/download-commands.ts"
CONVERT_PAGE = "ui/src/renderer/src/features/converter/ConvertPage.tsx"
DOWNLOAD_PAGE = "ui/src/renderer/src/features/downloader/DownloaderPage.tsx"
FIXTURE = "ui/tests/unit/fixtures/queue-slot-baseline.json"
QUEUE_DOC = "docs/build-plan/10-queue-card-ui.md"
MATRIX = "docs/build-plan/build-priority-matrix.md"
# §Files Modified, with each file's line-ending kind (implementation-plan.md §Line endings).
MODIFIED = {
    TOOLBAR: "CRLF",
    CONVERT_CMDS: "CRLF",
    DOWNLOAD_CMDS: "CRLF",
    CONVERT_PAGE: "CRLF",
    DOWNLOAD_PAGE: "MIXED",
    "ui/src/renderer/src/features/downloader/downloader-help-content.ts": "CRLF",
    FIXTURE: "CRLF",
    "ui/tests/unit/convert-page.behavior.test.ts": "CRLF",
    "ui/tests/unit/downloader-page.behavior.test.ts": "MIXED",
    "packages/core/src/avkit_core/services/transcript.py": "LF",
    "docs/build-plan/03-service-layer.md": "CRLF",
    QUEUE_DOC: "CRLF",
    MATRIX: "CRLF",
    ".agent/context/meu-status.yaml": "LF",
    ".agent/context/meu-registry.md": "LF",
    "docs/BUILD_PLAN.md": "LF",
    ".agent/context/known-issues.yaml": "LF",
    ".agent/context/known-issues.md": "LF",
    GROUPING: "LF",
}
NEW = {
    "ui/src/renderer/src/lib/queue/pause-request.ts": "LF",
    "ui/tests/unit/queue-pause-feedback.test.tsx": "LF",
    "ui/tests/e2e/queue-pause-feedback.test.ts": "LF",
    "tests/unit/test_transcript_pause_wake.py": "LF",
}
# §Project files "Read, never changed": bound by hash; their kind is recorded, not expected.
READ_ONLY = (
    "ui/src/renderer/src/components/queue/QueueHeaderRow.tsx",
    "ui/src/renderer/src/features/converter/convert-controls.ts",
    "ui/src/renderer/src/features/downloader/download-controls.ts",
    "ui/src/renderer/src/features/transcript/TranscriptToolbar.tsx",
    "ui/src/renderer/src/registry/commandRegistry.ts",
    "ui/tests/unit/queue-card-slots.test.tsx",
    "ui/tests/unit/queue-toolbar.test.ts",
    "ui/tests/unit/queue-header-row.test.tsx",
    "ui/tests/unit/convert-page.test.ts",
    "ui/tests/unit/downloader-page.test.ts",
    "ui/tests/unit/help-card.test.ts",
    "ui/tests/unit/layout-canon.test.ts",
    "ui/tests/unit/queue-canon.test.ts",
    "ui/tests/e2e/convert-queue.test.ts",
    "ui/tests/e2e/download-queue.test.ts",
    "ui/tests/e2e/convert-queue-labels.test.ts",
    "ui/tests/e2e/electron-app.ts",
    "packages/core/src/avkit_core/services/conversion.py",
    "packages/core/src/avkit_core/services/download.py",
    "packages/core/src/avkit_core/services/settings.py",
    "tests/unit/test_services.py",
)
# Shared state files: read first, own lines only; copied for eol-check.py (both CRLF).
SHARED = {"docs/execution/metrics.md": "CRLF", ".agent/context/current-focus.md": "CRLF"}
PLAN_FILES = {
    f"{PLAN.as_posix()}/{n}": "LF"
    for n in (
        "implementation-plan.md", "task.md", "register-meu-155.py", "red-check.py", "identity.py",
        "issue-resolve.py", "eol-check.py", "baseline.ps1",
    )
}
# The approved plan and task (the plan's sha moved only by the Status line's execute words).
PLAN_SHA = {
    f"{PLAN.as_posix()}/implementation-plan.md": "63c96d393bf6ee45be8e2cb02d1b26a838a80345e321fc823d90d56e2e9f6c7d",
    f"{PLAN.as_posix()}/task.md": "032bb156cd47a0b1357c172e0ea01b536866c45d8c57b1ee0445145a49b186f6",
}
PLAN_REVIEW = ".agent/context/handoffs/2026-11-17-queue-pause-feedback-plan-critical-review.md"
# The qp88-probe.txt anchors, each counted once at row 0 (S2).
ANCHORS = (
    (TOOLBAR, "pause: 'Pause',"),
    (TOOLBAR, "disabled={!canPauseResume}"),
    (FIXTURE, "Pause</button>"),
    (CONVERT_CMDS, "export async function pauseConversion"),
    (CONVERT_CMDS, "export function deliverPalettePause"),
    (DOWNLOAD_CMDS, "export async function pauseDownload"),
    (DOWNLOAD_CMDS, "export function deliverPalettePause"),
    (CONVERT_PAGE, "const label = processorLabel(processorState)"),
    (CONVERT_PAGE, "'convert:pause':"),
    (DOWNLOAD_PAGE, "const label = processorLabel(processorState)"),
    (DOWNLOAD_PAGE, "'download:pause':"),
    ("docs/build-plan/06-gui.md", '<a id="ready-line-buffer-residual"></a>'),
    ("docs/build-plan/06-gui.md", "## Validation Commands"),
    (MATRIX, "| 6.20 | MEU-154 |"),
    (".agent/context/meu-status.yaml", "row_key: MEU-154"),
    (".agent/context/meu-status.yaml", "MEU-14\u2013154"),
    (".agent/context/known-issues.yaml", "id: QUEUE-PAUSE-NO-FEEDBACK"),
)
SCOPE_PREFIXES = (
    PLAN.as_posix() + "/",
    ".agent/context/handoffs/2026-11-17-queue-pause-feedback-",
    "docs/execution/reflections/2026-11-17-queue-pause-feedback-",
)
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
for p in (*MODIFIED, *READ_ONLY):
    if scope[p] in ("absent", "not-a-file"):
        problems.append(f"S2: scoped path missing: {p}")
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

# The row-0 content of every existing scoped, read-only, shared and plan file: eol-check.py's base
# and the execution review's delta base.
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
# mcp-server/, tests/ and tools/, secret names dropped before any stat or read.
listed = git("ls-files", "--cached", "--others", "--exclude-standard", "packages", "mcp-server", "tests", "tools")
skip_paths = [n for n in listed.decode("utf-8").splitlines() if n and not secret(n)]
skips = {p: sha(p) for p in skip_paths if pathlib.Path(p).is_file()}
(PLAN / "baseline-skip-hashes.json").write_bytes((json.dumps(skips, indent=2, sort_keys=True) + "\n").encode())
print("baseline-skip-hashes.json", len(skips), "files under packages/, mcp-server/, tests/ and tools/")

# Line endings, measured with Python bytes.
eols = {}
for p, want in {**KINDS, **{q: None for q in READ_ONLY}, **SHARED, **PLAN_FILES}.items():
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

# S2: the anchors, the registers, the grouping row, the 10 anchor, graphify.
for p, needle in ANCHORS:
    n = pathlib.Path(p).read_bytes().decode("utf-8").count(needle)
    print("anchor", p, "::", repr(needle), "->", n)
    if n != 1:
        problems.append(f"S2: anchor {needle!r} in {p} counted {n}, not 1")
status = pathlib.Path(".agent/context/meu-status.yaml").read_bytes().decode("utf-8")
n155 = status.count("row_key: MEU-155")
print("meu-status row_key: MEU-155 count", n155)
if n155:
    problems.append("S2: MEU-155 is already registered")
register = pathlib.Path(".agent/context/known-issues.yaml").read_bytes().decode("utf-8")
m = re.search(r"^  - id: QUEUE-PAUSE-NO-FEEDBACK\n(?:    .*\n)*?    status: (\S+)", register, re.M)
state = m.group(1) if m else None
print("issue QUEUE-PAUSE-NO-FEEDBACK status", state)
if state != "open":
    problems.append(f"S2: QUEUE-PAUSE-NO-FEEDBACK is {state}, not open")
row = [ln for ln in pathlib.Path(GROUPING).read_bytes().decode("utf-8").split("\n") if ln.startswith("| 88 |")]
print("grouping row 88", row)
if len(row) != 1 or "| proposed |" not in row[0]:
    problems.append("S2: grouping row 88 is not one proposed row")
residual = pathlib.Path(QUEUE_DOC).read_bytes().count(b"queue-pause-feedback-residual")
print("10 queue-pause-feedback-residual count", residual)
if residual:
    problems.append("S2: 10 already holds the queue-pause-feedback-residual anchor")
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
for n in ("register-meu-155.py", "red-check.py", "identity.py", "issue-resolve.py", "eol-check.py"):
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
& rtk proxy uv run --no-sync pytest tests/ --tb=short -q -rfE *> "$receipts/qp-base-py.txt"
Write-Output ("base suite py exit={0} receipt={1}/qp-base-py.txt" -f $LASTEXITCODE, $receipts)
Get-Content "$receipts/qp-base-py.txt" | Select-String -Pattern '^FAILED |^ERROR |passed|failed' | Select-Object -Last 12
# Vitest from pwsh in ui/ (memory: vitest-from-pwsh-not-bash); the gate's ui-tests excuse list reads it.
Push-Location 'P:\av-kit\ui'
& rtk proxy npm run test *> "$receipts/qp-base-ui.txt"
$uiCode = $LASTEXITCODE
Pop-Location
Write-Output ("base suite ui exit={0} receipt={1}/qp-base-ui.txt" -f $uiCode, $receipts)
Get-Content "$receipts/qp-base-ui.txt" | Select-String -Pattern 'Test Files|Tests ' | Select-Object -Last 4
# Session 77 RULE-3: the base tree's format and lint findings, recorded before any edit.
& rtk proxy uv run --no-sync ruff format --check packages/core/src/avkit_core/services/transcript.py *> "$receipts/qp-base-ruff-format.txt"
Write-Output ("base ruff format --check exit={0} receipt={1}/qp-base-ruff-format.txt" -f $LASTEXITCODE, $receipts)
Get-Content "$receipts/qp-base-ruff-format.txt" | Select-Object -Last 6
& rtk proxy npm --prefix ui run lint *> "$receipts/qp-base-ui-lint.txt"
Write-Output ("base ui-lint exit={0} receipt={1}/qp-base-ui-lint.txt" -f $LASTEXITCODE, $receipts)
Get-Content "$receipts/qp-base-ui-lint.txt" | Select-Object -Last 6

# 4. The plan-local checkers (Session 82 RULE-1 on the plan folder's Python).
$planPy = @(Get-ChildItem -Path $plan -Filter '*.py' | ForEach-Object { "$plan/$($_.Name)" })
Invoke-Step 'ruff-format-plan' (@('uv', 'run', '--no-sync', 'ruff', 'format', '--check') + $planPy)
Invoke-Step 'ruff-check-plan' (@('uv', 'run', '--no-sync', 'ruff', 'check') + $planPy)
Invoke-Step 'red-check-selftest' @('uv', 'run', '--no-sync', 'python', "$plan/red-check.py", '--selftest')
Invoke-Step 'identity-selftest' @('uv', 'run', '--no-sync', 'python', "$plan/identity.py", '--selftest')
Invoke-Step 'eol-check-selftest' @('uv', 'run', '--no-sync', 'python', "$plan/eol-check.py", '--selftest')
Invoke-Step 'eol-check-row0' @('uv', 'run', '--no-sync', 'python', "$plan/eol-check.py")
Invoke-Step 'register-meu-155-selftest' @('uv', 'run', '--no-sync', 'python', "$plan/register-meu-155.py", '--selftest')
Write-Output 'baseline: all steps exit 0'
exit 0
