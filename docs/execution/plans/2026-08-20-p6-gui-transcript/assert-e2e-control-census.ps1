# Sole executable owner of E2E_CONTROL_CENSUS (plan named set).
# E2E_PER_CONTROL: after comment-strip, the allowed method must be
# chained on the same getByTestId('id') expression
# (expect(page.getByTestId('id')).toBeVisible() or
# page.getByTestId('id').click()). A nearby method on an unrelated
# receiver is a fail. Owner: Test-HasBound / Assert-HasBound.
# E2E_SEAM_PROOF / E2E_ACTUATE / E2E_ATTACHED_FIRST: see plan named sets.
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

function Assert-Contains([string]$Src, [string]$Needle, [string]$Label) {
    if ($Src -notmatch $Needle) {
        Write-Error $Label
        exit 1
    }
}

$visualOracle = 'toBeVisible|toBeHidden|toBeAttached|toHaveCSS'
$r41FalsePass = "page.getByTestId('channel-input'); await expect(unrelatedLocator).toBeVisible();"
if (Test-HasBound $r41FalsePass 'channel-input' $visualOracle) {
    Write-Error 'E2E_PER_CONTROL helper false-pass on unrelated receiver (R4-1)'
    exit 1
}
if (-not (Test-HasBound "await expect(page.getByTestId('channel-input')).toBeVisible()" 'channel-input' 'toBeVisible')) {
    Write-Error 'E2E_PER_CONTROL helper missed same-expression expect().toBeVisible'
    exit 1
}
if (-not (Test-HasBound "await page.getByTestId('add-btn').click(" 'add-btn' 'click\(')) {
    Write-Error 'E2E_PER_CONTROL helper missed same-expression .click('
    exit 1
}

$ids = @(
    'transcript-page', 'channel-input', 'channel-card', 'compile-btn',
    'channel-progress', 'add-btn', 'start-btn', 'pause-btn', 'resume-btn',
    'stop-btn', 'up-btn', 'down-btn', 'remove-btn', 'requeue-btn', 'retry-btn',
    'view-compiled-btn', 'open-zip-btn', 'open-folder-btn', 'processor-indicator',
    'output-tree', 'rate-display', 'eta-display', 'last-title', 'channel-url-hint',
    'remove-confirm-btn', 'remove-confirm-cancel'
)
$registry = 'ui/tests/e2e/test-ids.ts'
$wave2 = 'ui/tests/e2e/transcript-queue.test.ts'
foreach ($f in @($registry, $wave2)) {
    if (-not (Test-Path -LiteralPath $f)) {
        Write-Error ("missing " + $f)
        exit 1
    }
}
$regText = Get-Content -LiteralPath $registry -Raw
$waveSrc = Get-StrippedSource $wave2
if ($waveSrc -match 'test\.skip|test\.only|\.only\(') {
    Write-Error 'E2E_WAVE2 contains skip/only'
    exit 1
}
foreach ($id in $ids) {
    if ($regText -notmatch [regex]::Escape($id)) {
        Write-Error ("testid not registered: " + $id)
        exit 1
    }
}

foreach ($caseId in @('W2-1', 'W2-2', 'W2-3', 'W2-4', 'W2-5', 'W2-6')) {
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

$w1 = Get-CaseBlock $waveSrc 'W2-1'
foreach ($id in @('transcript-page', 'channel-input')) { Assert-HasBound $w1 $id 'toBeVisible' }

$w2 = Get-CaseBlock $waveSrc 'W2-2'
Assert-HasBound $w2 'transcript-page' 'toBeVisible'
if ($w2 -notmatch 'nav-transcript') { Write-Error 'W2-2 missing nav-transcript'; exit 1 }

$w3 = Get-CaseBlock $waveSrc 'W2-3'
$pageChromeVisible = @(
    'channel-input', 'channel-url-hint', 'add-btn', 'start-btn', 'pause-btn',
    'resume-btn', 'stop-btn', 'up-btn', 'down-btn', 'remove-btn', 'compile-btn',
    'view-compiled-btn', 'open-zip-btn', 'open-folder-btn'
)
foreach ($id in $pageChromeVisible) { Assert-HasBound $w3 $id 'toBeVisible' }
Assert-HasBound $w3 'processor-indicator' 'toBeAttached|toHaveCount'

$w4 = Get-CaseBlock $waveSrc 'W2-4'
Assert-HasBound $w4 'channel-input' 'fill\('
Assert-HasBound $w4 'add-btn' 'click\('
foreach ($id in @('channel-card', 'channel-progress', 'output-tree', 'last-title', 'rate-display', 'eta-display')) {
    Assert-HasBound $w4 $id 'toBeVisible'
}
# E2E_SEAM_PROOF — renderer fetch seam, not page.route
Assert-Contains $w4 'addInitScript' 'W2-4 missing E2E_SEAM addInitScript'
Assert-Contains $w4 '__e2eSeamInstalled' 'W2-4 missing E2E_SEAM_GATE __e2eSeamInstalled'
Assert-Contains $w4 '__e2eCalls' 'W2-4 missing E2E_SEAM_LEDGER __e2eCalls'
Assert-Contains $w4 'E2E_SEAM_UNHANDLED' 'W2-4 missing fail-closed E2E_SEAM_UNHANDLED'
Assert-Contains $w4 'channel_url' 'W2-4 missing CREATE_BODY channel_url'
Assert-Contains $w4 'reload' 'W2-4 missing page.reload after addInitScript'
if ($w4 -notmatch 'toContainText' -and $w4 -notmatch 'e2e-') {
    Write-Error 'W2-4 card is not traceable to the seam payload (toContainText or e2e- id)'
    exit 1
}
if ($w4 -match 'page\.route' -and $w4 -notmatch 'addInitScript') {
    Write-Error 'W2-4 page.route-only seam is not E2E_SEAM_PROOF'
    exit 1
}

$w5 = Get-CaseBlock $waveSrc 'W2-5'
$actuate = @(
    @{ Id = 'start-btn'; Path = '/transcripts/start' },
    @{ Id = 'pause-btn'; Path = '/transcripts/pause' },
    @{ Id = 'resume-btn'; Path = '/transcripts/resume' },
    @{ Id = 'stop-btn'; Path = '/transcripts/stop' },
    @{ Id = 'up-btn'; Path = '/transcripts/reorder' },
    @{ Id = 'down-btn'; Path = '/transcripts/reorder' },
    @{ Id = 'compile-btn'; Path = '/compile' },
    @{ Id = 'requeue-btn'; Path = '/requeue' },
    @{ Id = 'retry-btn'; Path = '/retry' }
)
foreach ($row in $actuate) {
    Assert-HasBound $w5 $row.Id 'click\('
    Assert-Contains $w5 ([regex]::Escape($row.Path)) ('W2-5 missing REST observable for ' + $row.Id + ' (' + $row.Path + ')')
}
Assert-HasBound $w5 'remove-btn' 'click\('
foreach ($id in @('remove-confirm-btn', 'remove-confirm-cancel')) {
    Assert-HasBound $w5 $id 'toBeVisible'
}
Assert-HasBound $w5 'remove-confirm-btn' 'click\('
Assert-HasBound $w5 'remove-confirm-cancel' 'click\('
Assert-Contains $w5 'Escape' 'W2-5 missing G20 Escape dismissal'
Assert-Contains $w5 'DELETE' 'W2-5 missing DELETE observable for IN_PAGE_CONFIRM'
foreach ($id in @('view-compiled-btn', 'open-zip-btn', 'open-folder-btn')) {
    Assert-HasBound $w5 $id 'click\('
}
Assert-Contains $w5 '__e2eIpc' 'W2-5 missing E2E_IPC_LEDGER __e2eIpc'
foreach ($id in @('requeue-btn', 'retry-btn')) {
    Assert-HasBound $w5 $id 'toBeVisible'
}
Assert-HasBound $w5 'processor-indicator' 'toBeVisible'
if ($w5 -match "getByTestId\('remove-confirm-btn'\)\)\s*\.toBeHidden" -or $w5 -match "getByTestId\('requeue-btn'\)\)\s*\.toBeHidden" -or $w5 -match "getByTestId\('retry-btn'\)\)\s*\.toBeHidden" -or $w5 -match "getByTestId\('processor-indicator'\)\)\s*\.toBeHidden") {
    Write-Error 'W2-5 uses toBeHidden as a presence oracle (E2E_ATTACHED_FIRST)'
    exit 1
}

$w6 = Get-CaseBlock $waveSrc 'W2-6'
Assert-HasBound $w6 'channel-input' 'toBeFocused'
if ($w6 -notmatch 'transcript:add') { Write-Error 'W2-6 missing palette id transcript:add'; exit 1 }

'PASS: E2E_CONTROL_CENSUS'
exit 0
