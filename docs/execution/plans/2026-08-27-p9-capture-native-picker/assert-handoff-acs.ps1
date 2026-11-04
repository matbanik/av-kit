# Prove HANDOFFS[0] contains the full plan AC set. Names/count from named-sets.json.
# Totality guard: the plan itself must expose exactly AC_COUNT distinct ACs matching
# AC_IDS, so a drifted or empty extraction can never pass vacuously.
$ErrorActionPreference = 'Stop'
$setsPath = Join-Path $PSScriptRoot 'named-sets.json'
if (-not (Test-Path -LiteralPath $setsPath)) { Write-Error ('missing NAMED_SETS_FILE ' + $setsPath); exit 1 }
$sets = Get-Content -LiteralPath $setsPath -Raw | ConvertFrom-Json
$planPath = [string]$sets.PLAN_FILE
$expectedCount = [int]$sets.AC_COUNT
$expectedIds = @($sets.AC_IDS | Sort-Object -Unique)
$re = [regex]::Escape([string]$sets.AC_PREFIX) + '\.[0-9]+'

if (-not (Test-Path -LiteralPath $planPath)) { Write-Error ('missing PLAN_FILE ' + $planPath); exit 1 }
# The plan keeps a retirement record naming the ACs deleted with their surface
# (round-11), so a raw token sweep of the plan sees dead IDs alongside live ones.
# RETIRED_ACS is the declared dead set: it is subtracted before the totality check,
# and both halves are asserted, so neither a resurrected AC nor a lost retirement
# record can slip through.
$retired = @($sets.RETIRED_ACS | Sort-Object -Unique)
if ($retired.Count -lt 1) { Write-Error 'RETIRED_ACS missing or empty'; exit 1 }
$overlap = @($retired | Where-Object { $expectedIds -contains $_ })
if ($overlap.Count -ne 0) {
    Write-Error ('RETIRED_ACS overlaps AC_IDS: ' + ($overlap -join ','))
    exit 1
}

$plan = Get-Content -LiteralPath $planPath -Raw
$planAll = @([regex]::Matches($plan, $re) | ForEach-Object { $_.Value } | Sort-Object -Unique)
$lostRetirements = @($retired | Where-Object { $planAll -notcontains $_ })
if ($lostRetirements.Count -ne 0) {
    Write-Error ('plan no longer records retired AC(s): ' + ($lostRetirements -join ','))
    exit 1
}
$planAcs = @($planAll | Where-Object { $retired -notcontains $_ })
if ($planAcs.Count -ne $expectedCount) {
    Write-Error ('plan exposes ' + $planAcs.Count + ' ACs, expected AC_COUNT ' + $expectedCount)
    exit 1
}
if (@(Compare-Object $planAcs $expectedIds).Count -ne 0) {
    Write-Error ('plan AC set does not equal AC_IDS: ' + ($planAcs -join ','))
    exit 1
}

$handoff = '.agent/context/handoffs/' + $sets.HANDOFFS[0]
if (-not (Test-Path -LiteralPath $handoff)) { Write-Error ('missing ' + $handoff); exit 1 }
$fileAcs = @([regex]::Matches((Get-Content -LiteralPath $handoff -Raw), $re) | ForEach-Object { $_.Value } | Sort-Object -Unique)
$missing = @(Compare-Object $planAcs $fileAcs | Where-Object SideIndicator -eq '<=')
if ($missing.Count -ne 0) {
    $missing | ForEach-Object { $_.InputObject }
    Write-Error ($handoff + ' missing ' + $missing.Count + ' ACs')
    exit 1
}
'PASS: HANDOFF_AC_SET ' + $planAcs.Count + ' live ACs, ' + $retired.Count + ' retired'
exit 0
