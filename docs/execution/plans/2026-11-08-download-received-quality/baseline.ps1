# Session 55 baseline (task row 0; implementation-plan.md §Verification Plan 1).
# Records HEAD and the dirty tree with each dirty path's SHA-256, installs Python from the lock
# without the network, proves ui/ and mcp-server/node_modules match their locks, asserts the
# pinned FFmpeg pair and the yt-dlp version, writes the shipped download_jobs DDL for AC-124.7,
# captures the base Python, UI and MCP suites, and runs the plan-local selftests. A copy of
# Session 54's with the yt-dlp and DDL steps added. The base suites' own failures are recorded,
# not fatal: the session gate excuses only the ids these receipts show failing. Every other step
# is fail-fast. Run from the repository root.
#
# `npm --prefix ui ci` and `npm --prefix mcp-server ci` are not run (Session 50's reason, still
# true on 2026-11-08): the avkit MCP servers that Claude sessions use run as
# `ui/node_modules/electron/dist/electron.exe mcp-server/dist/index.js` and `node
# mcp-server/dist/index.js`, so deleting either node_modules would fail on the locked binary or
# break them. The lock-sync step proves each installed tree is the locked one instead, and stops
# if it isn't.
$ErrorActionPreference = 'Stop'
$root = (git rev-parse --show-toplevel).Trim()
Set-Location $root
$plan = 'docs/execution/plans/2026-11-08-download-received-quality'
$receipts = 'C:/Temp/av-kit'
$env:ELECTRON_RUN_AS_NODE = $null
$env:PYTHONIOENCODING = 'utf-8'
# RC1 ECN-2 (CLOSEOUT-SELFTEST-ANCESTOR-AGENT-DIR): keep pytest's temp dirs away from the home folder.
$tmp = 'C:\Temp\av-kit\s55\tmp'
New-Item -ItemType Directory -Force -Path $tmp | Out-Null
$env:TMP = $tmp
$env:TEMP = $tmp

function Invoke-Step([string]$Id, [string[]]$Argv) {
    & rtk proxy @Argv
    $code = $LASTEXITCODE
    Write-Output ("baseline step {0} exit={1}" -f $Id, $code)
    if ($code -ne 0) { exit $code }
}

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

# --offline: this step can't fetch a package (plan-time dry run: s55-uv-offline-dry-run.txt).
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

# D-381 rests on yt-dlp 2026.10.26's source (YoutubeDL.py:3152); another version is S4.
$ytdlp = @'
import sys
from yt_dlp.version import __version__
print(f"yt-dlp {__version__}")
sys.exit(0 if __version__ == "2026.10.26" else 1)
'@
Invoke-Step 'yt-dlp-version' @('uv', 'run', 'python', '-c', $ytdlp)

# AC-124.7's old table is the shipped one: the download_jobs DDL that init_schema creates at
# baseline.sha, before row 1 adds the column. Built in a fresh folder under the temp root.
$ddl = @'
import pathlib, shutil, sqlite3, sys
from avkit_infra.database.engine import create_sqlite_engine, init_schema
folder = pathlib.Path(sys.argv[2])
shutil.rmtree(folder, ignore_errors=True)
folder.mkdir(parents=True)
engine = create_sqlite_engine(folder / "pre.db")
init_schema(engine)
engine.dispose()
with sqlite3.connect(folder / "pre.db") as conn:
    (sql,) = conn.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='download_jobs'").fetchone()
    columns = [row[1] for row in conn.execute("PRAGMA table_info(download_jobs)")]
pathlib.Path(sys.argv[1]).write_bytes((sql.strip() + "\n").encode("utf-8"))
print(f"pre-change download_jobs: {len(columns)} columns, last {columns[-1]}, received_height present: {'received_height' in columns}")
sys.exit(1 if "received_height" in columns else 0)
'@
Invoke-Step 'pre-change-ddl' @('uv', 'run', 'python', '-c', $ddl, "$plan/pre-change-download-jobs.sql", "$tmp/s55-ddl")

& rtk proxy uv run pytest tests/ --tb=short -q -rfE *> "$receipts/s55-base-py.txt"
Write-Output ("base suite py exit={0} receipt={1}/s55-base-py.txt" -f $LASTEXITCODE, $receipts)
Get-Content "$receipts/s55-base-py.txt" | Select-String -Pattern '^FAILED |^ERROR |passed|failed' | Select-Object -Last 12

& rtk proxy npm --prefix ui run test *> "$receipts/s55-base-ui.txt"
Write-Output ("base suite ui exit={0} receipt={1}/s55-base-ui.txt" -f $LASTEXITCODE, $receipts)
Get-Content "$receipts/s55-base-ui.txt" | Select-String -Pattern ' FAIL |Test Files|Tests ' | Select-Object -Last 12

& rtk proxy npm --prefix mcp-server run test *> "$receipts/s55-base-mcp.txt"
Write-Output ("base suite mcp exit={0} receipt={1}/s55-base-mcp.txt" -f $LASTEXITCODE, $receipts)
Get-Content "$receipts/s55-base-mcp.txt" | Select-String -Pattern ' FAIL |Test Files|Tests ' | Select-Object -Last 12

Invoke-Step 'red-check-selftest' @('uv', 'run', 'python', "$plan/red-check.py", '--selftest')
Invoke-Step 'identity-selftest' @('uv', 'run', 'python', "$plan/identity.py", '--selftest')
Write-Output 'baseline: all steps exit 0'
exit 0
