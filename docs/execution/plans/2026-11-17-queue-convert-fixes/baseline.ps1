# Queue convert fixes baseline (task row 0; implementation-plan.md §Verification Plan 1).
# The shape of docs/execution/plans/2026-11-17-queue-pause-feedback/baseline.ps1, with this
# plan's steps: 1. the tree state (baseline.sha, baseline-dirty.txt); 2. the path-scoped
# baseline: baseline-scope.json over §Files Modified and the "Read, never changed" files, with
# the four new files and the row-3a probe file absent; baseline-dirty-hashes.json, which binds
# every dirty path outside this scope by hash; the row-0 copies (the eol-check.py and AC-157.13
# base) and baseline-eol.json; baseline-skip-hashes.json over packages/, mcp-server/, tests/ and
# tools/ (secret names dropped before any stat or read, Session 83 RULE-2); the S2 binding: the
# qc89-probe.txt anchors each counted once, MEU-156 and MEU-157 pending, both issues open,
# HELP-F1-BEFORE-LAZY-MOUNT-LOST absent, grouping row 89 proposed, no graphify graph, and the
# plan and task hashes as approved (the plan's only post-review change is the Status line);
# 3. the base Vitest suite (qc-base-ui.txt) and the base ui lint; their own failures are
# recorded, not fatal (no Python suite runs in this session: no Python file changes); 4. the
# plan-local selftests, eol-check.py over the fresh copies, and ruff format --check and ruff
# check on the plan folder's Python (Session 82 RULE-1). Every other step is fail-fast. Run
# from the repository root in pwsh.
$ErrorActionPreference = 'Stop'
$root = (git rev-parse --show-toplevel).Trim()
Set-Location $root
$plan = 'docs/execution/plans/2026-11-17-queue-convert-fixes'
$receipts = 'C:/Temp/av-kit/queue-convert-fixes'
$env:ELECTRON_RUN_AS_NODE = $null
$env:PYTHONIOENCODING = 'utf-8'
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:RECEIPTS_DIR = 'C:/Temp/av-kit'
$tmp = 'C:\Temp\av-kit\queue-convert-fixes\tmp'
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

PLAN = pathlib.Path("docs/execution/plans/2026-11-17-queue-convert-fixes")
OUT = pathlib.Path("C:/Temp/av-kit/queue-convert-fixes")
COPIES = OUT / "baseline-copies"
GROUPING = ".agent/context/grouping/2026-11-17-post-session-88-triage-session-grouping.md"
CONVERT_CONTROLS = "ui/src/renderer/src/features/converter/convert-controls.ts"
DOWNLOAD_CONTROLS = "ui/src/renderer/src/features/downloader/download-controls.ts"
CONVERT_CMDS = "ui/src/renderer/src/features/converter/convert-commands.ts"
DOWNLOAD_CMDS = "ui/src/renderer/src/features/downloader/download-commands.ts"
CONVERT_PAGE = "ui/src/renderer/src/features/converter/ConvertPage.tsx"
DOWNLOAD_PAGE = "ui/src/renderer/src/features/downloader/DownloaderPage.tsx"
ROUTER = "ui/src/renderer/src/router.tsx"
GUI_DOC = "docs/build-plan/06-gui.md"
QUEUE_DOC = "docs/build-plan/10-queue-card-ui.md"
AC977 = "ui/tests/e2e/convert-queue.test.ts"
STATUS = ".agent/context/meu-status.yaml"
REGISTER = ".agent/context/known-issues.yaml"
# §Files Modified, with each file's line-ending kind (implementation-plan.md §Files Modified).
MODIFIED = {
    CONVERT_CONTROLS: "MIXED",
    DOWNLOAD_CONTROLS: "CRLF",
    CONVERT_CMDS: "CRLF",
    CONVERT_PAGE: "CRLF",
    DOWNLOAD_PAGE: "MIXED",
    "ui/tests/unit/convert-page.behavior.test.ts": "CRLF",
    "ui/tests/unit/downloader-page.behavior.test.ts": "MIXED",
    "ui/tests/unit/convert-page.test.ts": "MIXED",
    "ui/tests/unit/downloader-page.test.ts": "MIXED",
    GUI_DOC: "CRLF",
    QUEUE_DOC: "CRLF",
    STATUS: "LF",
    ".agent/context/meu-registry.md": "LF",
    "docs/BUILD_PLAN.md": "LF",
    REGISTER: "LF",
    ".agent/context/known-issues.md": "LF",
    GROUPING: "LF",
}
NEW = {
    "ui/tests/unit/queue-cancel-paused.test.tsx": "LF",
    "ui/tests/unit/convert-browse-hold.test.ts": "LF",
    "ui/tests/e2e/convert-browse-mount.test.ts": "LF",
    "ui/tests/e2e/queue-cancel-paused.test.ts": "LF",
    # Row 3a's temporary probe: absent at row 0 and from row 3a's end on.
    "ui/tests/e2e/s89-chunk-delay-probe.test.ts": "LF",
}
# §Project files "Read, never changed": bound by hash; their kind is recorded, not expected.
READ_ONLY = (
    DOWNLOAD_CMDS,
    "ui/src/renderer/src/features/transcript/transcript-controls.ts",
    "ui/src/renderer/src/registry/commandRegistry.ts",
    "ui/src/renderer/src/registry/shortcuts.ts",
    ROUTER,
    "ui/src/renderer/src/components/queue/QueueCard.tsx",
    "ui/src/renderer/src/components/queue/QueueList.tsx",
    "ui/src/renderer/src/components/layout/AppShell.tsx",
    "ui/src/renderer/src/features/settings/settings-commands.ts",
    "ui/src/renderer/src/components/help/HelpCard.tsx",
    "ui/tests/unit/palette-curation.test.tsx",
    "ui/tests/unit/queue-pause-feedback.test.tsx",
    "ui/tests/unit/shortcuts.test.ts",
    "ui/tests/unit/common-shortcuts.test.tsx",
    "ui/tests/unit/gui-actions-audit.test.ts",
    "ui/tests/unit/fixtures/chord-table.ts",
    AC977,
    "ui/tests/e2e/download-queue.test.ts",
    "ui/tests/e2e/queue-pause-feedback.test.ts",
    "ui/tests/e2e/electron-app.ts",
    "ui/src/main/ipc.ts",
    "ui/src/main/preload.ts",
)
# Shared state files: read first, own lines only; copied for eol-check.py (both CRLF).
SHARED = {"docs/execution/metrics.md": "CRLF", ".agent/context/current-focus.md": "CRLF"}
PLAN_FILES = {
    f"{PLAN.as_posix()}/{n}": "LF"
    for n in (
        "implementation-plan.md", "task.md", "red-check.py", "identity.py", "issue-resolve.py",
        "eol-check.py", "baseline.ps1",
    )
}
# The approved plan and task (the plan's sha moved only by the Status line's execute words).
PLAN_SHA = {
    f"{PLAN.as_posix()}/implementation-plan.md": "400ce496fe83d139d584c39a8d1247197959643e8e84ff732ce7b67975ba5112",
    f"{PLAN.as_posix()}/task.md": "f9e17914ad667eeaa854c17fe5589cc61e431902b283e6a62e08ea46e3cb13eb",
}
PLAN_REVIEW = ".agent/context/handoffs/2026-11-17-queue-convert-fixes-plan-critical-review.md"
# The qc89-probe.txt anchors, each counted once at row 0 (S2).
ANCHORS = (
    (CONVERT_CONTROLS, "case 'cancel':"),
    (DOWNLOAD_CONTROLS, "case 'cancel':"),
    (CONVERT_CMDS, "export const CONVERT_BROWSE_EVENT"),
    (CONVERT_CMDS, "function navigateAndDeliver"),
    (CONVERT_CMDS, "export function deliverPaletteBrowse"),
    (CONVERT_CMDS, "export function deliverPaletteCancel"),
    (CONVERT_CMDS, "export async function cancelConversion"),
    (DOWNLOAD_CMDS, "export function deliverPaletteCancel"),
    (DOWNLOAD_CMDS, "export async function cancelDownload"),
    (CONVERT_PAGE, "window.addEventListener(CONVERT_BROWSE_EVENT, browseForFiles)"),
    (CONVERT_PAGE, "window.addEventListener(CONVERT_CONFIRM_EVENT, onConfirmRequest)"),
    (CONVERT_PAGE, "'convert:cancel':"),
    (DOWNLOAD_PAGE, "window.addEventListener(DOWNLOAD_CONFIRM_EVENT, onConfirmRequest)"),
    (DOWNLOAD_PAGE, "'download:cancel':"),
    (ROUTER, "lazyRouteComponent(() => import('./features/converter/ConvertPage'), 'ConvertPage')"),
    (GUI_DOC, '<a id="convert-browse-after-mount-residual"></a>'),
    (GUI_DOC, "waits for the Convert page before Ctrl+O"),
    (QUEUE_DOC, '<a id="queue-cancel-paused-residual"></a>'),
    (AC977, "AC-97.7"),
    (STATUS, "row_key: MEU-156"),
    (STATUS, "row_key: MEU-157"),
    (REGISTER, "id: QUEUE-CANCEL-WHILE-PAUSED-NO-EFFECT"),
    (REGISTER, "id: CONVERT-CTRL-O-BEFORE-MOUNT-FLAKE"),
    (GROUPING, "| 89 | `queue-convert-fixes` | MEU-156, MEU-157 | P3 | proposed | \u2014 |"),
)
SCOPE_PREFIXES = (
    PLAN.as_posix() + "/",
    ".agent/context/handoffs/2026-11-17-queue-convert-fixes-",
    "docs/execution/reflections/2026-11-17-queue-convert-fixes-",
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
if head != "9d6d172778763fdf61ba3af165dea0243a1e6f9f":
    problems.append(f"S2: HEAD is {head}, not the brief's 9d6d172")
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

# The row-0 content of every existing scoped, read-only, shared and plan file: eol-check.py's
# base, the row 1 and row 3 diffs' base and the execution review's delta base.
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
    if want is not None and kind != want and p not in NEW:
        problems.append(f"S2: {p} is {kind}, the plan says {want}")
(PLAN / "baseline-eol.json").write_bytes((json.dumps(eols, indent=2) + "\n").encode())
print("baseline-eol.json", len(eols), "paths")

# S2: the anchors, the registers, the grouping row, graphify, the approved plan and task.
for p, needle in ANCHORS:
    n = pathlib.Path(p).read_bytes().decode("utf-8").count(needle)
    print("anchor", p, "::", repr(needle), "->", n)
    if n != 1:
        problems.append(f"S2: anchor {needle!r} in {p} counted {n}, not 1")
status = pathlib.Path(STATUS).read_bytes().decode("utf-8")
for meu in ("MEU-156", "MEU-157"):
    m = re.search(r"^- row_key: " + meu + r"\n(?:  .*\n)*?  status: (\S+)", status, re.M)
    state = m.group(1) if m else None
    print("meu-status", meu, "status", state)
    if state != "pending":
        problems.append(f"S2: {meu} is {state}, not pending")
register = pathlib.Path(REGISTER).read_bytes().decode("utf-8")
for issue in ("QUEUE-CANCEL-WHILE-PAUSED-NO-EFFECT", "CONVERT-CTRL-O-BEFORE-MOUNT-FLAKE"):
    m = re.search(r"^  - id: " + issue + r"\n(?:    .*\n)*?    status: (\S+)", register, re.M)
    state = m.group(1) if m else None
    print("issue", issue, "status", state)
    if state != "open":
        problems.append(f"S2: {issue} is {state}, not open")
f1 = register.count("id: HELP-F1-BEFORE-LAZY-MOUNT-LOST")
print("issue HELP-F1-BEFORE-LAZY-MOUNT-LOST entries", f1)
if f1:
    problems.append("S2: HELP-F1-BEFORE-LAZY-MOUNT-LOST is already registered")
row = [ln for ln in pathlib.Path(GROUPING).read_bytes().decode("utf-8").split("\n") if ln.startswith("| 89 |")]
print("grouping row 89", row)
if len(row) != 1 or "| proposed |" not in row[0]:
    problems.append("S2: grouping row 89 is not one proposed row")
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
for n in ("red-check.py", "identity.py", "issue-resolve.py", "eol-check.py"):
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
Invoke-Step 'uv-sync' @('uv', 'sync', '--frozen', '--all-packages')
Invoke-Step 'record' @('uv', 'run', '--no-sync', 'python', "$receipts/baseline-record.py")

# 3. The base Vitest suite from pwsh in ui/ (memory: vitest-from-pwsh-not-bash); the gate's
# ui-tests excuse list reads it. Its failures are recorded, not fatal. The base ui lint is
# recorded the same way.
Push-Location 'P:\av-kit\ui'
& rtk proxy npm run test *> "$receipts/qc-base-ui.txt"
$uiCode = $LASTEXITCODE
Pop-Location
Write-Output ("base suite ui exit={0} receipt={1}/qc-base-ui.txt" -f $uiCode, $receipts)
Get-Content "$receipts/qc-base-ui.txt" | Select-String -Pattern 'Test Files|Tests |FAIL ' | Select-Object -Last 12
& rtk proxy npm --prefix ui run lint *> "$receipts/qc-base-ui-lint.txt"
Write-Output ("base ui-lint exit={0} receipt={1}/qc-base-ui-lint.txt" -f $LASTEXITCODE, $receipts)
Get-Content "$receipts/qc-base-ui-lint.txt" | Select-Object -Last 6

# 4. The plan-local checkers (Session 82 RULE-1 on the plan folder's Python).
$planPy = @(Get-ChildItem -Path $plan -Filter '*.py' | ForEach-Object { "$plan/$($_.Name)" })
Invoke-Step 'ruff-format-plan' (@('uv', 'run', '--no-sync', 'ruff', 'format', '--check') + $planPy)
Invoke-Step 'ruff-check-plan' (@('uv', 'run', '--no-sync', 'ruff', 'check') + $planPy)
Invoke-Step 'red-check-selftest' @('uv', 'run', '--no-sync', 'python', "$plan/red-check.py", '--selftest')
Invoke-Step 'identity-selftest' @('uv', 'run', '--no-sync', 'python', "$plan/identity.py", '--selftest')
Invoke-Step 'eol-check-selftest' @('uv', 'run', '--no-sync', 'python', "$plan/eol-check.py", '--selftest')
Invoke-Step 'eol-check-row0' @('uv', 'run', '--no-sync', 'python', "$plan/eol-check.py")
Write-Output 'baseline: all steps exit 0'
exit 0
