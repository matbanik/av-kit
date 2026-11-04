# Sole executable owner of E2E_CONTROL_CENSUS (plan named set).
# Consumes E2E_CASES and WAVE9_* groups from named-sets.json (PR-9).
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

function Get-CompactJs([string]$Text) {
    return ([regex]::Replace([string]$Text, '\s+', ' ')).Trim()
}

function Get-RequiredPostListener {
    $c = [string]$script:Wave9PostCounter
    $m = [string]$script:Wave9PostMethod
    $p = [string]$script:Wave9CapturePostPath
    if ([string]::IsNullOrWhiteSpace($c) -or [string]::IsNullOrWhiteSpace($m) -or [string]::IsNullOrWhiteSpace($p)) {
        return ''
    }
    return Get-CompactJs ("page.on('request', (req) => { if (req.method() === '" + $m + "' && new URL(req.url()).pathname === '" + $p + "') { " + $c + " += 1 } })")
}

function Test-PostZero([string]$Block) {
    $counter = [string]$script:Wave9PostCounter
    $required = Get-RequiredPostListener
    if ([string]::IsNullOrWhiteSpace($counter) -or [string]::IsNullOrWhiteSpace($required)) { return $false }
    $compact = Get-CompactJs $Block
    if ($compact.Contains($required) -eq $false) { return $false }
    $expectZero = Get-CompactJs ('expect(' + $counter + ').toBe(0)')
    if ($compact.Contains($expectZero) -eq $false) { return $false }
    if ($compact.Contains('expect(0).toBe(0)')) { return $false }
    return $true
}

function Assert-PostZero([string]$Block, [string]$CaseId) {
    if (-not (Test-PostZero $Block)) {
        Write-Error ($CaseId + ' WAVE9_POST_ZERO_ORACLE requires WAVE9_REGISTER_POST compact listener (method+pathname predicates wrapping WAVE9_POST_COUNTER += 1) and expect(WAVE9_POST_COUNTER).toBe(0)')
        exit 1
    }
}

$setsPathEarly = Join-Path $PSScriptRoot 'named-sets.json'
$script:Wave9PostCounter = ''
$script:Wave9PostMethod = ''
$script:Wave9CapturePostPath = ''
if (Test-Path -LiteralPath $setsPathEarly) {
    $earlySets = Get-Content -LiteralPath $setsPathEarly -Raw | ConvertFrom-Json
    $script:Wave9PostCounter = [string]$earlySets.WAVE9_POST_COUNTER
    $script:Wave9PostMethod = [string]$earlySets.WAVE9_POST_METHOD
    $script:Wave9CapturePostPath = [string]$earlySets.WAVE9_CAPTURE_POST_PATH
}
$c = [string]$script:Wave9PostCounter
$p = [string]$script:Wave9CapturePostPath
$m = [string]$script:Wave9PostMethod
$vacuousPostZero = "await page.getByTestId('nav-capture').click(); '/captures POST'; expect(0).toBe(0)"
if (Test-PostZero $vacuousPostZero) {
    Write-Error 'WAVE9_POST_ZERO_ORACLE helper false-pass on expect(0).toBe(0) / bare /captures POST'
    exit 1
}
$noopPostZero = "let " + $c + " = 0; page.on('request', () => {}); '" + $p + "'; expect(" + $c + ").toBe(0)"
if (Test-PostZero $noopPostZero) {
    Write-Error 'WAVE9_POST_ZERO_ORACLE helper false-pass on no-op request listener plus route literal'
    exit 1
}
$unconditionalPostZero = "page.on('request', (req) => { " + $c + " += 1 }); expect(" + $c + ").toBe(0)"
if (Test-PostZero $unconditionalPostZero) {
    Write-Error 'WAVE9_POST_ZERO_ORACLE helper false-pass on increment without method/path predicates'
    exit 1
}
$includesPostZero = "page.on('request', (req) => { if (req.method() === '" + $m + "' && req.url().includes('" + $p + "')) { " + $c + " += 1 } }); expect(" + $c + ").toBe(0)"
if (Test-PostZero $includesPostZero) {
    Write-Error 'WAVE9_POST_ZERO_ORACLE helper false-pass on url().includes(path) (suffix would count)'
    exit 1
}
$canonicalPostZero = (Get-RequiredPostListener) + '; expect(' + $c + ').toBe(0)'
if (-not (Test-PostZero $canonicalPostZero)) {
    Write-Error 'WAVE9_POST_ZERO_ORACLE helper missed canonical listener + expect zero'
    exit 1
}
$multilinePostZero = @"
page.on('request', (req) => {
  if (req.method() === '$m' && new URL(req.url()).pathname === '$p') {
    $c += 1
  }
})
expect($c).toBe(0)
"@
if (-not (Test-PostZero $multilinePostZero)) {
    Write-Error 'WAVE9_POST_ZERO_ORACLE helper missed whitespace-normalized canonical listener'
    exit 1
}

$visualOracle = 'toBeVisible|toBeHidden|toBeAttached|toHaveCSS'
$r41FalsePass = "page.getByTestId('capture-page'); await expect(unrelatedLocator).toBeVisible();"
if (Test-HasBound $r41FalsePass 'capture-page' $visualOracle) {
    Write-Error 'E2E_PER_CONTROL helper false-pass on unrelated receiver (R4-1)'
    exit 1
}
if (-not (Test-HasBound "await expect(page.getByTestId('capture-page')).toBeVisible()" 'capture-page' 'toBeVisible')) {
    Write-Error 'E2E_PER_CONTROL helper missed same-expression expect().toBeVisible'
    exit 1
}
if (-not (Test-HasBound "await page.getByTestId('capture-region').click(" 'capture-region' 'click\(')) {
    Write-Error 'E2E_PER_CONTROL helper missed same-expression .click('
    exit 1
}

$setsPath = Join-Path $PSScriptRoot 'named-sets.json'
$sets = Get-Content -LiteralPath $setsPath -Raw | ConvertFrom-Json
$ids = @($sets.WAVE9_TESTIDS) + @($sets.WAVE9_EXTRA_TESTIDS)
$registry = 'ui/tests/e2e/test-ids.ts'
$wave9 = [string]$sets.E2E_WAVE9
$wave0 = 'ui/tests/e2e/launch.test.ts'
$cases = @($sets.E2E_CASES)
if ($cases.Count -lt 1) {
    Write-Error 'E2E_CASES empty'
    exit 1
}
foreach ($f in @($registry, $wave9, $wave0)) {
    if (-not (Test-Path -LiteralPath $f)) {
        Write-Error ("missing " + $f)
        exit 1
    }
}
$regText = Get-Content -LiteralPath $registry -Raw
$waveSrc = Get-StrippedSource $wave9
if ($waveSrc -match 'test\.skip|test\.only|\.only\(') {
    Write-Error 'E2E_WAVE9 contains skip/only'
    exit 1
}
foreach ($id in $ids) {
    if ($regText -notmatch [regex]::Escape($id)) {
        Write-Error ("testid not registered: " + $id)
        exit 1
    }
}

$wave0Text = Get-Content -LiteralPath $wave0 -Raw
$navCapture = [string]$sets.NAV_CAPTURE
if ($wave0Text -notmatch [regex]::Escape($navCapture)) {
    Write-Error ('wave0 missing ' + $navCapture)
    exit 1
}
$keepConvert = [string]$sets.KEEP_NAV_CONVERT
if ($wave0Text -notmatch [regex]::Escape($keepConvert)) {
    Write-Error ('wave0 missing KEEP_NAV_CONVERT ' + $keepConvert)
    exit 1
}

$visual = 'toBeVisible|toBeHidden|toBeAttached|toHaveCSS'
$enabled = 'toBeEnabled|toBeDisabled'
$interactBind = [string]$sets.WAVE9_INTERACT_BIND
if ([string]::IsNullOrWhiteSpace($interactBind)) {
    Write-Error 'WAVE9_INTERACT_BIND empty'
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

$w1 = $blocks['W9-1']
foreach ($id in @($sets.WAVE9_W9_1_VISIBLE)) { Assert-HasBound $w1 $id 'toBeVisible' }

$w2 = $blocks['W9-2']
Assert-HasBound $w2 'capture-page' 'toBeVisible'
foreach ($id in @($sets.WAVE9_W9_2_CLICK)) { Assert-HasBound $w2 $id 'click\(' }
Assert-PostZero $w2 'W9-2'

$w3 = $blocks['W9-3']
foreach ($id in @($sets.WAVE9_W9_3_VISIBLE)) { Assert-HasBound $w3 $id $visual }
foreach ($id in @($sets.WAVE9_W9_3_TOOL_CLICK)) { Assert-HasBound $w3 $id 'click\(' }
foreach ($id in @($sets.WAVE9_W9_3_FILL)) { Assert-HasBound $w3 $id 'fill\(' }
$settingsNav = [string]$sets.WAVE9_W9_3_SETTINGS_NAV
Assert-HasBound $w3 $settingsNav 'click\('
foreach ($id in @($sets.WAVE9_W9_3_SETTINGS)) { Assert-HasBound $w3 $id $visual }
foreach ($id in @($sets.WAVE9_W9_3_SETTINGS_INTERACT)) { Assert-HasBound $w3 $id 'click\(|fill\(' }

$w4 = $blocks['W9-4']
foreach ($id in @($sets.WAVE9_W9_4_REGION_CLICK)) { Assert-HasBound $w4 $id 'click\(' }
Assert-HasBound $w4 'capture-filmstrip-item' 'toBeVisible'
foreach ($id in @($sets.WAVE9_W9_4_DELETE_CLICK)) { Assert-HasBound $w4 $id 'click\(' }
foreach ($id in @($sets.WAVE9_W9_4_CONFIRM)) { Assert-HasBound $w4 $id 'click\(' }
if ($w4 -notmatch 'page\.route') { Write-Error 'W9-4 missing E2E_SEAM page.route'; exit 1 }

$w5 = $blocks['W9-5']
foreach ($id in @($sets.WAVE9_W9_5_ENABLED)) { Assert-HasBound $w5 $id $enabled }

$w6 = $blocks['W9-6']
if ($w6 -notmatch 'capture:region') { Write-Error 'W9-6 missing palette id capture:region'; exit 1 }
Assert-PostZero $w6 'W9-6'

$allBlocks = ($blocks.Values -join "`n")
$visualOnly = @($sets.WAVE9_VISUAL_ONLY)
foreach ($id in $ids) {
    if ($visualOnly -contains $id) {
        if (-not (Test-HasBound $allBlocks $id $visual)) {
            Write-Error ("WAVE9 totality: visual-only testid never bound: " + $id)
            exit 1
        }
    } else {
        if (-not (Test-HasBound $allBlocks $id $interactBind)) {
            Write-Error ("WAVE9 totality: interactive testid lacks click/fill/enabled/focus: " + $id)
            exit 1
        }
    }
}

'PASS: E2E_CONTROL_CENSUS'
exit 0
