# Session 104 fresh-full gate (task H1-2; implementation-plan.md §Session gate).
# The shape of docs/execution/plans/2026-11-22-tray-show-and-baseline-fixes/session-gate.ps1,
# with this plan's steps: identity; the static checks (py-types, py-lint, ui-types, ui-lint,
# mcp-types, task-contract, scope-paths, line-endings, home-path, pins-unchanged, red-unchanged,
# kept, canon, row-steps and the script selftests); openapi; the fresh full suites (py-tests,
# ui-tests, mcp-tests, ui-build, state-render, issues-render); e2e-remote (the snapshot still
# binds, and row 16's run folder holds exit 0 for it); then the identity again.
# Runs from the repository root (P:/av-kit, main only per AGENTS.md §Commits). One receipt per
# id under C:/Temp/av-kit/2026-11-26-ytdlp-challenge-and-cookie-test, named ycc-D6-<id>.txt,
# with the exit code beside it in <receipt>.exit.
# Fail-fast: the first non-zero step stops the gate and every later step is printed as not_run.
# The gate also fails when tested_state differs between its start and its end.
# Read-only apart from the receipts, the temp folder and ui/out (ui-build). No step starts
# Electron on this PC (the E2E evidence is row 16's mini-air run), reaches YouTube or dispatches
# a model. Nothing is excused: py-tests deselects nothing, and no step excuses a test by name.
# scope-paths binds content, not HEAD (task.md S4; D-1472).
$ErrorActionPreference = 'Continue'
$root = (git rev-parse --show-toplevel).Trim()
Set-Location $root
$plan = 'docs/execution/plans/2026-11-26-ytdlp-challenge-and-cookie-test'
$receipts = 'C:/Temp/av-kit/2026-11-26-ytdlp-challenge-and-cookie-test'
$env:RECEIPTS_DIR = 'C:/Temp/av-kit'
$env:PYTHONIOENCODING = 'utf-8'
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:ELECTRON_RUN_AS_NODE = $null
$tmp = 'C:\Temp\av-kit\s104-tmp'
New-Item -ItemType Directory -Force -Path $tmp | Out-Null
$env:TMP = $tmp
$env:TEMP = $tmp

Write-Output 'baseline ui failures excused: [] (ui-tests excuses nothing)'
Write-Output 'baseline py failures excused: [] (py-tests deselects nothing)'

$py = @('uv', 'run', '--no-sync', 'python')
$identity = $py + @("$plan/identity.py")
$rowCheck = $py + @("$plan/row-check.py")
$pytest = @('uv', 'run', '--no-sync', 'pytest', '-p', 'no:cacheprovider')
$planPy = @(Get-ChildItem -Path $plan -Filter '*.py' | Sort-Object Name | ForEach-Object { "$plan/$($_.Name)" })
$steps = @(
    @{ Id = 'identity-before'; Stage = 'identity'; Argv = $identity },
    @{ Id = 'py-types'; Stage = 'static'; Argv = @('uv', 'run', '--no-sync', 'pyright', 'packages/') },
    @{ Id = 'py-lint'; Stage = 'static'; Argv = @('uv', 'run', '--no-sync', 'ruff', 'check', 'packages/', 'tests/') + $planPy },
    @{ Id = 'py-format'; Stage = 'static'; Argv = @('uv', 'run', '--no-sync', 'ruff', 'format', '--check') + $planPy },
    @{ Id = 'ui-types'; Stage = 'static'; Cwd = 'ui'; Argv = @('npm', 'run', 'typecheck') },
    @{ Id = 'ui-lint'; Stage = 'static'; Cwd = 'ui'; Argv = @('npm', 'run', 'lint') },
    @{ Id = 'mcp-types'; Stage = 'static'; Argv = @('npm', '--prefix', 'mcp-server', 'run', 'typecheck') },
    @{ Id = 'task-contract'; Stage = 'static'; Argv = $py + @('tools/lint_task_contract.py', '--allowed-builder-classes', 'avkit_builder,avkit_coordinator,avkit_verifier', '--task', "$plan/task.md") },
    @{ Id = 'scope-paths'; Stage = 'static'; Argv = $rowCheck + @('scope-paths') },
    @{ Id = 'line-endings'; Stage = 'static'; Argv = $py + @("$plan/eol-check.py") },
    @{ Id = 'home-path'; Stage = 'static'; Argv = $py + @('tools/check_home_path.py') },
    @{ Id = 'pins-unchanged'; Stage = 'static'; Argv = $rowCheck + @('pins-unchanged') },
    @{ Id = 'red-unchanged'; Stage = 'static'; Argv = $rowCheck + @('red-unchanged') },
    @{ Id = 'kept'; Stage = 'static'; Argv = $rowCheck + @('kept') },
    @{ Id = 'canon'; Stage = 'static'; Argv = $rowCheck + @('canon') },
    @{ Id = 'row-steps'; Stage = 'static'; Argv = $rowCheck + @('steps') },
    @{ Id = 'row-check-selftest'; Stage = 'static'; Argv = $rowCheck + @('--selftest') },
    @{ Id = 'red-check-selftest'; Stage = 'static'; Argv = $py + @("$plan/red-check.py", '--selftest') },
    @{ Id = 'eol-check-selftest'; Stage = 'static'; Argv = $py + @("$plan/eol-check.py", '--selftest') },
    @{ Id = 'proof-selftest'; Stage = 'static'; Argv = $py + @("$plan/proof-extract.py", '--selftest') },
    @{ Id = 'identity-selftest'; Stage = 'static'; Argv = $py + @("$plan/identity.py", '--selftest') },
    @{ Id = 'openapi'; Stage = 'openapi'; Argv = $py + @('tools/export_openapi.py', '--check', 'openapi.committed.json') },
    @{ Id = 'py-tests'; Stage = 'full'; Argv = $pytest + @('tests/', '--tb=short', '-q') },
    @{ Id = 'ui-tests'; Stage = 'full'; Cwd = 'ui'; Argv = @('npm', 'run', 'test') },
    @{ Id = 'mcp-tests'; Stage = 'full'; Argv = @('npm', '--prefix', 'mcp-server', 'test') },
    @{ Id = 'ui-build'; Stage = 'full'; Cwd = 'ui'; Argv = @('npm', 'run', 'build') },
    @{ Id = 'state-render'; Stage = 'full'; Argv = $py + @('tools/meu_status.py', 'render', '--check') },
    @{ Id = 'issues-render'; Stage = 'full'; Argv = $py + @('tools/issue_triage.py', 'render', '--check') },
    @{ Id = 'e2e-snapshot'; Stage = 'e2e-remote'; Argv = $py + @("$plan/snapshot-commit.py", '--verify', "$receipts/ycc-snapshot.json") },
    @{ Id = 'e2e-remote'; Stage = 'e2e-remote'; Argv = $rowCheck + @('e2e-result') },
    @{ Id = 'identity-after'; Stage = 'identity'; Argv = $identity }
)

function Get-TestedState([string]$Receipt) {
    $line = Select-String -Path $Receipt -Pattern '^tested_state ' | Select-Object -Last 1
    if ($null -eq $line) { return $null }
    return $line.Line.Substring('tested_state '.Length).Trim()
}

for ($i = 0; $i -lt $steps.Count; $i++) {
    $step = $steps[$i]
    $receipt = "$receipts/ycc-D6-$($step.Id).txt"
    $argv = $step.Argv
    if ($step.ContainsKey('Cwd')) { Set-Location (Join-Path $root $step.Cwd) }
    & rtk proxy @argv *> $receipt
    $code = $LASTEXITCODE
    Set-Location $root
    Set-Content -Path "$receipt.exit" -Value $code -Encoding ascii
    Write-Output ("{0} stage={1} exit={2} receipt={3}" -f $step.Id, $step.Stage, $code, $receipt)
    Get-Content $receipt | Select-Object -Last 6
    if ($code -eq 0 -and $step.Id -eq 'identity-after') {
        $before = Get-TestedState "$receipts/ycc-D6-identity-before.txt"
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
