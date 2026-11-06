# Session 49b fresh-full gate (task H1-2; implementation-plan.md §Session gate).
# Session 49's shape (docs/execution/plans/2026-11-04-rc2-fetch-uninstall/session-gate.ps1), with this plan's steps.
# Runs from the repository root (P:/av-kit, main only per AGENTS.md §Commits) in stage order:
# input identity, then every static check, then the full suites, then the input identity again.
# One receipt per id under C:/Temp/av-kit, named s49b-D6-<id>.txt. Fail-fast: the first non-zero
# step stops the gate and every later step is printed as not_run. The gate also fails when
# tested_state differs between its start and its end (an input changed while it ran). Read-only
# apart from the receipts. Exit = the first failing step's code.
# py-tests runs the whole suite (no -x) and keeps Session 49's baseline rule: pytest exit 1 passes
# only when every FAILED id also FAILED in row 0's s49b-base-py.txt, and nothing ERRORs. Row 0
# saw no failure (1193 passed), so nothing is excused.
# Skipped, per the plan: py-types, ui-types, ui-lint, ui-tests, ui-build, ui-electron, mcp-types,
# mcp-build, mcp-tests, mcp-audit, openapi and build-record. Each is printed with its reason and
# runs nothing.
$ErrorActionPreference = 'Continue'
$root = (git rev-parse --show-toplevel).Trim()
Set-Location $root
$plan = 'docs/execution/plans/2026-11-05-closeout-register-grammar'
$receipts = 'C:/Temp/av-kit'
# lint_task_contract.py recognises the instantiated receipt paths only through RECEIPTS_DIR and
# fails closed (exit 3) when it is unset, which no user or machine scope sets on this host.
$env:RECEIPTS_DIR = $receipts
$env:PYTHONIOENCODING = 'utf-8'
$env:ELECTRON_RUN_AS_NODE = $null
# RC1 ECN-2 (CLOSEOUT-SELFTEST-ANCESTOR-AGENT-DIR): keep pytest's temp dirs away from C:/Users/Mat/.agent.
$tmp = "$receipts/s49b/tmp"
New-Item -ItemType Directory -Force -Path $tmp | Out-Null
$env:TMP = $tmp
$env:TEMP = $tmp
$base = (Get-Content "$plan/baseline.sha").Trim()

# Files Modified, the project files and the paths baseline-dirty.txt already held. Anything
# else changed, or HEAD moving, is S4.
$scopePaths = @"
import pathlib, subprocess, sys
allowed = {
    'tools/issue_triage/model.py',
    'tools/validate_closeout_artifacts.py',
    'tests/tooling/test_closeout_register_grammar.py',
    '.agent/docs/human-decision-protocol.md',
    '.agent/context/known-issues.yaml',
    '.agent/context/known-issues.md',
    '.agent/context/triage-output.yaml',
    '.agent/context/grouping/2026-11-04-rc2-triage-residuals-session-grouping.md',
    '.agent/context/current-focus.md',
    'docs/execution/metrics.md',
}
dirty = pathlib.Path('$plan/baseline-dirty.txt').read_text(encoding='utf-8').splitlines()
for line in dirty:
    path = line[3:]
    if not path or ' -> ' in path or path.startswith('"'):
        print('baseline-dirty.txt: unreadable line', repr(line))
        sys.exit(2)
    allowed.add(path)
prefixes = ('$plan/', '.agent/context/handoffs/2026-11-05-closeout-register-grammar-', 'docs/execution/reflections/2026-11-05-closeout-register-grammar-')
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
print('changed paths:', len(set(out)), 'outside scope:', extra, 'head:', head, 'head moved (S4):', moved)
sys.exit(1 if extra or moved else 0)
"@

# An id is excused only when row 0's baseline receipt really shows it FAILED: a missing
# receipt excuses nothing.
$baseReceipt = "$receipts/s49b-base-py.txt"
$baselinePyFailed = @()
if (Test-Path $baseReceipt) {
    $baselinePyFailed = @(Select-String -Path $baseReceipt -Pattern '^FAILED (\S+)' | ForEach-Object { $_.Matches[0].Groups[1].Value })
}
Write-Output ("baseline py failures excused: [{0}] (receipt {1})" -f ($baselinePyFailed -join ', '), $baseReceipt)

$skipped = @(
    @{ Id = 'py-types'; Stage = 'static'; Reason = 'pyright packages/, and nothing under packages/ changes' },
    @{ Id = 'ui-types'; Stage = 'static'; Reason = 'nothing under ui/ changes' },
    @{ Id = 'ui-lint'; Stage = 'static'; Reason = 'nothing under ui/ changes' },
    @{ Id = 'ui-tests'; Stage = 'full'; Reason = 'nothing under ui/ changes, and no UI test reads the files this session writes (layout-canon reads only a 2026-09-03 grouping file)' },
    @{ Id = 'ui-build'; Stage = 'full'; Reason = 'nothing under ui/ changes' },
    @{ Id = 'ui-electron'; Stage = 'runtime'; Reason = 'nothing under ui/ changes' },
    @{ Id = 'mcp-types'; Stage = 'static'; Reason = 'no MCP change' },
    @{ Id = 'mcp-build'; Stage = 'full'; Reason = 'no MCP change' },
    @{ Id = 'mcp-tests'; Stage = 'full'; Reason = 'no MCP change' },
    @{ Id = 'mcp-audit'; Stage = 'runtime'; Reason = 'no MCP change' },
    @{ Id = 'openapi'; Stage = 'full'; Reason = 'no packages/api change (H1-4 checks it)' },
    @{ Id = 'build-record'; Stage = 'full'; Reason = 'this session makes no build' }
)
foreach ($s in $skipped) {
    Write-Output ("{0} stage={1} skipped reason={2}" -f $s.Id, $s.Stage, $s.Reason)
}

$identity = @('uv', 'run', 'python', "$plan/identity.py")
$steps = @(
    @{ Id = 'identity-before'; Stage = 'identity'; Argv = $identity },
    @{ Id = 'py-lint'; Stage = 'static'; Argv = @('uv', 'run', 'ruff', 'check', 'packages/', 'tests/') },
    @{ Id = 'tools-lint'; Stage = 'static'; Argv = @('uv', 'run', 'ruff', 'check', 'tools/issue_triage/model.py', 'tools/validate_closeout_artifacts.py') },
    @{ Id = 'task-contract'; Stage = 'static'; Argv = @('uv', 'run', 'python', 'tools/lint_task_contract.py', '--allowed-builder-classes', 'avkit_builder,avkit_coordinator,avkit_verifier', '--task', "$plan/task.md") },
    @{ Id = 'scope-paths'; Stage = 'static'; Argv = @('uv', 'run', 'python', '-c', $scopePaths) },
    @{ Id = 'red-check-selftest'; Stage = 'static'; Argv = @('uv', 'run', 'python', "$plan/red-check.py", '--selftest') },
    @{ Id = 'py-tests'; Stage = 'full'; Argv = @('uv', 'run', 'pytest', 'tests/', '--tb=short', '-q', '-rfE') },
    @{ Id = 'state-render'; Stage = 'full'; Argv = @('uv', 'run', 'python', 'tools/meu_status.py', 'render', '--check') },
    @{ Id = 'issues-render'; Stage = 'full'; Argv = @('uv', 'run', 'python', 'tools/issue_triage.py', 'render', '--check') },
    @{ Id = 'identity-after'; Stage = 'identity'; Argv = $identity }
)

function Get-TestedState([string]$Receipt) {
    $line = Select-String -Path $Receipt -Pattern '^tested_state ' | Select-Object -Last 1
    if ($null -eq $line) { return $null }
    return $line.Line.Substring('tested_state '.Length).Trim()
}

for ($i = 0; $i -lt $steps.Count; $i++) {
    $step = $steps[$i]
    $receipt = "$receipts/s49b-D6-$($step.Id).txt"
    $argv = $step.Argv
    & rtk proxy @argv *> $receipt
    $code = $LASTEXITCODE
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
    if ($code -eq 0 -and $step.Id -eq 'identity-after') {
        $before = Get-TestedState "$receipts/s49b-D6-identity-before.txt"
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
