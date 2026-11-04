<#
.SYNOPSIS
  EXEC_DISPATCH_CHECK - bind EXEC_REVIEW_FILE to a real reviewer dispatch.

.DESCRIPTION
  AGENTS.md prohibits self-review: the implementing agent may not author its own
  `approved` verdict. A verdict file on disk proves nothing by itself, so this
  script ties EXEC_REVIEW_FILE to the Invoke-CodexDispatch run that produced it:

    1. EXEC_REVIEW_FILE exists and its YAML frontmatter carries agent,
       review_mode, verdict, findings_count and DISPATCH_ID_FIELD.
    2. agent == REVIEWER_AGENT, review_mode == EXEC_REVIEW_MODE,
       verdict == EXEC_REVIEW_APPROVED, findings_count == 0.
    3. DISPATCH_DIR/<dispatch_id>/status.json exists, declares
       DISPATCH_STATUS_SCHEMA, exited 0, ran REVIEWER_AGENT, and its own
       dispatch_id agrees with the frontmatter.
    4. The dispatch's prompt names EXEC_REVIEW_FILE, so an unrelated dispatch id
       cannot be borrowed to bless a hand-written verdict.
    5. The dispatch's final.md states the same verdict - an older
       changes_required receipt cannot be reused to approve a rewritten file.

  Every name and expected value comes from named-sets.json; nothing is hard-coded
  here, per the single-statement rule.

.PARAMETER Root
  Repository root, for resolving EXEC_REVIEW_FILE. Defaults to the repo this plan
  folder lives in. Overridden by -SelfTest's fixture tree.

.PARAMETER DispatchDir
  Overrides DISPATCH_DIR. Used by -SelfTest; the real value is in named-sets.

.PARAMETER SelfTest
  Build a fixture dispatch and prove the gate PASSES on a well-formed one and
  FAILS on each seeded negative: a hand-authored verdict with no dispatch id, a
  dispatch id with no status.json, a prompt that never names the review file, a
  final.md still saying changes_required, and an approved verdict that
  nevertheless reports findings.
#>
[CmdletBinding()]
param(
    [string]$Root,
    [string]$DispatchDir,
    [switch]$SelfTest
)

$ErrorActionPreference = 'Stop'

$setsPath = Join-Path $PSScriptRoot 'named-sets.json'
if (-not (Test-Path -LiteralPath $setsPath)) {
    Write-Error ('missing NAMED_SETS_FILE ' + $setsPath)
    exit 1
}
$sets = Get-Content -LiteralPath $setsPath -Raw | ConvertFrom-Json

$reviewRel = [string]$sets.EXEC_REVIEW_FILE.value
$agent = [string]$sets.REVIEWER_AGENT.value
$schema = [string]$sets.DISPATCH_STATUS_SCHEMA.value
$idField = [string]$sets.DISPATCH_ID_FIELD.value
$expectedMode = [string]$sets.EXEC_REVIEW_MODE.value
$expectedVerdict = [string]$sets.EXEC_REVIEW_APPROVED.value
if ([string]::IsNullOrWhiteSpace($DispatchDir)) {
    $DispatchDir = [string]$sets.DISPATCH_DIR.value
}

foreach ($pair in @(
        @{ n = 'EXEC_REVIEW_FILE'; v = $reviewRel },
        @{ n = 'REVIEWER_AGENT'; v = $agent },
        @{ n = 'DISPATCH_STATUS_SCHEMA'; v = $schema },
        @{ n = 'DISPATCH_ID_FIELD'; v = $idField },
        @{ n = 'EXEC_REVIEW_MODE'; v = $expectedMode },
        @{ n = 'EXEC_REVIEW_APPROVED'; v = $expectedVerdict },
        @{ n = 'DISPATCH_DIR'; v = $DispatchDir })) {
    if ([string]::IsNullOrWhiteSpace($pair.v)) {
        Write-Error ('named-sets missing ' + $pair.n)
        exit 1
    }
}

if ([string]::IsNullOrWhiteSpace($Root)) {
    $Root = (Resolve-Path (Join-Path $PSScriptRoot '../../../..')).Path
}

function Get-FrontmatterValue {
    param([string]$Frontmatter, [string]$Key)
    $pattern = '(?m)^' + [regex]::Escape($Key) + ':\s*"?([^"\r\n]+)"?\s*$'
    $m = [regex]::Match($Frontmatter, $pattern)
    if (-not $m.Success) { return $null }
    return $m.Groups[1].Value.Trim()
}

function Invoke-Check {
    $reviewPath = Join-Path $Root $reviewRel
    if (-not (Test-Path -LiteralPath $reviewPath)) {
        Write-Error ('missing EXEC_REVIEW_FILE ' + $reviewPath)
        return 1
    }
    $reviewText = Get-Content -LiteralPath $reviewPath -Raw
    if ($reviewText -notmatch '(?s)\A---\r?\n(?<fm>.*?)\r?\n---') {
        Write-Error 'EXEC_REVIEW_FILE has no YAML frontmatter'
        return 1
    }
    $fm = $Matches['fm']

    foreach ($check in @(
            @{ key = 'agent'; want = $agent },
            @{ key = 'review_mode'; want = $expectedMode },
            @{ key = 'verdict'; want = $expectedVerdict },
            @{ key = 'findings_count'; want = '0' })) {
        $live = Get-FrontmatterValue -Frontmatter $fm -Key $check.key
        if ($live -ne $check.want) {
            Write-Error ('frontmatter ' + $check.key + '=' + $live + ' expected ' + $check.want)
            return 1
        }
    }

    $dispatchId = Get-FrontmatterValue -Frontmatter $fm -Key $idField
    if ([string]::IsNullOrWhiteSpace($dispatchId)) {
        Write-Error ('frontmatter has no ' + $idField + ' - a self-authored verdict cannot satisfy the no-self-review rule')
        return 1
    }

    $runDir = Join-Path $DispatchDir $dispatchId
    $statusPath = Join-Path $runDir 'status.json'
    if (-not (Test-Path -LiteralPath $statusPath)) {
        Write-Error ('missing status.json for ' + $idField + '=' + $dispatchId + ' at ' + $statusPath)
        return 1
    }
    $st = Get-Content -LiteralPath $statusPath -Raw | ConvertFrom-Json
    if ([string]$st.schema_version -ne $schema) {
        Write-Error ('status schema_version=' + $st.schema_version + ' expected ' + $schema)
        return 1
    }
    if ([string]$st.dispatch_id -ne $dispatchId) {
        Write-Error ('status dispatch_id=' + $st.dispatch_id + ' != frontmatter ' + $dispatchId)
        return 1
    }
    if ([string]$st.model -ne $agent) {
        Write-Error ('dispatch model=' + $st.model + ' expected ' + $agent)
        return 1
    }
    if ([int]$st.exit_code -ne 0) {
        Write-Error ('dispatch exit_code=' + $st.exit_code + ' for ' + $dispatchId)
        return 1
    }

    $promptPath = Join-Path $runDir 'prompt_temp.txt'
    if (-not (Test-Path -LiteralPath $promptPath)) {
        Write-Error ('missing prompt_temp.txt for ' + $dispatchId)
        return 1
    }
    $prompt = (Get-Content -LiteralPath $promptPath -Raw).Replace('\', '/')
    $reviewNorm = $reviewRel.Replace('\', '/')
    $reviewName = [System.IO.Path]::GetFileName($reviewRel)
    if (($prompt -notlike ('*' + $reviewNorm + '*')) -and ($prompt -notlike ('*' + $reviewName + '*'))) {
        Write-Error ('dispatch ' + $dispatchId + ' never names ' + $reviewRel + ' - wrong dispatch borrowed')
        return 1
    }

    $finalPath = [string]$st.output_paths.final_output
    if ([string]::IsNullOrWhiteSpace($finalPath) -or -not (Test-Path -LiteralPath $finalPath)) {
        Write-Error ('missing dispatch final output for ' + $dispatchId)
        return 1
    }
    $final = Get-Content -LiteralPath $finalPath -Raw
    $verdictMatch = [regex]::Match($final, '(?im)^\s*verdict:\s*`?([a-z_]+)`?')
    if (-not $verdictMatch.Success) {
        Write-Error ('dispatch final output states no verdict for ' + $dispatchId)
        return 1
    }
    if ($verdictMatch.Groups[1].Value -ne $expectedVerdict) {
        Write-Error ('dispatch final verdict=' + $verdictMatch.Groups[1].Value + ' expected ' + $expectedVerdict + ' (a prior receipt cannot approve a rewritten file)')
        return 1
    }

    Write-Host ('  ok  ' + $idField + '=' + $dispatchId + '  agent=' + $agent + '  verdict=' + $expectedVerdict)
    return 0
}

function Invoke-Gate {
    param([string[]]$GateArgs)
    $childArgs = @('-NoProfile', '-File', $PSCommandPath) + $GateArgs
    & pwsh @childArgs *> $null
    return $LASTEXITCODE
}

if ($SelfTest) {
    $tmp = Join-Path ([System.IO.Path]::GetTempPath()) ('exec-dispatch-selftest-' + [guid]::NewGuid().ToString('N'))
    $fixtureRoot = Join-Path $tmp 'repo'
    $fixtureDispatch = Join-Path $tmp 'dispatch'
    $dispatchId = 'exec-review-selftest-r1'
    $runDir = Join-Path $fixtureDispatch $dispatchId
    $reviewPath = Join-Path $fixtureRoot $reviewRel
    New-Item -ItemType Directory -Path (Split-Path -Parent $reviewPath) -Force | Out-Null
    New-Item -ItemType Directory -Path $runDir -Force | Out-Null
    $finalPath = Join-Path $runDir 'final.md'
    $statusPath = Join-Path $runDir 'status.json'
    $promptPath = Join-Path $runDir 'prompt_temp.txt'

    function Write-FixtureReview {
        param([string]$DispatchIdValue, [string]$FindingsCount = '0')
        $idLine = ''
        if (-not [string]::IsNullOrWhiteSpace($DispatchIdValue)) {
            $idLine = $idField + ': ' + $DispatchIdValue + "`n"
        }
        $body = "---`nagent: " + $agent + "`nreview_mode: " + $expectedMode +
        "`nverdict: " + $expectedVerdict + "`nfindings_count: " + $FindingsCount + "`n" +
        $idLine + "---`n`nFixture body.`n"
        Set-Content -LiteralPath $reviewPath -Value $body -Encoding UTF8
    }

    try {
        Write-FixtureReview -DispatchIdValue $dispatchId
        Set-Content -LiteralPath $statusPath -Encoding UTF8 -Value (@{
                schema_version = $schema
                dispatch_id    = $dispatchId
                model          = $agent
                exit_code      = 0
                output_paths   = @{ final_output = $finalPath }
            } | ConvertTo-Json -Depth 5)
        Set-Content -LiteralPath $promptPath -Encoding UTF8 -Value ('Review the implementation and write your verdict to ' + $reviewRel + '.')
        Set-Content -LiteralPath $finalPath -Encoding UTF8 -Value ('verdict: ' + $expectedVerdict + "`nfindings_count: 0`n")

        $results = @()

        $code = Invoke-Gate @('-Root', $fixtureRoot, '-DispatchDir', $fixtureDispatch)
        $results += [pscustomobject]@{ Name = 'well-formed dispatch passes'; Ok = ($code -eq 0) }

        # Negative 1: self-authored verdict with no dispatch id at all.
        Write-FixtureReview -DispatchIdValue ''
        $code = Invoke-Gate @('-Root', $fixtureRoot, '-DispatchDir', $fixtureDispatch)
        $results += [pscustomobject]@{ Name = ('self-authored verdict (no ' + $idField + ')'); Ok = ($code -ne 0) }
        Write-FixtureReview -DispatchIdValue $dispatchId

        # Negative 2: a dispatch id that has no status.json behind it.
        $code = Invoke-Gate @('-Root', $fixtureRoot, '-DispatchDir', (Join-Path $tmp 'empty-dispatch-dir'))
        $results += [pscustomobject]@{ Name = 'dispatch id with no status.json'; Ok = ($code -ne 0) }

        # Negative 3: a real dispatch that never names the review file.
        Set-Content -LiteralPath $promptPath -Value 'Review something else entirely.' -Encoding UTF8
        $code = Invoke-Gate @('-Root', $fixtureRoot, '-DispatchDir', $fixtureDispatch)
        $results += [pscustomobject]@{ Name = 'borrowed dispatch (prompt names another target)'; Ok = ($code -ne 0) }
        Set-Content -LiteralPath $promptPath -Encoding UTF8 -Value ('Review the implementation and write your verdict to ' + $reviewRel + '.')

        # Negative 4: the reviewer's own receipt still says changes_required.
        Set-Content -LiteralPath $finalPath -Value "verdict: changes_required`n" -Encoding UTF8
        $code = Invoke-Gate @('-Root', $fixtureRoot, '-DispatchDir', $fixtureDispatch)
        $results += [pscustomobject]@{ Name = 'stale changes_required receipt'; Ok = ($code -ne 0) }
        Set-Content -LiteralPath $finalPath -Encoding UTF8 -Value ('verdict: ' + $expectedVerdict + "`n")

        # Negative 5: approved verdict that nevertheless reports findings.
        Write-FixtureReview -DispatchIdValue $dispatchId -FindingsCount '2'
        $code = Invoke-Gate @('-Root', $fixtureRoot, '-DispatchDir', $fixtureDispatch)
        $results += [pscustomobject]@{ Name = 'approved with findings_count > 0'; Ok = ($code -ne 0) }
        Write-FixtureReview -DispatchIdValue $dispatchId

        # Negative 6: the dispatch itself failed.
        Set-Content -LiteralPath $statusPath -Encoding UTF8 -Value (@{
                schema_version = $schema
                dispatch_id    = $dispatchId
                model          = $agent
                exit_code      = 1
                output_paths   = @{ final_output = $finalPath }
            } | ConvertTo-Json -Depth 5)
        $code = Invoke-Gate @('-Root', $fixtureRoot, '-DispatchDir', $fixtureDispatch)
        $results += [pscustomobject]@{ Name = 'dispatch exited non-zero'; Ok = ($code -ne 0) }

        $failed = 0
        foreach ($r in $results) {
            if ($r.Ok) { Write-Host ('  PASS  ' + $r.Name) }
            else { Write-Host ('  FAIL  ' + $r.Name); $failed += 1 }
        }
        Write-Host ''
        Write-Host ('self-test cases: ' + $results.Count + '  failed: ' + $failed)
        if ($failed -gt 0) {
            Write-Error 'SELFTEST FAIL: EXEC_DISPATCH_CHECK'
            exit 1
        }
    }
    finally {
        Remove-Item -LiteralPath $tmp -Recurse -Force -ErrorAction SilentlyContinue
    }
    'SELFTEST PASS: EXEC_DISPATCH_CHECK'
    exit 0
}

exit (Invoke-Check)
