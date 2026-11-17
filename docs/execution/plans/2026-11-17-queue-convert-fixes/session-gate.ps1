# Session 89 fresh-full gate (task H1-2; implementation-plan.md §Session gate).
# The shape of docs/execution/plans/2026-11-17-queue-pause-feedback/session-gate.ps1, with this
# plan's steps: identity, then the static checks (ui-types, ui-lint, the task contract,
# scope-paths, line-endings, home-path, the red-check and eol-check selftests, py-format and
# py-lint on this plan folder's Python), then the targeted suites (meu-156-unit, meu-157-unit),
# then host-load (Session 81 RULE-2), then the fresh full suites (ui-tests, ui-build), the
# Electron runs (e2e-cancel-paused, e2e-browse-mount, e2e-convert-queue with AC-97.7,
# e2e-download-queue, e2e-pause-feedback), state-render and issues-render-check, then the
# identity again.
# Runs from the repository root (P:/av-kit, main only per AGENTS.md §Commits). One receipt per
# id under C:/Temp/av-kit/queue-convert-fixes, named qc-D6-<id>.txt.
# Fail-fast: the first non-zero step stops the gate and every later step is printed as not_run.
# The gate also fails when tested_state differs between its start and its end (an input changed
# while it ran). Read-only apart from the receipts, the temp folder, ui/out (ui-build) and the
# Electron tests' scratch app data under the temp folder; all are ignored or outside the
# checkout. Nothing here reaches the network or YouTube, and no step dispatches a model.
# Exit = the first failing step's code.
# ui-tests excuses nothing: row 0's qc-base-ui.txt shows 1596 passed and no failure.
# meu-156-unit runs row 2's file list (the MEU-156 test files and the AC-156.13 pin files);
# meu-157-unit runs row 4's (the MEU-157 test files and the AC-157.13 pin files).
# host-load samples Win32_Processor.LoadPercentage five times; above 60 % it waits, re-sampling
# every 30 s for up to 10 minutes, and records the value it ran at. It never fails the gate.
# Skipped, per the plan: py-tests, py-types, openapi and mcp-* (H1-4 checks that every
# packages/, mcp-server/, tests/ and tools/ file keeps its baseline-skip-hashes.json hash, and
# none was added or removed; no Python, API, OpenAPI or MCP file changes, S9), and the rest of
# test:e2e (only the Convert and Downloader pages' cancel and browse paths changed, and their
# suites run). Each is printed with its reason and runs nothing.
$ErrorActionPreference = 'Continue'
$root = (git rev-parse --show-toplevel).Trim()
Set-Location $root
$plan = 'docs/execution/plans/2026-11-17-queue-convert-fixes'
$receipts = 'C:/Temp/av-kit/queue-convert-fixes'
# lint_task_contract.py recognises the instantiated receipt paths only through RECEIPTS_DIR and
# fails closed (exit 3) when it is unset, which no user or machine scope sets on this host.
$env:RECEIPTS_DIR = 'C:/Temp/av-kit'
$env:PYTHONIOENCODING = 'utf-8'
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:ELECTRON_RUN_AS_NODE = $null
# RC1 ECN-2: keep the temp dirs away from the home folder, as row 0 ran the base suites.
$tmp = 'C:\Temp\av-kit\queue-convert-fixes\tmp'
New-Item -ItemType Directory -Force -Path $tmp | Out-Null
$env:TMP = $tmp
$env:TEMP = $tmp
$base = (Get-Content "$plan/baseline.sha").Trim()

# §Files Modified, this plan folder, the closeout artifacts (the handoffs and reviews under
# .agent/context/handoffs/2026-11-17-queue-convert-fixes-*, the reflection, metrics.md and
# current-focus.md) and the paths baseline-dirty.txt already held. The row-3a probe file is not
# in `mine`, so it is checked as a "Read, never changed" entry whose row-0 value is `absent`. A
# new plan folder another session's planner writes is skipped the way identity.py skips it
# (untracked, docs/execution/plans/2026-11-1[5-7]-<slug>/, folder absent from HEAD). Anything
# else changed, HEAD moving, a "Read, never changed" file moving from baseline-scope.json, or a
# baseline-dirty path outside this scope moving from baseline-dirty-hashes.json is S4.
$scopePaths = @"
import hashlib, json, pathlib, re, subprocess, sys
plan = '$plan'
mine = {
    'ui/src/renderer/src/features/converter/convert-controls.ts',
    'ui/src/renderer/src/features/downloader/download-controls.ts',
    'ui/src/renderer/src/features/converter/convert-commands.ts',
    'ui/src/renderer/src/features/converter/ConvertPage.tsx',
    'ui/src/renderer/src/features/downloader/DownloaderPage.tsx',
    'ui/tests/unit/queue-cancel-paused.test.tsx',
    'ui/tests/unit/convert-browse-hold.test.ts',
    'ui/tests/unit/convert-page.behavior.test.ts',
    'ui/tests/unit/downloader-page.behavior.test.ts',
    'ui/tests/unit/convert-page.test.ts',
    'ui/tests/unit/downloader-page.test.ts',
    'ui/tests/e2e/convert-browse-mount.test.ts',
    'ui/tests/e2e/queue-cancel-paused.test.ts',
    'docs/build-plan/06-gui.md',
    'docs/build-plan/10-queue-card-ui.md',
    '.agent/context/meu-status.yaml',
    '.agent/context/meu-registry.md',
    'docs/BUILD_PLAN.md',
    '.agent/context/known-issues.yaml',
    '.agent/context/known-issues.md',
    '.agent/context/grouping/2026-11-17-post-session-88-triage-session-grouping.md',
    'docs/execution/metrics.md',
    '.agent/context/current-focus.md',
}
scope = json.loads(pathlib.Path(plan + '/baseline-scope.json').read_text(encoding='utf-8'))
read_only = tuple(p for p in scope if p not in mine)
prefixes = (plan + '/', '.agent/context/handoffs/2026-11-17-queue-convert-fixes-', 'docs/execution/reflections/2026-11-17-queue-convert-fixes-')
other_plan_re = re.compile(r'^docs/execution/plans/2026-11-1[5-7]-[^/]+/')
def git(*args):
    return subprocess.run(['git', *args], capture_output=True, check=True).stdout.decode('utf-8')
head_plans = {n for n in git('ls-tree', '--name-only', 'HEAD', 'docs/execution/plans/').splitlines() if n}
def other_plan(p):
    folder = '/'.join(p.split('/')[:4])
    return bool(other_plan_re.match(p)) and not p.startswith(plan + '/') and folder not in head_plans
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
untracked = [p for p in paths('ls-files', '--others', '--exclude-standard', '-z') if '__pycache__/' not in p]
others = sorted({p for p in untracked if other_plan(p)})
extra = sorted({p for p in tracked + untracked if p not in allowed and not p.startswith(prefixes) and p not in others})
print('changed paths:', len(set(tracked + untracked)), 'outside scope:', extra, 'other sessions plan files skipped:', len(others))
print('read-never-changed files:', len(read_only), 'mismatch:', read_only_moved, 'baseline-dirty hash mismatch:', dirty_moved)
print('head:', head, 'head moved (S4):', moved)
sys.exit(1 if extra or moved or read_only_moved or dirty_moved else 0)
"@

function Invoke-HostLoad {
    $samples = @(1..5 | ForEach-Object { (Get-CimInstance Win32_Processor | Measure-Object -Property LoadPercentage -Average).Average; Start-Sleep -Seconds 2 })
    $load = [math]::Round(($samples | Measure-Object -Average).Average, 1)
    Write-Output ("host-load samples: [{0}] mean={1}" -f ($samples -join ', '), $load)
    $deadline = (Get-Date).AddMinutes(10)
    while ($load -gt 60 -and (Get-Date) -lt $deadline) {
        Write-Output ("host-load {0} % is above 60 %; waiting 30 s" -f $load)
        Start-Sleep -Seconds 30
        $load = [math]::Round((Get-CimInstance Win32_Processor | Measure-Object -Property LoadPercentage -Average).Average, 1)
    }
    Write-Output ("host-load: ran at {0} %" -f $load)
}

Write-Output 'baseline ui failures excused: [] (ui-tests excuses nothing; qc-base-ui.txt shows 1596 passed and no failure)'

$skipped = @(
    @{ Id = 'py-tests'; Stage = 'full'; Reason = 'every packages/ and tests/ file keeps its baseline-skip-hashes.json hash (H1-4); no Python file changes (S9)' },
    @{ Id = 'py-types'; Stage = 'static'; Reason = 'every packages/ file keeps its baseline-skip-hashes.json hash (H1-4); no Python file changes (S9)' },
    @{ Id = 'openapi'; Stage = 'full'; Reason = 'every packages/api/ file keeps its baseline-skip-hashes.json hash (H1-4); no route or schema changes (S9)' },
    @{ Id = 'mcp-types/mcp-build/mcp-tests/mcp-audit'; Stage = 'full'; Reason = 'every mcp-server/ file keeps its baseline-skip-hashes.json hash (H1-4); no MCP tool changes (S9)' },
    @{ Id = 'e2e-other'; Stage = 'runtime'; Reason = 'only the Convert and Downloader pages cancel and browse paths changed, and their suites run' }
)
foreach ($s in $skipped) {
    Write-Output ("{0} stage={1} skipped reason={2}" -f $s.Id, $s.Stage, $s.Reason)
}

$py = @('uv', 'run', '--no-sync', 'python')
$identity = $py + @("$plan/identity.py")
$e2e = @('npm', '--prefix', 'ui', 'run', 'test:e2e', '--')
$vitest = @('npm', '--prefix', 'ui', 'run', 'test', '--')
$planPy = @(Get-ChildItem -Path $plan -Filter '*.py' | Sort-Object Name | ForEach-Object { "$plan/$($_.Name)" })
$unit156 = @(
    'tests/unit/queue-cancel-paused.test.tsx', 'tests/unit/convert-page.behavior.test.ts', 'tests/unit/downloader-page.behavior.test.ts',
    'tests/unit/convert-page.test.ts', 'tests/unit/downloader-page.test.ts', 'tests/unit/palette-curation.test.tsx',
    'tests/unit/queue-pause-feedback.test.tsx', 'tests/unit/convert-commands.test.ts', 'tests/unit/download-commands.test.ts',
    'tests/unit/command-palette.test.ts', 'tests/unit/queue-toolbar.test.ts'
)
$unit157 = @(
    'tests/unit/convert-browse-hold.test.ts', 'tests/unit/convert-page.behavior.test.ts', 'tests/unit/convert-page.test.ts',
    'tests/unit/convert-commands.test.ts', 'tests/unit/shortcuts.test.ts', 'tests/unit/common-shortcuts.test.tsx',
    'tests/unit/palette-curation.test.tsx', 'tests/unit/gui-actions-audit.test.ts', 'tests/unit/command-palette.test.ts'
)
$steps = @(
    @{ Id = 'identity-before'; Stage = 'identity'; Argv = $identity },
    @{ Id = 'ui-types'; Stage = 'static'; Argv = @('npm', '--prefix', 'ui', 'run', 'typecheck') },
    @{ Id = 'ui-lint'; Stage = 'static'; Argv = @('npm', '--prefix', 'ui', 'run', 'lint') },
    @{ Id = 'task-contract'; Stage = 'static'; Argv = $py + @('tools/lint_task_contract.py', '--allowed-builder-classes', 'avkit_builder,avkit_coordinator,avkit_verifier', '--task', "$plan/task.md") },
    @{ Id = 'scope-paths'; Stage = 'static'; Argv = $py + @('-c', $scopePaths) },
    @{ Id = 'line-endings'; Stage = 'static'; Argv = $py + @("$plan/eol-check.py") },
    @{ Id = 'home-path'; Stage = 'static'; Argv = $py + @('tools/check_home_path.py') },
    @{ Id = 'red-check-selftest'; Stage = 'static'; Argv = $py + @("$plan/red-check.py", '--selftest') },
    @{ Id = 'eol-check-selftest'; Stage = 'static'; Argv = $py + @("$plan/eol-check.py", '--selftest') },
    @{ Id = 'py-format'; Stage = 'static'; Argv = @('uv', 'run', '--no-sync', 'ruff', 'format', '--check') + $planPy },
    @{ Id = 'py-lint'; Stage = 'static'; Argv = @('uv', 'run', '--no-sync', 'ruff', 'check') + $planPy },
    @{ Id = 'meu-156-unit'; Stage = 'targeted'; Argv = $vitest + $unit156 },
    @{ Id = 'meu-157-unit'; Stage = 'targeted'; Argv = $vitest + $unit157 },
    @{ Id = 'host-load'; Stage = 'host'; HostLoad = $true },
    @{ Id = 'ui-tests'; Stage = 'full'; Argv = @('npm', '--prefix', 'ui', 'run', 'test') },
    @{ Id = 'ui-build'; Stage = 'full'; Argv = @('npm', '--prefix', 'ui', 'run', 'build') },
    @{ Id = 'e2e-cancel-paused'; Stage = 'runtime'; Argv = $e2e + @('tests/e2e/queue-cancel-paused.test.ts'); Passed = 2 },
    @{ Id = 'e2e-browse-mount'; Stage = 'runtime'; Argv = $e2e + @('tests/e2e/convert-browse-mount.test.ts'); Passed = 4 },
    @{ Id = 'e2e-convert-queue'; Stage = 'runtime'; Argv = $e2e + @('tests/e2e/convert-queue.test.ts'); Clean = $true },
    @{ Id = 'e2e-download-queue'; Stage = 'runtime'; Argv = $e2e + @('tests/e2e/download-queue.test.ts'); Clean = $true },
    @{ Id = 'e2e-pause-feedback'; Stage = 'runtime'; Argv = $e2e + @('tests/e2e/queue-pause-feedback.test.ts'); Passed = 4 },
    @{ Id = 'state-render'; Stage = 'full'; Argv = $py + @('tools/meu_status.py', 'render', '--check') },
    @{ Id = 'issues-render-check'; Stage = 'full'; Argv = $py + @('tools/issue_triage.py', 'render', '--check') },
    @{ Id = 'identity-after'; Stage = 'identity'; Argv = $identity }
)

function Get-TestedState([string]$Receipt) {
    $line = Select-String -Path $Receipt -Pattern '^tested_state ' | Select-Object -Last 1
    if ($null -eq $line) { return $null }
    return $line.Line.Substring('tested_state '.Length).Trim()
}

for ($i = 0; $i -lt $steps.Count; $i++) {
    $step = $steps[$i]
    $receipt = "$receipts/qc-D6-$($step.Id).txt"
    if ($step.ContainsKey('HostLoad')) {
        Invoke-HostLoad *> $receipt
        $code = 0
    } else {
        $argv = $step.Argv
        & rtk proxy @argv *> $receipt
        $code = $LASTEXITCODE
    }
    Write-Output ("{0} stage={1} exit={2} receipt={3}" -f $step.Id, $step.Stage, $code, $receipt)
    Get-Content $receipt | Select-Object -Last 6
    if ($code -eq 0 -and $step.ContainsKey('Passed')) {
        # A file list that selects fewer tests than planned must not pass quietly.
        $want = $step.Passed
        $passed = Select-String -Path $receipt -Pattern "^\s+$want passed" -Quiet
        $bad = Select-String -Path $receipt -Pattern '^\s+[0-9]+ (failed|flaky|skipped|did not run)' -Quiet
        Write-Output ("{0}: {1} passed={2} other outcomes={3}" -f $step.Id, $want, $passed, $bad)
        if (-not $passed -or $bad) { $code = 1 }
    }
    if ($code -eq 0 -and $step.ContainsKey('Clean')) {
        # An existing Electron suite passes only with no failed or flaky test (S5, S7).
        $passed = Select-String -Path $receipt -Pattern '^\s+[0-9]+ passed' -Quiet
        $bad = Select-String -Path $receipt -Pattern '^\s+[0-9]+ (failed|flaky|did not run)' -Quiet
        Write-Output ("{0}: passed line={1} failed or flaky={2}" -f $step.Id, $passed, $bad)
        if (-not $passed -or $bad) { $code = 1 }
    }
    if ($code -eq 0 -and $step.Id -eq 'identity-after') {
        $before = Get-TestedState "$receipts/qc-D6-identity-before.txt"
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
