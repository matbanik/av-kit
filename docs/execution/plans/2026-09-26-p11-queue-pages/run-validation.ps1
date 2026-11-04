# Fresh Session 24 UI gate, with independent before/after input identity.
$ErrorActionPreference = 'Stop'
$env:RECEIPTS_DIR = 'C:/Temp/av-kit'
$env:AGENT_MODEL_REGISTRY_HOME = 'P:/.agent'
$env:ELECTRON_RUN_AS_NODE = $null
$env:AVKIT_E2E_OUT_DIR = $null
$env:AVKIT_PRIMITIVE_HARNESS_BUILD = $null
$base = 'docs/execution/plans/2026-09-26-p11-queue-pages'

rtk proxy npm --prefix ui run build *> C:/Temp/av-kit/p11q-final-build.txt
$code = $LASTEXITCODE
if ($code -ne 0) { Get-Content C:/Temp/av-kit/p11q-final-build.txt -Tail 30; exit $code }
$env:AVKIT_PRIMITIVE_HARNESS_BUILD = '1'
rtk proxy npm --prefix ui run build -- --outDir P:/av-kit/ui/out-e2e *> C:/Temp/av-kit/p11q-final-harness-build.txt
$code = $LASTEXITCODE
if ($code -ne 0) { Get-Content C:/Temp/av-kit/p11q-final-harness-build.txt -Tail 30; exit $code }
$env:AVKIT_PRIMITIVE_HARNESS_BUILD = $null

rtk proxy uv run python "$base/validation-state.py" "$base/validation-state.json" *> C:/Temp/av-kit/p11q-final-state-before.txt
$code = $LASTEXITCODE
if ($code -ne 0) { Get-Content C:/Temp/av-kit/p11q-final-state-before.txt -Tail 30; exit $code }

foreach ($check in @('typecheck', 'lint')) {
    rtk proxy npm --prefix ui run $check *> "C:/Temp/av-kit/p11q-final-$check.txt"
    $code = $LASTEXITCODE
    if ($code -ne 0) { Get-Content "C:/Temp/av-kit/p11q-final-$check.txt" -Tail 30; exit $code }
}
rtk proxy npm --prefix ui run test -- tests/unit/bulk-action-bar.test.ts tests/unit/convert-page.test.ts tests/unit/downloader-page.test.ts tests/unit/layout-primitives.test.ts *> C:/Temp/av-kit/p11q-final-targeted.txt
$code = $LASTEXITCODE
if ($code -ne 0) { Get-Content C:/Temp/av-kit/p11q-final-targeted.txt -Tail 30; exit $code }
rtk proxy npm --prefix ui run test -- --reporter=json --outputFile=C:/Temp/av-kit/p11q-final-vitest.json *> C:/Temp/av-kit/p11q-final-vitest.txt
$code = $LASTEXITCODE
if ($code -ne 0) { Get-Content C:/Temp/av-kit/p11q-final-vitest.txt -Tail 30; exit $code }
rtk proxy npm --prefix ui run test:e2e -- --reporter=json --outputFile=C:/Temp/av-kit/p11q-final-electron.json *> C:/Temp/av-kit/p11q-final-electron.txt
$code = $LASTEXITCODE
if ($code -ne 0) { Get-Content C:/Temp/av-kit/p11q-final-electron.txt -Tail 35; exit $code }

rtk proxy uv run python "$base/validation-state.py" C:/Temp/av-kit/p11q-final-state-after.json *> C:/Temp/av-kit/p11q-final-state-after.txt
$code = $LASTEXITCODE
if ($code -ne 0) { Get-Content C:/Temp/av-kit/p11q-final-state-after.txt -Tail 30; exit $code }
$before = Get-Content "$base/validation-state.json" -Raw | ConvertFrom-Json
$after = Get-Content C:/Temp/av-kit/p11q-final-state-after.json -Raw | ConvertFrom-Json
if ($before.state_id -ne $after.state_id) { throw 'Validation inputs changed during the gate' }
$unit = Get-Content C:/Temp/av-kit/p11q-final-vitest.json -Raw | ConvertFrom-Json
$e2e = Get-Content C:/Temp/av-kit/p11q-final-electron.json -Raw | ConvertFrom-Json
if ($unit.numFailedTests -ne 0 -or $unit.numPendingTests -ne 0 -or $e2e.stats.unexpected -ne 0 -or $e2e.stats.skipped -ne 0) { throw 'Failed or skipped tests in final gate' }
"PASS UI gate: $($unit.numPassedTests) Vitest; $($e2e.stats.expected) Electron; typecheck/lint/build passed"
"STATE $($before.state_id) unchanged before/after"
