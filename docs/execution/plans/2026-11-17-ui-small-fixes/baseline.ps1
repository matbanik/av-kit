# UI small fixes baseline (task row 0; implementation-plan.md §Verification Plan 1).
# The shape of docs/execution/plans/2026-11-17-queue-convert-fixes/baseline.ps1 and Session 90's
# 2026-11-17-test-run-reliability/baseline.ps1, with this plan's steps:
# 1. the tree and host state (baseline.sha, baseline-dirty.txt, git worktree list, one host-load
#    sample); HEAD is recorded, never compared with a pinned commit. Session 91's untracked plan
#    folder and plan review (D-1142: Session 91 runs after this one) and the coordinator-owned
#    paths are recorded in baseline-dirty.txt as foreign and left out of this plan's scope checks;
# 2. the path-scoped baseline: baseline-scope.json over §Files Modified and the "Read, never
#    changed" files, with the five new files and the two temporary probe files absent;
#    baseline-dirty-hashes.json, which binds every other dirty path outside this scope by hash;
#    the row-0 copies (eol-check.py's base) and baseline-eol.json; baseline-skip-hashes.json over
#    packages/, mcp-server/, tests/ and tools/ (secret names dropped before any stat or read,
#    Session 83 RULE-2);
# 3. baseline-citations.txt: each anchor of §Verification Plan 1 step 3 found by text, counted
#    once, with its current line (a moved line is recorded; a missing or doubled anchor is S2);
# 4. the S2 binding: MEU-158 and MEU-159 pending, the three issues open (parsed with yaml),
#    grouping §6 row 94 proposed, dev-app-procs.py's sha256 prefix 03053bc97a32, and the plan
#    and task hashes as approved; the re-read of the E2E helpers rows 1a, 1b, 3, 3a and 7 copy or
#    launch through, with their anchors printed; the Playwright ok-line regex self-tested;
# 5. the base Vitest suite (us-base-ui.txt, pwsh in ui/), its failures recorded, not fatal (no
#    Python suite runs in this session: no Python product file changes);
# 6. ruff format --check and ruff check on the plan folder's Python (Session 82 RULE-1), the
#    plan-local selftests, and eol-check.py over the fresh copies.
# Session 90's `uv sync --frozen --all-packages` step is not run: this session touches no Python
# dependency and reaches no network; every Python step runs `uv run --no-sync`.
# Every step except the base suite is fail-fast. Run from the repository root in pwsh.
$ErrorActionPreference = 'Stop'
$root = (git rev-parse --show-toplevel).Trim()
Set-Location $root
$plan = 'docs/execution/plans/2026-11-17-ui-small-fixes'
$receipts = 'C:/Temp/av-kit/ui-small-fixes'
$env:ELECTRON_RUN_AS_NODE = $null
$env:PYTHONIOENCODING = 'utf-8'
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:RECEIPTS_DIR = 'C:/Temp/av-kit'
$tmp = 'C:\Temp\av-kit\ui-small-fixes\tmp'
New-Item -ItemType Directory -Force -Path $tmp | Out-Null
$env:TMP = $tmp
$env:TEMP = $tmp

function Invoke-Step([string]$Id, [string[]]$Argv) {
    & rtk proxy @Argv
    $code = $LASTEXITCODE
    Write-Output ("baseline step {0} exit={1}" -f $Id, $code)
    if ($code -ne 0) { exit $code }
}

# 1-4. Tree state, path-scoped baseline, citations and the S2 binding, in Python so every file
# is read and written as bytes.
$record = @'
import hashlib, importlib.util, json, pathlib, re, subprocess, sys

import yaml

PLAN = pathlib.Path("docs/execution/plans/2026-11-17-ui-small-fixes")
OUT = pathlib.Path("C:/Temp/av-kit/ui-small-fixes")
COPIES = OUT / "baseline-copies"
R = "ui/src/renderer/src"
SHELL_NAV = f"{R}/lib/shell-nav.ts"
CONVERT_CMDS = f"{R}/features/converter/convert-commands.ts"
SETTINGS_CMDS = f"{R}/features/settings/settings-commands.ts"
HELP_CARD = f"{R}/components/help/HelpCard.tsx"
DOWNLOADER = f"{R}/features/downloader/DownloaderPage.tsx"
DEV_MJS = "ui/scripts/electron-vite-dev.mjs"
PKG = "ui/package.json"
DEV_TEST = "ui/tests/unit/dev-script.test.ts"
COMMANDS = ".agent/docs/commands.md"
GUI06 = "docs/build-plan/06-gui.md"
LAYOUT11 = "docs/build-plan/11-page-layout.md"
MEU_STATUS = ".agent/context/meu-status.yaml"
REGISTER = ".agent/context/known-issues.yaml"
GROUPING = ".agent/context/grouping/2026-11-17-value-triage-session-grouping.md"
APP_SHELL = f"{R}/components/layout/AppShell.tsx"
ROUTER = f"{R}/router.tsx"
DISCLOSURE = f"{R}/components/ui/Disclosure.tsx"
CONVERT_PAGE = f"{R}/features/converter/ConvertPage.tsx"
CAPTURE_PAGE = f"{R}/features/capture/CapturePage.tsx"
MAIN_INDEX = "ui/src/main/index.ts"
E2E = "ui/tests/e2e"
APP = f"{E2E}/electron-app.ts"
ENV = f"{E2E}/electron-env.ts"
WATCH = f"{E2E}/main-error-watch.cjs"
BROWSE_MOUNT = f"{E2E}/convert-browse-mount.test.ts"
CONVERT_QUEUE = f"{E2E}/convert-queue.test.ts"
DOWNLOAD_QUEUE = f"{E2E}/download-queue.test.ts"
MATRIX = "docs/build-plan/build-priority-matrix.md"
DEV_APP_PROCS = "docs/execution/plans/2026-11-15-convert-settings-drafts/dev-app-procs.py"
HANDOFFS = ".agent/context/handoffs/2026-11-17-ui-small-fixes"
# §Files Modified, with each file's line-ending kind (implementation-plan.md §Files Modified).
MODIFIED = {
    SHELL_NAV: "LF",
    CONVERT_CMDS: "CRLF",
    SETTINGS_CMDS: "CRLF",
    HELP_CARD: "LF",
    DOWNLOADER: "MIXED",
    DEV_MJS: "LF",
    PKG: "CRLF",
    DEV_TEST: "LF",
    COMMANDS: "CRLF",
    GUI06: "CRLF",
    LAYOUT11: "CRLF",
    MEU_STATUS: "LF",
    ".agent/context/meu-registry.md": "LF",
    "docs/BUILD_PLAN.md": "LF",
    REGISTER: "LF",
    ".agent/context/known-issues.md": "LF",
    GROUPING: "LF",
}
NEW = {
    "ui/scripts/electron-vite-preview.mjs": "LF",
    "ui/tests/unit/help-f1-hold.test.tsx": "LF",
    "ui/tests/unit/preview-script.test.ts": "LF",
    f"{E2E}/help-f1-mount.test.ts": "LF",
    f"{E2E}/downloader-advanced-gap.test.ts": "LF",
}
PROBES = {f"{E2E}/s94-help-probe.test.ts": "LF", f"{E2E}/s94-gap-probe.test.ts": "LF"}
HANDOFF_FILES = (f"{HANDOFFS}-MEU-158-handoff.md", f"{HANDOFFS}-MEU-159-handoff.md", f"{HANDOFFS}-handoff.md")
UNIT = "ui/tests/unit"
# §Project files "Read, never changed": bound by hash; their kind is recorded, and checked where
# the plan names it (implementation-plan.md §Files Modified, Line endings).
READ_ONLY = {
    APP_SHELL: "CRLF",
    ROUTER: "LF",
    DISCLOSURE: "CRLF",
    CONVERT_PAGE: None,
    CAPTURE_PAGE: None,
    MAIN_INDEX: None,
    APP: "LF",
    ENV: None,
    WATCH: None,
    BROWSE_MOUNT: "LF",
    CONVERT_QUEUE: None,
    DOWNLOAD_QUEUE: "LF",
    f"{E2E}/keyboard-shortcuts.test.ts": "LF",
    f"{E2E}/help-search.spec.ts": "LF",
    f"{E2E}/layout-primitives.test.ts": None,
    f"{UNIT}/help-card.test.ts": "CRLF",
    f"{UNIT}/convert-browse-hold.test.ts": "LF",
    f"{UNIT}/convert-page.behavior.test.ts": None,
    f"{UNIT}/convert-page.test.ts": None,
    f"{UNIT}/convert-commands.test.ts": None,
    f"{UNIT}/common-shortcuts.test.tsx": None,
    f"{UNIT}/header-toggles.test.ts": None,
    f"{UNIT}/palette-curation.test.tsx": None,
    f"{UNIT}/gui-actions-audit.test.ts": None,
    f"{UNIT}/shortcuts.test.ts": None,
    f"{UNIT}/capture-page.test.ts": None,
    f"{UNIT}/downloader-page.test.ts": None,
    f"{UNIT}/downloader-page.behavior.test.ts": None,
    f"{UNIT}/layout-canon.test.ts": None,
    f"{UNIT}/layout-primitives.test.ts": None,
    MATRIX: "CRLF",
    DEV_APP_PROCS: "LF",
    "docs/execution/plans/2026-11-17-test-run-reliability/dev-proof.py": None,
    "docs/execution/plans/2026-11-17-test-run-reliability/load-run.py": None,
}
# Shared state files: read first, own lines only; copied for eol-check.py (both CRLF).
SHARED = {"docs/execution/metrics.md": "CRLF", ".agent/context/current-focus.md": "CRLF"}
PLAN_FILES = {
    f"{PLAN.as_posix()}/{n}": "LF"
    for n in (
        "implementation-plan.md", "task.md", "baseline.ps1", "red-check.py", "identity.py",
        "issue-resolve.py", "eol-check.py", "load-run.py", "host-wait.py", "preview-proof.py",
    )
}
# The approved plan and task (the brief's reviewed hashes, re-verified before row 0).
PLAN_SHA = {
    f"{PLAN.as_posix()}/implementation-plan.md": "a91c81f8f652b2436a2c04f2b1a9ebeba50a4fbd801916840994051b3a29a89c",
    f"{PLAN.as_posix()}/task.md": "07a356d2d2cbc0c57ad74f2d1ec6b2c8c9c2ecf705c0ef3cfed13d20feaf8e94",
}
PLAN_REVIEW = f"{HANDOFFS}-plan-critical-review.md"
# §Verification Plan 1 step 3: (file, needle, expected count, the line the plan cites or None).
# Each needle is the defining or unique form of the anchor the plan names; where the plan names
# one anchor on two lines (add-status and error-banner: the message and its placeholder; the two
# lazy routes) each line has its own needle, counted once.
CITATIONS = (
    (APP_SHELL, "const onHelpToggle = () => {", 203),
    (APP_SHELL, "const helpRoutes = [", 206),
    (SETTINGS_CMDS, "export const HELP_EVENTS = {", None),
    (SETTINGS_CMDS, "export const HELP_PENDING_TOGGLE_KEY", None),
    (SETTINGS_CMDS, "export const HELP_COMMANDS = {", None),
    (SETTINGS_CMDS, "queueToggleAfterNavigate: () => {", None),
    (HELP_CARD, "window.addEventListener('av-kit:help:toggle-local', onToggle)", 69),
    (HELP_CARD, "import { HELP_PENDING_TOGGLE_KEY } from", None),
    (CONVERT_CMDS, "let browseRequest: { held: boolean } | null = null", None),
    (CONVERT_CMDS, "export function deliverPaletteBrowse(): void {", None),
    (CONVERT_CMDS, "export function takeHeldBrowse(): boolean {", None),
    (CONVERT_CMDS, "export function isConvertHome(): boolean {", None),
    (CONVERT_PAGE, "if (takeHeldBrowse()) {", None),
    (SHELL_NAV, "export function navigateShell(", 4),
    (ROUTER, "component: lazyRouteComponent(() => import('./features/converter/ConvertPage')", 50),
    (ROUTER, "component: lazyRouteComponent(() => import('./features/capture/CapturePage')", 57),
    (DOWNLOADER, 'id="downloader-add-advanced"', None),
    (DOWNLOADER, '<div className="min-h-6 max-w-[var(--layout-page-max-width)]">', 818),
    (DOWNLOADER, '<p data-testid="add-status" className="text-fg-muted">', None),
    (DOWNLOADER, '<p data-testid="add-status" hidden />', 824),
    (DOWNLOADER, '<p data-testid="error-banner" className="text-error" role="alert">', None),
    (DOWNLOADER, '<p data-testid="error-banner" hidden className="text-error" />', 831),
    (DOWNLOADER, 'data-testid="download-queue-region"', None),
    (DOWNLOADER, "'URL is required'", 355),
    (APP, "export async function launchElectron(", 70),
    (BROWSE_MOUNT, "const CHUNK_DELAY_MS = 1_500", None),
    (BROWSE_MOUNT, "const TEST_TIMEOUT_MS = 240_000", None),
    (BROWSE_MOUNT, "async function launch(label: string)", 125),
    (BROWSE_MOUNT, "protocol.handle('file'", None),
    (BROWSE_MOUNT, "async function requireNotMounted(", 200),
    (BROWSE_MOUNT, "async function switchToLoadingConvert(", 207),
    (CONVERT_QUEUE, "browses on Convert and is inert", 1568),
    (DOWNLOAD_QUEUE, "setViewportSize({ width: 700", 1574),
    (DEV_TEST, "expect(pkg.scripts.preview).toBe('electron-vite preview')", 64),
    (PKG, '"preview": "electron-vite preview"', 18),
    (COMMANDS, "UI-PREVIEW-ELECTRON-RUN-AS-NODE-SILENT", 80),
    (GUI06, '<a id="help-f1-after-mount-residual"></a>', 1710),
    (GUI06, "### F1 help waits for the page (residual)", None),
    (GUI06, "## Validation Commands", 1723),
    (LAYOUT11, '<a id="downloader-advanced-gap-residual"></a>', 176),
    (LAYOUT11, "### Downloader Advanced gap (residual)", None),
    (LAYOUT11, "## Supersession", 190),
    (MATRIX, "| 6.22 | MEU-158 |", None),
    (MATRIX, "| 11.14 | MEU-159 |", None),
    (MAIN_INDEX, "return { width: 1280, height: 800 }", 145),
)
# The re-read of the E2E helpers the new specs copy or launch through (Session 91 edits
# ui/tests/e2e/ in the grouping; D-1142 runs it after this session): their anchors, printed.
HELPER_ANCHORS = (
    (APP, "export async function launchElectron("),
    (APP, "AVKIT_APP_DATA"),
    (APP, "export const DEFAULT_MAIN"),
    (ENV, "export function electronEnv("),
    (ENV, "export function requireScratchAppData("),
    (ENV, "export const MAIN_ERROR_WATCH"),
    (ENV, "export const MAIN_REJECTION_MARKER"),
    (WATCH, "process.on('uncaughtException'"),
    (WATCH, "process.on('unhandledRejection'"),
)
MEUS_PENDING = ("MEU-158", "MEU-159")
ISSUES_OPEN = (
    "HELP-F1-BEFORE-LAZY-MOUNT-LOST",
    "DOWNLOADER-ADVANCED-PANEL-GAP",
    "UI-PREVIEW-ELECTRON-RUN-AS-NODE-SILENT",
)
GROUPING_ROW = "| 94 | `ui-small-fixes` | MEU-158, MEU-159 | P4 | proposed | \u2014 |"
SCOPE_PREFIXES = (
    PLAN.as_posix() + "/",
    HANDOFFS + "-",
    "docs/execution/reflections/2026-11-17-ui-small-fixes-",
)
# Foreign: not this plan's, never touched, left out of this plan's scope checks (brief; D-1142;
# Session 92 RULE-3 for the coordinator-owned paths).
FOREIGN_PREFIXES = (
    "docs/execution/plans/2026-11-17-e2e-pointer-flakes/",
    ".agent/context/handoffs/2026-11-17-e2e-pointer-flakes-",
    ".claude/agents/",
    ".cursor/agents/",
)
FOREIGN_FILES = (".agent/model-registry.local.json",)
SKIP_ROOTS = ("packages", "mcp-server", "tests", "tools")
SECRET_BASES = (".mcp.json", "mcp-token.txt", ".claude.json", ".env")
OK_LINE = re.compile(r"^ +ok +[0-9]+ ")
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


def foreign(name):
    return name.startswith(FOREIGN_PREFIXES) or name in FOREIGN_FILES


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


def lines_of(path):
    return pathlib.Path(path).read_bytes().decode("utf-8").split("\n")


# 1. Tree and host state.
head = git("rev-parse", "HEAD").decode().strip()
(PLAN / "baseline.sha").write_bytes((head + "\n").encode())
print("baseline.sha", head)
origin = subprocess.run(["git", "rev-parse", "origin/main"], capture_output=True).stdout.decode().strip()
print("origin/main as found", origin or "none")
print("git worktree list:")
for ln in git("worktree", "list").decode("utf-8").splitlines():
    print("  " + ln)
spec = importlib.util.spec_from_file_location("load_run", PLAN / "load-run.py")
load_run = importlib.util.module_from_spec(spec)
spec.loader.exec_module(load_run)
print("host-load sample (2 s):", load_run.sample(2.0), "%")
porcelain = git("status", "--porcelain", "--untracked-files=all").decode("utf-8")
dirty = [line[3:].strip().strip('"') for line in porcelain.splitlines() if line.strip()]
foreign_dirty = [p for p in dirty if foreign(p)]
notes = "".join(f"# foreign (not this plan's; never touched, outside its scope checks): {p}\n" for p in foreign_dirty)
(PLAN / "baseline-dirty.txt").write_bytes((porcelain + notes).encode("utf-8"))
print("git status --porcelain --untracked-files=all:")
for ln in porcelain.splitlines():
    print("  " + ln)
print("baseline-dirty.txt", len(dirty), "paths,", len(foreign_dirty), "foreign")
for p in foreign_dirty:
    print("  foreign", p)

# 2. The path-scoped baseline.
KINDS = {**MODIFIED, **NEW, **PROBES}
scope = {p: sha(p) for p in (*KINDS, *READ_ONLY)}
for p in (*NEW, *PROBES):
    if scope[p] != "absent":
        problems.append(f"S2: a new or probe file already exists: {p}")
for p in HANDOFF_FILES:
    if sha(p) != "absent":
        problems.append(f"S2: a handoff already exists: {p}")
for p in (*MODIFIED, *READ_ONLY):
    if scope[p] in ("absent", "not-a-file"):
        problems.append(f"S2: scoped path missing: {p}")
(PLAN / "baseline-scope.json").write_bytes((json.dumps(scope, indent=2) + "\n").encode())
print("baseline-scope.json", len(scope), "paths;", sum(v == "absent" for v in scope.values()), "absent")
for p in (*NEW, *PROBES):
    print("  absent at row 0:", p, scope[p])
procs_sha = scope[DEV_APP_PROCS]
print("dev-app-procs.py", procs_sha[:12])
if not procs_sha.startswith("03053bc97a32"):
    problems.append(f"S2: dev-app-procs.py sha256 {procs_sha[:12]}, not the plan's 03053bc97a32")


def in_scope(p):
    return p in scope or p in SHARED or p.startswith(SCOPE_PREFIXES)


hashes = {
    p: (sha(p) if pathlib.Path(p).exists() else "deleted")
    for p in dirty
    if not in_scope(p) and not secret(p) and not foreign(p)
}
(PLAN / "baseline-dirty-hashes.json").write_bytes((json.dumps(hashes, indent=2, sort_keys=True) + "\n").encode())
print("baseline-dirty-hashes.json", len(hashes), "paths outside this scope (foreign paths left out)")
for p in sorted(hashes):
    print("  bound by hash", p, hashes[p][:16])
for p in SHARED:
    print("bound by content (read first, own lines only)", p, "dirty" if p in dirty else "clean at HEAD", sha(p)[:16])

copied = 0
for p in (*KINDS, *READ_ONLY, *SHARED, *PLAN_FILES):
    if not pathlib.Path(p).is_file():
        continue
    dest = COPIES / p
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(pathlib.Path(p).read_bytes())
    copied += 1
print("baseline-copies", copied, "row-0 copies under", COPIES.as_posix())

listed = git("ls-files", "--cached", "--others", "--exclude-standard", *SKIP_ROOTS)
skip_paths = [n for n in listed.decode("utf-8").splitlines() if n and not secret(n)]
skips = {p: sha(p) for p in skip_paths if pathlib.Path(p).is_file()}
(PLAN / "baseline-skip-hashes.json").write_bytes((json.dumps(skips, indent=2, sort_keys=True) + "\n").encode())
print("baseline-skip-hashes.json", len(skips), "files under packages/, mcp-server/, tests/ and tools/")

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
    if want is not None and kind != want:
        problems.append(f"S2: {p} is {kind}, the plan says {want}")
(PLAN / "baseline-eol.json").write_bytes((json.dumps(eols, indent=2) + "\n").encode())
print("baseline-eol.json", len(eols), "paths")
dl = pathlib.Path(DOWNLOADER).read_bytes().split(b"\n")
for n in (565, 573, 574, 575, 668, 815, 818):
    ending = "CRLF" if dl[n - 1].endswith(b"\r") else "LF"
    print(f"DownloaderPage.tsx:{n} ends {ending}")

# 3. The citation re-read.
cite_lines = []
for p, needle, cited in CITATIONS:
    at = [i + 1 for i, ln in enumerate(lines_of(p)) if needle in ln]
    if len(at) != 1:
        state = "S2"
        problems.append(f"S2: anchor {needle!r} in {p} found {len(at)} times at {at}")
    elif cited is not None and at[0] != cited:
        state = f"moved from :{cited}"
    else:
        state = "as cited" if cited is not None else "found"
    line = f"{p}:{at[0] if at else 0} count {len(at)} ({state}) :: {needle}"
    cite_lines.append(line)
    print("citation", line)
(PLAN / "baseline-citations.txt").write_bytes(("\n".join(cite_lines) + "\n").encode("utf-8"))
print("baseline-citations.txt", len(cite_lines), "anchors")
for p, needle in HELPER_ANCHORS:
    at = [i + 1 for i, ln in enumerate(lines_of(p)) if needle in ln]
    print("helper anchor", p, "::", repr(needle), "->", len(at), "at", at)
    if not at:
        problems.append(f"S2: helper anchor {needle!r} missing in {p}")
bm = lines_of(BROWSE_MOUNT)
print(f"{BROWSE_MOUNT}:27-212 sha256", hashlib.sha256("\n".join(bm[26:212]).encode("utf-8")).hexdigest()[:16])

# 4. The S2 binding.
meus = {m["id"]: m for m in yaml.safe_load(pathlib.Path(MEU_STATUS).read_bytes())["meus"]}
for m in MEUS_PENDING:
    state = meus.get(m, {}).get("status")
    print("meu", m, "status", state)
    if state != "pending":
        problems.append(f"S2: {m} is {state}, not pending")
issues = {i["id"]: i for i in yaml.safe_load(pathlib.Path(REGISTER).read_bytes())["issues"]}
for issue in ISSUES_OPEN:
    state = issues.get(issue, {}).get("status")
    print("issue", issue, "status", state)
    if state != "open":
        problems.append(f"S2: {issue} is {state}, not open")
rows = [ln for ln in lines_of(GROUPING) if ln.startswith("| 94 |")]
print("grouping row 94", rows)
if rows != [GROUPING_ROW]:
    problems.append("S2: grouping row 94 is not the one proposed row")
for ln in lines_of(GROUPING):
    if re.match(r"^\| (74|91|92|93) \|", ln):
        print("grouping row (other session)", ln)
graphs = [g for g in ("graphify-out", "ui/graphify-out") if pathlib.Path(g).exists()]
print("graphify graphs", graphs)
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

# The Playwright ok-line regex on a line numbered below 10 (Session 89 RULE-1).
ok_cases = (
    ("  ok 1 [electron] \u203a tests\\e2e\\x.test.ts:5:1 \u203a AC-158.8 x (2.1s)", True),
    ("  ok 9 [electron] \u203a tests\\e2e\\x.test.ts:5:1 \u203a AC-158.8 x (2.1s)", True),
    ("  ok 12 [electron] \u203a tests\\e2e\\x.test.ts:5:1 \u203a AC-158.8 x (2.1s)", True),
    ("  x  3 [electron] \u203a tests\\e2e\\x.test.ts:5:1 \u203a AC-158.8 x (2.1s)", False),
    ("ok 1 no indent", False),
)
for text, want in ok_cases:
    got = bool(OK_LINE.match(text))
    print(f"ok-line regex on {text[:8]!r}: {got} (expected {want})")
    if got != want:
        problems.append(f"ok-line regex wrong on {text!r}")

for p in problems:
    print("PROBLEM:", p)
print(f"baseline record: {len(problems)} problem(s)")
sys.exit(1 if problems else 0)
'@
New-Item -ItemType Directory -Force -Path $receipts | Out-Null
Set-Content -Path "$receipts/baseline-record.py" -Value $record -Encoding utf8
Invoke-Step 'record' @('uv', 'run', '--no-sync', 'python', "$receipts/baseline-record.py")

# 5. The base Vitest suite from pwsh in ui/ (memory: vitest-from-pwsh-not-bash); the gate's
# ui-tests excuse list reads it. Its failures are recorded, not fatal.
Push-Location 'P:\av-kit\ui'
& rtk proxy npm run test *> "$receipts/us-base-ui.txt"
$uiCode = $LASTEXITCODE
Pop-Location
Set-Content -Path "$receipts/us-base-ui.txt.exit" -Value $uiCode -Encoding ascii
Write-Output ("base suite ui exit={0} receipt={1}/us-base-ui.txt" -f $uiCode, $receipts)
Get-Content "$receipts/us-base-ui.txt" | Select-String -Pattern 'Test Files|Tests |FAIL ' | Select-Object -Last 12

# 6. The plan-local checkers (Session 82 RULE-1 on the plan folder's Python).
$planPy = @(Get-ChildItem -Path $plan -Filter '*.py' | ForEach-Object { "$plan/$($_.Name)" })
Invoke-Step 'ruff-format-plan' (@('uv', 'run', '--no-sync', 'ruff', 'format', '--check') + $planPy)
Invoke-Step 'ruff-check-plan' (@('uv', 'run', '--no-sync', 'ruff', 'check') + $planPy)
Invoke-Step 'red-check-selftest' @('uv', 'run', '--no-sync', 'python', "$plan/red-check.py", '--selftest')
Invoke-Step 'identity-selftest' @('uv', 'run', '--no-sync', 'python', "$plan/identity.py", '--selftest')
Invoke-Step 'eol-check-selftest' @('uv', 'run', '--no-sync', 'python', "$plan/eol-check.py", '--selftest')
Invoke-Step 'host-wait-selftest' @('uv', 'run', '--no-sync', 'python', "$plan/host-wait.py", '--selftest')
Invoke-Step 'preview-proof-selftest' @('uv', 'run', '--no-sync', 'python', "$plan/preview-proof.py", '--selftest')
Invoke-Step 'eol-check-row0' @('uv', 'run', '--no-sync', 'python', "$plan/eol-check.py")
Write-Output 'baseline: all steps exit 0'
exit 0
