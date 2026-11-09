# Session 57 fresh-full gate (task H1-2; implementation-plan.md Verification Plan §5).
# RC1's gate (docs/execution/plans/2026-11-03-release-rc1/session-gate.ps1) with this plan's scope,
# receipts and audit rule, and Session 56's baseline rule. Runs PROFILE D6 from the repository root
# (P:/av-kit, main only per AGENTS.md §Commits) in stage order: input identity, then every static
# check, then the full suites, then the runtime runs, then the input identity again. One receipt per
# id under C:/Temp/av-kit, named s57-D6-<id>.txt. Fail-fast: the first non-zero step stops the gate
# and every later step is printed as not_run. The gate also fails when tested_state differs between
# its start and its end (an input changed while it ran). Read-only apart from the receipts, ui/out,
# ui/out-e2e, mcp-server/dist and the E2E app data; all are ignored or outside the checkout.
# Exit = the first failing step's code.
# py-tests runs the whole suite (no -x) and keeps Session 49b's baseline rule: pytest exit 1 passes
# only when every FAILED id also FAILED in row 0's s57-base-py.txt, and nothing ERRORs.
# ui-tests and mcp-tests excuse nothing; row 0's receipts record their counts.
# mcp-audit runs last because it uses real YouTube traffic and the real screen (named in the plan,
# D-464). mcp-audit-clear runs just before it, and fail-fast stops the gate if the old output can't
# be removed, because a crashed Node process also exits 1 and the rule must never read an earlier
# run's summary. Exit 0 passes. Exit 1 continues only when audit-rule.py finds the caption block
# (YOUTUBE-CAPTIONS-IP-BLOCK) is the one thing wrong, in MEU-116's shape (the job pauses on the
# block and the later transcript steps are blocked), in a summary from this HEAD, and proves it with
# a direct caption fetch through the product's adapter. That isn't a clean audit: the report stays
# non-pass and the gate's last line says INCOMPLETE VERIFICATION. The report stays under C:/Temp so
# tested_state doesn't move; H1-3 copies it into .agent/context/MCP/. The baseline is never
# refreshed here.
$ErrorActionPreference = 'Continue'
$root = (git rev-parse --show-toplevel).Trim()
Set-Location $root
$plan = 'docs/execution/plans/2026-11-08-release-rc2'
$receipts = 'C:/Temp/av-kit'
# lint_task_contract.py recognises the instantiated receipt paths only through RECEIPTS_DIR and
# fails closed (exit 3) when it is unset, which no user or machine scope sets on this host.
$env:RECEIPTS_DIR = $receipts
$env:PYTHONIOENCODING = 'utf-8'
$env:ELECTRON_RUN_AS_NODE = $null
# RC1 ECN-2 (CLOSEOUT-SELFTEST-ANCESTOR-AGENT-DIR): keep pytest's temp dirs away from the home folder.
$tmp = "$receipts/s57/tmp"
New-Item -ItemType Directory -Force -Path $tmp | Out-Null
$env:TMP = $tmp
$env:TEMP = $tmp
$base = (Get-Content "$plan/baseline.sha").Trim()
$head = (git rev-parse HEAD).Trim()
$auditOut = "$receipts/s57-D6-mcp-audit"
# BUILD_RECORD: rows 4 to 7 tested this installer, so it must still match the tree and its bytes.
$record = 'C:/Temp/av-kit/s57/build-record.json'

# Files Modified, the project files and the paths baseline-dirty.txt already held. Anything
# else changed, ui/tests/e2e/test-ids.ts changing, or HEAD moving, is S3.
$scopePaths = @"
import pathlib, subprocess, sys
allowed = {
    'ui/package.json',
    'ui/package-lock.json',
    'mcp-server/package.json',
    'mcp-server/package-lock.json',
    'mcp-server/src/index.ts',
    'pyproject.toml',
    'packages/api/pyproject.toml',
    'packages/core/pyproject.toml',
    'packages/infrastructure/pyproject.toml',
    'packages/api/src/avkit_api/__init__.py',
    'uv.lock',
    'openapi.committed.json',
    'packaging/THIRD_PARTY_NOTICES.md',
    'tests/unit/test_release_packaging.py',
    'tests/unit/test_packaging_installer.py',
    # Only if the watch item fails again (D-470).
    'ui/tests/e2e/transcript-queue.test.ts',
    '.agent/context/known-issues.yaml',
    '.agent/context/known-issues.md',
    'docs/build-plan/07-distribution.md',
    '.agent/context/meu-status.yaml',
    'docs/BUILD_PLAN.md',
    '.agent/context/meu-registry.md',
    '.agent/context/grouping/2026-11-04-rc2-triage-residuals-session-grouping.md',
    '.agent/context/current-focus.md',
    '.agent/context/MCP/mcp-tool-audit-report.md',
    'docs/execution/metrics.md',
}
refused = {'ui/tests/e2e/test-ids.ts'}
dirty = pathlib.Path('$plan/baseline-dirty.txt').read_text(encoding='utf-8').splitlines()
# Each line is git's porcelain line, a tab, then the file's SHA-256 at row 0.
for line in dirty:
    path = line[3:].split('\t', 1)[0]
    if not path or ' -> ' in path or path.startswith('"'):
        print('baseline-dirty.txt: unreadable line', repr(line))
        sys.exit(2)
    allowed.add(path)
prefixes = ('$plan/', 'docs/releases/v0.1.0-rc.2', 'docs/releases/publish-checklist-v0.1.0-rc.2', '.agent/context/handoffs/2026-11-08-release-rc2-', 'docs/execution/reflections/2026-11-08-release-rc2-')
# --no-renames: a rename reports both its source deletion and its destination, so moving an
# out-of-scope file into an allowed path still shows the out-of-scope deletion.
# -z: NUL-separated, so a path with spaces or quoting is one entry.
def paths(*args):
    raw = subprocess.run(['git', *args], capture_output=True, check=True).stdout.decode('utf-8')
    return [p for p in raw.split('\0') if p]
head = subprocess.run(['git', 'rev-parse', 'HEAD'], capture_output=True, text=True, check=True).stdout.strip()
# Mat's S3 ruling A (2026-11-09): HEAD may sit on the commits ruled-commits.txt names, and only
# those, when baseline.sha is their ancestor and each touches only docs/ or .agent/ paths outside
# this plan's own prefixes. Any other commit, or a ruled one that touches more, is still S3.
ruled = set(pathlib.Path('$plan/ruled-commits.txt').read_text(encoding='utf-8').split())
between = set(subprocess.run(['git', 'rev-list', '$base..' + head], capture_output=True, text=True, check=True).stdout.split())
ancestor = subprocess.run(['git', 'merge-base', '--is-ancestor', '$base', head]).returncode == 0
ruled_ok = ancestor and between <= ruled
for c in sorted(between & ruled):
    touched = paths('diff-tree', '--no-commit-id', '--no-renames', '-r', '--name-only', '-z', c)
    wide = [p for p in touched if not p.startswith(('docs/', '.agent/')) or p.startswith(prefixes)]
    print('ruled commit', c[:7], 'paths:', len(touched), 'outside docs/.agent or in this plan:', wide)
    ruled_ok = ruled_ok and not wide
print('commits since baseline:', len(between), 'all ruled:', between <= ruled, 'baseline is ancestor:', ancestor)
moved = head != '$base' and not ruled_ok
out = paths('diff', '--no-renames', '--name-only', '-z', head)
out += paths('ls-files', '--others', '--exclude-standard', '-z')
extra = sorted({p for p in out if (p not in allowed and not p.startswith(prefixes)) or p in refused})
print('changed paths:', len(set(out)), 'outside scope:', extra, 'head:', head, 'head moved (S3):', moved)
sys.exit(1 if extra or moved else 0)
"@

# An id is excused only when row 0's baseline receipt really shows it FAILED: a missing
# receipt excuses nothing.
$baseReceipt = "$receipts/s57-base-py.txt"
$baselinePyFailed = @()
if (Test-Path $baseReceipt) {
    $baselinePyFailed = @(Select-String -Path $baseReceipt -Pattern '^FAILED (\S+)' | ForEach-Object { $_.Matches[0].Groups[1].Value })
}
Write-Output ("baseline py failures excused: [{0}] (receipt {1})" -f ($baselinePyFailed -join ', '), $baseReceipt)
Write-Output 'baseline ui failures excused: [] (ui-tests excuses nothing)'
Write-Output 'baseline mcp failures excused: [] (mcp-tests excuses nothing)'

$identity = @('uv', 'run', 'python', "$plan/identity.py")
# The Electron suite's gitignored prerequisites: the isolated primitive harness (AC-51.7) and the
# deterministic region-picker stub (capture-picker.test.ts names build:picker-stub). The full
# Electron suite runs because the release carries every page.
$harnessBuild = "`$env:AVKIT_PRIMITIVE_HARNESS_BUILD='1'; npm --prefix ui run build -- --outDir '$root/ui/out-e2e'; exit `$LASTEXITCODE"
$steps = @(
    @{ Id = 'identity-before'; Stage = 'identity'; Argv = $identity },
    @{ Id = 'py-types'; Stage = 'static'; Argv = @('uv', 'run', 'pyright', 'packages/') },
    @{ Id = 'py-lint'; Stage = 'static'; Argv = @('uv', 'run', 'ruff', 'check', 'packages/', 'tests/') },
    @{ Id = 'ui-types'; Stage = 'static'; Argv = @('npm', '--prefix', 'ui', 'run', 'typecheck') },
    @{ Id = 'ui-lint'; Stage = 'static'; Argv = @('npm', '--prefix', 'ui', 'run', 'lint') },
    @{ Id = 'mcp-types'; Stage = 'static'; Argv = @('npm', '--prefix', 'mcp-server', 'run', 'typecheck') },
    @{ Id = 'task-contract'; Stage = 'static'; Argv = @('uv', 'run', 'python', 'tools/lint_task_contract.py', '--allowed-builder-classes', 'avkit_builder,avkit_coordinator,avkit_verifier', '--task', "$plan/task.md") },
    @{ Id = 'scope-paths'; Stage = 'static'; Argv = @('uv', 'run', 'python', '-c', $scopePaths) },
    @{ Id = 'red-check-selftest'; Stage = 'static'; Argv = @('uv', 'run', 'python', "$plan/red-check.py", '--selftest') },
    @{ Id = 'build-identity-selftest'; Stage = 'static'; Argv = @('uv', 'run', 'python', "$plan/build-identity.py", '--selftest') },
    @{ Id = 'audit-rule-selftest'; Stage = 'static'; Argv = @('uv', 'run', 'python', "$plan/audit-rule.py", '--selftest') },
    @{ Id = 'audit-clear-selftest'; Stage = 'static'; Argv = @('pwsh', '-NoProfile', '-File', "$plan/audit-clear.ps1", '-Selftest') },
    @{ Id = 'py-tests'; Stage = 'full'; Argv = @('uv', 'run', 'pytest', 'tests/', '--tb=short', '-q', '-rfE') },
    @{ Id = 'ui-tests'; Stage = 'full'; Argv = @('npm', '--prefix', 'ui', 'run', 'test') },
    # G-1 (S2 decision 2026-10-16): build before the tests, which load mcp-server/dist (RULE-1).
    @{ Id = 'mcp-build'; Stage = 'full'; Argv = @('npm', '--prefix', 'mcp-server', 'run', 'build') },
    @{ Id = 'mcp-tests'; Stage = 'full'; Argv = @('npm', '--prefix', 'mcp-server', 'run', 'test') },
    @{ Id = 'ui-build'; Stage = 'full'; Argv = @('npm', '--prefix', 'ui', 'run', 'build') },
    @{ Id = 'ui-harness-build'; Stage = 'full'; Argv = @('pwsh', '-NoProfile', '-Command', $harnessBuild) },
    @{ Id = 'ui-picker-stub'; Stage = 'full'; Argv = @('npm', '--prefix', 'ui', 'run', 'build:picker-stub') },
    @{ Id = 'openapi'; Stage = 'full'; Argv = @('uv', 'run', 'python', 'tools/export_openapi.py', '--check', 'openapi.committed.json') },
    @{ Id = 'state-render'; Stage = 'full'; Argv = @('uv', 'run', 'python', 'tools/meu_status.py', 'render', '--check') },
    @{ Id = 'issues-render'; Stage = 'full'; Argv = @('uv', 'run', 'python', 'tools/issue_triage.py', 'render', '--check') },
    @{ Id = 'build-record'; Stage = 'full'; Argv = @('uv', 'run', 'python', "$plan/build-identity.py", '--verify-record', $record) },
    @{ Id = 'ui-electron'; Stage = 'runtime'; Argv = @('npm', '--prefix', 'ui', 'run', 'test:e2e') },
    @{ Id = 'mcp-audit-clear'; Stage = 'runtime'; Argv = @('pwsh', '-NoProfile', '-File', "$plan/audit-clear.ps1", '-Dir', $auditOut) },
    @{ Id = 'mcp-audit'; Stage = 'runtime'; Argv = @('npm', '--prefix', 'mcp-server', 'run', 'audit', '--', '--mode', 'authoritative', '--baseline', "$root/.agent/skills/mcp-tool-audit/resources/baseline-snapshot.json", '--report', "$auditOut/mcp-tool-audit-report.md", '--out', $auditOut, '--agent', 'claude-code') },
    @{ Id = 'identity-npm'; Stage = 'identity'; Argv = @('npm', '--prefix', 'ui', 'ls', 'electron', '@playwright/test') },
    @{ Id = 'identity-after'; Stage = 'identity'; Argv = $identity }
)

function Get-TestedState([string]$Receipt) {
    $line = Select-String -Path $Receipt -Pattern '^tested_state ' | Select-Object -Last 1
    if ($null -eq $line) { return $null }
    return $line.Line.Substring('tested_state '.Length).Trim()
}

$auditTolerated = $false
for ($i = 0; $i -lt $steps.Count; $i++) {
    $step = $steps[$i]
    $receipt = "$receipts/s57-D6-$($step.Id).txt"
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
    if ($code -eq 1 -and $step.Id -eq 'mcp-audit') {
        $ruleReceipt = "$receipts/s57-D6-mcp-audit-rule.txt"
        & rtk proxy uv run python "$plan/audit-rule.py" "$auditOut/mcp-audit-summary.json" --head $head *> $ruleReceipt
        $ruleCode = $LASTEXITCODE
        Get-Content $ruleReceipt | Select-Object -Last 12
        Write-Output ("mcp-audit audit rule: exit={0} receipt={1}" -f $ruleCode, $ruleReceipt)
        if ($ruleCode -eq 0) {
            $code = 0
            $auditTolerated = $true
        }
    }
    if ($code -eq 0 -and $step.Id -eq 'identity-after') {
        $before = Get-TestedState "$receipts/s57-D6-identity-before.txt"
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
if ($auditTolerated) {
    Write-Output 'session-gate: INCOMPLETE VERIFICATION: every other step exits 0, but the authoritative audit stays non-pass. Transcript is not verified end to end while YouTube blocks captions (YOUTUBE-CAPTIONS-IP-BLOCK); the job paused on the block as MEU-116 requires.'
    exit 0
}
Write-Output 'session-gate: all steps exit 0'
exit 0
