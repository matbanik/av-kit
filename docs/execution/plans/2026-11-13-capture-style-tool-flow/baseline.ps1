# Session 71 baseline (task row 0; implementation-plan.md §Verification Plan 1).
# First proves that the plan's Status line records Mat's execution budget and his words to
# execute (S9) and that D-713 carries his split ruling, that the queue is right (S8: MEU-87,
# MEU-99 and MEU-100 approved, MEU-105 and MEU-106 pending, no MEU-143 entry yet, 5e9ea7c an
# ancestor of HEAD), and that the shapes this plan calls are present by name, with this plan's
# own names and files still absent (S7). Then records HEAD and the dirty tree with each dirty
# path's SHA-256, records every Files Modified target's line endings and SHA-256 in
# s71-anchors.txt, installs Python from the lock without the network, proves ui/ and
# mcp-server/node_modules match their locks, asserts the pinned FFmpeg pair that the suite's
# real-FFmpeg modules run (S4), captures the base Python, UI, MCP and capture Electron runs and
# ruff, and runs the plan-local selftests. A copy of Session 70's with the checks changed for
# this plan. The base runs' own failures are recorded, not fatal: the session gate excuses only
# the Python ids the base receipt shows failing, and nothing else. Every other step is
# fail-fast. Run from the repository root with PowerShell 7 (pwsh -NoProfile -File).
#
# docs/proposals/2026-11-10-download-logic-divergence-report.md is hashed, never opened or printed.
# No step reads user data: the capture inbox, its sidecars, the app database or the settings file.
#
# `npm --prefix ui ci` and `npm --prefix mcp-server ci` are not run (Session 50's reason, still
# true on 2026-11-13): the avkit MCP servers that Claude sessions use run as
# `ui/node_modules/electron/dist/electron.exe mcp-server/dist/index.js` and `node
# mcp-server/dist/index.js`, so deleting either node_modules would fail on the locked binary or
# break them. The lock-sync step proves each installed tree is the locked one instead, and stops
# if it isn't.
$ErrorActionPreference = 'Stop'
$root = (git rev-parse --show-toplevel).Trim()
Set-Location $root
$plan = 'docs/execution/plans/2026-11-13-capture-style-tool-flow'
$receipts = 'C:/Temp/av-kit'
$env:ELECTRON_RUN_AS_NODE = $null
$env:PYTHONIOENCODING = 'utf-8'
# RC1 ECN-2 (CLOSEOUT-SELFTEST-ANCESTOR-AGENT-DIR): keep pytest's temp dirs away from the home folder.
$tmp = 'C:\Temp\av-kit\s71\tmp'
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
# execution budget and his word to execute, each as USER_EXPLICIT with a date and a quote, and
# D-713 (the split) must carry his ruling.
$ruled = @'
import pathlib, re, sys
text = pathlib.Path(sys.argv[1], "implementation-plan.md").read_text(encoding="utf-8")
status = [ln for ln in text.splitlines() if ln.startswith("> **Status:**")]
line = status[0] if len(status) == 1 else ""
budget = re.search(r"execution review budget to [0-9][0-9.,]*M? \(USER_EXPLICIT 2026-\d\d-\d\d '[^']+'\)", line)
execute = re.search(r"said to execute \(USER_EXPLICIT 2026-\d\d-\d\d '[^']+'\)", line)
start = text.find("  - id: D-713\n")
end = text.find("  - id: D-714\n")
d713 = text[start:end] if 0 <= start < end else ""
split = "resolution: human" in d713 and "human_message_reference: \"USER_EXPLICIT 2026-11-13 'A'\"" in d713
print(f"status lines: {len(status)}")
print(f"budget: {budget.group(0) if budget else None}")
print(f"execute: {execute.group(0) if execute else None}")
print(f"D-713 ruled by Mat: {split}")
ok = bool(line and budget and execute and split)
if not ok:
    print("the Status line lacks Mat's budget or his word to execute, or D-713 lacks his ruling (S9); the rows can't run")
sys.exit(0 if ok else 1)
'@
Invoke-Step 'rulings' @('uv', 'run', '--no-sync', 'python', '-c', $ruled, $plan)

# S8: the contract dependencies (MEU-87's options row, MEU-99's undo, MEU-100's toolbar) approved,
# MEU-105 and MEU-106 pending, no MEU-143 entry yet (row 6 adds it), and Session 70's commit an
# ancestor of HEAD.
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
want = {"MEU-87": "approved", "MEU-99": "approved", "MEU-100": "approved", "MEU-105": "pending", "MEU-106": "pending", "MEU-143": None}
have = {meu: status(meu) for meu in want}
entry_143 = any(line.strip() == "id: MEU-143" for line in lines)
print(f"queue: {have}")
print(f"MEU-143 entry present: {entry_143}")
s70 = subprocess.run(["git", "merge-base", "--is-ancestor", "5e9ea7c", "HEAD"], capture_output=True).returncode
print(f"5e9ea7c is an ancestor of HEAD: {s70 == 0}")
sys.exit(0 if have == want and not entry_143 and s70 == 0 else 1)
'@
Invoke-Step 'queue-order' @('uv', 'run', '--no-sync', 'python', '-c', $queue)

# S7: the names this plan calls, by name, and the names and files it adds, still absent. A shape
# that differs in signature is found when row 1 re-reads its anchors.
$shapes = @'
import pathlib, re, sys
CORE = "packages/core/src/avkit_core"
API = "packages/api/src/avkit_api"
UI = "ui/src/renderer/src/features/capture"
SERVICE = f"{CORE}/services/settings.py"
SCHEMA = f"{API}/schemas/settings.py"
MCP = "mcp-server/src/toolsets/settings.ts"
PUT = "ui/src/renderer/src/features/settings/settings-schemas.ts"
HOOK = f"{UI}/useCaptureSettings.ts"
TOOLBAR = f"{UI}/capture-toolbar.ts"
SCRUB = f"{UI}/CaptureScrubField.tsx"
SCRUBMATH = f"{UI}/capture-scrub.ts"
VIEWPORT = f"{UI}/CaptureViewport.tsx"
PAGE = f"{UI}/CapturePage.tsx"
HELP = f"{UI}/capture-help-content.ts"
IDS = "ui/tests/e2e/test-ids.ts"
INDEX = "docs/build-plan/gui-actions-index.md"
SPEC = "docs/build-plan/09-screenshot-capture.md"
present = (
    (SERVICE, r"^COOKIE_NEEDLES: tuple\[str, \.\.\.\] = ", "COOKIE_NEEDLES"),
    (SERVICE, r"^class SettingSpec:$", "SettingSpec"),
    (SERVICE, r"^    allow_negative: bool = False$", "SettingSpec.allow_negative"),
    (SERVICE, r'^    \("capture", "annotated_format"\): SettingSpec\("string", "png", frozenset\(ANNOTATED_FORMATS\)\),$', "the annotated_format row"),
    (SERVICE, r"^def _encode\(spec: SettingSpec, key: str, value: object\) -> str:$", "_encode"),
    (SCHEMA, r"^class SettingsPutIn\(ApiModel\):$", "SettingsPutIn"),
    (SCHEMA, r"^    annotated_format: str \| None = None$", "SettingsPutIn.annotated_format"),
    (MCP, r"^export const SETTINGS_SCHEMA: \{$", "SETTINGS_SCHEMA"),
    (MCP, r'^      annotated_format: \{ type: "string", default: "png", enum: ANNOTATED_FORMATS \},$', "SETTINGS_SCHEMA's annotated_format"),
    (MCP, r"^const settingsLeaves = \{$", "settingsLeaves"),
    (MCP, r"^  annotated_format: z\.enum\(ANNOTATED_FORMATS\)\.optional\(\),$", "settingsLeaves' annotated_format"),
    (PUT, r"^export const capturePutSchema = z$", "capturePutSchema"),
    (HOOK, r"^export const CAPTURE_SETTINGS_KEY = \['settings', 'capture'\] as const$", "CAPTURE_SETTINGS_KEY"),
    (HOOK, r"^export type CaptureForm = \{$", "CaptureForm"),
    (TOOLBAR, r"^export function optionGroups\($", "optionGroups"),
    (TOOLBAR, r"^function strokeApplies\(tool: CaptureTool, selected: Annotation \| null\): boolean \{$", "the select stroke rule"),
    (PAGE, r"^const COLOR_GATE_MESSAGE = 'Apply or Cancel color'$", "COLOR_GATE_MESSAGE"),
    (PAGE, r"^  const colorDirty = ", "colorDirty"),
    (PAGE, r"^  function changeTextBg\(value: string\): void \{$", "changeTextBg"),
    (PAGE, r"^  function inspectMark\(index: number\): void \{$", "inspectMark"),
    (PAGE, r"^function createDrawnMark\($", "createDrawnMark"),
    (PAGE, r"^type SizeBurst = \{$", "SizeBurst"),
    (PAGE, r"^  function chooseTool\(next: CaptureTool\): void \{$", "chooseTool"),
    (VIEWPORT, r'data-testid="capture-color-apply"', "the Apply button"),
    (VIEWPORT, r'data-testid="capture-color-cancel"', "the Cancel button"),
    (VIEWPORT, r'^\s+data-testid="capture-named-color"$', "the named colour select"),
    (VIEWPORT, r'^\s+data-testid="capture-color-well"$', "the colour well"),
    (VIEWPORT, r'^\s+data-testid="capture-text-bg"$', "the text background field"),
    (VIEWPORT, r'^\s+data-testid="capture-block-size"$', "the block size field"),
    (SCRUB, r"^export type CaptureScrubFieldProps = \{$", "CaptureScrubFieldProps"),
    (SCRUBMATH, r"^export const SCRUB_MIN = 1$", "SCRUB_MIN"),
    (SCRUBMATH, r"^export function clampScrub\(value: number, delta: number, min: number, max: number\): number \{$", "clampScrub"),
    (HELP, r"^    title: 'Annotation tools',$", "the Annotation tools help entry"),
    (HELP, r"Apply commits color\.", "the help sentence"),
    (INDEX, r"^\| `capture:tool_lock` \| Keep tool after drawing \(tool lock\) \|", "capture:tool_lock"),
    (IDS, r"^// MEU-51 primitive harness IDs\.", "the AC-51.6 hash boundary"),
    (IDS, r"^// MEU-102 Capture multi-line text \(additive IDs\)\.$", "the MEU-102 test-id block"),
    (SPEC, r'^<a id="style-and-tool-flow"></a>$', "09 §Style and tool flow"),
    (SPEC, r"^> \*\*MEU-105\.\*\* Synthesis slice 6 ", "09's MEU-105 header note"),
)
# This plan's names, keys, labels and files, absent from every file it writes.
absent_files = (
    SERVICE, SCHEMA, MCP, PUT, HOOK, TOOLBAR, SCRUB, VIEWPORT, PAGE, HELP, IDS, INDEX, SPEC,
    "openapi.committed.json", "mcp-server/tests/capture.test.ts", "tests/unit/test_capture_service.py",
    "ui/tests/e2e/capture-inbox.test.ts", "docs/build-plan/build-priority-matrix.md",
    ".agent/context/meu-status.yaml",
    ".agent/context/grouping/2026-10-29-capture-annotation-editor-session-grouping.md",
)
absent = re.compile(
    r"\bStyleTool\b|TOOL_STYLE_DEFAULTS|TOOL_STYLE_LEAVES|styleToolFor|styleToolOfMark|readToolStyles|"
    r"useCaptureToolStyles|saveToolStyle|fetchCaptureSettings|resetCaptureStyleStore|capture-style-store|captureStylePutSchema|arrow_color|box_stroke|text_font_size|"
    r"pixelate_block_size|capture-block-size-scrub|CAPTURE_BLOCK_SIZE_SCRUB|capture:style_mark|"
    r"capture:style_tool|Couldn't save the tool style|MEU-143|AC-105"
)
new_files = (
    f"{UI}/capture-tool-style.ts",
    f"{UI}/useCaptureToolStyles.ts",
    f"{UI}/capture-style-store.ts",
    "tests/unit/test_capture_style_settings.py",
    "tests/e2e/test_api_capture_style.py",
    "ui/tests/unit/capture-tool-style.test.ts",
    "ui/tests/unit/capture-style-flow.behavior.test.ts",
)
wrong = []
for rel, pattern, label in present:
    text = pathlib.Path(rel).read_text(encoding="utf-8")
    hits = [n for n, ln in enumerate(text.splitlines(), 1) if re.search(pattern, ln)]
    print(f"present {label}: {rel} lines {hits[:5]}")
    if len(hits) != 1:
        wrong.append(f"{label}: {len(hits)} match(es), want 1")
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
# keeps each line's own ending (S63 RULE-3). Rows 5 and 6 byte-edit the actions index, 09, the
# matrix and the grouping. The divergence report is hashed only.
$anchors = @'
import hashlib, pathlib, sys
UI = "ui/src/renderer/src/features/capture"
targets = (
    "packages/core/src/avkit_core/services/settings.py",
    "packages/api/src/avkit_api/schemas/settings.py",
    "openapi.committed.json",
    "mcp-server/src/toolsets/settings.ts",
    "ui/src/renderer/src/features/settings/settings-schemas.ts",
    f"{UI}/capture-toolbar.ts",
    f"{UI}/CaptureScrubField.tsx",
    f"{UI}/useCaptureSettings.ts",
    f"{UI}/CaptureViewport.tsx",
    f"{UI}/CapturePage.tsx",
    f"{UI}/capture-help-content.ts",
    "ui/tests/e2e/test-ids.ts",
    "ui/tests/unit/capture-page.behavior.test.ts",
    "ui/tests/unit/capture-action-row.test.ts",
    "ui/tests/unit/capture-help-content.test.ts",
    "ui/tests/unit/capture-toolbar.test.ts",
    "tests/unit/test_capture_service.py",
    "mcp-server/tests/capture.test.ts",
    "ui/tests/e2e/capture-inbox.test.ts",
    "docs/build-plan/gui-actions-index.md",
    "docs/build-plan/09-screenshot-capture.md",
    "docs/build-plan/build-priority-matrix.md",
    ".agent/context/meu-status.yaml",
    "docs/BUILD_PLAN.md",
    ".agent/context/meu-registry.md",
    ".agent/context/grouping/2026-10-29-capture-annotation-editor-session-grouping.md",
)
new = (
    f"{UI}/capture-tool-style.ts",
    f"{UI}/useCaptureToolStyles.ts",
    f"{UI}/capture-style-store.ts",
    "tests/unit/test_capture_style_settings.py",
    "tests/e2e/test_api_capture_style.py",
    "ui/tests/unit/capture-tool-style.test.ts",
    "ui/tests/unit/capture-style-flow.behavior.test.ts",
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
Invoke-Step 'anchors' @('uv', 'run', '--no-sync', 'python', '-c', $anchors, "$receipts/s71-anchors.txt")

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

& rtk proxy uv run --no-sync pytest tests/ --tb=short -q -rfE > "$receipts/s71-base-py.txt" 2>&1
Write-Output ("base suite py exit={0} receipt={1}/s71-base-py.txt" -f $LASTEXITCODE, $receipts)
Get-Content "$receipts/s71-base-py.txt" | Select-String -Pattern '^FAILED |^ERROR |passed|failed' | Select-Object -Last 12

& rtk proxy npm --prefix ui run test > "$receipts/s71-base-ui.txt" 2>&1
Write-Output ("base suite ui exit={0} receipt={1}/s71-base-ui.txt" -f $LASTEXITCODE, $receipts)
Get-Content "$receipts/s71-base-ui.txt" | Select-String -Pattern ' FAIL |Test Files|Tests ' | Select-Object -Last 12

& rtk proxy npm --prefix mcp-server run build > "$receipts/s71-base-mcp-build.txt" 2>&1
Write-Output ("base mcp build exit={0} receipt={1}/s71-base-mcp-build.txt" -f $LASTEXITCODE, $receipts)
& rtk proxy npm --prefix mcp-server run test > "$receipts/s71-base-mcp.txt" 2>&1
Write-Output ("base suite mcp exit={0} receipt={1}/s71-base-mcp.txt" -f $LASTEXITCODE, $receipts)
Get-Content "$receipts/s71-base-mcp.txt" | Select-String -Pattern ' FAIL |Test Files|Tests ' | Select-Object -Last 12

# The capture Electron spec the gate runs, on a fresh build, so its base count is on record.
& rtk proxy npm --prefix ui run build > "$receipts/s71-base-ui-build.txt" 2>&1
Write-Output ("base ui build exit={0} receipt={1}/s71-base-ui-build.txt" -f $LASTEXITCODE, $receipts)
& rtk proxy npm --prefix ui run test:e2e -- tests/e2e/capture-inbox.test.ts > "$receipts/s71-base-e2e.txt" 2>&1
Write-Output ("base capture e2e exit={0} receipt={1}/s71-base-e2e.txt" -f $LASTEXITCODE, $receipts)
Get-Content "$receipts/s71-base-e2e.txt" | Select-String -Pattern '^\s+\d+ (passed|failed|skipped|flaky)' | Select-Object -Last 6

& rtk proxy uv run --no-sync ruff check packages/ tests/ > "$receipts/s71-base-ruff.txt" 2>&1
Write-Output ("base ruff exit={0} receipt={1}/s71-base-ruff.txt" -f $LASTEXITCODE, $receipts)
Get-Content "$receipts/s71-base-ruff.txt" -Tail 5

Invoke-Step 'red-check-selftest' @('uv', 'run', '--no-sync', 'python', "$plan/red-check.py", '--selftest')
Invoke-Step 'identity-selftest' @('uv', 'run', '--no-sync', 'python', "$plan/identity.py", '--selftest')
Invoke-Step 'id-length-selftest' @('uv', 'run', '--no-sync', 'python', "$plan/id-length.py", '--selftest')
Write-Output 'baseline: all steps exit 0'
exit 0
