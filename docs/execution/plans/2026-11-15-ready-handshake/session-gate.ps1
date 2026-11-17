# Session 82 fresh-full gate (task H1-2; implementation-plan.md §Session gate).
# The shape of docs/execution/plans/2026-11-15-closeout-record-once/session-gate.ps1, with this
# plan's steps: identity, then the static checks (py-lint, py-format, py-types, ui-types,
# ui-lint, the task contract, scope-paths, line-endings, red-check's and gap-tally's selftests),
# then the targeted suites (meu-153-tests, meu-154-tests, packaged-receipt), then the fresh full
# suites (py-tests, ui-tests, ui-build, e2e-late-line, openapi, state-render,
# issues-render-check), then the identity again.
# Runs from the repository root (P:/av-kit, main only per AGENTS.md §Commits). One receipt per
# id under C:/Temp/av-kit/ready-handshake, named rh-D6-<id>.txt. The UI steps run in ui/.
# Fail-fast: the first non-zero step stops the gate and every later step is printed as not_run.
# The gate also fails when tested_state differs between its start and its end (an input changed
# while it ran). Read-only apart from the receipts, the temp folder, ui/out (ui-build) and the
# Electron test's scratch app data; all are ignored or outside the checkout. Nothing here
# reaches the network or YouTube, and no step dispatches a model. Exit = the first failing
# step's code.
# py-tests runs the whole suite (no -x) and keeps Session 49b's baseline rule: pytest exit 1
# passes only when every FAILED id also FAILED in row 0's rh-base-py.txt, and nothing ERRORs.
# ui-tests excuses nothing: row 0's rh-base-ui.txt shows no failure.
# Skipped, per the plan: mcp-*, the rest of test:e2e and the packaged build. Each is printed
# with its reason and runs nothing.
$ErrorActionPreference = 'Continue'
$root = (git rev-parse --show-toplevel).Trim()
Set-Location $root
$plan = 'docs/execution/plans/2026-11-15-ready-handshake'
$receipts = 'C:/Temp/av-kit/ready-handshake'
# lint_task_contract.py recognises the instantiated receipt paths only through RECEIPTS_DIR and
# fails closed (exit 3) when it is unset.
$env:RECEIPTS_DIR = 'C:/Temp/av-kit'
$env:PYTHONIOENCODING = 'utf-8'
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:ELECTRON_RUN_AS_NODE = $null
# RC1 ECN-2: keep the temp dirs away from the home folder, as row 0 ran the base suites.
$tmp = 'C:\Temp\av-kit\ready-handshake\tmp'
New-Item -ItemType Directory -Force -Path $tmp | Out-Null
$env:TMP = $tmp
$env:TEMP = $tmp
$base = (Get-Content "$plan/baseline.sha").Trim()

# §Files Modified, this plan folder, the closeout artifacts (the two handoffs, the rolling
# reviews, the reflection, metrics.md and current-focus.md) and the paths baseline-dirty.txt
# already held. A new plan folder another session's planner writes is skipped the way
# identity.py skips it (untracked, docs/execution/plans/2026-11-15-<slug>/, folder absent from
# HEAD). Anything else changed, HEAD moving, or a baseline-dirty path outside this scope moving
# from baseline-dirty-hashes.json is S4. The two MEU-108 pins (ready-probe-guard.test.ts,
# backend-output-after-close.test.ts) are read, never changed: they are tracked and not in
# scope, so any change to them shows as outside scope.
$scopePaths = @"
import hashlib, json, pathlib, subprocess, sys
plan = '$plan'
mine = {
    'packages/api/src/avkit_api/cli.py',
    'tests/unit/test_backend_cli.py',
    'tests/integration/test_backend_spawn.py',
    'ui/src/main/python-manager.ts',
    'ui/src/main/index.ts',
    'ui/tests/unit/ready-line-buffer.test.ts',
    'ui/tests/unit/ready-line-pipe.test.ts',
    'docs/build-plan/04-rest-api.md',
    'docs/build-plan/06-gui.md',
    '.agent/context/known-issues.yaml',
    '.agent/context/known-issues.md',
    '.agent/context/meu-status.yaml',
    '.agent/context/meu-registry.md',
    'docs/BUILD_PLAN.md',
    '.agent/context/grouping/2026-11-15-post-rc3-triage-residuals-session-grouping.md',
    'docs/execution/metrics.md',
    '.agent/context/current-focus.md',
}
prefixes = (plan + '/', '.agent/context/handoffs/2026-11-15-ready-handshake-', 'docs/execution/reflections/2026-11-15-ready-handshake-')
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
    return hashlib.sha256(target.read_bytes()).hexdigest() if target.is_file() else 'deleted'
dirty_hashes = json.loads(pathlib.Path(plan + '/baseline-dirty-hashes.json').read_text(encoding='utf-8'))
dirty_moved = [p for p, h in sorted(dirty_hashes.items()) if sha(p) != h]
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
print('baseline-dirty hash mismatch:', dirty_moved, 'of', len(dirty_hashes))
print('head:', head, 'head moved (S4):', moved)
sys.exit(1 if extra or moved or dirty_moved else 0)
"@

# Each §Files Modified file (and each plan-local script) keeps its row-0 kind from
# baseline-eol.json; the two new Vitest files are LF per §Files Modified. Entries whose expected
# kind is null are read-only pins and are covered by scope-paths. A lone CR fails any file.
$lineEndings = @"
import json, pathlib, sys
plan = '$plan'
eol = json.loads(pathlib.Path(plan + '/baseline-eol.json').read_text(encoding='utf-8'))
expected = {p: v['expected'] for p, v in eol.items() if v.get('expected')}
bad = []
for p, kind in sorted(expected.items()):
    data = pathlib.Path(p).read_bytes()
    crlf = data.count(b'\r\n')
    bare = data.count(b'\n') - crlf
    lone_cr = data.count(b'\r') - crlf
    now = 'CRLF' if crlf and not bare else 'LF' if bare and not crlf else 'MIXED' if crlf and bare else 'EMPTY'
    ok = lone_cr == 0 and now == kind
    print(p, 'expected', kind, 'now', now, 'crlf', crlf, 'bare_lf', bare, 'lone_cr', lone_cr, 'ok' if ok else 'mismatch')
    if not ok:
        bad.append(p)
print('line-endings files:', len(expected), 'mismatch:', bad)
sys.exit(1 if bad else 0)
"@

# Row 4's packaged smoke and measurement tested the cli.py whose SHA-256 rh-pack-cli-sha.txt
# holds; the step fails when cli.py has changed since, so row 4 would have to run again.
$packagedReceipt = @"
import hashlib, pathlib, sys
recorded = pathlib.Path('$receipts/rh-pack-cli-sha.txt').read_text(encoding='utf-8').split()[0]
current = hashlib.sha256(pathlib.Path('packages/api/src/avkit_api/cli.py').read_bytes()).hexdigest()
print('cli.py recorded_sha256', recorded)
print('cli.py current_sha256 ', current)
print('packaged-receipt:', 'match' if recorded == current else 'mismatch')
sys.exit(0 if recorded == current else 1)
"@

# An id is excused only when row 0's baseline receipt really shows it FAILED: a missing
# receipt excuses nothing.
$baseReceipt = "$receipts/rh-base-py.txt"
$baselinePyFailed = @()
if (Test-Path $baseReceipt) {
    $baselinePyFailed = @(Select-String -Path $baseReceipt -Pattern '^FAILED (\S+)' | ForEach-Object { $_.Matches[0].Groups[1].Value } | Sort-Object -Unique)
}
Write-Output ("baseline py failures excused: [{0}] (receipt {1})" -f ($baselinePyFailed -join ', '), $baseReceipt)
Write-Output 'baseline ui failures excused: [] (ui-tests excuses nothing; rh-base-ui.txt shows no failure)'

$skipped = @(
    @{ Id = 'mcp-types/mcp-build/mcp-tests/mcp-audit'; Stage = 'full'; Reason = 'no MCP change; the MCP Python tests run inside py-tests' },
    @{ Id = 'test:e2e-rest'; Stage = 'full'; Reason = 'only the main process output handler changed, and AC-108.7 (e2e-late-line) is the E2E test that drives it' },
    @{ Id = 'packaged-build'; Stage = 'full'; Reason = 'row 4 receipt, bound to cli.py by packaged-receipt' }
)
foreach ($s in $skipped) {
    Write-Output ("{0} stage={1} skipped reason={2}" -f $s.Id, $s.Stage, $s.Reason)
}

$py = @('uv', 'run', '--no-sync', 'python')
$identity = $py + @("$plan/identity.py")
$steps = @(
    @{ Id = 'identity-before'; Stage = 'identity'; Argv = $identity },
    @{ Id = 'py-lint'; Stage = 'static'; Argv = @('uv', 'run', '--no-sync', 'ruff', 'check', 'packages/', 'tests/') },
    @{ Id = 'py-format'; Stage = 'static'; Argv = @('uv', 'run', '--no-sync', 'ruff', 'format', '--check', 'packages/api/src/avkit_api/cli.py', 'tests/unit/test_backend_cli.py', 'tests/integration/test_backend_spawn.py', "$plan/gap-tally.py") },
    @{ Id = 'py-types'; Stage = 'static'; Argv = @('uv', 'run', '--no-sync', 'pyright', 'packages/') },
    @{ Id = 'ui-types'; Stage = 'static'; Cwd = 'ui'; Argv = @('npm', 'run', 'typecheck') },
    @{ Id = 'ui-lint'; Stage = 'static'; Cwd = 'ui'; Argv = @('npm', 'run', 'lint') },
    @{ Id = 'task-contract'; Stage = 'static'; Argv = $py + @('tools/lint_task_contract.py', '--allowed-builder-classes', 'avkit_builder,avkit_coordinator,avkit_verifier', '--task', "$plan/task.md") },
    @{ Id = 'scope-paths'; Stage = 'static'; Argv = $py + @('-c', $scopePaths) },
    @{ Id = 'line-endings'; Stage = 'static'; Argv = $py + @('-c', $lineEndings) },
    @{ Id = 'red-check-selftest'; Stage = 'static'; Argv = $py + @("$plan/red-check.py", '--selftest') },
    @{ Id = 'gap-tally-selftest'; Stage = 'static'; Argv = $py + @("$plan/gap-tally.py", '--selftest') },
    @{ Id = 'meu-153-tests'; Stage = 'targeted'; Argv = @('uv', 'run', '--no-sync', 'pytest', 'tests/unit/test_backend_cli.py', 'tests/integration/test_backend_spawn.py', '--tb=short', '-q', '-rfE'); Expect = '^11 passed' },
    @{ Id = 'meu-154-tests'; Stage = 'targeted'; Cwd = 'ui'; Argv = @('npm', 'run', 'test', '--', 'tests/unit/ready-line-buffer.test.ts', 'tests/unit/ready-line-pipe.test.ts', 'tests/unit/ready-probe-guard.test.ts'); Expect = 'Tests\s+17 passed \(17\)' },
    @{ Id = 'packaged-receipt'; Stage = 'targeted'; Argv = $py + @('-c', $packagedReceipt) },
    @{ Id = 'py-tests'; Stage = 'full'; Argv = @('uv', 'run', '--no-sync', 'pytest', 'tests/', '--tb=short', '-q', '-rfE') },
    @{ Id = 'ui-tests'; Stage = 'full'; Cwd = 'ui'; Argv = @('npm', 'run', 'test') },
    @{ Id = 'ui-build'; Stage = 'full'; Cwd = 'ui'; Argv = @('npm', 'run', 'build') },
    @{ Id = 'e2e-late-line'; Stage = 'full'; Cwd = 'ui'; Argv = @('npm', 'run', 'test:e2e', '--', 'tests/e2e/backend-output-after-close.test.ts'); Expect = '^\s+1 passed' },
    @{ Id = 'openapi'; Stage = 'full'; Argv = $py + @('tools/export_openapi.py', '--check', 'openapi.committed.json') },
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
    $receipt = "$receipts/rh-D6-$($step.Id).txt"
    $argv = $step.Argv
    if ($step.ContainsKey('Cwd')) { Set-Location (Join-Path $root $step.Cwd) }
    & rtk proxy @argv *> $receipt
    $code = $LASTEXITCODE
    Set-Location $root
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
    if ($code -eq 0 -and $step.ContainsKey('Expect')) {
        # A file list that selects fewer tests than planned must not pass quietly.
        $want = $step.Expect
        $hit = Select-String -Path $receipt -Pattern $want -Quiet
        $bad = Select-String -Path $receipt -Pattern '^\s+[0-9]+ (failed|flaky|skipped|did not run)' -Quiet
        Write-Output ("{0}: expect '{1}' found={2} other outcomes={3}" -f $step.Id, $want, $hit, $bad)
        if (-not $hit -or $bad) { $code = 1 }
    }
    if ($code -eq 0 -and $step.Id -eq 'identity-after') {
        $before = Get-TestedState "$receipts/rh-D6-identity-before.txt"
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
