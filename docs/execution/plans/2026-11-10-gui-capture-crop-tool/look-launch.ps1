# Session 60 look launch (task row 6, under D-522 A; implementation-plan.md LOOK_LAUNCH).
# Session 56's launch (docs/execution/plans/2026-11-08-light-accent-contrast/implementation-plan.md:332-333)
# on the app data look-seed.py built. Refuses to start when that app data is missing. Starts
# `npm run dev` in ui/ detached (Start-Process, no wait) with ELECTRON_RUN_AS_NODE cleared and
# AVKIT_APP_DATA set, then runs dev-app-procs.py record on the launched pwsh, so row 6 can later
# check and stop only this launch's processes by id. Exit = record's exit (1 is S6).
# Run from the repository root.
param([string]$Root = 'C:/Temp/av-kit/s60/look')
$ErrorActionPreference = 'Stop'
$repo = (git rev-parse --show-toplevel).Trim()
Set-Location $repo
$plan = 'docs/execution/plans/2026-11-10-gui-capture-crop-tool'
$receipts = 'C:/Temp/av-kit'
$appData = "$Root/app-data"
if (-not (Test-Path -LiteralPath "$appData/avkit.db" -PathType Leaf)) {
    Write-Output "look-launch: $appData/avkit.db is missing; run look-seed.py first"
    exit 1
}
New-Item -ItemType Directory -Force -Path "$receipts/s60" | Out-Null
$command = "Set-Location '$repo/ui'; `$env:ELECTRON_RUN_AS_NODE=`$null; `$env:AVKIT_APP_DATA='$appData'; npm run dev *> $receipts/s60-dev-app.txt"
$p = Start-Process pwsh -ArgumentList '-NoProfile', '-Command', $command -PassThru
Write-Output ("look-launch: started pwsh {0}; the app log is {1}/s60-dev-app.txt" -f $p.Id, $receipts)
$env:PYTHONIOENCODING = 'utf-8'
& rtk proxy uv run python "$plan/dev-app-procs.py" record --root-pid $p.Id --out "$receipts/s60/dev-app-launch.json" --roles electron,backend --wait 120 > "$receipts/s60-dev-app-record.txt" 2>&1
$code = $LASTEXITCODE
Get-Content "$receipts/s60-dev-app-record.txt"
Write-Output ("look-launch: record exit={0}" -f $code)
exit $code
