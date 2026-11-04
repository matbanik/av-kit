# Classify a named Playwright run (E2E_GREP / AC-61.17): assertion-red vs infrastructure vs pass.
# Case token is E2E_GREP from named-sets.json.
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('red', 'named', 'gate')]
    [string]$Mode,
    [string]$Receipt,
    [string]$JsonReceipt,
    [int]$PlaywrightExit = -1,
    [string]$PassReceipt,
    [string]$BlockedReceipt
)
$ErrorActionPreference = 'Stop'
$setsPath = Join-Path $PSScriptRoot 'named-sets.json'
$sets = Get-Content -LiteralPath $setsPath -Raw | ConvertFrom-Json
$case = [string]$sets.E2E_GREP
$sandbox = [string]$sets.E2E_SANDBOX
$namedMarker = [string]$sets.E2E_NAMED_MODE_MARKER
$redMarker = [string]$sets.E2E_RED_MODE_MARKER
if ([string]::IsNullOrWhiteSpace($PassReceipt)) { $PassReceipt = [string]$sets.E2E_PASS_RECEIPT }
$redBlocked = [string]$sets.E2E_RED_BLOCKED_RECEIPT
$namedBlocked = [string]$sets.E2E_NAMED_BLOCKED_RECEIPT
$greenReceipt = [string]$sets.E2E_GREEN_RECEIPT
$greenJson = [string]$sets.E2E_GREEN_JSON
$redReceipt = [string]$sets.RED_RECEIPT_E2E
$redJson = [string]$sets.RED_JSON_E2E
if ([string]::IsNullOrWhiteSpace($BlockedReceipt)) {
    if ($Mode -eq 'red') { $BlockedReceipt = $redBlocked }
    else { $BlockedReceipt = $namedBlocked }
}

function Test-Infra([string]$text) {
    foreach ($tok in @($sets.E2E_INFRA_TOKENS)) {
        if ($text.Contains([string]$tok)) { return $true }
    }
    return $false
}

function Walk-Playwright($node, [string]$Case, [ref]$passed, [ref]$failed, [ref]$ran, [ref]$skipped) {
    if ($null -eq $node) { return }
    foreach ($spec in @($node.specs)) {
        $titleHit = ([string]$spec.title).Contains($Case)
        $tests = @($spec.tests)
        if ($tests.Count -eq 0) {
            if ($titleHit) {
                $ran.Value = $true
                $ok = $false
                if ($null -ne $spec.PSObject.Properties['ok']) { $ok = [bool]$spec.ok }
                if ($ok) { $passed.Value = $true } else { $failed.Value = $true }
            }
            continue
        }
        foreach ($t in $tests) {
            $testHit = $titleHit
            if ([string]$t.title -and ([string]$t.title).Contains($Case)) { $testHit = $true }
            if (-not $testHit) { continue }
            $ran.Value = $true
            $saw = $false
            foreach ($r in @($t.results)) {
                $st = [string]$r.status
                if ([string]::IsNullOrWhiteSpace($st)) { continue }
                $saw = $true
                if ($st -eq 'passed' -or $st -eq 'expected') { $passed.Value = $true }
                if ($st -in @('failed', 'timedOut', 'interrupted', 'unexpected')) { $failed.Value = $true }
                if ($st -eq 'skipped') { $skipped.Value = $true }
            }
            if (-not $saw) {
                $ok = $false
                if ($null -ne $spec.PSObject.Properties['ok']) { $ok = [bool]$spec.ok }
                if ($ok) { $passed.Value = $true } else { $failed.Value = $true }
            }
        }
    }
    foreach ($suite in @($node.suites)) {
        Walk-Playwright $suite $Case $passed $failed $ran $skipped
    }
}

function Get-Outcome {
    param([string]$Text, [string]$JsonPath, [string]$Case)
    $passed = $false
    $failed = $false
    $ran = $false
    $skipped = $false
    $infra = Test-Infra $Text
    $jsonParsed = $false
    if (-not [string]::IsNullOrWhiteSpace($JsonPath) -and (Test-Path -LiteralPath $JsonPath)) {
        $raw = Get-Content -LiteralPath $JsonPath -Raw
        if (-not [string]::IsNullOrWhiteSpace($raw)) {
            try {
                $json = $raw | ConvertFrom-Json
                $p = $false; $f = $false; $r = $false; $s = $false
                Walk-Playwright $json $Case ([ref]$p) ([ref]$f) ([ref]$r) ([ref]$s)
                $passed = $p; $failed = $f; $ran = $r; $skipped = $s
                $jsonParsed = $true
            } catch {
                $infra = $true
            }
        }
    }
    # Structured reporter proving the named test never ran wins over leftover stdout assertion text.
    if (-not ($jsonParsed -and -not $ran)) {
        if (-not $passed -and -not $failed) {
            if ($Text.Contains($Case) -and ($Text -match '(?i)(\d+)\s+failed' -or $Text.Contains('Error: expect') -or $Text.Contains('AssertionError'))) {
                $failed = $true
                $ran = $true
            }
            if ($Text.Contains($Case) -and ($Text -match '(?i)(\d+)\s+passed') -and $Text -notmatch '(?i)(\d+)\s+failed') {
                $passed = $true
                $ran = $true
            }
        }
    }
    return [pscustomobject]@{
        passed = $passed
        failed = $failed
        infra = $infra
        ran = $ran
        skipped = $skipped
        jsonParsed = $jsonParsed
    }
}

function Write-Blocked([string]$path, [string]$marker, [string]$text) {
    $hits = @($sets.E2E_INFRA_TOKENS | Where-Object { $text.Contains([string]$_) })
    @(
        $marker,
        ('BLOCKED: ' + $sandbox),
        ('PlaywrightExit=' + $PlaywrightExit)
    ) + $hits | Set-Content -LiteralPath $path
}

if ($Mode -eq 'gate') {
    if ([string]::IsNullOrWhiteSpace($redBlocked) -or [string]::IsNullOrWhiteSpace($namedBlocked) -or ($redBlocked -eq $namedBlocked)) {
        Write-Error 'E2E gate: E2E_RED_BLOCKED_RECEIPT and E2E_NAMED_BLOCKED_RECEIPT must be distinct nonempty paths'
        exit 1
    }
    if ([string]::IsNullOrWhiteSpace($greenReceipt) -or ($greenReceipt -eq $redReceipt)) {
        Write-Error 'E2E gate: E2E_GREEN_RECEIPT must differ from RED_RECEIPT_E2E'
        exit 1
    }
    if ([string]::IsNullOrWhiteSpace($greenJson) -or ($greenJson -eq $redJson)) {
        Write-Error 'E2E gate: E2E_GREEN_JSON must differ from RED_JSON_E2E'
        exit 1
    }
    if ((Test-Path -LiteralPath $greenReceipt) -and (Test-Path -LiteralPath $greenJson)) {
        $gText = Get-Content -LiteralPath $greenReceipt -Raw
        $g = Get-Outcome -Text $gText -JsonPath $greenJson -Case $case
        if ($g.failed) {
            Write-Error ('E2E gate: named Green run failed ' + $case + ' — cannot [B] an assertion failure')
            exit 1
        }
        if ($g.skipped -and -not $g.failed) {
            Write-Error ('E2E gate: named Green run skipped ' + $case + ' (G36)')
            exit 1
        }
        if ($g.passed -and -not $g.failed) {
            if ((Test-Path -LiteralPath $PassReceipt) -and ((Get-Content -LiteralPath $PassReceipt -Raw) -match [regex]::Escape($case))) {
                'PASS: named E2E from Green raw+JSON plus pass receipt'
                exit 0
            }
            Write-Error 'E2E gate: Green JSON passed but E2E_PASS_RECEIPT missing or does not cite the case'
            exit 1
        }
    }
    if (Test-Path -LiteralPath $namedBlocked) {
        $b = Get-Content -LiteralPath $namedBlocked -Raw
        if (-not $b.Contains($namedMarker)) {
            Write-Error 'E2E gate: named blocked receipt missing MODE=named marker'
            exit 1
        }
        if ($b.Contains($redMarker)) {
            Write-Error 'E2E gate: named blocked receipt contains MODE=red'
            exit 1
        }
        if (-not ($b.Contains($sandbox) -and (Test-Infra $b))) {
            Write-Error 'E2E gate: named blocked receipt missing E2E_SANDBOX or infra token'
            exit 1
        }
        if (-not (Test-Path -LiteralPath $greenReceipt)) {
            Write-Error 'E2E gate: named blocked requires E2E_GREEN_RECEIPT from the named run'
            exit 1
        }
        if (-not (Test-Path -LiteralPath $greenJson)) {
            Write-Error 'E2E gate: named blocked requires E2E_GREEN_JSON from the named run'
            exit 1
        }
        $gText = Get-Content -LiteralPath $greenReceipt -Raw
        $g = Get-Outcome -Text $gText -JsonPath $greenJson -Case $case
        if (-not $g.jsonParsed) {
            Write-Error 'E2E gate: named blocked requires parseable E2E_GREEN_JSON'
            exit 1
        }
        if ($g.failed) {
            Write-Error ('E2E gate: named blocked cannot cover a ' + $case + ' assertion failure')
            exit 1
        }
        if ($g.infra -or -not $g.ran) {
            'PASS: named E2E valid MODE=named blocked receipt bound to Green raw+JSON'
            exit 0
        }
    }
    Write-Error 'E2E gate missing Green pass (raw+JSON+stamp) or MODE=named blocked bound to Green raw+JSON'
    exit 1
}

if ([string]::IsNullOrWhiteSpace($Receipt) -or -not (Test-Path -LiteralPath $Receipt)) {
    Write-Error ('missing Playwright receipt ' + $Receipt)
    exit 1
}
$text = Get-Content -LiteralPath $Receipt -Raw
if ([string]::IsNullOrWhiteSpace($text)) {
    Write-Error ('empty Playwright receipt ' + $Receipt)
    exit 1
}

$out = Get-Outcome -Text $text -JsonPath $JsonReceipt -Case $case

if ($Mode -eq 'red') {
    if ($out.passed -and -not $out.failed) {
        Write-Error 'E2E Red unexpectedly green'
        exit 1
    }
    if ($out.failed) {
        'PASS: E2E Red assertion failure for ' + $case
        exit 0
    }
    if ($out.skipped) {
        Write-Error ('E2E Red skipped ' + $case + ' (G36) — not an assertion failure and not infra')
        exit 1
    }
    if ($out.infra -and -not $out.failed) {
        Write-Blocked -path $BlockedReceipt -marker $redMarker -text $text
        'PASS: E2E Red run blocked as ' + $sandbox + ' to E2E_RED_BLOCKED_RECEIPT; census is the written-test oracle'
        exit 0
    }
    Write-Error 'E2E Red unclassified (not assertion-fail, not infra, not pass)'
    exit 1
}

if ($Mode -eq 'named') {
    if ($out.passed -and -not $out.failed) {
        Set-Content -LiteralPath $PassReceipt ('PASS: named E2E ' + $case)
        foreach ($p in @($namedBlocked, $BlockedReceipt) | Select-Object -Unique) {
            if (-not [string]::IsNullOrWhiteSpace($p) -and (Test-Path -LiteralPath $p)) {
                Remove-Item -LiteralPath $p -Force
            }
        }
        'PASS: named E2E ' + $case
        exit 0
    }
    if ($out.failed) {
        Write-Error ('named E2E assertion failure for ' + $case + ' (failure dominates infra tokens)')
        exit 1
    }
    if ($out.skipped) {
        Write-Error ('named E2E skipped for ' + $case + ' (G36)')
        exit 1
    }
    if ($out.infra -and -not $out.failed) {
        Write-Blocked -path $BlockedReceipt -marker $namedMarker -text $text
        'PASS: named E2E blocked as ' + $sandbox + ' to E2E_NAMED_BLOCKED_RECEIPT'
        exit 0
    }
    Write-Error ('named E2E unclassified for ' + $case)
    exit 1
}

Write-Error ('unknown mode ' + $Mode)
exit 1
