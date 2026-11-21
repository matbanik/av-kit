# Session 100 fresh-full gate (task H1-2; implementation-plan.md "Session gate (H1-2)").
# The shape of docs/execution/plans/2026-11-20-e2e-clipboard-specs/session-gate.ps1 (Session 98),
# with this plan's steps: identity; the static checks (the task contract, scope-paths,
# line-endings, home-path, host-details, split-check, guard-list, writer-scan, pins, known-list,
# the red-check, eol-check, split-specs, writer-scan, gated-count, pins-check, guard-check,
# flake-run, guard-logs and snapshot-commit selftests, py-format, py-lint in the D-1287 scope,
# snapshot-verify, test-hashes); the UI static checks (ui-types, ui-lint); the tests (ui-tests,
# the full Vitest suite with AC-43.13 and AC-44.13 and the new unit file; py-tests; canon);
# host-load (Session 81 RULE-2, through host-load.ps1, 50 %); the E2E (ui-build, e2e-full through
# flake-run.py with the guard on, then guard-logs over every run folder e2e-full's receipt
# names); the registers (issues-render-check, state-render, gated-count, guard-logs-remote over
# row 8's host/diag folder, remote-evidence); then the identity again.
# Runs from the repository root (P:/av-kit, main only per AGENTS.md "Commits"). One receipt per id
# under C:/Temp/av-kit/e2e-devpc-clipboard, named edc-D6-<id>.txt; every step's exit code is the
# code of the command that wrote that receipt, and the gate reads only those receipts.
# Fail-fast: the first non-zero step stops the gate and every later step is printed as not_run.
# The gate also fails when tested_state differs between its start and its end (an input changed
# while it ran; a Session 99 write in that window is named by scope-paths and the gate is rerun,
# D-1316).
# Writes nothing tracked: only the receipts, the temp folder, ui/out (ui-build, ignored), the
# snapshot selftest folder edc-snapshot-selftest-gate-<stamp>, the guard list
# edc-guard-list-gate-<stamp>.json (Playwright --list with AVKIT_E2E_CLIPBOARD_GATED removed: it
# runs no test), and the flake-run receipts and diag folders under C:/Temp/av-kit/e2e-devpc-clipboard,
# with <stamp> the gate's start time as yyyyMMdd-HHmmss (D-1285), so a rerun never meets an old
# file. No step reaches the network or the second Windows host (gated-count and remote-evidence
# read only row 8's local run folder), no step reads app data, and no step calls a model.
# flake-run.py stops only the processes its own runs started.
# e2e-full is flake-run.py --mode full --runs 1 --no-burn --label gate --expect-total 238: every
# E2E file except the two gated clipboard files (EXCLUDED; the OLD_CLIPBOARD guard refuses while
# an old file still calls the clipboard or clicks a writer, D-1319), with the clipboard guard on
# (AVKIT_E2E_CLIPBOARD_GATED is removed from every child; D-1310) and no busy children; an
# unrecorded failure reruns once alone, and a second failure or any receipt line holding
# `unhandled rejection:` or `CLIPBOARD_GUARD:` fails it. No clipboard file runs on this PC.
# guard-logs (D-1321, AC-21) is the guard's verdict independent of app.close(): every launch's
# <diag>/clipboard-<launch>.jsonl in the run and rerun folders the e2e-full receipt names (under
# flake-run's default --out) holds exactly one installed line and no failed or call line, but the
# AC-10 launch, which holds exactly its three calls; a launch with no installed line is counted.
# guard-logs-remote applies the same check to row 8's <run dir>/host/diag (the gated stage
# writes no log; its files are named by the known list).
# Exit = the first failing step's code.
# Skipped, per the plan: py-types, mcp-types, mcp-tests, mcp-build, openapi and mcp-audit (H1-4
# checks that every packages/, mcp-server/src, mcp-server/scripts, mcp-server/tests and native/
# file keeps its baseline-skip-hashes.json hash, and none was added or removed). Each is printed
# with its reason and runs nothing.
$ErrorActionPreference = 'Continue'
$root = (git rev-parse --show-toplevel).Trim()
Set-Location $root
$plan = 'docs/execution/plans/2026-11-20-e2e-devpc-clipboard'
$receipts = 'C:/Temp/av-kit/e2e-devpc-clipboard'
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
Write-Output "gate stamp: $stamp"
# lint_task_contract.py recognises the instantiated receipt paths only through RECEIPTS_DIR and
# fails closed (exit 3) when it is unset, which no user or machine scope sets on this host.
$env:RECEIPTS_DIR = 'C:/Temp/av-kit'
$env:PYTHONIOENCODING = 'utf-8'
$env:PYTHONDONTWRITEBYTECODE = '1'
Remove-Item Env:ELECTRON_RUN_AS_NODE -ErrorAction SilentlyContinue
Remove-Item Env:AVKIT_E2E_CLIPBOARD_GATED -ErrorAction SilentlyContinue
# RC1 ECN-2: keep the temp dirs away from the home folder.
$tmp = 'C:\Temp\av-kit\e2e-devpc-clipboard\tmp'
New-Item -ItemType Directory -Force -Path $tmp | Out-Null
$env:TMP = $tmp
$env:TEMP = $tmp
$base = (Get-Content "$plan/baseline.sha").Trim()
$cfg = Join-Path $HOME '.config/av-kit/e2e-host.json'

# Files Modified, this plan folder, the closeout artifacts (the handoffs and reviews under
# .agent/context/handoffs/2026-11-20-e2e-devpc-clipboard-*, the reflection, metrics.md and
# current-focus.md) and the paths baseline-dirty.txt already held. Foreign classes (Session 92
# RULE-3, D-1316): the coordinator's .agent/model-registry.local.json, .claude/agents/*.md and
# .cursor/agents/*.md, and Session 99's possible writes (ui/src/, its build-plan, MEU and skills
# files) are printed by name only, never with a content hash and never S4 (D-1330); Session 99's
# own folder, handoffs and reflection are named only, never read or hashed. D-1342 (coordinator
# ruling) adds Session 99's further paths to that class by name: its skill folder, its tool and
# test, test-ids.ts, failure-reason-copy.test.ts, its new unit, E2E and help-shots files,
# ui/package.json and ui/tsconfig.json; py-tests ignores its test, py-lint excludes it and
# ui-tests excludes its two new unit files. D-1343 adds its three tracked unit edits
# (capture-page, convert-page and settings-page tests), named only and bound by the tracked diff.
# Untracked plan folders of other sessions (2026-11-15 to 2026-11-29,
# absent from HEAD) are skipped. Anything else changed, HEAD moving, a "Read, never changed" file
# moving from baseline-scope.json, or a baseline-dirty-hashes.json path outside the foreign
# classes moving is S4.
$scopePaths = @"
import hashlib, json, pathlib, re, subprocess, sys
plan = '$plan'
mine = {
    'ui/tests/e2e/copy-system-clipboard.test.ts',
    'ui/tests/e2e/console-chrome.test.ts',
    'ui/tests/e2e/mcp-setup-prompt.test.ts',
    'ui/tests/e2e/settings.test.ts',
    'ui/tests/e2e/clipboard-guard.cjs',
    'ui/tests/e2e/clipboard-guard.test.ts',
    'ui/tests/e2e/electron-env.ts',
    'ui/tests/e2e/electron-app.ts',
    'ui/tests/unit/e2e-clipboard-guard.test.ts',
    'tools/e2e_host/known-failures.json',
    'tests/tooling/test_e2e_remote.py',
    '.agent/docs/e2e-remote-host.md',
    '.agent/docs/commands.md',
    '.agent/context/known-issues.yaml',
    '.agent/context/known-issues.md',
    '.agent/context/grouping/2026-11-20-e2e-devpc-clipboard-session-grouping.md',
    '.agent/context/current-focus.md',
    'docs/execution/metrics.md',
}
S99_PATHS = ('ui/src/', 'docs/build-plan/06-gui.md', 'docs/build-plan/build-priority-matrix.md', 'docs/BUILD_PLAN.md', '.agent/context/meu-status.yaml', '.agent/context/meu-registry.md', '.agent/skills/README.md', '.agent/skills/asd-ste100/', 'tools/help_guide_ste.py', 'tests/tooling/test_help_guide_ste.py', 'ui/tests/e2e/test-ids.ts', 'ui/tests/unit/failure-reason-copy.test.ts', 'ui/tests/unit/help-quick-start.test.tsx', 'ui/tests/unit/help-shots-privacy.test.ts', 'ui/tests/e2e/help-quick-start.test.ts', 'ui/tests/help-shots/', 'ui/playwright.help-shots.config.ts', 'ui/package.json', 'ui/tsconfig.json', 'ui/tests/unit/capture-page.test.ts', 'ui/tests/unit/convert-page.test.ts', 'ui/tests/unit/settings-page.test.ts')
S99_FOLDERS = ('docs/execution/plans/2026-11-20-help-quick-start/', '.agent/context/handoffs/2026-11-20-help-quick-start-', 'docs/execution/reflections/2026-11-20-help-quick-start')
def foreign_class(p):
    return p == '.agent/model-registry.local.json' or (
        p.startswith(('.claude/agents/', '.cursor/agents/')) and p.endswith('.md') and p.count('/') == 2
    )
def s99(p):
    return p.startswith(S99_PATHS)
def s99_folder(p):
    return p.startswith(S99_FOLDERS)
prefixes = (plan + '/', '.agent/context/handoffs/2026-11-20-e2e-devpc-clipboard-', 'docs/execution/reflections/2026-11-20-e2e-devpc-clipboard-')
scope = json.loads(pathlib.Path(plan + '/baseline-scope.json').read_text(encoding='utf-8'))
read_only = tuple(p for p in scope if p not in mine and not foreign_class(p) and not s99(p) and not p.startswith(prefixes))
s99_read = tuple(p for p in scope if s99(p) and p not in mine)
foreign_bound = tuple(p for p in scope if foreign_class(p))
other_plan_re = re.compile(r'^docs/execution/plans/2026-11-(1[5-9]|2[0-9])-[^/]+/')
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
dirty_all = [p for p, h in sorted(dirty_hashes.items()) if p not in mine and not p.startswith(prefixes) and drift(p, h)]
dirty_moved = [p for p in dirty_all if not s99(p) and not foreign_class(p)]
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
others = sorted({p for p in untracked if other_plan(p) or s99_folder(p)})
foreign = sorted({p for p in changed if foreign_class(p)})
s99_changed = sorted({p for p in changed if s99(p)})
extra = sorted({p for p in changed if p not in allowed and not p.startswith(prefixes) and p not in others and p not in foreign and p not in s99_changed})
print('changed paths:', len(changed), 'outside scope:', extra, 'other sessions plan files skipped (named only):', len(others))
print('read-never-changed files:', len(read_only), 'mismatch:', read_only_moved, 'baseline-dirty hash mismatch:', dirty_moved)
print('read-never-changed in the Session 99 class (names only, D-1316, D-1330):', [(p, 'peer-dirty at row 0' if scope[p] == 'peer-dirty, named only' else 'changed') for p in s99_read if scope[p] == 'peer-dirty, named only' or sha(p) != scope[p]])
print('foreign class (coordinator, printed only):', len(foreign_bound), 'changed:', foreign, 'row-0 hash moved:', foreign_moved)
print('foreign class (Session 99, names only, D-1330):', s99_changed)
print('head:', head, 'head moved (S4):', moved)
sys.exit(1 if extra or moved or read_only_moved or dirty_moved else 0)
"@

# known-list (D-1305): known [], skip [], gated holds exactly the two clipboard files for
# mini-air, every reason non-empty, LF.
$knownList = @"
import json, pathlib, sys
kp = 'tools/e2e_host/known-failures.json'
now = json.loads(pathlib.Path(kp).read_text(encoding='utf-8'))
raw = pathlib.Path(kp).read_bytes()
want = [('mini-air', 'capture-system-clipboard.test.ts'), ('mini-air', 'copy-system-clipboard.test.ts')]
gated = [(e.get('label'), e.get('file')) for e in now.get('gated', [])]
ok = now.get('known') == [] and now.get('skip') == [] and gated == want
reasons = all(str(e.get('reason', '')).strip() for e in now.get('gated', []))
print('keys:', sorted(now), 'skip:', now.get('skip'), 'gated:', gated, 'reasons:', reasons, 'LF:', b'\r' not in raw)
sys.exit(0 if ok and reasons and b'\r' not in raw else 1)
"@

# test-hashes (S3, Session 98 RULE-2): every test hash recorded at a Red still holds, read from
# every edc-test-sha-*.json in the order the rows wrote them, so a later Red's hash for a path
# replaces an earlier one (the newest Red binds).
$testHashes = @"
import hashlib, json, pathlib, sys
D = pathlib.Path('$receipts')
files = sorted(D.glob('edc-test-sha-*.json'), key=lambda p: p.stat().st_mtime)
want = {}
for f in files:
    for path, h in json.loads(f.read_text(encoding='utf-8')).items():
        want[path] = (h, f.name)
bad = []
for path, (h, name) in sorted(want.items()):
    have = hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()
    print(name, path, 'equal:', have == h)
    if have != h:
        bad.append(path)
print('test-hashes:', len(want), 'recorded in', [f.name for f in files], 'changed since their Red:', bad)
sys.exit(1 if bad or not want else 0)
"@

$run8 = (Get-Content "$receipts/edc-run-8-dir.txt" -ErrorAction SilentlyContinue | Select-Object -First 1)
Write-Output "row 8 run: $run8"

# remote-evidence: row 8's summary.json (its commit equal to the snapshot; the main stage 238
# tests, all expected, no new failure; the gated object present with an outcome from the five and
# both clipboard files) and the tool and every host file hash equal to its tool_sha256 (S13
# otherwise). The gated outcome itself is a receipt (D-1314); under a `run` outcome the three
# moved tests of copy-system-clipboard.test.ts must all be expected (their assertions are
# unchanged, D-1303), while a capture-system-clipboard.test.ts failure is the open primer issue's
# symptom: recorded by gated-count, never this step's failure. Reads only the local run folder.
$remoteEvidence = @"
import hashlib, json, pathlib, subprocess, sys
D = pathlib.Path('$receipts')
d = pathlib.Path((D / 'edc-run-8-dir.txt').read_text(encoding='utf-8').strip())
s = json.loads((d / 'summary.json').read_text(encoding='utf-8'))
snap = json.loads((D / 'edc-snapshot-8.json').read_text(encoding='utf-8')).get('commit')
recorded = s.get('tool_sha256') or {}
def sha(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
now = {'tools/e2e_remote.py': sha('tools/e2e_remote.py')}
for p in sorted(pathlib.Path('tools/e2e_host').iterdir()):
    if p.is_file() and p.suffix in ('.ps1', '.json'):
        now['tools/e2e_host/' + p.name] = sha(p)
diff = sorted(k for k in set(now).union(recorded) if now.get(k) != recorded.get(k))
main_ok = s.get('tests') == 238 and s.get('expected') == 238 and not s.get('new') and bool(snap) and s.get('commit') == snap
gated = s.get('gated')
outcomes = ('run', 'skipped-connected', 'skipped-undecided', 'voided-connected-during', 'voided-undecided-during')
files = sorted(gated.get('files') or []) if isinstance(gated, dict) else None
gated_ok = isinstance(gated, dict) and gated.get('outcome') in outcomes and files == ['capture-system-clipboard.test.ts', 'copy-system-clipboard.test.ts']
moved_ok = True
if gated_ok and gated.get('outcome') == 'run':
    out = subprocess.run([sys.executable, '$plan/gated-count.py', '--run', str(d)], capture_output=True, text=True)
    print(out.stdout.rstrip())
    moved_ok = out.returncode == 0 and ' other=3/3' in out.stdout
print('run folder name:', d.name, 'summary exit:', s.get('exit'), 'tests', s.get('tests'), 'expected', s.get('expected'), 'new', len(s.get('new') or []), 'commit equals the snapshot:', s.get('commit') == snap)
print('gated:', json.dumps(gated, sort_keys=True) if isinstance(gated, dict) else gated, 'moved tests all expected (or not run):', moved_ok)
print('files hashed now:', len(now), 'recorded:', len(recorded), 'remote-evidence mismatch:', diff)
if diff:
    print('S13: the tool, a host file or the known list changed after row 8')
sys.exit(0 if main_ok and gated_ok and moved_ok and not diff else 1)
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
    '--grown', '.agent/context/grouping/2026-11-20-e2e-devpc-clipboard-session-grouping.md', "$receipts/baseline-copies/.agent/context/grouping/2026-11-20-e2e-devpc-clipboard-session-grouping.md"
)
$steps = @(
    @{ Id = 'identity-before'; Stage = 'identity'; Argv = $identity },
    @{ Id = 'task-contract'; Stage = 'static'; Argv = $py + @('tools/lint_task_contract.py', '--allowed-builder-classes', 'avkit_builder,avkit_coordinator,avkit_verifier', '--task', "$plan/task.md") },
    @{ Id = 'scope-paths'; Stage = 'static'; Argv = $py + @('-c', $scopePaths) },
    @{ Id = 'line-endings'; Stage = 'static'; Argv = $py + @("$plan/eol-check.py") },
    @{ Id = 'home-path'; Stage = 'static'; Argv = $py + @('tools/check_home_path.py') },
    @{ Id = 'host-details'; Stage = 'static'; Argv = $py + @("$plan/host-details-scan.py", $cfg) + $grown },
    @{ Id = 'split-check'; Stage = 'static'; Argv = $py + @("$plan/split-specs.py", '--check') },
    @{ Id = 'guard-list'; Stage = 'static'; Argv = $py + @("$plan/guard-check.py", '--list', "$receipts/edc-guard-list-gate-$stamp.json") },
    @{ Id = 'writer-scan'; Stage = 'static'; Argv = $py + @("$plan/writer-scan.py") },
    @{ Id = 'pins'; Stage = 'static'; Argv = $py + @("$plan/pins-check.py") },
    @{ Id = 'known-list'; Stage = 'static'; Argv = $py + @('-c', $knownList) },
    @{ Id = 'red-check-selftest'; Stage = 'static'; Argv = $py + @("$plan/red-check.py", '--selftest') },
    @{ Id = 'eol-check-selftest'; Stage = 'static'; Argv = $py + @("$plan/eol-check.py", '--selftest') },
    @{ Id = 'split-specs-selftest'; Stage = 'static'; Argv = $py + @("$plan/split-specs.py", '--selftest') },
    @{ Id = 'writer-scan-selftest'; Stage = 'static'; Argv = $py + @("$plan/writer-scan.py", '--selftest') },
    @{ Id = 'gated-count-selftest'; Stage = 'static'; Argv = $py + @("$plan/gated-count.py", '--selftest') },
    @{ Id = 'pins-check-selftest'; Stage = 'static'; Argv = $py + @("$plan/pins-check.py", '--selftest') },
    @{ Id = 'guard-check-selftest'; Stage = 'static'; Argv = $py + @("$plan/guard-check.py", '--selftest') },
    @{ Id = 'flake-run-selftest'; Stage = 'static'; Argv = $py + @("$plan/flake-run.py", '--selftest') },
    @{ Id = 'guard-logs-selftest'; Stage = 'static'; Argv = $py + @("$plan/guard-logs.py", '--selftest') },
    @{ Id = 'snapshot-selftest'; Stage = 'static'; Argv = $py + @("$plan/snapshot-commit.py", '--selftest', "$receipts/edc-snapshot-selftest-gate-$stamp") },
    @{ Id = 'py-format'; Stage = 'static'; Argv = @('uv', 'run', '--no-sync', 'ruff', 'format', '--check', 'tests/tooling/test_e2e_remote.py') + $planPy },
    @{ Id = 'py-lint'; Stage = 'static'; Argv = @('uv', 'run', '--no-sync', 'ruff', 'check', '--extend-exclude', 'tests/tooling/test_help_guide_ste.py', 'packages/', 'tests/') + $planPy },
    @{ Id = 'snapshot-verify'; Stage = 'static'; Argv = $py + @("$plan/snapshot-commit.py", '--verify', "$receipts/edc-snapshot-8.json") },
    @{ Id = 'test-hashes'; Stage = 'static'; Argv = $py + @('-c', $testHashes) },
    @{ Id = 'ui-types'; Stage = 'ui-static'; Cwd = 'ui'; Argv = @('npm', 'run', 'typecheck') },
    @{ Id = 'ui-lint'; Stage = 'ui-static'; Cwd = 'ui'; Argv = @('npm', 'run', 'lint') },
    @{ Id = 'ui-tests'; Stage = 'tests'; Cwd = 'ui'; Argv = @('npm', 'run', 'test', '--', '--exclude', '**/tests/unit/help-quick-start.test.tsx', '--exclude', '**/tests/unit/help-shots-privacy.test.ts') },
    @{ Id = 'py-tests'; Stage = 'tests'; Argv = @('uv', 'run', '--no-sync', 'pytest', 'tests/', '-x', '-q', '-p', 'no:cacheprovider', '--ignore', 'tests/tooling/test_help_guide_ste.py') },
    @{ Id = 'canon'; Stage = 'tests'; Cwd = 'ui'; Argv = @('npm', 'run', 'test', '--', 'tests/unit/layout-canon.test.ts', 'tests/unit/queue-canon.test.ts') },
    @{ Id = 'host-load'; Stage = 'host'; Argv = @('pwsh', '-NoProfile', '-File', "$plan/host-load.ps1") },
    @{ Id = 'ui-build'; Stage = 'e2e'; Cwd = 'ui'; Argv = @('npm', 'run', 'build') },
    @{ Id = 'e2e-full'; Stage = 'e2e'; Argv = $py + @("$plan/flake-run.py", '--mode', 'full', '--runs', '1', '--no-burn', '--label', "gate-$stamp", '--expect-total', '238'); NoRejection = $true },
    @{ Id = 'guard-logs'; Stage = 'e2e'; Argv = $py + @("$plan/guard-logs.py", '--receipt', "$receipts/edc-D6-e2e-full.txt") },
    @{ Id = 'issues-render-check'; Stage = 'registers'; Argv = $py + @('tools/issue_triage.py', 'render', '--check') },
    @{ Id = 'state-render'; Stage = 'registers'; Argv = $py + @('tools/meu_status.py', 'render', '--check') },
    @{ Id = 'gated-count'; Stage = 'registers'; Argv = $py + @("$plan/gated-count.py", '--run', "$run8") },
    @{ Id = 'guard-logs-remote'; Stage = 'registers'; Argv = $py + @("$plan/guard-logs.py", '--diag', "$run8/host/diag") },
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
    $receipt = "$receipts/edc-D6-$($step.Id).txt"
    $argv = $step.Argv
    if ($step.ContainsKey('Cwd')) { Set-Location (Join-Path $root $step.Cwd) }
    & rtk proxy @argv *> $receipt
    $code = $LASTEXITCODE
    Set-Location $root
    Write-Output ("{0} stage={1} exit={2} receipt={3}" -f $step.Id, $step.Stage, $code, $receipt)
    Get-Content $receipt | Select-Object -Last 6
    if ($step.ContainsKey('NoRejection')) {
        # S10: any rejection record or clipboard-guard record fails the gate, whatever the exit code.
        $records = @(Select-String -Path $receipt -Pattern 'unhandled rejection:' -SimpleMatch).Count
        $guard = @(Select-String -Path $receipt -Pattern 'CLIPBOARD_GUARD:' -SimpleMatch).Count
        Write-Output ("{0}: rejection-record lines={1} clipboard-guard lines={2}" -f $step.Id, $records, $guard)
        if ($records -ne 0 -or $guard -ne 0) { $code = 10 }
    }
    if ($code -eq 0 -and $step.Id -eq 'identity-after') {
        $before = Get-TestedState "$receipts/edc-D6-identity-before.txt"
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
