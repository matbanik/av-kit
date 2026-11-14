# Session 71b baseline (task row 0; implementation-plan.md §Verification Plan 1).
# First proves that the plan's Status line records Mat's words to execute and that D-757 carries
# them (S9; the review loops have no token budget, so none is quoted), that the queue is right
# (S8: MEU-87, MEU-99, MEU-100 and MEU-105 approved, MEU-143, MEU-106 and MEU-107 pending,
# 42f02bc an ancestor of HEAD), and that the shapes this plan calls are present by name, with
# this plan's own names and files still absent (S7). Then records HEAD and the dirty tree with
# each dirty path's SHA-256, records every Files Modified target's line endings and SHA-256 in
# s71b-anchors.txt, installs Python from the lock without the network, proves ui/ and
# mcp-server/node_modules match their locks, asserts the pinned FFmpeg pair that the suite's
# real-FFmpeg modules run (S4), captures the base Python, UI, MCP and capture Electron runs and
# ruff, and runs the plan-local selftests. A copy of Session 71's with the checks changed for
# this plan. The base runs' own failures are recorded, not fatal: the session gate excuses only
# the Python ids the base receipt shows failing, and nothing else. Every other step is
# fail-fast. Run from the repository root with PowerShell 7 (pwsh -NoProfile -File).
#
# docs/proposals/2026-11-10-download-logic-divergence-report.md is hashed, never opened or printed.
# No step reads user data: the capture inbox, its sidecars, the app database or the settings file.
#
# `npm --prefix ui ci` and `npm --prefix mcp-server ci` are not run (Session 50's reason, still
# true on 2026-11-14): the avkit MCP servers that Claude sessions use run as
# `ui/node_modules/electron/dist/electron.exe mcp-server/dist/index.js` and `node
# mcp-server/dist/index.js`, so deleting either node_modules would fail on the locked binary or
# break them. The lock-sync step proves each installed tree is the locked one instead, and stops
# if it isn't.
$ErrorActionPreference = 'Stop'
$root = (git rev-parse --show-toplevel).Trim()
Set-Location $root
$plan = 'docs/execution/plans/2026-11-14-capture-tool-flow'
$receipts = 'C:/Temp/av-kit'
$env:ELECTRON_RUN_AS_NODE = $null
$env:PYTHONIOENCODING = 'utf-8'
# RC1 ECN-2 (CLOSEOUT-SELFTEST-ANCESTOR-AGENT-DIR): keep pytest's temp dirs away from the home folder.
$tmp = 'C:\Temp\av-kit\s71b\tmp'
New-Item -ItemType Directory -Force -Path $tmp | Out-Null
$env:TMP = $tmp
$env:TEMP = $tmp

function Invoke-Step([string]$Id, [string[]]$Argv) {
    & rtk proxy @Argv
    $code = $LASTEXITCODE
    Write-Output ("baseline step {0} exit={1}" -f $Id, $code)
    if ($code -ne 0) { exit $code }
}

# S9: the rows run only on Mat's words at the plan gate. The header's Status line must quote his
# word to execute as USER_EXPLICIT with a date and a quote, and D-757 must carry the same ruling.
$ruled = @'
import pathlib, re, sys
text = pathlib.Path(sys.argv[1], "implementation-plan.md").read_text(encoding="utf-8")
status = [ln for ln in text.splitlines() if ln.startswith("> **Status:**")]
line = status[0] if len(status) == 1 else ""
execute = re.search(r"said to execute \(USER_EXPLICIT 2026-\d\d-\d\d '[^']+'\)", line)
start = text.find("  - id: D-757\n")
end = text.find("```", start)
d757 = text[start:end] if 0 <= start < end else ""
ref = re.search(r"human_message_reference: \"(USER_EXPLICIT 2026-\d\d-\d\d '[^']+')\"", d757)
ruled = "resolution: human" in d757 and ref is not None
same = bool(execute and ref and ref.group(1) in execute.group(0))
print(f"status lines: {len(status)}")
print(f"execute: {execute.group(0) if execute else None}")
print(f"D-757 ruled by Mat: {ruled}; the same words as the Status line: {same}")
ok = bool(line and execute and ruled and same)
if not ok:
    print("the Status line lacks Mat's word to execute, or D-757 lacks the same ruling (S9); the rows can't run")
sys.exit(0 if ok else 1)
'@
Invoke-Step 'rulings' @('uv', 'run', '--no-sync', 'python', '-c', $ruled, $plan)

# S8: the contract dependencies (MEU-87's lock, MEU-99's undo, MEU-100's toolbar, MEU-105's style
# store) approved, MEU-143 and the two after it pending, and Session 71's commit an ancestor of
# HEAD.
$queue = @'
import pathlib, subprocess, sys
lines = pathlib.Path(".agent/context/meu-status.yaml").read_text(encoding="utf-8").splitlines()
def status(meu):
    for n, line in enumerate(lines):
        if line.strip() == f"id: {meu}":
            for follow in lines[n + 1 : n + 40]:
                if follow.strip().startswith("status:"):
                    return follow.split(":", 1)[1].strip().strip("'\"")
            return None
    return None
want = {"MEU-87": "approved", "MEU-99": "approved", "MEU-100": "approved", "MEU-105": "approved", "MEU-143": "pending", "MEU-106": "pending", "MEU-107": "pending"}
have = {meu: status(meu) for meu in want}
print(f"queue: {have}")
s71 = subprocess.run(["git", "merge-base", "--is-ancestor", "42f02bc", "HEAD"], capture_output=True).returncode
print(f"42f02bc is an ancestor of HEAD: {s71 == 0}")
sys.exit(0 if have == want and s71 == 0 else 1)
'@
Invoke-Step 'queue-order' @('uv', 'run', '--no-sync', 'python', '-c', $queue)

# S7: the names this plan calls, by name, and the names and files it adds, still absent. A shape
# that differs in signature is found when row 1 re-reads its anchors. A row's last field is the
# number of lines it must match.
$shapes = @'
import pathlib, re, sys
CORE = "packages/core/src/avkit_core"
API = "packages/api/src/avkit_api"
UI = "ui/src/renderer/src/features/capture"
REG = "ui/src/renderer/src/registry"
SERVICE = f"{CORE}/services/settings.py"
SCHEMA = f"{API}/schemas/settings.py"
MCP = "mcp-server/src/toolsets/settings.ts"
PUT = "ui/src/renderer/src/features/settings/settings-schemas.ts"
STORE = f"{UI}/capture-style-store.ts"
STYLE = f"{UI}/capture-tool-style.ts"
CROPBAR = f"{UI}/CaptureCropBar.tsx"
CROP = f"{UI}/capture-crop.ts"
TRANSFORM = f"{UI}/capture-transform.ts"
IMPORT = f"{UI}/capture-import.ts"
BUTTON = f"{UI}/ToolbarIconButton.tsx"
VIEWPORT = f"{UI}/CaptureViewport.tsx"
PAGE = f"{UI}/CapturePage.tsx"
HELP = f"{UI}/capture-help-content.ts"
SHORTCUTS = f"{REG}/shortcuts.ts"
REGISTRY = f"{REG}/commandRegistry.ts"
IDS = "ui/tests/e2e/test-ids.ts"
INDEX = "docs/build-plan/gui-actions-index.md"
SPEC = "docs/build-plan/09-screenshot-capture.md"
present = (
    (SERVICE, r"^class SettingSpec:$", "SettingSpec", 1),
    (SERVICE, r'^    \("capture", "pixelate_block_size"\): SettingSpec\($', "the pixelate_block_size row", 1),
    (SERVICE, r"^def _encode\(spec: SettingSpec, key: str, value: object\) -> str:$", "_encode", 1),
    (SERVICE, r"^        if not isinstance\(value, bool\):$", "_encode's boolean branch", 1),
    (SERVICE, r"^def _decode\(spec: SettingSpec, stored: str\) -> object:$", "_decode", 1),
    (SERVICE, r'^        return stored == "true"$', "_decode's boolean read", 1),
    (SCHEMA, r"^class SettingsPutIn\(ApiModel\):$", "SettingsPutIn", 1),
    (SCHEMA, r"^    pixelate_block_size: StrictInt \| None = None$", "SettingsPutIn.pixelate_block_size", 1),
    (MCP, r"^export const SETTINGS_SCHEMA: \{$", "SETTINGS_SCHEMA", 1),
    (MCP, r'^      pixelate_block_size: \{ type: "number", default: 10 \},$', "SETTINGS_SCHEMA's pixelate_block_size", 1),
    (MCP, r"^const settingsLeaves = \{$", "settingsLeaves", 1),
    (MCP, r"^  pixelate_block_size: z\.number\(\)\.int\(\)\.optional\(\),$", "settingsLeaves' pixelate_block_size", 1),
    (PUT, r"^export const capturePutSchema = z$", "capturePutSchema", 1),
    (PUT, r"^export const captureStylePutSchema = z$", "captureStylePutSchema", 1),
    (STORE, r"^type LeafEntry = \{ value: string \| number; commit: number; succeededAt: number \| null \}$", "LeafEntry", 1),
    (STORE, r"^export async function fetchCaptureSettings\(\): Promise<CapturePut> \{$", "fetchCaptureSettings", 1),
    (STORE, r"^export function resetCaptureStyleStore\(\): void \{$", "resetCaptureStyleStore", 1),
    (STORE, r"^export function styleSaveFailures\(\): number \{$", "styleSaveFailures", 1),
    (STORE, r"^export function committedStyleLeaves\(\)", "committedStyleLeaves", 1),
    (STORE, r"^export function saveCaptureToolStyle\(client: QueryClient, tool: StyleTool, patch: ToolStyle\): void \{$", "saveCaptureToolStyle", 1),
    (STYLE, r"^export const TOOL_STYLE_LEAVES: ", "TOOL_STYLE_LEAVES", 1),
    (SHORTCUTS, r"^export const PAGE_PRIMARY_CONTROL: Record<ShellPage, string \| null> = \{$", "PAGE_PRIMARY_CONTROL", 1),
    (SHORTCUTS, r"^export const BOUND_CONTROLS: ReadonlyArray<\{ testid: string; commandId: string \}> = \[$", "BOUND_CONTROLS", 1),
    (SHORTCUTS, r"^export function chordFromEvent\(event: KeyboardEvent\): string \| null \{$", "chordFromEvent", 1),
    (SHORTCUTS, r"The focused element is ignored", "the handler's focus comment", 1),
    (SHORTCUTS, r"^export function createShortcutHandler\(options: ShortcutHandlerOptions\): \(event: KeyboardEvent\) => boolean \{$", "createShortcutHandler", 1),
    (REGISTRY, r"^export const CAPTURE_PALETTE_IDS = \[$", "CAPTURE_PALETTE_IDS", 1),
    (REGISTRY, r"^export const SHORTCUT_ONLY_IDS = \['page:primary'\] as const$", "SHORTCUT_ONLY_IDS", 1),
    (REGISTRY, r"^    id: 'capture:open_folder',$", "the capture:open_folder entry", 1),
    (REGISTRY, r"^export function isRegistryChord\(event: KeyboardEvent\): boolean \{$", "isRegistryChord", 1),
    (PAGE, r"^const KEYBOARD_NUDGE_PX = 1$", "KEYBOARD_NUDGE_PX", 1),
    (PAGE, r"^const CROP_NUDGE_SHIFT_PX = 10$", "CROP_NUDGE_SHIFT_PX", 1),
    (PAGE, r"^function createDrawnMark\($", "createDrawnMark", 1),
    (PAGE, r"^  const \[toolLocked, setToolLocked\] = useState\(false\)$", "the lock state", 1),
    (PAGE, r"^  function chooseTool\(next: CaptureTool\): void \{$", "chooseTool", 1),
    (PAGE, r"^  function commitSelection\(index: number, list: Annotation\[\], nextTool: CaptureTool = 'select'\): void \{$", "commitSelection", 1),
    (PAGE, r"hitTestMarks\(\{$", "the three hit tests", 3),
    (PAGE, r"^\s+if \(!toolLocked\) \{$", "the two lock sites", 2),
    (PAGE, r"^  function handleEditorKey\(event: KeyboardEvent\): void \{$", "handleEditorKey", 1),
    (PAGE, r"window\.addEventListener\('keydown', onKeyDown\)", "the page's window key listener", 1),
    (VIEWPORT, r"^export type SurfacePointer = \{$", "SurfacePointer", 1),
    (VIEWPORT, r"^  shiftKey: boolean$", "SurfacePointer.shiftKey", 1),
    (VIEWPORT, r"^const handledViewKeys = new WeakSet<Event>\(\)$", "handledViewKeys", 1),
    (VIEWPORT, r"CAPTURE_CHORD_BUBBLE", "the chord-bubble comment", 1),
    (VIEWPORT, r'^\s+id="capture-tool-lock"$', "the lock button", 1),
    (CROPBAR, r"^const FIELD_STEP_SHIFT = 10$", "FIELD_STEP_SHIFT (not exported)", 1),
    (CROP, r"^export function ratioBox\(s: number, r: number\): CropSize \{$", "ratioBox", 1),
    (TRANSFORM, r"^export function isBoxMark\(mark: Annotation\): mark is BoxMark \{$", "isBoxMark", 1),
    (TRANSFORM, r"^export function resizeBox<T extends BoxMark>\(", "resizeBox", 1),
    (IMPORT, r"^export function isEditableTarget\(target: EventTarget \| null\): boolean \{$", "isEditableTarget", 1),
    (BUTTON, r"^  shortcut\?: string$", "ToolbarIconButton's shortcut", 1),
    (HELP, r"The lock button keeps the current tool after each mark\.", "the lock help sentence", 1),
    (HELP, r"Arrow keys nudge the selected mark, or the arrow end you grabbed or tabbed to\.", "the nudge help sentence", 1),
    (INDEX, r"^\| `capture:tool_lock` \| Keep tool after drawing \(tool lock\) \|", "capture:tool_lock", 1),
    (IDS, r"^// MEU-51 primitive harness IDs\.", "the AC-51.6 hash boundary", 1),
    (IDS, r"^// MEU-105 Capture style \(additive IDs\)\.$", "the MEU-105 test-id block", 1),
    (SPEC, r'^<a id="style-and-tool-flow"></a>$', "09 §Style and tool flow", 1),
    (SPEC, r"^> \*\*Delivered \(Session 71\)\.\*\*", "09's Session 71 Delivered note", 1),
)
# This plan's names, keys, labels and files, absent from every file it writes. `capture:tool_lock`
# is the existing index row, so the leaf is matched only where it isn't that id.
absent_files = (
    SERVICE, SCHEMA, MCP, PUT, STORE, STYLE, CROPBAR, IMPORT, VIEWPORT, PAGE, HELP, SHORTCUTS,
    REGISTRY, IDS, INDEX, SPEC, "openapi.committed.json", "mcp-server/tests/capture.test.ts",
    "tests/unit/test_capture_service.py", "ui/tests/e2e/capture-inbox.test.ts",
    "ui/tests/unit/capture-page.behavior.test.ts", "ui/tests/unit/capture-help-content.test.ts",
    ".agent/context/meu-status.yaml",
    ".agent/context/grouping/2026-10-29-capture-annotation-editor-session-grouping.md",
)
absent = re.compile(
    r"(?<!capture:)\btool_lock\b|readToolLock|saveCaptureToolLock|lockSaveFailures|"
    r"useCaptureToolLock|captureLockPutSchema|TOOL_LETTERS|CAPTURE_TOOL_IDS|handledEditorKeys|"
    r"drawBounds|snapArrowEnd|keepRatioResize|altKey: boolean|capture:tool_select|capture:tool_crop|"
    r"capture:draw_modifiers|Couldn't save the tool lock|AC-143\.|Delivered \(Session 71b\)"
)
new_files = (
    f"{UI}/capture-tool-lock.ts",
    f"{UI}/useCaptureToolLock.ts",
    f"{UI}/capture-modifiers.ts",
    "ui/src/renderer/src/lib/editable-target.ts",
    "tests/unit/test_capture_tool_lock.py",
    "tests/e2e/test_api_capture_tool_lock.py",
    "ui/tests/unit/capture-tool-lock.test.ts",
    "ui/tests/unit/capture-tool-flow.behavior.test.ts",
)
wrong = []
for rel, pattern, label, count in present:
    text = pathlib.Path(rel).read_text(encoding="utf-8")
    hits = [n for n, ln in enumerate(text.splitlines(), 1) if re.search(pattern, ln)]
    print(f"present {label}: {rel} lines {hits[:5]}")
    if len(hits) != count:
        wrong.append(f"{label}: {len(hits)} match(es), want {count}")
for rel in absent_files:
    text = pathlib.Path(rel).read_text(encoding="utf-8")
    hits = [n for n, ln in enumerate(text.splitlines(), 1) if absent.search(ln)]
    print(f"absent names and labels: {rel} lines {hits[:5]}")
    if hits:
        wrong.append(f"already present in {rel}")
for rel in new_files:
    exists = pathlib.Path(rel).exists()
    print(f"absent new file {rel}: exists={exists}")
    if exists:
        wrong.append(f"new file already present {rel}")
print("shapes wrong (S7):", wrong)
sys.exit(1 if wrong else 0)
'@
Invoke-Step 'shapes' @('uv', 'run', '--no-sync', 'python', '-c', $shapes)

$head = (git rev-parse HEAD).Trim()
Set-Content -Path "$plan/baseline.sha" -Value $head -NoNewline
# Each line is the porcelain line, a tab, then the path's SHA-256 (`deleted` when it is gone).
# The session gate reads the path as the text between column 3 and the tab.
$dirty = @'
import hashlib, pathlib, subprocess, sys
out = subprocess.run(["git", "status", "--porcelain", "--untracked-files=all"], capture_output=True, check=True).stdout.decode("utf-8")
lines = []
for line in out.splitlines():
    path = pathlib.Path(line[3:])
    digest = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else "deleted"
    lines.append(f"{line}\t{digest}")
pathlib.Path(sys.argv[1]).write_bytes(("\n".join(lines) + "\n").encode("utf-8"))
print(f"baseline-dirty.txt {len(lines)} paths")
'@
Invoke-Step 'baseline-dirty' @('uv', 'run', '--no-sync', 'python', '-c', $dirty, "$plan/baseline-dirty.txt")
Write-Output "baseline.sha $head"

# Every Files Modified target's line endings and SHA-256, which each row reads before it writes.
# A new file is recorded as absent; an existing target that is missing stops here. A MIXED file
# keeps each line's own ending (S63 RULE-3). Rows 5 and 6 and H2 byte-edit the actions index, 09,
# meu-status, the build plan, the registry and the grouping. The divergence report is hashed only.
$anchors = @'
import hashlib, pathlib, sys
UI = "ui/src/renderer/src/features/capture"
REG = "ui/src/renderer/src/registry"
targets = (
    "packages/core/src/avkit_core/services/settings.py",
    "packages/api/src/avkit_api/schemas/settings.py",
    "openapi.committed.json",
    "mcp-server/src/toolsets/settings.ts",
    "ui/src/renderer/src/features/settings/settings-schemas.ts",
    f"{UI}/capture-style-store.ts",
    f"{UI}/capture-toolbar.ts",
    f"{UI}/CaptureCropBar.tsx",
    f"{UI}/capture-crop.ts",
    f"{UI}/capture-transform.ts",
    f"{UI}/capture-import.ts",
    f"{UI}/ToolbarIconButton.tsx",
    f"{UI}/CaptureViewport.tsx",
    f"{UI}/CapturePage.tsx",
    f"{UI}/capture-help-content.ts",
    f"{REG}/shortcuts.ts",
    f"{REG}/commandRegistry.ts",
    "ui/tests/e2e/test-ids.ts",
    "ui/tests/unit/capture-page.behavior.test.ts",
    "ui/tests/unit/capture-action-row.test.ts",
    "ui/tests/unit/capture-help-content.test.ts",
    "ui/tests/unit/capture-toolbar.test.ts",
    "ui/tests/unit/capture-page.test.ts",
    "ui/tests/unit/capture-redact.behavior.test.ts",
    "ui/tests/unit/capture-crop-tool.behavior.test.ts",
    "tests/unit/test_capture_style_settings.py",
    "ui/tests/unit/capture-text-lines.behavior.test.ts",
    "ui/tests/unit/capture-style-flow.behavior.test.ts",
    "ui/tests/unit/capture-copy-image.behavior.test.ts",
    "ui/tests/unit/capture-filmstrip-actions.behavior.test.ts",
    "ui/tests/unit/capture-import.behavior.test.ts",
    "ui/tests/e2e/capture-filmstrip-actions.test.ts",
    "ui/tests/e2e/capture-import.test.ts",
    "ui/tests/e2e/capture-picker.test.ts",
    "ui/tests/unit/command-palette.test.ts",
    "ui/tests/unit/gui-actions-audit.test.ts",
    "ui/tests/unit/icon-hints.test.ts",
    "ui/tests/unit/common-shortcuts.test.tsx",
    "tests/unit/test_capture_service.py",
    "mcp-server/tests/capture.test.ts",
    "ui/tests/e2e/capture-inbox.test.ts",
    "docs/build-plan/gui-actions-index.md",
    "docs/build-plan/09-screenshot-capture.md",
    ".agent/context/meu-status.yaml",
    "docs/BUILD_PLAN.md",
    ".agent/context/meu-registry.md",
    ".agent/context/grouping/2026-10-29-capture-annotation-editor-session-grouping.md",
    "docs/execution/metrics.md",
    ".agent/context/current-focus.md",
)
new = (
    f"{UI}/capture-tool-lock.ts",
    f"{UI}/useCaptureToolLock.ts",
    f"{UI}/capture-modifiers.ts",
    "ui/src/renderer/src/lib/editable-target.ts",
    "tests/unit/test_capture_tool_lock.py",
    "tests/e2e/test_api_capture_tool_lock.py",
    "ui/tests/unit/capture-tool-lock.test.ts",
    "ui/tests/unit/capture-tool-flow.behavior.test.ts",
)
hashed_only = ("docs/proposals/2026-11-10-download-logic-divergence-report.md",)
out, missing, present = [], [], []
for rel in targets:
    p = pathlib.Path(rel)
    if not p.is_file():
        missing.append(rel)
        continue
    data = p.read_bytes()
    crlf = data.count(b"\r\n")
    lf = data.count(b"\n") - crlf
    kind = "CRLF" if crlf and not lf else "LF" if lf and not crlf else f"MIXED crlf={crlf} lf={lf}"
    out.append(f"{hashlib.sha256(data).hexdigest()} {len(data):>9} {kind:<6} {rel}")
for rel in hashed_only:
    p = pathlib.Path(rel)
    digest = hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else "absent"
    out.append(f"{digest} hashed-only {rel}")
for rel in new:
    exists = pathlib.Path(rel).exists()
    out.append(f"{'present' if exists else 'absent'} new {rel}")
    if exists:
        present.append(rel)
pathlib.Path(sys.argv[1]).write_text("\n".join(out) + "\n", encoding="utf-8")
print("\n".join(out))
print("missing targets:", missing, "new files already present:", present)
sys.exit(1 if missing or present else 0)
'@
Invoke-Step 'anchors' @('uv', 'run', '--no-sync', 'python', '-c', $anchors, "$receipts/s71b-anchors.txt")

# --offline: this step can't fetch a package.
Invoke-Step 'uv-sync' @('uv', 'sync', '--frozen', '--offline', '--all-packages')

$lockSync = @'
import json, pathlib, sys
pkg = sys.argv[1]
lock = json.loads(pathlib.Path(pkg, "package-lock.json").read_text(encoding="utf-8"))["packages"]
want = {k: v.get("version") for k, v in lock.items() if k.startswith("node_modules/") and not v.get("optional")}
missing = sorted(k for k in want if not pathlib.Path(pkg, k, "package.json").exists())
have = {k: json.loads(pathlib.Path(pkg, k, "package.json").read_text(encoding="utf-8")).get("version") for k in want if k not in missing}
bad = sorted(k for k in have if have[k] != want[k])
for k in bad[:20]: print("version differs", k, want[k], have[k])
for k in missing[:20]: print("missing", k)
print(f"{pkg} lock sync: {len(want)} locked packages, {len(bad)} differ, {len(missing)} missing")
sys.exit(1 if bad or missing else 0)
'@
Invoke-Step 'ui-lock-sync' @('uv', 'run', '--no-sync', 'python', '-c', $lockSync, 'ui')
Invoke-Step 'mcp-lock-sync' @('uv', 'run', '--no-sync', 'python', '-c', $lockSync, 'mcp-server')

# S4: the suite's real-FFmpeg modules (Sessions 54, 62 and 67) run this pair; a missing or
# truncated binary stops here. This session adds no real-FFmpeg module.
foreach ($name in @('ffmpeg.exe', 'ffprobe.exe')) {
    $exe = Join-Path $root "packaging/ffmpeg-win64/$name"
    if (-not (Test-Path -LiteralPath $exe -PathType Leaf)) {
        Write-Output "baseline step ffmpeg-pair exit=1 ($name is missing; S4)"
        exit 1
    }
    $size = (Get-Item -LiteralPath $exe).Length
    if ($size -le 1024) {
        Write-Output ("baseline step ffmpeg-pair exit=1 ({0} is {1} B; S4)" -f $name, $size)
        exit 1
    }
    $versionText = @(& $exe -version)
    $versionExit = $LASTEXITCODE
    $first = $versionText | Select-Object -First 1
    if ($versionExit -ne 0) {
        Write-Output ("baseline step ffmpeg-pair exit=1 ({0} -version exit={1}; S4)" -f $name, $versionExit)
        exit 1
    }
    Write-Output ("{0} {1} B: {2}" -f $name, $size, $first)
}
Write-Output 'baseline step ffmpeg-pair exit=0'

& rtk proxy uv run --no-sync pytest tests/ --tb=short -q -rfE > "$receipts/s71b-base-py.txt" 2>&1
Write-Output ("base suite py exit={0} receipt={1}/s71b-base-py.txt" -f $LASTEXITCODE, $receipts)
Get-Content "$receipts/s71b-base-py.txt" | Select-String -Pattern '^FAILED |^ERROR |passed|failed' | Select-Object -Last 12

& rtk proxy npm --prefix ui run test > "$receipts/s71b-base-ui.txt" 2>&1
Write-Output ("base suite ui exit={0} receipt={1}/s71b-base-ui.txt" -f $LASTEXITCODE, $receipts)
Get-Content "$receipts/s71b-base-ui.txt" | Select-String -Pattern ' FAIL |Test Files|Tests ' | Select-Object -Last 12

& rtk proxy npm --prefix mcp-server run build > "$receipts/s71b-base-mcp-build.txt" 2>&1
Write-Output ("base mcp build exit={0} receipt={1}/s71b-base-mcp-build.txt" -f $LASTEXITCODE, $receipts)
& rtk proxy npm --prefix mcp-server run test > "$receipts/s71b-base-mcp.txt" 2>&1
Write-Output ("base suite mcp exit={0} receipt={1}/s71b-base-mcp.txt" -f $LASTEXITCODE, $receipts)
Get-Content "$receipts/s71b-base-mcp.txt" | Select-String -Pattern ' FAIL |Test Files|Tests ' | Select-Object -Last 12

# The capture Electron spec the gate runs, on a fresh build, so its base count is on record.
& rtk proxy npm --prefix ui run build > "$receipts/s71b-base-ui-build.txt" 2>&1
Write-Output ("base ui build exit={0} receipt={1}/s71b-base-ui-build.txt" -f $LASTEXITCODE, $receipts)
& rtk proxy npm --prefix ui run test:e2e -- tests/e2e/capture-inbox.test.ts > "$receipts/s71b-base-e2e.txt" 2>&1
Write-Output ("base capture e2e exit={0} receipt={1}/s71b-base-e2e.txt" -f $LASTEXITCODE, $receipts)
Get-Content "$receipts/s71b-base-e2e.txt" | Select-String -Pattern '^\s+\d+ (passed|failed|skipped|flaky)' | Select-Object -Last 6

& rtk proxy uv run --no-sync ruff check packages/ tests/ > "$receipts/s71b-base-ruff.txt" 2>&1
Write-Output ("base ruff exit={0} receipt={1}/s71b-base-ruff.txt" -f $LASTEXITCODE, $receipts)
Get-Content "$receipts/s71b-base-ruff.txt" -Tail 5

Invoke-Step 'red-check-selftest' @('uv', 'run', '--no-sync', 'python', "$plan/red-check.py", '--selftest')
Invoke-Step 'identity-selftest' @('uv', 'run', '--no-sync', 'python', "$plan/identity.py", '--selftest')
Invoke-Step 'id-length-selftest' @('uv', 'run', '--no-sync', 'python', "$plan/id-length.py", '--selftest')
Write-Output 'baseline: all steps exit 0'
exit 0
