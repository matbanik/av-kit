# HDP v2 protocol baseline (task row 0; implementation-plan.md §Verification Plan 1).
# Records HEAD and the dirty tree; proves Session 84 has landed (s84-landed.py, S2); proves every file this
# session edits still equals base 6813232 and records the dirty paths' and the validator's hashes
# (scope-check.py --record, S3); snapshots the edited files' work-tree line endings for C6; captures
# the closeout selftest and the Session 84 tests verbosely as the C11 evidence; installs from the
# lock; captures the base Python suite; runs the plan-local selftests and the oracle's Red run.
# The base Python suite's own failures are recorded, not fatal. The Red run must fail (exit 1).
# Every other step is fail-fast. Run from the repository root.
$ErrorActionPreference = 'Stop'
$root = (git rev-parse --show-toplevel).Trim()
Set-Location $root
$plan = 'docs/execution/plans/2026-11-15-hdp-v2-protocol'
$receipts = 'C:/Temp/av-kit/hdp85'
$validator = 'tools/validate_closeout_artifacts.py'
$env:ELECTRON_RUN_AS_NODE = $null
$env:PYTHONIOENCODING = 'utf-8'
$env:RECEIPTS_DIR = 'C:/Temp/av-kit'
$userTmp = $env:TMP
$userTemp = $env:TEMP
$tmp = "$receipts/tmp"
New-Item -ItemType Directory -Force -Path $tmp | Out-Null

function Invoke-Step([string]$Id, [string[]]$Argv) {
    & rtk proxy @Argv
    $code = $LASTEXITCODE
    Write-Output ("baseline step {0} exit={1}" -f $Id, $code)
    if ($code -ne 0) { exit $code }
}

$head = (git rev-parse HEAD).Trim()
Set-Content -Path "$plan/baseline.sha" -Value $head -NoNewline
git status --porcelain --untracked-files=all | Set-Content -Path "$plan/baseline-dirty.txt"
Write-Output "baseline.sha $head"
Write-Output ("baseline-dirty.txt {0} paths" -f (Get-Content "$plan/baseline-dirty.txt").Count)

# S2: Session 84 has landed (s84-landed.py). Session 84's own read-only port-check.py finds
# its port shape and line endings in the validator, every Session 84 task row is [x], and its
# handoff and reflection exist. Any problem exits 12.
Invoke-Step 's84-landed' @('uv', 'run', 'python', "$plan/s84-landed.py")

# S3 and the S4 record: the edited files equal base; the dirty paths' and the validator's hashes.
Invoke-Step 'scope-record' @('uv', 'run', 'python', "$plan/scope-check.py", '--record')

# C6's baseline: the edited files' work-tree line endings, taken before any edit.
Invoke-Step 'eol-snapshot' @('uv', 'run', 'python', "$plan/hdp-check.py", '--eol-snapshot', "$plan/eol-baseline.json")

# C11's evidence: the landed validator's selftest arm names and the Session 84 test ids.
& rtk proxy uv run python $validator --selftest *> "$receipts/hdp-base-closeout-selftest.txt"
$code = $LASTEXITCODE
Get-Content "$receipts/hdp-base-closeout-selftest.txt" -Tail 2
Write-Output "baseline step closeout-selftest exit=$code"
if ($code -ne 0) { Write-Output 'the landed validator selftest fails (S2)'; exit $code }
if (-not (Select-String -Path "$receipts/hdp-base-closeout-selftest.txt" -Pattern ' 0 failure' -Quiet)) { Write-Output 'closeout selftest did not report 0 failures (S2)'; exit 12 }
& rtk proxy uv run pytest -v tests/tooling/test_closeout_record_once.py tests/tooling/test_closeout_register_grammar.py --tb=short *> "$receipts/hdp-base-s84-tests.txt"
$code = $LASTEXITCODE
Get-Content "$receipts/hdp-base-s84-tests.txt" -Tail 2
Write-Output "baseline step s84-tests exit=$code"
if ($code -ne 0) { Write-Output 'the Session 84 tests fail (S2)'; exit $code }

Invoke-Step 'uv-sync' @('uv', 'sync', '--frozen', '--all-packages')

$env:TMP = $tmp
$env:TEMP = $tmp
& rtk proxy uv run pytest tests/ --tb=short -q -rfE *> "$receipts/hdp-base-py.txt"
Write-Output ("base suite py exit={0} receipt={1}/hdp-base-py.txt" -f $LASTEXITCODE, $receipts)
Get-Content "$receipts/hdp-base-py.txt" | Select-String -Pattern '^FAILED |^ERROR |passed|failed' | Select-Object -Last 12
$env:TMP = $userTmp
$env:TEMP = $userTemp

Invoke-Step 'state-render-check' @('uv', 'run', 'python', 'tools/meu_status.py', 'render', '--check')
Invoke-Step 'identity-selftest' @('uv', 'run', 'python', "$plan/identity.py", '--selftest')
Invoke-Step 'scope-check-selftest' @('uv', 'run', 'python', "$plan/scope-check.py", '--selftest')
Invoke-Step 's84-landed-selftest' @('uv', 'run', 'python', "$plan/s84-landed.py", '--selftest')
Invoke-Step 'hdp-check-selftest' @('uv', 'run', 'python', "$plan/hdp-check.py", '--selftest')

# The Red run: the oracle on the unedited tree must fail. At plan time C1 to C4 fail (131), and
# C11 refuses because the binding is written only in row 1.
& rtk proxy uv run python "$plan/hdp-check.py" --eol-baseline "$plan/eol-baseline.json" *> "$receipts/hdp-red.txt"
$code = $LASTEXITCODE
Get-Content "$receipts/hdp-red.txt" -Tail 12
Write-Output "baseline step hdp-red exit=$code (must be 1)"
if ($code -ne 1) { exit 13 }
Write-Output 'baseline: all steps as expected'
exit 0
