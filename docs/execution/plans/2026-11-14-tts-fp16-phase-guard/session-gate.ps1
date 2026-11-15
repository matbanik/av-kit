# Session 73 fresh-full gate (task H1-2; implementation-plan.md §Session gate).
# Session 52's shape (docs/execution/plans/2026-11-06-tts-load-fp16/session-gate.ps1), with this plan's steps.
# Runs from the repository root (P:/av-kit, main only per AGENTS.md §Commits) in stage order:
# input identity, then every static check, then the full Python suite and the renders, then the
# runtime checks, then the input identity again. One receipt per id under C:/Temp/av-kit, named
# s73-D6-<id>.txt. Fail-fast: the first non-zero step stops the gate and every later step is
# printed as not_run. The gate also fails when tested_state differs between its start and its end
# (an input changed while it ran). Read-only apart from the receipts, packaging/build and
# packaging/dist (package-build), and the gate copies under C:/Temp/av-kit/s73/gate; all are
# ignored or outside the checkout. Exit = the first failing step's code.
# py-tests runs the whole suite (no -x) and keeps Session 49b's baseline rule: pytest exit 1
# passes only when every FAILED id also FAILED in row 0's s73-base-py.txt, and nothing ERRORs.
# Skipped, per the plan: the UI and MCP suites and builds, openapi, ui-electron, mcp-audit and
# build-record. Each is printed with its reason and runs nothing.
$ErrorActionPreference = 'Continue'
$root = (git rev-parse --show-toplevel).Trim()
Set-Location $root
$plan = 'docs/execution/plans/2026-11-14-tts-fp16-phase-guard'
$receipts = 'C:/Temp/av-kit'
# lint_task_contract.py recognises the instantiated receipt paths only through RECEIPTS_DIR and
# fails closed (exit 3) when it is unset, which no user or machine scope sets on this host.
$env:RECEIPTS_DIR = $receipts
$env:PYTHONIOENCODING = 'utf-8'
$env:ELECTRON_RUN_AS_NODE = $null
# RC1 ECN-2 (CLOSEOUT-SELFTEST-ANCESTOR-AGENT-DIR): keep pytest's temp dirs away from ~/.agent.
$tmp = "$receipts/s73/tmp"
New-Item -ItemType Directory -Force -Path $tmp | Out-Null
$env:TMP = $tmp
$env:TEMP = $tmp
$base = (Get-Content "$plan/baseline.sha").Trim()

# Files Modified, the project files and the paths baseline-dirty.txt already held. Anything
# else changed, or HEAD moving, is S3. No path under packages/, ui/, mcp-server/ or tools/, and
# no openapi snapshot, is in scope: this session changes no product code (§Files Modified).
$scopePaths = @"
import pathlib, subprocess, sys
allowed = {
    'docs/build-plan/03-service-layer.md',
    '.agent/context/meu-status.yaml',
    '.agent/context/meu-registry.md',
    'docs/BUILD_PLAN.md',
    '.agent/context/known-issues.yaml',
    '.agent/context/known-issues.md',
    '.agent/context/current-focus.md',
    'docs/execution/metrics.md',
}
refused = {'ui/tests/e2e/test-ids.ts', 'openapi.committed.json'}
dirty = pathlib.Path('$plan/baseline-dirty.txt').read_text(encoding='utf-8').splitlines()
for line in dirty:
    path = line[3:].split('  sha256=')[0]
    if not path or ' -> ' in path or path.startswith('"'):
        print('baseline-dirty.txt: unreadable line', repr(line))
        sys.exit(2)
    allowed.add(path)
prefixes = ('$plan/', '.agent/context/handoffs/2026-11-14-tts-fp16-phase-guard-', 'docs/execution/reflections/2026-11-14-tts-fp16-phase-guard-')
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
extra = sorted({p for p in out if p in refused or (p not in allowed and not p.startswith(prefixes))})
print('changed paths:', len(set(out)), 'outside scope:', extra, 'head:', head, 'head moved (S3):', moved)
sys.exit(1 if extra or moved else 0)
"@

# The gate's guarded graph must be byte-identical to row 2's (PATCH_COPY is deterministic).
$patchSame = @"
import json, sys
row = json.load(open('$receipts/s73-patch.json', encoding='utf-8'))
gate = json.load(open('$receipts/s73-D6-patch.json', encoding='utf-8'))
same = row['dst_sha256'] == gate['dst_sha256'] and gate['src_unchanged']
print('row 2', row['dst_sha256'], 'gate', gate['dst_sha256'], 'same', same)
sys.exit(0 if same else 1)
"@

# The gate's guarded smoke must pass all 149 jobs on FP16 (AC-127.6's command, on fresh copies).
$smokePass = @"
import json, sys
r = json.load(open('$receipts/s73-D6-smoke-guarded.json', encoding='utf-8'))
ok = r.get('passed') is True and r.get('variant_id') == 'kokoro-onnx-fp16' and r.get('jobs') == 149 and not r.get('failures') and not r.get('errors')
print('passed', r.get('passed'), 'variant', r.get('variant_id'), 'jobs', r.get('jobs'), 'failures', len(r.get('failures') or []), 'errors', len(r.get('errors') or []))
sys.exit(0 if ok else 1)
"@

# An id is excused only when row 0's baseline receipt really shows it FAILED: a missing
# receipt excuses nothing.
$baseReceipt = "$receipts/s73-base-py.txt"
$baselinePyFailed = @()
if (Test-Path $baseReceipt) {
    $baselinePyFailed = @(Select-String -Path $baseReceipt -Pattern '^FAILED (\S+)' | ForEach-Object { $_.Matches[0].Groups[1].Value })
}
Write-Output ("baseline py failures excused: [{0}] (receipt {1})" -f ($baselinePyFailed -join ', '), $baseReceipt)

$noProduct = 'no path under packages/, ui/, mcp-server/ or tools/ changes; scope-paths refuses one'
$skipped = @(
    @{ Id = 'ui-types'; Stage = 'static'; Reason = $noProduct },
    @{ Id = 'ui-lint'; Stage = 'static'; Reason = $noProduct },
    @{ Id = 'ui-tests'; Stage = 'full'; Reason = $noProduct },
    @{ Id = 'ui-build'; Stage = 'full'; Reason = $noProduct },
    @{ Id = 'openapi'; Stage = 'full'; Reason = $noProduct },
    @{ Id = 'mcp-types'; Stage = 'full'; Reason = $noProduct },
    @{ Id = 'mcp-tests'; Stage = 'full'; Reason = $noProduct },
    @{ Id = 'mcp-build'; Stage = 'full'; Reason = $noProduct },
    @{ Id = 'ui-electron'; Stage = 'runtime'; Reason = $noProduct },
    @{ Id = 'mcp-audit'; Stage = 'runtime'; Reason = 'live network and YouTube, which the brief forbids' },
    @{ Id = 'build-record'; Stage = 'full'; Reason = 'no installer build' }
)
foreach ($s in $skipped) {
    Write-Output ("{0} stage={1} skipped reason={2}" -f $s.Id, $s.Stage, $s.Reason)
}

# smoke-guarded runs the 149 jobs on FP16 on a fresh copy of package-build's onedir and a fresh
# copy of Session 52's cached models with the guarded graph written by gate-patch.
$gate = "$receipts/s73/gate"
$gateCopy = {
    Remove-Item -Recurse -Force $gate -ErrorAction SilentlyContinue
    New-Item -ItemType Directory -Force -Path "$gate/run" | Out-Null
    Copy-Item -Recurse "$receipts/s52/smoke-models" "$gate/models"
}
$gateBackend = {
    Copy-Item -Recurse 'packaging/dist/avkit-backend' "$gate/run/avkit-backend"
}
$fp16 = 'kokoro-v1.0-onnx/onnx/model_fp16.onnx'
# S16: the smoke stops its backend through its own process handle and records no PID, so list any
# avkit-backend.exe whose path is under the gate's folder. One left running fails the step, and the
# coordinator stops only that PID (Session 56 RULE-2). Nothing is stopped by name.
$leftover = @'
$left = @(Get-CimInstance Win32_Process -Filter "Name='avkit-backend.exe'" | Where-Object { $_.ExecutablePath -like 'C:\Temp\av-kit\s73\gate\*' })
foreach ($p in $left) { Write-Output ("S16: still running pid={0} path={1}" -f $p.ProcessId, $p.ExecutablePath) }
Write-Output ("avkit-backend.exe under the gate folder: {0}" -f $left.Count)
exit $(if ($left.Count) { 1 } else { 0 })
'@

$identity = @('uv', 'run', '--offline', '--no-sync', 'python', "$plan/identity.py")
$py = @('uv', 'run', '--offline', '--no-sync', 'python')
$steps = @(
    @{ Id = 'identity-before'; Stage = 'identity'; Argv = $identity },
    @{ Id = 'py-types'; Stage = 'static'; Argv = @('uv', 'run', '--offline', '--no-sync', 'pyright', 'packages/') },
    @{ Id = 'py-lint'; Stage = 'static'; Argv = @('uv', 'run', '--offline', '--no-sync', 'ruff', 'check', 'packages/', 'tests/') },
    @{ Id = 'plan-lint'; Stage = 'static'; Argv = @('uv', 'run', '--offline', '--no-sync', 'ruff', 'check', "$plan/phase-guard.py", "$plan/fresh-inputs.py") },
    # The two copies keep Session 52's long lines, so they diff cleanly against their sources.
    @{ Id = 'plan-lint-copies'; Stage = 'static'; Argv = @('uv', 'run', '--offline', '--no-sync', 'ruff', 'check', '--extend-ignore', 'E501', "$plan/identity.py", "$plan/issue-resolve.py") },
    @{ Id = 'task-contract'; Stage = 'static'; Argv = $py + @('tools/lint_task_contract.py', '--allowed-builder-classes', 'avkit_builder,avkit_coordinator,avkit_verifier', '--task', "$plan/task.md") },
    @{ Id = 'scope-paths'; Stage = 'static'; Argv = $py + @('-c', $scopePaths) },
    @{ Id = 'phase-guard-selftest'; Stage = 'static'; Argv = $py + @("$plan/phase-guard.py", 'selftest') },
    @{ Id = 'fresh-inputs-selftest'; Stage = 'static'; Argv = $py + @("$plan/fresh-inputs.py", 'selftest') },
    @{ Id = 'identity-selftest'; Stage = 'static'; Argv = $identity + @('--selftest') },
    @{ Id = 'py-tests'; Stage = 'full'; Argv = @('uv', 'run', '--offline', '--no-sync', 'pytest', 'tests/', '--tb=short', '-q', '-rfE') },
    @{ Id = 'state-render'; Stage = 'full'; Argv = $py + @('tools/meu_status.py', 'render', '--check') },
    @{ Id = 'issues-render'; Stage = 'full'; Argv = $py + @('tools/issue_triage.py', 'render', '--check') },
    @{ Id = 'gate-patch'; Stage = 'runtime'; Pre = $gateCopy; Argv = $py + @("$plan/phase-guard.py", 'patch', '--src', "$receipts/s52/smoke-models/$fp16", '--dst', "$gate/models/$fp16", '--out', "$receipts/s73-D6-patch.json") },
    @{ Id = 'patch-same'; Stage = 'runtime'; Argv = $py + @('-c', $patchSame) },
    @{ Id = 'package-build'; Stage = 'runtime'; Argv = $py + @('tools/package_backend.py') },
    @{ Id = 'smoke-guarded'; Stage = 'runtime'; Pre = $gateBackend; Argv = $py + @('tools/smoke_packaged_tts.py', '--phase', 'sentences', '--test-set', 'docs/execution/plans/2026-11-06-tts-load-fp16/fp16-test-set/test-set.json', '--variant', 'kokoro-onnx-fp16', '--backend-dir', "$gate/run/avkit-backend", '--models-dir', "$gate/models", '--out', "$receipts/s73-D6-smoke-guarded.json") },
    @{ Id = 'smoke-guarded-check'; Stage = 'runtime'; Argv = $py + @('-c', $smokePass) },
    @{ Id = 'smoke-leftover'; Stage = 'runtime'; Argv = @('pwsh', '-NoProfile', '-Command', $leftover) },
    @{ Id = 'identity-after'; Stage = 'identity'; Argv = $identity }
)

function Get-TestedState([string]$Receipt) {
    $line = Select-String -Path $Receipt -Pattern '^tested_state ' | Select-Object -Last 1
    if ($null -eq $line) { return $null }
    return $line.Line.Substring('tested_state '.Length).Trim()
}

for ($i = 0; $i -lt $steps.Count; $i++) {
    $step = $steps[$i]
    $receipt = "$receipts/s73-D6-$($step.Id).txt"
    $argv = $step.Argv
    if ($step.Pre) { & $step.Pre }
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
        $before = Get-TestedState "$receipts/s73-D6-identity-before.txt"
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
