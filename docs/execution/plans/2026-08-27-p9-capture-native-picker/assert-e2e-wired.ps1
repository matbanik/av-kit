# Sole executable owner of the real-Electron E2E gate (AC-40.18 / AC-40.19).
#
# Round-3 finding N4: the plan scheduled only xunit + vitest and PRESERVED an unconditional
#   `AVKIT_E2E` no-spawn short-circuit, so the F2 -> IPC -> real Electron -> picker spawn ->
#   publish -> register -> refresh chain could be entirely missing while every scheduled gate
#   passed. Project canon (AGENTS.md, testing-strategy.md) requires runtime GUI behavior to be
#   verified by Playwright against real Electron.
# Round-4 finding R4-3: every check was string presence over raw text, so a spec containing
#   ONLY the two marker strings as comments passed, `test:e2e` only had to contain the
#   substring "playwright test", the stub only had to be a directory, and a short-circuit
#   line could be "satisfied" by a trailing `// AVKIT_REGION_PICKER_PATH` comment. Nothing
#   proved a capture test ever RAN. Corrections:
#     * -Mode Wired  : comment-stripped scans; each E2E_REQUIRED_CASES title must be a real
#                      `test('<title>')` declaration; the stub needs a PROJECT FILE and a
#                      non-hollow `dotnet publish` build script; a dedicated capture script
#                      must carry the spec path and the JSON reporter.
#     * -Mode Executed: the Playwright JSON reporter receipt must show each required case
#                      present, passing, from the capture spec file, with zero skipped,
#                      unexpected, or flaky results. This is the only check that proves the
#                      capture path executed.
# -SelfTest is the mandatory negative oracle for both modes.
param([switch]$SelfTest, [ValidateSet('Wired', 'Executed')][string]$Mode = 'Wired')
$ErrorActionPreference = 'Stop'
$setsPath = Join-Path $PSScriptRoot 'named-sets.json'
if (-not (Test-Path -LiteralPath $setsPath)) { Write-Error ('missing NAMED_SETS_FILE ' + $setsPath); exit 1 }
$sets = Get-Content -LiteralPath $setsPath -Raw | ConvertFrom-Json
$specPath = [string]$sets.E2E_SPEC_FILE
$configPath = [string]$sets.E2E_PLAYWRIGHT_CONFIG
$testDir = [string]$sets.E2E_TESTDIR
$e2eScript = [string]$sets.E2E_SCRIPT
$captureScript = [string]$sets.E2E_CAPTURE_SCRIPT
$captureSegments = @($sets.E2E_CAPTURE_REQUIRED_SEGMENTS)
$executedReceipt = [string]$sets.E2E_EXECUTED_RECEIPT
$requiredCases = @($sets.E2E_REQUIRED_CASES)
$required = @($sets.E2E_REQUIRED_MARKERS)
$forbidden = @($sets.E2E_FORBIDDEN_MARKERS)
$shortEnv = [string]$sets.E2E_SHORTCIRCUIT_ENV
$overrideEnv = [string]$sets.PICKER_PATH_ENV
$pickerModule = 'ui/src/main/capture-picker.ts'
$stubDir = [string]$sets.E2E_STUB_PROJECT_DIR
$stubProject = [string]$sets.E2E_STUB_PROJECT_FILE
$stubBuild = [string]$sets.E2E_STUB_BUILD_SCRIPT
$stubBuildSegment = [string]$sets.E2E_STUB_BUILD_REQUIRED_SEGMENT
$playwrightHead = [string]$sets.E2E_PLAYWRIGHT_HEAD
$splitPattern = [string]$sets.SCRIPT_SEGMENT_SPLIT_PATTERN
$allowedPrefixes = @($sets.SCRIPT_ALLOWED_PREFIXES)
$hollowHeads = @($sets.SCRIPT_HOLLOW_HEADS)
$dispositionFile = [string]$sets.E2E_DISPOSITION_FILE
$dispositionMarkers = @($sets.E2E_DISPOSITION_MARKERS)
$blockedReceipt = [string]$sets.E2E_BLOCKED_RECEIPT
$blockedClasses = @($sets.BLOCKED_CLASSES)
$errorClasses = @($sets.BLOCKED_ERROR_CLASSES)
$followupPattern = [string]$sets.FOLLOWUP_PATTERN
$followupSources = @($sets.FOLLOWUP_SOURCES)
$runStamp = [string]$sets.RUN_STAMPS.'e2e-capture'.stamp
. (Join-Path $PSScriptRoot 'lib-disposition.ps1')

# Strip // and /* */ comments from TypeScript. String literals are PRESERVED, because the
# required test titles live inside them; comments are what must not count as evidence.
function Remove-TsComments {
    param([string]$Source)
    $sb = New-Object System.Text.StringBuilder
    $i = 0
    $n = $Source.Length
    while ($i -lt $n) {
        $c = $Source[$i]
        $d = if ($i + 1 -lt $n) { $Source[$i + 1] } else { [char]0 }
        if ($c -eq '/' -and $d -eq '/') {
            while ($i -lt $n -and $Source[$i] -ne "`n") { $i++ }
            continue
        }
        if ($c -eq '/' -and $d -eq '*') {
            $i += 2
            while ($i + 1 -lt $n -and -not ($Source[$i] -eq '*' -and $Source[$i + 1] -eq '/')) {
                if ($Source[$i] -eq "`n") { [void]$sb.Append("`n") }
                $i++
            }
            $i = [Math]::Min($n, $i + 2)
            continue
        }
        # Skip over string bodies verbatim so a '//' inside a literal is not treated as a comment.
        if ($c -eq '"' -or $c -eq "'" -or $c -eq '`') {
            $q = $c
            [void]$sb.Append($c); $i++
            while ($i -lt $n) {
                if ($Source[$i] -eq '\' -and $i + 1 -lt $n) { [void]$sb.Append($Source[$i]); [void]$sb.Append($Source[$i + 1]); $i += 2; continue }
                [void]$sb.Append($Source[$i])
                if ($Source[$i] -eq $q) { $i++; break }
                $i++
            }
            continue
        }
        [void]$sb.Append($c)
        $i++
    }
    $sb.ToString()
}

# Strip runner prefixes that legitimately precede the real command, so `npx playwright test`
# and `cross-env CI=1 playwright test` are still recognised as running playwright.
function Remove-ScriptPrefixes {
    param([string]$Segment, [string[]]$AllowedPrefixes)
    $s = $Segment.Trim()
    for ($guard = 0; $guard -lt 16; $guard++) {
        $before = $s
        foreach ($p in $AllowedPrefixes) {
            if ($s.StartsWith([string]$p)) { $s = $s.Substring(([string]$p).Length).Trim() }
        }
        if ($s -match '^[A-Za-z_][A-Za-z0-9_]*=\S*\s+') { $s = [regex]::Replace($s, '^[A-Za-z_][A-Za-z0-9_]*=\S*\s+', '') }
        if ($s -eq $before) { break }
    }
    $s
}

# Round-5 finding R4-3-R5: substring checks over a whole npm script body accepted
# `echo playwright test tests/e2e/capture-picker.test.ts --reporter=json`, which runs nothing.
# A script now only counts if some EXECUTABLE segment of it (split on &&, ||, ;, |) actually
# STARTS WITH the required head command after allowed prefixes, and carries every required
# segment in that same command. Segments whose first token is a declared hollow head
# (echo/printf/rem/...) are not executable evidence.
function Test-ScriptSegment {
    param(
        [string]$Body,
        [string]$Head,
        [string[]]$RequiredSegments,
        [string[]]$HollowHeads,
        [string[]]$AllowedPrefixes,
        [string]$SplitPattern
    )
    if ([string]::IsNullOrWhiteSpace($Body)) { return 'script body is empty' }
    $hollowCarrier = $null
    foreach ($raw in @([regex]::Split($Body, $SplitPattern))) {
        $t = $raw.Trim()
        if ($t.Length -eq 0) { continue }
        $first = @($t -split '\s+')[0]
        $stripped = Remove-ScriptPrefixes -Segment $t -AllowedPrefixes $AllowedPrefixes
        $carriesAll = $true
        foreach ($seg in $RequiredSegments) { if ($t.IndexOf([string]$seg) -lt 0) { $carriesAll = $false } }
        if ($HollowHeads -contains $first) {
            if ($carriesAll) { $hollowCarrier = $t }
            continue
        }
        # Round-6 (non-blocking finding): a bare StartsWith has no token boundary, so
        # `playwright test-does-nothing ...` and `dotnet publisher ...` would both count as the
        # head command. The head must end the segment or be followed by whitespace.
        if ([regex]::IsMatch($stripped, '^' + [regex]::Escape($Head) + '(\s|$)') -and $carriesAll) { return $null }
    }
    if ($null -ne $hollowCarrier) {
        return 'the required segments appear only in the non-executing command "' + $hollowCarrier + '" - printing a command is not running it'
    }
    return 'no executable segment of "' + $Body.Trim() + '" runs "' + $Head + '" with all of: ' + ($RequiredSegments -join ', ')
}

function Test-SpecBody {
    param([string]$Body, [string[]]$Required, [string[]]$Forbidden, [string[]]$Cases, [string]$OverrideEnv)
    if ([string]::IsNullOrWhiteSpace($Body)) { return 'e2e spec is empty' }
    # Traceability markers may live in comments, so they are checked against the raw body...
    foreach ($m in $Required) {
        if ($Body.IndexOf([string]$m) -lt 0) { return 'e2e spec does not reference required marker "' + $m + '"' }
    }
    # ...but everything that must be REAL is checked against the comment-stripped body.
    $clean = Remove-TsComments -Source $Body
    foreach ($m in $Forbidden) {
        if ($clean.IndexOf([string]$m) -ge 0) { return 'e2e spec is neutralized by "' + $m + '" (G36)' }
    }
    if ($clean.IndexOf($OverrideEnv) -lt 0) {
        return 'e2e spec names ' + $OverrideEnv + ' only in comments - the real spawn chain is never driven'
    }
    foreach ($c in $Cases) {
        $pat = 'test\s*\(\s*[' + "'" + '"`]' + [regex]::Escape([string]$c) + '[' + "'" + '"`]'
        if (-not [regex]::IsMatch($clean, $pat)) {
            return 'e2e spec does not declare the required case test("' + $c + '")'
        }
    }
    return $null
}

# Every short-circuit line must ALSO name the override, i.e. the no-spawn branch is disabled
# whenever the test supplies a real picker path. Comments are stripped first: a trailing
# `// AVKIT_REGION_PICKER_PATH` is not a guard (R4-3).
function Test-ShortCircuitGuard {
    param([string]$Body, [string]$ShortEnv, [string]$OverrideEnv)
    $clean = Remove-TsComments -Source $Body
    $lines = @($clean -split "`n" | Where-Object { $_.IndexOf($ShortEnv) -ge 0 })
    if ($lines.Count -lt 1) { return 'no ' + $ShortEnv + ' short-circuit found - AC-40.11 requires the hermetic branch to exist' }
    foreach ($l in $lines) {
        if ($l.IndexOf($OverrideEnv) -lt 0) {
            return 'unconditional ' + $ShortEnv + ' short-circuit (' + $l.Trim() + ') - the real spawn chain can never be exercised'
        }
    }
    return $null
}

# Flatten the Playwright JSON reporter tree into { title; ok; file; status } records.
function Get-ReportedSpecs {
    param($Node, [string]$File)
    $out = New-Object System.Collections.ArrayList
    if ($null -eq $Node) { return $out.ToArray() }
    $f = $File
    if ($null -ne $Node.PSObject.Properties['file'] -and -not [string]::IsNullOrWhiteSpace([string]$Node.file)) { $f = [string]$Node.file }
    if ($null -ne $Node.PSObject.Properties['specs']) {
        foreach ($s in @($Node.specs)) {
            $sf = $f
            if ($null -ne $s.PSObject.Properties['file'] -and -not [string]::IsNullOrWhiteSpace([string]$s.file)) { $sf = [string]$s.file }
            $statuses = @()
            foreach ($t in @($s.tests)) { $statuses += [string]$t.status }
            [void]$out.Add([pscustomobject]@{
                title    = [string]$s.title
                ok       = [bool]$s.ok
                file     = $sf
                statuses = $statuses
            })
        }
    }
    if ($null -ne $Node.PSObject.Properties['suites']) {
        foreach ($child in @($Node.suites)) {
            foreach ($r in @(Get-ReportedSpecs -Node $child -File $f)) { [void]$out.Add($r) }
        }
    }
    $out.ToArray()
}

function Test-ExecutedReport {
    param([string]$Body, [string[]]$Cases, [string]$SpecLeaf)
    if ([string]::IsNullOrWhiteSpace($Body)) { return 'e2e result report is empty - the capture spec never ran' }
    try { $rep = $Body | ConvertFrom-Json } catch { return 'e2e result report is not valid JSON: ' + $_.Exception.Message }
    if ($null -eq $rep.PSObject.Properties['stats']) { return 'e2e result report carries no stats block' }
    $st = $rep.stats
    foreach ($k in @('unexpected', 'skipped', 'flaky')) {
        if ($null -eq $st.PSObject.Properties[$k]) { return 'e2e result stats has no "' + $k + '" count' }
        if ([int]$st.$k -ne 0) { return 'e2e run reports ' + [string]$st.$k + ' ' + $k + ' result(s) - the capture path is not green' }
    }
    if ([int]$st.expected -lt $Cases.Count) {
        return 'e2e run reports ' + [string]$st.expected + ' passing test(s), expected at least ' + $Cases.Count
    }
    $specs = @(Get-ReportedSpecs -Node $rep -File '')
    if ($specs.Count -lt 1) { return 'e2e result report lists no specs' }
    foreach ($c in $Cases) {
        $hit = @($specs | Where-Object { $_.title -eq [string]$c })
        if ($hit.Count -lt 1) { return 'required case "' + $c + '" never ran (absent from the result report)' }
        foreach ($h in $hit) {
            if (-not $h.ok) { return 'required case "' + $c + '" did not pass' }
            if (@($h.statuses | Where-Object { $_ -ne 'expected' }).Count -gt 0) {
                return 'required case "' + $c + '" has a non-passing status (' + ($h.statuses -join ',') + ')'
            }
            if ($h.file.Replace('\', '/').IndexOf($SpecLeaf) -lt 0) {
                return 'required case "' + $c + '" was reported from "' + $h.file + '", not from ' + $SpecLeaf
            }
        }
    }
    return $null
}

if ($SelfTest) {
    $specLeaf = Split-Path -Leaf $specPath
    $caseLines = ($requiredCases | ForEach-Object { 'test("' + $_ + '", async () => { expect(1).toBe(1) })' }) -join "`n"
    $goodSpec = @"
import { test, expect } from "@playwright/test"
// AC-40.18 - real Electron capture path
const stubExe = process.env.AVKIT_REGION_PICKER_PATH
$caseLines
"@
    $err = Test-SpecBody -Body $goodSpec -Required $required -Forbidden $forbidden -Cases $requiredCases -OverrideEnv $overrideEnv
    if ($null -ne $err) { Write-Error ('SELFTEST valid e2e spec rejected: ' + $err); exit 1 }

    if ($null -eq (Test-SpecBody -Body ($goodSpec -replace 'test\("', 'test.skip("') -Required $required -Forbidden $forbidden -Cases $requiredCases -OverrideEnv $overrideEnv)) {
        Write-Error 'SELFTEST S1 neutralized spec (.skip) accepted'; exit 1
    }
    if ($null -eq (Test-SpecBody -Body ($goodSpec.Replace('process.env.AVKIT_REGION_PICKER_PATH', 'undefined')) -Required $required -Forbidden $forbidden -Cases $requiredCases -OverrideEnv $overrideEnv)) {
        Write-Error 'SELFTEST S2 spec not using the picker override accepted'; exit 1
    }
    if ($null -eq (Test-SpecBody -Body '' -Required $required -Forbidden $forbidden -Cases $requiredCases -OverrideEnv $overrideEnv)) {
        Write-Error 'SELFTEST S3 empty spec accepted'; exit 1
    }
    # S4 (R4-3) - a file that contains ONLY the marker strings, all inside comments.
    $markerOnly = "// AC-40.18`n// AVKIT_REGION_PICKER_PATH`nexport const nothing = 1`n"
    if ($null -eq (Test-SpecBody -Body $markerOnly -Required $required -Forbidden $forbidden -Cases $requiredCases -OverrideEnv $overrideEnv)) {
        Write-Error 'SELFTEST S4 comment-only marker spec accepted - markers are not tests'; exit 1
    }
    # S5 - one required case missing from the declarations.
    $missingCase = $goodSpec.Replace('test("' + $requiredCases[0] + '"', 'test("something else"')
    if ($null -eq (Test-SpecBody -Body $missingCase -Required $required -Forbidden $forbidden -Cases $requiredCases -OverrideEnv $overrideEnv)) {
        Write-Error 'SELFTEST S5 spec missing a required case accepted'; exit 1
    }

    $guarded = "  if (process.env.AVKIT_E2E === '1' && !process.env.AVKIT_REGION_PICKER_PATH) {`n    return null`n  }"
    if ($null -ne (Test-ShortCircuitGuard -Body $guarded -ShortEnv $shortEnv -OverrideEnv $overrideEnv)) {
        Write-Error ('SELFTEST guarded short-circuit rejected: ' + (Test-ShortCircuitGuard -Body $guarded -ShortEnv $shortEnv -OverrideEnv $overrideEnv)); exit 1
    }
    $unguarded = "  if (process.env.AVKIT_E2E === '1') {`n    return null`n  }"
    if ($null -eq (Test-ShortCircuitGuard -Body $unguarded -ShortEnv $shortEnv -OverrideEnv $overrideEnv)) {
        Write-Error 'SELFTEST G1 unconditional short-circuit accepted - the real chain stays untested'; exit 1
    }
    if ($null -eq (Test-ShortCircuitGuard -Body 'const x = 1' -ShortEnv $shortEnv -OverrideEnv $overrideEnv)) {
        Write-Error 'SELFTEST G2 missing short-circuit accepted'; exit 1
    }
    # G3 (R4-3) - a comment cannot be the guard.
    $commentGuard = "  if (process.env.AVKIT_E2E === '1') { // AVKIT_REGION_PICKER_PATH`n    return null`n  }"
    if ($null -eq (Test-ShortCircuitGuard -Body $commentGuard -ShortEnv $shortEnv -OverrideEnv $overrideEnv)) {
        Write-Error 'SELFTEST G3 comment-only short-circuit guard accepted'; exit 1
    }

    # ---- Executed-report oracles ----
    $okSpecs = ($requiredCases | ForEach-Object { '{"title":"' + $_ + '","ok":true,"tests":[{"status":"expected"}]}' }) -join ','
    $goodReport = '{"suites":[{"title":"' + $specLeaf + '","file":"' + $specLeaf + '","specs":[' + $okSpecs + '],"suites":[]}],"stats":{"expected":3,"unexpected":0,"skipped":0,"flaky":0}}'
    $rerr = Test-ExecutedReport -Body $goodReport -Cases $requiredCases -SpecLeaf $specLeaf
    if ($null -ne $rerr) { Write-Error ('SELFTEST valid e2e report rejected: ' + $rerr); exit 1 }

    # X1 - a required case never ran.
    $x1 = $goodReport.Replace($requiredCases[0], 'some other case')
    if ($null -eq (Test-ExecutedReport -Body $x1 -Cases $requiredCases -SpecLeaf $specLeaf)) {
        Write-Error 'SELFTEST X1 report missing a required case accepted'; exit 1
    }
    # X2 - the case ran but failed.
    $x2 = $goodReport.Replace('"ok":true,"tests":[{"status":"expected"}]}]', '"ok":false,"tests":[{"status":"unexpected"}]}]').Replace('"unexpected":0', '"unexpected":1')
    if ($null -eq (Test-ExecutedReport -Body $x2 -Cases $requiredCases -SpecLeaf $specLeaf)) {
        Write-Error 'SELFTEST X2 failing case accepted'; exit 1
    }
    # X3 - skipped results.
    $x3 = $goodReport.Replace('"skipped":0', '"skipped":1')
    if ($null -eq (Test-ExecutedReport -Body $x3 -Cases $requiredCases -SpecLeaf $specLeaf)) {
        Write-Error 'SELFTEST X3 skipped result accepted'; exit 1
    }
    # X4 - empty / non-JSON report.
    if ($null -eq (Test-ExecutedReport -Body '' -Cases $requiredCases -SpecLeaf $specLeaf)) {
        Write-Error 'SELFTEST X4 empty report accepted'; exit 1
    }
    if ($null -eq (Test-ExecutedReport -Body 'Passed! - Failed: 0' -Cases $requiredCases -SpecLeaf $specLeaf)) {
        Write-Error 'SELFTEST X4b non-JSON report accepted'; exit 1
    }
    # X5 - the cases passed, but from a DIFFERENT spec file (a green unrelated suite).
    $x5 = $goodReport.Replace($specLeaf, 'capture-inbox.test.ts')
    if ($null -eq (Test-ExecutedReport -Body $x5 -Cases $requiredCases -SpecLeaf $specLeaf)) {
        Write-Error 'SELFTEST X5 results from an unrelated spec file accepted'; exit 1
    }
    # X6 - a green run that executed fewer tests than required.
    $x6 = '{"suites":[{"file":"' + $specLeaf + '","specs":[' + $okSpecs + ']}],"stats":{"expected":1,"unexpected":0,"skipped":0,"flaky":0}}'
    if ($null -eq (Test-ExecutedReport -Body $x6 -Cases $requiredCases -SpecLeaf $specLeaf)) {
        Write-Error 'SELFTEST X6 short run accepted'; exit 1
    }

    # ---- Script-segment oracles (R4-3-R5): printing a command is not running it ----
    $goodCapture = 'playwright test tests/e2e/capture-picker.test.ts --reporter=json'
    if ($null -ne (Test-ScriptSegment -Body $goodCapture -Head $playwrightHead -RequiredSegments $captureSegments -HollowHeads $hollowHeads -AllowedPrefixes $allowedPrefixes -SplitPattern $splitPattern)) {
        Write-Error ('SELFTEST valid capture script rejected: ' + (Test-ScriptSegment -Body $goodCapture -Head $playwrightHead -RequiredSegments $captureSegments -HollowHeads $hollowHeads -AllowedPrefixes $allowedPrefixes -SplitPattern $splitPattern)); exit 1
    }
    # S6 (R4-3-R5) - the reviewer's exact false-pass input.
    if ($null -eq (Test-ScriptSegment -Body ('echo ' + $goodCapture) -Head $playwrightHead -RequiredSegments $captureSegments -HollowHeads $hollowHeads -AllowedPrefixes $allowedPrefixes -SplitPattern $splitPattern)) {
        Write-Error 'SELFTEST S6 echo-only capture script accepted - it prints the command, it does not run it'; exit 1
    }
    if ($null -eq (Test-ScriptSegment -Body 'echo dotnet publish native/region-picker-stub' -Head $stubBuildSegment -RequiredSegments @($stubBuildSegment) -HollowHeads $hollowHeads -AllowedPrefixes $allowedPrefixes -SplitPattern $splitPattern)) {
        Write-Error 'SELFTEST S6b echo-only stub build accepted'; exit 1
    }
    # S6c - the required segments smeared across two commands, only one of which executes.
    if ($null -eq (Test-ScriptSegment -Body 'playwright test && echo tests/e2e/capture-picker.test.ts --reporter=json' -Head $playwrightHead -RequiredSegments $captureSegments -HollowHeads $hollowHeads -AllowedPrefixes $allowedPrefixes -SplitPattern $splitPattern)) {
        Write-Error 'SELFTEST S6c split-across-commands capture script accepted'; exit 1
    }
    # S6d - the head command never appears at all.
    if ($null -eq (Test-ScriptSegment -Body 'node scripts/pretend.js tests/e2e/capture-picker.test.ts --reporter=json playwright test' -Head $playwrightHead -RequiredSegments $captureSegments -HollowHeads $hollowHeads -AllowedPrefixes $allowedPrefixes -SplitPattern $splitPattern)) {
        Write-Error 'SELFTEST S6d script mentioning the head mid-command accepted'; exit 1
    }
    # S6e (round-6, non-blocking) - a DIFFERENT command that merely starts with the head's text.
    if ($null -eq (Test-ScriptSegment -Body 'playwright test-does-nothing tests/e2e/capture-picker.test.ts --reporter=json' -Head $playwrightHead -RequiredSegments $captureSegments -HollowHeads $hollowHeads -AllowedPrefixes $allowedPrefixes -SplitPattern $splitPattern)) {
        Write-Error 'SELFTEST S6e a command that only starts with the head''s characters accepted'; exit 1
    }
    # S7 (positive) - legitimate runner prefixes must still pass, or the rule is over-strict.
    foreach ($ok in @('npx ' + $goodCapture, 'cross-env CI=1 ' + $goodCapture, 'npm run build:picker-stub && ' + $goodCapture)) {
        $e = Test-ScriptSegment -Body $ok -Head $playwrightHead -RequiredSegments $captureSegments -HollowHeads $hollowHeads -AllowedPrefixes $allowedPrefixes -SplitPattern $splitPattern
        if ($null -ne $e) { Write-Error ('SELFTEST S7 prefixed capture script rejected ("' + $ok + '"): ' + $e); exit 1 }
    }

    # ---- Disposition / freshness oracles (R5-2, R4-3-R5) ----
    $fx = Join-Path ([System.IO.Path]::GetTempPath()) 'avkit-e2e-selftest'
    if (Test-Path -LiteralPath $fx) { Remove-Item -LiteralPath $fx -Recurse -Force }
    New-Item -ItemType Directory -Path $fx -Force | Out-Null
    $fxReceipt = Join-Path $fx 'ui-e2e-capture.txt'
    $fxSource = Join-Path $fx 'known-issues.md'
    Set-Content -LiteralPath $fxReceipt -Value "npm --prefix ui run test:e2e:capture`nError: Missing X server or `$DISPLAY`nelectron exited 1" -Encoding utf8
    Set-Content -LiteralPath $fxSource -Value '| E2E-SANDBOX-NODISPLAY | Electron cannot launch headless in the agent sandbox |' -Encoding utf8
    $fxSources = @($fxSource)
    $blockedGood = "BLOCKED=yes`nREASON=Electron cannot open a display in this sandbox`nCLASS=external-error`nFOLLOWUP=E2E-SANDBOX-NODISPLAY`nRECEIPT=$fxReceipt`nERROR_SIGNATURE=Missing X server"
    # Y0 (positive) - a fully-evidenced external blocker is the declared `[B]` path.
    $y0 = Test-BlockedEvidence -Map (Get-DispositionMap -Body $blockedGood) -Classes $blockedClasses -ErrorClasses $errorClasses -FollowupPattern $followupPattern -FollowupSources $fxSources -RequiredReceipt $fxReceipt
    if ($null -ne $y0) { Write-Error ('SELFTEST Y0 evidenced no-display blocker rejected: ' + $y0); exit 1 }
    # Y1 - a subjective class is never a valid `[B]`.
    if ($null -eq (Test-BlockedEvidence -Map (Get-DispositionMap -Body ($blockedGood.Replace('CLASS=external-error', 'CLASS=out-of-scope'))) -Classes $blockedClasses -ErrorClasses $errorClasses -FollowupPattern $followupPattern -FollowupSources $fxSources -RequiredReceipt $fxReceipt)) {
        Write-Error 'SELFTEST Y1 subjective blocked class accepted'; exit 1
    }
    # Y2 (R4-4-R5) - a regex-shaped follow-up that names nothing registered.
    if ($null -eq (Test-BlockedEvidence -Map (Get-DispositionMap -Body ($blockedGood.Replace('FOLLOWUP=E2E-SANDBOX-NODISPLAY', 'FOLLOWUP=SOME-FUTURE-TASK'))) -Classes $blockedClasses -ErrorClasses $errorClasses -FollowupPattern $followupPattern -FollowupSources $fxSources -RequiredReceipt $fxReceipt)) {
        Write-Error 'SELFTEST Y2 unregistered follow-up id accepted'; exit 1
    }
    # Y3 - the receipt exists but does not contain the claimed error.
    Set-Content -LiteralPath (Join-Path $fx 'unrelated.txt') -Value 'PASS: something else entirely' -Encoding utf8
    if ($null -eq (Test-BlockedEvidence -Map (Get-DispositionMap -Body ($blockedGood.Replace('ERROR_SIGNATURE=Missing X server', 'ERROR_SIGNATURE=some error that never happened'))) -Classes $blockedClasses -ErrorClasses $errorClasses -FollowupPattern $followupPattern -FollowupSources $fxSources -RequiredReceipt $fxReceipt)) {
        Write-Error 'SELFTEST Y3 unreproduced error signature accepted'; exit 1
    }
    # Y4 - the receipt is a real file, but not the one this row produces.
    if ($null -eq (Test-BlockedEvidence -Map (Get-DispositionMap -Body ($blockedGood.Replace('RECEIPT=' + $fxReceipt, 'RECEIPT=' + (Join-Path $fx 'unrelated.txt')))) -Classes $blockedClasses -ErrorClasses $errorClasses -FollowupPattern $followupPattern -FollowupSources $fxSources -RequiredReceipt $fxReceipt)) {
        Write-Error 'SELFTEST Y4 unrelated receipt accepted - evidence must come from the failing run'; exit 1
    }
    # X7 (R4-3-R5) - a green report left behind by an earlier run is not this run's evidence.
    $fxStamp = Join-Path $fx 'run.stamp'
    $fxReport = Join-Path $fx 'results.json'
    Set-Content -LiteralPath $fxReport -Value $goodReport -Encoding utf8
    Set-Content -LiteralPath $fxStamp -Value 'armed' -Encoding utf8
    (Get-Item -LiteralPath $fxReport).LastWriteTimeUtc = (Get-Item -LiteralPath $fxStamp).LastWriteTimeUtc.AddSeconds(-60)
    if ($null -eq (Test-ArtifactFresh -Artifact $fxReport -Stamp $fxStamp)) {
        Write-Error 'SELFTEST X7 stale (pre-arming) e2e report accepted'; exit 1
    }
    # X7b - no stamp at all means the step was never armed.
    Remove-Item -LiteralPath $fxStamp -Force
    if ($null -eq (Test-ArtifactFresh -Artifact $fxReport -Stamp $fxStamp)) {
        Write-Error 'SELFTEST X7b unarmed run accepted'; exit 1
    }
    Remove-Item -LiteralPath $fx -Recurse -Force

    'PASS: E2E_WIRED self-test (S1 .skip, S2 no override, S3 empty, S4 comment-only markers, S5 missing case, S6/S6b/S6c/S6d hollow+split scripts, S6e head-prefix impostor, G1 unconditional, G2 absent, G3 comment guard, X1 missing case, X2 failing, X3 skipped, X4 empty/non-JSON, X5 wrong spec file, X6 short run, X7/X7b stale+unarmed report, Y1 subjective class, Y2 unregistered follow-up, Y3 unreproduced error, Y4 unrelated receipt all rejected; S7 prefixed scripts and Y0 evidenced blocker accepted)'
    exit 0
}

if ($Mode -eq 'Executed') {
    # Round-5 finding R5-2: the plan declared a no-display `[B]` path for this row while the
    # verification runner propagated the same failure unconditionally, so the declared path
    # could never reach DONE. This mode is now the single DISPOSITION point for the capture
    # E2E: it either accepts a fully-evidenced external blocker, or demands a fresh green run.
    if (-not (Test-Path -LiteralPath $dispositionFile)) {
        Write-Error ('missing E2E_DISPOSITION_FILE ' + $dispositionFile + ' - the capture E2E must be dispositioned BLOCKED=no or BLOCKED=yes with evidence'); exit 1
    }
    $dBody = Get-Content -LiteralPath $dispositionFile -Raw
    $mErr = Test-DispositionMarkers -Body $dBody -Markers $dispositionMarkers
    if ($null -ne $mErr) { Write-Error ($dispositionFile + ': ' + $mErr); exit 1 }
    $dMap = Get-DispositionMap -Body $dBody
    $blocked = [string]$dMap['BLOCKED']
    if ($blocked -ne 'yes' -and $blocked -ne 'no') {
        Write-Error ($dispositionFile + ': BLOCKED must be exactly "yes" or "no" (got "' + $blocked + '")'); exit 1
    }
    if ($blocked -eq 'yes') {
        $bErr = Test-BlockedEvidence -Map $dMap -Classes $blockedClasses -ErrorClasses $errorClasses -FollowupPattern $followupPattern -FollowupSources $followupSources -RequiredReceipt $blockedReceipt
        if ($null -ne $bErr) { Write-Error ($dispositionFile + ': ' + $bErr); exit 1 }
        'PASS: E2E_EXECUTED [B] ' + [string]$dMap['CLASS'] + ' blocker evidenced in ' + [string]$dMap['RECEIPT'] + ', follow-up ' + [string]$dMap['FOLLOWUP'] + ' registered'
        exit 0
    }
    # BLOCKED=no: the report must have been produced BY THIS RUN, not left behind by an
    # earlier one (R4-3-R5), and it must be green for every required case.
    $fErr = Test-ArtifactFresh -Artifact $executedReceipt -Stamp $runStamp
    if ($null -ne $fErr) { Write-Error ('E2E_EXECUTED_RECEIPT: ' + $fErr); exit 1 }
    $rErr = Test-ExecutedReport -Body (Get-Content -LiteralPath $executedReceipt -Raw) -Cases $requiredCases -SpecLeaf (Split-Path -Leaf $specPath)
    if ($null -ne $rErr) { Write-Error ($executedReceipt + ': ' + $rErr); exit 1 }
    'PASS: E2E_EXECUTED ' + $requiredCases.Count + ' capture cases ran green from ' + $specPath + ' (report freshly produced by this run)'
    exit 0
}

foreach ($p in @($specPath, $configPath, 'ui/package.json', $pickerModule)) {
    if (-not (Test-Path -LiteralPath $p)) { Write-Error ('missing ' + $p); exit 1 }
}

# 1. Spec discoverable + not neutralized + declares the required cases.
$config = Get-Content -LiteralPath $configPath -Raw
if ($config.IndexOf($testDir) -lt 0) { Write-Error ($configPath + ' does not declare testDir ' + $testDir); exit 1 }
$specName = Split-Path -Leaf $specPath
if ($specName -notlike '*.test.ts' -and $specName -notlike '*.spec.ts') {
    Write-Error ($specName + ' does not match the playwright testMatch patterns (*.test.ts / *.spec.ts)')
    exit 1
}
$specDir = (Split-Path -Parent $specPath) -replace '\\', '/'
if ($specDir -ne (('ui/' + $testDir) -replace '\./', '')) {
    Write-Error ($specPath + ' is not inside the configured testDir (' + $testDir + ')')
    exit 1
}
$specErr = Test-SpecBody -Body (Get-Content -LiteralPath $specPath -Raw) -Required $required -Forbidden $forbidden -Cases $requiredCases -OverrideEnv $overrideEnv
if ($null -ne $specErr) { Write-Error ($specPath + ': ' + $specErr); exit 1 }

# 2. Scripts: the suite runner, the capture-only runner that emits the JSON receipt, and a
#    non-hollow stub build.
$pkg = Get-Content -LiteralPath 'ui/package.json' -Raw | ConvertFrom-Json
$names = @($pkg.scripts.PSObject.Properties.Name)
foreach ($s in @($e2eScript, $captureScript, $stubBuild)) {
    if ($names -notcontains $s) { Write-Error ('ui/package.json has no "' + $s + '" script'); exit 1 }
}
# Round-11 trim: the full suite's own script shape is no longer policed here. What proves the
# product is the capture spec below; `test:e2e` only has to exist so the row that runs it resolves.
$captureErr = Test-ScriptSegment -Body ([string]$pkg.scripts.$captureScript) -Head $playwrightHead -RequiredSegments $captureSegments -HollowHeads $hollowHeads -AllowedPrefixes $allowedPrefixes -SplitPattern $splitPattern
if ($null -ne $captureErr) { Write-Error ('"' + $captureScript + '": ' + $captureErr); exit 1 }
$stubErr = Test-ScriptSegment -Body ([string]$pkg.scripts.$stubBuild) -Head $stubBuildSegment -RequiredSegments @($stubBuildSegment) -HollowHeads $hollowHeads -AllowedPrefixes $allowedPrefixes -SplitPattern $splitPattern
if ($null -ne $stubErr) { Write-Error ('"' + $stubBuild + '": ' + $stubErr + ' - a hollow script cannot produce the stub'); exit 1 }

# 3. Conditional short-circuit in the production module.
$guardErr = Test-ShortCircuitGuard -Body (Get-Content -LiteralPath $pickerModule -Raw) -ShortEnv $shortEnv -OverrideEnv $overrideEnv
if ($null -ne $guardErr) { Write-Error ($pickerModule + ': ' + $guardErr); exit 1 }

# 4. Deterministic sidecar stub exists as a real project, not just a folder.
if (-not (Test-Path -LiteralPath $stubDir)) { Write-Error ('missing e2e sidecar stub project ' + $stubDir); exit 1 }
if (-not (Test-Path -LiteralPath $stubProject)) { Write-Error ('missing e2e sidecar stub project file ' + $stubProject); exit 1 }

'PASS: E2E_WIRED ' + $specPath + ' discoverable, un-neutralized, override-driven, ' + $requiredCases.Count + ' required cases declared'
exit 0
