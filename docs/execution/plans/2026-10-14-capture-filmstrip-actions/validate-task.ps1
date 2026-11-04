# Exact validation procedures for 2026-10-14-capture-filmstrip-actions (Session 38).
# Ports the Session 30 helpers (docs/execution/plans/2026-10-02-capture-flatten-backup/validate-task.sh and .ps1)
# to one PowerShell script, because the Windows host is the only gate location for this plan.
# Run from the worktree root (P:/av-kit-wt/s38-capture-filmstrip-actions):
#   pwsh -NoProfile -File docs/execution/plans/2026-10-14-capture-filmstrip-actions/validate-task.ps1 -Check <name>
# Every tool runs through `rtk proxy` with its raw output in C:/Temp/av-kit/s38-<stage>.txt. Report checks
# (Red shape, Green, COUNT_FLOORS, scope, state) live in plan_checks.py next to this script.
# A check exits nonzero on its first failure.
param(
    [Parameter(Mandatory = $true)][string]$Check,
    [string]$Review = '',
    [string]$Mode = '',
    [int]$Cap = 0
)
$ErrorActionPreference = 'Stop'
# Native exit codes are read from $LASTEXITCODE; never let pwsh 7.4+ turn them into throws.
$PSNativeCommandUseErrorActionPreference = $false
$rd = 'C:/Temp/av-kit'
New-Item -ItemType Directory -Force -Path $rd | Out-Null
$plan = 'docs/execution/plans/2026-10-14-capture-filmstrip-actions'
$pc = "$plan/plan_checks.py"
Remove-Item Env:ELECTRON_RUN_AS_NODE -ErrorAction SilentlyContinue
Remove-Item Env:AVKIT_E2E_OUT_DIR -ErrorAction SilentlyContinue
# The parent checkout's venv must not leak into this worktree's `uv run`.
Remove-Item Env:VIRTUAL_ENV -ErrorAction SilentlyContinue
# lint_task_contract.py recognises absolute receipt paths only against the configured receipts dir.
$env:RECEIPTS_DIR = $rd

$e2eSpec = 'tests/e2e/capture-filmstrip-actions.test.ts'
$unit88 = @(
    'tests/unit/capture-filmstrip-actions.behavior.test.ts', 'tests/unit/capture-clipboard.test.ts',
    'tests/unit/clipboard-image-main.test.ts', 'tests/unit/ipc-strict-census.test.ts',
    'tests/unit/login-item-ipc.test.ts', 'tests/unit/gui-actions-audit.test.ts')
$unit89 = @(
    'tests/unit/capture-filmstrip-select.test.ts', 'tests/unit/capture-batch-delete.test.ts',
    'tests/unit/capture-filmstrip-actions.behavior.test.ts', 'tests/unit/capture-help-content.test.ts')
# Capture and IPC regression set (both MEUs touch these surfaces).
$regcap = @(
    'tests/unit/capture-page.test.ts', 'tests/unit/capture-page.behavior.test.ts', 'tests/unit/capture-flatten.test.ts',
    'tests/unit/capture-filmstrip-label.test.ts', 'tests/unit/capture-help-content.test.ts',
    'tests/unit/capture-main.behavior.test.ts', 'tests/unit/capture-picker.test.ts', 'tests/unit/web-prefs-ipc.test.ts',
    'tests/unit/shell-ipc-ledger.test.ts', 'tests/unit/api-base-ipc.test.ts', 'tests/unit/settings-page.test.ts',
    'tests/unit/layout-canon.test.ts', 'tests/unit/queue-canon.test.ts', 'tests/unit/gui-actions-audit.test.ts',
    'tests/unit/e2e-wiring.test.ts')
$docSuites = @('tests/unit/gui-actions-audit.test.ts', 'tests/unit/layout-canon.test.ts', 'tests/unit/queue-canon.test.ts')
# Source audit: the renderer and main files this plan creates or edits.
$auditSrc = @(
    'ui/src/main/ipc.ts', 'ui/src/main/clipboard-image.ts', 'ui/src/main/index.ts', 'ui/src/main/preload.ts',
    'ui/src/renderer/src/env.d.ts',
    'ui/src/renderer/src/features/capture/capture-clipboard.ts',
    'ui/src/renderer/src/features/capture/CaptureFilmstripMenu.tsx',
    'ui/src/renderer/src/features/capture/CaptureFilmstrip.tsx',
    'ui/src/renderer/src/features/capture/CapturePage.tsx',
    'ui/src/renderer/src/features/capture/capture-filmstrip-select.ts',
    'ui/src/renderer/src/features/capture/capture-commands.ts',
    'ui/src/renderer/src/features/capture/capture-help-content.ts')
$auditPattern = 'TODO|FIXME|transition-all|bg-\[#|console\.log\(|@ts-ignore|@ts-expect-error|: any\b'
$handoff88 = '.agent/context/handoffs/2026-10-14-capture-filmstrip-actions-MEU-88-handoff.md'
$handoff89 = '.agent/context/handoffs/2026-10-14-capture-filmstrip-actions-MEU-89-handoff.md'

function Stop-Check([string]$Msg) { Write-Host "FAIL: $Msg"; exit 1 }

function Invoke-Stage([string]$Id, [string[]]$Argv) {
    $receipt = "$rd/s38-$Id.txt"
    & rtk proxy @Argv *> $receipt
    $code = $LASTEXITCODE
    Get-Content $receipt -Tail 15 | Write-Host
    return $code
}

function Assert-Stage([string]$Id, [string[]]$Argv) {
    $code = Invoke-Stage $Id $Argv
    if ($code -ne 0) { Stop-Check "$Id exit $code (receipt $rd/s38-$Id.txt)" }
    Write-Host "PASS $Id"
}

function Invoke-PlanCheck([string]$Name, [string[]]$Rest = @()) {
    $code = Invoke-Stage "pc-$Name" (@('uv', 'run', 'python', $pc, $Name) + $Rest)
    if ($code -ne 0) { Stop-Check "plan_checks $Name (receipt $rd/s38-pc-$Name.txt)" }
}

function Invoke-Vitest([string]$Id, [string[]]$Files) {
    Remove-Item "$rd/s38-$Id.json" -ErrorAction SilentlyContinue
    # The default reporter keeps unhandled errors in the text receipt; the JSON reporter drops them (F3).
    $code = Invoke-Stage $Id (@('npm', '--prefix', 'ui', 'run', 'test', '--') + $Files + @('--reporter=default', '--reporter=json', "--outputFile=$rd/s38-$Id.json"))
    if (-not (Test-Path "$rd/s38-$Id.json")) { Stop-Check "$Id produced no Vitest JSON (exit $code)" }
    return $code
}

function Invoke-E2E([string]$Id, [string[]]$Extra) {
    Remove-Item "$rd/s38-$Id.json" -ErrorAction SilentlyContinue
    $code = Invoke-Stage $Id (@('npm', '--prefix', 'ui', 'run', 'test:e2e', '--') + $Extra + @('--reporter=json', "--outputFile=$rd/s38-$Id.json"))
    if (-not (Test-Path "$rd/s38-$Id.json")) { Stop-Check "$Id produced no Playwright JSON (exit $code)" }
    return $code
}

# Green helpers: zero failures, no load errors, no pending; nonzero exit without a failure is a runner error.
function Assert-VitestGreen([string]$Id, [string[]]$Files) {
    $code = Invoke-Vitest $Id $Files
    Invoke-PlanCheck 'vitest' @($Id, "$rd/s38-$Id.json", "$code", "$rd/s38-$Id.txt")
}
function Assert-E2EGreen([string]$Id, [string[]]$Extra) {
    $code = Invoke-E2E $Id $Extra
    Invoke-PlanCheck 'e2e' @($Id, "$rd/s38-$Id.json", "$code")
}

function Invoke-Build { Assert-Stage 'ui-build' @('npm', '--prefix', 'ui', 'run', 'build') }
function Invoke-HarnessBuild {
    # layout-primitives.test.ts and the primitive harness spec read ui/out-e2e.
    Assert-Stage 'ui-harness-build' @('pwsh', '-NoProfile', '-Command', "`$env:AVKIT_PRIMITIVE_HARNESS_BUILD='1'; npm --prefix ui run build -- --outDir '$((Resolve-Path ui).Path)/out-e2e'; exit `$LASTEXITCODE")
}
# Session 27 A-5: Electron 42 downloads its binary on first require; install it once, serially.
$npmCi = @('pwsh', '-NoProfile', '-Command', "npm --prefix ui ci; if (`$LASTEXITCODE -ne 0) { exit `$LASTEXITCODE }; node ui/node_modules/electron/install.js; if (`$LASTEXITCODE -ne 0) { exit `$LASTEXITCODE }; if (-not (Test-Path ui/node_modules/electron/path.txt)) { exit 3 }; exit 0")

# Red: the run must fail, every failure must be an assertion in this MEU's ACs (or a TA pin / a
# declared new module's missing symbol), and the Electron AC must fail on an expect().
function Invoke-Red([string]$Meu, [string]$Tag, [string[]]$Files, [string]$Suffix = '', [string[]]$Since = @()) {
    # $Since (D-25 rework): only ACs numbered at or above it must be red; the earlier ones stay green.
    $id = "red$($Meu.Substring(4))$Suffix-vitest"
    $code = Invoke-Vitest $id $Files
    if ($code -eq 0) { Stop-Check "$Meu Vitest Red expected a failing run, got exit 0" }
    Invoke-PlanCheck 'vitest-red' (@($Meu, "$rd/s38-$id.json", "$rd/s38-$id.txt") + $Since)
    Invoke-Build
    $eid = "red$($Meu.Substring(4))$Suffix-e2e"
    $code = Invoke-E2E $eid @($e2eSpec, '-g', $Tag)
    if ($code -eq 0) { Stop-Check "$Meu E2E Red expected a failing run, got exit 0" }
    Invoke-PlanCheck 'e2e-red' (@($Meu, "$rd/s38-$eid.json") + $Since)
}

function Invoke-Green([string]$Meu, [string]$Tag, [string[]]$Files) {
    $n = $Meu.Substring(4)
    Assert-VitestGreen "green$n-vitest" $Files
    Invoke-Build
    Assert-E2EGreen "green$n-e2e" @($e2eSpec, '-g', $Tag)
}

function Invoke-MeuGate([string]$Meu, [string]$Tag, [string[]]$Files) {
    $n = $Meu.Substring(4)
    Assert-Stage 'ui-types' @('npm', '--prefix', 'ui', 'run', 'typecheck')
    Assert-Stage 'ui-lint' @('npm', '--prefix', 'ui', 'run', 'lint')
    Assert-VitestGreen "gate$n-vitest" (@($Files + $regcap) | Select-Object -Unique)
    Invoke-Build
    Assert-E2EGreen "gate$n-e2e" @($e2eSpec, 'tests/e2e/capture-inbox.test.ts')
    Assert-E2EGreen "gate$n-repeat" @($e2eSpec, '-g', $Tag, '--repeat-each=10')
}

function Invoke-Prereq {
    foreach ($g in @('graphify-out', 'graphify-out-research')) {
        if (Test-Path $g) { Stop-Check "graph directory $g present: re-run the context-tool gate with Mat (S1)" }
    }
    # headroom on PATH needs the execution-phase context_tool_decision in task.md that names it (S1 re-run, 2026-10-16).
    if (Get-Command headroom -ErrorAction SilentlyContinue) {
        $t = Get-Content "$plan/task.md" -Raw
        if ($t -notmatch '(?ms)phase: execution\s.*?eligibility_basis: "[^"]*headroom') { Stop-Check 'headroom on PATH: re-run the context-tool gate with Mat (S1)' }
        Write-Host 'headroom on PATH: execution-phase context_tool_decision recorded in task.md'
    }
    Invoke-PlanCheck 'prereq'
    Invoke-PlanCheck 'selftest'
    Assert-Stage 'npm-ci' $npmCi
    Write-Host 'PASS prereq'
}

switch ($Check) {
    'static' {
        Invoke-PlanCheck 'static'
        Invoke-PlanCheck 'selftest'
        Assert-Stage 'task-lint' @('uv', 'run', 'python', 'tools/lint_task_contract.py', '--allowed-builder-classes',
            'avkit_builder,avkit_coordinator,avkit_verifier', '--task', "$plan/task.md")
    }
    'prereq' { Invoke-Prereq }
    'baseline' {
        Invoke-Prereq
        $dirty = (git status --porcelain -- ui | Out-String).Trim()
        if ($dirty) { Stop-Check "ui/ has uncommitted changes before the baseline: $dirty" }
        (git rev-parse HEAD).Trim() | Set-Content -Path "$plan/baseline.sha" -Encoding ascii
        Invoke-Build
        Invoke-HarnessBuild
        Assert-VitestGreen 'baseline-vitest' @()
        Assert-E2EGreen 'baseline-e2e' @()
        Invoke-PlanCheck 'baseline-counts' @("$rd/s38-baseline-vitest.json", "$rd/s38-baseline-e2e.json")
        Write-Host "PASS baseline @ $(Get-Content "$plan/baseline.sha")"
    }
    'census' {
        # TEST_AMENDMENTS census: every hit gets a disposition in walkthrough.md §Census (S2 on a new contradiction).
        $pats = @('toHaveLength\(19\)', 'listRegisteredChannels', 'getPreloadApiKeys', 'RENDERER_TO_MAIN_CHANNELS',
            'API_KEYS', 'write-clipboard', 'writeClipboard', 'capture-filmstrip', 'capture-delete-confirm',
            'capture-confirm-strip', 'Delete this capture', 'capture-status', 'deleteCapture', 'CaptureFilmstrip',
            'onSelect', 'four-tools', 'CAPTURE_HELP_SECTIONS', 'capture:delete', 'contextmenu', 'IPC_NO_PAYLOAD', 'clipboard')
        $argv = @('rg', '-n') + ($pats | ForEach-Object { @('-e', $_) }) + @('ui/tests')
        $code = Invoke-Stage 'census' $argv
        if ($code -gt 1) { Stop-Check "census rg exit $code" }
        $hits = (Get-Content "$rd/s38-census.txt" | Measure-Object -Line).Lines
        Write-Host "PASS census: $hits lines in $rd/s38-census.txt; disposition each in walkthrough.md §Census"
    }
    'red88' { Invoke-Red 'MEU-88' 'AC-88' $unit88; Write-Host 'PASS red88' }
    'green88-main' {
        # Main and preload only. The whole-project typecheck waits for row 4: ui/tsconfig.json includes the
        # renderer tests, which import capture-clipboard.ts before it exists (F5).
        Assert-VitestGreen 'green88-main-vitest' @('tests/unit/clipboard-image-main.test.ts', 'tests/unit/ipc-strict-census.test.ts', 'tests/unit/login-item-ipc.test.ts')
        Write-Host 'PASS green88-main'
    }
    'green88' { Invoke-Green 'MEU-88' 'AC-88' $unit88; Write-Host 'PASS green88' }
    'gate88' { Invoke-MeuGate 'MEU-88' 'AC-88' $unit88; Write-Host 'PASS gate88' }
    'red89' { Invoke-Red 'MEU-89' 'AC-89' $unit89; Write-Host 'PASS red89' }
    'red89b' { Invoke-Red 'MEU-89' 'AC-89' $unit89 'b' @('10'); Write-Host 'PASS red89b' }
    'green89' { Invoke-Green 'MEU-89' 'AC-89' $unit89; Write-Host 'PASS green89' }
    'gate89' {
        Invoke-MeuGate 'MEU-89' 'AC-89' (@($unit88 + $unit89) | Select-Object -Unique)
        Assert-E2EGreen 'gate89-repeat88' @($e2eSpec, '-g', 'AC-88', '--repeat-each=10')
        Write-Host 'PASS gate89'
    }
    'hub' {
        Invoke-PlanCheck 'hub'
        Assert-VitestGreen 'hub-vitest' $docSuites
        Write-Host 'PASS hub'
    }
    'task-state' { Invoke-PlanCheck 'task-state' }
    'gate' {
        # Full PROFILE D6 UI set, fresh and in order. py/mcp/openapi are skipped on the scope basis
        # (no change under packages/, mcp-server/ or openapi.committed.json; -Check scope proves it).
        $out = "$plan/gate-result.json"
        Get-ChildItem -Path $rd -Filter 's38-gate-*' -ErrorAction SilentlyContinue | Remove-Item -Force
        $product = @('ui', 'docs/build-plan')
        $result = [ordered]@{
            schema                = 's38-gate.v1'
            tested_commit         = (git rev-parse HEAD).Trim()
            product_uncommitted   = @(git status --porcelain --untracked-files=all -- @product)
            # Working-tree content of every uncommitted product path, untracked files included.
            product_file_sha256   = [ordered]@{}
            lockfile_sha256       = (Get-FileHash ui/package-lock.json -Algorithm SHA256).Hash
            node                  = (node --version).Trim()
            skipped               = 'py-types, py-lint, py-tests, mcp-*, openapi: no change outside the Files Modified rows and closeout outputs, so none under packages/, mcp-server/, openapi.committed.json, pyproject.toml or uv.lock (-Check scope)'
            started               = (Get-Date).ToString('o')
            stages                = @()
        }
        foreach ($line in $result.product_uncommitted) {
            $path = $line.Substring(3).Trim('"')
            $result.product_file_sha256[$path] = $(if (Test-Path $path -PathType Leaf) { (Get-FileHash $path -Algorithm SHA256).Hash } else { 'deleted' })
        }
        $vjson = "$rd/s38-gate-vitest.json"
        $ejson = "$rd/s38-gate-e2e.json"
        $stages = @(
            @('gate-npm-ci', $npmCi),
            @('gate-ui-types', @('npm', '--prefix', 'ui', 'run', 'typecheck')),
            @('gate-ui-lint', @('npm', '--prefix', 'ui', 'run', 'lint')),
            # Builds precede the suites: global-setup refuses a stale out/, and layout-primitives reads out-e2e.
            @('gate-ui-build', @('npm', '--prefix', 'ui', 'run', 'build')),
            @('gate-ui-harness-build', @('pwsh', '-NoProfile', '-Command', "`$env:AVKIT_PRIMITIVE_HARNESS_BUILD='1'; npm --prefix ui run build -- --outDir '$((Resolve-Path ui).Path)/out-e2e'; exit `$LASTEXITCODE")),
            @('gate-ui-tests', @('npm', '--prefix', 'ui', 'run', 'test', '--', '--reporter=default', '--reporter=json', "--outputFile=$vjson")),
            @('gate-ui-electron', @('npm', '--prefix', 'ui', 'run', 'test:e2e', '--', '--reporter=json', "--outputFile=$ejson")),
            @('gate-state-render', @('uv', 'run', 'python', 'tools/meu_status.py', 'render', '--check')),
            @('gate-task-contract', @('uv', 'run', 'python', 'tools/lint_task_contract.py', '--allowed-builder-classes', 'avkit_builder,avkit_coordinator,avkit_verifier', '--task', "$plan/task.md")),
            @('gate-source-audit', (@('rg', '-n', '-e', $auditPattern) + $auditSrc))
        )
        $failed = $false
        foreach ($s in $stages) {
            $code = Invoke-Stage $s[0] $s[1]
            $row = [ordered]@{ id = $s[0]; exit = $code; receipt = "$rd/s38-$($s[0]).txt" }
            if ($s[0] -eq 'gate-source-audit') {
                # rg exit 1 = no hits (clean); 0 = hits; 2+ = IO error.
                $row.note = "rg exit $code (1 = no hits)"
                $row.exit = $(if ($code -eq 1) { 0 } else { 1 })
            } elseif ($s[0] -in @('gate-ui-tests', 'gate-ui-electron')) {
                $kind = $(if ($s[0] -eq 'gate-ui-tests') { 'vitest' } else { 'e2e' })
                $json = $(if ($kind -eq 'vitest') { $vjson } else { $ejson })
                # @(...) keeps a one-element array; $(...) would unroll it to a string, and splatting a string passes one character per argument.
                $extra = @(if ($kind -eq 'vitest') { "$rd/s38-$($s[0]).txt" })
                & rtk proxy uv run python $pc $kind $s[0] $json "$code" @extra *> "$rd/s38-$($s[0])-check.txt"
                $row.exit = $LASTEXITCODE
                Get-Content "$rd/s38-$($s[0])-check.txt" | Write-Host
            }
            $result.stages += $row
            if ($row.exit -ne 0) { $failed = $true; break }
        }
        if (-not $failed) {
            $v = Get-Content $vjson -Raw | ConvertFrom-Json
            $e = Get-Content $ejson -Raw | ConvertFrom-Json
            $result.vitest = [ordered]@{ passed = $v.numPassedTests; failed = $v.numFailedTests; total = $v.numTotalTests }
            $result.e2e = [ordered]@{ expected = $e.stats.expected; unexpected = $e.stats.unexpected; skipped = $e.stats.skipped; flaky = $e.stats.flaky }
            $result.electron = ((npm --prefix ui ls electron --depth=0 2>$null) | Select-String 'electron@' | Out-String).Trim()
            & rtk proxy uv run python $pc floors $vjson $ejson "$rd/s38-gate-ui-tests.txt" *> "$rd/s38-gate-floors.txt"
            $fcode = $LASTEXITCODE
            Get-Content "$rd/s38-gate-floors.txt" | Write-Host
            $result.stages += [ordered]@{ id = 'gate-floors'; exit = $fcode; receipt = "$rd/s38-gate-floors.txt" }
            if ($fcode -ne 0) { $failed = $true }
        }
        $result.finished = (Get-Date).ToString('o')
        $result.passed = (-not $failed)
        $result | ConvertTo-Json -Depth 6 | Set-Content -Path $out -Encoding utf8
        Get-Content $out
        if ($failed) { Stop-Check 'gate failed; see the receipts named in gate-result.json' }
        Write-Host 'PASS gate'
    }
    'ssot-review' {
        foreach ($m in @('MEU-88', 'MEU-89')) {
            Assert-Stage "ssot-$m" @('uv', 'run', 'python', 'tools/meu_status.py', 'update', $m, 'ready_for_review', '--plan', $plan)
        }
        Assert-Stage 'ssot-render' @('uv', 'run', 'python', 'tools/meu_status.py', 'render')
        Assert-Stage 'ssot-render-check' @('uv', 'run', 'python', 'tools/meu_status.py', 'render', '--check')
        Invoke-PlanCheck 'ssot-review'
    }
    'scope' { Invoke-PlanCheck 'scope' }
    'handoff-ac' {
        foreach ($h in @($handoff88, $handoff89)) {
            Assert-Stage "handoff-$(Split-Path $h -Leaf)" @('uv', 'run', 'python', 'tools/validate_closeout_artifacts.py', '--handoff', $h, '--plan', "$plan/implementation-plan.md")
        }
        Write-Host 'PASS handoff-ac'
    }
    'review-check' {
        if (-not $Review -or -not $Mode -or $Cap -lt 1) { Stop-Check 'review-check needs -Review, -Mode and -Cap' }
        Invoke-PlanCheck 'review-check' @($Review, $Mode, "$Cap")
    }
    'post-review-state' {
        Assert-Stage 'post-render-check' @('uv', 'run', 'python', 'tools/meu_status.py', 'render', '--check')
        Assert-Stage 'post-issues-check' @('uv', 'run', 'python', 'tools/issue_triage.py', 'render', '--check')
        Invoke-PlanCheck 'post-review-state'
    }
    default { Stop-Check "unknown check: $Check" }
}
exit 0
