# Fail-closed SIZE_CAP owner. Never treats a missing artifact as PASS.
# Caller must have already run NSIS_BUILD_CMD (receipt = -BuildReceipt).
param(
    [Parameter(Mandatory = $true)]
    [string]$BuildReceipt,
    [string]$DistDir = 'ui/dist'
)
$ErrorActionPreference = 'Stop'
$setsPath = Join-Path $PSScriptRoot 'named-sets.json'
$sets = Get-Content -LiteralPath $setsPath -Raw | ConvertFrom-Json
$cap = [int64]$sets.SIZE_CAP_BYTES
$follow = [string]$sets.NSIS_PACK_FOLLOWUP
$ci = [string]$sets.NSIS_CI_JOB
if (-not (Test-Path -LiteralPath $BuildReceipt)) {
    Write-Error ("missing NSIS_BUILD_CMD receipt " + $BuildReceipt)
    exit 1
}
$buildText = Get-Content -LiteralPath $BuildReceipt -Raw
if ([string]::IsNullOrWhiteSpace($buildText)) {
    Write-Error ("empty NSIS_BUILD_CMD receipt " + $BuildReceipt)
    exit 1
}
$arts = @()
if (Test-Path -LiteralPath $DistDir) {
    $arts = @(Get-ChildItem -Path $DistDir -Filter '*.exe' -Recurse -ErrorAction SilentlyContinue)
}
if ($arts.Count -lt 1) {
    Write-Error ("NSIS artifact missing after NSIS_BUILD_CMD. Mark row [B] " + $follow + " + CI " + $ci + " only if this receipt shows an external/environment error. Not a PASS.")
    exit 1
}
$max = ($arts | Measure-Object -Property Length -Maximum).Maximum
if ($max -ge $cap) {
    Write-Error ("SIZE_CAP fail bytes=" + $max + " cap=" + $cap)
    exit 1
}
('PASS: SIZE_CAP bytes=' + $max) | Set-Content -Path 'C:/Temp/av-kit/nsis-size.txt'
Get-Content 'C:/Temp/av-kit/nsis-size.txt'
exit 0
