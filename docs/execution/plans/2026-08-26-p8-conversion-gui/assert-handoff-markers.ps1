# Sole executable owner of HANDOFF_BUNDLE_MARKERS. Names/count come from named-sets.json.
$ErrorActionPreference = 'Stop'
$setsPath = Join-Path $PSScriptRoot 'named-sets.json'
if (-not (Test-Path -LiteralPath $setsPath)) {
    Write-Error ("missing NAMED_SETS_FILE " + $setsPath)
    exit 1
}
$sets = Get-Content -LiteralPath $setsPath -Raw | ConvertFrom-Json
$expectedCount = [int]$sets.HANDOFF_COUNT
$expected = @($sets.HANDOFFS)
$filter = [string]$sets.HANDOFF_FILTER
$files = @(Get-ChildItem -Path '.agent/context/handoffs' -Filter $filter)
if ($files.Count -ne $expectedCount) {
    Write-Error ("HANDOFF_COUNT mismatch, got " + $files.Count + " expected " + $expectedCount)
    exit 1
}
$got = @($files.Name | Sort-Object)
$want = @($expected | Sort-Object)
if (@(Compare-Object $got $want).Count -ne 0) {
    Write-Error ("HANDOFF_GLOB mismatch: " + ($got -join ','))
    exit 1
}
$markers = @($sets.HANDOFF_BUNDLE_MARKERS)
if ($markers.Count -lt 1) {
    Write-Error 'HANDOFF_BUNDLE_MARKERS empty'
    exit 1
}
foreach ($f in $files) {
    foreach ($pattern in $markers) {
        if (-not (Select-String -Path $f.FullName -Pattern $pattern -Quiet)) {
            Write-Error ('missing ' + $pattern + ' in ' + $f.Name)
            exit 1
        }
    }
}
'PASS: HANDOFF_MARKER_CHECK'
exit 0
