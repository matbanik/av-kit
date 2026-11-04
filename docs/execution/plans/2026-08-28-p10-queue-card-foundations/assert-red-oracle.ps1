# Sole executable owner of RED_ORACLE. Counts/prefixes come from named-sets.json.
# -SelfTest proves the oracle itself before any Red row trusts it (R1-F1).
param(
    [Parameter(Mandatory = $false)]
    [ValidateSet('py', 'ui')]
    [string]$Kind,
    [Parameter(Mandatory = $false)]
    [string]$Receipt,
    [string]$JsonReceipt,
    [Parameter(Mandatory = $false)]
    [ValidateSet('41', '42', '43', '44')]
    [string]$Meu,
    [switch]$SelfTest
)
$ErrorActionPreference = 'Stop'
$setsPath = Join-Path $PSScriptRoot 'named-sets.json'
if (-not (Test-Path -LiteralPath $setsPath)) {
    Write-Error ("missing NAMED_SETS_FILE " + $setsPath)
    exit 1
}
$sets = Get-Content -LiteralPath $setsPath -Raw | ConvertFrom-Json

# An AC id is written 'AC-42.2' in the plan. Vitest titles carry that form verbatim.
# pytest node ids cannot contain '.' or '-', so a py Red test is named test_ac_42_2_*;
# both spellings are accepted for -Kind py, and nothing else is.
function Get-IdPattern {
    param([string]$Id, [string]$TestKind)
    $dotted = [regex]::Escape($Id) + '(?![0-9])'
    if ($TestKind -ne 'py') { return $dotted }
    $snake = $Id.ToLowerInvariant().Replace('-', '_').Replace('.', '_')
    return '(?i)(' + $dotted + '|' + [regex]::Escape($snake) + '(?![0-9]))'
}

# Returns $null on success, or a non-empty failure reason string. Never exits.
function Invoke-RedOracle {
    param(
        [string]$TestKind,
        [string]$ReceiptPath,
        [string]$JsonPath,
        [string]$Prefix,
        [int]$ExpectedCount
    )
    if ([string]::IsNullOrWhiteSpace($Prefix) -or $ExpectedCount -lt 1) {
        return 'named-sets missing RED_* values'
    }
    if ($Prefix -match '\.$') {
        return ('RED_PREFIX must not end in a dot: ' + $Prefix)
    }
    if (-not (Test-Path -LiteralPath $ReceiptPath)) {
        return ('missing RED receipt ' + $ReceiptPath)
    }
    $text = Get-Content -LiteralPath $ReceiptPath -Raw
    if ([string]::IsNullOrWhiteSpace($text)) {
        return ('empty RED receipt ' + $ReceiptPath)
    }

    $deny = @(
        'ERROR collecting',
        'INTERNALERROR',
        'no tests ran',
        'No test files found',
        'failed to resolve config',
        'ERR_LOAD_CONFIG',
        'Cannot find package',
        'command not found',
        'is not recognized'
    )
    $pyModule = "ModuleNotFoundError: No module named 'avkit_api'"
    foreach ($d in $deny) {
        if ($text -match [regex]::Escape($d)) {
            if ($TestKind -eq 'py' -and $d -eq 'ERROR collecting' -and $text.Contains($pyModule)) {
                continue
            }
            return ('RED_ORACLE deny: ' + $d)
        }
    }

    if ($TestKind -eq 'py') {
        $allow = @('FAILED', 'AssertionError', $pyModule)
    } else {
        $allow = @('FAIL', 'AssertionError', 'Cannot find module')
    }
    $hit = $false
    foreach ($a in $allow) {
        if ($text.Contains($a)) { $hit = $true; break }
    }
    if (-not $hit) {
        return ('RED_ORACLE missing allow-marker for ' + $TestKind)
    }

    $ids = @(1..$ExpectedCount | ForEach-Object { $Prefix + '.' + $_ })

    # ---- name extraction (R1-F1: this block is what makes every check below reachable) ----
    $names = New-Object System.Collections.Generic.List[string]
    if ($TestKind -eq 'ui' -and -not [string]::IsNullOrWhiteSpace($JsonPath)) {
        if (-not (Test-Path -LiteralPath $JsonPath)) {
            return ('missing RED_JSON ' + $JsonPath)
        }
        $raw = Get-Content -LiteralPath $JsonPath -Raw
        if ([string]::IsNullOrWhiteSpace($raw)) {
            return ('empty RED_JSON ' + $JsonPath)
        }
        $json = $raw | ConvertFrom-Json
        foreach ($suite in @($json.testResults)) {
            foreach ($a in @($suite.assertionResults)) {
                $name = [string]$a.fullName
                if ([string]::IsNullOrWhiteSpace($name)) { $name = [string]$a.title }
                if ([string]::IsNullOrWhiteSpace($name)) { continue }
                if ($a.status -and $a.status.ToString().ToLowerInvariant() -notin @('failed', 'fail')) {
                    continue
                }
                $names.Add($name)
            }
        }
    } else {
        # Text fallback. This is the contract path when the vitest JSON reporter is not used
        # and the only path for -Kind py, where pytest --json-report may be absent.
        # A missing plugin is NOT a [B]; these line shapes are the receipt contract:
        #   pytest : FAILED tests/unit/test_x.py::test_ac_42_2_widened - AssertionError: ...
        #   vitest : FAIL  ui/tests/unit/x.test.tsx > AC-43.3 contrast ...
        foreach ($line in ($text -split "`r?`n")) {
            $trimmed = $line.Trim()
            if ($trimmed -match '^FAILED\s' -or $trimmed -match '^FAIL\s' -or $trimmed -match 'AssertionError') {
                $names.Add($trimmed)
            }
        }
    }
    if ($names.Count -lt 1) {
        return 'RED_ORACLE extracted zero failed test names from the receipt'
    }

    foreach ($id in $ids) {
        $pattern = Get-IdPattern -Id $id -TestKind $TestKind
        $hits = @($names | Where-Object { $_ -match $pattern })
        if ($hits.Count -lt 1) {
            return ('RED_ORACLE missing failed title for ' + $id)
        }
    }

    $allMapped = @()
    foreach ($name in $names) {
        $mapped = @($ids | Where-Object { $name -match (Get-IdPattern -Id $_ -TestKind $TestKind) })
        if ($mapped.Count -gt 1) {
            return ('RED_ORACLE multi-id title: ' + $name)
        }
        if ($mapped.Count -eq 1) { $allMapped += $mapped[0] }
    }
    $unique = @($allMapped | Sort-Object -Unique)
    if ($unique.Count -ne $ExpectedCount) {
        return ('RED_ORACLE expected ' + $ExpectedCount + ' distinct ' + $Prefix + '.* failed titles, got ' + $unique.Count)
    }

    return $null
}

# ---------------------------------------------------------------------------
if ($SelfTest) {
    $dir = Join-Path ([string]$sets.RECEIPT_DIR) 'red-oracle-selftest'
    New-Item -ItemType Directory -Force -Path $dir | Out-Null

    function New-Fixture {
        param([string]$Name, [string]$Body)
        $p = Join-Path $dir $Name
        Set-Content -LiteralPath $p -Value $Body -Encoding UTF8
        return $p
    }
    function New-UiJson {
        param([string[]]$Titles)
        $results = @($Titles | ForEach-Object { @{ fullName = $_; status = 'failed' } })
        $results += @{ fullName = 'unrelated green test'; status = 'passed' }
        return (@{ testResults = @(@{ assertionResults = $results }) } | ConvertTo-Json -Depth 8)
    }

    $uiTextBody = "FAIL  ui/tests/unit/x.test.tsx > AC-90.1 renders" + [Environment]::NewLine +
                  "FAIL  ui/tests/unit/x.test.tsx > AC-90.2 clamps" + [Environment]::NewLine +
                  "AssertionError: expected"
    $pyHappyBody = "FAILED tests/unit/test_domain.py::test_ac_91_1_requeue_widened - AssertionError: x" + [Environment]::NewLine +
                   "FAILED tests/unit/test_domain.py::test_ac_91_2_conflict_raised - AssertionError: y"
    $pyMultiBody = "FAILED tests/unit/test_domain.py::test_ac_91_1_and_ac_91_2_together - AssertionError: x" + [Environment]::NewLine +
                   "FAILED tests/unit/test_domain.py::test_ac_91_2_conflict_raised - AssertionError: y"
    $pyCollectBody = "ERROR collecting tests/unit/test_domain.py" + [Environment]::NewLine + $pyHappyBody
    $uiReceiptBody = "FAIL  ui/tests/unit/x.test.tsx" + [Environment]::NewLine + "AssertionError: expected"

    $cases = New-Object System.Collections.Generic.List[object]

    # 1. UI JSON, every dotted id failed -> pass.
    $cases.Add(@{
        name = 'ui-json-happy'; expect = 'pass'; kind = 'ui'; prefix = 'AC-90'; count = 3
        receipt = (New-Fixture 'ui-json-happy.txt' $uiReceiptBody)
        json = (New-Fixture 'ui-json-happy.json' (New-UiJson @('AC-90.1 renders', 'AC-90.2 clamps', 'AC-90.3 announces')))
    })
    # 2. UI JSON missing AC-90.3 -> fail.
    $cases.Add(@{
        name = 'ui-json-missing-id'; expect = 'fail'; kind = 'ui'; prefix = 'AC-90'; count = 3
        receipt = (New-Fixture 'ui-json-missing.txt' $uiReceiptBody)
        json = (New-Fixture 'ui-json-missing.json' (New-UiJson @('AC-90.1 renders', 'AC-90.2 clamps')))
    })
    # 3. UI JSON with one title stuffing two ids -> fail.
    $cases.Add(@{
        name = 'ui-json-multi-id'; expect = 'fail'; kind = 'ui'; prefix = 'AC-90'; count = 3
        receipt = (New-Fixture 'ui-json-multi.txt' $uiReceiptBody)
        json = (New-Fixture 'ui-json-multi.json' (New-UiJson @('AC-90.1 and AC-90.2 together', 'AC-90.3 announces')))
    })
    # 4. UI JSON with a green (passed) AC title -> fail; Red must actually be red.
    $cases.Add(@{
        name = 'ui-json-green-ac'; expect = 'fail'; kind = 'ui'; prefix = 'AC-90'; count = 2
        receipt = (New-Fixture 'ui-json-green.txt' $uiReceiptBody)
        json = (New-Fixture 'ui-json-green.json' (@{ testResults = @(@{ assertionResults = @(
            @{ fullName = 'AC-90.1 renders'; status = 'failed' },
            @{ fullName = 'AC-90.2 clamps'; status = 'passed' }
        ) }) } | ConvertTo-Json -Depth 8))
    })
    # 5. UI text-only path (no JsonReceipt supplied) -> pass.
    $cases.Add(@{
        name = 'ui-text-fallback'; expect = 'pass'; kind = 'ui'; prefix = 'AC-90'; count = 2
        receipt = (New-Fixture 'ui-text.txt' $uiTextBody)
        json = ''
    })
    # 6. pytest snake-case node ids with no --json-report -> pass. Documented no-plugin path.
    $cases.Add(@{
        name = 'py-text-snake'; expect = 'pass'; kind = 'py'; prefix = 'AC-91'; count = 2
        receipt = (New-Fixture 'py-text.txt' $pyHappyBody)
        json = ''
    })
    # 7. pytest, one node id stuffing two AC ids -> fail.
    $cases.Add(@{
        name = 'py-text-multi-id'; expect = 'fail'; kind = 'py'; prefix = 'AC-91'; count = 2
        receipt = (New-Fixture 'py-multi.txt' $pyMultiBody)
        json = ''
    })
    # 8. Only unrelated failures -> fail.
    $cases.Add(@{
        name = 'py-unrelated-only'; expect = 'fail'; kind = 'py'; prefix = 'AC-91'; count = 2
        receipt = (New-Fixture 'py-unrelated.txt' 'FAILED tests/unit/test_other.py::test_something - AssertionError: z')
        json = ''
    })
    # 9. Collection error -> fail even though both ids are present.
    $cases.Add(@{
        name = 'py-collect-error'; expect = 'fail'; kind = 'py'; prefix = 'AC-91'; count = 2
        receipt = (New-Fixture 'py-collect.txt' $pyCollectBody)
        json = ''
    })
    # 10. Prefix carrying a trailing dot -> fail (guards the 'AC-41..1' class of bug).
    $cases.Add(@{
        name = 'prefix-trailing-dot'; expect = 'fail'; kind = 'py'; prefix = 'AC-91.'; count = 2
        receipt = (New-Fixture 'py-dot.txt' $pyHappyBody)
        json = ''
    })
    # 11. -Kind ui with a JsonReceipt path that does not exist -> fail, never silently text-fallback.
    $cases.Add(@{
        name = 'ui-json-missing-file'; expect = 'fail'; kind = 'ui'; prefix = 'AC-90'; count = 2
        receipt = (New-Fixture 'ui-json-nofile.txt' $uiTextBody)
        json = (Join-Path $dir 'does-not-exist.json')
    })

    $bad = 0
    foreach ($c in $cases) {
        $err = Invoke-RedOracle -TestKind $c.kind -ReceiptPath $c.receipt -JsonPath $c.json -Prefix $c.prefix -ExpectedCount $c.count
        $got = if ($null -eq $err) { 'pass' } else { 'fail' }
        if ($got -ne $c.expect) {
            $bad++
            Write-Error ('SELFTEST ' + $c.name + ' expected ' + $c.expect + ' got ' + $got + ' :: ' + $err)
        } else {
            ('  ok ' + $c.name + ' -> ' + $got)
        }
    }
    if ($bad -gt 0) {
        Write-Error ('RED_ORACLE selftest failures: ' + $bad)
        exit 1
    }
    'PASS: RED_ORACLE selftest ' + $cases.Count + ' cases'
    exit 0
}

if ([string]::IsNullOrWhiteSpace($Kind) -or [string]::IsNullOrWhiteSpace($Receipt) -or [string]::IsNullOrWhiteSpace($Meu)) {
    Write-Error 'RED_ORACLE requires -Kind, -Receipt and -Meu unless -SelfTest is used'
    exit 1
}
$Prefix = [string]$sets.("RED_PREFIX_" + $Meu)
$ExpectedCount = [int]$sets.("RED_COUNT_" + $Meu)
$ExpectedKind = [string]$sets.("RED_KIND_" + $Meu)
if ($ExpectedKind -ne $Kind) {
    Write-Error ('RED_ORACLE -Kind ' + $Kind + ' contradicts RED_KIND_' + $Meu + '=' + $ExpectedKind)
    exit 1
}
$err = Invoke-RedOracle -TestKind $Kind -ReceiptPath $Receipt -JsonPath $JsonReceipt -Prefix $Prefix -ExpectedCount $ExpectedCount
if ($null -ne $err) {
    Write-Error $err
    exit 1
}
'PASS: RED_ORACLE ' + $Kind + ' MEU-' + $Meu + ' ' + $Prefix + ' count=' + $ExpectedCount
exit 0
