# Session 66 fresh-full gate (task H1-2; implementation-plan.md §Session gate).
# Session 65's shape (docs/execution/plans/2026-11-11-download-failure-visibility/session-gate.ps1),
# with this plan's scope, the settings Electron spec, and the package build, Deno copy, runtime
# smoke and licence steps that MEU-141 needs.
# Runs from the repository root (P:/av-kit, main only per AGENTS.md §Commits) in stage order:
# input identity, then every static check, then the full suites, then the runtime checks, then
# the input identity again. One receipt per id under C:/Temp/av-kit, named s66-D6-<id>.txt.
# Fail-fast: the first non-zero step stops the gate and every later step is printed as not_run.
# The gate also fails when tested_state differs between its start and its end (an input changed
# while it ran). Read-only apart from the receipts, ui/out (ui-build), mcp-server/dist
# (mcp-build), ui/test-results (ui-electron), packaging/build and packaging/dist (package-build,
# deno-copy, licences), which git ignores. Nothing here reaches the network or YouTube.
# Exit = the first failing step's code.
# py-tests runs the whole suite (no -x) and keeps Session 49b's baseline rule: pytest exit 1
# passes only when every FAILED id also FAILED in row 0's s66-base-py.txt, and nothing ERRORs.
# ui-tests, mcp-tests and ui-electron excuse nothing; row 0's receipts record their counts.
# The package steps run only when MEU-141 ran here, read from one fact: active-set.py's set
# (active-meus.txt, written at the split point and checked against D-640 to D-642; task.md
# §Split). MEU-141's status must agree with it: ready_for_review when active, pending when
# deferred to Session 66b. A refused set or a disagreeing status stops the gate (exit 2).
# Skipped, per the plan: mcp-audit (network and YouTube), build-record (no release), the live
# probes (D-642's manual check, after the gate), and the real-FFmpeg module (no FFmpeg change;
# py-tests still runs it). Each is printed with its reason and runs nothing.
$ErrorActionPreference = 'Continue'
$root = (git rev-parse --show-toplevel).Trim()
Set-Location $root
$plan = 'docs/execution/plans/2026-11-12-youtube-client-runtime'
$receipts = 'C:/Temp/av-kit'
# lint_task_contract.py recognises the instantiated receipt paths only through RECEIPTS_DIR and
# fails closed (exit 3) when it is unset, which no user or machine scope sets on this host.
$env:RECEIPTS_DIR = $receipts
$env:PYTHONIOENCODING = 'utf-8'
$env:ELECTRON_RUN_AS_NODE = $null
# RC1 ECN-2 (CLOSEOUT-SELFTEST-ANCESTOR-AGENT-DIR): keep pytest's temp dirs away from the home folder.
$tmp = 'C:\Temp\av-kit\s66\tmp'
New-Item -ItemType Directory -Force -Path $tmp | Out-Null
$env:TMP = $tmp
$env:TEMP = $tmp
$base = (Get-Content "$plan/baseline.sha").Trim()

# Files Modified, the new files, the project files and the paths baseline-dirty.txt already held.
# Anything else changed, or HEAD moving, is S3. So is a baseline-dirty.txt path this plan doesn't
# write whose SHA-256 differs from row 0's (another session wrote it while this one ran); its
# content is hashed, never printed. ui/tests/e2e/test-ids.ts is allowed here because row 2b adds
# one block at its end (S9); its AC-51.6 and AC-81.13 guards run in py-tests and ui-tests.
$scopePaths = @"
import hashlib, pathlib, subprocess, sys
allowed = {
    'packages/infrastructure/src/avkit_infra/youtube/adapter.py',
    'packages/infrastructure/src/avkit_infra/youtube/js_runtime.py',
    'packages/core/src/avkit_core/ports/youtube.py',
    'packages/core/src/avkit_core/services/extract.py',
    'packages/core/src/avkit_core/services/download.py',
    'packages/core/src/avkit_core/services/settings.py',
    'packages/core/src/avkit_core/services/health.py',
    'packages/core/src/avkit_core/domain/health.py',
    'packages/api/src/avkit_api/wiring.py',
    'packages/api/src/avkit_api/schemas/health.py',
    'packages/api/src/avkit_api/schemas/settings.py',
    'packages/api/src/avkit_api/routes/health.py',
    'openapi.committed.json',
    'packages/infrastructure/pyproject.toml',
    'uv.lock',
    'packaging/avkit-backend.spec',
    'packaging/THIRD_PARTY_NOTICES.md',
    'ui/electron-builder.yml',
    '.gitignore',
    'tools/generate_third_party_licenses.py',
    'tools/smoke_packaged_runtime.py',
    'tools/fetch_deno_windows.ps1',
    'mcp-server/src/toolsets/settings.ts',
    'mcp-server/scripts/audit/classify.ts',
    'mcp-server/tests/audit/isolation.test.ts',
    'mcp-server/tests/settings-runtime.test.ts',
    'ui/tests/e2e/test-ids.ts',
    'ui/src/renderer/src/features/settings/SettingsPage.tsx',
    'ui/src/renderer/src/features/settings/settings-schemas.ts',
    'ui/src/renderer/src/features/settings/useSettingsPage.ts',
    'ui/tests/unit/settings-runtime.test.ts',
    'tests/integration/test_youtube_adapter.py',
    'tests/unit/test_domain.py',
    'tests/unit/test_transcript_metadata.py',
    'tests/unit/test_services.py',
    'tests/e2e/real_stack.py',
    'tests/e2e/test_api_error_surface.py',
    'tests/integration/test_download_received_quality.py',
    'tests/integration/test_youtube_client_fallback.py',
    'tests/unit/test_extract_options.py',
    'tests/e2e/test_api_client_fallback.py',
    'tests/unit/test_js_runtime.py',
    'tests/integration/test_js_runtime_wiring.py',
    'tests/e2e/test_api_js_runtime.py',
    'tests/unit/test_fetch_deno.py',
    'tests/integration/test_api_wiring.py',
    'tests/e2e/test_api_health_settings.py',
    'tests/e2e/test_api_auth.py',
    # D-658's third fixture repair (D-662).
    'tests/e2e/api_fakes.py',
    'docs/build-plan/02-infrastructure.md',
    'docs/build-plan/06-gui.md',
    'docs/build-plan/07-distribution.md',
    '.agent/context/known-issues.yaml',
    '.agent/context/known-issues.md',
    '.agent/context/triage-output.yaml',
    '.agent/context/meu-status.yaml',
    'docs/BUILD_PLAN.md',
    '.agent/context/meu-registry.md',
    '.agent/context/grouping/2026-11-10-download-reliability-session-grouping.md',
    '.agent/context/current-focus.md',
    'docs/execution/metrics.md',
}
ours = set(allowed)
refused = set()
prefixes = ('$plan/', '.agent/context/handoffs/2026-11-12-youtube-client-runtime-', 'docs/execution/reflections/2026-11-12-youtube-client-runtime-')
dirty = pathlib.Path('$plan/baseline-dirty.txt').read_text(encoding='utf-8').splitlines()
changed_dirty = []
# Each line is git's porcelain line, a tab, then the file's SHA-256 at row 0.
for line in dirty:
    path, _, recorded = line[3:].partition('\t')
    if not path or not recorded or ' -> ' in path or path.startswith('"'):
        print('baseline-dirty.txt: unreadable line', repr(line))
        sys.exit(2)
    allowed.add(path)
    if path in ours or path.startswith(prefixes):
        continue
    p = pathlib.Path(path)
    now = hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else 'deleted'
    if now != recorded:
        changed_dirty.append(path)
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
extra = sorted({p for p in out if (p not in allowed and not p.startswith(prefixes)) or p in refused})
print('changed paths:', len(set(out)), 'outside scope:', extra, 'head:', head, 'head moved (S3):', moved)
print('baseline-dirty paths changed since row 0 (S3):', changed_dirty)
sys.exit(1 if extra or moved or changed_dirty else 0)
"@

# The active set decides whether the package steps run (task.md §Split), and MEU-141's
# status must agree with it.
$active = (& uv run --no-sync python "$plan/active-set.py" meus | Out-String).Trim()
$setCode = $LASTEXITCODE
Write-Output "active set: $active"
if ($setCode -ne 0) {
    Write-Output 'active-set.py refused; the gate cannot tell which MEUs ran here'
    exit 2
}
$meu141 = (& uv run --no-sync python -c "import sys; sys.path.insert(0, 'tools'); from tools.meu_status.model import load, get_meu; print(get_meu(load(), 'MEU-141')['status'])" | Out-String).Trim()
Write-Output "MEU-141 status: $meu141"
if ($active -eq 'MEU-140 MEU-141' -and $meu141 -eq 'ready_for_review') {
    $packageSteps = $true
} elseif ($active -eq 'MEU-140' -and $meu141 -eq 'pending') {
    $packageSteps = $false
} else {
    Write-Output "MEU-141 status $meu141 disagrees with the active set $active"
    exit 2
}

# An id is excused only when row 0's baseline receipt really shows it FAILED: a missing
# receipt excuses nothing.
$baseReceipt = "$receipts/s66-base-py.txt"
$baselinePyFailed = @()
if (Test-Path $baseReceipt) {
    $baselinePyFailed = @(Select-String -Path $baseReceipt -Pattern '^FAILED (\S+)' | ForEach-Object { $_.Matches[0].Groups[1].Value })
}
Write-Output ("baseline py failures excused: [{0}] (receipt {1})" -f ($baselinePyFailed -join ', '), $baseReceipt)
Write-Output 'baseline ui failures excused: [] (ui-tests excuses nothing)'
Write-Output 'baseline mcp failures excused: [] (mcp-tests excuses nothing)'
Write-Output 'baseline e2e failures excused: [] (ui-electron excuses nothing)'

$skipped = @(
    @{ Id = 'mcp-audit'; Stage = 'runtime'; Reason = 'live network and YouTube, which the brief forbids' },
    @{ Id = 'build-record'; Stage = 'full'; Reason = 'no release; the NSIS build runs in row 5 (D-650)' },
    @{ Id = 'live-probes'; Stage = 'runtime'; Reason = 'network and YouTube; a recorded manual check after the gate, each probe brought to Mat first (D-642)' },
    @{ Id = 'real-ffmpeg'; Stage = 'runtime'; Reason = 'no FFmpeg change; py-tests still runs the module' }
)
if (-not $packageSteps) {
    foreach ($id in 'package-build', 'deno-copy', 'runtime-smoke', 'licences') {
        $skipped += @{ Id = $id; Stage = 'runtime'; Reason = 'MEU-141 moved to Session 66b' }
    }
}
foreach ($s in $skipped) {
    Write-Output ("{0} stage={1} skipped reason={2}" -f $s.Id, $s.Stage, $s.Reason)
}

# The pinned Deno beside the fresh onedir, as the installer lays it out: bundled_deno() reads
# Path(sys.executable).resolve().parent.parent / "deno" / "deno.exe". The fetched zip stays
# behind. packaging/dist/deno is git-ignored and this gate's own output.
$denoCopy = @'
import hashlib, pathlib, shutil, sys
src = pathlib.Path("packaging/deno-win64")
dst = pathlib.Path("packaging/dist/deno")
if not (src / "deno.exe").is_file() or not (src / "LICENSE.md").is_file():
    print("deno-copy: packaging/deno-win64 lacks deno.exe or LICENSE.md")
    sys.exit(1)
if dst.exists():
    shutil.rmtree(dst)
dst.mkdir(parents=True)
for name in ("deno.exe", "LICENSE.md"):
    shutil.copy2(src / name, dst / name)
    print(f"deno-copy {name} sha256={hashlib.sha256((dst / name).read_bytes()).hexdigest()}")
print("deno-copy:", sorted(p.name for p in dst.iterdir()))
'@

$identity = @('uv', 'run', '--no-sync', 'python', "$plan/identity.py")
$pyLint = @('uv', 'run', '--no-sync', 'ruff', 'check', 'packages/', 'tests/', 'tools/generate_third_party_licenses.py')
if ($packageSteps) { $pyLint += 'tools/smoke_packaged_runtime.py' }
$steps = @(
    @{ Id = 'identity-before'; Stage = 'identity'; Argv = $identity },
    @{ Id = 'py-types'; Stage = 'static'; Argv = @('uv', 'run', '--no-sync', 'pyright', 'packages/') },
    # tools/ as a whole fails ruff at baseline in files this plan doesn't touch; the tools files
    # this plan writes are checked by name, the smoke only when MEU-141 ran here (row 5 makes it).
    @{ Id = 'py-lint'; Stage = 'static'; Argv = $pyLint },
    @{ Id = 'ui-types'; Stage = 'static'; Argv = @('npm', '--prefix', 'ui', 'run', 'typecheck') },
    @{ Id = 'ui-lint'; Stage = 'static'; Argv = @('npm', '--prefix', 'ui', 'run', 'lint') },
    @{ Id = 'task-contract'; Stage = 'static'; Argv = @('uv', 'run', '--no-sync', 'python', 'tools/lint_task_contract.py', '--allowed-builder-classes', 'avkit_builder,avkit_coordinator,avkit_verifier', '--task', "$plan/task.md") },
    @{ Id = 'scope-paths'; Stage = 'static'; Argv = @('uv', 'run', '--no-sync', 'python', '-c', $scopePaths) },
    @{ Id = 'red-check-selftest'; Stage = 'static'; Argv = @('uv', 'run', '--no-sync', 'python', "$plan/red-check.py", '--selftest') },
    @{ Id = 'active-set'; Stage = 'static'; Argv = @('uv', 'run', '--no-sync', 'python', "$plan/active-set.py", 'check') },
    @{ Id = 'py-tests'; Stage = 'full'; Argv = @('uv', 'run', '--no-sync', 'pytest', 'tests/', '--tb=short', '-q', '-rfE') },
    # With MEU-141 the snapshot carries JsRuntimeOut, DependenciesOut.js_runtime and
    # SettingsPutIn.deno_path; without it, nothing changes. H1-4 proves the delta either way.
    @{ Id = 'openapi'; Stage = 'full'; Argv = @('uv', 'run', '--no-sync', 'python', 'tools/export_openapi.py', '--check', 'openapi.committed.json') },
    @{ Id = 'ui-tests'; Stage = 'full'; Argv = @('npm', '--prefix', 'ui', 'run', 'test') },
    @{ Id = 'ui-build'; Stage = 'full'; Argv = @('npm', '--prefix', 'ui', 'run', 'build') },
    @{ Id = 'mcp-types'; Stage = 'full'; Argv = @('npm', '--prefix', 'mcp-server', 'run', 'typecheck') },
    # mcp-build runs first: runner-fake-backend.test.ts reads the served actions from dist.
    @{ Id = 'mcp-build'; Stage = 'full'; Argv = @('npm', '--prefix', 'mcp-server', 'run', 'build') },
    @{ Id = 'mcp-tests'; Stage = 'full'; Argv = @('npm', '--prefix', 'mcp-server', 'run', 'test') },
    @{ Id = 'state-render'; Stage = 'full'; Argv = @('uv', 'run', '--no-sync', 'python', 'tools/meu_status.py', 'render', '--check') },
    @{ Id = 'issues-render'; Stage = 'full'; Argv = @('uv', 'run', '--no-sync', 'python', 'tools/issue_triage.py', 'render', '--check') },
    # The Settings module against the ui-build output above: the Deno path field and the runtime
    # line run in the real app with the seam backend, no network.
    @{ Id = 'ui-electron'; Stage = 'runtime'; Argv = @('npm', '--prefix', 'ui', 'run', 'test:e2e', '--', 'tests/e2e/settings.test.ts') }
)
if ($packageSteps) {
    $steps += @(
        @{ Id = 'package-build'; Stage = 'runtime'; Argv = @('uv', 'run', '--no-sync', 'python', 'tools/package_backend.py') },
        @{ Id = 'deno-copy'; Stage = 'runtime'; Argv = @('uv', 'run', '--no-sync', 'python', '-c', $denoCopy) },
        # AC-141.12's Green half on the fresh build, offline.
        @{ Id = 'runtime-smoke'; Stage = 'runtime'; Argv = @('uv', 'run', '--no-sync', 'python', 'tools/smoke_packaged_runtime.py', '--backend-dir', 'packaging/dist/avkit-backend', '--out', "$receipts/s66-D6-smoke.json") },
        # The licence gate on the fresh build: yt-dlp-ejs and Deno listed, nothing GPL beyond the allow-list.
        @{ Id = 'licences'; Stage = 'runtime'; Argv = @('uv', 'run', '--no-sync', 'python', 'tools/generate_third_party_licenses.py') }
    )
}
$steps += @(
    @{ Id = 'identity-after'; Stage = 'identity'; Argv = $identity }
)

function Get-TestedState([string]$Receipt) {
    $line = Select-String -Path $Receipt -Pattern '^tested_state ' | Select-Object -Last 1
    if ($null -eq $line) { return $null }
    return $line.Line.Substring('tested_state '.Length).Trim()
}

for ($i = 0; $i -lt $steps.Count; $i++) {
    $step = $steps[$i]
    $receipt = "$receipts/s66-D6-$($step.Id).txt"
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
        $before = Get-TestedState "$receipts/s66-D6-identity-before.txt"
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
