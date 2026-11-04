# A-4 (Mat chose option 1, 2026-10-16): the ui-tests baseline rule, called by session-gate.ps1.
# Zorivest 1f254832 (MEU-662, its main, 2026-10-16 21:30) darkened three light status hexes that
# queue-canon.test.ts AC-41.3 reads live from P:/zorivest, so AC-41.3 fails on av-kit main as well;
# the re-port is known issue QUEUE-PILL-TOKEN-DRIFT. A Vitest exit 1 passes only when every
# `FAIL  <file> > ... > <test>` id is listed in $Baseline, the summary's failed-test count equals
# the number of those ids, and there is no unhandled error. Anything else fails the step.
# Exit 0 = baseline-only failures; exit 1 = any failure outside the baseline.
param(
    [Parameter(Mandatory = $true)][string]$Receipt,
    [Parameter(Mandatory = $true)][string]$Baseline
)
$ansi = [regex]'\x1b\[[0-9;]*m'
$lines = @(Get-Content $Receipt | ForEach-Object { $ansi.Replace($_, '') })
$listed = @(Get-Content $Baseline | ForEach-Object { $_.Trim() } | Where-Object { $_ })
$failed = @($lines | Where-Object { $_ -match '^\s*FAIL\s+(\S.*?)\s*$' } | ForEach-Object { ($_ -replace '^\s*FAIL\s+', '').Trim() } | Sort-Object -Unique)
$summary = @($lines | Where-Object { $_ -match '^\s*Tests\s+(\d+) failed' } | ForEach-Object { [int]([regex]::Match($_, 'Tests\s+(\d+) failed').Groups[1].Value) })
$summaryFailed = if ($summary.Count -gt 0) { $summary[-1] } else { -1 }
$unhandled = @($lines | Where-Object { $_ -match 'Unhandled (Error|Rejection)|^\s*Errors\s+\d+ error' })
$outside = @($failed | Where-Object { $listed -notcontains $_ })
Write-Output ("ui-tests baseline rule: failed={0} summary_failed={1} outside_baseline=[{2}] unhandled={3}" -f $failed.Count, $summaryFailed, ($outside -join ' | '), $unhandled.Count)
if ($failed.Count -gt 0 -and $failed.Count -eq $summaryFailed -and $outside.Count -eq 0 -and $unhandled.Count -eq 0) {
    Write-Output 'ui-tests: every failure is in baseline-ui-failed.txt; not a regression'
    exit 0
}
exit 1
