# Closeout-record-once fresh-full gate (task H1-2; implementation-plan.md §Session gate).
# Session 83's shape (docs/execution/plans/2026-11-14-review-limits-no-token-budget/session-gate.ps1),
# with this plan's scope (Files Modified, the plan folder, the closeout artifacts and the paths
# baseline-dirty.txt held) and steps: tools-lint on the validator and the tooling tests, py-lint,
# the task contract, scope-paths, port-check and red-check's selftest; then the record-once tests
# (AC-1 to AC-10), the validator selftest with TMP elsewhere checked by selftest-arms-check.py
# (AC-11, AC-12), the selftest under the user's own temp (AC-15, AC-16), the reflections check
# (AC-13), the stage-log survey compare (AC-14) and the issues render check (AC-17); then the full
# Python suite and the state render.
# Runs from the repository root (P:/av-kit, main only per AGENTS.md §Commits) in stage order:
# input identity, then every static check, then the targeted checks, then the full suites, then
# the input identity again. One receipt per id under C:/Temp/av-kit/cro, named cro-D6-<id>.txt.
# Fail-fast: the first non-zero step stops the gate and every later step is printed as not_run.
# The gate also fails when tested_state differs between its start and its end (an input changed
# while it ran). Read-only apart from the receipts and the temp folders, which sit outside the
# repository. Nothing here reaches the network or YouTube, and no step dispatches a model.
# Exit = the first failing step's code.
# py-tests runs the whole suite (no -x) and keeps Session 49b's baseline rule: pytest exit 1
# passes only when every FAILED id also FAILED in row 0's cro-base-py.txt, and nothing ERRORs.
# Skipped, per the plan: py-types (nothing under packages/ changes), ui-* (nothing under ui/
# changes), mcp-* (no MCP change), openapi (no packages/api change; H1-4) and build-record (no
# build). Each is printed with its reason and runs nothing.
$ErrorActionPreference = 'Continue'
$root = (git rev-parse --show-toplevel).Trim()
Set-Location $root
$plan = 'docs/execution/plans/2026-11-15-closeout-record-once'
$receipts = 'C:/Temp/av-kit/cro'
# lint_task_contract.py recognises the instantiated receipt paths only through RECEIPTS_DIR and
# fails closed (exit 3) when it is unset, which no user or machine scope sets on this host.
$env:RECEIPTS_DIR = 'C:/Temp/av-kit'
$env:PYTHONIOENCODING = 'utf-8'
$env:ELECTRON_RUN_AS_NODE = $null
# RC1 ECN-2: keep the temp dirs away from the home folder, as row 0 ran the base suite. The
# closeout-selftest-default-tmp step alone runs with the user's own TMP and TEMP (AC-15).
$userTmp = $env:TMP
$userTemp = $env:TEMP
$tmp = 'C:\Temp\av-kit\cro\tmp'
New-Item -ItemType Directory -Force -Path $tmp | Out-Null
$env:TMP = $tmp
$env:TEMP = $tmp
$base = (Get-Content "$plan/baseline.sha").Trim()

# Files Modified, the plan folder, the closeout artifacts and the paths baseline-dirty.txt
# already held. Anything else changed, HEAD moving, or a baseline-dirty path outside this scope
# whose content moved from baseline-dirty-content.txt is S4.
$scopePaths = @"
import hashlib, pathlib, subprocess, sys
mine = {
    'tools/validate_closeout_artifacts.py',
    'tests/tooling/test_closeout_record_once.py',
    'tests/tooling/test_closeout_register_grammar.py',
    '.agent/context/known-issues.yaml',
    '.agent/context/known-issues.md',
    'docs/execution/metrics.md',
    '.agent/context/current-focus.md',
}
prefixes = ('$plan/', '.agent/context/handoffs/2026-11-15-closeout-record-once-', 'docs/execution/reflections/2026-11-15-closeout-record-once-')
def in_scope(path):
    return path in mine or path.startswith(prefixes)
allowed = set(mine)
for line in pathlib.Path('$plan/baseline-dirty.txt').read_text(encoding='utf-8-sig').splitlines():
    if not line:
        continue
    path = line[3:]
    if not path or ' -> ' in path or path.startswith('"'):
        print('baseline-dirty.txt: unreadable line', repr(line))
        sys.exit(2)
    allowed.add(path)
moved_content = []
for line in pathlib.Path('$plan/baseline-dirty-content.txt').read_text(encoding='utf-8').splitlines():
    path, _, recorded = line.partition(' ')
    if not path or in_scope(path):
        continue
    target = pathlib.Path(path)
    got = 'sha256 ' + hashlib.sha256(target.read_bytes()).hexdigest() if target.is_file() else 'absent'
    if got != recorded:
        moved_content.append(path)
# --no-renames: a rename reports both its source deletion and its destination, so moving an
# out-of-scope file into an allowed path still shows the out-of-scope deletion.
# -z: NUL-separated, so a path with spaces or quoting is one entry.
def paths(*args):
    raw = subprocess.run(['git', *args], capture_output=True, check=True).stdout.decode('utf-8')
    return [p for p in raw.split('\0') if p]
head = subprocess.run(['git', 'rev-parse', 'HEAD'], capture_output=True, text=True, check=True).stdout.strip()
moved = head != '$base'
out = paths('diff', '--no-renames', '--name-only', '-z', head)
out += paths('ls-files', '--others', '--exclude-standard', '-z')
extra = sorted({p for p in out if p not in allowed and not p.startswith(prefixes)})
print('changed paths:', len(set(out)), 'outside scope:', extra, 'baseline-dirty content moved:', moved_content, 'head:', head, 'head moved (S4):', moved)
sys.exit(1 if extra or moved or moved_content else 0)
"@

# An id is excused only when row 0's baseline receipt really shows it FAILED: a missing
# receipt excuses nothing.
$baseReceipt = "$receipts/cro-base-py.txt"
$baselinePyFailed = @()
if (Test-Path $baseReceipt) {
    $baselinePyFailed = @(Select-String -Path $baseReceipt -Pattern '^FAILED (\S+)' | ForEach-Object { $_.Matches[0].Groups[1].Value })
}
Write-Output ("baseline py failures excused: {0} id(s) (receipt {1})" -f $baselinePyFailed.Count, $baseReceipt)

$skipped = @(
    @{ Id = 'py-types'; Stage = 'static'; Reason = 'pyright packages/: nothing under packages/ changes' },
    @{ Id = 'ui-types/ui-lint/ui-tests/ui-build/ui-electron'; Stage = 'full'; Reason = 'nothing under ui/ changes' },
    @{ Id = 'mcp-types/mcp-build/mcp-tests/mcp-audit'; Stage = 'full'; Reason = 'no MCP change' },
    @{ Id = 'openapi'; Stage = 'full'; Reason = 'no packages/api change (H1-4)' },
    @{ Id = 'build-record'; Stage = 'full'; Reason = 'no build' }
)
foreach ($s in $skipped) {
    Write-Output ("{0} stage={1} skipped reason={2}" -f $s.Id, $s.Stage, $s.Reason)
}

$py = @('uv', 'run', '--no-sync', 'python')
$identity = $py + @("$plan/identity.py")
$validator = 'tools/validate_closeout_artifacts.py'
$steps = @(
    @{ Id = 'identity-before'; Stage = 'identity'; Argv = $identity },
    @{ Id = 'tools-lint'; Stage = 'static'; Argv = @('uv', 'run', '--no-sync', 'ruff', 'check', $validator, 'tests/tooling/') },
    @{ Id = 'py-lint'; Stage = 'static'; Argv = @('uv', 'run', '--no-sync', 'ruff', 'check', 'packages/', 'tests/') },
    @{ Id = 'task-contract'; Stage = 'static'; Argv = $py + @('tools/lint_task_contract.py', '--allowed-builder-classes', 'avkit_builder,avkit_coordinator,avkit_verifier', '--task', "$plan/task.md") },
    @{ Id = 'scope-paths'; Stage = 'static'; Argv = $py + @('-c', $scopePaths) },
    @{ Id = 'port-check'; Stage = 'static'; Argv = $py + @("$plan/port-check.py") },
    @{ Id = 'red-check-selftest'; Stage = 'static'; Argv = $py + @("$plan/red-check.py", '--selftest') },
    @{ Id = 'record-once-tests'; Stage = 'targeted'; Argv = @('uv', 'run', '--no-sync', 'pytest', 'tests/tooling/test_closeout_record_once.py', 'tests/tooling/test_closeout_register_grammar.py', '--tb=short', '-q') },
    @{ Id = 'closeout-selftest'; Stage = 'targeted'; Argv = $py + @($validator, '--selftest') },
    @{ Id = 'arms-check'; Stage = 'targeted'; Argv = $py + @("$plan/selftest-arms-check.py", '--before', "$plan/selftest-arms-before.txt", "$receipts/cro-D6-closeout-selftest.txt") },
    @{ Id = 'closeout-selftest-default-tmp'; Stage = 'targeted'; Argv = $py + @($validator, '--selftest'); UserTemp = $true },
    @{ Id = 'reflections-check'; Stage = 'targeted'; Argv = $py + @("$plan/reflections-check.py", '--before', "$receipts/base/validate_closeout_artifacts.py", '--out', "$receipts/cro-D6-reflections-out.txt") },
    @{ Id = 'survey-compare'; Stage = 'targeted'; Argv = $py + @("$plan/stage-log-survey.py", '--out', "$receipts/cro-D6-survey-out.txt", '--compare', "$receipts/cro-base-survey.txt") },
    @{ Id = 'issues-render-check'; Stage = 'targeted'; Argv = $py + @('tools/issue_triage.py', 'render', '--check') },
    @{ Id = 'py-tests'; Stage = 'full'; Argv = @('uv', 'run', '--no-sync', 'pytest', 'tests/', '--tb=short', '-q', '-rfE') },
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
    $receipt = "$receipts/cro-D6-$($step.Id).txt"
    $argv = $step.Argv
    if ($step.UserTemp) {
        $env:TMP = $userTmp
        $env:TEMP = $userTemp
    }
    & rtk proxy @argv *> $receipt
    $code = $LASTEXITCODE
    $env:TMP = $tmp
    $env:TEMP = $tmp
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
    if ($code -eq 0 -and $step.Id -in @('closeout-selftest', 'closeout-selftest-default-tmp')) {
        if (-not (Select-String -Path $receipt -Pattern ' 0 failure' -Quiet)) {
            Write-Output "$($step.Id): the receipt does not report 0 failures"
            $code = 1
        }
    }
    if ($code -eq 0 -and $step.Id -eq 'identity-after') {
        $before = Get-TestedState "$receipts/cro-D6-identity-before.txt"
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
