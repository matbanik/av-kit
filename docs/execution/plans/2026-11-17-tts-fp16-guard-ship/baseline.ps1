# TTS FP16 guard ship baseline (task row 0; implementation-plan.md §Verification Plan 1).
# The shape of docs/execution/plans/2026-11-17-test-run-reliability/baseline.ps1, with this
# plan's steps: 1. the tree state (baseline.sha, baseline-dirty.txt with the four sibling
# sessions' paths recorded as foreign, the worktree list); 2. the path-scoped baseline:
# baseline-scope.json over §Files Modified and the "Read, never changed" files, with the four
# new Python files and the handoff absent; baseline-dirty-hashes.json, which binds every dirty
# path outside this scope by hash (the foreign sibling paths excluded, D-1140);
# the row-0 copies (eol-check.py's base and the execution review's delta base) and
# baseline-eol.json; baseline-skip-hashes.json over ui/, mcp-server/, tools/, packages/api/
# and packages/core/ (secret names dropped before any stat or read, Session 83 RULE-2); the S2
# binding: every cited anchor found by its text and counted, its line now printed beside its
# plan-time line (a moved line is recorded for the handoff; only a missing or doubled anchor
# stops), the issue open with its four meu_links, grouping row 74 proposed, MEU-144, AC-144.
# and D-1135 to D-1144 absent, phase_guard.py absent, no graphify graph, the Session 73 inputs
# (S8), and the plan and task hashes as approved; 3. the host-load wait (host-load.ps1, S15),
# then the base receipts: the full Python suite with the D6 argv without -x (ff-base-py.txt,
# failures recorded, not fatal) and ruff format --check and ruff check on adapter.py and the
# four pin files (ff-base-ruff.txt); 4. the five plan-local selftests and ruff format --check
# and ruff check on the plan folder's Python (Session 82 RULE-1), then eol-check.py over the
# fresh copies. The reference's `uv sync --frozen --all-packages` step is not run: it can reach
# the network, and the environment is used as found (`uv run --no-sync`). Every other step is
# fail-fast. Run from the repository root in pwsh.
$ErrorActionPreference = 'Stop'
$root = (git rev-parse --show-toplevel).Trim()
Set-Location $root
$plan = 'docs/execution/plans/2026-11-17-tts-fp16-guard-ship'
$receipts = 'C:/Temp/av-kit/tts-fp16-guard-ship'
$env:ELECTRON_RUN_AS_NODE = $null
$env:PYTHONIOENCODING = 'utf-8'
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:RECEIPTS_DIR = 'C:/Temp/av-kit'
$tmp = 'C:\Temp\av-kit\tts-fp16-guard-ship\tmp'
New-Item -ItemType Directory -Force -Path $tmp | Out-Null
$env:TMP = $tmp
$env:TEMP = $tmp

function Invoke-Step([string]$Id, [string[]]$Argv) {
    & rtk proxy @Argv
    $code = $LASTEXITCODE
    Write-Output ("baseline step {0} exit={1}" -f $Id, $code)
    if ($code -ne 0) { exit $code }
}

# 1-2. Tree state, path-scoped baseline and the S2 binding, in Python so every file is read and
# written as bytes.
$record = @'
import hashlib, json, pathlib, re, subprocess, sys

PLAN = pathlib.Path("docs/execution/plans/2026-11-17-tts-fp16-guard-ship")
OUT = pathlib.Path("C:/Temp/av-kit/tts-fp16-guard-ship")
COPIES = OUT / "baseline-copies"
TTS = "packages/infrastructure/src/avkit_infra/tts"
ADAPTER = f"{TTS}/adapter.py"
VOICES = f"{TTS}/voices.py"
GUARD = f"{TTS}/phase_guard.py"
CONTROLS = "ui/src/renderer/src/features/tts/tts-controls.ts"
SERVICE = "docs/build-plan/03-service-layer.md"
MATRIX = "docs/build-plan/build-priority-matrix.md"
STATUS = ".agent/context/meu-status.yaml"
MEU_REGISTRY = ".agent/context/meu-registry.md"
BUILD_PLAN = "docs/BUILD_PLAN.md"
REGISTER = ".agent/context/known-issues.yaml"
REGISTER_MD = ".agent/context/known-issues.md"
GROUPING = ".agent/context/grouping/2026-11-17-value-triage-session-grouping.md"
HANDOFF = ".agent/context/handoffs/2026-11-17-tts-fp16-guard-ship-MEU-144-handoff.md"
HANDOFFS = pathlib.Path(".agent/context/handoffs")
# §Files Modified, with each file's line-ending kind (implementation-plan.md §Files Modified).
MODIFIED = {
    ADAPTER: "CRLF",
    SERVICE: "CRLF",
    MATRIX: "CRLF",
    STATUS: "LF",
    MEU_REGISTRY: "LF",
    BUILD_PLAN: "LF",
    REGISTER: "LF",
    REGISTER_MD: "LF",
    GROUPING: "LF",
}
NEW = {
    GUARD: "CRLF",
    "tests/tts_onnx_synthetic.py": "CRLF",
    "tests/unit/test_tts_phase_guard.py": "CRLF",
    "tests/integration/test_tts_phase_guard_load.py": "CRLF",
}
# §Project files "Read, never changed": bound by hash; the kind is checked where the plan's
# line-ending note names it, recorded otherwise.
READ_ONLY = {
    CONTROLS: "CRLF",
    VOICES: "CRLF",
    f"{TTS}/__init__.py": "LF",
    "packaging/avkit-backend.spec": None,
    "tools/package_backend.py": None,
    "tools/smoke_packaged_tts.py": None,
    "tests/integration/test_tts_device_resolution.py": "CRLF",
    "tests/integration/test_tts_models.py": "CRLF",
    "tests/integration/test_tts_no_torch.py": "CRLF",
    "tests/e2e/test_api_model_load_keeps.py": "LF",
    "tests/tts_g2p_fakes.py": "CRLF",
    "docs/execution/plans/2026-11-06-tts-load-fp16/fp16-test-set/test-set.json": None,
}
# Shared state files: read first, own lines only; copied for eol-check.py (both CRLF).
SHARED = {"docs/execution/metrics.md": "CRLF", ".agent/context/current-focus.md": "CRLF"}
PLAN_FILES = {
    f"{PLAN.as_posix()}/{n}": "LF"
    for n in (
        "implementation-plan.md", "task.md", "red-check.py", "identity.py", "issue-resolve.py",
        "eol-check.py", "smoke-check.py", "home-redact.py", "host-load.ps1", "baseline.ps1",
    )
}
# The approved plan and task. The plan moved from f7cca9f396c1... (as reviewed) to
# a87b5cc2f49d... (LF, 0 CR) before execution; task.md is unchanged since the review.
PLAN_SHA = {
    f"{PLAN.as_posix()}/implementation-plan.md": "a87b5cc2f49d97aab8c1c55b7d8539f6bc61894941277567792a1ec054708aac",
    f"{PLAN.as_posix()}/task.md": "ae954894bb0401693db3dc7e0c8e6a44584827c3261eaa7f7848391d1c0aa831",
}
PLAN_REVIEW = ".agent/context/handoffs/2026-11-17-tts-fp16-guard-ship-plan-critical-review.md"
# The S2 anchors: (path, needle, expected count, the plan's lines or None where the plan cites
# the text without a line). A count other than the expected one stops (S2); a line other than
# the plan's is printed as moved and recorded for the handoff (Session 51 RULE-3).
ANCHORS = (
    (ADAPTER, "InferenceSession(str(path)", 2, (402, 414)),
    (ADAPTER, 'log = structlog.get_logger(module="tts")', 1, (46,)),
    (ADAPTER, "from avkit_infra.tts.g2p import KokoroG2p, split_phonemes", 1, None),
    (ADAPTER, "    def _load_onnx(", 1, (397,)),
    (ADAPTER, '        if target == "cuda":', 1, None),
    (VOICES, 'ONNX_REVISION = "', 1, (84,)),
    (VOICES, "SIDELOAD_SUFFIXES = (", 1, (126,)),
    (CONTROLS, "export const PRESELECT_ORDER = ['kokoro-onnx-int8', 'kokoro-onnx-fp32'] as const", 1, (157,)),
    (SERVICE, '<a id="download-failure-reason-residual"></a>', 1, (704,)),
    (SERVICE, '<a id="tts-fp16-phase-guard-residual"></a>', 1, None),
    (SERVICE, "## TTS FP16 phase guard (residual)", 1, None),
    (MATRIX, "| 3.20 | MEU-142 | `svc-download-audio-extract` |", 1, (53,)),
    (MATRIX, "| 3.21 |", 0, None),
    (STATUS, "- row_key: MEU-143", 1, (3753,)),
    (STATUS, "- row_key: MEU-145", 1, (3780,)),
    (STATUS, "    3.21 is held for Session 74's MEU-144.", 1, (43,)),
    (STATUS, "with MEU-144 held for Session 74", 1, (4171,)),
    (STATUS, "id: MEU-144", 0, None),
    (MEU_REGISTRY, "| MEU-144 |", 0, None),
    (GUARD, None, None, None),
)
ISSUE = "TTS-ONNX-FP16-NONFINITE-AUDIO"
ISSUE_LINKS = ["MEU-62", "MEU-72", "MEU-121", "MEU-127"]
GROUPING_ROW = "| 74 | `tts-fp16-guard-ship` | MEU-144 (held) | P2 | proposed | \u2014 |"
# MEU-144, AC-144. and D-1135..D-1144 must be absent from the registers and the handoffs.
# This plan's own plan review is excluded: it reviews D-1135 and D-1136 and the AC table; the
# foreign sibling handoffs are not read (D-1140).
ABSENT_REGISTERS = (STATUS, MEU_REGISTRY, BUILD_PLAN, REGISTER, REGISTER_MD, SERVICE, MATRIX)
D_IDS = tuple(f"D-{n}" for n in range(1135, 1145))
# Session 73's inputs named in the plan's §Goal (S8).
S73_DIRS = (
    "C:/Temp/av-kit/s73/models-original",
    "C:/Temp/av-kit/s73/models-guarded",
    "C:/Temp/av-kit/s73/models-download",
    "C:/Temp/av-kit/s73/run-control",
    "C:/Temp/av-kit/s73/run-guarded",
    "C:/Temp/av-kit/s73/run-int8",
    "C:/Temp/av-kit/s52/smoke-models",
)
S73_DBS = tuple(f"C:/Temp/av-kit/s73/{r}/app-data/avkit.db" for r in ("run-control", "run-guarded", "run-int8"))
FP16_REL = "kokoro-v1.0-onnx/onnx/model_fp16.onnx"
FP16_SHA = "ba4527a874b42b21e35f468c10d326fdff3c7fc8cac1f85e9eb6c0dfc35c334a"
FP16_BYTES = 163234740
INPUT_SHA = {
    "C:/Temp/av-kit/s52-smoke-red.json": "add8770339bc45ca2ab8ad6448b76bca3d481228df19ab900ab46afc0ff03135",
    "docs/execution/plans/2026-11-06-tts-load-fp16/fp16-test-set/test-set.json": "53c941543295b48439b633faf2746b33123c17482207a4a6e99faad6f6760ef3",
}
# The plan records no hash for these three; each must exist and its row-0 hash is recorded.
INPUT_PRESENT = (
    "C:/Temp/av-kit/s73-smoke-control.json",
    "C:/Temp/av-kit/s73-smoke-guarded.json",
    "C:/Temp/av-kit/s73-smoke-int8.json",
)
RUN_FOLDERS = ("run-control", "run-guarded", "run-int8", "models-copy")
SCOPE_PREFIXES = (
    PLAN.as_posix() + "/",
    ".agent/context/handoffs/2026-11-17-tts-fp16-guard-ship-",
    "docs/execution/reflections/2026-11-17-tts-fp16-guard-ship-",
)
# The four sibling sessions' plan folders and handoffs are foreign (D-1140): recorded in
# baseline-dirty.txt, never hashed, read or bound; their planners write them while this runs.
SIBLINGS = "e2e-pointer-flakes|mcp-audit-refresh|ui-small-fixes|video-tail-frame"
FOREIGN = re.compile(
    r"^(?:docs/execution/plans/2026-11-1[5-7]-(?:" + SIBLINGS + r")/"
    r"|\.agent/context/handoffs/2026-11-1[5-7]-(?:" + SIBLINGS + r")-[^/]+$)"
)
SKIP_ROOTS = ("ui", "mcp-server", "tools", "packages/api", "packages/core")
SECRET_BASES = (".mcp.json", "mcp-token.txt", ".claude.json", ".env")
problems = []
moved = []


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


head = git("rev-parse", "HEAD").decode().strip()
(PLAN / "baseline.sha").write_bytes((head + "\n").encode())
print("baseline.sha", head)
if head != "174bafa8a9ff327d38e54bd36f3edcb0e0b62085":
    problems.append(f"S2: HEAD is {head}, not the brief's 174bafa")
origin = subprocess.run(["git", "rev-parse", "origin/main"], capture_output=True).stdout.decode().strip()
print("origin/main as found", origin or "<none>")
for line in git("worktree", "list").decode("utf-8").splitlines():
    print("worktree", line)
porcelain = git("status", "--porcelain", "--untracked-files=all").decode("utf-8")
dirty = [line[3:].strip().strip('"') for line in porcelain.splitlines() if line.strip()]
foreign = sorted(p for p in dirty if FOREIGN.match(p))
trailer = "".join(f"## foreign {p}\n" for p in foreign)
(PLAN / "baseline-dirty.txt").write_bytes((porcelain + trailer).encode("utf-8"))
print("baseline-dirty.txt", len(dirty), "paths,", len(foreign), "foreign (sibling sessions, D-1140)")
for p in dirty:
    print("  dirty", "foreign" if p in foreign else "-", p)

KINDS = {**MODIFIED, **NEW}
scope = {p: sha(p) for p in (*KINDS, *READ_ONLY)}
for p in NEW:
    if scope[p] != "absent":
        problems.append(f"S2: new file already exists: {p}")
if sha(HANDOFF) != "absent":
    problems.append(f"S2: the handoff already exists: {HANDOFF}")
for p in (*MODIFIED, *READ_ONLY):
    if scope[p] in ("absent", "not-a-file"):
        problems.append(f"S2: scoped path missing: {p}")
(PLAN / "baseline-scope.json").write_bytes((json.dumps(scope, indent=2) + "\n").encode())
print("baseline-scope.json", len(scope), "paths;", sum(v == "absent" for v in scope.values()), "absent")


def in_scope(p):
    return p in scope or p in SHARED or p.startswith(SCOPE_PREFIXES)


hashes = {
    p: (sha(p) if pathlib.Path(p).exists() else "deleted")
    for p in dirty
    if not in_scope(p) and not secret(p) and p not in foreign
}
(PLAN / "baseline-dirty-hashes.json").write_bytes((json.dumps(hashes, indent=2, sort_keys=True) + "\n").encode())
print("baseline-dirty-hashes.json", len(hashes), "paths outside this scope (foreign excluded)")
for p in sorted(hashes):
    print("  bound by hash", p, hashes[p][:16])
for p in SHARED:
    print("bound by content (read first, own lines only)", p, "dirty" if p in dirty else "clean at HEAD", sha(p)[:16])

# The row-0 content of every existing scoped, read-only, shared and plan file: eol-check.py's
# base and the execution review's delta base.
copied = 0
for p in (*KINDS, *READ_ONLY, *SHARED, *PLAN_FILES):
    if not pathlib.Path(p).is_file():
        continue
    dest = COPIES / p
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(pathlib.Path(p).read_bytes())
    copied += 1
print("baseline-copies", copied, "row-0 copies under", COPIES.as_posix())

# baseline-skip-hashes.json (H1-4): every tracked or untracked, not-ignored file under ui/,
# mcp-server/, tools/, packages/api/ and packages/core/, secret names dropped before any stat.
listed = git("ls-files", "--cached", "--others", "--exclude-standard", *SKIP_ROOTS)
names = [n for n in listed.decode("utf-8").splitlines() if n]
skip_paths = [n for n in names if not secret(n)]
if len(skip_paths) != len(names):
    problems.append(f"H1-4: {len(names) - len(skip_paths)} secret name(s) under the skip roots; H1-4 would see them")
skips = {p: sha(p) for p in skip_paths if pathlib.Path(p).is_file()}
(PLAN / "baseline-skip-hashes.json").write_bytes((json.dumps(skips, indent=2, sort_keys=True) + "\n").encode())
print("baseline-skip-hashes.json", len(skips), "files under", ", ".join(SKIP_ROOTS))

# Line endings, measured with Python bytes.
eols = {}
for p, want in {**KINDS, **READ_ONLY, **SHARED, **PLAN_FILES}.items():
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

# S2: the anchors, each found by its text and counted.
for p, needle, want_n, plan_lines in ANCHORS:
    if needle is None:
        print("absent check", p, "->", sha(p))
        if sha(p) != "absent":
            problems.append(f"S2: {p} already exists")
        continue
    lines = pathlib.Path(p).read_bytes().decode("utf-8").split("\n")
    at = tuple(i + 1 for i, ln in enumerate(lines) if needle in ln)
    plan_txt = list(plan_lines) if plan_lines else "-"
    state = "ok"
    if len(at) != want_n:
        state = "COUNT"
        problems.append(f"S2: anchor {needle!r} in {p}: {len(at)} found at {list(at)}, expected {want_n}")
    elif plan_lines is not None and at != plan_lines:
        state = "moved"
        moved.append(f"{p} :: {needle!r}: plan {list(plan_lines)}, now {list(at)}")
    print("anchor", state, p, "::", repr(needle), "-> count", len(at), "now", list(at), "plan", plan_txt)
register = pathlib.Path(REGISTER).read_bytes().decode("utf-8")
m = re.search(r"^  - id: " + ISSUE + r"\n(?:    .*\n)*?    status: (\S+)", register, re.M)
state = m.group(1) if m else None
at = [i + 1 for i, ln in enumerate(register.split("\n")) if ln == "  - id: " + ISSUE]
print("issue", ISSUE, "status", state, "at", at, "(plan 4374)")
if state != "open" or len(at) != 1:
    problems.append(f"S2: {ISSUE} is {state} with {len(at)} entries, not one open entry")
if at and at != [4374]:
    moved.append(f"{REGISTER} :: {ISSUE}: plan [4374], now {at}")
block = register[m.start():] if m else ""
nxt = re.search(r"^  - id: ", block[5:], re.M)
block = block[: nxt.start() + 5] if nxt else block
lm = re.search(r"^    meu_links:\n((?:      - .*\n)+)", block, re.M)
links = [x.strip()[2:] for x in lm.group(1).splitlines()] if lm else None
print("issue meu_links", links)
if links != ISSUE_LINKS:
    problems.append(f"S2: {ISSUE} meu_links {links}, not {ISSUE_LINKS}")
rows = [
    (i + 1, ln)
    for i, ln in enumerate(pathlib.Path(GROUPING).read_bytes().decode("utf-8").split("\n"))
    if ln.startswith("| 74 |")
]
print("grouping row 74", rows, "(plan 162)")
if [r[1] for r in rows] != [GROUPING_ROW]:
    problems.append("S2: grouping row 74 is not the one proposed row")
elif rows[0][0] != 162:
    moved.append(f"{GROUPING} :: row 74: plan [162], now [{rows[0][0]}]")
# MEU-144 rows, AC-144. and D-1135..D-1144 absent from the registers and the handoffs.
absent_sources = list(ABSENT_REGISTERS) + sorted(
    h.as_posix()
    for h in HANDOFFS.glob("*.md")
    if h.as_posix() != PLAN_REVIEW and not FOREIGN.match(h.as_posix())
)
for p in absent_sources:
    text = pathlib.Path(p).read_bytes().decode("utf-8", errors="replace")
    found = []
    if "AC-144." in text:
        found.append("AC-144.")
    found += [d for d in D_IDS if re.search(re.escape(d) + r"(?![0-9])", text)]
    if found:
        problems.append(f"S2: {p} already names {found}")
print("absent check: AC-144. and", D_IDS[0], "to", D_IDS[-1], "over", len(absent_sources), "register and handoff files")
graphs = [g for g in ("graphify-out", "graphify-out-research") if pathlib.Path(g).exists()]
print("graphify graphs", graphs)
if graphs:
    problems.append(f"S1: a graphify graph exists: {graphs}")
# S8: Session 73's inputs.
for d in S73_DIRS:
    ok = pathlib.Path(d).is_dir()
    print("input dir", d, "exists" if ok else "MISSING")
    if not ok:
        problems.append(f"S8: {d} is missing")
for d in S73_DBS:
    ok = pathlib.Path(d).is_file()
    print("input db", d, "exists" if ok else "MISSING")
    if not ok:
        problems.append(f"S8: {d} is missing")
fp16 = pathlib.Path("C:/Temp/av-kit/s73/models-original") / FP16_REL
got = sha(fp16)
size = fp16.stat().st_size if fp16.is_file() else None
print("input fp16", FP16_REL, got, size)
if got != FP16_SHA or size != FP16_BYTES:
    problems.append(f"S8: models-original FP16 is {got} with {size} bytes, not {FP16_SHA[:12]} with {FP16_BYTES}")
for p, want in INPUT_SHA.items():
    got = sha(p)
    print("input", p, got)
    if got != want:
        problems.append(f"S8: {p} sha256 {got}, not the plan's {want[:12]}")
for p in INPUT_PRESENT:
    got = sha(p)
    print("input (bound at row 0)", p, got)
    if got in ("absent", "not-a-file"):
        problems.append(f"S8: {p} is missing")
for r in RUN_FOLDERS:
    print("run folder", r, "exists (S9 at row 2)" if (OUT / r).exists() else "absent")
for p, want in PLAN_SHA.items():
    got = sha(p)
    print("approved", p, got)
    if got != want:
        problems.append(f"S2: {p} sha256 {got}, not the approved {want}")
print("plan review", PLAN_REVIEW, sha(PLAN_REVIEW))
for p in PLAN_FILES:
    print("plan file", p, sha(p)[:16])
    if not pathlib.Path(p).is_file():
        problems.append(f"row 0: {p} is missing")
for x in moved:
    print("MOVED (record in the handoff):", x)
print("moved anchors", len(moved))
for p in problems:
    print("PROBLEM:", p)
sys.exit(1 if problems else 0)
'@
New-Item -ItemType Directory -Force -Path $receipts | Out-Null
Set-Content -Path "$receipts/baseline-record.py" -Value $record -Encoding utf8
Invoke-Step 'record' @('uv', 'run', '--offline', '--no-sync', 'python', "$receipts/baseline-record.py")

# 3. The host-load wait (host-load.ps1; S15 when it stays above 50 % for 20 minutes).
Invoke-Step 'host-load' @('pwsh', '-NoProfile', '-File', "$plan/host-load.ps1")

# The full Python suite with the D6 argv (.agent/docs/commands.md, py-tests) without -x, so
# every base failure is recorded; the gate excuses only those ids. Not fatal.
& rtk proxy uv run --offline --no-sync pytest tests/ --tb=short -q *> "$receipts/ff-base-py.txt"
$pyCode = $LASTEXITCODE
Write-Output ("base suite py exit={0} receipt={1}/ff-base-py.txt" -f $pyCode, $receipts)
Get-Content "$receipts/ff-base-py.txt" | Select-String -Pattern '^FAILED |^ERROR | in [0-9.]+s' | Select-Object -Last 20

# ruff on adapter.py and the four pin files (s74-plan-ruff-base.txt covered adapter.py and
# test_tts_device_resolution.py only). D-1141: `ruff check` on all five, and `ruff format
# --check` on the files this session edits (adapter.py), are fatal; a pin file's format drift
# is recorded as base, not fatal, because the pins are read-only here and the gate's py-format
# step does not cover them (the first run found test_tts_models.py unformatted, unchanged since
# b216681; 25 files under packages/ and tests/ are unformatted at 174bafa).
$base = @(
    'packages/infrastructure/src/avkit_infra/tts/adapter.py',
    'tests/integration/test_tts_device_resolution.py',
    'tests/integration/test_tts_models.py',
    'tests/integration/test_tts_no_torch.py',
    'tests/e2e/test_api_model_load_keeps.py'
)
& rtk proxy uv run --offline --no-sync ruff format --check @base *> "$receipts/tmp/ff-base-ruff-format.txt"
$fmtCode = $LASTEXITCODE
& rtk proxy uv run --offline --no-sync ruff check @base *> "$receipts/tmp/ff-base-ruff-check.txt"
$chkCode = $LASTEXITCODE
$ruffText = @(
    'ruff format --check (adapter.py and the four pin files):'
    (Get-Content "$receipts/tmp/ff-base-ruff-format.txt")
    ("ruff format exit={0}" -f $fmtCode)
    'ruff check (adapter.py and the four pin files):'
    (Get-Content "$receipts/tmp/ff-base-ruff-check.txt")
    ("ruff check exit={0}" -f $chkCode)
)
& rtk proxy uv run --offline --no-sync ruff format --check $base[0] *> "$receipts/tmp/ff-base-ruff-edited.txt"
$editCode = $LASTEXITCODE
$ruffText += @(
    'ruff format --check (adapter.py, the file this session edits; fatal):'
    (Get-Content "$receipts/tmp/ff-base-ruff-edited.txt")
    ("ruff format adapter.py exit={0}" -f $editCode)
)
Set-Content -Path "$receipts/ff-base-ruff.txt" -Value $ruffText -Encoding utf8
Get-Content "$receipts/ff-base-ruff.txt"
if ($fmtCode -ne 0) { Write-Output 'base-ruff: pin-file format drift recorded as base (D-1141), not fatal' }
Write-Output ("baseline step base-ruff exit={0}" -f ([int]($editCode -ne 0 -or $chkCode -ne 0)))
if ($editCode -ne 0 -or $chkCode -ne 0) { exit 1 }

# 4. The plan-local checkers (Session 82 RULE-1 on the plan folder's Python).
$planPy = @(Get-ChildItem -Path $plan -Filter '*.py' | ForEach-Object { "$plan/$($_.Name)" })
Invoke-Step 'ruff-format-plan' (@('uv', 'run', '--offline', '--no-sync', 'ruff', 'format', '--check') + $planPy)
Invoke-Step 'ruff-check-plan' (@('uv', 'run', '--offline', '--no-sync', 'ruff', 'check') + $planPy)
Invoke-Step 'red-check-selftest' @('uv', 'run', '--offline', '--no-sync', 'python', "$plan/red-check.py", '--selftest')
Invoke-Step 'identity-selftest' @('uv', 'run', '--offline', '--no-sync', 'python', "$plan/identity.py", '--selftest')
Invoke-Step 'eol-check-selftest' @('uv', 'run', '--offline', '--no-sync', 'python', "$plan/eol-check.py", '--selftest')
Invoke-Step 'smoke-check-selftest' @('uv', 'run', '--offline', '--no-sync', 'python', "$plan/smoke-check.py", '--selftest')
Invoke-Step 'home-redact-selftest' @('uv', 'run', '--offline', '--no-sync', 'python', "$plan/home-redact.py", '--selftest')
Invoke-Step 'eol-check-row0' @('uv', 'run', '--offline', '--no-sync', 'python', "$plan/eol-check.py")
Write-Output 'baseline: all steps exit 0'
exit 0
