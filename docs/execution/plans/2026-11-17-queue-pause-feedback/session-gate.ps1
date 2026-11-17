# Session 88 fresh-full gate (task H1-2; implementation-plan.md §Session gate).
# The shape of docs/execution/plans/2026-11-15-convert-settings-drafts/session-gate.ps1, with this
# plan's steps: identity, then the static checks (ui-types, ui-lint, the task contract,
# scope-paths, line-endings, home-path, the red-check, eol-check and register selftests,
# py-format, py-lint, py-types), then the targeted suites (meu-155-unit, meu-155-py), then
# host-load (Session 81 RULE-2), then the fresh full suites (ui-tests, py-tests, ui-build), the
# Electron runs (e2e-pause, e2e-convert-queue, e2e-download-queue), state-render and
# issues-render-check, then the identity again.
# Runs from the repository root (P:/av-kit, main only per AGENTS.md §Commits). One receipt per
# id under C:/Temp/av-kit/queue-pause-feedback, named qp-D6-<id>.txt.
# Fail-fast: the first non-zero step stops the gate and every later step is printed as not_run.
# The gate also fails when tested_state differs between its start and its end (an input changed
# while it ran). Read-only apart from the receipts, the temp folder, ui/out (ui-build) and the
# Electron tests' scratch app data under the temp folder; all are ignored or outside the
# checkout. Nothing here reaches the network or YouTube, and no step dispatches a model.
# Exit = the first failing step's code.
# py-tests runs the whole suite (no -x) and keeps Session 49b's baseline rule: pytest exit 1
# passes only when every FAILED id also FAILED in row 0's qp-base-py.txt, and nothing ERRORs.
# Row 0 saw no failure (qp-base-py.txt: 3082 passed), so nothing is excused. ui-tests
# (qp-base-ui.txt: 1578 passed) excuses nothing.
# meu-155-unit runs row 3's file list: the three MEU-155 test files and the AC-155.9 pin files
# (the slot fixture, toolbar, header, page, command, help and canon tests).
# host-load samples Win32_Processor.LoadPercentage five times; above 60 % it waits, re-sampling
# every 30 s for up to 10 minutes, and records the value it ran at. It never fails the gate.
# Skipped, per the plan: openapi and mcp-* (H1-4 checks every packages/, mcp-server/, tests/ and
# tools/ file against baseline-skip-hashes.json; only transcript.py changed and
# test_transcript_pause_wake.py was added, and TRANSCRIPT_WAKE changes no route, schema or tool),
# and the rest of test:e2e (only the Convert and Downloader toolbars changed, and their two suites
# run; the Transcript page's markup is unchanged). Each is printed with its reason and runs nothing.
$ErrorActionPreference = 'Continue'
$root = (git rev-parse --show-toplevel).Trim()
Set-Location $root
$plan = 'docs/execution/plans/2026-11-17-queue-pause-feedback'
$receipts = 'C:/Temp/av-kit/queue-pause-feedback'
# lint_task_contract.py recognises the instantiated receipt paths only through RECEIPTS_DIR and
# fails closed (exit 3) when it is unset, which no user or machine scope sets on this host.
$env:RECEIPTS_DIR = 'C:/Temp/av-kit'
$env:PYTHONIOENCODING = 'utf-8'
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:ELECTRON_RUN_AS_NODE = $null
# RC1 ECN-2: keep the temp dirs away from the home folder, as row 0 ran the base suites.
$tmp = 'C:\Temp\av-kit\queue-pause-feedback\tmp'
New-Item -ItemType Directory -Force -Path $tmp | Out-Null
$env:TMP = $tmp
$env:TEMP = $tmp
$base = (Get-Content "$plan/baseline.sha").Trim()

# §Files Modified, this plan folder, the closeout artifacts (the handoffs and reviews under
# .agent/context/handoffs/2026-11-17-queue-pause-feedback-*, the reflection, metrics.md and
# current-focus.md) and the paths baseline-dirty.txt already held. A new plan folder another
# session's planner writes is skipped the way identity.py skips it (untracked,
# docs/execution/plans/2026-11-1[5-7]-<slug>/, folder absent from HEAD). Anything else changed,
# HEAD moving, a "Read, never changed" file moving from baseline-scope.json, or a
# baseline-dirty path outside this scope moving from baseline-dirty-hashes.json is S4.
$scopePaths = @"
import hashlib, json, pathlib, re, subprocess, sys
plan = '$plan'
mine = {
    'ui/src/renderer/src/lib/queue/pause-request.ts',
    'ui/src/renderer/src/components/queue/QueueToolbar.tsx',
    'ui/src/renderer/src/features/converter/convert-commands.ts',
    'ui/src/renderer/src/features/downloader/download-commands.ts',
    'ui/src/renderer/src/features/converter/ConvertPage.tsx',
    'ui/src/renderer/src/features/downloader/DownloaderPage.tsx',
    'ui/src/renderer/src/features/downloader/downloader-help-content.ts',
    'ui/tests/unit/fixtures/queue-slot-baseline.json',
    'ui/tests/unit/queue-pause-feedback.test.tsx',
    'ui/tests/unit/convert-page.behavior.test.ts',
    'ui/tests/unit/downloader-page.behavior.test.ts',
    'ui/tests/e2e/queue-pause-feedback.test.ts',
    'packages/core/src/avkit_core/services/transcript.py',
    'tests/unit/test_transcript_pause_wake.py',
    'docs/build-plan/03-service-layer.md',
    'docs/build-plan/10-queue-card-ui.md',
    'docs/build-plan/build-priority-matrix.md',
    '.agent/context/meu-status.yaml',
    '.agent/context/meu-registry.md',
    'docs/BUILD_PLAN.md',
    '.agent/context/known-issues.yaml',
    '.agent/context/known-issues.md',
    '.agent/context/grouping/2026-11-15-post-rc3-triage-residuals-session-grouping.md',
    'docs/execution/metrics.md',
    '.agent/context/current-focus.md',
}
scope = json.loads(pathlib.Path(plan + '/baseline-scope.json').read_text(encoding='utf-8'))
read_only = tuple(p for p in scope if p not in mine)
prefixes = (plan + '/', '.agent/context/handoffs/2026-11-17-queue-pause-feedback-', 'docs/execution/reflections/2026-11-17-queue-pause-feedback-')
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

# An id is excused only when row 0's baseline receipt really shows it FAILED: a missing
# receipt excuses nothing.
$baseReceipt = "$receipts/qp-base-py.txt"
$baselinePyFailed = @()
if (Test-Path $baseReceipt) {
    $baselinePyFailed = @(Select-String -Path $baseReceipt -Pattern '^FAILED (\S+)' | ForEach-Object { $_.Matches[0].Groups[1].Value })
}
Write-Output ("baseline py failures excused: [{0}] (receipt {1})" -f ($baselinePyFailed -join ', '), $baseReceipt)
Write-Output 'baseline ui failures excused: [] (ui-tests excuses nothing; qp-base-ui.txt shows no failure)'

$skipped = @(
    @{ Id = 'openapi'; Stage = 'full'; Reason = 'every packages/api/ file keeps its baseline-skip-hashes.json hash (H1-4); TRANSCRIPT_WAKE changes no route or schema' },
    @{ Id = 'mcp-types/mcp-build/mcp-tests/mcp-audit'; Stage = 'full'; Reason = 'every mcp-server/ file keeps its baseline-skip-hashes.json hash (H1-4); no MCP tool changes' },
    @{ Id = 'e2e-other'; Stage = 'runtime'; Reason = 'only the Convert and Downloader toolbars changed and their two suites run; the Transcript page markup is unchanged' }
)
foreach ($s in $skipped) {
    Write-Output ("{0} stage={1} skipped reason={2}" -f $s.Id, $s.Stage, $s.Reason)
}

$py = @('uv', 'run', '--no-sync', 'python')
$identity = $py + @("$plan/identity.py")
$e2e = @('npm', '--prefix', 'ui', 'run', 'test:e2e', '--')
$vitest = @('npm', '--prefix', 'ui', 'run', 'test', '--')
$planPy = @(Get-ChildItem -Path $plan -Filter '*.py' | Sort-Object Name | ForEach-Object { "$plan/$($_.Name)" })
$pyTouched = $planPy + @('packages/core/src/avkit_core/services/transcript.py', 'tests/unit/test_transcript_pause_wake.py')
$unitFiles = @(
    'tests/unit/queue-pause-feedback.test.tsx', 'tests/unit/convert-page.behavior.test.ts', 'tests/unit/downloader-page.behavior.test.ts',
    'tests/unit/queue-card-slots.test.tsx', 'tests/unit/queue-toolbar.test.ts', 'tests/unit/queue-header-row.test.tsx',
    'tests/unit/convert-page.test.ts', 'tests/unit/downloader-page.test.ts', 'tests/unit/convert-commands.test.ts',
    'tests/unit/download-commands.test.ts', 'tests/unit/help-card.test.ts', 'tests/unit/layout-canon.test.ts',
    'tests/unit/queue-canon.test.ts', 'tests/unit/command-palette.test.ts'
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
    @{ Id = 'register-selftest'; Stage = 'static'; Argv = $py + @("$plan/register-meu-155.py", '--selftest') },
    @{ Id = 'py-format'; Stage = 'static'; Argv = @('uv', 'run', '--no-sync', 'ruff', 'format', '--check') + $pyTouched },
    @{ Id = 'py-lint'; Stage = 'static'; Argv = @('uv', 'run', '--no-sync', 'ruff', 'check') + $pyTouched },
    @{ Id = 'py-types'; Stage = 'static'; Argv = @('uv', 'run', '--no-sync', 'pyright', 'packages/') },
    @{ Id = 'meu-155-unit'; Stage = 'targeted'; Argv = $vitest + $unitFiles },
    @{ Id = 'meu-155-py'; Stage = 'targeted'; Argv = @('uv', 'run', '--no-sync', 'pytest', 'tests/unit/test_transcript_pause_wake.py', 'tests/unit/test_services.py', '--tb=short', '-q', '-rfE') },
    @{ Id = 'host-load'; Stage = 'host'; HostLoad = $true },
    @{ Id = 'ui-tests'; Stage = 'full'; Argv = @('npm', '--prefix', 'ui', 'run', 'test') },
    @{ Id = 'py-tests'; Stage = 'full'; Argv = @('uv', 'run', '--no-sync', 'pytest', 'tests/', '--tb=short', '-q', '-rfE') },
    @{ Id = 'ui-build'; Stage = 'full'; Argv = @('npm', '--prefix', 'ui', 'run', 'build') },
    @{ Id = 'e2e-pause'; Stage = 'runtime'; Argv = $e2e + @('tests/e2e/queue-pause-feedback.test.ts'); Passed = 4 },
    @{ Id = 'e2e-convert-queue'; Stage = 'runtime'; Argv = $e2e + @('tests/e2e/convert-queue.test.ts'); Clean = $true },
    @{ Id = 'e2e-download-queue'; Stage = 'runtime'; Argv = $e2e + @('tests/e2e/download-queue.test.ts'); Clean = $true },
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
    $receipt = "$receipts/qp-D6-$($step.Id).txt"
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
        # A file list that selects fewer tests than planned must not pass quietly.
        $want = $step.Passed
        $passed = Select-String -Path $receipt -Pattern "^\s+$want passed" -Quiet
        $bad = Select-String -Path $receipt -Pattern '^\s+[0-9]+ (failed|flaky|skipped|did not run)' -Quiet
        Write-Output ("{0}: {1} passed={2} other outcomes={3}" -f $step.Id, $want, $passed, $bad)
        if (-not $passed -or $bad) { $code = 1 }
    }
    if ($code -eq 0 -and $step.ContainsKey('Clean')) {
        # An existing Electron suite passes only with no failed or flaky test (S5, S8).
        $passed = Select-String -Path $receipt -Pattern '^\s+[0-9]+ passed' -Quiet
        $bad = Select-String -Path $receipt -Pattern '^\s+[0-9]+ (failed|flaky|did not run)' -Quiet
        Write-Output ("{0}: passed line={1} failed or flaky={2}" -f $step.Id, $passed, $bad)
        if (-not $passed -or $bad) { $code = 1 }
    }
    if ($code -eq 0 -and $step.Id -eq 'identity-after') {
        $before = Get-TestedState "$receipts/qp-D6-identity-before.txt"
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
