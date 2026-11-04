# Registered MEU-scoped quality gate: pytest + pyright + ruff + anti-placeholder/G36.
# File lists owned by named-sets.json GATE_* / PLACEHOLDER_* / G36_*.
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('34', '35', '36', 'all')]
    [string]$Meu
)
$ErrorActionPreference = 'Stop'
$setsPath = Join-Path $PSScriptRoot 'named-sets.json'
if (-not (Test-Path -LiteralPath $setsPath)) {
    Write-Error ('missing NAMED_SETS_FILE ' + $setsPath)
    exit 1
}
$sets = Get-Content -LiteralPath $setsPath -Raw | ConvertFrom-Json
$key = $Meu.ToUpperInvariant()
if ($Meu -eq 'all') { $key = 'ALL' }

function Get-NamedStringArray {
    param([object]$Sets, [string]$Name)
    $value = $Sets.$Name
    if ($null -eq $value) {
        Write-Error ('named-sets missing ' + $Name)
        exit 1
    }
    return @($value | ForEach-Object { [string]$_ })
}

function Invoke-RtkUv {
    param(
        [string[]]$InnerArgs,
        [string]$Receipt
    )
    if (-not (Get-Command rtk -ErrorAction SilentlyContinue)) {
        Write-Error 'rtk is required for P0 routing (AGENTS.md); missing rtk is a [B] dependency'
        exit 1
    }
    & rtk proxy uv @InnerArgs *> $Receipt
    return $LASTEXITCODE
}

$pytestFiles = Get-NamedStringArray -Sets $sets -Name ('GATE_PYTEST_' + $key)
$ruffFiles = Get-NamedStringArray -Sets $sets -Name ('GATE_RUFF_' + $key)
$pyrightFiles = Get-NamedStringArray -Sets $sets -Name ('GATE_PYRIGHT_' + $key)

if ($Meu -eq 'all') {
    $pytestReceipt = 'C:/Temp/av-kit/pytest-p9-engine-h1.txt'
    $pyrightReceipt = 'C:/Temp/av-kit/pyright-p9-engine.txt'
    $ruffReceipt = 'C:/Temp/av-kit/ruff-p9-engine.txt'
    $placeholderReceipt = 'C:/Temp/av-kit/placeholder-p9-engine.txt'
} else {
    $pytestReceipt = 'C:/Temp/av-kit/pytest-meu-' + $Meu + '-gate.txt'
    $pyrightReceipt = 'C:/Temp/av-kit/pyright-meu-' + $Meu + '.txt'
    $ruffReceipt = 'C:/Temp/av-kit/ruff-meu-' + $Meu + '.txt'
    $placeholderReceipt = 'C:/Temp/av-kit/placeholder-meu-' + $Meu + '.txt'
}

$pytestInner = @('run', 'pytest') + $pytestFiles + @('-x', '--tb=short', '-v')
$code = Invoke-RtkUv -InnerArgs $pytestInner -Receipt $pytestReceipt
if ($code -ne 0) {
    Get-Content $pytestReceipt | Select-Object -Last 40
    exit $code
}

$pyrightInner = @('run', 'pyright') + $pyrightFiles
$code = Invoke-RtkUv -InnerArgs $pyrightInner -Receipt $pyrightReceipt
if ($code -ne 0) {
    Get-Content $pyrightReceipt | Select-Object -Last 40
    exit $code
}

$ruffInner = @('run', 'ruff', 'check') + $ruffFiles
$code = Invoke-RtkUv -InnerArgs $ruffInner -Receipt $ruffReceipt
if ($code -ne 0) {
    Get-Content $ruffReceipt | Select-Object -Last 40
    exit $code
}

$placeholderScript = Join-Path $PSScriptRoot 'assert-anti-placeholder.ps1'
& rtk proxy pwsh -NoProfile -File $placeholderScript -Meu $Meu *> $placeholderReceipt
$code = $LASTEXITCODE
if ($code -ne 0) {
    Get-Content $placeholderReceipt
    exit $code
}

'PASS: MEU_SCOPED_GATE quality MEU-' + $Meu
exit 0
