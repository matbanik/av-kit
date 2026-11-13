# Session 67 fresh-full gate (task H1-2; implementation-plan.md §Session gate).
# Session 66's shape (docs/execution/plans/2026-11-12-youtube-client-runtime/session-gate.ps1),
# with this plan's scope, no split or package steps, Session 54's ci-collect step for the new
# real-FFmpeg module, that module run on the pinned pair, and the download-queue Electron spec.
# Runs from the repository root (P:/av-kit, main only per AGENTS.md §Commits) in stage order:
# input identity, then every static check, then the full suites, then the runtime checks, then
# the input identity again. One receipt per id under C:/Temp/av-kit, named s67-D6-<id>.txt.
# Fail-fast: the first non-zero step stops the gate and every later step is printed as not_run.
# The gate also fails when tested_state differs between its start and its end (an input changed
# while it ran). Read-only apart from the receipts, ui/out (ui-build), mcp-server/dist
# (mcp-build), ui/test-results (ui-electron) and pytest's temp folder, which git ignores.
# Nothing here reaches the network or YouTube. Exit = the first failing step's code.
# py-tests runs the whole suite (no -x) and keeps Session 49b's baseline rule: pytest exit 1
# passes only when every FAILED id also FAILED in row 0's s67-base-py.txt, and nothing ERRORs.
# ui-tests, mcp-tests, real-ffmpeg and ui-electron excuse nothing; row 0's receipts record
# their counts.
# Skipped, per the plan: mcp-audit (network and YouTube), build-record (no release), and the
# live MP3 download (D-671's manual check, after the gate, only on Mat's words). Each is printed
# with its reason and runs nothing.
$ErrorActionPreference = 'Continue'
$root = (git rev-parse --show-toplevel).Trim()
Set-Location $root
$plan = 'docs/execution/plans/2026-11-12-download-audio-extract'
$receipts = 'C:/Temp/av-kit'
# lint_task_contract.py recognises the instantiated receipt paths only through RECEIPTS_DIR and
# fails closed (exit 3) when it is unset, which no user or machine scope sets on this host.
$env:RECEIPTS_DIR = $receipts
$env:PYTHONIOENCODING = 'utf-8'
$env:ELECTRON_RUN_AS_NODE = $null
# RC1 ECN-2 (CLOSEOUT-SELFTEST-ANCESTOR-AGENT-DIR): keep pytest's temp dirs away from the home folder.
$tmp = 'C:\Temp\av-kit\s67\tmp'
New-Item -ItemType Directory -Force -Path $tmp | Out-Null
$env:TMP = $tmp
$env:TEMP = $tmp
$base = (Get-Content "$plan/baseline.sha").Trim()

# Files Modified, the new files, the project files and the paths baseline-dirty.txt already held.
# Anything else changed, or HEAD moving, is S3. So is a baseline-dirty.txt path this plan doesn't
# write whose SHA-256 differs from row 0's (another session wrote it while this one ran); its
# content is hashed, never printed. ui/tests/e2e/test-ids.ts is refused: this plan never writes it.
$scopePaths = @"
import hashlib, pathlib, subprocess, sys
allowed = {
    'packages/core/src/avkit_core/services/download.py',
    'packages/api/src/avkit_api/wiring.py',
    'tests/unit/test_download_audio_extract.py',
    'tests/integration/test_download_audio_extract_real_ffmpeg.py',
    'tests/integration/test_api_wiring.py',
    'tests/e2e/real_stack.py',
    'tests/e2e/test_api_error_surface.py',
    'tests/integration/test_download_received_quality.py',
    'tests/unit/test_download_failure_visibility.py',
    'tests/unit/test_extract_options.py',
    'tests/unit/test_services.py',
    '.github/workflows/ci.yml',
    'docs/build-plan/03-service-layer.md',
    '.agent/context/known-issues.yaml',
    '.agent/context/known-issues.md',
    '.agent/context/triage-output.yaml',
    '.agent/context/meu-status.yaml',
    'docs/BUILD_PLAN.md',
    '.agent/context/meu-registry.md',
    '.agent/context/grouping/2026-11-10-download-reliability-session-grouping.md',
    '.agent/context/current-focus.md',
    'docs/execution/metrics.md',
}
ours = set(allowed)
refused = {'ui/tests/e2e/test-ids.ts'}
prefixes = ('$plan/', '.agent/context/handoffs/2026-11-12-download-audio-extract-', 'docs/execution/reflections/2026-11-12-download-audio-extract-')
dirty = pathlib.Path('$plan/baseline-dirty.txt').read_text(encoding='utf-8').splitlines()
changed_dirty = []
# Each line is git's porcelain line, a tab, then the file's SHA-256 at row 0.
for line in dirty:
    if not line:
        continue
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
$baseReceipt = "$receipts/s67-base-py.txt"
$baselinePyFailed = @()
if (Test-Path $baseReceipt) {
    $baselinePyFailed = @(Select-String -Path $baseReceipt -Pattern '^FAILED (\S+)' | ForEach-Object { $_.Matches[0].Groups[1].Value })
}
Write-Output ("baseline py failures excused: [{0}] (receipt {1})" -f ($baselinePyFailed -join ', '), $baseReceipt)
Write-Output 'baseline ui failures excused: [] (ui-tests excuses nothing)'
Write-Output 'baseline mcp failures excused: [] (mcp-tests excuses nothing)'
Write-Output 'baseline e2e failures excused: [] (ui-electron excuses nothing)'

$skipped = @(
    @{ Id = 'mcp-audit'; Stage = 'runtime'; Reason = 'live network and YouTube, which the brief forbids' },
    @{ Id = 'build-record'; Stage = 'full'; Reason = 'no release and no package build in this session' },
    @{ Id = 'live-mp3-download'; Stage = 'runtime'; Reason = 'network and YouTube; a recorded manual check after the gate, only on Mat''s words (D-671)' }
)
foreach ($s in $skipped) {
    Write-Output ("{0} stage={1} skipped reason={2}" -f $s.Id, $s.Stage, $s.Reason)
}

$identity = @('uv', 'run', '--no-sync', 'python', "$plan/identity.py")
$steps = @(
    @{ Id = 'identity-before'; Stage = 'identity'; Argv = $identity },
    @{ Id = 'py-types'; Stage = 'static'; Argv = @('uv', 'run', '--no-sync', 'pyright', 'packages/') },
    @{ Id = 'py-lint'; Stage = 'static'; Argv = @('uv', 'run', '--no-sync', 'ruff', 'check', 'packages/', 'tests/') },
    @{ Id = 'ui-types'; Stage = 'static'; Argv = @('npm', '--prefix', 'ui', 'run', 'typecheck') },
    @{ Id = 'ui-lint'; Stage = 'static'; Argv = @('npm', '--prefix', 'ui', 'run', 'lint') },
    @{ Id = 'task-contract'; Stage = 'static'; Argv = @('uv', 'run', '--no-sync', 'python', 'tools/lint_task_contract.py', '--allowed-builder-classes', 'avkit_builder,avkit_coordinator,avkit_verifier', '--task', "$plan/task.md") },
    @{ Id = 'scope-paths'; Stage = 'static'; Argv = @('uv', 'run', '--no-sync', 'python', '-c', $scopePaths) },
    @{ Id = 'red-check-selftest'; Stage = 'static'; Argv = @('uv', 'run', '--no-sync', 'python', "$plan/red-check.py", '--selftest') },
    # CI_DESELECT (AC-142.19): the Tests step as ci.yml holds it deselects the new module once,
    # and the same run without that deselect collects it.
    @{ Id = 'ci-collect'; Stage = 'static'; Argv = @('uv', 'run', '--no-sync', 'python', "$plan/ci-collect.py") },
    @{ Id = 'py-tests'; Stage = 'full'; Argv = @('uv', 'run', '--no-sync', 'pytest', 'tests/', '--tb=short', '-q', '-rfE') },
    # No schema changes; H1-4 proves the snapshot is unchanged.
    @{ Id = 'openapi'; Stage = 'full'; Argv = @('uv', 'run', '--no-sync', 'python', 'tools/export_openapi.py', '--check', 'openapi.committed.json') },
    @{ Id = 'ui-tests'; Stage = 'full'; Argv = @('npm', '--prefix', 'ui', 'run', 'test') },
    @{ Id = 'ui-build'; Stage = 'full'; Argv = @('npm', '--prefix', 'ui', 'run', 'build') },
    @{ Id = 'mcp-types'; Stage = 'full'; Argv = @('npm', '--prefix', 'mcp-server', 'run', 'typecheck') },
    # mcp-build runs first: runner-fake-backend.test.ts reads the served actions from dist.
    @{ Id = 'mcp-build'; Stage = 'full'; Argv = @('npm', '--prefix', 'mcp-server', 'run', 'build') },
    @{ Id = 'mcp-tests'; Stage = 'full'; Argv = @('npm', '--prefix', 'mcp-server', 'run', 'test') },
    @{ Id = 'state-render'; Stage = 'full'; Argv = @('uv', 'run', '--no-sync', 'python', 'tools/meu_status.py', 'render', '--check') },
    @{ Id = 'issues-render'; Stage = 'full'; Argv = @('uv', 'run', '--no-sync', 'python', 'tools/issue_triage.py', 'render', '--check') },
    # AC-142.17 on the pinned pair (git-ignored, bound by identity.py). py-tests runs it too; this
    # receipt names it on its own, with -rs so a skip shows its reason.
    @{ Id = 'real-ffmpeg'; Stage = 'runtime'; Argv = @('uv', 'run', '--no-sync', 'pytest', 'tests/integration/test_download_audio_extract_real_ffmpeg.py', '--tb=short', '-q', '-rfEs') },
    # The Downloader module against the ui-build output above, with the seam backend, no network:
    # the card still shows a job's error_message.
    @{ Id = 'ui-electron'; Stage = 'runtime'; Argv = @('npm', '--prefix', 'ui', 'run', 'test:e2e', '--', 'tests/e2e/download-queue.test.ts') },
    @{ Id = 'identity-after'; Stage = 'identity'; Argv = $identity }
)

function Get-TestedState([string]$Receipt) {
    $line = Select-String -Path $Receipt -Pattern '^tested_state ' | Select-Object -Last 1
    if ($null -eq $line) { return $null }
    return $line.Line.Substring('tested_state '.Length).Trim()
}

for ($i = 0; $i -lt $steps.Count; $i++) {
    $step = $steps[$i]
    $receipt = "$receipts/s67-D6-$($step.Id).txt"
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
    if ($code -eq 0 -and $step.Id -eq 'real-ffmpeg') {
        # A skip would pass pytest; the module must really run on the pair.
        $skips = @(Select-String -Path $receipt -Pattern '^SKIPPED ')
        if ($skips.Count -gt 0) {
            Write-Output ("real-ffmpeg: {0} skipped test(s); the pinned pair did not run" -f $skips.Count)
            $code = 1
        }
    }
    if ($code -eq 0 -and $step.Id -eq 'identity-after') {
        $before = Get-TestedState "$receipts/s67-D6-identity-before.txt"
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
