# Session 102 fresh-full gate (task H1-2; implementation-plan.md §Session gate).
# The shape of docs/execution/plans/2026-11-21-transcript-job-resume/session-gate.ps1, with this
# plan's steps: identity, then the static checks (ui-types, ui-lint, py-types, py-lint,
# py-format, the task contract, scope-paths, line-endings, home-path, pins-unchanged,
# named-edits --stage green, slug-edit, canon, red-unchanged and the red-check, eol-check and
# row-check selftests), then the targeted suites (py-debt, closeout-selftest, ui-tray), then
# host-load (Session 81 RULE-2), then the fresh full suites (ui-tests, py-tests, ui-build), the
# Electron runs (e2e-tray-double-click, e2e-startup-reveal), state-render, issues-render, then
# the identity again.
# Runs from the repository root (P:/av-kit, main only per AGENTS.md §Commits). One receipt per
# id under C:/Temp/av-kit/2026-11-22-tray-show-and-baseline-fixes, named tsb-D6-<id>.txt.
# Fail-fast: the first non-zero step stops the gate and every later step is printed as not_run.
# The gate also fails when tested_state differs between its start and its end (an input changed
# while it ran). Read-only apart from the receipts, the temp folders, ui/out (ui-build) and the
# Electron runs' scratch app data under the temp folder; all are ignored or outside the checkout.
# Nothing here reaches the network or YouTube, and no step dispatches a model.
# Exit = the first failing step's code.
# Nothing is excused: ui-tests and py-tests run whole, and py-tests holds no --deselect
# (AC-164.8 and AC-164.9 fixed the two ids Session 101's gate deselected).
# TEMP and TMP are the undated C:\Temp\av-kit\s102-tmp for every step but closeout-selftest,
# which runs under the dated tmp-dated folder on purpose (TOOLING-PLAN-SLUG-ANCESTOR-MATCH).
# ui-tray runs capture-tray.test.ts and the four §Test pins unit files.
# host-load is host-wait.py (the copied load-run.py's host_load_wait, limit 50 %): it waits,
# re-sampling every 30 s for up to 10 minutes, and records the value it ran at. It runs once as
# its own step and again before every Electron step (each into tsb-D6-<id>-load.txt); a load
# still above 50 % after 10 minutes fails that step, so no Electron step runs above the limit.
# Every E2E step fails on an `unhandled rejection:` line, and on a failed, flaky, skipped or
# did-not-run line; each also needs its planned `N passed` line (one run each: 2 for
# tray-double-click.test.ts, 2 for startup-reveal.test.ts as in row 6).
# HEAD has not moved since row 0 (baseline.sha); scope-paths requires HEAD at baseline.sha, and
# any other HEAD is S4.
# Skipped, per the plan: the rest of test:e2e, the mcp-server tests and openapi. Each is printed
# with its reason and runs nothing.
$ErrorActionPreference = 'Continue'
$root = (git rev-parse --show-toplevel).Trim()
Set-Location $root
$plan = 'docs/execution/plans/2026-11-22-tray-show-and-baseline-fixes'
$receipts = 'C:/Temp/av-kit/2026-11-22-tray-show-and-baseline-fixes'
# lint_task_contract.py recognises the instantiated receipt paths only through RECEIPTS_DIR and
# fails closed (exit 3) when it is unset, which no user or machine scope sets on this host.
$env:RECEIPTS_DIR = 'C:/Temp/av-kit'
$env:PYTHONIOENCODING = 'utf-8'
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:ELECTRON_RUN_AS_NODE = $null
# RC1 ECN-2: keep the temp dirs away from the home folder. Undated on purpose, as row 0 ran the
# base suites: a dated TEMP folder is the ancestor that TOOLING-PLAN-SLUG-ANCESTOR-MATCH read.
$tmp = 'C:\Temp\av-kit\s102-tmp'
$tmpDated = 'C:\Temp\av-kit\2026-11-22-tray-show-and-baseline-fixes\tmp-dated'
New-Item -ItemType Directory -Force -Path $tmp | Out-Null
New-Item -ItemType Directory -Force -Path $tmpDated | Out-Null
$env:TMP = $tmp
$env:TEMP = $tmp
$base = (Get-Content "$plan/baseline.sha").Trim()

# §Files Modified, this plan folder, the closeout artifacts (the handoffs and reviews under
# .agent/context/handoffs/2026-11-22-tray-show-and-baseline-fixes-*, the reflection, metrics.md
# and current-focus.md) and the paths baseline-dirty.txt already held (its `#` lines are notes,
# not paths). A new plan folder another session's planner writes is skipped the way identity.py
# skips it (untracked, docs/execution/plans/2026-11-16 to 2026-11-22-<slug>/, folder absent from
# HEAD). Anything else changed, HEAD moving, a "Read, never changed" file moving, or a
# baseline-dirty path outside this scope moving from baseline-dirty-hashes.json is S4.
$scopePaths = @"
import hashlib, json, pathlib, re, subprocess, sys
plan = '$plan'
base = '$base'
mine = {
    'ui/src/main/capture-tray.ts',
    'ui/tests/unit/capture-tray.test.ts',
    'ui/tests/e2e/tray-double-click.test.ts',
    'tests/unit/test_capture_adapter.py',
    'tools/validate_closeout_artifacts.py',
    'tests/tooling/test_closeout_plan_slug.py',
    'docs/build-plan/09-screenshot-capture.md',
    '.agent/context/known-issues.yaml',
    '.agent/context/known-issues.md',
    '.agent/context/meu-status.yaml',
    '.agent/context/meu-registry.md',
    'docs/BUILD_PLAN.md',
    '.agent/context/grouping/2026-11-22-tray-show-and-baseline-fixes-session-grouping.md',
    '.agent/context/current-focus.md',
    'docs/execution/metrics.md',
}
prefixes = (plan + '/', '.agent/context/handoffs/2026-11-22-tray-show-and-baseline-fixes-', 'docs/execution/reflections/2026-11-22-tray-show-and-baseline-fixes-')
def is_mine(p):
    return p in mine or p.startswith(prefixes)
scope = json.loads(pathlib.Path(plan + '/baseline-scope.json').read_text(encoding='utf-8'))
shared = {p for p, v in scope.items() if v == 'shared'}
read_only = tuple(p for p in scope if p not in shared and not is_mine(p))
other_plan_re = re.compile(r'^docs/execution/plans/2026-11-(1[6-9]|2[0-2])-[^/]+/')
def git(*args):
    return subprocess.run(['git', *args], capture_output=True, check=True).stdout.decode('utf-8')
def paths(*args):
    return [p for p in git(*args).split('\0') if p]
head_plans = {n for n in git('ls-tree', '--name-only', 'HEAD', 'docs/execution/plans/').splitlines() if n}
def other_plan(p):
    folder = '/'.join(p.split('/')[:4])
    return bool(other_plan_re.match(p)) and not p.startswith(plan + '/') and folder not in head_plans
head = git('rev-parse', 'HEAD').strip()
moved = head != base
allowed = set(mine) | shared
for line in pathlib.Path(plan + '/baseline-dirty.txt').read_text(encoding='utf-8').splitlines():
    if not line or line.startswith('#'):
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
def dirty_now(p):
    return sha(p) if pathlib.Path(p).exists() else 'deleted'
dirty_moved = [p for p, h in sorted(dirty_hashes.items()) if not is_mine(p) and p not in shared and dirty_now(p) != h]
# --no-renames: a rename reports both its source deletion and its destination, so moving an
# out-of-scope file into an allowed path still shows the out-of-scope deletion.
# -z: NUL-separated, so a path with spaces or quoting is one entry.
tracked = paths('diff', '--no-renames', '--name-only', '-z', head)
untracked = [p for p in paths('ls-files', '--others', '--exclude-standard', '-z') if '__pycache__/' not in p]
others = sorted({p for p in untracked if other_plan(p)})
extra = sorted({p for p in tracked + untracked if p not in allowed and not is_mine(p) and p not in others})
print('changed paths:', len(set(tracked + untracked)), 'outside scope:', extra, 'other sessions plan files skipped:', len(others))
print('read-never-changed files:', len(read_only), 'mismatch:', read_only_moved, 'baseline-dirty hash mismatch:', dirty_moved)
print('head:', head, 'baseline:', base)
print('head moved (S4):', moved)
sys.exit(1 if extra or moved or read_only_moved or dirty_moved else 0)
"@

Write-Output 'baseline ui failures excused: [] (ui-tests excuses nothing)'
Write-Output 'baseline py failures excused: [] (py-tests holds no --deselect)'

$skipped = @(
    @{ Id = 'e2e-other'; Stage = 'runtime'; Reason = 'only the tray module changed in the app; tray-double-click runs the tray, and startup-reveal covers the launch and reveal' },
    @{ Id = 'mcp-tests'; Stage = 'full'; Reason = 'no mcp-server file changed' },
    @{ Id = 'openapi'; Stage = 'full'; Reason = 'no API file changed' }
)
foreach ($s in $skipped) {
    Write-Output ("{0} stage={1} skipped reason={2}" -f $s.Id, $s.Stage, $s.Reason)
}

$py = @('uv', 'run', '--no-sync', 'python')
$identity = $py + @("$plan/identity.py")
$hostWait = $py + @("$plan/host-wait.py")
$rowCheck = $py + @("$plan/row-check.py")
$e2e = @('npm', 'run', 'test:e2e', '--')
$vitest = @('npm', 'run', 'test', '--')
$pytest = @('uv', 'run', '--no-sync', 'pytest', '-p', 'no:cacheprovider')
$planPy = @(Get-ChildItem -Path $plan -Filter '*.py' | Sort-Object Name | ForEach-Object { "$plan/$($_.Name)" })
$formatPy = @('tests/tooling/test_closeout_plan_slug.py') + $planPy
$uiTray = @(
    'tests/unit/capture-tray.test.ts', 'tests/unit/app-icon.test.ts', 'tests/unit/capture-main.behavior.test.ts',
    'tests/unit/capture-page.test.ts', 'tests/unit/login-item-ipc.test.ts'
)
$steps = @(
    @{ Id = 'identity-before'; Stage = 'identity'; Argv = $identity },
    @{ Id = 'ui-types'; Stage = 'static'; Cwd = 'ui'; Argv = @('npm', 'run', 'typecheck') },
    @{ Id = 'ui-lint'; Stage = 'static'; Cwd = 'ui'; Argv = @('npm', 'run', 'lint') },
    @{ Id = 'py-types'; Stage = 'static'; Argv = @('uv', 'run', '--no-sync', 'pyright', 'packages/') },
    @{ Id = 'py-lint'; Stage = 'static'; Argv = @('uv', 'run', '--no-sync', 'ruff', 'check', 'packages/', 'tests/', 'tools/validate_closeout_artifacts.py') + $planPy },
    @{ Id = 'py-format'; Stage = 'static'; Argv = @('uv', 'run', '--no-sync', 'ruff', 'format', '--check') + $formatPy },
    @{ Id = 'task-contract'; Stage = 'static'; Argv = $py + @('tools/lint_task_contract.py', '--allowed-builder-classes', 'avkit_builder,avkit_coordinator,avkit_verifier', '--task', "$plan/task.md") },
    @{ Id = 'scope-paths'; Stage = 'static'; Argv = $py + @('-c', $scopePaths) },
    @{ Id = 'line-endings'; Stage = 'static'; Argv = $py + @("$plan/eol-check.py") },
    @{ Id = 'home-path'; Stage = 'static'; Argv = $py + @('tools/check_home_path.py') },
    @{ Id = 'pins-unchanged'; Stage = 'static'; Argv = $rowCheck + @('pins-unchanged') },
    @{ Id = 'named-edits'; Stage = 'static'; Argv = $rowCheck + @('named-edits', '--stage', 'green') },
    @{ Id = 'slug-edit'; Stage = 'static'; Argv = $rowCheck + @('slug-edit') },
    @{ Id = 'canon'; Stage = 'static'; Argv = $rowCheck + @('canon') },
    @{ Id = 'red-unchanged'; Stage = 'static'; Argv = $rowCheck + @('red-unchanged') },
    @{ Id = 'red-check-selftest'; Stage = 'static'; Argv = $py + @("$plan/red-check.py", '--selftest') },
    @{ Id = 'eol-check-selftest'; Stage = 'static'; Argv = $py + @("$plan/eol-check.py", '--selftest') },
    @{ Id = 'row-check-selftest'; Stage = 'static'; Argv = $rowCheck + @('--selftest') },
    @{ Id = 'py-debt'; Stage = 'targeted'; Argv = $pytest + @('tests/tooling/test_closeout_plan_slug.py', 'tests/unit/test_capture_adapter.py', '-k', 'ac_130_10 or ac_164', '-q') },
    @{ Id = 'closeout-selftest'; Stage = 'targeted'; Argv = $py + @('tools/validate_closeout_artifacts.py', '--selftest'); Temp = $tmpDated },
    @{ Id = 'ui-tray'; Stage = 'targeted'; Cwd = 'ui'; Argv = $vitest + $uiTray },
    @{ Id = 'host-load'; Stage = 'host'; Argv = $hostWait },
    @{ Id = 'ui-tests'; Stage = 'full'; Cwd = 'ui'; Argv = @('npm', 'run', 'test') },
    @{ Id = 'py-tests'; Stage = 'full'; Argv = $pytest + @('tests/', '-x', '--tb=short', '-q') },
    @{ Id = 'ui-build'; Stage = 'full'; Cwd = 'ui'; Argv = @('npm', 'run', 'build') },
    @{ Id = 'e2e-tray-double-click'; Stage = 'runtime'; Cwd = 'ui'; Argv = $e2e + @('tests/e2e/tray-double-click.test.ts'); Passed = 2; Electron = $true },
    @{ Id = 'e2e-startup-reveal'; Stage = 'runtime'; Cwd = 'ui'; Argv = $e2e + @('tests/e2e/startup-reveal.test.ts'); Passed = 2; Electron = $true },
    @{ Id = 'state-render'; Stage = 'full'; Argv = $py + @('tools/meu_status.py', 'render', '--check') },
    @{ Id = 'issues-render'; Stage = 'full'; Argv = $py + @('tools/issue_triage.py', 'render', '--check') },
    @{ Id = 'identity-after'; Stage = 'identity'; Argv = $identity }
)

function Get-TestedState([string]$Receipt) {
    $line = Select-String -Path $Receipt -Pattern '^tested_state ' | Select-Object -Last 1
    if ($null -eq $line) { return $null }
    return $line.Line.Substring('tested_state '.Length).Trim()
}

for ($i = 0; $i -lt $steps.Count; $i++) {
    $step = $steps[$i]
    $receipt = "$receipts/tsb-D6-$($step.Id).txt"
    $code = 0
    if ($step.ContainsKey('Electron')) {
        # No Electron step runs above the 50 % limit.
        $loadReceipt = "$receipts/tsb-D6-$($step.Id)-load.txt"
        & rtk proxy @hostWait *> $loadReceipt
        $code = $LASTEXITCODE
        Get-Content $loadReceipt | Select-Object -Last 1 | ForEach-Object { Write-Output ("{0} host-load {1}" -f $step.Id, $_) }
        if ($code -ne 0) {
            Write-Output ("{0}: the host load stayed above 50 %; the step did not run" -f $step.Id)
        }
    }
    if ($code -eq 0) {
        $argv = $step.Argv
        if ($step.ContainsKey('Cwd')) { Set-Location (Join-Path $root $step.Cwd) }
        if ($step.ContainsKey('Temp')) {
            $env:TMP = $step.Temp
            $env:TEMP = $step.Temp
            Write-Output ("{0}: TEMP and TMP are {1} for this step" -f $step.Id, $step.Temp)
        }
        & rtk proxy @argv *> $receipt
        $code = $LASTEXITCODE
        $env:TMP = $tmp
        $env:TEMP = $tmp
        Set-Location $root
        Write-Output ("{0} stage={1} exit={2} receipt={3}" -f $step.Id, $step.Stage, $code, $receipt)
        Get-Content $receipt | Select-Object -Last 6
    }
    if ($code -eq 0 -and $step.ContainsKey('Passed')) {
        # A file list that selects fewer tests than planned must not pass quietly.
        $want = $step.Passed
        $passed = Select-String -Path $receipt -Pattern "^\s+$want passed" -Quiet
        $bad = Select-String -Path $receipt -Pattern '^\s+[0-9]+ (failed|flaky|skipped|did not run)' -Quiet
        Write-Output ("{0}: {1} passed={2} other outcomes={3}" -f $step.Id, $want, $passed, $bad)
        if (-not $passed -or $bad) { $code = 1 }
    }
    if ($code -eq 0 -and $step.Id.StartsWith('e2e-')) {
        # Any rejection record fails the gate, whatever the exit code (S7).
        $records = @(Select-String -Path $receipt -Pattern 'unhandled rejection:' -SimpleMatch).Count
        Write-Output ("{0}: rejection-record lines={1}" -f $step.Id, $records)
        if ($records -ne 0) { $code = 10 }
    }
    if ($code -eq 0 -and $step.Id -eq 'identity-after') {
        $before = Get-TestedState "$receipts/tsb-D6-identity-before.txt"
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
