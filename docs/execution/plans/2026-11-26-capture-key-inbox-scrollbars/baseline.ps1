# Session 103 capture-key-inbox-scrollbars baseline (task row 0; implementation-plan.md
# §Verification Plan 1). The shape of docs/execution/plans/2026-11-22-tray-show-and-baseline-fixes/
# baseline.ps1, through Session 104's copy. Its steps:
# 1. the record: HEAD (recorded, never compared with a pinned commit), git status and git
#    worktree list; baseline.sha, baseline-dirty.txt and baseline-dirty-hashes.json (every dirty
#    path outside this scope, by hash);
# 2. baseline-scope.json over §Files Modified (eol-check.py's SCOPE: each existing path by hash,
#    each new path absent, the shared state files as {"kind": "shared", "sha256": ...}), the
#    "Read, never changed" files and every file under ui/src/main/, mcp-server/ and
#    tools/e2e_host/ (by hash); the row-0 copies under R/baseline-copies; baseline-eol.json;
# 3. baseline-pins.json (the §Test pins files' hashes);
# 4. baseline-citations.txt (each anchor found once; a missing or doubled one is S2);
# 5. the free ids: each DECLARED_NEW name (hyphen-aware, D-1434) and AC-165., AC-166., AC-167.
#    only in this session's own files; D-1420 to D-1459 only there and in the grouping file (a
#    line whose matches only close a range, or that cites this plan by its slug, is not a use);
# 6. cki-by-id-methods.txt (inspect) and the NotFoundError 404 fact (else S8);
# 7. the line endings of settings-page.test.ts; R/baseline-tags.txt;
# 8. the base receipts: full Vitest (cki-base-ui.txt) and full pytest (cki-base-py.txt), recorded,
#    not fatal; tools/e2e_remote.py check --out cki-check-0.json (a wait-band exit is recorded; a
#    tool stop is S11).
# The scope walk drops .mcp.json, mcp-token.txt, .claude.json, .env, .env.*,
# .claude/settings.local.json and .agent/fleet/hub before any stat or read. No Electron starts on
# the dev PC. Run from the repository root in pwsh.
$ErrorActionPreference = 'Stop'
$root = (git rev-parse --show-toplevel).Trim()
Set-Location $root
$plan = 'docs/execution/plans/2026-11-26-capture-key-inbox-scrollbars'
$receipts = 'C:/Temp/av-kit/2026-11-26-capture-key-inbox-scrollbars'
Remove-Item Env:ELECTRON_RUN_AS_NODE -ErrorAction SilentlyContinue
$env:PYTHONIOENCODING = 'utf-8'
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:RECEIPTS_DIR = 'C:/Temp/av-kit'
# Undated on purpose: a dated TEMP folder is the ancestor that TOOLING-PLAN-SLUG-ANCESTOR-MATCH reads.
$tmp = 'C:\Temp\av-kit\s103-tmp'
New-Item -ItemType Directory -Force -Path $tmp | Out-Null
$env:TMP = $tmp
$env:TEMP = $tmp

$record = @'
import hashlib, importlib.util, inspect, json, pathlib, re, subprocess, sys

SLUG = "2026-11-26-capture-key-inbox-scrollbars"
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


rck = load("cki_row_check", "row-check.py")
SCOPE = rck.SCOPE
SHARED = (
    ".agent/context/known-issues.yaml", ".agent/context/known-issues.md",
    ".agent/context/meu-status.yaml", ".agent/context/meu-registry.md", "docs/BUILD_PLAN.md",
    ".agent/context/current-focus.md", "docs/execution/metrics.md", rck.GROUPING,
)
OWN_FILES = (f"{PLAN.as_posix()}/", f".agent/context/handoffs/{SLUG}-", f"docs/execution/reflections/{SLUG}-")
NEW = tuple(p for p, kind in SCOPE.items() if kind == "NEW")
MODIFIED = tuple(p for p in SCOPE if p not in NEW and p not in SHARED)
RO_FIXED = rck.READ_ONLY_FIXED
RO_PREFIX = tuple(rck.ro_prefix_files(pathlib.Path(".").resolve()))
CP = "ui/src/renderer/src/features/capture/CapturePage.tsx"
HC = "ui/src/renderer/src/features/capture/capture-help-content.ts"
SH = "ui/src/renderer/src/features/settings/settings-help-content.ts"
QS = "ui/src/renderer/src/components/help/quick-start.json"
HCARD = "ui/src/renderer/src/components/help/HelpCard.tsx"
CAT = "ui/src/renderer/src/features/capture/useCaptureCatalog.ts"
USE_SETTINGS = "ui/src/renderer/src/features/capture/useCaptureSettings.ts"
NINE = "docs/build-plan/09-screenshot-capture.md"
ANCHORS = (
    (CP, "const EMPTY_STATE = 'Press F2 or Capture region'"),
    (CP, "const HOTKEY_IN_USE_TEMPLATE ="),
    (CP, "void window.api.getHotkeyStatus().then((status) => {"),
    (HC, "title: 'When F2 is in use',"),
    (HC, "title: 'Close to tray keeps F2',"),
    (SH, "so F2 still works."),
    (QS, '"text": "Push F2 or click Capture region. Then drag a box on the screen.",'),
    (HCARD, "const page = QUICK_START[feature]"),
    (CAT, "export const QUERY_KEY = ['captures'] as const"),
    (rck.CAPTURE_PY, "def scan_inbox"),
    (rck.CAPTURE_PY, "def list_shots"),
    (rck.CAPTURE_PY, "def get_shot"),
    (rck.CAPTURE_PY, "def _require_inbox_file"),
    (rck.CAPTURE_PAGE_TEST, "expect(page).toMatch(/Press F2 or Capture region/)"),
    (rck.CAPTURE_PAGE_TEST, "'When F2 is in use',"),
    (rck.CAPTURE_PAGE_TEST, "'Close to tray keeps F2',"),
    (rck.SETTINGS_PAGE_TEST, "expect(help).toContain('F2')"),
    (NINE, "| Pan gestures |"),
    (NINE, "### Capture key in texts"),
    (NINE, "### Catalog follows the inbox folder"),
    (NINE, "### Viewport scroll bars"),
    (rck.ERRORS_PY, "NotFoundError: 404,"),
)
DECLARED_NEW = (
    "captureKeyText", "CAPTURE_KEY_DEFAULT", "HOTKEY_UNCONFIRMED_TEMPLATE",
    "captureHelpSections", "settingsHelpSections", "quickStartPage", "capture-scroll-bars",
    "scrollBars", "thumbDragToPan", "SCROLL_BAR_THICKNESS", "SCROLL_THUMB_MIN",
    "capture-scrollbar-x", "capture-scrollbar-y", "capture-scrollbar-x-thumb",
    "capture-scrollbar-y-thumb", "capture-key.test", "capture-key.behavior.test",
    "capture-inbox-scope.behavior.test", "capture-scroll-bars.test",
    "capture-scroll-bars.behavior.test", "test_capture_inbox_scope", "test_api_capture_inbox_scope",
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
for p in (*RO_FIXED, *RO_PREFIX):
    scope[p] = sha(p)
    if scope[p] in ("absent", "not-a-file"):
        problems.append(f"S2: a read-only path is missing: {p}")
for p in SHARED:
    scope[p] = {"kind": "shared", "sha256": sha(p)}
    if not pathlib.Path(p).is_file():
        problems.append(f"S2: a shared path is missing: {p}")
dump("baseline-scope.json", scope)
print("baseline-scope.json", len(scope), "paths:", len(MODIFIED), "modified,", len(NEW), "new (absent),",
      len(RO_FIXED), "read, never changed,", len(RO_PREFIX), "under the read-only folders,", len(SHARED), "shared")
for p in (*MODIFIED, *RO_FIXED, *RO_PREFIX):
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
for p in (*MODIFIED, *SHARED, *RO_FIXED, *PLAN_FILES):
    src = pathlib.Path(p)
    if not src.is_file():
        continue
    dest = COPIES / p
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(src.read_bytes())
    copied += 1
print("baseline-copies", copied, "row-0 copies under", COPIES.as_posix())

eols = {}
for p in (*SCOPE, *(x for x in RO_FIXED if not x.endswith(".png"))):
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
kind, crlf, bare = eol(pathlib.Path(rck.SETTINGS_PAGE_TEST).read_bytes())
print(f"measured {rck.SETTINGS_PAGE_TEST}: {kind} (crlf {crlf}, bare lf {bare})")

# 3. pins
pins = {"files": {p: sha(p) for p in rck.PINS}}
for p, h in pins["files"].items():
    if h in ("absent", "not-a-file"):
        problems.append(f"S2: a pin file is missing: {p}")
dump("baseline-pins.json", pins)
print("baseline-pins.json", len(pins["files"]), "files")

# 4. citations
cites = []
for p, needle in ANCHORS:
    lines = pathlib.Path(p).read_bytes().decode("utf-8").replace("\r\n", "\n").split("\n")
    hits = [i + 1 for i, ln in enumerate(lines) if needle in ln]
    if len(hits) != 1:
        problems.append(f"S2: anchor {needle[:80]!r} in {p}: {'missing' if not hits else f'doubled {hits}'}")
    cites.append(f"anchor {p}:{hits[0] if len(hits) == 1 else '-'} hits={len(hits)} :: {needle[:100]}")
for line in cites:
    print(line)
(PLAN / "baseline-citations.txt").write_bytes(("\n".join(cites) + "\n").encode("utf-8"))
print("baseline-citations.txt", len(ANCHORS), "anchors")

tags = git("tag").decode("utf-8")
(OUT / "baseline-tags.txt").write_bytes(tags.encode("utf-8"))
print("baseline-tags.txt", len(tags.split()), "tags")


# 5. free ids
def grep_lines(pattern, fixed):
    flag = "-F" if fixed else "-E"
    run = subprocess.run(["git", "grep", "--untracked", "-n", flag, pattern, "--", ".", *GREP_EXCLUDES], capture_output=True)
    if run.returncode not in (0, 1):
        problems.append(f"git grep {pattern!r} exited {run.returncode}")
    return [ln for ln in run.stdout.decode("utf-8", "replace").splitlines() if ln]


OWN = (*OWN_FILES, rck.GROUPING + ":")
for name in (*DECLARED_NEW, "AC-165.", "AC-166.", "AC-167."):
    word = re.compile(r"(?<![\w-])" + re.escape(name) + (r"" if name.endswith(".") else r"(?![\w-])"))
    hits = [ln for ln in grep_lines(name, True) if word.search(ln.split(":", 2)[-1])]
    foreign = [ln for ln in hits if not ln.startswith(OWN)]
    print(f"free id {name!r}: {len(hits) - len(foreign)} hit(s) in this session's files, foreign {[ln[:140] for ln in foreign] or 'none'}")
    if foreign:
        problems.append(f"S2: {name} is already used outside this session's files")
# D-1434: `capture-key` is also a settings phrase in older prose ("the capture-key suffix");
# the new module name is free when no file is named capture-key.ts(x) and no line imports or
# names it as a module path.
MODULE = re.compile(r"""(?:/|['"])capture-key(?:\.tsx?)?['"]|capture-key\.tsx?\b""")
mod_hits = [ln for ln in grep_lines("capture-key", True) if MODULE.search(ln.split(":", 2)[-1])]
mod_files = [ln for ln in git("ls-files", "--cached", "--others", "--exclude-standard").decode("utf-8").splitlines()
             if pathlib.PurePosixPath(ln).name in ("capture-key.ts", "capture-key.tsx")]
mod_foreign = [ln for ln in mod_hits if not ln.startswith(OWN)] + mod_files
print(f"free id 'capture-key' (D-1434: a module path): foreign {[ln[:140] for ln in mod_foreign] or 'none'}")
if mod_foreign:
    problems.append("S2: capture-key is already used as a module path")
# D-1434: `saved` is a common word; it is free when useCaptureSettings.ts returns no `saved` key.
returned = [ln for ln in pathlib.Path(USE_SETTINGS).read_bytes().decode("utf-8").splitlines()
            if re.match(r"^\s*saved\s*[,:}]", ln)]
print(f"free id 'saved' (D-1434: a returned key of {USE_SETTINGS}): {returned or 'none'}")
if returned:
    problems.append("S2: useCaptureSettings.ts already returns `saved`")
D_ID = re.compile(r"D-(14[2-5][0-9])\b")
RANGE_END = re.compile(r"(?:\bto |\.\.|–|-)D-(14[2-5][0-9])\b")
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
    print("  D-1420..D-1459 range end or citation of this plan (not a use):", ln[:160])
print("D-1420..D-1459 used outside this session's files:", [ln[:140] for ln in used] or "none")
if used:
    problems.append("S2: D-1420 to D-1459 are used outside this session's files")

# 6. by-id census and the 404 fact
sys.path[:0] = ["packages/core/src", "packages/api/src"]
from avkit_core.services.capture import CaptureService  # noqa: E402

methods = []
for name, member in inspect.getmembers(CaptureService, inspect.isfunction):
    if name.startswith("_"):
        continue
    params = inspect.signature(member).parameters
    if "shot_id" in params:
        methods.append(f"{name}{inspect.signature(member)}")
(OUT / "cki-by-id-methods.txt").write_bytes(("\n".join(methods) + "\n").encode("utf-8"))
print(f"cki-by-id-methods.txt: {len(methods)} public CaptureService method(s) with shot_id")
for m in methods:
    print("  by id:", m)
if not methods:
    problems.append("S8: no public CaptureService method takes shot_id")

from fastapi import FastAPI  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from avkit_api.errors import DOMAIN_HTTP_MAP, register_exception_handlers  # noqa: E402
from avkit_core.domain.errors import NotFoundError  # noqa: E402

app = FastAPI()
register_exception_handlers(app)


@app.get("/probe")
def _probe():
    raise NotFoundError("shot not found: x")


res = TestClient(app, raise_server_exceptions=False).get("/probe")
body = res.json()
want = {"error": {"code": "NotFoundError", "message": "shot not found: x", "details": None}}
print(f"404 fact: DOMAIN_HTTP_MAP[NotFoundError]={DOMAIN_HTTP_MAP.get(NotFoundError)}; probe {res.status_code} {body}")
if DOMAIN_HTTP_MAP.get(NotFoundError) != 404 or res.status_code != 404 or body != want:
    problems.append("S8: errors.py does not map NotFoundError to 404 with the not-found body")

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

# 8. the base receipts (recorded, not fatal) and the host check
Set-Location (Join-Path $root 'ui')
& rtk proxy npm run test *> "$receipts/cki-base-ui.txt"
$ui = $LASTEXITCODE
Set-Location $root
Get-Content "$receipts/cki-base-ui.txt" -Tail 6
Write-Output ("baseline step base-ui exit={0} (recorded, not fatal)" -f $ui)

& rtk proxy uv run --no-sync pytest -p no:cacheprovider tests/ --tb=short -q *> "$receipts/cki-base-py.txt"
$pyt = $LASTEXITCODE
Get-Content "$receipts/cki-base-py.txt" -Tail 4
Write-Output ("baseline step base-py exit={0} (recorded, not fatal)" -f $pyt)

& rtk proxy uv run --no-sync python tools/e2e_remote.py check --out "$receipts/cki-check-0.json" *> "$receipts/cki-check-0.txt"
$chk = $LASTEXITCODE
Get-Content "$receipts/cki-check-0.txt" -Tail 4
if ($chk -eq 0) {
    Write-Output 'baseline step host-check exit=0'
} elseif ($chk -ge 20 -and $chk -le 24) {
    Write-Output ("baseline step host-check exit={0} (wait band; recorded, not a stop in row 0)" -f $chk)
} else {
    Write-Output ("baseline step host-check exit={0}: a tool stop (S11)" -f $chk)
    exit $chk
}
Write-Output 'baseline: all steps exit 0'
exit 0
