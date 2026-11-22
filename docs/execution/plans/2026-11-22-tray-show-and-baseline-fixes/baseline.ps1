# Session 102 tray-show-and-baseline-fixes baseline (task row 0; implementation-plan.md §Verification Plan 1).
# The shape of docs/execution/plans/2026-11-21-transcript-job-resume/baseline.ps1. Its steps:
# 1. uv sync --frozen --offline --all-packages (S7 on a held file);
# 2. the record: HEAD (recorded, never compared with a pinned commit), git status and git
#    worktree list; baseline.sha and baseline-dirty.txt; baseline-scope.json over §Files Modified
#    (each existing path by hash, each new path absent), the "Read, never changed" files (hash)
#    and the shared files (current-focus.md, metrics.md, known-issues.yaml and .md: an object
#    {"kind": "shared", "sha256": ...}); baseline-dirty-hashes.json, which binds every dirty path
#    outside this scope by hash; the row-0 copies under R/baseline-copies (eol-check.py's and
#    row-check.py's base); baseline-eol.json; baseline-pins.json (the §Test pins files' hashes, and
#    the top-level ast sources of test_capture_adapter.py and validate_closeout_artifacts.py
#    through row-check.py's top_level_sources); a dry run of debt-edit.py's Red and Green edits
#    on the row-0 bytes (each old text found once); baseline-citations.txt (each §Verification
#    Plan 1 step 4 anchor found once by text, its line recorded); the free ids (DECLARED_NEW,
#    AC-164., D-1365 to D-1399; a match that only closes another session's claimed range,
#    "to D-1399" or "..D-1399", is not a use, D-1370);
# 3. one host-load sample (host-wait.py; the 50 % limit);
# 4. the base receipts: full Vitest (pwsh in ui/) and full pytest under the undated TEMP,
#    failures recorded, not fatal;
# 5. the plan-local checkers' selftests, eol-check.py over the fresh copies, and ruff on this
#    folder's Python (Session 82 RULE-1).
# Every step except 4 is fail-fast. The scope walk drops .mcp.json, mcp-token.txt, .claude.json,
# .env, .env.*, .claude/settings.local.json and .agent/fleet/hub before any stat or read. Run from
# the repository root in pwsh.
$ErrorActionPreference = 'Stop'
$root = (git rev-parse --show-toplevel).Trim()
Set-Location $root
$plan = 'docs/execution/plans/2026-11-22-tray-show-and-baseline-fixes'
$receipts = 'C:/Temp/av-kit/2026-11-22-tray-show-and-baseline-fixes'
Remove-Item Env:ELECTRON_RUN_AS_NODE -ErrorAction SilentlyContinue
$env:PYTHONIOENCODING = 'utf-8'
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:RECEIPTS_DIR = 'C:/Temp/av-kit'
# Undated on purpose: a dated TEMP folder is the ancestor that TOOLING-PLAN-SLUG-ANCESTOR-MATCH reads.
$tmp = 'C:\Temp\av-kit\s102-tmp'
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
import hashlib, importlib.util, json, pathlib, re, subprocess, sys

PLAN = pathlib.Path("docs/execution/plans/2026-11-22-tray-show-and-baseline-fixes")
OUT = pathlib.Path("C:/Temp/av-kit/2026-11-22-tray-show-and-baseline-fixes")
COPIES = OUT / "baseline-copies"
SLUG = "2026-11-22-tray-show-and-baseline-fixes"
E2E = "ui/tests/e2e"
UNIT = "ui/tests/unit"
TRAY = "ui/src/main/capture-tray.ts"
INDEX = "ui/src/main/index.ts"
E2E_SHELL = "ui/src/main/e2e-shell.ts"
ELECTRON_ENV = f"{E2E}/electron-env.ts"
ADAPTER = "tests/unit/test_capture_adapter.py"
VALIDATOR = "tools/validate_closeout_artifacts.py"
CANON = "docs/build-plan/09-screenshot-capture.md"
GROUPING = f".agent/context/grouping/{SLUG}-session-grouping.md"
HANDOFF = f".agent/context/handoffs/{SLUG}-MEU-164-handoff.md"
IMPL_REVIEW = f".agent/context/handoffs/{SLUG}-implementation-critical-review.md"
PLAN_REVIEW = f".agent/context/handoffs/{SLUG}-plan-critical-review.md"
REFLECTION = f"docs/execution/reflections/{SLUG}-reflection.md"
# §Files Modified that exist at row 0, with each file's line-ending kind (measured at plan time).
MODIFIED = {
    TRAY: "LF",
    ADAPTER: "CRLF",
    VALIDATOR: "CRLF",
    CANON: "CRLF",
    ".agent/context/meu-status.yaml": "LF",
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
    f"{UNIT}/capture-tray.test.ts",
    f"{E2E}/tray-double-click.test.ts",
    "tests/tooling/test_closeout_plan_slug.py",
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


# §Test pins files (by hash). test_capture_adapter.py and validate_closeout_artifacts.py are
# pinned by ast, node by node.
PIN_FILES = (
    f"{UNIT}/app-icon.test.ts",
    f"{UNIT}/capture-main.behavior.test.ts",
    f"{UNIT}/capture-page.test.ts",
    f"{UNIT}/login-item-ipc.test.ts",
    f"{E2E}/startup-reveal.test.ts",
    "tests/tooling/test_framework_adoption.py",
)
# "Read, never changed": bound by hash; their kind is recorded, not expected.
READ_ONLY = (
    INDEX,
    E2E_SHELL,
    "ui/src/main/app-icon.ts",
    "ui/src/main/notify-user.ts",
    f"{UNIT}/helpers/electron-stub.ts",
    "ui/vitest.config.ts",
    f"{E2E}/electron-app.ts",
    ELECTRON_ENV,
    f"{E2E}/test-ids.ts",
    "packages/infrastructure/src/avkit_infra/capture/adapter.py",
    "tests/tooling/test_closeout_record_once.py",
    *PIN_FILES,
)
SCOPE_PREFIXES = (
    PLAN.as_posix() + "/",
    f".agent/context/handoffs/{SLUG}-",
    f"docs/execution/reflections/{SLUG}-",
)
DECLARED_NEW = (
    "showWindow", "__AVKIT_E2E_TRAY__", "capture-tray.test", "tray-double-click.test",
    "_same_icc_ignoring_creation", "test_closeout_plan_slug",
)
problems = []


def load(name, file):
    spec = importlib.util.spec_from_file_location(name, PLAN / file)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


rck = load("tsb_row_check", "row-check.py")
dbt = rck.dbt

# Anchors (path, plan line or None, text): found once by text; a moved line is recorded for the
# handoff; a missing or doubled anchor is S2. The plan gives no line numbers, so each found line
# is recorded as is.
ANCHORS = (
    (TRAY, None, "label: 'Show window',"),
    (TRAY, None, "opts.window.show()"),
    (TRAY, None, "tray.setContextMenu(menu)"),
    (TRAY, None, "registerNotifyTray(tray)"),
    (INDEX, None, "startCaptureTray({"),
    (INDEX, None, "target.on('second-instance'"),
    (E2E_SHELL, None, "shellGlobal.__AVKIT_E2E_SHELL_LOG__ = e2eShellLog"),
    (ELECTRON_ENV, None, "env.AVKIT_E2E = '1'"),
    (ADAPTER, None, "def test_ac_130_10_cmyk_icc_to_srgb"),
    (ADAPTER, None, dbt.AC_130_10_LINE_OLD.strip()),
    (VALIDATOR, None, "def plan_slug("),
    (VALIDATOR, None, 'for part in reversed(parts[:-1] if parts[-1].endswith(".md") else parts):'),
    (VALIDATOR, None, '"unslugged-plan-path-is-usage",'),
    (CANON, None, rck.TRAY_ROW_OLD),
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

# baseline-pins.json: the pin files' hashes, and the two Python files' top-level ast sources.
pins = {"files": {p: sha(p) for p in PIN_FILES}, "ast": {}}
for p, h in pins["files"].items():
    if h in ("absent", "not-a-file"):
        problems.append(f"S2: a pin file is missing: {p}")
for p in (ADAPTER, VALIDATOR):
    nodes = rck.top_level_sources(pathlib.Path(p).read_bytes().decode("utf-8"))
    pins["ast"][p] = nodes
    doubled = [k for k in nodes if "#" in k.split(":", 1)[0]]
    print("pins ast", p, len(nodes), "nodes; doubled keys (a note, not a problem):", doubled or "none")
adapter_130 = pins["ast"][ADAPTER].get(dbt.AC_130_10, "")
checks = {
    "AC-130.10 starts at its first decorator": adapter_130.startswith(dbt.AC_130_10_HEAD),
    "AC-130.10 holds its comparison line once": adapter_130.count(dbt.AC_130_10_LINE_OLD.rstrip("\n")) == 1,
    "AC-130.10 ends with its last line": adapter_130.endswith(dbt.AC_130_10_LAST.rstrip("\n")),
    "plan_slug is debt-edit.py's old form": pins["ast"][VALIDATOR].get(dbt.PLAN_SLUG_FN) == dbt.PLAN_SLUG_OLD,
    "no new name is a node yet": not ({dbt.HELPER, *dbt.AC_164_8} & set(pins["ast"][ADAPTER])),
}
for name, ok in checks.items():
    print("pins old form:", name, ok)
    if not ok:
        problems.append(f"S2: {name} is false")
dump("baseline-pins.json", pins)
print("baseline-pins.json", len(pins["files"]), "files,", sum(len(v) for v in pins["ast"].values()), "ast nodes")

# A dry run of debt-edit.py on the row-0 bytes: every old text found once, nothing written.
red, red_problems = dbt.apply(pathlib.Path(ADAPTER).read_bytes(), dbt.red_edits(), ADAPTER)
green = dbt.green_edits()
_, green_problems = dbt.apply(red, green[ADAPTER], ADAPTER)
_, slug_problems = dbt.apply(pathlib.Path(VALIDATOR).read_bytes(), green[VALIDATOR], VALIDATOR)
for p in red_problems + green_problems + slug_problems:
    problems.append(f"S2: debt-edit dry run: {p}")
print("debt-edit dry run:", len(red_problems + green_problems + slug_problems), "problem(s)")

# baseline-citations.txt.
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
for line in cites:
    print(line)
(PLAN / "baseline-citations.txt").write_bytes(("\n".join(cites) + "\n").encode("utf-8"))
print("baseline-citations.txt", len(ANCHORS), "anchors")


# Free ids. This session's own files (the plan folder, its handoffs and reflection, and the
# grouping file, whose path names this session) may name them; nothing else.
def grep_lines(pattern, fixed):
    flag = "-F" if fixed else "-E"
    run = subprocess.run(["git", "grep", "--untracked", "-n", flag, pattern, "--", ".", *GREP_EXCLUDES], capture_output=True)
    if run.returncode not in (0, 1):
        problems.append(f"git grep {pattern!r} exited {run.returncode}")
    return [ln for ln in run.stdout.decode("utf-8", "replace").splitlines() if ln]


OWN = (*SCOPE_PREFIXES, GROUPING + ":")
for name in (*DECLARED_NEW, "AC-164."):
    hits = grep_lines(name, True)
    foreign = [ln for ln in hits if not ln.startswith(OWN)]
    own = len(hits) - len(foreign)
    print(f"free id {name!r}: {own} hit(s) in this session's files, foreign {[ln[:120] for ln in foreign] or 'none'}")
    if foreign:
        problems.append(f"S2: {name} is already used outside this session's files")
# D-1370: "to D-1399" or "..D-1399" closes another session's claimed range; it uses no id.
D_ID = re.compile(r"D-(136[5-9]|13[7-9][0-9])\b")
RANGE_END = re.compile(r"(?:\bto |\.\.)D-(136[5-9]|13[7-9][0-9])\b")
used, range_ends = [], []
for ln in grep_lines(D_ID.pattern, False):
    if ln.startswith(OWN):
        continue
    text = ln.split(":", 2)[-1]
    (used if len(D_ID.findall(text)) > len(RANGE_END.findall(text)) else range_ends).append(ln)
print("D-1365..D-1399 range ends outside this session's files (not a use):", len(range_ends))
for ln in range_ends:
    print("  range end", ln[:140])
print("D-1365..D-1399 used outside this session's files:", [ln[:120] for ln in used] or "none")
if used:
    problems.append("S2: D-1365 to D-1399 are used outside this session's files")

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
& rtk proxy uv run --no-sync python "$plan/host-wait.py" > "$receipts/tsb-base-load.txt" 2>&1
$loadCode = $LASTEXITCODE
Get-Content "$receipts/tsb-base-load.txt" | Select-Object -Last 3
Write-Output ("baseline step host-load exit={0} receipt={1}/tsb-base-load.txt" -f $loadCode, $receipts)
if ($loadCode -ne 0) { exit $loadCode }

# 4. The base receipts: failures recorded, not fatal; the gate excuses only those ids.
Push-Location 'P:\av-kit\ui'
& rtk proxy npm run test *> "$receipts/tsb-base-ui.txt"
$uiCode = $LASTEXITCODE
Pop-Location
Set-Content -Path "$receipts/tsb-base-ui.txt.exit" -Value $uiCode -Encoding ascii
Write-Output ("base suite ui exit={0} receipt={1}/tsb-base-ui.txt" -f $uiCode, $receipts)
Get-Content "$receipts/tsb-base-ui.txt" | Select-String -Pattern 'Test Files|Tests |FAIL ' | Select-Object -Last 12

& rtk proxy uv run --no-sync pytest -q *> "$receipts/tsb-base-py.txt"
$pyCode = $LASTEXITCODE
Set-Content -Path "$receipts/tsb-base-py.txt.exit" -Value $pyCode -Encoding ascii
Write-Output ("base suite pytest exit={0} receipt={1}/tsb-base-py.txt" -f $pyCode, $receipts)
Get-Content "$receipts/tsb-base-py.txt" | Select-String -Pattern '^FAILED|^ERROR|passed|failed' | Select-Object -Last 12

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
