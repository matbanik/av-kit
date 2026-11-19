# Session 97 fresh-full gate (task H1-2; implementation-plan.md "Session gate (H1-2)").
# The shape of docs/execution/plans/2026-11-18-e2e-remote-host/session-gate.ps1 (Session 96), with
# this plan's steps: identity; the static checks (the task contract, scope-paths, line-endings,
# home-path, host-details, pins, the red-check, eol-check, diff-check and snapshot-commit
# selftests, py-format, py-lint, segoe-check, fixture-check, known-empty, snapshot-verify,
# test-hashes); the UI static checks (ui-types, ui-lint); the tests (ui-tests, py-tests, canon);
# host-load (Session 81 RULE-2, through host-load.ps1, 50 %); the E2E (ui-build, e2e-touched,
# e2e-full through flake-run.py); the registers (issues-render-check, state-render,
# remote-evidence); then the identity again.
# Runs from the repository root (P:/av-kit, main only per AGENTS.md "Commits"). One receipt per id
# under C:/Temp/av-kit/e2e-host-parity, named ehp-D6-<id>.txt; every step's exit code is the code
# of the command that wrote that receipt, and the gate reads only those receipts.
# Fail-fast: the first non-zero step stops the gate and every later step is printed as not_run.
# The gate also fails when tested_state differs between its start and its end (an input changed
# while it ran).
# Writes nothing tracked: only the receipts, the temp folder, ui/out (ui-build, ignored), the
# snapshot selftest folder ehp-snapshot-selftest-gate-<stamp>, the touched report
# ehp-touched-gate-<stamp>.json, and the flake-run receipts and diag folders under
# C:/Temp/av-kit/e2e-host-parity, with <stamp> the gate's start time as yyyyMMdd-HHmmss, so a
# rerun never meets an old folder. No step reaches the network or the second Windows host
# (remote-evidence reads only row 10's local summary.json), no step reads app data, and no step
# calls a model. flake-run.py and e2e-subset.ps1 stop only the processes their own runs started.
# e2e-full is flake-run.py --mode full --runs 1 --no-burn --label gate --expect-total 232: every
# E2E file except the two clipboard specs, with no busy children; an unrecorded failure reruns
# once alone, and a second failure or any receipt line holding `unhandled rejection:` fails it.
# Exit = the first failing step's code.
# Skipped, per the plan: py-types, mcp-types, mcp-tests, mcp-build, openapi and mcp-audit (H1-4
# checks that every packages/, mcp-server/src, mcp-server/scripts, mcp-server/tests and native/
# file keeps its baseline-skip-hashes.json hash, and none was added or removed). Each is printed
# with its reason and runs nothing.
$ErrorActionPreference = 'Continue'
$root = (git rev-parse --show-toplevel).Trim()
Set-Location $root
$plan = 'docs/execution/plans/2026-11-19-e2e-host-parity'
$receipts = 'C:/Temp/av-kit/e2e-host-parity'
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
Write-Output "gate stamp: $stamp"
# lint_task_contract.py recognises the instantiated receipt paths only through RECEIPTS_DIR and
# fails closed (exit 3) when it is unset, which no user or machine scope sets on this host.
$env:RECEIPTS_DIR = 'C:/Temp/av-kit'
$env:PYTHONIOENCODING = 'utf-8'
$env:PYTHONDONTWRITEBYTECODE = '1'
Remove-Item Env:ELECTRON_RUN_AS_NODE -ErrorAction SilentlyContinue
# RC1 ECN-2: keep the temp dirs away from the home folder.
$tmp = 'C:\Temp\av-kit\e2e-host-parity\tmp'
New-Item -ItemType Directory -Force -Path $tmp | Out-Null
$env:TMP = $tmp
$env:TEMP = $tmp
$base = (Get-Content "$plan/baseline.sha").Trim()
$cfg = Join-Path $HOME '.config/av-kit/e2e-host.json'

# Files Modified, this plan folder, the closeout artifacts (the handoffs and reviews under
# .agent/context/handoffs/2026-11-19-e2e-host-parity-*, the reflection, metrics.md and
# current-focus.md) and the paths baseline-dirty.txt already held. Foreign class (Session 92
# RULE-3): .agent/model-registry.local.json, .claude/agents/*.md and .cursor/agents/*.md belong
# to the coordinator; a change there is printed, never S4. Untracked plan folders of other
# sessions (2026-11-15 to 2026-11-19, absent from HEAD) are skipped. Anything else changed,
# HEAD moving, a "Read, never changed" file moving from baseline-scope.json, or a
# baseline-dirty-hashes.json path moving is S4.
$scopePaths = @"
import hashlib, json, pathlib, re, subprocess, sys
plan = '$plan'
mine = {
    'ui/tests/unit/e2e-harness.test.ts',
    'ui/tests/e2e/electron-app.ts',
    'ui/tests/e2e/settings.test.ts',
    'ui/tests/e2e/capture-inbox.test.ts',
    'ui/tests/e2e/fixtures/capture-text-plates.json',
    'ui/tests/unit/capture-text-plates.test.ts',
    'tests/unit/test_capture_text_plates.py',
    'ui/tests/unit/capture-text-metrics.test.ts',
    'ui/tests/unit/capture-transform.test.ts',
    'ui/tests/unit/capture-text-lines.behavior.test.ts',
    'ui/tests/unit/capture-page.behavior.test.ts',
    'ui/src/renderer/src/features/capture/capture-segoe-metrics.ts',
    'ui/src/renderer/src/features/capture/capture-text-metrics.ts',
    'tools/e2e_host/known-failures.json',
    'tests/tooling/test_e2e_remote.py',
    '.agent/context/meu-status.yaml',
    'docs/build-plan/09-screenshot-capture.md',
    'docs/build-plan/build-priority-matrix.md',
    '.agent/context/meu-registry.md',
    'docs/BUILD_PLAN.md',
    '.agent/context/known-issues.yaml',
    '.agent/context/known-issues.md',
    '.agent/context/grouping/2026-11-18-e2e-remote-host-session-grouping.md',
    '.agent/context/current-focus.md',
    'docs/execution/metrics.md',
}
def foreign_class(p):
    return p == '.agent/model-registry.local.json' or (
        p.startswith(('.claude/agents/', '.cursor/agents/')) and p.endswith('.md') and p.count('/') == 2
    )
prefixes = (plan + '/', '.agent/context/handoffs/2026-11-19-e2e-host-parity-', 'docs/execution/reflections/2026-11-19-e2e-host-parity-')
scope = json.loads(pathlib.Path(plan + '/baseline-scope.json').read_text(encoding='utf-8'))
read_only = tuple(p for p in scope if p not in mine and not foreign_class(p) and not p.startswith(prefixes))
foreign_bound = tuple(p for p in scope if foreign_class(p))
other_plan_re = re.compile(r'^docs/execution/plans/2026-11-1[5-9]-[^/]+/')
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
foreign_moved = [p for p in foreign_bound if sha(p) != scope[p]]
dirty_hashes = json.loads(pathlib.Path(plan + '/baseline-dirty-hashes.json').read_text(encoding='utf-8'))
def drift(p, h):
    return (sha(p) if pathlib.Path(p).exists() else 'deleted') != h
dirty_moved = [p for p, h in sorted(dirty_hashes.items()) if p not in mine and not p.startswith(prefixes) and drift(p, h)]
# --no-renames: a rename reports both its source deletion and its destination, so moving an
# out-of-scope file into an allowed path still shows the out-of-scope deletion.
# -z: NUL-separated, so a path with spaces or quoting is one entry.
def paths(*args):
    return [p for p in git(*args).split('\0') if p]
head = git('rev-parse', 'HEAD').strip()
moved = head != '$base'
tracked = paths('diff', '--no-renames', '--name-only', '-z', head)
untracked = [p for p in paths('ls-files', '--others', '--exclude-standard', '-z') if '__pycache__/' not in p]
changed = set(tracked + untracked)
others = sorted({p for p in untracked if other_plan(p)})
foreign = sorted({p for p in changed if foreign_class(p)})
extra = sorted({p for p in changed if p not in allowed and not p.startswith(prefixes) and p not in others and p not in foreign})
print('changed paths:', len(changed), 'outside scope:', extra, 'other sessions plan files skipped:', len(others))
print('read-never-changed files:', len(read_only), 'mismatch:', read_only_moved, 'baseline-dirty hash mismatch:', dirty_moved)
print('foreign class (coordinator, printed only):', len(foreign_bound), 'changed:', foreign, 'row-0 hash moved:', foreign_moved)
print('head:', head, 'head moved (S4):', moved)
sys.exit(1 if extra or moved or read_only_moved or dirty_moved else 0)
"@

# known-empty (KNOWN_EMPTY, D-1253): the tracked list loads to its row-0 copy with known empty.
$knownEmpty = @"
import json, pathlib, sys
kp = 'tools/e2e_host/known-failures.json'
now = json.loads(pathlib.Path(kp).read_text(encoding='utf-8'))
old = json.loads((pathlib.Path('$receipts/baseline-copies') / kp).read_text(encoding='utf-8'))
want = dict(old)
want['known'] = []
raw = pathlib.Path(kp).read_bytes()
ok = now == want and len(old.get('known', [])) == 4 and b'\r' not in raw
print('known now:', now.get('known'), 'row-0 known entries:', len(old.get('known', [])), 'skip entries:', len(now.get('skip', [])), 'equal to the row-0 copy with known empty:', now == want, 'LF:', b'\r' not in raw)
sys.exit(0 if ok else 1)
"@

# test-hashes (S3): every hash recorded at Red (rows 3, 5 and 6) still holds.
$testHashes = @"
import hashlib, json, pathlib, sys
bad = []
count = 0
for name in ('ehp-test-sha-3b.json', 'ehp-test-sha-5.json', 'ehp-test-sha-6.json'):
    for path, want in json.loads((pathlib.Path('$receipts') / name).read_text(encoding='utf-8')).items():
        count += 1
        have = hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()
        print(name, path, 'equal:', have == want)
        if have != want:
            bad.append(path)
print('test-hashes:', count, 'recorded, changed since their Red:', bad)
sys.exit(1 if bad or count == 0 else 0)
"@

# remote-evidence: row 10's summary.json (exit 0, 232 tests and 232 expected, its commit equal to
# the snapshot) and the tool and every host file hash equal to its tool_sha256 (S13 otherwise).
# Reads only the local run folder named in ehp-run-10b-dir.txt (D-1257: the second run).
$remoteEvidence = @"
import hashlib, json, pathlib, sys
D = pathlib.Path('$receipts')
d = pathlib.Path((D / 'ehp-run-10b-dir.txt').read_text(encoding='utf-8').strip())
s = json.loads((d / 'summary.json').read_text(encoding='utf-8'))
snap = json.loads((D / 'ehp-snapshot-10b.json').read_text(encoding='utf-8')).get('commit')
recorded = s.get('tool_sha256') or {}
def sha(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
now = {'tools/e2e_remote.py': sha('tools/e2e_remote.py')}
for p in sorted(pathlib.Path('tools/e2e_host').iterdir()):
    if p.is_file() and p.suffix in ('.ps1', '.json'):
        now['tools/e2e_host/' + p.name] = sha(p)
diff = sorted(k for k in set(now).union(recorded) if now.get(k) != recorded.get(k))
counts = s.get('exit') == 0 and s.get('tests') == 232 and s.get('expected') == 232 and bool(snap) and s.get('commit') == snap
print('run folder name:', d.name, 'summary exit:', s.get('exit'), 'tests', s.get('tests'), 'expected', s.get('expected'), 'commit equals the snapshot:', s.get('commit') == snap)
print('files hashed now:', len(now), 'recorded:', len(recorded), 'remote-evidence mismatch:', diff)
if diff:
    print('S13: the tool, a host file or the known list changed after row 10')
sys.exit(0 if counts and not diff else 1)
"@

$skipped = @(
    @{ Id = 'py-types'; Stage = 'static'; Reason = 'every packages/ file keeps its baseline-skip-hashes.json hash (H1-4); no product Python changes' },
    @{ Id = 'mcp-types/mcp-tests/mcp-build'; Stage = 'full'; Reason = 'every mcp-server/src, mcp-server/scripts and mcp-server/tests file keeps its baseline-skip-hashes.json hash (H1-4); no server file changes' },
    @{ Id = 'openapi'; Stage = 'full'; Reason = 'every packages/api/ file keeps its baseline-skip-hashes.json hash (H1-4); no route or schema changes' },
    @{ Id = 'mcp-audit'; Stage = 'runtime'; Reason = 'no server file changes (H1-4); the audit is a network run and this gate uses no network' }
)
foreach ($s in $skipped) {
    Write-Output ("{0} stage={1} skipped reason={2}" -f $s.Id, $s.Stage, $s.Reason)
}

$py = @('uv', 'run', '--no-sync', 'python')
$identity = $py + @("$plan/identity.py")
$planPy = @(Get-ChildItem -Path $plan -Filter '*.py' | Sort-Object Name | ForEach-Object { "$plan/$($_.Name)" })
$pins = @(
    'ui/tests/unit/e2e-harness.test.ts', 'ui/tests/e2e/electron-app.ts', 'ui/tests/e2e/settings.test.ts',
    'ui/tests/e2e/capture-inbox.test.ts', 'ui/tests/unit/capture-text-metrics.test.ts',
    'ui/tests/unit/capture-transform.test.ts', 'ui/tests/unit/capture-text-lines.behavior.test.ts',
    'ui/tests/unit/capture-page.behavior.test.ts'
)
$grown = @(
    '--grown', '.agent/context/known-issues.yaml', "$receipts/baseline-copies/.agent/context/known-issues.yaml",
    '--grown', '.agent/context/known-issues.md', "$receipts/baseline-copies/.agent/context/known-issues.md",
    '--grown', '.agent/context/grouping/2026-11-18-e2e-remote-host-session-grouping.md', "$receipts/baseline-copies/.agent/context/grouping/2026-11-18-e2e-remote-host-session-grouping.md"
)
$steps = @(
    @{ Id = 'identity-before'; Stage = 'identity'; Argv = $identity },
    @{ Id = 'task-contract'; Stage = 'static'; Argv = $py + @('tools/lint_task_contract.py', '--allowed-builder-classes', 'avkit_builder,avkit_coordinator,avkit_verifier', '--task', "$plan/task.md") },
    @{ Id = 'scope-paths'; Stage = 'static'; Argv = $py + @('-c', $scopePaths) },
    @{ Id = 'line-endings'; Stage = 'static'; Argv = $py + @("$plan/eol-check.py") },
    @{ Id = 'home-path'; Stage = 'static'; Argv = $py + @('tools/check_home_path.py') },
    @{ Id = 'host-details'; Stage = 'static'; Argv = $py + @("$plan/host-details-scan.py", $cfg) + $grown },
    @{ Id = 'pins'; Stage = 'static'; Argv = $py + @("$plan/diff-check.py", '--expect-changed') + $pins },
    @{ Id = 'red-check-selftest'; Stage = 'static'; Argv = $py + @("$plan/red-check.py", '--selftest') },
    @{ Id = 'eol-check-selftest'; Stage = 'static'; Argv = $py + @("$plan/eol-check.py", '--selftest') },
    @{ Id = 'diff-check-selftest'; Stage = 'static'; Argv = $py + @("$plan/diff-check.py", '--selftest') },
    @{ Id = 'snapshot-selftest'; Stage = 'static'; Argv = $py + @("$plan/snapshot-commit.py", '--selftest', "$receipts/ehp-snapshot-selftest-gate-$stamp") },
    @{ Id = 'py-format'; Stage = 'static'; Argv = @('uv', 'run', '--no-sync', 'ruff', 'format', '--check', 'tests/unit/test_capture_text_plates.py') + $planPy },
    @{ Id = 'py-lint'; Stage = 'static'; Argv = @('uv', 'run', '--no-sync', 'ruff', 'check', 'packages/', 'tests/') + $planPy },
    @{ Id = 'segoe-check'; Stage = 'static'; Argv = $py + @("$plan/segoe-units.py", '--check') },
    @{ Id = 'fixture-check'; Stage = 'static'; Argv = $py + @("$plan/plate-fixture.py", '--check') },
    @{ Id = 'known-empty'; Stage = 'static'; Argv = $py + @('-c', $knownEmpty) },
    @{ Id = 'snapshot-verify'; Stage = 'static'; Argv = $py + @("$plan/snapshot-commit.py", '--verify', "$receipts/ehp-snapshot-10b.json") },
    @{ Id = 'test-hashes'; Stage = 'static'; Argv = $py + @('-c', $testHashes) },
    @{ Id = 'ui-types'; Stage = 'ui-static'; Cwd = 'ui'; Argv = @('npm', 'run', 'typecheck') },
    @{ Id = 'ui-lint'; Stage = 'ui-static'; Cwd = 'ui'; Argv = @('npm', 'run', 'lint') },
    @{ Id = 'ui-tests'; Stage = 'tests'; Cwd = 'ui'; Argv = @('npm', 'run', 'test') },
    @{ Id = 'py-tests'; Stage = 'tests'; Argv = @('uv', 'run', '--no-sync', 'pytest', 'tests/', '-x', '-q', '-p', 'no:cacheprovider') },
    @{ Id = 'canon'; Stage = 'tests'; Cwd = 'ui'; Argv = @('npm', 'run', 'test', '--', 'tests/unit/layout-canon.test.ts', 'tests/unit/queue-canon.test.ts') },
    @{ Id = 'host-load'; Stage = 'host'; Argv = @('pwsh', '-NoProfile', '-File', "$plan/host-load.ps1") },
    @{ Id = 'ui-build'; Stage = 'e2e'; Cwd = 'ui'; Argv = @('npm', 'run', 'build') },
    @{ Id = 'e2e-touched'; Stage = 'e2e'; Argv = @('pwsh', '-NoProfile', '-File', "$plan/e2e-subset.ps1", '-Set', 'touched', '-Out', "$receipts/ehp-touched-gate-$stamp.json"); NoRejection = $true },
    @{ Id = 'e2e-full'; Stage = 'e2e'; Argv = $py + @("$plan/flake-run.py", '--mode', 'full', '--runs', '1', '--no-burn', '--label', 'gate', '--expect-total', '232'); NoRejection = $true },
    @{ Id = 'issues-render-check'; Stage = 'registers'; Argv = $py + @('tools/issue_triage.py', 'render', '--check') },
    @{ Id = 'state-render'; Stage = 'registers'; Argv = $py + @('tools/meu_status.py', 'render', '--check') },
    @{ Id = 'remote-evidence'; Stage = 'registers'; Argv = $py + @('-c', $remoteEvidence) },
    @{ Id = 'identity-after'; Stage = 'identity'; Argv = $identity }
)

function Get-TestedState([string]$Receipt) {
    $line = Select-String -Path $Receipt -Pattern '^tested_state ' | Select-Object -Last 1
    if ($null -eq $line) { return $null }
    return $line.Line.Substring('tested_state '.Length).Trim()
}

for ($i = 0; $i -lt $steps.Count; $i++) {
    $step = $steps[$i]
    $receipt = "$receipts/ehp-D6-$($step.Id).txt"
    $argv = $step.Argv
    if ($step.ContainsKey('Cwd')) { Set-Location (Join-Path $root $step.Cwd) }
    & rtk proxy @argv *> $receipt
    $code = $LASTEXITCODE
    Set-Location $root
    Write-Output ("{0} stage={1} exit={2} receipt={3}" -f $step.Id, $step.Stage, $code, $receipt)
    Get-Content $receipt | Select-Object -Last 6
    if ($step.ContainsKey('NoRejection')) {
        # S10: any rejection record fails the gate, whatever the exit code.
        $records = @(Select-String -Path $receipt -Pattern 'unhandled rejection:' -SimpleMatch).Count
        Write-Output ("{0}: rejection-record lines={1}" -f $step.Id, $records)
        if ($records -ne 0) { $code = 10 }
    }
    if ($code -eq 0 -and $step.Id -eq 'identity-after') {
        $before = Get-TestedState "$receipts/ehp-D6-identity-before.txt"
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
