# Tooling test hermeticity fresh-full gate (task H1-2; implementation-plan.md §Session gate).
# The peer's shape (docs/execution/plans/2026-11-15-framework-small-syncs/session-gate.ps1), with
# this plan's steps: tools-lint and py-lint, the task contract, scope-paths (S4), fixture-check
# (AC-1), hermetic-check with --asserts and --eol (AC-5), dispatch-source (AC-10), the red-check
# selftest, the adoption tests with adoption-check (AC-2, AC-6 to AC-9, AC-11, AC-14), the
# adoption registry selection under HOSTILE (AC-3, AC-4), the dispatch tests with --expect-clean
# (AC-10), the full Python suite, the state render, the issues render (AC-13), the closeout
# validator's selftest and the live probe (AC-12).
# Runs from the repository root (P:/av-kit, main only per AGENTS.md §Commits) in stage order:
# input identity, then every static check, then the targeted checks, then the full suites, then
# the input identity again. One receipt per id under C:/Temp/av-kit/tth, named tth-D6-<id>.txt.
# Fail-fast: the first non-zero step stops the gate and every later step is printed as not_run.
# The gate also fails when tested_state differs between its start and its end (an input changed
# while it ran). Read-only apart from the receipts and the temp folders, which sit outside the
# repository. Nothing here reaches the network or YouTube, and no step dispatches a model.
# Exit = the first failing step's code.
# adoption-hostile sets HOSTILE (AGENT_MODEL_REGISTRY to the red registry home) around its own
# process only, in a try/finally that removes it again; no other step sees it.
# dispatch-tests runs DISPATCH_TEST with the user's own TMP and TEMP (UserTemp), as rows 0 and 6
# ran it, writes its exit file and is judged by dispatch-check.py --expect-clean. It also records
# that the leftover %TEMP% dispatch-tests folder's mtime is unchanged and that no
# cli-dispatch-ph-* folder is left behind.
# py-tests runs the whole suite (no -x) and keeps Session 49b's baseline rule: pytest exit 1
# passes only when every FAILED id also FAILED in row 0's tth-base-py.txt, and nothing ERRORs.
# Skipped, per the plan: py-types (nothing under packages/ changes), ui-* (nothing under ui/
# changes), mcp-* (no MCP change), openapi (no packages/api file differs from row 0's
# baseline-api.json; H1-4) and build-record (no build). Each is printed with its reason and runs
# nothing.
$ErrorActionPreference = 'Continue'
$root = (git rev-parse --show-toplevel).Trim()
Set-Location $root
$plan = 'docs/execution/plans/2026-11-15-tooling-test-hermeticity'
$receipts = 'C:/Temp/av-kit/tth'
# lint_task_contract.py recognises the instantiated receipt paths only through RECEIPTS_DIR and
# fails closed (exit 3) when it is unset, which no user or machine scope sets on this host.
$env:RECEIPTS_DIR = 'C:/Temp/av-kit'
$env:PYTHONIOENCODING = 'utf-8'
$env:ELECTRON_RUN_AS_NODE = $null
$env:AGENT_MODEL_REGISTRY = $null
# The dispatch suite loads ModelRegistry.psm1 from the shared registry home (memory:
# codex-dispatch-registry-home); the adoption tests set their own AGENT_MODEL_REGISTRY.
$env:AGENT_MODEL_REGISTRY_HOME = 'P:/.agent'
$hostile = 'C:/Temp/av-kit/tth/red-home/model-registry.json'
# RC1 ECN-2 (CLOSEOUT-SELFTEST-ANCESTOR-AGENT-DIR): keep pytest's temp dirs away from the home folder.
# The dispatch suite alone runs with the user's own TMP and TEMP.
$userTmp = $env:TMP
$userTemp = $env:TEMP
$tmp = 'C:\Temp\av-kit\tth\tmp'
New-Item -ItemType Directory -Force -Path $tmp | Out-Null
$env:TMP = $tmp
$env:TEMP = $tmp

# An id is excused only when row 0's baseline receipt really shows it FAILED: a missing
# receipt excuses nothing.
$baseReceipt = "$receipts/tth-base-py.txt"
$baselinePyFailed = @()
if (Test-Path $baseReceipt) {
    $baselinePyFailed = @(Select-String -Path $baseReceipt -Pattern '^FAILED (\S+)' | ForEach-Object { $_.Matches[0].Groups[1].Value })
}
Write-Output ("baseline py failures excused: {0} id(s) (receipt {1})" -f $baselinePyFailed.Count, $baseReceipt)

$skipped = @(
    @{ Id = 'py-types'; Stage = 'static'; Reason = 'pyright packages/: nothing under packages/ changes' },
    @{ Id = 'ui-types/ui-lint/ui-tests/ui-build/ui-electron'; Stage = 'full'; Reason = 'nothing under ui/ changes' },
    @{ Id = 'mcp-types/mcp-build/mcp-tests/mcp-audit'; Stage = 'full'; Reason = 'no MCP change' },
    @{ Id = 'openapi'; Stage = 'full'; Reason = 'no packages/api file differs from baseline-api.json (H1-4)' },
    @{ Id = 'build-record'; Stage = 'full'; Reason = 'no build' }
)
foreach ($s in $skipped) {
    Write-Output ("{0} stage={1} skipped reason={2}" -f $s.Id, $s.Stage, $s.Reason)
}

$py = @('uv', 'run', '--no-sync', 'python')
$identity = $py + @("$plan/identity.py")
$testFile = 'tests/tooling/test_framework_adoption.py'
$hostileK = 'preserves_bindings or vendor_independence or unsupported_harness or bad_configuration or wrapper_refuses or test_ac_2_'
$steps = @(
    @{ Id = 'identity-before'; Stage = 'identity'; Argv = $identity },
    @{ Id = 'tools-lint'; Stage = 'static'; Argv = @('uv', 'run', '--no-sync', 'ruff', 'check', 'tests/tooling/') },
    @{ Id = 'py-lint'; Stage = 'static'; Argv = @('uv', 'run', '--no-sync', 'ruff', 'check', 'packages/', 'tests/') },
    @{ Id = 'task-contract'; Stage = 'static'; Argv = $py + @('tools/lint_task_contract.py', '--allowed-builder-classes', 'avkit_builder,avkit_coordinator,avkit_verifier', '--task', "$plan/task.md") },
    @{ Id = 'scope-paths'; Stage = 'static'; Argv = $py + @("$plan/scope-check.py") },
    @{ Id = 'fixture-check'; Stage = 'static'; Argv = $py + @("$plan/fixture-check.py") },
    @{ Id = 'hermetic-check'; Stage = 'static'; Argv = $py + @("$plan/hermetic-check.py", '--asserts', '--eol') },
    @{ Id = 'dispatch-source'; Stage = 'static'; Argv = $py + @("$plan/dispatch-check.py", '--source') },
    @{ Id = 'red-check-selftest'; Stage = 'static'; Argv = $py + @("$plan/red-check.py", '--selftest') },
    @{ Id = 'adoption-tests'; Stage = 'targeted'; Argv = @('uv', 'run', '--no-sync', 'pytest', $testFile, '--tb=short', '-q') },
    @{ Id = 'adoption-hostile'; Stage = 'targeted'; Argv = @('uv', 'run', '--no-sync', 'pytest', $testFile, '-k', $hostileK, '--tb=short', '-q'); Hostile = $true },
    @{ Id = 'dispatch-tests'; Stage = 'targeted'; Argv = @('pwsh', '-NoProfile', '-File', '.agent/skills/cli-dispatch/tests/Test-CliDispatch.ps1'); UserTemp = $true },
    @{ Id = 'py-tests'; Stage = 'full'; Argv = @('uv', 'run', '--no-sync', 'pytest', 'tests/', '--tb=short', '-q', '-rfE') },
    @{ Id = 'state-render'; Stage = 'full'; Argv = $py + @('tools/meu_status.py', 'render', '--check') },
    @{ Id = 'issues-render'; Stage = 'full'; Argv = $py + @('tools/issue_triage.py', 'render', '--check') },
    @{ Id = 'closeout-selftest'; Stage = 'full'; Argv = $py + @('tools/validate_closeout_artifacts.py', '--selftest') },
    @{ Id = 'live-probe'; Stage = 'full'; Argv = $py + @("$plan/live-probe.py") },
    @{ Id = 'identity-after'; Stage = 'identity'; Argv = $identity }
)

function Get-TestedState([string]$Receipt) {
    $line = Select-String -Path $Receipt -Pattern '^tested_state ' | Select-Object -Last 1
    if ($null -eq $line) { return $null }
    return $line.Line.Substring('tested_state '.Length).Trim()
}

function Get-Mtime([string]$Path) {
    if (Test-Path -LiteralPath $Path) { return (Get-Item -LiteralPath $Path).LastWriteTime.ToString('s') }
    return 'absent'
}

$leftover = Join-Path $userTemp 'av-kit/receipts/dispatch-tests'
for ($i = 0; $i -lt $steps.Count; $i++) {
    $step = $steps[$i]
    $receipt = "$receipts/tth-D6-$($step.Id).txt"
    $argv = $step.Argv
    if ($step.UserTemp) {
        $leftBefore = Get-Mtime $leftover
        $phBefore = @(Get-ChildItem -LiteralPath $userTemp -Directory -Filter 'cli-dispatch-ph-*' -ErrorAction SilentlyContinue).Count
        $env:TMP = $userTmp
        $env:TEMP = $userTemp
    }
    if ($step.Hostile) {
        $env:AGENT_MODEL_REGISTRY = $hostile
        try {
            & rtk proxy @argv *> $receipt
            $code = $LASTEXITCODE
        }
        finally {
            $env:AGENT_MODEL_REGISTRY = $null
        }
    }
    else {
        & rtk proxy @argv *> $receipt
        $code = $LASTEXITCODE
    }
    $env:TMP = $tmp
    $env:TEMP = $tmp
    Write-Output ("{0} stage={1} exit={2} receipt={3}" -f $step.Id, $step.Stage, $code, $receipt)
    Get-Content $receipt | Select-Object -Last 6
    if ($code -eq 0 -and $step.Id -eq 'adoption-tests') {
        # adoption-check (AC-11): 0 failed and passed = row 0's count + 5.
        $countReceipt = "$receipts/tth-D6-adoption-check.txt"
        $countArgv = $py + @("$plan/hermetic-check.py", '--count', $receipt)
        & rtk proxy @countArgv *> $countReceipt
        $code = $LASTEXITCODE
        Write-Output ("adoption-check exit={0} receipt={1}" -f $code, $countReceipt)
        Get-Content $countReceipt | Select-Object -Last 6
    }
    if ($step.Id -eq 'dispatch-tests') {
        Set-Content -Path "$receipt.exit" -Value $code
        $leftAfter = Get-Mtime $leftover
        $phAfter = @(Get-ChildItem -LiteralPath $userTemp -Directory -Filter 'cli-dispatch-ph-*' -ErrorAction SilentlyContinue).Count
        Write-Output ("dispatch-tests leftover %TEMP% dispatch-tests mtime before={0} after={1}; cli-dispatch-ph-* folders before={2} after={3}" -f $leftBefore, $leftAfter, $phBefore, $phAfter)
        $cleanReceipt = "$receipts/tth-D6-dispatch-clean.txt"
        $cleanArgv = $py + @("$plan/dispatch-check.py", '--expect-clean', '--exit-file', "$receipt.exit", $receipt)
        & rtk proxy @cleanArgv *> $cleanReceipt
        $code = $LASTEXITCODE
        Write-Output ("dispatch-clean exit={0} receipt={1}" -f $code, $cleanReceipt)
        Get-Content $cleanReceipt | Select-Object -Last 6
        if ($code -eq 0 -and ($leftBefore -ne $leftAfter -or $phAfter -ne $phBefore)) {
            Write-Output 'dispatch-tests: the suite changed the leftover folder or left a placeholder folder behind'
            $code = 1
        }
    }
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
        $before = Get-TestedState "$receipts/tth-D6-identity-before.txt"
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
