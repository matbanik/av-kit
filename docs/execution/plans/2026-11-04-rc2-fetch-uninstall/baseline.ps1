# Session 49 baseline (task row 0; implementation-plan.md §Verification Plan 1).
# Records HEAD and the dirty tree, keeps RC1's installer as RC1_INSTALLER before anything can
# overwrite it, requires RC1's unpacked app (row 4 repackages it), installs from the locks and
# captures the base suites. The base suites' own failures are recorded, not fatal: the session
# gate excuses only the ids this receipt shows failing. Every other step is fail-fast.
# Run from the repository root.
$ErrorActionPreference = 'Stop'
$root = (git rev-parse --show-toplevel).Trim()
Set-Location $root
$plan = 'docs/execution/plans/2026-11-04-rc2-fetch-uninstall'
$receipts = 'C:/Temp/av-kit'
$rc2 = "$receipts/rc2"
$rc1Source = 'ui/dist/av-kit-Setup-0.1.0-rc.1.exe'
$rc1Installer = "$rc2/rc1-installer.exe"
$rc1Sha = 'beabc50990e10c30afe8895170fd7fa3deedf622b182b5d343cc5f3aa09768a7'
$env:ELECTRON_RUN_AS_NODE = $null
# RC1 ECN-2 (CLOSEOUT-SELFTEST-ANCESTOR-AGENT-DIR): keep pytest's temp dirs away from C:/Users/Mat/.agent.
$tmp = "$rc2/tmp"
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
Write-Output ("baseline-dirty.txt {0} paths" -f (Get-Content "$plan/baseline-dirty.txt").Count)

if (-not (Test-Path $rc1Source)) { Write-Output "missing $rc1Source"; exit 10 }
if (Test-Path $rc1Installer) {
    Write-Output "RC1_INSTALLER exists already; not overwritten"
} else {
    Copy-Item -LiteralPath $rc1Source -Destination $rc1Installer
}
$sha = (Get-FileHash -Algorithm SHA256 -LiteralPath $rc1Installer).Hash.ToLowerInvariant()
Write-Output "RC1_INSTALLER sha256 $sha"
if ($sha -ne $rc1Sha) { Write-Output "RC1_INSTALLER sha256 mismatch, expected $rc1Sha"; exit 11 }
if (-not (Test-Path 'ui/dist/win-unpacked/av-kit.exe')) { Write-Output 'missing ui/dist/win-unpacked/av-kit.exe'; exit 12 }
Write-Output 'ui/dist/win-unpacked/av-kit.exe present'

Invoke-Step 'uv-sync' @('uv', 'sync', '--frozen', '--all-packages')
Invoke-Step 'ui-ci' @('npm', '--prefix', 'ui', 'ci')
Invoke-Step 'electron-install' @('node', 'ui/node_modules/electron/install.js')
Invoke-Step 'mcp-ci' @('npm', '--prefix', 'mcp-server', 'ci')
Invoke-Step 'mcp-build' @('npm', '--prefix', 'mcp-server', 'run', 'build')

& rtk proxy uv run pytest tests/ --tb=short -q -rfE *> "$receipts/s49-base-py.txt"
Write-Output ("base suite py exit={0} receipt={1}/s49-base-py.txt" -f $LASTEXITCODE, $receipts)
Get-Content "$receipts/s49-base-py.txt" | Select-String -Pattern '^FAILED |^ERROR |passed|failed' | Select-Object -Last 12
& rtk proxy npm --prefix ui run test *> "$receipts/s49-base-ui.txt"
Write-Output ("base suite ui exit={0} receipt={1}/s49-base-ui.txt" -f $LASTEXITCODE, $receipts)
Get-Content "$receipts/s49-base-ui.txt" | Select-Object -Last 6

Invoke-Step 'red-check-selftest' @('uv', 'run', 'python', "$plan/red-check.py", '--selftest')
Invoke-Step 'identity-selftest' @('uv', 'run', 'python', "$plan/identity.py", '--selftest')
Write-Output 'baseline: all steps exit 0'
exit 0
