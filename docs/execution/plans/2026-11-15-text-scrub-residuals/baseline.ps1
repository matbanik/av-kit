# Text scrub residuals baseline (task row 0; implementation-plan.md §Verification Plan 1).
# The shape of docs/execution/plans/2026-11-15-tooling-test-hermeticity/baseline.ps1, with this
# plan's steps: 1. the tree state (baseline.sha, baseline-dirty.txt); 2. the path-scoped baseline
# (baseline-scope.json, each §Files Modified path's SHA-256 or absent, the two new test files
# absent; baseline-dirty-hashes.json; baseline-eol.json, each §Files Modified path's line-ending
# kind re-measured with Python bytes against the plan's table; S2: the five product files and
# 03-service-layer.md must equal HEAD's blob); 3. the plan-local copies: red-check.py and
# identity.py from 2026-11-15-framework-small-syncs (PLAN, PROJECT_ARTIFACTS, DECLARED_NEW
# extended with clean_text, home_forms and short_path_name, and D-919's pytest header pattern
# with its long-title fixture), issue-resolve.py from 2026-11-15-closeout-record-once (SCRATCH at
# C:/Temp/av-kit/text-scrub-residuals/issue-resolve), each replacement made exactly once;
# 4. uv sync (run first) and the base Python suite (tsr-base-py.txt; its failures are recorded,
# not fatal: the session gate excuses only the ids this receipt shows failing), with TMP and
# TEMP and the rest of the environment as the session gate sets them (Session 76 RULE-2);
# 5. the red-check.py and identity.py selftests and a scope-check.py run for row 1. Every other
# step is fail-fast. Run from the repository root.
$ErrorActionPreference = 'Stop'
$root = (git rev-parse --show-toplevel).Trim()
Set-Location $root
$plan = 'docs/execution/plans/2026-11-15-text-scrub-residuals'
$receipts = 'C:/Temp/av-kit/text-scrub-residuals'
$env:ELECTRON_RUN_AS_NODE = $null
$env:AGENT_MODEL_REGISTRY = $null
$env:PYTHONIOENCODING = 'utf-8'
$env:RECEIPTS_DIR = 'C:/Temp/av-kit'
$env:AGENT_MODEL_REGISTRY_HOME = 'P:/.agent'
$tmp = 'C:\Temp\av-kit\text-scrub-residuals\tmp'
New-Item -ItemType Directory -Force -Path $tmp | Out-Null

function Invoke-Step([string]$Id, [string[]]$Argv) {
    & rtk proxy @Argv
    $code = $LASTEXITCODE
    Write-Output ("baseline step {0} exit={1}" -f $Id, $code)
    if ($code -ne 0) { exit $code }
}

Invoke-Step 'uv-sync' @('uv', 'sync', '--frozen', '--all-packages')

# 1-3. Tree state, path-scoped baseline, S2 and the plan-local copies, in Python so every file is
# read and written as bytes.
$record = @'
import hashlib, json, pathlib, subprocess, sys

PLAN = pathlib.Path("docs/execution/plans/2026-11-15-text-scrub-residuals")
FSS = pathlib.Path("docs/execution/plans/2026-11-15-framework-small-syncs")
CRO = pathlib.Path("docs/execution/plans/2026-11-15-closeout-record-once")
PRODUCT = (
    "packages/core/src/avkit_core/domain/download.py",
    "packages/infrastructure/src/avkit_infra/youtube/adapter.py",
    "packages/core/src/avkit_core/services/transcript.py",
    "packages/core/src/avkit_core/services/health.py",
    "packages/core/src/avkit_core/services/download.py",
)
DOC03 = "docs/build-plan/03-service-layer.md"
NEW = ("tests/unit/test_transcript_title_cleaning.py", "tests/unit/test_console_home_short_form.py")
REGISTERS = (
    ".agent/context/known-issues.yaml",
    ".agent/context/known-issues.md",
    ".agent/context/meu-status.yaml",
    ".agent/context/meu-registry.md",
    "docs/BUILD_PLAN.md",
    ".agent/context/grouping/2026-11-15-post-rc3-triage-residuals-session-grouping.md",
)
FILES_MODIFIED = PRODUCT + NEW + (DOC03,) + REGISTERS
#: The plan's §Files Modified line-ending column (and task.md's line-ending note).
WANT_EOL = {
    "packages/core/src/avkit_core/domain/download.py": "crlf",
    "packages/infrastructure/src/avkit_infra/youtube/adapter.py": "crlf",
    "packages/core/src/avkit_core/services/transcript.py": "lf",
    "packages/core/src/avkit_core/services/health.py": "crlf",
    "packages/core/src/avkit_core/services/download.py": "crlf",
    DOC03: "crlf",
    ".agent/context/known-issues.yaml": "lf",
    ".agent/context/known-issues.md": "lf",
    ".agent/context/meu-status.yaml": "lf",
    ".agent/context/meu-registry.md": "lf",
    "docs/BUILD_PLAN.md": "lf",
    ".agent/context/grouping/2026-11-15-post-rc3-triage-residuals-session-grouping.md": "lf",
}
SHARED_EOL = {"docs/execution/metrics.md": "crlf", ".agent/context/current-focus.md": "crlf"}
SCOPE_PREFIXES = (
    PLAN.as_posix() + "/",
    ".agent/context/handoffs/2026-11-15-text-scrub-residuals-",
    "docs/execution/reflections/2026-11-15-text-scrub-residuals-",
)
SHARED = tuple(SHARED_EOL)
problems = []

def git(*args, data=None):
    return subprocess.run(["git", *args], capture_output=True, check=True, input=data).stdout

def sha(path):
    p = pathlib.Path(path)
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else ("absent" if not p.exists() else "not-a-file")

def paths(porcelain):
    out = []
    for line in porcelain.splitlines():
        if not line.strip():
            continue
        name = line[3:].strip()
        if " -> " in name:
            name = name.split(" -> ", 1)[1]
        out.append(name.strip('"'))
    return out

def dump(obj):
    return (json.dumps(obj, indent=2, sort_keys=True) + "\n").encode()

def eol_kind(data):
    crlf = data.count(b"\r\n")
    lf = data.count(b"\n") - crlf
    cr = data.count(b"\r") - crlf
    if crlf and not lf and not cr:
        return "crlf"
    if lf and not crlf and not cr:
        return "lf"
    return f"mixed crlf={crlf} lf={lf} cr={cr}"

# 1. Tree state.
head = git("rev-parse", "HEAD").decode().strip()
(PLAN / "baseline.sha").write_bytes((head + "\n").encode())
print("baseline.sha", head)
porcelain = git("status", "--porcelain", "--untracked-files=all").decode("utf-8")
(PLAN / "baseline-dirty.txt").write_bytes(porcelain.encode("utf-8"))
dirty = paths(porcelain)
print("baseline-dirty.txt", len(dirty), "paths")

# 2. Path-scoped baseline.
scope = {p: sha(p) for p in FILES_MODIFIED}
for p in NEW:
    if scope[p] != "absent":
        problems.append(f"new path already exists: {p}")
for p in PRODUCT + (DOC03,) + REGISTERS:
    if scope[p] in ("absent", "not-a-file"):
        problems.append(f"existing path missing: {p}")
(PLAN / "baseline-scope.json").write_bytes((json.dumps(scope, indent=2) + "\n").encode())
print("baseline-scope.json", len(scope), "paths;", sum(v == "absent" for v in scope.values()), "absent")
print("   known-issues.yaml sha256", scope[".agent/context/known-issues.yaml"])
for p in FILES_MODIFIED:
    print("   Files Modified", p, "dirty at row 0" if p in dirty else "clean at HEAD")

base_plans = {n for n in git("ls-tree", "--name-only", head, "docs/execution/plans/").decode().splitlines() if n}

def other_plan(p):
    folder = "/".join(p.split("/")[:4])
    return p.startswith("docs/execution/plans/2026-11-15-") and folder != p and folder not in base_plans

def in_scope(p):
    return p in scope or p in SHARED or p.startswith(SCOPE_PREFIXES) or other_plan(p)

hashes = {p: (sha(p) if pathlib.Path(p).exists() else "deleted") for p in dirty if not in_scope(p)}
(PLAN / "baseline-dirty-hashes.json").write_bytes(dump(hashes))
print("baseline-dirty-hashes.json", len(hashes), "paths outside this scope")
for p in sorted(hashes):
    print("   ", p)
for p in SHARED:
    print("shared", p, "dirty" if p in dirty else "clean at HEAD", sha(p))

# S2: the five product files and the 03 file equal HEAD's blob (git hash-object applies the
# repository's text=auto filter, so a CRLF checkout of an LF blob compares equal).
for p in PRODUCT + (DOC03,):
    work = git("hash-object", p).decode().strip()
    listed = git("ls-tree", head, "--", p).decode().split()
    committed = listed[2] if len(listed) >= 3 else "missing"
    print(f"S2 {p}: work {work} HEAD {committed} {'same' if work == committed else 'DIFFERS'}")
    if work != committed:
        problems.append(f"S2: {p} differs from HEAD")

# Line endings, re-measured with Python bytes (the plan measured them at 6aaf9b0).
eol = {}
for p in FILES_MODIFIED + SHARED:
    path = pathlib.Path(p)
    if not path.is_file():
        eol[p] = "absent-new-lf"
        print(f"EOL {p}: absent (new, LF)")
        continue
    data = path.read_bytes()
    kind = eol_kind(data)
    want = WANT_EOL.get(p) or SHARED_EOL.get(p)
    bom = data.startswith(b"\xef\xbb\xbf")
    print(f"EOL {p}: {kind} bom={bom} bytes={len(data)} plan={want} {'ok' if kind == want and not bom else 'DIFFERS'}")
    if kind != want or bom:
        problems.append(f"line endings: {p} is {kind} bom={bom}, the plan says {want}")
    if p in scope:
        eol[p] = kind
(PLAN / "baseline-eol.json").write_bytes(dump(eol))
print("baseline-eol.json", len(eol), "paths")

grouping = pathlib.Path(REGISTERS[-1]).read_text(encoding="utf-8")
row77 = [ln for ln in grouping.splitlines() if ln.startswith("| 77 |")]
print("grouping row 77:", row77)
if len(row77) != 1:
    problems.append(f"grouping §6 row 77 found {len(row77)} times")

# 3. Plan-local copies, each replacement exactly once.
def copy(src, dest, edits):
    text = src.read_bytes().decode("utf-8")
    if b"\r" in src.read_bytes():
        problems.append(f"{src} is not LF")
    for old, new in edits:
        n = text.count(old)
        if n != 1:
            problems.append(f"copy {src.name}: {old[:60]!r} occurs {n} times")
            continue
        text = text.replace(old, new)
    dest.write_bytes(text.encode("utf-8"))
    print("copied", src.as_posix(), "->", dest.as_posix(), "sha256", sha(dest), "edits", len(edits))

copy(FSS / "red-check.py", PLAN / "red-check.py", [
    ('"""Session 87 Red proof (task rows 1 and 5; implementation-plan.md Verification Plan §2). A copy of\n'
     "Session 49b's (2026-11-05-closeout-register-grammar), unchanged apart from this line.\n",
     '"""Session 77 Red proof (task rows 1, 3 and 4; implementation-plan.md Verification Plan §2). A copy\n'
     "of Session 87's (2026-11-15-framework-small-syncs) with D-919's pytest header pattern and its\n"
     "long-title fixture (Session 76 RULE-1), and DECLARED_NEW extended (task row 0).\n"),
    ("    # Session 87 declares no new export or module. These are the names the --selftest\n"
     "    # fixtures declare; nothing in this session uses them.\n",
     "    # Session 77 declares clean_text, home_forms and short_path_name (task row 0). Its Red\n"
     "    # tests assert each with hasattr first, so a --require test still fails by assertion.\n"
     '    "clean_text",\n'
     '    "home_forms",\n'
     '    "short_path_name",\n'
     "    # The names the --selftest fixtures declare; nothing in this session uses them.\n"),
    ('PYTEST_HEADER = re.compile(r"^_{3,} (.+?) _{3,}\\s*$")\n',
     "# pytest frames a failure title with at least one underscore on each side; a title wider than\n"
     "# the terminal gets exactly one (D-919, Session 76 row 1: the long preserves_bindings ids).\n"
     'PYTEST_HEADER = re.compile(r"^_+ (.+?) _+\\s*$")\n'),
    ('    ("pytest-did-not-raise", _py([("test_ac_94_9", ["E   Failed: DID NOT RAISE ModelLoadError"])], "1 failed, 4 deselected in 0.2s"), 1, (), True),\n',
     '    ("pytest-did-not-raise", _py([("test_ac_94_9", ["E   Failed: DID NOT RAISE ModelLoadError"])], "1 failed, 4 deselected in 0.2s"), 1, (), True),\n'
     "    (\n"
     '        "pytest-long-title-one-underscore",\n'
     '        _py([("test_long[" + "x" * 90 + "]", ASSERT_PY)], "1 failed in 0.1s").replace("_" * 12 + " ", "_ ").replace(" " + "_" * 12, " _"),\n'
     '        1, ("test_long[" + "x" * 90 + "]",), True,\n'
     "    ),\n"),
])
copy(FSS / "identity.py", PLAN / "identity.py", [
    ('"""Session 87 input identity (implementation-plan.md §Validation stage contract). A copy of\n'
     "Session 49b's (2026-11-05-closeout-register-grammar), with this plan's PLAN and PROJECT_ARTIFACTS.\n",
     '"""Session 77 input identity (implementation-plan.md §Validation stage contract). A copy of\n'
     "Session 87's (2026-11-15-framework-small-syncs), with this plan's PLAN and PROJECT_ARTIFACTS.\n"),
    ('PLAN = "docs/execution/plans/2026-11-15-framework-small-syncs"\n',
     'PLAN = "docs/execution/plans/2026-11-15-text-scrub-residuals"\n'),
    ("#: Sessions 84 to 86 left uncommitted, so they are bound by content.\n",
     "#: other sessions left uncommitted (the Sessions 78 to 83 plan reviews), so they are bound by content.\n"),
    ('    ".agent/context/handoffs/2026-11-15-framework-small-syncs-*",\n'
     '    "docs/execution/reflections/2026-11-15-framework-small-syncs-*",\n',
     '    ".agent/context/handoffs/2026-11-15-text-scrub-residuals-*",\n'
     '    "docs/execution/reflections/2026-11-15-text-scrub-residuals-*",\n'),
    ("#: Session 87 changes no Python dependency; the whole distribution set is still hashed.\n",
     "#: Session 77 changes no Python dependency; the whole distribution set is still hashed.\n"),
    ('        ".agent/context/handoffs/2026-11-15-framework-small-syncs-handoff.md",\n'
     '        ".agent/context/handoffs/2026-11-15-framework-small-syncs-implementation-critical-review.md",\n'
     '        "docs/execution/reflections/2026-11-15-framework-small-syncs-reflection.md",\n',
     '        ".agent/context/handoffs/2026-11-15-text-scrub-residuals-MEU-147-handoff.md",\n'
     '        ".agent/context/handoffs/2026-11-15-text-scrub-residuals-MEU-148-handoff.md",\n'
     '        ".agent/context/handoffs/2026-11-15-text-scrub-residuals-implementation-critical-review.md",\n'
     '        "docs/execution/reflections/2026-11-15-text-scrub-residuals-reflection.md",\n'),
])
copy(CRO / "issue-resolve.py", PLAN / "issue-resolve.py", [
    ('"""Session 84 register update (task row 7; plan §Closing the known issue). A copy of Session 73\'s\n'
     "(`2026-11-14-tts-fp16-phase-guard/issue-resolve.py`) with SCRATCH at C:/Temp/av-kit/cro and\n",
     '"""Session 77 register update (task row 5). A copy of Session 84\'s\n'
     "(`2026-11-15-closeout-record-once/issue-resolve.py`), itself a copy of Session 73's\n"
     "(`2026-11-14-tts-fp16-phase-guard/issue-resolve.py`), with SCRATCH at\n"
     "C:/Temp/av-kit/text-scrub-residuals/issue-resolve and\n"),
    ('SCRATCH = Path("C:/Temp/av-kit/cro")\n',
     'SCRATCH = Path("C:/Temp/av-kit/text-scrub-residuals/issue-resolve")\n'),
])
for name in ("red-check.py", "identity.py", "issue-resolve.py"):
    if "framework-small-syncs\"" in (PLAN / name).read_text(encoding="utf-8").split("PLAN = ", 1)[-1][:80]:
        problems.append(f"{name}: PLAN still names framework-small-syncs")

for p in problems:
    print("PROBLEM:", p)
sys.exit(1 if problems else 0)
'@
Set-Content -Path "$receipts/baseline-record.py" -Value $record -Encoding utf8
Invoke-Step 'record' @('uv', 'run', '--no-sync', 'python', "$receipts/baseline-record.py")

# 4. The base Python suite with TMP and TEMP outside the user profile, in the gate's environment.
$env:TMP = $tmp
$env:TEMP = $tmp
& rtk proxy uv run --no-sync pytest tests/ --tb=short -q -rfE *> "$receipts/tsr-base-py.txt"
Write-Output ("base suite py exit={0} receipt={1}/tsr-base-py.txt" -f $LASTEXITCODE, $receipts)
Get-Content "$receipts/tsr-base-py.txt" | Select-String -Pattern '^FAILED |^ERROR |passed|failed' | Select-Object -Last 12

# 5. The plan-local checkers' selftests, then the S4 check for row 1.
Invoke-Step 'red-check-selftest' @('uv', 'run', '--no-sync', 'python', "$plan/red-check.py", '--selftest')
Invoke-Step 'identity-selftest' @('uv', 'run', '--no-sync', 'python', "$plan/identity.py", '--selftest')
Invoke-Step 'scope-check-row-1' @('uv', 'run', '--no-sync', 'python', "$plan/scope-check.py", '--row', '1')
Invoke-Step 'scope-check-eol' @('uv', 'run', '--no-sync', 'python', "$plan/scope-check.py", '--eol')
Write-Output 'baseline: all steps exit 0'
exit 0
