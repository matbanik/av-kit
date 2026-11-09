# Session 58 baseline (task row 0; implementation-plan.md §Verification Plan 1).
# First proves the queue this session waits on: Session 55 is committed (it edits
# tests/unit/test_domain.py and openapi.committed.json, which rows 1 to 5 edit too) and rc.2's
# Session 57 has closed (D-405). Then records HEAD and the dirty tree with each dirty path's
# SHA-256, installs Python from the lock without the network, proves ui/ and
# mcp-server/node_modules match their locks, asserts the pinned FFmpeg pair, captures the base
# Python, UI and MCP suites, and runs the plan-local selftests. A copy of Session 55's with the
# queue checks added and the yt-dlp and DDL steps removed. The base suites' own failures are
# recorded, not fatal: the session gate excuses only the ids these receipts show failing. Every
# other step is fail-fast. Run from the repository root.
#
# `npm --prefix ui ci` and `npm --prefix mcp-server ci` are not run (Session 50's reason, still
# true on 2026-11-08): the avkit MCP servers that Claude sessions use run as
# `ui/node_modules/electron/dist/electron.exe mcp-server/dist/index.js` and `node
# mcp-server/dist/index.js`, so deleting either node_modules would fail on the locked binary or
# break them. The lock-sync step proves each installed tree is the locked one instead, and stops
# if it isn't.
#
# -QueueWaived: only when Mat has said in words to run before Session 57 closes. The row's
# receipt then shows the waiver, and the handoff quotes Mat's message (S3).
param([switch]$QueueWaived)
$ErrorActionPreference = 'Stop'
$root = (git rev-parse --show-toplevel).Trim()
Set-Location $root
$plan = 'docs/execution/plans/2026-11-08-capture-region-import'
$receipts = 'C:/Temp/av-kit'
$env:ELECTRON_RUN_AS_NODE = $null
$env:PYTHONIOENCODING = 'utf-8'
# RC1 ECN-2 (CLOSEOUT-SELFTEST-ANCESTOR-AGENT-DIR): keep pytest's temp dirs away from the home folder.
$tmp = 'C:\Temp\av-kit\s58\tmp'
New-Item -ItemType Directory -Force -Path $tmp | Out-Null
$env:TMP = $tmp
$env:TEMP = $tmp

function Invoke-Step([string]$Id, [string[]]$Argv) {
    & rtk proxy @Argv
    $code = $LASTEXITCODE
    Write-Output ("baseline step {0} exit={1}" -f $Id, $code)
    if ($code -ne 0) { exit $code }
}

# S3: Session 55 shares two files with this session, so its work must be on main and nothing of
# it may be left in the tree. A commit subject ending in (MEU-124) is its closeout commit.
$queue = @'
import pathlib, subprocess, sys
subjects = subprocess.run(["git", "log", "--format=%s", "-n", "40"], capture_output=True, check=True).stdout.decode("utf-8").splitlines()
committed = [s for s in subjects if s.rstrip().endswith("(MEU-124)")]
porcelain = subprocess.run(["git", "status", "--porcelain", "--untracked-files=all"], capture_output=True, check=True).stdout.decode("utf-8").splitlines()
prefixes = (
    "docs/execution/plans/2026-11-08-download-received-quality/",
    ".agent/context/handoffs/2026-11-08-download-received-quality-",
    "docs/execution/reflections/2026-11-08-download-received-quality-",
    "tests/integration/test_download_received_quality.py",
)
left = [line for line in porcelain if line[3:].startswith(prefixes)]
print(f"session 55 commit: {committed[0] if committed else 'none in the last 40 commits'}")
for line in left:
    print(f"session 55 path still in the tree: {line}")
status = None
lines = pathlib.Path(".agent/context/meu-status.yaml").read_text(encoding="utf-8").splitlines()
for n, line in enumerate(lines):
    if line.strip() == "id: MEU-125":
        for follow in lines[n + 1 : n + 40]:
            if follow.strip().startswith("status:"):
                status = follow.split(":", 1)[1].strip().strip("'\"")
                break
        break
print(f"session 57 (MEU-125 release-rc2) status: {status}")
waived = len(sys.argv) > 1 and sys.argv[1] == "waived"
if waived and status != "approved":
    print("queue check for session 57 waived by Mat (D-405); quote the message in the handoff")
ok = bool(committed) and not left and (status == "approved" or waived)
sys.exit(0 if ok else 1)
'@
$queueArg = if ($QueueWaived) { 'waived' } else { 'strict' }
Invoke-Step 'queue-order' @('uv', 'run', '--no-sync', 'python', '-c', $queue, $queueArg)

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

# --offline: this step can't fetch a package (plan-time dry run: s58-uv-offline-dry-run.txt).
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

# D-409 and D-417 rest on Pillow 13.0.0's LANCZOS filter and MAX_IMAGE_PIXELS (89,478,485 at
# plan time, s58-plan-exif-probe.txt); another version is S4.
$pillow = @'
import sys
import PIL
from PIL import Image
print(f"pillow {PIL.__version__} MAX_IMAGE_PIXELS {Image.MAX_IMAGE_PIXELS}")
sys.exit(0 if PIL.__version__ == "13.0.0" and Image.MAX_IMAGE_PIXELS == 89478485 else 1)
'@
Invoke-Step 'pillow-version' @('uv', 'run', 'python', '-c', $pillow)

& rtk proxy uv run pytest tests/ --tb=short -q -rfE *> "$receipts/s58-base-py.txt"
Write-Output ("base suite py exit={0} receipt={1}/s58-base-py.txt" -f $LASTEXITCODE, $receipts)
Get-Content "$receipts/s58-base-py.txt" | Select-String -Pattern '^FAILED |^ERROR |passed|failed' | Select-Object -Last 12

& rtk proxy npm --prefix ui run test *> "$receipts/s58-base-ui.txt"
Write-Output ("base suite ui exit={0} receipt={1}/s58-base-ui.txt" -f $LASTEXITCODE, $receipts)
Get-Content "$receipts/s58-base-ui.txt" | Select-String -Pattern ' FAIL |Test Files|Tests ' | Select-Object -Last 12

& rtk proxy npm --prefix mcp-server run test *> "$receipts/s58-base-mcp.txt"
Write-Output ("base suite mcp exit={0} receipt={1}/s58-base-mcp.txt" -f $LASTEXITCODE, $receipts)
Get-Content "$receipts/s58-base-mcp.txt" | Select-String -Pattern ' FAIL |Test Files|Tests ' | Select-Object -Last 12

Invoke-Step 'red-check-selftest' @('uv', 'run', 'python', "$plan/red-check.py", '--selftest')
Invoke-Step 'identity-selftest' @('uv', 'run', 'python', "$plan/identity.py", '--selftest')
Write-Output 'baseline: all steps exit 0'
exit 0
