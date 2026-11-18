# Session 92 fresh-full gate (task H1-2; implementation-plan.md "Session gate (H1-2)").
# The shape of docs/execution/plans/2026-11-17-queue-convert-fixes/session-gate.ps1, with this
# plan's steps: identity, then the static checks (mcp-types, the task contract, scope-paths,
# line-endings, home-path, the red-check, eol-check, desc-check, eval-rerun and baseline-diff
# selftests, py-format and py-lint on this plan folder's Python, desc-check-syntax), then the
# targeted checks (mcp-unit, desc-check, baseline-diff), then host-load (Session 81 RULE-2,
# through host-load.ps1, bar 50 %), then the fresh full checks (mcp-build, mcp-tests,
# issues-render-check, state-render), then the identity again.
# Runs from the repository root (P:/av-kit, main only per AGENTS.md "Commits"). One receipt per
# id under C:/Temp/av-kit/mcp-audit-refresh, named mar-D6-<id>.txt; every step's exit code is
# the code of the command that wrote that receipt, and the gate reads only those receipts.
# Fail-fast: the first non-zero step stops the gate and every later step is printed as not_run.
# The gate also fails when tested_state differs between its start and its end (an input changed
# while it ran). Read-only apart from the receipts, the temp folder and mcp-server/dist
# (mcp-build; ignored). Nothing here reaches the network or YouTube, no step starts the app or
# an MCP backend, no step reads app data, and no step dispatches a model.
# Exit = the first failing step's code.
# mcp-tests excuses nothing: row 0's mar-base-mcp.txt shows Test Files 36 passed (36), Tests
# 535 passed (535) and no failure. mcp-unit and mcp-tests pass only with a Tests passed line and
# no failed, skipped or todo test; mcp-unit must also run all five of its files.
# desc-check reads mcp-server/dist as rows 4, 5 and 7 built it from the current sources;
# mcp-build then rebuilds it fresh (dist is ignored and is not a tested_state input).
# baseline-diff checks the committed baseline against its row-0 copy with the five pending
# keys and HEAD, as row 7 did; when C:/Temp/av-kit/mcp-audit-refresh/mar-d1161.txt exists it
# instead checks the baseline, the report and coverage.test.ts byte for byte against their
# row-0 copies (D-1161).
# Skipped, per the plan: py-tests, py-types, ui-types, ui-lint, ui-tests, ui-build, ui-electron
# and openapi (H1-4 checks that every packages/, tools/, ui/ and tests/ file keeps its
# baseline-skip-hashes.json hash, and none was added or removed), and mcp-audit (run
# authoritatively at row 7 on this tree; a second network run adds nothing). Each is printed
# with its reason and runs nothing.
$ErrorActionPreference = 'Continue'
$root = (git rev-parse --show-toplevel).Trim()
Set-Location $root
$plan = 'docs/execution/plans/2026-11-17-mcp-audit-refresh'
$receipts = 'C:/Temp/av-kit/mcp-audit-refresh'
# lint_task_contract.py recognises the instantiated receipt paths only through RECEIPTS_DIR and
# fails closed (exit 3) when it is unset, which no user or machine scope sets on this host.
$env:RECEIPTS_DIR = 'C:/Temp/av-kit'
$env:PYTHONIOENCODING = 'utf-8'
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:ELECTRON_RUN_AS_NODE = $null
# RC1 ECN-2: keep the temp dirs away from the home folder, as row 0 ran the base suites.
$tmp = 'C:\Temp\av-kit\mcp-audit-refresh\tmp'
New-Item -ItemType Directory -Force -Path $tmp | Out-Null
$env:TMP = $tmp
$env:TEMP = $tmp
$base = (Get-Content "$plan/baseline.sha").Trim()

# Files Modified, this plan folder, the closeout artifacts (the handoffs and reviews under
# .agent/context/handoffs/2026-11-17-mcp-audit-refresh-*, the reflection, metrics.md and
# current-focus.md) and the paths baseline-dirty.txt already held. Foreign, never S4 here (the
# executor brief): the sibling Sessions 91, 93 and 94 plan folders and plan-review handoffs, and
# the six coordinator-owned paths of D-1185, each bound to the SHA-256 the coordinator's restamp
# left (C:/Temp/av-kit/mcp-audit-refresh/mar-coordinator-owned.txt). A sibling file's drift from
# baseline-dirty-hashes.json is printed, not failed. Anything else changed, HEAD moving, a
# "Read, never changed" file moving from baseline-scope.json, a D-1185 path moving from its
# restamp hash, or a non-sibling baseline-dirty path moving is S4.
$scopePaths = @"
import hashlib, json, pathlib, re, subprocess, sys
plan = '$plan'
mine = {
    'mcp-server/scripts/audit/network-proof.ts',
    'mcp-server/scripts/audit/run.ts',
    'mcp-server/tests/audit/network-proof.test.ts',
    '.agent/workflows/mcp-audit.md',
    'mcp-server/tests/capture-description.test.ts',
    'mcp-server/src/toolsets/capture.ts',
    'mcp-server/src/toolsets/registry.ts',
    'docs/build-plan/05-mcp-server.md',
    'mcp-server/tests/audit/coverage.test.ts',
    '.agent/skills/mcp-tool-audit/resources/baseline-snapshot.json',
    '.agent/context/MCP/mcp-tool-audit-report.md',
    '.agent/context/known-issues.yaml',
    '.agent/context/known-issues.md',
    '.agent/context/grouping/2026-11-17-value-triage-session-grouping.md',
    '.agent/context/handoffs/2026-11-17-mcp-audit-refresh-handoff.md',
    'docs/execution/metrics.md',
    '.agent/context/current-focus.md',
}
coordinator = {
    '.agent/model-registry.local.json': '866f16205e987a57dd5cd670c1a6acef695058669ba00cda0856e103cd393563',
    '.claude/agents/av-kit-builder.md': '62dd4721bec60f4e8a05f7bb096bc2f4ddafc1f06a1dc3c88ad859fb367daaa8',
    '.claude/agents/av-kit-peer-reviewer.md': 'eacc56753fcea2eb187eb98ff32204c5032b48e0b3dc49cff84d0a92cd7d7260',
    '.claude/agents/av-kit-verifier.md': '3250a8cc0203f78a7b2a82bee2bba71cd81044aaa359bdfe8b88026db2b46331',
    '.cursor/agents/av-kit-builder.md': '99a0eb3b5daaf7755fd7be23fd5bcfd9e488e73ec078dabf2d2c1651b73f08c0',
    '.cursor/agents/av-kit-verifier.md': 'f3bee961a77faf34c3ce056d6b028d0d9734f1602b9d940738269e3544b2ff25',
}
siblings = ('e2e-pointer-flakes', 'video-tail-frame', 'ui-small-fixes')
sibling_prefixes = tuple(
    p
    for s in siblings
    for p in ('docs/execution/plans/2026-11-17-' + s + '/', '.agent/context/handoffs/2026-11-17-' + s + '-plan-critical-review.md')
)
scope = json.loads(pathlib.Path(plan + '/baseline-scope.json').read_text(encoding='utf-8'))
read_only = tuple(p for p in scope if p not in mine)
prefixes = (plan + '/', '.agent/context/handoffs/2026-11-17-mcp-audit-refresh-', 'docs/execution/reflections/2026-11-17-mcp-audit-refresh-')
other_plan_re = re.compile(r'^docs/execution/plans/2026-11-1[5-7]-[^/]+/')
def git(*args):
    return subprocess.run(['git', *args], capture_output=True, check=True).stdout.decode('utf-8')
head_plans = {n for n in git('ls-tree', '--name-only', 'HEAD', 'docs/execution/plans/').splitlines() if n}
def other_plan(p):
    folder = '/'.join(p.split('/')[:4])
    return bool(other_plan_re.match(p)) and not p.startswith(plan + '/') and folder not in head_plans
allowed = set(mine) | set(coordinator)
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
coordinator_moved = [p for p, h in sorted(coordinator.items()) if sha(p) != h]
dirty_hashes = json.loads(pathlib.Path(plan + '/baseline-dirty-hashes.json').read_text(encoding='utf-8'))
def drift(p, h):
    return (sha(p) if pathlib.Path(p).exists() else 'deleted') != h
dirty_moved = [p for p, h in sorted(dirty_hashes.items()) if not p.startswith(sibling_prefixes) and drift(p, h)]
sibling_moved = [p for p, h in sorted(dirty_hashes.items()) if p.startswith(sibling_prefixes) and drift(p, h)]
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
foreign = sorted({p for p in changed if p.startswith(sibling_prefixes) and p not in others})
extra = sorted({p for p in changed if p not in allowed and not p.startswith(prefixes) and p not in others and p not in foreign})
print('changed paths:', len(changed), 'outside scope:', extra, 'other sessions plan files skipped:', len(others), 'sibling handoffs skipped:', foreign)
print('read-never-changed files:', len(read_only), 'mismatch:', read_only_moved, 'baseline-dirty hash mismatch:', dirty_moved)
print('coordinator-owned (D-1185):', len(coordinator), 'changed:', sorted(p for p in coordinator if p in changed), 'restamp hash mismatch:', coordinator_moved)
print('sibling baseline-dirty drift (foreign, printed only):', sibling_moved)
print('head:', head, 'head moved (S4):', moved)
sys.exit(1 if extra or moved or read_only_moved or dirty_moved or coordinator_moved else 0)
"@

# D-1161 only: the byte check of the three restored files against their row-0 copies.
$d1161Bytes = @"
import hashlib, pathlib, sys
copies = pathlib.Path('C:/Temp/av-kit/mcp-audit-refresh/baseline-copies')
bad = []
for p in ('.agent/skills/mcp-tool-audit/resources/baseline-snapshot.json', '.agent/context/MCP/mcp-tool-audit-report.md', 'mcp-server/tests/audit/coverage.test.ts'):
    same = pathlib.Path(p).read_bytes() == (copies / p).read_bytes()
    print(p, 'row-0 bytes:', same)
    if not same:
        bad.append(p)
print('d1161 byte check:', 'ok' if not bad else 'failed ' + str(bad))
sys.exit(1 if bad else 0)
"@

$pending = @('avkit_convert.probe', 'avkit_capture.crop', 'avkit_capture.frames', 'avkit_capture.sheet', 'avkit_capture.export')
$skipped = @(
    @{ Id = 'py-tests'; Stage = 'full'; Reason = 'every packages/ and tests/ file keeps its baseline-skip-hashes.json hash (H1-4); no Python file changes (S12)' },
    @{ Id = 'py-types'; Stage = 'static'; Reason = 'every packages/ file keeps its baseline-skip-hashes.json hash (H1-4); no Python file changes (S12)' },
    @{ Id = 'ui-types/ui-lint/ui-tests/ui-build/ui-electron'; Stage = 'full'; Reason = 'every ui/ file keeps its baseline-skip-hashes.json hash (H1-4); no UI file changes (S12)' },
    @{ Id = 'openapi'; Stage = 'full'; Reason = 'every packages/api/ file keeps its baseline-skip-hashes.json hash (H1-4); no route or schema changes (S12)' },
    @{ Id = 'mcp-audit'; Stage = 'runtime'; Reason = 'run authoritatively at row 7 on this tree (mar-r7-audit.txt); a second network run adds nothing' }
)
Write-Output 'baseline mcp failures excused: [] (mcp-tests excuses nothing; mar-base-mcp.txt shows Tests 535 passed (535) and no failure)'
foreach ($s in $skipped) {
    Write-Output ("{0} stage={1} skipped reason={2}" -f $s.Id, $s.Stage, $s.Reason)
}

$py = @('uv', 'run', '--no-sync', 'python')
$identity = $py + @("$plan/identity.py")
$vitest = @('npx', 'vitest', 'run')
$planPy = @(Get-ChildItem -Path $plan -Filter '*.py' | Sort-Object Name | ForEach-Object { "$plan/$($_.Name)" })
$unit = @(
    'tests/audit/network-proof.test.ts', 'tests/capture-description.test.ts', 'tests/audit/coverage.test.ts',
    'tests/audit/docs.test.ts', 'tests/audit/run-cli.test.ts'
)
if (Test-Path 'C:/Temp/av-kit/mcp-audit-refresh/mar-d1161.txt') {
    $baselineArgv = $py + @('-c', $d1161Bytes)
} else {
    $baselineArgv = $py + @(
        "$plan/baseline-diff.py", 'baseline',
        '--old', 'C:/Temp/av-kit/mcp-audit-refresh/baseline-copies/.agent/skills/mcp-tool-audit/resources/baseline-snapshot.json',
        '--new', '.agent/skills/mcp-tool-audit/resources/baseline-snapshot.json',
        '--pending') + $pending + @('--head', $base)
}
$steps = @(
    @{ Id = 'identity-before'; Stage = 'identity'; Argv = $identity },
    @{ Id = 'mcp-types'; Stage = 'static'; Argv = @('npm', '--prefix', 'mcp-server', 'run', 'typecheck') },
    @{ Id = 'task-contract'; Stage = 'static'; Argv = $py + @('tools/lint_task_contract.py', '--allowed-builder-classes', 'avkit_builder,avkit_coordinator,avkit_verifier', '--task', "$plan/task.md") },
    @{ Id = 'scope-paths'; Stage = 'static'; Argv = $py + @('-c', $scopePaths) },
    @{ Id = 'line-endings'; Stage = 'static'; Argv = $py + @("$plan/eol-check.py") },
    @{ Id = 'home-path'; Stage = 'static'; Argv = $py + @('tools/check_home_path.py') },
    @{ Id = 'red-check-selftest'; Stage = 'static'; Argv = $py + @("$plan/red-check.py", '--selftest') },
    @{ Id = 'eol-check-selftest'; Stage = 'static'; Argv = $py + @("$plan/eol-check.py", '--selftest') },
    @{ Id = 'desc-check-selftest'; Stage = 'static'; Argv = @('node', "$plan/desc-check.mjs", '--selftest') },
    @{ Id = 'eval-rerun-selftest'; Stage = 'static'; Argv = $py + @("$plan/eval-rerun.py", '--selftest') },
    @{ Id = 'baseline-diff-selftest'; Stage = 'static'; Argv = $py + @("$plan/baseline-diff.py", '--selftest') },
    @{ Id = 'py-format'; Stage = 'static'; Argv = @('uv', 'run', '--no-sync', 'ruff', 'format', '--check') + $planPy },
    @{ Id = 'py-lint'; Stage = 'static'; Argv = @('uv', 'run', '--no-sync', 'ruff', 'check') + $planPy },
    @{ Id = 'desc-check-syntax'; Stage = 'static'; Argv = @('node', '--check', "$plan/desc-check.mjs") },
    @{ Id = 'mcp-unit'; Stage = 'targeted'; Cwd = 'mcp-server'; Argv = $vitest + $unit; Clean = $true; Files = $unit.Count },
    @{ Id = 'desc-check'; Stage = 'targeted'; Argv = @('node', "$plan/desc-check.mjs", '--baseline', 'C:/Temp/av-kit/mcp-audit-refresh/mar-desc-record.json', '--expected', "$plan/capture-description.expected.txt") },
    @{ Id = 'baseline-diff'; Stage = 'targeted'; Argv = $baselineArgv },
    @{ Id = 'host-load'; Stage = 'host'; Argv = @('pwsh', '-NoProfile', '-File', "$plan/host-load.ps1") },
    @{ Id = 'mcp-build'; Stage = 'full'; Argv = @('npm', '--prefix', 'mcp-server', 'run', 'build') },
    @{ Id = 'mcp-tests'; Stage = 'full'; Cwd = 'mcp-server'; Argv = $vitest; Clean = $true },
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
    $receipt = "$receipts/mar-D6-$($step.Id).txt"
    $argv = $step.Argv
    if ($step.ContainsKey('Cwd')) { Push-Location (Join-Path $root $step.Cwd) }
    try {
        & rtk proxy @argv *> $receipt
        $code = $LASTEXITCODE
    } finally {
        if ($step.ContainsKey('Cwd')) { Pop-Location }
    }
    Write-Output ("{0} stage={1} exit={2} receipt={3}" -f $step.Id, $step.Stage, $code, $receipt)
    Get-Content $receipt | Select-Object -Last 6
    if ($code -eq 0 -and $step.ContainsKey('Clean')) {
        # A Vitest run passes only with a Tests passed line and no failed, skipped or todo test
        # (S5); a file list that selects fewer files than planned must not pass quietly.
        $passed = Select-String -Path $receipt -Pattern '^\s+Tests\s+[0-9]+ passed \(' -Quiet
        $bad = Select-String -Path $receipt -Pattern '[0-9]+ (failed|skipped|todo)' -Quiet
        $filesOk = $true
        if ($step.ContainsKey('Files')) {
            $want = $step.Files
            $filesOk = Select-String -Path $receipt -Pattern "^\s+Test Files\s+$want passed \($want\)" -Quiet
        }
        Write-Output ("{0}: passed line={1} failed, skipped or todo={2} files ok={3}" -f $step.Id, $passed, $bad, $filesOk)
        if (-not $passed -or $bad -or -not $filesOk) { $code = 1 }
    }
    if ($code -eq 0 -and $step.Id -eq 'identity-after') {
        $before = Get-TestedState "$receipts/mar-D6-identity-before.txt"
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
