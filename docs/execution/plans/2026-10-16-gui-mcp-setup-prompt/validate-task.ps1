# Exact validation procedures for 2026-10-16-gui-mcp-setup-prompt (Session 31b).
# Adapts Session 38's validate-task.ps1 (docs/execution/plans/2026-10-14-capture-filmstrip-actions/) to two
# Vitest projects (ui and mcp-server) and adds the packaged probe (PKG_PROBE).
# Run from the worktree root (P:/av-kit-wt/s31b-gui-mcp-setup-prompt):
#   pwsh -NoProfile -File docs/execution/plans/2026-10-16-gui-mcp-setup-prompt/validate-task.ps1 -Check <name>
# Every tool runs through `rtk proxy` with its raw output in C:/Temp/av-kit/s31b-<stage>.txt. Report checks
# (Red shape, Green, COUNT_FLOORS, the MCP probe, scope, state) live in plan_checks.py next to this script.
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
$plan = 'docs/execution/plans/2026-10-16-gui-mcp-setup-prompt'
$pc = "$plan/plan_checks.py"
# The parent shell's value would make every Electron launch run as Node; the MCP probe sets it on its child only.
Remove-Item Env:ELECTRON_RUN_AS_NODE -ErrorAction SilentlyContinue
Remove-Item Env:AVKIT_E2E_OUT_DIR -ErrorAction SilentlyContinue
# The parent checkout's venv must not leak into this worktree's `uv run`.
Remove-Item Env:VIRTUAL_ENV -ErrorAction SilentlyContinue
# lint_task_contract.py recognises absolute receipt paths only against the configured receipts dir.
$env:RECEIPTS_DIR = $rd

$e2eSpec = 'tests/e2e/mcp-setup-prompt.test.ts'
# ui Vitest files (paths relative to ui/).
$ui71Main = @(
    'tests/unit/mcp-setup-prompt.test.ts', 'tests/unit/mcp-server-entry.test.ts', 'tests/unit/mcp-prompt-ipc.test.ts',
    'tests/unit/mcp-spawn-electron.test.ts', 'tests/unit/clipboard-image-main.test.ts',
    'tests/unit/ipc-strict-census.test.ts', 'tests/unit/login-item-ipc.test.ts')
$ui71 = @($ui71Main + @('tests/unit/settings-mcp-prompt.test.ts', 'tests/unit/gui-actions-audit.test.ts'))
# mcp-server Vitest files (paths relative to mcp-server/).
$mcp71 = @('tests/entry-guard.test.ts', 'tests/entry-spawn.test.ts', 'tests/example-config.test.ts', 'tests/runtime.test.ts')
$mcp92 = @('tests/bundle.test.ts', 'tests/bundle-licenses.test.ts')
# IPC and Settings regression set (MEU-71 touches the channel census, the preload and the Settings card).
$regui = @(
    'tests/unit/settings-page.test.ts', 'tests/unit/settings-emphasis.test.tsx', 'tests/unit/settings-rail.test.tsx',
    'tests/unit/settings-tail-spacer.test.ts', 'tests/unit/settings-deps-refresh.test.ts',
    'tests/unit/settings-tts-runtime.test.ts', 'tests/unit/copy-mcp-config.test.ts', 'tests/unit/web-prefs-ipc.test.ts',
    'tests/unit/shell-ipc-ledger.test.ts', 'tests/unit/api-base-ipc.test.ts', 'tests/unit/app-shell-wiring.test.ts',
    'tests/unit/layout-canon.test.ts', 'tests/unit/queue-canon.test.ts', 'tests/unit/e2e-wiring.test.ts')
$docSuites = @('tests/unit/gui-actions-audit.test.ts', 'tests/unit/layout-canon.test.ts', 'tests/unit/queue-canon.test.ts')
# Source audit: the product files this plan creates or edits.
$auditSrc = @(
    'ui/src/main/ipc.ts', 'ui/src/main/index.ts', 'ui/src/main/preload.ts', 'ui/src/main/mcp-setup-prompt.ts',
    'ui/src/renderer/src/env.d.ts', 'ui/src/renderer/src/features/settings/SettingsPage.tsx',
    'mcp-server/src/entry-guard.ts', 'mcp-server/src/index.ts',
    'mcp-server/scripts/bundle.ts', 'mcp-server/scripts/bundle-licenses.ts')
$auditPattern = 'TODO|FIXME|transition-all|bg-\[#|console\.log\(|@ts-ignore|@ts-expect-error|: any\b'
$handoff71 = '.agent/context/handoffs/2026-10-16-gui-mcp-setup-prompt-MEU-71-handoff.md'
$handoff92 = '.agent/context/handoffs/2026-10-16-gui-mcp-setup-prompt-MEU-92-handoff.md'
$unpacked = 'ui/dist/win-unpacked'
$hermetic = "$rd/s31b-pkg-probe"

function Stop-Check([string]$Msg) { Write-Host "FAIL: $Msg"; exit 1 }

function Invoke-Stage([string]$Id, [string[]]$Argv) {
    $receipt = "$rd/s31b-$Id.txt"
    & rtk proxy @Argv *> $receipt
    $code = $LASTEXITCODE
    Get-Content $receipt -Tail 15 | Write-Host
    return $code
}

function Assert-Stage([string]$Id, [string[]]$Argv) {
    $code = Invoke-Stage $Id $Argv
    if ($code -ne 0) { Stop-Check "$Id exit $code (receipt $rd/s31b-$Id.txt)" }
    Write-Host "PASS $Id"
}

function Invoke-PlanCheck([string]$Name, [string[]]$Rest = @()) {
    $code = Invoke-Stage "pc-$Name" (@('uv', 'run', 'python', $pc, $Name) + $Rest)
    if ($code -ne 0) { Stop-Check "plan_checks $Name (receipt $rd/s31b-pc-$Name.txt)" }
}

# $Project is 'ui' or 'mcp-server'; $Files are relative to it (empty = the whole suite).
function Invoke-Vitest([string]$Id, [string]$Project, [string[]]$Files) {
    Remove-Item "$rd/s31b-$Id.json" -ErrorAction SilentlyContinue
    # The default reporter keeps unhandled errors in the text receipt; the JSON reporter drops them.
    $code = Invoke-Stage $Id (@('npm', '--prefix', $Project, 'run', 'test', '--') + $Files + @('--reporter=default', '--reporter=json', "--outputFile=$rd/s31b-$Id.json"))
    if (-not (Test-Path "$rd/s31b-$Id.json")) { Stop-Check "$Id produced no Vitest JSON (exit $code)" }
    return $code
}

function Invoke-E2E([string]$Id, [string[]]$Extra) {
    Remove-Item "$rd/s31b-$Id.json" -ErrorAction SilentlyContinue
    $code = Invoke-Stage $Id (@('npm', '--prefix', 'ui', 'run', 'test:e2e', '--') + $Extra + @('--reporter=json', "--outputFile=$rd/s31b-$Id.json"))
    if (-not (Test-Path "$rd/s31b-$Id.json")) { Stop-Check "$Id produced no Playwright JSON (exit $code)" }
    return $code
}

# Green helpers: zero failures, no load errors, no pending; nonzero exit without a failure is a runner error.
function Assert-VitestGreen([string]$Id, [string]$Project, [string[]]$Files) {
    $code = Invoke-Vitest $Id $Project $Files
    Invoke-PlanCheck 'vitest' @($Id, "$rd/s31b-$Id.json", "$code", "$rd/s31b-$Id.txt")
}
function Assert-E2EGreen([string]$Id, [string[]]$Extra) {
    $code = Invoke-E2E $Id $Extra
    Invoke-PlanCheck 'e2e' @($Id, "$rd/s31b-$Id.json", "$code")
}

function Invoke-Build { Assert-Stage 'ui-build' @('npm', '--prefix', 'ui', 'run', 'build') }
function Invoke-HarnessBuild {
    # layout-primitives.test.ts and the primitive harness spec read ui/out-e2e.
    Assert-Stage 'ui-harness-build' @('pwsh', '-NoProfile', '-Command', "`$env:AVKIT_PRIMITIVE_HARNESS_BUILD='1'; npm --prefix ui run build -- --outDir '$((Resolve-Path ui).Path)/out-e2e'; exit `$LASTEXITCODE")
}
# AC-71.9 and AC-71.10 spawn mcp-server/dist/index.js, so the server is built before any test run.
function Invoke-McpBuild { Assert-Stage 'mcp-build' @('npm', '--prefix', 'mcp-server', 'run', 'build') }
function Invoke-McpTypes { Assert-Stage 'mcp-types' @('npm', '--prefix', 'mcp-server', 'run', 'typecheck') }
function Invoke-McpBundle { Assert-Stage 'mcp-bundle' @('npm', '--prefix', 'mcp-server', 'run', 'bundle') }
# D-93 (RULE-1): the capture-picker specs need the gitignored region-picker stub, which a fresh worktree lacks.
function Invoke-PickerStub { Assert-Stage 'picker-stub' @('npm', '--prefix', 'ui', 'run', 'build:picker-stub') }
# Session 27 A-5: Electron 42 downloads its binary on first require; install it once, serially.
$npmCi = @('pwsh', '-NoProfile', '-Command', "npm --prefix ui ci; if (`$LASTEXITCODE -ne 0) { exit `$LASTEXITCODE }; npm --prefix mcp-server ci; if (`$LASTEXITCODE -ne 0) { exit `$LASTEXITCODE }; node ui/node_modules/electron/install.js; if (`$LASTEXITCODE -ne 0) { exit `$LASTEXITCODE }; if (-not (Test-Path ui/node_modules/electron/path.txt)) { exit 3 }; exit 0")

# Red: each run must fail, every failure must be an assertion in this MEU's ACs (or a TA pin / a declared
# new module's missing symbol), and MEU-71's Electron AC must fail on an expect().
function Invoke-Red71 {
    Invoke-McpBuild
    $uid = 'red71-ui-vitest'
    $mid = 'red71-mcp-vitest'
    $ucode = Invoke-Vitest $uid 'ui' $ui71
    $mcode = Invoke-Vitest $mid 'mcp-server' $mcp71
    if ($ucode -eq 0) { Stop-Check "MEU-71 ui Vitest Red expected a failing run, got exit 0" }
    if ($mcode -eq 0) { Stop-Check "MEU-71 mcp-server Vitest Red expected a failing run, got exit 0" }
    Invoke-PlanCheck 'vitest-red' @('MEU-71', "$rd/s31b-$uid.json,$rd/s31b-$mid.json", "$rd/s31b-$uid.txt,$rd/s31b-$mid.txt")
    Invoke-Build
    $code = Invoke-E2E 'red71-e2e' @($e2eSpec, '-g', 'AC-71')
    if ($code -eq 0) { Stop-Check 'MEU-71 E2E Red expected a failing run, got exit 0' }
    Invoke-PlanCheck 'e2e-red' @('MEU-71', "$rd/s31b-red71-e2e.json")
}

function Assert-PackagingPins {
    $yml = Get-Content ui/electron-builder.yml -Raw
    if ($yml -notmatch '(?m)^\s*- from: \.\./mcp-server/bundle\s*$' -or $yml -match '\.\./mcp-server/dist') { Stop-Check 'PACKAGING_INPUTS: electron-builder.yml does not copy ../mcp-server/bundle only' }
    # FUSE_PIN: the RunAsNode fuse stays on, or the MCP_LAUNCH command cannot run the server.
    if ($yml -match 'runAsNode:\s*false' -or $yml -match 'electronFuses') { Stop-Check 'FUSE_PIN: electron-builder.yml disables or configures the RunAsNode fuse' }
    $prep = (Get-Content ui/package.json -Raw | ConvertFrom-Json).scripts.'dist:prep'
    if (-not $prep.EndsWith('&& npm --prefix ../mcp-server run bundle')) { Stop-Check "PACKAGING_INPUTS: dist:prep is '$prep'" }
    Write-Host 'PASS packaging pins'
}

function Invoke-Prereq {
    foreach ($g in @('graphify-out', 'graphify-out-research')) {
        if (Test-Path $g) { Stop-Check "graph directory $g present: re-run the context-tool gate with Mat (S1)" }
    }
    # headroom on PATH needs the execution-phase context_tool_decision in task.md that names it (S1).
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
    'decouple' {
        # Amendment A-1 (row 0a, D-89 to D-91): the copies, no live Zorivest path, AC-41.3 on the copy, the issue closed.
        Invoke-PlanCheck 'decouple'
        Assert-VitestGreen 'decouple-ui-vitest' 'ui' @('tests/unit/queue-canon.test.ts')
        Assert-Stage 'decouple-issues-render' @('uv', 'run', 'python', 'tools/issue_triage.py', 'render', '--check')
        Assert-Stage 'decouple-state-render' @('uv', 'run', 'python', 'tools/meu_status.py', 'render', '--check')
        Write-Host 'PASS decouple'
    }
    'baseline' {
        Invoke-Prereq
        # Amendment A-1: row 0a's one ui edit (AC-41.3 reads the copy) precedes the baseline and is its only allowed change.
        $dirty = (git status --porcelain -- ui mcp-server | Where-Object { $_.Substring(3).Trim('"') -ne 'ui/tests/unit/queue-canon.test.ts' } | Out-String).Trim()
        if ($dirty) { Stop-Check "ui/ or mcp-server/ has uncommitted changes before the baseline: $dirty" }
        (git rev-parse HEAD).Trim() | Set-Content -Path "$plan/baseline.sha" -Encoding ascii
        Invoke-McpBuild
        Invoke-Build
        Invoke-HarnessBuild
        Invoke-PickerStub
        Assert-VitestGreen 'baseline-ui-vitest' 'ui' @()
        Assert-VitestGreen 'baseline-mcp-vitest' 'mcp-server' @()
        Assert-E2EGreen 'baseline-e2e' @()
        Invoke-PlanCheck 'baseline-counts' @("$rd/s31b-baseline-ui-vitest.json", "$rd/s31b-baseline-mcp-vitest.json", "$rd/s31b-baseline-e2e.json")
        Write-Host "PASS baseline @ $(Get-Content "$plan/baseline.sha")"
    }
    'census' {
        # TEST_AMENDMENTS census: every hit gets a disposition in walkthrough.md §Census (S2 on a new contradiction).
        $pats = @('toHaveLength\(20\)', 'listRegisteredChannels', 'getPreloadApiKeys', 'RENDERER_TO_MAIN_CHANNELS',
            'API_KEYS', 'copy-mcp-btn', 'pin-mcp-btn', 'mcp-token-present', 'copyMcpConfig', 'SERVER_INSTRUCTIONS',
            'resolveIpcChannel', 'SETTINGS_HELP_TESTIDS', 'IPC_NO_PAYLOAD', 'mcp\.json\.example', 'mcp-server/dist',
            'import\.meta\.url', 'process\.argv\[1\]')
        $argv = @('rg', '-n') + ($pats | ForEach-Object { @('-e', $_) }) + @('ui/tests', 'mcp-server/tests')
        $code = Invoke-Stage 'census' $argv
        if ($code -gt 1) { Stop-Check "census rg exit $code" }
        $hits = (Get-Content "$rd/s31b-census.txt" | Measure-Object -Line).Lines
        Write-Host "PASS census: $hits lines in $rd/s31b-census.txt; disposition each in walkthrough.md §Census"
    }
    'red71' { Invoke-Red71; Write-Host 'PASS red71' }
    'green71-main' {
        # Main, preload and server only. The renderer files (AC-71.13, AC-71.14, AC-71.15) wait for row 4.
        Invoke-McpTypes
        Invoke-McpBuild
        Assert-VitestGreen 'green71-main-mcp-vitest' 'mcp-server' $mcp71
        Assert-VitestGreen 'green71-main-ui-vitest' 'ui' $ui71Main
        Write-Host 'PASS green71-main'
    }
    'green71' {
        Invoke-McpBuild
        Assert-VitestGreen 'green71-mcp-vitest' 'mcp-server' $mcp71
        Assert-VitestGreen 'green71-ui-vitest' 'ui' $ui71
        Invoke-Build
        Assert-E2EGreen 'green71-e2e' @($e2eSpec, '-g', 'AC-71')
        Write-Host 'PASS green71'
    }
    'gate71' {
        Assert-Stage 'ui-types' @('npm', '--prefix', 'ui', 'run', 'typecheck')
        Assert-Stage 'ui-lint' @('npm', '--prefix', 'ui', 'run', 'lint')
        Invoke-McpTypes
        Invoke-McpBuild
        Assert-VitestGreen 'gate71-mcp-vitest' 'mcp-server' @()
        Assert-VitestGreen 'gate71-ui-vitest' 'ui' (@($ui71 + $regui) | Select-Object -Unique)
        Invoke-Build
        Assert-E2EGreen 'gate71-e2e' @($e2eSpec, 'tests/e2e/settings.test.ts')
        Assert-E2EGreen 'gate71-repeat' @($e2eSpec, '-g', 'AC-71', '--repeat-each=10')
        Write-Host 'PASS gate71'
    }
    'red92' {
        # A stale bundle from an earlier run would turn the existence Red green.
        Remove-Item mcp-server/bundle -Recurse -Force -ErrorAction SilentlyContinue
        $id = 'red92-mcp-vitest'
        $code = Invoke-Vitest $id 'mcp-server' $mcp92
        if ($code -eq 0) { Stop-Check 'MEU-92 Vitest Red expected a failing run, got exit 0' }
        Invoke-PlanCheck 'vitest-red' @('MEU-92', "$rd/s31b-$id.json", "$rd/s31b-$id.txt")
        Write-Host 'PASS red92'
    }
    'green92' {
        Invoke-McpTypes
        Invoke-McpBundle
        Assert-VitestGreen 'green92-mcp-vitest' 'mcp-server' $mcp92
        Write-Host 'PASS green92'
    }
    'pkg-probe' {
        Assert-PackagingPins
        Remove-Item $unpacked -Recurse -Force -ErrorAction SilentlyContinue
        Remove-Item $hermetic -Recurse -Force -ErrorAction SilentlyContinue
        Remove-Item "$plan/pkg-probe-result.json" -ErrorAction SilentlyContinue
        Assert-Stage 'pkg-dist-prep' @('npm', '--prefix', 'ui', 'run', 'dist:prep')
        Assert-Stage 'pkg-builder' @('pwsh', '-NoProfile', '-Command', 'Set-Location ui; npx electron-builder --win dir --x64; exit $LASTEXITCODE')
        $exe = "$unpacked/av-kit.exe"
        $entry = "$unpacked/resources/mcp-server/index.mjs"
        if (-not (Test-Path $exe)) { Stop-Check "$exe missing after electron-builder" }
        if (-not (Test-Path $entry)) { Stop-Check "$entry missing: the packaged tree does not hold the bundle" }
        # The hermetic copy has no node_modules anywhere above it.
        New-Item -ItemType Directory -Force -Path "$hermetic/mcp-server" | Out-Null
        Copy-Item "$unpacked/resources/mcp-server/*" "$hermetic/mcp-server/" -Recurse
        $code = Invoke-Stage 'pkg-probe-in-place' @('uv', 'run', 'python', $pc, 'mcp-probe', "$rd/s31b-pkg-probe-in-place.json", $exe, $entry)
        $code2 = Invoke-Stage 'pkg-probe-hermetic' @('uv', 'run', 'python', $pc, 'mcp-probe', "$rd/s31b-pkg-probe-hermetic.json", $exe, "$hermetic/mcp-server/index.mjs")
        Write-Host "probe exits: in-place $code, hermetic $code2"
        # PKG_EVIDENCE: the result records the hash of every bound file; pkg-current re-checks them later.
        Invoke-PlanCheck 'pkg-result' @("$rd/s31b-pkg-probe-in-place.json", "$rd/s31b-pkg-probe-hermetic.json")
        Write-Host 'PASS pkg-probe'
    }
    'gate92' {
        Invoke-McpTypes
        Invoke-McpBuild
        Invoke-McpBundle
        Assert-VitestGreen 'gate92-mcp-vitest' 'mcp-server' @()
        # SERVER_ENTRY names the bundle (index.mjs) once MEU-92 is in, so the MEU-71 unit set re-runs.
        Assert-VitestGreen 'gate92-ui-vitest' 'ui' $ui71
        # The rebuilt bundle and the packaged tree must still be the bytes row 8 proved (PKG_EVIDENCE).
        Invoke-PlanCheck 'pkg-current'
        Write-Host 'PASS gate92'
    }
    'hub' {
        Invoke-PlanCheck 'hub'
        Assert-VitestGreen 'hub-vitest' 'ui' $docSuites
        Write-Host 'PASS hub'
    }
    'task-state' { Invoke-PlanCheck 'task-state' }
    'gate' {
        # Full PROFILE D6 UI set plus the mcp-server set, fresh and in order. py-* and openapi are skipped on the
        # scope basis; mcp-audit is skipped because no tool surface changes (see skipped below).
        $out = "$plan/gate-result.json"
        Get-ChildItem -Path $rd -Filter 's31b-gate-*' -ErrorAction SilentlyContinue | Remove-Item -Force
        $product = @('ui', 'mcp-server', 'docs')
        $result = [ordered]@{
            schema              = 's31b-gate.v1'
            tested_commit       = (git rev-parse HEAD).Trim()
            product_uncommitted = @(git status --porcelain --untracked-files=all -- @product)
            # Working-tree content of every uncommitted product path, untracked files included.
            product_file_sha256 = [ordered]@{}
            lockfile_sha256     = [ordered]@{
                ui         = (Get-FileHash ui/package-lock.json -Algorithm SHA256).Hash
                mcp_server = (Get-FileHash mcp-server/package-lock.json -Algorithm SHA256).Hash
            }
            node                = (node --version).Trim()
            skipped             = 'py-types, py-lint, py-tests, openapi: no change under packages/, openapi.committed.json, pyproject.toml or uv.lock (-Check scope). mcp-audit: no MCP tool, schema or annotation changes; the audit snapshot does not cover the server instructions (AC-71.12 does), and mcp-server/scripts/audit/run.ts audits tool surfaces, not the instructions.'
            started             = (Get-Date).ToString('o')
            stages              = @()
        }
        foreach ($line in $result.product_uncommitted) {
            $path = $line.Substring(3).Trim('"')
            $result.product_file_sha256[$path] = $(if (Test-Path $path -PathType Leaf) { (Get-FileHash $path -Algorithm SHA256).Hash } else { 'deleted' })
        }
        $uvjson = "$rd/s31b-gate-ui-tests.json"
        $mvjson = "$rd/s31b-gate-mcp-tests.json"
        $ejson = "$rd/s31b-gate-ui-electron.json"
        $stages = @(
            @('gate-npm-ci', $npmCi),
            @('gate-ui-types', @('npm', '--prefix', 'ui', 'run', 'typecheck')),
            @('gate-ui-lint', @('npm', '--prefix', 'ui', 'run', 'lint')),
            @('gate-mcp-types', @('npm', '--prefix', 'mcp-server', 'run', 'typecheck')),
            # Builds precede the suites: the spawn tests read mcp-server/dist and bundle, global-setup refuses a
            # stale out/, and layout-primitives reads out-e2e.
            @('gate-mcp-build', @('npm', '--prefix', 'mcp-server', 'run', 'build')),
            @('gate-mcp-bundle', @('npm', '--prefix', 'mcp-server', 'run', 'bundle')),
            # PKG_EVIDENCE: after the fresh bundle, the packaged proof must still match every bound file.
            @('gate-pkg-current', @('uv', 'run', 'python', $pc, 'pkg-current')),
            @('gate-ui-build', @('npm', '--prefix', 'ui', 'run', 'build')),
            @('gate-ui-harness-build', @('pwsh', '-NoProfile', '-Command', "`$env:AVKIT_PRIMITIVE_HARNESS_BUILD='1'; npm --prefix ui run build -- --outDir '$((Resolve-Path ui).Path)/out-e2e'; exit `$LASTEXITCODE")),
            @('gate-picker-stub', @('npm', '--prefix', 'ui', 'run', 'build:picker-stub')),
            @('gate-mcp-tests', @('npm', '--prefix', 'mcp-server', 'run', 'test', '--', '--reporter=default', '--reporter=json', "--outputFile=$mvjson")),
            @('gate-ui-tests', @('npm', '--prefix', 'ui', 'run', 'test', '--', '--reporter=default', '--reporter=json', "--outputFile=$uvjson")),
            @('gate-ui-electron', @('npm', '--prefix', 'ui', 'run', 'test:e2e', '--', '--reporter=json', "--outputFile=$ejson")),
            @('gate-state-render', @('uv', 'run', 'python', 'tools/meu_status.py', 'render', '--check')),
            @('gate-task-contract', @('uv', 'run', 'python', 'tools/lint_task_contract.py', '--allowed-builder-classes', 'avkit_builder,avkit_coordinator,avkit_verifier', '--task', "$plan/task.md")),
            @('gate-source-audit', (@('rg', '-n', '-e', $auditPattern) + $auditSrc))
        )
        $failed = $false
        foreach ($s in $stages) {
            $code = Invoke-Stage $s[0] $s[1]
            $row = [ordered]@{ id = $s[0]; exit = $code; receipt = "$rd/s31b-$($s[0]).txt" }
            if ($s[0] -eq 'gate-source-audit') {
                # rg exit 1 = no hits (clean); 0 = hits; 2+ = IO error.
                $row.note = "rg exit $code (1 = no hits)"
                $row.exit = $(if ($code -eq 1) { 0 } else { 1 })
            } elseif ($s[0] -in @('gate-mcp-tests', 'gate-ui-tests', 'gate-ui-electron')) {
                $kind = $(if ($s[0] -eq 'gate-ui-electron') { 'e2e' } else { 'vitest' })
                $json = $(switch ($s[0]) { 'gate-mcp-tests' { $mvjson } 'gate-ui-tests' { $uvjson } default { $ejson } })
                # @(...) keeps a one-element array; $(...) would unroll it to a string, and splatting a string passes one character per argument.
                $extra = @(if ($kind -eq 'vitest') { "$rd/s31b-$($s[0]).txt" })
                & rtk proxy uv run python $pc $kind $s[0] $json "$code" @extra *> "$rd/s31b-$($s[0])-check.txt"
                $row.exit = $LASTEXITCODE
                Get-Content "$rd/s31b-$($s[0])-check.txt" | Write-Host
            }
            $result.stages += $row
            if ($row.exit -ne 0) { $failed = $true; break }
        }
        if (-not $failed) {
            $u = Get-Content $uvjson -Raw | ConvertFrom-Json
            $m = Get-Content $mvjson -Raw | ConvertFrom-Json
            $e = Get-Content $ejson -Raw | ConvertFrom-Json
            $result.ui_vitest = [ordered]@{ passed = $u.numPassedTests; failed = $u.numFailedTests; total = $u.numTotalTests }
            $result.mcp_vitest = [ordered]@{ passed = $m.numPassedTests; failed = $m.numFailedTests; total = $m.numTotalTests }
            $result.e2e = [ordered]@{ expected = $e.stats.expected; unexpected = $e.stats.unexpected; skipped = $e.stats.skipped; flaky = $e.stats.flaky }
            $result.electron = ((npm --prefix ui ls electron --depth=0 2>$null) | Select-String 'electron@' | Out-String).Trim()
            & rtk proxy uv run python $pc floors $uvjson $mvjson $ejson "$rd/s31b-gate-ui-tests.txt,$rd/s31b-gate-mcp-tests.txt" *> "$rd/s31b-gate-floors.txt"
            $fcode = $LASTEXITCODE
            Get-Content "$rd/s31b-gate-floors.txt" | Write-Host
            $result.stages += [ordered]@{ id = 'gate-floors'; exit = $fcode; receipt = "$rd/s31b-gate-floors.txt" }
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
        foreach ($m in @('MEU-71', 'MEU-92')) {
            Assert-Stage "ssot-$m" @('uv', 'run', 'python', 'tools/meu_status.py', 'update', $m, 'ready_for_review', '--plan', $plan)
        }
        Assert-Stage 'ssot-render' @('uv', 'run', 'python', 'tools/meu_status.py', 'render')
        Assert-Stage 'ssot-render-check' @('uv', 'run', 'python', 'tools/meu_status.py', 'render', '--check')
        Invoke-PlanCheck 'ssot-review'
    }
    'scope' { Invoke-PlanCheck 'scope' }
    'handoff-ac' {
        foreach ($h in @($handoff71, $handoff92)) {
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
