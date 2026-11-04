# Session 44 packaged probes on win-unpacked (task row 11; implementation-plan.md section 4).
# AC-110.13: Session 31b's plan_checks.py mcp-probe starts the MCP entry through av-kit.exe with
# ELECTRON_RUN_AS_NODE, on an empty app-data folder so a running app's backend.json can't matter.
# This script then checks the version the entry reported.
# AC-110.14: smoke_packaged_tts.py's offline phase on a copy of the packaged backend, because the
# phase refuses a backend inside the checkout. Its online phase rebuilds the onedir: never run it.
# Exit = the failing step's own code, or 30 for a wrong version.
$ErrorActionPreference = 'Stop'
$env:ELECTRON_RUN_AS_NODE = $null

$root = (git rev-parse --show-toplevel).Trim()
Set-Location -LiteralPath $root

$unpacked = 'ui/dist/win-unpacked'
$probeChecks = 'docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/plan_checks.py'
$probeOut = 'C:/Temp/av-kit/rc1/mcp-probe.json'
$probeAppData = 'C:/Temp/av-kit/rc1/mcp-probe-app-data'
$ttsRun = 'C:/Temp/av-kit/rc1/tts-run'
$ttsOut = 'C:/Temp/av-kit/rc1/tts-offline.json'

foreach ($stale in $probeOut, $probeAppData, $ttsRun, $ttsOut) {
    if (Test-Path -LiteralPath $stale) {
        Remove-Item -LiteralPath $stale -Recurse -Force
    }
}

Write-Output '== mcp-probe'
New-Item -ItemType Directory -Force -Path $probeAppData | Out-Null
$env:AVKIT_APP_DATA = $probeAppData
uv run --frozen python $probeChecks mcp-probe $probeOut "$unpacked/av-kit.exe" "$unpacked/resources/mcp-server/index.mjs"
$code = $LASTEXITCODE
$env:AVKIT_APP_DATA = $null
Write-Output "== mcp-probe exit=$code"
if ($code -ne 0) { exit $code }
$firstLine = (Get-Content -LiteralPath $probeOut -Raw | ConvertFrom-Json).first_stdout
Write-Output "mcp first line: $firstLine"
if ($firstLine -notmatch '"name":"av-kit","version":"0\.1\.0-rc\.1"') {
    Write-Output 'refused: the MCP entry did not report 0.1.0-rc.1'
    exit 30
}

Write-Output '== tts offline'
New-Item -ItemType Directory -Force -Path $ttsRun | Out-Null
Copy-Item -LiteralPath "$unpacked/resources/avkit-backend" -Destination "$ttsRun/avkit-backend" -Recurse
uv run --frozen python tools/smoke_packaged_tts.py --phase offline --models-dir C:/Temp/av-kit/s32-smoke-models --backend-dir "$ttsRun/avkit-backend" --out $ttsOut
$code = $LASTEXITCODE
Write-Output "== tts offline exit=$code"
exit $code
