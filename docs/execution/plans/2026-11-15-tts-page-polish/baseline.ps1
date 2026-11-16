# TTS page polish baseline (task row 0; implementation-plan.md §Verification Plan 1).
# The shape of docs/execution/plans/2026-11-15-framework-small-syncs/baseline.ps1, with this plan's
# steps: 1. the tree state (baseline.sha, baseline-dirty.txt); 2. the path-scoped baseline
# (baseline-scope.json with every new path absent, baseline-readonly.json for the files this plan
# reads but must not change, baseline-dirty-hashes.json, and the BASE copies of every existing
# scope and read-only file in C:/Temp/av-kit/tts-page-polish/base/); 3. the S2 binding: nothing is
# compared with HEAD, because Sessions 75 to 79 may leave a shared file changed and uncommitted,
# and the content at row 0 is the baseline; the two home sections exist and hold no Delivered note;
# the code anchors hold; the three issues are open and MEU-149 and MEU-150 pending;
# 4. uv sync, the base Python suite (tpp-base-py.txt) and the base UI suite (tpp-base-ui.txt);
# their own failures are recorded, not fatal: the session gate excuses only the Python ids this
# receipt shows failing, and the UI suite excuses nothing; 5. the plan-local selftests.
# Every other step is fail-fast. Run from the repository root in pwsh.
$ErrorActionPreference = 'Stop'
$root = (git rev-parse --show-toplevel).Trim()
Set-Location $root
$plan = 'docs/execution/plans/2026-11-15-tts-page-polish'
$receipts = 'C:/Temp/av-kit/tts-page-polish'
$env:ELECTRON_RUN_AS_NODE = $null
$env:PYTHONIOENCODING = 'utf-8'
$env:RECEIPTS_DIR = 'C:/Temp/av-kit'
$userTmp = $env:TMP
$userTemp = $env:TEMP
$tmp = 'C:\Temp\av-kit\tts-page-polish\tmp'
New-Item -ItemType Directory -Force -Path $tmp | Out-Null

function Invoke-Step([string]$Id, [string[]]$Argv) {
    & rtk proxy @Argv
    $code = $LASTEXITCODE
    Write-Output ("baseline step {0} exit={1}" -f $Id, $code)
    if ($code -ne 0) { exit $code }
}

# 1-3. Tree state, path-scoped baseline and the S2 binding, in Python so every file is read and
# written as bytes.
$record = @'
import hashlib, json, pathlib, re, subprocess, sys

PLAN = pathlib.Path("docs/execution/plans/2026-11-15-tts-page-polish")
BASE = pathlib.Path("C:/Temp/av-kit/tts-page-polish/base")
SVC_DOC = "docs/build-plan/03-service-layer.md"
GUI_DOC = "docs/build-plan/06-gui.md"
GROUPING = ".agent/context/grouping/2026-11-15-post-rc3-triage-residuals-session-grouping.md"
PRODUCT = (
    "ui/src/renderer/src/features/tts/tts-controls.ts",
    "ui/src/renderer/src/features/tts/TTSPage.tsx",
    "ui/tests/unit/tts-page.test.ts",
    "ui/tests/unit/tts-page.behavior.test.ts",
    "ui/tests/unit/queue-primitives.test.ts",
    "tests/unit/test_tts_output_name.py",
)
READ_ONLY = (
    "packages/core/src/avkit_core/domain/tts.py",
    "packages/core/src/avkit_core/services/tts.py",
    "ui/src/renderer/src/components/ui/StatusChip.tsx",
    "ui/src/renderer/src/components/ui/ProgressBar.tsx",
    "ui/src/renderer/src/lib/queue/status-tokens.ts",
    "ui/src/renderer/src/styles.css",
    "ui/tests/e2e/test-ids.ts",
    "ui/tests/e2e/tts-generate.test.ts",
    "openapi.committed.json",
)
REGISTERS = (
    SVC_DOC,
    GUI_DOC,
    ".agent/context/known-issues.yaml",
    ".agent/context/known-issues.md",
    ".agent/context/meu-status.yaml",
    ".agent/context/meu-registry.md",
    "docs/BUILD_PLAN.md",
    GROUPING,
)
EXISTING = PRODUCT + REGISTERS
NEW = ("ui/tests/unit/tts-pill-contrast.test.ts", PLAN.as_posix() + "/human-check.md")
SCOPE_PREFIXES = (
    PLAN.as_posix() + "/",
    ".agent/context/handoffs/2026-11-15-tts-page-polish-",
    "docs/execution/reflections/2026-11-15-tts-page-polish-",
)
SHARED = ("docs/execution/metrics.md", ".agent/context/current-focus.md")
ISSUES = ("TTS-STATUS-PILL-BELOW-AA-CONTRAST", "TTS-AUDIO-RANDOM-FILE-NAMES", "TTS-SEGMENTS-LABEL-IS-PROGRESS-SCALE")
# Each home section runs from its anchor to the next heading of its own level or higher.
HOMES = (
    (SVC_DOC, '<a id="tts-output-names-progress-residual"></a>', "\n## What this layer must not do"),
    (GUI_DOC, '<a id="tts-status-pill-contrast-residual"></a>', '\n<a id="settings-draft-baseline-residual"></a>'),
)
WIREFRAME = "68%  \u00b7  Segment 34/50     \u2502"
# D-955: the wireframe's output example predates the rc.3 F5 name; row 6 redraws it at the same width.
WIREFRAME_OUTPUT = "Last output: speech_output_2026-05-30.mp3    ["
# The ProgressBar spec's label example; row 6 changes it so no segment wording is left in 06.
PROGRESS_SPEC = '  label?: string;   // e.g. "45.2%" or "Segment 34/50"'
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
readonly = {p: sha(p) for p in READ_ONLY}
for p, v in readonly.items():
    if v in ("absent", "not-a-file"):
        problems.append(f"read-only path missing: {p}")
(PLAN / "baseline-readonly.json").write_bytes((json.dumps(readonly, indent=2) + "\n").encode())
print("baseline-readonly.json", len(readonly), "paths")

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
for p in SHARED + REGISTERS:
    print("bound by content", p, "dirty" if p in dirty else "clean at HEAD", sha(p)[:16])

# The row-0 content of every existing scope and read-only file: the execution review's diff base.
for p in EXISTING + READ_ONLY:
    dest = BASE / p
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(pathlib.Path(p).read_bytes())
print("BASE", len(EXISTING + READ_ONLY), "row-0 copies under", BASE.as_posix())

# Bound by content, never by HEAD: a file an earlier session left uncommitted is this plan's baseline.
for p in PRODUCT + READ_ONLY:
    print("row-0 content", p, "dirty at row 0" if p in dirty else "clean at HEAD", sha(p)[:16])

def section(text, start, end):
    at = text.find(start)
    stop = text.find(end, at + 1) if at >= 0 else -1
    return text[at:stop] if at >= 0 and stop > at else None

for path, start, end in HOMES:
    now = section(pathlib.Path(path).read_bytes().decode("utf-8"), start, end)
    if now is None:
        problems.append(f"S2: the home section {start} in {path} is missing")
    elif "Delivered" in now:
        problems.append(f"S2: the home section {start} in {path} already holds a Delivered note")
    else:
        print("S2 home section", start, "found, no Delivered note;", now.count("\n"), "lines")
gui = pathlib.Path(GUI_DOC).read_bytes().decode("utf-8")
if gui.count(WIREFRAME) != 1:
    problems.append(f"S2: {GUI_DOC} holds the TTS wireframe's Segment line {gui.count(WIREFRAME)} times, not once")
if gui.count(WIREFRAME_OUTPUT) != 1:
    problems.append(f"S2: {GUI_DOC} holds the TTS wireframe's Last output line {gui.count(WIREFRAME_OUTPUT)} times, not once")
if gui.count(PROGRESS_SPEC) != 1:
    problems.append(f"S2: {GUI_DOC} holds the ProgressBar label example {gui.count(PROGRESS_SPEC)} times, not once")
controls = pathlib.Path(PRODUCT[0]).read_bytes().decode("utf-8")
page = pathlib.Path(PRODUCT[1]).read_bytes().decode("utf-8")
for label, ok in (
    ("tts-controls.ts exports STATUS_COLORS", "export const STATUS_COLORS" in controls),
    ("tts-controls.ts has no progressLabel, progressFraction or TTS_STATUS_TONE", all(n not in controls for n in ("progressLabel", "progressFraction", "TTS_STATUS_TONE"))),
    ("TTSPage.tsx prints Segments", "Segments {job?.segments_done ?? 0}/{job?.segments_total ?? 0}" in page),
    ("TTSPage.tsx has no tts-status-pill", "tts-status-pill" not in page),
    ("TTSPage.tsx defaults a missing status with ??", "const status = job?.status ?? 'Idle'" in page),
    ("TTSPage.tsx run bar value", "value={segmentsTotal > 0 ? segmentsDone / segmentsTotal : 0}" in page),
):
    print("S2 anchor", label, ok)
    if not ok:
        problems.append(f"S2: anchor failed: {label}")

register = pathlib.Path(".agent/context/known-issues.yaml").read_bytes().decode("utf-8")
for issue in ISSUES:
    m = re.search(r"^  - id: " + re.escape(issue) + r"\n(?:    .*\n)*?    status: (\S+)", register, re.M)
    state = m.group(1) if m else None
    print("issue", issue, "status", state)
    if state != "open":
        problems.append(f"S2: {issue} is {state}, not open")
status = pathlib.Path(".agent/context/meu-status.yaml").read_bytes().decode("utf-8")
for meu in ("MEU-149", "MEU-150"):
    m = re.search(r"^- row_key: " + meu + r"\n(?:  .*\n)*?  status: (\S+)", status, re.M)
    state = m.group(1) if m else None
    print("meu", meu, "status", state)
    if state != "pending":
        problems.append(f"S2: {meu} is {state}, not pending")
row = [ln for ln in pathlib.Path(GROUPING).read_bytes().decode("utf-8").split("\n") if ln.startswith("| 80 |")]
print("grouping row 80", row)
if len(row) != 1 or "| proposed |" not in row[0]:
    problems.append("S2: grouping §6 row 80 is not one proposed row")
for p in problems:
    print("PROBLEM:", p)
sys.exit(1 if problems else 0)
'@
New-Item -ItemType Directory -Force -Path $receipts | Out-Null
Set-Content -Path "$receipts/baseline-record.py" -Value $record -Encoding utf8
Invoke-Step 'record' @('uv', 'run', 'python', "$receipts/baseline-record.py")

# 4. Install from the lock; the base suites with TMP and TEMP outside the user profile.
Invoke-Step 'uv-sync' @('uv', 'sync', '--frozen', '--all-packages')
$env:TMP = $tmp
$env:TEMP = $tmp
& rtk proxy uv run --no-sync pytest tests/ --tb=short -q -rfE *> "$receipts/tpp-base-py.txt"
Write-Output ("base suite py exit={0} receipt={1}/tpp-base-py.txt" -f $LASTEXITCODE, $receipts)
Get-Content "$receipts/tpp-base-py.txt" | Select-String -Pattern '^FAILED |^ERROR |passed|failed' | Select-Object -Last 12
$env:TMP = $userTmp
$env:TEMP = $userTemp
# Vitest from pwsh in ui/ (memory: vitest-from-pwsh-not-bash).
Push-Location 'P:\av-kit\ui'
& rtk proxy npm run test *> "$receipts/tpp-base-ui.txt"
$uiCode = $LASTEXITCODE
Pop-Location
Write-Output ("base suite ui exit={0} receipt={1}/tpp-base-ui.txt" -f $uiCode, $receipts)
Get-Content "$receipts/tpp-base-ui.txt" | Select-String -Pattern 'Test Files|Tests ' | Select-Object -Last 4

# 5. The plan-local checkers.
Invoke-Step 'red-check-selftest' @('uv', 'run', '--no-sync', 'python', "$plan/red-check.py", '--selftest')
Invoke-Step 'identity-selftest' @('uv', 'run', '--no-sync', 'python', "$plan/identity.py", '--selftest')
Invoke-Step 'dev-app-procs-selftest' @('uv', 'run', '--no-sync', 'python', "$plan/dev-app-procs.py", '--selftest')
Write-Output 'baseline: all steps exit 0'
exit 0
