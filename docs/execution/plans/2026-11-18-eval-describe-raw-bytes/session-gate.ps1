# Session 95 fresh-full gate (task H1-2; implementation-plan.md "Session gate (H1-2)").
# The shape of docs/execution/plans/2026-11-17-mcp-audit-refresh/session-gate.ps1, with this
# plan's steps: identity, then the static checks (the task contract, scope-paths, line-endings,
# home-path, the red-check, eol-check and edr-check selftests, py-format and py-lint on this
# plan folder's Python and Session 64's eval-describe.py), then the targeted checks (edr-tests,
# edr-records, edr-doc, edr-old-refused), then host-load (Session 81 RULE-2, through
# host-load.ps1, bar 50 %), then the fresh full checks (mcp-build, edr-live-gate,
# issues-render-check, state-render), then the identity again.
# Runs from the repository root (P:/av-kit, main only per AGENTS.md "Commits"). One receipt per
# id under C:/Temp/av-kit/eval-describe-raw-bytes, named edr-D6-<id>.txt; every step's exit
# code is the code of the command that wrote that receipt, and the gate reads only those
# receipts. Fail-fast: the first non-zero step stops the gate and every later step is printed
# as not_run. The gate also fails when tested_state differs between its start and its end (an
# input changed while it ran).
# Writes nothing tracked: only the receipts, the temp folder, mcp-server/dist (mcp-build;
# ignored), the two new eval roots s95-gate-<stamp> and s95-gate-<stamp>-direct under
# C:/Temp/av-kit/s64/eval/ (edr-live-gate) and their receipts D/edr-gate-<stamp>*.txt, with
# <stamp> the gate's start time as yyyyMMdd-HHmmss, so NO_OVERWRITE never trips on a rerun.
# Nothing here reaches the network or YouTube, no step starts the app, no step reads app data,
# and no step dispatches a model (the harness describe step builds the prompts and calls none).
# Exit = the first failing step's code.
# Skipped, per the plan: py-tests, py-types, ui-types, ui-lint, ui-tests, ui-build, ui-electron,
# mcp-types, mcp-tests, openapi and mcp-audit (H1-4 checks that every packages/, tools/, ui/,
# tests/, mcp-server/src, mcp-server/scripts and mcp-server/tests file keeps its
# baseline-skip-hashes.json hash, and none was added or removed). Each is printed with its
# reason and runs nothing.
$ErrorActionPreference = 'Continue'
$root = (git rev-parse --show-toplevel).Trim()
Set-Location $root
$plan = 'docs/execution/plans/2026-11-18-eval-describe-raw-bytes'
$s64 = 'docs/execution/plans/2026-11-11-capture-export-copy'
$receipts = 'C:/Temp/av-kit/eval-describe-raw-bytes'
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
Write-Output "gate stamp: $stamp"
# lint_task_contract.py recognises the instantiated receipt paths only through RECEIPTS_DIR and
# fails closed (exit 3) when it is unset, which no user or machine scope sets on this host.
$env:RECEIPTS_DIR = 'C:/Temp/av-kit'
$env:PYTHONIOENCODING = 'utf-8'
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:ELECTRON_RUN_AS_NODE = $null
# RC1 ECN-2: keep the temp dirs away from the home folder.
$tmp = 'C:\Temp\av-kit\eval-describe-raw-bytes\tmp'
New-Item -ItemType Directory -Force -Path $tmp | Out-Null
$env:TMP = $tmp
$env:TEMP = $tmp
$base = (Get-Content "$plan/baseline.sha").Trim()

# Files Modified, this plan folder, the closeout artifacts (the handoffs and reviews under
# .agent/context/handoffs/2026-11-18-eval-describe-raw-bytes-*, the reflection, metrics.md and
# current-focus.md) and the paths baseline-dirty.txt already held. Foreign class (Session 92
# RULE-3): .agent/model-registry.local.json, .claude/agents/*.md and .cursor/agents/*.md belong
# to the coordinator; a change there is printed, never S4. Untracked plan folders of other
# sessions (2026-11-15 to 2026-11-18, absent from HEAD) are skipped. Anything else changed,
# HEAD moving, a "Read, never changed" file moving from baseline-scope.json, or a
# baseline-dirty-hashes.json path moving is S4.
$scopePaths = @"
import hashlib, json, pathlib, re, subprocess, sys
plan = '$plan'
mine = {
    '$s64/eval-describe.py',
    '$s64/eval-run.md',
    '.agent/context/known-issues.yaml',
    '.agent/context/known-issues.md',
    '.agent/context/grouping/2026-11-18-eval-describe-session-grouping.md',
    '.agent/context/current-focus.md',
    'docs/execution/metrics.md',
    '.agent/context/handoffs/2026-11-18-eval-describe-raw-bytes-handoff.md',
    plan + '/test_eval_describe.py',
}
def foreign_class(p):
    return p == '.agent/model-registry.local.json' or (
        p.startswith(('.claude/agents/', '.cursor/agents/')) and p.endswith('.md') and p.count('/') == 2
    )
scope = json.loads(pathlib.Path(plan + '/baseline-scope.json').read_text(encoding='utf-8'))
read_only = tuple(p for p in scope if p not in mine and not foreign_class(p))
foreign_bound = tuple(p for p in scope if foreign_class(p))
prefixes = (plan + '/', '.agent/context/handoffs/2026-11-18-eval-describe-raw-bytes-', 'docs/execution/reflections/2026-11-18-eval-describe-raw-bytes-')
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

# edr-tests: the pytest file at its Red hash (S3), no skip, and a passed line.
$edrTests = @"
import hashlib, pathlib, re, subprocess, sys
test = '$plan/test_eval_describe.py'
want = pathlib.Path('$receipts/edr-test-sha.txt').read_text(encoding='utf-8').strip()
have = hashlib.sha256(pathlib.Path(test).read_bytes()).hexdigest()
print('test_sha256 ' + have, 'red ' + want, 'equal:', have == want)
if have != want:
    print('S3: the test file changed since Red')
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

# edr-old-refused: check exits 1 with a non-zero mojibake count on each old receipt (AC-8).
$oldRefused = @"
import re, subprocess, sys
script = '$s64/eval-describe.py'
bad = []
for f in ('$receipts/edr-old-e1.txt', '$receipts/edr-old-step3.txt', 'C:/Temp/av-kit/s64-E1-describe.txt'):
    proc = subprocess.run([sys.executable, script, 'check', f], capture_output=True)
    out = proc.stdout.decode('utf-8', 'replace') + proc.stderr.decode('utf-8', 'replace')
    print(out.rstrip())
    moj = bool(re.search(r'mojibake: [1-9][0-9]* match', out))
    print(f, 'exit', proc.returncode, 'mojibake refusal:', moj)
    if proc.returncode != 1 or not moj:
        bad.append(f)
print('edr-old-refused:', 'ok, 3 of 3 refused' if not bad else 'failed ' + str(bad))
sys.exit(1 if bad else 0)
"@

# edr-live-gate: capture on a new root, then edr-check.py live against a direct read on another.
$liveGate = @"
import subprocess, sys
cap = '$receipts/edr-gate-$stamp.txt'
argv = [sys.executable, '$s64/eval-describe.py', 'capture', 'C:/Temp/av-kit/s64/eval/s95-gate-$stamp/root', cap]
proc = subprocess.run(argv, capture_output=True)
out = proc.stdout.decode('utf-8', 'replace') + proc.stderr.decode('utf-8', 'replace')
print(out.rstrip())
print('capture exit:', proc.returncode)
if proc.returncode != 0:
    print('S10: the capture refused; stop and record')
    sys.exit(proc.returncode)
argv = [sys.executable, '$plan/edr-check.py', 'live', cap, 'C:/Temp/av-kit/s64/eval/s95-gate-$stamp-direct/root', '$receipts/edr-gate-$stamp-direct.txt']
proc = subprocess.run(argv, capture_output=True)
out = proc.stdout.decode('utf-8', 'replace') + proc.stderr.decode('utf-8', 'replace')
print(out.rstrip())
print('live exit:', proc.returncode)
sys.exit(proc.returncode)
"@

$skipped = @(
    @{ Id = 'py-tests'; Stage = 'full'; Reason = 'every packages/ and tests/ file keeps its baseline-skip-hashes.json hash (H1-4); no product Python changes' },
    @{ Id = 'py-types'; Stage = 'static'; Reason = 'every packages/ file keeps its baseline-skip-hashes.json hash (H1-4); no product Python changes' },
    @{ Id = 'ui-types/ui-lint/ui-tests/ui-build/ui-electron'; Stage = 'full'; Reason = 'every ui/ file keeps its baseline-skip-hashes.json hash (H1-4); no UI file changes' },
    @{ Id = 'mcp-types/mcp-tests'; Stage = 'full'; Reason = 'every mcp-server/src, mcp-server/scripts and mcp-server/tests file keeps its baseline-skip-hashes.json hash (H1-4); no server file changes' },
    @{ Id = 'openapi'; Stage = 'full'; Reason = 'every packages/api/ file keeps its baseline-skip-hashes.json hash (H1-4); no route or schema changes' },
    @{ Id = 'mcp-audit'; Stage = 'runtime'; Reason = 'no server file changes (H1-4); the audit is a network run and this session uses no network' }
)
foreach ($s in $skipped) {
    Write-Output ("{0} stage={1} skipped reason={2}" -f $s.Id, $s.Stage, $s.Reason)
}

$py = @('uv', 'run', '--no-sync', 'python')
$identity = $py + @("$plan/identity.py")
$lintPy = @(Get-ChildItem -Path $plan -Filter '*.py' | Sort-Object Name | ForEach-Object { "$plan/$($_.Name)" }) + @("$s64/eval-describe.py")
$steps = @(
    @{ Id = 'identity-before'; Stage = 'identity'; Argv = $identity },
    @{ Id = 'task-contract'; Stage = 'static'; Argv = $py + @('tools/lint_task_contract.py', '--allowed-builder-classes', 'avkit_builder,avkit_coordinator,avkit_verifier', '--task', "$plan/task.md") },
    @{ Id = 'scope-paths'; Stage = 'static'; Argv = $py + @('-c', $scopePaths) },
    @{ Id = 'line-endings'; Stage = 'static'; Argv = $py + @("$plan/eol-check.py") },
    @{ Id = 'home-path'; Stage = 'static'; Argv = $py + @('tools/check_home_path.py') },
    @{ Id = 'red-check-selftest'; Stage = 'static'; Argv = $py + @("$plan/red-check.py", '--selftest') },
    @{ Id = 'eol-check-selftest'; Stage = 'static'; Argv = $py + @("$plan/eol-check.py", '--selftest') },
    @{ Id = 'edr-check-selftest'; Stage = 'static'; Argv = $py + @("$plan/edr-check.py", '--selftest') },
    @{ Id = 'py-format'; Stage = 'static'; Argv = @('uv', 'run', '--no-sync', 'ruff', 'format', '--check') + $lintPy },
    @{ Id = 'py-lint'; Stage = 'static'; Argv = @('uv', 'run', '--no-sync', 'ruff', 'check') + $lintPy },
    @{ Id = 'edr-tests'; Stage = 'targeted'; Argv = $py + @('-c', $edrTests) },
    @{ Id = 'edr-records'; Stage = 'targeted'; Argv = $py + @("$plan/edr-check.py", 'records') },
    @{ Id = 'edr-doc'; Stage = 'targeted'; Argv = $py + @("$plan/edr-check.py", 'doc', "$receipts/edr-describe.txt") },
    @{ Id = 'edr-old-refused'; Stage = 'targeted'; Argv = $py + @('-c', $oldRefused) },
    @{ Id = 'host-load'; Stage = 'host'; Argv = @('pwsh', '-NoProfile', '-File', "$plan/host-load.ps1") },
    @{ Id = 'mcp-build'; Stage = 'full'; Argv = @('npm', '--prefix', 'mcp-server', 'run', 'build') },
    @{ Id = 'edr-live-gate'; Stage = 'full'; Argv = $py + @('-c', $liveGate) },
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
    $receipt = "$receipts/edr-D6-$($step.Id).txt"
    $argv = $step.Argv
    & rtk proxy @argv *> $receipt
    $code = $LASTEXITCODE
    Write-Output ("{0} stage={1} exit={2} receipt={3}" -f $step.Id, $step.Stage, $code, $receipt)
    Get-Content $receipt | Select-Object -Last 6
    if ($code -eq 0 -and $step.Id -eq 'identity-after') {
        $before = Get-TestedState "$receipts/edr-D6-identity-before.txt"
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
