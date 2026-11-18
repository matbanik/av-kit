# Session 93 fresh-full gate (task H1-2; implementation-plan.md §Session gate).
# The shape of docs/execution/plans/2026-11-17-test-run-reliability/session-gate.ps1, with this
# plan's steps: identity, then the static checks (the task contract, scope-paths by diff-check.py,
# line-endings, home-path, the nine plan-script selftests, py-format and py-lint on adapter.py,
# both test files and this plan folder's Python, py-types on packages/), then the targeted checks
# (py-frames, ui-canon), then host-load (Session 81 RULE-2, 50 % here), then the fresh full suite
# (py-tests), issues-render-check and state-render, then the identity again.
# Runs from the repository root (P:/av-kit, main only per AGENTS.md §Commits). One receipt per
# id under C:/Temp/av-kit/video-tail-frame, named vtf-D6-<id>.txt.
# Fail-fast: the first non-zero step stops the gate and every later step is printed as not_run.
# The gate also fails when tested_state differs between its start and its end (an input changed
# while it ran). Read-only apart from the receipts and the temp folder; both are outside the
# checkout. Nothing here reaches the network or YouTube, and no step dispatches a model.
# Exit = the first failing step's code.
# py-tests runs the D6 argv (-x). If it stops on a failure, it runs the D6 argv again without -x
# and passes only when its failing ids are a subset of the ids vtf-base-py.txt shows failing and
# none is in the two test files this plan changes (vtf-base-py.txt: 3112 passed, none failing).
# ui-canon runs Vitest from ui/ (Set-Location ui, then back), the only UI tests that read the
# registers rows 1 and 6 write.
# host-load samples Win32_Processor.LoadPercentage five times; above 50 % it waits, re-sampling
# every 30 s for up to 10 minutes, and records the value it ran at. It never fails the gate.
# Skipped, per the plan: the other ui-* steps, openapi and mcp-* (H1-4 checks that every file
# under packages/ other than adapter.py, and under mcp-server/, tools/ and ui/, keeps its
# baseline-skip-hashes.json hash, and none was added or removed). Each is printed with its reason
# and runs nothing.
$ErrorActionPreference = 'Continue'
$root = (git rev-parse --show-toplevel).Trim()
Set-Location $root
$plan = 'docs/execution/plans/2026-11-17-video-tail-frame'
$receipts = 'C:/Temp/av-kit/video-tail-frame'
# lint_task_contract.py recognises the instantiated receipt paths only through RECEIPTS_DIR and
# fails closed (exit 3) when it is unset, which no user or machine scope sets on this host.
$env:RECEIPTS_DIR = 'C:/Temp/av-kit'
$env:PYTHONIOENCODING = 'utf-8'
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:ELECTRON_RUN_AS_NODE = $null
# RC1 ECN-2: keep the temp dirs away from the home folder, as row 0 ran the base suite.
$tmp = 'C:\Temp\av-kit\video-tail-frame\tmp'
New-Item -ItemType Directory -Force -Path $tmp | Out-Null
$env:TMP = $tmp
$env:TEMP = $tmp

# py-tests: the D6 argv; on a failure, the argv again without -x, passing only when every failing
# id is one that vtf-base-py.txt shows failing and is not in a test file this plan changes.
$pyTests = @"
import re, subprocess, sys
argv = ['uv', 'run', '--no-sync', 'pytest', 'tests/', '-x', '--tb=short', '-q']
changed = ('tests/unit/test_media_adapter_frames.py', 'tests/integration/test_video_real_ffmpeg.py')
first = subprocess.run(argv)
if first.returncode == 0:
    print('py-tests: D6 argv exit 0')
    sys.exit(0)
def failing(text):
    return {m.group(1) for m in re.finditer(r'^(?:FAILED|ERROR) (\S+)', text, re.M)}
base = {t for t in failing(open('$receipts/vtf-base-py.txt', encoding='utf-8', errors='replace').read()) if not t.startswith(changed)}
second = subprocess.run([a for a in argv if a != '-x'], capture_output=True, text=True, encoding='utf-8', errors='replace')
sys.stdout.write(second.stdout[-4000:])
now = failing(second.stdout)
new = sorted(now - base)
print('py-tests: D6 argv exit', first.returncode, '; rerun without -x exit', second.returncode, '; failing', sorted(now), '; base failing (excusable)', sorted(base), '; not excused', new)
sys.exit(0 if second.returncode in (0, 1) and not new and (second.returncode == 0 or now) else 1)
"@

function Invoke-HostLoad {
    $samples = @(1..5 | ForEach-Object { (Get-CimInstance Win32_Processor | Measure-Object -Property LoadPercentage -Average).Average; Start-Sleep -Seconds 2 })
    $load = [math]::Round(($samples | Measure-Object -Average).Average, 1)
    Write-Output ("host-load samples: [{0}] mean={1}" -f ($samples -join ', '), $load)
    $deadline = (Get-Date).AddMinutes(10)
    while ($load -gt 50 -and (Get-Date) -lt $deadline) {
        Write-Output ("host-load {0} % is above 50 %; waiting 30 s" -f $load)
        Start-Sleep -Seconds 30
        $load = [math]::Round((Get-CimInstance Win32_Processor | Measure-Object -Property LoadPercentage -Average).Average, 1)
    }
    Write-Output ("host-load: ran at {0} %" -f $load)
}

Write-Output 'baseline py failures excused: [] (vtf-base-py.txt shows 3112 passed and no failure)'

$skipped = @(
    @{ Id = 'ui-types/ui-lint/ui-tests/ui-build/ui-electron'; Stage = 'full'; Reason = 'every ui/ file keeps its baseline-skip-hashes.json hash (H1-4); no UI file changes' },
    @{ Id = 'openapi'; Stage = 'full'; Reason = 'every packages/ file other than adapter.py keeps its baseline-skip-hashes.json hash (H1-4); no route or schema changes' },
    @{ Id = 'mcp-types/mcp-build/mcp-tests/mcp-audit'; Stage = 'full'; Reason = 'every mcp-server/ file keeps its baseline-skip-hashes.json hash (H1-4); no MCP tool changes' }
)
foreach ($s in $skipped) {
    Write-Output ("{0} stage={1} skipped reason={2}" -f $s.Id, $s.Stage, $s.Reason)
}

$py = @('uv', 'run', '--no-sync', 'python')
$identity = $py + @("$plan/identity.py")
$planPy = @(Get-ChildItem -Path $plan -Filter '*.py' | Sort-Object Name | ForEach-Object { "$plan/$($_.Name)" })
$adapter = 'packages/infrastructure/src/avkit_infra/media/adapter.py'
$unit = 'tests/unit/test_media_adapter_frames.py'
$integ = 'tests/integration/test_video_real_ffmpeg.py'
$steps = @(
    @{ Id = 'identity-before'; Stage = 'identity'; Argv = $identity },
    @{ Id = 'task-contract'; Stage = 'static'; Argv = $py + @('tools/lint_task_contract.py', '--allowed-builder-classes', 'avkit_builder,avkit_coordinator,avkit_verifier', '--task', "$plan/task.md") },
    @{ Id = 'scope-paths'; Stage = 'static'; Argv = $py + @("$plan/diff-check.py") },
    @{ Id = 'line-endings'; Stage = 'static'; Argv = $py + @("$plan/eol-check.py") },
    @{ Id = 'home-path'; Stage = 'static'; Argv = $py + @('tools/check_home_path.py') },
    @{ Id = 'red-check-selftest'; Stage = 'static'; Argv = $py + @("$plan/red-check.py", '--selftest') },
    @{ Id = 'identity-selftest'; Stage = 'static'; Argv = $py + @("$plan/identity.py", '--selftest') },
    @{ Id = 'eol-check-selftest'; Stage = 'static'; Argv = $py + @("$plan/eol-check.py", '--selftest') },
    @{ Id = 'grab-trace-selftest'; Stage = 'static'; Argv = $py + @("$plan/grab_trace.py", '--selftest') },
    @{ Id = 'load-run-selftest'; Stage = 'static'; Argv = $py + @("$plan/load-run.py", '--selftest') },
    @{ Id = 'trace-check-selftest'; Stage = 'static'; Argv = $py + @("$plan/trace-check.py", '--selftest') },
    @{ Id = 'packet-stress-selftest'; Stage = 'static'; Argv = $py + @("$plan/packet-stress.py", '--selftest') },
    @{ Id = 'diff-check-selftest'; Stage = 'static'; Argv = $py + @("$plan/diff-check.py", '--selftest') },
    @{ Id = 'meu-register-selftest'; Stage = 'static'; Argv = $py + @("$plan/meu-register.py", '--selftest') },
    @{ Id = 'py-format'; Stage = 'static'; Argv = @('uv', 'run', '--no-sync', 'ruff', 'format', '--check', $adapter, $unit, $integ) + $planPy },
    @{ Id = 'py-lint'; Stage = 'static'; Argv = @('uv', 'run', '--no-sync', 'ruff', 'check', $adapter, $unit, $integ) + $planPy },
    @{ Id = 'py-types'; Stage = 'static'; Argv = @('uv', 'run', '--no-sync', 'pyright', 'packages/') },
    @{ Id = 'py-frames'; Stage = 'targeted'; Argv = $py + @('-m', 'pytest', '-q', '--tb=short', '-p', 'no:cacheprovider', $unit, $integ) },
    @{ Id = 'ui-canon'; Stage = 'targeted'; Cwd = 'ui'; Argv = @('npm', 'run', 'test', '--', 'tests/unit/layout-canon.test.ts', 'tests/unit/queue-canon.test.ts') },
    @{ Id = 'host-load'; Stage = 'host'; HostLoad = $true },
    @{ Id = 'py-tests'; Stage = 'full'; Argv = $py + @('-c', $pyTests) },
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
    $receipt = "$receipts/vtf-D6-$($step.Id).txt"
    if ($step.ContainsKey('HostLoad')) {
        Invoke-HostLoad *> $receipt
        $code = 0
    } else {
        $argv = $step.Argv
        if ($step.ContainsKey('Cwd')) { Set-Location (Join-Path $root $step.Cwd) }
        & rtk proxy @argv *> $receipt
        $code = $LASTEXITCODE
        Set-Location $root
    }
    Write-Output ("{0} stage={1} exit={2} receipt={3}" -f $step.Id, $step.Stage, $code, $receipt)
    Get-Content $receipt | Select-Object -Last 6
    if ($code -eq 0 -and $step.Id -eq 'identity-after') {
        $before = Get-TestedState "$receipts/vtf-D6-identity-before.txt"
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
