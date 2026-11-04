# Prove each HANDOFFS entry contains the plan AC set for its MEU. Names from named-sets.json.
$ErrorActionPreference = 'Stop'
$setsPath = Join-Path $PSScriptRoot 'named-sets.json'
$sets = Get-Content -LiteralPath $setsPath -Raw | ConvertFrom-Json
$planPath = [string]$sets.PLAN_FOLDER + '/implementation-plan.md'
$plan = Get-Content -LiteralPath $planPath -Raw
$pattern = [string]$sets.HANDOFF_AC_PATTERNS.'MEU-61'
$handoff = '.agent/context/handoffs/' + $sets.HANDOFFS[0]
if (-not (Test-Path -LiteralPath $handoff)) {
    Write-Error ('missing ' + $handoff)
    exit 1
}
$planAcs = @([regex]::Matches($plan, $pattern) | ForEach-Object { $_.Value } | Sort-Object -Unique)
$fileAcs = @([regex]::Matches((Get-Content -LiteralPath $handoff -Raw), $pattern) | ForEach-Object { $_.Value } | Sort-Object -Unique)
$missing = @(Compare-Object $planAcs $fileAcs | Where-Object SideIndicator -eq '<=')
if ($missing) {
    $missing
    Write-Error ($handoff + ' missing ACs')
    exit 1
}
'PASS: per-MEU AC set from HANDOFFS'
exit 0
