# Session 103 fresh-full gate (task H1-2; implementation-plan.md §Session gate).
# The shape of docs/execution/plans/2026-11-22-tray-show-and-baseline-fixes/session-gate.ps1,
# through Session 104's copy, with this plan's steps: identity; the static checks (ui-types,
# ui-lint, py-types, py-lint, py-format, task-contract, scope-paths, line-endings, home-path,
# guards --row 11, canon, ste-lint, openapi and the script selftests); the targeted suites
# (py-inbox, ui-capture); the fresh full suites (ui-tests, py-tests, ui-build), e2e-remote
# (row-check.py remote-fresh, D-1430), state-render and issues-render; then the identity again.
# Skipped, with reason: Electron on the dev PC (D-1411: E2E runs on mini-air); the mcp-server
# tests (no MCP file changed; mcp-server/ is read-only and scope-paths binds it by hash).
# Runs from the repository root (P:/av-kit, main only per AGENTS.md §Commits). One receipt per
# step under C:/Temp/av-kit/2026-11-26-capture-key-inbox-scrollbars, named cki-D6-<step>.txt,
# with the exit code beside it in <receipt>.exit.
# Fail-fast: the first non-zero step stops the gate and every later step is printed as not_run.
# The gate also fails when tested_state differs between its start and its end.
# Read-only apart from the receipts, the temp folder and ui/out (ui-build). No step starts
# Electron on this PC, reaches YouTube or dispatches a model. Nothing is excused: py-tests
# deselects nothing, and no step excuses a test by name. scope-paths binds content, not HEAD.
$ErrorActionPreference = 'Continue'
$root = (git rev-parse --show-toplevel).Trim()
Set-Location $root
$plan = 'docs/execution/plans/2026-11-26-capture-key-inbox-scrollbars'
$receipts = 'C:/Temp/av-kit/2026-11-26-capture-key-inbox-scrollbars'
$env:RECEIPTS_DIR = 'C:/Temp/av-kit'
$env:PYTHONIOENCODING = 'utf-8'
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:ELECTRON_RUN_AS_NODE = $null
# Undated on purpose: a dated TEMP folder is the ancestor that TOOLING-PLAN-SLUG-ANCESTOR-MATCH reads.
$tmp = 'C:\Temp\av-kit\s103-tmp'
New-Item -ItemType Directory -Force -Path $tmp | Out-Null
$env:TMP = $tmp
$env:TEMP = $tmp

Write-Output 'skipped: electron-devpc reason=D-1411 (E2E runs on mini-air; the e2e-remote step)'
Write-Output 'skipped: mcp-tests reason=no MCP file changed (mcp-server/ is read-only, bound by scope-paths)'
Write-Output 'baseline ui failures excused: [] (ui-tests excuses nothing)'
Write-Output 'baseline py failures excused: [] (py-tests deselects nothing)'

$py = @('uv', 'run', '--no-sync', 'python')
$identity = $py + @("$plan/identity.py")
$rowCheck = $py + @("$plan/row-check.py")
$pytest = @('uv', 'run', '--no-sync', 'pytest', '-p', 'no:cacheprovider')
$planPy = @(Get-ChildItem -Path $plan -Filter '*.py' | Sort-Object Name | ForEach-Object { "$plan/$($_.Name)" })
$newPy = @('tests/unit/test_capture_inbox_scope.py', 'tests/e2e/test_api_capture_inbox_scope.py')
$inboxPy = $newPy + @('tests/unit/test_capture_service.py', 'tests/e2e/test_api_captures.py', 'tests/e2e/test_api_capture_crop.py', 'tests/tooling/test_help_guide_ste.py')
$newUi = @('tests/unit/capture-key.test.ts', 'tests/unit/capture-key.behavior.test.ts', 'tests/unit/capture-inbox-scope.behavior.test.ts', 'tests/unit/capture-scroll-bars.test.ts', 'tests/unit/capture-scroll-bars.behavior.test.ts')
$pinUi = @('capture-page.behavior.test.ts', 'capture-action-row.test.ts', 'help-quick-start.test.tsx', 'capture-help-content.test.ts', 'capture-tool-style.test.ts', 'capture-copy-image.behavior.test.ts', 'capture-redact.behavior.test.ts', 'failure-reason-copy.test.ts', 'help-card.test.ts', 'capture-zoom.test.ts', 'capture-fit-map.test.ts', 'e2e-pointer.test.ts', 'gui-actions-audit.test.ts', 'capture-page.test.ts', 'settings-page.test.ts') | ForEach-Object { "tests/unit/$_" }
$snapSelftest = Join-Path $tmp ("cki-snapshot-selftest-{0}" -f [DateTime]::UtcNow.Ticks)
$steps = @(
    @{ Id = 'identity-before'; Stage = 'identity'; Argv = $identity },
    @{ Id = 'ui-types'; Stage = 'static'; Cwd = 'ui'; Argv = @('npm', 'run', 'typecheck') },
    @{ Id = 'ui-lint'; Stage = 'static'; Cwd = 'ui'; Argv = @('npm', 'run', 'lint') },
    @{ Id = 'py-types'; Stage = 'static'; Argv = @('uv', 'run', '--no-sync', 'pyright', 'packages/') },
    @{ Id = 'py-lint'; Stage = 'static'; Argv = @('uv', 'run', '--no-sync', 'ruff', 'check', 'packages/', 'tests/') + $planPy },
    @{ Id = 'py-format'; Stage = 'static'; Argv = @('uv', 'run', '--no-sync', 'ruff', 'format', '--check') + $newPy + $planPy },
    @{ Id = 'task-contract'; Stage = 'static'; Argv = $py + @('tools/lint_task_contract.py', '--allowed-builder-classes', 'avkit_builder,avkit_coordinator,avkit_verifier', '--task', "$plan/task.md") },
    @{ Id = 'scope-paths'; Stage = 'static'; Argv = $rowCheck + @('scope-paths') },
    @{ Id = 'line-endings'; Stage = 'static'; Argv = $py + @("$plan/eol-check.py") },
    @{ Id = 'home-path'; Stage = 'static'; Argv = $py + @('tools/check_home_path.py') },
    @{ Id = 'guards'; Stage = 'static'; Argv = $rowCheck + @('guards', '--row', '11') },
    @{ Id = 'canon'; Stage = 'static'; Argv = $rowCheck + @('canon') },
    @{ Id = 'ste-lint'; Stage = 'static'; Argv = $py + @('tools/help_guide_ste.py') },
    @{ Id = 'openapi'; Stage = 'static'; Argv = $py + @('tools/export_openapi.py', '--check', 'openapi.committed.json') },
    @{ Id = 'row-check-selftest'; Stage = 'static'; Argv = $rowCheck + @('--selftest') },
    @{ Id = 'red-check-selftest'; Stage = 'static'; Argv = $py + @("$plan/red-check.py", '--selftest') },
    @{ Id = 'eol-check-selftest'; Stage = 'static'; Argv = $py + @("$plan/eol-check.py", '--selftest') },
    @{ Id = 'identity-selftest'; Stage = 'static'; Argv = $py + @("$plan/identity.py", '--selftest') },
    @{ Id = 'snapshot-selftest'; Stage = 'static'; Argv = $py + @("$plan/snapshot-commit.py", '--selftest', $snapSelftest) },
    @{ Id = 'py-inbox'; Stage = 'targeted'; Argv = $pytest + $inboxPy + @('--tb=short', '-q') },
    @{ Id = 'ui-capture'; Stage = 'targeted'; Cwd = 'ui'; Argv = @('npx', 'vitest', 'run', '--allowOnly=false') + $newUi + $pinUi },
    @{ Id = 'ui-tests'; Stage = 'full'; Cwd = 'ui'; Argv = @('npm', 'run', 'test') },
    @{ Id = 'py-tests'; Stage = 'full'; Argv = $pytest + @('tests/', '-x', '--tb=short', '-q') },
    @{ Id = 'ui-build'; Stage = 'full'; Cwd = 'ui'; Argv = @('npm', 'run', 'build') },
    @{ Id = 'e2e-remote'; Stage = 'full'; Argv = $rowCheck + @('remote-fresh') },
    @{ Id = 'state-render'; Stage = 'full'; Argv = $py + @('tools/meu_status.py', 'render', '--check') },
    @{ Id = 'issues-render'; Stage = 'full'; Argv = $py + @('tools/issue_triage.py', 'render', '--check') },
    @{ Id = 'identity-after'; Stage = 'identity'; Argv = $identity }
)

function Get-TestedState([string]$Receipt) {
    $line = Select-String -Path $Receipt -Pattern '^tested_state ' | Select-Object -Last 1
    if ($null -eq $line) { return $null }
    return $line.Line.Substring('tested_state '.Length).Trim()
}

for ($i = 0; $i -lt $steps.Count; $i++) {
    $step = $steps[$i]
    $receipt = "$receipts/cki-D6-$($step.Id).txt"
    $argv = $step.Argv
    if ($step.ContainsKey('Cwd')) { Set-Location (Join-Path $root $step.Cwd) }
    & rtk proxy @argv *> $receipt
    $code = $LASTEXITCODE
    Set-Location $root
    Set-Content -Path "$receipt.exit" -Value $code -Encoding ascii
    Write-Output ("{0} stage={1} exit={2} receipt={3}" -f $step.Id, $step.Stage, $code, $receipt)
    Get-Content $receipt | Select-Object -Last 6
    if ($code -eq 0 -and $step.Id -eq 'identity-after') {
        $before = Get-TestedState "$receipts/cki-D6-identity-before.txt"
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
