# Require E2E_REQUIRED_CASES titles and E2E_TESTIDS in the Capture inbox spec.
$ErrorActionPreference = 'Stop'
$setsPath = Join-Path $PSScriptRoot 'named-sets.json'
$sets = Get-Content -LiteralPath $setsPath -Raw | ConvertFrom-Json
$spec = [string]$sets.E2E_SPEC
$idsFile = 'ui/tests/e2e/test-ids.ts'
if (-not (Test-Path -LiteralPath $spec)) {
    Write-Error ('missing E2E_SPEC ' + $spec)
    exit 1
}
$text = Get-Content -LiteralPath $spec -Raw
$idsText = Get-Content -LiteralPath $idsFile -Raw
$decl = [string]$sets.E2E_TEST_DECL
foreach ($case in @($sets.E2E_REQUIRED_CASES)) {
    $hit = $false
    foreach ($line in ($text -split "`r?`n")) {
        if ($line.Contains($decl) -and $line.Contains([string]$case)) {
            $hit = $true
            break
        }
    }
    if (-not $hit) {
        Write-Error ('E2E_SPEC missing test( declaration whose title contains ' + $case)
        exit 1
    }
}
foreach ($id in @($sets.E2E_TESTIDS)) {
    $token = [string]$id
    if ($idsText.IndexOf($token, [StringComparison]::Ordinal) -lt 0 -and $text.IndexOf($token, [StringComparison]::Ordinal) -lt 0) {
        Write-Error ('E2E testid unregistered: ' + $token)
        exit 1
    }
}
'PASS: E2E census'
exit 0
