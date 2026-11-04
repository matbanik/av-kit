# Sole executable owner of E2E_CONTROL_CENSUS (plan named set).
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

function Get-FunctionBody([string]$Src, [string]$Name) {
    $start = [regex]::Match($Src, 'async\s+function\s+' + [regex]::Escape($Name) + '\s*\(')
    if (-not $start.Success) { return '' }
    $braceAt = $Src.IndexOf('{', $start.Index)
    if ($braceAt -lt 0) { return '' }
    $depth = 0
    for ($i = $braceAt; $i -lt $Src.Length; $i++) {
        $ch = $Src[$i]
        if ($ch -eq '{') { $depth++ }
        elseif ($ch -eq '}') {
            $depth--
            if ($depth -eq 0) {
                return $Src.Substring($braceAt, $i - $braceAt + 1)
            }
        }
    }
    return ''
}

function Test-CallsInstaller([string]$Src) {
    $code = Get-CodeWithoutStrings $Src
    return [bool]($code -match 'installTtsSeam\s*\(')
}

function Test-GateOutsideStrings([string]$Src) {
    return [bool]((Get-CodeWithoutStrings $Src) -match '__e2eSeamInstalled')
}

function Assert-CallsInstaller([string]$Src, [string]$CaseId) {
    if (-not (Test-CallsInstaller $Src)) {
        Write-Error ($CaseId + ' missing E2E_SEAM_INSTALL call installTtsSeam(')
        exit 1
    }
}

function Get-CodeWithoutStrings([string]$Src) {
    $out = [regex]::Replace($Src, '(?s)"(?:\\.|[^"\\])*"', '""')
    $out = [regex]::Replace($out, "(?s)'(?:\\.|[^'\\])*'", "''")
    $out = [regex]::Replace($out, '(?s)`(?:\\.|[^`\\])*`', '``')
    return $out
}

function Test-ExecutableSeamCalls([string]$Body) {
    $code = Get-CodeWithoutStrings $Body
    return [bool]($code -match 'addInitScript\s*\(' -and $code -match 'window\.fetch\s*=' -and $code -match 'reload\s*\(' -and $code -match 'new\s+Response')
}

function Assert-ExecutableSeamBody([string]$Body, [string]$Label) {
    $code = Get-CodeWithoutStrings $Body
    Assert-Contains $code 'addInitScript\s*\(' ($Label + ' missing page.addInitScript( outside strings')
    Assert-Contains $code 'window\.fetch\s*=' ($Label + ' missing window.fetch = outside strings')
    Assert-Contains $code 'new\s+Response' ($Label + ' missing new Response outside strings')
    Assert-Contains $code 'reload\s*\(' ($Label + ' missing reload( outside strings')
    Assert-Contains $Body '__e2eSeamInstalled' ($Label + ' missing __e2eSeamInstalled')
    Assert-Contains $Body '__e2eCalls' ($Label + ' missing __e2eCalls')
    Assert-Contains $Body 'E2E_SEAM_UNHANDLED' ($Label + ' missing E2E_SEAM_UNHANDLED')
    Assert-Contains $Body '\b599\b' ($Label + ' missing HTTP 599')
    foreach ($prefix in @('/tts', '/models', '/settings/tts')) {
        Assert-Contains $Body ([regex]::Escape($prefix)) ($Label + ' missing protected prefix ' + $prefix)
    }
    foreach ($line in ($code -split "`r?`n")) {
        if ($line -match '(originalFetch|origFetch|nativeFetch)\s*\(' -and $line -match '/tts|/models|/settings/tts') {
            Write-Error ($Label + ' calls original fetch on a protected prefix')
            exit 1
        }
    }
}

$visualOracle = 'toBeVisible|toBeHidden|toBeAttached|toHaveCSS'
$r41FalsePass = "page.getByTestId('text-input'); await expect(unrelatedLocator).toBeVisible();"
if (Test-HasBound $r41FalsePass 'text-input' $visualOracle) {
    Write-Error 'E2E_PER_CONTROL helper false-pass on unrelated receiver (R4-1)'
    exit 1
}
if (-not (Test-HasBound "await expect(page.getByTestId('text-input')).toBeVisible()" 'text-input' 'toBeVisible')) {
    Write-Error 'E2E_PER_CONTROL helper missed same-expression expect().toBeVisible'
    exit 1
}
if (-not (Test-HasBound "await page.getByTestId('generate-btn').click(" 'generate-btn' 'click\(')) {
    Write-Error 'E2E_PER_CONTROL helper missed same-expression .click('
    exit 1
}

$tokenOnlyW24 = @"
test('W2-4 happy', async () => {
  expect('addInitScript window.fetch = /tts /models /settings/tts 599 new Response E2E_SEAM_NEG __e2e-unhandled E2E_SEAM_UNHANDLED enabled_steps reload __e2eSeamInstalled __e2eCalls').toBeTruthy()
})
"@
if (Test-CallsInstaller $tokenOnlyW24) {
    Write-Error 'E2E_SEAM_PROOF helper false-pass on token-only W2-4 blob (R2-F1)'
    exit 1
}
$w5NoSeam = @"
test('W2-5 actuate', async () => {
  await page.getByTestId('generate-btn').click()
  await page.getByTestId('model-get-btn').click()
  await page.getByTestId('model-load-btn').click()
})
"@
if (Test-CallsInstaller $w5NoSeam) {
    Write-Error 'E2E_SEAM_PROOF helper false-pass on W2-5 actuation without installTtsSeam (R2-F1)'
    exit 1
}
if (-not (Test-CallsInstaller 'await installTtsSeam(page)')) {
    Write-Error 'E2E_SEAM_PROOF helper missed executable installTtsSeam( call'
    exit 1
}
$quotedW24 = @"
test('W2-4 happy', async () => {
  expect('installTtsSeam( E2E_SEAM_NEG __e2e-unhandled 599').toBeTruthy()
  await page.getByTestId('text-input').fill('x')
  await page.getByTestId('preview-cleanup-btn').click()
  await page.getByTestId('generate-btn').click()
})
"@
if (Test-CallsInstaller $quotedW24) {
    Write-Error 'E2E_SEAM_PROOF helper false-pass on quoted installTtsSeam( in W2-4 (R3-F1)'
    exit 1
}
$quotedW25 = @"
test('W2-5 actuate', async () => {
  expect('installTtsSeam( __e2eSeamInstalled').toBeTruthy()
  await page.getByTestId('generate-btn').click()
  await page.getByTestId('model-get-btn').click()
  await page.getByTestId('model-load-btn').click()
})
"@
if (Test-CallsInstaller $quotedW25) {
    Write-Error 'E2E_SEAM_PROOF helper false-pass on quoted installTtsSeam( in W2-5 (R3-F1)'
    exit 1
}
if (Test-GateOutsideStrings $quotedW25) {
    Write-Error 'E2E_SEAM_GATE helper false-pass on quoted __e2eSeamInstalled in W2-5 (R3-F1)'
    exit 1
}
if (-not (Test-GateOutsideStrings 'expect(window.__e2eSeamInstalled).toBe(true)')) {
    Write-Error 'E2E_SEAM_GATE helper missed executable __e2eSeamInstalled gate'
    exit 1
}
$stringOnlyInstaller = 'async function installTtsSeam(page) { return "addInitScript( window.fetch = /tts /models /settings/tts 599 new Response E2E_SEAM_UNHANDLED reload(" }'
$stringOnlyBody = Get-FunctionBody $stringOnlyInstaller 'installTtsSeam'
if (Test-ExecutableSeamCalls $stringOnlyBody) {
    Write-Error 'E2E_SEAM_INSTALL helper false-pass on string-only installer body (R2-F1)'
    exit 1
}

$ids = @(
    'tts-page', 'text-input', 'model-manager', 'voice-grid', 'generate-btn',
    'speed-slider', 'cleanup-pipeline', 'preview-cleanup-btn', 'load-file-btn',
    'paste-btn', 'word-count', 'sentence-count', 'duration-estimate',
    'preview-raw', 'preview-cleaned', 'language-select', 'format-select',
    'device-select', 'output-path', 'browse-output-btn', 'cancel-btn',
    'segment-progress', 'last-output', 'open-output-btn', 'open-output-folder-btn',
    'loaded-model', 'unload-btn', 'model-row', 'model-get-btn', 'model-load-btn',
    'voice-card', 'download-progress'
)
$registry = 'ui/tests/e2e/test-ids.ts'
$wave2 = 'ui/tests/e2e/tts-generate.test.ts'
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
foreach ($id in @('tts-page', 'text-input')) { Assert-HasBound $w1 $id 'toBeVisible' }

$w2 = Get-CaseBlock $waveSrc 'W2-2'
Assert-HasBound $w2 'tts-page' 'toBeVisible'
if ($w2 -notmatch 'nav-tts') { Write-Error 'W2-2 missing nav-tts'; exit 1 }

$w3 = Get-CaseBlock $waveSrc 'W2-3'
$pageChromeVisible = @(
    'text-input', 'load-file-btn', 'paste-btn', 'cleanup-pipeline',
    'preview-cleanup-btn', 'model-manager', 'voice-grid', 'generate-btn',
    'speed-slider', 'cancel-btn', 'browse-output-btn'
)
foreach ($id in $pageChromeVisible) { Assert-HasBound $w3 $id 'toBeVisible' }
Assert-HasBound $w3 'segment-progress' 'toBeAttached|toHaveCount'

$installerBody = Get-FunctionBody $waveSrc 'installTtsSeam'
if ([string]::IsNullOrWhiteSpace($installerBody)) {
    Write-Error 'missing file-level E2E_SEAM_INSTALL async function installTtsSeam'
    exit 1
}
Assert-ExecutableSeamBody $installerBody 'E2E_SEAM_INSTALL'
foreach ($caseId in @('W2-1', 'W2-2', 'W2-3', 'W2-4', 'W2-5', 'W2-6')) {
    Assert-CallsInstaller (Get-CaseBlock $waveSrc $caseId) $caseId
}

$w4 = Get-CaseBlock $waveSrc 'W2-4'
Assert-HasBound $w4 'text-input' 'fill\('
Assert-HasBound $w4 'preview-cleanup-btn' 'click\('
Assert-HasBound $w4 'generate-btn' 'click\('
foreach ($id in @('preview-cleaned', 'last-output')) {
    Assert-HasBound $w4 $id 'toBeVisible'
}
Assert-Contains $w4 'enabled_steps' 'W2-4 missing PREPARE/GENERATE enabled_steps'
Assert-Contains $w4 'E2E_SEAM_NEG' 'W2-4 missing E2E_SEAM_NEG token'
Assert-Contains $w4 '__e2e-unhandled' 'W2-4 missing unhandled protected URL token __e2e-unhandled'
Assert-Contains $w4 '\b599\b' 'W2-4 missing E2E_SEAM_NEG HTTP 599 assertion'
if ($w4 -match 'page\.route' -and -not (Test-CallsInstaller $w4)) {
    Write-Error 'W2-4 page.route-only seam is not E2E_SEAM_PROOF'
    exit 1
}

$w5 = Get-CaseBlock $waveSrc 'W2-5'
if (-not (Test-GateOutsideStrings $w5)) {
    Write-Error 'W2-5 missing E2E_SEAM_GATE assert outside strings before Generate/Get/Load'
    exit 1
}
$restActuate = @(
    @{ Id = 'preview-cleanup-btn'; Path = '/tts/prepare' },
    @{ Id = 'generate-btn'; Path = '/tts/generate' },
    @{ Id = 'cancel-btn'; Path = '/tts/' },
    @{ Id = 'browse-output-btn'; Path = '/settings/tts' },
    @{ Id = 'unload-btn'; Path = '/models/unload' },
    @{ Id = 'model-get-btn'; Path = '/models/download' },
    @{ Id = 'model-load-btn'; Path = '/models/load' }
)
foreach ($row in $restActuate) {
    Assert-HasBound $w5 $row.Id 'click\('
    Assert-Contains $w5 ([regex]::Escape($row.Path)) ('W2-5 missing REST observable for ' + $row.Id + ' (' + $row.Path + ')')
}
$ipcActuate = @(
    @{ Id = 'load-file-btn'; Channel = 'readTextFile' },
    @{ Id = 'paste-btn'; Channel = 'readClipboardText' },
    @{ Id = 'open-output-btn'; Channel = 'openPath' },
    @{ Id = 'open-output-folder-btn'; Channel = 'showItemInFolder' },
    @{ Id = 'browse-output-btn'; Channel = 'showDirectoryDialog' }
)
foreach ($row in $ipcActuate) {
    Assert-HasBound $w5 $row.Id 'click\('
    Assert-Contains $w5 ([regex]::Escape($row.Channel)) ('W2-5 missing per-control IPC channel ' + $row.Channel + ' for ' + $row.Id)
}
Assert-Contains $w5 '__e2eIpc' 'W2-5 missing E2E_IPC_LEDGER __e2eIpc'
Assert-HasBound $w5 'voice-card' 'click\('
Assert-Contains $w5 '/settings/tts' 'W2-5 missing PUT /settings/tts for voice-card'
if ($w5 -notmatch "'voice'" -and $w5 -notmatch '"voice"') {
    Write-Error 'W2-5 missing voice key on PUT /settings/tts'
    exit 1
}
foreach ($id in @('language-select', 'format-select', 'device-select')) {
    Assert-HasBound $w5 $id 'toBeVisible'
}
Assert-HasBound $w5 'segment-progress' 'toBeVisible'
if ($w5 -match "getByTestId\('segment-progress'\)\)\s*\.toBeHidden") {
    Write-Error 'W2-5 uses toBeHidden as a presence oracle (E2E_ATTACHED_FIRST)'
    exit 1
}

$w6 = Get-CaseBlock $waveSrc 'W2-6'
Assert-HasBound $w6 'tts-page' 'toBeVisible'
if ($w6 -notmatch 'tts:prepare') { Write-Error 'W2-6 missing palette id tts:prepare'; exit 1 }

'PASS: E2E_CONTROL_CENSUS'
exit 0
