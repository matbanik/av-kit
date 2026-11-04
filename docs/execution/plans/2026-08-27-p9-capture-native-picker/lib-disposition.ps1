# Shared, single-owner helpers for evidence binding (PR-9: one owner per rule).
#
# Round-11 trim: this file used to carry a nonce/arming protocol, a Playwright/vitest
# report-cause adjudicator and a failure-block parser - ~480 lines of machinery guarding a
# 200-line C# helper. All of it is deleted. What is left is the three rules two gates
# genuinely share, and nothing here polices the shape of anyone's source code.
#
# Two gates need the SAME three rules, and round-5 findings R4-3-R5 / R4-4-R5 / R5-2 all
# stem from each gate having invented its own weaker version:
#   * KEY=VALUE disposition parsing              (smoke row 9, e2e row 7a)
#   * "blocked" evidence is real                 (a `[B]` needs a command receipt carrying the
#                                                 actual error signature and a REGISTERED
#                                                 follow-up id, per AGENTS.md's `[B]` rule)
#   * an artifact was produced BY THIS RUN       (freshness against an arming stamp, so a
#                                                 stale prior receipt cannot satisfy a gate)
# Dot-source this file; do not re-implement any of it in a consumer gate.

function Get-DispositionMap {
    param([string]$Body)
    $map = @{}
    foreach ($line in @($Body -split "`n")) {
        $t = $line.Trim()
        if ($t.Length -eq 0 -or $t.StartsWith('#')) { continue }
        $eq = $t.IndexOf('=')
        if ($eq -lt 1) { continue }
        $k = $t.Substring(0, $eq).Trim()
        $v = $t.Substring($eq + 1).Trim()
        if (-not $map.ContainsKey($k)) { $map[$k] = $v }
    }
    return $map
}

function Test-DispositionMarkers {
    param([string]$Body, [string[]]$Markers)
    foreach ($m in $Markers) {
        if ($Body.IndexOf([string]$m) -lt 0) { return 'disposition is missing the required key "' + $m + '"' }
    }
    return $null
}

# A follow-up id is only real if it is REGISTERED somewhere a human will see it. A regex-shaped
# string that names nothing is exactly the R4-4-R5 false pass.
function Resolve-Followup {
    param([string]$Id, [string[]]$Sources)
    if ([string]::IsNullOrWhiteSpace($Id)) { return 'FOLLOWUP is empty' }
    foreach ($s in $Sources) {
        if (-not (Test-Path -LiteralPath $s)) { continue }
        $body = Get-Content -LiteralPath $s -Raw
        if ($null -eq $body) { continue }
        if ($body.IndexOf($Id) -ge 0) { return $null }
    }
    return 'FOLLOWUP "' + $Id + '" is not registered in any of ' + ($Sources -join ', ') + ' - a `[B]` requires a linked follow-up task, not a well-formed string'
}

# The evidence contract for a BLOCKED=yes disposition. `$Map` comes from Get-DispositionMap.
# `$ErrorClasses` are the classes that must additionally carry a reproduced error signature
# (AGENTS.md `[B]` cases (a) external error and (b) missing dependency); `human-decision` is
# a gate, not an error, so it needs no error text.
function Test-BlockedEvidence {
    param(
        [hashtable]$Map,
        [string[]]$Classes,
        [string[]]$ErrorClasses,
        [string]$FollowupPattern,
        [string[]]$FollowupSources,
        [string]$RequiredReceipt
    )
    $reason = [string]$Map['REASON']
    if ([string]::IsNullOrWhiteSpace($reason)) { return 'BLOCKED=yes with an empty REASON' }
    $class = [string]$Map['CLASS']
    if ($Classes -notcontains $class) {
        return 'CLASS "' + $class + '" is not one of the objective blocked classes (' + ($Classes -join ', ') + ') - subjective reasons are never a valid `[B]`'
    }
    $followup = [string]$Map['FOLLOWUP']
    if (-not [regex]::IsMatch($followup, $FollowupPattern)) {
        return 'FOLLOWUP "' + $followup + '" does not match the registered-id form ' + $FollowupPattern
    }
    $fErr = Resolve-Followup -Id $followup -Sources $FollowupSources
    if ($null -ne $fErr) { return $fErr }
    $receipt = [string]$Map['RECEIPT']
    if ([string]::IsNullOrWhiteSpace($receipt)) { return 'BLOCKED=yes with no RECEIPT' }
    if (-not [string]::IsNullOrWhiteSpace($RequiredReceipt) -and $receipt.Replace('\', '/') -ne $RequiredReceipt.Replace('\', '/')) {
        return 'RECEIPT "' + $receipt + '" is not the receipt this row produces (' + $RequiredReceipt + ') - evidence must come from the failing run itself'
    }
    if (-not (Test-Path -LiteralPath $receipt)) { return 'RECEIPT "' + $receipt + '" does not exist - a blocked claim needs a real receipt' }
    $body = Get-Content -LiteralPath $receipt -Raw
    if ([string]::IsNullOrWhiteSpace($body)) { return 'RECEIPT "' + $receipt + '" is empty' }
    if ($ErrorClasses -contains $class) {
        $sig = [string]$Map['ERROR_SIGNATURE']
        if ([string]::IsNullOrWhiteSpace($sig)) {
            return 'CLASS ' + $class + ' requires a non-empty ERROR_SIGNATURE - a reproduced error is the evidence'
        }
        if ($body.IndexOf($sig) -lt 0) {
            return 'ERROR_SIGNATURE "' + $sig + '" does not appear in RECEIPT "' + $receipt + '" - the error is asserted, not reproduced'
        }
    }
    return $null
}
function Test-ArtifactFresh {
    param([string]$Artifact, [string]$Stamp)
    if (-not (Test-Path -LiteralPath $Stamp)) {
        return 'missing run stamp ' + $Stamp + ' - the step was never armed, so its artifact cannot be attributed to this run'
    }
    if (-not (Test-Path -LiteralPath $Artifact)) { return 'missing artifact ' + $Artifact }
    $sTime = (Get-Item -LiteralPath $Stamp).LastWriteTimeUtc
    $aTime = (Get-Item -LiteralPath $Artifact).LastWriteTimeUtc
    if ($aTime -lt $sTime) {
        return 'artifact ' + $Artifact + ' (' + $aTime.ToString('o') + ') predates the run stamp ' + $Stamp + ' (' + $sTime.ToString('o') + ') - it is a stale receipt from an earlier run'
    }
    return $null
}
