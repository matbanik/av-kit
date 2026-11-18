# Video tail frame baseline (task row 0; implementation-plan.md §Verification Plan 1).
# The shape of docs/execution/plans/2026-11-17-test-run-reliability/baseline.ps1, with this
# plan's steps: 1. the tree state (baseline.sha, baseline-dirty.txt with the hash of each dirty
# path outside this scope in baseline-dirty-hashes.json), the worktree list and origin/main;
# 2. baseline-scope.json over §Files Modified, the closeout artifacts (absent) and the "Read,
# never changed" files; baseline-eol.json; baseline-skip-hashes.json over packages/ (other than
# adapter.py), mcp-server/, tools/ and ui/ (secret names dropped before any stat or read,
# Session 83 RULE-2); the row-0 copies under C:/Temp/av-kit/video-tail-frame/baseline-copies;
# the S1 and S2 binding (OLD_ADAPTER, start and END_GAP_LOOKBACK_MS once each, both ARGV_NAMED
# old lines once each, the two test_ac_134_10 tests and no test_ac_160_, the issue open,
# grouping row 93 proposed, MEU-160 and matrix 9.45 free, the plan and task as approved);
# Session 74's footprint: the three plan-time SHA-256 prefixes and every cited line re-read, a
# moved line recorded for the handoff (only S1 stops); 3. the host-load wait at 50 % or less,
# then the full Python suite with the D6 argv without -x (vtf-base-py.txt), its failures
# recorded, not fatal; 4. the plan-local selftests, eol-check.py over the fresh copies, and ruff
# format --check and ruff check on the plan folder's Python (Session 82 RULE-1). Every other
# step is fail-fast. Run from the repository root in pwsh.
$ErrorActionPreference = 'Stop'
$root = (git rev-parse --show-toplevel).Trim()
Set-Location $root
$plan = 'docs/execution/plans/2026-11-17-video-tail-frame'
$receipts = 'C:/Temp/av-kit/video-tail-frame'
$env:ELECTRON_RUN_AS_NODE = $null
$env:PYTHONIOENCODING = 'utf-8'
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:RECEIPTS_DIR = 'C:/Temp/av-kit'
$tmp = 'C:\Temp\av-kit\video-tail-frame\tmp'
New-Item -ItemType Directory -Force -Path $tmp | Out-Null
$env:TMP = $tmp
$env:TEMP = $tmp

function Invoke-Step([string]$Id, [string[]]$Argv) {
    & rtk proxy @Argv
    $code = $LASTEXITCODE
    Write-Output ("baseline step {0} exit={1}" -f $Id, $code)
    if ($code -ne 0) { exit $code }
}

# 1-2. Tree state, path-scoped baseline and the S1 and S2 binding, in Python so every file is
# read and written as bytes.
$record = @'
import hashlib, json, pathlib, re, subprocess, sys

PLAN = pathlib.Path("docs/execution/plans/2026-11-17-video-tail-frame")
OUT = pathlib.Path("C:/Temp/av-kit/video-tail-frame")
COPIES = OUT / "baseline-copies"
ADAPTER = "packages/infrastructure/src/avkit_infra/media/adapter.py"
UNIT = "tests/unit/test_media_adapter_frames.py"
INTEG = "tests/integration/test_video_real_ffmpeg.py"
STATUS = ".agent/context/meu-status.yaml"
NINE = "docs/build-plan/09-screenshot-capture.md"
MATRIX = "docs/build-plan/build-priority-matrix.md"
REGISTER = ".agent/context/known-issues.yaml"
GROUPING = ".agent/context/grouping/2026-11-17-value-triage-session-grouping.md"
PORT = "packages/core/src/avkit_core/ports/capture.py"
PEER = "docs/execution/plans/2026-11-17-test-run-reliability/load-run.py"
HANDOFF = ".agent/context/handoffs/2026-11-17-video-tail-frame-MEU-160-handoff.md"
REVIEW = ".agent/context/handoffs/2026-11-17-video-tail-frame-implementation-critical-review.md"
REFLECTION = "docs/execution/reflections/2026-11-17-video-tail-frame-reflection.md"
PLAN_REVIEW = ".agent/context/handoffs/2026-11-17-video-tail-frame-plan-critical-review.md"
# §Files Modified, with each file's line-ending kind.
MODIFIED = {
    ADAPTER: "CRLF",
    UNIT: "LF",
    INTEG: "LF",
    STATUS: "LF",
    NINE: "CRLF",
    MATRIX: "CRLF",
    ".agent/context/meu-registry.md": "LF",
    "docs/BUILD_PLAN.md": "LF",
    REGISTER: "LF",
    ".agent/context/known-issues.md": "LF",
    GROUPING: "LF",
    "docs/execution/metrics.md": "CRLF",
    ".agent/context/current-focus.md": "CRLF",
}
# The closeout artifacts (§Files Modified, last row): new, absent at row 0.
NEW = {HANDOFF: "LF", REVIEW: "LF", REFLECTION: "LF"}
# "Read, never changed": bound by hash; the kind is expected where the plan names it.
READ_ONLY = {
    "packages/core/src/avkit_core/services/capture.py": "CRLF",
    PORT: None,
    "packages/api/src/avkit_api/routes/captures.py": None,
    "tests/conftest.py": "CRLF",
    PEER: "LF",
}
# packaging/ffmpeg-win64/ (ignored, the pinned binaries): bound by hash, never copied.
PINNED = tuple(
    sorted(p.as_posix() for p in pathlib.Path("packaging/ffmpeg-win64").iterdir() if p.is_file())
)
PLAN_FILES = {
    f"{PLAN.as_posix()}/{n}": "LF"
    for n in (
        "implementation-plan.md", "task.md", "grab_trace.py", "load-run.py", "trace-check.py",
        "packet-stress.py", "diff-check.py", "meu-register.py", "baseline.ps1", "red-check.py",
        "identity.py", "eol-check.py", "issue-resolve.py",
    )
}
# The approved plan and task (the plan's sha moved only by the Status line's execute words:
# 92d51947... as reviewed, be8734878d20... with the approval line).
PLAN_SHA = {
    f"{PLAN.as_posix()}/implementation-plan.md": "be8734878d202f85c0fbc7ff7867dc877e32f97db1e2a7bf7f58b7d54a0fb770",
    f"{PLAN.as_posix()}/task.md": "a70b433ffc3bf914252c486b907eb8f4d63edd38be414cd3f8a7386533664ac3",
}
# Session 74's footprint (plan §Harness): the plan-time SHA-256 prefixes.
PREFIXES = {ADAPTER: "88e1246284a3", UNIT: "c4fc8920b64c", INTEG: "fbfe8f040d17"}
OLD_ADAPTER = '            f"{_seek_text(start)}%",'
START = "        start = max(0, time_ms - END_GAP_LOOKBACK_MS)"
LOOKBACK = "END_GAP_LOOKBACK_MS = 60_000"
ARGV_OLD = ('        "0.000%",', '    assert packet[packet.index("-read_intervals") + 1] == "7140.021%"')
# S1 and S2 (exact counts; a wrong count is a problem).
BINDING = (
    (ADAPTER, OLD_ADAPTER, 1),
    (ADAPTER, START, 1),
    (ADAPTER, LOOKBACK, 1),
    (UNIT, ARGV_OLD[0], 1),
    (UNIT, ARGV_OLD[1], 1),
    (INTEG, "def test_ac_134_10_counter_clip_frames_match_a_full_decode(", 1),
    (INTEG, "def test_ac_134_10_long_audio_past_the_last_frame(", 1),
    (INTEG, "test_ac_160_", 0),
    (UNIT, "test_ac_160_", 0),
)
# Every line the plan cites, with the line it gives: a moved line is recorded for the handoff
# (Session 51 RULE-3), not a problem.
CITED = (
    (ADAPTER, LOOKBACK, 48),
    (ADAPTER, '        """END_GAP: the last video packet', 623),
    (ADAPTER, START, 636),
    (ADAPTER, OLD_ADAPTER, 644),
    (UNIT, "def test_ac_134_9_end_gap_reads_the_last_packet_and_grabs_again(", 270),
    (UNIT, ARGV_OLD[0], 289),
    (UNIT, "def test_ac_134_9_end_gap_reads_from_60_seconds_before(", 302),
    (UNIT, ARGV_OLD[1], 313),
    (UNIT, '    assert retry[retry.index("-ss") + 1] == "7199.979"', 315),
    (UNIT, "def test_ac_134_9_the_largest_packet_time_wins(", 318),
    (INTEG, "def test_ac_134_10_counter_clip_frames_match_a_full_decode(", 239),
    (INTEG, "def test_ac_134_10_long_audio_past_the_last_frame(", 273),
    (INTEG, "def test_ac_134_10_every_clip_is_unchanged_after_frames(", 335),
    (INTEG, "def test_ac_135_14_counter_sheet_cells_match_a_scaled_full_decode(", 447),
    (INTEG, "def test_ac_135_14_every_clip_is_unchanged_after_sheets(", 534),
    (NINE, "| MEU-146 | `capture-exif-orientation` |", 1370),
    (MATRIX, "| 9.44 | MEU-146 |", 153),
    (GROUPING, "| 93 | `video-tail-frame` |", 165),
    (GROUPING, "- **Gate:** no retries and no raised timeouts", 94),
    (PORT, "    def grab_frame(", 120),
    (REGISTER, "  - id: VIDEO-REAL-FFMPEG-TAIL-FRAME-FLAKE", None),
)
ISSUE = "VIDEO-REAL-FFMPEG-TAIL-FRAME-FLAKE"
GROUPING_ROW = "| 93 | `video-tail-frame` | \u2014 | P3 | proposed | \u2014 |"
HEAD = "9c655bdf6ac2436308e20d4b889268e051d4e19d"
SCOPE_PREFIXES = (
    PLAN.as_posix() + "/",
    ".agent/context/handoffs/2026-11-17-video-tail-frame-",
    "docs/execution/reflections/2026-11-17-video-tail-frame-",
)
SKIP_ROOTS = ("packages", "mcp-server", "tools", "ui")
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


def lines_of(path):
    return [ln.rstrip("\r") for ln in pathlib.Path(path).read_bytes().decode("utf-8").split("\n")]


head = git("rev-parse", "HEAD").decode().strip()
(PLAN / "baseline.sha").write_bytes((head + "\n").encode())
print("baseline.sha", head)
if head != HEAD:
    problems.append(f"HEAD is {head}, not the brief's 9c655bd")
origin = subprocess.run(["git", "rev-parse", "origin/main"], capture_output=True).stdout.decode().strip()
print("origin/main as found", origin or "<none>")
for line in git("worktree", "list").decode("utf-8").splitlines():
    print("worktree", line)
porcelain = git("status", "--porcelain", "--untracked-files=all").decode("utf-8")
(PLAN / "baseline-dirty.txt").write_bytes(porcelain.encode("utf-8"))
dirty = [line[3:].strip().strip('"') for line in porcelain.splitlines() if line.strip()]
print("baseline-dirty.txt", len(dirty), "paths")
for p in dirty:
    print("  dirty", p)

KINDS = {**MODIFIED, **NEW}
scope = {p: sha(p) for p in (*KINDS, *READ_ONLY, *PINNED)}
for p in NEW:
    if scope[p] != "absent":
        problems.append(f"S2: a closeout artifact already exists: {p}")
for p in (*MODIFIED, *READ_ONLY):
    if scope[p] in ("absent", "not-a-file"):
        problems.append(f"S2: scoped path missing: {p}")
if not PINNED:
    problems.append("S2: packaging/ffmpeg-win64/ holds no file")
(PLAN / "baseline-scope.json").write_bytes((json.dumps(scope, indent=2) + "\n").encode())
print("baseline-scope.json", len(scope), "paths;", sum(v == "absent" for v in scope.values()), "absent")
for p in PINNED:
    print("pinned", p, scope[p][:16])
for p, want in PREFIXES.items():
    got = scope[p][:12]
    print("plan-time prefix", p, "now", got, "plan", want, "same" if got == want else "CHANGED")
    if got != want:
        moved.append(f"{p}: sha256 {got}, plan-time {want} (re-read below; only S1 stops)")


def in_scope(p):
    return p in scope or p.startswith(SCOPE_PREFIXES)


hashes = {p: (sha(p) if pathlib.Path(p).exists() else "deleted") for p in dirty if not in_scope(p) and not secret(p)}
(PLAN / "baseline-dirty-hashes.json").write_bytes((json.dumps(hashes, indent=2, sort_keys=True) + "\n").encode())
print("baseline-dirty-hashes.json", len(hashes), "paths outside this scope (foreign: never touched)")
for p in sorted(hashes):
    print("  bound by hash", p, hashes[p][:16])

# The row-0 content of every existing scoped, read-only and plan file, and the plan review:
# diff-check.py's, eol-check.py's and the execution review's delta base. The pinned binaries are
# bound by hash only.
copied = 0
for p in (*KINDS, *READ_ONLY, *PLAN_FILES, PLAN_REVIEW):
    if not pathlib.Path(p).is_file():
        continue
    dest = COPIES / p
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(pathlib.Path(p).read_bytes())
    copied += 1
print("baseline-copies", copied, "row-0 copies under", COPIES.as_posix())

# baseline-skip-hashes.json (H1-4): every tracked or untracked, not-ignored file under packages/
# other than adapter.py, and under mcp-server/, tools/ and ui/; secret names dropped before any
# stat or read.
listed = git("ls-files", "--cached", "--others", "--exclude-standard", *SKIP_ROOTS)
skip_paths = [n for n in listed.decode("utf-8").splitlines() if n and n != ADAPTER and not secret(n)]
skips = {p: sha(p) for p in skip_paths if pathlib.Path(p).is_file()}
(PLAN / "baseline-skip-hashes.json").write_bytes((json.dumps(skips, indent=2, sort_keys=True) + "\n").encode())
print("baseline-skip-hashes.json", len(skips), "files under packages/ (not adapter.py), mcp-server/, tools/ and ui/")

# Line endings, measured with Python bytes.
eols = {}
for p, want in {**KINDS, **READ_ONLY, **PLAN_FILES}.items():
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

# S1 and S2: the END_GAP read, the named assertions and the integration tests.
for p, needle, want in BINDING:
    n = sum(1 for ln in lines_of(p) if (ln == needle if not needle.startswith(("def ", "test_")) else needle in ln))
    print("binding", p, "::", repr(needle), "count", n, "want", want)
    if n != want:
        tag = "S1" if p == ADAPTER else "S2"
        problems.append(f"{tag}: {needle!r} in {p} occurs {n} time(s), want {want}")

# Every cited line, re-read.
for p, needle, line in CITED:
    at = [i + 1 for i, ln in enumerate(lines_of(p)) if ln.startswith(needle) or ln == needle]
    state = "as cited" if line is None or at == [line] else "MOVED"
    print("cited", p, "::", repr(needle), "plan", line, "now", at, state)
    if not at:
        problems.append(f"S2: cited line {needle!r} not found in {p}")
    elif state == "MOVED":
        moved.append(f"{p}:{line} {needle!r} is now at {at}")

# The register, the grouping row, MEU-160 and matrix 9.45, graphify, the approved plan.
register = pathlib.Path(REGISTER).read_bytes().decode("utf-8")
m = re.search(r"^  - id: " + ISSUE + r"\n(?:    .*\n)*?    status: (\S+)", register, re.M)
state = m.group(1) if m else None
print("issue", ISSUE, "status", state)
if state != "open":
    problems.append(f"S2: {ISSUE} is {state}, not open")
row = [ln for ln in lines_of(GROUPING) if ln.startswith("| 93 |")]
print("grouping row 93", row)
if row != [GROUPING_ROW]:
    problems.append("S2: grouping row 93 is not the one proposed row")
for p in (STATUS, NINE, MATRIX):
    text = pathlib.Path(p).read_bytes().decode("utf-8")
    n160 = len(re.findall(r"\bMEU-160\b", text))
    n945 = text.count("| 9.45 |")
    print("free check", p, "MEU-160", n160, "9.45", n945)
    if n160 or n945:
        problems.append(f"row 1: MEU-160 or 9.45 is taken in {p}; record the next free pair")
graphs = [g for g in ("graphify-out", "graphify-out-research") if pathlib.Path(g).exists()]
print("graphify graphs", graphs)
if graphs:
    problems.append(f"a graphify graph exists: {graphs}")
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
for p in moved:
    print("MOVED (for the handoff, Session 51 RULE-3):", p)
for p in problems:
    print("PROBLEM:", p)
sys.exit(1 if problems else 0)
'@
New-Item -ItemType Directory -Force -Path $receipts | Out-Null
Set-Content -Path "$receipts/baseline-record.py" -Value $record -Encoding utf8
Invoke-Step 'uv-sync' @('uv', 'sync', '--frozen', '--all-packages')
Invoke-Step 'record' @('uv', 'run', '--no-sync', 'python', "$receipts/baseline-record.py")

# 3. The host-load wait at 50 % or less (Session 81 RULE-2; Session 90's host_load_wait waits
# only for 60 %, so host-wait50.py samples with its peer sample() and waits for 50 %).
Invoke-Step 'host-load' @('uv', 'run', '--no-sync', 'python', "$receipts/host-wait50.py")

# The full Python suite with the D6 argv (.agent/docs/commands.md, py-tests) without -x, so
# every base failure is recorded; the gate excuses only those ids. Not fatal.
& rtk proxy uv run --no-sync pytest tests/ --tb=short -q *> "$receipts/vtf-base-py.txt"
$pyCode = $LASTEXITCODE
Write-Output ("base suite py exit={0} receipt={1}/vtf-base-py.txt" -f $pyCode, $receipts)
Get-Content "$receipts/vtf-base-py.txt" | Select-String -Pattern '^FAILED |^ERROR | in [0-9.]+s' | Select-Object -Last 20

# 4. The plan-local checkers, then Session 82 RULE-1 on the plan folder's Python.
Invoke-Step 'red-check-selftest' @('uv', 'run', '--no-sync', 'python', "$plan/red-check.py", '--selftest')
Invoke-Step 'identity-selftest' @('uv', 'run', '--no-sync', 'python', "$plan/identity.py", '--selftest')
Invoke-Step 'eol-check-selftest' @('uv', 'run', '--no-sync', 'python', "$plan/eol-check.py", '--selftest')
Invoke-Step 'grab-trace-selftest' @('uv', 'run', '--no-sync', 'python', "$plan/grab_trace.py", '--selftest')
Invoke-Step 'load-run-selftest' @('uv', 'run', '--no-sync', 'python', "$plan/load-run.py", '--selftest')
Invoke-Step 'trace-check-selftest' @('uv', 'run', '--no-sync', 'python', "$plan/trace-check.py", '--selftest')
Invoke-Step 'packet-stress-selftest' @('uv', 'run', '--no-sync', 'python', "$plan/packet-stress.py", '--selftest')
Invoke-Step 'diff-check-selftest' @('uv', 'run', '--no-sync', 'python', "$plan/diff-check.py", '--selftest')
Invoke-Step 'meu-register-selftest' @('uv', 'run', '--no-sync', 'python', "$plan/meu-register.py", '--selftest')
Invoke-Step 'eol-check-row0' @('uv', 'run', '--no-sync', 'python', "$plan/eol-check.py")
$planPy = @(Get-ChildItem -Path $plan -Filter '*.py' | ForEach-Object { "$plan/$($_.Name)" })
Invoke-Step 'ruff-format-plan' (@('uv', 'run', '--no-sync', 'ruff', 'format', '--check') + $planPy)
Invoke-Step 'ruff-check-plan' (@('uv', 'run', '--no-sync', 'ruff', 'check') + $planPy)
Write-Output 'baseline: all steps exit 0'
exit 0
