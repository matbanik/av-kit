# Session 104 ytdlp-challenge-and-cookie-test baseline (task row 0; implementation-plan.md
# §Verification Plan 1). The shape of docs/execution/plans/2026-11-22-tray-show-and-baseline-fixes/
# baseline.ps1. Its steps:
# 1. the record: HEAD (recorded, never compared with a pinned commit), git status and git
#    worktree list; baseline.sha and baseline-dirty.txt; baseline-scope.json over §Files Modified
#    (eol-check.py's SCOPE: each existing path by hash, each new path absent, the shared closeout
#    files as {"kind": "shared", "sha256": ...}) and the "Read, never changed" files (hash);
#    baseline-dirty-hashes.json, which binds every dirty path outside this scope by hash; the
#    row-0 copies under R/baseline-copies; baseline-eol.json; baseline-pins.json (the read-only
#    test files' hashes, the top-level ast sources of the five pytest files of §Pins that move,
#    and the SABR_KEPT member sources); baseline-citations.txt (each anchor found once);
#    R/baseline-tags.txt; the free ids (AC-168., AC-169., AC-170. only in this session's own
#    files; D-1460 to D-1499 only in the plan folder, the grouping file and this session's own
#    handoffs and reflection, which cite the plan's decisions; a line that only closes a range
#    or cites this plan by its slug is not a use, D-1471);
# 2. one host-load sample (host-wait.py; recorded, the dev PC starts no Electron).
# Uv sync is not run: row 1 needs the installed yt-dlp 2026.10.26 as found. The scope walk drops
# .mcp.json, mcp-token.txt, .claude.json, .env, .env.*, .claude/settings.local.json and
# .agent/fleet/hub before any stat or read. Run from the repository root in pwsh.
$ErrorActionPreference = 'Stop'
$root = (git rev-parse --show-toplevel).Trim()
Set-Location $root
$plan = 'docs/execution/plans/2026-11-26-ytdlp-challenge-and-cookie-test'
$receipts = 'C:/Temp/av-kit/2026-11-26-ytdlp-challenge-and-cookie-test'
Remove-Item Env:ELECTRON_RUN_AS_NODE -ErrorAction SilentlyContinue
$env:PYTHONIOENCODING = 'utf-8'
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:RECEIPTS_DIR = 'C:/Temp/av-kit'
# Undated on purpose: a dated TEMP folder is the ancestor that TOOLING-PLAN-SLUG-ANCESTOR-MATCH reads.
$tmp = 'C:\Temp\av-kit\s104-tmp'
New-Item -ItemType Directory -Force -Path $tmp | Out-Null
$env:TMP = $tmp
$env:TEMP = $tmp

$record = @'
import hashlib, importlib.util, json, pathlib, re, subprocess, sys

SLUG = "2026-11-26-ytdlp-challenge-and-cookie-test"
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


rck = load("ycc_row_check", "row-check.py")
SCOPE = rck.SCOPE
SHARED = (
    ".agent/context/known-issues.yaml", ".agent/context/known-issues.md",
    ".agent/context/meu-status.yaml", ".agent/context/meu-registry.md", "docs/BUILD_PLAN.md",
    ".agent/context/current-focus.md", "docs/execution/metrics.md", rck.GROUPING,
)
OWN_FILES = (f"{PLAN.as_posix()}/", f".agent/context/handoffs/{SLUG}-", f"docs/execution/reflections/{SLUG}-")
NEW = tuple(p for p, kind in SCOPE.items() if kind == "NEW")
MODIFIED = tuple(p for p in SCOPE if p not in NEW and p not in SHARED)
ANCHORS = (
    (rck.TEST_API, "def test_ac_15_7_cookie_test_envelope("),
    (rck.TEST_API, 'assert "HTTP_COOKIE" not in ok.text'),
    (rck.TEST_DOMAIN, "def test_ac_4_4_cookie_test_result_shape("),
    (rck.TEST_DOMAIN, 'assert "cookies" not in _field_names(CookieTestResult)'),
    (rck.YT_TEST, "def test_ac_6_13_test_cookies_never_raises_cookie_error("),
    (rck.YT_TEST, 'assert "Netscape" not in (missing.error_message or "")'),
    (rck.INFRA_PY, '"yt-dlp",'),
    (rck.DOMAIN, "class CookieTestResult"),
    (rck.TEST_IDS, "export const HELP_SHOT = 'help-shot'"),
    (rck.LOCK, 'version = "2026.10.26"'),
)


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

scope = {}
for p in MODIFIED:
    scope[p] = sha(p)
    if scope[p] in ("absent", "not-a-file"):
        problems.append(f"S2: a modified path is missing: {p}")
for p in NEW:
    scope[p] = sha(p)
    if scope[p] != "absent":
        problems.append(f"S2: a new path already exists: {p}")
for p in rck.READ_ONLY:
    scope[p] = sha(p)
    if scope[p] in ("absent", "not-a-file"):
        problems.append(f"S2: a read-only path is missing: {p}")
for p in SHARED:
    scope[p] = {"kind": "shared", "sha256": sha(p)}
    if not pathlib.Path(p).is_file():
        problems.append(f"S2: a shared path is missing: {p}")
dump("baseline-scope.json", scope)
print("baseline-scope.json", len(scope), "paths:", len(MODIFIED), "modified,", len(NEW), "new (absent),",
      len(rck.READ_ONLY), "read, never changed,", len(SHARED), "shared")
for p in (*MODIFIED, *rck.READ_ONLY):
    if p in dirty:
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
for p in (*MODIFIED, *SHARED, *rck.READ_ONLY, *PLAN_FILES):
    src = pathlib.Path(p)
    if not src.is_file():
        continue
    dest = COPIES / p
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(src.read_bytes())
    copied += 1
print("baseline-copies", copied, "row-0 copies under", COPIES.as_posix())

eols = {}
for p in (*SCOPE, *rck.READ_ONLY):
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

pins = {"files": {p: sha(p) for p in rck.READ_TESTS}, "ast": {}, "kept": {}}
for p, h in pins["files"].items():
    if h in ("absent", "not-a-file"):
        problems.append(f"S2: a pin file is missing: {p}")
for p in rck.PY_PINNED:
    nodes = rck.top_level_sources(pathlib.Path(p).read_bytes().decode("utf-8"))
    pins["ast"][p] = nodes
    print("pins ast", p, len(nodes), "nodes")
for p, names in rck.KEPT.items():
    pins["kept"][p] = rck.member_sources(pathlib.Path(p).read_bytes().decode("utf-8"), names)
    missing = [n for n, s in pins["kept"][p].items() if s == "<missing>"]
    print("pins kept", p, len(names), "members; missing", missing or "none")
    if missing:
        problems.append(f"S2: SABR_KEPT members missing in {p}: {missing}")
for p, tests in rck.MOVED_PY.items():
    for name, (new, kept) in tests.items():
        src = pins["ast"][p].get(name, "")
        if not src or any(k not in src for k in kept):
            problems.append(f"S2: {p}:{name} lacks its kept needles at row 0")
dump("baseline-pins.json", pins)
print("baseline-pins.json", len(pins["files"]), "files,", sum(len(v) for v in pins["ast"].values()), "ast nodes")

cites = []
for p, needle in ANCHORS:
    lines = pathlib.Path(p).read_bytes().decode("utf-8").replace("\r\n", "\n").split("\n")
    hits = [i + 1 for i, ln in enumerate(lines) if needle in ln]
    if len(hits) != 1:
        problems.append(f"S2: anchor {needle[:80]!r} in {p}: {'missing' if not hits else f'doubled {hits}'}")
    cites.append(f"anchor {p}:{hits[0] if len(hits) == 1 else '-'} hits={len(hits)} :: {needle[:100]}")
if not pathlib.Path(rck.TEST_IDS).read_bytes().endswith(b"export const HELP_SHOT = 'help-shot'\r\n"):
    problems.append("S2: test-ids.ts does not end with the HELP_SHOT line and CRLF")
for line in cites:
    print(line)
(PLAN / "baseline-citations.txt").write_bytes(("\n".join(cites) + "\n").encode("utf-8"))
print("baseline-citations.txt", len(ANCHORS), "anchors")

tags = git("tag").decode("utf-8")
(OUT / "baseline-tags.txt").write_bytes(tags.encode("utf-8"))
print("baseline-tags.txt", len(tags.split()), "tags")


def grep_lines(pattern, fixed):
    flag = "-F" if fixed else "-E"
    run = subprocess.run(["git", "grep", "--untracked", "-n", flag, pattern, "--", ".", *GREP_EXCLUDES], capture_output=True)
    if run.returncode not in (0, 1):
        problems.append(f"git grep {pattern!r} exited {run.returncode}")
    return [ln for ln in run.stdout.decode("utf-8", "replace").splitlines() if ln]


OWN = (*OWN_FILES, rck.GROUPING + ":")
for name in ("AC-168.", "AC-169.", "AC-170."):
    hits = grep_lines(name, True)
    foreign = [ln for ln in hits if not ln.startswith(OWN)]
    print(f"free id {name!r}: {len(hits) - len(foreign)} hit(s) in this session's files, foreign {[ln[:120] for ln in foreign] or 'none'}")
    if foreign:
        problems.append(f"S2: {name} is already used outside this session's files")
D_ID = re.compile(r"D-(14[6-9][0-9])\b")
RANGE_END = re.compile(r"(?:\bto |\.\.)D-(14[6-9][0-9])\b")
used, notes = [], []
for ln in grep_lines(D_ID.pattern, False):
    if ln.startswith(OWN):
        continue
    text = ln.split(":", 2)[-1]
    if SLUG in text or len(D_ID.findall(text)) <= len(RANGE_END.findall(text)):
        notes.append(ln)
    else:
        used.append(ln)
for ln in notes:
    print("  D-1460..D-1499 range end or citation of this plan (not a use):", ln[:160])
print("D-1460..D-1499 used outside this session's files:", [ln[:120] for ln in used] or "none")
if used:
    problems.append("S2: D-1460 to D-1499 are used outside this session's files")

for p in PLAN_FILES:
    print("plan file", p, sha(p)[:16])
for p in problems:
    print("PROBLEM:", p)
print(f"baseline record: {len(problems)} problem(s)")
sys.exit(1 if problems else 0)
'@

New-Item -ItemType Directory -Force -Path $receipts | Out-Null
Set-Content -Path "$receipts/baseline-record.py" -Value $record -Encoding utf8

& rtk proxy uv run --no-sync python "$receipts/baseline-record.py"
$code = $LASTEXITCODE
Write-Output ("baseline step record exit={0}" -f $code)
if ($code -ne 0) { exit $code }

& rtk proxy uv run --no-sync python "$plan/host-wait.py" > "$receipts/ycc-base-load.txt" 2>&1
$load = $LASTEXITCODE
Get-Content "$receipts/ycc-base-load.txt" -Tail 3
Write-Output ("baseline step host-load exit={0} (recorded; no Electron starts on the dev PC)" -f $load)
Write-Output 'baseline: all steps exit 0'
exit 0
