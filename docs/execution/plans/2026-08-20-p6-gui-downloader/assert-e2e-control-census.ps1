# Sole executable owner of E2E_CONTROL_CENSUS (plan named set).
# E2E_PER_CONTROL: after comment-strip, the allowed method must be
# chained on the same getByTestId('id') expression
# (expect(page.getByTestId('id')).toBeVisible() or
# page.getByTestId('id').click()). A nearby method on an unrelated
# receiver is a fail. Owner: Test-HasBound / Assert-HasBound.
$ErrorActionPreference = 'Stop'

function Get-StrippedSource([string]$Path) {
    $src = Get-Content -LiteralPath $Path -Raw
    $src = [regex]::Replace($src, '(?s)/\*.*?\*/', '')
    $src = [regex]::Replace($src, '//[^\n]*', '')
    return $src
}

function Get-CaseBlock([string]$Src, [string]$CaseId) {
    $pattern = "test\([^)]*" + [regex]::Escape($CaseId) + "[\s\S]*?(?=\r?\ntest\(|\z)"
    $m = [regex]::Match($Src, $pattern)
    if (-not $m.Success) { return '' }
    return $m.Value
}

function Test-HasBound([string]$Src, [string]$Id, [string]$MethodsRegex) {
    $lit = [regex]::Escape("getByTestId('" + $Id + "')")
    $pattern = $lit + '(?:\)\s*)?\s*\.(' + $MethodsRegex + ')'
    return [bool]($Src -match $pattern)
}

function Assert-HasBound([string]$Src, [string]$Id, [string]$MethodsRegex) {
    if (-not (Test-HasBound $Src $Id $MethodsRegex)) {
        Write-Error ("E2E_PER_CONTROL missing same-expression assertion for " + $Id + " / " + $MethodsRegex)
        exit 1
    }
}

$visualOracle = 'toBeVisible|toBeHidden|toBeAttached|toHaveCSS'
$r41FalsePass = "page.getByTestId('quality-select'); await expect(unrelatedLocator).toBeVisible();"
if (Test-HasBound $r41FalsePass 'quality-select' $visualOracle) {
    Write-Error 'E2E_PER_CONTROL helper false-pass on unrelated receiver (R4-1)'
    exit 1
}
if (-not (Test-HasBound "await expect(page.getByTestId('quality-select')).toBeVisible()" 'quality-select' 'toBeVisible')) {
    Write-Error 'E2E_PER_CONTROL helper missed same-expression expect().toBeVisible'
    exit 1
}
if (-not (Test-HasBound "await page.getByTestId('add-btn').click(" 'add-btn' 'click\(')) {
    Write-Error 'E2E_PER_CONTROL helper missed same-expression .click('
    exit 1
}

$ids = @(
    'downloader-page', 'url-input', 'add-btn', 'queue-table', 'queue-row',
    'start-btn', 'pause-btn', 'resume-btn', 'cancel-btn', 'sabr-status',
    'sabr-check-btn', 'quality-select', 'audio-only', 'audio-format',
    'cookie-mode-none', 'cookie-mode-browser', 'cookie-mode-file',
    'cookie-browser', 'cookie-profile', 'cookie-file', 'cookie-test-btn',
    'sabr-force-btn', 'sabr-clear-btn', 'up-btn', 'down-btn', 'top-btn',
    'bottom-btn', 'reset-btn', 'remove-btn', 'clear-all-btn', 'queue-summary',
    'processor-indicator', 'open-file-btn', 'open-folder-btn'
)
$registry = 'ui/tests/e2e/test-ids.ts'
$wave1 = 'ui/tests/e2e/download-queue.test.ts'
$wave0 = 'ui/tests/e2e/launch.test.ts'
foreach ($f in @($registry, $wave1, $wave0)) {
    if (-not (Test-Path -LiteralPath $f)) {
        Write-Error ("missing " + $f)
        exit 1
    }
}
$regText = Get-Content -LiteralPath $registry -Raw
$waveSrc = Get-StrippedSource $wave1
if ($waveSrc -match 'test\.skip|test\.only|\.only\(') {
    Write-Error 'E2E_WAVE1 contains skip/only'
    exit 1
}
foreach ($id in $ids) {
    if ($regText -notmatch [regex]::Escape($id)) {
        Write-Error ("testid not registered: " + $id)
        exit 1
    }
}

$visual = 'toBeVisible|toBeHidden|toBeAttached|toHaveCSS'
$enabled = 'toBeEnabled|toBeDisabled'
foreach ($caseId in @('W1-1', 'W1-2', 'W1-3', 'W1-4', 'W1-5', 'W1-6')) {
    $block = Get-CaseBlock $waveSrc $caseId
    if ([string]::IsNullOrWhiteSpace($block)) {
        Write-Error ("E2E_CASES missing test() titled " + $caseId)
        exit 1
    }
    if ($block -notmatch 'expect\(') {
        Write-Error ($caseId + ' missing expect(')
        exit 1
    }
}

$w1 = Get-CaseBlock $waveSrc 'W1-1'
foreach ($id in @('downloader-page', 'url-input')) { Assert-HasBound $w1 $id 'toBeVisible' }

$w2 = Get-CaseBlock $waveSrc 'W1-2'
Assert-HasBound $w2 'downloader-page' 'toBeVisible'
if ($w2 -notmatch 'nav-downloader|transcript') { Write-Error 'W1-2 missing nav/transcript'; exit 1 }

$w3 = Get-CaseBlock $waveSrc 'W1-3'
$extra = @(
    'quality-select', 'audio-only', 'audio-format', 'cookie-mode-none',
    'cookie-mode-browser', 'cookie-mode-file', 'cookie-browser', 'cookie-profile',
    'cookie-file', 'cookie-test-btn', 'sabr-check-btn', 'sabr-force-btn',
    'sabr-clear-btn', 'up-btn', 'down-btn', 'top-btn', 'bottom-btn', 'reset-btn',
    'remove-btn', 'clear-all-btn', 'queue-table', 'queue-summary',
    'processor-indicator', 'open-file-btn', 'open-folder-btn', 'sabr-status'
)
foreach ($id in $extra) { Assert-HasBound $w3 $id $visual }

$w4 = Get-CaseBlock $waveSrc 'W1-4'
Assert-HasBound $w4 'url-input' 'fill\('
Assert-HasBound $w4 'add-btn' 'click\('
Assert-HasBound $w4 'queue-row' 'toBeVisible'
if ($w4 -notmatch 'page\.route') { Write-Error 'W1-4 missing E2E_SEAM page.route'; exit 1 }

$w5 = Get-CaseBlock $waveSrc 'W1-5'
foreach ($id in @('start-btn', 'pause-btn', 'resume-btn', 'cancel-btn', 'up-btn', 'down-btn', 'top-btn', 'bottom-btn', 'reset-btn', 'remove-btn', 'clear-all-btn', 'open-file-btn', 'open-folder-btn')) {
    Assert-HasBound $w5 $id $enabled
}

$w6 = Get-CaseBlock $waveSrc 'W1-6'
Assert-HasBound $w6 'url-input' 'toBeFocused'
if ($w6 -notmatch 'download:add') { Write-Error 'W1-6 missing palette id download:add'; exit 1 }

'PASS: E2E_CONTROL_CENSUS'
exit 0
