# Sole executable owner of E2E_CONTROL_CENSUS / E2E_CASE_ORACLES (plan named sets).
# E2E_PER_CONTROL: after comment-strip, the allowed method must be
# chained on the same getByTestId('id') expression
# (expect(page.getByTestId('id')).toBeVisible() or
# page.getByTestId('id').click()). A nearby method on an unrelated
# receiver is a fail. Owner: Test-HasBound / Assert-HasBound.
# Closed-panel oracle is same-expression getByTestId('console-panel').toHaveCount(0).
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

function Assert-ContainsLiteral([string]$Src, [string]$Needle, [string]$Label) {
    if ($Src.IndexOf($Needle) -lt 0) {
        Write-Error ($Label + ' missing literal ' + $Needle)
        exit 1
    }
}

function Get-BoundMatchCount([string]$Src, [string]$Id, [string]$MethodsRegex) {
    $lit = [regex]::Escape("getByTestId('" + $Id + "')")
    $pattern = $lit + '(?:\)\s*)?\s*\.(' + $MethodsRegex + ')'
    return [regex]::Matches($Src, $pattern).Count
}

function Get-LastBoundIndex([string]$Src, [string]$Id, [string]$MethodsRegex) {
    $lit = [regex]::Escape("getByTestId('" + $Id + "')")
    $pattern = $lit + '(?:\)\s*)?\s*\.(' + $MethodsRegex + ')'
    $ms = [regex]::Matches($Src, $pattern)
    if ($ms.Count -eq 0) { return -1 }
    return $ms[$ms.Count - 1].Index
}

function Assert-C14EachPathEndsAbsent([string]$Src) {
    $zero = 'toHaveCount\(0\)'
    $actions = @(
        @{ Name = 'C1-4 X'; Index = Get-LastBoundIndex $Src 'console-close' 'click\(' },
        @{ Name = 'C1-4 collapse'; Index = Get-LastBoundIndex $Src 'console-collapse' 'click\(' },
        @{ Name = 'C1-4 header toggle'; Index = Get-LastBoundIndex $Src 'header-console-btn' 'click\(' },
        @{ Name = 'C1-4 Escape'; Index = $Src.LastIndexOf('Escape') }
    )
    foreach ($action in $actions) {
        if ($action.Index -lt 0) {
            Write-Error ($action.Name + ' missing close-path action')
            exit 1
        }
    }
    $ordered = @($actions | Sort-Object Index)
    for ($i = 0; $i -lt $ordered.Count; $i++) {
        $start = $ordered[$i].Index
        $end = if ($i -lt ($ordered.Count - 1)) { $ordered[$i + 1].Index } else { $Src.Length }
        $window = $Src.Substring($start, ($end - $start))
        if (-not (Test-HasBound $window 'console-panel' $zero)) {
            Write-Error ($ordered[$i].Name + ' missing console-panel toHaveCount(0) before next close path')
            exit 1
        }
    }
}

$visualOracle = 'toBeVisible|toBeHidden|toBeAttached|toHaveCSS'
$r41FalsePass = "page.getByTestId('header-console-btn'); await expect(unrelatedLocator).toBeVisible();"
if (Test-HasBound $r41FalsePass 'header-console-btn' $visualOracle) {
    Write-Error 'E2E_PER_CONTROL helper false-pass on unrelated receiver (R4-1)'
    exit 1
}
if (-not (Test-HasBound "await expect(page.getByTestId('header-console-btn')).toBeVisible()" 'header-console-btn' 'toBeVisible')) {
    Write-Error 'E2E_PER_CONTROL helper missed same-expression expect().toBeVisible'
    exit 1
}
if (-not (Test-HasBound "await page.getByTestId('header-console-btn').click(" 'header-console-btn' 'click\(')) {
    Write-Error 'E2E_PER_CONTROL helper missed same-expression .click('
    exit 1
}

$closedZero = 'toHaveCount(0)'
$closedOne = "await expect(page.getByTestId('console-panel')).toHaveCount(1)"
if ($closedOne.IndexOf($closedZero) -ge 0) {
    Write-Error 'C1-1 oracle helper false-pass: toHaveCount(1) must not satisfy toHaveCount(0)'
    exit 1
}

$c1UnrelatedZero = @"
await expect(page.getByTestId('console-panel')).toHaveCount(1)
await expect(unrelatedLocator).toHaveCount(0)
"@
if (Test-HasBound $c1UnrelatedZero 'console-panel' 'toHaveCount\(0\)') {
    Write-Error 'C1-1 oracle helper false-pass: unrelated toHaveCount(0) must not bind console-panel'
    exit 1
}
if (-not (Test-HasBound "await expect(page.getByTestId('console-panel')).toHaveCount(0)" 'console-panel' 'toHaveCount\(0\)')) {
    Write-Error 'C1-1 oracle helper missed same-expression console-panel toHaveCount(0)'
    exit 1
}

$c4SingleOracle = @"
await page.getByTestId('console-close').click()
await page.getByTestId('console-collapse').click()
await page.keyboard.press('Escape')
await page.getByTestId('header-console-btn').click()
await expect(page.getByTestId('console-panel')).toHaveCount(0)
"@
$c4Threw = $false
try {
    Assert-C14EachPathEndsAbsent $c4SingleOracle
} catch {
    $c4Threw = $true
}
if (-not $c4Threw) {
    Write-Error 'C1-4 oracle helper false-pass: four actions plus one trailing toHaveCount(0) must fail'
    exit 1
}

$ids = @(
    'header-console-btn', 'header-palette-btn', 'console-panel', 'console-filter',
    'console-search', 'console-clear', 'console-copy', 'console-collapse',
    'console-expand', 'console-close', 'console-ytdlp-toggle', 'console-log-to-file',
    'nav-collapse', 'nav-settings', 'settings-page', 'download-settings',
    'transcript-settings', 'tts-settings', 'console-settings', 'appearance-settings',
    'dependencies-section'
)
$registry = 'ui/tests/e2e/test-ids.ts'
$wave = 'ui/tests/e2e/console-chrome.test.ts'
foreach ($f in @($registry, $wave)) {
    if (-not (Test-Path -LiteralPath $f)) {
        Write-Error ("missing " + $f)
        exit 1
    }
}
$regText = Get-Content -LiteralPath $registry -Raw
$waveSrc = Get-StrippedSource $wave
if ($waveSrc -match 'test\.skip|test\.only|\.only\(') {
    Write-Error 'E2E_WAVE contains skip/only'
    exit 1
}
foreach ($id in $ids) {
    if ($regText -notmatch [regex]::Escape($id)) {
        Write-Error ("testid not registered: " + $id)
        exit 1
    }
}

$visual = 'toBeVisible|toBeHidden|toBeAttached|toHaveCSS'
foreach ($caseId in @('C1-1', 'C1-2', 'C1-3', 'C1-4', 'C1-5', 'C1-6')) {
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

$c1 = Get-CaseBlock $waveSrc 'C1-1'
Assert-HasBound $c1 'header-console-btn' $visual
Assert-HasBound $c1 'header-palette-btn' $visual
Assert-HasBound $c1 'console-panel' 'toHaveCount\(0\)'

$c2 = Get-CaseBlock $waveSrc 'C1-2'
Assert-HasBound $c2 'header-console-btn' 'click\('
foreach ($id in @('console-panel', 'console-filter', 'console-search', 'console-clear', 'console-ytdlp-toggle')) {
    Assert-HasBound $c2 $id $visual
}

$c3 = Get-CaseBlock $waveSrc 'C1-3'
Assert-HasBound $c3 'console-expand' 'click\('
Assert-ContainsLiteral $c3 'w-full' 'C1-3 expand geometry'
Assert-ContainsLiteral $c3 'min-w-[320px]' 'C1-3 restore geometry'

$c4 = Get-CaseBlock $waveSrc 'C1-4'
Assert-HasBound $c4 'console-close' 'click\('
Assert-HasBound $c4 'console-collapse' 'click\('
Assert-HasBound $c4 'header-console-btn' 'click\('
Assert-ContainsLiteral $c4 'Escape' 'C1-4'
if ((Get-BoundMatchCount $c4 'console-panel' 'toHaveCount\(0\)') -lt 4) {
    Write-Error 'C1-4 needs >=4 same-expression console-panel toHaveCount(0) oracles'
    exit 1
}
Assert-C14EachPathEndsAbsent $c4

$c5 = Get-CaseBlock $waveSrc 'C1-5'
Assert-HasBound $c5 'console-copy' 'click\('
Assert-HasBound $c5 'console-log-to-file' 'click\('
if ($c5 -notmatch 'clipboard') {
    Write-Error 'C1-5 missing clipboard write effect'
    exit 1
}
if ($c5 -notmatch [regex]::Escape('settings/app')) {
    Write-Error 'C1-5 missing LOG_TO_FILE_PUT path settings/app'
    exit 1
}
if ($c5 -notmatch 'log_to_file') {
    Write-Error 'C1-5 missing LOG_TO_FILE_PUT body log_to_file'
    exit 1
}

$c6 = Get-CaseBlock $waveSrc 'C1-6'
Assert-HasBound $c6 'nav-settings' $visual
Assert-HasBound $c6 'nav-collapse' 'click\('
Assert-ContainsLiteral $c6 'nav-rail--collapsed' 'C1-6'
foreach ($id in @('settings-page', 'download-settings', 'transcript-settings', 'tts-settings', 'console-settings', 'appearance-settings', 'dependencies-section')) {
    Assert-HasBound $c6 $id $visual
}

'PASS: E2E_CONTROL_CENSUS'
exit 0
