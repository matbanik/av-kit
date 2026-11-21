# Session 100 e2e-devpc-clipboard baseline (task row 0; implementation-plan.md §Verification Plan 1).
# The shape of docs/execution/plans/2026-11-20-e2e-clipboard-specs/baseline.ps1 (Session 98), with
# its post-approval stamp fix (D-1285: yyyyMMdd-HHmmss) and this plan's steps: 1. uv sync --frozen
# --offline --all-packages (S7 on a held file); 2. the record: the tree state (baseline.sha,
# baseline-dirty.txt with the foreign classes marked, git worktree list); HEAD is f1ba411 or a
# descendant (edc-since.txt: every commit since f1ba411; a commit that touches an own scope path is
# S2, one that touches only a shared closeout file is recorded); baseline-scope.json over §Files
# Modified, the "Read, never changed" files and the coordinator's foreign class, with the four new
# test files, the handoff, the implementation review and the reflection absent;
# baseline-dirty-hashes.json, which binds every dirty path outside this scope by hash, except
# Session 99's plan folder, handoffs and reflection, which are recorded by name only and never
# read (SESSION99_FOLDERS), and Session 99's class, named only when dirty (SESSION99_PATHS;
# D-1330: no plan-folder file or receipt holds a content hash of a Session 99 path that differs
# from HEAD, so baseline-scope.json records such a path as 'peer-dirty, named only'); the row-0
# copies under D/baseline-copies (pins-check.py's and eol-check.py's
# base); baseline-eol.json; baseline-skip-hashes.json over packages/, mcp-server/{src,scripts,tests}
# and native/ (secret names dropped before any stat or read, Session 83 RULE-2); the S2 anchors by
# line and text (a line that only moved is recorded for the handoff, Session 51 RULE-3), the known
# list (one gated entry, no known and no skip entry), both issues open with no MEU link
# (yaml.safe_load, by key, Session 92 RULE-2), grouping row 100 approved, 30 spec files at HEAD
# with one gated file, no graphify graph, and the plan, task and plan-review hashes; 3. the OS-wide
# probe (Session 91 RULE-1: host-load.ps1 and every Electron and node process,
# D/edc-os-probe-0.txt); 4. the home-path check before (edc-home-before.txt, S8); 5. the plan
# checkers' selftests (guard-logs.py's too, D-1321) and eol-check.py over the fresh copies; 6. split-specs.py --out into a new
# folder, each file's sha256 against its plan-time value (S9); 7. the row-0 refusals and counts:
# split-specs.py --check exits 1, writer-scan.py counts the 10 plan-time writers
# (--expect 10), flake-run.py --mode full exits 2 before any run (the OLD_CLIPBOARD guard), the
# row-0 --list-check total is 237 (HEAD's 239 minus the gated file's 2), and guard-check.py --list
# exits 1 (one gated file, not two); 8. the snapshot-commit --out sentinel (no overwrite); 9. the
# host-detail scan (AC-19) and its sentinel; 10. ruff on this folder's Python (Session 82 RULE-1).
# Every step is fail-fast. Run from the repository root in pwsh. No step reaches the network or the
# second Windows host, starts Electron or touches the system clipboard. This file names no host
# alias, account or folder of the real host (LOCAL_HOST_DETAILS).
$ErrorActionPreference = 'Stop'
$root = (git rev-parse --show-toplevel).Trim()
Set-Location $root
$plan = 'docs/execution/plans/2026-11-20-e2e-devpc-clipboard'
$receipts = 'C:/Temp/av-kit/e2e-devpc-clipboard'
Remove-Item Env:ELECTRON_RUN_AS_NODE -ErrorAction SilentlyContinue
Remove-Item Env:AVKIT_E2E_CLIPBOARD_GATED -ErrorAction SilentlyContinue
$env:PYTHONIOENCODING = 'utf-8'
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:RECEIPTS_DIR = 'C:/Temp/av-kit'
$tmp = 'C:\Temp\av-kit\e2e-devpc-clipboard\tmp'
New-Item -ItemType Directory -Force -Path $tmp | Out-Null
$env:TMP = $tmp
$env:TEMP = $tmp
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'

function Invoke-Step([string]$Id, [string[]]$Argv) {
    & rtk proxy @Argv
    $code = $LASTEXITCODE
    Write-Output ("baseline step {0} exit={1}" -f $Id, $code)
    if ($code -ne 0) { exit $code }
}

# A step whose tool must refuse with one exit code: that code is the pass; any other stops it.
function Invoke-Refusal([string]$Id, [string[]]$Argv, [int]$Want = 1) {
    & rtk proxy @Argv
    $code = $LASTEXITCODE
    $ok = if ($code -eq $Want) { 0 } else { 1 }
    Write-Output ("baseline step {0} exit={1} (the tool exited {2}; {3} expected)" -f $Id, $ok, $code, $Want)
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

PLAN = pathlib.Path("docs/execution/plans/2026-11-20-e2e-devpc-clipboard")
OUT = pathlib.Path("C:/Temp/av-kit/e2e-devpc-clipboard")
COPIES = OUT / "baseline-copies"
BASE_FULL = "f1ba411bed2fb9e043d1b37623dc2664670b9627"
BASE = "f1ba411"
GROUPING = ".agent/context/grouping/2026-11-20-e2e-devpc-clipboard-session-grouping.md"
REGISTER = ".agent/context/known-issues.yaml"
KNOWN = "tools/e2e_host/known-failures.json"
ISSUES = ("E2E-DEVPC-CLIPBOARD-SPECS", "E2E-CLIPBOARD-PRIMER-EMPTY")
HANDOFF = ".agent/context/handoffs/2026-11-20-e2e-devpc-clipboard-handoff.md"
IMPL_REVIEW = ".agent/context/handoffs/2026-11-20-e2e-devpc-clipboard-implementation-critical-review.md"
PLAN_REVIEW = ".agent/context/handoffs/2026-11-20-e2e-devpc-clipboard-plan-critical-review.md"
REFLECTION = "docs/execution/reflections/2026-11-20-e2e-devpc-clipboard-reflection.md"
E2E = "ui/tests/e2e/"
CONSOLE = E2E + "console-chrome.test.ts"
MCP = E2E + "mcp-setup-prompt.test.ts"
SETTINGS = E2E + "settings.test.ts"
COPY = E2E + "copy-system-clipboard.test.ts"
GUARD_CJS = E2E + "clipboard-guard.cjs"
GUARD_SPEC = E2E + "clipboard-guard.test.ts"
UNIT = "ui/tests/unit/e2e-clipboard-guard.test.ts"
ENV_TS = E2E + "electron-env.ts"
APP_TS = E2E + "electron-app.ts"
CLIP = E2E + "capture-system-clipboard.test.ts"
TESTS = "tests/tooling/test_e2e_remote.py"
RUN_BOOK = ".agent/docs/e2e-remote-host.md"
COMMANDS = ".agent/docs/commands.md"
CURRENT_FOCUS = ".agent/context/current-focus.md"
METRICS = "docs/execution/metrics.md"
# Files both this session and Session 99 may write at closeout: a commit since BASE that touches
# only these is recorded, not S2; each is re-read before this session's write (D-1316).
SHARED = (COMMANDS, CURRENT_FOCUS, METRICS, REGISTER, ".agent/context/known-issues.md")
# §Files Modified that exist at row 0, with each file's line-ending kind.
MODIFIED = {
    CONSOLE: "CRLF",
    MCP: "CRLF",
    SETTINGS: "CRLF",
    ENV_TS: "LF",
    APP_TS: "LF",
    KNOWN: "LF",
    TESTS: "LF",
    RUN_BOOK: "LF",
    COMMANDS: "CRLF",
    REGISTER: "LF",
    ".agent/context/known-issues.md": "LF",
    GROUPING: "LF",
    CURRENT_FOCUS: "CRLF",
    METRICS: "CRLF",
}
# §Files Modified that are new; each must be absent at row 0. The plan review exists by design
# (it approved the plan) and is bound by its hash below, not here.
NEW = {
    COPY: "LF",
    GUARD_CJS: "LF",
    GUARD_SPEC: "LF",
    UNIT: "LF",
    HANDOFF: "LF",
    IMPL_REVIEW: "LF",
    REFLECTION: "LF",
}
# §Files Modified "Read, never changed": bound by hash; their kind is recorded, not expected.
READ_ONLY = (
    CLIP,
    E2E + "main-error-watch.cjs",
    E2E + "global-setup.ts",
    "ui/playwright.config.ts",
    "ui/vitest.config.ts",
    "ui/eslint.config.js",
    "ui/scripts/playwright-with-outputfile.mjs",
    "ui/package.json",
    "ui/src/main/index.ts",
    "tools/e2e_remote.py",
    "tools/e2e_host/run-e2e.ps1",
    "tools/e2e_host/host-facts.ps1",
    "tools/e2e_host/host-status.ps1",
    "tools/e2e_host/e2e-host.example.json",
    ".github/workflows/ci.yml",
)
# The coordinator's foreign class (Session 92 RULE-3): bound by hash; a change is recorded in the
# handoff, is not S4 and stays out of the commit paths.
FOREIGN_CLASS = (
    ".agent/model-registry.local.json",
    *sorted(p.as_posix() for p in pathlib.Path(".claude/agents").glob("*.md")),
    *sorted(p.as_posix() for p in pathlib.Path(".cursor/agents").glob("*.md")),
)
# Session 99's foreign class (the brief, D-1330): its possible writes are recorded by name when
# dirty, never content-hashed, never failed on, and stay out of this session's commit paths.
SESSION99_PATHS = (
    "ui/src/",
    "docs/build-plan/06-gui.md",
    "docs/build-plan/build-priority-matrix.md",
    "docs/BUILD_PLAN.md",
    ".agent/context/meu-status.yaml",
    ".agent/context/meu-registry.md",
    ".agent/skills/README.md",
    # D-1342 (coordinator ruling, after row 0 ran): Session 99's further paths, names only.
    ".agent/skills/asd-ste100/",
    "tools/help_guide_ste.py",
    "tests/tooling/test_help_guide_ste.py",
    "ui/tests/e2e/test-ids.ts",
    "ui/tests/unit/failure-reason-copy.test.ts",
    "ui/tests/unit/help-quick-start.test.tsx",
    "ui/tests/unit/help-shots-privacy.test.ts",
    "ui/tests/e2e/help-quick-start.test.ts",
    "ui/tests/help-shots/",
    "ui/playwright.help-shots.config.ts",
    "ui/package.json",
    "ui/tsconfig.json",
    # D-1343: three tracked unit edits of Session 99's, names only.
    "ui/tests/unit/capture-page.test.ts",
    "ui/tests/unit/convert-page.test.ts",
    "ui/tests/unit/settings-page.test.ts",
    CURRENT_FOCUS,
    METRICS,
    COMMANDS,
)
# Session 99's own folder and handoffs: named from git status only; never read, hashed or bound.
SESSION99_FOLDERS = (
    "docs/execution/plans/2026-11-20-help-quick-start/",
    ".agent/context/handoffs/2026-11-20-help-quick-start-",
    "docs/execution/reflections/2026-11-20-help-quick-start",
)
PLAN_FILES = {
    p.as_posix(): "LF"
    for p in sorted(PLAN.iterdir())
    if p.is_file() and p.suffix in (".md", ".py", ".ps1", ".mjs", ".cjs")
}
# The task row 0 anchors: (path, line, text). The text must be on its line; one hit elsewhere
# is a moved line (recorded for the handoff, Session 51 RULE-3); otherwise S2.
ANCHORS = (
    (CONSOLE, 77, "test('C1-5 copy writes clipboard and log-to-file PUTs settings/app'"),
    (MCP, 28, "async function launchApp("),
    (MCP, 83, "}"),
    (MCP, 91, "test('AC-71.15 Codex prompt carries execPath and app data, Copy prompt fills"),
    (MCP, 126, "test('AC-71.15 Advanced starts closed and holds Copy MCP config;"),
    (SETTINGS, 216, "await page.getByTestId('copy-mcp-btn').click()"),
    (SETTINGS, 217, "await page.getByTestId('pin-mcp-btn').click()"),
    (ENV_TS, 20, "export const MAIN_ERROR_LOG_ENV = 'AVKIT_E2E_MAIN_ERROR_LOG'"),
    (ENV_TS, 23, "export const MAIN_ERROR_WATCH = resolve(here, 'main-error-watch.cjs')"),
    (APP_TS, 86, "async function checkMainErrors(dir: string, log: string): Promise<void> {"),
    (APP_TS, 112, "export async function launchElectron("),
    (APP_TS, 166, "await checkMainErrors(dir, log)"),
    (TESTS, 1564, "def test_ac_11_known_tracked_list("),
    (TESTS, 1572, '("mini-air", "capture-system-clipboard.test.ts"),'),
    (RUN_BOOK, 222, "`ui/tests/e2e/capture-system-clipboard.test.ts` holds the tests that write"),
    (GROUPING, 105, "| 100 | `e2e-devpc-clipboard` |"),
    (REGISTER, 3630, "  - id: E2E-CLIPBOARD-PRIMER-EMPTY"),
    (REGISTER, 6103, "  - id: E2E-DEVPC-CLIPBOARD-SPECS"),
    ("ui/src/main/index.ts", 162, "function readOrCreateMcpToken("),
)
SKIP_DIRS = ("packages", "mcp-server/src", "mcp-server/scripts", "mcp-server/tests", "native")
SECRET_BASES = (".mcp.json", "mcp-token.txt", ".claude.json", ".env")
SCOPE_PREFIXES = (
    PLAN.as_posix() + "/",
    ".agent/context/handoffs/2026-11-20-e2e-devpc-clipboard-",
    "docs/execution/reflections/2026-11-20-e2e-devpc-clipboard-",
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


def session99_folder(p):
    return p.startswith(SESSION99_FOLDERS)


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
    if p in FOREIGN_CLASS:
        return "coordinator, foreign class"
    if session99_folder(p):
        return "Session 99 folder, named only"
    if p.startswith(SESSION99_PATHS):
        return "Session 99, foreign class"
    return None


def text_lines(p):
    return pathlib.Path(p).read_bytes().decode("utf-8").replace("\r\n", "\n").split("\n")


OUT.mkdir(parents=True, exist_ok=True)
(OUT / "tmp").mkdir(parents=True, exist_ok=True)
head = git("rev-parse", "HEAD").decode().strip()
(PLAN / "baseline.sha").write_bytes((head + "\n").encode())
print("baseline.sha", head)
descendant = subprocess.run(["git", "merge-base", "--is-ancestor", BASE_FULL, "HEAD"]).returncode == 0
print("HEAD is f1ba411 or a descendant:", descendant)
if not descendant:
    problems.append(f"S2: HEAD {head} does not descend from {BASE}")
origin = subprocess.run(["git", "rev-parse", "origin/main"], capture_output=True).stdout.decode().strip()
print("origin/main as found", origin or "<none>")
print("branch", git("rev-parse", "--abbrev-ref", "HEAD").decode().strip())
worktrees = git("worktree", "list").decode("utf-8")
print("git worktree list:")
for line in worktrees.splitlines():
    print("  ", line)

KINDS = {**MODIFIED, **NEW}
SCOPE_PATHS = (*KINDS, *READ_ONLY)
OWN = tuple(p for p in SCOPE_PATHS if p not in SHARED)

# The sibling check: every commit since f1ba411; an own scope path changed since it is S2, a
# shared closeout file changed since it is recorded (another session's closeout).
since = git("log", "--oneline", f"{BASE}..HEAD").decode("utf-8")
own_stat = git("diff", "--stat", BASE, "HEAD", "--", *OWN).decode("utf-8")
shared_stat = git("diff", "--stat", BASE, "HEAD", "--", *SHARED).decode("utf-8")
(OUT / "edc-since.txt").write_bytes(
    (
        f"git log --oneline {BASE}..HEAD\n" + (since or "(empty)\n")
        + f"\ngit diff --stat {BASE} HEAD -- <{len(OWN)} own scope paths>\n" + (own_stat or "(empty)\n")
        + f"\ngit diff --stat {BASE} HEAD -- <{len(SHARED)} shared closeout paths>\n" + (shared_stat or "(empty)\n")
    ).encode("utf-8")
)
print(f"edc-since.txt: commits since {BASE}:", since.splitlines() or "none")
print(f"  own scope diff since {BASE}:", own_stat.splitlines() or "empty")
print(f"  shared closeout diff since {BASE} (recorded):", shared_stat.splitlines() or "empty")
if own_stat.strip():
    problems.append(f"S2: an own scope path changed since {BASE}: {own_stat.splitlines()}")

porcelain = git("status", "--porcelain", "--untracked-files=all").decode("utf-8")
dirty = [line[3:].strip().strip('"') for line in porcelain.splitlines() if line.strip()]
marks = [f"# foreign ({foreign(p)}): {p}" for p in dirty if foreign(p)]
(PLAN / "baseline-dirty.txt").write_bytes((porcelain + "".join(m + "\n" for m in marks)).encode("utf-8"))
print("baseline-dirty.txt", len(dirty), "paths,", len(marks), "foreign")
for p in dirty:
    print("  dirty", p, f"(foreign: {foreign(p)})" if foreign(p) else "")

# D-1330: a Session 99-class path that differs from HEAD at row 0 holds Session 99's work, so it
# is named, never hashed; a clean one hashes HEAD's content.
dirty_set = set(dirty)


def peer_dirty(p):
    return p.startswith(SESSION99_PATHS) and p in dirty_set


PEER_DIRTY = "peer-dirty, named only"
scope = {p: (PEER_DIRTY if peer_dirty(p) else sha(p)) for p in (*KINDS, *READ_ONLY, *FOREIGN_CLASS)}
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


hashes = {
    p: (sha(p) if pathlib.Path(p).exists() else "deleted")
    for p in dirty
    if not in_scope(p) and not secret(p) and not session99_folder(p) and not p.startswith(SESSION99_PATHS)
}
named = sorted(p for p in dirty if session99_folder(p) or (not in_scope(p) and p.startswith(SESSION99_PATHS)))
(PLAN / "baseline-dirty-hashes.json").write_bytes((json.dumps(hashes, indent=2, sort_keys=True) + "\n").encode())
print("baseline-dirty-hashes.json", len(hashes), "paths outside this scope;", len(named), "Session 99 paths named, not hashed")
for p in sorted(hashes):
    print("  bound by hash", p, hashes[p][:16], f"({foreign(p)})" if foreign(p) else "")
for p in named:
    print("  named only (Session 99)", p)
for p in sorted(q for q, v in scope.items() if v == PEER_DIRTY):
    print("  baseline-scope.json, peer-dirty, named only (D-1330)", p)

# The row-0 bytes of every existing scope, read-only and plan file and the plan review:
# pins-check.py's and eol-check.py's base and the execution review's delta base.
copied = 0
for p in (*KINDS, *READ_ONLY, *PLAN_FILES, PLAN_REVIEW):
    src = pathlib.Path(p)
    if src.is_absolute() or not src.is_file():
        continue
    # D-1330: a peer-dirty read-only path is not copied (no checker reads its copy); a shared
    # closeout file this session writes keeps its local copy as its own delta base.
    if peer_dirty(p) and p not in KINDS:
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
    elif p.startswith("ui/src/"):
        # Session 99's foreign class (D-1316): a ui/src anchor it moved is recorded, never S2.
        moved.append(f"{p}:{line} foreign (Session 99 class): {state}")
    else:
        problems.append(f"S2: anchor {needle!r} in {p}:{line}: {state}")
row100 = text_lines(GROUPING)[104]
print("grouping :105 approved:", "| approved |" in row100)
if "| approved |" not in row100:
    problems.append("S2: grouping row 100 is not approved")
print("anchor lines moved:", moved or "none")

# S2: the known list (one gated entry for capture-system-clipboard, no known, no skip entry).
known = json.loads(pathlib.Path(KNOWN).read_bytes().decode("utf-8"))
gated = [(e.get("label"), e.get("file")) for e in known.get("gated", [])]
print("known list: keys", sorted(known), "known", len(known.get("known", [])), "skip", len(known.get("skip", [])), "gated", gated)
if known.get("known") != [] or known.get("skip") != [] or gated != [("mini-air", "capture-system-clipboard.test.ts")]:
    problems.append("S2: the known list is not known [], skip [], gated [mini-air capture-system-clipboard]")

# S2: the issues, read by key with yaml.safe_load (Session 92 RULE-2).
data = yaml.safe_load(pathlib.Path(REGISTER).read_bytes().decode("utf-8"))
for issue in ISSUES:
    matches = [i for i in data.get("issues", []) if isinstance(i, dict) and i.get("id") == issue]
    entry = matches[0] if len(matches) == 1 else {}
    print(f"issue {issue}: entries {len(matches)}, status {entry.get('status')}, category {entry.get('category')}, meu_links {entry.get('meu_links')!r}")
    if entry.get("status") != "open" or entry.get("meu_links") != []:
        problems.append(f"S2: {issue} is not open with meu_links []")

# S2: the spec files at HEAD: 30, one of them the gated file, none of the new files.
names = git("ls-tree", "--name-only", "HEAD", E2E).decode("utf-8").splitlines()
specs = sorted(n.rsplit("/", 1)[-1] for n in names if n.endswith((".test.ts", ".spec.ts")))
print("spec files at HEAD:", len(specs))
if len(specs) != 30 or "capture-system-clipboard.test.ts" not in specs or any(
    n in specs for n in ("copy-system-clipboard.test.ts", "clipboard-guard.test.ts")
):
    problems.append(f"S2: {len(specs)} spec files at HEAD (30 with the one gated file expected)")

# S1: no graphify graph.
graphs = [g for g in ("graphify-out", "graphify-out-research") if pathlib.Path(g).exists()]
print("graphify graphs", graphs)
if graphs:
    problems.append(f"S1: a graphify graph exists: {graphs}")

# The plan, task and plan review as found: the plan review must exist (it approved the plan);
# the execution review compares these hashes with the ones that review names.
for p in (PLAN / "implementation-plan.md", PLAN / "task.md", pathlib.Path(PLAN_REVIEW)):
    print("as found", p.as_posix(), sha(p))
if sha(PLAN_REVIEW) == "absent":
    problems.append("S2: the plan review is absent; the plan is not approved")
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
$lines = @("edc-os-probe-0 $(Get-Date -Format o)")
$procs = Get-CimInstance Win32_Process | Where-Object { $_.Name -match '^(electron|node)(\.exe)?$' -or $_.Name -match 'av-kit' } | Sort-Object ProcessId
foreach ($p in $procs) {
    $path = [string]$p.ExecutablePath
    if ($home_prefix -and $path.StartsWith($home_prefix, [StringComparison]::OrdinalIgnoreCase)) { $path = '<HOME>' + $path.Substring($home_prefix.Length) }
    $lines += ("process pid={0} name={1} created={2} path={3}" -f $p.ProcessId, $p.Name, $p.CreationDate.ToString('o'), $path)
}
$lines += ("electron_node_processes={0}" -f @($procs).Count)
$lines
'@

# 9. The host-detail sentinel (AC-19): the config's host value is written to one scratch file,
# never printed; the scan must exit 1 naming the key only; that one file is removed.
$hostSentinel = @'
import json, pathlib, subprocess, sys

cfg, plan = pathlib.Path(sys.argv[1]), sys.argv[2]
target = pathlib.Path("C:/Temp/av-kit/e2e-devpc-clipboard/edc-host-sentinel.txt")
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
named = "('host'," in out and "edc-host-sentinel.txt" in out
print(out.rstrip() if not leaked else "(the scan output held the value; withheld)")
print(f"host sentinel: scan exit {run.returncode}, key named {named}, value printed {leaked}, file removed {not target.exists()}")
sys.exit(0 if run.returncode == 1 and named and not leaked and not target.exists() else 1)
'@

New-Item -ItemType Directory -Force -Path $receipts | Out-Null
Set-Content -Path "$receipts/baseline-record.py" -Value $record -Encoding utf8
Set-Content -Path "$receipts/baseline-os-probe.ps1" -Value $probe -Encoding utf8
Set-Content -Path "$receipts/baseline-host-sentinel.py" -Value $hostSentinel -Encoding utf8
$py = @('uv', 'run', '--no-sync', 'python')

# 1. The environment (S7 on a held file).
Invoke-Step 'uv-sync' @('uv', 'sync', '--frozen', '--offline', '--all-packages')
# 2. The record.
Invoke-Step 'record' ($py + @("$receipts/baseline-record.py"))

# 3. The OS-wide probe: the host load (the 50 % wait) and the Electron and node processes.
& pwsh -NoProfile -File "$plan/host-load.ps1" > "$receipts/edc-os-probe-0-load.txt" 2>&1
$loadCode = $LASTEXITCODE
& pwsh -NoProfile -File "$receipts/baseline-os-probe.ps1" > "$receipts/edc-os-probe-0-procs.txt" 2>&1
$procCode = $LASTEXITCODE
$probeText = @(Get-Content "$receipts/edc-os-probe-0-load.txt") + @("host-load.ps1 exit=$loadCode") + @(Get-Content "$receipts/edc-os-probe-0-procs.txt") + @("process probe exit=$procCode")
[System.IO.File]::WriteAllText("$receipts/edc-os-probe-0.txt", (($probeText -join "`n") + "`n"))
Remove-Item -LiteralPath "$receipts/edc-os-probe-0-load.txt", "$receipts/edc-os-probe-0-procs.txt"
Get-Content "$receipts/edc-os-probe-0.txt" | Select-Object -Last 12
Exit-Step 'os-probe' ([int]($loadCode -ne 0 -or $procCode -ne 0)) "receipt=$receipts/edc-os-probe-0.txt"

# 4. The home-path check before (S8).
& rtk proxy uv run --no-sync python tools/check_home_path.py > "$receipts/edc-home-before.txt" 2>&1
$homeCode = $LASTEXITCODE
Get-Content "$receipts/edc-home-before.txt" | Select-Object -Last 4
Exit-Step 'home-path' $homeCode "receipt=$receipts/edc-home-before.txt"

# 5. The plan checkers' selftests, eol-check.py over the fresh copies, and the snapshot selftest
# in a new folder.
foreach ($s in @('red-check', 'identity', 'eol-check', 'flake-run', 'split-specs', 'writer-scan', 'gated-count', 'pins-check', 'guard-check', 'guard-logs')) {
    Invoke-Step "$s-selftest" ($py + @("$plan/$s.py", '--selftest'))
}
Invoke-Step 'eol-check-row0' ($py + @("$plan/eol-check.py"))
Invoke-Step 'snapshot-selftest' ($py + @("$plan/snapshot-commit.py", '--selftest', "$receipts/snap-selftest-0-$stamp"))

# 6. The split, built into a new folder from the BASE blobs: each file's sha256 must equal the
# plan-time value (S9 when one differs).
$splitOut = "$receipts/edc-split-0-$stamp"
Invoke-Step 'split-out' ($py + @("$plan/split-specs.py", '--out', $splitOut))
$planTime = @{
    'console-chrome.test.ts' = 'ca33af993d389512adfcd8fa362a901e97b762c853fae5b80133feb796048e90'
    'copy-system-clipboard.test.ts' = '0b75576ecc0a79be0b6d37b8b26706110d944f3f975f5c33b3c5a52cb785e7f9'
    'mcp-setup-prompt.test.ts' = '525c4705ea3bce9add794697dccc968cbe5845f56ca6333e2643ced994df4485'
    'settings.test.ts' = 'a71bf7ca57160b3a84beecac4d53f8df751df40786e505d9a336a876194409ce'
}
foreach ($name in ($planTime.Keys | Sort-Object)) {
    $h = (Get-FileHash -Algorithm SHA256 -LiteralPath "$splitOut/$name").Hash.ToLower()
    Exit-Step "split-hash-$name" ([int]($h -ne $planTime[$name])) ("sha256 {0} plan-time {1} (S9 when it differs)" -f $h.Substring(0, 16), $planTime[$name].Substring(0, 16))
}

# 7. The row-0 refusals and counts: the split is not written; the static scan counts the ten
# plan-time writers (D-1312); the OLD_CLIPBOARD guard refuses a dev-PC run while an old file still
# clicks a writer or the second gated file is missing (D-1319).
Invoke-Refusal 'split-check-before' ($py + @("$plan/split-specs.py", '--check'))
Invoke-Step 'writer-scan-before' ($py + @("$plan/writer-scan.py", '--expect', '10'))
Invoke-Refusal 'flake-guard-before' ($py + @("$plan/flake-run.py", '--mode', 'full', '--runs', '1', '--no-burn', '--label', "guard-0-$stamp")) 2
# The row-0 list (Playwright --list starts no Electron and touches no clipboard): the dev-PC full
# total with the gated file excluded must be 237 (HEAD's 239 minus its 2); after rows 1 and 2 it
# must be 238 (D-1313: the 3 moved tests are excluded, the guard spec's 1 test is added).
& rtk proxy @($py + @("$plan/flake-run.py", '--list-check', '--label', "list-0-$stamp")) > "$receipts/edc-list-0.txt" 2>&1
$listCode = $LASTEXITCODE
$total = (Select-String -Path "$receipts/edc-list-0.txt" -Pattern '^expect-total (\d+)$' | Select-Object -Last 1).Matches.Groups[1].Value
Get-Content "$receipts/edc-list-0.txt" | Select-Object -Last 5
Exit-Step 'list-0' ([int]($listCode -ne 0 -or $total -ne '237')) "expect-total=$total (237 expected; S2 otherwise) receipt=$receipts/edc-list-0.txt"
# The guard list at row 0 (D-1305): npm run test:e2e -- --list with the gate variable removed
# lists 30 files and one gated file, so guard-check.py exits 1. --list runs no test.
Invoke-Refusal 'guard-list-before' ($py + @("$plan/guard-check.py", '--list', "$receipts/edc-guard-list-0-$stamp.json"))

# 8. No overwrite (NO_PARTIAL): snapshot-commit.py --out refuses an existing receipt.
$sentinel = "$receipts/edc-sentinel-0-snapshot.json"
if (-not (Test-Path -LiteralPath $sentinel)) {
    [System.IO.File]::WriteAllBytes($sentinel, [System.Text.Encoding]::UTF8.GetBytes("edc row-0 sentinel; never overwritten`n"))
}
$before = (Get-FileHash -Algorithm SHA256 -LiteralPath $sentinel).Hash
Invoke-Refusal 'snapshot-sentinel' ($py + @("$plan/snapshot-commit.py", '--out', $sentinel, 'ui/tests/e2e/console-chrome.test.ts'))
$after = (Get-FileHash -Algorithm SHA256 -LiteralPath $sentinel).Hash
Exit-Step 'snapshot-sentinel-kept' ([int]($before -ne $after)) ("sha256 before {0} after {1}" -f $before.Substring(0, 16), $after.Substring(0, 16))

# 9. The host-detail scan (AC-19) and its sentinel. The config path is built here, never
# printed, and its values never leave the Python step.
$cfg = Join-Path $HOME '.config/av-kit/e2e-host.json'
Invoke-Step 'host-details-scan' ($py + @("$plan/host-details-scan.py", $cfg, '--allow-absent'))
Invoke-Step 'host-details-sentinel' ($py + @("$receipts/baseline-host-sentinel.py", $cfg, $plan))

# 10. Ruff on this folder's Python (Session 82 RULE-1).
$planPy = @(Get-ChildItem -Path $plan -Filter '*.py' | Sort-Object Name | ForEach-Object { "$plan/$($_.Name)" })
Write-Output ("baseline plan Python: {0}" -f ($planPy -join ', '))
Invoke-Step 'ruff-format-plan' (@('uv', 'run', '--no-sync', 'ruff', 'format', '--check') + $planPy)
Invoke-Step 'ruff-check-plan' (@('uv', 'run', '--no-sync', 'ruff', 'check') + $planPy)
Write-Output 'baseline: all steps exit 0'
exit 0
