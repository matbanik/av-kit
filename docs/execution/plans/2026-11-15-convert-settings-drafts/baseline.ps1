# Convert settings drafts baseline (task row 0; implementation-plan.md §Verification Plan 1).
# The shape of docs/execution/plans/2026-11-15-tts-page-polish/baseline.ps1, with this plan's
# steps: 1. the tree state (baseline.sha, baseline-dirty.txt); 2. the path-scoped baseline
# (baseline-scope.json over §Files Modified and §Project files "Read, never changed", with the
# three new test files absent; baseline-dirty-hashes.json; the row-0 copies in
# C:/Temp/av-kit/convert-settings-drafts/baseline-copies/ and baseline-predecessor.diff there;
# baseline-eol.json; baseline-skip-hashes.json); the S2 binding: nothing is compared with HEAD,
# the content at row 0 is the baseline, the row-0 anchors hold, the two home sections hold no
# Session 81 note, the five issues are open, MEU-151 and MEU-152 pending and grouping row 81
# proposed; 3. uv sync, the base Python suite (cs81-base-py.txt) and the base Vitest suite
# (cs81-base-ui.txt), and the Session 77 RULE-3 base checks (ruff format --check on
# services/conversion.py, ui-lint); their own failures are recorded, not fatal; 4. the plan-local
# selftests. Every other step is fail-fast. Run from the repository root in pwsh.
$ErrorActionPreference = 'Stop'
$root = (git rev-parse --show-toplevel).Trim()
Set-Location $root
$plan = 'docs/execution/plans/2026-11-15-convert-settings-drafts'
$receipts = 'C:/Temp/av-kit/convert-settings-drafts'
$env:ELECTRON_RUN_AS_NODE = $null
$env:PYTHONIOENCODING = 'utf-8'
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:RECEIPTS_DIR = 'C:/Temp/av-kit'
$userTmp = $env:TMP
$userTemp = $env:TEMP
$tmp = 'C:\Temp\av-kit\convert-settings-drafts\tmp'
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

PLAN = pathlib.Path("docs/execution/plans/2026-11-15-convert-settings-drafts")
OUT = pathlib.Path("C:/Temp/av-kit/convert-settings-drafts")
COPIES = OUT / "baseline-copies"
GUI_DOC = "docs/build-plan/06-gui.md"
VIDEO_DOC = "docs/build-plan/08-video-conversion.md"
GROUPING = ".agent/context/grouping/2026-11-15-post-rc3-triage-residuals-session-grouping.md"
CAPTURE_HOOK = "ui/src/renderer/src/features/capture/useCaptureSettings.ts"
CONVERT_PAGE = "ui/src/renderer/src/features/converter/ConvertPage.tsx"
CONVERT_TIME = "ui/src/renderer/src/features/converter/convert-time.ts"
CONVERT_CONTROLS = "ui/src/renderer/src/features/converter/convert-controls.ts"
QUEUE_CARD = "ui/src/renderer/src/components/queue/QueueCard.tsx"
SERVICE = "packages/core/src/avkit_core/services/conversion.py"
CAPTURE_BEHAVIOR = "ui/tests/unit/capture-page.behavior.test.ts"
CONVERT_BEHAVIOR = "ui/tests/unit/convert-page.behavior.test.ts"
CONTROLS_TEST = "ui/tests/unit/convert-controls.test.ts"
SERVICE_TEST = "tests/unit/test_conversion_service.py"
E2E_CONVERT = "ui/tests/e2e/convert-queue.test.ts"
E2E_CAPTURE = "ui/tests/e2e/capture-inbox.test.ts"
SLOT = "ui/tests/unit/fixtures/queue-slot-baseline.json"
# §Files Modified, with each file's line-ending kind; None for a regenerated or tool-written file
# whose kind is LF too but which a tool, not this plan, writes.
MODIFIED = {
    CAPTURE_HOOK: "CRLF",
    CONVERT_PAGE: "CRLF",
    CONVERT_TIME: "CRLF",
    CONVERT_CONTROLS: "MIXED",
    QUEUE_CARD: "CRLF",
    SERVICE: "CRLF",
    CAPTURE_BEHAVIOR: "CRLF",
    CONVERT_BEHAVIOR: "CRLF",
    CONTROLS_TEST: "CRLF",
    GUI_DOC: "CRLF",
    VIDEO_DOC: "LF",
    ".agent/context/known-issues.yaml": "LF",
    ".agent/context/known-issues.md": "LF",
    ".agent/context/meu-status.yaml": "LF",
    ".agent/context/meu-registry.md": "LF",
    "docs/BUILD_PLAN.md": "LF",
    GROUPING: "LF",
}
NEW = {
    "ui/tests/unit/capture-settings-draft.behavior.test.ts": "LF",
    "ui/tests/unit/convert-queue-labels.test.ts": "LF",
    "tests/unit/test_convert_cut_encoder.py": "LF",
}
# §Project files "Read, never changed".
READ_ONLY = {SLOT: "CRLF", E2E_CONVERT: "LF", E2E_CAPTURE: "LF", SERVICE_TEST: "CRLF"}
KINDS = {**MODIFIED, **NEW, **READ_ONLY}
MIXED_BARE_LF = 8
SCOPE_PREFIXES = (
    PLAN.as_posix() + "/",
    ".agent/context/handoffs/2026-11-15-convert-settings-drafts-",
    "docs/execution/reflections/2026-11-15-convert-settings-drafts-",
)
SHARED = ("docs/execution/metrics.md", ".agent/context/current-focus.md")
ISSUES = (
    "SETTINGS-DRAFT-STALE-BASELINE",
    "CONVERT-ADVANCED-EDIT-REPLACED",
    "CONVERT-CUT-TIME-RAW-MS",
    "CONVERT-POSITIONS-NOT-RENUMBERED",
    "CONVERT-CUT-ENCODER-LABEL",
)
# implementation-plan.md §Verification Plan 1, the row-0 anchor table: each at least once.
ANCHORS = {
    CAPTURE_HOOK: ("patchForm", "parseSettingsPut('capture', form)", "CAPTURE_SETTINGS_KEY"),
    CONVERT_PAGE: ("presetTouched", "selectPreset", "position: item.queue_position"),
    CONVERT_TIME: ("export function parseConvertTime",),
    CONVERT_CONTROLS: ("${row.in_ms}\u2013${row.out_ms}", "convertMetaSegments"),
    QUEUE_CARD: ("Waiting - position ${String(job.position)} in queue",),
    SERVICE: ("def _dispatch", "if job.kind is not ConversionKind.Extract:"),
    CAPTURE_BEHAVIOR: (
        "describe('MEU-39 capture GUI runtime (exec r1 F1 F2 F5)'",
        "AC-39.4 AC-39.15 Capture page Save PUTs capture settings only when dirty",
        "AC-57.1 header row",
    ),
    CONVERT_BEHAVIOR: (
        "describe('MEU-33 convert GUI runtime (exec r1 F1\u2013F4)'",
        "async function renderConvertBeforeSettings(",
        "async function savedSettingChangesTo(",
        "queue_position: row.position",
    ),
    CONTROLS_TEST: ("'1000\u20134500'", "AC-45.17 convertMetaSegments"),
    SERVICE_TEST: (
        "class RecordingMedia",
        "def _stack(",
        "def _write_clip(",
        "def _nvidia_caps(",
        "def _process(",
        "class GpuCountingMedia(",
        "def test_ac_112_4_",
        "def test_ac_123_6_",
        "def test_ac_123_7_",
        "def test_ac_123_8_",
    ),
    E2E_CONVERT: ("test('W8-1 ", "test('W8-7 "),
    E2E_CAPTURE: ("test('W9-3 ", "test('AC-57.10 header", "test('AC-67.24 "),
    SLOT: ("Waiting - position 1 in queue",),
    GUI_DOC: ('<a id="settings-draft-baseline-residual"></a>',),
    VIDEO_DOC: ('<a id="convert-queue-labels-residual"></a>',),
}
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

scope = {p: sha(p) for p in KINDS}
for p in NEW:
    if scope[p] != "absent":
        problems.append(f"S2: new test file already exists: {p}")
for p in (*MODIFIED, *READ_ONLY):
    if scope[p] in ("absent", "not-a-file"):
        problems.append(f"S2: scoped path missing: {p}")
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
for p in sorted(hashes):
    print("  bound by hash", p, hashes[p][:16])
for p in SHARED:
    print("bound by content (read first, own lines only)", p, "dirty" if p in dirty else "clean at HEAD", sha(p)[:16])

# The row-0 content of every existing scoped file: the execution review's delta base.
copied = 0
for p in KINDS:
    if scope[p] in ("absent", "not-a-file"):
        continue
    dest = COPIES / p
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(pathlib.Path(p).read_bytes())
    copied += 1
print("baseline-copies", copied, "row-0 copies under", COPIES.as_posix())
predecessor = [p for p in KINDS if p in dirty]
diff = git("diff", "HEAD", "--", *predecessor) if predecessor else b""
(OUT / "baseline-predecessor.diff").write_bytes(diff)
print("baseline-predecessor.diff", len(predecessor), "scoped paths dirty at row 0:", predecessor, len(diff), "bytes")
for p in KINDS:
    print("row-0 content", p, "dirty at row 0" if p in dirty else ("absent" if scope[p] == "absent" else "clean at HEAD"), scope[p][:16])

# Line endings, measured with Python bytes.
eols = {}
for p, want in KINDS.items():
    if scope[p] == "absent":
        eols[p] = {"kind": "absent", "expected": want, "crlf": 0, "bare_lf": 0}
        continue
    kind, crlf, bare = eol(pathlib.Path(p).read_bytes())
    eols[p] = {"kind": kind, "expected": want, "crlf": crlf, "bare_lf": bare}
    print("eol", kind, "crlf", crlf, "bare_lf", bare, p)
    if kind != want:
        problems.append(f"S2: {p} is {kind}, the plan says {want}")
    if want == "MIXED" and bare != MIXED_BARE_LF:
        problems.append(f"S2: {p} has {bare} bare-LF lines, the plan says {MIXED_BARE_LF}")
if eols[CONVERT_CONTROLS]["kind"] == "MIXED":
    lines = pathlib.Path(CONVERT_CONTROLS).read_bytes().split(b"\n")
    bare_at = [n + 1 for n, ln in enumerate(lines[:-1]) if not ln.endswith(b"\r")]
    eols[CONVERT_CONTROLS]["bare_lf_lines"] = bare_at
    print("convert-controls.ts bare-LF lines", bare_at)
(PLAN / "baseline-eol.json").write_bytes((json.dumps(eols, indent=2) + "\n").encode())
print("baseline-eol.json", len(eols), "paths")

skip_paths = [n for n in git("ls-files", "--cached", "--others", "--exclude-standard", "packages/api", "mcp-server").decode().splitlines() if n]
skips = {p: sha(p) for p in skip_paths if pathlib.Path(p).is_file()}
(PLAN / "baseline-skip-hashes.json").write_bytes((json.dumps(skips, indent=2, sort_keys=True) + "\n").encode())
print("baseline-skip-hashes.json", len(skips), "packages/api and mcp-server files")

# The row-0 anchors, in the row-0 content; never compared with HEAD.
for p, anchors in ANCHORS.items():
    text = pathlib.Path(p).read_bytes().decode("utf-8")
    for a in anchors:
        n = text.count(a)
        print("anchor", p, repr(a), n)
        if n < 1:
            problems.append(f"S2: anchor missing in {p}: {a!r}")

# The two home sections hold no Session 81 note yet.
for path in (GUI_DOC, VIDEO_DOC):
    n = pathlib.Path(path).read_bytes().count(b"Delivered (Session 81)")
    print("home", path, "Delivered (Session 81) notes:", n)
    if n:
        problems.append(f"S2: {path} already holds a Session 81 Delivered note")

register = pathlib.Path(".agent/context/known-issues.yaml").read_bytes().decode("utf-8")
for issue in ISSUES:
    m = re.search(r"^  - id: " + re.escape(issue) + r"\n(?:    .*\n)*?    status: (\S+)", register, re.M)
    state = m.group(1) if m else None
    print("issue", issue, "status", state)
    if state != "open":
        problems.append(f"S2: {issue} is {state}, not open")
status = pathlib.Path(".agent/context/meu-status.yaml").read_bytes().decode("utf-8")
for meu in ("MEU-151", "MEU-152"):
    m = re.search(r"^- row_key: " + meu + r"\n(?:  .*\n)*?  status: (\S+)", status, re.M)
    state = m.group(1) if m else None
    print("meu", meu, "status", state)
    if state != "pending":
        problems.append(f"S2: {meu} is {state}, not pending")
row = [ln for ln in pathlib.Path(GROUPING).read_bytes().decode("utf-8").split("\n") if ln.startswith("| 81 |")]
print("grouping row 81", row)
if len(row) != 1 or "| proposed |" not in row[0]:
    problems.append("S2: grouping §6 row 81 is not one proposed row")
graphs = [g for g in ("graphify-out", "graphify-out-research") if pathlib.Path(g).exists()]
print("graphify graphs", graphs)
if graphs:
    problems.append(f"S1: a graphify graph exists: {graphs}")
for p in problems:
    print("PROBLEM:", p)
sys.exit(1 if problems else 0)
'@
New-Item -ItemType Directory -Force -Path $receipts | Out-Null
Set-Content -Path "$receipts/baseline-record.py" -Value $record -Encoding utf8
Invoke-Step 'record' @('uv', 'run', 'python', "$receipts/baseline-record.py")

# 3. Install from the lock; the base suites with TMP and TEMP outside the user profile.
Invoke-Step 'uv-sync' @('uv', 'sync', '--frozen', '--all-packages')
$env:TMP = $tmp
$env:TEMP = $tmp
& rtk proxy uv run --no-sync pytest tests/ --tb=short -q -rfE *> "$receipts/cs81-base-py.txt"
Write-Output ("base suite py exit={0} receipt={1}/cs81-base-py.txt" -f $LASTEXITCODE, $receipts)
Get-Content "$receipts/cs81-base-py.txt" | Select-String -Pattern '^FAILED |^ERROR |passed|failed' | Select-Object -Last 12
$env:TMP = $userTmp
$env:TEMP = $userTemp
# Vitest from pwsh in ui/ (memory: vitest-from-pwsh-not-bash).
Push-Location 'P:\av-kit\ui'
& rtk proxy npm run test *> "$receipts/cs81-base-ui.txt"
$uiCode = $LASTEXITCODE
Pop-Location
Write-Output ("base suite ui exit={0} receipt={1}/cs81-base-ui.txt" -f $uiCode, $receipts)
Get-Content "$receipts/cs81-base-ui.txt" | Select-String -Pattern 'Test Files|Tests ' | Select-Object -Last 4
# Session 77 RULE-3: the base tree's format and lint findings, recorded before any edit.
& rtk proxy uv run --no-sync ruff format --check packages/core/src/avkit_core/services/conversion.py *> "$receipts/cs81-base-ruff-format.txt"
Write-Output ("base ruff format --check exit={0} receipt={1}/cs81-base-ruff-format.txt" -f $LASTEXITCODE, $receipts)
Get-Content "$receipts/cs81-base-ruff-format.txt" | Select-Object -Last 4
& rtk proxy npm --prefix ui run lint *> "$receipts/cs81-base-ui-lint.txt"
Write-Output ("base ui-lint exit={0} receipt={1}/cs81-base-ui-lint.txt" -f $LASTEXITCODE, $receipts)
Get-Content "$receipts/cs81-base-ui-lint.txt" | Select-Object -Last 6

# 4. The plan-local checkers.
Invoke-Step 'red-check-selftest' @('uv', 'run', '--no-sync', 'python', "$plan/red-check.py", '--selftest')
Invoke-Step 'identity-selftest' @('uv', 'run', '--no-sync', 'python', "$plan/identity.py", '--selftest')
Invoke-Step 'dev-app-procs-selftest' @('uv', 'run', '--no-sync', 'python', "$plan/dev-app-procs.py", '--selftest')
Write-Output 'baseline: all steps exit 0'
exit 0
