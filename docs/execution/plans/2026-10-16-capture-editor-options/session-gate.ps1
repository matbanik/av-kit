# Session 37 fresh-full gate (task row 8 and H1-2; implementation-plan.md Verification Plan §4-§5).
# Runs PROFILE D6 (.agent/docs/commands.md:190-210) from the worktree root in stage order:
# input identity, then every static check (D6 static ids and SCOPE_CHECK), then the full
# behavioural suites, then the runtime Electron runs, then the input identity again. One
# receipt per id under C:/Temp/av-kit. Fail-fast: the first non-zero step stops the gate and
# every later step is printed as not_run. The gate also fails when tested_state differs
# between its start and its end (an input changed while it ran). Read-only apart from the
# receipts. Exit = the first failing step's code.
# Session 37 changes no Python, API or MCP source: py-*, mcp-* and openapi run as no-drift checks.
# py-tests runs the whole suite (no -x) and applies the plan's baseline rule
# (implementation-plan.md §Baseline): pytest exit 1 passes only when every FAILED id is in
# $plan/baseline-py-failed.txt (written by task row 0, bound by identity.py) and nothing ERRORs.
# Any other failure, or any other pytest exit code, fails the step.
# ui-tests applies the same rule (A-4, walkthrough.md §Gate): Vitest exit 1 passes only when
# ui-baseline-rule.ps1 finds every failed test listed in $plan/baseline-ui-failed.txt (AC-41.3,
# known issue QUEUE-PILL-TOKEN-DRIFT), the failed count agrees and nothing is unhandled.
$ErrorActionPreference = 'Continue'
$root = (git rev-parse --show-toplevel).Trim()
Set-Location $root
$plan = 'docs/execution/plans/2026-10-16-capture-editor-options'
$receipts = 'C:/Temp/av-kit'
# lint_task_contract.py recognises the instantiated receipt paths only through RECEIPTS_DIR and
# fails closed (exit 3) when it is unset, which no user or machine scope sets on this host.
$env:RECEIPTS_DIR = $receipts
$env:ELECTRON_RUN_AS_NODE = $null
# RENDERER_PIN: main loads ELECTRON_RENDERER_URL instead of the built renderer whenever it is set
# (ui/src/main/index.ts:504), and the E2E launch passes process.env through.
$env:ELECTRON_RENDERER_URL = $null
$base = (Get-Content "$plan/baseline.sha").Trim()

$scopePaths = @"
import subprocess, sys
allowed = {
    'ui/src/renderer/src/features/capture/capture-scrub.ts',
    'ui/src/renderer/src/features/capture/CaptureScrubField.tsx',
    'ui/src/renderer/src/features/capture/capture-color.ts',
    'ui/src/renderer/src/features/capture/capture-toolbar.ts',
    'ui/src/renderer/src/features/capture/capture-help-content.ts',
    'ui/src/renderer/src/features/capture/CaptureViewport.tsx',
    'ui/src/renderer/src/features/capture/CapturePage.tsx',
    'ui/tests/unit/capture-scrub.test.ts',
    'ui/tests/unit/capture-color.test.ts',
    'ui/tests/unit/capture-toolbar.test.ts',
    'ui/tests/unit/capture-help-content.test.ts',
    'ui/tests/unit/capture-page.behavior.test.ts',
    'ui/tests/unit/icon-hints.test.ts',
    'ui/tests/e2e/capture-inbox.test.ts',
    'ui/tests/e2e/test-ids.ts',
    'docs/build-plan/09-screenshot-capture.md',
    'docs/build-plan/gui-actions-index.md',
    'docs/build-plan/build-priority-matrix.md',
    'docs/BUILD_PLAN.md',
    '.agent/context/meu-status.yaml',
    '.agent/context/meu-registry.md',
    '.agent/context/current-focus.md',
    '.agent/context/known-issues.yaml',
    '.agent/context/known-issues.md',
    'docs/execution/metrics.md',
}
prefixes = ('$plan/', '.agent/context/handoffs/2026-10-16-capture-editor-options-', 'docs/execution/reflections/2026-10-16-capture-editor-options-')
# --no-renames lists both sides of a move, so an allowed destination cannot hide an out-of-scope source.
out = subprocess.run(['git', 'diff', '--name-only', '--no-renames', '-z', '$base'], capture_output=True, text=True, check=True).stdout.split('\0')
out += subprocess.run(['git', 'ls-files', '--others', '--exclude-standard', '-z'], capture_output=True, text=True, check=True).stdout.split('\0')
out = [p for p in out if p]
extra = sorted({p for p in out if p not in allowed and not p.startswith(prefixes)})
print('changed paths:', len(set(out)), 'outside scope:', extra)
sys.exit(1 if extra else 0)
"@

# walkthrough.md §Baseline (s37-base-py): the failed ids row 0 recorded, one per line. Expected to be
# Session 36's and 39's environmental packaging pair (the gitignored pack tree and ffmpeg binaries).
$baselinePyFailed = @(Get-Content "$plan/baseline-py-failed.txt" | ForEach-Object { $_.Trim() } | Where-Object { $_ })

$identity = @('uv', 'run', 'python', "$plan/identity.py")
# The Electron suite's gitignored prerequisites, which a fresh worktree does not have: the
# isolated primitive harness (AC-51.7; Session 31 validate-task.ps1 ui-harness-build) and the
# deterministic region-picker stub (capture-picker.test.ts names build:picker-stub).
$harnessBuild = "`$env:AVKIT_PRIMITIVE_HARNESS_BUILD='1'; npm --prefix ui run build -- --outDir '$root/ui/out-e2e'; exit `$LASTEXITCODE"
$steps = @(
    @{ Id = 'identity-before'; Stage = 'identity'; Argv = $identity },
    @{ Id = 'py-types'; Stage = 'static'; Argv = @('uv', 'run', 'pyright', 'packages/') },
    @{ Id = 'py-lint'; Stage = 'static'; Argv = @('uv', 'run', 'ruff', 'check', 'packages/', 'tests/') },
    @{ Id = 'ui-types'; Stage = 'static'; Argv = @('npm', '--prefix', 'ui', 'run', 'typecheck') },
    @{ Id = 'ui-lint'; Stage = 'static'; Argv = @('npm', '--prefix', 'ui', 'run', 'lint') },
    @{ Id = 'mcp-types'; Stage = 'static'; Argv = @('npm', '--prefix', 'mcp-server', 'run', 'typecheck') },
    @{ Id = 'task-contract'; Stage = 'static'; Argv = @('uv', 'run', 'python', 'tools/lint_task_contract.py', '--allowed-builder-classes', 'avkit_builder,avkit_coordinator,avkit_verifier', '--task', "$plan/task.md") },
    @{ Id = 'scope-paths'; Stage = 'static'; Argv = @('uv', 'run', 'python', '-c', $scopePaths) },
    @{ Id = 'py-tests'; Stage = 'full'; Argv = @('uv', 'run', 'pytest', 'tests/', '--tb=short', '-q', '-rfE') },
    @{ Id = 'ui-tests'; Stage = 'full'; Argv = @('npm', '--prefix', 'ui', 'run', 'test') },
    # G-1 (Session 39 S2 decision 2026-10-16): build before the tests, which load mcp-server/dist (RULE-1).
    @{ Id = 'mcp-build'; Stage = 'full'; Argv = @('npm', '--prefix', 'mcp-server', 'run', 'build') },
    @{ Id = 'mcp-tests'; Stage = 'full'; Argv = @('npm', '--prefix', 'mcp-server', 'run', 'test') },
    @{ Id = 'ui-build'; Stage = 'full'; Argv = @('npm', '--prefix', 'ui', 'run', 'build') },
    @{ Id = 'ui-harness-build'; Stage = 'full'; Argv = @('pwsh', '-NoProfile', '-Command', $harnessBuild) },
    @{ Id = 'ui-picker-stub'; Stage = 'full'; Argv = @('npm', '--prefix', 'ui', 'run', 'build:picker-stub') },
    @{ Id = 'openapi'; Stage = 'full'; Argv = @('uv', 'run', 'python', 'tools/export_openapi.py', '--check', 'openapi.committed.json') },
    @{ Id = 'state-render'; Stage = 'full'; Argv = @('uv', 'run', 'python', 'tools/meu_status.py', 'render', '--check') },
    @{ Id = 'ui-electron'; Stage = 'runtime'; Argv = @('npm', '--prefix', 'ui', 'run', 'test:e2e') },
    @{ Id = 'e2e-repeat'; Stage = 'runtime'; Argv = @('npm', '--prefix', 'ui', 'run', 'test:e2e', '--', 'tests/e2e/capture-inbox.test.ts', '--grep', 'AC-85.10|AC-86.3|AC-87.6', '--repeat-each=10') },
    @{ Id = 'identity-npm'; Stage = 'identity'; Argv = @('npm', '--prefix', 'ui', 'ls', 'electron', '@playwright/test') },
    @{ Id = 'identity-after'; Stage = 'identity'; Argv = $identity }
)

function Get-TestedState([string]$Receipt) {
    $line = Select-String -Path $Receipt -Pattern '^tested_state ' | Select-Object -Last 1
    if ($null -eq $line) { return $null }
    return $line.Line.Substring('tested_state '.Length).Trim()
}

for ($i = 0; $i -lt $steps.Count; $i++) {
    $step = $steps[$i]
    $receipt = "$receipts/s37-D6-$($step.Id).txt"
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
            Write-Output 'py-tests: every failure is in baseline-py-failed.txt; not a regression'
            $code = 0
        }
    }
    if ($code -eq 1 -and $step.Id -eq 'ui-tests') {
        & pwsh -NoProfile -File "$plan/ui-baseline-rule.ps1" -Receipt $receipt -Baseline "$plan/baseline-ui-failed.txt"
        if ($LASTEXITCODE -eq 0) { $code = 0 }
    }
    if ($code -eq 0 -and $step.Id -eq 'identity-after') {
        $before = Get-TestedState "$receipts/s37-D6-identity-before.txt"
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
