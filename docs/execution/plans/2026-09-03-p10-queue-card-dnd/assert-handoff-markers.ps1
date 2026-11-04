<#
.SYNOPSIS
  HANDOFF_MARKER_CHECK - sole executable owner of HANDOFF_BUNDLE_MARKERS.

.DESCRIPTION
  Every name, count, glob and marker string comes from this plan's
  named-sets.json (single-statement rule); nothing is spelled twice here.

  Two modes:
    (no argument)  every HANDOFFS entry exists, the directory holds exactly
                   HANDOFF_COUNT files matching HANDOFF_FILTER, and each carries
                   every HANDOFF_BUNDLE_MARKERS entry. This is the closeout form.
    -Only <name>   one handoff, for the per-MEU task rows that run before the
                   later MEUs' handoffs exist. The name must be a HANDOFFS member.

  ABSENT_VALIDATOR_RULE: tools/validate_closeout_artifacts.py does not exist in
  this tree. This plan-local script is the check, and it is created (row 9a)
  before the first row that invokes it (row 10).

.PARAMETER Only
  A single handoff filename (not a path) to check instead of the whole set.

.PARAMETER Root
  Repository root. Overridden by -SelfTest to point at a fixture tree.

.PARAMETER SelfTest
  Build a fixture tree and prove the gate FAILS on a handoff that is missing one
  HANDOFF_BUNDLE_MARKERS entry, and PASSES on the same tree once it is restored.
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

$expected = @($sets.HANDOFFS.value)
$expectedCount = [int]$sets.HANDOFF_COUNT.value
$filter = [string]$sets.HANDOFF_FILTER.value
$markers = @($sets.HANDOFF_BUNDLE_MARKERS.value)

if ($markers.Count -lt 1) {
    Write-Error 'HANDOFF_BUNDLE_MARKERS is empty'
    exit 1
}
if ($expected.Count -ne $expectedCount) {
    Write-Error ('named-sets self-inconsistent: HANDOFFS has ' + $expected.Count + ' entries, HANDOFF_COUNT says ' + $expectedCount)
    exit 1
}

if ([string]::IsNullOrWhiteSpace($Root)) {
    $Root = (Resolve-Path (Join-Path $PSScriptRoot '../../../..')).Path
}
$handoffDir = Join-Path $Root '.agent/context/handoffs'

function Test-Markers {
    param([string]$Path, [string]$Name)
    $text = Get-Content -LiteralPath $Path -Raw
    $missing = @()
    foreach ($marker in $markers) {
        if ($text.IndexOf($marker, [StringComparison]::Ordinal) -lt 0) {
            $missing += $marker
        }
    }
    if ($missing.Count -gt 0) {
        Write-Error ($Name + ' is missing HANDOFF_BUNDLE_MARKERS: ' + ($missing -join ', '))
        return $false
    }
    Write-Host ('  ok  ' + $Name + '  (' + $markers.Count + ' markers)')
    return $true
}

function Invoke-Gate {
    param([string[]]$GateArgs)
    $childArgs = @('-NoProfile', '-File', $PSCommandPath) + $GateArgs
    & pwsh @childArgs *> $null
    return $LASTEXITCODE
}

if ($SelfTest) {
    $tmp = Join-Path ([System.IO.Path]::GetTempPath()) ('handoff-markers-selftest-' + [guid]::NewGuid().ToString('N'))
    $fixtureDir = Join-Path $tmp '.agent/context/handoffs'
    New-Item -ItemType Directory -Path $fixtureDir -Force | Out-Null
    try {
        foreach ($name in $expected) {
            $body = "---`nverdict: n/a`n---`n`n" + (($markers | ForEach-Object { '## ' + $_ }) -join "`n") + "`n"
            Set-Content -LiteralPath (Join-Path $fixtureDir $name) -Value $body -Encoding UTF8
        }
        $positive = Invoke-Gate @('-Root', $tmp)
        if ($positive -ne 0) {
            Write-Error ('self-test fixture should PASS but exited ' + $positive)
            exit 1
        }
        Write-Host '  PASS  complete fixture passes'

        # Seeded negative: drop exactly one marker from the first handoff.
        $victimName = $expected[0]
        $victim = Join-Path $fixtureDir $victimName
        $dropped = $markers[$markers.Count - 1]
        $text = (Get-Content -LiteralPath $victim -Raw).Replace('## ' + $dropped, '## (removed)')
        Set-Content -LiteralPath $victim -Value $text -Encoding UTF8
        $negative = Invoke-Gate @('-Root', $tmp)
        if ($negative -eq 0) {
            Write-Error ('seeded negative PASSED: ' + $victimName + ' lost marker "' + $dropped + '" and the gate did not notice')
            exit 1
        }
        Write-Host ('  PASS  seeded negative fails (dropped "' + $dropped + '" from ' + $victimName + ')')

        # The same negative must also fail through -Only, which the per-MEU rows use.
        $negativeOnly = Invoke-Gate @('-Root', $tmp, '-Only', $victimName)
        if ($negativeOnly -eq 0) {
            Write-Error '-Only PASSED on the seeded negative'
            exit 1
        }
        Write-Host '  PASS  seeded negative fails through -Only'
    }
    finally {
        Remove-Item -LiteralPath $tmp -Recurse -Force -ErrorAction SilentlyContinue
    }
    'SELFTEST PASS: HANDOFF_MARKER_CHECK'
    exit 0
}

if (-not [string]::IsNullOrWhiteSpace($Only)) {
    if ($expected -notcontains $Only) {
        Write-Error ('-Only ' + $Only + ' is not a HANDOFFS member: ' + ($expected -join ', '))
        exit 1
    }
    $path = Join-Path $handoffDir $Only
    if (-not (Test-Path -LiteralPath $path)) {
        Write-Error ('missing handoff ' + $path)
        exit 1
    }
    if (-not (Test-Markers -Path $path -Name $Only)) { exit 1 }
    'PASS: HANDOFF_MARKER_CHECK -Only ' + $Only
    exit 0
}

if (-not (Test-Path -LiteralPath $handoffDir)) {
    Write-Error ('missing handoff directory ' + $handoffDir)
    exit 1
}
$files = @(Get-ChildItem -Path $handoffDir -Filter $filter -File)
if ($files.Count -ne $expectedCount) {
    Write-Error ('HANDOFF_COUNT mismatch: ' + $filter + ' matched ' + $files.Count + ', expected ' + $expectedCount)
    exit 1
}
$got = @($files.Name | Sort-Object)
$want = @($expected | Sort-Object)
if (@(Compare-Object -ReferenceObject $want -DifferenceObject $got).Count -ne 0) {
    Write-Error ('HANDOFFS mismatch: found ' + ($got -join ', '))
    exit 1
}
$failed = 0
foreach ($file in $files) {
    if (-not (Test-Markers -Path $file.FullName -Name $file.Name)) { $failed += 1 }
}
if ($failed -gt 0) { exit 1 }
'PASS: HANDOFF_MARKER_CHECK ' + $files.Count + ' handoffs x ' + $markers.Count + ' markers'
exit 0
