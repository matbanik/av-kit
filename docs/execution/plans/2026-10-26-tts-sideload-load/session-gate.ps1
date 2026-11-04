# Session 42 fresh-full gate (task row 8 and H1-2; implementation-plan.md Verification Plan §4-§5).
# Adapted from Session 40's gate (docs/execution/plans/2026-10-24-gui-theme-path-fields/session-gate.ps1)
# for a Python-only session (PRODUCT_SCOPE, D-122): the ui, mcp and Electron D6 ids are not run,
# apart from the two Vitest canon suites that read the state files row 9 writes (state-canon).
# Runs PROFILE D6 (.agent/docs/commands.md:190-210) from the repository root (D-120) in stage order:
# input identity, then every static check (D6 static ids and SCOPE_CHECK), then the full
# behavioural suites, then the input identity again. One receipt per id under C:/Temp/av-kit.
# Fail-fast: the first non-zero step stops the gate and every later step is printed as not_run.
# The gate also fails when tested_state differs between its start and its end (an input changed
# while it ran). Read-only apart from the receipts. Exit = the first failing step's code.
# py-tests runs the whole suite (no -x) and applies the plan's baseline rule
# (implementation-plan.md §Verification Plan 1): pytest exit 1 passes only when every FAILED id
# is an expected environmental packaging id that also FAILED in row 0's s42-base-py.txt, and
# nothing ERRORs. Any other failure, or any other pytest exit code, fails the step.
$ErrorActionPreference = 'Continue'
$root = (git rev-parse --show-toplevel).Trim()
Set-Location $root
$plan = 'docs/execution/plans/2026-10-26-tts-sideload-load'
$receipts = 'C:/Temp/av-kit'
$base = (Get-Content "$plan/baseline.sha").Trim()

$scopePaths = @"
import subprocess, sys
allowed = {
    'packages/core/src/avkit_core/services/models.py',
    'packages/infrastructure/src/avkit_infra/tts/adapter.py',
    'packages/infrastructure/src/avkit_infra/tts/assets.py',
    'tests/unit/test_services.py',
    'tests/integration/test_tts_device_resolution.py',
    'tests/integration/test_tts_assets.py',
    'tests/integration/test_tts_models.py',
    'docs/build-plan/03-service-layer.md',
    'docs/BUILD_PLAN.md',
    '.agent/context/meu-status.yaml',
    '.agent/context/meu-registry.md',
    '.agent/context/current-focus.md',
    '.agent/context/known-issues.yaml',
    '.agent/context/known-issues.md',
    '.agent/context/grouping/2026-10-17-gui-shell-and-tts-sideload-session-grouping.md',
    'docs/execution/metrics.md',
}
prefixes = ('$plan/', '.agent/context/handoffs/2026-10-26-tts-sideload-load-', 'docs/execution/reflections/2026-10-26-tts-sideload-load-')
# --no-renames: a rename reports both its source deletion and its destination, so moving an
# out-of-scope file into an allowed path still shows the out-of-scope deletion.
# -z: NUL-separated, so a path with spaces or quoting is one entry.
def paths(*args):
    raw = subprocess.run(['git', *args], capture_output=True, check=True).stdout.decode('utf-8')
    return [p for p in raw.split('\0') if p]
out = paths('diff', '--no-renames', '--name-only', '-z', '$base')
out += paths('ls-files', '--others', '--exclude-standard', '-z')
extra = sorted({p for p in out if p not in allowed and not p.startswith(prefixes)})
print('changed paths:', len(set(out)), 'outside scope:', extra)
sys.exit(1 if extra else 0)
"@

# walkthrough.md §Baseline (s42-base-py), the Sessions 35, 36, 39 and 40 set: the environmental
# packaging tests that need the gitignored pack tree and ffmpeg binaries, plus Session 40's EC-1
# id. They are excused only if row 0 really saw them fail.
$expectedBaselinePyFailed = @(
    'tests/unit/test_packaging_backend.py::test_pack_dist_onedir_layout[AC-24.10]',
    'tests/unit/test_packaging_installer.py::test_nsis_pack_check_script[AC-25.10]',
    'tests/unit/test_packaging_installer.py::test_mcp_snippet_keys[AC-25.7]'
)
# An expected id is excused only when row 0's baseline receipt really shows it FAILED: a missing
# receipt, or an id that passed at baseline, excuses nothing.
$baseReceipt = "$receipts/s42-base-py.txt"
$observedBaseFailed = @()
if (Test-Path $baseReceipt) {
    $observedBaseFailed = @(Select-String -Path $baseReceipt -Pattern '^FAILED (\S+)' | ForEach-Object { $_.Matches[0].Groups[1].Value })
}
$baselinePyFailed = @($expectedBaselinePyFailed | Where-Object { $observedBaseFailed -contains $_ })
Write-Output ("baseline py failures excused: [{0}] (receipt {1})" -f ($baselinePyFailed -join ', '), $baseReceipt)

$identity = @('uv', 'run', 'python', "$plan/identity.py")
$steps = @(
    @{ Id = 'identity-before'; Stage = 'identity'; Argv = $identity },
    @{ Id = 'py-types'; Stage = 'static'; Argv = @('uv', 'run', 'pyright', 'packages/') },
    @{ Id = 'py-lint'; Stage = 'static'; Argv = @('uv', 'run', 'ruff', 'check', 'packages/', 'tests/') },
    @{ Id = 'task-contract'; Stage = 'static'; Argv = @('uv', 'run', 'python', 'tools/lint_task_contract.py', '--allowed-builder-classes', 'avkit_builder,avkit_coordinator,avkit_verifier', '--task', "$plan/task.md") },
    @{ Id = 'scope-paths'; Stage = 'static'; Argv = @('uv', 'run', 'python', '-c', $scopePaths) },
    @{ Id = 'py-tests'; Stage = 'full'; Argv = @('uv', 'run', 'pytest', 'tests/', '--tb=short', '-q', '-rfE') },
    @{ Id = 'openapi'; Stage = 'full'; Argv = @('uv', 'run', 'python', 'tools/export_openapi.py', '--check', 'openapi.committed.json') },
    @{ Id = 'state-render'; Stage = 'full'; Argv = @('uv', 'run', 'python', 'tools/meu_status.py', 'render', '--check') },
    # The two Vitest suites that read meu-status.yaml and the rendered BUILD_PLAN.md, which row 9 writes.
    @{ Id = 'state-canon'; Stage = 'full'; Argv = @('npm', '--prefix', 'ui', 'run', 'test', '--', 'tests/unit/layout-canon.test.ts', 'tests/unit/queue-canon.test.ts') },
    @{ Id = 'identity-after'; Stage = 'identity'; Argv = $identity }
)

function Get-TestedState([string]$Receipt) {
    $line = Select-String -Path $Receipt -Pattern '^tested_state ' | Select-Object -Last 1
    if ($null -eq $line) { return $null }
    return $line.Line.Substring('tested_state '.Length).Trim()
}

for ($i = 0; $i -lt $steps.Count; $i++) {
    $step = $steps[$i]
    $receipt = "$receipts/s42-D6-$($step.Id).txt"
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
    if ($code -eq 0 -and $step.Id -eq 'identity-after') {
        $before = Get-TestedState "$receipts/s42-D6-identity-before.txt"
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
