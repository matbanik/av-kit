# Sole executable owner of RED_ORACLE (plan named set).
# UI Red requires Vitest JSON: 20 distinct failed tests, one per RED_AC_IDS (AC-23.1–23.20).
# AC-23.21–23.22 use Playwright E2E_RED receipts (not this oracle).
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('py', 'ui')]
    [string]$Kind,
    [Parameter(Mandatory = $true)]
    [string]$Receipt,
    [string]$JsonReceipt
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

if ($Kind -eq 'ui') {
    if ([string]::IsNullOrWhiteSpace($JsonReceipt)) {
        Write-Error 'UI Red requires -JsonReceipt (RED_JSON)'
        exit 1
    }
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
    $assertions = New-Object System.Collections.Generic.List[object]
    foreach ($suite in @($json.testResults)) {
        foreach ($a in @($suite.assertionResults)) {
            $name = [string]$a.fullName
            if ([string]::IsNullOrWhiteSpace($name)) { $name = [string]$a.title }
            if ([string]::IsNullOrWhiteSpace($name)) { continue }
            $assertions.Add([pscustomobject]@{
                    Name   = $name
                    Status = [string]$a.status
                })
        }
    }
    if ($assertions.Count -lt 1) {
        Write-Error 'RED_JSON has no testResults[].assertionResults[]'
        exit 1
    }
    # Vitest Red covers AC-23.1–23.20. AC-23.21–23.22 are Playwright (E2E_RED + E2E_CONTROL_CENSUS).
    $ids = @(
        'AC-23.1', 'AC-23.2', 'AC-23.3', 'AC-23.4', 'AC-23.5', 'AC-23.6',
        'AC-23.7', 'AC-23.8', 'AC-23.9', 'AC-23.10', 'AC-23.11', 'AC-23.12',
        'AC-23.13', 'AC-23.14', 'AC-23.15', 'AC-23.16', 'AC-23.17', 'AC-23.18',
        'AC-23.19', 'AC-23.20'
    )
    foreach ($row in $assertions) {
        $mapped = @($ids | Where-Object { $row.Name -match ([regex]::Escape($_) + '(?![0-9])') })
        if ($mapped.Count -gt 1) {
            Write-Error ("RED_ORACLE multi-id title: " + $row.Name)
            exit 1
        }
    }
    foreach ($id in $ids) {
        $pattern = [regex]::Escape($id) + '(?![0-9])'
        $hits = @($assertions | Where-Object { $_.Name -match $pattern })
        if ($hits.Count -ne 1) {
            Write-Error ("RED_ORACLE expected 1 test for " + $id + " got " + $hits.Count)
            exit 1
        }
        $st = $hits[0].Status.ToLowerInvariant()
        if ($st -ne 'failed' -and $st -ne 'fail') {
            Write-Error ("RED_ORACLE " + $id + " status=" + $hits[0].Status + " (want failed)")
            exit 1
        }
    }
}

'PASS: RED_ORACLE ' + $Kind
exit 0
