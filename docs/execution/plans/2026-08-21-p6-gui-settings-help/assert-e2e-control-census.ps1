# Sole executable owner of E2E_CONTROL_CENSUS for Wave 4 settings + Wave 6 help.
# Canonical control list must match plan named sets WAVE4_TESTIDS + WAVE4_EXTRA_TESTIDS + WAVE6_TESTIDS.
$ErrorActionPreference = 'Stop'

function Get-StrippedSource([string]$Path) {
    $src = Get-Content -LiteralPath $Path -Raw
    $src = [regex]::Replace($src, '(?s)/\*.*?\*/', '')
    $src = [regex]::Replace($src, '//[^\n]*', '')
    return $src
}

function Get-CodeWithoutStrings([string]$Src) {
    $out = [regex]::Replace($Src, '(?s)"(?:\\.|[^"\\])*"', '""')
    $out = [regex]::Replace($out, "(?s)'(?:\\.|[^'\\])*'", "''")
    $out = [regex]::Replace($out, '(?s)`(?:\\.|[^`\\])*`', '``')
    return $out
}

function Assert-HasBound([string]$Src, [string]$Id, [string]$MethodsRegex) {
    $lit = [regex]::Escape("getByTestId('" + $Id + "')")
    $pattern = $lit + '(?:\)\s*)?\s*\.(' + $MethodsRegex + ')'
    if (-not ($Src -match $pattern)) {
        Write-Error ("E2E_PER_CONTROL missing same-expression assertion for " + $Id + " / " + $MethodsRegex)
        exit 1
    }
}

function Assert-CaseHasInstaller([string]$Src, [string]$CaseId) {
    $pattern = "test\([^)]*" + [regex]::Escape($CaseId) + "[\s\S]*?(?=\r?\ntest\(|\z)"
    $m = [regex]::Match($Src, $pattern)
    if (-not $m.Success) {
        Write-Error ("missing case block " + $CaseId)
        exit 1
    }
    $code = Get-CodeWithoutStrings $m.Value
    if ($code -notmatch 'installSettingsSeam\s*\(') {
        Write-Error ($CaseId + ' missing E2E_SEAM_INSTALL call installSettingsSeam(')
        exit 1
    }
    if ($code -notmatch '__e2eSeamInstalled') {
        Write-Error ($CaseId + ' missing E2E_SEAM_GATE __e2eSeamInstalled outside strings')
        exit 1
    }
}

$settingsPath = 'ui/tests/e2e/settings.test.ts'
$helpPath = 'ui/tests/e2e/help-search.spec.ts'
if (-not (Test-Path -LiteralPath $settingsPath)) {
    Write-Error ("missing " + $settingsPath)
    exit 1
}
if (-not (Test-Path -LiteralPath $helpPath)) {
    Write-Error ("missing " + $helpPath)
    exit 1
}

$settings = Get-StrippedSource $settingsPath
$help = Get-StrippedSource $helpPath

$wave4Section = @(
    'settings-page', 'download-settings', 'transcript-settings', 'tts-settings',
    'console-settings', 'appearance-settings', 'dependencies-section'
)
$wave4Extra = @(
    'browse-download-path-btn', 'apply-defaults-btn', 'browse-ffmpeg-btn', 'browse-cookie-file-btn',
    'browse-transcript-dir-btn', 'browse-models-dir-btn', 'check-deps-btn', 'copy-mcp-btn',
    'pin-mcp-btn', 'theme-dark-btn', 'theme-light-btn', 'readiness-card', 'mcp-access-card',
    'mcp-token-present'
)
$wave6 = @('help-card', 'help-search')

foreach ($id in ($wave4Section + $wave4Extra)) {
    Assert-HasBound $settings $id 'toBeVisible|toBeAttached|click|toHaveCount|toBeEnabled|toBeDisabled'
}
foreach ($id in $wave6) {
    Assert-HasBound $help $id 'toBeVisible|toBeAttached|click|fill|toHaveCount'
}

foreach ($caseId in @('W4-1', 'W4-2', 'W4-3')) {
    if ($settings -notmatch ("test\([^)]*" + [regex]::Escape($caseId))) {
        Write-Error ("settings.test.ts missing case " + $caseId)
        exit 1
    }
}
Assert-CaseHasInstaller $settings 'W4-3'

foreach ($caseId in @('W6-1', 'W6-2')) {
    if ($help -notmatch ("test\([^)]*" + [regex]::Escape($caseId))) {
        Write-Error ("help-search.spec.ts missing case " + $caseId)
        exit 1
    }
}

$expected = $wave4Section.Count + $wave4Extra.Count + $wave6.Count
Write-Output ("PASS: E2E_CONTROL_CENSUS enforced=" + $expected + " (WAVE4_TESTIDS+WAVE4_EXTRA+WAVE6)")
exit 0
