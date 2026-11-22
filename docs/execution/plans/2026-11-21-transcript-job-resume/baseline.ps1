# Session 101 transcript-job-resume baseline (task row 0; implementation-plan.md §Verification Plan 1).
# The shape of docs/execution/plans/2026-11-20-help-quick-start/baseline.ps1. Its steps:
# 1. uv sync --frozen --offline --all-packages (S7 on a held file);
# 2. the record: HEAD (recorded, never compared with a pinned commit), git status and git
#    worktree list; baseline.sha and baseline-dirty.txt; baseline-scope.json over §Files Modified
#    (each existing path by hash, each new path absent), the "Read, never changed" files (hash)
#    and the shared files (current-focus.md, metrics.md, known-issues.yaml and .md: an object
#    {"kind": "shared", "sha256": ...}); baseline-dirty-hashes.json, which binds every dirty path
#    outside this scope by hash; the row-0 copies under R/baseline-copies (eol-check.py's and
#    row-check.py's base); baseline-mcp-hashes.json (every tracked or untracked, not-ignored file
#    under mcp-server/); baseline-eol.json; baseline-pins.json (the §Test pins files' hashes, and
#    the top-level ast sources of test_services.py and test_transcript_metadata.py through
#    row-check.py's top_level_sources); baseline-citations.txt (each §Verification Plan 1 step 4
#    anchor found once by text, its line recorded); the free ids (DECLARED_NEW, AC-163.,
#    D-1358 to D-1399);
# 3. one host-load sample (host-wait.py; the 50 % limit);
# 4. the base receipts: full Vitest (pwsh in ui/), full pytest, and the MCP suite (pwsh in
#    mcp-server/), failures recorded, not fatal;
# 5. the plan-local checkers' selftests, eol-check.py over the fresh copies, and ruff on this
#    folder's Python (Session 82 RULE-1).
# Every step except 4 is fail-fast. The scope walk drops .mcp.json, mcp-token.txt, .claude.json,
# .env, .env.*, .claude/settings.local.json and .agent/fleet/hub before any stat or read. Run from
# the repository root in pwsh.
$ErrorActionPreference = 'Stop'
$root = (git rev-parse --show-toplevel).Trim()
Set-Location $root
$plan = 'docs/execution/plans/2026-11-21-transcript-job-resume'
$receipts = 'C:/Temp/av-kit/2026-11-21-transcript-job-resume'
Remove-Item Env:ELECTRON_RUN_AS_NODE -ErrorAction SilentlyContinue
$env:PYTHONIOENCODING = 'utf-8'
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:RECEIPTS_DIR = 'C:/Temp/av-kit'
$tmp = 'C:\Temp\av-kit\2026-11-21-transcript-job-resume\tmp'
New-Item -ItemType Directory -Force -Path $tmp | Out-Null
$env:TMP = $tmp
$env:TEMP = $tmp

function Invoke-Step([string]$Id, [string[]]$Argv) {
    & rtk proxy @Argv
    $code = $LASTEXITCODE
    Write-Output ("baseline step {0} exit={1}" -f $Id, $code)
    if ($code -ne 0) { exit $code }
}

# 2. The record, in Python so every file is read and written as bytes.
$record = @'
import hashlib, importlib.util, json, pathlib, subprocess, sys

PLAN = pathlib.Path("docs/execution/plans/2026-11-21-transcript-job-resume")
OUT = pathlib.Path("C:/Temp/av-kit/2026-11-21-transcript-job-resume")
COPIES = OUT / "baseline-copies"
SLUG = "2026-11-21-transcript-job-resume"
T = "ui/src/renderer/src/features/transcript"
E2E = "ui/tests/e2e"
UNIT = "ui/tests/unit"
CONTROLS = f"{T}/transcript-controls.ts"
CARD = f"{T}/transcript-card.ts"
COMMANDS = f"{T}/transcript-commands.ts"
PAGE = f"{T}/TranscriptPage.tsx"
SERVICE = "packages/core/src/avkit_core/services/transcript.py"
SERVICES = "tests/unit/test_services.py"
METADATA = "tests/unit/test_transcript_metadata.py"
SETTINGS_PY = "packages/core/src/avkit_core/services/settings.py"
SETTINGS_TS = "mcp-server/src/toolsets/settings.ts"
GUI = "docs/build-plan/06-gui.md"
SERVICE_LAYER = "docs/build-plan/03-service-layer.md"
INDEX = "docs/build-plan/gui-actions-index.md"
GROUPING = f".agent/context/grouping/{SLUG}-session-grouping.md"
ENGINE = "packages/infrastructure/src/avkit_infra/database/engine.py"
QUEUE_E2E = f"{E2E}/transcript-queue.test.ts"
CANCEL_E2E = f"{E2E}/queue-cancel-paused.test.ts"
HANDOFF = f".agent/context/handoffs/{SLUG}-MEU-163-handoff.md"
IMPL_REVIEW = f".agent/context/handoffs/{SLUG}-implementation-critical-review.md"
PLAN_REVIEW = f".agent/context/handoffs/{SLUG}-plan-critical-review.md"
REFLECTION = f"docs/execution/reflections/{SLUG}-reflection.md"
MEU_STATUS = ".agent/context/meu-status.yaml"
# §Files Modified that exist at row 0, with each file's line-ending kind (measured at plan time).
MODIFIED = {
    CONTROLS: "LF",
    CARD: "CRLF",
    COMMANDS: "LF",
    PAGE: "CRLF",
    SERVICE: "LF",
    SERVICES: "CRLF",
    METADATA: "LF",
    SETTINGS_PY: "CRLF",
    SETTINGS_TS: "CRLF",
    GUI: "CRLF",
    SERVICE_LAYER: "CRLF",
    INDEX: "CRLF",
    "docs/build-plan/10-queue-card-ui.md": "CRLF",
    MEU_STATUS: "LF",
    ".agent/context/meu-registry.md": "LF",
    "docs/BUILD_PLAN.md": "LF",
    GROUPING: "LF",
}
# Shared: another session may write these; recorded with their hash, and the row that writes one
# re-reads it just before the edit.
SHARED = {
    ".agent/context/current-focus.md": "CRLF",
    "docs/execution/metrics.md": "CRLF",
    ".agent/context/known-issues.yaml": "CRLF",
    ".agent/context/known-issues.md": "CRLF",
}
# §Files Modified that are new, and the session's own new documents: each must be absent.
NEW = (
    "tests/unit/test_transcript_defaults.py",
    "mcp-server/tests/transcript-defaults.test.ts",
    "tests/transcript_paused_fixture.py",
    f"{UNIT}/transcript-job-resume.test.tsx",
    f"{E2E}/transcript-job-resume.test.ts",
    HANDOFF,
    IMPL_REVIEW,
    REFLECTION,
)
SECRET_BASES = (".mcp.json", "mcp-token.txt", ".claude.json", ".env")
GREP_EXCLUDES = (
    ":(exclude,glob)**/.mcp.json", ":(exclude,glob)**/mcp-token.txt", ":(exclude,glob)**/.claude.json",
    ":(exclude,glob)**/.env", ":(exclude,glob)**/.env.*", ":(exclude,glob)**/.claude/settings.local.json",
    ":(exclude).agent/fleet/hub",
)


def secret(name):
    parts = name.split("/")
    base = parts[-1]
    return (
        base in SECRET_BASES
        or base.startswith(".env.")
        or (len(parts) >= 2 and parts[-2] == ".claude" and base == "settings.local.json")
        or name.startswith(".agent/fleet/hub/")
        or name == ".agent/fleet/hub"
    )


def git(*args):
    return subprocess.run(["git", *args], capture_output=True, check=True).stdout


def listed(*dirs):
    out = git("ls-files", "--cached", "--others", "--exclude-standard", *dirs).decode("utf-8")
    return sorted(n for n in out.splitlines() if n and not secret(n))


MCP_FILES = [
    n for n in listed("mcp-server")
    if not n.startswith(("mcp-server/node_modules/", "mcp-server/dist/"))
]
MCP_TESTS = [n for n in MCP_FILES if n.startswith("mcp-server/tests/")]
SETTINGS_UI = listed("ui/src/renderer/src/features/settings")
# §Test pins files (by hash). test_services.py and test_transcript_metadata.py are pinned by ast.
PIN_FILES = (
    f"{UNIT}/transcript-page.behavior.test.ts",
    f"{UNIT}/transcript-page.test.ts",
    f"{UNIT}/gui-actions-audit.test.ts",
    f"{UNIT}/layout-primitives.test.ts",
    f"{E2E}/test-ids.ts",
    QUEUE_E2E,
    *MCP_TESTS,
    "tests/unit/test_transcript_pause_wake.py",
)
# "Read, never changed": bound by hash; their kind is recorded, not expected. The mcp-server/
# files are bound by baseline-mcp-hashes.json (H1-4).
READ_ONLY = (
    f"{T}/TranscriptToolbar.tsx",
    f"{T}/useTranscriptQueue.ts",
    "packages/api/src/avkit_api/routes/transcripts.py",
    "openapi.committed.json",
    "packages/api/src/avkit_api/schemas/settings.py",
    *SETTINGS_UI,
    f"{E2E}/electron-app.ts",
    "tests/orientation_fixtures.py",
    "_inspiration/_transcript_pseudo_logic.md",
    CANCEL_E2E,
    *(p for p in PIN_FILES if not p.startswith("mcp-server/")),
)
SCOPE_PREFIXES = (
    PLAN.as_posix() + "/",
    f".agent/context/handoffs/{SLUG}-",
    f"docs/execution/reflections/{SLUG}-",
)
DECLARED_NEW = (
    "resume-job", "resume-job-btn", "resumeTranscriptJob", "transcript:resume_job",
    "transcript_paused_fixture", "test_transcript_defaults", "transcript-defaults.test",
    "MEU_116_PACING", "test_ac_116_9_a_retry_makes_a_300_an_hour_cap_wait",
)
problems = []

spec = importlib.util.spec_from_file_location("tjr_row_check", PLAN / "row-check.py")
rck = importlib.util.module_from_spec(spec)
sys.modules["tjr_row_check"] = rck
spec.loader.exec_module(rck)

# Anchors (path, plan line or None, text): found once by text; a moved line is recorded for the
# handoff; a missing or doubled anchor is S2. The six settings lines of each file, the six 06
# rows and the 03 Rate cap row are row-check.py's own old texts, so the anchor and the later
# check read the same bytes.
ANCHORS = (
    (CONTROLS, 24, "  | 'open-folder'"),
    (CONTROLS, 66, "case 'resume':"),
    (CARD, 24, "export const TRANSCRIPT_MENU_ORDER"),
    (CARD, 37, "export const CARD_ACTION_TESTIDS"),
    (CARD, 66, "Paused: [],"),
    (CARD, 87, "export function cardActionAvailable"),
    (COMMANDS, 88, "async function queueContext"),
    (COMMANDS, 144, "export async function resumeTranscripts"),
    (PAGE, 94, "const ACTION_LABELS"),
    (PAGE, 320, "function runCardAction"),
    (SERVICE, 239, "def resume_processing"),
    (SERVICES, 1278, "def test_ac_11_3_resume_only_from_paused"),
    (SERVICES, 3071, "def _four_hundred"),
    (SERVICES, 3085, "def test_ac_116_5_default_cap_delays_nothing_without_retries"),
    (SERVICES, 3091, "def test_ac_116_9_a_retry_makes_the_default_cap_wait"),
    (METADATA, 264, "def test_ac_122_12_no_extra_request_per_video"),
    (INDEX, 37, "| `transcript:resume` |"),
    (QUEUE_E2E, 56, "function installTranscriptSeam"),
    (CANCEL_E2E, 209, "async function launch("),
    (ENGINE, 38, 'os.environ.get("AVKIT_APP_DATA"'),
    *((SETTINGS_PY, 69 + i, old) for i, (old, _) in enumerate(rck.VALUE_EDITS[rck.SETTINGS_PY])),
    *((SETTINGS_TS, 34 + i, old) for i, (old, _) in enumerate(rck.VALUE_EDITS[rck.SETTINGS_TS])),
    *((GUI, 1055 + i, old) for i, (old, _) in enumerate(rck.CANON_EDITS[rck.GUI])),
    (SERVICE_LAYER, 577, rck.RATE_CAP_OLD),
)


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


def text_lines(p):
    return pathlib.Path(p).read_bytes().decode("utf-8").replace("\r\n", "\n").split("\n")


def dump(name, data):
    (PLAN / name).write_bytes((json.dumps(data, indent=2, ensure_ascii=False) + "\n").encode("utf-8"))


OUT.mkdir(parents=True, exist_ok=True)
head = git("rev-parse", "HEAD").decode().strip()
(PLAN / "baseline.sha").write_bytes((head + "\n").encode())
print("HEAD (recorded, not compared)", head)
origin = subprocess.run(["git", "rev-parse", "origin/main"], capture_output=True).stdout.decode().strip()
print("origin/main as found", origin or "<none>")
print("git worktree list:")
for line in git("worktree", "list").decode("utf-8").splitlines():
    print("  ", line)

porcelain = git("status", "--porcelain", "--untracked-files=all").decode("utf-8")
print("git status --porcelain --untracked-files=all:")
for line in porcelain.splitlines():
    print("  ", line)
dirty = [line[3:].strip().strip('"') for line in porcelain.splitlines() if line.strip()]
(PLAN / "baseline-dirty.txt").write_bytes(porcelain.encode("utf-8"))
print("baseline-dirty.txt", len(dirty), "paths")

# Scope binding.
scope = {}
for p in MODIFIED:
    scope[p] = sha(p)
    if scope[p] in ("absent", "not-a-file"):
        problems.append(f"S2: a modified path is missing: {p}")
for p in NEW:
    scope[p] = sha(p)
    if scope[p] != "absent":
        problems.append(f"S2: a new path already exists: {p}")
for p in READ_ONLY:
    scope[p] = sha(p)
    if scope[p] in ("absent", "not-a-file"):
        problems.append(f"S2: a read-only path is missing: {p}")
for p in SHARED:
    scope[p] = {"kind": "shared", "sha256": sha(p)}
    if not pathlib.Path(p).is_file():
        problems.append(f"S2: a shared path is missing: {p}")
dump("baseline-scope.json", scope)
print(
    "baseline-scope.json", len(scope), "paths:", len(MODIFIED), "modified,", len(NEW), "new (absent),",
    len(READ_ONLY), "read, never changed,", len(SHARED), "shared",
)
for p in READ_ONLY:
    if p in dirty:
        print("  read-only path dirty at row 0 (another session's; in baseline-dirty.txt):", p)


def in_scope(p):
    return p in scope or p.startswith(SCOPE_PREFIXES)


hashes = {p: (sha(p) if pathlib.Path(p).exists() else "deleted") for p in dirty if not in_scope(p) and not secret(p)}
(PLAN / "baseline-dirty-hashes.json").write_bytes((json.dumps(hashes, indent=2, sort_keys=True) + "\n").encode())
print("baseline-dirty-hashes.json", len(hashes), "paths outside this scope")
for p in sorted(hashes):
    print("  bound by hash", p, hashes[p][:16])

# The row-0 bytes: eol-check.py's and row-check.py's base, and the execution review's delta base.
PLAN_FILES = {p.as_posix(): "LF" for p in sorted(PLAN.iterdir()) if p.is_file() and p.suffix in (".md", ".py", ".ps1", ".json")}
copied = 0
for p in (*MODIFIED, *SHARED, *READ_ONLY, *PLAN_FILES, PLAN_REVIEW):
    src = pathlib.Path(p)
    if src.is_absolute() or not src.is_file():
        continue
    dest = COPIES / p
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(src.read_bytes())
    copied += 1
print("baseline-copies", copied, "row-0 copies under", COPIES.as_posix())

# baseline-mcp-hashes.json (H1-4): secret names dropped before any stat or read.
mcp = {p: sha(p) for p in MCP_FILES if pathlib.Path(p).is_file()}
(PLAN / "baseline-mcp-hashes.json").write_bytes((json.dumps(mcp, indent=2, sort_keys=True) + "\n").encode())
print("baseline-mcp-hashes.json", len(mcp), "files,", len(MCP_TESTS), "under mcp-server/tests/")
if SETTINGS_TS not in mcp or "mcp-server/tests/transcript-defaults.test.ts" in mcp:
    problems.append("S2: baseline-mcp-hashes.json lacks settings.ts or already holds the new test")

# Line endings, measured with Python bytes.
eols = {}
for p, want in {**MODIFIED, **SHARED, **{q: None for q in READ_ONLY}, **PLAN_FILES, PLAN_REVIEW: "LF"}.items():
    if not pathlib.Path(p).is_file():
        eols[p] = {"kind": "absent", "expected": want}
        continue
    raw = pathlib.Path(p).read_bytes()
    kind, crlf, bare = eol(raw)
    eols[p] = {"kind": kind, "expected": want, "crlf": crlf, "bare_lf": bare, "bom": raw.startswith(b"\xef\xbb\xbf"), "bytes": len(raw)}
    print("eol", kind, "crlf", crlf, "bare_lf", bare, "bytes", len(raw), p)
    if want is not None and kind != want:
        problems.append(f"S2: {p} is {kind}, the plan says {want}")
dump("baseline-eol.json", eols)
print("baseline-eol.json", len(eols), "paths")

# baseline-pins.json: the pin files' hashes, and the two pytest files' top-level ast sources.
pins = {"files": {p: sha(p) for p in PIN_FILES}, "ast": {}}
for p, h in pins["files"].items():
    if h in ("absent", "not-a-file"):
        problems.append(f"S2: a pin file is missing: {p}")
for p in (SERVICES, METADATA):
    nodes = rck.top_level_sources(pathlib.Path(p).read_bytes().decode("utf-8"))
    pins["ast"][p] = nodes
    doubled = [k for k in nodes if "#" in k]
    pinned = [k for k in nodes if rck._pinned_test(k)]
    print("pins ast", p, len(nodes), "nodes,", len(pinned), "AC-11/AC-116 pinned, doubled", doubled)
    if doubled:
        problems.append(f"S2: {p} has doubled top-level names: {doubled}")
olds = {
    SERVICES: {rck.FOUR: rck.FOUR_OLD, rck.AC_116_5: rck.AC_116_5_OLD, rck.AC_116_9_OLD: rck.AC_116_9_OLD_SRC},
    METADATA: {rck.AC_122_12: rck.AC_122_12_OLD},
}
for p, forms in olds.items():
    for name, form in forms.items():
        same = pins["ast"][p].get(name) == form
        print("pins old form", p, name, "matches row-check.py" if same else "DIFFERS")
        if not same:
            problems.append(f"S2: {p}::{name} is not row-check.py's old form")
if not any(rck._pinned_test(k) for k in pins["ast"][SERVICES]):
    problems.append("S2: no AC-11 or AC-116 test found in test_services.py")
dump("baseline-pins.json", pins)
print("baseline-pins.json", len(pins["files"]), "files,", sum(len(v) for v in pins["ast"].values()), "ast nodes")

# baseline-citations.txt: the anchors, and the RESUME_GUARD line inside resume_processing.
cites = []
for p, plan_line, needle in ANCHORS:
    lines = text_lines(p)
    hits = [i + 1 for i, ln in enumerate(lines) if needle in ln]
    if len(hits) != 1:
        state = "missing" if not hits else f"doubled {hits}"
        problems.append(f"S2: anchor {needle[:80]!r} in {p}: {state}")
    else:
        state = "at line" if plan_line in (None, hits[0]) else f"moved from {plan_line}"
    cites.append(f"anchor {p}:{hits[0] if len(hits) == 1 else '-'} {state} hits={len(hits)} :: {needle[:100]}")
lines = text_lines(SERVICE)
start = [i for i, ln in enumerate(lines) if "def resume_processing" in ln]
lock = None
if len(start) == 1:
    for i in range(start[0] + 1, len(lines)):
        if lines[i].startswith("    def "):
            break
        if "with self._lock:" in lines[i]:
            lock = i + 1
            break
if lock is None:
    problems.append("S2: no `with self._lock:` inside resume_processing")
cites.append(f"anchor {SERVICE}:{lock or '-'} {'at line' if lock == 242 else 'moved from 242'} :: with self._lock: (first in resume_processing)")
for line in cites:
    print(line)
(PLAN / "baseline-citations.txt").write_bytes(("\n".join(cites) + "\n").encode("utf-8"))
print("baseline-citations.txt", len(ANCHORS) + 1, "anchors")


# Free ids. This session's own files (the plan folder, its handoffs and reflection, and the
# grouping file, whose path names this session) may name them; nothing else.
def grep_lines(pattern, fixed):
    flag = "-F" if fixed else "-E"
    run = subprocess.run(["git", "grep", "--untracked", "-n", flag, pattern, "--", ".", *GREP_EXCLUDES], capture_output=True)
    if run.returncode not in (0, 1):
        problems.append(f"git grep {pattern!r} exited {run.returncode}")
    return [ln for ln in run.stdout.decode("utf-8", "replace").splitlines() if ln]


OWN = (*SCOPE_PREFIXES, GROUPING + ":")
for name in (*DECLARED_NEW, "AC-163."):
    hits = grep_lines(name, True)
    foreign = [ln for ln in hits if not ln.startswith(OWN)]
    own = len(hits) - len(foreign)
    print(f"free id {name!r}: {own} hit(s) in this session's files, foreign {[ln[:120] for ln in foreign] or 'none'}")
    if foreign:
        problems.append(f"S2: {name} is already used outside this session's files")
decisions = [ln for ln in grep_lines(r"D-(135[89]|13[6-9][0-9])\b", False) if not ln.startswith(OWN)]
print("D-1358..D-1399 outside this session's files:", [ln[:120] for ln in decisions] or "none")
if decisions:
    problems.append("S2: D-1358 to D-1399 are used outside this session's files")

for p in sorted(PLAN_FILES):
    print("plan file", p, sha(p)[:16])
print("plan review", PLAN_REVIEW, sha(PLAN_REVIEW)[:16])
for p in problems:
    print("PROBLEM:", p)
print(f"baseline record: {len(problems)} problem(s)")
sys.exit(1 if problems else 0)
'@

New-Item -ItemType Directory -Force -Path $receipts | Out-Null
Set-Content -Path "$receipts/baseline-record.py" -Value $record -Encoding utf8

# 1. The environment (S7 on a held file).
Invoke-Step 'uv-sync' @('uv', 'sync', '--frozen', '--offline', '--all-packages')
# 2. The record.
Invoke-Step 'record' @('uv', 'run', '--no-sync', 'python', "$receipts/baseline-record.py")

# 3. One host-load sample (the 50 % limit).
& rtk proxy uv run --no-sync python "$plan/host-wait.py" > "$receipts/tjr-base-load.txt" 2>&1
$loadCode = $LASTEXITCODE
Get-Content "$receipts/tjr-base-load.txt" | Select-Object -Last 3
Write-Output ("baseline step host-load exit={0} receipt={1}/tjr-base-load.txt" -f $loadCode, $receipts)
if ($loadCode -ne 0) { exit $loadCode }

# 4. The base receipts: failures recorded, not fatal; the gate excuses only those ids.
Push-Location 'P:\av-kit\ui'
& rtk proxy npm run test *> "$receipts/tjr-base-ui.txt"
$uiCode = $LASTEXITCODE
Pop-Location
Set-Content -Path "$receipts/tjr-base-ui.txt.exit" -Value $uiCode -Encoding ascii
Write-Output ("base suite ui exit={0} receipt={1}/tjr-base-ui.txt" -f $uiCode, $receipts)
Get-Content "$receipts/tjr-base-ui.txt" | Select-String -Pattern 'Test Files|Tests |FAIL ' | Select-Object -Last 12

& rtk proxy uv run --no-sync pytest -q *> "$receipts/tjr-base-py.txt"
$pyCode = $LASTEXITCODE
Set-Content -Path "$receipts/tjr-base-py.txt.exit" -Value $pyCode -Encoding ascii
Write-Output ("base suite pytest exit={0} receipt={1}/tjr-base-py.txt" -f $pyCode, $receipts)
Get-Content "$receipts/tjr-base-py.txt" | Select-String -Pattern '^FAILED|^ERROR|passed|failed' | Select-Object -Last 12

Push-Location 'P:\av-kit\mcp-server'
& rtk proxy npm test *> "$receipts/tjr-base-mcp.txt"
$mcpCode = $LASTEXITCODE
Pop-Location
Set-Content -Path "$receipts/tjr-base-mcp.txt.exit" -Value $mcpCode -Encoding ascii
Write-Output ("base suite mcp exit={0} receipt={1}/tjr-base-mcp.txt" -f $mcpCode, $receipts)
Get-Content "$receipts/tjr-base-mcp.txt" | Select-String -Pattern 'Test Files|Tests |FAIL ' | Select-Object -Last 12

# 5. The plan-local checkers, then ruff on this folder's Python (Session 82 RULE-1).
Invoke-Step 'red-check-selftest' @('uv', 'run', '--no-sync', 'python', "$plan/red-check.py", '--selftest')
Invoke-Step 'identity-selftest' @('uv', 'run', '--no-sync', 'python', "$plan/identity.py", '--selftest')
Invoke-Step 'eol-check-selftest' @('uv', 'run', '--no-sync', 'python', "$plan/eol-check.py", '--selftest')
Invoke-Step 'host-wait-selftest' @('uv', 'run', '--no-sync', 'python', "$plan/host-wait.py", '--selftest')
Invoke-Step 'load-run-selftest' @('uv', 'run', '--no-sync', 'python', "$plan/load-run.py", '--selftest')
Invoke-Step 'row-check-selftest' @('uv', 'run', '--no-sync', 'python', "$plan/row-check.py", '--selftest')
Invoke-Step 'eol-check-row0' @('uv', 'run', '--no-sync', 'python', "$plan/eol-check.py")
$planPy = @(Get-ChildItem -Path $plan -Filter '*.py' | Sort-Object Name | ForEach-Object { "$plan/$($_.Name)" })
Write-Output ("baseline plan Python: {0}" -f ($planPy -join ', '))
Invoke-Step 'ruff-format-plan' (@('uv', 'run', '--no-sync', 'ruff', 'format', '--check') + $planPy)
Invoke-Step 'ruff-check-plan' (@('uv', 'run', '--no-sync', 'ruff', 'check') + $planPy)
Write-Output 'baseline: all steps exit 0'
exit 0
