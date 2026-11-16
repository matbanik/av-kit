# TTS page polish fresh-full gate (task H1-2; implementation-plan.md §Session gate).
# The peers' shape (docs/execution/plans/2026-11-15-framework-small-syncs/session-gate.ps1 for the
# runner, 2026-11-08-light-accent-contrast/session-gate.ps1 for the UI and Electron steps).
# Runs from the repository root (P:/av-kit, main only per AGENTS.md §Commits) in stage order:
# input identity, then every static check, then the targeted checks, then the full suites, then
# the runtime checks, then the input identity again. One receipt per id under
# C:/Temp/av-kit/tts-page-polish, named tpp-D6-<id>.txt.
# Fail-fast: the first non-zero step stops the gate and every later step is printed as not_run.
# The gate also fails when tested_state differs between its start and its end (an input changed
# while it ran). Read-only apart from the receipts, the temp folders, ui/out (ui-build) and the
# E2E app data; all are ignored or outside the checkout. Nothing here reaches the network or
# YouTube, and no step dispatches a model.
# Exit = the first failing step's code.
# tts-py-targeted fails when its receipt shows a skip, so every name guard must run (AC-150.4 to
# AC-150.7).
# py-tests runs the whole suite (no -x) and keeps Session 49b's baseline rule: pytest exit 1
# passes only when every FAILED id also FAILED in row 0's tpp-base-py.txt, and nothing ERRORs.
# ui-tests excuses nothing.
# Skipped, per the plan: mcp-* (no MCP change; the API shape is pinned by openapi) and
# build-record (no build). Each is printed with its reason and runs nothing.
$ErrorActionPreference = 'Continue'
$root = (git rev-parse --show-toplevel).Trim()
Set-Location $root
$plan = 'docs/execution/plans/2026-11-15-tts-page-polish'
$receipts = 'C:/Temp/av-kit/tts-page-polish'
# lint_task_contract.py recognises the instantiated receipt paths only through RECEIPTS_DIR and
# fails closed (exit 3) when it is unset, which no user or machine scope sets on this host.
$env:RECEIPTS_DIR = 'C:/Temp/av-kit'
$env:PYTHONIOENCODING = 'utf-8'
# Every Electron launch breaks while this is set (memory: electron-run-as-node-blocks-playwright).
$env:ELECTRON_RUN_AS_NODE = $null
# RC1 ECN-2 (CLOSEOUT-SELFTEST-ANCESTOR-AGENT-DIR): keep pytest's temp dirs away from the home folder.
$tmp = 'C:\Temp\av-kit\tts-page-polish\tmp'
New-Item -ItemType Directory -Force -Path $tmp | Out-Null
$env:TMP = $tmp
$env:TEMP = $tmp

# An id is excused only when row 0's baseline receipt really shows it FAILED: a missing
# receipt excuses nothing.
$baseReceipt = "$receipts/tpp-base-py.txt"
$baselinePyFailed = @()
if (Test-Path $baseReceipt) {
    $baselinePyFailed = @(Select-String -Path $baseReceipt -Pattern '^FAILED (\S+)' | ForEach-Object { $_.Matches[0].Groups[1].Value })
}
Write-Output ("baseline py failures excused: {0} id(s) (receipt {1})" -f $baselinePyFailed.Count, $baseReceipt)
Write-Output 'baseline ui failures excused: [] (ui-tests excuses nothing)'

$skipped = @(
    @{ Id = 'mcp-types/mcp-build/mcp-tests/mcp-audit'; Stage = 'full'; Reason = 'no MCP change; openapi pins the API shape (AC-150.8)' },
    @{ Id = 'build-record'; Stage = 'full'; Reason = 'no build' }
)
foreach ($s in $skipped) {
    Write-Output ("{0} stage={1} skipped reason={2}" -f $s.Id, $s.Stage, $s.Reason)
}

# line-endings: each §Files Modified file keeps the kind row 0 measured (tpp-eol.txt); the new
# contrast test is LF. A file that is absent fails, except the new test before it exists.
$lineEndings = @'
import pathlib, sys
KINDS = {
    "ui/src/renderer/src/features/tts/tts-controls.ts": "CRLF",
    "ui/src/renderer/src/features/tts/TTSPage.tsx": "CRLF",
    "ui/tests/unit/tts-page.test.ts": "CRLF",
    "ui/tests/unit/tts-page.behavior.test.ts": "CRLF",
    "ui/tests/unit/queue-primitives.test.ts": "CRLF",
    "ui/tests/unit/tts-pill-contrast.test.ts": "LF",
    "tests/unit/test_tts_output_name.py": "LF",
    "docs/build-plan/03-service-layer.md": "CRLF",
    "docs/build-plan/06-gui.md": "CRLF",
    ".agent/context/known-issues.yaml": "LF",
    ".agent/context/known-issues.md": "LF",
    ".agent/context/meu-status.yaml": "LF",
    ".agent/context/meu-registry.md": "LF",
    "docs/BUILD_PLAN.md": "LF",
    ".agent/context/grouping/2026-11-15-post-rc3-triage-residuals-session-grouping.md": "LF",
    "docs/execution/metrics.md": "CRLF",
    ".agent/context/current-focus.md": "CRLF",
}
bad = 0
for path, want in KINDS.items():
    b = pathlib.Path(path).read_bytes()
    crlf = b.count(b"\r\n")
    lf = b.count(b"\n") - crlf
    got = "CRLF" if crlf and not lf else ("LF" if lf and not crlf else f"MIXED crlf={crlf} lf={lf}")
    ok = got == want
    bad += not ok
    print("ok  " if ok else "BAD ", want, got, path)
print(f"line-endings: {len(KINDS) - bad} of {len(KINDS)} kept")
sys.exit(1 if bad else 0)
'@

$py = @('uv', 'run', '--no-sync', 'python')
$identity = $py + @("$plan/identity.py")
$steps = @(
    @{ Id = 'identity-before'; Stage = 'identity'; Argv = $identity },
    @{ Id = 'py-lint'; Stage = 'static'; Argv = @('uv', 'run', '--no-sync', 'ruff', 'check', 'packages/', 'tests/') },
    @{ Id = 'py-format'; Stage = 'static'; Argv = @('uv', 'run', '--no-sync', 'ruff', 'format', '--check', 'tests/unit/test_tts_output_name.py') },
    @{ Id = 'py-types'; Stage = 'static'; Argv = @('uv', 'run', '--no-sync', 'pyright', 'packages/') },
    @{ Id = 'ui-types'; Stage = 'static'; Argv = @('npm', '--prefix', 'ui', 'run', 'typecheck') },
    @{ Id = 'ui-lint'; Stage = 'static'; Argv = @('npm', '--prefix', 'ui', 'run', 'lint') },
    @{ Id = 'task-contract'; Stage = 'static'; Argv = $py + @('tools/lint_task_contract.py', '--allowed-builder-classes', 'avkit_builder,avkit_coordinator,avkit_verifier', '--task', "$plan/task.md") },
    @{ Id = 'scope-paths'; Stage = 'static'; Argv = $py + @("$plan/scope-check.py") },
    @{ Id = 'line-endings'; Stage = 'static'; Argv = $py + @('-c', $lineEndings) },
    @{ Id = 'red-check-selftest'; Stage = 'static'; Argv = $py + @("$plan/red-check.py", '--selftest') },
    @{ Id = 'tts-py-targeted'; Stage = 'targeted'; Argv = @('uv', 'run', '--no-sync', 'pytest', 'tests/unit/test_tts_output_name.py', 'tests/unit/test_tts_async.py', '--tb=short', '-q', '-rs') },
    @{ Id = 'tts-ui-targeted'; Stage = 'targeted'; Argv = @('npm', '--prefix', 'ui', 'run', 'test', '--', 'tests/unit/tts-page.test.ts', 'tests/unit/tts-page.behavior.test.ts', 'tests/unit/tts-pill-contrast.test.ts', 'tests/unit/queue-primitives.test.ts', 'tests/unit/layout-primitives.test.ts', 'tests/unit/tts-run-bar.test.ts') },
    @{ Id = 'py-tests'; Stage = 'full'; Argv = @('uv', 'run', '--no-sync', 'pytest', 'tests/', '--tb=short', '-q', '-rfE') },
    @{ Id = 'openapi'; Stage = 'full'; Argv = $py + @('tools/export_openapi.py', '--check', 'openapi.committed.json') },
    @{ Id = 'ui-tests'; Stage = 'full'; Argv = @('npm', '--prefix', 'ui', 'run', 'test') },
    @{ Id = 'ui-build'; Stage = 'full'; Argv = @('npm', '--prefix', 'ui', 'run', 'build') },
    @{ Id = 'state-render'; Stage = 'full'; Argv = $py + @('tools/meu_status.py', 'render', '--check') },
    @{ Id = 'issues-render'; Stage = 'full'; Argv = $py + @('tools/issue_triage.py', 'render', '--check') },
    @{ Id = 'ui-electron'; Stage = 'runtime'; Argv = @('npm', '--prefix', 'ui', 'run', 'test:e2e', '--', 'tests/e2e/tts-generate.test.ts') },
    @{ Id = 'identity-after'; Stage = 'identity'; Argv = $identity }
)

function Get-TestedState([string]$Receipt) {
    $line = Select-String -Path $Receipt -Pattern '^tested_state ' | Select-Object -Last 1
    if ($null -eq $line) { return $null }
    return $line.Line.Substring('tested_state '.Length).Trim()
}

for ($i = 0; $i -lt $steps.Count; $i++) {
    $step = $steps[$i]
    $receipt = "$receipts/tpp-D6-$($step.Id).txt"
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
    if ($code -eq 0 -and $step.Id -eq 'tts-py-targeted') {
        if (Select-String -Path $receipt -Pattern 'SKIPPED' -SimpleMatch -Quiet) {
            Write-Output 'tts-py-targeted: the receipt shows a skipped test; every case must run'
            $code = 1
        }
    }
    if ($code -eq 0 -and $step.Id -eq 'identity-after') {
        $before = Get-TestedState "$receipts/tpp-D6-identity-before.txt"
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
