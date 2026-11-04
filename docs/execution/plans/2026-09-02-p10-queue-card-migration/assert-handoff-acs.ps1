<#
.SYNOPSIS
  HANDOFF_AC_CHECK - each HANDOFFS entry carries its MEU's full plan AC set.

.DESCRIPTION
  The MEU -> AC-id-regex mapping is HANDOFF_AC_PATTERNS in named-sets.json, and
  the handoff filenames are HANDOFFS; neither is spelled again here. For each
  pair the script collects every distinct AC id the implementation plan states
  for that MEU and requires the handoff to mention all of them. An AC that the
  plan defines but the handoff never reports is exactly the evidence gap the
  Execution Contract's "evidence-first completion" rule forbids.

  -Only restricts the run to one MEU key, for the per-MEU rows that execute
  before the later handoffs exist.

  ABSENT_VALIDATOR_RULE: tools/validate_closeout_artifacts.py does not exist in
  this tree; this plan-local script is the check.

.PARAMETER Only
  A single HANDOFF_AC_PATTERNS key, e.g. MEU-45.

.PARAMETER Root
  Repository root. Overridden by -SelfTest to point at a fixture tree.

.PARAMETER SelfTest
  Prove the gate FAILS on a handoff that dropped one AC id, and PASSES once the
  same fixture reports the complete set.
#>
[CmdletBinding()]
param(
    [string]$Only,
    [string]$Root,
    [switch]$SelfTest
)

$ErrorActionPreference = 'Stop'

$setsPath = Join-Path $PSScriptRoot 'named-sets.json'
if (-not (Test-Path -LiteralPath $setsPath)) {
    Write-Error ('missing NAMED_SETS_FILE ' + $setsPath)
    exit 1
}
$sets = Get-Content -LiteralPath $setsPath -Raw | ConvertFrom-Json

$handoffs = @($sets.HANDOFFS.value)
$patterns = $sets.HANDOFF_AC_PATTERNS.value
$meuKeys = @($patterns.PSObject.Properties.Name)
if ($meuKeys.Count -lt 1) {
    Write-Error 'HANDOFF_AC_PATTERNS is empty'
    exit 1
}
if ($meuKeys.Count -ne $handoffs.Count) {
    Write-Error ('HANDOFF_AC_PATTERNS has ' + $meuKeys.Count + ' keys but HANDOFFS has ' + $handoffs.Count + ' entries')
    exit 1
}

if ([string]::IsNullOrWhiteSpace($Root)) {
    $Root = (Resolve-Path (Join-Path $PSScriptRoot '../../../..')).Path
}
# `project` is a bare string in this named-sets file while the rule entries are
# {value, source} objects, so accept either shape and fall back to the plan
# folder this script lives in.
$project = if ($sets.project -is [string]) { $sets.project } else { [string]$sets.project.value }
if ([string]::IsNullOrWhiteSpace($project)) { $project = Split-Path -Leaf $PSScriptRoot }
$planRel = 'docs/execution/plans/' + $project + '/implementation-plan.md'
$planPath = Join-Path $Root $planRel
if (-not (Test-Path -LiteralPath $planPath)) {
    Write-Error ('missing implementation plan ' + $planPath)
    exit 1
}
$plan = Get-Content -LiteralPath $planPath -Raw

# HANDOFFS is ordered by MEU, and so are the pattern keys; pair them by index so
# the mapping has one home rather than a second literal table here.
$pairs = @()
for ($i = 0; $i -lt $meuKeys.Count; $i++) {
    $pairs += [pscustomobject]@{
        Meu     = $meuKeys[$i]
        Pattern = [string]$patterns.($meuKeys[$i])
        Handoff = $handoffs[$i]
    }
}

function Get-AcIds {
    param([string]$Text, [string]$Pattern)
    return @([regex]::Matches($Text, $Pattern) | ForEach-Object { $_.Value } | Sort-Object -Unique)
}

function Invoke-Check {
    param([object[]]$Rows)
    $failed = 0
    foreach ($row in $Rows) {
        $path = Join-Path (Join-Path $Root '.agent/context/handoffs') $row.Handoff
        if (-not (Test-Path -LiteralPath $path)) {
            Write-Error ('missing handoff ' + $path)
            $failed += 1
            continue
        }
        $planAcs = Get-AcIds -Text $plan -Pattern $row.Pattern
        if ($planAcs.Count -lt 1) {
            Write-Error ('implementation plan states no ' + $row.Meu + ' ACs for pattern ' + $row.Pattern)
            $failed += 1
            continue
        }
        $handoffAcs = Get-AcIds -Text (Get-Content -LiteralPath $path -Raw) -Pattern $row.Pattern
        $missing = @($planAcs | Where-Object { $handoffAcs -notcontains $_ })
        if ($missing.Count -gt 0) {
            Write-Error ($row.Handoff + ' is missing ' + $missing.Count + ' ' + $row.Meu + ' ACs: ' + ($missing -join ', '))
            $failed += 1
            continue
        }
        Write-Host ('  ok  ' + $row.Meu + '  ' + $planAcs.Count + ' ACs in ' + $row.Handoff)
    }
    return $failed
}

function Invoke-Gate {
    param([string[]]$GateArgs)
    $childArgs = @('-NoProfile', '-File', $PSCommandPath) + $GateArgs
    & pwsh @childArgs *> $null
    return $LASTEXITCODE
}

if ($SelfTest) {
    $tmp = Join-Path ([System.IO.Path]::GetTempPath()) ('handoff-acs-selftest-' + [guid]::NewGuid().ToString('N'))
    $fixtureHandoffs = Join-Path $tmp '.agent/context/handoffs'
    $fixturePlan = Join-Path $tmp (Split-Path -Parent $planRel)
    New-Item -ItemType Directory -Path $fixtureHandoffs -Force | Out-Null
    New-Item -ItemType Directory -Path $fixturePlan -Force | Out-Null
    try {
        Copy-Item -LiteralPath $planPath -Destination (Join-Path $tmp $planRel) -Force
        foreach ($row in $pairs) {
            $ids = Get-AcIds -Text $plan -Pattern $row.Pattern
            Set-Content -LiteralPath (Join-Path $fixtureHandoffs $row.Handoff) -Value (($ids | ForEach-Object { '- ' + $_ + ' met' }) -join "`n") -Encoding UTF8
        }
        $positive = Invoke-Gate @('-Root', $tmp)
        if ($positive -ne 0) {
            Write-Error ('complete fixture should PASS but exited ' + $positive)
            exit 1
        }
        Write-Host '  PASS  complete fixture passes'

        # Seeded negative: drop the last AC id from the first handoff.
        $victim = $pairs[0]
        $victimPath = Join-Path $fixtureHandoffs $victim.Handoff
        $ids = Get-AcIds -Text $plan -Pattern $victim.Pattern
        $dropped = $ids[$ids.Count - 1]
        $kept = @($ids | Where-Object { $_ -ne $dropped })
        Set-Content -LiteralPath $victimPath -Value (($kept | ForEach-Object { '- ' + $_ + ' met' }) -join "`n") -Encoding UTF8
        $negative = Invoke-Gate @('-Root', $tmp)
        if ($negative -eq 0) {
            Write-Error ('seeded negative PASSED: ' + $victim.Handoff + ' dropped ' + $dropped + ' and the gate did not notice')
            exit 1
        }
        Write-Host ('  PASS  seeded negative fails (dropped ' + $dropped + ' from ' + $victim.Handoff + ')')

        $negativeOnly = Invoke-Gate @('-Root', $tmp, '-Only', $victim.Meu)
        if ($negativeOnly -eq 0) {
            Write-Error '-Only PASSED on the seeded negative'
            exit 1
        }
        Write-Host '  PASS  seeded negative fails through -Only'
    }
    finally {
        Remove-Item -LiteralPath $tmp -Recurse -Force -ErrorAction SilentlyContinue
    }
    'SELFTEST PASS: HANDOFF_AC_CHECK'
    exit 0
}

$rows = $pairs
if (-not [string]::IsNullOrWhiteSpace($Only)) {
    $rows = @($pairs | Where-Object { $_.Meu -eq $Only })
    if ($rows.Count -ne 1) {
        Write-Error ('-Only ' + $Only + ' is not a HANDOFF_AC_PATTERNS key: ' + ($meuKeys -join ', '))
        exit 1
    }
}
$failed = Invoke-Check -Rows $rows
if ($failed -gt 0) { exit 1 }
'PASS: HANDOFF_AC_CHECK ' + $rows.Count + ' MEU(s)'
exit 0
