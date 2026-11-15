# Framework small syncs fresh-full gate (task H1-2; implementation-plan.md §Session gate).
# The peer's shape (docs/execution/plans/2026-11-15-hdp-expert-pass/session-gate.ps1), with this
# plan's steps: tools-lint and py-lint, the task contract, scope-paths (S4), port-check (AC-7 to
# AC-9), script-check (AC-19), the red-check selftest, the strip and identity tests with -rs
# (AC-1 to AC-6, AC-11 to AC-18), the adoption tests (AC-10), the full Python suite, the state
# render, the closeout validator's selftest and the live identity check (AC-20).
# Runs from the repository root (P:/av-kit, main only per AGENTS.md §Commits) in stage order:
# input identity, then every static check, then the targeted checks, then the full suites, then
# the input identity again. One receipt per id under C:/Temp/av-kit/fs, named fs-D6-<id>.txt.
# Fail-fast: the first non-zero step stops the gate and every later step is printed as not_run.
# The gate also fails when tested_state differs between its start and its end (an input changed
# while it ran). Read-only apart from the receipts and the temp folders, which sit outside the
# repository. Nothing here reaches the network or YouTube, and no step dispatches a model.
# Exit = the first failing step's code.
# tools-lint ignores E501 in STRIP only: STRIP is upstream's file byte for byte (AC-7), and its
# line 151 is 102 characters (D-894). CI does not lint that folder (ci.yml ruff step).
# strip-tests and identity-tests fail when their receipt shows a skip, so AC-18 must run.
# identity-live runs CHECKER twice (AC-20): with the real environment it must print ok, and with
# the synthetic --expected it must exit 1. Neither receipt may hold an address.
# py-tests runs the whole suite (no -x) and keeps Session 49b's baseline rule: pytest exit 1
# passes only when every FAILED id also FAILED in row 0's fs-base-py.txt, and nothing ERRORs.
# Skipped, per the plan: py-types (nothing under packages/ changes), ui-* (nothing under ui/
# changes), mcp-* (no MCP change), openapi (no packages/api change; H1-4) and build-record (no
# build). Each is printed with its reason and runs nothing.
$ErrorActionPreference = 'Continue'
$root = (git rev-parse --show-toplevel).Trim()
Set-Location $root
$plan = 'docs/execution/plans/2026-11-15-framework-small-syncs'
$receipts = 'C:/Temp/av-kit/fs'
# lint_task_contract.py recognises the instantiated receipt paths only through RECEIPTS_DIR and
# fails closed (exit 3) when it is unset, which no user or machine scope sets on this host.
$env:RECEIPTS_DIR = 'C:/Temp/av-kit'
$env:PYTHONIOENCODING = 'utf-8'
$env:ELECTRON_RUN_AS_NODE = $null
# The adoption tests read the shared registry home (memory: codex-dispatch-registry-home).
$env:AGENT_MODEL_REGISTRY_HOME = 'P:/.agent'
# RC1 ECN-2 (CLOSEOUT-SELFTEST-ANCESTOR-AGENT-DIR): keep pytest's temp dirs away from the home folder.
$tmp = 'C:\Temp\av-kit\fs\tmp'
New-Item -ItemType Directory -Force -Path $tmp | Out-Null
$env:TMP = $tmp
$env:TEMP = $tmp

# An id is excused only when row 0's baseline receipt really shows it FAILED: a missing
# receipt excuses nothing.
$baseReceipt = "$receipts/fs-base-py.txt"
$baselinePyFailed = @()
if (Test-Path $baseReceipt) {
    $baselinePyFailed = @(Select-String -Path $baseReceipt -Pattern '^FAILED (\S+)' | ForEach-Object { $_.Matches[0].Groups[1].Value })
}
Write-Output ("baseline py failures excused: {0} id(s) (receipt {1})" -f $baselinePyFailed.Count, $baseReceipt)

$skipped = @(
    @{ Id = 'py-types'; Stage = 'static'; Reason = 'pyright packages/: nothing under packages/ changes' },
    @{ Id = 'ui-types/ui-lint/ui-tests/ui-build/ui-electron'; Stage = 'full'; Reason = 'nothing under ui/ changes' },
    @{ Id = 'mcp-types/mcp-build/mcp-tests/mcp-audit'; Stage = 'full'; Reason = 'no MCP change' },
    @{ Id = 'openapi'; Stage = 'full'; Reason = 'no packages/api change (H1-4)' },
    @{ Id = 'build-record'; Stage = 'full'; Reason = 'no build' }
)
foreach ($s in $skipped) {
    Write-Output ("{0} stage={1} skipped reason={2}" -f $s.Id, $s.Stage, $s.Reason)
}

$py = @('uv', 'run', '--no-sync', 'python')
$identity = $py + @("$plan/identity.py")
$strip = '.agent/skills/deep-research-prompting/scripts/strip_embedded_images.py'
$checker = 'tools/check_commit_identity.py'
$synthetic = '100+fixture@users.noreply.github.com'
$steps = @(
    @{ Id = 'identity-before'; Stage = 'identity'; Argv = $identity },
    @{ Id = 'tools-lint'; Stage = 'static'; Argv = @('uv', 'run', '--no-sync', 'ruff', 'check', '--per-file-ignores', "${strip}:E501", $checker, 'tests/tooling/', '.agent/skills/deep-research-prompting/scripts/') },
    @{ Id = 'py-lint'; Stage = 'static'; Argv = @('uv', 'run', '--no-sync', 'ruff', 'check', 'packages/', 'tests/') },
    @{ Id = 'task-contract'; Stage = 'static'; Argv = $py + @('tools/lint_task_contract.py', '--allowed-builder-classes', 'avkit_builder,avkit_coordinator,avkit_verifier', '--task', "$plan/task.md") },
    @{ Id = 'scope-paths'; Stage = 'static'; Argv = $py + @("$plan/scope-check.py") },
    @{ Id = 'port-check'; Stage = 'static'; Argv = $py + @("$plan/port-check.py") },
    @{ Id = 'script-check'; Stage = 'static'; Argv = $py + @("$plan/script-check.py") },
    @{ Id = 'red-check-selftest'; Stage = 'static'; Argv = $py + @("$plan/red-check.py", '--selftest') },
    @{ Id = 'strip-tests'; Stage = 'targeted'; Argv = @('uv', 'run', '--no-sync', 'pytest', 'tests/tooling/test_strip_embedded_images.py', '--tb=short', '-q', '-rs') },
    @{ Id = 'identity-tests'; Stage = 'targeted'; Argv = @('uv', 'run', '--no-sync', 'pytest', 'tests/tooling/test_check_commit_identity.py', '--tb=short', '-q', '-rs') },
    @{ Id = 'adoption-tests'; Stage = 'targeted'; Argv = @('uv', 'run', '--no-sync', 'pytest', 'tests/tooling/test_framework_adoption.py', '--tb=short', '-q') },
    @{ Id = 'py-tests'; Stage = 'full'; Argv = @('uv', 'run', '--no-sync', 'pytest', 'tests/', '--tb=short', '-q', '-rfE') },
    @{ Id = 'state-render'; Stage = 'full'; Argv = $py + @('tools/meu_status.py', 'render', '--check') },
    @{ Id = 'closeout-selftest'; Stage = 'full'; Argv = $py + @('tools/validate_closeout_artifacts.py', '--selftest') },
    @{ Id = 'identity-live'; Stage = 'full'; Argv = $py + @($checker) },
    @{ Id = 'identity-after'; Stage = 'identity'; Argv = $identity }
)

function Get-TestedState([string]$Receipt) {
    $line = Select-String -Path $Receipt -Pattern '^tested_state ' | Select-Object -Last 1
    if ($null -eq $line) { return $null }
    return $line.Line.Substring('tested_state '.Length).Trim()
}

for ($i = 0; $i -lt $steps.Count; $i++) {
    $step = $steps[$i]
    $receipt = "$receipts/fs-D6-$($step.Id).txt"
    $argv = $step.Argv
    & rtk proxy @argv *> $receipt
    $code = $LASTEXITCODE
    Write-Output ("{0} stage={1} exit={2} receipt={3}" -f $step.Id, $step.Stage, $code, $receipt)
    Get-Content $receipt | Select-Object -Last 6
    if ($code -eq 1 -and $step.Id -eq 'py-tests') {
        $failed = @(Select-String -Path $receipt -Pattern '^FAILED (\S+)' | ForEach-Object { $_.Matches[0].Groups[1].Value } | Sort-Object -Unique)
        $errored = @(Select-String -Path $receipt -Pattern '^ERROR ')
        $outside = @($failed | Where-Object { $baselinePyFailed -notcontains $_ })
        Write-Output ("py-tests baseline rule: failed={0} outside_baseline=[{1}] errors={2}" -f $failed.Count, ($outside -join ', '), $errored.Count)
        if ($failed.Count -gt 0 -and $outside.Count -eq 0 -and $errored.Count -eq 0) {
            Write-Output 'py-tests: every failure is in the row 0 baseline failed set; not a regression'
            $code = 0
        }
    }
    if ($code -eq 0 -and $step.Id -in @('strip-tests', 'identity-tests')) {
        if (Select-String -Path $receipt -Pattern 'SKIPPED' -SimpleMatch -Quiet) {
            Write-Output "$($step.Id): the receipt shows a skipped test; every case must run"
            $code = 1
        }
    }
    if ($code -eq 0 -and $step.Id -eq 'closeout-selftest') {
        if (-not (Select-String -Path $receipt -Pattern ' 0 failure' -Quiet)) {
            Write-Output 'closeout-selftest: the receipt does not report 0 failures'
            $code = 1
        }
    }
    if ($code -eq 0 -and $step.Id -eq 'identity-live') {
        $negReceipt = "$receipts/fs-D6-identity-live-neg.txt"
        $negArgv = $py + @($checker, '--expected', $synthetic)
        & rtk proxy @negArgv *> $negReceipt
        $neg = $LASTEXITCODE
        Write-Output ("identity-live-neg exit={0} receipt={1}" -f $neg, $negReceipt)
        Get-Content $negReceipt | Select-Object -Last 6
        if (-not (Select-String -Path $receipt -Pattern 'check_commit_identity: ok' -SimpleMatch -Quiet)) {
            Write-Output 'identity-live: the real environment did not print ok'
            $code = 1
        }
        elseif ($neg -ne 1) {
            Write-Output 'identity-live: the synthetic --expected run was not refused with exit 1'
            $code = 1
        }
        elseif (Select-String -Path $receipt, $negReceipt -Pattern '@' -SimpleMatch -Quiet) {
            Write-Output 'identity-live: an address reached a receipt'
            $code = 1
        }
    }
    if ($code -eq 0 -and $step.Id -eq 'identity-after') {
        $before = Get-TestedState "$receipts/fs-D6-identity-before.txt"
        $after = Get-TestedState $receipt
        Write-Output "tested_state before=$before after=$after"
        if ([string]::IsNullOrEmpty($before) -or $before -ne $after) {
            Write-Output 'identity-after: tested_state changed while the gate ran; the gate is not fresh'
            $code = 1
        }
    }
    if ($code -ne 0) {
        for ($j = $i + 1; $j -lt $steps.Count; $j++) {
            Write-Output ("{0} stage={1} not_run reason=fail-fast after {2}" -f $steps[$j].Id, $steps[$j].Stage, $step.Id)
        }
        exit $code
    }
}
Write-Output 'session-gate: all steps exit 0'
exit 0
