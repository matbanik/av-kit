# Session 92 mcp-audit-refresh baseline (task row 0; implementation-plan.md §Verification Plan 1).
# The shape of docs/execution/plans/2026-11-17-queue-convert-fixes/baseline.ps1, with this
# plan's steps: 1. the tree state (baseline.sha, baseline-dirty.txt with the other sessions'
# planning files marked foreign, git worktree list); the sibling check (mar-since.txt: the
# commits since ecfa3f3, and none of them touching the audit paths, S2); 2. the path-scoped
# baseline: baseline-scope.json over §Files Modified and the "Read, never changed" files, with
# the three new files and the handoff absent; baseline-dirty-hashes.json, which binds every
# dirty path outside this scope by hash; the row-0 copies (eol-check.py's base, D-1161's
# restore source) and baseline-eol.json; baseline-skip-hashes.json over packages/, tools/, ui/
# and tests/ (secret names dropped before any stat or read, Session 83 RULE-2); the S2 binding:
# the mar92-probe.txt anchors re-read by line and text (a line that only moved is recorded for
# the handoff, Session 51 RULE-3), the three issues open, YOUTUBE-CAPTIONS-IP-BLOCK resolved,
# grouping row 92 proposed, no graphify graph, and the plan and task hashes as approved; 3. the
# start condition (grouping §5): caption_probe.py and adapter_probe.py, where a FAIL is S2 and
# the session waits; 4. the MCP build and desc-check.mjs --record, checked against the AC-10
# table; 5. the host-load wait, then the base typecheck and the full MCP Vitest run, whose
# failures are recorded, not fatal; 6. the plan-local selftests, eval-rerun.py --session64,
# eol-check.py over the fresh copies, and ruff format --check and ruff check on the plan
# folder's Python (Session 82 RULE-1). Every other step is fail-fast. Run from the repository
# root in pwsh.
$ErrorActionPreference = 'Stop'
$root = (git rev-parse --show-toplevel).Trim()
Set-Location $root
$plan = 'docs/execution/plans/2026-11-17-mcp-audit-refresh'
$receipts = 'C:/Temp/av-kit/mcp-audit-refresh'
$env:ELECTRON_RUN_AS_NODE = $null
$env:PYTHONIOENCODING = 'utf-8'
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:RECEIPTS_DIR = 'C:/Temp/av-kit'
$tmp = 'C:\Temp\av-kit\mcp-audit-refresh\tmp'
New-Item -ItemType Directory -Force -Path $tmp | Out-Null
$env:TMP = $tmp
$env:TEMP = $tmp

function Invoke-Step([string]$Id, [string[]]$Argv) {
    & rtk proxy @Argv
    $code = $LASTEXITCODE
    Write-Output ("baseline step {0} exit={1}" -f $Id, $code)
    if ($code -ne 0) { exit $code }
}

# 1-2. Tree state, the sibling check, the path-scoped baseline and the S2 binding, in Python so
# every file is read and written as bytes.
$record = @'
import hashlib, json, pathlib, re, subprocess, sys

PLAN = pathlib.Path("docs/execution/plans/2026-11-17-mcp-audit-refresh")
OUT = pathlib.Path("C:/Temp/av-kit/mcp-audit-refresh")
COPIES = OUT / "baseline-copies"
EXPECTED_HEAD = "cba97fe9795b8a76532c5c6fa9da37ffad10e206"
GROUPING = ".agent/context/grouping/2026-11-17-value-triage-session-grouping.md"
RUN = "mcp-server/scripts/audit/run.ts"
REG = "mcp-server/src/toolsets/registry.ts"
CAP = "mcp-server/src/toolsets/capture.ts"
COV = "mcp-server/tests/audit/coverage.test.ts"
WORKFLOW = ".agent/workflows/mcp-audit.md"
DOC05 = "docs/build-plan/05-mcp-server.md"
BASELINE = ".agent/skills/mcp-tool-audit/resources/baseline-snapshot.json"
REPORT = ".agent/context/MCP/mcp-tool-audit-report.md"
REGISTER = ".agent/context/known-issues.yaml"
HANDOFF = ".agent/context/handoffs/2026-11-17-mcp-audit-refresh-handoff.md"
S64 = "docs/execution/plans/2026-11-11-capture-export-copy"
# §Files Modified, with each file's line-ending kind (implementation-plan.md §Line endings).
MODIFIED = {
    RUN: "CRLF",
    WORKFLOW: "CRLF",
    CAP: "CRLF",
    REG: "CRLF",
    DOC05: "CRLF",
    COV: "CRLF",
    BASELINE: "CRLF",
    REPORT: "LF",
    REGISTER: "LF",
    ".agent/context/known-issues.md": "LF",
    GROUPING: "LF",
}
NEW = {
    "mcp-server/scripts/audit/network-proof.ts": "LF",
    "mcp-server/tests/audit/network-proof.test.ts": "LF",
    "mcp-server/tests/capture-description.test.ts": "LF",
    HANDOFF: "LF",
}
# §Files Modified "Read, never changed": bound by hash; their kind is recorded, not expected.
READ_ONLY = (
    "mcp-server/scripts/audit/census.ts",
    "mcp-server/scripts/audit/plan.ts",
    "mcp-server/scripts/audit/classify.ts",
    "mcp-server/scripts/audit/backend.ts",
    "mcp-server/tests/audit/run-cli.test.ts",
    "mcp-server/tests/audit/runner-fake-backend.test.ts",
    "mcp-server/tests/audit/census-signature.test.ts",
    "mcp-server/tests/audit/classify.test.ts",
    "mcp-server/tests/audit/transcript-oracle.test.ts",
    "mcp-server/tests/audit/docs.test.ts",
    "mcp-server/tests/audit/forbidden-imports.txt",
    "mcp-server/tests/m7-resource.test.ts",
    "mcp-server/tests/capture.test.ts",
    "mcp-server/tests/fixtures.ts",
    ".agent/skills/mcp-tool-audit/SKILL.md",
    f"{S64}/eval-run.md",
    f"{S64}/eval-harness.ts",
    f"{S64}/eval-check.py",
    f"{S64}/eval-seed.py",
)
# Shared state files: read first, own lines only; copied for eol-check.py (both CRLF).
SHARED = {"docs/execution/metrics.md": "CRLF", ".agent/context/current-focus.md": "CRLF"}
PLAN_FILES = {
    f"{PLAN.as_posix()}/{n}": "LF"
    for n in (
        "implementation-plan.md", "task.md", "red-check.py", "identity.py", "issue-resolve.py",
        "eol-check.py", "baseline.ps1", "host-load.ps1", "desc-check.mjs", "eval-rerun.py",
        "baseline-diff.py", "caption_probe.py", "adapter_probe.py",
        "capture-description.expected.txt",
    )
}
# The approved plan and task (the plan's sha moved only by the Status line's execute words,
# from 903b4033... to the value here; task.md and the plan review are unchanged).
PLAN_SHA = {
    f"{PLAN.as_posix()}/implementation-plan.md": "e86ecbf8ba8a3eaf41cec5d93c15d3116bdf755727504a3d63987ae06455e408",
    f"{PLAN.as_posix()}/task.md": "ed299c128443dac5222110bb0749c0bd7860c93cd9aba9a1e5ad4be1486771bc",
}
PLAN_REVIEW = ".agent/context/handoffs/2026-11-17-mcp-audit-refresh-plan-critical-review.md"
PLAN_REVIEW_SHA = "67bd8e9fffca79f1f1114477b20d9af1554a01ae36e1f64ead5a0093568660b5"
# Other sessions' planning files, untracked in this tree: foreign, never touched, bound by hash.
FOREIGN = (
    ("docs/execution/plans/2026-11-17-e2e-pointer-flakes/", "Session 91"),
    ("docs/execution/plans/2026-11-17-video-tail-frame/", "Session 93"),
    ("docs/execution/plans/2026-11-17-ui-small-fixes/", "Session 94"),
    (".agent/context/handoffs/2026-11-17-video-tail-frame-", "Session 93"),
    (".agent/context/handoffs/2026-11-17-ui-small-fixes-", "Session 94"),
)
# The mar92-probe.txt anchors and the task row 0 ranges: (path, line, text, unique). A unique
# text must occur once in the file; if it is not on its line, the line moved and is recorded
# (Session 51 RULE-3). A non-unique text (a bracket or blank line closing a range) must be on
# its line exactly.
ANCHORS = (
    (RUN, 36, "import { AUDIT_PLAN, NETWORK_STEP_URLS, payload, type OutSub, type StepContext, type StepOutcome, type StepSpec } from \"./plan.js\";", True),
    (RUN, 102, "export type AuditDeps = {", True),
    (RUN, 107, "};", False),
    (RUN, 353, "function youtubeExtractWorks(url: string): boolean {", True),
    (RUN, 368, "function mediaFetchBlocked(url: string, wall: RegExp): boolean {", True),
    (RUN, 389, "function captionFetchBlocked(sourceUrl: string): boolean {", True),
    (RUN, 547, "discovery = classifyDiscovery({ tools: toolList, expectedTools: AUDIT_TOOLS, baseline, ghosts });", True),
    (RUN, 548, "const env: EnvFacts = { platform };", True),
    (RUN, 555, "if (options.mode === \"container\" && fixtures) {", True),
    (RUN, 564, "probe[member.key] = !urls.every((url) => url !== undefined && !youtubeExtractWorks(url));", True),
    (RUN, 576, "if (Object.keys(probe).length > 0) env.networkProbe = probe;", True),
    (RUN, 577, "}", False),
    (REG, 17, "import { captureDescriptions, captureSchema, GET_QUERY_KEYS, IMAGE_MAX_BYTES } from \"./capture.js\";", True),
    (REG, 164, "const TOOL_TOP_LEVEL: Record<string, string> = {", True),
    (REG, 172, "avkit_capture: \"Workflow: capture or list \u2192 get/image \u2192 annotate. Prerequisite: local screen and inbox files. Returns: catalog JSON or image. Errors: TOOL_ERROR.\",", True),
    (REG, 624, "description: TOOL_TOP_LEVEL[name],", True),
    (REG, 626, "_meta: { action_descriptions },", True),
    (CAP, 33, "function desc(action: string, method: string, path: string): string {", True),
    (CAP, 40, "}", False),
    (CAP, 71, "const SHEET_TEXT = [", True),
    (CAP, 79, "\"To zoom, call again with a narrower start and end; no state is kept between calls.\",", True),
    (CAP, 91, "const ANNOTATE_EXAMPLE =", True),
    (CAP, 94, "export const captureDescriptions: Record<string, string> = {", True),
    (COV, 15, "// D-499 A (Session 59, MEU-130): served actions the committed baseline doesn't hold yet,", True),
    (COV, 23, "const BASELINE_PENDING = [", True),
    (COV, 29, "];", False),
    (COV, 165, "expect(pendingProblems(BASELINE_PENDING, [...baselineKeys, \"avkit_capture.crop\"], ACTION_SET)).toEqual([", True),
    (COV, 299, "it(\"AC-135.19 sheet parity and audit coverage: BASELINE_PENDING ends with the served sheet action\", () => {", True),
    (COV, 301, "expect(BASELINE_PENDING.slice(-2)).toEqual([\"avkit_capture.sheet\", \"avkit_capture.export\"]);", True),
    (COV, 304, "});", False),
    (COV, 328, "it(\"AC-136.18 export parity and audit coverage: BASELINE_PENDING ends with the served export action\", () => {", True),
    (COV, 329, "expect(BASELINE_PENDING[BASELINE_PENDING.length - 1]).toBe(\"avkit_capture.export\");", True),
    (COV, 332, "});", False),
    (WORKFLOW, 20, "- Container: `npm --prefix mcp-server run audit -- --mode container --no-baseline --out <abs dir> --agent <name>`", True),
    (WORKFLOW, 23, "4. **Read the exit code and the summary**", True),
    (WORKFLOW, 28, "- 4 runner or CLI error.", True),
    (DOC05, 101, "### Descriptions (M7)", True),
    (DOC05, 102, "", False),
    (DOC05, 103, "Every tool/action description includes at least three of", True),
    (DOC05, 104, "", False),
    (GROUPING, 164, "| 92 | `mcp-audit-refresh` | \u2014 | P3 | proposed | \u2014 |", True),
)
OPEN_ISSUES = (
    "MCP-AUDIT-CENSUS-PROBE-SINGLE-SHOT",
    "MCP-ACTION-DESCRIPTIONS-HIDDEN-FROM-MODEL",
    "MCP-AUDIT-BASELINE-PENDING-CROP",
)
PLAN_TIME_ISSUE_LINES = {
    "MCP-AUDIT-CENSUS-PROBE-SINGLE-SHOT": 1191,
    "MCP-ACTION-DESCRIPTIONS-HIDDEN-FROM-MODEL": 5126,
    "MCP-AUDIT-BASELINE-PENDING-CROP": 5021,
    "YOUTUBE-CAPTIONS-IP-BLOCK": 3037,
}
AUDIT_PATHS = (
    "mcp-server", ".agent/skills/mcp-tool-audit", ".agent/context/MCP", WORKFLOW, DOC05,
)
SCOPE_PREFIXES = (
    PLAN.as_posix() + "/",
    ".agent/context/handoffs/2026-11-17-mcp-audit-refresh-",
    "docs/execution/reflections/2026-11-17-mcp-audit-refresh-",
)
SECRET_BASES = (".mcp.json", "mcp-token.txt", ".claude.json", ".env")
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
    for prefix, who in FOREIGN:
        if p.startswith(prefix):
            return who
    return None


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

# The sibling check (§Sibling overlap): every commit since ecfa3f3, and none touching the audit paths.
since = git("log", "--oneline", "ecfa3f3..HEAD").decode("utf-8")
touching = git("log", "--oneline", "ecfa3f3..HEAD", "--", *AUDIT_PATHS).decode("utf-8")
(OUT / "mar-since.txt").write_bytes(
    (
        "git log --oneline ecfa3f3..HEAD\n" + since
        + "\ngit log --oneline ecfa3f3..HEAD -- " + " ".join(AUDIT_PATHS) + "\n"
        + (touching or "(empty)\n")
    ).encode("utf-8")
)
print("mar-since.txt:")
for line in since.splitlines():
    print("  since", line)
print("  session 74 commit named:", any("MEU-144" in ln for ln in since.splitlines()))
print("  session 91 commit: none; the queue runs 92, 93, 94, then 91 (the brief: deferred on a ledger stop)")
print("  commits touching the audit paths:", touching.splitlines() or "none")
if touching.strip():
    problems.append(f"S2: commits since ecfa3f3 touch the audit paths: {touching.splitlines()}")

porcelain = git("status", "--porcelain", "--untracked-files=all").decode("utf-8")
dirty = [line[3:].strip().strip('"') for line in porcelain.splitlines() if line.strip()]
marks = [f"# foreign ({foreign(p)}): {p}" for p in dirty if foreign(p)]
(PLAN / "baseline-dirty.txt").write_bytes((porcelain + "".join(m + "\n" for m in marks)).encode("utf-8"))
print("baseline-dirty.txt", len(dirty), "paths,", len(marks), "foreign")
for p in dirty:
    print("  dirty", p, f"(foreign: {foreign(p)})" if foreign(p) else "")

KINDS = {**MODIFIED, **NEW}
scope = {p: sha(p) for p in (*KINDS, *READ_ONLY)}
for p in NEW:
    if scope[p] != "absent":
        problems.append(f"S2: new file already exists: {p}")
for p in (*MODIFIED, *READ_ONLY):
    if scope[p] in ("absent", "not-a-file"):
        problems.append(f"S2: scoped path missing: {p}")
(PLAN / "baseline-scope.json").write_bytes((json.dumps(scope, indent=2) + "\n").encode())
print("baseline-scope.json", len(scope), "paths;", sum(v == "absent" for v in scope.values()), "absent")


def in_scope(p):
    return p in scope or p in SHARED or p.startswith(SCOPE_PREFIXES)


hashes = {p: (sha(p) if pathlib.Path(p).exists() else "deleted") for p in dirty if not in_scope(p) and not secret(p)}
(PLAN / "baseline-dirty-hashes.json").write_bytes((json.dumps(hashes, indent=2, sort_keys=True) + "\n").encode())
print("baseline-dirty-hashes.json", len(hashes), "paths outside this scope")
for p in sorted(hashes):
    print("  bound by hash", p, hashes[p][:16])
for p in SHARED:
    print("bound by content (read first, own lines only)", p, "dirty" if p in dirty else "clean at HEAD", sha(p)[:16])

# The row-0 content of every existing scoped, read-only, shared and plan file: eol-check.py's
# base, D-1161's restore source, the S3 diffs' base and the execution review's delta base.
copied = 0
for p in (*KINDS, *READ_ONLY, *SHARED, *PLAN_FILES, PLAN_REVIEW):
    if not pathlib.Path(p).is_file():
        continue
    dest = COPIES / p
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(pathlib.Path(p).read_bytes())
    copied += 1
print("baseline-copies", copied, "row-0 copies under", COPIES.as_posix())

# baseline-skip-hashes.json (H1-4): every tracked or untracked, not-ignored file under packages/,
# tools/, ui/ and tests/, secret names dropped before any stat or read.
listed = git("ls-files", "--cached", "--others", "--exclude-standard", "packages", "tools", "ui", "tests")
skip_paths = [n for n in listed.decode("utf-8").splitlines() if n and not secret(n)]
skips = {p: sha(p) for p in skip_paths if pathlib.Path(p).is_file()}
(PLAN / "baseline-skip-hashes.json").write_bytes((json.dumps(skips, indent=2, sort_keys=True) + "\n").encode())
print("baseline-skip-hashes.json", len(skips), "files under packages/, tools/, ui/ and tests/")

# Line endings, measured with Python bytes.
eols = {}
for p, want in {**KINDS, **{q: None for q in READ_ONLY}, **SHARED, **PLAN_FILES}.items():
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

# S2: the anchors by line and text.
moved = []
for p, line, needle, unique in ANCHORS:
    text = pathlib.Path(p).read_bytes().decode("utf-8")
    lines = text.replace("\r\n", "\n").split("\n")
    here = lines[line - 1] if line <= len(lines) else None
    if unique:
        n = text.count(needle)
        hits = [i + 1 for i, ln in enumerate(lines) if needle in ln]
        at = here is not None and needle in here
        state = "at line" if at else (f"moved to {hits}" if len(hits) == 1 else "missing")
        print(f"anchor {p}:{line} {state} count={n} :: {needle[:100]!r}")
        if n != 1:
            problems.append(f"S2: anchor {needle[:80]!r} in {p} counted {n}, not 1")
        elif not at:
            moved.append(f"{p}:{line} -> {hits[0]}")
    else:
        ok = here is not None and here.strip() == needle
        print(f"anchor {p}:{line} {'at line' if ok else 'NOT at line'} :: {needle!r} (got {here!r})")
        if not ok:
            problems.append(f"S2: {p}:{line} is {here!r}, not {needle!r}")
print("anchor lines moved:", moved or "none")

# S2: the registers, the grouping row, graphify, the approved plan and task.
register = pathlib.Path(REGISTER).read_bytes().decode("utf-8")
reg_lines = register.split("\n")


def issue_state(issue):
    m = re.search(r"^  - id: " + re.escape(issue) + r"\n(?:    .*\n)*?    status: (\S+)", register, re.M)
    line = next((i + 1 for i, ln in enumerate(reg_lines) if ln == f"  - id: {issue}"), None)
    return (m.group(1) if m else None), line


for issue in (*OPEN_ISSUES, "YOUTUBE-CAPTIONS-IP-BLOCK"):
    state, line = issue_state(issue)
    want = "resolved" if issue == "YOUTUBE-CAPTIONS-IP-BLOCK" else "open"
    was = PLAN_TIME_ISSUE_LINES[issue]
    note = "" if line == was else f" (moved from plan-time :{was})"
    print(f"issue {issue} line {line}{note} status {state}")
    if state != want:
        problems.append(f"S2: {issue} is {state}, not {want}")
rows = [ln for ln in pathlib.Path(GROUPING).read_bytes().decode("utf-8").split("\n") if ln.startswith("| 92 |")]
print("grouping row 92", rows)
if len(rows) != 1 or "| proposed |" not in rows[0]:
    problems.append("S2: grouping row 92 is not one proposed row")
graphs = [g for g in ("graphify-out", "graphify-out-research") if pathlib.Path(g).exists()]
print("graphify graphs", graphs)
if graphs:
    problems.append(f"S1: a graphify graph exists: {graphs}")
for p, want in PLAN_SHA.items():
    got = sha(p)
    print("approved", p, got)
    if got != want:
        problems.append(f"S2: {p} sha256 {got}, not the approved {want}")
got = sha(PLAN_REVIEW)
print("plan review", PLAN_REVIEW, got)
if got != PLAN_REVIEW_SHA:
    problems.append(f"S2: the plan review's sha256 is {got}, not {PLAN_REVIEW_SHA}")
for n in ("red-check.py", "identity.py", "issue-resolve.py", "eol-check.py", "host-load.ps1"):
    p = PLAN / n
    print("plan script", p.as_posix(), sha(p)[:16])
    if not p.is_file():
        problems.append(f"row 0: {p.as_posix()} is missing")
for p in problems:
    print("PROBLEM:", p)
sys.exit(1 if problems else 0)
'@

# 4. The AC-10 table against the row-0 record (S2).
$ac10 = @'
import hashlib, json, sys

TABLE = {
    "avkit_download": (91, "c22a90eba581b02973d531d87ca02ac43fa5226e73ad4c890f01fa257c0496d8"),
    "avkit_transcript": (98, "c6b3660065afdc2cc9f36021433c6ff4f1dcd6cd25c90e1137d2c01cbea01379"),
    "avkit_tts": (109, "df5d6471a68ba7ed77c54b02db24929ded517cebfe3dd1d61596b78888af1ec7"),
    "avkit_models": (89, "2345edcba75c2441a16c92340c70c7979cc0ee92b26a0cdbc7e69000c9bddf41"),
    "avkit_settings": (107, "160dfcbbdcd118fd98e8ff890e0e58d5e157c964b209c1b7dbae1d4b4a4b2702"),
    "avkit_health": (103, "4c49f8fc874d1ca8131c0fc4f998333bae5bef4c15834dfca71ff079d490583b"),
    "avkit_convert": (102, "215e7640860933c37722ba8ab3e959efa8404903f5ca570867a716f2b18bbaaf"),
}
record = json.loads(open(sys.argv[1], encoding="utf-8").read())
bad = []
for tool, (chars, digest) in TABLE.items():
    d = (record.get(tool) or {}).get("description")
    got = (len(d), hashlib.sha256(d.encode("utf-8")).hexdigest()) if isinstance(d, str) else None
    ok = got == (chars, digest)
    print(f"ac10 {tool} chars={got and got[0]} sha256={got and got[1]} {'match' if ok else 'MISMATCH'}")
    if not ok:
        bad.append(tool)
cap = (record.get("avkit_capture") or {}).get("description") or ""
print(f"ac10 avkit_capture row-0 description {len(cap)} chars (replaced in row 4)")
print(f"ac10: {len(TABLE) - len(bad)} of {len(TABLE)} match the plan's table")
sys.exit(1 if bad else 0)
'@
New-Item -ItemType Directory -Force -Path $receipts | Out-Null
Set-Content -Path "$receipts/baseline-record.py" -Value $record -Encoding utf8
Set-Content -Path "$receipts/baseline-ac10.py" -Value $ac10 -Encoding utf8
Invoke-Step 'uv-sync' @('uv', 'sync', '--frozen', '--all-packages')
Invoke-Step 'record' @('uv', 'run', '--no-sync', 'python', "$receipts/baseline-record.py")

# 3. The start condition (grouping §5): one caption fetch and one adapter fetch, read only.
& rtk proxy uv run --no-sync python "$plan/caption_probe.py" *> "$receipts/mar-caption-probe.txt"
$capCode = $LASTEXITCODE
& rtk proxy uv run --no-sync python "$plan/adapter_probe.py" *> "$receipts/mar-adapter-probe.txt"
$adCode = $LASTEXITCODE
Get-Content "$receipts/mar-caption-probe.txt", "$receipts/mar-adapter-probe.txt"
Write-Output ("baseline step probes caption_exit={0} adapter_exit={1}" -f $capCode, $adCode)
$probeText = (Get-Content "$receipts/mar-caption-probe.txt", "$receipts/mar-adapter-probe.txt" -Raw) -join "`n"
if ($capCode -ne 0 -or $adCode -ne 0 -or $probeText -match '\bFAIL\b') {
    Write-Output 'S2: captions blocked; the session waits'
    exit 1
}

# 4. The host-load wait (before each build, the brief), the MCP build and the row-0 description
# record, checked against the AC-10 table.
& pwsh -NoProfile -File "$plan/host-load.ps1" *> "$receipts/mar-host-load-r0-build.txt"
$loadCode = $LASTEXITCODE
Get-Content "$receipts/mar-host-load-r0-build.txt" | Select-Object -Last 2
Write-Output ("baseline step host-load-build exit={0}" -f $loadCode)
if ($loadCode -ne 0) { exit $loadCode }
Invoke-Step 'mcp-build' @('npm', '--prefix', 'mcp-server', 'run', 'build')
Invoke-Step 'desc-record' @('node', "$plan/desc-check.mjs", '--record', "$receipts/mar-desc-record.json")
Invoke-Step 'ac10-table' @('uv', 'run', '--no-sync', 'python', "$receipts/baseline-ac10.py", "$receipts/mar-desc-record.json")

# 5. The host-load wait, then the base receipts from pwsh in mcp-server/ (memory:
# vitest-from-pwsh-not-bash); the gate's mcp-tests excuse list reads mar-base-mcp.txt. Their
# failures are recorded, not fatal.
& pwsh -NoProfile -File "$plan/host-load.ps1" *> "$receipts/mar-host-load-r0.txt"
$loadCode = $LASTEXITCODE
Get-Content "$receipts/mar-host-load-r0.txt" | Select-Object -Last 3
Write-Output ("baseline step host-load exit={0}" -f $loadCode)
if ($loadCode -ne 0) { exit $loadCode }
& rtk proxy npm --prefix mcp-server run typecheck *> "$receipts/mar-base-mcp-types.txt"
Write-Output ("base mcp-types exit={0} receipt={1}/mar-base-mcp-types.txt" -f $LASTEXITCODE, $receipts)
Get-Content "$receipts/mar-base-mcp-types.txt" | Select-Object -Last 6
Push-Location 'P:\av-kit\mcp-server'
& rtk proxy npx vitest run *> "$receipts/mar-base-mcp.txt"
$mcpCode = $LASTEXITCODE
Pop-Location
Set-Content -Path "$receipts/mar-base-mcp.txt.exit" -Value $mcpCode -Encoding ascii
Write-Output ("base suite mcp exit={0} receipt={1}/mar-base-mcp.txt" -f $mcpCode, $receipts)
Get-Content "$receipts/mar-base-mcp.txt" | Select-String -Pattern 'Test Files|Tests |FAIL ' | Select-Object -Last 12

# 6. The plan-local checkers (Session 82 RULE-1 on the plan folder's Python).
$planPy = @(Get-ChildItem -Path $plan -Filter '*.py' | ForEach-Object { "$plan/$($_.Name)" })
Invoke-Step 'ruff-format-plan' (@('uv', 'run', '--no-sync', 'ruff', 'format', '--check') + $planPy)
Invoke-Step 'ruff-check-plan' (@('uv', 'run', '--no-sync', 'ruff', 'check') + $planPy)
Invoke-Step 'red-check-selftest' @('uv', 'run', '--no-sync', 'python', "$plan/red-check.py", '--selftest')
Invoke-Step 'identity-selftest' @('uv', 'run', '--no-sync', 'python', "$plan/identity.py", '--selftest')
Invoke-Step 'eol-check-selftest' @('uv', 'run', '--no-sync', 'python', "$plan/eol-check.py", '--selftest')
Invoke-Step 'desc-check-selftest' @('node', "$plan/desc-check.mjs", '--selftest')
Invoke-Step 'eval-rerun-selftest' @('uv', 'run', '--no-sync', 'python', "$plan/eval-rerun.py", '--selftest')
Invoke-Step 'baseline-diff-selftest' @('uv', 'run', '--no-sync', 'python', "$plan/baseline-diff.py", '--selftest')
Invoke-Step 'eval-rerun-session64' @('uv', 'run', '--no-sync', 'python', "$plan/eval-rerun.py", '--session64')
Invoke-Step 'eol-check-row0' @('uv', 'run', '--no-sync', 'python', "$plan/eol-check.py")
Write-Output 'baseline: all steps exit 0'
exit 0
