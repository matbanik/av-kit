<#
.SYNOPSIS
  RED_PHASE_ORACLE - fail-closed proof that the MEU-49 Red phase is genuinely red.

.DESCRIPTION
  The Red-phase task row previously ended `exit 0` unconditionally, so a fully
  green suite, a suite that silently skipped the new files, or a failure with an
  entirely unrelated cause all satisfied the TDD checkpoint identically. This
  script is the oracle that replaces that receipt.

  It reads the Vitest JSON report and the vitest process exit code and requires
  ALL of:

    (a)  the captured vitest exit code is NON-ZERO;
    (b)  numTotalTests > VITEST_BASELINE_COUNT - the new cases in the EXISTING
         test files were collected, not skipped or left unwritten;
    (b2) every RED_PHASE_UNCOLLECTED_FILES entry appears in the report with
         status=failed, ZERO assertionResults, and a top-level `message` that
         both matches VITEST_UNRESOLVED_MODULE_PATTERN and names that file's
         expected-absent module specifier;
    (b3) no OTHER file failed collection: every report entry carrying a
         non-empty `message` must be a RED_PHASE_UNCOLLECTED_FILES entry, and
         every RED_PHASE_TEST_FILES entry that is NOT one must have collected
         normally (empty `message`);
    (c)  numFailedTests > 0;
    (d)  EVERY failing test's fullName contains an `AC-49.` token - a
         pre-existing unrelated failure or a dependency-guard failure cannot
         stand in for the Red phase;
    (e)  the AC ids appearing among the failures cover every id passed in
         -RequiredAcIds (RED_PHASE_REQUIRED_ACS - the unit ACs row 3 owns that
         must be RED).

  Clause (d) is why every new test name must embed its own AC id: the oracle
  reads test names, so the naming convention is load-bearing.

  Clauses (b2)/(b3) exist because a MISSING MODULE and a MISSING NAMED EXPORT
  produce different Vitest report shapes (VITEST_COLLECTION_FAILURE_SHAPE,
  measured on this tree - the captured artifact ships beside this script as
  vitest-shape-probe.json). The two checks inside (b2) are deliberately
  independent: the PATTERN establishes the KIND of failure and the specifier
  establishes its IDENTITY, and a message may legitimately arrive in either of
  two wordings (Vite import-analysis or the Node ESM loader - both were seen in
  one run, see VITEST_UNRESOLVED_MODULE_PATTERN), so neither wording may be
  hard-coded and neither check may shadow the other.
  A missing module kills collection for the WHOLE
  file: its tests vanish from numTotalTests entirely and none of its assertions
  reach clause (d). Without (b2)/(b3) a collection failure is an untracked hole
  in the evidence; with them it is a positively asserted Red-phase fact, and a
  typo'd import anywhere else is caught instead of silently deleting tests from
  the count clause (b) reads.

  RED_PHASE_PRESERVATION_ACS are deliberately NOT in the clause-(e) set: they
  assert that behaviour which already works is not broken, so they are green
  from the first run and can never appear among the failures. They are enforced
  by -Census's source scan and by the Green-phase gate instead.

  The baseline, the AC-id pattern, the file lists and the expected-absent
  specifiers are all read from named-sets.json (VITEST_BASELINE_COUNT,
  HANDOFF_AC_PATTERNS, RED_PHASE_TEST_FILES, RED_PHASE_UNCOLLECTED_FILES,
  RED_PHASE_REQUIRED_ACS, RED_PHASE_PRESERVATION_ACS,
  VITEST_UNRESOLVED_MODULE_PATTERN) and are not spelled again here.

  ABSENT_VALIDATOR_RULE: no repo-level Red-phase validator exists in this tree;
  this plan-local script is the check.

.PARAMETER ReportPath
  Vitest `--reporter=json --outputFile=` artifact for the Red run.

.PARAMETER VitestExitCode
  $LASTEXITCODE captured immediately after the vitest process, before any other
  command. A zero exit code is itself a Red-phase failure.

.PARAMETER RequiredAcIds
  AC ids that MUST appear among the failing test names. Omit to use
  RED_PHASE_REQUIRED_ACS from named-sets.json, which is where the list is stated
  exactly once; pass an explicit list to override it, or an empty array to check
  clauses (a)-(d) only.

.PARAMETER Census
  Static pre-check for the Red row, run BEFORE the suite: every
  RED_PHASE_TEST_FILES file exists; every RED_PHASE_REQUIRED_ACS **and**
  RED_PHASE_PRESERVATION_ACS id appears in at least one of them; none contains
  `.skip(`, `.only(` or `.todo(` (G36_RULE); every RED_PHASE_UNCOLLECTED_FILES
  key is itself a RED_PHASE_TEST_FILES entry, imports its declared
  expected-absent specifier, and that module genuinely does not exist on disk
  yet. This proves the tests are written and armed and that the oracle's own
  premises hold; the oracle proper then proves they are red. Takes no other
  parameters.

.PARAMETER SelfTest
  Prove the oracle FAILS on each defect shape (green suite, under-collected
  suite, no failures, an off-target failure, incomplete AC coverage, a
  collection failure outside the Red set, a Red file that should have collected
  but did not, an uncollected file that actually collected) and PASSES on a
  correctly red report built in the REAL Vitest report shape. Also replays the
  captured vitest-shape-probe.json to prove that shape assumption against real
  Vitest output rather than against this script's own belief about it.
#>
[CmdletBinding()]
param(
    [string]$ReportPath,
    [Nullable[int]]$VitestExitCode,
    [string[]]$RequiredAcIds,
    [switch]$Census,
    [switch]$SelfTest
)

$ErrorActionPreference = 'Stop'

$setsPath = Join-Path $PSScriptRoot 'named-sets.json'
if (-not (Test-Path -LiteralPath $setsPath)) {
    Write-Error ('missing NAMED_SETS_FILE ' + $setsPath)
    exit 1
}
$sets = Get-Content -LiteralPath $setsPath -Raw | ConvertFrom-Json

$baseline = [int]$sets.VITEST_BASELINE_COUNT.value
$acPattern = [string]$sets.HANDOFF_AC_PATTERNS.value.'MEU-49'
if ([string]::IsNullOrWhiteSpace($acPattern)) {
    Write-Error 'HANDOFF_AC_PATTERNS has no MEU-49 entry'
    exit 1
}

$redFiles = @($sets.RED_PHASE_TEST_FILES.value)
if ($redFiles.Count -lt 1) {
    Write-Error 'RED_PHASE_TEST_FILES is missing or empty in named-sets.json'
    exit 1
}

$uncollected = @{}
foreach ($prop in $sets.RED_PHASE_UNCOLLECTED_FILES.value.PSObject.Properties) {
    $uncollected[[string]$prop.Name] = [string]$prop.Value
}
if ($uncollected.Count -lt 1) {
    Write-Error 'RED_PHASE_UNCOLLECTED_FILES is missing or empty in named-sets.json'
    exit 1
}

$preservationAcs = @($sets.RED_PHASE_PRESERVATION_ACS.value)

# The KIND half of clause (b2). Read from the sets file rather than written here
# because the wording is layer-dependent, not fixed: see
# VITEST_UNRESOLVED_MODULE_PATTERN.
$unresolvedPattern = [string]$sets.VITEST_UNRESOLVED_MODULE_PATTERN.value
if ([string]::IsNullOrWhiteSpace($unresolvedPattern)) {
    Write-Error 'VITEST_UNRESOLVED_MODULE_PATTERN is missing or empty in named-sets.json'
    exit 1
}

# RED_PHASE_AC_OWNERSHIP maps each RED_PHASE_TEST_FILES entry to the AC ids task
# row 3 assigns to it. It exists because clause (e) reads ids out of FAILING TEST
# NAMES, and a file that never collects reports zero assertionResults - so an id
# owned only by a RED_PHASE_UNCOLLECTED_FILES entry can never appear there. Round 4
# required eight such ids (AC-49.3-49.7, AC-49.16, AC-49.17, AC-49.31) and was
# therefore unsatisfiable in exactly the way R3-F2 had already fixed one level up.
$acOwnership = @{}
foreach ($prop in $sets.RED_PHASE_AC_OWNERSHIP.value.PSObject.Properties) {
    $acOwnership[[string]$prop.Name] = @($prop.Value)
}
if ($acOwnership.Count -lt 1) {
    Write-Error 'RED_PHASE_AC_OWNERSHIP is missing or empty in named-sets.json'
    exit 1
}

# Derive, never hand-list: an id is clause-(e)-eligible iff at least one file that
# OWNS it is expected to collect. Moving an AC between files, or creating a module
# early, re-partitions this automatically.
function Get-ClauseEIds {
    param([string[]]$Required, [hashtable]$Ownership, [hashtable]$Uncollected)
    if ($Ownership.Count -lt 1) { return @($Required) }
    $eligible = New-Object System.Collections.Generic.HashSet[string]
    foreach ($rel in @($Ownership.Keys)) {
        if ($Uncollected.ContainsKey($rel)) { continue }
        foreach ($id in @($Ownership[$rel])) { [void]$eligible.Add([string]$id) }
    }
    return @($Required | Where-Object { $eligible.Contains($_) })
}

# -RequiredAcIds defaults to RED_PHASE_REQUIRED_ACS so the id list lives in exactly
# one place. An explicitly passed empty array disables clause (e); omitting the
# parameter does not.
if (-not $PSBoundParameters.ContainsKey('RequiredAcIds')) {
    $RequiredAcIds = @($sets.RED_PHASE_REQUIRED_ACS.value)
    if ($RequiredAcIds.Count -lt 1) {
        Write-Error 'RED_PHASE_REQUIRED_ACS is missing or empty in named-sets.json'
        exit 1
    }
}

# Vitest reports `name` as an absolute path with forward slashes; every list in
# named-sets.json is repo-relative. Match by normalized suffix, never by equality.
function Test-SuiteIsFile {
    param([string]$SuiteName, [string]$RelativePath)
    $n = ([string]$SuiteName) -replace '\\', '/'
    return $n.EndsWith('/' + $RelativePath) -or ($n -eq $RelativePath)
}

function Invoke-RedOracle {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][int]$ExitCode,
        [string[]]$Required,
        [int]$Baseline,
        [string]$Pattern,
        [string[]]$RedFiles = @(),
        [hashtable]$Uncollected = @{},
        [hashtable]$Ownership = @{},
        [string]$UnresolvedPattern = 'Cannot find module|Failed to resolve import'
    )

    $failures = New-Object System.Collections.Generic.List[string]

    if (-not (Test-Path -LiteralPath $Path)) {
        $failures.Add('(report) missing vitest JSON report ' + $Path)
        return $failures
    }

    $report = Get-Content -LiteralPath $Path -Raw | ConvertFrom-Json
    $suites = @($report.testResults)

    # (a) the suite must have failed as a process
    if ($ExitCode -eq 0) {
        $failures.Add('(a) vitest exited 0 - the Red phase requires a non-zero exit code')
    }

    # (b) the new cases in the EXISTING test files must have been collected
    $total = [int]$report.numTotalTests
    if ($total -le $Baseline) {
        $failures.Add('(b) numTotalTests ' + $total + ' is not greater than VITEST_BASELINE_COUNT ' + $Baseline + ' - the new cases in the existing test files were not collected')
    }

    # (b2) every expected-uncollected file must be present AND uncollected for the
    #      declared reason. A file that collected means its module already exists,
    #      which is not a Red phase; a different message means a real defect.
    foreach ($rel in @($Uncollected.Keys)) {
        $spec = [string]$Uncollected[$rel]
        $entries = @($suites | Where-Object { Test-SuiteIsFile -SuiteName $_.name -RelativePath $rel })
        if ($entries.Count -lt 1) {
            $failures.Add('(b2) RED_PHASE_UNCOLLECTED_FILES entry absent from the report: ' + $rel + ' - the file was never written or never run')
            continue
        }
        foreach ($entry in $entries) {
            $msg = [string]$entry.message
            $assertionCount = @($entry.assertionResults).Count
            if ([string]$entry.status -ne 'failed') {
                $failures.Add('(b2) ' + $rel + ' has status ' + $entry.status + ' - a Red-phase file importing ' + $spec + ' must fail collection')
            }
            if ($assertionCount -ne 0) {
                $failures.Add('(b2) ' + $rel + ' reported ' + $assertionCount + ' assertionResults - it COLLECTED, so ' + $spec + ' already exists and this is not a Red phase')
            }
            # Two INDEPENDENT checks, never chained: the pattern says the file
            # failed for an unresolved module (the KIND), the specifier says it
            # was the RIGHT one (the IDENTITY). Chaining them through an elseif
            # let an unrecognised wording hide a typo'd import behind it.
            if ($msg -notmatch $UnresolvedPattern) {
                $failures.Add('(b2) ' + $rel + ' carries no unresolved-module message matching /' + $UnresolvedPattern + '/ (message: "' + $msg + '")')
            }
            if ($msg -notmatch [regex]::Escape($spec)) {
                $failures.Add('(b2) ' + $rel + ' failed collection on a DIFFERENT module than the expected ' + $spec + ' (message: "' + $msg + '") - likely a typo''d import')
            }
        }
    }

    # (b3) no collection failure anywhere else. A missing module removes a whole
    #      file's tests from numTotalTests without producing a single failing
    #      assertion, so clause (d) cannot see it.
    foreach ($entry in $suites) {
        $msg = [string]$entry.message
        $name = ([string]$entry.name) -replace '\\', '/'
        $isExpected = $false
        foreach ($rel in @($Uncollected.Keys)) {
            if (Test-SuiteIsFile -SuiteName $name -RelativePath $rel) { $isExpected = $true; break }
        }
        if (-not [string]::IsNullOrWhiteSpace($msg) -and -not $isExpected) {
            $failures.Add('(b3) unexpected collection failure in ' + $name + ': ' + $msg)
        }
    }
    foreach ($rel in $RedFiles) {
        if ($Uncollected.ContainsKey($rel)) { continue }
        $entries = @($suites | Where-Object { Test-SuiteIsFile -SuiteName $_.name -RelativePath $rel })
        if ($entries.Count -lt 1) {
            $failures.Add('(b3) RED_PHASE_TEST_FILES entry absent from the report: ' + $rel)
            continue
        }
        foreach ($entry in $entries) {
            if (-not [string]::IsNullOrWhiteSpace([string]$entry.message)) {
                $failures.Add('(b3) ' + $rel + ' was expected to collect normally but failed collection: ' + $entry.message)
            }
        }
    }

    # (c) at least one test must actually fail
    $failed = [int]$report.numFailedTests
    if ($failed -lt 1) {
        $failures.Add('(c) numFailedTests is ' + $failed + ' - no test failed')
    }

    # collect the failing assertion names
    $failingNames = New-Object System.Collections.Generic.List[string]
    foreach ($suite in $suites) {
        foreach ($assertion in @($suite.assertionResults)) {
            if ($assertion.status -eq 'failed') {
                $name = [string]$assertion.fullName
                if ([string]::IsNullOrWhiteSpace($name)) { $name = [string]$assertion.title }
                $failingNames.Add($name)
            }
        }
    }

    if ($failed -ge 1 -and $failingNames.Count -lt 1) {
        $failures.Add('(c) numFailedTests is ' + $failed + ' but no failing assertionResults were reported - the report is unusable as evidence')
    }

    # (d) every failure must be an MEU-49 failure
    $offTarget = @($failingNames | Where-Object { $_ -notmatch $Pattern })
    if ($offTarget.Count -gt 0) {
        foreach ($name in ($offTarget | Select-Object -First 10)) {
            $failures.Add('(d) failing test carries no AC-49 id: ' + $name)
        }
    }

    # (e) the failures must cover the ACs this row owns AND CAN PROVE HERE. Ids
    # owned only by an expected-uncollected file are proven by (b2) instead - the
    # whole file failing for its own missing specifier is a STRONGER Red fact than
    # one failing assertion, because it proves the module under test does not exist
    # yet. Excluding them is scoping, not excusing. (Round-5 R4-F1.)
    $clauseE = @(Get-ClauseEIds -Required $Required -Ownership $Ownership -Uncollected $Uncollected)
    if ($clauseE.Count -gt 0) {
        $seen = New-Object System.Collections.Generic.HashSet[string]
        foreach ($name in $failingNames) {
            foreach ($m in ([regex]$Pattern).Matches($name)) {
                [void]$seen.Add($m.Value)
            }
        }
        $missing = @($clauseE | Where-Object { -not $seen.Contains($_) })
        if ($missing.Count -gt 0) {
            $failures.Add('(e) no failing test covers: ' + ($missing -join ', '))
        }
    } elseif ($Required.Count -gt 0 -and $Ownership.Count -gt 0) {
        # Every required id was filtered out - the oracle would be inert. That is a
        # defect in the sets, not a pass.
        $failures.Add('(e) every required AC id is owned only by an expected-uncollected file - clause (e) would be inert; check RED_PHASE_AC_OWNERSHIP')
    }

    return $failures
}

# ---------------------------------------------------------------------------
# Fixture builders. These emit the REAL Vitest --reporter=json shape measured on
# this tree (VITEST_COLLECTION_FAILURE_SHAPE): per-file testResults entries with
# `name` (absolute, forward slashes), `status`, a top-level `message` that is
# non-empty ONLY on a collection failure, and `assertionResults` carrying
# `fullName`/`title`/`status`/`failureMessages`. The previous flat single-entry
# fixture could not express a collection failure at all, so clauses (b2)/(b3)
# would have been untestable.
# ---------------------------------------------------------------------------

function New-SuiteEntry {
    param(
        [Parameter(Mandatory = $true)][string]$Rel,
        [string]$MissingModule = '',
        [ValidateSet('node', 'vite')][string]$MessageStyle = 'node',
        [AllowEmptyCollection()][string[]]$Failing = @(),
        [int]$Passing = 0,
        [string]$RawMessage = ''
    )
    $abs = 'P:/av-kit/' + $Rel
    $assertions = @()
    for ($i = 0; $i -lt $Passing; $i++) {
        $assertions += [pscustomobject]@{
            ancestorTitles  = @('fixture')
            fullName        = 'fixture > preserved case ' + $i
            title           = 'preserved case ' + $i
            status          = 'passed'
            failureMessages = @()
        }
    }
    foreach ($n in $Failing) {
        $assertions += [pscustomobject]@{
            ancestorTitles  = @('fixture')
            fullName        = $n
            title           = $n
            status          = 'failed'
            failureMessages = @('AssertionError: expected undefined to be defined')
        }
    }
    $message = ''
    if (-not [string]::IsNullOrWhiteSpace($RawMessage)) {
        # Escape hatch for the negative cases: an arbitrary collection failure
        # that is neither wording.
        $message = $RawMessage
        $assertions = @()
    }
    elseif (-not [string]::IsNullOrWhiteSpace($MissingModule)) {
        # Both real wordings are reproducible here because both were observed in
        # one real run (VITEST_UNRESOLVED_MODULE_PATTERN); a fixture that could
        # only emit one of them is what let correction X2's defect ship.
        if ($MessageStyle -eq 'vite') {
            $message = 'Failed to resolve import "' + $MissingModule + '" from "' + $Rel + '". Does the file exist?'
        }
        else {
            $message = "Cannot find module '" + $MissingModule + "' imported from '" + $abs + "'"
        }
        $assertions = @()
    }
    $status = 'passed'
    if ($message -ne '' -or @($assertions | Where-Object { $_.status -eq 'failed' }).Count -gt 0) {
        $status = 'failed'
    }
    return [pscustomobject]@{
        name             = $abs
        status           = $status
        message          = $message
        startTime        = 0
        endTime          = 0
        assertionResults = $assertions
    }
}

function New-RedFixture {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][int]$Total,
        [Parameter(Mandatory = $true)][AllowEmptyCollection()][object[]]$Files
    )
    $failedTests = 0
    foreach ($f in $Files) {
        $failedTests += @($f.assertionResults | Where-Object { $_.status -eq 'failed' }).Count
    }
    $payload = [pscustomobject]@{
        numTotalTestSuites  = @($Files).Count
        numFailedTestSuites = @($Files | Where-Object { $_.status -eq 'failed' }).Count
        numPassedTestSuites = @($Files | Where-Object { $_.status -eq 'passed' }).Count
        numTotalTests       = $Total
        numFailedTests      = $failedTests
        numPassedTests      = [Math]::Max(0, $Total - $failedTests)
        numPendingTests     = 0
        numTodoTests        = 0
        success             = $false
        testResults         = @($Files)
    }
    $payload | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $Path -Encoding utf8
}

# The canonical well-formed Red report: every RED_PHASE_UNCOLLECTED_FILES entry
# fails collection on its declared specifier, every other RED_PHASE_TEST_FILES
# entry collects and carries the failing AC cases, and one unrelated file is
# green. Callers mutate one aspect of it per negative case.
function New-CanonicalRedFiles {
    param(
        [string[]]$RedFiles,
        [hashtable]$Uncollected,
        [string[]]$Required,
        [hashtable]$Ownership = @{},
        [ValidateSet('node', 'vite')][string]$MessageStyle = 'node'
    )
    $files = @()
    $collected = @($RedFiles | Where-Object { -not $Uncollected.ContainsKey($_) })
    if ($collected.Count -lt 1) { $collected = @('ui/tests/unit/queue-card.test.ts') }

    # Replay the DECLARED topology, not a friendlier one. The previous version
    # spread the required ids round-robin across whichever files collect, which
    # silently relocated the eight ids that really live in uncollected files and
    # made case 10 prove satisfiability for a plan nobody wrote (round-5 R4-F1).
    # With $Ownership supplied, each id is emitted in the file that actually owns
    # it - so an id owned only by an uncollected file appears in NO failing name,
    # exactly as it will on the real Red run.
    $buckets = @{}
    foreach ($rel in $collected) { $buckets[$rel] = New-Object System.Collections.Generic.List[string] }
    if ($Ownership.Count -gt 0) {
        foreach ($rel in $collected) {
            foreach ($id in @($Ownership[$rel])) {
                if ($Required -contains $id) {
                    $buckets[$rel].Add($rel + ' > ' + $id + ' fixture case')
                }
            }
        }
    } else {
        $i = 0
        foreach ($id in $Required) {
            $rel = $collected[$i % $collected.Count]
            $buckets[$rel].Add($rel + ' > ' + $id + ' fixture case')
            $i++
        }
    }
    foreach ($rel in $collected) {
        $files += New-SuiteEntry -Rel $rel -Failing $buckets[$rel].ToArray() -Passing 3
    }
    foreach ($rel in @($Uncollected.Keys)) {
        $files += New-SuiteEntry -Rel $rel -MissingModule ([string]$Uncollected[$rel]) -MessageStyle $MessageStyle
    }
    $files += New-SuiteEntry -Rel 'ui/tests/unit/queue-canon.test.ts' -Passing 8
    return $files
}

if ($Census) {
    $root = (Resolve-Path (Join-Path $PSScriptRoot '../../../..')).Path
    $problems = New-Object System.Collections.Generic.List[string]
    $present = New-Object System.Collections.Generic.List[string]

    foreach ($rel in $redFiles) {
        $full = Join-Path $root $rel
        if (-not (Test-Path -LiteralPath $full)) {
            $problems.Add('missing test file: ' + $rel)
            continue
        }
        $present.Add($full)
        $neutralized = @(Select-String -LiteralPath $full -Pattern '\.(skip|only|todo)\(')
        foreach ($hit in $neutralized) {
            $problems.Add('G36_RULE violation - neutralized test at ' + $rel + ':' + $hit.LineNumber + ' -> ' + $hit.Line.Trim())
        }
    }

    # Every AC row 3 owns must be WRITTEN, including the preservation ACs that are
    # green by construction and therefore invisible to clause (e).
    $censusIds = @($RequiredAcIds) + @($preservationAcs)
    if ($present.Count -gt 0) {
        foreach ($id in $censusIds) {
            if (-not (Select-String -LiteralPath $present.ToArray() -Pattern ([regex]::Escape($id)) -Quiet)) {
                $problems.Add('no test name carries ' + $id)
            }
        }
    }

    # (Round-5 R4-F2.) The ownership map must account for EXACTLY the ids the plan
    # declares - no more, no fewer. This is the check that makes an unregistered AC
    # structurally impossible rather than merely fixed once: AC-49.37 and AC-49.38
    # were introduced in round 4 as full ACs, never added to RED_PHASE_REQUIRED_ACS,
    # and nothing in the toolchain was capable of noticing.
    $ownedIds = New-Object System.Collections.Generic.HashSet[string]
    foreach ($rel in @($acOwnership.Keys)) {
        if ($redFiles -notcontains $rel) {
            $problems.Add('RED_PHASE_AC_OWNERSHIP names a file that is not a RED_PHASE_TEST_FILES entry: ' + $rel)
        }
        foreach ($id in @($acOwnership[$rel])) { [void]$ownedIds.Add([string]$id) }
    }
    foreach ($rel in $redFiles) {
        if (-not $acOwnership.ContainsKey($rel)) {
            $problems.Add('RED_PHASE_TEST_FILES entry has no RED_PHASE_AC_OWNERSHIP row: ' + $rel)
        }
    }
    foreach ($id in $censusIds) {
        if (-not $ownedIds.Contains($id)) {
            $problems.Add('AC id is required or preservation but no file owns it in RED_PHASE_AC_OWNERSHIP: ' + $id)
        }
    }
    foreach ($id in @($ownedIds)) {
        if ($censusIds -notcontains $id) {
            $problems.Add('RED_PHASE_AC_OWNERSHIP owns an id that is neither required nor preservation: ' + $id)
        }
    }

    # Placement, not merely presence: an id must appear in the file that OWNS it.
    # Without this, clause (e)'s scoping could be defeated by writing an
    # uncollected file's AC into a collecting file, which would pass the census and
    # then fail the oracle for a reason no one could read.
    foreach ($rel in @($acOwnership.Keys)) {
        $full = Join-Path $root $rel
        if (-not (Test-Path -LiteralPath $full)) { continue }
        foreach ($id in @($acOwnership[$rel])) {
            if (-not (Select-String -LiteralPath $full -Pattern ([regex]::Escape([string]$id)) -Quiet)) {
                $problems.Add($rel + ' owns ' + $id + ' in RED_PHASE_AC_OWNERSHIP but no test name in that file carries it')
            }
        }
    }

    # And the derived clause-(e) set must be non-empty, or the oracle is inert.
    $clauseEIds = @(Get-ClauseEIds -Required $RequiredAcIds -Ownership $acOwnership -Uncollected $uncollected)
    if ($clauseEIds.Count -lt 1) {
        $problems.Add('the derived clause (e) id set is empty - every required AC is owned only by an expected-uncollected file, so the oracle would be inert')
    }

    # The oracle's own premises: each expected-uncollected file is a declared Red
    # file, actually imports the specifier whose absence clause (b2) asserts, and
    # that module really is absent right now.
    foreach ($rel in @($uncollected.Keys)) {
        $spec = [string]$uncollected[$rel]
        if ($redFiles -notcontains $rel) {
            $problems.Add('RED_PHASE_UNCOLLECTED_FILES entry is not a RED_PHASE_TEST_FILES entry: ' + $rel)
            continue
        }
        $full = Join-Path $root $rel
        if (-not (Test-Path -LiteralPath $full)) { continue }
        $leaf = ($spec -split '/')[-1]
        if (-not (Select-String -LiteralPath $full -Pattern ([regex]::Escape($leaf)) -Quiet)) {
            $problems.Add($rel + ' does not import ' + $spec + ' - clause (b2) would assert a collection failure that cannot happen')
        }
        $moduleExists = $false
        foreach ($ext in @('.ts', '.tsx')) {
            if (Test-Path -LiteralPath (Join-Path $root ('ui/' + $spec + $ext))) { $moduleExists = $true; break }
        }
        if ($moduleExists) {
            $problems.Add('module ' + $spec + ' already exists - ' + $rel + ' will COLLECT and clause (b2) cannot pass; this is not a Red phase')
        }
    }

    if ($problems.Count -gt 0) {
        foreach ($p in $problems) { Write-Error $p -ErrorAction Continue }
        Write-Output ('FAIL: RED_PHASE_ORACLE census (' + $problems.Count + ' problems)')
        exit 1
    }

    Write-Output ('PASS: RED_PHASE_ORACLE census (' + $redFiles.Count + ' files, ' + $censusIds.Count + ' AC ids present and correctly placed [' + $RequiredAcIds.Count + ' required-red + ' + $preservationAcs.Count + ' preservation], ownership union exact, ' + $clauseEIds.Count + ' ids proven by clause (e) and ' + ($RequiredAcIds.Count - $clauseEIds.Count) + ' by clause (b2), ' + $uncollected.Count + ' expected-uncollected files verified, no neutralized tests)')
    exit 0
}

if ($SelfTest) {
    $fixtureRoot = Join-Path ([System.IO.Path]::GetTempPath()) ('red-oracle-selftest-' + [guid]::NewGuid().ToString('N'))
    New-Item -ItemType Directory -Path $fixtureRoot -Force | Out-Null
    $selfTestFailures = New-Object System.Collections.Generic.List[string]
    $required = @('AC-49.3', 'AC-49.31')
    $caseCount = 0

    # A two-file toy Uncollected map keeps the negative cases readable; the real
    # RED_PHASE_UNCOLLECTED_FILES map is exercised by cases 10-13.
    $toyUncollected = @{ 'ui/tests/unit/reorder-body.test.ts' = 'src/renderer/src/lib/queue/reorder-body' }
    $toyRed = @('ui/tests/unit/reorder-body.test.ts', 'ui/tests/unit/queue-card.test.ts')

    function Invoke-Toy {
        param([string]$Path, [int]$ExitCode, [string[]]$Req)
        return Invoke-RedOracle -Path $Path -ExitCode $ExitCode -Required $Req -Baseline $baseline `
            -Pattern $acPattern -RedFiles $toyRed -Uncollected $toyUncollected `
            -UnresolvedPattern $unresolvedPattern
    }

    try {
        # Case 1: correctly red -> must PASS
        $caseCount++
        $good = Join-Path $fixtureRoot 'good.json'
        New-RedFixture -Path $good -Total ($baseline + 12) -Files @(
            (New-SuiteEntry -Rel 'ui/tests/unit/queue-card.test.ts' -Passing 4 -Failing @(
                    'queue-card > AC-49.3 re-export keeps reference identity',
                    'queue-card > AC-49.31 second acquire returns null'
                )),
            (New-SuiteEntry -Rel 'ui/tests/unit/reorder-body.test.ts' -MissingModule 'src/renderer/src/lib/queue/reorder-body')
        )
        $r = Invoke-Toy -Path $good -ExitCode 1 -Req $required
        if ($r.Count -ne 0) { $selfTestFailures.Add('case1 (correctly red) should PASS but reported: ' + ($r -join '; ')) }

        # Case 2: green suite (exit 0, no failures) -> must FAIL on (a) and (c)
        $caseCount++
        $green = Join-Path $fixtureRoot 'green.json'
        New-RedFixture -Path $green -Total ($baseline + 12) -Files @(
            (New-SuiteEntry -Rel 'ui/tests/unit/queue-card.test.ts' -Passing 6),
            (New-SuiteEntry -Rel 'ui/tests/unit/reorder-body.test.ts' -MissingModule 'src/renderer/src/lib/queue/reorder-body')
        )
        $r = Invoke-Toy -Path $green -ExitCode 0 -Req $required
        if (-not (@($r) -match '^\(a\)')) { $selfTestFailures.Add('case2 (green suite) did not fail clause (a)') }
        if (-not (@($r) -match '^\(c\)')) { $selfTestFailures.Add('case2 (green suite) did not fail clause (c)') }

        # Case 3: tests not collected -> must FAIL on (b)
        $caseCount++
        $short = Join-Path $fixtureRoot 'short.json'
        New-RedFixture -Path $short -Total $baseline -Files @(
            (New-SuiteEntry -Rel 'ui/tests/unit/queue-card.test.ts' -Failing @('queue-card > AC-49.8 handle is the first child')),
            (New-SuiteEntry -Rel 'ui/tests/unit/reorder-body.test.ts' -MissingModule 'src/renderer/src/lib/queue/reorder-body')
        )
        $r = Invoke-Toy -Path $short -ExitCode 1 -Req @()
        if (-not (@($r) -match '^\(b\)')) { $selfTestFailures.Add('case3 (under-collected) did not fail clause (b)') }

        # Case 4: an unrelated failure -> must FAIL on (d)
        $caseCount++
        $offTarget = Join-Path $fixtureRoot 'offtarget.json'
        New-RedFixture -Path $offTarget -Total ($baseline + 12) -Files @(
            (New-SuiteEntry -Rel 'ui/tests/unit/queue-card.test.ts' -Failing @('dependency guard > forbids react-virtual')),
            (New-SuiteEntry -Rel 'ui/tests/unit/reorder-body.test.ts' -MissingModule 'src/renderer/src/lib/queue/reorder-body')
        )
        $r = Invoke-Toy -Path $offTarget -ExitCode 1 -Req @()
        if (-not (@($r) -match '^\(d\)')) { $selfTestFailures.Add('case4 (off-target failure) did not fail clause (d)') }

        # Case 5: red, but missing an owned AC -> must FAIL on (e)
        $caseCount++
        $partial = Join-Path $fixtureRoot 'partial.json'
        New-RedFixture -Path $partial -Total ($baseline + 12) -Files @(
            (New-SuiteEntry -Rel 'ui/tests/unit/queue-card.test.ts' -Failing @('queue-card > AC-49.3 re-export keeps reference identity')),
            (New-SuiteEntry -Rel 'ui/tests/unit/reorder-body.test.ts' -MissingModule 'src/renderer/src/lib/queue/reorder-body')
        )
        $r = Invoke-Toy -Path $partial -ExitCode 1 -Req $required
        if (-not (@($r) -match '^\(e\)')) { $selfTestFailures.Add('case5 (incomplete AC coverage) did not fail clause (e)') }

        # Case 6: missing report -> must FAIL
        $caseCount++
        $r = Invoke-Toy -Path (Join-Path $fixtureRoot 'nope.json') -ExitCode 1 -Req @()
        if ($r.Count -eq 0) { $selfTestFailures.Add('case6 (missing report) should FAIL') }

        # Case 7: the -RequiredAcIds default resolved from RED_PHASE_REQUIRED_ACS, and every
        # id in it is well formed. A silently empty default would turn clause (e) off.
        $caseCount++
        if ($RequiredAcIds.Count -lt 1) {
            $selfTestFailures.Add('case7 (default AC list) resolved to an empty set - clause (e) would be inert')
        }
        $malformed = @($RequiredAcIds | Where-Object { $_ -notmatch ('^' + $acPattern + '$') })
        if ($malformed.Count -gt 0) {
            $selfTestFailures.Add('case7 (default AC list) contains ids that cannot match HANDOFF_AC_PATTERNS: ' + ($malformed -join ', '))
        }
        # A preservation AC in the required-red set is the R3-F2 defect: it can never
        # appear among the failures, so clause (e) becomes unsatisfiable.
        $overlap = @($RequiredAcIds | Where-Object { $preservationAcs -contains $_ })
        if ($overlap.Count -gt 0) {
            $selfTestFailures.Add('case7 (default AC list) includes RED_PHASE_PRESERVATION_ACS ids, which are green by construction and can never fail: ' + ($overlap -join ', '))
        }

        # Case 8: -Census has a non-empty, well-formed file list to work from.
        $caseCount++
        $badPaths = @($redFiles | Where-Object { $_ -notmatch '^ui/tests/unit/.+\.test\.ts$' })
        if ($badPaths.Count -gt 0) {
            $selfTestFailures.Add('case8 (census file list) entries are not unit test paths: ' + ($badPaths -join ', '))
        }
        $orphanUncollected = @(@($uncollected.Keys) | Where-Object { $redFiles -notcontains $_ })
        if ($orphanUncollected.Count -gt 0) {
            $selfTestFailures.Add('case8 (census file list) RED_PHASE_UNCOLLECTED_FILES entries missing from RED_PHASE_TEST_FILES: ' + ($orphanUncollected -join ', '))
        }

        # Case 9: replay the CAPTURED real Vitest report and prove the shape this
        # oracle depends on is what Vitest actually emits, not what this script
        # believes. Anchors VITEST_COLLECTION_FAILURE_SHAPE on an artifact.
        $caseCount++
        $probePath = Join-Path $PSScriptRoot 'vitest-shape-probe.json'
        if (-not (Test-Path -LiteralPath $probePath)) {
            $selfTestFailures.Add('case9 (real shape probe) vitest-shape-probe.json is missing - the shape claim has no artifact behind it')
        }
        else {
            $probe = Get-Content -LiteralPath $probePath -Raw | ConvertFrom-Json
            $missingModuleEntry = @($probe.testResults | Where-Object { ([string]$_.message) -match 'Cannot find module' })
            if ($missingModuleEntry.Count -lt 1) {
                $selfTestFailures.Add('case9 (real shape probe) contains no "Cannot find module" entry')
            }
            else {
                if (@($missingModuleEntry[0].assertionResults).Count -ne 0) {
                    $selfTestFailures.Add('case9 (real shape probe) a missing-module file reported assertionResults - clause (b2) assumes zero')
                }
                if ([string]$missingModuleEntry[0].status -ne 'failed') {
                    $selfTestFailures.Add('case9 (real shape probe) a missing-module file did not report status=failed')
                }
            }
            # the missing-NAMED-export control: collects, empty message, one failure
            $namedEntry = @($probe.testResults | Where-Object {
                    ([string]$_.status -eq 'failed') -and
                    ([string]::IsNullOrWhiteSpace([string]$_.message)) -and
                    (@($_.assertionResults).Count -gt 0)
                })
            if ($namedEntry.Count -lt 1) {
                $selfTestFailures.Add('case9 (real shape probe) contains no missing-named-export control entry - the shape distinction is unproven')
            }
        }

        # Case 10: the REAL RED_PHASE_UNCOLLECTED_FILES / RED_PHASE_TEST_FILES /
        # RED_PHASE_REQUIRED_ACS sets, in the real report shape -> must PASS.
        # This is the satisfiability proof: an oracle no correct Red run can pass
        # is worse than no oracle.
        $caseCount++
        $realGood = Join-Path $fixtureRoot 'real-good.json'
        $realFiles = New-CanonicalRedFiles -RedFiles $redFiles -Uncollected $uncollected `
            -Required $RequiredAcIds -Ownership $acOwnership
        New-RedFixture -Path $realGood -Total ($baseline + 18) -Files $realFiles
        $r = Invoke-RedOracle -Path $realGood -ExitCode 1 -Required $RequiredAcIds -Baseline $baseline `
            -Pattern $acPattern -RedFiles $redFiles -Uncollected $uncollected -Ownership $acOwnership
        if ($r.Count -ne 0) {
            $selfTestFailures.Add('case10 (real sets, real shape) should PASS but reported: ' + ($r -join '; '))
        }

        # Case 11: an expected-uncollected file that actually COLLECTED (its module
        # already exists) -> must FAIL on (b2). This is a green-in-disguise Red run.
        $caseCount++
        $collectedAnyway = Join-Path $fixtureRoot 'collected-anyway.json'
        $firstUncollected = @($uncollected.Keys)[0]
        $mutated = @()
        foreach ($f in $realFiles) {
            if (Test-SuiteIsFile -SuiteName $f.name -RelativePath $firstUncollected) {
                $mutated += New-SuiteEntry -Rel $firstUncollected -Failing @($firstUncollected + ' > AC-49.3 fixture case') -Passing 2
            }
            else { $mutated += $f }
        }
        New-RedFixture -Path $collectedAnyway -Total ($baseline + 18) -Files $mutated
        $r = Invoke-RedOracle -Path $collectedAnyway -ExitCode 1 -Required @() -Baseline $baseline `
            -Pattern $acPattern -RedFiles $redFiles -Uncollected $uncollected
        if (-not (@($r) -match '^\(b2\)')) { $selfTestFailures.Add('case11 (uncollected file actually collected) did not fail clause (b2)') }

        # Case 12: a collection failure OUTSIDE the Red set - the exact defect that
        # silently deletes passing tests from numTotalTests -> must FAIL on (b3).
        $caseCount++
        $strayBreak = Join-Path $fixtureRoot 'stray-break.json'
        $stray = @($realFiles) + @(New-SuiteEntry -Rel 'ui/tests/unit/queue-canon.test.ts' -MissingModule 'src/renderer/src/lib/queue/typo-path')
        New-RedFixture -Path $strayBreak -Total ($baseline + 18) -Files $stray
        $r = Invoke-RedOracle -Path $strayBreak -ExitCode 1 -Required @() -Baseline $baseline `
            -Pattern $acPattern -RedFiles $redFiles -Uncollected $uncollected
        if (-not (@($r) -match '^\(b3\)')) { $selfTestFailures.Add('case12 (stray collection failure) did not fail clause (b3)') }

        # Case 13: a Red file that was supposed to collect but failed collection
        # (a typo'd import in an EXISTING test file) -> must FAIL on (b3).
        $caseCount++
        $typoInExisting = Join-Path $fixtureRoot 'typo-existing.json'
        $collectedRed = @($redFiles | Where-Object { -not $uncollected.ContainsKey($_) })[0]
        $mutated2 = @()
        foreach ($f in $realFiles) {
            if (Test-SuiteIsFile -SuiteName $f.name -RelativePath $collectedRed) {
                $mutated2 += New-SuiteEntry -Rel $collectedRed -MissingModule 'src/renderer/src/lib/queue/reorder-bdoy'
            }
            else { $mutated2 += $f }
        }
        New-RedFixture -Path $typoInExisting -Total ($baseline + 18) -Files $mutated2
        $r = Invoke-RedOracle -Path $typoInExisting -ExitCode 1 -Required @() -Baseline $baseline `
            -Pattern $acPattern -RedFiles $redFiles -Uncollected $uncollected
        if (-not (@($r) -match '^\(b3\)')) { $selfTestFailures.Add('case13 (typo in an existing Red file) did not fail clause (b3)') }

        # Case 14: an expected-uncollected file missing from the report entirely
        # (never written, or filtered out) -> must FAIL on (b2).
        $caseCount++
        $absentFile = Join-Path $fixtureRoot 'absent-file.json'
        $withoutOne = @($realFiles | Where-Object { -not (Test-SuiteIsFile -SuiteName $_.name -RelativePath $firstUncollected) })
        New-RedFixture -Path $absentFile -Total ($baseline + 18) -Files $withoutOne
        $r = Invoke-RedOracle -Path $absentFile -ExitCode 1 -Required @() -Baseline $baseline `
            -Pattern $acPattern -RedFiles $redFiles -Uncollected $uncollected
        if (-not (@($r) -match '^\(b2\)')) { $selfTestFailures.Add('case14 (uncollected file absent from report) did not fail clause (b2)') }

        # Case 15 (round-5 R4-F1): the DIRECT refutation of the round-4 defect. Feed
        # the real topology WITHOUT the ownership map, so clause (e) reverts to
        # demanding every required id among the failures - including the eight owned
        # by files that cannot report any. It must FAIL on (e). Case 10 above feeds
        # the same fixture WITH the map and must PASS. The pair is the proof that the
        # scoping is what makes the oracle satisfiable, not the fixture.
        $caseCount++
        $r = Invoke-RedOracle -Path $realGood -ExitCode 1 -Required $RequiredAcIds -Baseline $baseline `
            -Pattern $acPattern -RedFiles $redFiles -Uncollected $uncollected
        if (-not (@($r) -match '^\(e\)')) {
            $selfTestFailures.Add('case15 (real topology, ownership scoping disabled) did not fail clause (e) - the round-4 unsatisfiability is no longer being reproduced, so case 10 proves nothing')
        }

        # Case 16 (round-5 R4-F1): a required id owned ONLY by an uncollected file
        # must be excluded from clause (e) - and an id owned by a collecting file
        # must not be. Asserted on the derivation directly, so a future edit that
        # widens or narrows Get-ClauseEIds is caught at its source.
        $caseCount++
        $derived = @(Get-ClauseEIds -Required $RequiredAcIds -Ownership $acOwnership -Uncollected $uncollected)
        foreach ($rel in @($uncollected.Keys)) {
            foreach ($id in @($acOwnership[$rel])) {
                $alsoElsewhere = $false
                foreach ($other in @($acOwnership.Keys)) {
                    if ($other -ne $rel -and -not $uncollected.ContainsKey($other) -and (@($acOwnership[$other]) -contains $id)) {
                        $alsoElsewhere = $true
                    }
                }
                if (-not $alsoElsewhere -and ($derived -contains $id)) {
                    $selfTestFailures.Add('case16: ' + $id + ' is owned only by the uncollected ' + $rel + ' but survived into clause (e)')
                }
            }
        }
        if ($derived.Count -ge $RequiredAcIds.Count) {
            $selfTestFailures.Add('case16: clause (e) scoping excluded nothing - on the real sets it must exclude the ids owned only by expected-uncollected files')
        }
        if ($derived.Count -lt 1) {
            $selfTestFailures.Add('case16: clause (e) scoping excluded everything - the oracle would be inert')
        }

        # Case 17 (round-5 R4-F2): the ownership map must account for exactly the
        # declared ids. This is the same assertion the census makes, replayed here so
        # -SelfTest alone catches an unregistered AC without needing a checked-out
        # tree of test files.
        $caseCount++
        $ownedAll = New-Object System.Collections.Generic.HashSet[string]
        foreach ($rel in @($acOwnership.Keys)) {
            foreach ($id in @($acOwnership[$rel])) { [void]$ownedAll.Add([string]$id) }
        }
        $declared = @($RequiredAcIds) + @($preservationAcs)
        foreach ($id in $declared) {
            if (-not $ownedAll.Contains($id)) {
                $selfTestFailures.Add('case17: ' + $id + ' is declared but unowned in RED_PHASE_AC_OWNERSHIP')
            }
        }
        foreach ($id in @($ownedAll)) {
            if ($declared -notcontains $id) {
                $selfTestFailures.Add('case17: RED_PHASE_AC_OWNERSHIP owns undeclared id ' + $id)
            }
        }

        # Case 18 (execution-phase correction X2): the SAME real topology as case
        # 10, but every uncollected file reports the OTHER real wording - Vite's
        # import-analysis message instead of the Node loader's. This must PASS.
        # The round-4 oracle hard-coded "Cannot find module" and therefore failed
        # the genuine, correctly-red first run of this MEU, in which one of the
        # three files used each wording (VITEST_UNRESOLVED_MODULE_PATTERN). The
        # second half of the case keeps the widened check honest: a collection
        # failure that is neither wording - and so is not evidence of an absent
        # module at all - must still be rejected by clause (b2).
        $caseCount++
        $viteWording = Join-Path $fixtureRoot 'real-good-vite.json'
        New-RedFixture -Path $viteWording -Total ($baseline + 18) -Files (
            New-CanonicalRedFiles -RedFiles $redFiles -Uncollected $uncollected `
                -Required $RequiredAcIds -Ownership $acOwnership -MessageStyle 'vite'
        )
        $r = Invoke-RedOracle -Path $viteWording -ExitCode 1 -Required $RequiredAcIds -Baseline $baseline `
            -Pattern $acPattern -RedFiles $redFiles -Uncollected $uncollected -Ownership $acOwnership `
            -UnresolvedPattern $unresolvedPattern
        if ($r.Count -ne 0) {
            $selfTestFailures.Add('case18 (Vite import-analysis wording) should PASS but reported: ' + ($r -join '; '))
        }

        $unrelatedMsg = @()
        foreach ($entry in @($realFiles)) {
            $isUncollected = $false
            foreach ($rel in @($uncollected.Keys)) {
                if (Test-SuiteIsFile -SuiteName $entry.name -RelativePath $rel) { $isUncollected = $true; break }
            }
            if ($isUncollected) {
                $relPath = (([string]$entry.name) -replace '.*?(ui/tests/.*)$', '$1')
                $unrelatedMsg += New-SuiteEntry -Rel $relPath -RawMessage 'SyntaxError: Unexpected token in tests/unit fixture'
            }
            else { $unrelatedMsg += $entry }
        }
        $notAModuleError = Join-Path $fixtureRoot 'not-a-module-error.json'
        New-RedFixture -Path $notAModuleError -Total ($baseline + 18) -Files $unrelatedMsg
        $r = Invoke-RedOracle -Path $notAModuleError -ExitCode 1 -Required @() -Baseline $baseline `
            -Pattern $acPattern -RedFiles $redFiles -Uncollected $uncollected -Ownership $acOwnership `
            -UnresolvedPattern $unresolvedPattern
        if (-not (@($r) -match '^\(b2\)')) {
            $selfTestFailures.Add('case18 (unrelated collection failure) did not fail clause (b2) - the widened pattern accepts anything')
        }
    }
    finally {
        Remove-Item -LiteralPath $fixtureRoot -Recurse -Force -ErrorAction SilentlyContinue
    }

    if ($selfTestFailures.Count -gt 0) {
        foreach ($f in $selfTestFailures) { Write-Error $f -ErrorAction Continue }
        Write-Output 'FAIL: RED_PHASE_ORACLE self-test'
        exit 1
    }
    Write-Output ('PASS: RED_PHASE_ORACLE self-test (' + $caseCount + ' cases, baseline ' + $baseline + ', ' + $RequiredAcIds.Count + ' required-red AC ids, ' + $preservationAcs.Count + ' preservation ACs, ' + $uncollected.Count + ' expected-uncollected files)')
    exit 0
}

if ([string]::IsNullOrWhiteSpace($ReportPath)) {
    Write-Error '-ReportPath is required (or use -SelfTest)'
    exit 1
}
if ($null -eq $VitestExitCode) {
    Write-Error '-VitestExitCode is required: capture $LASTEXITCODE immediately after the vitest process, before any other command'
    exit 1
}

$result = Invoke-RedOracle -Path $ReportPath -ExitCode ([int]$VitestExitCode) -Required $RequiredAcIds `
    -Baseline $baseline -Pattern $acPattern -RedFiles $redFiles -Uncollected $uncollected `
    -Ownership $acOwnership -UnresolvedPattern $unresolvedPattern
if ($result.Count -gt 0) {
    foreach ($f in $result) { Write-Error $f -ErrorAction Continue }
    Write-Output 'FAIL: RED_PHASE_ORACLE'
    exit 1
}

$clauseEFinal = @(Get-ClauseEIds -Required $RequiredAcIds -Ownership $acOwnership -Uncollected $uncollected)
Write-Output ('PASS: RED_PHASE_ORACLE (vitest exit ' + $VitestExitCode + ', baseline ' + $baseline + ', ' + $clauseEFinal.Count + ' AC ids proven by clause (e) and ' + ($RequiredAcIds.Count - $clauseEFinal.Count) + ' by clause (b2), ' + $uncollected.Count + ' expected-uncollected files verified, report ' + $ReportPath + ')')
exit 0
