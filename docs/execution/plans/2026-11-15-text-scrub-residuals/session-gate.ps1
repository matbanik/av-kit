# Text scrub residuals fresh-full gate (task H1-2; implementation-plan.md §Session gate).
# The shape of docs/execution/plans/2026-11-15-closeout-record-once/session-gate.ps1, with this
# plan's steps: identity before; then py-lint, py-format (the seven changed or new Python
# files), py-types, the task contract, scope-paths and line-endings (scope-check.py, D-929) and
# red-check's selftest; then the MEU-147 tests (the new file with test_transcript_metadata.py,
# and the adapter's -k ac_122 run: AC-147.1 to AC-147.6), the MEU-148 tests (the new file with
# no skip, and test_services.py -k ac_119_10 as its own run: AC-148.1 to AC-148.9), the
# empty-lookup mutant on AC-148.8 with red-check on its receipt, and the scrub callers; then the
# full Python suite, the state and issue render checks and the UI canon tests; then identity
# after.
# Runs from the repository root (P:/av-kit, main only per AGENTS.md §Commits) in stage order.
# One receipt per id under C:/Temp/av-kit/text-scrub-residuals, named tsr-D6-<id>.txt.
# Fail-fast: the first non-zero step stops the gate and every later step is printed as not_run.
# The gate also fails when tested_state differs between its start and its end (an input changed
# while it ran). Read-only apart from the receipts and the temp folder, which sit outside the
# repository. Nothing here reaches the network or YouTube, and no step dispatches a model.
# Exit = the first failing step's code.
# py-tests runs the whole suite (no -x) and keeps Session 49b's baseline rule: pytest exit 1
# passes only when every FAILED id also FAILED in row 0's tsr-base-py.txt, and nothing ERRORs.
# Row 0's receipt has no FAILED id, so nothing is excused.
# meu-148-mutant must fail: it passes only when pytest exits non-zero, the receipt has a
# "failed" count and no "passed" count (no AC-148.8 test passes under the mutant). Its raw pytest
# exit code goes to tsr-D6-meu-148-mutant.txt.exit, which meu-148-mutant-check's red-check reads.
# ui-canon runs from ui/ (the canon tests read meu-status.yaml and docs/BUILD_PLAN.md, which
# row 5 changes). Skipped, per the plan: ui-lint, ui-types and ui-tests beyond ui-canon
# (nothing under ui/ changes), mcp-* (no MCP change; the MCP Python tests run in py-tests),
# e2e (no renderer or launch change), openapi (no packages/api change; H1-4) and build-record
# (no build). Each is printed with its reason and runs nothing.
$ErrorActionPreference = 'Continue'
$root = (git rev-parse --show-toplevel).Trim()
Set-Location $root
$plan = 'docs/execution/plans/2026-11-15-text-scrub-residuals'
$receipts = 'C:/Temp/av-kit/text-scrub-residuals'
# The same environment as row 0's base suite (baseline.ps1).
$env:RECEIPTS_DIR = 'C:/Temp/av-kit'
$env:PYTHONIOENCODING = 'utf-8'
$env:ELECTRON_RUN_AS_NODE = $null
$env:AGENT_MODEL_REGISTRY = $null
$env:AGENT_MODEL_REGISTRY_HOME = 'P:/.agent'
$tmp = 'C:\Temp\av-kit\text-scrub-residuals\tmp'
New-Item -ItemType Directory -Force -Path $tmp | Out-Null
$env:TMP = $tmp
$env:TEMP = $tmp

# An id is excused only when row 0's baseline receipt really shows it FAILED: a missing
# receipt excuses nothing.
$baseReceipt = "$receipts/tsr-base-py.txt"
$baselinePyFailed = @()
if (Test-Path $baseReceipt) {
    $baselinePyFailed = @(Select-String -Path $baseReceipt -Pattern '^FAILED (\S+)' | ForEach-Object { $_.Matches[0].Groups[1].Value })
}
Write-Output ("baseline py failures excused: {0} id(s) (receipt {1})" -f $baselinePyFailed.Count, $baseReceipt)

$skipped = @(
    @{ Id = 'ui-lint/ui-types/ui-tests'; Stage = 'full'; Reason = 'nothing under ui/ changes; ui-canon runs the only UI tests that read a file this session writes' },
    @{ Id = 'mcp-types/mcp-build/mcp-tests/mcp-audit'; Stage = 'full'; Reason = 'no MCP change; the MCP Python tests run inside py-tests' },
    @{ Id = 'e2e'; Stage = 'full'; Reason = 'no renderer or launch change' },
    @{ Id = 'openapi'; Stage = 'full'; Reason = 'no packages/api change (H1-4)' },
    @{ Id = 'build-record'; Stage = 'full'; Reason = 'no build' }
)
foreach ($s in $skipped) {
    Write-Output ("{0} stage={1} skipped reason={2}" -f $s.Id, $s.Stage, $s.Reason)
}

$py = @('uv', 'run', '--no-sync', 'python')
$pytest = @('uv', 'run', '--no-sync', 'pytest')
$identity = $py + @("$plan/identity.py")
$pyFiles = @(
    'packages/core/src/avkit_core/domain/download.py',
    'packages/infrastructure/src/avkit_infra/youtube/adapter.py',
    'packages/core/src/avkit_core/services/transcript.py',
    'packages/core/src/avkit_core/services/health.py',
    'packages/core/src/avkit_core/services/download.py',
    'tests/unit/test_transcript_title_cleaning.py',
    'tests/unit/test_console_home_short_form.py'
)
$steps = @(
    @{ Id = 'identity-before'; Stage = 'identity'; Argv = $identity },
    @{ Id = 'py-lint'; Stage = 'static'; Argv = @('uv', 'run', '--no-sync', 'ruff', 'check', 'packages/', 'tests/') },
    @{ Id = 'py-format'; Stage = 'static'; Argv = @('uv', 'run', '--no-sync', 'ruff', 'format', '--check') + $pyFiles },
    @{ Id = 'py-types'; Stage = 'static'; Argv = @('uv', 'run', '--no-sync', 'pyright', 'packages/') },
    @{ Id = 'task-contract'; Stage = 'static'; Argv = $py + @('tools/lint_task_contract.py', '--allowed-builder-classes', 'avkit_builder,avkit_coordinator,avkit_verifier', '--task', "$plan/task.md") },
    @{ Id = 'scope-paths'; Stage = 'static'; Argv = $py + @("$plan/scope-check.py") },
    @{ Id = 'line-endings'; Stage = 'static'; Argv = $py + @("$plan/scope-check.py", '--eol') },
    @{ Id = 'red-check-selftest'; Stage = 'static'; Argv = $py + @("$plan/red-check.py", '--selftest') },
    @{ Id = 'meu-147-tests'; Stage = 'targeted'; Argv = $pytest + @('tests/unit/test_transcript_title_cleaning.py', 'tests/unit/test_transcript_metadata.py', '--tb=short', '-q') },
    @{ Id = 'meu-147-adapter'; Stage = 'targeted'; Argv = $pytest + @('tests/integration/test_youtube_adapter.py', '-k', 'ac_122', '--tb=short', '-q') },
    @{ Id = 'meu-148-tests'; Stage = 'targeted'; Argv = $pytest + @('tests/unit/test_console_home_short_form.py', '--tb=short', '-q', '-rs'); NoSkip = $true },
    @{ Id = 'meu-148-ac119'; Stage = 'targeted'; Argv = $pytest + @('tests/unit/test_services.py', '-k', 'ac_119_10', '--tb=short', '-q') },
    @{ Id = 'meu-148-mutant'; Stage = 'targeted'; Argv = $pytest + @('-p', 'mutant_empty_lookup', 'tests/unit/test_console_home_short_form.py', '-k', 'ac_148_8', '--tb=short', '-q'); PythonPath = (Join-Path $root $plan); MustFail = $true },
    @{ Id = 'meu-148-mutant-check'; Stage = 'targeted'; Argv = $py + @("$plan/red-check.py", '--require', 'test_ac_148_8', "$receipts/tsr-D6-meu-148-mutant.txt") },
    @{ Id = 'scrub-callers'; Stage = 'targeted'; Argv = $pytest + @('tests/unit/test_download_failure_visibility.py', 'tests/unit/test_download_audio_extract.py', 'tests/unit/test_transcript_metadata.py', '--tb=short', '-q') },
    @{ Id = 'py-tests'; Stage = 'full'; Argv = $pytest + @('tests/', '--tb=short', '-q', '-rfE') },
    @{ Id = 'state-render'; Stage = 'full'; Argv = $py + @('tools/meu_status.py', 'render', '--check') },
    @{ Id = 'issues-render-check'; Stage = 'full'; Argv = $py + @('tools/issue_triage.py', 'render', '--check') },
    @{ Id = 'ui-canon'; Stage = 'full'; Argv = @('npx', 'vitest', 'run', '--allowOnly=false', 'tests/unit/layout-canon.test.ts', 'tests/unit/queue-canon.test.ts'); Cwd = 'ui' },
    @{ Id = 'identity-after'; Stage = 'identity'; Argv = $identity }
)

function Get-TestedState([string]$Receipt) {
    $line = Select-String -Path $Receipt -Pattern '^tested_state ' | Select-Object -Last 1
    if ($null -eq $line) { return $null }
    return $line.Line.Substring('tested_state '.Length).Trim()
}

for ($i = 0; $i -lt $steps.Count; $i++) {
    $step = $steps[$i]
    $receipt = "$receipts/tsr-D6-$($step.Id).txt"
    $argv = $step.Argv
    if ($step.PythonPath) { $env:PYTHONPATH = $step.PythonPath }
    if ($step.Cwd) { Set-Location (Join-Path $root $step.Cwd) }
    & rtk proxy @argv *> $receipt
    $code = $LASTEXITCODE
    Set-Location $root
    $env:PYTHONPATH = $null
    Write-Output ("{0} stage={1} exit={2} receipt={3}" -f $step.Id, $step.Stage, $code, $receipt)
    Get-Content $receipt | Select-Object -Last 6
    if ($step.MustFail) {
        # red-check reads the child exit code beside the receipt (RECEIPT.exit), as row 4 wrote it.
        Set-Content "$receipt.exit" $code
        $failedCount = Select-String -Path $receipt -Pattern '\d+ failed' -Quiet
        $passedCount = Select-String -Path $receipt -Pattern '\d+ passed' -Quiet
        Write-Output ("{0} must fail: pytest exit={1} failed_count={2} passed_count={3}" -f $step.Id, $code, $failedCount, $passedCount)
        $code = if ($code -ne 0 -and $failedCount -and -not $passedCount) { 0 } else { 1 }
    }
    if ($code -eq 0 -and $step.NoSkip) {
        if (Select-String -Path $receipt -Pattern 'skipped|SKIPPED' -Quiet) {
            Write-Output "$($step.Id): a test was skipped; every AC-148 test must run"
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
    if ($code -eq 0 -and $step.Id -eq 'identity-after') {
        $before = Get-TestedState "$receipts/tsr-D6-identity-before.txt"
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
