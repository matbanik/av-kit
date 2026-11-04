# Sole executable owner of RED_ORACLE_CHECK for MEU-59. IDs come from named-sets.json.
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('py', 'ui', 'mcp')]
    [string]$Kind,
    [Parameter(Mandatory = $true)]
    [string]$Receipt,
    [string]$JsonReceipt
)
$ErrorActionPreference = 'Stop'
$setsPath = Join-Path $PSScriptRoot 'named-sets.json'
if (-not (Test-Path -LiteralPath $setsPath)) {
    Write-Error ('missing NAMED_SETS_FILE ' + $setsPath)
    exit 1
}
$sets = Get-Content -LiteralPath $setsPath -Raw | ConvertFrom-Json
$Prefix = [string]$sets.RED_PREFIX_59
if ($Kind -eq 'ui') {
    $ids = @($sets.RED_AC_IDS_UI)
    $ExpectedCount = [int]$sets.RED_COUNT_59_UI
} elseif ($Kind -eq 'mcp') {
    $ids = @($sets.RED_AC_IDS_MCP)
    $ExpectedCount = [int]$sets.RED_COUNT_59_MCP
} else {
    $ids = @($sets.RED_AC_IDS_PY)
    $ExpectedCount = [int]$sets.RED_COUNT_59_PY
}
if ([string]::IsNullOrWhiteSpace($Prefix) -or $ids.Count -lt 1 -or $ids.Count -ne $ExpectedCount) {
    Write-Error ('named-sets RED_* mismatch for kind=' + $Kind)
    exit 1
}
if (-not (Test-Path -LiteralPath $Receipt)) {
    Write-Error ('missing RED receipt ' + $Receipt)
    exit 1
}
$text = Get-Content -LiteralPath $Receipt -Raw
if ([string]::IsNullOrWhiteSpace($text)) {
    Write-Error ('empty RED receipt ' + $Receipt)
    exit 1
}

$deny = @(
    'INTERNALERROR',
    'no tests ran',
    'No test files found',
    'failed to resolve config',
    'ERR_LOAD_CONFIG',
    'Cannot find package',
    'command not found',
    'is not recognized'
)
foreach ($d in $deny) {
    if ($text -match [regex]::Escape($d)) {
        Write-Error ('RED_ORACLE deny: ' + $d)
        exit 1
    }
}

if ($Kind -eq 'py') {
    $allow = @('FAILED', 'AssertionError', 'failed')
} else {
    $allow = @('FAIL', 'AssertionError', 'failed')
}
$hit = $false
foreach ($a in $allow) {
    if ($text.Contains($a)) { $hit = $true; break }
}
if (-not $hit -and ($Kind -eq 'ui' -or $Kind -eq 'mcp') -and -not [string]::IsNullOrWhiteSpace($JsonReceipt) -and (Test-Path -LiteralPath $JsonReceipt)) {
    $jsonProbe = Get-Content -LiteralPath $JsonReceipt -Raw | ConvertFrom-Json
    if ([int]$jsonProbe.numFailedTests -gt 0) { $hit = $true }
}
if (-not $hit) {
    Write-Error ('RED_ORACLE missing allow-marker for ' + $Kind)
    exit 1
}

$names = New-Object System.Collections.Generic.List[string]
if (($Kind -eq 'ui' -or $Kind -eq 'mcp') -and -not [string]::IsNullOrWhiteSpace($JsonReceipt)) {
    if (-not (Test-Path -LiteralPath $JsonReceipt)) {
        Write-Error ('missing RED_JSON ' + $JsonReceipt)
        exit 1
    }
    $raw = Get-Content -LiteralPath $JsonReceipt -Raw
    if ([string]::IsNullOrWhiteSpace($raw)) {
        Write-Error ('empty RED_JSON ' + $JsonReceipt)
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
    $pattern = [regex]::Escape([string]$id) + '(?![0-9])'
    $hits = @($names | Where-Object { $_ -match $pattern })
    if ($hits.Count -lt 1) {
        Write-Error ('RED_ORACLE missing failed title for ' + $id)
        exit 1
    }
}

foreach ($name in $names) {
    $mapped = @($ids | Where-Object { $name -match ([regex]::Escape([string]$_) + '(?![0-9])') })
    if ($mapped.Count -gt 1) {
        Write-Error ('RED_ORACLE multi-id title: ' + $name)
        exit 1
    }
}

'PASS: RED_ORACLE ' + $Kind + ' MEU-59 count=' + $ExpectedCount
exit 0
