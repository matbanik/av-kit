# Aggregate closeout gate (H2-4). Every constituent check is an on-disk executable in this
# plan folder or tools/ - no phantom validator. Replaces the non-existent
# tools/validate_closeout_artifacts.py named in plan-review round 1, finding #2.
$ErrorActionPreference = 'Stop'
$root = $PSScriptRoot
$setsPath = Join-Path $root 'named-sets.json'
if (-not (Test-Path -LiteralPath $setsPath)) { Write-Error ('missing NAMED_SETS_FILE ' + $setsPath); exit 1 }
$sets = Get-Content -LiteralPath $setsPath -Raw | ConvertFrom-Json

function Invoke-Gate {
    param([string]$Name, [string]$Script, [string[]]$Arguments = @())
    $path = Join-Path $root $Script
    if (-not (Test-Path -LiteralPath $path)) { Write-Error ('missing gate script ' + $path); exit 1 }
    & pwsh -NoProfile -File $path @Arguments
    if ($LASTEXITCODE -ne 0) { Write-Error ($Name + ' failed with exit ' + $LASTEXITCODE); exit $LASTEXITCODE }
}

Invoke-Gate -Name 'ORACLE_SELFTESTS' -Script 'assert-oracle-selftests.ps1'
# Predecessor completeness only: H2-4 and the rows after it are open BY CONSTRUCTION while
# this gate runs (round-3 finding N1 - a zero-open-rows demand deadlocks the task table).
Invoke-Gate -Name 'TASK_ROW_GATE' -Script 'assert-task-rows.ps1' -Arguments @('-Through', ([string]$sets.ROW_BOUNDARY_CLOSEOUT))
Invoke-Gate -Name 'OVERLAY_DELETION' -Script 'assert-overlay-deleted.ps1'
Invoke-Gate -Name 'PACKAGING_CLEAN_PATH' -Script 'assert-packaging-clean.ps1' -Arguments @('-SkipBuild')
Invoke-Gate -Name 'E2E_WIRED' -Script 'assert-e2e-wired.ps1' -Arguments @('-Mode', 'Wired')
# Round-4 R4-3: wiring is not evidence of execution - the closeout also re-checks that the
# required capture cases actually ran green (Playwright JSON reporter receipt).
Invoke-Gate -Name 'E2E_EXECUTED' -Script 'assert-e2e-wired.ps1' -Arguments @('-Mode', 'Executed')
# Round-5 R5-1: the hub every agent reads first must not still describe the deleted Chromium
# design. This is a failing predicate, not the report-only audit the plan used to schedule.
Invoke-Gate -Name 'BUILD_PLAN_HUB' -Script 'assert-build-plan-hub.ps1'
Invoke-Gate -Name 'HANDOFF_MARKER_CHECK' -Script 'assert-handoff-markers.ps1'
Invoke-Gate -Name 'HANDOFF_AC_SET' -Script 'assert-handoff-acs.ps1'
Invoke-Gate -Name 'EXEC_REVIEW_DISPATCH' -Script 'assert-exec-review-dispatch.ps1'

# Independent reviewer verdict: live frontmatter only (tools/check_exec_review.py exists).
$reviewFile = [string]$sets.EXEC_REVIEW_FILE
$maxRound = [int]$sets.EXEC_REVIEW_MAX_ROUND
$target = [string]$sets.EXEC_REVIEW_TARGET
$mode = [string]$sets.EXEC_REVIEW_MODE
uv run python tools/check_exec_review.py --review-file $reviewFile --expected-mode $mode --expected-target $target --max-round $maxRound
if ($LASTEXITCODE -ne 0) { Write-Error ('CHECK_EXEC_REVIEW failed with exit ' + $LASTEXITCODE); exit $LASTEXITCODE }

# Reflection: exists and carries the Instruction Coverage YAML block AGENTS.md requires.
# Round-11 trim: the 306-line prose validator that used to adjudicate distinct-sentence ratios
# and placeholder wording is deleted. A human and the independent reviewer read the reflection;
# a regex cannot tell an honest one from a fluent one, and pretending otherwise cost more than it
# ever caught.
$reflection = [string]$sets.REFLECTION_FILE
if (-not (Test-Path -LiteralPath $reflection)) { Write-Error ('missing ' + $reflection); exit 1 }
if (-not (Select-String -LiteralPath $reflection -Pattern '```yaml' -SimpleMatch -Quiet)) {
    Write-Error ($reflection + ' has no fenced yaml block - the Instruction Coverage section is missing')
    exit 1
}

$metrics = 'docs/execution/metrics.md'
if (-not (Test-Path -LiteralPath $metrics)) { Write-Error ('missing ' + $metrics); exit 1 }
if (-not (Select-String -LiteralPath $metrics -Pattern ([string]$sets.METRICS_SLUG) -SimpleMatch -Quiet)) {
    Write-Error ('metrics.md has no row for ' + $sets.METRICS_SLUG)
    exit 1
}

# Registry drift.
uv run python tools/meu_status.py render --check
if ($LASTEXITCODE -ne 0) { Write-Error ('meu_status render --check failed with exit ' + $LASTEXITCODE); exit $LASTEXITCODE }

'PASS: CLOSEOUT_GATE'
exit 0
