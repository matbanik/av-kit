# AC-59.14 + G36 + placeholder scans for MEU-59. Names come from named-sets.json.
$ErrorActionPreference = 'Stop'
$setsPath = Join-Path $PSScriptRoot 'named-sets.json'
$sets = Get-Content -LiteralPath $setsPath -Raw | ConvertFrom-Json

$pkg = Get-Content -LiteralPath 'ui/package.json' -Raw
foreach ($n in @($sets.NO_NEW_PACKAGES)) {
    if ($pkg -match [regex]::Escape([string]$n)) {
        Write-Error ('NO_NEW_PACKAGES hit ' + $n)
        exit 1
    }
}

$pyProjects = @('pyproject.toml', 'packages/api/pyproject.toml', 'packages/core/pyproject.toml', 'packages/infrastructure/pyproject.toml')
foreach ($py in $pyProjects) {
    if (-not (Test-Path -LiteralPath $py)) { continue }
    $txt = Get-Content -LiteralPath $py -Raw
    foreach ($n in @($sets.NO_NEW_PACKAGES)) {
        if ($txt -match [regex]::Escape([string]$n)) {
            Write-Error ('NO_NEW_PACKAGES hit ' + $n + ' in ' + $py)
            exit 1
        }
    }
}

$src = Get-Content -LiteralPath ([string]$sets.ANNOTATE_SCHEMA) -Raw
foreach ($t in @($sets.FORBIDDEN_TYPES)) {
    $needle = 'type:\s*z\.literal\(''' + [regex]::Escape([string]$t) + '''\)'
    if ($src -match $needle) {
        Write-Error ('FORBIDDEN_TYPES in zod ' + $t)
        exit 1
    }
}

$g36Hits = New-Object System.Collections.Generic.List[string]
foreach ($root in @($sets.G36_SCAN_ROOTS)) {
    if (-not (Test-Path -LiteralPath ([string]$root))) { continue }
    $files = Get-ChildItem -LiteralPath ([string]$root) -Recurse -File -Include *.ts,*.tsx,*.js,*.py
    foreach ($f in $files) {
        $lines = Get-Content -LiteralPath $f.FullName
        $i = 0
        foreach ($line in $lines) {
            $i++
            foreach ($tok in @($sets.G36_TOKENS)) {
                if ($line.Contains([string]$tok)) {
                    $g36Hits.Add($f.FullName + ':' + $i + ':' + $tok)
                }
            }
        }
    }
}
if ($g36Hits.Count -gt 0) {
    Write-Error ('G36_RULE hits: ' + ($g36Hits -join '; '))
    exit 1
}

$phHits = New-Object System.Collections.Generic.List[string]
foreach ($root in @($sets.PLACEHOLDER_PATHS_59)) {
    $path = [string]$root
    $files = @()
    if (Test-Path -LiteralPath $path -PathType Leaf) {
        $files = @(Get-Item -LiteralPath $path)
    } elseif (Test-Path -LiteralPath $path -PathType Container) {
        $files = @(Get-ChildItem -LiteralPath $path -Recurse -File -Include *.ts,*.tsx,*.py)
    } else {
        Write-Error ('missing PLACEHOLDER_PATHS_59 ' + $path)
        exit 1
    }
    foreach ($f in $files) {
        $lines = Get-Content -LiteralPath $f.FullName
        $i = 0
        foreach ($line in $lines) {
            $i++
            foreach ($tok in @($sets.PLACEHOLDER_TOKENS)) {
                if ($line.Contains([string]$tok)) {
                    $phHits.Add($f.FullName + ':' + $i + ':' + $tok)
                }
            }
        }
    }
}
if ($phHits.Count -gt 0) {
    Write-Error ('placeholder hits: ' + ($phHits -join '; '))
    exit 1
}

'PASS: MEU-59 scans'
exit 0
