# Session 96 e2e-remote-host baseline (task row 0; implementation-plan.md §Verification Plan 1).
# The shape of docs/execution/plans/2026-11-18-eval-describe-raw-bytes/baseline.ps1, with this
# plan's steps: 1. uv sync --frozen --offline --all-packages (S7 on a held file); 2. the tree
# state (baseline.sha, baseline-dirty.txt with the foreign class marked, git worktree list); the
# sibling check (erh-since.txt: every commit since a43cdb2, and the product diff since a43cdb2,
# which must be empty, S2); the path-scoped baseline: baseline-scope.json over §Files Modified,
# the "Read, never changed" files and the foreign class, with every new file and the handoff
# absent; baseline-dirty-hashes.json, which binds every dirty path outside this scope by hash;
# the row-0 copies (eol-check.py's base and the execution review's delta base) and
# baseline-eol.json; baseline-skip-hashes.json over packages/, ui/, mcp-server/{src,scripts,tests}
# and native/ (secret names dropped before any stat or read, Session 83 RULE-2); the hand
# scripts' and hand reports' hashes (erh-hand-hashes.json); the S2 binding: the anchors by line
# and text (a line that only moved is recorded for the handoff, Session 51 RULE-3), the spec
# count, .node-version, the three issues open (yaml.safe_load, by key, Session 92 RULE-2),
# grouping row 96 pending, the stub's four files, no graphify graph, and the plan, task and
# plan-review hashes as approved; the local config, written once with exclusive create from the
# plan-time scratch values (other values are S2; its values are never printed); 3. the host
# probe (erh-host-probe-0.txt) and its facts (a busy, locked or unsigned host is recorded, not a
# stop); 4. the host load, recorded; 5. the home-path check before (erh-home-before.txt, S8);
# 6. the red-check.py, identity.py and eol-check.py selftests, eol-check.py over the fresh
# copies, and ruff format --check and ruff check on the plan folder's Python (Session 82
# RULE-1). Every step is fail-fast. Run from the repository root in pwsh. This file names no
# host alias, account or folder of the real host (LOCAL_HOST_DETAILS).
$ErrorActionPreference = 'Stop'
$root = (git rev-parse --show-toplevel).Trim()
Set-Location $root
$plan = 'docs/execution/plans/2026-11-18-e2e-remote-host'
$receipts = 'C:/Temp/av-kit/e2e-remote-host'
$env:ELECTRON_RUN_AS_NODE = $null
$env:PYTHONIOENCODING = 'utf-8'
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:RECEIPTS_DIR = 'C:/Temp/av-kit'
$tmp = 'C:\Temp\av-kit\e2e-remote-host\tmp'
New-Item -ItemType Directory -Force -Path $tmp | Out-Null
$env:TMP = $tmp
$env:TEMP = $tmp

function Invoke-Step([string]$Id, [string[]]$Argv) {
    & rtk proxy @Argv
    $code = $LASTEXITCODE
    Write-Output ("baseline step {0} exit={1}" -f $Id, $code)
    if ($code -ne 0) { exit $code }
}

# 2. Tree state, the sibling check, the path-scoped baseline, the S2 binding and the local
# config, in Python so every file is read and written as bytes.
$record = @'
import hashlib, json, pathlib, subprocess, sys

import yaml

PLAN = pathlib.Path("docs/execution/plans/2026-11-18-e2e-remote-host")
OUT = pathlib.Path("C:/Temp/av-kit/e2e-remote-host")
COPIES = OUT / "baseline-copies"
HAND = pathlib.Path("C:/Temp/av-kit/fleet-research/miniair")
EXPECTED_HEAD = "a43cdb24f97af6f10498fa70abb5ada4b0882835"
GROUPING = ".agent/context/grouping/2026-11-18-e2e-remote-host-session-grouping.md"
REGISTER = ".agent/context/known-issues.yaml"
COMMANDS = ".agent/docs/commands.md"
ISSUES = ("CI-E2E-FLEET-HOST-UNTRACKED", "CAPTURE-TEXT-PIXEL-2PX-MINIAIR", "E2E-HOVER-NO-POINTER-DEVICE")
HANDOFF = ".agent/context/handoffs/2026-11-18-e2e-remote-host-handoff.md"
SKIP_SPECS = ("capture-filmstrip-actions.test.ts", "capture-import.test.ts")
STUB = pathlib.Path("native/region-picker-stub/publish")
STUB_FILES = (
    "avkit-region-picker-stub.exe",
    "avkit-region-picker-stub.dll",
    "avkit-region-picker-stub.deps.json",
    "avkit-region-picker-stub.runtimeconfig.json",
)
HOST_SCRIPTS = ("host-facts", "host-lock", "host-prepare", "host-start", "host-status", "host-release", "run-e2e")
# §Files Modified, with each file's line-ending kind (implementation-plan.md §Files Modified).
MODIFIED = {
    COMMANDS: "CRLF",
    REGISTER: "LF",
    ".agent/context/known-issues.md": "LF",
    GROUPING: "LF",
}
NEW = {
    "tests/tooling/test_e2e_remote.py": "LF",
    "tools/e2e_remote.py": "LF",
    "tools/e2e_host/e2e-host.example.json": "LF",
    "tools/e2e_host/known-failures.json": "LF",
    **{f"tools/e2e_host/{n}.ps1": "LF" for n in HOST_SCRIPTS},
    ".agent/docs/e2e-remote-host.md": "LF",
    HANDOFF: "LF",
}
# §Files Modified "Read, never changed": bound by hash; their kind is recorded, not expected.
READ_ONLY = (
    "ui/tests/e2e/global-setup.ts",
    "ui/playwright.config.ts",
    "ui/scripts/playwright-with-outputfile.mjs",
    "ui/package.json",
    ".node-version",
    ".gitignore",
    "pyproject.toml",
    "docs/BUILD_PLAN.md",
)
# The foreign class (Session 92 RULE-3): the coordinator's files, bound by hash; a change is
# recorded in the handoff, is not S4 and stays out of the commit paths.
FOREIGN_CLASS = (
    ".agent/model-registry.local.json",
    *sorted(p.as_posix() for p in pathlib.Path(".claude/agents").glob("*.md")),
    *sorted(p.as_posix() for p in pathlib.Path(".cursor/agents").glob("*.md")),
)
# Shared state files: read first, own lines only; copied for eol-check.py (both CRLF).
SHARED = {"docs/execution/metrics.md": "CRLF", ".agent/context/current-focus.md": "CRLF"}
PLAN_FILES = {
    f"{PLAN.as_posix()}/{n}": "LF"
    for n in (
        "implementation-plan.md", "task.md", "zip-time.py", "host-probe.ps1", "host-probe-run.py",
        "host-details-scan.py", "red-check.py", "identity.py", "issue-resolve.py", "eol-check.py",
        "baseline.ps1", "host-load.ps1",
    )
}
# The approved plan and task. The plan's sha moved only by the Status line's execute words
# (the coordinator, 2026-11-18), from 8a301a7f... (reviewed) to the value here; task.md is
# unchanged since review. The plan review's hash is the one found before row 0 ran.
PLAN_SHA = {
    f"{PLAN.as_posix()}/implementation-plan.md": "82548e628895e168675e97803e796903002212a34054de21592b36b200418d74",
    f"{PLAN.as_posix()}/task.md": "4036d3e931a56926fd3058e1fde54910c80a01de019d0f210561061d2ea3b870",
}
PLAN_REVIEW = ".agent/context/handoffs/2026-11-18-e2e-remote-host-plan-critical-review.md"
PLAN_REVIEW_SHA = "d45e16c73c049b174b418f3a5398ab92acfcde25473180127695e16c4d06c5cf"
# The task row 0 anchors: (path, line, text). Each text must occur once in its file; if it is
# not on its line, the line moved and is recorded (Session 51 RULE-3).
ANCHORS = (
    ("ui/tests/e2e/global-setup.ts", 43, "newest.mtimeMs > built"),
    ("ui/playwright.config.ts", 14, "globalSetup"),
    ("ui/playwright.config.ts", 18, "workers: 1"),
    (COMMANDS, 205, "| ui-electron |"),
    (GROUPING, 133, "| 96 |"),
)
PRODUCT = ("ui", "native", "packages", "backend", "mcp-server/src")
SCOPE_PREFIXES = (
    PLAN.as_posix() + "/",
    ".agent/context/handoffs/2026-11-18-e2e-remote-host-",
    "docs/execution/reflections/2026-11-18-e2e-remote-host-",
)
SKIP_DIRS = ("packages", "ui", "mcp-server/src", "mcp-server/scripts", "mcp-server/tests", "native")
SECRET_BASES = (".mcp.json", "mcp-token.txt", ".claude.json", ".env")
HAND_FILES = (
    "run-e2e.ps1",
    "02-build.ps1",
    "03-finish-deps.ps1",
    "04-register-start.ps1",
    "11-rerun.ps1",
    "results/20261118-191358/report.json",
    "results/20261118-185348/report.json",
)
# The local config (D-1222): the plan-time scratch values plus the example's other keys, in the
# plan's key order. The values come from the scratch file and are never printed here.
CFG = pathlib.Path.home() / ".config" / "av-kit" / "e2e-host.json"
CFG_KEYS = ("host", "user", "label", "root", "task", "node_exe", "ffmpeg_bin", "busy_users", "min_free_gb", "poll_s", "timeout_min")
CFG_EXTRA = {"node_exe": "C:\\Program Files\\nodejs\\node.exe", "min_free_gb": 20, "poll_s": 30, "timeout_min": 110}
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

# The sibling check: every commit since a43cdb2, and no product diff since it.
since = git("log", "--oneline", "a43cdb2..HEAD").decode("utf-8")
stat = git("diff", "--stat", "a43cdb2", "HEAD", "--", *PRODUCT).decode("utf-8")
(OUT / "erh-since.txt").write_bytes(
    (
        "git log --oneline a43cdb2..HEAD\n" + (since or "(empty)\n")
        + "\ngit diff --stat a43cdb2 HEAD -- " + " ".join(PRODUCT) + "\n"
        + (stat or "(empty)\n")
    ).encode("utf-8")
)
print("erh-since.txt: commits since a43cdb2:", since.splitlines() or "none")
print("  product diff since a43cdb2:", stat.splitlines() or "empty")
if stat.strip():
    problems.append(f"S2: the product changed since a43cdb2: {stat.splitlines()}")

porcelain = git("status", "--porcelain", "--untracked-files=all").decode("utf-8")
dirty = [line[3:].strip().strip('"') for line in porcelain.splitlines() if line.strip()]
marks = [f"# foreign ({foreign(p)}): {p}" for p in dirty if foreign(p)]
(PLAN / "baseline-dirty.txt").write_bytes((porcelain + "".join(m + "\n" for m in marks)).encode("utf-8"))
print("baseline-dirty.txt", len(dirty), "paths,", len(marks), "foreign")
for p in dirty:
    print("  dirty", p, f"(foreign: {foreign(p)})" if foreign(p) else "")

KINDS = {**MODIFIED, **NEW}
scope = {p: sha(p) for p in (*KINDS, *READ_ONLY, *FOREIGN_CLASS)}
for p in NEW:
    if scope[p] != "absent":
        problems.append(f"S2: new file already exists: {p}")
for p in (*MODIFIED, *READ_ONLY):
    if scope[p] in ("absent", "not-a-file"):
        problems.append(f"S2: scoped path missing: {p}")
(PLAN / "baseline-scope.json").write_bytes((json.dumps(scope, indent=2) + "\n").encode())
print("baseline-scope.json", len(scope), "paths;", sum(v == "absent" for v in scope.values()), "absent;", len(FOREIGN_CLASS), "foreign class")
for p in FOREIGN_CLASS:
    print("  foreign class", p, scope[p][:16])


def in_scope(p):
    return p in scope or p in SHARED or p.startswith(SCOPE_PREFIXES)


hashes = {p: (sha(p) if pathlib.Path(p).exists() else "deleted") for p in dirty if not in_scope(p) and not secret(p)}
(PLAN / "baseline-dirty-hashes.json").write_bytes((json.dumps(hashes, indent=2, sort_keys=True) + "\n").encode())
print("baseline-dirty-hashes.json", len(hashes), "paths outside this scope")
for p in sorted(hashes):
    print("  bound by hash", p, hashes[p][:16])
for p in SHARED:
    print("bound by content (read first, own lines only)", p, "dirty" if p in dirty else "clean at HEAD", sha(p)[:16])

# The row-0 content of every existing repository scope, read-only, shared and plan file:
# eol-check.py's base, row 4's commands.md base, row 7's register base and the execution
# review's delta base.
copied = 0
for p in (*KINDS, *READ_ONLY, *SHARED, *PLAN_FILES, PLAN_REVIEW):
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
for p, want in {**KINDS, **{q: None for q in READ_ONLY}, **SHARED, **PLAN_FILES}.items():
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

# The hand scripts and both hand reports, hashed (read, never moved or changed).
hand = {}
for n in HAND_FILES:
    hand[n] = sha(HAND / n)
    print("hand", n, hand[n][:16])
    if hand[n] in ("absent", "not-a-file"):
        problems.append(f"S2: hand file missing: {n}")
hand_out = OUT / "erh-hand-hashes.json"
hand_bytes = (json.dumps(hand, indent=2) + "\n").encode()
if hand_out.is_file():
    same = hand_out.read_bytes() == hand_bytes
    print("erh-hand-hashes.json exists from an earlier run of this row; same:", same)
    if not same:
        problems.append("S2: the hand files changed since the earlier run of this row")
else:
    hand_out.write_bytes(hand_bytes)
    print("erh-hand-hashes.json written,", len(hand), "files")

# S2: the anchors by line and text.
moved = []
for p, line, needle in ANCHORS:
    text = pathlib.Path(p).read_bytes().decode("utf-8")
    lines = text.replace("\r\n", "\n").split("\n")
    here = lines[line - 1] if line <= len(lines) else None
    n = text.count(needle)
    hits = [i + 1 for i, ln in enumerate(lines) if needle in ln]
    at = here is not None and needle in here
    state = "at line" if at else (f"moved to {hits}" if len(hits) == 1 else "missing")
    print(f"anchor {p}:{line} {state} count={n} :: {needle!r}")
    if n != 1:
        problems.append(f"S2: anchor {needle!r} in {p} counted {n}, not 1")
    elif not at:
        moved.append(f"{p}:{line} -> {hits[0]}")
cmd = text_lines(COMMANDS)
row = [i + 1 for i, ln in enumerate(cmd) if ln.startswith("| ui-electron |")]
print("commands.md rows starting '| ui-electron |':", row)
if len(row) != 1:
    problems.append(f"S2: commands.md has {len(row)} rows starting '| ui-electron |'")
grouping = text_lines(GROUPING)
row96 = [(i + 1, ln) for i, ln in enumerate(grouping) if ln.startswith("| 96 |")]
row_ok = len(row96) == 1 and "pending" in row96[0][1]
print("grouping row 96", row96, "one pending row:", row_ok)
if not row_ok:
    problems.append("S2: grouping row 96 is not one pending row")
print("anchor lines moved:", moved or "none")

# S2: the spec files at HEAD, .node-version and the stub.
names = git("ls-tree", "--name-only", "HEAD", "ui/tests/e2e/").decode("utf-8").splitlines()
specs = sorted(n.rsplit("/", 1)[-1] for n in names if n.endswith((".test.ts", ".spec.ts")))
kept = [s for s in specs if s not in SKIP_SPECS]
print("spec files at HEAD:", len(specs), "without the skip files:", len(kept), "skip files present:", [s for s in SKIP_SPECS if s in specs])
if len(specs) != 29 or len(kept) != 27:
    problems.append(f"S2: {len(specs)} spec files, {len(kept)} without the skip files (29 and 27 expected)")
nv = pathlib.Path(".node-version").read_bytes().decode("utf-8").strip()
print(".node-version", nv)
if nv != "26.13.0":
    problems.append(f"S2: .node-version is {nv}, not 26.13.0")
for n in STUB_FILES:
    present = (STUB / n).is_file()
    print("stub", n, "present:", present)
    if not present:
        problems.append(f"S2: the stub file {n} is missing")

# S2: the issues, read by key with yaml.safe_load (Session 92 RULE-2).
data = yaml.safe_load(pathlib.Path(REGISTER).read_bytes().decode("utf-8"))
for issue in ISSUES:
    matches = [i for i in data.get("issues", []) if isinstance(i, dict) and i.get("id") == issue]
    status = matches[0].get("status") if len(matches) == 1 else None
    reg_line = next((i + 1 for i, ln in enumerate(text_lines(REGISTER)) if ln == f"  - id: {issue}"), None)
    print(f"issue {issue}: entries {len(matches)}, status {status}, line {reg_line}")
    if status != "open":
        problems.append(f"S2: {issue} is {status}, not open")

# S1: no graphify graph.
graphs = [g for g in ("graphify-out", "graphify-out-research") if pathlib.Path(g).exists()]
print("graphify graphs", graphs)
if graphs:
    problems.append(f"S1: a graphify graph exists: {graphs}")

# The approved plan, task and plan review.
for p, want in PLAN_SHA.items():
    got = sha(p)
    print("approved", p, got)
    if got != want:
        problems.append(f"S2: {p} sha256 {got}, not the approved {want}")
got = sha(PLAN_REVIEW)
print("plan review", PLAN_REVIEW, got)
if got != PLAN_REVIEW_SHA:
    problems.append(f"S2: the plan review's sha256 is {got}, not {PLAN_REVIEW_SHA}")
for n in ("red-check.py", "identity.py", "issue-resolve.py", "eol-check.py", "host-load.ps1", "zip-time.py", "host-probe.ps1", "host-probe-run.py", "host-details-scan.py"):
    p = PLAN / n
    print("plan script", p.as_posix(), sha(p)[:16])
    if not p.is_file():
        problems.append(f"row 0: {p.as_posix()} is missing")

# The local config (D-1222): exclusive create; the same values are kept; other values are S2.
values = json.loads((OUT / "erh-host-values.json").read_bytes().decode("utf-8"))
want_cfg = {k: (values[k] if k in values else CFG_EXTRA[k]) for k in CFG_KEYS}
cfg_bytes = (json.dumps(want_cfg, indent=2) + "\n").encode("utf-8")
if CFG.exists():
    have = json.loads(CFG.read_bytes().decode("utf-8"))
    same = have == want_cfg
    print("local config <HOME>/.config/av-kit/e2e-host.json exists; same values:", same, "keys:", sorted(have))
    if not same:
        problems.append("S2: a local config exists with other values")
else:
    CFG.parent.mkdir(parents=True, exist_ok=True)
    with open(CFG, "xb") as f:
        f.write(cfg_bytes)
    print("local config <HOME>/.config/av-kit/e2e-host.json written (exclusive create), keys:", list(want_cfg), "CR", cfg_bytes.count(b"\r"))
for p in problems:
    print("PROBLEM:", p)
sys.exit(1 if problems else 0)
'@

# 3b. The host probe's facts (task row 0): S2 on a task, launcher, Node or layout difference; a
# busy, locked or unsigned host is recorded only.
$probeCheck = @'
import pathlib, re, sys

t = pathlib.Path("C:/Temp/av-kit/e2e-remote-host/erh-host-probe-0.txt").read_text(encoding="utf-8")
lines = t.splitlines()
must = {
    "exit 0": lines[-1:] == ["exit=0"],
    "task=True logon=Interactive runlevel=Limited": re.search(r"^task=True .*logon=Interactive runlevel=Limited$", t, re.M) is not None,
    "task action ends run-e2e.ps1": re.search(r"^task_action=.*run-e2e\.ps1$", t, re.M) is not None,
    "lock=False bin=False": re.search(r"^lock=False .*bin=False$", t, re.M) is not None,
    "runs=False results_r=0": re.search(r"^runs=False results_r=0 ", t, re.M) is not None,
    "ssh_shell ends powershell.exe": re.search(r"^ssh_shell=.*powershell\.exe$", t, re.M) is not None,
    "launcher sha256=5AB99494 tracked_marker=False": re.search(r"^launcher=True sha256=5AB99494\S* tracked_marker=False$", t, re.M) is not None,
    "node ver=v26.13.0": re.search(r"^node=True ver=v26\.13\.0$", t, re.M) is not None,
}
recorded = {
    "a sessions entry Active": re.search(r"^sessions=.*\|Active\|", t, re.M) is not None,
    "logonui empty": re.search(r"^logonui=$", t, re.M) is not None,
    "busy_user_test_processes=0": re.search(r"^busy_user_test_processes=0(\s|$)", t, re.M) is not None,
}
for k, v in must.items():
    print("probe fact", k, v)
for k, v in recorded.items():
    print("probe recorded (not a stop)", k, v)
for ln in lines:
    if ln.startswith(("runner_processes=", "busy_users_missing=", "free_gb=", "task_limit=")):
        print("probe", ln)
miss = [k for k, v in must.items() if not v]
print("probe facts that differ (S2):", miss)
sys.exit(1 if miss else 0)
'@

New-Item -ItemType Directory -Force -Path $receipts | Out-Null
Set-Content -Path "$receipts/baseline-record.py" -Value $record -Encoding utf8
Set-Content -Path "$receipts/baseline-probe-check.py" -Value $probeCheck -Encoding utf8

# 1. The environment (S7 on a held file).
Invoke-Step 'uv-sync' @('uv', 'sync', '--frozen', '--offline', '--all-packages')
# 2. The record and the local config.
Invoke-Step 'record' @('uv', 'run', '--no-sync', 'python', "$receipts/baseline-record.py")

# 3. The host probe (read only). A rerun of this row after a later step failed finds the probe
# written (the runner refuses an existing OUT); it then checks that receipt.
$cfg = Join-Path $HOME '.config/av-kit/e2e-host.json'
if (Test-Path -LiteralPath "$receipts/erh-host-probe-0.txt") {
    Write-Output 'baseline host probe: erh-host-probe-0.txt exists from an earlier run of this row; checking it'
} else {
    Invoke-Step 'host-probe' @('uv', 'run', '--no-sync', 'python', "$plan/host-probe-run.py", $cfg, "$receipts/erh-host-probe-0.txt")
}
Invoke-Step 'host-probe-facts' @('uv', 'run', '--no-sync', 'python', "$receipts/baseline-probe-check.py")

# 4. The host load, recorded only: row 0 runs no build or suite, so it does not wait.
# host-load.ps1 (the 50 % wait) runs before row 1's Red and in the H1-2 gate.
$samples = @()
for ($i = 0; $i -lt 5; $i++) {
    if ($i -gt 0) { Start-Sleep -Seconds 2 }
    $samples += [math]::Round([double](Get-CimInstance Win32_Processor | Measure-Object -Property LoadPercentage -Average).Average, 1)
}
$mean = [math]::Round((($samples | Measure-Object -Average).Average), 1)
Write-Output ("baseline host load recorded: samples [{0}] mean={1} % (not a wait; row 1 and H1-2 wait at 50 %)" -f ($samples -join ', '), $mean)

# 5. The home-path check before (S8).
& rtk proxy uv run --no-sync python tools/check_home_path.py *> "$receipts/erh-home-before.txt"
$homeCode = $LASTEXITCODE
Get-Content "$receipts/erh-home-before.txt" | Select-Object -Last 4
Write-Output ("baseline step home-path exit={0} receipt={1}/erh-home-before.txt" -f $homeCode, $receipts)
if ($homeCode -ne 0) { exit $homeCode }

# 6. The plan-local checkers (Session 82 RULE-1 on the plan folder's Python).
Invoke-Step 'red-check-selftest' @('uv', 'run', '--no-sync', 'python', "$plan/red-check.py", '--selftest')
Invoke-Step 'identity-selftest' @('uv', 'run', '--no-sync', 'python', "$plan/identity.py", '--selftest')
Invoke-Step 'eol-check-selftest' @('uv', 'run', '--no-sync', 'python', "$plan/eol-check.py", '--selftest')
Invoke-Step 'eol-check-row0' @('uv', 'run', '--no-sync', 'python', "$plan/eol-check.py")
$planPy = @(Get-ChildItem -Path $plan -Filter '*.py' | Sort-Object Name | ForEach-Object { "$plan/$($_.Name)" })
Write-Output ("baseline plan Python: {0}" -f ($planPy -join ', '))
Invoke-Step 'ruff-format-plan' (@('uv', 'run', '--no-sync', 'ruff', 'format', '--check') + $planPy)
Invoke-Step 'ruff-check-plan' (@('uv', 'run', '--no-sync', 'ruff', 'check') + $planPy)
Write-Output 'baseline: all steps exit 0'
exit 0
