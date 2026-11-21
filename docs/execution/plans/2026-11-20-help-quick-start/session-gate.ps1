# Session 99 fresh-full gate (task H1-2; implementation-plan.md §Session gate).
# The shape of docs/execution/plans/2026-11-17-ui-small-fixes/session-gate.ps1, with the
# per-step working folder (Cwd) of 2026-11-19-e2e-host-parity/session-gate.ps1, and this plan's
# steps: identity, then the static checks (ui-types, ui-lint, the task contract, scope-paths,
# line-endings, home-path, skill-identity, pins-unchanged, red-unchanged, the red-check,
# eol-check and row-check selftests, py-format and py-lint), then the targeted suites (ste-gate,
# help-unit), then host-load (Session 81 RULE-2), then the fresh full suites (ui-tests,
# py-tooling, ui-build), the Electron runs (e2e-help-quick-start, e2e-help-search,
# e2e-help-f1-mount, e2e-keyboard-shortcuts), state-render, then the identity again.
# Runs from the repository root (P:/av-kit, main only per AGENTS.md §Commits). One receipt per
# id under C:/Temp/av-kit/help-quick-start, named hq-D6-<id>.txt.
# Fail-fast: the first non-zero step stops the gate and every later step is printed as not_run.
# The gate also fails when tested_state differs between its start and its end (an input changed
# while it ran). Read-only apart from the receipts, the temp folder, ui/out (ui-build) and the
# Electron runs' scratch app data under the temp folder; all are ignored or outside the
# checkout. Nothing here reaches the network or YouTube, and no step dispatches a model.
# The screenshot generator (help:shots) is not a gate step: AC-162.7 (in help-unit and
# ui-tests) and AC-162.11 (in e2e-help-quick-start) check its output.
# Exit = the first failing step's code.
# ui-tests excuses nothing: row 0's hq-base-ui.txt shows no failure.
# help-unit runs help-quick-start.test.tsx, help-shots-privacy.test.ts, the §Test pins unit files
# and settings-page.test.ts (D-1296).
# host-load is host-wait.py (the copied load-run.py's host_load_wait, limit 50 %): it waits,
# re-sampling every 30 s for up to 10 minutes, and records the value it ran at. It runs once as
# its own step and again before every Electron step (each into hq-D6-<id>-load.txt); a load
# still above 50 % after 10 minutes fails that step, so no Electron step runs above the limit.
# Every E2E step fails on an `unhandled rejection:` line, and on a failed, flaky, skipped or
# did-not-run line; each also needs its planned `N passed` line (row 9's counts, one run each).
# HEAD moved once after row 0: Session 100 committed 49ab790 on top of baseline.sha (f1ba411),
# with none of this plan's paths apart from the `shared` files of baseline-scope.json (the
# re-baseline note of 2026-11-21 in the handoff). scope-paths accepts HEAD at baseline.sha or at
# that one commit, and only when f1ba411 is its ancestor and the commit changed no path of this
# plan other than the shared files. A path that commit changed is checked against HEAD (clean in
# git status) instead of its row-0 hash; every other path keeps its row-0 hash. Any other HEAD
# is S4.
# Skipped, per the plan: py-types and the full py-tests (no Python product file changes; H1-4
# checks that every packages/ and mcp-server/ file keeps its baseline-skip-hashes.json hash, and
# tests/tooling runs in full as py-tooling), openapi and mcp-* (the same H1-4 hashes), and the
# rest of test:e2e (only the help card changed, and its suites run). Each is printed with its
# reason and runs nothing.
$ErrorActionPreference = 'Continue'
$root = (git rev-parse --show-toplevel).Trim()
Set-Location $root
$plan = 'docs/execution/plans/2026-11-20-help-quick-start'
$receipts = 'C:/Temp/av-kit/help-quick-start'
# lint_task_contract.py recognises the instantiated receipt paths only through RECEIPTS_DIR and
# fails closed (exit 3) when it is unset, which no user or machine scope sets on this host.
$env:RECEIPTS_DIR = 'C:/Temp/av-kit'
$env:PYTHONIOENCODING = 'utf-8'
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:ELECTRON_RUN_AS_NODE = $null
# RC1 ECN-2: keep the temp dirs away from the home folder, as row 0 ran the base suites.
$tmp = 'C:\Temp\av-kit\help-quick-start\tmp'
New-Item -ItemType Directory -Force -Path $tmp | Out-Null
$env:TMP = $tmp
$env:TEMP = $tmp
$base = (Get-Content "$plan/baseline.sha").Trim()
$rebase = '49ab790cac04dfb7cdd042476a717985d4359ac8'

# §Files Modified (with D-1296's settings-page.test.ts), this plan folder, the closeout
# artifacts (the handoffs and reviews under .agent/context/handoffs/2026-11-20-help-quick-start-*,
# the reflection, metrics.md and current-focus.md) and the paths baseline-dirty.txt already held
# (its `#` lines are notes, not paths). A new plan folder another session's planner writes is
# skipped the way identity.py skips it (untracked, docs/execution/plans/2026-11-15 to
# 2026-11-21-<slug>/, folder absent from HEAD). Anything else changed, HEAD moving other than as
# described above, a "Read, never changed" file moving, or a baseline-dirty path moving from
# baseline-dirty-hashes.json is S4.
$scopePaths = @"
import hashlib, json, pathlib, re, subprocess, sys
plan = '$plan'
base = '$base'
rebase = '$rebase'
mine = {
    'ui/src/renderer/src/components/help/HelpCard.tsx',
    'ui/src/renderer/src/components/help/quick-start.json',
    'ui/src/renderer/src/components/help/quick-start.ts',
    'ui/src/renderer/src/components/help/help-shots.ts',
    'ui/src/renderer/src/styles.css',
    'ui/src/renderer/src/features/downloader/downloader-help-content.ts',
    'ui/src/renderer/src/features/transcript/transcript-help-content.ts',
    'ui/src/renderer/src/features/tts/tts-help-content.ts',
    'ui/src/renderer/src/features/converter/convert-help-content.ts',
    'ui/src/renderer/src/features/capture/capture-help-content.ts',
    'ui/src/renderer/src/features/settings/settings-help-content.ts',
    'ui/tsconfig.json',
    'ui/package.json',
    'ui/playwright.help-shots.config.ts',
    'ui/tests/unit/help-quick-start.test.tsx',
    'ui/tests/unit/help-shots-privacy.test.ts',
    'ui/tests/e2e/help-quick-start.test.ts',
    'ui/tests/e2e/test-ids.ts',
    'ui/tests/unit/failure-reason-copy.test.ts',
    'ui/tests/unit/capture-page.test.ts',
    'ui/tests/unit/convert-page.test.ts',
    'ui/tests/unit/settings-page.test.ts',
    '.agent/skills/README.md',
    'tools/help_guide_ste.py',
    'tests/tooling/test_help_guide_ste.py',
    'docs/build-plan/06-gui.md',
    'docs/build-plan/build-priority-matrix.md',
    '.agent/context/meu-status.yaml',
    '.agent/context/meu-registry.md',
    'docs/BUILD_PLAN.md',
    '.agent/docs/commands.md',
    'docs/execution/metrics.md',
    '.agent/context/current-focus.md',
}
mine_dirs = ('ui/src/renderer/src/assets/help', 'ui/tests/help-shots', '.agent/skills/asd-ste100')
prefixes = (plan + '/', '.agent/context/handoffs/2026-11-20-help-quick-start-', 'docs/execution/reflections/2026-11-20-help-quick-start-')
def is_mine(p):
    return p in mine or p.startswith(prefixes) or any(p == d or p.startswith(d + '/') for d in mine_dirs)
scope = json.loads(pathlib.Path(plan + '/baseline-scope.json').read_text(encoding='utf-8'))
shared = {p for p, v in scope.items() if v == 'shared'}
read_only = tuple(p for p in scope if p not in shared and not is_mine(p))
other_plan_re = re.compile(r'^docs/execution/plans/2026-11-(1[5-9]|2[01])-[^/]+/')
def git(*args):
    return subprocess.run(['git', *args], capture_output=True, check=True).stdout.decode('utf-8')
def paths(*args):
    return [p for p in git(*args).split('\0') if p]
head_plans = {n for n in git('ls-tree', '--name-only', 'HEAD', 'docs/execution/plans/').splitlines() if n}
def other_plan(p):
    folder = '/'.join(p.split('/')[:4])
    return bool(other_plan_re.match(p)) and not p.startswith(plan + '/') and folder not in head_plans
head = git('rev-parse', 'HEAD').strip()
committed = set()
rebase_ok = True
if head == rebase:
    rebase_ok = subprocess.run(['git', 'merge-base', '--is-ancestor', base, rebase]).returncode == 0
    committed = set(paths('diff', '--no-renames', '--name-only', '-z', base, rebase))
committed_mine = sorted(p for p in committed if is_mine(p) and p not in shared)
moved = head not in (base, rebase) or not rebase_ok or bool(committed_mine)
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
def clean(p):
    return git('status', '--porcelain', '--untracked-files=all', '--', p) == ''
read_only_moved = [p for p in read_only if (not clean(p) if p in committed else sha(p) != scope[p])]
dirty_hashes = json.loads(pathlib.Path(plan + '/baseline-dirty-hashes.json').read_text(encoding='utf-8'))
def dirty_now(p):
    return sha(p) if pathlib.Path(p).exists() else 'deleted'
dirty_moved = [p for p, h in sorted(dirty_hashes.items()) if (not clean(p) if p in committed else dirty_now(p) != h)]
# --no-renames: a rename reports both its source deletion and its destination, so moving an
# out-of-scope file into an allowed path still shows the out-of-scope deletion.
# -z: NUL-separated, so a path with spaces or quoting is one entry.
tracked = paths('diff', '--no-renames', '--name-only', '-z', head)
untracked = [p for p in paths('ls-files', '--others', '--exclude-standard', '-z') if '__pycache__/' not in p]
others = sorted({p for p in untracked if other_plan(p)})
extra = sorted({p for p in tracked + untracked if p not in allowed and not is_mine(p) and p not in others})
print('changed paths:', len(set(tracked + untracked)), 'outside scope:', extra, 'other sessions plan files skipped:', len(others))
print('read-never-changed files:', len(read_only), 'mismatch:', read_only_moved, 'baseline-dirty hash mismatch:', dirty_moved)
print('head:', head, 'baseline:', base, 're-baseline:', rebase, 'committed since baseline:', len(committed), 'of them this plan s (not shared):', committed_mine, 'ancestor ok:', rebase_ok)
print('head moved (S4):', moved)
sys.exit(1 if extra or moved or read_only_moved or dirty_moved else 0)
"@

Write-Output 'baseline ui failures excused: [] (ui-tests excuses nothing)'

$skipped = @(
    @{ Id = 'py-types'; Stage = 'static'; Reason = 'every packages/ file keeps its baseline-skip-hashes.json hash (H1-4); no Python product file changes' },
    @{ Id = 'py-tests'; Stage = 'full'; Reason = 'every packages/ file keeps its baseline-skip-hashes.json hash (H1-4); no Python product file changes; tests/tooling runs in full as py-tooling' },
    @{ Id = 'openapi'; Stage = 'full'; Reason = 'every packages/api/ file keeps its baseline-skip-hashes.json hash (H1-4); no route or schema changes' },
    @{ Id = 'mcp-types/mcp-build/mcp-tests/mcp-audit'; Stage = 'full'; Reason = 'every mcp-server/ file keeps its baseline-skip-hashes.json hash (H1-4); no MCP tool changes' },
    @{ Id = 'e2e-other'; Stage = 'runtime'; Reason = 'only the help card changed, and its suites run (help-quick-start, help-search, help-f1-mount, keyboard-shortcuts)' }
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
$planPy = @(Get-ChildItem -Path $plan -Filter '*.py' | Sort-Object Name | ForEach-Object { "$plan/$($_.Name)" })
$stePy = @('tools/help_guide_ste.py', 'tests/tooling/test_help_guide_ste.py') + $planPy
$helpUnit = @(
    'tests/unit/help-quick-start.test.tsx', 'tests/unit/help-shots-privacy.test.ts',
    'tests/unit/help-card.test.ts', 'tests/unit/help-f1-hold.test.tsx', 'tests/unit/capture-help-content.test.ts',
    'tests/unit/capture-action-row.test.ts', 'tests/unit/capture-copy-image.behavior.test.ts',
    'tests/unit/capture-redact.behavior.test.ts', 'tests/unit/capture-tool-style.test.ts',
    'tests/unit/failure-reason-copy.test.ts', 'tests/unit/queue-pause-feedback.test.tsx',
    'tests/unit/layout-primitives.test.ts', 'tests/unit/settings-rail.test.tsx', 'tests/unit/common-shortcuts.test.tsx',
    'tests/unit/gui-actions-audit.test.ts', 'tests/unit/capture-page.test.ts', 'tests/unit/convert-page.test.ts',
    'tests/unit/settings-page.test.ts'
)
$steps = @(
    @{ Id = 'identity-before'; Stage = 'identity'; Argv = $identity },
    @{ Id = 'ui-types'; Stage = 'static'; Cwd = 'ui'; Argv = @('npm', 'run', 'typecheck') },
    @{ Id = 'ui-lint'; Stage = 'static'; Cwd = 'ui'; Argv = @('npm', 'run', 'lint') },
    @{ Id = 'task-contract'; Stage = 'static'; Argv = $py + @('tools/lint_task_contract.py', '--allowed-builder-classes', 'avkit_builder,avkit_coordinator,avkit_verifier', '--task', "$plan/task.md") },
    @{ Id = 'scope-paths'; Stage = 'static'; Argv = $py + @('-c', $scopePaths) },
    @{ Id = 'line-endings'; Stage = 'static'; Argv = $py + @("$plan/eol-check.py") },
    @{ Id = 'home-path'; Stage = 'static'; Argv = $py + @('tools/check_home_path.py') },
    @{ Id = 'skill-identity'; Stage = 'static'; Argv = $rowCheck + @('skill') },
    @{ Id = 'pins-unchanged'; Stage = 'static'; Argv = $rowCheck + @('pins-unchanged') },
    @{ Id = 'red-unchanged'; Stage = 'static'; Argv = $rowCheck + @('red-unchanged') },
    @{ Id = 'red-check-selftest'; Stage = 'static'; Argv = $py + @("$plan/red-check.py", '--selftest') },
    @{ Id = 'eol-check-selftest'; Stage = 'static'; Argv = $py + @("$plan/eol-check.py", '--selftest') },
    @{ Id = 'row-check-selftest'; Stage = 'static'; Argv = $rowCheck + @('--selftest') },
    @{ Id = 'py-format'; Stage = 'static'; Argv = @('uv', 'run', '--no-sync', 'ruff', 'format', '--check') + $stePy },
    @{ Id = 'py-lint'; Stage = 'static'; Argv = @('uv', 'run', '--no-sync', 'ruff', 'check') + $stePy },
    @{ Id = 'ste-gate'; Stage = 'targeted'; Argv = @('uv', 'run', '--no-sync', 'pytest', 'tests/tooling/test_help_guide_ste.py', '-q', '-p', 'no:cacheprovider') },
    @{ Id = 'help-unit'; Stage = 'targeted'; Cwd = 'ui'; Argv = $vitest + $helpUnit },
    @{ Id = 'host-load'; Stage = 'host'; Argv = $hostWait },
    @{ Id = 'ui-tests'; Stage = 'full'; Cwd = 'ui'; Argv = @('npm', 'run', 'test') },
    @{ Id = 'py-tooling'; Stage = 'full'; Argv = @('uv', 'run', '--no-sync', 'pytest', 'tests/tooling', '-q', '-p', 'no:cacheprovider') },
    @{ Id = 'ui-build'; Stage = 'full'; Cwd = 'ui'; Argv = @('npm', 'run', 'build') },
    @{ Id = 'e2e-help-quick-start'; Stage = 'runtime'; Cwd = 'ui'; Argv = $e2e + @('tests/e2e/help-quick-start.test.ts'); Passed = 9; Electron = $true },
    @{ Id = 'e2e-help-search'; Stage = 'runtime'; Cwd = 'ui'; Argv = $e2e + @('tests/e2e/help-search.spec.ts'); Passed = 3; Electron = $true },
    @{ Id = 'e2e-help-f1-mount'; Stage = 'runtime'; Cwd = 'ui'; Argv = $e2e + @('tests/e2e/help-f1-mount.test.ts'); Passed = 5; Electron = $true },
    @{ Id = 'e2e-keyboard-shortcuts'; Stage = 'runtime'; Cwd = 'ui'; Argv = $e2e + @('tests/e2e/keyboard-shortcuts.test.ts'); Passed = 2; Electron = $true },
    @{ Id = 'state-render'; Stage = 'full'; Argv = $py + @('tools/meu_status.py', 'render', '--check') },
    @{ Id = 'identity-after'; Stage = 'identity'; Argv = $identity }
)

function Get-TestedState([string]$Receipt) {
    $line = Select-String -Path $Receipt -Pattern '^tested_state ' | Select-Object -Last 1
    if ($null -eq $line) { return $null }
    return $line.Line.Substring('tested_state '.Length).Trim()
}

for ($i = 0; $i -lt $steps.Count; $i++) {
    $step = $steps[$i]
    $receipt = "$receipts/hq-D6-$($step.Id).txt"
    $code = 0
    if ($step.ContainsKey('Electron')) {
        # No Electron step runs above the 50 % limit.
        $loadReceipt = "$receipts/hq-D6-$($step.Id)-load.txt"
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
        & rtk proxy @argv *> $receipt
        $code = $LASTEXITCODE
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
        $before = Get-TestedState "$receipts/hq-D6-identity-before.txt"
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
