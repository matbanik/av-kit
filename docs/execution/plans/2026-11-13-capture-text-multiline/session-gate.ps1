# Session 70 fresh-full gate (task H1-2; implementation-plan.md §Session gate).
# Session 69's shape (docs/execution/plans/2026-11-13-capture-copy-image/session-gate.ps1),
# with this plan's scope (ui/tests/e2e/test-ids.ts is allowed: row 1 writes it), no ci-collect,
# real-FFmpeg, live or never-probe step, and these steps of its own: py-lint adds
# tools/capture_bake_fixture.py by name (row 2 edits it; `ruff check tools/` fails at baseline on
# other files, so the scope is the edited file), id-length on the new pytest modules (Session 59
# RULE-2), capture-action-row.test.ts on its own (AC-51.6 hashes test-ids.ts; Session 50), and
# the capture Electron spec (AC-102.19 and AC-102.20, the multi-line parity oracle).
# Runs from the repository root (P:/av-kit, main only per AGENTS.md §Commits) in stage order:
# input identity, then every static check, then the full suites, then the runtime checks, then
# the input identity again. One receipt per id under C:/Temp/av-kit, named s70-D6-<id>.txt.
# Fail-fast: the first non-zero step stops the gate and every later step is printed as not_run.
# The gate also fails when tested_state differs between its start and its end (an input changed
# while it ran). Read-only apart from the receipts, ui/out (ui-build), mcp-server/dist
# (mcp-build), ui/test-results (ui-electron) and pytest's temp folder, which git ignores or
# which sit outside the repository. No step writes the system clipboard. Nothing here reaches
# the network or YouTube. Exit = the first failing step's code.
# py-tests runs the whole suite (no -x) and keeps Session 49b's baseline rule: pytest exit 1
# passes only when every FAILED id also FAILED in row 0's s70-base-py.txt, and nothing ERRORs.
# ui-tests, action-row, mcp-tests and ui-electron excuse nothing; row 0's receipts record
# their counts.
# Skipped, per the plan: mcp-audit (network and YouTube) and build-record (no release). Each is
# printed with its reason and runs nothing.
$ErrorActionPreference = 'Continue'
$root = (git rev-parse --show-toplevel).Trim()
Set-Location $root
$plan = 'docs/execution/plans/2026-11-13-capture-text-multiline'
$receipts = 'C:/Temp/av-kit'
# lint_task_contract.py recognises the instantiated receipt paths only through RECEIPTS_DIR and
# fails closed (exit 3) when it is unset, which no user or machine scope sets on this host.
$env:RECEIPTS_DIR = $receipts
$env:PYTHONIOENCODING = 'utf-8'
$env:ELECTRON_RUN_AS_NODE = $null
# RC1 ECN-2 (CLOSEOUT-SELFTEST-ANCESTOR-AGENT-DIR): keep pytest's temp dirs away from the home folder.
$tmp = 'C:\Temp\av-kit\s70\tmp'
New-Item -ItemType Directory -Force -Path $tmp | Out-Null
$env:TMP = $tmp
$env:TEMP = $tmp
$base = (Get-Content "$plan/baseline.sha").Trim()

# Files Modified, the new files, the project files and the paths baseline-dirty.txt already held.
# Anything else changed, or HEAD moving, is S3. So is a baseline-dirty.txt path this plan doesn't
# write whose SHA-256 differs from row 0's (another session wrote it while this one ran); its
# content is hashed, never printed. The MCP audit baseline is refused: MCP gains no action and
# only the annotate description changes (D-711), so this plan never writes it.
$scopePaths = @"
import hashlib, pathlib, subprocess, sys
allowed = {
    'packages/core/src/avkit_core/domain/capture.py',
    'packages/api/src/avkit_api/schemas/captures.py',
    'packages/infrastructure/src/avkit_infra/capture/adapter.py',
    'tools/capture_bake_fixture.py',
    'mcp-server/src/toolsets/capture.ts',
    'mcp-server/tests/capture.test.ts',
    'ui/src/renderer/src/features/capture/capture-text-metrics.ts',
    'ui/src/renderer/src/features/capture/CaptureViewport.tsx',
    'ui/tests/e2e/fixtures/capture-geometry.json',
    'ui/tests/e2e/fixtures/capture-fidelity-multiline-original.png',
    'ui/tests/e2e/fixtures/capture-fidelity-multiline-annotated.png',
    'ui/tests/e2e/test-ids.ts',
    'ui/tests/e2e/capture-inbox.test.ts',
    'ui/tests/unit/capture-text-lines.behavior.test.ts',
    'tests/unit/test_capture_text_lines.py',
    'tests/e2e/test_api_capture_text_lines.py',
    'tests/unit/test_capture_bake_fixture.py',
    'docs/build-plan/09-screenshot-capture.md',
    '.agent/context/meu-status.yaml',
    'docs/BUILD_PLAN.md',
    '.agent/context/meu-registry.md',
    '.agent/context/grouping/2026-10-29-capture-annotation-editor-session-grouping.md',
    '.agent/context/current-focus.md',
    'docs/execution/metrics.md',
}
ours = set(allowed)
refused = {'.agent/skills/mcp-tool-audit/resources/baseline-snapshot.json'}
prefixes = ('$plan/', '.agent/context/handoffs/2026-11-13-capture-text-multiline-', 'docs/execution/reflections/2026-11-13-capture-text-multiline-')
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
$baseReceipt = "$receipts/s70-base-py.txt"
$baselinePyFailed = @()
if (Test-Path $baseReceipt) {
    $baselinePyFailed = @(Select-String -Path $baseReceipt -Pattern '^FAILED (\S+)' | ForEach-Object { $_.Matches[0].Groups[1].Value })
}
Write-Output ("baseline py failures excused: [{0}] (receipt {1})" -f ($baselinePyFailed -join ', '), $baseReceipt)
Write-Output 'baseline ui failures excused: [] (ui-tests and action-row excuse nothing)'
Write-Output 'baseline mcp failures excused: [] (mcp-tests excuses nothing)'
Write-Output 'baseline e2e failures excused: [] (ui-electron excuses nothing)'

$skipped = @(
    @{ Id = 'mcp-audit'; Stage = 'runtime'; Reason = 'live network and YouTube, which the brief forbids' },
    @{ Id = 'build-record'; Stage = 'full'; Reason = 'no release and no package build in this session' }
)
foreach ($s in $skipped) {
    Write-Output ("{0} stage={1} skipped reason={2}" -f $s.Id, $s.Stage, $s.Reason)
}

$identity = @('uv', 'run', '--no-sync', 'python', "$plan/identity.py")
$steps = @(
    @{ Id = 'identity-before'; Stage = 'identity'; Argv = $identity },
    @{ Id = 'py-types'; Stage = 'static'; Argv = @('uv', 'run', '--no-sync', 'pyright', 'packages/') },
    @{ Id = 'py-lint'; Stage = 'static'; Argv = @('uv', 'run', '--no-sync', 'ruff', 'check', 'packages/', 'tests/', 'tools/capture_bake_fixture.py') },
    @{ Id = 'ui-types'; Stage = 'static'; Argv = @('npm', '--prefix', 'ui', 'run', 'typecheck') },
    @{ Id = 'ui-lint'; Stage = 'static'; Argv = @('npm', '--prefix', 'ui', 'run', 'lint') },
    @{ Id = 'task-contract'; Stage = 'static'; Argv = @('uv', 'run', '--no-sync', 'python', 'tools/lint_task_contract.py', '--allowed-builder-classes', 'avkit_builder,avkit_coordinator,avkit_verifier', '--task', "$plan/task.md") },
    @{ Id = 'scope-paths'; Stage = 'static'; Argv = @('uv', 'run', '--no-sync', 'python', '-c', $scopePaths) },
    @{ Id = 'red-check-selftest'; Stage = 'static'; Argv = @('uv', 'run', '--no-sync', 'python', "$plan/red-check.py", '--selftest') },
    # Every title in the two new pytest modules fits red-check's header pattern (Session 59 RULE-2).
    @{ Id = 'id-length'; Stage = 'static'; Argv = @('uv', 'run', '--no-sync', 'python', "$plan/id-length.py", 'tests/unit/test_capture_text_lines.py', 'tests/e2e/test_api_capture_text_lines.py') },
    @{ Id = 'py-tests'; Stage = 'full'; Argv = @('uv', 'run', '--no-sync', 'pytest', 'tests/', '--tb=short', '-q', '-rfE') },
    # TEXT_API_NEWLINES (D-703) changes no schema: the committed snapshot is unchanged (H1-4).
    @{ Id = 'openapi'; Stage = 'full'; Argv = @('uv', 'run', '--no-sync', 'python', 'tools/export_openapi.py', '--check', 'openapi.committed.json') },
    # AC-51.6 / AC-81.13 hash test-ids.ts's prefix; row 1 edits the file, so this test is its own
    # receipt (Session 50) as well as part of ui-tests.
    @{ Id = 'action-row'; Stage = 'full'; Argv = @('npm', '--prefix', 'ui', 'run', 'test', '--', 'tests/unit/capture-action-row.test.ts') },
    @{ Id = 'ui-tests'; Stage = 'full'; Argv = @('npm', '--prefix', 'ui', 'run', 'test') },
    @{ Id = 'ui-build'; Stage = 'full'; Argv = @('npm', '--prefix', 'ui', 'run', 'build') },
    @{ Id = 'mcp-types'; Stage = 'full'; Argv = @('npm', '--prefix', 'mcp-server', 'run', 'typecheck') },
    # mcp-build runs first: runner-fake-backend.test.ts reads the served actions from dist.
    @{ Id = 'mcp-build'; Stage = 'full'; Argv = @('npm', '--prefix', 'mcp-server', 'run', 'build') },
    @{ Id = 'mcp-tests'; Stage = 'full'; Argv = @('npm', '--prefix', 'mcp-server', 'run', 'test') },
    @{ Id = 'state-render'; Stage = 'full'; Argv = @('uv', 'run', '--no-sync', 'python', 'tools/meu_status.py', 'render', '--check') },
    @{ Id = 'issues-render'; Stage = 'full'; Argv = @('uv', 'run', '--no-sync', 'python', 'tools/issue_triage.py', 'render', '--check') },
    # The capture module against the ui-build output above, with the seam backend, no network:
    # AC-102.19 (multi-line preview and bake agree) and AC-102.20 (AC-82.6 through the parameterised seam).
    @{ Id = 'ui-electron'; Stage = 'runtime'; Argv = @('npm', '--prefix', 'ui', 'run', 'test:e2e', '--', 'tests/e2e/capture-inbox.test.ts') },
    @{ Id = 'identity-after'; Stage = 'identity'; Argv = $identity }
)

function Get-TestedState([string]$Receipt) {
    $line = Select-String -Path $Receipt -Pattern '^tested_state ' | Select-Object -Last 1
    if ($null -eq $line) { return $null }
    return $line.Line.Substring('tested_state '.Length).Trim()
}

for ($i = 0; $i -lt $steps.Count; $i++) {
    $step = $steps[$i]
    $receipt = "$receipts/s70-D6-$($step.Id).txt"
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
        $before = Get-TestedState "$receipts/s70-D6-identity-before.txt"
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
