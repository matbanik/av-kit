# Session 50 baseline (task row 0; implementation-plan.md §Verification Plan 1).
# Records HEAD and the dirty tree and the real console.log's state, installs Python from the
# lock, proves ui/node_modules matches ui/package-lock.json, and captures the base Python and UI
# suites. The base suites' own failures are recorded, not fatal: the session gate excuses only the
# ids these receipts show failing. Every other step is fail-fast. Run from the repository root.
#
# `npm --prefix ui ci` is not run: the avkit MCP servers that Claude sessions use run on
# ui/node_modules/electron (`electron.exe mcp-server/dist/index.js`), so deleting node_modules
# would fail on the locked binary or break them. The lock-sync step proves the installed tree
# is the locked one instead, and stops if it isn't.
$ErrorActionPreference = 'Stop'
$root = (git rev-parse --show-toplevel).Trim()
Set-Location $root
$plan = 'docs/execution/plans/2026-11-05-transcript-failure-reason'
$receipts = 'C:/Temp/av-kit'
$env:ELECTRON_RUN_AS_NODE = $null
$env:PYTHONIOENCODING = 'utf-8'
# RC1 ECN-2 (CLOSEOUT-SELFTEST-ANCESTOR-AGENT-DIR): keep pytest's temp dirs away from C:/Users/Mat/.agent.
$tmp = "$receipts/s50/tmp"
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

Invoke-Step 'real-log-record' @('uv', 'run', 'python', "$plan/real-log-check.py", '--record', "$plan/real-log-before.json")
Invoke-Step 'uv-sync' @('uv', 'sync', '--frozen', '--all-packages')

$lockSync = @'
import json, pathlib, sys
lock = json.loads(pathlib.Path("ui/package-lock.json").read_text(encoding="utf-8"))["packages"]
want = {k: v.get("version") for k, v in lock.items() if k.startswith("node_modules/") and not v.get("optional")}
missing = sorted(k for k in want if not pathlib.Path("ui", k, "package.json").exists())
have = {k: json.loads(pathlib.Path("ui", k, "package.json").read_text(encoding="utf-8")).get("version") for k in want if k not in missing}
bad = sorted(k for k in have if have[k] != want[k])
for k in bad[:20]: print("version differs", k, want[k], have[k])
for k in missing[:20]: print("missing", k)
print(f"ui lock sync: {len(want)} locked packages, {len(bad)} differ, {len(missing)} missing")
sys.exit(1 if bad or missing else 0)
'@
Invoke-Step 'ui-lock-sync' @('uv', 'run', 'python', '-c', $lockSync)

& rtk proxy uv run pytest tests/ --tb=short -q -rfE *> "$receipts/s50-base-py.txt"
Write-Output ("base suite py exit={0} receipt={1}/s50-base-py.txt" -f $LASTEXITCODE, $receipts)
Get-Content "$receipts/s50-base-py.txt" | Select-String -Pattern '^FAILED |^ERROR |passed|failed' | Select-Object -Last 12

& rtk proxy npm --prefix ui run test *> "$receipts/s50-base-ui.txt"
Write-Output ("base suite ui exit={0} receipt={1}/s50-base-ui.txt" -f $LASTEXITCODE, $receipts)
Get-Content "$receipts/s50-base-ui.txt" | Select-String -Pattern ' FAIL |Test Files|Tests ' | Select-Object -Last 12

Invoke-Step 'red-check-selftest' @('uv', 'run', 'python', "$plan/red-check.py", '--selftest')
Invoke-Step 'identity-selftest' @('uv', 'run', 'python', "$plan/identity.py", '--selftest')
Invoke-Step 'real-log-selftest' @('uv', 'run', 'python', "$plan/real-log-check.py", '--selftest')
Write-Output 'baseline: all steps exit 0'
exit 0
