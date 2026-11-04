# Prove each HANDOFFS entry contains the plan AC set for its MEU. Names from named-sets.json.
$ErrorActionPreference = 'Stop'
$setsPath = Join-Path $PSScriptRoot 'named-sets.json'
$planPath = Join-Path $PSScriptRoot 'implementation-plan.md'
$sets = Get-Content -LiteralPath $setsPath -Raw | ConvertFrom-Json
$plan = Get-Content -LiteralPath $planPath -Raw
$pairs = @(
    @{ re = 'AC-34\.[0-9]+'; f = '.agent/context/handoffs/' + $sets.HANDOFFS[0] },
    @{ re = 'AC-35\.[0-9]+'; f = '.agent/context/handoffs/' + $sets.HANDOFFS[1] },
    @{ re = 'AC-36\.[0-9]+'; f = '.agent/context/handoffs/' + $sets.HANDOFFS[2] }
)
foreach ($row in $pairs) {
    if (-not (Test-Path $row.f)) { Write-Error ('missing ' + $row.f); exit 1 }
    $planAcs = @([regex]::Matches($plan, $row.re) | ForEach-Object { $_.Value } | Sort-Object -Unique)
    $fileAcs = @([regex]::Matches((Get-Content $row.f -Raw), $row.re) | ForEach-Object { $_.Value } | Sort-Object -Unique)
    $missing = @(Compare-Object $planAcs $fileAcs | Where-Object SideIndicator -eq '<=')
    if ($missing) { $missing; Write-Error ($row.f + ' missing ACs'); exit 1 }
}
'PASS: per-MEU AC set from HANDOFFS'
exit 0
