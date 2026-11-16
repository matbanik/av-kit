# Session 75 fresh-full gate (task H1-2; implementation-plan.md §Session gate).
# Session 72's shape (docs/execution/plans/2026-11-14-capture-shapes-steps/session-gate.ps1), with
# this plan's scope (§Files Modified, the pins that move, this folder and the project files) and
# these changes: id-length runs on this plan's four new pytest modules (Session 67 RULE-4); there
# are no never-probe, openapi-delta or action-row steps (no union grows, no API shape changes and
# test-ids.ts is not touched); openapi --check runs against the committed snapshot, which this
# plan never writes (an API shape change is a stop, S6); and scope-paths binds to content, not to
# HEAD (Sessions 87 and 75 to 83 share main and may run without commits in between). It diffs the
# tree against row 0's baseline.sha, so a commit made since row 0 is still counted, and it prints
# whether HEAD moved without failing on it. routes/captures.py may change only in comment
# lines (MEU-146 item 4; the route-comment-only step). Another session's plan folder under
# docs/execution/plans/ is reported, never fatal: plan-local files are no input to any suite.
# Runs from the repository root (P:/av-kit, main only per AGENTS.md §Commits) in stage order:
# input identity, then every static check, then the full suites, then the runtime checks, then
# the input identity again. One receipt per id under C:/Temp/av-kit/capture-inbox-probe, named
# s75-D6-<id>.txt. Fail-fast: the first non-zero step stops the gate and every later step is
# printed as not_run. The gate also fails when tested_state differs between its start and its end
# (an input changed while it ran). Read-only apart from the receipts, ui/out (ui-build),
# mcp-server/dist (mcp-build), ui/test-results (ui-electron) and pytest's temp folder, which git
# ignores or which sit outside the repository. No step writes the system clipboard. Nothing here
# reaches the network or YouTube. Exit = the first failing step's code. py-tests runs the whole
# suite (no -x) and keeps Session 49b's baseline rule: pytest exit 1 passes only when every FAILED
# id also FAILED in row 0's s75-base-py.txt, and nothing ERRORs. ui-tests, mcp-tests and
# ui-electron excuse nothing; row 0's receipts record their counts. Skipped, per the plan:
# mcp-audit and build-record.
$ErrorActionPreference = 'Continue'
$root = (git rev-parse --show-toplevel).Trim()
Set-Location $root
$plan = 'docs/execution/plans/2026-11-15-capture-inbox-probe'
$receipts = 'C:/Temp/av-kit/capture-inbox-probe'
New-Item -ItemType Directory -Force -Path $receipts | Out-Null
# lint_task_contract.py recognises the instantiated receipt paths only through RECEIPTS_DIR and
# fails closed (exit 3) when it is unset, which no user or machine scope sets on this host.
$env:RECEIPTS_DIR = 'C:/Temp/av-kit'
$env:PYTHONIOENCODING = 'utf-8'
$env:ELECTRON_RUN_AS_NODE = $null
# RC1 ECN-2 (CLOSEOUT-SELFTEST-ANCESTOR-AGENT-DIR): keep pytest's temp dirs away from the home folder.
$tmp = 'C:\Temp\av-kit\capture-inbox-probe\tmp'
New-Item -ItemType Directory -Force -Path $tmp | Out-Null
$env:TMP = $tmp
$env:TEMP = $tmp
$base = (Get-Content "$plan/baseline.sha").Trim()

# Files Modified, the moved pins, the new files, the project files and the paths
# baseline-dirty.txt already held. Anything else changed since row 0's baseline.sha is S3. So is
# a baseline-dirty.txt path this plan doesn't write whose SHA-256 differs from row 0's (another
# session wrote it while this one ran), other than another session's plan folder; its content
# is hashed, never printed. The OpenAPI snapshot and the MCP audit baseline are refused: no
# REST or MCP shape changes, so this plan never writes them. The refusal binds to row 0's
# content, not to HEAD: a refused path that baseline-dirty.txt already held (an earlier session
# left it changed) passes while its SHA-256 still equals row 0's, and fails as changed_dirty
# otherwise.
$scopePaths = @"
import hashlib, pathlib, subprocess, sys
allowed = {
    'packages/infrastructure/src/avkit_infra/capture/adapter.py',
    'packages/core/src/avkit_core/services/capture.py',
    'packages/core/src/avkit_core/ports/capture.py',
    # Comment lines only (MEU-146 item 4); the route-comment-only step checks the code.
    'packages/api/src/avkit_api/routes/captures.py',
    # The two fakes gain read_shown and shown_tag; no assertion changes.
    'tests/unit/test_capture_service.py',
    'tests/unit/test_capture_export_service.py',
    'tests/orientation_fixtures.py',
    'tests/unit/test_capture_scan_unreadable.py',
    'tests/unit/test_capture_orientation.py',
    'tests/e2e/test_api_capture_scan_unreadable.py',
    'tests/e2e/test_api_capture_orientation.py',
    # The pins that move (§Pins that move).
    'tests/unit/test_capture_export_adapter.py',
    'tests/e2e/test_api_capture_crop.py',
    # AC-146.19 is appended (§Sibling overlap: Session 78 edits launch sites in other specs).
    'ui/tests/e2e/capture-inbox.test.ts',
    'docs/build-plan/09-screenshot-capture.md',
    '.agent/context/meu-status.yaml',
    'docs/BUILD_PLAN.md',
    '.agent/context/meu-registry.md',
    '.agent/context/known-issues.yaml',
    '.agent/context/known-issues.md',
    '.agent/context/grouping/2026-11-15-post-rc3-triage-residuals-session-grouping.md',
    '.agent/context/current-focus.md',
    'docs/execution/metrics.md',
}
ours = set(allowed)
refused = {'openapi.committed.json', '.agent/skills/mcp-tool-audit/resources/baseline-snapshot.json'}
prefixes = ('$plan/', '.agent/context/handoffs/2026-11-15-capture-inbox-probe-', 'docs/execution/reflections/2026-11-15-capture-inbox-probe-')
others = 'docs/execution/plans/'
dirty = pathlib.Path('$plan/baseline-dirty.txt').read_text(encoding='utf-8').splitlines()
changed_dirty, reported = [], []
# Each line is git's porcelain line, a tab, then the file's SHA-256 at row 0.
for line in dirty:
    if not line:
        continue
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
        (reported if path.startswith(others) else changed_dirty).append(path)
# --no-renames: a rename reports both its source deletion and its destination, so moving an
# out-of-scope file into an allowed path still shows the out-of-scope deletion.
# -z: NUL-separated, so a path with spaces or quoting is one entry.
def paths(*args):
    raw = subprocess.run(['git', *args], capture_output=True, check=True).stdout.decode('utf-8')
    return [p for p in raw.split('\0') if p]
head = subprocess.run(['git', 'rev-parse', 'HEAD'], capture_output=True, text=True, check=True).stdout.strip()
out = paths('diff', '--no-renames', '--name-only', '-z', '$base')
out += paths('ls-files', '--others', '--exclude-standard', '-z')
def inside(p):
    return any(p == a or p.startswith(a.rstrip('/') + '/') for a in allowed) or p.startswith(prefixes)
dirty_paths = {ln[3:].partition('	')[0] for ln in dirty if ln}
refused_now = {p for p in refused if p not in dirty_paths}
outside = sorted({p for p in out if not inside(p) or p in refused_now})
extra = [p for p in outside if p in refused_now or not p.startswith(others)]
plans = [p for p in outside if p not in extra]
print('changed paths since', '$base'[:12], ':', len(set(out)), 'outside scope (S3):', extra)
print('other plan folders changed (reported, not fatal):', sorted(set(plans)), reported)
print('head:', head, 'head moved since row 0 (reported, not fatal):', head != '$base')
print('baseline-dirty paths changed since row 0 (S3):', changed_dirty)
sys.exit(1 if extra or changed_dirty else 0)
"@

# MEU-146 item 4 (S6): every line of the route that differs from its row-0 copy is blank or a
# comment on both sides, so the route's code, docstring and OpenAPI text are unchanged.
$routeComment = @'
import difflib, pathlib, sys
rel = 'packages/api/src/avkit_api/routes/captures.py'
a = (pathlib.Path(sys.argv[1]) / rel).read_text(encoding='utf-8').splitlines()
b = pathlib.Path(rel).read_text(encoding='utf-8').splitlines()
def comment(line):
    return not line.strip() or line.strip().startswith('#')
changed, code = 0, []
for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
    if op == 'equal':
        continue
    changed += (i2 - i1) + (j2 - j1)
    code += [f'row0:{n + 1}' for n in range(i1, i2) if not comment(a[n])]
    code += [f'now:{n + 1}' for n in range(j1, j2) if not comment(b[n])]
print('route lines changed against row 0:', changed, 'non-comment lines among them:', code)
sys.exit(1 if code else 0)
'@

# An id is excused only when row 0's baseline receipt really shows it FAILED: a missing
# receipt excuses nothing.
$baseReceipt = "$receipts/s75-base-py.txt"
$baselinePyFailed = @()
if (Test-Path $baseReceipt) {
    $baselinePyFailed = @(Select-String -Path $baseReceipt -Pattern '^FAILED (\S+)' | ForEach-Object { $_.Matches[0].Groups[1].Value })
}
Write-Output ("baseline py failures excused: [{0}] (receipt {1})" -f ($baselinePyFailed -join ', '), $baseReceipt)
Write-Output 'baseline ui failures excused: [] (ui-tests excuses nothing)'
Write-Output 'baseline mcp failures excused: [] (mcp-tests excuses nothing)'
Write-Output 'baseline e2e failures excused: [] (ui-electron excuses nothing)'

$skipped = @(
    @{ Id = 'mcp-audit'; Stage = 'runtime'; Reason = 'live network, YouTube and the installed avkit servers, which the brief forbids' },
    @{ Id = 'build-record'; Stage = 'full'; Reason = 'no release and no package build in this session' }
)
foreach ($s in $skipped) {
    Write-Output ("{0} stage={1} skipped reason={2}" -f $s.Id, $s.Stage, $s.Reason)
}

$identity = @('uv', 'run', '--no-sync', 'python', "$plan/identity.py")
$steps = @(
    @{ Id = 'identity-before'; Stage = 'identity'; Argv = $identity },
    @{ Id = 'py-types'; Stage = 'static'; Argv = @('uv', 'run', '--no-sync', 'pyright', 'packages/') },
    @{ Id = 'py-lint'; Stage = 'static'; Argv = @('uv', 'run', '--no-sync', 'ruff', 'check', 'packages/', 'tests/') },
    @{ Id = 'ui-types'; Stage = 'static'; Argv = @('npm', '--prefix', 'ui', 'run', 'typecheck') },
    @{ Id = 'ui-lint'; Stage = 'static'; Argv = @('npm', '--prefix', 'ui', 'run', 'lint') },
    @{ Id = 'mcp-types'; Stage = 'static'; Argv = @('npm', '--prefix', 'mcp-server', 'run', 'typecheck') },
    @{ Id = 'task-contract'; Stage = 'static'; Argv = @('uv', 'run', '--no-sync', 'python', 'tools/lint_task_contract.py', '--allowed-builder-classes', 'avkit_builder,avkit_coordinator,avkit_verifier', '--task', "$plan/task.md") },
    @{ Id = 'scope-paths'; Stage = 'static'; Argv = @('uv', 'run', '--no-sync', 'python', '-c', $scopePaths) },
    @{ Id = 'route-comment-only'; Stage = 'static'; Argv = @('uv', 'run', '--no-sync', 'python', '-c', $routeComment, "$receipts/row0") },
    @{ Id = 'red-check-selftest'; Stage = 'static'; Argv = @('uv', 'run', '--no-sync', 'python', "$plan/red-check.py", '--selftest') },
    # Every title in the four new pytest modules fits red-check's header pattern (Session 67 RULE-4).
    @{ Id = 'id-length'; Stage = 'static'; Argv = @('uv', 'run', '--no-sync', 'python', "$plan/id-length.py", 'tests/unit/test_capture_scan_unreadable.py', 'tests/unit/test_capture_orientation.py', 'tests/e2e/test_api_capture_scan_unreadable.py', 'tests/e2e/test_api_capture_orientation.py') },
    @{ Id = 'py-tests'; Stage = 'full'; Argv = @('uv', 'run', '--no-sync', 'pytest', 'tests/', '--tb=short', '-q', '-rfE') },
    # No REST shape changes (D-900, D-905): the committed snapshot must still match the app.
    @{ Id = 'openapi'; Stage = 'full'; Argv = @('uv', 'run', '--no-sync', 'python', 'tools/export_openapi.py', '--check', 'openapi.committed.json') },
    @{ Id = 'ui-tests'; Stage = 'full'; Argv = @('npm', '--prefix', 'ui', 'run', 'test') },
    @{ Id = 'ui-build'; Stage = 'full'; Argv = @('npm', '--prefix', 'ui', 'run', 'build') },
    # mcp-build runs first: runner-fake-backend.test.ts reads the served actions from dist.
    @{ Id = 'mcp-build'; Stage = 'full'; Argv = @('npm', '--prefix', 'mcp-server', 'run', 'build') },
    # AC-145.14: the existing list pin (capture.test.ts:24) still passes unchanged.
    @{ Id = 'mcp-tests'; Stage = 'full'; Argv = @('npm', '--prefix', 'mcp-server', 'run', 'test') },
    @{ Id = 'state-render'; Stage = 'full'; Argv = @('uv', 'run', '--no-sync', 'python', 'tools/meu_status.py', 'render', '--check') },
    @{ Id = 'issues-render'; Stage = 'full'; Argv = @('uv', 'run', '--no-sync', 'python', 'tools/issue_triage.py', 'render', '--check') },
    # The capture module against the ui-build output above, with the seam backend, no network:
    # AC-146.19 (Chromium orients a tagged JPEG, MPO and PNG with an EXIF block before the
    # pixels, and never a tagged WebP, an eXIf after IDAT, a raw-profile PNG or an XMP-only
    # JPEG; the fixture builder's report is checked first) and the existing capture specs.
    @{ Id = 'ui-electron'; Stage = 'runtime'; Argv = @('npm', '--prefix', 'ui', 'run', 'test:e2e', '--', 'tests/e2e/capture-inbox.test.ts') },
    @{ Id = 'identity-after'; Stage = 'identity'; Argv = $identity }
)

function Get-TestedState([string]$Receipt) {
    $line = Select-String -Path $Receipt -Pattern '^tested_state ' | Select-Object -Last 1
    if ($null -eq $line) { return $null }
    return $line.Line.Substring('tested_state '.Length).Trim()
}

for ($i = 0; $i -lt $steps.Count; $i++) {
    $step = $steps[$i]
    $receipt = "$receipts/s75-D6-$($step.Id).txt"
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
        $before = Get-TestedState "$receipts/s75-D6-identity-before.txt"
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
