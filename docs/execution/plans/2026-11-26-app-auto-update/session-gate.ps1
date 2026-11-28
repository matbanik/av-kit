# Session 106 fresh-full gate (task H1-2; implementation-plan.md §Verification Plan 5).
# The shape of docs/execution/plans/2026-11-26-capture-key-inbox-scrollbars/session-gate.ps1
# (Session 103's, itself from 2026-11-22-tray-show-and-baseline-fixes and
# 2026-11-20-e2e-devpc-clipboard), with this plan's steps: identity; the static checks (ui-types,
# ui-lint, py-types, py-lint, py-format, task-contract, scope-paths, line-endings, pins-scan,
# red-unchanged, canon, the checker selftests and feed-check-selftest); the fresh full suites
# (ui-tests, py-tests, ui-build, mcp-types, mcp-tests, mcp-build, mcp-audit, openapi,
# state-render, issues-render); remote-run-2 (row-check.py remote-run-2: row 17's receipts bound
# by run id and snapshot commit, no scope file changed since that snapshot); then the identity
# again. Skipped, with reason: Electron on the dev PC (D-1411: E2E runs on mini-air, rows 7 and 17).
# Runs from the repository root (P:/av-kit, main only per AGENTS.md §Commits). One receipt per
# step under C:/Temp/av-kit/2026-11-26-app-auto-update, named aau-D6-<step>.txt, with the exit
# code beside it in <receipt>.exit.
# Fail-fast: the first non-zero step stops the gate and every later step is printed as not_run.
# The gate also fails when tested_state differs between its start and its end.
# Read-only apart from the receipts, the temp folder, ui/out (ui-build) and mcp-server/dist
# (mcp-build). No step starts Electron on this PC, reaches YouTube or dispatches a model. Nothing
# is excused: py-tests deselects nothing, and no step excuses a test by name.
$ErrorActionPreference = 'Continue'
$root = (git rev-parse --show-toplevel).Trim()
Set-Location $root
$plan = 'docs/execution/plans/2026-11-26-app-auto-update'
$receipts = 'C:/Temp/av-kit/2026-11-26-app-auto-update'
$env:RECEIPTS_DIR = 'C:/Temp/av-kit'
$env:PYTHONIOENCODING = 'utf-8'
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:ELECTRON_RUN_AS_NODE = $null
# Undated on purpose: a dated TEMP folder is the ancestor that TOOLING-PLAN-SLUG-ANCESTOR-MATCH reads.
$tmp = 'C:\Temp\av-kit\s106-tmp'
New-Item -ItemType Directory -Force -Path $tmp | Out-Null
$env:TMP = $tmp
$env:TEMP = $tmp

Write-Output 'skipped: electron-devpc reason=D-1411 (E2E runs on mini-air; rows 7 and 17, bound by remote-run-2)'
Write-Output 'baseline ui failures excused: [] (ui-tests excuses nothing)'
Write-Output 'baseline py failures excused: [] (py-tests deselects nothing)'

$py = @('uv', 'run', '--no-sync', 'python')
$identity = $py + @("$plan/identity.py")
$rowCheck = $py + @("$plan/row-check.py")
$pytest = @('uv', 'run', '--no-sync', 'pytest', '-p', 'no:cacheprovider')
$planPy = @(Get-ChildItem -Path $plan -Filter '*.py' | Sort-Object Name | ForEach-Object { "$plan/$($_.Name)" })
$newPy = @('tools/check_update_feed.py', 'tests/unit/test_update_feed_config.py', 'tests/unit/test_check_update_feed.py', 'tests/unit/test_update_interval_setting.py')
$snapSelftest = Join-Path $tmp ("aau-snapshot-selftest-{0}" -f [DateTime]::UtcNow.Ticks)
$steps = @(
    @{ Id = 'identity-before'; Stage = 'identity'; Argv = $identity },
    @{ Id = 'ui-types'; Stage = 'static'; Cwd = 'ui'; Argv = @('npm', 'run', 'typecheck') },
    @{ Id = 'ui-lint'; Stage = 'static'; Cwd = 'ui'; Argv = @('npm', 'run', 'lint') },
    @{ Id = 'py-types'; Stage = 'static'; Argv = @('uv', 'run', '--no-sync', 'pyright', 'packages/') },
    @{ Id = 'py-lint'; Stage = 'static'; Argv = @('uv', 'run', '--no-sync', 'ruff', 'check', 'packages/', 'tests/', 'tools/check_update_feed.py', 'tools/e2e_remote.py') + $planPy },
    @{ Id = 'py-format'; Stage = 'static'; Argv = @('uv', 'run', '--no-sync', 'ruff', 'format', '--check') + $newPy + $planPy },
    @{ Id = 'task-contract'; Stage = 'static'; Argv = $py + @('tools/lint_task_contract.py', '--allowed-builder-classes', 'avkit_builder,avkit_coordinator,avkit_verifier', '--task', "$plan/task.md") },
    @{ Id = 'scope-paths'; Stage = 'static'; Argv = $rowCheck + @('scope-paths') },
    @{ Id = 'line-endings'; Stage = 'static'; Argv = $py + @("$plan/eol-check.py") },
    @{ Id = 'pins-scan'; Stage = 'static'; Argv = $py + @("$plan/pins-scan.py", '--check') },
    @{ Id = 'red-unchanged'; Stage = 'static'; Argv = $rowCheck + @('red-unchanged') },
    @{ Id = 'canon'; Stage = 'static'; Argv = $rowCheck + @('canon') },
    @{ Id = 'row-check-selftest'; Stage = 'static'; Argv = $rowCheck + @('--selftest') },
    @{ Id = 'pins-scan-selftest'; Stage = 'static'; Argv = $py + @("$plan/pins-scan.py", '--selftest') },
    @{ Id = 'run-check-selftest'; Stage = 'static'; Argv = $py + @("$plan/run-check.py", '--selftest') },
    @{ Id = 'licence-check-selftest'; Stage = 'static'; Argv = $py + @("$plan/licence-check.py", '--selftest') },
    @{ Id = 'red-check-selftest'; Stage = 'static'; Argv = $py + @("$plan/red-check.py", '--selftest') },
    @{ Id = 'eol-check-selftest'; Stage = 'static'; Argv = $py + @("$plan/eol-check.py", '--selftest') },
    @{ Id = 'identity-selftest'; Stage = 'static'; Argv = $py + @("$plan/identity.py", '--selftest') },
    @{ Id = 'snapshot-selftest'; Stage = 'static'; Argv = $py + @("$plan/snapshot-commit.py", '--selftest', $snapSelftest) },
    @{ Id = 'feed-check-selftest'; Stage = 'static'; Argv = $py + @('tools/check_update_feed.py', '--selftest') },
    @{ Id = 'ui-tests'; Stage = 'full'; Cwd = 'ui'; Argv = @('npm', 'run', 'test') },
    @{ Id = 'py-tests'; Stage = 'full'; Argv = $pytest + @('tests/', '-x', '--tb=short', '-q') },
    @{ Id = 'ui-build'; Stage = 'full'; Cwd = 'ui'; Argv = @('npm', 'run', 'build') },
    @{ Id = 'mcp-types'; Stage = 'full'; Argv = @('npm', '--prefix', 'mcp-server', 'run', 'typecheck') },
    @{ Id = 'mcp-tests'; Stage = 'full'; Argv = @('npm', '--prefix', 'mcp-server', 'run', 'test') },
    @{ Id = 'mcp-build'; Stage = 'full'; Argv = @('npm', '--prefix', 'mcp-server', 'run', 'build') },
    # D-1590: row 11's form (D-1568); the runner refuses a bare `run audit` (exit 4).
    @{ Id = 'mcp-audit'; Stage = 'full'; Argv = @('npm', '--prefix', 'mcp-server', 'run', 'audit', '--',
        '--mode', 'authoritative', '--baseline', "$root/.agent/skills/mcp-tool-audit/resources/baseline-snapshot.json",
        '--report', "$receipts/aau-gate-audit-report.md", '--out', "$receipts/audit-gate", '--agent', 'claude') },
    @{ Id = 'openapi'; Stage = 'full'; Argv = $py + @('tools/export_openapi.py', '--check', 'openapi.committed.json') },
    @{ Id = 'state-render'; Stage = 'full'; Argv = $py + @('tools/meu_status.py', 'render', '--check') },
    @{ Id = 'issues-render'; Stage = 'full'; Argv = $py + @('tools/issue_triage.py', 'render', '--check') },
    @{ Id = 'remote-run-2'; Stage = 'full'; Argv = $rowCheck + @('remote-run-2') },
    @{ Id = 'identity-after'; Stage = 'identity'; Argv = $identity }
)

function Get-TestedState([string]$Receipt) {
    $line = Select-String -Path $Receipt -Pattern '^tested_state ' | Select-Object -Last 1
    if ($null -eq $line) { return $null }
    return $line.Line.Substring('tested_state '.Length).Trim()
}

# D-1580: row 17 is [B] (B-17). A failing remote-run-2 is reported as blocked, the gate still
# runs identity-after, and it ends exit 3; every other step must exit 0 as before.
$b17 = Select-String -Path (Join-Path $root 'docs/execution/plans/2026-11-26-app-auto-update/task.md') -Pattern '^### B-17$' -Quiet
$blocked = $null
for ($i = 0; $i -lt $steps.Count; $i++) {
    $step = $steps[$i]
    $receipt = "$receipts/aau-D6-$($step.Id).txt"
    $argv = $step.Argv
    if ($step.ContainsKey('Cwd')) { Set-Location (Join-Path $root $step.Cwd) }
    & rtk proxy @argv *> $receipt
    $code = $LASTEXITCODE
    Set-Location $root
    Set-Content -Path "$receipt.exit" -Value $code -Encoding ascii
    Write-Output ("{0} stage={1} exit={2} receipt={3}" -f $step.Id, $step.Stage, $code, $receipt)
    Get-Content $receipt | Select-Object -Last 6
    if ($code -eq 0 -and $step.Id -eq 'identity-after') {
        $before = Get-TestedState "$receipts/aau-D6-identity-before.txt"
        $after = Get-TestedState $receipt
        Write-Output "tested_state before=$before after=$after"
        if ([string]::IsNullOrEmpty($before) -or $before -ne $after) {
            Write-Output 'identity-after: tested_state changed while the gate ran; the gate is not fresh'
            $code = 1
        }
    }
    if ($code -ne 0 -and $step.Id -eq 'remote-run-2' -and $b17) {
        Write-Output "remote-run-2 blocked reason=B-17 exit=$code (D-1580); the gate continues to identity-after"
        $blocked = $step.Id
        continue
    }
    if ($code -ne 0) {
        for ($j = $i + 1; $j -lt $steps.Count; $j++) {
            Write-Output ("{0} stage={1} not_run reason=fail-fast after {2}" -f $steps[$j].Id, $steps[$j].Stage, $step.Id)
        }
        exit $code
    }
}
if ($blocked) {
    Write-Output 'session-gate: every step exit 0 except remote-run-2, blocked by B-17 (D-1580)'
    exit 3
}
Write-Output 'session-gate: all steps exit 0'
exit 0
