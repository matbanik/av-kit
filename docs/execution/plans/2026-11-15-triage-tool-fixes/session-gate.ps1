# Triage-tool-fixes fresh-full gate (task H1-2; implementation-plan.md §Session gate).
# The shape of docs/execution/plans/2026-11-15-closeout-record-once/session-gate.ps1, with this
# plan's scope (Files Modified, the plan folder, the closeout artifacts and the paths
# baseline-dirty.txt held) and steps: py-lint, tools-lint (every (path, code) pair must be in
# row 0's ttf-ruff-base.txt), py-format on the new test file, the task contract, scope-paths,
# line-endings (each Files Modified file keeps its row-0 kind), doc-check and red-check's
# selftest; then the triage tests (AC-1 to AC-11), the register callers that import
# issue_triage.model, the framework adoption test and the live smoke (AC-12, AC-13: the real
# register's hash before and after verify --deep); then the full Python suite, the state render
# and the issues render check (AC-14).
# Runs from the repository root (P:/av-kit, main only per AGENTS.md §Commits) in stage order:
# input identity, then every static check, then the targeted checks, then the full suites, then
# the input identity again. One receipt per id under C:/Temp/av-kit/triage-tool-fixes, named
# ttf-D6-<id>.txt, and beside it ttf-D6-<id>.txt.exit with the step's own exit code (no step
# here is MustFail; the Red runs are rows 1, 3, 5 and 7, not gate steps).
# Fail-fast: the first non-zero step stops the gate and every later step is printed as not_run.
# The gate also fails when tested_state differs between its start and its end (an input changed
# while it ran). Read-only apart from the receipts and the temp folder, which sit outside the
# repository. Nothing here reaches the network or YouTube, and no step dispatches a model.
# Every step runs the changed tools/issue_triage* of the working tree.
# Exit = the first failing step's code.
# py-tests runs the whole suite (no -x) and keeps Session 49b's baseline rule: pytest exit 1
# passes only when every FAILED id also FAILED in row 0's ttf-base-py.txt, and nothing ERRORs.
# Skipped, per the plan: py-types (pyright covers packages/ only, and nothing there changes),
# ui-* (nothing under ui/ changes), mcp-* (no MCP change; the MCP Python tests run inside
# py-tests), e2e (no renderer or launch change), openapi (no packages/api change; H1-4) and
# build-record (no build). Each is printed with its reason and runs nothing.
$ErrorActionPreference = 'Continue'
$root = (git rev-parse --show-toplevel).Trim()
Set-Location $root
$plan = 'docs/execution/plans/2026-11-15-triage-tool-fixes'
$receipts = 'C:/Temp/av-kit/triage-tool-fixes'
# lint_task_contract.py recognises the instantiated receipt paths only through RECEIPTS_DIR and
# fails closed (exit 3) when it is unset, which no user or machine scope sets on this host.
$env:RECEIPTS_DIR = 'C:/Temp/av-kit'
$env:PYTHONIOENCODING = 'utf-8'
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:ELECTRON_RUN_AS_NODE = $null
# RC1 ECN-2: keep the temp dirs away from the home folder, as row 0 ran the base suite.
$tmp = 'C:/Temp/av-kit/triage-tool-fixes/tmp'
New-Item -ItemType Directory -Force -Path $tmp | Out-Null
$env:TMP = $tmp
$env:TEMP = $tmp

# tools-lint: ruff on the four tool files; every (path, code) pair it reports must be one of
# row 0's ttf-ruff-base.txt pairs (I001 in issue_triage.py; E501 and I001 in verify.py). Lines
# move with the fix, so only the pair is compared.
$toolsLint = @"
import re, subprocess, sys
files = ['tools/issue_triage.py', 'tools/issue_triage/verify.py', 'tools/issue_triage/discover.py', 'tools/issue_triage/triage.py']
pat = re.compile(r'^(\S+?):\d+:\d+: ([A-Z]+\d+) ')
def pairs(text):
    return {(m.group(1).replace(chr(92), '/'), m.group(2)) for m in map(pat.match, text.splitlines()) if m}
base = pairs(open('$receipts/ttf-ruff-base.txt', encoding='utf-8', errors='replace').read())
run = subprocess.run(['ruff', 'check', '--output-format', 'concise', *files], capture_output=True, text=True, encoding='utf-8', errors='replace')
print(run.stdout.strip())
now = pairs(run.stdout)
new = sorted(now - base)
print('base pairs:', sorted(base))
print('current pairs:', sorted(now))
print('new pairs (not in ttf-ruff-base.txt):', new)
sys.exit(1 if new or not base else 0)
"@

# Files Modified, the plan folder, the closeout artifacts and the paths baseline-dirty.txt
# already held. Anything else changed, HEAD moving, or a baseline-dirty path outside this scope
# whose content moved from baseline-dirty-hashes.json is S4. Other sessions' new plan folders
# (untracked, under docs/execution/plans/2026-11-15-<other slug>/, absent from HEAD) are
# theirs, as identity.py's OTHER_PLAN_PREFIX rule treats them.
$scopePaths = @"
import hashlib, json, pathlib, subprocess, sys
plan = '$plan'
mine = set(json.loads(pathlib.Path(plan + '/baseline-scope.json').read_text(encoding='utf-8')))
mine |= {'docs/execution/metrics.md', '.agent/context/current-focus.md'}
prefixes = (plan + '/', '.agent/context/handoffs/2026-11-15-triage-tool-fixes-', 'docs/execution/reflections/2026-11-15-triage-tool-fixes-')
def in_scope(path):
    return path in mine or path.startswith(prefixes)
allowed = set(mine)
for line in pathlib.Path(plan + '/baseline-dirty.txt').read_text(encoding='utf-8-sig').splitlines():
    if not line:
        continue
    path = line[3:]
    if not path or ' -> ' in path or path.startswith('"'):
        print('baseline-dirty.txt: unreadable line', repr(line))
        sys.exit(2)
    allowed.add(path)
moved_content = []
for path, recorded in json.loads(pathlib.Path(plan + '/baseline-dirty-hashes.json').read_text(encoding='utf-8')).items():
    if in_scope(path):
        continue
    target = pathlib.Path(path)
    got = hashlib.sha256(target.read_bytes()).hexdigest() if target.is_file() else 'absent'
    if got != recorded:
        moved_content.append(path)
def paths(*args):
    raw = subprocess.run(['git', *args], capture_output=True, check=True).stdout.decode('utf-8')
    return [p for p in raw.split(chr(0)) if p]
head = subprocess.run(['git', 'rev-parse', 'HEAD'], capture_output=True, text=True, check=True).stdout.strip()
base = pathlib.Path(plan + '/baseline.sha').read_text(encoding='utf-8').strip()
moved = head != base
head_folders = {'/'.join(p.split('/')[:4]) for p in paths('ls-tree', '-r', '--name-only', '-z', 'HEAD', 'docs/execution/plans/')}
untracked = paths('ls-files', '--others', '--exclude-standard', '-z')
def other_plan(p):
    folder = '/'.join(p.split('/')[:4])
    return p.startswith('docs/execution/plans/2026-11-15-') and not p.startswith(plan + '/') and folder != p and folder not in head_folders and p in untracked
out = paths('diff', '--no-renames', '--name-only', '-z', head) + untracked
extra = sorted({p for p in out if p not in allowed and not in_scope(p) and not other_plan(p)})
print('changed paths:', len(set(out)), 'outside scope:', extra, 'baseline-dirty content moved:', moved_content, 'head:', head, 'head moved (S4):', moved)
sys.exit(1 if extra or moved or moved_content else 0)
"@

# line-endings: each Files Modified file keeps its row-0 kind (the plan's Files Modified table;
# row 0's ttf-row0-eol.txt measured the same kinds). Python bytes only.
$lineEndings = @"
import pathlib, sys
crlf = bytes([13, 10])
kinds = {
    'tools/issue_triage.py': 'LF',
    'tools/issue_triage/verify.py': 'CRLF',
    'tools/issue_triage/discover.py': 'LF',
    'tools/issue_triage/triage.py': 'LF',
    'tests/unit/test_issue_triage.py': 'LF',
    '.agent/workflows/issue-triage.md': 'CRLF',
    '.agent/skills/issue-triage/SKILL.md': 'LF',
    '.agent/docs/issue-lifecycle-guide.md': 'CRLF',
    '.agent/docs/commands.md': 'CRLF',
    '.agent/docs/cloud-local-collaboration.md': 'CRLF',
    '.agent/context/known-issues.yaml': 'LF',
    '.agent/context/known-issues.md': 'LF',
    '.agent/context/grouping/2026-11-15-post-rc3-triage-residuals-session-grouping.md': 'LF',
}
bad = []
for path, want in kinds.items():
    data = pathlib.Path(path).read_bytes()
    lf, pairs, cr = data.count(bytes([10])), data.count(crlf), data.count(bytes([13]))
    got = 'CRLF' if lf and pairs == lf and cr == pairs else ('LF' if cr == 0 else 'MIXED')
    print(path, want, got, len(data), 'bytes')
    if got != want:
        bad.append(path)
print('line-ending problems:', bad)
sys.exit(1 if bad else 0)
"@

# An id is excused only when row 0's baseline receipt really shows it FAILED: a missing
# receipt excuses nothing. Row 0's receipt has 2982 passed and no FAILED id.
$baseReceipt = "$receipts/ttf-base-py.txt"
$baselinePyFailed = @()
if (Test-Path $baseReceipt) {
    $baselinePyFailed = @(Select-String -Path $baseReceipt -Pattern '^FAILED (\S+)' | ForEach-Object { $_.Matches[0].Groups[1].Value })
}
Write-Output ("baseline py failures excused: {0} id(s) (receipt {1})" -f $baselinePyFailed.Count, $baseReceipt)

$skipped = @(
    @{ Id = 'py-types'; Stage = 'static'; Reason = 'pyright covers packages/ only (pyproject.toml [tool.pyright] include), and nothing there changes' },
    @{ Id = 'ui-types/ui-lint/ui-tests/ui-build/ui-electron'; Stage = 'full'; Reason = 'nothing under ui/ changes' },
    @{ Id = 'mcp-types/mcp-build/mcp-tests/mcp-audit'; Stage = 'full'; Reason = 'no MCP change; the MCP Python tests run inside py-tests' },
    @{ Id = 'e2e'; Stage = 'full'; Reason = 'no renderer or launch change' },
    @{ Id = 'openapi'; Stage = 'full'; Reason = 'no packages/api change (H1-4)' },
    @{ Id = 'build-record'; Stage = 'full'; Reason = 'no build' }
)
foreach ($s in $skipped) {
    Write-Output ("{0} stage={1} skipped reason={2}" -f $s.Id, $s.Stage, $s.Reason)
}

$py = @('uv', 'run', '--no-sync', 'python')
$pytest = @('uv', 'run', '--no-sync', 'pytest')
$identity = $py + @("$plan/identity.py")
$steps = @(
    @{ Id = 'identity-before'; Stage = 'identity'; Argv = $identity },
    @{ Id = 'py-lint'; Stage = 'static'; Argv = @('uv', 'run', '--no-sync', 'ruff', 'check', 'packages/', 'tests/') },
    @{ Id = 'tools-lint'; Stage = 'static'; Argv = $py + @('-c', $toolsLint) },
    @{ Id = 'py-format'; Stage = 'static'; Argv = @('uv', 'run', '--no-sync', 'ruff', 'format', '--check', 'tests/unit/test_issue_triage.py') },
    @{ Id = 'task-contract'; Stage = 'static'; Argv = $py + @('tools/lint_task_contract.py', '--allowed-builder-classes', 'avkit_builder,avkit_coordinator,avkit_verifier', '--task', "$plan/task.md") },
    @{ Id = 'scope-paths'; Stage = 'static'; Argv = $py + @('-c', $scopePaths) },
    @{ Id = 'line-endings'; Stage = 'static'; Argv = $py + @('-c', $lineEndings) },
    @{ Id = 'doc-check'; Stage = 'static'; Argv = $py + @("$plan/doc-check.py", '--check') },
    @{ Id = 'red-check-selftest'; Stage = 'static'; Argv = $py + @("$plan/red-check.py", '--selftest') },
    @{ Id = 'triage-tests'; Stage = 'targeted'; Argv = $pytest + @('tests/unit/test_issue_triage.py', '--tb=short', '-q') },
    @{ Id = 'register-callers'; Stage = 'targeted'; Argv = $pytest + @('tests/tooling/test_closeout_record_once.py', 'tests/tooling/test_closeout_register_grammar.py', '--tb=short', '-q') },
    @{ Id = 'adoption'; Stage = 'targeted'; Argv = $pytest + @('tests/tooling/test_framework_adoption.py', '--tb=short', '-q') },
    @{ Id = 'live-smoke'; Stage = 'targeted'; Argv = $py + @("$plan/live-smoke.py") },
    @{ Id = 'py-tests'; Stage = 'full'; Argv = $pytest + @('tests/', '--tb=short', '-q', '-rfE') },
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
    $receipt = "$receipts/ttf-D6-$($step.Id).txt"
    $argv = $step.Argv
    & rtk proxy @argv *> $receipt
    $code = $LASTEXITCODE
    # The child's own exit code beside the receipt, before any gate rule below adjusts it.
    Set-Content -Path "$receipt.exit" -Value $code
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
    if ($code -eq 0 -and $step.Id -eq 'live-smoke') {
        if (-not (Select-String -Path $receipt -Pattern '^live-smoke: pass' -Quiet)) {
            Write-Output 'live-smoke: the receipt does not report live-smoke: pass'
            $code = 1
        }
    }
    if ($code -eq 0 -and $step.Id -eq 'identity-after') {
        $before = Get-TestedState "$receipts/ttf-D6-identity-before.txt"
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
