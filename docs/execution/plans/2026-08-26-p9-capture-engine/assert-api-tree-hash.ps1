# Write SHA256 manifest of packages/api. Called from task row 1. Owner: named-sets API_*.
param([ValidateSet('write','check')][string]$Mode = 'write')
$ErrorActionPreference = 'Stop'
$setsPath = Join-Path $PSScriptRoot 'named-sets.json'
$sets = Get-Content -LiteralPath $setsPath -Raw | ConvertFrom-Json
$baseline = [string]$sets.API_BASELINE
$tree = [string]$sets.API_TREE
$hasher = [System.Security.Cryptography.SHA256]::Create()
$files = @(Get-ChildItem -LiteralPath $tree -Recurse -File | Sort-Object FullName)
$sb = New-Object System.Text.StringBuilder
foreach ($f in $files) {
    $rel = $f.FullName.Substring((Resolve-Path $tree).Path.Length).TrimStart('\','/')
    $bytes = [System.IO.File]::ReadAllBytes($f.FullName)
    $hash = [BitConverter]::ToString($hasher.ComputeHash($bytes)).Replace('-','').ToLowerInvariant()
    [void]$sb.AppendLine($rel + ' ' + $hash)
}
$text = $sb.ToString()
if ($Mode -eq 'write') {
    $dir = Split-Path -Parent $baseline
    if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Force -Path $dir | Out-Null }
    Set-Content -LiteralPath $baseline -Value $text -NoNewline
    'PASS: API_BASELINE written count=' + $files.Count
    exit 0
}
& (Join-Path $PSScriptRoot 'assert-openapi-skip.ps1')
exit $LASTEXITCODE
