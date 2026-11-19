# Session 97 e2e-host-parity baseline (task row 0; implementation-plan.md §Verification Plan 1).
# The shape of docs/execution/plans/2026-11-18-e2e-remote-host/baseline.ps1, with this plan's
# steps: 1. uv sync --frozen --offline --all-packages (S7 on a held file); 2. the record: the
# tree state (baseline.sha, baseline-dirty.txt with the foreign class marked, git worktree list);
# the sibling check (ehp-since.txt: every commit since 2c41c70, and the scope diff since 2c41c70,
# which must be empty, S2); baseline-scope.json over §Files Modified, the "Read, never changed"
# files and the foreign class, with the three new test files, the handoff and the implementation
# review absent; baseline-dirty-hashes.json, which binds every dirty path outside this scope by
# hash; the row-0 copies under D/baseline-copies (diff-check.py's and eol-check.py's base);
# baseline-eol.json; baseline-skip-hashes.json over packages/, mcp-server/{src,scripts,tests}
# and native/ (secret names dropped before any stat or read, Session 83 RULE-2); the S2 anchors
# by line and text (a line that only moved is recorded for the handoff, Session 51 RULE-3), the
# known list, both issues open with no MEU link (yaml.safe_load, by key, Session 92 RULE-2),
# grouping row 97 pending, MEU-161 and 9.46 free, SEGOE_LA_ in three code files, 29 spec files,
# the dev PC's font SHA-256, no graphify graph, and the plan, task and plan-review hashes as
# approved; 3. the OS-wide probe (Session 91 RULE-1: host-load.ps1 and every Electron and node
# process, D/ehp-os-probe-0.txt); 4. the home-path check before (ehp-home-before.txt, S8);
# 5. the copied checkers' selftests and eol-check.py over the fresh copies; 6. meu-register.py's
# dry run and selftest; 7. snapshot-commit.py's selftest in a new folder; 8. the generators'
# --out hashes (S9) and their --check, which must exit 1 now; 9. the AC-161.10 sentinels and
# write faults; 10. the AC-161.12 host-detail scan and its sentinel; 11. ruff on this folder's
# Python (Session 82 RULE-1). Every step is fail-fast. Run from the repository root in pwsh.
# This file names no host alias, account or folder of the real host (LOCAL_HOST_DETAILS).
$ErrorActionPreference = 'Stop'
$root = (git rev-parse --show-toplevel).Trim()
Set-Location $root
$plan = 'docs/execution/plans/2026-11-19-e2e-host-parity'
$receipts = 'C:/Temp/av-kit/e2e-host-parity'
Remove-Item Env:ELECTRON_RUN_AS_NODE -ErrorAction SilentlyContinue
Remove-Item Env:EHP_WRITE_FAULT -ErrorAction SilentlyContinue
$env:PYTHONIOENCODING = 'utf-8'
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:RECEIPTS_DIR = 'C:/Temp/av-kit'
$tmp = 'C:\Temp\av-kit\e2e-host-parity\tmp'
New-Item -ItemType Directory -Force -Path $tmp | Out-Null
$env:TMP = $tmp
$env:TEMP = $tmp
$stamp = Get-Date -Format 'yyyyMMddTHHmmss'

function Invoke-Step([string]$Id, [string[]]$Argv) {
    & rtk proxy @Argv
    $code = $LASTEXITCODE
    Write-Output ("baseline step {0} exit={1}" -f $Id, $code)
    if ($code -ne 0) { exit $code }
}

# A step whose tool must refuse: exit 1 is the pass; any other exit stops the baseline.
function Invoke-Refusal([string]$Id, [string[]]$Argv) {
    & rtk proxy @Argv
    $code = $LASTEXITCODE
    $ok = if ($code -eq 1) { 0 } else { 1 }
    Write-Output ("baseline step {0} exit={1} (the tool exited {2}; 1 expected)" -f $Id, $ok, $code)
    if ($ok -ne 0) { exit 1 }
}

function Exit-Step([string]$Id, [int]$Code, [string]$Why) {
    Write-Output ("baseline step {0} exit={1} {2}" -f $Id, $Code, $Why)
    if ($Code -ne 0) { exit $Code }
}

# 2. The record, in Python so every file is read and written as bytes.
$record = @'
import hashlib, json, pathlib, subprocess, sys

import yaml

PLAN = pathlib.Path("docs/execution/plans/2026-11-19-e2e-host-parity")
OUT = pathlib.Path("C:/Temp/av-kit/e2e-host-parity")
COPIES = OUT / "baseline-copies"
EXPECTED_HEAD = "2c41c70a50863f013988e2a153fdef9c1f19032e"
BASE = "2c41c70"
GROUPING = ".agent/context/grouping/2026-11-18-e2e-remote-host-session-grouping.md"
REGISTER = ".agent/context/known-issues.yaml"
MEU_STATUS = ".agent/context/meu-status.yaml"
MATRIX = "docs/build-plan/build-priority-matrix.md"
KNOWN = "tools/e2e_host/known-failures.json"
ISSUES = ("CAPTURE-TEXT-PIXEL-2PX-MINIAIR", "E2E-HOVER-NO-POINTER-DEVICE")
HANDOFF = ".agent/context/handoffs/2026-11-19-e2e-host-parity-MEU-161-handoff.md"
IMPL_REVIEW = ".agent/context/handoffs/2026-11-19-e2e-host-parity-implementation-critical-review.md"
PLAN_REVIEW = ".agent/context/handoffs/2026-11-19-e2e-host-parity-plan-critical-review.md"
REFLECTION = "docs/execution/reflections/2026-11-19-e2e-host-parity-reflection.md"
SKIP_SPECS = ("capture-filmstrip-actions.test.ts", "capture-import.test.ts")
METRICS_TS = "ui/src/renderer/src/features/capture/capture-text-metrics.ts"
SEGOE_TS = "ui/src/renderer/src/features/capture/capture-segoe-metrics.ts"
ADAPTER = "packages/infrastructure/src/avkit_infra/capture/adapter.py"
INBOX = "ui/tests/e2e/capture-inbox.test.ts"
SETTINGS = "ui/tests/e2e/settings.test.ts"
ELECTRON_APP = "ui/tests/e2e/electron-app.ts"
METRICS_TEST = "ui/tests/unit/capture-text-metrics.test.ts"
TRANSFORM_TEST = "ui/tests/unit/capture-transform.test.ts"
PAGE_TEST = "ui/tests/unit/capture-page.behavior.test.ts"
LINES_TEST = "ui/tests/unit/capture-text-lines.behavior.test.ts"
FONT = "C:/Windows/Fonts/segoeui.ttf"
FONT_SHA = "704eada12961a27fd271f7d3b09e2066520e758390c1776744eff430fee30f6e"
# §Files Modified that exist at row 0, with each file's line-ending kind.
MODIFIED = {
    "ui/tests/unit/e2e-harness.test.ts": "LF",
    ELECTRON_APP: "LF",
    SETTINGS: "CRLF",
    INBOX: "LF",
    METRICS_TEST: "CRLF",
    TRANSFORM_TEST: "CRLF",
    LINES_TEST: "LF",
    PAGE_TEST: "CRLF",
    SEGOE_TS: "CRLF",
    METRICS_TS: "CRLF",
    KNOWN: "LF",
    MEU_STATUS: "LF",
    "docs/build-plan/09-screenshot-capture.md": "CRLF",
    MATRIX: "CRLF",
    ".agent/context/meu-registry.md": "LF",
    "docs/BUILD_PLAN.md": "LF",
    REGISTER: "LF",
    ".agent/context/known-issues.md": "LF",
    GROUPING: "LF",
    ".agent/context/current-focus.md": "CRLF",
    "docs/execution/metrics.md": "CRLF",
}
# §Files Modified that are new; each must be absent at row 0. The plan review exists by design
# (it approved the plan) and is bound by its hash below, not here.
NEW = {
    "ui/tests/e2e/fixtures/capture-text-plates.json": "LF",
    "ui/tests/unit/capture-text-plates.test.ts": "LF",
    "tests/unit/test_capture_text_plates.py": "LF",
    HANDOFF: "LF",
    IMPL_REVIEW: "LF",
    REFLECTION: "LF",
}
# §Files Modified "Read, never changed": bound by hash; their kind is recorded, not expected.
READ_ONLY = (
    ADAPTER,
    "ui/tests/e2e/fixtures/capture-geometry.json",
    "ui/tests/unit/capture-hit-test.test.ts",
    "tests/unit/test_capture_text_lines.py",
    "tools/e2e_remote.py",
    *sorted(
        p.as_posix() for p in pathlib.Path("tools/e2e_host").iterdir() if p.is_file() and p.as_posix() != KNOWN
    ),
    "ui/tests/e2e/electron-env.ts",
    "ui/tests/e2e/global-setup.ts",
    "ui/playwright.config.ts",
    "ui/scripts/playwright-with-outputfile.mjs",
    "ui/package.json",
    ".github/workflows/ci.yml",
)
# The foreign class (Session 92 RULE-3): the coordinator's files, bound by hash; a change is
# recorded in the handoff, is not S4 and stays out of the commit paths.
FOREIGN_CLASS = (
    ".agent/model-registry.local.json",
    *sorted(p.as_posix() for p in pathlib.Path(".claude/agents").glob("*.md")),
    *sorted(p.as_posix() for p in pathlib.Path(".cursor/agents").glob("*.md")),
)
PLAN_FILES = {
    p.as_posix(): "LF"
    for p in sorted(PLAN.iterdir())
    if p.is_file() and p.suffix in (".md", ".py", ".ps1", ".mjs", ".cjs")
}
# The approved plan and task. The plan's sha moved only by the Status line's execute words
# (Mat, 2026-11-18), from daa38c1a... (reviewed) to the value here; task.md is unchanged since
# review. The plan review's hash is the one found before row 0 ran.
PLAN_SHA = {
    f"{PLAN.as_posix()}/implementation-plan.md": "39a31c7dcdb2df327715778c432b41a134689800424f3dc01b41201768cbb30a",
    f"{PLAN.as_posix()}/task.md": "5122fb557f482e7ed5145b4f5707ccc3af0aa2c25f7ff6b0ae71d47460c6e5e0",
}
PLAN_REVIEW_SHA = "d6e03153b97e9261c5f0c6aa4fedf0af56b0a3021ddf72e00051fb9a4364936e"
# meu-register.py: the reviewer's Low (DESCRIPTION and the Residual row set to AC-161.5's
# limits) is the only plan-local script change after approval.
MEU_REGISTER_SHA = {
    "plan time": "6d00606bf29650a81aef05d4761ed33f6060631523dc5b0bdf51af819fd17595",
    "after the reviewer's Low": "50fedf0656fe72a4091d7aa2d237c6fd7b55045557d0a925ce2b761c4f08a36a",
}
# The task row 0 anchors: (path, line, text). The text must be on its line; one hit elsewhere
# is a moved line (recorded for the handoff, Session 51 RULE-3); otherwise S2.
ANCHORS = (
    (METRICS_TS, 5, "import { SEGOE_LA_BASE_SIZE, SEGOE_LA_GLYPHS"),
    (METRICS_TS, 51, "const FALLBACK_GLYPH = "),
    (METRICS_TS, 58, "export function textBackgroundBox("),
    (METRICS_TS, 88, "    x: Math.round(left),"),
    (METRICS_TS, 89, "    y: Math.round(top),"),
    (METRICS_TS, 90, "width: Math.max(1, Math.round(right) - Math.round(left)),"),
    (METRICS_TS, 91, "height: Math.max(1, Math.round(bottom) - Math.round(top)),"),
    (ADAPTER, 223, "def text_plate_box("),
    (ADAPTER, 1124, "draw.rectangle("),
    (INBOX, 68, "async function launchApp() {"),
    (INBOX, 2243, "AC-82.6 TEXT_PIXEL_ORACLE"),
    (INBOX, 2301, "async function fidelityViews("),
    (INBOX, 3078, "AC-101.6"),
    (SETTINGS, 22, "async function launchApp() {"),
    (SETTINGS, 700, "AC-126.8 light accent paints the ruled colours"),
    (ELECTRON_APP, 35, "LaunchOptions"),
    (ELECTRON_APP, 110, "launchElectron"),
    (ELECTRON_APP, 134, "main ?? DEFAULT_MAIN]"),
    (METRICS_TEST, 12, "AC-59.19"),
    (TRANSFORM_TEST, 189, "toEqual({ x: 10, y: 6, width: 15, height: 12 })"),
    (TRANSFORM_TEST, 191, "toEqual({ x: 10, y: -6, font_size: 32 })"),
    (TRANSFORM_TEST, 192, "toEqual({ x: 10, y: 6, width: 30, height: 24 })"),
    (PAGE_TEST, 932, "AC-82.4"),
    (PAGE_TEST, 3211, "doubleClickAt(surface, 87, 62)"),
    (PAGE_TEST, 3264, "AC-101.4 a selected text mark"),
    (PAGE_TEST, 3292, "AC-101.4 after a corner scale"),
    (PAGE_TEST, 3495, "AC-59.19 SVG text"),
    (LINES_TEST, 14, "import { SEGOE_LA_BASE_SIZE, SEGOE_LA_GLYPHS }"),
    (LINES_TEST, 315, "AC-102.10"),
    (GROUPING, 134, "| 97 | `e2e-host-parity` |"),
)
SEGOE_LA_FILES = sorted((SEGOE_TS, METRICS_TS, LINES_TEST))
CODE_DIRS = ("ui", "packages", "tests", "tools", "backend", "mcp-server", "native")
SKIP_DIRS = ("packages", "mcp-server/src", "mcp-server/scripts", "mcp-server/tests", "native")
SECRET_BASES = (".mcp.json", "mcp-token.txt", ".claude.json", ".env")
SCOPE_PREFIXES = (
    PLAN.as_posix() + "/",
    ".agent/context/handoffs/2026-11-19-e2e-host-parity-",
    "docs/execution/reflections/2026-11-19-e2e-host-parity-",
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


def foreign(p):
    return "coordinator, foreign class" if p in FOREIGN_CLASS else None


def text_lines(p):
    return pathlib.Path(p).read_bytes().decode("utf-8").replace("\r\n", "\n").split("\n")


OUT.mkdir(parents=True, exist_ok=True)
(OUT / "tmp").mkdir(parents=True, exist_ok=True)
head = git("rev-parse", "HEAD").decode().strip()
(PLAN / "baseline.sha").write_bytes((head + "\n").encode())
print("baseline.sha", head)
if head != EXPECTED_HEAD:
    problems.append(f"S2: HEAD is {head}, not the brief's {EXPECTED_HEAD[:7]}")
origin = subprocess.run(["git", "rev-parse", "origin/main"], capture_output=True).stdout.decode().strip()
print("origin/main as found", origin or "<none>")
worktrees = git("worktree", "list").decode("utf-8")
print("git worktree list:")
for line in worktrees.splitlines():
    print("  ", line)

KINDS = {**MODIFIED, **NEW}
SCOPE_PATHS = (*KINDS, *READ_ONLY)

# The sibling check: every commit since 2c41c70, and no scope diff since it.
since = git("log", "--oneline", f"{BASE}..HEAD").decode("utf-8")
stat = git("diff", "--stat", BASE, "HEAD", "--", *SCOPE_PATHS).decode("utf-8")
(OUT / "ehp-since.txt").write_bytes(
    (
        f"git log --oneline {BASE}..HEAD\n" + (since or "(empty)\n")
        + f"\ngit diff --stat {BASE} HEAD -- <{len(SCOPE_PATHS)} scope paths>\n"
        + (stat or "(empty)\n")
    ).encode("utf-8")
)
print(f"ehp-since.txt: commits since {BASE}:", since.splitlines() or "none")
print(f"  scope diff since {BASE}:", stat.splitlines() or "empty")
if stat.strip():
    problems.append(f"S2: a scope path changed since {BASE}: {stat.splitlines()}")

porcelain = git("status", "--porcelain", "--untracked-files=all").decode("utf-8")
dirty = [line[3:].strip().strip('"') for line in porcelain.splitlines() if line.strip()]
marks = [f"# foreign ({foreign(p)}): {p}" for p in dirty if foreign(p)]
(PLAN / "baseline-dirty.txt").write_bytes((porcelain + "".join(m + "\n" for m in marks)).encode("utf-8"))
print("baseline-dirty.txt", len(dirty), "paths,", len(marks), "foreign")
for p in dirty:
    print("  dirty", p, f"(foreign: {foreign(p)})" if foreign(p) else "")

scope = {p: sha(p) for p in (*KINDS, *READ_ONLY, *FOREIGN_CLASS)}
for p in NEW:
    if scope[p] != "absent":
        problems.append(f"S2: new file already exists: {p}")
for p in (*MODIFIED, *READ_ONLY):
    if scope[p] in ("absent", "not-a-file"):
        problems.append(f"S2: scoped path missing: {p}")
(PLAN / "baseline-scope.json").write_bytes((json.dumps(scope, indent=2) + "\n").encode())
print(
    "baseline-scope.json", len(scope), "paths;", sum(v == "absent" for v in scope.values()), "absent;",
    len(FOREIGN_CLASS), "foreign class;", len(READ_ONLY), "read, never changed",
)
for p in FOREIGN_CLASS:
    print("  foreign class", p, scope[p][:16])
for p in NEW:
    print("  new, absent at row 0:", p, scope[p])


def in_scope(p):
    return p in scope or p.startswith(SCOPE_PREFIXES)


hashes = {p: (sha(p) if pathlib.Path(p).exists() else "deleted") for p in dirty if not in_scope(p) and not secret(p)}
(PLAN / "baseline-dirty-hashes.json").write_bytes((json.dumps(hashes, indent=2, sort_keys=True) + "\n").encode())
print("baseline-dirty-hashes.json", len(hashes), "paths outside this scope")
for p in sorted(hashes):
    print("  bound by hash", p, hashes[p][:16])

# The row-0 bytes of every existing scope, read-only and plan file and the plan review:
# diff-check.py's and eol-check.py's base and the execution review's delta base.
copied = 0
for p in (*KINDS, *READ_ONLY, *PLAN_FILES, PLAN_REVIEW):
    src = pathlib.Path(p)
    if src.is_absolute() or not src.is_file():
        continue
    dest = COPIES / p
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(src.read_bytes())
    copied += 1
print("baseline-copies", copied, "row-0 copies under", COPIES.as_posix())

# baseline-skip-hashes.json (H1-4): every tracked or untracked, not-ignored file under the skip
# dirs, secret names dropped before any stat or read.
listed = git("ls-files", "--cached", "--others", "--exclude-standard", *SKIP_DIRS)
skip_paths = [n for n in listed.decode("utf-8").splitlines() if n and not secret(n)]
skips = {p: sha(p) for p in skip_paths if pathlib.Path(p).is_file()}
(PLAN / "baseline-skip-hashes.json").write_bytes((json.dumps(skips, indent=2, sort_keys=True) + "\n").encode())
per_dir = {d: sum(1 for p in skips if p.startswith(d + "/")) for d in SKIP_DIRS}
print("baseline-skip-hashes.json", len(skips), "files:", per_dir)

# Line endings, measured with Python bytes.
eols = {}
for p, want in {**KINDS, **{q: None for q in READ_ONLY}, **PLAN_FILES}.items():
    if not pathlib.Path(p).is_file():
        eols[p] = {"kind": "absent", "expected": want, "crlf": 0, "bare_lf": 0}
        print("eol absent", p)
        continue
    raw = pathlib.Path(p).read_bytes()
    kind, crlf, bare = eol(raw)
    eols[p] = {"kind": kind, "expected": want, "crlf": crlf, "bare_lf": bare, "bom": raw.startswith(b"\xef\xbb\xbf"), "bytes": len(raw)}
    print("eol", kind, "crlf", crlf, "bare_lf", bare, "bom", eols[p]["bom"], "bytes", len(raw), p)
    if want is not None and kind != want and p not in NEW:
        problems.append(f"S2: {p} is {kind}, the plan says {want}")
(PLAN / "baseline-eol.json").write_bytes((json.dumps(eols, indent=2) + "\n").encode())
print("baseline-eol.json", len(eols), "paths")

# S2: the anchors by line and text.
moved = []
for p, line, needle in ANCHORS:
    lines = text_lines(p)
    here = lines[line - 1] if line <= len(lines) else None
    hits = [i + 1 for i, ln in enumerate(lines) if needle in ln]
    at = here is not None and needle in here
    state = "at line" if at else (f"moved to {hits}" if len(hits) == 1 else f"missing ({len(hits)} hits)")
    print(f"anchor {p}:{line} {state} hits={len(hits)} :: {needle!r}")
    if at:
        continue
    if len(hits) == 1:
        moved.append(f"{p}:{line} -> {hits[0]}")
    else:
        problems.append(f"S2: anchor {needle!r} in {p}:{line}: {state}")
row97 = text_lines(GROUPING)[133]
print("grouping :134 pending:", "pending" in row97)
if "pending" not in row97:
    problems.append("S2: grouping row 97 is not pending")
print("anchor lines moved:", moved or "none")

# S2: the known list.
known = json.loads(pathlib.Path(KNOWN).read_bytes().decode("utf-8"))
entries = [*known.get("known", []), *known.get("skip", [])]
labels = sorted({e.get("label") for e in entries})
print("known list:", len(known.get("known", [])), "known,", len(known.get("skip", [])), "skip, labels", labels, "keys", sorted(known))
print("  known:", [(e.get("file"), e.get("ac"), e.get("issue")) for e in known.get("known", [])])
if len(known.get("known", [])) != 4 or len(known.get("skip", [])) != 2 or labels != ["mini-air"]:
    problems.append("S2: the known list is not label mini-air with 4 known and 2 skip entries")

# S2: the issues, read by key with yaml.safe_load (Session 92 RULE-2).
data = yaml.safe_load(pathlib.Path(REGISTER).read_bytes().decode("utf-8"))
for issue in ISSUES:
    matches = [i for i in data.get("issues", []) if isinstance(i, dict) and i.get("id") == issue]
    entry = matches[0] if len(matches) == 1 else {}
    reg_line = next((i + 1 for i, ln in enumerate(text_lines(REGISTER)) if ln == f"  - id: {issue}"), None)
    print(f"issue {issue}: entries {len(matches)}, status {entry.get('status')}, meu_links {entry.get('meu_links')!r}, line {reg_line}")
    if entry.get("status") != "open" or entry.get("meu_links") != []:
        problems.append(f"S2: {issue} is not open with meu_links []")

# S2: MEU-161 and 9.46 free.
meus = yaml.safe_load(pathlib.Path(MEU_STATUS).read_bytes().decode("utf-8"))
rows = meus.get("meus", meus.get("rows", [])) if isinstance(meus, dict) else []
ids = {r.get("id") for r in rows if isinstance(r, dict)}
items = {str(r.get("matrix_item")) for r in rows if isinstance(r, dict)}
raw_status = pathlib.Path(MEU_STATUS).read_bytes().decode("utf-8")
matrix_rows = [ln for ln in text_lines(MATRIX) if ln.startswith("| 9.46 |")]
print("meu-status rows", len(rows), "MEU-161 in ids:", "MEU-161" in ids, "9.46 in items:", "9.46" in items,
      "'MEU-161' in text:", "MEU-161" in raw_status, "matrix rows '| 9.46 |':", len(matrix_rows))
if not rows or "MEU-161" in ids or "9.46" in items or "MEU-161" in raw_status or matrix_rows:
    problems.append("S2: MEU-161 or 9.46 is taken (or the MEU rows did not parse)")

# S2: SEGOE_LA_ only in the three code files (tracked code folders); docs hits recorded.
code_hits = sorted(n for n in git("grep", "-l", "SEGOE_LA_", "--", *CODE_DIRS).decode("utf-8").splitlines() if n)
all_hits = sorted(n for n in git("grep", "-l", "SEGOE_LA_").decode("utf-8").splitlines() if n)
print("SEGOE_LA_ in code:", code_hits)
print("SEGOE_LA_ elsewhere (recorded):", [n for n in all_hits if n not in code_hits])
if code_hits != SEGOE_LA_FILES:
    problems.append(f"S2: SEGOE_LA_ occurs in {code_hits}")

# S2: the spec files at HEAD.
names = git("ls-tree", "--name-only", "HEAD", "ui/tests/e2e/").decode("utf-8").splitlines()
specs = sorted(n.rsplit("/", 1)[-1] for n in names if n.endswith((".test.ts", ".spec.ts")))
kept = [s for s in specs if s not in SKIP_SPECS]
print("spec files at HEAD:", len(specs), "without the skip files:", len(kept))
if len(specs) != 29 or len(kept) != 27:
    problems.append(f"S2: {len(specs)} spec files, {len(kept)} without the skip files (29 and 27 expected)")

# S2: the dev PC's font.
font = sha(FONT)
print("segoeui.ttf sha256", font, "plan's:", font == FONT_SHA)
if font != FONT_SHA:
    problems.append(f"S2: segoeui.ttf sha256 {font[:16]} is not the plan's {FONT_SHA[:16]}")

# S1: no graphify graph.
graphs = [g for g in ("graphify-out", "graphify-out-research") if pathlib.Path(g).exists()]
print("graphify graphs", graphs)
if graphs:
    problems.append(f"S1: a graphify graph exists: {graphs}")

# The approved plan, task and plan review; the plan-local scripts' hashes.
for p, want in PLAN_SHA.items():
    got = sha(p)
    print("approved", p, got)
    if got != want:
        problems.append(f"S2: {p} sha256 {got}, not the approved {want}")
got = sha(PLAN_REVIEW)
print("plan review", PLAN_REVIEW, got)
if got != PLAN_REVIEW_SHA:
    problems.append(f"S2: the plan review's sha256 is {got}, not {PLAN_REVIEW_SHA}")
got = sha(PLAN / "meu-register.py")
print("meu-register.py", got, "plan time", MEU_REGISTER_SHA["plan time"][:16], "after the Low", MEU_REGISTER_SHA["after the reviewer's Low"][:16])
if got != MEU_REGISTER_SHA["after the reviewer's Low"]:
    problems.append("meu-register.py is not the reviewed copy plus the reviewer's Low")
for p in sorted(PLAN_FILES):
    print("plan file", p, sha(p)[:16])
for p in problems:
    print("PROBLEM:", p)
sys.exit(1 if problems else 0)
'@

# 3. The OS-wide probe (Session 91 RULE-1), before any measurement row. The user profile prefix
# of a process path is written as <HOME>.
$probe = @'
$ErrorActionPreference = 'Stop'
$home_prefix = [Environment]::GetFolderPath('UserProfile')
$lines = @("ehp-os-probe-0 $(Get-Date -Format o)")
$procs = Get-CimInstance Win32_Process | Where-Object { $_.Name -match '^(electron|node)(\.exe)?$' -or $_.Name -match 'av-kit' } | Sort-Object ProcessId
foreach ($p in $procs) {
    $path = [string]$p.ExecutablePath
    if ($home_prefix -and $path.StartsWith($home_prefix, [StringComparison]::OrdinalIgnoreCase)) { $path = '<HOME>' + $path.Substring($home_prefix.Length) }
    $lines += ("process pid={0} name={1} created={2} path={3}" -f $p.ProcessId, $p.Name, $p.CreationDate.ToString('o'), $path)
}
$lines += ("electron_node_processes={0}" -f @($procs).Count)
$lines
'@

# 10. The host-detail sentinel (AC-161.12): the config's host value is written to one scratch
# file, never printed; the scan must exit 1 naming the key only; that one file is removed.
$hostSentinel = @'
import json, pathlib, subprocess, sys

cfg, plan = pathlib.Path(sys.argv[1]), sys.argv[2]
target = pathlib.Path("C:/Temp/av-kit/e2e-host-parity/ehp-host-sentinel.txt")
value = str(json.loads(cfg.read_bytes().decode("utf-8"))["host"])
with open(target, "xb") as f:
    f.write(("sentinel " + value + "\n").encode("utf-8"))
try:
    run = subprocess.run(
        [sys.executable, f"{plan}/host-details-scan.py", str(cfg), "--allow-absent", "--file", str(target)],
        capture_output=True,
    )
    out = run.stdout.decode("utf-8", "replace") + run.stderr.decode("utf-8", "replace")
finally:
    target.unlink()
leaked = value.lower() in out.lower()
named = "('host'," in out and "ehp-host-sentinel.txt" in out
print(out.rstrip() if not leaked else "(the scan output held the value; withheld)")
print(f"host sentinel: scan exit {run.returncode}, key named {named}, value printed {leaked}, file removed {not target.exists()}")
sys.exit(0 if run.returncode == 1 and named and not leaked and not target.exists() else 1)
'@

New-Item -ItemType Directory -Force -Path $receipts | Out-Null
Set-Content -Path "$receipts/baseline-record.py" -Value $record -Encoding utf8
Set-Content -Path "$receipts/baseline-os-probe.ps1" -Value $probe -Encoding utf8
Set-Content -Path "$receipts/baseline-host-sentinel.py" -Value $hostSentinel -Encoding utf8

# 1. The environment (S7 on a held file).
Invoke-Step 'uv-sync' @('uv', 'sync', '--frozen', '--offline', '--all-packages')
# 2. The record.
Invoke-Step 'record' @('uv', 'run', '--no-sync', 'python', "$receipts/baseline-record.py")

# 3. The OS-wide probe: the host load (the 50 % wait) and the Electron and node processes.
& pwsh -NoProfile -File "$plan/host-load.ps1" > "$receipts/ehp-os-probe-0-load.txt" 2>&1
$loadCode = $LASTEXITCODE
& pwsh -NoProfile -File "$receipts/baseline-os-probe.ps1" > "$receipts/ehp-os-probe-0-procs.txt" 2>&1
$procCode = $LASTEXITCODE
$probeText = @(Get-Content "$receipts/ehp-os-probe-0-load.txt") + @("host-load.ps1 exit=$loadCode") + @(Get-Content "$receipts/ehp-os-probe-0-procs.txt") + @("process probe exit=$procCode")
[System.IO.File]::WriteAllText("$receipts/ehp-os-probe-0.txt", (($probeText -join "`n") + "`n"))
Remove-Item -LiteralPath "$receipts/ehp-os-probe-0-load.txt", "$receipts/ehp-os-probe-0-procs.txt"
Get-Content "$receipts/ehp-os-probe-0.txt" | Select-Object -Last 12
Exit-Step 'os-probe' ([int]($loadCode -ne 0 -or $procCode -ne 0)) "receipt=$receipts/ehp-os-probe-0.txt"

# 4. The home-path check before (S8).
& rtk proxy uv run --no-sync python tools/check_home_path.py > "$receipts/ehp-home-before.txt" 2>&1
$homeCode = $LASTEXITCODE
Get-Content "$receipts/ehp-home-before.txt" | Select-Object -Last 4
Exit-Step 'home-path' $homeCode "receipt=$receipts/ehp-home-before.txt"

# 5. The copied checkers and the plan-time checkers' selftests.
Invoke-Step 'red-check-selftest' @('uv', 'run', '--no-sync', 'python', "$plan/red-check.py", '--selftest')
Invoke-Step 'identity-selftest' @('uv', 'run', '--no-sync', 'python', "$plan/identity.py", '--selftest')
Invoke-Step 'eol-check-selftest' @('uv', 'run', '--no-sync', 'python', "$plan/eol-check.py", '--selftest')
Invoke-Step 'eol-check-row0' @('uv', 'run', '--no-sync', 'python', "$plan/eol-check.py")
Invoke-Step 'diff-check-selftest' @('uv', 'run', '--no-sync', 'python', "$plan/diff-check.py", '--selftest')
Invoke-Step 'flake-run-selftest' @('uv', 'run', '--no-sync', 'python', "$plan/flake-run.py", '--selftest')

# 6. The MEU registration's dry run and selftest.
Invoke-Step 'meu-register-dry-run' @('uv', 'run', '--no-sync', 'python', "$plan/meu-register.py", '--dry-run', '--baseline-scope', "$plan/baseline-scope.json")
Invoke-Step 'meu-register-selftest' @('uv', 'run', '--no-sync', 'python', "$plan/meu-register.py", '--selftest')

# 7. The snapshot commit's selftest, in a new folder.
Invoke-Step 'snapshot-selftest' @('uv', 'run', '--no-sync', 'python', "$plan/snapshot-commit.py", '--selftest', "$receipts/snap-selftest-0-$stamp")

# 8. The generators: --out to D (a rerun of this row checks the existing receipt), the
# plan-time hash prefixes (S9), and --check, which must exit 1 before rows 6 and 7.
$gens = @(
    @{ id = 'segoe-units'; script = 'segoe-units.py'; out = "$receipts/ehp-segoe-units-0.ts"; prefix = 'f93720ecdc6cb72d' },
    @{ id = 'plate-fixture'; script = 'plate-fixture.py'; out = "$receipts/ehp-plates-0.json"; prefix = '36b15443d46282a6' }
)
foreach ($g in $gens) {
    if (Test-Path -LiteralPath $g.out) {
        Write-Output ("baseline {0}: {1} exists from an earlier run of this row; checking it" -f $g.id, $g.out)
    } else {
        Invoke-Step "$($g.id)-out" @('uv', 'run', '--no-sync', 'python', "$plan/$($g.script)", '--out', $g.out)
    }
    $h = (Get-FileHash -Algorithm SHA256 -LiteralPath $g.out).Hash.ToLower()
    $len = (Get-Item -LiteralPath $g.out).Length
    $ok = [int](-not $h.StartsWith($g.prefix))
    Exit-Step "$($g.id)-hash" $ok ("sha256 {0} bytes {1} plan-time prefix {2} (S9 when it differs)" -f $h, $len, $g.prefix)
    Invoke-Refusal "$($g.id)-check-before" @('uv', 'run', '--no-sync', 'python', "$plan/$($g.script)", '--check')
}

# 9. No overwrite and no partial file (AC-161.10).
$sentinels = @(
    @{ id = 'segoe-units'; argv = @('uv', 'run', '--no-sync', 'python', "$plan/segoe-units.py", '--out'); path = "$receipts/ehp-sentinel-0-segoe.ts"; tail = @() },
    @{ id = 'plate-fixture'; argv = @('uv', 'run', '--no-sync', 'python', "$plan/plate-fixture.py", '--out'); path = "$receipts/ehp-sentinel-0-plates.json"; tail = @() },
    @{ id = 'snapshot-commit'; argv = @('uv', 'run', '--no-sync', 'python', "$plan/snapshot-commit.py", '--out'); path = "$receipts/ehp-sentinel-0-snapshot.json"; tail = @('ui/tests/e2e/electron-app.ts') }
)
$sentinelBytes = [System.Text.Encoding]::UTF8.GetBytes("ehp row-0 sentinel; never overwritten`n")
foreach ($s in $sentinels) {
    if (-not (Test-Path -LiteralPath $s.path)) { [System.IO.File]::WriteAllBytes($s.path, $sentinelBytes) }
    $before = (Get-FileHash -Algorithm SHA256 -LiteralPath $s.path).Hash
    Invoke-Refusal "$($s.id)-sentinel" (@($s.argv) + @($s.path) + @($s.tail))
    $after = (Get-FileHash -Algorithm SHA256 -LiteralPath $s.path).Hash
    Exit-Step "$($s.id)-sentinel-kept" ([int]($before -ne $after)) ("sha256 before {0} after {1}" -f $before.Substring(0, 16), $after.Substring(0, 16))
}
foreach ($g in $gens) {
    $faultOut = "$receipts/ehp-fault-0-$($g.id)-$stamp" + [System.IO.Path]::GetExtension($g.out)
    $env:EHP_WRITE_FAULT = '1'
    Invoke-Refusal "$($g.id)-fault" @('uv', 'run', '--no-sync', 'python', "$plan/$($g.script)", '--out', $faultOut)
    Remove-Item Env:EHP_WRITE_FAULT
    Exit-Step "$($g.id)-fault-no-file" ([int](Test-Path -LiteralPath $faultOut)) "path=$faultOut"
}

# 10. The host-detail scan (AC-161.12) and its sentinel. The config path is built here, never
# printed, and its values never leave the Python step.
$cfg = Join-Path $HOME '.config/av-kit/e2e-host.json'
Invoke-Step 'host-details-scan' @('uv', 'run', '--no-sync', 'python', "$plan/host-details-scan.py", $cfg, '--allow-absent')
Invoke-Step 'host-details-sentinel' @('uv', 'run', '--no-sync', 'python', "$receipts/baseline-host-sentinel.py", $cfg, $plan)

# 11. Ruff on this folder's Python (Session 82 RULE-1).
$planPy = @(Get-ChildItem -Path $plan -Filter '*.py' | Sort-Object Name | ForEach-Object { "$plan/$($_.Name)" })
Write-Output ("baseline plan Python: {0}" -f ($planPy -join ', '))
Invoke-Step 'ruff-format-plan' (@('uv', 'run', '--no-sync', 'ruff', 'format', '--check') + $planPy)
Invoke-Step 'ruff-check-plan' (@('uv', 'run', '--no-sync', 'ruff', 'check') + $planPy)
Write-Output 'baseline: all steps exit 0'
exit 0
