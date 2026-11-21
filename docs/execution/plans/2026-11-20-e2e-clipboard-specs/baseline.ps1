# Session 98 e2e-clipboard-specs baseline (task row 0; implementation-plan.md §Verification Plan 1).
# The shape of docs/execution/plans/2026-11-19-e2e-host-parity/baseline.ps1 (Session 97), with this
# plan's steps: 1. uv sync --frozen --offline --all-packages (S7 on a held file); 2. the record: the
# tree state (baseline.sha, baseline-dirty.txt with the foreign class marked, git worktree list);
# the sibling check (ecs-since.txt: every commit since b59207b, and the scope diff since b59207b,
# which must be empty, S2); baseline-scope.json over §Files Modified, the "Read, never changed"
# files and the foreign class, with the new spec file, the handoff, the implementation review and
# the reflection absent; baseline-dirty-hashes.json, which binds every dirty path outside this
# scope by hash; the row-0 copies under D/baseline-copies (pins-check.py's and eol-check.py's base);
# baseline-eol.json; baseline-skip-hashes.json over packages/, mcp-server/{src,scripts,tests} and
# native/ (secret names dropped before any stat or read, Session 83 RULE-2); the S2 anchors by
# line and text (a line that only moved is recorded for the handoff, Session 51 RULE-3), the known
# list (2 skip entries, no known and no gated entry), both issues open with no MEU link
# (yaml.safe_load, by key, Session 92 RULE-2), grouping row 98 pending, 29 spec files, the
# clipboard calls of the four clipboard spec files, no graphify graph, and the plan, task and
# plan-review hashes; 3. the OS-wide probe (Session 91 RULE-1: host-load.ps1 and every Electron and
# node process, D/ecs-os-probe-0.txt); 4. the home-path check before (ecs-home-before.txt, S8);
# 5. the plan checkers' selftests and eol-check.py over the fresh copies; 6. split-specs.py --out
# into a new folder, each file's sha256 against its plan-time value (S9); 7. the row-0 refusals:
# split-specs.py --check and probe-check.py --block exit 1, flake-run.py --mode full exits 2 before
# any run (the OLD_CLIPBOARD guard), the row-0 --list-check total is 239, and guard-check.py --list
# exits 1 (no guarded clipboard file yet; D-1282); 8. the
# snapshot-commit --out sentinel (no overwrite); 9. the host-detail
# scan (AC-17) and its sentinel; 10. ruff on this folder's Python (Session 82 RULE-1). Every step is
# fail-fast. Run from the repository root in pwsh. No step reaches the network or the second
# Windows host. This file names no host alias, account or folder of the real host
# (LOCAL_HOST_DETAILS).
$ErrorActionPreference = 'Stop'
$root = (git rev-parse --show-toplevel).Trim()
Set-Location $root
$plan = 'docs/execution/plans/2026-11-20-e2e-clipboard-specs'
$receipts = 'C:/Temp/av-kit/e2e-clipboard-specs'
Remove-Item Env:ELECTRON_RUN_AS_NODE -ErrorAction SilentlyContinue
$env:PYTHONIOENCODING = 'utf-8'
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:RECEIPTS_DIR = 'C:/Temp/av-kit'
$tmp = 'C:\Temp\av-kit\e2e-clipboard-specs\tmp'
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
import hashlib, json, pathlib, re, subprocess, sys

import yaml

PLAN = pathlib.Path("docs/execution/plans/2026-11-20-e2e-clipboard-specs")
OUT = pathlib.Path("C:/Temp/av-kit/e2e-clipboard-specs")
COPIES = OUT / "baseline-copies"
EXPECTED_HEAD = "b59207b084cfe18e54acdec0799541762f3a67a0"
BASE = "b59207b"
GROUPING = ".agent/context/grouping/2026-11-20-e2e-clipboard-specs-session-grouping.md"
REGISTER = ".agent/context/known-issues.yaml"
KNOWN = "tools/e2e_host/known-failures.json"
ISSUES = ("E2E-CLIPBOARD-SPECS-UNGATED", "E2E-CLIPBOARD-PRIMER-EMPTY")
HANDOFF = ".agent/context/handoffs/2026-11-20-e2e-clipboard-specs-handoff.md"
IMPL_REVIEW = ".agent/context/handoffs/2026-11-20-e2e-clipboard-specs-implementation-critical-review.md"
PLAN_REVIEW = ".agent/context/handoffs/2026-11-20-e2e-clipboard-specs-plan-critical-review.md"
REFLECTION = "docs/execution/reflections/2026-11-20-e2e-clipboard-specs-reflection.md"
FILM = "ui/tests/e2e/capture-filmstrip-actions.test.ts"
IMPORT = "ui/tests/e2e/capture-import.test.ts"
CLIP = "ui/tests/e2e/capture-system-clipboard.test.ts"
CONSOLE = "ui/tests/e2e/console-chrome.test.ts"
MCP = "ui/tests/e2e/mcp-setup-prompt.test.ts"
REMOTE = "tools/e2e_remote.py"
FACTS = "tools/e2e_host/host-facts.ps1"
STATUS = "tools/e2e_host/host-status.ps1"
RUN_E2E = "tools/e2e_host/run-e2e.ps1"
TESTS = "tests/tooling/test_e2e_remote.py"
RUN_BOOK = ".agent/docs/e2e-remote-host.md"
SKIP_SPECS = ("capture-filmstrip-actions.test.ts", "capture-import.test.ts")
# §Files Modified that exist at row 0, with each file's line-ending kind.
MODIFIED = {
    FILM: "CRLF",
    IMPORT: "LF",
    REMOTE: "LF",
    FACTS: "LF",
    STATUS: "LF",
    RUN_E2E: "LF",
    KNOWN: "LF",
    TESTS: "LF",
    RUN_BOOK: "LF",
    ".agent/docs/commands.md": "CRLF",
    REGISTER: "LF",
    ".agent/context/known-issues.md": "LF",
    GROUPING: "LF",
    ".agent/context/current-focus.md": "CRLF",
    "docs/execution/metrics.md": "CRLF",
}
# §Files Modified that are new; each must be absent at row 0. The plan review exists by design
# (it approved the plan) and is bound by its hash below, not here.
NEW = {CLIP: "LF", HANDOFF: "LF", IMPL_REVIEW: "LF", REFLECTION: "LF"}
# §Files Modified "Read, never changed": bound by hash; their kind is recorded, not expected.
READ_ONLY = (
    CONSOLE,
    MCP,
    "ui/tests/e2e/electron-app.ts",
    "ui/tests/e2e/electron-env.ts",
    "ui/tests/e2e/global-setup.ts",
    "ui/playwright.config.ts",
    "ui/scripts/playwright-with-outputfile.mjs",
    "ui/package.json",
    "tools/e2e_host/host-lock.ps1",
    "tools/e2e_host/host-prepare.ps1",
    "tools/e2e_host/host-release.ps1",
    "tools/e2e_host/host-start.ps1",
    "tools/e2e_host/e2e-host.example.json",
    "docs/BUILD_PLAN.md",
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
# The task row 0 anchors: (path, line, text). The text must be on its line; one hit elsewhere
# is a moved line (recorded for the handoff, Session 51 RULE-3); otherwise S2.
ANCHORS = (
    (FILM, 210, "AC-88.12 f"),
    (FILM, 242, "test('AC-88.12 (a)(b)(f) Copy full path and Copy image"),
    (FILM, 269, "test('AC-88.12 (c) Shift+F10"),
    (FILM, 286, "test('AC-88.12 (d)(e) menu Delete"),
    (FILM, 314, "test('AC-89.9 Shift-click range"),
    (FILM, 353, "test('AC-89.15 a checkbox left of each thumb"),
    (IMPORT, 238, "test('AC-132.22 a drop of two PNGs"),
    (IMPORT, 337, "test('AC-132.23 Ctrl+V pastes"),
    (CONSOLE, 77, "test('C1-5 copy writes clipboard"),
    (MCP, 91, "test('AC-71.15 Codex prompt"),
    (REMOTE, 51, "REASONS: dict[str, int] = {"),
    (REMOTE, 391, "def load_known("),
    (REMOTE, 406, "def label_skip("),
    (REMOTE, 574, "def fact_lines("),
    (REMOTE, 635, "def host_call("),
    (REMOTE, 941, "def _poll("),
    (REMOTE, 1045, "def _collect_and_summarize("),
    (REMOTE, 1115, "def _run("),
    (REMOTE, 1268, "def _check("),
    (RUN_E2E, 114, "$p = Start-Process -FilePath $nodeExe"),
    (RUN_E2E, 116, "'pid.txt'"),
    (RUN_E2E, 117, "$p.WaitForExit()"),
    (RUN_E2E, 120, "AvDone $res $code ''"),
    (TESTS, 37, "SCRIPTS = ("),
    (TESTS, 46, "BUSY_COPIES = ("),
    (TESTS, 1561, "def test_ac_11_known_tracked_list("),
    (TESTS, 2263, 'assert "Session 97" in text'),
    (GROUPING, 108, "| 98 | `e2e-clipboard-specs` |"),
    (REGISTER, 3628, "  - id: E2E-CLIPBOARD-PRIMER-EMPTY"),
    (REGISTER, 6037, "  - id: E2E-CLIPBOARD-SPECS-UNGATED"),
)
CLIPBOARD_CALL = re.compile(r"clipboard\.(read|write)[A-Za-z]*\(")
CODE_DIRS = ("ui", "packages", "tests", "tools", "backend", "mcp-server", "native")
SKIP_DIRS = ("packages", "mcp-server/src", "mcp-server/scripts", "mcp-server/tests", "native")
SECRET_BASES = (".mcp.json", "mcp-token.txt", ".claude.json", ".env")
SCOPE_PREFIXES = (
    PLAN.as_posix() + "/",
    ".agent/context/handoffs/2026-11-20-e2e-clipboard-specs-",
    "docs/execution/reflections/2026-11-20-e2e-clipboard-specs-",
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

# The sibling check: every commit since b59207b, and no scope diff since it.
since = git("log", "--oneline", f"{BASE}..HEAD").decode("utf-8")
stat = git("diff", "--stat", BASE, "HEAD", "--", *SCOPE_PATHS).decode("utf-8")
(OUT / "ecs-since.txt").write_bytes(
    (
        f"git log --oneline {BASE}..HEAD\n" + (since or "(empty)\n")
        + f"\ngit diff --stat {BASE} HEAD -- <{len(SCOPE_PATHS)} scope paths>\n"
        + (stat or "(empty)\n")
    ).encode("utf-8")
)
print(f"ecs-since.txt: commits since {BASE}:", since.splitlines() or "none")
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
# pins-check.py's and eol-check.py's base and the execution review's delta base.
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
row98 = text_lines(GROUPING)[107]
print("grouping :108 pending:", "pending" in row98)
if "pending" not in row98:
    problems.append("S2: grouping row 98 is not pending")
print("anchor lines moved:", moved or "none")

# S2: the known list (2 skip entries for the two old files, no known entry, no gated list).
known = json.loads(pathlib.Path(KNOWN).read_bytes().decode("utf-8"))
skip_files = sorted(e.get("file") for e in known.get("skip", []))
labels = sorted({e.get("label") for e in known.get("skip", [])})
print("known list: keys", sorted(known), "known", len(known.get("known", [])), "skip", skip_files, "labels", labels)
if known.get("known") != [] or skip_files != sorted(SKIP_SPECS) or labels != ["mini-air"] or "gated" in known:
    problems.append("S2: the known list is not label mini-air, known [], the two old files skipped, no gated list")

# S2: the issues, read by key with yaml.safe_load (Session 92 RULE-2).
data = yaml.safe_load(pathlib.Path(REGISTER).read_bytes().decode("utf-8"))
for issue in ISSUES:
    matches = [i for i in data.get("issues", []) if isinstance(i, dict) and i.get("id") == issue]
    entry = matches[0] if len(matches) == 1 else {}
    print(f"issue {issue}: entries {len(matches)}, status {entry.get('status')}, category {entry.get('category')}, meu_links {entry.get('meu_links')!r}")
    if entry.get("status") != "open" or entry.get("meu_links") != []:
        problems.append(f"S2: {issue} is not open with meu_links []")

# S2: the spec files at HEAD, and the clipboard calls of the four clipboard spec files.
names = git("ls-tree", "--name-only", "HEAD", "ui/tests/e2e/").decode("utf-8").splitlines()
specs = sorted(n.rsplit("/", 1)[-1] for n in names if n.endswith((".test.ts", ".spec.ts")))
kept = [s for s in specs if s not in SKIP_SPECS]
print("spec files at HEAD:", len(specs), "without the skip files:", len(kept))
if len(specs) != 29 or len(kept) != 27 or CLIP.rsplit("/", 1)[-1] in specs:
    problems.append(f"S2: {len(specs)} spec files, {len(kept)} without the skip files (29 and 27 expected)")
calls = {}
for p in (FILM, IMPORT, CONSOLE, MCP):
    calls[p] = [i + 1 for i, ln in enumerate(text_lines(p)) if CLIPBOARD_CALL.search(ln)]
    print("clipboard calls", p, calls[p])
if not all(calls.values()):
    problems.append("S2: a clipboard spec file holds no clipboard call")
other = sorted(
    n for n in git("grep", "-l", "-E", r"clipboard\.(read|write)", "--", "ui/tests/e2e/").decode("utf-8").splitlines()
    if n and n not in (FILM, IMPORT, CONSOLE, MCP)
)
print("other E2E files with a clipboard call (D-1277 counts four):", other)
if other:
    problems.append(f"S2: more E2E files call the clipboard than D-1277 names: {other}")

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
$lines = @("ecs-os-probe-0 $(Get-Date -Format o)")
$procs = Get-CimInstance Win32_Process | Where-Object { $_.Name -match '^(electron|node)(\.exe)?$' -or $_.Name -match 'av-kit' } | Sort-Object ProcessId
foreach ($p in $procs) {
    $path = [string]$p.ExecutablePath
    if ($home_prefix -and $path.StartsWith($home_prefix, [StringComparison]::OrdinalIgnoreCase)) { $path = '<HOME>' + $path.Substring($home_prefix.Length) }
    $lines += ("process pid={0} name={1} created={2} path={3}" -f $p.ProcessId, $p.Name, $p.CreationDate.ToString('o'), $path)
}
$lines += ("electron_node_processes={0}" -f @($procs).Count)
$lines
'@

# 9. The host-detail sentinel (AC-17): the config's host value is written to one scratch file,
# never printed; the scan must exit 1 naming the key only; that one file is removed.
$hostSentinel = @'
import json, pathlib, subprocess, sys

cfg, plan = pathlib.Path(sys.argv[1]), sys.argv[2]
target = pathlib.Path("C:/Temp/av-kit/e2e-clipboard-specs/ecs-host-sentinel.txt")
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
named = "('host'," in out and "ecs-host-sentinel.txt" in out
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
& pwsh -NoProfile -File "$plan/host-load.ps1" > "$receipts/ecs-os-probe-0-load.txt" 2>&1
$loadCode = $LASTEXITCODE
& pwsh -NoProfile -File "$receipts/baseline-os-probe.ps1" > "$receipts/ecs-os-probe-0-procs.txt" 2>&1
$procCode = $LASTEXITCODE
$probeText = @(Get-Content "$receipts/ecs-os-probe-0-load.txt") + @("host-load.ps1 exit=$loadCode") + @(Get-Content "$receipts/ecs-os-probe-0-procs.txt") + @("process probe exit=$procCode")
[System.IO.File]::WriteAllText("$receipts/ecs-os-probe-0.txt", (($probeText -join "`n") + "`n"))
Remove-Item -LiteralPath "$receipts/ecs-os-probe-0-load.txt", "$receipts/ecs-os-probe-0-procs.txt"
Get-Content "$receipts/ecs-os-probe-0.txt" | Select-Object -Last 12
Exit-Step 'os-probe' ([int]($loadCode -ne 0 -or $procCode -ne 0)) "receipt=$receipts/ecs-os-probe-0.txt"

# 4. The home-path check before (S8).
& rtk proxy uv run --no-sync python tools/check_home_path.py > "$receipts/ecs-home-before.txt" 2>&1
$homeCode = $LASTEXITCODE
Get-Content "$receipts/ecs-home-before.txt" | Select-Object -Last 4
Exit-Step 'home-path' $homeCode "receipt=$receipts/ecs-home-before.txt"

# 5. The plan checkers' selftests, eol-check.py over the fresh copies, and the snapshot selftest
# in a new folder.
foreach ($s in @('red-check', 'identity', 'eol-check', 'flake-run', 'split-specs', 'probe-check', 'pins-check', 'guard-check')) {
    Invoke-Step "$s-selftest" ($py + @("$plan/$s.py", '--selftest'))
}
Invoke-Step 'eol-check-row0' ($py + @("$plan/eol-check.py"))
Invoke-Step 'snapshot-selftest' ($py + @("$plan/snapshot-commit.py", '--selftest', "$receipts/snap-selftest-0-$stamp"))

# 6. The split, built into a new folder from the BASE blobs: each file's sha256 must equal the
# plan-time value (S9 when one differs).
$splitOut = "$receipts/ecs-split-0-$stamp"
Invoke-Step 'split-out' ($py + @("$plan/split-specs.py", '--out', $splitOut))
$planTime = @{
    'capture-system-clipboard.test.ts' = 'f848f6b48826ed128e197f49753cf09513bfa2a3e0fde7d763a5d4d48635d069'
    'capture-filmstrip-actions.test.ts' = '026997846ea516bf1e05c03d3beaf2300dd0ce0b101663ba5ae0cb94323f282a'
    'capture-import.test.ts' = 'e6a28e77c3c2bd617d7a0477e3b776d2a24634830b38432eb420701e8c9d8edb'
}
foreach ($name in ($planTime.Keys | Sort-Object)) {
    $h = (Get-FileHash -Algorithm SHA256 -LiteralPath "$splitOut/$name").Hash.ToLower()
    Exit-Step "split-hash-$name" ([int]($h -ne $planTime[$name])) ("sha256 {0} plan-time {1} (S9 when it differs)" -f $h.Substring(0, 16), $planTime[$name].Substring(0, 16))
}

# 7. The row-0 refusals: the split is not written, the probe block does not exist, and the
# OLD_CLIPBOARD guard refuses a dev-PC run while an old file still calls the clipboard.
Invoke-Refusal 'split-check-before' ($py + @("$plan/split-specs.py", '--check'))
Invoke-Refusal 'probe-block-before' ($py + @("$plan/probe-check.py", '--block'))
Invoke-Refusal 'flake-guard-before' ($py + @("$plan/flake-run.py", '--mode', 'full', '--runs', '1', '--no-burn', '--label', "guard-0-$stamp")) 2
# The row-0 list (Playwright --list starts no Electron and touches no clipboard): the full total
# with both old files listed must be 239 (Session 97's 232 plus the 7 tests of the two old files);
# after the split it must be 237 (D-1276).
& rtk proxy @($py + @("$plan/flake-run.py", '--list-check', '--label', "list-0-$stamp")) > "$receipts/ecs-list-0.txt" 2>&1
$listCode = $LASTEXITCODE
$total = (Select-String -Path "$receipts/ecs-list-0.txt" -Pattern '^expect-total (\d+)$' | Select-Object -Last 1).Matches.Groups[1].Value
Get-Content "$receipts/ecs-list-0.txt" | Select-Object -Last 5
Exit-Step 'list-0' ([int]($listCode -ne 0 -or $total -ne '239')) "expect-total=$total (239 expected; S2 otherwise) receipt=$receipts/ecs-list-0.txt"
# The guard list at row 0 (D-1282): npm run test:e2e -- --list with the gate variable removed
# lists 29 files and no guarded clipboard file, so guard-check.py exits 1. --list runs no test.
Invoke-Refusal 'guard-list-before' ($py + @("$plan/guard-check.py", '--list', "$receipts/ecs-guard-list-0-$stamp.json"))

# 8. No overwrite (NO_PARTIAL): snapshot-commit.py --out refuses an existing receipt.
$sentinel = "$receipts/ecs-sentinel-0-snapshot.json"
if (-not (Test-Path -LiteralPath $sentinel)) {
    [System.IO.File]::WriteAllBytes($sentinel, [System.Text.Encoding]::UTF8.GetBytes("ecs row-0 sentinel; never overwritten`n"))
}
$before = (Get-FileHash -Algorithm SHA256 -LiteralPath $sentinel).Hash
Invoke-Refusal 'snapshot-sentinel' ($py + @("$plan/snapshot-commit.py", '--out', $sentinel, 'ui/tests/e2e/capture-import.test.ts'))
$after = (Get-FileHash -Algorithm SHA256 -LiteralPath $sentinel).Hash
Exit-Step 'snapshot-sentinel-kept' ([int]($before -ne $after)) ("sha256 before {0} after {1}" -f $before.Substring(0, 16), $after.Substring(0, 16))

# 9. The host-detail scan (AC-17) and its sentinel. The config path is built here, never
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
