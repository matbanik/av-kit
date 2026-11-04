# Sole executable owner of the FAIL_TO_PASS RED gate (plan-review round 1, finding #6).
# A RED row passes ONLY when the suite exited nonzero AND the receipt carries the expected
# failing-test signatures. An unexpectedly green suite, an absent/empty receipt, or an
# unrelated compile/setup failure all FAIL this gate.
param(
    [Parameter(Mandatory = $true)][ValidateSet('dotnet', 'vitest')][string]$Suite,
    [int]$ExitCode = -1,
    [switch]$SelfTest
)
$ErrorActionPreference = 'Stop'
$setsPath = Join-Path $PSScriptRoot 'named-sets.json'
if (-not (Test-Path -LiteralPath $setsPath)) { Write-Error ('missing NAMED_SETS_FILE ' + $setsPath); exit 1 }
$sets = Get-Content -LiteralPath $setsPath -Raw | ConvertFrom-Json
if ($Suite -eq 'dotnet') {
    $receipt = [string]$sets.RED_DOTNET_RECEIPT
    $signatures = @($sets.RED_DOTNET_SIGNATURES)
} else {
    $receipt = [string]$sets.RED_VITEST_RECEIPT
    $signatures = @($sets.RED_VITEST_SIGNATURES)
}

function Test-Red {
    param([int]$Code, [string]$Path, [string[]]$Signatures)
    if ($Signatures.Count -lt 1) { return 'RED signature list empty for suite ' + $Suite }
    if ($Code -eq 0) { return 'RED phase requires a nonzero exit code; suite exited 0 (unexpectedly green)' }
    if (-not (Test-Path -LiteralPath $Path)) { return 'missing RED receipt ' + $Path }
    $text = Get-Content -LiteralPath $Path -Raw
    if ([string]::IsNullOrWhiteSpace($text)) { return 'empty RED receipt ' + $Path }
    foreach ($sig in $Signatures) {
        if ($text -notlike ('*' + $sig + '*')) {
            return 'RED receipt missing expected failure signature "' + $sig + '" (failure is unrelated to the new tests)'
        }
    }
    return $null
}

if ($SelfTest) {
    $tmp = Join-Path ([System.IO.Path]::GetTempPath()) ('red-selftest-' + [guid]::NewGuid().ToString('N') + '.txt')
    try {
        ($signatures -join ' ') | Set-Content -LiteralPath $tmp
        $good = Test-Red -Code 1 -Path $tmp -Signatures $signatures
        if ($null -ne $good) { Write-Error ('SELFTEST valid RED rejected: ' + $good); exit 1 }
        $green = Test-Red -Code 0 -Path $tmp -Signatures $signatures
        if ($null -eq $green) { Write-Error 'SELFTEST green suite accepted as RED'; exit 1 }
        'unrelated compiler error CS0103' | Set-Content -LiteralPath $tmp
        $unrelated = Test-Red -Code 1 -Path $tmp -Signatures $signatures
        if ($null -eq $unrelated) { Write-Error 'SELFTEST unrelated failure accepted as RED'; exit 1 }
        $absent = Test-Red -Code 1 -Path ($tmp + '.nope') -Signatures $signatures
        if ($null -eq $absent) { Write-Error 'SELFTEST missing receipt accepted as RED'; exit 1 }
        'PASS: RED_ORACLE self-test (' + $Suite + '): green / unrelated / absent all rejected'
        exit 0
    } finally {
        Remove-Item -LiteralPath $tmp -Force -ErrorAction SilentlyContinue
    }
}

$err = Test-Red -Code $ExitCode -Path $receipt -Signatures $signatures
if ($null -ne $err) { Write-Error $err; exit 1 }
'PASS: RED_ORACLE ' + $Suite + ' exit=' + $ExitCode + ' signatures=' + $signatures.Count
exit 0
