# Session 49b baseline (task row 0; implementation-plan.md §Verification Plan 1).
# Records HEAD and the dirty tree, checks the register is the one the plan measured, installs
# from the lock and captures the base Python suite. The base suite's own failures are recorded,
# not fatal: the session gate excuses only the ids this receipt shows failing. DONE_PROOF must
# fail today (AC-11 Red). Every other step is fail-fast. Run from the repository root.
$ErrorActionPreference = 'Stop'
$root = (git rev-parse --show-toplevel).Trim()
Set-Location $root
$plan = 'docs/execution/plans/2026-11-05-closeout-register-grammar'
$receipts = 'C:/Temp/av-kit'
$register = '.agent/context/known-issues.yaml'
$registerSha = '900b2cb05e7266fad83f329e555f1da135f6268da39662a80dc35f60a12d8fe4'
$env:ELECTRON_RUN_AS_NODE = $null
# RC1 ECN-2 (CLOSEOUT-SELFTEST-ANCESTOR-AGENT-DIR): keep pytest's temp dirs away from C:/Users/Mat/.agent.
$tmp = "$receipts/s49b/tmp"
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

$sha = (Get-FileHash -Algorithm SHA256 -LiteralPath $register).Hash.ToLowerInvariant()
Write-Output "register sha256 $sha"
if ($sha -ne $registerSha) { Write-Output "register sha256 mismatch, expected $registerSha (S4)"; exit 10 }

Invoke-Step 'uv-sync' @('uv', 'sync', '--frozen', '--all-packages')

& rtk proxy uv run pytest tests/ --tb=short -q -rfE *> "$receipts/s49b-base-py.txt"
Write-Output ("base suite py exit={0} receipt={1}/s49b-base-py.txt" -f $LASTEXITCODE, $receipts)
Get-Content "$receipts/s49b-base-py.txt" | Select-String -Pattern '^FAILED |^ERROR |passed|failed' | Select-Object -Last 12

# DONE_PROOF as it stands (task row 6's command): AC-11's Red.
$doneProof = @(
    'uv', 'run', 'python', 'tools/validate_closeout_artifacts.py',
    '--reflection', 'docs/execution/reflections/2026-11-04-rc2-fetch-uninstall-reflection.md',
    '--reflection-template', 'docs/execution/reflections/TEMPLATE.md',
    '--reflection-schema', '.agent/schemas/reflection.v1.yaml',
    '--decision-source', 'docs/execution/plans/2026-11-04-rc2-fetch-uninstall/implementation-plan.md',
    '--decision-source', '.agent/context/handoffs/2026-11-04-rc2-fetch-uninstall-MEU-113-handoff.md',
    '--decision-source', '.agent/context/handoffs/2026-11-04-rc2-fetch-uninstall-MEU-114-handoff.md',
    '--decision-source', '.agent/context/grouping/2026-11-04-rc2-triage-residuals-session-grouping.md',
    '--decision-source', $register,
    '--decision-issue', 'UNINSTALL-LEAVES-INSTALLER-COPY',
    '--decision-issue', 'FFMPEG-LIBDVDCSS-BUNDLED'
)
& rtk proxy @doneProof *> "$receipts/s49b-done-proof-red.txt"
$code = $LASTEXITCODE
Set-Content -Path "$receipts/s49b-done-proof-red.txt.exit" -Value $code
Get-Content "$receipts/s49b-done-proof-red.txt" -Tail 6
Write-Output "done-proof red exit=$code"
if ($code -ne 1) { Write-Output 'done-proof red: expected exit 1'; exit 11 }
if (-not (Select-String -Path "$receipts/s49b-done-proof-red.txt" -Pattern 'is not valid YAML' -Quiet)) {
    Write-Output 'done-proof red: expected "is not valid YAML"'; exit 12
}

Invoke-Step 'red-check-selftest' @('uv', 'run', 'python', "$plan/red-check.py", '--selftest')
Invoke-Step 'identity-selftest' @('uv', 'run', 'python', "$plan/identity.py", '--selftest')
Write-Output 'baseline: all steps exit 0'
exit 0
