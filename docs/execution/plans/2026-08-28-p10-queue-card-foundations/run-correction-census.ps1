# Blast-radius census driver (plan-corrections.md Step 5c / plan-critical-review.md PR-6).
# Sweeps every literal named in correction-census.json across BOTH plan files, in ALL THREE
# directions -- old, new, AND variants -- one untruncated receipt per swept literal. Nothing is
# filtered or headed -- the whole point of a census is the hit you did not expect.
#
# The `variants` array is NOT optional decoration: a fixed-string sweep of `old`/`new` cannot find
# a rephrasing, so every other form the same value takes in this plan is declared there as its own
# searchable literal and swept like any other. A driver that iterates only old/new leaves the
# declared variants unswept while still printing PASS -- that is the exact defect Round 3 caught.
#
#   rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-08-28-p10-queue-card-foundations/run-correction-census.ps1 *> C:/Temp/av-kit/census-run.txt; $code=$LASTEXITCODE; Get-Content C:/Temp/av-kit/census-run.txt; exit $code
#
# rg exit codes: 0 = matched, 1 = no match, >1 = real execution/IO error. Only >1 is a failure.
# For an OLD literal, 1 is the good outcome (nothing stale left); for a NEW literal, 1 means the
# edit did not land where it was believed to. Both are reported, neither is silently swallowed.

$ErrorActionPreference = 'Stop'

$planDir = Split-Path -Parent $PSCommandPath
$repoRoot = (Resolve-Path -LiteralPath (Join-Path $planDir '../../../..')).Path
$plan = Join-Path $planDir 'implementation-plan.md'
$task = Join-Path $planDir 'task.md'
$spec = Get-Content (Join-Path $planDir 'correction-census.json') -Raw | ConvertFrom-Json

$outDir = 'C:/Temp/av-kit/census'
New-Item -ItemType Directory -Force -Path $outDir | Out-Null
Get-ChildItem -Path $outDir -Filter 'census-*.txt' -ErrorAction SilentlyContinue | Remove-Item -Force

$index = New-Object System.Collections.Generic.List[string]
$index.Add('slug|finding|direction|i|rc|hits|literal')  # direction in {old,new,variant}

$totalValues = 0
$totalLiterals = 0
$totalHits = 0
$hardFail = 0

foreach ($v in $spec.values) {
    $totalValues++
    foreach ($vt in @($v.variants)) {
        if ($null -eq $vt.literal -or [string]$vt.literal -eq '') {
            Write-Host ('CENSUS ERROR: ' + $v.slug + ' declares a variant with no literal')
            $hardFail++
        }
    }
    foreach ($dir in @('old', 'new', 'variant')) {
        # `old`/`new` hold bare strings; `variants` holds {literal, note} objects. Project both
        # onto a plain string array so the sweep below is identical for all three directions.
        if ($dir -eq 'variant') {
            $terms = @(@($v.variants) | ForEach-Object { [string]$_.literal })
        } else {
            $terms = @($v.$dir)
        }
        $terms = @($terms | Where-Object { $_ -ne $null -and $_ -ne '' })
        for ($i = 0; $i -lt $terms.Count; $i++) {
            $totalLiterals++
            $term = [string]$terms[$i]
            $receipt = Join-Path $outDir ('census-' + $v.slug + '-' + $dir + '-' + $i + '.txt')
            # -F: literal text, so regex metacharacters inside the value cannot silently
            # change what was searched for. No -m, no head, no Select-Object.
            & rg -F -n -- $term $plan $task *> $receipt
            $rc = $LASTEXITCODE
            if ($rc -gt 1) {
                Write-Host ('CENSUS ERROR rc=' + $rc + ' on ' + $v.slug + '/' + $dir + '/' + $i)
                Get-Content $receipt
                $hardFail++
                continue
            }
            $hits = 0
            if ($rc -eq 0) { $hits = @(Get-Content $receipt).Count }
            $totalHits += $hits
            $index.Add(($v.slug + '|' + $v.finding + '|' + $dir + '|' + $i + '|' + $rc + '|' + $hits + '|' + $term))
        }
    }
}

# ---- predicate census: AC counts per MEU must still equal RED_COUNT_4x after the F3/F4 AC rewrites.
$sets = Get-Content (Join-Path $planDir 'named-sets.json') -Raw | ConvertFrom-Json
$planText = Get-Content $plan -Raw
$predicate = New-Object System.Collections.Generic.List[string]
$predicate.Add('meu|declared RED_COUNT|AC rows found in plan|verdict')
foreach ($meu in @('41', '42', '43', '44')) {
    $declared = [int]$sets.("RED_COUNT_" + $meu)
    $found = ([regex]::Matches($planText, '(?m)^\| AC-' + $meu + '\.\d+ \|')).Count
    $verdict = if ($declared -eq $found) { 'MATCH' } else { 'MISMATCH'; }
    if ($declared -ne $found) { $hardFail++ }
    $predicate.Add($meu + '|' + $declared + '|' + $found + '|' + $verdict)
}
Set-Content -Path (Join-Path $outDir 'census-red-counts-predicate.txt') -Value $predicate -Encoding utf8

Set-Content -Path (Join-Path $outDir 'INDEX.txt') -Value $index -Encoding utf8

Write-Host ('Blast-radius census: ' + $totalValues + ' values changed, ' + $totalLiterals +
            ' literals swept (old+new+variant), ' + $totalHits + ' sites found.')
Write-Host ('Receipts: ' + $outDir + ' (INDEX.txt + one file per literal + census-red-counts-predicate.txt)')
foreach ($line in $predicate) { Write-Host ('  predicate ' + $line) }
if ($hardFail -gt 0) { Write-Host ('CENSUS FAILURES: ' + $hardFail); exit 1 }
Write-Host 'PASS: CORRECTION_CENSUS'
exit 0
