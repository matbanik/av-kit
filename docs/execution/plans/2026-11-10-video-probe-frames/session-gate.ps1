# Session 62 fresh-full gate (task H1-2; implementation-plan.md §Session gate).
# Session 58's shape (docs/execution/plans/2026-11-08-capture-region-import/session-gate.ps1), with this plan's steps.
# Runs from the repository root (P:/av-kit, main only per AGENTS.md §Commits) in stage order:
# input identity, then every static check, then the full suites, then the runtime checks, then
# the input identity again. One receipt per id under C:/Temp/av-kit, named s62-D6-<id>.txt.
# Fail-fast: the first non-zero step stops the gate and every later step is printed as not_run.
# The gate also fails when tested_state differs between its start and its end (an input changed
# while it ran). Read-only apart from the receipts and mcp-server/dist (mcp-build), which git
# ignores.
# Exit = the first failing step's code.
# py-tests runs the whole suite (no -x) and keeps Session 49b's baseline rule: pytest exit 1
# passes only when every FAILED id also FAILED in row 0's s62-base-py.txt, and nothing ERRORs.
# mcp-tests, status-canon and real-ffmpeg excuse nothing; row 0's receipts record the counts.
# Skipped, per the plan: the UI type, lint, test, build and Electron steps (no ui/ file
# changes; status-canon runs the only UI tests that read a file this session writes),
# mcp-audit, build-record and the package build with its smokes. Each is printed with its
# reason and runs nothing.
$ErrorActionPreference = 'Continue'
$root = (git rev-parse --show-toplevel).Trim()
Set-Location $root
$plan = 'docs/execution/plans/2026-11-10-video-probe-frames'
$receipts = 'C:/Temp/av-kit'
# lint_task_contract.py recognises the instantiated receipt paths only through RECEIPTS_DIR and
# fails closed (exit 3) when it is unset, which no user or machine scope sets on this host.
$env:RECEIPTS_DIR = $receipts
$env:PYTHONIOENCODING = 'utf-8'
$env:ELECTRON_RUN_AS_NODE = $null
# RC1 ECN-2 (CLOSEOUT-SELFTEST-ANCESTOR-AGENT-DIR): keep pytest's temp dirs away from the home folder.
$tmp = 'C:\Temp\av-kit\s62\tmp'
New-Item -ItemType Directory -Force -Path $tmp | Out-Null
$env:TMP = $tmp
$env:TEMP = $tmp
$base = (Get-Content "$plan/baseline.sha").Trim()

# Files Modified, the project files and the paths baseline-dirty.txt already held. Anything
# else changed, ui/tests/e2e/test-ids.ts changing, or HEAD moving, is S3. So is a
# baseline-dirty.txt path this plan doesn't write whose SHA-256 differs from row 0's (another
# session wrote it while this one ran); its content is hashed, never printed.
$scopePaths = @"
import hashlib, pathlib, subprocess, sys
allowed = {
    'packages/core/src/avkit_core/services/video_input.py',
    'packages/core/src/avkit_core/ports/capture.py',
    'packages/core/src/avkit_core/ports/media.py',
    'packages/core/src/avkit_core/domain/enums.py',
    'packages/core/src/avkit_core/services/conversion.py',
    'packages/core/src/avkit_core/services/capture.py',
    'packages/infrastructure/src/avkit_infra/media/adapter.py',
    'packages/api/src/avkit_api/routes/conversions.py',
    'packages/api/src/avkit_api/schemas/conversions.py',
    'packages/api/src/avkit_api/routes/captures.py',
    'packages/api/src/avkit_api/schemas/captures.py',
    'packages/api/src/avkit_api/wiring.py',
    'openapi.committed.json',
    'mcp-server/src/toolsets/convert.ts',
    'mcp-server/src/toolsets/capture.ts',
    'mcp-server/src/toolsets/registry.ts',
    'mcp-server/scripts/audit/plan.ts',
    'tests/unit/test_video_input.py',
    'tests/unit/test_conversion_probe.py',
    'tests/unit/test_media_adapter_frames.py',
    'tests/unit/test_capture_frames_service.py',
    'tests/e2e/test_api_conversion_probe.py',
    'tests/e2e/test_api_capture_frames.py',
    'tests/integration/test_video_real_ffmpeg.py',
    'tests/unit/test_domain_capture.py',
    'tests/unit/test_domain.py',
    'tests/e2e/test_api_captures.py',
    'tests/e2e/test_api_openapi.py',
    'tests/e2e/test_api_downloads.py',
    'tests/e2e/test_api_bodies.py',
    'tests/e2e/test_api_conversions.py',
    'mcp-server/tests/convert.test.ts',
    'mcp-server/tests/capture.test.ts',
    'mcp-server/tests/action-index.test.ts',
    'mcp-server/tests/m7-resource.test.ts',
    'mcp-server/tests/fixtures.ts',
    'mcp-server/tests/audit/coverage.test.ts',
    'mcp-server/tests/audit/runner-fake-backend.test.ts',
    '.github/workflows/ci.yml',
    'docs/build-plan/08-video-conversion.md',
    'docs/build-plan/09-screenshot-capture.md',
    '.agent/context/meu-status.yaml',
    'docs/BUILD_PLAN.md',
    '.agent/context/meu-registry.md',
    '.agent/context/grouping/2026-11-09-video-stills-session-grouping.md',
    '.agent/context/current-focus.md',
    'docs/execution/metrics.md',
}
ours = set(allowed)
refused = {'ui/tests/e2e/test-ids.ts'}
prefixes = ('$plan/', '.agent/context/handoffs/2026-11-10-video-probe-frames-', 'docs/execution/reflections/2026-11-10-video-probe-frames-')
dirty = pathlib.Path('$plan/baseline-dirty.txt').read_text(encoding='utf-8').splitlines()
changed_dirty = []
# Each line is git's porcelain line, a tab, then the file's SHA-256 at row 0.
for line in dirty:
    path, _, recorded = line[3:].partition('\t')
    if not path or not recorded or ' -> ' in path or path.startswith('"'):
        print('baseline-dirty.txt: unreadable line', repr(line))
        sys.exit(2)
    allowed.add(path)
    if path in ours or path.startswith(prefixes):
        continue
    p = pathlib.Path(path)
    now = hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else 'deleted'
    if now != recorded:
        changed_dirty.append(path)
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
extra = sorted({p for p in out if (p not in allowed and not p.startswith(prefixes)) or p in refused})
print('changed paths:', len(set(out)), 'outside scope:', extra, 'head:', head, 'head moved (S3):', moved)
print('baseline-dirty paths changed since row 0 (S3):', changed_dirty)
sys.exit(1 if extra or moved or changed_dirty else 0)
"@

# An id is excused only when row 0's baseline receipt really shows it FAILED: a missing
# receipt excuses nothing.
$baseReceipt = "$receipts/s62-base-py.txt"
$baselinePyFailed = @()
if (Test-Path $baseReceipt) {
    $baselinePyFailed = @(Select-String -Path $baseReceipt -Pattern '^FAILED (\S+)' | ForEach-Object { $_.Matches[0].Groups[1].Value })
}
Write-Output ("baseline py failures excused: [{0}] (receipt {1})" -f ($baselinePyFailed -join ', '), $baseReceipt)
Write-Output 'baseline mcp failures excused: [] (mcp-tests excuses nothing)'

$skipped = @(
    @{ Id = 'ui-types'; Stage = 'static'; Reason = 'no ui/ file changes' },
    @{ Id = 'ui-lint'; Stage = 'static'; Reason = 'no ui/ file changes' },
    @{ Id = 'ui-tests'; Stage = 'full'; Reason = 'no ui/ file changes; status-canon runs the only UI tests that read a file this session writes' },
    @{ Id = 'ui-build'; Stage = 'full'; Reason = 'no ui/ file changes' },
    @{ Id = 'ui-electron'; Stage = 'runtime'; Reason = 'no ui/ file changes' },
    @{ Id = 'mcp-audit'; Stage = 'runtime'; Reason = 'live network, which the brief forbids' },
    @{ Id = 'build-record'; Stage = 'full'; Reason = 'no installer build' },
    @{ Id = 'package-build'; Stage = 'runtime'; Reason = 'no packaged surface changes; MEU-125 ran the package build and its smokes' }
)
foreach ($s in $skipped) {
    Write-Output ("{0} stage={1} skipped reason={2}" -f $s.Id, $s.Stage, $s.Reason)
}

$identity = @('uv', 'run', 'python', "$plan/identity.py")
$steps = @(
    @{ Id = 'identity-before'; Stage = 'identity'; Argv = $identity },
    @{ Id = 'py-types'; Stage = 'static'; Argv = @('uv', 'run', 'pyright', 'packages/') },
    @{ Id = 'py-lint'; Stage = 'static'; Argv = @('uv', 'run', 'ruff', 'check', 'packages/', 'tests/') },
    @{ Id = 'task-contract'; Stage = 'static'; Argv = @('uv', 'run', 'python', 'tools/lint_task_contract.py', '--allowed-builder-classes', 'avkit_builder,avkit_coordinator,avkit_verifier', '--task', "$plan/task.md") },
    @{ Id = 'scope-paths'; Stage = 'static'; Argv = @('uv', 'run', 'python', '-c', $scopePaths) },
    @{ Id = 'red-check-selftest'; Stage = 'static'; Argv = @('uv', 'run', 'python', "$plan/red-check.py", '--selftest') },
    @{ Id = 'py-tests'; Stage = 'full'; Argv = @('uv', 'run', 'pytest', 'tests/', '--tb=short', '-q', '-rfE') },
    @{ Id = 'openapi'; Stage = 'full'; Argv = @('uv', 'run', 'python', 'tools/export_openapi.py', '--check', 'openapi.committed.json') },
    @{ Id = 'mcp-types'; Stage = 'full'; Argv = @('npm', '--prefix', 'mcp-server', 'run', 'typecheck') },
    @{ Id = 'mcp-build'; Stage = 'full'; Argv = @('npm', '--prefix', 'mcp-server', 'run', 'build') },
    @{ Id = 'mcp-tests'; Stage = 'full'; Argv = @('npm', '--prefix', 'mcp-server', 'run', 'test') },
    @{ Id = 'state-render'; Stage = 'full'; Argv = @('uv', 'run', 'python', 'tools/meu_status.py', 'render', '--check') },
    @{ Id = 'issues-render'; Stage = 'full'; Argv = @('uv', 'run', 'python', 'tools/issue_triage.py', 'render', '--check') },
    # The two UI canon tests read meu-status.yaml and docs/BUILD_PLAN.md directly, and row 6
    # changes both.
    @{ Id = 'status-canon'; Stage = 'full'; Argv = @('npm', '--prefix', 'ui', 'run', 'test', '--', 'tests/unit/layout-canon.test.ts', 'tests/unit/queue-canon.test.ts') },
    # The real-FFmpeg modules on their own, with durations, so S6 reads one receipt: the new
    # module, and the extract module because _run changes (py-tests runs both too).
    @{ Id = 'real-ffmpeg'; Stage = 'runtime'; Argv = @('uv', 'run', 'pytest', 'tests/integration/test_video_real_ffmpeg.py', 'tests/integration/test_extract_real_ffmpeg.py', '--tb=short', '-q', '-rfE', '--durations=10') },
    @{ Id = 'identity-after'; Stage = 'identity'; Argv = $identity }
)

function Get-TestedState([string]$Receipt) {
    $line = Select-String -Path $Receipt -Pattern '^tested_state ' | Select-Object -Last 1
    if ($null -eq $line) { return $null }
    return $line.Line.Substring('tested_state '.Length).Trim()
}

for ($i = 0; $i -lt $steps.Count; $i++) {
    $step = $steps[$i]
    $receipt = "$receipts/s62-D6-$($step.Id).txt"
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
        $before = Get-TestedState "$receipts/s62-D6-identity-before.txt"
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
