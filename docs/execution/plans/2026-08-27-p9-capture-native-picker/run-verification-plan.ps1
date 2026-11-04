# Single executable owner of the Verification Plan section list (task row H1-2).
#
# Round-11 trim. This file used to carry ~400 lines of deferral adjudication: a Playwright /
# vitest JSON report enumerator, a failure-block partitioner, cause-pattern totality in two
# directions, and a run-nonce identity check. That machinery guarded a 200-line C# helper and
# it twice passed for the wrong reason under its own mutation tests. It is deleted.
#
# What remains is the rule that actually matters, stated once: a step marked `deferrable` may
# fail ONLY when its disposition file says `BLOCKED=yes`, satisfies the shared `[B]` evidence
# contract (objective class, registered follow-up, real receipt - Test-BlockedEvidence in
# lib-disposition.ps1, per AGENTS.md), and names an ERROR_SIGNATURE that appears in THAT step's
# own receipt. Every other step blocks unconditionally. Three steps are deferrable and each is
# deferrable for the same objective reason - they need hardware the agent sandbox may not have
# (a display, a real desktop, an installable Windows target).
param([switch]$SelfTest, [switch]$List)
$ErrorActionPreference = 'Stop'
$root = $PSScriptRoot
$setsPath = Join-Path $root 'named-sets.json'
if (-not (Test-Path -LiteralPath $setsPath)) { Write-Error ('missing NAMED_SETS_FILE ' + $setsPath); exit 1 }
. (Join-Path $root 'lib-disposition.ps1')
$sets = Get-Content -LiteralPath $setsPath -Raw | ConvertFrom-Json
$out = 'C:/Temp/av-kit'

$steps = @(
    @{ id = '0';  name = 'ORACLE_SELFTESTS';     gate = 'assert-oracle-selftests.ps1'; args = @();             receipt = "$out/oracle-selftests.txt" },
    @{ id = '1';  name = 'DOTNET_TESTS';         exe  = 'dotnet'; args = @('test', [string]$sets.PICKER_TESTS_DIR, '-c', 'Release', '--filter', 'Category!=RealDesktop'); receipt = "$out/dotnet-test.txt" },
    @{ id = '1b'; name = 'DOTNET_REALDESKTOP';   exe  = 'dotnet'; args = @('test', [string]$sets.PICKER_TESTS_DIR, '-c', 'Release', '--filter', 'Category=RealDesktop'); receipt = [string]$sets.REALDESKTOP_RECEIPT; deferrable = $true; disposition = [string]$sets.REALDESKTOP_DISPOSITION_FILE },
    @{ id = '2';  name = 'PACKAGING_CLEAN_PATH'; gate = 'assert-packaging-clean.ps1';  args = @();             receipt = "$out/packaging-clean.txt" },
    @{ id = '2b'; name = 'PACKAGING_INSTALLED';  gate = 'assert-packaging-clean.ps1';  args = @('-Installed'); receipt = [string]$sets.PACKAGING_INSTALLED_RECEIPT; deferrable = $true; disposition = [string]$sets.PACKAGING_DISPOSITION_FILE },
    @{ id = '3';  name = 'UI_UNIT';              exe  = 'npm'; args = @('--prefix', 'ui', 'test');             receipt = "$out/ui-test.txt" },
    @{ id = '4a'; name = 'UI_TYPECHECK';         exe  = 'npm'; args = @('--prefix', 'ui', 'run', 'typecheck'); receipt = "$out/ui-typecheck.txt" },
    @{ id = '4b'; name = 'UI_LINT';              exe  = 'npm'; args = @('--prefix', 'ui', 'run', 'lint');      receipt = "$out/ui-lint.txt" },
    @{ id = '5a'; name = 'OVERLAY_DELETION';     gate = 'assert-overlay-deleted.ps1';  args = @();             receipt = "$out/overlay-deletion.txt" },
    @{ id = '6';  name = 'REGISTRY_DRIFT';       exe  = 'uv'; args = @('run', 'python', 'tools/meu_status.py', 'render', '--check'); receipt = "$out/drift-check.txt" },
    @{ id = '7';  name = 'PY_CORE_TESTS';        exe  = 'uv'; args = @('run', 'pytest', [string]$sets.CAPTURE_SERVICE_TEST_FILE, '-q'); receipt = "$out/pytest-core.txt" },
    @{ id = '8';  name = 'OPENAPI_DRIFT';        exe  = 'uv'; args = @('run', 'python', 'tools/export_openapi.py', '--check', 'openapi.committed.json'); receipt = "$out/openapi-check.txt" },
    @{ id = '8a'; name = 'BUILD_PLAN_HUB';       gate = 'assert-build-plan-hub.ps1';   args = @();             receipt = "$out/build-plan-hub.txt" },
    @{ id = '9a'; name = 'E2E_WIRED';            gate = 'assert-e2e-wired.ps1';        args = @('-Mode', 'Wired'); receipt = "$out/e2e-wired.txt" },
    @{ id = '9a1'; name = 'ARM_E2E_CAPTURE';     gate = 'arm-run.ps1';                 args = @('-Name', 'e2e-capture'); receipt = "$out/arm-e2e-capture.txt" },
    @{ id = '9b'; name = 'UI_E2E';               exe  = 'npm'; args = @('--prefix', 'ui', 'run', [string]$sets.E2E_SCRIPT); receipt = "$out/ui-e2e.txt"; deferrable = $true; disposition = [string]$sets.E2E_DISPOSITION_FILE },
    @{ id = '9c'; name = 'E2E_CAPTURE_RUN';      exe  = 'npm'; args = @('--prefix', 'ui', 'run', [string]$sets.E2E_CAPTURE_SCRIPT); receipt = [string]$sets.E2E_BLOCKED_RECEIPT; env = @{ ([string]$sets.E2E_JSON_ENV) = [string]$sets.E2E_EXECUTED_RECEIPT }; deferrable = $true; disposition = [string]$sets.E2E_DISPOSITION_FILE },
    @{ id = '9d'; name = 'E2E_EXECUTED';         gate = 'assert-e2e-wired.ps1';        args = @('-Mode', 'Executed'); receipt = "$out/e2e-executed.txt" }
)

# The single deferral rule. Returns $null when the failure is excused, else the refusal reason.
function Resolve-StepExcuse {
    param([hashtable]$Step, [string]$Receipt, [string[]]$Sources)
    if (-not $Sources) { $Sources = @($sets.FOLLOWUP_SOURCES) }
    $file = [string]$Step.disposition
    if ([string]::IsNullOrWhiteSpace($file)) { return 'step is deferrable but names no disposition file' }
    if (-not (Test-Path -LiteralPath $file)) { return 'missing disposition file ' + $file + ' - a failing step is a failure until a [B] is filed for it' }
    $map = Get-DispositionMap -Body (Get-Content -LiteralPath $file -Raw)
    if ([string]$map['BLOCKED'] -ne 'yes') { return 'disposition says BLOCKED=' + [string]$map['BLOCKED'] + ' - a red run with no filed blocker is a failure' }
    $err = Test-BlockedEvidence -Map $map -Classes @($sets.BLOCKED_CLASSES) -ErrorClasses @($sets.BLOCKED_ERROR_CLASSES) `
        -FollowupPattern ([string]$sets.FOLLOWUP_PATTERN) -FollowupSources $Sources -RequiredReceipt $Receipt
    if ($null -ne $err) { return $err }
    $sig = [string]$map['ERROR_SIGNATURE']
    if ([string]::IsNullOrWhiteSpace($sig)) { return 'BLOCKED=yes with no ERROR_SIGNATURE' }
    $body = Get-Content -LiteralPath $Receipt -Raw
    if ($null -eq $body -or $body.IndexOf($sig) -lt 0) {
        return 'ERROR_SIGNATURE "' + $sig + '" does not appear in this step''s own receipt ' + $Receipt + ' - the blocker is asserted, not reproduced here'
    }
    return $null
}

if ($List) {
    $steps | ForEach-Object { '{0,-4} {1,-22} {2}' -f $_.id, $_.name, $_.receipt }
    exit 0
}

if ($SelfTest) {
    # The inventory must be real before it is scheduled: every gate a section names exists.
    foreach ($s in $steps) {
        if ($s.ContainsKey('gate')) {
            $p = Join-Path $root ([string]$s.gate)
            if (-not (Test-Path -LiteralPath $p)) { Write-Error ('section ' + $s.id + ' names a gate script that does not exist: ' + $p); exit 1 }
        } elseif (-not $s.ContainsKey('exe')) {
            Write-Error ('section ' + $s.id + ' names neither a gate nor an executable'); exit 1
        }
        if ($s.deferrable -and [string]::IsNullOrWhiteSpace([string]$s.disposition)) {
            Write-Error ('section ' + $s.id + ' is deferrable but declares no disposition file'); exit 1
        }
    }
    if (@($sets.BLOCKED_CLASSES).Count -lt 1 -or @($sets.BLOCKED_ERROR_CLASSES).Count -lt 1) {
        Write-Error 'BLOCKED_CLASSES / BLOCKED_ERROR_CLASSES are empty - the [B] contract would accept any class'; exit 1
    }

    # J-oracles for the one rule this runner owns. Each replays a way a red run could be laundered.
    $tmp = Join-Path ([System.IO.Path]::GetTempPath()) ('avkit-vp-' + [guid]::NewGuid().ToString('N'))
    New-Item -ItemType Directory -Path $tmp -Force | Out-Null
    try {
        $sig = 'Error: browserType.launch: Missing X server or $DISPLAY'
        $own = Join-Path $tmp 'own.txt'
        Set-Content -LiteralPath $own -Value ("Running 3 tests`n" + $sig)
        $other = Join-Path $tmp 'other.txt'
        Set-Content -LiteralPath $other -Value "1 failed`n  expected 200, received 500 (POST /captures)"
        $dispFile = Join-Path $tmp 'disp.txt'
        $fx = @(
            'BLOCKED=yes',
            'CLASS=external-error',
            'REASON=no display in the agent sandbox',
            'FOLLOWUP=E2E-SANDBOX-NODISPLAY',
            ('ERROR_SIGNATURE=' + $sig),
            ('RECEIPT=' + $own)
        ) -join "`n"
        Set-Content -LiteralPath $dispFile -Value $fx
        $step = @{ id = 'T'; deferrable = $true; disposition = $dispFile }
        # The follow-up registry is a repo fact, not a gate fact: register the fixture id in a
        # fixture source so these oracles test the rule and not today's known-issues.md.
        $fxSource = Join-Path $tmp 'known-issues.md'
        Set-Content -LiteralPath $fxSource -Value "| E2E-SANDBOX-NODISPLAY | Electron cannot open a display in the agent sandbox |"
        $fxSources = @($fxSource)

        # J1 positive control - a genuinely blocked step, evidenced in its own receipt, is excused.
        $e = Resolve-StepExcuse -Step $step -Receipt $own -Sources $fxSources
        if ($null -ne $e) { Write-Error ('SELFTEST J1 refused a genuinely blocked step: ' + $e); exit 1 }
        # J2 - the signature must appear in THIS step's receipt, not merely somewhere in the run.
        Set-Content -LiteralPath $dispFile -Value ($fx.Replace('RECEIPT=' + $own, 'RECEIPT=' + $other))
        if ($null -eq (Resolve-StepExcuse -Step $step -Receipt $other -Sources $fxSources)) {
            Write-Error 'SELFTEST J2 excused a step whose own receipt does not carry the blocker'; exit 1
        }
        # J3 - BLOCKED=no keeps a red run a failure (the whole point of the gate).
        Set-Content -LiteralPath $dispFile -Value ($fx.Replace('BLOCKED=yes', 'BLOCKED=no'))
        if ($null -eq (Resolve-StepExcuse -Step $step -Receipt $own -Sources $fxSources)) { Write-Error 'SELFTEST J3 excused BLOCKED=no'; exit 1 }
        # J4 - a subjective class is never a valid [B] (AGENTS.md).
        Set-Content -LiteralPath $dispFile -Value ($fx.Replace('CLASS=external-error', 'CLASS=out-of-scope'))
        if ($null -eq (Resolve-StepExcuse -Step $step -Receipt $own -Sources $fxSources)) { Write-Error 'SELFTEST J4 excused a subjective block class'; exit 1 }
        # J5 - an unregistered follow-up id is a well-formed string, not a linked task.
        Set-Content -LiteralPath $dispFile -Value ($fx.Replace('FOLLOWUP=E2E-SANDBOX-NODISPLAY', 'FOLLOWUP=NEVER-REGISTERED-ID'))
        if ($null -eq (Resolve-StepExcuse -Step $step -Receipt $own -Sources $fxSources)) { Write-Error 'SELFTEST J5 excused an unregistered follow-up'; exit 1 }
        # J6 - no disposition filed at all: the failure stands.
        Remove-Item -LiteralPath $dispFile -Force
        if ($null -eq (Resolve-StepExcuse -Step $step -Receipt $own -Sources $fxSources)) { Write-Error 'SELFTEST J6 excused a step with no disposition on disk'; exit 1 }
        'PASS: VERIFICATION_PLAN self-test (' + $steps.Count + ' sections, J1-J6 deferral oracles)'
        exit 0
    } finally { Remove-Item -LiteralPath $tmp -Recurse -Force -ErrorAction SilentlyContinue }
}

if (-not (Test-Path -LiteralPath $out)) { New-Item -ItemType Directory -Path $out -Force | Out-Null }
$failures = @()
foreach ($s in $steps) {
    $receipt = [string]$s.receipt
    $dir = Split-Path -Parent $receipt
    if ($dir -and -not (Test-Path -LiteralPath $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
    $restore = @{}
    if ($s.ContainsKey('env')) {
        foreach ($k in $s.env.Keys) { $restore[$k] = [Environment]::GetEnvironmentVariable($k); [Environment]::SetEnvironmentVariable($k, [string]$s.env[$k]) }
    }
    try {
        if ($s.ContainsKey('gate')) {
            & pwsh -NoProfile -File (Join-Path $root ([string]$s.gate)) @($s.args) *> $receipt
        } else {
            & ([string]$s.exe) @($s.args) *> $receipt
        }
        $code = $LASTEXITCODE
    } finally {
        foreach ($k in $restore.Keys) { [Environment]::SetEnvironmentVariable($k, $restore[$k]) }
    }
    if ($code -eq 0) { '[PASS] {0,-4} {1}' -f $s.id, $s.name; continue }
    if ($s.deferrable) {
        $excuse = Resolve-StepExcuse -Step $s -Receipt $receipt
        if ($null -eq $excuse) { '[B]    {0,-4} {1} - blocked, evidenced in {2}' -f $s.id, $s.name, $receipt; continue }
        '[FAIL] {0,-4} {1} (exit {2}) - not excused: {3}' -f $s.id, $s.name, $code, $excuse
        $failures += ($s.id + ' ' + $s.name)
        continue
    }
    '[FAIL] {0,-4} {1} (exit {2}) - see {3}' -f $s.id, $s.name, $code, $receipt
    $failures += ($s.id + ' ' + $s.name)
}
if ($failures.Count -ne 0) { Write-Error ('VERIFICATION_PLAN failed: ' + ($failures -join '; ')); exit 1 }
'PASS: VERIFICATION_PLAN ' + $steps.Count + ' sections'
exit 0
