# Session 96 fresh-full gate (task H1-2; implementation-plan.md "Session gate (H1-2)").
# The shape of docs/execution/plans/2026-11-18-eval-describe-raw-bytes/session-gate.ps1, with
# this plan's steps: identity, then the static checks (the task contract, scope-paths,
# line-endings, home-path, the red-check and eol-check selftests, py-format on
# tools/e2e_remote.py, the test file and this plan folder's Python, py-lint as
# ruff check packages/ tests/ tools/e2e_remote.py plus this plan folder's Python, json-valid),
# then the targeted checks (erh-tests, erh-summary-191358, erh-summary-185348, erh-zip-time),
# then host-load (Session 81 RULE-2, through host-load.ps1), then the fresh full checks
# (py-tests, remote-evidence, issues-render-check, state-render), then the identity again.
# Runs from the repository root (P:/av-kit, main only per AGENTS.md "Commits"). One receipt per
# id under C:/Temp/av-kit/e2e-remote-host, named erh-D6-<id>.txt; every step's exit code is the
# code of the command that wrote that receipt, and the gate reads only those receipts.
# Fail-fast: the first non-zero step stops the gate and every later step is printed as
# not_run. The gate also fails when tested_state differs between its start and its end (an
# input changed while it ran).
# Writes nothing tracked: only the receipts, the temp folder, two summarize folders
# erh-sum-gate-<stamp>-191358 and erh-sum-gate-<stamp>-185348, the reproduction folder
# zip-gate-<stamp> and the pytest base folders under C:/Temp/av-kit/e2e-remote-host, with
# <stamp> the gate's start time as yyyyMMdd-HHmmss, so a rerun never meets an old folder.
# No step reaches the network or the second Windows host (remote-evidence reads only row 6's
# local summary.json), no step starts the app, no step reads app data, and no step calls a
# model. Exit = the first failing step's code.
# Skipped, per the plan: py-types, ui-types, ui-lint, ui-tests, ui-build, ui-electron,
# mcp-types, mcp-tests, mcp-build, openapi and mcp-audit (H1-4 checks that every packages/,
# ui/, mcp-server/src, mcp-server/scripts, mcp-server/tests and native/ file keeps its
# baseline-skip-hashes.json hash, and none was added or removed). Each is printed with its
# reason and runs nothing.
$ErrorActionPreference = 'Continue'
$root = (git rev-parse --show-toplevel).Trim()
Set-Location $root
$plan = 'docs/execution/plans/2026-11-18-e2e-remote-host'
$receipts = 'C:/Temp/av-kit/e2e-remote-host'
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
Write-Output "gate stamp: $stamp"
# lint_task_contract.py recognises the instantiated receipt paths only through RECEIPTS_DIR and
# fails closed (exit 3) when it is unset, which no user or machine scope sets on this host.
$env:RECEIPTS_DIR = 'C:/Temp/av-kit'
$env:PYTHONIOENCODING = 'utf-8'
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:ELECTRON_RUN_AS_NODE = $null
# RC1 ECN-2: keep the temp dirs away from the home folder.
$tmp = 'C:\Temp\av-kit\e2e-remote-host\tmp'
New-Item -ItemType Directory -Force -Path $tmp | Out-Null
$env:TMP = $tmp
$env:TEMP = $tmp
$base = (Get-Content "$plan/baseline.sha").Trim()

# Files Modified, this plan folder, the closeout artifacts (the handoffs and reviews under
# .agent/context/handoffs/2026-11-18-e2e-remote-host-*, the reflection, metrics.md and
# current-focus.md) and the paths baseline-dirty.txt already held. Foreign class (Session 92
# RULE-3): .agent/model-registry.local.json, .claude/agents/*.md and .cursor/agents/*.md belong
# to the coordinator; a change there is printed, never S4. Untracked plan folders of other
# sessions (2026-11-15 to 2026-11-18, absent from HEAD) are skipped. Anything else changed,
# HEAD moving, a "Read, never changed" file moving from baseline-scope.json, or a
# baseline-dirty-hashes.json path moving is S4.
$scopePaths = @"
import hashlib, json, pathlib, re, subprocess, sys
plan = '$plan'
host_scripts = ('host-facts', 'host-lock', 'host-prepare', 'host-start', 'host-status', 'host-release', 'run-e2e')
mine = {
    'tests/tooling/test_e2e_remote.py',
    'tools/e2e_remote.py',
    'tools/e2e_host/e2e-host.example.json',
    'tools/e2e_host/known-failures.json',
    *('tools/e2e_host/' + n + '.ps1' for n in host_scripts),
    '.agent/docs/e2e-remote-host.md',
    '.agent/docs/commands.md',
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
scope = json.loads(pathlib.Path(plan + '/baseline-scope.json').read_text(encoding='utf-8'))
read_only = tuple(p for p in scope if p not in mine and not foreign_class(p) and not p.startswith('.agent/context/handoffs/'))
foreign_bound = tuple(p for p in scope if foreign_class(p))
prefixes = (plan + '/', '.agent/context/handoffs/2026-11-18-e2e-remote-host-', 'docs/execution/reflections/2026-11-18-e2e-remote-host-')
other_plan_re = re.compile(r'^docs/execution/plans/2026-11-1[5-8]-[^/]+/')
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
dirty_moved = [p for p, h in sorted(dirty_hashes.items()) if drift(p, h)]
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

# json-valid: the example and the known list parse, and the example passes load_config.
$jsonValid = @"
import importlib.util, json, pathlib, sys
spec = importlib.util.spec_from_file_location('e2e_remote', 'tools/e2e_remote.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
example = pathlib.Path('tools/e2e_host/e2e-host.example.json')
known = pathlib.Path('tools/e2e_host/known-failures.json')
ex = json.loads(example.read_text(encoding='utf-8'))
kn = json.loads(known.read_text(encoding='utf-8'))
cfg = mod.load_config(example)
keys = sorted(cfg) == sorted(mod.CONFIG_KEYS)
print('example keys:', len(ex), 'load_config ok, config keys match:', keys)
print('known list type:', type(kn).__name__, 'entries:', len(kn) if hasattr(kn, '__len__') else None)
sys.exit(0 if keys and isinstance(ex, dict) and kn else 1)
"@

# erh-tests: the pytest file at its recorded hash (S3; D-1235 re-recorded it), no skip, and a
# passed line.
$erhTests = @"
import hashlib, pathlib, re, subprocess, sys
test = 'tests/tooling/test_e2e_remote.py'
want = pathlib.Path('$receipts/erh-test-sha.txt').read_text(encoding='utf-8').strip()
have = hashlib.sha256(pathlib.Path(test).read_bytes()).hexdigest()
print('test_sha256 ' + have, 'recorded ' + want, 'equal:', have == want)
if have != want:
    print('S3: the test file changed since its recorded hash')
    sys.exit(1)
argv = [sys.executable, '-m', 'pytest', test, '--tb=short', '-q', '-rs', '-p', 'no:cacheprovider', '--basetemp', '$receipts/pytest-gate-$stamp']
proc = subprocess.run(argv, capture_output=True)
out = proc.stdout.decode('utf-8', 'replace') + proc.stderr.decode('utf-8', 'replace')
print(out.rstrip())
passed = re.search(r'^([0-9]+) passed in ', out, re.M)
skipped = re.search(r'[0-9]+ (skipped|xfailed|xpassed|deselected)', out)
print('pytest exit:', proc.returncode, 'passed line:', passed.group(0) if passed else None, 'skip found:', bool(skipped))
sys.exit(proc.returncode if proc.returncode else (0 if passed and not skipped else 1))
"@

# erh-summary-<id>: summarize a hand report into a fresh folder; row 3's exit and counts.
function New-SummaryCheck([string]$Id, [int]$WantExit) {
    return @"
import json, pathlib, subprocess, sys
rid = '$Id'
out = pathlib.Path('$receipts/erh-sum-gate-$stamp-' + rid)
report = 'C:/Temp/av-kit/fleet-research/miniair/results/20261118-' + rid + '/report.json'
argv = [sys.executable, 'tools/e2e_remote.py', 'summarize', report, '--label', 'mini-air', '--out', str(out)]
proc = subprocess.run(argv, capture_output=True)
text = proc.stdout.decode('utf-8', 'replace') + proc.stderr.decode('utf-8', 'replace')
print(text.rstrip())
print('summarize exit:', proc.returncode, 'want $WantExit')
if proc.returncode != $($WantExit):
    sys.exit(1)
s = json.loads((out / 'summary.json').read_text(encoding='utf-8'))
known = sorted(k['ac'] for k in s['known'])
new = sorted(k['ac'] for k in s['new'])
skip = sorted(e['file'] for e in s['skip'])
four = ['AC-102.19', 'AC-102.20', 'AC-126.8', 'AC-82.6']
eight = sorted(['AC-152.21', 'AC-152.22', 'AC-152.23', 'AC-152.24', 'AC-155.10', 'AC-155.11', 'AC-155.15', 'AC-156.11'])
if rid == '191358':
    ok = s['tests'] == 232 and s['expected'] == 228 and known == four and new == [] and skip == ['capture-filmstrip-actions.test.ts', 'capture-import.test.ts'] and s['exit'] == 0
else:
    ok = s['expected'] == 220 and s['unexpected'] == 12 and len(known) == 4 and new == eight and s['exit'] == 40
print(rid + ':', 'tests', s['tests'], 'expected', s['expected'], 'unexpected', s['unexpected'], 'known', known, 'new', new, 'summary exit', s['exit'], 'counts ok:', ok)
sys.exit(0 if ok else 1)
"@
}

# remote-evidence: the tool and every host file hash equal tool_sha256 in row 6's summary.json
# (S13 otherwise). Reads only the local run folder named in erh-run-6-dir.txt.
$remoteEvidence = @"
import hashlib, json, pathlib, sys
d = pathlib.Path(pathlib.Path('$receipts/erh-run-6-dir.txt').read_text(encoding='utf-8').strip())
s = json.loads((d / 'summary.json').read_text(encoding='utf-8'))
recorded = s.get('tool_sha256') or {}
def sha(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
now = {'tools/e2e_remote.py': sha('tools/e2e_remote.py')}
for p in sorted(pathlib.Path('tools/e2e_host').iterdir()):
    if p.is_file():
        now['tools/e2e_host/' + p.name] = sha(p)
diff = sorted(k for k in set(now).union(recorded) if now.get(k) != recorded.get(k))
print('run folder name:', d.name, 'summary exit:', s.get('exit'), 'files hashed now:', len(now), 'recorded:', len(recorded))
print('remote-evidence mismatch:', diff)
if diff:
    print('S13: the tool or a host file changed after row 6')
sys.exit(1 if diff else 0)
"@

$skipped = @(
    @{ Id = 'py-types'; Stage = 'static'; Reason = 'every packages/ file keeps its baseline-skip-hashes.json hash (H1-4); no product Python changes' },
    @{ Id = 'ui-types/ui-lint/ui-tests/ui-build/ui-electron'; Stage = 'full'; Reason = 'every ui/ and native/ file keeps its baseline-skip-hashes.json hash (H1-4); no UI file changes; the full E2E evidence is row 6 run on the second Windows host of the same product' },
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
$fmtPy = @('tools/e2e_remote.py', 'tests/tooling/test_e2e_remote.py') + $planPy
$lintPy = @('packages/', 'tests/', 'tools/e2e_remote.py') + $planPy
$steps = @(
    @{ Id = 'identity-before'; Stage = 'identity'; Argv = $identity },
    @{ Id = 'task-contract'; Stage = 'static'; Argv = $py + @('tools/lint_task_contract.py', '--allowed-builder-classes', 'avkit_builder,avkit_coordinator,avkit_verifier', '--task', "$plan/task.md") },
    @{ Id = 'scope-paths'; Stage = 'static'; Argv = $py + @('-c', $scopePaths) },
    @{ Id = 'line-endings'; Stage = 'static'; Argv = $py + @("$plan/eol-check.py") },
    @{ Id = 'home-path'; Stage = 'static'; Argv = $py + @('tools/check_home_path.py') },
    @{ Id = 'red-check-selftest'; Stage = 'static'; Argv = $py + @("$plan/red-check.py", '--selftest') },
    @{ Id = 'eol-check-selftest'; Stage = 'static'; Argv = $py + @("$plan/eol-check.py", '--selftest') },
    @{ Id = 'py-format'; Stage = 'static'; Argv = @('uv', 'run', '--no-sync', 'ruff', 'format', '--check') + $fmtPy },
    @{ Id = 'py-lint'; Stage = 'static'; Argv = @('uv', 'run', '--no-sync', 'ruff', 'check') + $lintPy },
    @{ Id = 'json-valid'; Stage = 'static'; Argv = $py + @('-c', $jsonValid) },
    @{ Id = 'erh-tests'; Stage = 'targeted'; Argv = $py + @('-c', $erhTests) },
    @{ Id = 'erh-summary-191358'; Stage = 'targeted'; Argv = $py + @('-c', (New-SummaryCheck '191358' 0)) },
    @{ Id = 'erh-summary-185348'; Stage = 'targeted'; Argv = $py + @('-c', (New-SummaryCheck '185348' 40)) },
    @{ Id = 'erh-zip-time'; Stage = 'targeted'; Argv = $py + @("$plan/zip-time.py", $base, "$receipts/zip-gate-$stamp", '-8') },
    @{ Id = 'host-load'; Stage = 'host'; Argv = @('pwsh', '-NoProfile', '-File', "$plan/host-load.ps1") },
    @{ Id = 'py-tests'; Stage = 'full'; Argv = @('uv', 'run', '--no-sync', 'pytest', 'tests/', '-x', '--tb=short', '-q') },
    @{ Id = 'remote-evidence'; Stage = 'full'; Argv = $py + @('-c', $remoteEvidence) },
    @{ Id = 'issues-render-check'; Stage = 'full'; Argv = $py + @('tools/issue_triage.py', 'render', '--check') },
    @{ Id = 'state-render'; Stage = 'full'; Argv = $py + @('tools/meu_status.py', 'render', '--check') },
    @{ Id = 'identity-after'; Stage = 'identity'; Argv = $identity }
)

function Get-TestedState([string]$Receipt) {
    $line = Select-String -Path $Receipt -Pattern '^tested_state ' | Select-Object -Last 1
    if ($null -eq $line) { return $null }
    return $line.Line.Substring('tested_state '.Length).Trim()
}

New-Item -ItemType Directory -Force -Path "$receipts/zip-gate-$stamp" | Out-Null
for ($i = 0; $i -lt $steps.Count; $i++) {
    $step = $steps[$i]
    $receipt = "$receipts/erh-D6-$($step.Id).txt"
    $argv = $step.Argv
    & rtk proxy @argv *> $receipt
    $code = $LASTEXITCODE
    Write-Output ("{0} stage={1} exit={2} receipt={3}" -f $step.Id, $step.Stage, $code, $receipt)
    Get-Content $receipt | Select-Object -Last 6
    if ($code -eq 0 -and $step.Id -eq 'identity-after') {
        $before = Get-TestedState "$receipts/erh-D6-identity-before.txt"
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
