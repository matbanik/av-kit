# Sole executable owner of E2E_CONTROL_CENSUS (plan named set).
# Consumes E2E_CASES and WAVE8_* groups from named-sets.json (PR-9).
# E2E_PER_CONTROL: after comment-strip, the allowed method must be
# chained on the same getByTestId('id') expression.
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

function Assert-PostZero([string]$Block, [string]$CaseId) {
    if ($Block -notmatch '/conversions') {
        Write-Error ($CaseId + ' missing /conversions in WAVE8_POST_ZERO_ORACLE')
        exit 1
    }
    if ($Block -notmatch '(?i)post') {
        Write-Error ($CaseId + ' missing POST in WAVE8_POST_ZERO_ORACLE')
        exit 1
    }
    if ($Block -notmatch 'toBe\(0\)|toEqual\(0\)') {
        Write-Error ($CaseId + ' missing toBe(0)|toEqual(0) in WAVE8_POST_ZERO_ORACLE')
        exit 1
    }
}

$visualOracle = 'toBeVisible|toBeHidden|toBeAttached|toHaveCSS'
$r41FalsePass = "page.getByTestId('convert-page'); await expect(unrelatedLocator).toBeVisible();"
if (Test-HasBound $r41FalsePass 'convert-page' $visualOracle) {
    Write-Error 'E2E_PER_CONTROL helper false-pass on unrelated receiver (R4-1)'
    exit 1
}
if (-not (Test-HasBound "await expect(page.getByTestId('convert-page')).toBeVisible()" 'convert-page' 'toBeVisible')) {
    Write-Error 'E2E_PER_CONTROL helper missed same-expression expect().toBeVisible'
    exit 1
}
if (-not (Test-HasBound "await page.getByTestId('convert-add').click(" 'convert-add' 'click\(')) {
    Write-Error 'E2E_PER_CONTROL helper missed same-expression .click('
    exit 1
}

$setsPath = Join-Path $PSScriptRoot 'named-sets.json'
$sets = Get-Content -LiteralPath $setsPath -Raw | ConvertFrom-Json
$ids = @($sets.WAVE8_TESTIDS) + @($sets.WAVE8_EXTRA_TESTIDS)
$registry = 'ui/tests/e2e/test-ids.ts'
$wave8 = [string]$sets.E2E_WAVE8
$wave0 = 'ui/tests/e2e/launch.test.ts'
$cases = @($sets.E2E_CASES)
if ($cases.Count -lt 1) {
    Write-Error 'E2E_CASES empty'
    exit 1
}
foreach ($f in @($registry, $wave8, $wave0)) {
    if (-not (Test-Path -LiteralPath $f)) {
        Write-Error ("missing " + $f)
        exit 1
    }
}
$regText = Get-Content -LiteralPath $registry -Raw
$waveSrc = Get-StrippedSource $wave8
if ($waveSrc -match 'test\.skip|test\.only|\.only\(') {
    Write-Error 'E2E_WAVE8 contains skip/only'
    exit 1
}
foreach ($id in $ids) {
    if ($regText -notmatch [regex]::Escape($id)) {
        Write-Error ("testid not registered: " + $id)
        exit 1
    }
}

$wave0Text = Get-Content -LiteralPath $wave0 -Raw
$navConvert = [string]$sets.NAV_CONVERT
if ($wave0Text -notmatch [regex]::Escape($navConvert)) {
    Write-Error ('wave0 missing ' + $navConvert)
    exit 1
}

$visual = 'toBeVisible|toBeHidden|toBeAttached|toHaveCSS'
$enabled = 'toBeEnabled|toBeDisabled'
$interactBind = [string]$sets.WAVE8_INTERACT_BIND
if ([string]::IsNullOrWhiteSpace($interactBind)) {
    Write-Error 'WAVE8_INTERACT_BIND empty'
    exit 1
}
$blocks = @{}
foreach ($caseId in $cases) {
    $block = Get-CaseBlock $waveSrc $caseId
    if ([string]::IsNullOrWhiteSpace($block)) {
        Write-Error ("E2E_CASES missing test() titled " + $caseId)
        exit 1
    }
    if ($block -notmatch 'expect\(') {
        Write-Error ($caseId + ' missing expect(')
        exit 1
    }
    $blocks[$caseId] = $block
}

$w1 = $blocks['W8-1']
foreach ($id in @($sets.WAVE8_W8_1_VISIBLE)) { Assert-HasBound $w1 $id 'toBeVisible' }

$w2 = $blocks['W8-2']
Assert-HasBound $w2 'convert-page' 'toBeVisible'
foreach ($id in @($sets.WAVE8_W8_2_CLICK)) { Assert-HasBound $w2 $id 'click\(' }
Assert-PostZero $w2 'W8-2'

$w3 = $blocks['W8-3']
foreach ($id in @($sets.WAVE8_W8_3_VISIBLE)) { Assert-HasBound $w3 $id $visual }
foreach ($id in @($sets.WAVE8_W8_3_TASK_CLICKS)) { Assert-HasBound $w3 $id 'click\(' }
foreach ($id in @($sets.WAVE8_W8_3_PRESET_CLICK)) { Assert-HasBound $w3 $id 'click\(' }
foreach ($id in @($sets.WAVE8_W8_3_FILL)) { Assert-HasBound $w3 $id 'fill\(' }
foreach ($id in @($sets.WAVE8_W8_3_TOGGLE_CLICK)) { Assert-HasBound $w3 $id 'click\(' }
foreach ($id in @($sets.WAVE8_W8_3_CUT)) { Assert-HasBound $w3 $id $visual }
foreach ($id in @($sets.WAVE8_W8_3_EXTRACT)) { Assert-HasBound $w3 $id $visual }
foreach ($id in @($sets.WAVE8_W8_3_ADVANCED)) { Assert-HasBound $w3 $id $visual }
foreach ($id in @($sets.WAVE8_W8_3_ADVANCED_CLICK)) { Assert-HasBound $w3 $id 'click\(' }
$settingsNav = [string]$sets.WAVE8_W8_3_SETTINGS_NAV
Assert-HasBound $w3 $settingsNav 'click\('
foreach ($id in @($sets.WAVE8_W8_3_SETTINGS)) { Assert-HasBound $w3 $id $visual }
foreach ($id in @($sets.WAVE8_W8_3_SETTINGS_INTERACT)) { Assert-HasBound $w3 $id 'click\(|fill\(' }

$w4 = $blocks['W8-4']
Assert-HasBound $w4 'convert-browse' 'click\('
Assert-HasBound $w4 'convert-add' 'click\('
Assert-HasBound $w4 'convert-queue-row' 'toBeVisible'
foreach ($id in @($sets.WAVE8_W8_4_REMOVE_CLICK)) { Assert-HasBound $w4 $id 'click\(' }
foreach ($id in @($sets.WAVE8_W8_4_CONFIRM)) { Assert-HasBound $w4 $id 'click\(' }
if ($w4 -notmatch 'page\.route') { Write-Error 'W8-4 missing E2E_SEAM page.route'; exit 1 }

$w5 = $blocks['W8-5']
foreach ($id in @($sets.WAVE8_W8_5_ENABLED)) { Assert-HasBound $w5 $id $enabled }

$w6 = $blocks['W8-6']
Assert-HasBound $w6 'convert-dropzone' 'toBeFocused'
if ($w6 -notmatch 'convert:add') { Write-Error 'W8-6 missing palette id convert:add'; exit 1 }
Assert-PostZero $w6 'W8-6'

$allBlocks = ($blocks.Values -join "`n")
$visualOnly = @($sets.WAVE8_VISUAL_ONLY)
foreach ($id in $ids) {
    if ($visualOnly -contains $id) {
        if (-not (Test-HasBound $allBlocks $id $visual)) {
            Write-Error ("WAVE8 totality: visual-only testid never bound: " + $id)
            exit 1
        }
    } else {
        if (-not (Test-HasBound $allBlocks $id $interactBind)) {
            Write-Error ("WAVE8 totality: interactive testid lacks click/fill/enabled/focus: " + $id)
            exit 1
        }
    }
}

'PASS: E2E_CONTROL_CENSUS'
exit 0
