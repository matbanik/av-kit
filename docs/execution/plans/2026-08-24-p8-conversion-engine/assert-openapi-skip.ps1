# Fail-closed OpenAPI skip: compare packages/api tree hash to baseline written at row 1.
# Does not use git. Missing baseline or hash drift is FAIL.
$ErrorActionPreference = 'Stop'
$setsPath = Join-Path $PSScriptRoot 'named-sets.json'
$sets = Get-Content -LiteralPath $setsPath -Raw | ConvertFrom-Json
$baseline = [string]$sets.API_BASELINE
$tree = [string]$sets.API_TREE
if (-not (Test-Path -LiteralPath $baseline)) {
    Write-Error 'missing API_BASELINE — row 1 must write it before H1-4'
    exit 1
}
if (-not (Test-Path -LiteralPath $tree)) {
    Write-Error ('missing API_TREE ' + $tree)
    exit 1
}
$hasher = [System.Security.Cryptography.SHA256]::Create()
$files = @(Get-ChildItem -LiteralPath $tree -Recurse -File | Sort-Object FullName)
$sb = New-Object System.Text.StringBuilder
foreach ($f in $files) {
    $rel = $f.FullName.Substring((Resolve-Path $tree).Path.Length).TrimStart('\','/')
    $bytes = [System.IO.File]::ReadAllBytes($f.FullName)
    $hash = [BitConverter]::ToString($hasher.ComputeHash($bytes)).Replace('-','').ToLowerInvariant()
    [void]$sb.AppendLine($rel + ' ' + $hash)
}
$current = $sb.ToString()
$want = Get-Content -LiteralPath $baseline -Raw
if ($current -ne $want) {
    Write-Error 'packages/api tree hash drifted — G8 required (do not skip OpenAPI)'
    exit 1
}
'PASS: OPENAPI_SKIP api-tree-unchanged count=' + $files.Count
exit 0
