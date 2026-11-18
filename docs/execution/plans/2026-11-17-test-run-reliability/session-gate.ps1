# Session 90 fresh-full gate (task H1-2; implementation-plan.md §Session gate).
# The shape of docs/execution/plans/2026-11-17-queue-convert-fixes/session-gate.ps1, with this
# plan's steps: identity, then the static checks (ui-types, ui-lint, the task contract,
# scope-paths, line-endings, home-path, the red-check, eol-check, wait-check, load-run and
# dev-proof selftests, py-format on the TTS file and this plan folder's Python, py-lint on both
# test files and this plan folder's Python, dev-script-syntax), then the targeted checks (py-two,
# wait-check, ui-unit), then host-load (Session 81 RULE-2), then the runtime dev-proof-set
# before ui-build, then the fresh full suites (py-tests, ui-tests, ui-build, ui-electron),
# issues-render-check and state-render, then the identity again.
# Runs from the repository root (P:/av-kit, main only per AGENTS.md §Commits). One receipt per
# id under C:/Temp/av-kit/test-run-reliability, named trr-D6-<id>.txt.
# Fail-fast: the first non-zero step stops the gate and every later step is printed as not_run.
# The gate also fails when tested_state differs between its start and its end (an input changed
# while it ran). Read-only apart from the receipts, the temp folder, ui/out (dev-proof-set and
# ui-build) and the scratch app data under the temp folder; all are ignored or outside the
# checkout. Nothing here reaches the network or YouTube, and no step dispatches a model.
# dev-proof-set stops only the process tree its own launch started (S11).
# Exit = the first failing step's code.
# ui-tests excuses only ids that trr-base-ui.txt shows failing (none: 1614 passed).
# py-tests runs the D6 argv (-x). If it stops on a failure, it runs the D6 argv again without -x
# and passes only when its failing ids are a subset of the ids trr-base-py.txt shows failing.
# ui-electron is the full test:e2e; any receipt line holding `unhandled rejection:` fails it (S10).
# host-load samples Win32_Processor.LoadPercentage five times; above 60 % it waits, re-sampling
# every 30 s for up to 10 minutes, and records the value it ran at. It never fails the gate.
# Skipped, per the plan: py-types, openapi and mcp-* (H1-4 checks that every packages/,
# mcp-server/ and tools/ file keeps its baseline-skip-hashes.json hash, and none was added or
# removed; S13). Each is printed with its reason and runs nothing.
$ErrorActionPreference = 'Continue'
$root = (git rev-parse --show-toplevel).Trim()
Set-Location $root
$plan = 'docs/execution/plans/2026-11-17-test-run-reliability'
$receipts = 'C:/Temp/av-kit/test-run-reliability'
# lint_task_contract.py recognises the instantiated receipt paths only through RECEIPTS_DIR and
# fails closed (exit 3) when it is unset, which no user or machine scope sets on this host.
$env:RECEIPTS_DIR = 'C:/Temp/av-kit'
$env:PYTHONIOENCODING = 'utf-8'
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:ELECTRON_RUN_AS_NODE = $null
# RC1 ECN-2: keep the temp dirs away from the home folder, as row 0 ran the base suites.
$tmp = 'C:\Temp\av-kit\test-run-reliability\tmp'
New-Item -ItemType Directory -Force -Path $tmp | Out-Null
$env:TMP = $tmp
$env:TEMP = $tmp
$base = (Get-Content "$plan/baseline.sha").Trim()

# §Files Modified, this plan folder, the closeout artifacts (the handoffs and reviews under
# .agent/context/handoffs/2026-11-17-test-run-reliability-*, the reflection, metrics.md and
# current-focus.md) and the paths baseline-dirty.txt already held. A new plan folder another
# session's planner writes is skipped the way identity.py skips it (untracked,
# docs/execution/plans/2026-11-1[5-7]-<slug>/, folder absent from HEAD). Anything else changed,
# HEAD moving, a "Read, never changed" file moving from baseline-scope.json, or a baseline-dirty
# path outside this scope moving from baseline-dirty-hashes.json is S4.
$scopePaths = @"
import hashlib, json, pathlib, re, subprocess, sys
plan = '$plan'
mine = {
    'tests/integration/test_tts_assets.py',
    'tests/integration/test_youtube_adapter.py',
    'ui/tests/e2e/main-error-watch.cjs',
    'ui/tests/e2e/electron-env.ts',
    'ui/tests/e2e/electron-app.ts',
    'ui/package.json',
    'ui/scripts/electron-vite-dev.mjs',
    'ui/tests/unit/rejection-watch.test.ts',
    'ui/tests/unit/dev-script.test.ts',
    'ui/tests/e2e/main-rejection-watch.test.ts',
    '.agent/docs/commands.md',
    '.agent/context/known-issues.yaml',
    '.agent/context/known-issues.md',
    '.agent/context/grouping/2026-11-17-post-session-88-triage-session-grouping.md',
    'docs/execution/metrics.md',
    '.agent/context/current-focus.md',
}
scope = json.loads(pathlib.Path(plan + '/baseline-scope.json').read_text(encoding='utf-8'))
read_only = tuple(p for p in scope if p not in mine)
prefixes = (plan + '/', '.agent/context/handoffs/2026-11-17-test-run-reliability-', 'docs/execution/reflections/2026-11-17-test-run-reliability-')
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
dirty_moved = [p for p, h in sorted(dirty_hashes.items()) if not p.startswith(prefixes) and p not in mine and (sha(p) if pathlib.Path(p).exists() else 'deleted') != h]
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

# py-tests: the D6 argv; on a failure, the argv again without -x, passing only when every failing
# id is one that trr-base-py.txt shows failing.
$pyTests = @"
import re, subprocess, sys
argv = ['uv', 'run', '--no-sync', 'pytest', 'tests/', '-x', '--tb=short', '-q']
first = subprocess.run(argv)
if first.returncode == 0:
    print('py-tests: D6 argv exit 0')
    sys.exit(0)
def failing(text):
    return {m.group(1) for m in re.finditer(r'^(?:FAILED|ERROR) (\S+)', text, re.M)}
base = failing(open('$receipts/trr-base-py.txt', encoding='utf-8', errors='replace').read())
second = subprocess.run([a for a in argv if a != '-x'], capture_output=True, text=True, encoding='utf-8', errors='replace')
sys.stdout.write(second.stdout[-4000:])
now = failing(second.stdout)
new = sorted(now - base)
print('py-tests: D6 argv exit', first.returncode, '; rerun without -x exit', second.returncode, '; failing', sorted(now), '; base failing', sorted(base), '; not in base', new)
sys.exit(0 if second.returncode in (0, 1) and not new and (second.returncode == 0 or now) else 1)
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

Write-Output 'baseline ui failures excused: [] (ui-tests excuses nothing; trr-base-ui.txt shows 1614 passed and no failure)'

$skipped = @(
    @{ Id = 'py-types'; Stage = 'static'; Reason = 'every packages/ file keeps its baseline-skip-hashes.json hash (H1-4); no product Python file changes (S13)' },
    @{ Id = 'openapi'; Stage = 'full'; Reason = 'every packages/api/ file keeps its baseline-skip-hashes.json hash (H1-4); no route or schema changes (S13)' },
    @{ Id = 'mcp-types/mcp-build/mcp-tests/mcp-audit'; Stage = 'full'; Reason = 'every mcp-server/ file keeps its baseline-skip-hashes.json hash (H1-4); no MCP tool changes (S13)' }
)
foreach ($s in $skipped) {
    Write-Output ("{0} stage={1} skipped reason={2}" -f $s.Id, $s.Stage, $s.Reason)
}

$py = @('uv', 'run', '--no-sync', 'python')
$identity = $py + @("$plan/identity.py")
$planPy = @(Get-ChildItem -Path $plan -Filter '*.py' | Sort-Object Name | ForEach-Object { "$plan/$($_.Name)" })
$tts = 'tests/integration/test_tts_assets.py'
$yt = 'tests/integration/test_youtube_adapter.py'
$two = @($tts, $yt, 'tests/integration/test_tts_voice_packs.py')
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
    @{ Id = 'wait-check-selftest'; Stage = 'static'; Argv = $py + @("$plan/wait-check.py", '--selftest') },
    @{ Id = 'load-run-selftest'; Stage = 'static'; Argv = $py + @("$plan/load-run.py", '--selftest') },
    @{ Id = 'dev-proof-selftest'; Stage = 'static'; Argv = $py + @("$plan/dev-proof.py", '--selftest') },
    @{ Id = 'py-format'; Stage = 'static'; Argv = @('uv', 'run', '--no-sync', 'ruff', 'format', '--check', $tts) + $planPy },
    @{ Id = 'py-lint'; Stage = 'static'; Argv = @('uv', 'run', '--no-sync', 'ruff', 'check', $tts, $yt) + $planPy },
    @{ Id = 'dev-script-syntax'; Stage = 'static'; Argv = @('node', '--check', 'ui/scripts/electron-vite-dev.mjs') },
    @{ Id = 'py-two'; Stage = 'targeted'; Argv = $py + @('-m', 'pytest', '-q', '--tb=short', '-p', 'no:cacheprovider') + $two },
    @{ Id = 'wait-check'; Stage = 'targeted'; Argv = $py + @("$plan/wait-check.py") },
    @{ Id = 'ui-unit'; Stage = 'targeted'; Argv = @('npm', '--prefix', 'ui', 'run', 'test', '--', 'tests/unit/rejection-watch.test.ts', 'tests/unit/dev-script.test.ts', 'tests/unit/e2e-harness.test.ts') },
    @{ Id = 'host-load'; Stage = 'host'; HostLoad = $true },
    @{ Id = 'dev-proof-set'; Stage = 'runtime'; Argv = $py + @("$plan/dev-proof.py", '--run-as-node', 'set', '--expect', 'window', '--expect-notice', 'yes') },
    @{ Id = 'py-tests'; Stage = 'full'; Argv = $py + @('-c', $pyTests) },
    @{ Id = 'ui-tests'; Stage = 'full'; Argv = @('npm', '--prefix', 'ui', 'run', 'test') },
    @{ Id = 'ui-build'; Stage = 'full'; Argv = @('npm', '--prefix', 'ui', 'run', 'build') },
    @{ Id = 'ui-electron'; Stage = 'full'; Argv = @('npm', '--prefix', 'ui', 'run', 'test:e2e'); Clean = $true; NoRejection = $true },
    @{ Id = 'issues-render-check'; Stage = 'full'; Argv = $py + @('tools/issue_triage.py', 'render', '--check') },
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
    $receipt = "$receipts/trr-D6-$($step.Id).txt"
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
    if ($step.Id -eq 'dev-proof-set') {
        Select-String -Path $receipt -Pattern '^(window|notice|left):' | ForEach-Object { Write-Output ("dev-proof-set {0}" -f $_.Line) }
    }
    if ($code -eq 0 -and $step.ContainsKey('Clean')) {
        # A full Electron suite passes only with no failed or flaky test (S5).
        $passed = Select-String -Path $receipt -Pattern '^\s+[0-9]+ passed' -Quiet
        $bad = Select-String -Path $receipt -Pattern '^\s+[0-9]+ (failed|flaky|did not run)' -Quiet
        Write-Output ("{0}: passed line={1} failed or flaky={2}" -f $step.Id, $passed, $bad)
        if (-not $passed -or $bad) { $code = 1 }
    }
    if ($step.ContainsKey('NoRejection')) {
        # S10: any rejection record fails the gate, whatever the exit code.
        $records = @(Select-String -Path $receipt -Pattern 'unhandled rejection:' -SimpleMatch).Count
        Write-Output ("{0}: rejection-record lines={1}" -f $step.Id, $records)
        if ($records -ne 0) { $code = 10 }
    }
    if ($code -eq 0 -and $step.Id -eq 'identity-after') {
        $before = Get-TestedState "$receipts/trr-D6-identity-before.txt"
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
