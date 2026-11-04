# AC-60.14 exact dep allowlists + AC-60.18 exact DTO/MCP shape + G36/G37/placeholder.
$ErrorActionPreference = 'Stop'
$setsPath = Join-Path $PSScriptRoot 'named-sets.json'
$sets = Get-Content -LiteralPath $setsPath -Raw | ConvertFrom-Json

function Assert-SameSet([string]$label, $actual, $expected) {
    $a = @($actual | ForEach-Object { [string]$_ } | Sort-Object)
    $e = @($expected | ForEach-Object { [string]$_ } | Sort-Object)
    if (($a -join '|') -ne ($e -join '|')) {
        Write-Error ($label + ' expected [' + ($e -join ',') + '] got [' + ($a -join ',') + ']')
        exit 1
    }
}

function Get-ZodTypeLiterals([string]$src) {
    $rx = [regex]"type:\s*z\.literal\(['""]([^'""]+)['""]\)"
    return @($rx.Matches($src) | ForEach-Object { $_.Groups[1].Value } | Sort-Object -Unique)
}

function Get-ZodFieldsForType([string]$src, [string]$typeName) {
    $pat = "type:\s*z\.literal\(['""]$([regex]::Escape($typeName))['""]\)"
    $m = [regex]::Match($src, $pat)
    if (-not $m.Success) { return @() }
    $rest = $src.Substring($m.Index)
    $end = $rest.IndexOf('.strict()')
    if ($end -lt 0) { return @() }
    $block = $rest.Substring(0, $end)
    $found = @([regex]::Matches($block, '(?m)^\s+([A-Za-z_][A-Za-z0-9_]*)\s*:') | ForEach-Object { $_.Groups[1].Value })
    if ($found -notcontains 'type') { $found = @('type') + $found }
    return @($found | Sort-Object -Unique)
}

$pkg = Get-Content -LiteralPath 'ui/package.json' -Raw | ConvertFrom-Json
Assert-SameSet 'UI_DEP_NAMES' @($pkg.dependencies.PSObject.Properties.Name) @($sets.UI_DEP_NAMES)
Assert-SameSet 'UI_DEVDEP_NAMES' @($pkg.devDependencies.PSObject.Properties.Name) @($sets.UI_DEVDEP_NAMES)

$pkgRaw = Get-Content -LiteralPath 'ui/package.json' -Raw
foreach ($n in @($sets.NO_NEW_PACKAGES)) {
    if ($pkgRaw -match [regex]::Escape([string]$n)) {
        Write-Error ('NO_NEW_PACKAGES example hit ' + $n)
        exit 1
    }
}

$nsArg = (Resolve-Path -LiteralPath $setsPath).Path
& uv run python -c "import json,tomllib,pathlib,sys; sets=json.loads(pathlib.Path(sys.argv[1]).read_text(encoding='utf-8')); allow=sets['PY_DEP_ALLOWLIST'];
def names(path):
 p=pathlib.Path(path)
 if not p.exists():
  raise SystemExit('missing '+path)
 data=tomllib.loads(p.read_text(encoding='utf-8'))
 proj=data.get('project',{})
 out=[]
 def add(item):
  out.append(item.split('[')[0].split('>')[0].split('<')[0].split('=')[0].split('~')[0].split('!')[0].split(' ')[0])
 for item in proj.get('dependencies',[]): add(item)
 for vals in proj.get('optional-dependencies',{}).values():
  for item in vals: add(item)
 return sorted(set([x for x in out if x]))
bad=False
for path, expected in allow.items():
 got=names(path)
 exp=sorted(expected)
 if got!=exp:
  print('PY_DEP_ALLOWLIST mismatch', path, 'got', got, 'expected', exp); bad=True
sys.exit(1 if bad else 0)" $nsArg
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

$src = Get-Content -LiteralPath ([string]$sets.ANNOTATE_SCHEMA) -Raw
Assert-SameSet 'ANNOTATE_TYPES zod' (Get-ZodTypeLiterals $src) @($sets.ANNOTATE_TYPES)
foreach ($t in @($sets.ANNOTATE_TYPES)) {
    $fields = Get-ZodFieldsForType $src ([string]$t)
    $expect = @($sets.ANNOTATE_FIELDS.$t)
    Assert-SameSet ('ANNOTATE_FIELDS ' + $t + ' zod') $fields $expect
}
if ($src -notmatch 'annotateInSchema[\s\S]*\.strict\(\)') {
    Write-Error 'annotateInSchema missing .strict()'
    exit 1
}
foreach ($t in @($sets.FORBIDDEN_TYPES)) {
    $needle = 'type:\s*z\.literal\([''"]' + [regex]::Escape([string]$t) + '[''"]\)'
    if ($src -match $needle) {
        Write-Error ('FORBIDDEN_TYPES in zod ' + $t)
        exit 1
    }
}

$mcp = Get-Content -LiteralPath ([string]$sets.MCP_CAPTURE) -Raw
$mcpActions = @([regex]::Matches($mcp, 'action:\s*z\.literal\(["'']([^"'']+)["'']\)') | ForEach-Object { $_.Groups[1].Value } | Sort-Object -Unique)
Assert-SameSet 'MCP_CAPTURE_ACTIONS' $mcpActions @($sets.MCP_CAPTURE_ACTIONS)
Assert-SameSet 'ANNOTATE_TYPES mcp' (Get-ZodTypeLiterals $mcp) @($sets.ANNOTATE_TYPES)
foreach ($t in @($sets.ANNOTATE_TYPES)) {
    $fields = Get-ZodFieldsForType $mcp ([string]$t)
    $expect = @($sets.ANNOTATE_FIELDS.$t)
    Assert-SameSet ('ANNOTATE_FIELDS ' + $t + ' mcp') $fields $expect
}

function Get-PyWireFields([string]$src, [string]$typeName) {
    $m = [regex]::Match($src, 'type:\s*Literal\["' + [regex]::Escape($typeName) + '"\]')
    if (-not $m.Success) { return @() }
    $rest = $src.Substring($m.Index)
    $next = $rest.IndexOf("`nclass ")
    if ($next -lt 0) { $next = $rest.Length }
    $block = $rest.Substring(0, $next)
    $aliases = @{}
    foreach ($am in [regex]::Matches($block, '(?m)^\s+([A-Za-z_][A-Za-z0-9_]*)\s*:.*alias="([^"]+)"')) {
        $aliases[$am.Groups[1].Value] = $am.Groups[2].Value
    }
    $keys = New-Object System.Collections.Generic.List[string]
    [void]$keys.Add('type')
    foreach ($km in [regex]::Matches($block, '(?m)^\s+([A-Za-z_][A-Za-z0-9_]*)\s*:')) {
        $name = $km.Groups[1].Value
        if ($aliases.ContainsKey($name)) { $keys.Add([string]$aliases[$name]) }
        else { $keys.Add($name) }
    }
    return @($keys | Sort-Object -Unique)
}

$api = Get-Content -LiteralPath ([string]$sets.API_SCHEMA_FILE) -Raw
$apiTypes = @([regex]::Matches($api, 'type:\s*Literal\["([^"]+)"\]') | ForEach-Object { $_.Groups[1].Value } | Sort-Object -Unique)
Assert-SameSet 'ANNOTATE_TYPES api' $apiTypes @($sets.ANNOTATE_TYPES)
if ($api -notmatch 'class AnnotateIn') {
    Write-Error 'missing AnnotateIn'
    exit 1
}
foreach ($t in @($sets.ANNOTATE_TYPES)) {
    $fields = Get-PyWireFields $api ([string]$t)
    $expect = @($sets.ANNOTATE_FIELDS.$t)
    Assert-SameSet ('ANNOTATE_FIELDS ' + $t + ' api') $fields $expect
}

$g37 = Get-Content -LiteralPath ([string]$sets.G37_FILE) -Raw
if ($g37 -match "from 'react-dom/client'" -or $g37 -match 'createRoot') {
    Write-Error 'G37_RULE createRoot in G37_FILE'
    exit 1
}
if ($g37 -notmatch '@testing-library/react' -or $g37 -notmatch 'userEvent') {
    Write-Error 'G37_RULE missing Testing Library / userEvent in G37_FILE'
    exit 1
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
foreach ($root in @($sets.PLACEHOLDER_PATHS_60)) {
    $path = [string]$root
    $files = @()
    if (Test-Path -LiteralPath $path -PathType Leaf) {
        $files = @(Get-Item -LiteralPath $path)
    } elseif (Test-Path -LiteralPath $path -PathType Container) {
        $files = @(Get-ChildItem -LiteralPath $path -Recurse -File -Include *.ts,*.tsx,*.py)
    } else {
        Write-Error ('missing PLACEHOLDER_PATHS_60 ' + $path)
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

'PASS: MEU-60 scans'
exit 0
