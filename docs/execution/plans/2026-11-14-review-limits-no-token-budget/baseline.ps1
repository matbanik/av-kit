# Review-limits baseline (task row 0; implementation-plan.md §Verification Plan 1).
# Records HEAD and the dirty tree, checks the ledger is HEAD's, records the selftest's arm names,
# installs from the lock, captures the base Python suite and the dispatch suite, then runs the
# five plan-local selftests. The base Python suite's own failures are recorded, not fatal: the
# session gate excuses only the ids this receipt shows failing. The dispatch suite fails today on
# the two baseline ids (D-739); dispatch-check.py --exact-baseline requires exactly that pair.
# Every other step is fail-fast. Run from the repository root.
$ErrorActionPreference = 'Stop'
$root = (git rev-parse --show-toplevel).Trim()
Set-Location $root
$plan = 'docs/execution/plans/2026-11-14-review-limits-no-token-budget'
$receipts = 'C:/Temp/av-kit/rl'
$ledger = 'tools/review_ledger.py'
$env:ELECTRON_RUN_AS_NODE = $null
# The dispatch suite loads ModelRegistry.psm1 from the shared registry home (memory: codex-dispatch-registry-home).
$env:AGENT_MODEL_REGISTRY_HOME = 'P:/.agent'
# RC1 ECN-2 (CLOSEOUT-SELFTEST-ANCESTOR-AGENT-DIR): keep pytest's temp dirs away from C:/Users/Mat/.agent.
$tmp = "$receipts/tmp"
$userTmp = $env:TMP
$userTemp = $env:TEMP
New-Item -ItemType Directory -Force -Path $tmp | Out-Null
$env:TMP = $tmp
$env:TEMP = $tmp

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

# The ledger must be HEAD's. The blob is LF and the work-tree copy CRLF (text=auto), so the
# work-tree bytes are compared with their CRLF read as LF; both hashes are printed.
$ledgerCheck = @'
import hashlib, subprocess, sys
work = open(sys.argv[1], "rb").read()
blob = subprocess.run(["git", "show", "HEAD:" + sys.argv[1]], capture_output=True, check=True).stdout
print("ledger work-tree sha256", hashlib.sha256(work).hexdigest(), "crlf", work.count(b"\r\n"), "bare-lf", work.count(b"\n") - work.count(b"\r\n"))
print("ledger HEAD blob sha256", hashlib.sha256(blob).hexdigest())
same = work.replace(b"\r\n", b"\n") == blob
print("ledger equals HEAD (CRLF read as LF):", same)
sys.exit(0 if same else 10)
'@
Set-Content -Path "$receipts/ledger-equals-head.py" -Value $ledgerCheck -Encoding utf8
Invoke-Step 'ledger-equals-head' @('uv', 'run', 'python', "$receipts/ledger-equals-head.py", $ledger)

& rtk proxy uv run python $ledger selftest *> "$receipts/rl-base-selftest.txt"
$code = $LASTEXITCODE
Get-Content "$receipts/rl-base-selftest.txt" -Tail 2
Write-Output "baseline step ledger-selftest exit=$code"
if ($code -ne 0) { exit $code }
Invoke-Step 'arms-before' @('uv', 'run', 'python', "$plan/selftest-arms-check.py", '--write-before', "$plan/selftest-arms-before.txt", "$receipts/rl-base-selftest.txt")
$arms = (Get-Content "$plan/selftest-arms-before.txt").Count
Write-Output "selftest-arms-before.txt $arms arm(s)"
if ($arms -ne 105) { Write-Output 'expected 105 arms, the plan-time count'; exit 11 }

Invoke-Step 'uv-sync' @('uv', 'sync', '--frozen', '--all-packages')

& rtk proxy uv run pytest tests/ --tb=short -q -rfE *> "$receipts/rl-base-py.txt"
Write-Output ("base suite py exit={0} receipt={1}/rl-base-py.txt" -f $LASTEXITCODE, $receipts)
Get-Content "$receipts/rl-base-py.txt" | Select-String -Pattern '^FAILED |^ERROR |passed|failed' | Select-Object -Last 12

# The dispatch suite runs with the user's own TMP and TEMP, as row 8 and the gate run it: under the
# pytest temp root its temp wrapper copy resolves the avkit_* class aliases differently and fails.
$env:TMP = $userTmp
$env:TEMP = $userTemp
[Environment]::SetEnvironmentVariable('RECEIPTS_DIR', (Split-Path -Parent 'C:/Temp/av-kit/dispatch'))
& rtk proxy pwsh -NoProfile -File .agent/skills/cli-dispatch/tests/Test-CliDispatch.ps1 *> "$receipts/rl-base-dispatch.txt"
Set-Content -Path "$receipts/rl-base-dispatch.txt.exit" -Value $LASTEXITCODE
Get-Content "$receipts/rl-base-dispatch.txt" -Tail 3
Invoke-Step 'dispatch-baseline' @('uv', 'run', 'python', "$plan/dispatch-check.py", '--exact-baseline', '--exit-file', "$receipts/rl-base-dispatch.txt.exit", "$receipts/rl-base-dispatch.txt")

Invoke-Step 'red-check-selftest' @('uv', 'run', 'python', "$plan/red-check.py", '--selftest')
Invoke-Step 'identity-selftest' @('uv', 'run', 'python', "$plan/identity.py", '--selftest')
Invoke-Step 'prose-check-selftest' @('uv', 'run', 'python', "$plan/prose-check.py", '--selftest')
Invoke-Step 'arms-check-selftest' @('uv', 'run', 'python', "$plan/selftest-arms-check.py", '--selftest')
Invoke-Step 'dispatch-check-selftest' @('uv', 'run', 'python', "$plan/dispatch-check.py", '--selftest', '--base', "$receipts/rl-base-dispatch.txt")
Write-Output 'baseline: all steps exit 0'
exit 0
