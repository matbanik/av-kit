# Docs path hygiene fresh-full gate (task H1-2; implementation-plan.md §Session gate).
# The shape of docs/execution/plans/2026-11-15-framework-small-syncs/session-gate.ps1, with this
# plan's steps: tools-lint and py-lint, the task contract, scope-paths (S4), home-path (the new D6
# row) and inventory-check (AC-21), edit-check for all four groups, the red-check selftest,
# ui-types and ui-lint; then home-path-tests with -rs (AC-1 to AC-7, AC-22, AC-23), ui-targeted
# (AC-15, AC-16) and the adoption tests (AC-19); then the full Python and Vitest suites, the state
# and register renders and the closeout validator's selftest.
# Runs from the repository root (P:/av-kit, main only per AGENTS.md §Commits) in stage order:
# input identity, then every static check, then the targeted checks, then the full suites, then
# the input identity again. One receipt per id under C:/Temp/av-kit/dph, named dph-D6-<id>.txt.
# Fail-fast: the first non-zero step stops the gate and every later step is printed as not_run.
# The gate also fails when tested_state differs between its start and its end (an input changed
# while it ran). Read-only apart from the receipts and the temp folders, which sit outside the
# repository. Nothing here reaches the network or YouTube, and no step dispatches a model.
# Exit = the first failing step's code.
# edit-check runs the register group at stage 10, the register's final state for this session.
# home-path-tests fails when its receipt shows a skip, so every case must run.
# py-tests and ui-tests run the whole suites (no -x) and keep Session 49b's baseline rule: a
# suite's exit 1 passes only when every failing id also failed in row 0's receipt
# (dph-base-py.txt, dph-base-ui-full.txt), and pytest shows no ERROR. A missing receipt excuses
# nothing.
# The ui-* steps run in ui/ from pwsh with the user's TMP and TEMP, as row 0's baseline ran them;
# the Python steps run with TMP and TEMP in the dph tmp folder.
# Skipped, per the plan: py-types (nothing under packages/ changes), ui-build and ui-electron
# (only two unit-test files change under ui/, no source), mcp-* (no MCP change), openapi (no
# packages/api change; H1-4) and build-record (no build). Each is printed with its reason and
# runs nothing.
$ErrorActionPreference = 'Continue'
$root = (git rev-parse --show-toplevel).Trim()
Set-Location $root
$plan = 'docs/execution/plans/2026-11-15-docs-path-hygiene'
$receipts = 'C:/Temp/av-kit/dph'
# lint_task_contract.py recognises the instantiated receipt paths only through RECEIPTS_DIR and
# fails closed (exit 3) when it is unset, which no user or machine scope sets on this host.
$env:RECEIPTS_DIR = 'C:/Temp/av-kit'
$env:PYTHONIOENCODING = 'utf-8'
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:ELECTRON_RUN_AS_NODE = $null
# The adoption tests read the shared registry home (memory: codex-dispatch-registry-home).
$env:AGENT_MODEL_REGISTRY_HOME = 'P:/.agent'
$userTmp = $env:TMP
$userTemp = $env:TEMP
# RC1 ECN-2 (CLOSEOUT-SELFTEST-ANCESTOR-AGENT-DIR): keep pytest's temp dirs away from the home folder.
$tmp = 'C:\Temp\av-kit\dph\tmp'
New-Item -ItemType Directory -Force -Path $tmp | Out-Null

# An id is excused only when row 0's baseline receipt really shows it failing.
$basePy = "$receipts/dph-base-py.txt"
$baselinePyFailed = @()
if (Test-Path $basePy) {
    $baselinePyFailed = @(Select-String -Path $basePy -Pattern '^FAILED (\S+)' | ForEach-Object { $_.Matches[0].Groups[1].Value })
}
Write-Output ("baseline py failures excused: {0} id(s) (receipt {1})" -f $baselinePyFailed.Count, $basePy)
# Vitest marks a failing file FAIL and a failing test with U+00D7 (kept out of this file's bytes).
$uiFailPattern = '^\s*(?:FAIL|' + [char]0x00D7 + ')\s+(.+?)\s*$'
$baseUi = "$receipts/dph-base-ui-full.txt"
$baselineUiFailed = @()
if (Test-Path $baseUi) {
    $baselineUiFailed = @(Select-String -Path $baseUi -Pattern $uiFailPattern | ForEach-Object { $_.Matches[0].Groups[1].Value })
}
Write-Output ("baseline ui failures excused: {0} id(s) (receipt {1})" -f $baselineUiFailed.Count, $baseUi)

$skipped = @(
    @{ Id = 'py-types'; Stage = 'static'; Reason = 'pyright packages/: nothing under packages/ changes' },
    @{ Id = 'ui-build/ui-electron'; Stage = 'full'; Reason = 'only two unit-test files change under ui/, no source' },
    @{ Id = 'mcp-types/mcp-build/mcp-tests/mcp-audit'; Stage = 'full'; Reason = 'no MCP change' },
    @{ Id = 'openapi'; Stage = 'full'; Reason = 'no packages/api change (H1-4)' },
    @{ Id = 'build-record'; Stage = 'full'; Reason = 'no build' }
)
foreach ($s in $skipped) {
    Write-Output ("{0} stage={1} skipped reason={2}" -f $s.Id, $s.Stage, $s.Reason)
}

$py = @('uv', 'run', '--no-sync', 'python')
$identity = $py + @("$plan/identity.py")
$editCheck = $py + @("$plan/edit-check.py", '--group')
$steps = @(
    @{ Id = 'identity-before'; Stage = 'identity'; Argv = $identity },
    @{ Id = 'tools-lint'; Stage = 'static'; Argv = @('uv', 'run', '--no-sync', 'ruff', 'check', 'tools/check_home_path.py', 'tests/tooling/test_check_home_path.py') },
    @{ Id = 'py-lint'; Stage = 'static'; Argv = @('uv', 'run', '--no-sync', 'ruff', 'check', 'packages/', 'tests/') },
    @{ Id = 'task-contract'; Stage = 'static'; Argv = $py + @('tools/lint_task_contract.py', '--allowed-builder-classes', 'avkit_builder,avkit_coordinator,avkit_verifier', '--task', "$plan/task.md") },
    @{ Id = 'scope-paths'; Stage = 'static'; Argv = $py + @("$plan/scope-check.py") },
    @{ Id = 'home-path'; Stage = 'static'; Argv = $py + @('tools/check_home_path.py') },
    @{ Id = 'inventory-check'; Stage = 'static'; Argv = $py + @("$plan/inventory.py", '--check-allowlist', '--cross-check') },
    @{ Id = 'edit-check-docs'; Stage = 'static'; Argv = $editCheck + @('docs') },
    @{ Id = 'edit-check-tests'; Stage = 'static'; Argv = $editCheck + @('tests') },
    @{ Id = 'edit-check-commands'; Stage = 'static'; Argv = $editCheck + @('commands') },
    @{ Id = 'edit-check-register'; Stage = 'static'; Argv = $editCheck + @('register', '--stage', '10') },
    @{ Id = 'red-check-selftest'; Stage = 'static'; Argv = $py + @("$plan/red-check.py", '--selftest') },
    @{ Id = 'ui-types'; Stage = 'static'; Ui = $true; Argv = @('npm', 'run', 'typecheck') },
    @{ Id = 'ui-lint'; Stage = 'static'; Ui = $true; Argv = @('npm', 'run', 'lint') },
    @{ Id = 'home-path-tests'; Stage = 'targeted'; Argv = @('uv', 'run', '--no-sync', 'pytest', 'tests/tooling/test_check_home_path.py', '--tb=short', '-q', '-rs') },
    @{ Id = 'ui-targeted'; Stage = 'targeted'; Ui = $true; Argv = @('npm', 'run', 'test', '--', 'tests/unit/dev-spawn.test.ts', 'tests/unit/capture-interactive.test.ts') },
    @{ Id = 'adoption-tests'; Stage = 'targeted'; Argv = @('uv', 'run', '--no-sync', 'pytest', 'tests/tooling/test_framework_adoption.py', 'tests/tooling/test_hdp_expert_pass.py', '--tb=short', '-q') },
    @{ Id = 'py-tests'; Stage = 'full'; Argv = @('uv', 'run', '--no-sync', 'pytest', 'tests/', '--tb=short', '-q', '-rfE') },
    @{ Id = 'ui-tests'; Stage = 'full'; Ui = $true; Argv = @('npm', 'run', 'test') },
    @{ Id = 'state-render'; Stage = 'full'; Argv = $py + @('tools/meu_status.py', 'render', '--check') },
    @{ Id = 'issues-render'; Stage = 'full'; Argv = $py + @('tools/issue_triage.py', 'render', '--check') },
    @{ Id = 'closeout-selftest'; Stage = 'full'; Argv = $py + @('tools/validate_closeout_artifacts.py', '--selftest') },
    @{ Id = 'identity-after'; Stage = 'identity'; Argv = $identity }
)

function Get-TestedState([string]$Receipt) {
    $line = Select-String -Path $Receipt -Pattern '^tested_state ' | Select-Object -Last 1
    if ($null -eq $line) { return $null }
    return $line.Line.Substring('tested_state '.Length).Trim()
}

for ($i = 0; $i -lt $steps.Count; $i++) {
    $step = $steps[$i]
    $receipt = "$receipts/dph-D6-$($step.Id).txt"
    $argv = $step.Argv
    if ($step.Ui) {
        $env:TMP = $userTmp
        $env:TEMP = $userTemp
        Push-Location (Join-Path $root 'ui')
        & rtk proxy @argv *> $receipt
        $code = $LASTEXITCODE
        Pop-Location
    }
    else {
        $env:TMP = $tmp
        $env:TEMP = $tmp
        & rtk proxy @argv *> $receipt
        $code = $LASTEXITCODE
    }
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
    if ($code -eq 1 -and $step.Id -eq 'ui-tests') {
        $failed = @(Select-String -Path $receipt -Pattern $uiFailPattern | ForEach-Object { $_.Matches[0].Groups[1].Value } | Sort-Object -Unique)
        $outside = @($failed | Where-Object { $baselineUiFailed -notcontains $_ })
        Write-Output ("ui-tests baseline rule: failed={0} outside_baseline=[{1}]" -f $failed.Count, ($outside -join ', '))
        if ($failed.Count -gt 0 -and $outside.Count -eq 0) {
            Write-Output 'ui-tests: every failure is in the row 0 baseline failed set; not a regression'
            $code = 0
        }
    }
    if ($code -eq 0 -and $step.Id -eq 'home-path-tests') {
        if (Select-String -Path $receipt -Pattern 'SKIPPED' -SimpleMatch -Quiet) {
            Write-Output 'home-path-tests: the receipt shows a skipped test; every case must run'
            $code = 1
        }
    }
    if ($code -eq 0 -and $step.Id -eq 'closeout-selftest') {
        if (-not (Select-String -Path $receipt -Pattern ' 0 failure' -Quiet)) {
            Write-Output 'closeout-selftest: the receipt does not report 0 failures'
            $code = 1
        }
    }
    if ($code -eq 0 -and $step.Id -eq 'identity-after') {
        $before = Get-TestedState "$receipts/dph-D6-identity-before.txt"
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
