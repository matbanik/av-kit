# Session 98 fresh-full gate (task H1-2; implementation-plan.md "Session gate (H1-2)").
# The shape of docs/execution/plans/2026-11-19-e2e-host-parity/session-gate.ps1 (Session 97), with
# this plan's steps: identity; the static checks (the task contract, scope-paths, line-endings,
# home-path, host-details, split-check, guard-list, pins, probe-block, probe-local, gate-judge,
# known-list, the red-check, eol-check, split-specs, probe-check, pins-check, guard-check and
# snapshot-commit selftests, py-format,
# py-lint, snapshot-verify, test-hashes); the UI static checks (ui-types, ui-lint); the tests
# (ui-tests, py-tests, canon); host-load (Session 81 RULE-2, through host-load.ps1, 50 %); the E2E
# (ui-build, e2e-full through flake-run.py); the registers (issues-render-check, state-render,
# remote-evidence); then the identity again.
# Runs from the repository root (P:/av-kit, main only per AGENTS.md "Commits"). One receipt per id
# under C:/Temp/av-kit/e2e-clipboard-specs, named ecs-D6-<id>.txt; every step's exit code is the
# code of the command that wrote that receipt, and the gate reads only those receipts.
# Fail-fast: the first non-zero step stops the gate and every later step is printed as not_run.
# The gate also fails when tested_state differs between its start and its end (an input changed
# while it ran).
# Writes nothing tracked: only the receipts, the temp folder, ui/out (ui-build, ignored), the
# snapshot selftest folder ecs-snapshot-selftest-gate-<stamp>, the local probe receipt
# ecs-probe-local-gate-<stamp>.json, the guard list ecs-guard-list-gate-<stamp>.json (Playwright
# --list with AVKIT_E2E_CLIPBOARD_GATED removed: it runs no test; D-1282), and the flake-run receipts and diag folders under
# C:/Temp/av-kit/e2e-clipboard-specs, with <stamp> the gate's start time as yyyyMMdd-HHmmss, so a
# rerun never meets an old file. No step reaches the network or the second Windows host
# (remote-evidence reads only row 8's local summary.json), no step reads app data, and no step
# calls a model. flake-run.py stops only the processes its own runs started.
# e2e-full is flake-run.py --mode full --runs 1 --no-burn --label gate --expect-total 237: every
# E2E file except capture-system-clipboard.test.ts (EXCLUDED; the OLD_CLIPBOARD guard refuses
# while either old file still calls the clipboard), with no busy children; an unrecorded failure
# reruns once alone, and a second failure or any receipt line holding `unhandled rejection:`
# fails it. The clipboard file never runs on this PC.
# Exit = the first failing step's code.
# Skipped, per the plan: py-types, mcp-types, mcp-tests, mcp-build, openapi and mcp-audit (H1-4
# checks that every packages/, mcp-server/src, mcp-server/scripts, mcp-server/tests and native/
# file keeps its baseline-skip-hashes.json hash, and none was added or removed). Each is printed
# with its reason and runs nothing.
$ErrorActionPreference = 'Continue'
$root = (git rev-parse --show-toplevel).Trim()
Set-Location $root
$plan = 'docs/execution/plans/2026-11-20-e2e-clipboard-specs'
$receipts = 'C:/Temp/av-kit/e2e-clipboard-specs'
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
Write-Output "gate stamp: $stamp"
# lint_task_contract.py recognises the instantiated receipt paths only through RECEIPTS_DIR and
# fails closed (exit 3) when it is unset, which no user or machine scope sets on this host.
$env:RECEIPTS_DIR = 'C:/Temp/av-kit'
$env:PYTHONIOENCODING = 'utf-8'
$env:PYTHONDONTWRITEBYTECODE = '1'
Remove-Item Env:ELECTRON_RUN_AS_NODE -ErrorAction SilentlyContinue
# RC1 ECN-2: keep the temp dirs away from the home folder.
$tmp = 'C:\Temp\av-kit\e2e-clipboard-specs\tmp'
New-Item -ItemType Directory -Force -Path $tmp | Out-Null
$env:TMP = $tmp
$env:TEMP = $tmp
$base = (Get-Content "$plan/baseline.sha").Trim()
$cfg = Join-Path $HOME '.config/av-kit/e2e-host.json'

# Files Modified, this plan folder, the closeout artifacts (the handoffs and reviews under
# .agent/context/handoffs/2026-11-20-e2e-clipboard-specs-*, the reflection, metrics.md and
# current-focus.md) and the paths baseline-dirty.txt already held. Foreign class (Session 92
# RULE-3): .agent/model-registry.local.json, .claude/agents/*.md and .cursor/agents/*.md belong
# to the coordinator; a change there is printed, never S4. Untracked plan folders of other
# sessions (2026-11-15 to 2026-11-20, absent from HEAD) are skipped. Anything else changed,
# HEAD moving, a "Read, never changed" file moving from baseline-scope.json, or a
# baseline-dirty-hashes.json path moving is S4.
$scopePaths = @"
import hashlib, json, pathlib, re, subprocess, sys
plan = '$plan'
mine = {
    'ui/tests/e2e/capture-system-clipboard.test.ts',
    'ui/tests/e2e/capture-filmstrip-actions.test.ts',
    'ui/tests/e2e/capture-import.test.ts',
    'tools/e2e_remote.py',
    'tools/e2e_host/host-facts.ps1',
    'tools/e2e_host/host-status.ps1',
    'tools/e2e_host/run-e2e.ps1',
    'tools/e2e_host/known-failures.json',
    'tests/tooling/test_e2e_remote.py',
    '.agent/docs/e2e-remote-host.md',
    '.agent/docs/commands.md',
    '.agent/context/known-issues.yaml',
    '.agent/context/known-issues.md',
    '.agent/context/grouping/2026-11-20-e2e-clipboard-specs-session-grouping.md',
    '.agent/context/current-focus.md',
    'docs/execution/metrics.md',
}
def foreign_class(p):
    return p == '.agent/model-registry.local.json' or (
        p.startswith(('.claude/agents/', '.cursor/agents/')) and p.endswith('.md') and p.count('/') == 2
    )
prefixes = (plan + '/', '.agent/context/handoffs/2026-11-20-e2e-clipboard-specs-', 'docs/execution/reflections/2026-11-20-e2e-clipboard-specs-')
scope = json.loads(pathlib.Path(plan + '/baseline-scope.json').read_text(encoding='utf-8'))
read_only = tuple(p for p in scope if p not in mine and not foreign_class(p) and not p.startswith(prefixes))
foreign_bound = tuple(p for p in scope if foreign_class(p))
other_plan_re = re.compile(r'^docs/execution/plans/2026-11-(1[5-9]|20)-[^/]+/')
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

# known-list (D-1272, D-1274): the tracked list against its row-0 copy, by the split flag row 7
# wrote. probe: skip [] and gated holds exactly the clipboard file for mini-air. fallback: skip
# holds exactly the clipboard file for mini-air and there is no gated list. known stays [].
$knownList = @"
import json, pathlib, sys
kp = 'tools/e2e_host/known-failures.json'
flag = pathlib.Path('$receipts/ecs-split-flag.txt').read_text(encoding='utf-8').strip()
now = json.loads(pathlib.Path(kp).read_text(encoding='utf-8'))
raw = pathlib.Path(kp).read_bytes()
entry = {'label': 'mini-air', 'file': 'capture-system-clipboard.test.ts'}
def files(key):
    return [{k: e.get(k) for k in ('label', 'file')} for e in now.get(key, [])]
if flag == 'probe':
    ok = now.get('known') == [] and now.get('skip') == [] and files('gated') == [entry]
elif flag == 'fallback':
    ok = now.get('known') == [] and files('skip') == [entry] and 'gated' not in now
else:
    ok = False
reasons = all(str(e.get('reason', '')).strip() for e in [*now.get('skip', []), *now.get('gated', [])])
print('split flag:', flag, 'keys:', sorted(now), 'skip:', files('skip'), 'gated:', files('gated'), 'reasons:', reasons, 'LF:', b'\r' not in raw)
sys.exit(0 if ok and reasons and b'\r' not in raw else 1)
"@

# test-hashes (S3): every hash recorded at Red (row 3) still holds. Under the fallback (D-1274)
# row 7 drops the test_s98_ tests and records the new hash in ecs-test-sha-7.json, which is read
# instead. Under the probe form, D-1284's Red records ecs-test-sha-r1fix.json, which is read in
# place of ecs-test-sha-3.json when it exists.
$testHashes = @"
import hashlib, json, pathlib, sys
bad = []
count = 0
flag = pathlib.Path('$receipts/ecs-split-flag.txt').read_text(encoding='utf-8').strip()
for name in (('ecs-test-sha-7.json',) if flag == 'fallback' else (('ecs-test-sha-r1fix.json',) if (pathlib.Path('$receipts') / 'ecs-test-sha-r1fix.json').exists() else ('ecs-test-sha-3.json',))):
    for path, want in json.loads((pathlib.Path('$receipts') / name).read_text(encoding='utf-8')).items():
        count += 1
        have = hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()
        print(name, path, 'equal:', have == want)
        if have != want:
            bad.append(path)
print('test-hashes:', count, 'recorded, changed since their Red:', bad)
sys.exit(1 if bad or count == 0 else 0)
"@

# Row 8's run: ecs-run-8b-dir.txt and ecs-snapshot-8b.json when row 8 reran in the fallback form
# after probe-check.py --judge-gate exited 3 (D-1280), otherwise the 8 files.
$r8 = if (Test-Path -LiteralPath "$receipts/ecs-run-8b-dir.txt") { '8b' } else { '8' }
$run8 = (Get-Content "$receipts/ecs-run-$r8-dir.txt" -ErrorAction SilentlyContinue | Select-Object -First 1)
Write-Output "row 8 run: $r8"

# remote-evidence: row 8's summary.json (its commit equal to the snapshot; the main stage 237
# tests, all expected, no new failure; the gated object present with an outcome from
# GATED_OUTCOMES when the split flag is probe, absent when it is fallback) and the tool and every
# host file hash equal to its tool_sha256 (S13 otherwise). The gated outcome itself is a receipt,
# not a pass condition (D-1279). Reads only the local run folder named in ecs-run-8-dir.txt.
$remoteEvidence = @"
import hashlib, json, pathlib, sys
D = pathlib.Path('$receipts')
flag = (D / 'ecs-split-flag.txt').read_text(encoding='utf-8').strip()
d = pathlib.Path((D / 'ecs-run-$r8-dir.txt').read_text(encoding='utf-8').strip())
s = json.loads((d / 'summary.json').read_text(encoding='utf-8'))
snap = json.loads((D / 'ecs-snapshot-$r8.json').read_text(encoding='utf-8')).get('commit')
recorded = s.get('tool_sha256') or {}
def sha(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
now = {'tools/e2e_remote.py': sha('tools/e2e_remote.py')}
for p in sorted(pathlib.Path('tools/e2e_host').iterdir()):
    if p.is_file() and p.suffix in ('.ps1', '.json'):
        now['tools/e2e_host/' + p.name] = sha(p)
diff = sorted(k for k in set(now).union(recorded) if now.get(k) != recorded.get(k))
main_ok = s.get('tests') == 237 and s.get('expected') == 237 and not s.get('new') and bool(snap) and s.get('commit') == snap
gated = s.get('gated')
outcomes = ('run', 'skipped-connected', 'skipped-undecided', 'voided-connected-during', 'voided-undecided-during')
if flag == 'probe':
    gated_ok = isinstance(gated, dict) and gated.get('outcome') in outcomes and gated.get('files') == ['capture-system-clipboard.test.ts']
else:
    gated_ok = gated is None and [e.get('file') for e in s.get('skip', [])] == ['capture-system-clipboard.test.ts']
print('run folder name:', d.name, 'summary exit:', s.get('exit'), 'tests', s.get('tests'), 'expected', s.get('expected'), 'new', len(s.get('new') or []), 'commit equals the snapshot:', s.get('commit') == snap)
print('split flag:', flag, 'gated:', json.dumps(gated, sort_keys=True) if isinstance(gated, dict) else gated)
print('files hashed now:', len(now), 'recorded:', len(recorded), 'remote-evidence mismatch:', diff)
if diff:
    print('S13: the tool, a host file or the known list changed after row 8')
sys.exit(0 if main_ok and gated_ok and not diff else 1)
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
$grown = @(
    '--grown', '.agent/context/known-issues.yaml', "$receipts/baseline-copies/.agent/context/known-issues.yaml",
    '--grown', '.agent/context/known-issues.md', "$receipts/baseline-copies/.agent/context/known-issues.md",
    '--grown', '.agent/context/grouping/2026-11-20-e2e-clipboard-specs-session-grouping.md', "$receipts/baseline-copies/.agent/context/grouping/2026-11-20-e2e-clipboard-specs-session-grouping.md"
)
$steps = @(
    @{ Id = 'identity-before'; Stage = 'identity'; Argv = $identity },
    @{ Id = 'task-contract'; Stage = 'static'; Argv = $py + @('tools/lint_task_contract.py', '--allowed-builder-classes', 'avkit_builder,avkit_coordinator,avkit_verifier', '--task', "$plan/task.md") },
    @{ Id = 'scope-paths'; Stage = 'static'; Argv = $py + @('-c', $scopePaths) },
    @{ Id = 'line-endings'; Stage = 'static'; Argv = $py + @("$plan/eol-check.py") },
    @{ Id = 'home-path'; Stage = 'static'; Argv = $py + @('tools/check_home_path.py') },
    @{ Id = 'host-details'; Stage = 'static'; Argv = $py + @("$plan/host-details-scan.py", $cfg) + $grown },
    @{ Id = 'split-check'; Stage = 'static'; Argv = $py + @("$plan/split-specs.py", '--check') },
    @{ Id = 'guard-list'; Stage = 'static'; Argv = $py + @("$plan/guard-check.py", '--list', "$receipts/ecs-guard-list-gate-$stamp.json") },
    @{ Id = 'pins'; Stage = 'static'; Argv = $py + @("$plan/pins-check.py") },
    @{ Id = 'probe-block'; Stage = 'static'; Argv = $py + @("$plan/probe-check.py", '--block') },
    @{ Id = 'probe-local'; Stage = 'static'; Argv = $py + @("$plan/probe-check.py", '--local', "$receipts/ecs-probe-local-gate-$stamp.json") },
    @{ Id = 'gate-judge'; Stage = 'static'; Argv = $py + @("$plan/probe-check.py", '--judge-gate', "$run8/summary.json") },
    @{ Id = 'known-list'; Stage = 'static'; Argv = $py + @('-c', $knownList) },
    @{ Id = 'red-check-selftest'; Stage = 'static'; Argv = $py + @("$plan/red-check.py", '--selftest') },
    @{ Id = 'eol-check-selftest'; Stage = 'static'; Argv = $py + @("$plan/eol-check.py", '--selftest') },
    @{ Id = 'split-specs-selftest'; Stage = 'static'; Argv = $py + @("$plan/split-specs.py", '--selftest') },
    @{ Id = 'probe-check-selftest'; Stage = 'static'; Argv = $py + @("$plan/probe-check.py", '--selftest') },
    @{ Id = 'pins-check-selftest'; Stage = 'static'; Argv = $py + @("$plan/pins-check.py", '--selftest') },
    @{ Id = 'guard-check-selftest'; Stage = 'static'; Argv = $py + @("$plan/guard-check.py", '--selftest') },
    @{ Id = 'snapshot-selftest'; Stage = 'static'; Argv = $py + @("$plan/snapshot-commit.py", '--selftest', "$receipts/ecs-snapshot-selftest-gate-$stamp") },
    @{ Id = 'py-format'; Stage = 'static'; Argv = @('uv', 'run', '--no-sync', 'ruff', 'format', '--check', 'tools/e2e_remote.py', 'tests/tooling/test_e2e_remote.py') + $planPy },
    @{ Id = 'py-lint'; Stage = 'static'; Argv = @('uv', 'run', '--no-sync', 'ruff', 'check', 'packages/', 'tools/e2e_remote.py', 'tests/') + $planPy },
    @{ Id = 'snapshot-verify'; Stage = 'static'; Argv = $py + @("$plan/snapshot-commit.py", '--verify', "$receipts/ecs-snapshot-$r8.json") },
    @{ Id = 'test-hashes'; Stage = 'static'; Argv = $py + @('-c', $testHashes) },
    @{ Id = 'ui-types'; Stage = 'ui-static'; Cwd = 'ui'; Argv = @('npm', 'run', 'typecheck') },
    @{ Id = 'ui-lint'; Stage = 'ui-static'; Cwd = 'ui'; Argv = @('npm', 'run', 'lint') },
    @{ Id = 'ui-tests'; Stage = 'tests'; Cwd = 'ui'; Argv = @('npm', 'run', 'test') },
    @{ Id = 'py-tests'; Stage = 'tests'; Argv = @('uv', 'run', '--no-sync', 'pytest', 'tests/', '-x', '-q', '-p', 'no:cacheprovider') },
    @{ Id = 'canon'; Stage = 'tests'; Cwd = 'ui'; Argv = @('npm', 'run', 'test', '--', 'tests/unit/layout-canon.test.ts', 'tests/unit/queue-canon.test.ts') },
    @{ Id = 'host-load'; Stage = 'host'; Argv = @('pwsh', '-NoProfile', '-File', "$plan/host-load.ps1") },
    @{ Id = 'ui-build'; Stage = 'e2e'; Cwd = 'ui'; Argv = @('npm', 'run', 'build') },
    @{ Id = 'e2e-full'; Stage = 'e2e'; Argv = $py + @("$plan/flake-run.py", '--mode', 'full', '--runs', '1', '--no-burn', '--label', "gate-$stamp", '--expect-total', '237'); NoRejection = $true },
    @{ Id = 'issues-render-check'; Stage = 'registers'; Argv = $py + @('tools/issue_triage.py', 'render', '--check') },
    @{ Id = 'state-render'; Stage = 'registers'; Argv = $py + @('tools/meu_status.py', 'render', '--check') },
    @{ Id = 'remote-evidence'; Stage = 'registers'; Argv = $py + @('-c', $remoteEvidence) },
    @{ Id = 'identity-after'; Stage = 'identity'; Argv = $identity }
)

# D-1274, D-1280: under the fallback the host files keep their row-0 bytes, so there is no probe
# block to check and no gated object to judge; the three probe steps are printed as skipped and
# run nothing. A missing flag fails known-list. guard-list runs under both flags (D-1282).
$flag = (Get-Content "$receipts/ecs-split-flag.txt" -ErrorAction SilentlyContinue | Select-Object -First 1)
Write-Output "split flag: $flag"
if ($flag -eq 'fallback') {
    $steps = @($steps | Where-Object { $_.Id -notin @('probe-block', 'probe-local', 'gate-judge') })
    Write-Output 'probe-block, probe-local, gate-judge stage=static skipped reason=split flag fallback (D-1274, D-1280)'
}

function Get-TestedState([string]$Receipt) {
    $line = Select-String -Path $Receipt -Pattern '^tested_state ' | Select-Object -Last 1
    if ($null -eq $line) { return $null }
    return $line.Line.Substring('tested_state '.Length).Trim()
}

for ($i = 0; $i -lt $steps.Count; $i++) {
    $step = $steps[$i]
    $receipt = "$receipts/ecs-D6-$($step.Id).txt"
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
        $before = Get-TestedState "$receipts/ecs-D6-identity-before.txt"
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
