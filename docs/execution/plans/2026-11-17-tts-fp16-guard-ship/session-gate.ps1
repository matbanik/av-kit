# Session 74 fresh-full gate (task H1-2; implementation-plan.md §Session gate).
# The shape of docs/execution/plans/2026-11-17-test-run-reliability/session-gate.ps1, with this
# plan's steps: identity, then the static checks (the task contract, scope-paths, line-endings,
# home-path, the red-check, eol-check, smoke-check and home-redact selftests, py-format on the
# changed and new Python and this plan folder's Python, py-lint with the D6 argv plus this plan
# folder's Python, py-types), then the targeted checks (meu-144-unit, meu-144-integration with
# the four pin files, guard-check on models-copy, green-source), then host-load through
# host-load.ps1 (Session 81 RULE-2, this session's 50 % bar; still above it after 20 minutes is
# S15 and fails the gate), then the fresh full checks (py-tests, state-render,
# issues-render-check, canon-vitest), then the identity again.
# Runs from the repository root (P:/av-kit, main only per AGENTS.md §Commits). One receipt per
# id under C:/Temp/av-kit/tts-fp16-guard-ship, named ff-D6-<id>.txt.
# Fail-fast: the first non-zero step stops the gate and every later step is printed as not_run.
# The gate also fails when tested_state differs between its start and its end (an input changed
# while it ran). Read-only apart from the receipts, the temp folder and guard-check's JSON; all
# are outside the checkout. Nothing here reaches the network, YouTube or Hugging Face, no step
# dispatches a model, and no step starts or stops a backend.
# Exit = the first failing step's code.
# py-tests runs the D6 argv (-x). If it stops on a failure, it runs the D6 argv again without -x
# and passes only when its failing ids are a subset of the ids ff-base-py.txt shows failing
# (none: 3087 passed at row 0).
# Skipped, per the plan: ui-*, mcp-* and openapi (H1-4 checks that every ui/, mcp-server/,
# tools/, packages/api/ and packages/core/ file keeps its baseline-skip-hashes.json hash, and
# none was added or removed; S14), and the packaged smokes (rows 7 and 8 ran them on the final
# phase_guard.py and adapter.py; green-source compares both with ff-green-source-hashes.json).
# Each is printed with its reason and runs nothing.
$ErrorActionPreference = 'Continue'
$root = (git rev-parse --show-toplevel).Trim()
Set-Location $root
$plan = 'docs/execution/plans/2026-11-17-tts-fp16-guard-ship'
$receipts = 'C:/Temp/av-kit/tts-fp16-guard-ship'
# lint_task_contract.py recognises the instantiated receipt paths only through RECEIPTS_DIR and
# fails closed (exit 3) when it is unset, which no user or machine scope sets on this host.
$env:RECEIPTS_DIR = 'C:/Temp/av-kit'
$env:PYTHONIOENCODING = 'utf-8'
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:ELECTRON_RUN_AS_NODE = $null
# RC1 ECN-2: keep the temp dirs away from the home folder, as row 0 ran the base suites.
$tmp = 'C:\Temp\av-kit\tts-fp16-guard-ship\tmp'
New-Item -ItemType Directory -Force -Path $tmp | Out-Null
$env:TMP = $tmp
$env:TEMP = $tmp
$base = (Get-Content "$plan/baseline.sha").Trim()

# §Files Modified, this plan folder, the closeout artifacts (the handoffs and reviews under
# .agent/context/handoffs/2026-11-17-tts-fp16-guard-ship-*, the reflection, metrics.md and
# current-focus.md) and the paths baseline-dirty.txt already held. The sibling sessions' files
# are skipped the way identity.py skips them (D-1140): an untracked file in a plan folder
# docs/execution/plans/2026-11-1[5-7]-<slug>/ absent from HEAD, or an untracked handoff of the
# four sibling slugs. Anything else changed, HEAD moving, a "Read, never changed" file moving
# from baseline-scope.json, or a baseline-dirty path outside this scope moving from
# baseline-dirty-hashes.json fails the step.
$scopePaths = @"
import hashlib, json, pathlib, re, subprocess, sys
plan = '$plan'
mine = {
    'packages/infrastructure/src/avkit_infra/tts/phase_guard.py',
    'packages/infrastructure/src/avkit_infra/tts/adapter.py',
    'tests/tts_onnx_synthetic.py',
    'tests/unit/test_tts_phase_guard.py',
    'tests/integration/test_tts_phase_guard_load.py',
    'docs/build-plan/03-service-layer.md',
    'docs/build-plan/build-priority-matrix.md',
    '.agent/context/meu-status.yaml',
    '.agent/context/meu-registry.md',
    'docs/BUILD_PLAN.md',
    '.agent/context/known-issues.yaml',
    '.agent/context/known-issues.md',
    '.agent/context/grouping/2026-11-17-value-triage-session-grouping.md',
    'docs/execution/metrics.md',
    '.agent/context/current-focus.md',
}
scope = json.loads(pathlib.Path(plan + '/baseline-scope.json').read_text(encoding='utf-8'))
read_only = tuple(p for p in scope if p not in mine)
prefixes = (plan + '/', '.agent/context/handoffs/2026-11-17-tts-fp16-guard-ship-', 'docs/execution/reflections/2026-11-17-tts-fp16-guard-ship-')
other_plan_re = re.compile(r'^docs/execution/plans/2026-11-1[5-7]-[^/]+/')
other_handoff_re = re.compile(r'^\.agent/context/handoffs/2026-11-1[5-7]-(e2e-pointer-flakes|mcp-audit-refresh|ui-small-fixes|video-tail-frame)-[^/]+$')
def git(*args):
    return subprocess.run(['git', *args], capture_output=True, check=True).stdout.decode('utf-8')
head_plans = {n for n in git('ls-tree', '--name-only', 'HEAD', 'docs/execution/plans/').splitlines() if n}
def other_plan(p):
    if other_handoff_re.match(p):
        return True
    folder = '/'.join(p.split('/')[:4])
    return bool(other_plan_re.match(p)) and not p.startswith(plan + '/') and folder not in head_plans
allowed = set(mine)
for line in pathlib.Path(plan + '/baseline-dirty.txt').read_text(encoding='utf-8').splitlines():
    if not line or line.startswith('## foreign '):
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

# green-source: phase_guard.py and adapter.py equal the hashes row 7 recorded before its build,
# so the packaged smokes of rows 7 and 8 ran on the files this gate tests.
$greenSource = @"
import hashlib, json, pathlib, sys
want = json.loads(pathlib.Path('$receipts/ff-green-source-hashes.json').read_text(encoding='utf-8'))
now = {p: hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest() for p in want}
for p in sorted(want):
    print(p, 'row-7 sha256', want[p], 'now', now[p], 'same', now[p] == want[p])
ok = len(want) == 2 and now == want
print('green-source:', 'same as row 7' if ok else 'CHANGED since row 7')
sys.exit(0 if ok else 1)
"@

# py-tests: the D6 argv; on a failure, the argv again without -x, passing only when every failing
# id is one that ff-base-py.txt shows failing.
$pyTests = @"
import re, subprocess, sys
argv = ['uv', 'run', '--no-sync', 'pytest', 'tests/', '-x', '--tb=short', '-q']
first = subprocess.run(argv)
if first.returncode == 0:
    print('py-tests: D6 argv exit 0')
    sys.exit(0)
def failing(text):
    return {m.group(1) for m in re.finditer(r'^(?:FAILED|ERROR) (\S+)', text, re.M)}
base = failing(open('$receipts/ff-base-py.txt', encoding='utf-8', errors='replace').read())
second = subprocess.run([a for a in argv if a != '-x'], capture_output=True, text=True, encoding='utf-8', errors='replace')
sys.stdout.write(second.stdout[-4000:])
now = failing(second.stdout)
new = sorted(now - base)
print('py-tests: D6 argv exit', first.returncode, '; rerun without -x exit', second.returncode, '; failing', sorted(now), '; base failing', sorted(base), '; not in base', new)
sys.exit(0 if second.returncode in (0, 1) and not new and (second.returncode == 0 or now) else 1)
"@

Write-Output 'baseline py failures excused: [] (ff-base-py.txt shows 3087 passed and no failure)'

$skipped = @(
    @{ Id = 'ui-types/ui-lint/ui-tests/ui-build/ui-electron'; Stage = 'full'; Reason = 'every ui/ file keeps its baseline-skip-hashes.json hash and none was added or removed (H1-4); no UI file changes (S14); canon-vitest runs the two suites that read the changed registers' },
    @{ Id = 'mcp-types/mcp-build/mcp-tests/mcp-audit'; Stage = 'full'; Reason = 'every mcp-server/ file keeps its baseline-skip-hashes.json hash (H1-4); no MCP tool changes (S14)' },
    @{ Id = 'openapi'; Stage = 'full'; Reason = 'every packages/api/ and packages/core/ file keeps its baseline-skip-hashes.json hash (H1-4); no route or schema changes (S14)' },
    @{ Id = 'packaged-smokes'; Stage = 'runtime'; Reason = 'rows 7 and 8 ran them on the final phase_guard.py and adapter.py; green-source compares both with ff-green-source-hashes.json and scope-paths with identity shows nothing else moved' }
)
foreach ($s in $skipped) {
    Write-Output ("{0} stage={1} skipped reason={2}" -f $s.Id, $s.Stage, $s.Reason)
}

$py = @('uv', 'run', '--no-sync', 'python')
$pytest = @('uv', 'run', '--no-sync', 'pytest', '-q', '--tb=short', '-p', 'no:cacheprovider')
$identity = $py + @("$plan/identity.py")
$planPy = @(Get-ChildItem -Path $plan -Filter '*.py' | Sort-Object Name | ForEach-Object { "$plan/$($_.Name)" })
$changedPy = @(
    'packages/infrastructure/src/avkit_infra/tts/phase_guard.py',
    'packages/infrastructure/src/avkit_infra/tts/adapter.py',
    'tests/tts_onnx_synthetic.py',
    'tests/unit/test_tts_phase_guard.py',
    'tests/integration/test_tts_phase_guard_load.py'
)
$pins = @(
    'tests/integration/test_tts_device_resolution.py',
    'tests/integration/test_tts_models.py',
    'tests/integration/test_tts_no_torch.py',
    'tests/e2e/test_api_model_load_keeps.py'
)
$steps = @(
    @{ Id = 'identity-before'; Stage = 'identity'; Argv = $identity },
    @{ Id = 'task-contract'; Stage = 'static'; Argv = $py + @('tools/lint_task_contract.py', '--allowed-builder-classes', 'avkit_builder,avkit_coordinator,avkit_verifier', '--task', "$plan/task.md") },
    @{ Id = 'scope-paths'; Stage = 'static'; Argv = $py + @('-c', $scopePaths) },
    @{ Id = 'line-endings'; Stage = 'static'; Argv = $py + @("$plan/eol-check.py") },
    @{ Id = 'home-path'; Stage = 'static'; Argv = $py + @('tools/check_home_path.py') },
    @{ Id = 'red-check-selftest'; Stage = 'static'; Argv = $py + @("$plan/red-check.py", '--selftest') },
    @{ Id = 'eol-check-selftest'; Stage = 'static'; Argv = $py + @("$plan/eol-check.py", '--selftest') },
    @{ Id = 'smoke-check-selftest'; Stage = 'static'; Argv = $py + @("$plan/smoke-check.py", '--selftest') },
    @{ Id = 'home-redact-selftest'; Stage = 'static'; Argv = $py + @("$plan/home-redact.py", '--selftest') },
    @{ Id = 'py-format'; Stage = 'static'; Argv = @('uv', 'run', '--no-sync', 'ruff', 'format', '--check') + $changedPy + $planPy },
    @{ Id = 'py-lint'; Stage = 'static'; Argv = @('uv', 'run', '--no-sync', 'ruff', 'check', 'packages/', 'tests/') + $planPy },
    @{ Id = 'py-types'; Stage = 'static'; Argv = @('uv', 'run', '--no-sync', 'pyright', 'packages/') },
    @{ Id = 'meu-144-unit'; Stage = 'targeted'; Argv = $pytest + @('tests/unit/test_tts_phase_guard.py') },
    @{ Id = 'meu-144-integration'; Stage = 'targeted'; Argv = $pytest + @('tests/integration/test_tts_phase_guard_load.py') + $pins },
    @{ Id = 'guard-check'; Stage = 'targeted'; Argv = $py + @("$plan/guard-check.py", '--models', "$receipts/models-copy", '--out', "$receipts/ff-D6-guard-check.json") },
    @{ Id = 'green-source'; Stage = 'targeted'; Argv = $py + @('-c', $greenSource) },
    @{ Id = 'host-load'; Stage = 'host'; Argv = @('pwsh', '-NoProfile', '-File', "$plan/host-load.ps1") },
    @{ Id = 'py-tests'; Stage = 'full'; Argv = $py + @('-c', $pyTests) },
    @{ Id = 'state-render'; Stage = 'full'; Argv = $py + @('tools/meu_status.py', 'render', '--check') },
    @{ Id = 'issues-render-check'; Stage = 'full'; Argv = $py + @('tools/issue_triage.py', 'render', '--check') },
    @{ Id = 'canon-vitest'; Stage = 'full'; Cwd = 'ui'; Argv = @('npm', 'run', 'test', '--', 'tests/unit/layout-canon.test.ts', 'tests/unit/queue-canon.test.ts') },
    @{ Id = 'identity-after'; Stage = 'identity'; Argv = $identity }
)

function Get-TestedState([string]$Receipt) {
    $line = Select-String -Path $Receipt -Pattern '^tested_state ' | Select-Object -Last 1
    if ($null -eq $line) { return $null }
    return $line.Line.Substring('tested_state '.Length).Trim()
}

for ($i = 0; $i -lt $steps.Count; $i++) {
    $step = $steps[$i]
    $receipt = "$receipts/ff-D6-$($step.Id).txt"
    $argv = $step.Argv
    if ($step.ContainsKey('Cwd')) { Push-Location (Join-Path $root $step.Cwd) }
    & rtk proxy @argv *> $receipt
    $code = $LASTEXITCODE
    if ($step.ContainsKey('Cwd')) { Pop-Location }
    Write-Output ("{0} stage={1} exit={2} receipt={3}" -f $step.Id, $step.Stage, $code, $receipt)
    Get-Content $receipt | Select-Object -Last 6
    if ($code -eq 0 -and $step.Id -eq 'identity-after') {
        $before = Get-TestedState "$receipts/ff-D6-identity-before.txt"
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
