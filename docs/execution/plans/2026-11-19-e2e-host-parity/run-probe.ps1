# Session 97 (task row 1): runs hover-probe.mjs or fidelity-probe.mjs with ELECTRON_RUN_AS_NODE
# removed, from this plan folder. It prints the probe's JSON lines and exits with the probe's exit.
param(
    [Parameter(Mandatory = $true)][ValidateSet('hover', 'fidelity')][string]$Probe
)
$ErrorActionPreference = 'Stop'
Remove-Item Env:ELECTRON_RUN_AS_NODE -ErrorAction SilentlyContinue
Set-Location -LiteralPath $PSScriptRoot
& node (Join-Path $PSScriptRoot "$Probe-probe.mjs")
"probe exit=$LASTEXITCODE"
exit $LASTEXITCODE
