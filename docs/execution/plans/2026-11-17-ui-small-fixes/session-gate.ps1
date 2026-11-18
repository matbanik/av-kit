# Session 94 fresh-full gate (task H1-2; implementation-plan.md §Session gate).
# The shape of docs/execution/plans/2026-11-17-queue-convert-fixes/session-gate.ps1, with the
# rejection check and the proof lines of 2026-11-17-test-run-reliability/session-gate.ps1, and
# this plan's steps: identity, then the static checks (ui-types, ui-lint, scripts-syntax, the
# task contract, scope-paths, line-endings, home-path, the red-check, eol-check and
# preview-proof selftests, py-format and py-lint on this plan folder's Python), then the
# targeted suites (meu-158-unit, meu-159-unit, preview-unit), then host-load (Session 81
# RULE-2), then the fresh full suites (ui-tests, preview-proof, ui-build), the Electron runs
# (e2e-help-f1-mount, e2e-browse-mount, e2e-ctrl-o, e2e-help-search, e2e-keyboard-shortcuts,
# e2e-advanced-gap, e2e-download-queue, e2e-layout-primitives), state-render and
# issues-render-check, then the identity again.
# Runs from the repository root (P:/av-kit, main only per AGENTS.md §Commits). One receipt per
# id under C:/Temp/av-kit/ui-small-fixes, named us-D6-<id>.txt.
# Fail-fast: the first non-zero step stops the gate and every later step is printed as not_run.
# The gate also fails when tested_state differs between its start and its end (an input changed
# while it ran). Read-only apart from the receipts, the temp folder, ui/out (preview-proof and
# ui-build) and the Electron runs' scratch app data under the temp folder; all are ignored or
# outside the checkout. Nothing here reaches the network or YouTube, and no step dispatches a
# model. preview-proof stops only the process tree its own launch started.
# Exit = the first failing step's code.
# ui-tests excuses nothing: row 0's us-base-ui.txt shows 1619 passed and no failure.
# meu-158-unit runs help-f1-hold.test.tsx and the AC-158.14 pin files; meu-159-unit the
# AC-159.6 unit files; preview-unit preview-script.test.ts and dev-script.test.ts.
# host-load is host-wait.py (the copied load-run.py's host_load_wait, limit 50 %): it waits,
# re-sampling every 30 s for up to 10 minutes, and records the value it ran at. It runs once as
# its own step and again before every Electron step (each into us-D6-<id>-load.txt); a load
# still above 50 % after 10 minutes fails that step, so no Electron step runs above the limit
# (S11).
# Every E2E step fails on an `unhandled rejection:` line, and on a failed, flaky or did-not-run
# line; a step with a planned count also needs its `N passed` line.
# Skipped, per the plan: py-tests, py-types, openapi and mcp-* (H1-4 checks that every
# packages/, mcp-server/, tests/ and tools/ file keeps its baseline-skip-hashes.json hash, and
# none was added or removed; no Python, API, OpenAPI or MCP file changes, S10), and the rest of
# test:e2e (only the help toggle, the Convert browse hold, the Downloader status slot and the
# preview script changed, and their suites run; the clipboard specs never run). Each is printed
# with its reason and runs nothing.
$ErrorActionPreference = 'Continue'
$root = (git rev-parse --show-toplevel).Trim()
Set-Location $root
$plan = 'docs/execution/plans/2026-11-17-ui-small-fixes'
$receipts = 'C:/Temp/av-kit/ui-small-fixes'
# lint_task_contract.py recognises the instantiated receipt paths only through RECEIPTS_DIR and
# fails closed (exit 3) when it is unset, which no user or machine scope sets on this host.
$env:RECEIPTS_DIR = 'C:/Temp/av-kit'
$env:PYTHONIOENCODING = 'utf-8'
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:ELECTRON_RUN_AS_NODE = $null
# RC1 ECN-2: keep the temp dirs away from the home folder, as row 0 ran the base suites.
$tmp = 'C:\Temp\av-kit\ui-small-fixes\tmp'
New-Item -ItemType Directory -Force -Path $tmp | Out-Null
$env:TMP = $tmp
$env:TEMP = $tmp
$base = (Get-Content "$plan/baseline.sha").Trim()

# §Files Modified, this plan folder, the closeout artifacts (the handoffs and reviews under
# .agent/context/handoffs/2026-11-17-ui-small-fixes-*, the reflection, metrics.md and
# current-focus.md) and the paths baseline-dirty.txt already held (its `#` lines are notes, not
# paths). The two temporary probe files are not in `mine`, so they are checked as "Read, never
# changed" entries whose row-0 value is `absent`. A new plan folder another session's planner
# writes is skipped the way identity.py skips it (untracked, docs/execution/plans/
# 2026-11-1[5-7]-<slug>/, folder absent from HEAD). Anything else changed, HEAD moving, a "Read,
# never changed" file moving from baseline-scope.json, or a baseline-dirty path outside this
# scope moving from baseline-dirty-hashes.json is S4.
$scopePaths = @"
import hashlib, json, pathlib, re, subprocess, sys
plan = '$plan'
mine = {
    'ui/src/renderer/src/lib/shell-nav.ts',
    'ui/src/renderer/src/features/converter/convert-commands.ts',
    'ui/src/renderer/src/features/settings/settings-commands.ts',
    'ui/src/renderer/src/components/help/HelpCard.tsx',
    'ui/src/renderer/src/features/downloader/DownloaderPage.tsx',
    'ui/scripts/electron-vite-dev.mjs',
    'ui/scripts/electron-vite-preview.mjs',
    'ui/package.json',
    'ui/tests/unit/dev-script.test.ts',
    'ui/tests/unit/help-f1-hold.test.tsx',
    'ui/tests/unit/preview-script.test.ts',
    'ui/tests/e2e/help-f1-mount.test.ts',
    'ui/tests/e2e/downloader-advanced-gap.test.ts',
    '.agent/docs/commands.md',
    'docs/build-plan/06-gui.md',
    'docs/build-plan/11-page-layout.md',
    '.agent/context/meu-status.yaml',
    '.agent/context/meu-registry.md',
    'docs/BUILD_PLAN.md',
    '.agent/context/known-issues.yaml',
    '.agent/context/known-issues.md',
    '.agent/context/grouping/2026-11-17-value-triage-session-grouping.md',
    'docs/execution/metrics.md',
    '.agent/context/current-focus.md',
}
probes = ('ui/tests/e2e/s94-help-probe.test.ts', 'ui/tests/e2e/s94-gap-probe.test.ts')
scope = json.loads(pathlib.Path(plan + '/baseline-scope.json').read_text(encoding='utf-8'))
read_only = tuple(p for p in scope if p not in mine)
prefixes = (plan + '/', '.agent/context/handoffs/2026-11-17-ui-small-fixes-', 'docs/execution/reflections/2026-11-17-ui-small-fixes-')
other_plan_re = re.compile(r'^docs/execution/plans/2026-11-1[5-7]-[^/]+/')
def git(*args):
    return subprocess.run(['git', *args], capture_output=True, check=True).stdout.decode('utf-8')
head_plans = {n for n in git('ls-tree', '--name-only', 'HEAD', 'docs/execution/plans/').splitlines() if n}
def other_plan(p):
    folder = '/'.join(p.split('/')[:4])
    return bool(other_plan_re.match(p)) and not p.startswith(plan + '/') and folder not in head_plans
allowed = set(mine)
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
probes_present = [p for p in probes if pathlib.Path(p).exists()]
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
print('temporary probe files present:', probes_present)
print('head:', head, 'head moved (S4):', moved)
sys.exit(1 if extra or moved or read_only_moved or dirty_moved or probes_present else 0)
"@

# node --check on both wrapper scripts, which tsc and eslint do not cover.
$scriptsSyntax = @"
import subprocess, sys
bad = 0
for script in ('ui/scripts/electron-vite-dev.mjs', 'ui/scripts/electron-vite-preview.mjs'):
    code = subprocess.run(['node', '--check', script]).returncode
    print('node --check', script, 'exit', code)
    bad = bad or code
sys.exit(1 if bad else 0)
"@

Write-Output 'baseline ui failures excused: [] (ui-tests excuses nothing; us-base-ui.txt shows 1619 passed and no failure)'

$skipped = @(
    @{ Id = 'py-tests'; Stage = 'full'; Reason = 'every packages/ and tests/ file keeps its baseline-skip-hashes.json hash (H1-4); no Python file changes (S10)' },
    @{ Id = 'py-types'; Stage = 'static'; Reason = 'every packages/ file keeps its baseline-skip-hashes.json hash (H1-4); no Python file changes (S10)' },
    @{ Id = 'openapi'; Stage = 'full'; Reason = 'every packages/api/ file keeps its baseline-skip-hashes.json hash (H1-4); no route or schema changes (S10)' },
    @{ Id = 'mcp-types/mcp-build/mcp-tests/mcp-audit'; Stage = 'full'; Reason = 'every mcp-server/ file keeps its baseline-skip-hashes.json hash (H1-4); no MCP tool changes (S10)' },
    @{ Id = 'e2e-other'; Stage = 'runtime'; Reason = 'only the help toggle, the Convert browse hold, the Downloader status slot and the preview script changed, and their suites run; the clipboard specs never run' }
)
foreach ($s in $skipped) {
    Write-Output ("{0} stage={1} skipped reason={2}" -f $s.Id, $s.Stage, $s.Reason)
}

$py = @('uv', 'run', '--no-sync', 'python')
$identity = $py + @("$plan/identity.py")
$hostWait = $py + @("$plan/host-wait.py")
$e2e = @('npm', '--prefix', 'ui', 'run', 'test:e2e', '--')
$vitest = @('npm', '--prefix', 'ui', 'run', 'test', '--')
$planPy = @(Get-ChildItem -Path $plan -Filter '*.py' | Sort-Object Name | ForEach-Object { "$plan/$($_.Name)" })
$unit158 = @(
    'tests/unit/help-f1-hold.test.tsx', 'tests/unit/help-card.test.ts', 'tests/unit/convert-browse-hold.test.ts',
    'tests/unit/convert-page.behavior.test.ts', 'tests/unit/convert-page.test.ts', 'tests/unit/convert-commands.test.ts',
    'tests/unit/common-shortcuts.test.tsx', 'tests/unit/header-toggles.test.ts', 'tests/unit/palette-curation.test.tsx',
    'tests/unit/gui-actions-audit.test.ts', 'tests/unit/capture-page.test.ts', 'tests/unit/shortcuts.test.ts'
)
$unit159 = @(
    'tests/unit/downloader-page.test.ts', 'tests/unit/downloader-page.behavior.test.ts',
    'tests/unit/layout-canon.test.ts', 'tests/unit/layout-primitives.test.ts'
)
$unitPreview = @('tests/unit/preview-script.test.ts', 'tests/unit/dev-script.test.ts')
$steps = @(
    @{ Id = 'identity-before'; Stage = 'identity'; Argv = $identity },
    @{ Id = 'ui-types'; Stage = 'static'; Argv = @('npm', '--prefix', 'ui', 'run', 'typecheck') },
    @{ Id = 'ui-lint'; Stage = 'static'; Argv = @('npm', '--prefix', 'ui', 'run', 'lint') },
    @{ Id = 'scripts-syntax'; Stage = 'static'; Argv = $py + @('-c', $scriptsSyntax) },
    @{ Id = 'task-contract'; Stage = 'static'; Argv = $py + @('tools/lint_task_contract.py', '--allowed-builder-classes', 'avkit_builder,avkit_coordinator,avkit_verifier', '--task', "$plan/task.md") },
    @{ Id = 'scope-paths'; Stage = 'static'; Argv = $py + @('-c', $scopePaths) },
    @{ Id = 'line-endings'; Stage = 'static'; Argv = $py + @("$plan/eol-check.py") },
    @{ Id = 'home-path'; Stage = 'static'; Argv = $py + @('tools/check_home_path.py') },
    @{ Id = 'red-check-selftest'; Stage = 'static'; Argv = $py + @("$plan/red-check.py", '--selftest') },
    @{ Id = 'eol-check-selftest'; Stage = 'static'; Argv = $py + @("$plan/eol-check.py", '--selftest') },
    @{ Id = 'preview-proof-selftest'; Stage = 'static'; Argv = $py + @("$plan/preview-proof.py", '--selftest') },
    @{ Id = 'py-format'; Stage = 'static'; Argv = @('uv', 'run', '--no-sync', 'ruff', 'format', '--check') + $planPy },
    @{ Id = 'py-lint'; Stage = 'static'; Argv = @('uv', 'run', '--no-sync', 'ruff', 'check') + $planPy },
    @{ Id = 'meu-158-unit'; Stage = 'targeted'; Argv = $vitest + $unit158 },
    @{ Id = 'meu-159-unit'; Stage = 'targeted'; Argv = $vitest + $unit159 },
    @{ Id = 'preview-unit'; Stage = 'targeted'; Argv = $vitest + $unitPreview },
    @{ Id = 'host-load'; Stage = 'host'; Argv = $hostWait },
    @{ Id = 'ui-tests'; Stage = 'full'; Argv = @('npm', '--prefix', 'ui', 'run', 'test') },
    @{ Id = 'preview-proof'; Stage = 'runtime'; Argv = $py + @("$plan/preview-proof.py", '--launch', 'preview', '--run-as-node', 'set', '--expect', 'window', '--expect-notice', 'yes'); Electron = $true },
    @{ Id = 'ui-build'; Stage = 'full'; Argv = @('npm', '--prefix', 'ui', 'run', 'build') },
    @{ Id = 'e2e-help-f1-mount'; Stage = 'runtime'; Argv = $e2e + @('tests/e2e/help-f1-mount.test.ts'); Passed = 5; Electron = $true },
    @{ Id = 'e2e-browse-mount'; Stage = 'runtime'; Argv = $e2e + @('tests/e2e/convert-browse-mount.test.ts'); Passed = 4; Electron = $true },
    @{ Id = 'e2e-ctrl-o'; Stage = 'runtime'; Argv = $e2e + @('tests/e2e/convert-queue.test.ts', '-g', 'browses on Convert and is inert'); Passed = 1; Electron = $true },
    @{ Id = 'e2e-help-search'; Stage = 'runtime'; Argv = $e2e + @('tests/e2e/help-search.spec.ts'); Clean = $true; Electron = $true },
    @{ Id = 'e2e-keyboard-shortcuts'; Stage = 'runtime'; Argv = $e2e + @('tests/e2e/keyboard-shortcuts.test.ts'); Clean = $true; Electron = $true },
    @{ Id = 'e2e-advanced-gap'; Stage = 'runtime'; Argv = $e2e + @('tests/e2e/downloader-advanced-gap.test.ts'); Passed = 4; Electron = $true },
    @{ Id = 'e2e-download-queue'; Stage = 'runtime'; Argv = $e2e + @('tests/e2e/download-queue.test.ts'); Clean = $true; Electron = $true },
    @{ Id = 'e2e-layout-primitives'; Stage = 'runtime'; Argv = $e2e + @('tests/e2e/layout-primitives.test.ts'); Clean = $true; Electron = $true },
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
    $receipt = "$receipts/us-D6-$($step.Id).txt"
    $code = 0
    if ($step.ContainsKey('Electron')) {
        # S11: no Electron step runs above the 50 % limit.
        $loadReceipt = "$receipts/us-D6-$($step.Id)-load.txt"
        & rtk proxy @hostWait *> $loadReceipt
        $code = $LASTEXITCODE
        Get-Content $loadReceipt | Select-Object -Last 1 | ForEach-Object { Write-Output ("{0} {1}" -f $step.Id, $_) }
        if ($code -ne 0) {
            Write-Output ("{0}: the host load stayed above 50 % (S11); the step did not run" -f $step.Id)
        }
    }
    if ($code -eq 0) {
        $argv = $step.Argv
        & rtk proxy @argv *> $receipt
        $code = $LASTEXITCODE
        Write-Output ("{0} stage={1} exit={2} receipt={3}" -f $step.Id, $step.Stage, $code, $receipt)
        Get-Content $receipt | Select-Object -Last 6
    }
    if ($step.Id -eq 'preview-proof') {
        Select-String -Path $receipt -Pattern '^(window|notice|notice on stdout|left):' | ForEach-Object { Write-Output ("preview-proof {0}" -f $_.Line) }
    }
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
    if ($code -eq 0 -and $step.Id.StartsWith('e2e-')) {
        # Any rejection record fails the gate, whatever the exit code (S7).
        $records = @(Select-String -Path $receipt -Pattern 'unhandled rejection:' -SimpleMatch).Count
        Write-Output ("{0}: rejection-record lines={1}" -f $step.Id, $records)
        if ($records -ne 0) { $code = 10 }
    }
    if ($code -eq 0 -and $step.Id -eq 'identity-after') {
        $before = Get-TestedState "$receipts/us-D6-identity-before.txt"
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
