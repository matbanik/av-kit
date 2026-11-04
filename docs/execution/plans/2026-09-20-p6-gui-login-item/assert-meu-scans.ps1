# MEU-61 scans: dep allowlists, two executable NSIS DeleteRegValue HKCU lines, nsis.include value, G36.
# Negative fixtures prove comment-token / misplaced-include cases fail (PCR-2).
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

function Get-NsisCodeLines([string]$src) {
    $out = New-Object System.Collections.Generic.List[string]
    foreach ($line in ($src -split "`r?`n")) {
        $code = $line
        $semi = $code.IndexOf(';')
        if ($semi -ge 0) { $code = $code.Substring(0, $semi) }
        $code = $code.Trim()
        if ($code.Length -gt 0) { $out.Add($code) }
    }
    return @($out)
}

function Test-NsisUninstallCode {
    param($NamedSets, [string]$Src)
    $codeLines = @(Get-NsisCodeLines $Src)
    $macro = [string]$NamedSets.NSH_MACRO
    $delete = [string]$NamedSets.NSH_DELETE
    $hkcu = [string]$NamedSets.NSH_HKCU
    $name = [string]$NamedSets.LOGIN_ITEM_NAME
    $runKey = [string]$NamedSets.NSH_RUN_KEY
    $approvedKey = [string]$NamedSets.NSH_APPROVED_KEY
    $macroOk = $false
    foreach ($line in $codeLines) {
        if ($line.Contains($macro)) { $macroOk = $true; break }
    }
    $deletes = @($codeLines | Where-Object { $_ -match ('^' + [regex]::Escape($delete) + '\s+' + [regex]::Escape($hkcu) + '\b') })
    $runHits = @($deletes | Where-Object { $_.Contains($runKey) -and $_.Contains($name) -and -not $_.Contains('StartupApproved') })
    $approvedHits = @($deletes | Where-Object { $_.Contains($approvedKey) -and $_.Contains($name) })
    return [pscustomobject]@{
        Ok            = [bool]($macroOk -and ($deletes.Count -eq 2) -and ($runHits.Count -eq 1) -and ($approvedHits.Count -eq 1))
        DeleteCount   = $deletes.Count
        RunHits       = $runHits.Count
        ApprovedHits  = $approvedHits.Count
        MacroOk       = $macroOk
    }
}

function Get-NsisIncludeValue([string[]]$ymlLines) {
    $inNsis = $false
    $includeVal = $null
    foreach ($line in $ymlLines) {
        if ($line -match '^nsis:\s*$') { $inNsis = $true; continue }
        if ($inNsis -and $line -match '^\S') { $inNsis = $false }
        if ($inNsis -and $line -match '^\s+include:\s*(.+)\s*$') {
            $includeVal = $Matches[1].Trim().Trim('"').Trim("'")
        }
    }
    return $includeVal
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

$login = Get-Content -LiteralPath ([string]$sets.LOGIN_ITEM_MODULE) -Raw
if ($login.IndexOf([string]$sets.LOGIN_ITEM_NAME, [StringComparison]::Ordinal) -lt 0) {
    Write-Error 'LOGIN_ITEM_MODULE missing LOGIN_ITEM_NAME'
    exit 1
}

$startup = Get-Content -LiteralPath ([string]$sets.STARTUP_MODE_MODULE) -Raw
if ($startup.IndexOf([string]$sets.START_MINIMIZED_FLAG, [StringComparison]::Ordinal) -lt 0) {
    Write-Error 'STARTUP_MODE_MODULE missing START_MINIMIZED_FLAG'
    exit 1
}

$ipc = Get-Content -LiteralPath ([string]$sets.IPC_FILE) -Raw
foreach ($ch in @([string]$sets.IPC_GET, [string]$sets.IPC_SET)) {
    if ($ipc.IndexOf($ch, [StringComparison]::Ordinal) -lt 0) {
        Write-Error ('IPC_FILE missing channel ' + $ch)
        exit 1
    }
}
if ($ipc.IndexOf([string]$sets.FORBIDDEN_ELECTRON, [StringComparison]::Ordinal) -ge 0) {
    Write-Error 'IPC_FILE contains FORBIDDEN_ELECTRON'
    exit 1
}

$preload = Get-Content -LiteralPath ([string]$sets.PRELOAD_FILE) -Raw
foreach ($k in @($sets.PRELOAD_GET, $sets.PRELOAD_SET)) {
    if ($preload.IndexOf([string]$k, [StringComparison]::Ordinal) -lt 0) {
        Write-Error ('PRELOAD_FILE missing ' + $k)
        exit 1
    }
}

$negNsh = @(
    ('; ' + [string]$sets.NSH_MACRO + ' ' + [string]$sets.NSH_DELETE + ' ' + [string]$sets.NSH_HKCU),
    ('; ' + [string]$sets.NSH_RUN_KEY),
    ('; ' + [string]$sets.NSH_APPROVED_KEY + ' ' + [string]$sets.LOGIN_ITEM_NAME),
    ('!macro ' + [string]$sets.NSH_MACRO),
    ('  ' + [string]$sets.NSH_DELETE + ' ' + [string]$sets.NSH_HKCU + ' "' + [string]$sets.NSH_RUN_KEY + '" "' + [string]$sets.LOGIN_ITEM_NAME + '"'),
    '!macroend'
) -join "`n"
$negNsis = Test-NsisUninstallCode $sets $negNsh
if ($negNsis.Ok) {
    Write-Error 'NSIS negative fixture unexpectedly passed (comment-only StartupApproved plus one Run delete)'
    exit 1
}

$nsh = Get-Content -LiteralPath ([string]$sets.NSH_FILE) -Raw
$gotNsis = Test-NsisUninstallCode $sets $nsh
if (-not $gotNsis.Ok) {
    Write-Error ('NSH_FILE uninstall bind failed MacroOk=' + $gotNsis.MacroOk + ' DeleteCount=' + $gotNsis.DeleteCount + ' RunHits=' + $gotNsis.RunHits + ' ApprovedHits=' + $gotNsis.ApprovedHits)
    exit 1
}

$negYml = @(
    ('# include: ' + [string]$sets.NSH_INCLUDE),
    'nsis:',
    '  deleteAppDataOnUninstall: false',
    'files:',
    ('  include: ' + [string]$sets.NSH_INCLUDE)
)
$negInclude = Get-NsisIncludeValue $negYml
if ($negInclude -eq [string]$sets.NSH_INCLUDE) {
    Write-Error 'YAML negative fixture unexpectedly bound nsis.include from a comment or non-nsis mapping'
    exit 1
}

$ymlLines = Get-Content -LiteralPath ([string]$sets.BUILDER_YML)
$includeVal = Get-NsisIncludeValue $ymlLines
if ($includeVal -ne [string]$sets.NSH_INCLUDE) {
    Write-Error ('BUILDER_YML nsis.include=[' + $includeVal + '] want [' + $sets.NSH_INCLUDE + ']')
    exit 1
}

$help = Get-Content -LiteralPath ([string]$sets.HELP_FILE) -Raw
foreach ($tok in @($sets.HELP_STARTUP_TOKENS)) {
    if ($help.IndexOf([string]$tok, [StringComparison]::Ordinal) -lt 0) {
        Write-Error ('HELP_FILE missing HELP_STARTUP_TOKEN ' + $tok)
        exit 1
    }
}

$schemas = Get-Content -LiteralPath 'ui/src/renderer/src/features/settings/settings-schemas.ts' -Raw
foreach ($leaf in @($sets.FORBIDDEN_SETTINGS_LEAVES)) {
    if ($schemas.IndexOf([string]$leaf, [StringComparison]::Ordinal) -ge 0) {
        Write-Error ('settings-schemas contains FORBIDDEN_SETTINGS_LEAF ' + $leaf)
        exit 1
    }
}

$prodHits = @($sets.LOGIN_ITEM_MODULE, $sets.CONTROL_FILE, $sets.PAGE_FILE, $sets.INDEX_FILE)
foreach ($path in $prodHits) {
    $src = Get-Content -LiteralPath ([string]$path) -Raw
    foreach ($tok in @($sets.FORBIDDEN_SERVICE_TOKENS)) {
        if ($src.IndexOf([string]$tok, [StringComparison]::Ordinal) -ge 0) {
            Write-Error ($path + ' contains FORBIDDEN_SERVICE_TOKEN ' + $tok)
            exit 1
        }
    }
}

$indexActions = Get-Content -LiteralPath ([string]$sets.ACTIONS_INDEX) -Raw
foreach ($id in @($sets.ACTION_IDS)) {
    if ($indexActions.IndexOf([string]$id, [StringComparison]::Ordinal) -lt 0) {
        Write-Error ('ACTIONS_INDEX missing ' + $id)
        exit 1
    }
}

foreach ($root in @($sets.G36_SCAN_ROOTS)) {
    $files = @(Get-ChildItem -Path ([string]$root) -Recurse -Include *.ts,*.tsx -File)
    foreach ($f in $files) {
        $t = Get-Content -LiteralPath $f.FullName -Raw
        foreach ($tok in @($sets.G36_TOKENS)) {
            if ($t.Contains([string]$tok)) {
                Write-Error ('G36 token ' + $tok + ' in ' + $f.FullName)
                exit 1
            }
        }
    }
}

foreach ($path in @($sets.PLACEHOLDER_PATHS_61)) {
    if (-not (Test-Path -LiteralPath ([string]$path))) {
        Write-Error ('missing PLACEHOLDER_PATH ' + $path)
        exit 1
    }
    $t = Get-Content -LiteralPath ([string]$path) -Raw
    foreach ($tok in @($sets.PLACEHOLDER_TOKENS)) {
        if ($t.Contains([string]$tok)) {
            Write-Error ('placeholder ' + $tok + ' in ' + $path)
            exit 1
        }
    }
}

'PASS: MEU-61 scans'
exit 0
