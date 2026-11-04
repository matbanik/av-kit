# Fail closed on TODO/FIXME/NotImplementedError and G36 skip/xfail in every Files Modified path for the MEU.
# Paths owned by named-sets.json PLACEHOLDER_PATHS_* / G36_TEST_PATHS_*.
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

function Get-NamedStringArray {
    param([object]$Sets, [string]$Key)
    $value = $Sets.$Key
    if ($null -eq $value) {
        Write-Error ('named-sets missing ' + $Key)
        exit 1
    }
    return @($value | ForEach-Object { [string]$_ })
}

function Get-ScanFiles {
    param([string[]]$Paths)
    $files = New-Object System.Collections.Generic.List[string]
    foreach ($p in $Paths) {
        if (-not (Test-Path -LiteralPath $p)) {
            Write-Error ('missing PLACEHOLDER/G36 path ' + $p)
            exit 1
        }
        $item = Get-Item -LiteralPath $p
        if ($item.PSIsContainer) {
            $children = @(Get-ChildItem -LiteralPath $p -Recurse -File -Filter '*.py')
            if ($children.Count -lt 1) {
                Write-Error ('empty PLACEHOLDER directory ' + $p)
                exit 1
            }
            foreach ($c in $children) { $files.Add($c.FullName) }
        } else {
            $files.Add($item.FullName)
        }
    }
    return @($files)
}

$meus = @()
if ($Meu -eq 'all') { $meus = @('34', '35', '36') } else { $meus = @($Meu) }

$placeholderPaths = New-Object System.Collections.Generic.List[string]
$g36Paths = New-Object System.Collections.Generic.List[string]
foreach ($m in $meus) {
    foreach ($p in (Get-NamedStringArray -Sets $sets -Key ('PLACEHOLDER_PATHS_' + $m))) { $placeholderPaths.Add($p) }
    foreach ($p in (Get-NamedStringArray -Sets $sets -Key ('G36_TEST_PATHS_' + $m))) { $g36Paths.Add($p) }
}

$placeholderFiles = @(Get-ScanFiles -Paths @($placeholderPaths) | Sort-Object -Unique)
$placeholderHits = @(Select-String -Path $placeholderFiles -Pattern 'TODO|FIXME|NotImplementedError')
if ($placeholderHits.Count -gt 0) {
    $placeholderHits | ForEach-Object { $_.Path + ':' + $_.LineNumber + ':' + $_.Line }
    Write-Error ('anti-placeholder hits=' + $placeholderHits.Count)
    exit 1
}

$g36Files = @(Get-ScanFiles -Paths @($g36Paths) | Sort-Object -Unique)
$g36Hits = @(Select-String -Path $g36Files -Pattern 'pytest\.skip|pytest\.xfail|pytest\.mark\.skip|pytest\.mark\.xfail|unittest\.skip|\.skip\(|\.xfail\(')
if ($g36Hits.Count -gt 0) {
    $g36Hits | ForEach-Object { $_.Path + ':' + $_.LineNumber + ':' + $_.Line }
    Write-Error ('G36 skip/xfail hits=' + $g36Hits.Count)
    exit 1
}

'PASS: ANTI_PLACEHOLDER MEU-' + $Meu
exit 0
