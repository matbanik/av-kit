# Sole executable owner of RED_ORACLE (plan named set).
# Proves a Red receipt is a missing-module / failed-assertion oracle, not a
# collection, config, or toolchain failure.
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('py', 'ui')]
    [string]$Kind,
    [Parameter(Mandatory = $true)]
    [string]$Receipt
)
$ErrorActionPreference = 'Stop'
if (-not (Test-Path -LiteralPath $Receipt)) {
    Write-Error ("missing RED receipt " + $Receipt)
    exit 1
}
$text = Get-Content -LiteralPath $Receipt -Raw
if ([string]::IsNullOrWhiteSpace($text)) {
    Write-Error ("empty RED receipt " + $Receipt)
    exit 1
}

$deny = @(
    'ERROR collecting',
    'INTERNALERROR',
    'no tests ran',
    'No test files found',
    'failed to resolve config',
    'ERR_LOAD_CONFIG',
    'Cannot find package',
    'command not found',
    'is not recognized'
)
# Missing-module collection is the intended Python Red (M5). Allow that one deny-exception.
$pyModule = "ModuleNotFoundError: No module named 'avkit_api'"
foreach ($d in $deny) {
    if ($text -match [regex]::Escape($d)) {
        if ($Kind -eq 'py' -and $d -eq 'ERROR collecting' -and $text.Contains($pyModule)) {
            continue
        }
        Write-Error ("RED_ORACLE deny: " + $d)
        exit 1
    }
}

if ($Kind -eq 'py') {
    $allow = @('FAILED', 'AssertionError', $pyModule)
} else {
    $allow = @('FAIL', 'AssertionError', 'Cannot find module')
}
$hit = $false
foreach ($a in $allow) {
    if ($text.Contains($a)) { $hit = $true; break }
}
if (-not $hit) {
    Write-Error ('RED_ORACLE missing allow-marker for ' + $Kind)
    exit 1
}
'PASS: RED_ORACLE ' + $Kind
exit 0
