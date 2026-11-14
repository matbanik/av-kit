# Review-limits fresh-full gate (task H1-2; implementation-plan.md §Session gate).
# Session 71's shape (docs/execution/plans/2026-11-13-capture-style-tool-flow/session-gate.ps1),
# with this plan's scope (Files Modified and the project files) and steps: tools-lint on the
# ledger and the tooling tests, prose-check (AC-14, AC-15), the ledger selftest with
# selftest-arms-check.py (AC-12), the review-limits tests (AC-1 to AC-11), the dispatch suite
# checked by dispatch-check.py (AC-13), the full Python suite, the state render and the closeout
# validator's selftest.
# Runs from the repository root (P:/av-kit, main only per AGENTS.md §Commits) in stage order:
# input identity, then every static check, then the targeted checks, then the full suites, then
# the input identity again. One receipt per id under C:/Temp/av-kit/rl, named rl-D6-<id>.txt.
# Fail-fast: the first non-zero step stops the gate and every later step is printed as not_run.
# The gate also fails when tested_state differs between its start and its end (an input changed
# while it ran). Read-only apart from the receipts and the temp folders, which sit outside the
# repository. Nothing here reaches the network or YouTube, and no step dispatches a model.
# Exit = the first failing step's code.
# py-tests runs the whole suite (no -x) and keeps Session 49b's baseline rule: pytest exit 1
# passes only when every FAILED id also FAILED in row 0's rl-base-py.txt, and nothing ERRORs.
# dispatch-tests excuses only the two baseline FAIL ids, through dispatch-check.py (D-739).
# Skipped, per the plan: py-types (nothing under packages/ changes), ui-* (nothing under ui/
# changes), mcp-* (no MCP change), openapi (no packages/api change; H1-4) and build-record (no
# build). Each is printed with its reason and runs nothing.
$ErrorActionPreference = 'Continue'
$root = (git rev-parse --show-toplevel).Trim()
Set-Location $root
$plan = 'docs/execution/plans/2026-11-14-review-limits-no-token-budget'
$receipts = 'C:/Temp/av-kit/rl'
# lint_task_contract.py recognises the instantiated receipt paths only through RECEIPTS_DIR and
# fails closed (exit 3) when it is unset, which no user or machine scope sets on this host.
$env:RECEIPTS_DIR = 'C:/Temp/av-kit'
$env:PYTHONIOENCODING = 'utf-8'
$env:ELECTRON_RUN_AS_NODE = $null
# The dispatch suite loads ModelRegistry.psm1 from the shared registry home (memory: codex-dispatch-registry-home).
$env:AGENT_MODEL_REGISTRY_HOME = 'P:/.agent'
# RC1 ECN-2 (CLOSEOUT-SELFTEST-ANCESTOR-AGENT-DIR): keep pytest's temp dirs away from the home
# folder. The dispatch suite alone runs with the user's own TMP and TEMP, as rows 0 and 8 ran it.
$userTmp = $env:TMP
$userTemp = $env:TEMP
$tmp = 'C:\Temp\av-kit\rl\tmp'
New-Item -ItemType Directory -Force -Path $tmp | Out-Null
$env:TMP = $tmp
$env:TEMP = $tmp
$base = (Get-Content "$plan/baseline.sha").Trim()

# Files Modified, the project files and the paths baseline-dirty.txt already held. Anything else
# changed, or HEAD moving, is S4. baseline-dirty.txt holds only this plan's own paths (row 0), so
# it records no content hashes.
$scopePaths = @"
import pathlib, subprocess, sys
allowed = {
    'tools/review_ledger.py',
    '.agent/review-limits.json',
    'tests/tooling/test_review_limits.py',
    'docs/execution/plans/PLAN-TEMPLATE.md',
    'docs/execution/plans/TASK-TEMPLATE.md',
    '.agent/templates/PLAN-TEMPLATE.md',
    '.agent/templates/TASK-TEMPLATE.md',
    'docs/execution/plans/2026-09-26-framework-update-adoption/rule-preservation.md',
    '.agent/workflows/create-plan.md',
    '.agent/workflows/delegated-plan-creation.md',
    '.agent/workflows/execution-session.md',
    '.agent/workflows/validation-review.md',
    '.agent/docs/development-lifecycle.md',
    '.agent/docs/issue-lifecycle-guide.md',
    '.agent/docs/model-routing.md',
    '.agent/skills/cli-dispatch/SKILL.md',
    'AGENTS.md',
    'PROJECT-PROFILE.md',
    'docs/execution/metrics.md',
    '.agent/context/current-focus.md',
}
prefixes = ('$plan/', '.agent/context/handoffs/2026-11-14-review-limits-no-token-budget-', 'docs/execution/reflections/2026-11-14-review-limits-no-token-budget-')
for line in pathlib.Path('$plan/baseline-dirty.txt').read_text(encoding='utf-8').splitlines():
    if not line:
        continue
    path = line[3:]
    if not path or ' -> ' in path or path.startswith('"'):
        print('baseline-dirty.txt: unreadable line', repr(line))
        sys.exit(2)
    allowed.add(path)
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
$baseReceipt = "$receipts/rl-base-py.txt"
$baselinePyFailed = @()
if (Test-Path $baseReceipt) {
    $baselinePyFailed = @(Select-String -Path $baseReceipt -Pattern '^FAILED (\S+)' | ForEach-Object { $_.Matches[0].Groups[1].Value })
}
Write-Output ("baseline py failures excused: {0} id(s) (receipt {1})" -f $baselinePyFailed.Count, $baseReceipt)
Write-Output 'baseline dispatch failures excused: placeholder receipts dir refused, refusal created no placeholder dir (dispatch-check.py, D-739)'

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
$steps = @(
    @{ Id = 'identity-before'; Stage = 'identity'; Argv = $identity },
    @{ Id = 'tools-lint'; Stage = 'static'; Argv = @('uv', 'run', '--no-sync', 'ruff', 'check', 'tools/review_ledger.py', 'tests/tooling/') },
    @{ Id = 'py-lint'; Stage = 'static'; Argv = @('uv', 'run', '--no-sync', 'ruff', 'check', 'packages/', 'tests/') },
    @{ Id = 'task-contract'; Stage = 'static'; Argv = $py + @('tools/lint_task_contract.py', '--allowed-builder-classes', 'avkit_builder,avkit_coordinator,avkit_verifier', '--task', "$plan/task.md") },
    @{ Id = 'scope-paths'; Stage = 'static'; Argv = $py + @('-c', $scopePaths) },
    @{ Id = 'prose-check'; Stage = 'static'; Argv = $py + @("$plan/prose-check.py", '--rows', 'P1-P22', '--begin-examples', '--agents-size', '--templates') },
    @{ Id = 'red-check-selftest'; Stage = 'static'; Argv = $py + @("$plan/red-check.py", '--selftest') },
    @{ Id = 'ledger-selftest'; Stage = 'targeted'; Argv = $py + @('tools/review_ledger.py', 'selftest') },
    @{ Id = 'arms-check'; Stage = 'targeted'; Argv = $py + @("$plan/selftest-arms-check.py", '--before', "$plan/selftest-arms-before.txt", "$receipts/rl-D6-ledger-selftest.txt") },
    @{ Id = 'review-limits-tests'; Stage = 'targeted'; Argv = @('uv', 'run', '--no-sync', 'pytest', 'tests/tooling/test_review_limits.py', '--tb=short', '-q') },
    @{ Id = 'dispatch-tests'; Stage = 'targeted'; Argv = @('pwsh', '-NoProfile', '-File', '.agent/skills/cli-dispatch/tests/Test-CliDispatch.ps1'); UserTemp = $true },
    @{ Id = 'dispatch-check'; Stage = 'targeted'; Argv = $py + @("$plan/dispatch-check.py", '--exit-file', "$receipts/rl-D6-dispatch-tests.txt.exit", "$receipts/rl-D6-dispatch-tests.txt") },
    @{ Id = 'py-tests'; Stage = 'full'; Argv = @('uv', 'run', '--no-sync', 'pytest', 'tests/', '--tb=short', '-q', '-rfE') },
    @{ Id = 'state-render'; Stage = 'full'; Argv = $py + @('tools/meu_status.py', 'render', '--check') },
    @{ Id = 'closeout-selftest'; Stage = 'full'; Argv = $py + @('tools/validate_closeout_artifacts.py', '--selftest') },
    @{ Id = 'identity-after'; Stage = 'identity'; Argv = $identity }
)

function Get-TestedState([string]$Receipt) {
    $line = Select-String -Path $Receipt -Pattern '^tested_state ' | Select-Object -Last 1
    if ($null -eq $line) { return $null }
    return $line.Line.Substring('tested_state '.Length).Trim()
}

for ($i = 0; $i -lt $steps.Count; $i++) {
    $step = $steps[$i]
    $receipt = "$receipts/rl-D6-$($step.Id).txt"
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
    if ($step.Id -eq 'dispatch-tests') {
        # The suite exits 1 on the two baseline FAILs (D-739); dispatch-check judges the receipt
        # and this exit next, so the step itself records the exit and passes on.
        Set-Content -Path "$receipt.exit" -Value $code
        Write-Output "dispatch-tests: exit $code saved to $receipt.exit for dispatch-check"
        $code = 0
    }
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
    if ($code -eq 0 -and $step.Id -eq 'closeout-selftest') {
        if (-not (Select-String -Path $receipt -Pattern ' 0 failure' -Quiet)) {
            Write-Output 'closeout-selftest: the receipt does not report 0 failures'
            $code = 1
        }
    }
    if ($code -eq 0 -and $step.Id -eq 'identity-after') {
        $before = Get-TestedState "$receipts/rl-D6-identity-before.txt"
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
