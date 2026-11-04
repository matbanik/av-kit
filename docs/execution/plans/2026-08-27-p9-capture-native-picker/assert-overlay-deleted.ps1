# Sole executable owner of the Chromium-overlay deletion oracle (AC-40.9).
# Round 11 (R11-4): source deletion is not enough. `electron-builder` packages `ui/out`, so a
# stale build output tree ships the deleted overlay even after `ui/src` is clean. This gate now
# scans every root in OVERLAY_SCAN_ROOTS for the forbidden token AND for `overlay*` build
# artifacts by name, because a compiled overlay bundle may not contain the source token verbatim.
# -SelfTest proves non-vacuity: a synthetic tree containing the token, and one containing only a
# name-matched artifact, must each fail.
param([switch]$SelfTest)
$ErrorActionPreference = 'Stop'
$setsPath = Join-Path $PSScriptRoot 'named-sets.json'
if (-not (Test-Path -LiteralPath $setsPath)) { Write-Error ('missing NAMED_SETS_FILE ' + $setsPath); exit 1 }
$sets = Get-Content -LiteralPath $setsPath -Raw | ConvertFrom-Json
$token = [string]$sets.OVERLAY_FORBIDDEN_TOKEN
$roots = @($sets.OVERLAY_SCAN_ROOTS)
$namePattern = [string]$sets.OVERLAY_FORBIDDEN_NAME_PATTERN
$deleted = @($sets.OVERLAY_DELETED_FILES)

function Measure-Token {
    param([string]$Root, [string]$Token)
    if (-not (Test-Path -LiteralPath $Root)) { return 0 }
    @(Get-ChildItem -LiteralPath $Root -Recurse -File | Select-String -Pattern $Token -SimpleMatch).Count
}
function Find-NamedArtifact {
    param([string]$Root, [string]$Pattern)
    if (-not (Test-Path -LiteralPath $Root)) { return @() }
    @(Get-ChildItem -LiteralPath $Root -Recurse -File -Filter $Pattern | ForEach-Object { $_.FullName })
}

if ($SelfTest) {
    if ($roots.Count -lt 2) { Write-Error 'SELFTEST OVERLAY_SCAN_ROOTS must cover source AND build output'; exit 1 }
    if ($deleted.Count -lt 1) { Write-Error 'SELFTEST OVERLAY_DELETED_FILES empty'; exit 1 }
    if ([string]::IsNullOrWhiteSpace($namePattern)) { Write-Error 'SELFTEST OVERLAY_FORBIDDEN_NAME_PATTERN empty'; exit 1 }
    $tmp = Join-Path ([System.IO.Path]::GetTempPath()) ('overlay-selftest-' + [guid]::NewGuid().ToString('N'))
    New-Item -ItemType Directory -Path $tmp | Out-Null
    try {
        # O1 clean tree
        'const x = 1' | Set-Content -LiteralPath (Join-Path $tmp 'clean.ts')
        $clean = Measure-Token -Root $tmp -Token $token
        if ($clean -ne 0) { Write-Error ('SELFTEST O1 clean tree count=' + $clean + ' expected 0'); exit 1 }
        if ((Find-NamedArtifact -Root $tmp -Pattern $namePattern).Count -ne 0) { Write-Error 'SELFTEST O1 clean tree matched the artifact pattern'; exit 1 }
        # O2 token present
        ('import { ' + $token + ' } from "electron"') | Set-Content -LiteralPath (Join-Path $tmp 'dirty.ts')
        if ((Measure-Token -Root $tmp -Token $token) -lt 1) { Write-Error 'SELFTEST O2 forbidden token not detected - oracle is vacuous'; exit 1 }
        Remove-Item -LiteralPath (Join-Path $tmp 'dirty.ts') -Force
        # O3 name-matched build artifact with no token in it - the R11-4 case
        $nested = Join-Path $tmp 'preload'
        New-Item -ItemType Directory -Path $nested | Out-Null
        'var e=1;' | Set-Content -LiteralPath (Join-Path $nested 'overlay.js')
        if ((Measure-Token -Root $tmp -Token $token) -ne 0) { Write-Error 'SELFTEST O3 setup: token leaked into the name-only case'; exit 1 }
        $named = Find-NamedArtifact -Root $tmp -Pattern $namePattern
        if ($named.Count -lt 1) { Write-Error 'SELFTEST O3 stale overlay build artifact not detected by name - a token-free bundle would ship'; exit 1 }
        # O4 missing root contributes nothing rather than erroring
        if ((Measure-Token -Root (Join-Path $tmp 'no-such-dir') -Token $token) -ne 0) { Write-Error 'SELFTEST O4 missing root did not read as empty'; exit 1 }
        'PASS: OVERLAY_DELETION self-test (O1 clean, O2 token, O3 stale artifact by name, O4 absent root)'
        exit 0
    } finally {
        Remove-Item -LiteralPath $tmp -Recurse -Force -ErrorAction SilentlyContinue
    }
}

if (-not (@($roots | Where-Object { Test-Path -LiteralPath $_ })).Count) {
    Write-Error ('none of OVERLAY_SCAN_ROOTS exist: ' + ($roots -join ',') + ' - run this gate from the repo root')
    exit 1
}
$tokenHits = 0
$named = @()
foreach ($r in $roots) {
    $tokenHits += Measure-Token -Root $r -Token $token
    $named += Find-NamedArtifact -Root $r -Pattern $namePattern
}
$leftover = @($deleted | Where-Object { Test-Path -LiteralPath $_ })
$viteInputs = 'ui/electron.vite.config.ts'
$viteOverlay = 0
if (Test-Path -LiteralPath $viteInputs) {
    $viteOverlay = @(Select-String -LiteralPath $viteInputs -Pattern 'overlay' -SimpleMatch).Count
}
[pscustomobject]@{
    forbiddenToken   = $token
    scanRoots        = $roots
    tokenCount       = $tokenHits
    staleArtifacts   = $named
    leftoverFiles    = $leftover
    viteOverlayRefs  = $viteOverlay
} | ConvertTo-Json -Depth 3
if ($tokenHits -ne 0) { Write-Error ($token + ' still present ' + $tokenHits + ' times under ' + ($roots -join ',')); exit 1 }
if ($named.Count -ne 0) { Write-Error ('overlay build artifacts still present: ' + ($named -join ',') + ' - dist:prep must clean DIST_CLEAN_DIRS'); exit 1 }
if ($leftover.Count -ne 0) { Write-Error ('overlay files still on disk: ' + ($leftover -join ',')); exit 1 }
if ($viteOverlay -ne 0) { Write-Error ('overlay entries still referenced in ' + $viteInputs); exit 1 }
'PASS: OVERLAY_DELETION'
exit 0
