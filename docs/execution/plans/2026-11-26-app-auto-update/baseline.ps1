# Session 106 app-auto-update baseline (task row 0; implementation-plan.md §Verification Plan 1).
# The shape of docs/execution/plans/2026-11-22-tray-show-and-baseline-fixes/baseline.ps1, through
# Session 103's copy (2026-11-26-capture-key-inbox-scrollbars/baseline.ps1). Fail-fast. Its steps:
# 0. uv sync --frozen --offline --all-packages;
# 1. the record: HEAD (recorded, never compared with a pinned commit), git status and git
#    worktree list; baseline.sha, baseline-dirty.txt and baseline-dirty-hashes.json (every dirty
#    path outside this scope, by hash);
# 2. baseline-scope.json over §Files Modified and §Test pins (eol-check.py's SCOPE: each existing
#    path by hash, each new path absent, the shared state files as {"kind": "shared",
#    "sha256": ...}); the row-0 copies under R/baseline-copies; baseline-eol.json;
# 3. baseline-pins.json (pins-scan.py: which §Test pins files enumerate a list, and their hashes);
# 4. the free ids: AC-173., AC-174. and D-1540 to D-1599 only in this session's own files and the
#    grouping file (a line whose matches only close a range, or that cites this plan by its slug,
#    is not a use); D-1555 is the first unused id; the DECLARED_NEW names are printed with their
#    hits (informational; every new path is checked absent in step 2);
# 5. the base receipts: full Vitest (aau-base-ui.txt, pwsh in ui/), full pytest (aau-base-py.txt)
#    and the MCP tests (aau-base-mcp.txt), recorded, not fatal;
# 6. npm view electron-updater dist-tags --json into aau-dist-tags.json (one of the two network
#    rows; S7 when latest is not a 6.8 version);
# 7. tools/e2e_remote.py check --out aau-host-check-0.json (any result recorded, not fatal here;
#    an unreachable host becomes S9 at row 7);
# 8. every plan-local selftest, then ruff format --check and ruff check on the plan's Python.
# The scope walk drops .mcp.json, mcp-token.txt, .claude.json, .env, .env.*,
# .claude/settings.local.json and .agent/fleet/hub before any stat or read. No Electron starts on
# the dev PC. Run from the repository root in pwsh.
param([switch]$SelftestsOnly)
$ErrorActionPreference = 'Stop'
$root = (git rev-parse --show-toplevel).Trim()
Set-Location $root
$plan = 'docs/execution/plans/2026-11-26-app-auto-update'
$receipts = 'C:/Temp/av-kit/2026-11-26-app-auto-update'
Remove-Item Env:ELECTRON_RUN_AS_NODE -ErrorAction SilentlyContinue
$env:PYTHONIOENCODING = 'utf-8'
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:RECEIPTS_DIR = 'C:/Temp/av-kit'
# Undated on purpose: a dated TEMP folder is the ancestor that TOOLING-PLAN-SLUG-ANCESTOR-MATCH reads.
$tmp = 'C:\Temp\av-kit\s106-tmp'
New-Item -ItemType Directory -Force -Path $tmp | Out-Null
$env:TMP = $tmp
$env:TEMP = $tmp
New-Item -ItemType Directory -Force -Path $receipts | Out-Null

# -SelftestsOnly runs step 8 alone (D-1558): steps 0 to 7 recorded the tree before row 1, and a
# second record after row 1 would find its new files present.
if (-not $SelftestsOnly) {
& rtk proxy uv sync --frozen --offline --all-packages
$code = $LASTEXITCODE
Write-Output ("baseline step uv-sync exit={0}" -f $code)
if ($code -ne 0) { exit $code }

$record = @'
import hashlib, importlib.util, json, pathlib, re, subprocess, sys

SLUG = "2026-11-26-app-auto-update"
PLAN = pathlib.Path(f"docs/execution/plans/{SLUG}")
OUT = pathlib.Path(f"C:/Temp/av-kit/{SLUG}")
COPIES = OUT / "baseline-copies"
SECRET_BASES = (".mcp.json", "mcp-token.txt", ".claude.json", ".env")
GREP_EXCLUDES = (
    ":(exclude,glob)**/.mcp.json", ":(exclude,glob)**/mcp-token.txt", ":(exclude,glob)**/.claude.json",
    ":(exclude,glob)**/.env", ":(exclude,glob)**/.env.*", ":(exclude,glob)**/.claude/settings.local.json",
    ":(exclude).agent/fleet/hub",
)
problems = []


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


def load(name, file):
    spec = importlib.util.spec_from_file_location(name, PLAN / file)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


rck = load("aau_row_check", "row-check.py")
red = load("aau_red_check", "red-check.py")
SCOPE = rck.SCOPE
SHARED = tuple(rck.eolc.SHARED_KINDS)
OWN_FILES = (f"{PLAN.as_posix()}/", f".agent/context/handoffs/{SLUG}-", f"docs/execution/reflections/{SLUG}-")
NEW = tuple(p for p, kind in SCOPE.items() if kind == "NEW")
MODIFIED = tuple(p for p in SCOPE if p not in NEW and p not in SHARED)
DECLARED_NEW = tuple(red.DECLARED_NEW[:22])


def sha(p):
    path = pathlib.Path(p)
    if not path.exists():
        return "absent"
    if not path.is_file():
        return "not-a-file"
    return hashlib.sha256(path.read_bytes()).hexdigest()


def eol(raw):
    crlf = raw.count(b"\r\n")
    bare = raw.count(b"\n") - crlf
    kind = "MIXED" if crlf and bare else "CRLF" if crlf else "LF" if bare else "none"
    return kind, crlf, bare


def dump(name, data):
    (PLAN / name).write_bytes((json.dumps(data, indent=2, ensure_ascii=False) + "\n").encode("utf-8"))


# 1. the tree
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

# 2. scope binding, copies, line endings
scope = {}
for p in MODIFIED:
    scope[p] = sha(p)
    if scope[p] in ("absent", "not-a-file"):
        problems.append(f"S2: a modified path is missing: {p}")
for p in NEW:
    scope[p] = sha(p)
    if scope[p] != "absent":
        problems.append(f"S2: a new path already exists: {p}")
for p in SHARED:
    scope[p] = {"kind": "shared", "sha256": sha(p)}
    if not pathlib.Path(p).is_file():
        problems.append(f"S2: a shared path is missing: {p}")
dump("baseline-scope.json", scope)
print("baseline-scope.json", len(scope), "paths:", len(MODIFIED), "modified or pinned,", len(NEW),
      "new (absent),", len(SHARED), "shared")
for p in MODIFIED:
    if p in dirty and not p.startswith(OWN_FILES):
        print("  scope path dirty at row 0 (recorded by hash):", p)


def in_scope(p):
    return p in scope or p.startswith(OWN_FILES)


hashes = {p: (sha(p) if pathlib.Path(p).exists() else "deleted") for p in dirty if not in_scope(p) and not secret(p)}
(PLAN / "baseline-dirty-hashes.json").write_bytes((json.dumps(hashes, indent=2, sort_keys=True) + "\n").encode())
print("baseline-dirty-hashes.json", len(hashes), "paths outside this scope")
for p in sorted(hashes):
    print("  bound by hash", p, hashes[p][:16])

PLAN_FILES = [p.as_posix() for p in sorted(PLAN.iterdir()) if p.is_file() and p.suffix in (".md", ".py", ".ps1", ".json")]
copied = 0
for p in (*MODIFIED, *SHARED, *PLAN_FILES):
    src = pathlib.Path(p)
    if not src.is_file():
        continue
    dest = COPIES / p
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(src.read_bytes())
    copied += 1
print("baseline-copies", copied, "row-0 copies under", COPIES.as_posix())

eols = {}
for p in SCOPE:
    want = SCOPE.get(p)
    want = "absent" if want == "NEW" else want
    if not pathlib.Path(p).is_file():
        eols[p] = {"kind": "absent", "expected": want}
        if want != "absent":
            problems.append(f"S2: {p} is absent, the plan says {want}")
        continue
    raw = pathlib.Path(p).read_bytes()
    kind, crlf, bare = eol(raw)
    eols[p] = {"kind": kind, "expected": want, "crlf": crlf, "bare_lf": bare,
               "bom": raw.startswith(b"\xef\xbb\xbf"), "bytes": len(raw)}
    print("eol", kind, "crlf", crlf, "bare_lf", bare, "bytes", len(raw), p)
    if want is not None and kind != want:
        if p in SHARED:
            print("  measured, not expected (shared, as measured in row 0):", p, kind)
        else:
            problems.append(f"S2: {p} is {kind}, the plan says {want}")
dump("baseline-eol.json", eols)
print("baseline-eol.json", len(eols), "paths")


# 4. free ids
def grep_lines(pattern, fixed):
    flag = "-F" if fixed else "-E"
    run = subprocess.run(["git", "grep", "--untracked", "-n", flag, pattern, "--", ".", *GREP_EXCLUDES], capture_output=True)
    if run.returncode not in (0, 1):
        problems.append(f"git grep {pattern!r} exited {run.returncode}")
    return [ln for ln in run.stdout.decode("utf-8", "replace").splitlines() if ln]


OWN = (*OWN_FILES, rck.GROUPING + ":")
for name in ("AC-173.", "AC-174."):
    hits = grep_lines(name, True)
    foreign = [ln for ln in hits if not ln.startswith(OWN)]
    print(f"free id {name!r}: {len(hits) - len(foreign)} hit(s) in this session's files, foreign {[ln[:140] for ln in foreign] or 'none'}")
    if foreign:
        problems.append(f"S2: {name} is already used outside this session's files")
for name in DECLARED_NEW:
    word = re.compile(r"(?<![\w-])" + re.escape(name) + r"(?![\w-])")
    hits = [ln for ln in grep_lines(name, True) if word.search(ln.split(":", 2)[-1])]
    foreign = sorted({ln.split(":", 1)[0] for ln in hits if not ln.startswith(OWN)})
    print(f"name {name!r} (informational): {len(hits)} hit(s); files outside this session's: {foreign[:6] or 'none'}")
D_ID = re.compile(r"D-(15[4-9][0-9])\b")
RANGE_END = re.compile(r"(?:\bto |\.\.|–|-)D-(15[4-9][0-9])\b")
# A use is a definition: a decision-log "id: D-15xx" entry or a "### D-15xx" heading. Any other
# line names a reserved id in passing, such as a later plan citing this reservation (D-1557).
DEFINES = re.compile(r"(?:\bid:\s*|^#+\s*)D-(15[4-9][0-9])\b")
used, notes, own_ids = [], [], set()
for ln in grep_lines(D_ID.pattern, False):
    text = ln.split(":", 2)[-1]
    if ln.startswith(OWN):
        own_ids.update(int(x) for x in DEFINES.findall(text.strip()))
        continue
    if SLUG in text or not DEFINES.search(text.strip()) or len(D_ID.findall(text)) <= len(RANGE_END.findall(text)):
        notes.append(ln)
    else:
        used.append(ln)
for ln in notes:
    print("  D-1540..D-1599 range end or citation of this plan (not a use):", ln[:160])
print("D-1540..D-1599 used outside this session's files:", [ln[:140] for ln in used] or "none")
if used:
    problems.append("S2: D-1540 to D-1599 are used outside this session's files")
first_free = next(n for n in range(1540, 1600) if n not in own_ids)
print(f"D-1540..D-1599 defined in this session's files: {sorted(own_ids)}; first unused D-{first_free}")
if first_free != 1555:
    problems.append(f"S2: the first unused id is D-{first_free}, not D-1555")

for p in PLAN_FILES:
    print("plan file", p, sha(p)[:16])
for p in problems:
    print("PROBLEM:", p)
print(f"baseline record: {len(problems)} problem(s)")
sys.exit(1 if problems else 0)
'@

Set-Content -Path "$receipts/baseline-record.py" -Value $record -Encoding utf8

& rtk proxy uv run --no-sync python "$receipts/baseline-record.py"
$code = $LASTEXITCODE
Write-Output ("baseline step record exit={0}" -f $code)
if ($code -ne 0) { exit $code }

# 3. the pins scan
& rtk proxy uv run --no-sync python "$plan/pins-scan.py"
$code = $LASTEXITCODE
Write-Output ("baseline step pins-scan exit={0}" -f $code)
if ($code -ne 0) { exit $code }

# 5. the base receipts (recorded, not fatal)
Set-Location (Join-Path $root 'ui')
& rtk proxy npm run test *> "$receipts/aau-base-ui.txt"
$ui = $LASTEXITCODE
Set-Location $root
Get-Content "$receipts/aau-base-ui.txt" -Tail 6
Write-Output ("baseline step base-ui exit={0} (recorded, not fatal)" -f $ui)

& rtk proxy uv run --no-sync pytest -p no:cacheprovider tests/ --tb=short -q *> "$receipts/aau-base-py.txt"
$pyt = $LASTEXITCODE
Get-Content "$receipts/aau-base-py.txt" -Tail 4
Write-Output ("baseline step base-py exit={0} (recorded, not fatal)" -f $pyt)

& rtk proxy npm --prefix mcp-server run test *> "$receipts/aau-base-mcp.txt"
$mcp = $LASTEXITCODE
Get-Content "$receipts/aau-base-mcp.txt" -Tail 6
Write-Output ("baseline step base-mcp exit={0} (recorded, not fatal)" -f $mcp)

# 6. the npm dist-tags (network row 1 of 2)
$tags = (& npm view electron-updater dist-tags --json) -join "`n"
$code = $LASTEXITCODE
[IO.File]::WriteAllText("$receipts/aau-dist-tags.json", $tags + "`n")
Write-Output $tags
if ($code -ne 0) { Write-Output ("baseline step dist-tags exit={0}" -f $code); exit $code }
$latest = ($tags | ConvertFrom-Json).latest
if ($latest -notmatch '^6\.8\.\d+$') {
    Write-Output "baseline step dist-tags: latest is $latest, not a 6.8 version (S7)"
    exit 7
}
Write-Output "baseline step dist-tags exit=0 latest=$latest"

# 7. the host check (recorded, not fatal)
& rtk proxy uv run --no-sync python tools/e2e_remote.py check --out "$receipts/aau-host-check-0.json" *> "$receipts/aau-host-check-0.txt"
$chk = $LASTEXITCODE
Get-Content "$receipts/aau-host-check-0.txt" -Tail 4
Write-Output ("baseline step host-check exit={0} (recorded, not fatal in row 0; an unreachable host is S9 at row 7)" -f $chk)
}

# 8. selftests and ruff on the plan's Python
$py = @('uv', 'run', '--no-sync', 'python')
$snapSelftest = Join-Path $tmp ("aau-snapshot-selftest-{0}" -f [DateTime]::UtcNow.Ticks)
$selftests = @(
    @("$plan/row-check.py", '--selftest'),
    @("$plan/pins-scan.py", '--selftest'),
    @("$plan/run-check.py", '--selftest'),
    @("$plan/licence-check.py", '--selftest'),
    @("$plan/red-check.py", '--selftest'),
    @("$plan/eol-check.py", '--selftest'),
    @("$plan/identity.py", '--selftest'),
    @("$plan/snapshot-commit.py", '--selftest', $snapSelftest)
)
# canon-edit.py, issue-resolve.py and crlf.py have no --selftest, in their sources as here (D-1558);
# ruff below covers them.
foreach ($s in $selftests) {
    $name = [IO.Path]::GetFileNameWithoutExtension($s[0])
    $argv = $py + $s
    & rtk proxy @argv *> "$receipts/aau-selftest-$name.txt"
    $code = $LASTEXITCODE
    Get-Content "$receipts/aau-selftest-$name.txt" -Tail 1
    Write-Output ("baseline step selftest-{0} exit={1}" -f $name, $code)
    if ($code -ne 0) { exit $code }
}
$planPy = @(Get-ChildItem -Path $plan -Filter '*.py' | Sort-Object Name | ForEach-Object { "$plan/$($_.Name)" })
& rtk proxy uv run --no-sync ruff format --check @planPy
$code = $LASTEXITCODE
Write-Output ("baseline step ruff-format exit={0}" -f $code)
if ($code -ne 0) { exit $code }
& rtk proxy uv run --no-sync ruff check @planPy
$code = $LASTEXITCODE
Write-Output ("baseline step ruff-check exit={0}" -f $code)
if ($code -ne 0) { exit $code }
Write-Output 'baseline: all steps exit 0'
exit 0
