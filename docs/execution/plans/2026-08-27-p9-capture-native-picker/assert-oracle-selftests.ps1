# Runs every gate's negative oracle in one receipt. Any gate that would false-pass fails here.
# This is the executable answer to plan-review round 1 findings #1 and #6: the gates are proven
# non-vacuous BEFORE they are trusted to close a task row.
#
# Round-11 trim: PICKER_BINDING (Roslyn source-shape policing), SMOKE_DISPOSITION, SMOKE_PRODUCER
# and REFLECTION_QUALITY are gone with the scripts they ran. Those gates policed the shape of
# av-kit's own source and prose; what remains checks facts about the product - does the picker
# build, does the package ship clean, did the capture E2E actually run.
$ErrorActionPreference = 'Stop'
$root = $PSScriptRoot
$checks = @(
    @{ name = 'TASK_ROW_GATE';        script = 'assert-task-rows.ps1';        args = @('-SelfTest') },
    @{ name = 'RED_ORACLE_dotnet';    script = 'assert-red-oracle.ps1';       args = @('-Suite', 'dotnet', '-SelfTest') },
    @{ name = 'RED_ORACLE_vitest';    script = 'assert-red-oracle.ps1';       args = @('-Suite', 'vitest', '-SelfTest') },
    @{ name = 'OVERLAY_DELETION';     script = 'assert-overlay-deleted.ps1';  args = @('-SelfTest') },
    @{ name = 'PACKAGING_CLEAN_PATH'; script = 'assert-packaging-clean.ps1';  args = @('-SelfTest') },
    @{ name = 'E2E_WIRED';            script = 'assert-e2e-wired.ps1';        args = @('-SelfTest') },
    @{ name = 'RUN_ARM';              script = 'arm-run.ps1';                 args = @('-Name', 'e2e-capture', '-SelfTest') },
    @{ name = 'BUILD_PLAN_HUB';       script = 'assert-build-plan-hub.ps1';   args = @('-SelfTest') },
    # The runner's deferred-step adjudication decides whether a red step is a failure or a `[B]`,
    # so it is a gate and must prove its own oracles here too (round-6 R6-4).
    @{ name = 'VERIFICATION_ADJUDICATION'; script = 'run-verification-plan.ps1'; args = @('-SelfTest') }
)
$failed = 0
foreach ($c in $checks) {
    $path = Join-Path $root $c.script
    if (-not (Test-Path -LiteralPath $path)) {
        Write-Error ('missing gate script ' + $path)
        exit 1
    }
    & pwsh -NoProfile -File $path @($c.args)
    if ($LASTEXITCODE -ne 0) {
        Write-Error ($c.name + ' self-test FAILED with exit ' + $LASTEXITCODE)
        $failed++
    }
}
if ($failed -ne 0) { Write-Error ([string]$failed + ' oracle self-tests failed'); exit 1 }
'PASS: ORACLE_SELFTESTS ' + $checks.Count + ' gates proven non-vacuous'
exit 0
