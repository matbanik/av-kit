# HDP v2 protocol fresh-full gate (task H1-2; implementation-plan.md §Session gate).
# The peer's shape (docs/execution/plans/2026-11-14-review-limits-no-token-budget/session-gate.ps1),
# with this plan's steps: tools-lint on the plan-local scripts, the task contract on this task.md
# and on the task template, scope-paths (scope-check.py --check), the oracle with its binding and
# evidence (AC-1 to AC-19), the plan-local selftests, the adoption tests, the closeout validator's
# selftest, the full Python suite and the state render.
# Runs from the repository root (P:/av-kit, main only per AGENTS.md §Commits) in stage order:
# input identity, then every static check, then the targeted checks, then the full suites, then
# the input identity again. One receipt per id under C:/Temp/av-kit/hdp85, named hdp-D6-<id>.txt.
# Fail-fast: the first non-zero step stops the gate and every later step is printed as not_run.
# The gate also fails when tested_state differs between its start and its end (an input changed
# while it ran). Read-only apart from the receipts and the temp folder, which sit outside the
# repository. Nothing here reaches the network or YouTube, and no step dispatches a model.
# Exit = the first failing step's code.
# py-tests runs the whole suite (no -x): pytest exit 1 passes only when every FAILED id also
# FAILED in row 0's hdp-base-py.txt, and nothing ERRORs.
# Skipped, per the plan: py-lint and py-types (nothing under packages/ or tests/ changes), ui-*
# (nothing under ui/ changes), mcp-* (no MCP change), openapi (no packages/api change; H1-4) and
# build-record (no build). Each is printed with its reason and runs nothing.
$ErrorActionPreference = 'Continue'
$root = (git rev-parse --show-toplevel).Trim()
Set-Location $root
$plan = 'docs/execution/plans/2026-11-15-hdp-v2-protocol'
$receipts = 'C:/Temp/av-kit/hdp85'
# lint_task_contract.py recognises the instantiated receipt paths only through RECEIPTS_DIR and
# fails closed (exit 3) when it is unset.
$env:RECEIPTS_DIR = 'C:/Temp/av-kit'
$env:PYTHONIOENCODING = 'utf-8'
$env:ELECTRON_RUN_AS_NODE = $null
# RC1 ECN-2 (CLOSEOUT-SELFTEST-ANCESTOR-AGENT-DIR): keep pytest's temp dirs away from the home
# folder, as row 0 ran the base suite.
$tmp = 'C:\Temp\av-kit\hdp85\tmp'
New-Item -ItemType Directory -Force -Path $tmp | Out-Null
$env:TMP = $tmp
$env:TEMP = $tmp

# An id is excused only when row 0's baseline receipt really shows it FAILED: a missing
# receipt excuses nothing.
$baseReceipt = "$receipts/hdp-base-py.txt"
$baselinePyFailed = @()
if (Test-Path $baseReceipt) {
    $baselinePyFailed = @(Select-String -Path $baseReceipt -Pattern '^FAILED (\S+)' | ForEach-Object { $_.Matches[0].Groups[1].Value })
}
Write-Output ("baseline py failures excused: {0} id(s) (receipt {1})" -f $baselinePyFailed.Count, $baseReceipt)

$skipped = @(
    @{ Id = 'py-lint/py-types'; Stage = 'static'; Reason = 'nothing under packages/ or tests/ changes' },
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
$builders = 'avkit_builder,avkit_coordinator,avkit_verifier'
$steps = @(
    @{ Id = 'identity-before'; Stage = 'identity'; Argv = $identity },
    @{ Id = 'tools-lint'; Stage = 'static'; Argv = @('uv', 'run', '--no-sync', 'ruff', 'check', "$plan/hdp-check.py", "$plan/scope-check.py", "$plan/s84-landed.py") },
    @{ Id = 'task-contract'; Stage = 'static'; Argv = $py + @('tools/lint_task_contract.py', '--allowed-builder-classes', $builders, '--task', "$plan/task.md") },
    # D-857: the template-mode lint takes the same builder classes as the peer gates.
    @{ Id = 'task-template'; Stage = 'static'; Argv = $py + @('tools/lint_task_contract.py', '--allowed-builder-classes', $builders, '--task', '.agent/templates/TASK-TEMPLATE.md', '--template-mode') },
    @{ Id = 'scope-paths'; Stage = 'static'; Argv = $py + @("$plan/scope-check.py", '--check') },
    @{ Id = 'hdp-check'; Stage = 'static'; Argv = $py + @("$plan/hdp-check.py", '--eol-baseline', "$plan/eol-baseline.json", '--binding', "$plan/validator-binding.json", '--evidence-receipt', "$receipts/hdp-base-closeout-selftest.txt", '--evidence-receipt', "$receipts/hdp-base-s84-tests.txt") },
    @{ Id = 'hdp-check-selftest'; Stage = 'static'; Argv = $py + @("$plan/hdp-check.py", '--selftest') },
    @{ Id = 'scope-check-selftest'; Stage = 'static'; Argv = $py + @("$plan/scope-check.py", '--selftest') },
    @{ Id = 's84-landed-selftest'; Stage = 'static'; Argv = $py + @("$plan/s84-landed.py", '--selftest') },
    @{ Id = 'adoption'; Stage = 'targeted'; Argv = @('uv', 'run', '--no-sync', 'pytest', 'tests/tooling/test_framework_adoption.py', '--tb=short', '-q') },
    @{ Id = 'closeout-selftest'; Stage = 'targeted'; Argv = $py + @('tools/validate_closeout_artifacts.py', '--selftest') },
    @{ Id = 'py-tests'; Stage = 'full'; Argv = @('uv', 'run', '--no-sync', 'pytest', 'tests/', '--tb=short', '-q', '-rfE') },
    @{ Id = 'state-render'; Stage = 'full'; Argv = $py + @('tools/meu_status.py', 'render', '--check') },
    @{ Id = 'identity-after'; Stage = 'identity'; Argv = $identity }
)

function Get-TestedState([string]$Receipt) {
    $line = Select-String -Path $Receipt -Pattern '^tested_state ' | Select-Object -Last 1
    if ($null -eq $line) { return $null }
    return $line.Line.Substring('tested_state '.Length).Trim()
}

for ($i = 0; $i -lt $steps.Count; $i++) {
    $step = $steps[$i]
    $receipt = "$receipts/hdp-D6-$($step.Id).txt"
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
    if ($code -eq 0 -and $step.Id -eq 'closeout-selftest') {
        if (-not (Select-String -Path $receipt -Pattern ' 0 failure' -Quiet)) {
            Write-Output 'closeout-selftest: the receipt does not report 0 failures'
            $code = 1
        }
    }
    if ($code -eq 0 -and $step.Id -eq 'identity-after') {
        $before = Get-TestedState "$receipts/hdp-D6-identity-before.txt"
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
