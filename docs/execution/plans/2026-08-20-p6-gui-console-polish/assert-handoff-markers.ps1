# Sole executable owner of HANDOFF_BUNDLE_MARKERS (plan named set).
$ErrorActionPreference = 'Stop'
$files = @(Get-ChildItem -Path '.agent/context/handoffs' -Filter '2026-08-20-p6-gui-console-polish-MEU-*-handoff.md')
if ($files.Count -ne 1) {
    Write-Error ("HANDOFF_COUNT mismatch, got " + $files.Count)
    exit 1
}
$markers = @(
    'Acceptance Criteria',
    'CACHE BOUNDARY',
    'FAIL_TO_PASS',
    'Changed Files',
    'Quality Gate Results',
    'Commands Executed',
    '## Evidence'
)
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
