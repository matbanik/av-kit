# E2E harness hardening fresh-full gate (task H1-2; implementation-plan.md §Session gate).
# The shape of docs/execution/plans/2026-11-15-framework-small-syncs/session-gate.ps1, with this
# plan's steps and the RC2 gate's Electron prerequisites (2026-11-08-release-rc2: the isolated
# primitive harness build and the region-picker stub, both gitignored and read by the full suite).
# Runs from the repository root (P:/av-kit, main only per AGENTS.md §Commits) in stage order:
# input identity, then every static check, then the targeted checks, then the full suites and
# builds, then the runtime Electron runs, then the input identity again. One receipt per id
# under C:/Temp/av-kit/e2e-harness-hardening, named ehh-D6-<id>.txt.
# Fail-fast: the first non-zero step stops the gate and every later step is printed as not_run.
# The gate also fails when tested_state differs between its start and its end (an input changed
# while it ran). Writes only the receipts, the temp folders, ui/out, ui/out-e2e, the stub's
# publish folder and ui/test-results, all ignored or outside the checkout. Nothing here reaches
# the network or YouTube, and no step dispatches a model. Exit = the first failing step's code.
# ui-tests and ui-electron excuse nothing: row 0's receipts showed both suites passing.
# ui-electron runs the whole Electron suite with ELECTRON_RUN_AS_NODE unset and also fails unless
# it reports 0 failed and at least base-e2e-count.txt + 5 passed (the five electron-harness cases:
# AC-5, AC-6, the two AC-7 cases and AC-8).
# ui-electron-flag runs launch.test.ts and electron-harness.test.ts with ELECTRON_RUN_AS_NODE=1
# (AC-18) and DEBUG=pw:browser, so electron.exe's stderr reaches the receipt (D-1030); both are
# reset straight after, before identity-after hashes it.
# Each Electron step runs through owned-procs.ps1, which records the step's own process tree by
# pid and creation time. After the step, only a recorded electron.exe that is still alive, runs
# this checkout's binary and started during the gate is reported and stopped; Mat's app and other
# sessions' apps keep running, even on this checkout's binary.
# Skipped, per the plan: py-types, py-lint and py-tests (nothing under packages/ or tests/
# changes since row 0; the register is checked by register-grammar, issues-render and
# issue-resolve.py's own validator pass), mcp-* (no MCP change since row 0), openapi (no
# packages/api change since row 0) and build-record (no release build). Each is printed with its
# reason and runs nothing. The skip basis is the 'untouched' step: untouched-check.py compares
# every file under packages/, tests/, mcp-server/src, mcp-server/tests, ui/src and tools/ with the
# hashes row 0 recorded, never with HEAD, because Sessions 75 to 77 may leave their own changes
# there uncommitted.
$ErrorActionPreference = 'Continue'
$root = (git rev-parse --show-toplevel).Trim()
Set-Location $root
$plan = 'docs/execution/plans/2026-11-15-e2e-harness-hardening'
$receipts = 'C:/Temp/av-kit/e2e-harness-hardening'
# lint_task_contract.py recognises the instantiated receipt paths only through RECEIPTS_DIR and
# fails closed (exit 3) when it is unset, which no user or machine scope sets on this host.
$env:RECEIPTS_DIR = 'C:/Temp/av-kit'
$env:PYTHONIOENCODING = 'utf-8'
$env:ELECTRON_RUN_AS_NODE = $null
$env:DEBUG = $null
$env:AGENT_MODEL_REGISTRY_HOME = 'P:/.agent'
# Temp dirs (and every mkdtempSync(tmpdir()) app-data folder) away from the home folder.
$tmp = 'C:\Temp\av-kit\e2e-harness-hardening\tmp'
New-Item -ItemType Directory -Force -Path $tmp | Out-Null
$env:TMP = $tmp
$env:TEMP = $tmp
$started = Get-Date
. (Join-Path $PSScriptRoot 'owned-procs.ps1')
$electronDist = (Join-Path $root 'ui\node_modules\electron\dist\').Replace('/', '\')

$baseCount = $null
if (Test-Path "$plan/base-e2e-count.txt") { $baseCount = [int](Get-Content "$plan/base-e2e-count.txt" -Raw).Trim() }
Write-Output ("base e2e passed count: {0} (row 0's base-e2e-count.txt); ui-electron needs at least {0} + 5" -f $baseCount)
Write-Output 'baseline ui and e2e failures excused: [] (ui-tests and ui-electron excuse nothing)'

$skipped = @(
    @{ Id = 'py-types/py-lint/py-tests'; Stage = 'full'; Reason = 'nothing under packages/ or tests/ changes since row 0 (untouched step)' },
    @{ Id = 'mcp-types/mcp-build/mcp-tests/mcp-audit'; Stage = 'full'; Reason = 'no MCP change since row 0 (untouched step)' },
    @{ Id = 'openapi'; Stage = 'full'; Reason = 'no packages/api change since row 0 (untouched step)' },
    @{ Id = 'build-record'; Stage = 'full'; Reason = 'no release build' }
)
foreach ($s in $skipped) {
    Write-Output ("{0} stage={1} skipped reason={2}" -f $s.Id, $s.Stage, $s.Reason)
}

$py = @('uv', 'run', '--no-sync', 'python')
$identity = $py + @("$plan/identity.py")
$harnessBuild = "`$env:AVKIT_PRIMITIVE_HARNESS_BUILD='1'; npm --prefix ui run build -- --outDir '$root/ui/out-e2e'; exit `$LASTEXITCODE"
$flagRun = "`$env:ELECTRON_RUN_AS_NODE='1'; `$env:DEBUG='pw:browser'; npm --prefix ui run test:e2e -- tests/e2e/launch.test.ts tests/e2e/electron-harness.test.ts; exit `$LASTEXITCODE"
$steps = @(
    @{ Id = 'identity-before'; Stage = 'identity'; Argv = $identity },
    @{ Id = 'ui-types'; Stage = 'static'; Argv = @('npm', '--prefix', 'ui', 'run', 'typecheck') },
    @{ Id = 'ui-lint'; Stage = 'static'; Argv = @('npm', '--prefix', 'ui', 'run', 'lint') },
    @{ Id = 'task-contract'; Stage = 'static'; Argv = $py + @('tools/lint_task_contract.py', '--allowed-builder-classes', 'avkit_builder,avkit_coordinator,avkit_verifier', '--task', "$plan/task.md") },
    @{ Id = 'scope-paths'; Stage = 'static'; Argv = $py + @("$plan/scope-check.py", '--before-row', '13') },
    @{ Id = 'scope-check-selftest'; Stage = 'static'; Argv = $py + @("$plan/scope-check.py", '--selftest') },
    @{ Id = 'red-check-selftest'; Stage = 'static'; Argv = $py + @("$plan/red-check.py", '--selftest') },
    @{ Id = 'site-check-selftest'; Stage = 'static'; Argv = $py + @("$plan/site-check.py", '--selftest') },
    @{ Id = 'site-check'; Stage = 'static'; Argv = $py + @("$plan/site-check.py") },
    @{ Id = 'mutation-selftest'; Stage = 'static'; Argv = $py + @("$plan/mutation.py", '--selftest') },
    @{ Id = 'mutation-status'; Stage = 'static'; Argv = $py + @("$plan/mutation.py", 'status') },
    @{ Id = 'untouched-selftest'; Stage = 'static'; Argv = $py + @("$plan/untouched-check.py", '--selftest') },
    @{ Id = 'owned-procs-selftest'; Stage = 'static'; Argv = @('pwsh', '-NoProfile', '-File', "$plan/owned-procs.ps1", '-Selftest') },
    @{ Id = 'untouched'; Stage = 'static'; Argv = $py + @("$plan/untouched-check.py") },
    @{ Id = 'register-grammar'; Stage = 'targeted'; Argv = @('uv', 'run', '--no-sync', 'pytest', 'tests/tooling/test_closeout_register_grammar.py', '--tb=short', '-q') },
    @{ Id = 'ui-tests'; Stage = 'full'; Argv = @('npm', '--prefix', 'ui', 'run', 'test') },
    @{ Id = 'ui-build'; Stage = 'full'; Argv = @('npm', '--prefix', 'ui', 'run', 'build') },
    @{ Id = 'ui-harness-build'; Stage = 'full'; Argv = @('pwsh', '-NoProfile', '-Command', $harnessBuild) },
    @{ Id = 'ui-picker-stub'; Stage = 'full'; Argv = @('npm', '--prefix', 'ui', 'run', 'build:picker-stub') },
    @{ Id = 'state-render'; Stage = 'full'; Argv = $py + @('tools/meu_status.py', 'render', '--check') },
    @{ Id = 'issues-render'; Stage = 'full'; Argv = $py + @('tools/issue_triage.py', 'render', '--check') },
    @{ Id = 'ui-electron'; Stage = 'runtime'; Argv = @('npm', '--prefix', 'ui', 'run', 'test:e2e') },
    @{ Id = 'ui-electron-flag'; Stage = 'runtime'; Argv = @('pwsh', '-NoProfile', '-Command', $flagRun) },
    @{ Id = 'identity-after'; Stage = 'identity'; Argv = $identity }
)

function Get-TestedState([string]$Receipt) {
    $line = Select-String -Path $Receipt -Pattern '^tested_state ' | Select-Object -Last 1
    if ($null -eq $line) { return $null }
    return $line.Line.Substring('tested_state '.Length).Trim()
}

for ($i = 0; $i -lt $steps.Count; $i++) {
    $step = $steps[$i]
    $receipt = "$receipts/ehh-D6-$($step.Id).txt"
    $argv = $step.Argv
    $electronStep = $step.Id -in @('ui-electron', 'ui-electron-flag')
    if ($electronStep) {
        $run = Invoke-OwnedRun -Argv $argv -Receipt $receipt
        $code = $run.Code
    } else {
        & rtk proxy @argv *> $receipt
        $code = $LASTEXITCODE
    }
    # The flag run sets the variable only in its own child pwsh; reset here as well, so nothing
    # later in this process can inherit it.
    $env:ELECTRON_RUN_AS_NODE = $null
    $env:DEBUG = $null
    Write-Output ("{0} stage={1} exit={2} receipt={3}" -f $step.Id, $step.Stage, $code, $receipt)
    Get-Content $receipt | Select-Object -Last 6
    if ($electronStep) {
        Stop-OwnedElectron -Label $step.Id -Owned $run.Owned -Dist $electronDist -Started $started
    }
    if ($code -eq 0 -and $step.Id -eq 'ui-electron') {
        $passed = Select-String -Path $receipt -Pattern '^\s+(\d+) passed' | Select-Object -Last 1
        $bad = Select-String -Path $receipt -Pattern '^\s+\d+ (failed|flaky|did not run|interrupted)\s*$'
        $n = if ($null -eq $passed) { -1 } else { [int]$passed.Matches[0].Groups[1].Value }
        Write-Output ("ui-electron: passed={0} base={1} needed={2}" -f $n, $baseCount, ($baseCount + 5))
        if ($null -eq $baseCount -or $n -lt ($baseCount + 5) -or $bad) {
            Write-Output 'ui-electron: fewer passed than row 0 plus the five new cases, or a failed/flaky/not-run line'
            $code = 1
        }
    }
    if ($code -eq 0 -and $step.Id -eq 'ui-electron-flag') {
        if (-not (Select-String -Path $receipt -Pattern '^\s+\d+ passed' -Quiet) -or (Select-String -Path $receipt -Pattern 'bad option' -SimpleMatch -Quiet)) {
            Write-Output 'ui-electron-flag: no passed line, or a "bad option" launch failure, with ELECTRON_RUN_AS_NODE=1'
            $code = 1
        }
    }
    if ($code -eq 0 -and $step.Id -eq 'identity-after') {
        $before = Get-TestedState "$receipts/ehh-D6-identity-before.txt"
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
