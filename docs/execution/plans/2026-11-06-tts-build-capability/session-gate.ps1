# Session 51 fresh-full gate (task H1-2; implementation-plan.md §Session gate).
# Session 50's shape (docs/execution/plans/2026-11-05-transcript-failure-reason/session-gate.ps1), with this plan's steps.
# Runs from the repository root (P:/av-kit, main only per AGENTS.md §Commits) in stage order:
# input identity, then every static check, then the full suites, then the runtime checks, then
# the input identity again. One receipt per id under C:/Temp/av-kit, named s51-D6-<id>.txt.
# Fail-fast: the first non-zero step stops the gate and every later step is printed as not_run.
# The gate also fails when tested_state differs between its start and its end (an input changed
# while it ran). Read-only apart from the receipts, ui/out (ui-build), mcp-server/dist
# (mcp-build), packaging/build and packaging/dist (package-build), the E2E app data and the
# onedir copy and smoke folders under C:/Temp/av-kit/s51; all are ignored or outside the checkout.
# Exit = the first failing step's code.
# py-tests runs the whole suite (no -x) and keeps Session 49b's baseline rule: pytest exit 1
# passes only when every FAILED id also FAILED in row 0's s51-base-py.txt, and nothing ERRORs.
# Row 0 saw no failure (1265 passed), so nothing is excused. ui-tests (row 0: 1144 passed) and
# mcp-tests (row 0: 466 passed) excuse nothing.
# Skipped, per the plan: mcp-audit and build-record. Each is printed with its reason and runs
# nothing.
$ErrorActionPreference = 'Continue'
$root = (git rev-parse --show-toplevel).Trim()
Set-Location $root
$plan = 'docs/execution/plans/2026-11-06-tts-build-capability'
$receipts = 'C:/Temp/av-kit'
# lint_task_contract.py recognises the instantiated receipt paths only through RECEIPTS_DIR and
# fails closed (exit 3) when it is unset, which no user or machine scope sets on this host.
$env:RECEIPTS_DIR = $receipts
$env:PYTHONIOENCODING = 'utf-8'
$env:ELECTRON_RUN_AS_NODE = $null
# RC1 ECN-2 (CLOSEOUT-SELFTEST-ANCESTOR-AGENT-DIR): keep pytest's temp dirs away from C:/Users/Mat/.agent.
$tmp = "$receipts/s51/tmp"
New-Item -ItemType Directory -Force -Path $tmp | Out-Null
$env:TMP = $tmp
$env:TEMP = $tmp
$base = (Get-Content "$plan/baseline.sha").Trim()

# Files Modified, the project files and the paths baseline-dirty.txt already held. Anything
# else changed, or HEAD moving, is S3.
$scopePaths = @"
import pathlib, subprocess, sys
allowed = {
    'packages/core/src/avkit_core/domain/tts.py',
    'packages/core/src/avkit_core/ports/tts.py',
    'packages/infrastructure/src/avkit_infra/tts/adapter.py',
    'packages/core/src/avkit_core/services/models.py',
    'packages/api/src/avkit_api/schemas/models.py',
    'packages/api/src/avkit_api/routes/models.py',
    'openapi.committed.json',
    'mcp-server/src/toolsets/models.ts',
    'tools/smoke_packaged_tts.py',
    'ui/src/renderer/src/components/ui/SelectInput.tsx',
    'ui/src/renderer/src/features/tts/useTtsJob.ts',
    'ui/src/renderer/src/features/tts/tts-controls.ts',
    'ui/src/renderer/src/features/tts/tts-devices.ts',
    'ui/src/renderer/src/features/tts/TTSPage.tsx',
    'ui/src/renderer/src/features/settings/SettingsPage.tsx',
    'tests/unit/test_domain.py',
    'tests/integration/test_tts_device_resolution.py',
    'tests/integration/test_tts_no_torch.py',
    'tests/unit/test_services.py',
    'tests/e2e/api_fakes.py',
    'tests/e2e/test_api_model_capability.py',
    'tests/e2e/test_api_tts_models.py',
    'mcp-server/tests/models-availability.test.ts',
    'ui/tests/unit/tts-page.behavior.test.ts',
    'ui/tests/unit/tts-model-selection.test.ts',
    'ui/tests/unit/tts-devices.test.ts',
    'ui/tests/unit/settings-tts-device.test.ts',
    'ui/tests/e2e/tts-generate.test.ts',
    'ui/tests/e2e/settings.test.ts',
    'docs/build-plan/03-service-layer.md',
    'docs/build-plan/04-rest-api.md',
    'docs/build-plan/05-mcp-server.md',
    'docs/build-plan/06-gui.md',
    '.agent/context/meu-status.yaml',
    'docs/BUILD_PLAN.md',
    '.agent/context/meu-registry.md',
    '.agent/context/known-issues.yaml',
    '.agent/context/known-issues.md',
    '.agent/context/triage-output.yaml',
    '.agent/context/grouping/2026-11-04-rc2-triage-residuals-session-grouping.md',
    '.agent/context/current-focus.md',
    'docs/execution/metrics.md',
}
dirty = pathlib.Path('$plan/baseline-dirty.txt').read_text(encoding='utf-8').splitlines()
for line in dirty:
    path = line[3:]
    if not path or ' -> ' in path or path.startswith('"'):
        print('baseline-dirty.txt: unreadable line', repr(line))
        sys.exit(2)
    allowed.add(path)
prefixes = ('$plan/', '.agent/context/handoffs/2026-11-06-tts-build-capability-', 'docs/execution/reflections/2026-11-06-tts-build-capability-')
# --no-renames: a rename reports both its source deletion and its destination, so moving an
# out-of-scope file into an allowed path still shows the out-of-scope deletion.
# -z: NUL-separated, so a path with spaces or quoting is one entry.
def paths(*args):
    raw = subprocess.run(['git', *args], capture_output=True, check=True).stdout.decode('utf-8')
    return [p for p in raw.split('\0') if p]
head = subprocess.run(['git', 'rev-parse', 'HEAD'], capture_output=True, text=True, check=True).stdout.strip()
moved = head != '$base'
out = paths('diff', '--no-renames', '--name-only', '-z', head)
out += paths('ls-files', '--others', '--exclude-standard', '-z')
extra = sorted({p for p in out if p not in allowed and not p.startswith(prefixes)})
print('changed paths:', len(set(out)), 'outside scope:', extra, 'head:', head, 'head moved (S3):', moved)
sys.exit(1 if extra or moved else 0)
"@

# An id is excused only when row 0's baseline receipt really shows it FAILED: a missing
# receipt excuses nothing.
$baseReceipt = "$receipts/s51-base-py.txt"
$baselinePyFailed = @()
if (Test-Path $baseReceipt) {
    $baselinePyFailed = @(Select-String -Path $baseReceipt -Pattern '^FAILED (\S+)' | ForEach-Object { $_.Matches[0].Groups[1].Value })
}
Write-Output ("baseline py failures excused: [{0}] (receipt {1})" -f ($baselinePyFailed -join ', '), $baseReceipt)
Write-Output 'baseline ui failures excused: [] (ui-tests excuses nothing)'
Write-Output 'baseline mcp failures excused: [] (mcp-tests excuses nothing)'

$skipped = @(
    @{ Id = 'mcp-audit'; Stage = 'runtime'; Reason = 'live network and YouTube, which the brief forbids' },
    @{ Id = 'build-record'; Stage = 'full'; Reason = 'no installer build' }
)
foreach ($s in $skipped) {
    Write-Output ("{0} stage={1} skipped reason={2}" -f $s.Id, $s.Stage, $s.Reason)
}

# smoke-capability runs on a fresh copy of package-build's onedir outside the checkout, with a
# fresh models folder (row 8's Green, D-315).
$smokeBackend = "$receipts/s51/gate-backend"
$smokeModels = "$receipts/s51/gate-smoke-models"
$smokeCopy = {
    Remove-Item -Recurse -Force $smokeBackend, $smokeModels -ErrorAction SilentlyContinue
    New-Item -ItemType Directory -Force -Path $smokeBackend | Out-Null
    Copy-Item -Recurse 'packaging/dist/avkit-backend' "$smokeBackend/avkit-backend"
}

$identity = @('uv', 'run', 'python', "$plan/identity.py")
$steps = @(
    @{ Id = 'identity-before'; Stage = 'identity'; Argv = $identity },
    @{ Id = 'py-types'; Stage = 'static'; Argv = @('uv', 'run', 'pyright', 'packages/') },
    @{ Id = 'py-lint'; Stage = 'static'; Argv = @('uv', 'run', 'ruff', 'check', 'packages/', 'tests/') },
    @{ Id = 'ui-types'; Stage = 'static'; Argv = @('npm', '--prefix', 'ui', 'run', 'typecheck') },
    @{ Id = 'ui-lint'; Stage = 'static'; Argv = @('npm', '--prefix', 'ui', 'run', 'lint') },
    @{ Id = 'task-contract'; Stage = 'static'; Argv = @('uv', 'run', 'python', 'tools/lint_task_contract.py', '--allowed-builder-classes', 'avkit_builder,avkit_coordinator,avkit_verifier', '--task', "$plan/task.md") },
    @{ Id = 'scope-paths'; Stage = 'static'; Argv = @('uv', 'run', 'python', '-c', $scopePaths) },
    @{ Id = 'red-check-selftest'; Stage = 'static'; Argv = @('uv', 'run', 'python', "$plan/red-check.py", '--selftest') },
    @{ Id = 'py-tests'; Stage = 'full'; Argv = @('uv', 'run', 'pytest', 'tests/', '--tb=short', '-q', '-rfE') },
    @{ Id = 'ui-tests'; Stage = 'full'; Argv = @('npm', '--prefix', 'ui', 'run', 'test') },
    @{ Id = 'ui-build'; Stage = 'full'; Argv = @('npm', '--prefix', 'ui', 'run', 'build') },
    @{ Id = 'openapi'; Stage = 'full'; Argv = @('uv', 'run', 'python', 'tools/export_openapi.py', '--check', 'openapi.committed.json') },
    @{ Id = 'mcp-types'; Stage = 'full'; Argv = @('npm', '--prefix', 'mcp-server', 'run', 'typecheck') },
    @{ Id = 'mcp-tests'; Stage = 'full'; Argv = @('npm', '--prefix', 'mcp-server', 'run', 'test') },
    @{ Id = 'mcp-build'; Stage = 'full'; Argv = @('npm', '--prefix', 'mcp-server', 'run', 'build') },
    @{ Id = 'state-render'; Stage = 'full'; Argv = @('uv', 'run', 'python', 'tools/meu_status.py', 'render', '--check') },
    @{ Id = 'issues-render'; Stage = 'full'; Argv = @('uv', 'run', 'python', 'tools/issue_triage.py', 'render', '--check') },
    @{ Id = 'ui-electron'; Stage = 'runtime'; Argv = @('npm', '--prefix', 'ui', 'run', 'test:e2e', '--', 'tests/e2e/settings.test.ts', 'tests/e2e/tts-generate.test.ts') },
    @{ Id = 'package-build'; Stage = 'runtime'; Argv = @('uv', 'run', 'python', 'tools/package_backend.py') },
    @{ Id = 'smoke-capability'; Stage = 'runtime'; Pre = $smokeCopy; Argv = @('uv', 'run', 'python', 'tools/smoke_packaged_tts.py', '--phase', 'capability', '--backend-dir', "$smokeBackend/avkit-backend", '--models-dir', $smokeModels, '--out', "$receipts/s51-D6-smoke-capability.json") },
    @{ Id = 'dev-pytorch'; Stage = 'runtime'; Argv = @('uv', 'run', 'python', "$plan/dev-pytorch-check.py") },
    @{ Id = 'models-untouched'; Stage = 'runtime'; Argv = @('uv', 'run', 'python', "$plan/models-snapshot.py", '--compare', "$plan/models-before.json") },
    @{ Id = 'identity-after'; Stage = 'identity'; Argv = $identity }
)

function Get-TestedState([string]$Receipt) {
    $line = Select-String -Path $Receipt -Pattern '^tested_state ' | Select-Object -Last 1
    if ($null -eq $line) { return $null }
    return $line.Line.Substring('tested_state '.Length).Trim()
}

for ($i = 0; $i -lt $steps.Count; $i++) {
    $step = $steps[$i]
    $receipt = "$receipts/s51-D6-$($step.Id).txt"
    $argv = $step.Argv
    if ($step.Pre) { & $step.Pre }
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
        $before = Get-TestedState "$receipts/s51-D6-identity-before.txt"
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
