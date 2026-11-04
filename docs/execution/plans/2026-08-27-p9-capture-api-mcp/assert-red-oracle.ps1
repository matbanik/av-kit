# Sole executable owner of RED_ORACLE_CHECK. Counts/prefixes come from named-sets.json.
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('py', 'ui')]
    [string]$Kind,
    [Parameter(Mandatory = $true)]
    [string]$Receipt,
    [string]$JsonReceipt,
    [Parameter(Mandatory = $true)]
    [ValidateSet('37', '38')]
    [string]$Meu
)
$ErrorActionPreference = 'Stop'
$setsPath = Join-Path $PSScriptRoot 'named-sets.json'
if (-not (Test-Path -LiteralPath $setsPath)) {
    Write-Error ("missing NAMED_SETS_FILE " + $setsPath)
    exit 1
}
$sets = Get-Content -LiteralPath $setsPath -Raw | ConvertFrom-Json
$Prefix = [string]$sets.("RED_PREFIX_" + $Meu)
$ExpectedCount = [int]$sets.("RED_COUNT_" + $Meu)
if ([string]::IsNullOrWhiteSpace($Prefix) -or $ExpectedCount -lt 1) {
    Write-Error ("named-sets missing RED_* for MEU-" + $Meu)
    exit 1
}
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

$ids = @(1..$ExpectedCount | ForEach-Object { $Prefix + '.' + $_ })
$names = New-Object System.Collections.Generic.List[string]
if ($Kind -eq 'ui' -and -not [string]::IsNullOrWhiteSpace($JsonReceipt)) {
    if (-not (Test-Path -LiteralPath $JsonReceipt)) {
        Write-Error ("missing RED_JSON " + $JsonReceipt)
        exit 1
    }
    $raw = Get-Content -LiteralPath $JsonReceipt -Raw
    if ([string]::IsNullOrWhiteSpace($raw)) {
        Write-Error ("empty RED_JSON " + $JsonReceipt)
        exit 1
    }
    $json = $raw | ConvertFrom-Json
    foreach ($suite in @($json.testResults)) {
        foreach ($a in @($suite.assertionResults)) {
            $name = [string]$a.fullName
            if ([string]::IsNullOrWhiteSpace($name)) { $name = [string]$a.title }
            if ([string]::IsNullOrWhiteSpace($name)) { continue }
            if ($a.status -and $a.status.ToString().ToLowerInvariant() -notin @('failed', 'fail')) {
                continue
            }
            $names.Add($name)
        }
    }
} else {
    foreach ($line in ($text -split "`r?`n")) {
        if ($line -match 'FAILED|AssertionError|FAIL ') {
            $names.Add($line)
        }
    }
}

foreach ($id in $ids) {
    $pattern = [regex]::Escape($id) + '(?![0-9])'
    $hits = @($names | Where-Object { $_ -match $pattern })
    if ($hits.Count -lt 1) {
        Write-Error ("RED_ORACLE missing failed title for " + $id)
        exit 1
    }
}

$allMapped = @()
foreach ($name in $names) {
    $mapped = @($ids | Where-Object { $name -match ([regex]::Escape($_) + '(?![0-9])') })
    if ($mapped.Count -gt 1) {
        Write-Error ("RED_ORACLE multi-id title: " + $name)
        exit 1
    }
    if ($mapped.Count -eq 1) { $allMapped += $mapped[0] }
}
$unique = @($allMapped | Sort-Object -Unique)
if ($unique.Count -ne $ExpectedCount) {
    Write-Error ("RED_ORACLE expected " + $ExpectedCount + " distinct " + $Prefix + ".* failed titles, got " + $unique.Count)
    exit 1
}

'PASS: RED_ORACLE ' + $Kind + ' MEU-' + $Meu + ' ' + $Prefix + ' count=' + $ExpectedCount
exit 0
