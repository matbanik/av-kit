# Session 61 baseline (task row 0; implementation-plan.md §Verification Plan 1).
# First proves that D-560 and D-561 carry Mat's ruling (S14), that Session 60 has closed (S8),
# and that the import route, the preload path, the dialog channel and the hotkey publication
# path this plan calls are present by name, with this plan's own names still absent (S11). Then
# records HEAD and the dirty tree with each dirty path's SHA-256, records every Files Modified
# target's line endings and SHA-256 in s61-anchors.txt, installs Python from the lock without
# the network, proves ui/ and mcp-server/node_modules match their locks, asserts the pinned
# FFmpeg pair and Pillow, checks that F2, the work tree's Electron and the clipboard are free
# (S6), captures the base Python, UI, MCP and Electron runs, and runs the plan-local selftests.
# A copy of Session 60's with the checks changed for this plan. The base runs' own failures are
# recorded, not fatal: the session gate excuses only the Python ids the py receipt shows
# failing, and nothing else. Every other step is fail-fast. Run from the repository root.
#
# `npm --prefix ui ci` and `npm --prefix mcp-server ci` are not run (Session 50's reason, still
# true on 2026-11-10): the avkit MCP servers that Claude sessions use run as
# `ui/node_modules/electron/dist/electron.exe mcp-server/dist/index.js` and `node
# mcp-server/dist/index.js`, so deleting either node_modules would fail on the locked binary or
# break them. The lock-sync step proves each installed tree is the locked one instead, and stops
# if it isn't.
$ErrorActionPreference = 'Stop'
$root = (git rev-parse --show-toplevel).Trim()
Set-Location $root
$plan = 'docs/execution/plans/2026-11-10-gui-capture-image-import'
$receipts = 'C:/Temp/av-kit'
$env:ELECTRON_RUN_AS_NODE = $null
$env:PYTHONIOENCODING = 'utf-8'
# RC1 ECN-2 (CLOSEOUT-SELFTEST-ANCESTOR-AGENT-DIR): keep pytest's temp dirs away from the home folder.
$tmp = 'C:\Temp\av-kit\s61\tmp'
New-Item -ItemType Directory -Force -Path $tmp | Out-Null
$env:TMP = $tmp
$env:TEMP = $tmp

function Invoke-Step([string]$Id, [string[]]$Argv) {
    & rtk proxy @Argv
    $code = $LASTEXITCODE
    Write-Output ("baseline step {0} exit={1}" -f $Id, $code)
    if ($code -ne 0) { exit $code }
}

# S14: the paste proof and row 6 run on Mat's rulings. A ruled entry's chosen starts with the
# option letter and its human_message_reference quotes Mat (look-check.py ruling(), the plan's
# §1 item 1).
$ruled = @'
import importlib.util, pathlib, sys
spec = importlib.util.spec_from_file_location("look_check", sys.argv[1] + "/look-check.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
text = pathlib.Path(sys.argv[1], "implementation-plan.md").read_text(encoding="utf-8")
ok = True
for decision, letters in (("D-560", "ABC"), ("D-561", "AB")):
    letter, why = mod.ruling(text, decision)
    print(why)
    if letter is None or letter not in letters:
        ok = False
if not ok:
    print("a decision is unruled (S14); the paste proof and row 6 can't run without Mat's words")
sys.exit(0 if ok else 1)
'@
Invoke-Step 'd560-d561-ruled' @('uv', 'run', '--no-sync', 'python', '-c', $ruled, $plan)

# S8: Session 60 has closed (MEU-131 approved, none of its paths left in the tree).
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
s131 = status("MEU-131")
print(f"session 60: MEU-131 {s131}")
porcelain = subprocess.run(["git", "status", "--porcelain", "--untracked-files=all"], capture_output=True, check=True).stdout.decode("utf-8").splitlines()
# Session 60's Files Modified and its own closeout files
# (docs/execution/plans/2026-11-10-gui-capture-crop-tool/implementation-plan.md §Files Modified).
session60 = {
    "ui/src/renderer/src/features/capture/capture-crop.ts",
    "ui/src/renderer/src/features/capture/CaptureCropBar.tsx",
    "ui/src/renderer/src/features/capture/CaptureCropOverlay.tsx",
    "ui/src/renderer/src/features/capture/CaptureViewport.tsx",
    "ui/src/renderer/src/features/capture/CapturePage.tsx",
    "ui/src/renderer/src/features/capture/capture-toolbar.ts",
    "ui/src/renderer/src/features/capture/capture-commands.ts",
    "ui/tests/unit/capture-crop.test.ts",
    "ui/tests/unit/capture-crop-tool.behavior.test.ts",
    "ui/tests/unit/capture-toolbar.test.ts",
    "ui/tests/unit/icon-hints.test.ts",
    "ui/tests/e2e/capture-inbox.test.ts",
    "ui/tests/e2e/test-ids.ts",
    "docs/build-plan/09-screenshot-capture.md",
}
prefixes = (
    "docs/execution/plans/2026-11-10-gui-capture-crop-tool/",
    ".agent/context/handoffs/2026-11-10-gui-capture-crop-tool-",
    "docs/execution/reflections/2026-11-10-gui-capture-crop-tool-",
)
left = [line for line in porcelain if line[3:] in session60 or line[3:].startswith(prefixes)]
for line in left:
    print(f"session 60 path still in the tree: {line}")
sys.exit(0 if s131 == "approved" and not left else 1)
'@
Invoke-Step 'queue-order' @('uv', 'run', '--no-sync', 'python', '-c', $queue)

# S11: the names this plan calls, by name, and the names it adds, still absent. A shape that
# differs in signature is found when row 1 re-reads its anchors.
$shapes = @'
import pathlib, re, sys
present = (
    ("packages/api/src/avkit_api/schemas/captures.py", r"^class CaptureImportIn\(", "CaptureImportIn"),
    ("packages/api/src/avkit_api/schemas/captures.py", r"mode: Literal\[\"import\"\]", "the import mode"),
    ("packages/api/src/avkit_api/routes/captures.py", r"isinstance\(body, CaptureImportIn\)", "the import route branch"),
    ("ui/src/main/preload.ts", r"getPathForFile: \(file: File\)", "getPathForFile"),
    ("ui/src/main/ipc.ts", r"^  'show-files-dialog',$", "show-files-dialog in RENDERER_TO_MAIN_CHANNELS"),
    ("ui/src/main/ipc.ts", r"case 'show-files-dialog':", "the show-files-dialog handler"),
    ("ui/src/main/capture-picker.ts", r"^async function publishStagedCapture\(", "publishStagedCapture"),
    ("ui/src/main/capture-picker.ts", r"^function claimInboxName\(", "claimInboxName"),
    ("ui/src/main/capture-picker.ts", r"^export const PICKER_STAGING_PREFIX\b", "PICKER_STAGING_PREFIX"),
    ("ui/src/main/capture-register.ts", r"^export async function finalizeCapturedPng\(", "finalizeCapturedPng"),
    ("ui/src/renderer/src/components/queue/BulkResultToast.tsx", r"^export function BulkResultToast\(", "BulkResultToast"),
)
absent = (
    ("ui/src/main/ipc.ts", r"capture-paste-image", "capture-paste-image in ipc.ts"),
    ("ui/src/main/preload.ts", r"pasteCaptureImage", "pasteCaptureImage in preload"),
    ("ui/src/renderer/src/env.d.ts", r"pasteCaptureImage", "pasteCaptureImage in env.d.ts"),
    ("ui/src/main/capture-picker.ts", r"pasteClipboardImage|PasteOutcome", "pasteClipboardImage"),
    ("ui/src/main/index.ts", r"pasteCaptureImage|pasteClipboardImage", "the paste dep in index.ts"),
    ("ui/src/renderer/src/features/capture/capture-commands.ts", r"\bimportCapture\b", "importCapture"),
    ("ui/src/renderer/src/features/capture/CapturePage.tsx", r"capture-import", "capture-import on the page"),
    ("ui/tests/e2e/test-ids.ts", r"capture-import|CAPTURE_IMPORT", "capture-import in test-ids"),
    ("docs/build-plan/gui-actions-index.md", r"capture:import|capture:drop|capture:paste", "the index rows"),
)
wrong = []
for rel, pattern, label in present:
    text = pathlib.Path(rel).read_text(encoding="utf-8")
    hits = [n for n, ln in enumerate(text.splitlines(), 1) if re.search(pattern, ln)]
    print(f"present {label}: {rel} lines {hits[:5]}")
    if not hits:
        wrong.append(f"missing {label}")
for rel, pattern, label in absent:
    text = pathlib.Path(rel).read_text(encoding="utf-8")
    hits = [n for n, ln in enumerate(text.splitlines(), 1) if re.search(pattern, ln)]
    print(f"absent {label}: {rel} lines {hits[:5]}")
    if hits:
        wrong.append(f"already present {label}")
# 'Ctrl+V' stays a member of RESERVED_CHORDS (D-136): the paste listener needs no registry entry.
shortcuts = pathlib.Path("ui/src/renderer/src/registry/shortcuts.ts").read_text(encoding="utf-8")
reserved = re.search(r"^export const RESERVED_CHORDS[^=]*=\s*new Set\(\[(.*?)\]\)", shortcuts, re.DOTALL | re.MULTILINE)
members = re.findall(r"'([^']+)'", reserved.group(1)) if reserved else []
print(f"RESERVED_CHORDS: {members}")
if "Ctrl+V" not in members:
    wrong.append("missing 'Ctrl+V' in RESERVED_CHORDS")
module = pathlib.Path("ui/src/renderer/src/features/capture/capture-import.ts")
print(f"absent capture-import.ts: exists={module.exists()}")
if module.exists():
    wrong.append("already present capture-import.ts")
print("shapes wrong (S11):", wrong)
sys.exit(1 if wrong else 0)
'@
Invoke-Step 'shapes' @('uv', 'run', '--no-sync', 'python', '-c', $shapes)

$head = (git rev-parse HEAD).Trim()
Set-Content -Path "$plan/baseline.sha" -Value $head -NoNewline
# Each line is the porcelain line, a tab, then the path's SHA-256 (`deleted` when it is gone).
# The session gate reads the path as the text between column 3 and the tab. The other session's
# proposal is hashed here and never opened as text.
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
# A new file is recorded as absent; an existing target that is missing stops here.
$anchors = @'
import hashlib, pathlib, sys
targets = (
    "ui/src/renderer/src/features/capture/CapturePage.tsx",
    "ui/src/renderer/src/features/capture/capture-commands.ts",
    "ui/src/renderer/src/env.d.ts",
    "ui/src/main/capture-picker.ts",
    "ui/src/main/ipc.ts",
    "ui/src/main/preload.ts",
    "ui/src/main/index.ts",
    "ui/tests/unit/gui-actions-audit.test.ts",
    "ui/tests/unit/clipboard-image-main.test.ts",
    "ui/tests/unit/ipc-strict-census.test.ts",
    "ui/tests/unit/login-item-ipc.test.ts",
    "ui/tests/unit/mcp-prompt-ipc.test.ts",
    "ui/tests/unit/web-prefs-ipc.test.ts",
    "ui/tests/unit/ipc-channels.ts",
    "ui/tests/e2e/test-ids.ts",
    "docs/build-plan/09-screenshot-capture.md",
    "docs/build-plan/gui-actions-index.md",
    ".agent/context/meu-status.yaml",
    "docs/BUILD_PLAN.md",
    ".agent/context/meu-registry.md",
    ".agent/context/grouping/2026-11-08-capture-crop-session-grouping.md",
)
new = (
    "ui/src/renderer/src/features/capture/capture-import.ts",
    "ui/tests/unit/capture-import.test.ts",
    "ui/tests/unit/capture-paste-main.test.ts",
    "ui/tests/unit/capture-import.behavior.test.ts",
    "tests/e2e/test_api_capture_import_names.py",
    "ui/tests/e2e/capture-import.test.ts",
)
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
Invoke-Step 'anchors' @('uv', 'run', '--no-sync', 'python', '-c', $anchors, "$receipts/s61-anchors.txt")

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
Invoke-Step 'ui-lock-sync' @('uv', 'run', 'python', '-c', $lockSync, 'ui')
Invoke-Step 'mcp-lock-sync' @('uv', 'run', 'python', '-c', $lockSync, 'mcp-server')

# The full Python suite runs Session 54's real-FFmpeg module; a missing or truncated binary is
# Stop Condition S4, not a fetch.
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
    $first = (& $exe -version | Select-Object -First 1)
    Write-Output ("{0} {1} B: {2}" -f $name, $size, $first)
}
Write-Output 'baseline step ffmpeg-pair exit=0'

# AC-132.21 and the look's seed draw with Pillow, and the import route rests on 13.0.0.
$pillow = @'
import sys
import PIL
from PIL import Image
print(f"pillow {PIL.__version__} MAX_IMAGE_PIXELS {Image.MAX_IMAGE_PIXELS}")
sys.exit(0 if PIL.__version__ == "13.0.0" and Image.MAX_IMAGE_PIXELS == 89478485 else 1)
'@
Invoke-Step 'pillow-version' @('uv', 'run', 'python', '-c', $pillow)

# S6: the E2E suite registers F2 (capture-inbox.test.ts:84), and the paste proof needs the
# clipboard. Taken is a stop, not a retry; nothing is stopped.
Invoke-Step 'hotkey-free' @('uv', 'run', 'python', "$plan/hotkey-free.py")

& rtk proxy uv run pytest tests/ --tb=short -q -rfE *> "$receipts/s61-base-py.txt"
Write-Output ("base suite py exit={0} receipt={1}/s61-base-py.txt" -f $LASTEXITCODE, $receipts)
Get-Content "$receipts/s61-base-py.txt" | Select-String -Pattern '^FAILED |^ERROR |passed|failed' | Select-Object -Last 12

& rtk proxy npm --prefix ui run test *> "$receipts/s61-base-ui.txt"
Write-Output ("base suite ui exit={0} receipt={1}/s61-base-ui.txt" -f $LASTEXITCODE, $receipts)
Get-Content "$receipts/s61-base-ui.txt" | Select-String -Pattern ' FAIL |Test Files|Tests ' | Select-Object -Last 12

& rtk proxy npm --prefix mcp-server run test *> "$receipts/s61-base-mcp.txt"
Write-Output ("base suite mcp exit={0} receipt={1}/s61-base-mcp.txt" -f $LASTEXITCODE, $receipts)
Get-Content "$receipts/s61-base-mcp.txt" | Select-String -Pattern ' FAIL |Test Files|Tests ' | Select-Object -Last 12

# The base Electron run: the renderer build, then the two capture modules the Greens rerun.
& rtk proxy npm --prefix ui run build *> "$receipts/s61-base-ui-build.txt"
$buildCode = $LASTEXITCODE
Write-Output ("base ui build exit={0} receipt={1}/s61-base-ui-build.txt" -f $buildCode, $receipts)
if ($buildCode -ne 0) { exit $buildCode }
& rtk proxy npm --prefix ui run test:e2e -- tests/e2e/capture-picker.test.ts tests/e2e/capture-inbox.test.ts *> "$receipts/s61-base-e2e.txt"
Write-Output ("base e2e capture-picker and capture-inbox exit={0} receipt={1}/s61-base-e2e.txt" -f $LASTEXITCODE, $receipts)
Get-Content "$receipts/s61-base-e2e.txt" | Select-String -Pattern '✘|passed|failed|flaky' | Select-Object -Last 12

Invoke-Step 'red-check-selftest' @('uv', 'run', 'python', "$plan/red-check.py", '--selftest')
Invoke-Step 'identity-selftest' @('uv', 'run', 'python', "$plan/identity.py", '--selftest')
Invoke-Step 'dev-app-procs-selftest' @('uv', 'run', 'python', "$plan/dev-app-procs.py", '--selftest')
Invoke-Step 'hotkey-free-selftest' @('uv', 'run', 'python', "$plan/hotkey-free.py", '--selftest')
Invoke-Step 'look-check-selftest' @('uv', 'run', 'python', "$plan/look-check.py", '--selftest')
Write-Output 'baseline: all steps exit 0'
exit 0
