# Session 41 fresh-full gate (task row 6 and H1-2; implementation-plan.md Verification Plan §4-§5).
# Runs PROFILE D6 (.agent/docs/commands.md:190-210) from the repository root (P:/av-kit, D-133)
# in stage order: input identity, then every static check (D6 static ids and SCOPE_CHECK), then
# the full behavioural suites, then the runtime Electron runs, then the input identity again.
# One receipt per id under C:/Temp/av-kit. Fail-fast: the first non-zero step stops the gate and
# every later step is printed as not_run. The gate also fails when tested_state differs between
# its start and its end (an input changed while it ran). Read-only apart from the receipts.
# Exit = the first failing step's code.
# py-tests runs the whole suite (no -x) and applies the plan's baseline rule
# (implementation-plan.md §Verification Plan 1): pytest exit 1 passes only when every FAILED id
# is an expected environmental packaging id that also FAILED in row 0's s41-base-py.txt, and
# nothing ERRORs. Any other failure, or any other pytest exit code, fails the step.
# ui-tests keeps the same rule with an empty expected set: QUEUE-PILL-TOKEN-DRIFT is resolved
# (known-issues.yaml), so any Vitest failure fails the step.
$ErrorActionPreference = 'Continue'
$root = (git rev-parse --show-toplevel).Trim()
Set-Location $root
$plan = 'docs/execution/plans/2026-10-26-gui-keyboard-palette'
$receipts = 'C:/Temp/av-kit'
# lint_task_contract.py recognises the instantiated receipt paths only through RECEIPTS_DIR and
# fails closed (exit 3) when it is unset, which no user or machine scope sets on this host.
$env:RECEIPTS_DIR = $receipts
$env:ELECTRON_RUN_AS_NODE = $null
$base = (Get-Content "$plan/baseline.sha").Trim()

$scopePaths = @"
import subprocess, sys
allowed = {
    'ui/src/renderer/src/registry/shortcuts.ts',
    'ui/src/renderer/src/registry/command-state.ts',
    'ui/src/renderer/src/registry/appearance.ts',
    'ui/src/renderer/src/registry/commandRegistry.ts',
    'ui/src/renderer/src/components/CommandPalette.tsx',
    'ui/src/renderer/src/components/layout/AppShell.tsx',
    'ui/src/renderer/src/components/layout/NavRail.tsx',
    'ui/src/renderer/src/components/layout/Header.tsx',
    'ui/src/renderer/src/components/help/HelpCard.tsx',
    'ui/src/renderer/src/features/capture/ToolbarIconButton.tsx',
    'ui/src/renderer/src/features/capture/CapturePage.tsx',
    'ui/src/renderer/src/features/capture/CaptureViewport.tsx',
    'ui/src/renderer/src/features/capture/capture-commands.ts',
    'ui/src/renderer/src/features/settings/useSettingsPage.ts',
    'ui/src/renderer/src/features/settings/SettingsPage.tsx',
    'ui/src/renderer/src/features/downloader/download-commands.ts',
    'ui/src/renderer/src/features/downloader/DownloaderPage.tsx',
    'ui/src/renderer/src/features/converter/convert-commands.ts',
    'ui/src/renderer/src/features/converter/ConvertPage.tsx',
    'ui/src/renderer/src/features/transcript/TranscriptPage.tsx',
    'ui/src/renderer/src/features/tts/TTSPage.tsx',
    'ui/src/renderer/src/features/tts/tts-commands.ts',
    'ui/tests/unit/shortcuts.test.ts',
    'ui/tests/unit/palette-curation.test.tsx',
    'ui/tests/unit/common-shortcuts.test.tsx',
    'ui/tests/unit/fixtures/chord-table.ts',
    'ui/tests/unit/helpers/bound-hint.ts',
    'ui/tests/unit/app-shell-wiring.test.ts',
    'ui/tests/unit/capture-page.test.ts',
    'ui/tests/unit/capture-page.behavior.test.ts',
    'ui/tests/unit/convert-page.test.ts',
    'ui/tests/unit/gui-actions-audit.test.ts',
    'ui/tests/unit/downloader-page.behavior.test.ts',
    'ui/tests/unit/convert-page.behavior.test.ts',
    'ui/tests/unit/tts-page.behavior.test.ts',
    'ui/tests/unit/transcript-page.behavior.test.ts',
    'ui/tests/unit/settings-page.test.ts',
    'ui/tests/e2e/keyboard-shortcuts.test.ts',
    'ui/tests/e2e/test-ids.ts',
    'ui/tests/e2e/download-queue.test.ts',
    'ui/tests/e2e/transcript-queue.test.ts',
    'ui/tests/e2e/convert-queue.test.ts',
    'ui/tests/e2e/capture-inbox.test.ts',
    'ui/tests/e2e/settings.test.ts',
    'docs/build-plan/06-gui.md',
    'docs/build-plan/gui-actions-index.md',
    'docs/BUILD_PLAN.md',
    '.agent/context/meu-status.yaml',
    '.agent/context/meu-registry.md',
    '.agent/context/current-focus.md',
    '.agent/context/known-issues.yaml',
    '.agent/context/known-issues.md',
    '.agent/context/grouping/2026-10-17-gui-shell-and-tts-sideload-session-grouping.md',
    'docs/execution/metrics.md',
}
prefixes = ('$plan/', '.agent/context/handoffs/2026-10-26-gui-keyboard-palette-', 'docs/execution/reflections/2026-10-26-gui-keyboard-palette-')
# --no-renames: a rename reports both its source deletion and its destination, so moving an
# out-of-scope file into an allowed path still shows the out-of-scope deletion (round 1 F2).
# -z: NUL-separated, so a path with spaces or quoting is one entry.
def paths(*args):
    raw = subprocess.run(['git', *args], capture_output=True, check=True).stdout.decode('utf-8')
    return [p for p in raw.split('\0') if p]
out = paths('diff', '--no-renames', '--name-only', '-z', '$base')
out += paths('ls-files', '--others', '--exclude-standard', '-z')
extra = sorted({p for p in out if p not in allowed and not p.startswith(prefixes)})
# S8: this session runs alone on main; HEAD must still be the row 0 baseline.
head = subprocess.run(['git', 'rev-parse', 'HEAD'], capture_output=True, text=True, check=True).stdout.strip()
moved = head != '$base'
print('changed paths:', len(set(out)), 'outside scope:', extra, 'head:', head, 'head moved (S8):', moved)
sys.exit(1 if extra or moved else 0)
"@

# walkthrough.md §Baseline (s41-base-py), the Sessions 35, 36, 39 and 40 set: the environmental packaging tests that need the
# gitignored pack tree and ffmpeg binaries. They are excused only if row 0 really saw them fail.
$expectedBaselinePyFailed = @(
    'tests/unit/test_packaging_backend.py::test_pack_dist_onedir_layout[AC-24.10]',
    'tests/unit/test_packaging_installer.py::test_nsis_pack_check_script[AC-25.10]',
    # Session 40 EC-1 (known issue PACKAGING-MCP-SNIPPET-TOKEN-STALE): fails against the committed mcp.json.example, outside PRODUCT_SCOPE.
    'tests/unit/test_packaging_installer.py::test_mcp_snippet_keys[AC-25.7]',
    # Session 41 EC-2: bb481ec added two lines to AGENTS.md, so the framework-adoption rule map refuses
    # (`REFUSE: rule map identity mismatch: AGENTS.md`). HEAD state outside PRODUCT_SCOPE. The last two ids hold a
    # space, so they are listed as '^FAILED (\S+)' captures them (cut at the first space), at row 0 and at the gate alike.
    'tests/tooling/test_framework_adoption.py::test_review_pipeline_governance_static_oracles[none]',
    'tests/tooling/test_framework_adoption.py::test_governance_preservation_and_routing_inventory[history]',
    'tests/tooling/test_framework_adoption.py::test_registry_contract_generic_class_census[Resolve-AgentModel',
    'tests/tooling/test_framework_adoption.py::test_registry_contract_generic_class_census[builder_model'
)
# An expected id is excused only when row 0's baseline receipt really shows it FAILED (round 1 Q7):
# a missing receipt, or an id that passed at baseline, excuses nothing.
$baseReceipt = "$receipts/s41-base-py.txt"
$observedBaseFailed = @()
if (Test-Path $baseReceipt) {
    $observedBaseFailed = @(Select-String -Path $baseReceipt -Pattern '^FAILED (\S+)' | ForEach-Object { $_.Matches[0].Groups[1].Value })
}
$baselinePyFailed = @($expectedBaselinePyFailed | Where-Object { $observedBaseFailed -contains $_ })
Write-Output ("baseline py failures excused: [{0}] (receipt {1})" -f ($baselinePyFailed -join ', '), $baseReceipt)

$ansi = [regex]'\x1b\[[0-9;]*m'
function Get-VitestFailIds([string]$Receipt) {
    return @(Get-Content $Receipt | ForEach-Object { $ansi.Replace($_, '') } | Where-Object { $_ -match '^\s*FAIL\s+\S' } | ForEach-Object { ($_ -replace '^\s*FAIL\s+', '').Trim() } | Sort-Object -Unique)
}
# Empty: QUEUE-PILL-TOKEN-DRIFT is resolved, so no Vitest failure is excused.
$expectedBaselineUiFailed = @()
$baseUiReceipt = "$receipts/s41-base-ui.txt"
$observedBaseUiFailed = @()
if (Test-Path $baseUiReceipt) { $observedBaseUiFailed = Get-VitestFailIds $baseUiReceipt }
$baselineUiFailed = @($expectedBaselineUiFailed | Where-Object { $observedBaseUiFailed -contains $_ })
Write-Output ("baseline ui failures excused: [{0}] (receipt {1})" -f ($baselineUiFailed -join ' | '), $baseUiReceipt)

$identity = @('uv', 'run', 'python', "$plan/identity.py")
# The Electron suite's gitignored prerequisites: the isolated primitive harness (AC-51.7) and the
# deterministic region-picker stub (capture-picker.test.ts names build:picker-stub). The full
# Electron suite runs because AppShell, the command registry and the palette are on every page:
# it is regression evidence for every page, not only the five AC specs.
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
    # G-1 (S2 decision 2026-10-16): build before the tests, which load mcp-server/dist (RULE-1).
    @{ Id = 'mcp-build'; Stage = 'full'; Argv = @('npm', '--prefix', 'mcp-server', 'run', 'build') },
    @{ Id = 'mcp-tests'; Stage = 'full'; Argv = @('npm', '--prefix', 'mcp-server', 'run', 'test') },
    @{ Id = 'ui-build'; Stage = 'full'; Argv = @('npm', '--prefix', 'ui', 'run', 'build') },
    @{ Id = 'ui-harness-build'; Stage = 'full'; Argv = @('pwsh', '-NoProfile', '-Command', $harnessBuild) },
    @{ Id = 'ui-picker-stub'; Stage = 'full'; Argv = @('npm', '--prefix', 'ui', 'run', 'build:picker-stub') },
    @{ Id = 'openapi'; Stage = 'full'; Argv = @('uv', 'run', 'python', 'tools/export_openapi.py', '--check', 'openapi.committed.json') },
    @{ Id = 'state-render'; Stage = 'full'; Argv = @('uv', 'run', 'python', 'tools/meu_status.py', 'render', '--check') },
    @{ Id = 'ui-electron'; Stage = 'runtime'; Argv = @('npm', '--prefix', 'ui', 'run', 'test:e2e') },
    @{ Id = 'e2e-repeat'; Stage = 'runtime'; Argv = @('npm', '--prefix', 'ui', 'run', 'test:e2e', '--', 'tests/e2e/keyboard-shortcuts.test.ts', 'tests/e2e/download-queue.test.ts', 'tests/e2e/convert-queue.test.ts', 'tests/e2e/capture-inbox.test.ts', 'tests/e2e/settings.test.ts', '--grep', 'AC-95|AC-96|AC-97', '--repeat-each=10') },
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
    $receipt = "$receipts/s41-D6-$($step.Id).txt"
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
    if ($code -eq 1 -and $step.Id -eq 'ui-tests') {
        $plain = @(Get-Content $receipt | ForEach-Object { $ansi.Replace($_, '') })
        $failed = Get-VitestFailIds $receipt
        $summary = @($plain | Where-Object { $_ -match '^\s*Tests\s+\d+ failed' } | ForEach-Object { [int]([regex]::Match($_, 'Tests\s+(\d+) failed').Groups[1].Value) })
        $summaryFailed = if ($summary.Count -gt 0) { $summary[-1] } else { -1 }
        $unhandled = @($plain | Where-Object { $_ -match 'Unhandled (Error|Rejection)|^\s*Errors\s+\d+ error' })
        $outside = @($failed | Where-Object { $baselineUiFailed -notcontains $_ })
        Write-Output ("ui-tests baseline rule: failed={0} summary_failed={1} outside_baseline=[{2}] unhandled={3}" -f $failed.Count, $summaryFailed, ($outside -join ' | '), $unhandled.Count)
        if ($failed.Count -gt 0 -and $failed.Count -eq $summaryFailed -and $outside.Count -eq 0 -and $unhandled.Count -eq 0) {
            Write-Output 'ui-tests: every failure is in the row 0 baseline failed set; not a regression'
            $code = 0
        }
    }
    if ($code -eq 0 -and $step.Id -eq 'identity-after') {
        $before = Get-TestedState "$receipts/s41-D6-identity-before.txt"
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
