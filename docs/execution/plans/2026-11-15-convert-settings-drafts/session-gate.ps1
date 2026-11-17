# Session 81 fresh-full gate (task H1-2; implementation-plan.md §Session gate).
# The shape of docs/execution/plans/2026-11-07-convert-extract-index/session-gate.ps1 and
# docs/execution/plans/2026-11-15-closeout-record-once/session-gate.ps1, with this plan's steps:
# identity, then the static checks (py-types, py-lint, py-format, ui-types, ui-lint, the task
# contract, scope-paths, line-endings, red-check's selftest), then the targeted suites
# (meu-151-ui, meu-152-ui, meu-152-py), then the fresh full suites (py-tests, ui-tests, ui-build,
# state-render, issues-render-check), then the Electron runs (ui-electron-convert,
# ui-electron-capture and A2's ui-electron-a2, D-975), then the identity again.
# Runs from the repository root (P:/av-kit, main only per AGENTS.md §Commits). One receipt per
# id under C:/Temp/av-kit/convert-settings-drafts, named cs81-D6-<id>.txt.
# Fail-fast: the first non-zero step stops the gate and every later step is printed as not_run.
# The gate also fails when tested_state differs between its start and its end (an input changed
# while it ran). Read-only apart from the receipts, the temp folder, ui/out (ui-build) and the
# Electron tests' scratch app data under the temp folder; all are ignored or outside the
# checkout. Nothing here reaches the network or YouTube, and no step dispatches a model.
# Exit = the first failing step's code.
# py-tests runs the whole suite (no -x) and keeps Session 49b's baseline rule: pytest exit 1
# passes only when every FAILED id also FAILED in row 0's cs81-base-py.txt, and nothing ERRORs.
# Row 0 saw no failure (cs81-base-py.txt: 3008 passed), so nothing is excused. ui-tests
# (cs81-base-ui.txt: 1547 passed) excuses nothing.
# The capture grep is the plan's "W9-3|AC-57.10 header|AC-67.24" with each space written as '.',
# so no argument carries a space through rtk, npm and the Playwright wrapper; it selects the same
# three tests, and the step checks that exactly 3 passed.
# Skipped, per the plan: openapi and mcp-* (H1-4 checks every packages/api/ and mcp-server/ file
# against baseline-skip-hashes.json), build-record (no build) and the GUI references (no GUI
# reference image is shipped for these surfaces). Each is printed with its reason and runs nothing.
$ErrorActionPreference = 'Continue'
$root = (git rev-parse --show-toplevel).Trim()
Set-Location $root
$plan = 'docs/execution/plans/2026-11-15-convert-settings-drafts'
$receipts = 'C:/Temp/av-kit/convert-settings-drafts'
# lint_task_contract.py recognises the instantiated receipt paths only through RECEIPTS_DIR and
# fails closed (exit 3) when it is unset, which no user or machine scope sets on this host.
$env:RECEIPTS_DIR = 'C:/Temp/av-kit'
$env:PYTHONIOENCODING = 'utf-8'
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:ELECTRON_RUN_AS_NODE = $null
# RC1 ECN-2: keep the temp dirs away from the home folder, as row 0 ran the base suites.
$tmp = 'C:\Temp\av-kit\convert-settings-drafts\tmp'
New-Item -ItemType Directory -Force -Path $tmp | Out-Null
$env:TMP = $tmp
$env:TEMP = $tmp
$base = (Get-Content "$plan/baseline.sha").Trim()

# §Files Modified, this plan folder, the closeout artifacts (the two handoffs, the reflection,
# the A1 plan review's canonical copy, metrics.md and current-focus.md) and the paths
# baseline-dirty.txt already held. A new plan folder another session's planner writes is skipped
# the way baseline.ps1 and identity.py skip it (untracked, docs/execution/plans/2026-11-15-<slug>/,
# folder absent from HEAD). Anything else changed, HEAD moving, a "Read, never changed" file
# moving from baseline-scope.json, or a baseline-dirty path outside this scope moving from
# baseline-dirty-hashes.json is S4.
$scopePaths = @"
import hashlib, json, pathlib, subprocess, sys
plan = '$plan'
mine = {
    'ui/src/renderer/src/features/capture/useCaptureSettings.ts',
    'ui/src/renderer/src/features/converter/ConvertPage.tsx',
    'ui/src/renderer/src/features/converter/convert-time.ts',
    'ui/src/renderer/src/features/converter/convert-controls.ts',
    'ui/src/renderer/src/components/queue/QueueCard.tsx',
    'packages/core/src/avkit_core/services/conversion.py',
    'ui/tests/unit/capture-settings-draft.behavior.test.ts',
    'ui/tests/unit/capture-page.behavior.test.ts',
    'ui/tests/unit/capture-shapes.behavior.test.ts',
    'ui/tests/unit/capture-style-flow.behavior.test.ts',
    'ui/tests/unit/capture-tool-flow.behavior.test.ts',
    'ui/tests/unit/convert-page.behavior.test.ts',
    'ui/tests/unit/convert-queue-labels.test.ts',
    'ui/tests/unit/convert-controls.test.ts',
    'tests/unit/test_convert_cut_encoder.py',
    'tests/unit/test_convert_output_reserved.py',
    'ui/tests/e2e/capture-settings-draft.test.ts',
    'ui/tests/e2e/convert-queue-labels.test.ts',
    'docs/build-plan/06-gui.md',
    'docs/build-plan/08-video-conversion.md',
    '.agent/context/known-issues.yaml',
    '.agent/context/known-issues.md',
    '.agent/context/meu-status.yaml',
    '.agent/context/meu-registry.md',
    'docs/BUILD_PLAN.md',
    '.agent/context/grouping/2026-11-15-post-rc3-triage-residuals-session-grouping.md',
    'docs/execution/metrics.md',
    '.agent/context/current-focus.md',
    '.agent/context/handoffs/2026-11-16-convert-settings-drafts-amendment-a1-plan-critical-review.md',
}
read_only = (
    'ui/tests/unit/fixtures/queue-slot-baseline.json',
    'ui/tests/e2e/convert-queue.test.ts',
    'ui/tests/e2e/capture-inbox.test.ts',
    'tests/unit/test_conversion_service.py',
)
prefixes = (plan + '/', '.agent/context/handoffs/2026-11-15-convert-settings-drafts-', 'docs/execution/reflections/2026-11-15-convert-settings-drafts-')
def git(*args):
    return subprocess.run(['git', *args], capture_output=True, check=True).stdout.decode('utf-8')
head_plans = {n for n in git('ls-tree', '--name-only', 'HEAD', 'docs/execution/plans/').splitlines() if n}
def other_plan(p):
    folder = '/'.join(p.split('/')[:4])
    return p.startswith('docs/execution/plans/2026-11-15-') and not p.startswith(plan + '/') and folder != p and folder not in head_plans
allowed = set(mine)
for line in pathlib.Path(plan + '/baseline-dirty.txt').read_text(encoding='utf-8').splitlines():
    if not line:
        continue
    path = line[3:]
    if not path or ' -> ' in path or path.startswith('"'):
        print('baseline-dirty.txt: unreadable line', repr(line))
        sys.exit(2)
    allowed.add(path)
def sha(p):
    target = pathlib.Path(p)
    return hashlib.sha256(target.read_bytes()).hexdigest() if target.is_file() else 'absent'
scope = json.loads(pathlib.Path(plan + '/baseline-scope.json').read_text(encoding='utf-8'))
read_only_moved = [p for p in read_only if sha(p) != scope[p]]
dirty_hashes = json.loads(pathlib.Path(plan + '/baseline-dirty-hashes.json').read_text(encoding='utf-8'))
dirty_moved = [p for p, h in sorted(dirty_hashes.items()) if (sha(p) if pathlib.Path(p).exists() else 'deleted') != h]
# --no-renames: a rename reports both its source deletion and its destination, so moving an
# out-of-scope file into an allowed path still shows the out-of-scope deletion.
# -z: NUL-separated, so a path with spaces or quoting is one entry.
def paths(*args):
    return [p for p in git(*args).split('\0') if p]
head = git('rev-parse', 'HEAD').strip()
moved = head != '$base'
tracked = paths('diff', '--no-renames', '--name-only', '-z', head)
untracked = paths('ls-files', '--others', '--exclude-standard', '-z')
others = sorted({p for p in untracked if other_plan(p)})
extra = sorted({p for p in tracked + untracked if p not in allowed and not p.startswith(prefixes) and p not in others})
print('changed paths:', len(set(tracked + untracked)), 'outside scope:', extra, 'other sessions plan files skipped:', len(others))
print('read-never-changed mismatch:', read_only_moved, 'baseline-dirty hash mismatch:', dirty_moved)
print('head:', head, 'head moved (S4):', moved)
sys.exit(1 if extra or moved or read_only_moved or dirty_moved else 0)
"@

# Each §Files Modified file keeps its row-0 kind from baseline-eol.json; the A1 test file and the
# two A2 Electron files were added after row 0 and are LF per §Files Modified, and so are D-1066's three capture tests. The MIXED file
# keeps its 8 bare-LF lines. A lone CR fails any file.
$lineEndings = @"
import json, pathlib, sys
plan = '$plan'
eol = json.loads(pathlib.Path(plan + '/baseline-eol.json').read_text(encoding='utf-8'))
read_only = {'ui/tests/unit/fixtures/queue-slot-baseline.json', 'ui/tests/e2e/convert-queue.test.ts', 'ui/tests/e2e/capture-inbox.test.ts', 'tests/unit/test_conversion_service.py'}
expected = {p: v['expected'] for p, v in eol.items() if p not in read_only}
expected.update({'tests/unit/test_convert_output_reserved.py': 'LF', 'ui/tests/e2e/capture-settings-draft.test.ts': 'LF', 'ui/tests/e2e/convert-queue-labels.test.ts': 'LF', 'ui/tests/unit/capture-shapes.behavior.test.ts': 'LF', 'ui/tests/unit/capture-style-flow.behavior.test.ts': 'LF', 'ui/tests/unit/capture-tool-flow.behavior.test.ts': 'LF'})
bad = []
for p, kind in sorted(expected.items()):
    data = pathlib.Path(p).read_bytes()
    crlf = data.count(b'\r\n')
    bare = data.count(b'\n') - crlf
    lone_cr = data.count(b'\r') - crlf
    now = 'CRLF' if crlf and not bare else 'LF' if bare and not crlf else 'MIXED' if crlf and bare else 'EMPTY'
    ok = lone_cr == 0 and (bare == 8 if kind == 'MIXED' else now == kind)
    print(p, 'expected', kind, 'now', now, 'crlf', crlf, 'bare_lf', bare, 'lone_cr', lone_cr, 'ok' if ok else 'mismatch')
    if not ok:
        bad.append(p)
print('line-endings files:', len(expected), 'mismatch:', bad)
sys.exit(1 if bad else 0)
"@

# An id is excused only when row 0's baseline receipt really shows it FAILED: a missing
# receipt excuses nothing.
$baseReceipt = "$receipts/cs81-base-py.txt"
$baselinePyFailed = @()
if (Test-Path $baseReceipt) {
    $baselinePyFailed = @(Select-String -Path $baseReceipt -Pattern '^FAILED (\S+)' | ForEach-Object { $_.Matches[0].Groups[1].Value })
}
Write-Output ("baseline py failures excused: [{0}] (receipt {1})" -f ($baselinePyFailed -join ', '), $baseReceipt)
Write-Output 'baseline ui failures excused: [] (ui-tests excuses nothing; cs81-base-ui.txt shows no failure)'

$skipped = @(
    @{ Id = 'openapi'; Stage = 'full'; Reason = 'every packages/api/ file keeps its baseline-skip-hashes.json hash (H1-4)' },
    @{ Id = 'mcp-types/mcp-build/mcp-tests/mcp-audit'; Stage = 'full'; Reason = 'every mcp-server/ file keeps its baseline-skip-hashes.json hash (H1-4); gpu_encoder keeps its nullable shape' },
    @{ Id = 'build-record'; Stage = 'full'; Reason = 'no build' },
    @{ Id = 'gui-refs-not-shipped'; Stage = 'runtime'; Reason = 'no GUI reference image is shipped for these surfaces' }
)
foreach ($s in $skipped) {
    Write-Output ("{0} stage={1} skipped reason={2}" -f $s.Id, $s.Stage, $s.Reason)
}

$py = @('uv', 'run', '--no-sync', 'python')
$identity = $py + @("$plan/identity.py")
$e2e = @('npm', '--prefix', 'ui', 'run', 'test:e2e', '--')
$vitest = @('npm', '--prefix', 'ui', 'run', 'test', '--')
$steps = @(
    @{ Id = 'identity-before'; Stage = 'identity'; Argv = $identity },
    @{ Id = 'py-types'; Stage = 'static'; Argv = @('uv', 'run', '--no-sync', 'pyright', 'packages/') },
    @{ Id = 'py-lint'; Stage = 'static'; Argv = @('uv', 'run', '--no-sync', 'ruff', 'check', 'packages/', 'tests/') },
    @{ Id = 'py-format'; Stage = 'static'; Argv = @('uv', 'run', '--no-sync', 'ruff', 'format', '--check', 'packages/core/src/avkit_core/services/conversion.py', 'tests/unit/test_convert_cut_encoder.py', 'tests/unit/test_convert_output_reserved.py') },
    @{ Id = 'ui-types'; Stage = 'static'; Argv = @('npm', '--prefix', 'ui', 'run', 'typecheck') },
    @{ Id = 'ui-lint'; Stage = 'static'; Argv = @('npm', '--prefix', 'ui', 'run', 'lint') },
    @{ Id = 'task-contract'; Stage = 'static'; Argv = $py + @('tools/lint_task_contract.py', '--allowed-builder-classes', 'avkit_builder,avkit_coordinator,avkit_verifier', '--task', "$plan/task.md") },
    @{ Id = 'scope-paths'; Stage = 'static'; Argv = $py + @('-c', $scopePaths) },
    @{ Id = 'line-endings'; Stage = 'static'; Argv = $py + @('-c', $lineEndings) },
    @{ Id = 'red-check-selftest'; Stage = 'static'; Argv = $py + @("$plan/red-check.py", '--selftest') },
    @{ Id = 'meu-151-ui'; Stage = 'targeted'; Argv = $vitest + @('tests/unit/capture-settings-draft.behavior.test.ts', 'tests/unit/capture-page.behavior.test.ts', 'tests/unit/convert-page.behavior.test.ts', 'tests/unit/capture-page.test.ts', 'tests/unit/settings-page.test.ts', 'tests/unit/convert-page.test.ts') },
    @{ Id = 'meu-152-ui'; Stage = 'targeted'; Argv = $vitest + @('tests/unit/convert-queue-labels.test.ts', 'tests/unit/convert-controls.test.ts', 'tests/unit/queue-card.test.ts') },
    @{ Id = 'meu-152-py'; Stage = 'targeted'; Argv = @('uv', 'run', '--no-sync', 'pytest', 'tests/unit/test_convert_cut_encoder.py', 'tests/unit/test_convert_output_reserved.py', 'tests/unit/test_conversion_service.py', 'tests/e2e/test_api_conversions.py', '--tb=short', '-q', '-rfE') },
    @{ Id = 'py-tests'; Stage = 'full'; Argv = @('uv', 'run', '--no-sync', 'pytest', 'tests/', '--tb=short', '-q', '-rfE') },
    @{ Id = 'ui-tests'; Stage = 'full'; Argv = @('npm', '--prefix', 'ui', 'run', 'test') },
    @{ Id = 'ui-build'; Stage = 'full'; Argv = @('npm', '--prefix', 'ui', 'run', 'build') },
    @{ Id = 'state-render'; Stage = 'full'; Argv = $py + @('tools/meu_status.py', 'render', '--check') },
    @{ Id = 'issues-render-check'; Stage = 'full'; Argv = $py + @('tools/issue_triage.py', 'render', '--check') },
    @{ Id = 'ui-electron-convert'; Stage = 'runtime'; Argv = $e2e + @('tests/e2e/convert-queue.test.ts') },
    @{ Id = 'ui-electron-capture'; Stage = 'runtime'; Argv = $e2e + @('tests/e2e/capture-inbox.test.ts', '-g', 'W9-3.capture|AC-57.10.header|AC-67.24.Settings'); Passed = 3 },
    @{ Id = 'ui-electron-a2'; Stage = 'runtime'; Argv = $e2e + @('tests/e2e/capture-settings-draft.test.ts', 'tests/e2e/convert-queue-labels.test.ts'); Passed = 5 },
    @{ Id = 'identity-after'; Stage = 'identity'; Argv = $identity }
)

function Get-TestedState([string]$Receipt) {
    $line = Select-String -Path $Receipt -Pattern '^tested_state ' | Select-Object -Last 1
    if ($null -eq $line) { return $null }
    return $line.Line.Substring('tested_state '.Length).Trim()
}

for ($i = 0; $i -lt $steps.Count; $i++) {
    $step = $steps[$i]
    $receipt = "$receipts/cs81-D6-$($step.Id).txt"
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
    if ($code -eq 0 -and $step.ContainsKey('Passed')) {
        # A grep or file list that selects fewer tests than planned must not pass quietly.
        $want = $step.Passed
        $passed = Select-String -Path $receipt -Pattern "^\s+$want passed" -Quiet
        $bad = Select-String -Path $receipt -Pattern '^\s+[0-9]+ (failed|flaky|skipped|did not run)' -Quiet
        Write-Output ("{0}: {1} passed={2} other outcomes={3}" -f $step.Id, $want, $passed, $bad)
        if (-not $passed -or $bad) { $code = 1 }
    }
    if ($code -eq 0 -and $step.Id -eq 'identity-after') {
        $before = Get-TestedState "$receipts/cs81-D6-identity-before.txt"
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
