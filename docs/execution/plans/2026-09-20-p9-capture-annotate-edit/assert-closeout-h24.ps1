# H2-4 closeout owner: markers + ACs + dispatch + exec-review + reflection + metrics + render.
$ErrorActionPreference = 'Stop'
$root = $PSScriptRoot
$sets = Get-Content -LiteralPath (Join-Path $root 'named-sets.json') -Raw | ConvertFrom-Json

& pwsh -NoProfile -File (Join-Path $root 'assert-handoff-markers.ps1')
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

& pwsh -NoProfile -File (Join-Path $root 'assert-handoff-acs.ps1')
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

& pwsh -NoProfile -File (Join-Path $root 'assert-exec-review-dispatch.ps1')
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

$review = [string]$sets.EXEC_REVIEW_FILE
$plan = [string]$sets.EXEC_REVIEW_TARGET
$max = [int]$sets.EXEC_REVIEW_MAX_ROUND
uv run python tools/check_exec_review.py --review-file $review --expected-mode implementation --expected-target $plan --max-round $max
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

$reflection = [string]$sets.REFLECTION_FILE
foreach ($pattern in @($sets.REFLECTION_MARKERS)) {
    if (-not (Select-String -Path $reflection -Pattern ([string]$pattern) -Quiet)) {
        Write-Error ('missing reflection marker ' + $pattern)
        exit 1
    }
}

if (-not (Select-String -Path 'docs/execution/metrics.md' -Pattern ([string]$sets.METRICS_SLUG) -Quiet)) {
    Write-Error 'missing metrics row'
    exit 1
}

uv run python tools/meu_status.py render --check
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

'PASS: H2-4 closeout'
exit 0
