# One Playwright Electron run for a task row (rows 2, 3, 5, 6 and 11; implementation-plan.md
# §Verification Plan 2). Runs `npm --prefix ui run test:e2e -- <Files>` from the repository root
# through rtk proxy into -Receipt, writes the child exit code to <Receipt>.exit (red-check.py reads
# it), then reports and stops the electron.exe processes that this run launched and left running:
# owned-procs.ps1 records the run's own process tree by pid and creation time while it runs, and
# only a recorded process that is still alive, runs this checkout's ui/node_modules/electron/dist
# binary and started during the run is stopped. Never by name or by path alone, so Mat's own app
# and other sessions' apps keep running, even when they use this checkout's binary.
#   -Flag       runs the child with ELECTRON_RUN_AS_NODE=1 (AC-18) and DEBUG=pw:browser, so
#               electron.exe's stderr reaches the receipt (D-1030); otherwise both are unset.
#   -MinPassed  fails the run unless the receipt's last "N passed" line is at least this number.
#   -BaseExtra  fails the run unless it passed at least base-e2e-count.txt + this number.
#   -Clean      fails the run on any "N failed", "N flaky", "N did not run" or "N interrupted" line.
# The exit code is the child's, or 1 when a count check fails after a zero exit. A Red row passes
# a non-zero exit to red-check.py, so it never sets -MinPassed, -BaseExtra or -Clean.
[CmdletBinding(PositionalBinding = $false)]
param(
    [Parameter(Mandatory = $true)][string]$Receipt,
    [switch]$Flag,
    [int]$MinPassed = -1,
    [int]$BaseExtra = -1,
    [switch]$Clean,
    [Parameter(ValueFromRemainingArguments = $true)][string[]]$Files
)
$ErrorActionPreference = 'Continue'
$root = (git rev-parse --show-toplevel).Trim()
Set-Location $root
$plan = 'docs/execution/plans/2026-11-15-e2e-harness-hardening'
$tmp = 'C:\Temp\av-kit\e2e-harness-hardening\tmp'
New-Item -ItemType Directory -Force -Path $tmp | Out-Null
$env:TMP = $tmp
$env:TEMP = $tmp
$env:PYTHONIOENCODING = 'utf-8'
$env:RECEIPTS_DIR = 'C:/Temp/av-kit'
$env:ELECTRON_RUN_AS_NODE = $null
$env:DEBUG = $null
$electronDist = (Join-Path $root 'ui\node_modules\electron\dist\').Replace('/', '\')
$started = Get-Date
. (Join-Path $PSScriptRoot 'owned-procs.ps1')

$npm = @('npm', '--prefix', 'ui', 'run', 'test:e2e')
if ($Files.Count -gt 0) { $npm += @('--') + $Files }
$argv = $npm
if ($Flag) {
    $line = "`$env:ELECTRON_RUN_AS_NODE='1'; `$env:DEBUG='pw:browser'; " + ($npm -join ' ') + "; exit `$LASTEXITCODE"
    $argv = @('pwsh', '-NoProfile', '-Command', $line)
}
$run = Invoke-OwnedRun -Argv $argv -Receipt $Receipt
$code = $run.Code
$env:ELECTRON_RUN_AS_NODE = $null
$env:DEBUG = $null
Set-Content -Path "$Receipt.exit" -Value $code -Encoding ascii
Write-Output ("e2e-run flag={0} files={1} exit={2} receipt={3}" -f [bool]$Flag, ($Files -join ','), $code, $Receipt)
Get-Content $Receipt | Select-String -Pattern '^\s+\d+ (passed|failed|skipped|flaky|did not run|interrupted)' | Select-Object -Last 6

Stop-OwnedElectron -Label 'e2e-run' -Owned $run.Owned -Dist $electronDist -Started $started

if ($code -ne 0) { exit $code }
$passedLine = Select-String -Path $Receipt -Pattern '^\s+(\d+) passed' | Select-Object -Last 1
$passed = if ($null -eq $passedLine) { -1 } else { [int]$passedLine.Matches[0].Groups[1].Value }
$need = $MinPassed
if ($BaseExtra -ge 0) {
    if (-not (Test-Path "$plan/base-e2e-count.txt")) { Write-Output 'e2e-run: base-e2e-count.txt is missing; run row 0 first'; exit 1 }
    $need = [Math]::Max($need, [int](Get-Content "$plan/base-e2e-count.txt" -Raw).Trim() + $BaseExtra)
}
Write-Output ("e2e-run: passed={0} needed={1}" -f $passed, $need)
if ($need -ge 0 -and $passed -lt $need) { Write-Output 'e2e-run: fewer passed than needed'; exit 1 }
if ($Clean -and (Select-String -Path $Receipt -Pattern '^\s+\d+ (failed|flaky|did not run|interrupted)\s*$' -Quiet)) {
    Write-Output 'e2e-run: a failed, flaky, not-run or interrupted line'
    exit 1
}
if ($Flag -and (Select-String -Path $Receipt -Pattern 'bad option' -SimpleMatch -Quiet)) {
    Write-Output 'e2e-run: a "bad option" launch failure with ELECTRON_RUN_AS_NODE=1'
    exit 1
}
exit 0
