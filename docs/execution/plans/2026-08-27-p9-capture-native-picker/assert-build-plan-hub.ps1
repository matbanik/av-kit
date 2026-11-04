# Sole executable owner of the BUILD_PLAN hub reconciliation gate (AC-40.21).
#
# Round-5 finding R5-1: the plan's BUILD_PLAN.md treatment was a REPORT-ONLY audit - the task
# row said "audit the hub for stale overlay/desktopCapturer language", which a run can satisfy
# by printing the hits and changing nothing. `docs/BUILD_PLAN.md` is the hub every other agent
# reads first; leaving it describing "F2 region overlay" and a Chromium `desktopCapturer` grab
# after this MEU deletes both is exactly the AGENTS.md §Pre-Handoff Self-Review item 4 failure
# ("if you changed architecture, rg canonical docs for the old pattern").
#
# Round-6 finding R6-3: the line-scoped exemption was satisfied by the mere CO-OCCURRENCE of a
# required token, so appending " region picker" to each otherwise-unchanged stale line passed a
# hub that still described the deleted design. Token co-occurrence is not reconciliation. The
# gate now has three halves:
#   1. Final state - every HUB_REQUIRED_LINES entry must appear VERBATIM. These are the exact
#                    replacement texts for hub lines 32/93/111/143, so "reconciled" has one
#                    defined meaning that a cosmetic suffix cannot reach.
#   2. Totality    - every HUB_FORBIDDEN_TOKENS term describing the deleted Chromium design must
#                    be gone. Matching is case-insensitive, so "Overlay" cannot slip past by
#                    capitalisation. A forbidden term survives ONLY on a line that carries BOTH a
#                    HUB_REQUIRED_TOKENS term AND a HUB_RETIREMENT_MARKERS term - i.e. the
#                    sentence explicitly retires the old word ("the region picker REPLACED the
#                    Chromium overlay"), not merely mentions the new one beside it.
#   3. Presence    - every HUB_REQUIRED_TOKENS term must be present somewhere in the hub.
#
# Non-vacuity: TODAY's hub has four bare `overlay` lines (32, 93, 111, 143), zero
# `region picker`, and none of the four required replacement lines, so this predicate FAILS on
# the unmodified repo. Oracle H0 pins those exact line texts as a permanent fixture, and H6 pins
# the reviewer's cosmetic-suffix bypass, so both proofs survive the hub being fixed.
param([switch]$SelfTest)
$ErrorActionPreference = 'Stop'
$setsPath = Join-Path $PSScriptRoot 'named-sets.json'
if (-not (Test-Path -LiteralPath $setsPath)) { Write-Error ('missing NAMED_SETS_FILE ' + $setsPath); exit 1 }
$sets = Get-Content -LiteralPath $setsPath -Raw | ConvertFrom-Json
$hubFile = [string]$sets.HUB_FILE
$forbidden = @($sets.HUB_FORBIDDEN_TOKENS)
$required = @($sets.HUB_REQUIRED_TOKENS)
$retirement = @($sets.HUB_RETIREMENT_MARKERS)
$requiredLines = @($sets.HUB_REQUIRED_LINES)

function Test-Hub {
    param([string]$Body, [string[]]$Forbidden, [string[]]$Required, [string[]]$Retirement, [string[]]$RequiredLines)
    if ([string]::IsNullOrWhiteSpace($Body)) { return 'hub file is empty' }
    $lines = @(($Body -replace "`r", '') -split "`n")
    $trimmed = @($lines | ForEach-Object { ([string]$_).Trim() })

    # 1. Final state. The hub is reconciled only when it CARRIES the replacement text.
    foreach ($rl in $RequiredLines) {
        $want = ([string]$rl).Trim()
        if (@($trimmed | Where-Object { $_ -ceq $want }).Count -lt 1) {
            return 'hub does not carry the required reconciled line verbatim - a cosmetic edit is not a rewrite. Expected: ' + $want
        }
    }

    # 2. Totality, with an explicit-retirement exemption.
    for ($i = 0; $i -lt $lines.Count; $i++) {
        $line = [string]$lines[$i]
        $carriesRequired = $false
        foreach ($r in $Required) {
            if ($line.IndexOf([string]$r, [System.StringComparison]::OrdinalIgnoreCase) -ge 0) { $carriesRequired = $true }
        }
        $carriesRetirement = $false
        foreach ($m in $Retirement) {
            if ($line.IndexOf([string]$m, [System.StringComparison]::OrdinalIgnoreCase) -ge 0) { $carriesRetirement = $true }
        }
        if ($carriesRequired -and $carriesRetirement) { continue }
        foreach ($f in $Forbidden) {
            if ($line.IndexOf([string]$f, [System.StringComparison]::OrdinalIgnoreCase) -ge 0) {
                $why = if ($carriesRequired) {
                    ' - naming the replacement on the same line is not retiring the old design; say what replaced it'
                } else { '' }
                return 'line ' + ($i + 1) + ' still describes the deleted Chromium design ("' + $f + '")' + $why + ': ' + $line.Trim()
            }
        }
    }

    # 3. Presence.
    foreach ($r in $Required) {
        if ($Body.IndexOf([string]$r, [System.StringComparison]::OrdinalIgnoreCase) -lt 0) {
            return 'hub never mentions "' + $r + '" - the replacement architecture is not reflected in the hub every agent reads first'
        }
    }
    return $null
}

if ($SelfTest) {
    $hubArgs = @{ Forbidden = $forbidden; Required = $required; Retirement = $retirement; RequiredLines = $requiredLines }
    # H0 - the four requirement-stating hub lines as they stand TODAY. Pinned verbatim so the
    #      non-vacuity proof outlives the hub edit that this gate forces.
    $todayLines = @(
        '| 9 | Screenshot capture | F2 region overlay, inbox filmstrip, annotate; tray + MCP | Phase 1-6 (ports, chrome) | [09-screenshot-capture.md](build-plan/09-screenshot-capture.md) |',
        '| Capture GUI | Rail **Capture** below Convert (`/capture`, Ctrl+5); filmstrip + viewport; tray + F2 overlay | Phase 9 |',
        '| [09-screenshot-capture.md](build-plan/09-screenshot-capture.md) | CaptureShot, tray/F2 overlay, `/captures`, `avkit_capture`, Capture page |',
        '| [09-screenshot-capture.md](build-plan/09-screenshot-capture.md) ShareX source map | Capture | Tray + F2 + light-region overlay + save-to-folder; rewrite, do not paste GPL-3.0 C# |'
    )
    if ($null -eq (Test-Hub -Body ($todayLines -join "`n") @hubArgs)) {
        Write-Error 'SELFTEST H0 accepted the CURRENT hub text - the gate is vacuous'; exit 1
    }
    # H5 (positive) - the reconciled hub: every required replacement line verbatim, plus a
    #      sentence that keeps the old words only to declare them retired.
    $reconciled = @($requiredLines) + @(
        'Phase 9.1 replaced the Chromium overlay + desktopCapturer grab with the native region picker sidecar.'
    )
    $e = Test-Hub -Body ($reconciled -join "`n") @hubArgs
    if ($null -ne $e) { Write-Error ('SELFTEST H5 reconciled hub rejected: ' + $e); exit 1 }
    # H6 (R6-3) - the reviewer's exact bypass: append the required token to each stale line and
    #      change nothing else. Co-occurrence is not reconciliation.
    $cosmetic = @($todayLines | ForEach-Object { $_ + ' region picker' })
    if ($null -eq (Test-Hub -Body ($cosmetic -join "`n") @hubArgs)) {
        Write-Error 'SELFTEST H6 cosmetic "region picker" suffix accepted - the hub still describes the deleted design'; exit 1
    }
    # H7 - reconciled lines present, but a surviving forbidden term sits on a line that only
    #      NAMES the replacement without retiring the old design.
    $unframed = @($requiredLines) + @('The region picker and the desktopCapturer grab both exist.')
    if ($null -eq (Test-Hub -Body ($unframed -join "`n") @hubArgs)) {
        Write-Error 'SELFTEST H7 unframed forbidden term accepted - co-occurrence is not a retirement statement'; exit 1
    }
    # H1 - the Chromium grab API named in a bare requirement line.
    $bareGrab = @($requiredLines) + @('| grab | desktopCapturer freeze + crop |')
    if ($null -eq (Test-Hub -Body ($bareGrab -join "`n") @hubArgs)) {
        Write-Error 'SELFTEST H1 bare desktopCapturer line accepted'; exit 1
    }
    # H2 - capitalisation must not launder the term.
    $capitalised = @($requiredLines) + @('| chrome | Tray + F2 Overlay window |')
    if ($null -eq (Test-Hub -Body ($capitalised -join "`n") @hubArgs)) {
        Write-Error 'SELFTEST H2 capitalised Overlay accepted'; exit 1
    }
    # H3 - deleting the old words but never naming the replacement leaves the hub silent.
    if ($null -eq (Test-Hub -Body '| 9 | Screenshot capture | F2 selection, inbox filmstrip, annotate |' @hubArgs)) {
        Write-Error 'SELFTEST H3 hub without the replacement term accepted'; exit 1
    }
    # H4 - empty hub.
    if ($null -eq (Test-Hub -Body '' @hubArgs)) {
        Write-Error 'SELFTEST H4 empty hub accepted'; exit 1
    }

    'PASS: BUILD_PLAN_HUB self-test (H0 today''s hub, H1 desktopCapturer, H2 capitalised Overlay, H3 no replacement term, H4 empty, H6 cosmetic required-token suffix, H7 unframed forbidden term all rejected; H5 reconciled hub with all ' + $requiredLines.Count + ' required lines accepted)'
    exit 0
}

$hubPath = Join-Path (Split-Path -Parent (Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $PSScriptRoot)))) $hubFile
if (-not (Test-Path -LiteralPath $hubPath)) { Write-Error ('missing HUB_FILE ' + $hubPath); exit 1 }
$err = Test-Hub -Body (Get-Content -LiteralPath $hubPath -Raw) -Forbidden $forbidden -Required $required -Retirement $retirement -RequiredLines $requiredLines
if ($null -ne $err) { Write-Error ($hubFile + ': ' + $err); exit 1 }
'PASS: BUILD_PLAN_HUB ' + $hubFile + ' (' + $requiredLines.Count + ' reconciled lines verbatim; no stale ' + ($forbidden -join '/') + ' language outside an explicit retirement statement; names ' + ($required -join ', ') + ')'
exit 0
