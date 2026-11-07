# Session 51 baseline (task row 0; implementation-plan.md §Verification Plan 1).
# Records HEAD and the dirty tree, snapshots the real models folder (MODELS_SNAPSHOT), installs
# Python from the lock, proves ui/ and mcp-server/node_modules match their locks, captures the base
# Python, UI and MCP suites, runs DEV_CHECK in its baseline mode, keeps a copy of the pre-session
# onedir for row 8's Red, and runs the plan-local selftests. The base suites' own failures are
# recorded, not fatal: the session gate excuses only the ids these receipts show failing. Every
# other step is fail-fast. Run from the repository root.
#
# `npm --prefix ui ci` and `npm --prefix mcp-server ci` are not run (Session 50's reason, still
# true on 2026-11-06): the avkit MCP servers that Claude sessions use run as
# `ui/node_modules/electron/dist/electron.exe mcp-server/dist/index.js` and `node
# mcp-server/dist/index.js`, so deleting either node_modules would fail on the locked binary or
# break them. The lock-sync step proves each installed tree is the locked one instead, and stops
# if it isn't.
$ErrorActionPreference = 'Stop'
$root = (git rev-parse --show-toplevel).Trim()
Set-Location $root
$plan = 'docs/execution/plans/2026-11-06-tts-build-capability'
$receipts = 'C:/Temp/av-kit'
$env:ELECTRON_RUN_AS_NODE = $null
$env:PYTHONIOENCODING = 'utf-8'
# RC1 ECN-2 (CLOSEOUT-SELFTEST-ANCESTOR-AGENT-DIR): keep pytest's temp dirs away from C:/Users/Mat/.agent.
$tmp = "$receipts/s51/tmp"
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
git status --porcelain --untracked-files=all | Set-Content -Path "$plan/baseline-dirty.txt"
Write-Output "baseline.sha $head"
Write-Output ("baseline-dirty.txt {0} paths" -f @(Get-Content "$plan/baseline-dirty.txt").Count)

# `--record` refuses to overwrite, so a re-run compares against the first snapshot instead (S4).
if (Test-Path "$plan/models-before.json") {
    Invoke-Step 'models-compare' @('uv', 'run', 'python', "$plan/models-snapshot.py", '--compare', "$plan/models-before.json")
} else {
    Invoke-Step 'models-record' @('uv', 'run', 'python', "$plan/models-snapshot.py", '--record', "$plan/models-before.json")
}
Invoke-Step 'uv-sync' @('uv', 'sync', '--frozen', '--all-packages')

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

& rtk proxy uv run pytest tests/ --tb=short -q -rfE *> "$receipts/s51-base-py.txt"
Write-Output ("base suite py exit={0} receipt={1}/s51-base-py.txt" -f $LASTEXITCODE, $receipts)
Get-Content "$receipts/s51-base-py.txt" | Select-String -Pattern '^FAILED |^ERROR |passed|failed' | Select-Object -Last 12

& rtk proxy npm --prefix ui run test *> "$receipts/s51-base-ui.txt"
Write-Output ("base suite ui exit={0} receipt={1}/s51-base-ui.txt" -f $LASTEXITCODE, $receipts)
Get-Content "$receipts/s51-base-ui.txt" | Select-String -Pattern ' FAIL |Test Files|Tests ' | Select-Object -Last 12

& rtk proxy npm --prefix mcp-server run test *> "$receipts/s51-base-mcp.txt"
Write-Output ("base suite mcp exit={0} receipt={1}/s51-base-mcp.txt" -f $LASTEXITCODE, $receipts)
Get-Content "$receipts/s51-base-mcp.txt" | Select-String -Pattern ' FAIL |Test Files|Tests ' | Select-Object -Last 12

# DEV_CHECK before any change; a failure is S9.
& rtk proxy uv run python "$plan/dev-pytorch-check.py" --baseline *> "$receipts/s51-base-dev.txt"
$code = $LASTEXITCODE
Get-Content "$receipts/s51-base-dev.txt" -Tail 25
Write-Output ("baseline step dev-pytorch-baseline exit={0}" -f $code)
if ($code -ne 0) { Write-Output 'S9: the dev path fails before any change'; exit $code }

# The pre-session onedir, the input of row 8's Red. An existing copy is never overwritten: it is
# kept only when its exe is byte-identical to the one in packaging/dist.
$source = 'packaging/dist/avkit-backend'
$copy = "$receipts/s51/backend-before/avkit-backend"
$sourceSha = (Get-FileHash "$source/avkit-backend.exe" -Algorithm SHA256).Hash.ToLower()
if (Test-Path $copy) {
    $copySha = (Get-FileHash "$copy/avkit-backend.exe" -Algorithm SHA256).Hash.ToLower()
    if ($copySha -ne $sourceSha) { Write-Output "$copy exists with another exe ($copySha); refusing to overwrite it"; exit 1 }
    Write-Output "$copy already there with the same exe; not copied again"
} else {
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $copy) | Out-Null
    Copy-Item -Recurse $source $copy
    $copySha = (Get-FileHash "$copy/avkit-backend.exe" -Algorithm SHA256).Hash.ToLower()
}
$exe = Get-Item "$copy/avkit-backend.exe"
$files = @(Get-ChildItem -Recurse -File $copy).Count
@(
    "source $source/avkit-backend.exe sha256 $sourceSha",
    "copy $copy/avkit-backend.exe sha256 $copySha bytes $($exe.Length) mtime $($exe.LastWriteTime.ToString('o'))",
    "copy files $files"
) | Set-Content -Path "$receipts/s51-base-onedir.txt"
Get-Content "$receipts/s51-base-onedir.txt"
if ($copySha -ne $sourceSha) { Write-Output 'the onedir copy differs from its source'; exit 1 }
Write-Output 'baseline step onedir-copy exit=0'

Invoke-Step 'red-check-selftest' @('uv', 'run', 'python', "$plan/red-check.py", '--selftest')
Invoke-Step 'identity-selftest' @('uv', 'run', 'python', "$plan/identity.py", '--selftest')
Invoke-Step 'models-snapshot-selftest' @('uv', 'run', 'python', "$plan/models-snapshot.py", '--selftest')
Write-Output 'baseline: all steps exit 0'
exit 0
