# Validation cases for 2026-10-14-capture-chrome (Session 34). Every task.md row and every
# implementation-plan.md §Verification Plan step calls one case:
#   pwsh -NoProfile -File docs/execution/plans/2026-10-14-capture-chrome/validate-task.ps1 -Check <name>
# Run from the worktree root (P:/av-kit-wt/s34-capture-chrome). Each case runs its tools through
# `rtk proxy`, writes raw receipts to C:/Temp/av-kit/ (prefix s34-), and exits nonzero on the first
# refusal. JSON evaluation lives in plan_checks.py (CASE_EVIDENCE: named cases in the raw reports, never counts);
# this script runs the tools and never edits product files.
param(
    [Parameter(Mandatory = $true)][string]$Check
)
$ErrorActionPreference = 'Stop'
# Native exit codes are read explicitly from $LASTEXITCODE; never let pwsh 7.4+ turn them into throws.
$PSNativeCommandUseErrorActionPreference = $false
$rd = 'C:/Temp/av-kit'
New-Item -ItemType Directory -Force -Path $rd | Out-Null
$env:RECEIPTS_DIR = $rd
$plan = 'docs/execution/plans/2026-10-14-capture-chrome'
if (-not (Test-Path "$plan/plan_checks.py")) { throw "run from the worktree root (no $plan/plan_checks.py here)" }
Remove-Item Env:ELECTRON_RUN_AS_NODE -ErrorAction SilentlyContinue
Remove-Item Env:AVKIT_E2E_OUT_DIR -ErrorAction SilentlyContinue

$handoffs = @(
    '.agent/context/handoffs/2026-10-14-capture-chrome-MEU-80-handoff.md',
    '.agent/context/handoffs/2026-10-14-capture-chrome-MEU-81-handoff.md')
$execReview = '.agent/context/handoffs/2026-10-14-capture-chrome-implementation-critical-review.md'
$execLoop = 's34-execution-2026-10-14-capture-chrome'
$grouping = '.agent/context/grouping/2026-10-09-triage-residuals-session-grouping.md'
$issues = @('CAPTURE-TOOLTIPS-NOT-SHOWN', 'CAPTURE-ACTION-ROW-ICONS', 'CAPTURE-MARKS-ROW-SQUEEZED',
    'CAPTURE-SAMPLE-ORIGINAL-UNLABELED', 'CAPTURE-HOTKEY-BANNER-GAP')
$stub = 'native/region-picker-stub/publish/avkit-region-picker-stub.exe'
# Regression neighbours of the targeted Green runs (implementation-plan.md §Verification Plan 4).
$neighbours = @('capture-page.behavior.test.ts', 'capture-toolbar.test.ts', 'capture-page.test.ts',
    'layout-primitives.test.ts', 'queue-card.test.ts', 'queue-card-slots.test.tsx', 'transcript-page.behavior.test.ts',
    'convert-page.behavior.test.ts', 'console-polish.test.ts', 'capture-help-content.test.ts', 'queue-dnd.test.ts')
# The hover, geometry and keyboard specs repeated ten times by the targeted gates; one -g run each (no '|' through
# npm/cmd). e2e-ok --ac then requires that exact case in the report.
$repeat80 = @('AC-80.10', 'AC-80.11')
$repeat81 = @('AC-80.10', 'AC-80.11', 'AC-81.9', 'AC-81.11', 'AC-81.14')

function Fail([string]$Msg) {
    Write-Host "FAIL: $Msg"
    exit 1
}

function Invoke-Receipt([string]$Id, [string[]]$Argv) {
    $receipt = "$rd/$Id.txt"
    & rtk proxy @Argv *> $receipt
    $code = $LASTEXITCODE
    Get-Content $receipt -Tail 15 | Where-Object { $_ -notmatch 'VIRTUAL_ENV' } | Write-Host
    return $code
}

function Step([string]$Id, [string[]]$Argv) {
    $code = Invoke-Receipt $Id $Argv
    if ($code -ne 0) { Fail "$Id exit $code (receipt $rd/$Id.txt)" }
}

function PlanCheck([string]$Sub, [string[]]$Rest = @()) {
    $receipt = "$rd/s34-pc-$Sub.txt"
    & rtk proxy uv run python "$plan/plan_checks.py" $Sub @Rest *> $receipt
    $code = $LASTEXITCODE
    Get-Content $receipt | Where-Object { $_ -notmatch 'VIRTUAL_ENV' } | Write-Host
    if ($code -ne 0) { Fail "plan_checks.py $Sub refused (exit $code; $receipt)" }
}

function Get-Baseline {
    if (-not (Test-Path "$plan/baseline.sha")) { Fail 'baseline.sha is missing (row 0)' }
    return (Get-Content "$plan/baseline.sha" -Raw).Trim()
}

function Get-Identity {
    $out = & uv run python "$plan/plan_checks.py" identity 2>$null
    if ($LASTEXITCODE -ne 0) { Fail 'plan_checks.py identity failed' }
    return ($out | Select-Object -Last 1).Trim()
}

# Vitest with two reporters: the default text (the receipt, read for unhandled errors) and JSON (the named cases).
# An empty file list runs everything.
function Invoke-Vitest([string]$Id, [string[]]$Files) {
    $json = "$rd/$Id.json"
    Remove-Item $json -ErrorAction SilentlyContinue
    $argv = @('npm', '--prefix', 'ui', 'run', 'test', '--') + $Files + @('--reporter=default', '--reporter=json', "--outputFile.json=$json")
    return (Invoke-Receipt $Id $argv)
}

function Test-VitestOk([string]$Id, [string[]]$Files, [string]$Meu = '') {
    $code = Invoke-Vitest $Id $Files
    $rest = @('--json', "$rd/$Id.json", '--txt', "$rd/$Id.txt", '--rc', "$code")
    if ($Meu) { $rest += @('--meu', $Meu) }
    PlanCheck 'vitest-ok' $rest
}

# Playwright _electron through ui/scripts/playwright-with-outputfile.mjs, which turns --outputFile into the JSON reporter.
function Invoke-E2e([string]$Id, [string[]]$PwArgs) {
    $json = "$rd/$Id.json"
    Remove-Item $json -ErrorAction SilentlyContinue
    $argv = @('npm', '--prefix', 'ui', 'run', 'test:e2e', '--') + $PwArgs + @('--reporter=json', "--outputFile=$json")
    return (Invoke-Receipt $Id $argv)
}

# $Check holds extra e2e-ok arguments: --meu, --tags, --ac.
function Test-E2eOk([string]$Id, [string[]]$PwArgs, [string[]]$Check = @()) {
    $code = Invoke-E2e $Id $PwArgs
    PlanCheck 'e2e-ok' (@('--json', "$rd/$Id.json", '--rc', "$code") + $Check)
}

function Build-Ui([string]$Id, [switch]$Harness) {
    Step "$Id-build" @('npm', '--prefix', 'ui', 'run', 'build')
    if ($Harness) {
        Step "$Id-harness" @('pwsh', '-NoProfile', '-Command', "`$env:AVKIT_PRIMITIVE_HARNESS_BUILD='1'; npm --prefix ui run build -- --outDir '$((Resolve-Path ui).Path)/out-e2e'; exit `$LASTEXITCODE")
    }
}

# CASE_EVIDENCE, Red mode: plan_checks.py reads AC_CASES, SETUP_SENTINEL, TA_TAGS, FIXTURE_RED and BASELINE_RED itself.
function Invoke-Red([string]$Meu, [string[]]$Files) {
    $id = "s34-red-$Meu-vitest"
    $code = Invoke-Vitest $id $Files
    PlanCheck 'vitest-red' @('--meu', $Meu, '--json', "$rd/$id.json", '--txt', "$rd/$id.txt", '--rc', "$code")
    Build-Ui "s34-red-$Meu"
    $code = Invoke-E2e "s34-red-$Meu-e2e" @('capture-inbox', 'console-chrome', '-g', "AC-$Meu")
    PlanCheck 'e2e-red' @('--meu', $Meu, '--json', "$rd/s34-red-$Meu-e2e.json", '--rc', "$code")
}

# MEU-81's Green also re-runs MEU-80's cases, so its Electron filter is AC-8[01].
function Invoke-Green([string]$Meu, [string[]]$Files, [string]$Grep) {
    Test-VitestOk "s34-green-$Meu-vitest" ($Files + $neighbours) $Meu
    Build-Ui "s34-green-$Meu"
    Test-E2eOk "s34-green-$Meu-e2e" @('capture-inbox', 'console-chrome', '-g', $Grep) @('--meu', $Meu)
}

function Invoke-TargetedGate([string]$Meu, [string[]]$Repeat) {
    Step "s34-gate$Meu-types" @('npm', '--prefix', 'ui', 'run', 'typecheck')
    Step "s34-gate$Meu-lint" @('npm', '--prefix', 'ui', 'run', 'lint')
    Test-VitestOk "s34-gate$Meu-vitest" @() $Meu
    Build-Ui "s34-gate$Meu" -Harness
    Test-E2eOk "s34-gate$Meu-e2e" @('capture-inbox', 'console-chrome') @('--meu', $Meu, '--tags')
    $i = 0
    foreach ($ac in $Repeat) {
        $i++
        $g = ($ac -replace '\.', '\.') + '\b'
        Test-E2eOk "s34-gate$Meu-repeat-$i" @('capture-inbox', 'console-chrome', '-g', $g, '--repeat-each=10', '--output', "$rd/s34-repeat-$Meu-$i") @('--ac', $ac)
    }
}

switch ($Check) {
    'install' {
        Step 's34-install-uv' @('uv', 'sync', '--frozen', '--all-packages')
        Step 's34-install-ui' @('npm', '--prefix', 'ui', 'ci')
        # Electron 42 has no postinstall; install its binary serially (Session 27 A-5).
        Step 's34-install-electron' @('node', 'ui/node_modules/electron/install.js')
        Step 's34-install-mcp' @('npm', '--prefix', 'mcp-server', 'ci')
        Step 's34-install-stub' @('npm', '--prefix', 'ui', 'run', 'build:picker-stub')
        'PASS install'
        exit 0
    }
    'prereq' {
        foreach ($d in 'graphify-out', 'graphify-out-research') {
            if (Test-Path $d) { Fail "$d exists: re-run the context-tool gate with the human (S1)" }
        }
        PlanCheck 'meu-state' @('--want', 'MEU-65=approved', '--want', 'MEU-67=approved', '--want', 'MEU-80=pending', '--want', 'MEU-81=pending')
        $wt = "$plan/walkthrough.md"
        if (-not (Test-Path $wt) -or -not (Select-String -Path $wt -Pattern '^## Execution authorization' -Quiet)) {
            Fail 'walkthrough.md §Execution authorization is missing (record the user''s execution message first)'
        }
        foreach ($p in 'ui/node_modules', 'ui/node_modules/electron/path.txt', $stub) {
            if (-not (Test-Path $p)) { Fail "$p is missing: run -Check install" }
        }
        # HOTKEY_IN_USE_FIXTURE needs F2 free in the free run (S4).
        Add-Type -Namespace S34 -Name Hotkey -MemberDefinition '[DllImport("user32.dll")] public static extern bool RegisterHotKey(IntPtr h, int id, uint mods, uint vk); [DllImport("user32.dll")] public static extern bool UnregisterHotKey(IntPtr h, int id);'
        if (-not [S34.Hotkey]::RegisterHotKey([IntPtr]::Zero, 0x5334, 0, 0x71)) { Fail 'F2 is held by another process (S4)' }
        [void][S34.Hotkey]::UnregisterHotKey([IntPtr]::Zero, 0x5334)
        'PASS prereq'
        exit 0
    }
    'baseline' {
        # Nothing may be changed outside this plan's own files (plan folder, plan-review handoff).
        PlanCheck 'clean'
        (git rev-parse HEAD).Trim() | Set-Content -Path "$plan/baseline.sha" -NoNewline
        Test-VitestOk 's34-baseline-vitest' @()
        Build-Ui 's34-baseline' -Harness
        Test-E2eOk 's34-baseline-e2e' @('capture-inbox', 'console-chrome', 'convert-queue', 'download-queue', 'transcript-queue')
        "PASS baseline @ $(Get-Baseline)"
        exit 0
    }
    'census' {
        $pattern = 'capture-nudge-|capture-color-sample|CAPTURE_NUDGE_|CAPTURE_COLOR_SAMPLE|capture-sample|image-reason|hotkey-banner|Sample original|Save overlay|getAttribute\(''title''\)|toHaveAttribute\(''title''|\.title\)|capture-chrome-marks|capture-remove-mark|queue-card-kebab|queue-card-drag-handle|console-close|bulk-toast-dismiss|up-btn|down-btn|convert-staged-remove|HELP_EDIT_SENTENCE|819760B9|aria-describedby|setActivatorNodeRef|listeners\.'
        & rtk proxy rg -n --path-separator / -e $pattern ui/tests *> "$rd/s34-census.txt"
        if ($LASTEXITCODE -ne 0) { Fail "census rg exit $LASTEXITCODE (0 = hits expected)" }
        PlanCheck 'census-check' @('--census', "$rd/s34-census.txt")
        exit 0
    }
    'probe' {
        if (-not (Test-Path "$plan/tooltip-probe.mjs")) { Fail "$plan/tooltip-probe.mjs is missing" }
        $head = (git rev-parse HEAD).Trim()
        if ($head -ne (Get-Baseline)) { Fail "HEAD $head is not baseline.sha (the probe runs on the baseline product)" }
        PlanCheck 'clean'
        Build-Ui 's34-probe'
        $runJson = "$rd/s34-probe-run.json"
        Remove-Item $runJson -ErrorAction SilentlyContinue
        Get-ChildItem -Path $rd -Filter 's34-probe-h*.png' -ErrorAction SilentlyContinue | Remove-Item -Force
        $started = (Get-Date).ToString('o')
        $code = Invoke-Receipt 's34-probe-run' @('node', "$plan/tooltip-probe.mjs", '--out', $rd, '--run', $runJson)
        if (-not (Test-Path $runJson)) { Fail "tooltip-probe.mjs wrote no run record (exit $code)" }
        # PROBE_RUN (D-28, D-31): bind the record to this producer, head, clean check, build, probe script and
        # receipt. plan_checks.py root-cause re-hashes all three files, so a later rebuild or edit refuses.
        $run = Get-Content $runJson -Raw | ConvertFrom-Json -AsHashtable
        $run.check = 'probe'
        $run.head = $head
        $run.gated_clean = $true
        $run.build_sha256 = (Get-FileHash ui/out/main/index.js -Algorithm SHA256).Hash
        $run.probe_sha256 = (Get-FileHash "$plan/tooltip-probe.mjs" -Algorithm SHA256).Hash
        $run.receipt_sha256 = (Get-FileHash "$rd/s34-probe-run.txt" -Algorithm SHA256).Hash
        $run.exit = $code
        $run.started = $started
        $run.finished = (Get-Date).ToString('o')
        $run | ConvertTo-Json -Depth 8 | Set-Content -Path $runJson -Encoding utf8
        if ($code -ne 0) { Fail "tooltip-probe.mjs exit $code (receipt $rd/s34-probe-run.txt)" }
        'PASS probe: view the 6 PNGs, then write walkthrough.md §Root cause and run -Check root-cause'
        exit 0
    }
    'root-cause' {
        PlanCheck 'root-cause'
        exit 0
    }
    'red-80' {
        Invoke-Red '80' @('tooltip.test.tsx', 'icon-hints.test.ts', 'capture-page.behavior.test.ts', 'queue-card.test.ts', 'queue-card-slots.test.tsx')
        'PASS red-80'
        exit 0
    }
    'green-80' {
        Invoke-Green '80' @('tooltip.test.tsx', 'icon-hints.test.ts') 'AC-80'
        'PASS green-80'
        exit 0
    }
    'gate80' {
        Invoke-TargetedGate '80' $repeat80
        'PASS gate80'
        exit 0
    }
    'red-81' {
        Invoke-Red '81' @('capture-action-row.test.ts', 'capture-page.behavior.test.ts', 'capture-help-content.test.ts', 'layout-primitives.test.ts')
        'PASS red-81'
        exit 0
    }
    'green-81' {
        Invoke-Green '81' @('capture-action-row.test.ts', 'tooltip.test.tsx', 'icon-hints.test.ts') 'AC-8[01]'
        'PASS green-81'
        exit 0
    }
    'gate81' {
        Invoke-TargetedGate '81' $repeat81
        'PASS gate81'
        exit 0
    }
    'registry' {
        $base = Get-Baseline
        PlanCheck 'registry' @('--baseline', $base)
        PlanCheck 'fixture' @('--baseline', $base)
        exit 0
    }
    'hub' {
        PlanCheck 'hub' @('--baseline', (Get-Baseline))
        Step 's34-hub-render-check' @('uv', 'run', 'python', 'tools/meu_status.py', 'render', '--check')
        Test-VitestOk 's34-hub-vitest' @('layout-canon.test.ts', 'gui-actions-audit.test.ts', 'capture-page.test.ts')
        exit 0
    }
    'task-state' {
        PlanCheck 'task-state'
        exit 0
    }
    'gate' {
        $out = "$plan/gate-result.json"
        # Execution review R1 F2: clear this run's names only; archived runs (s34-gate-run<n>*) are kept.
        Get-ChildItem -Path $rd -Filter 's34-gate-*' -ErrorAction SilentlyContinue |
            Where-Object { $_.Name -notmatch '^s34-gate-run\d' } | Remove-Item -Recurse -Force
        PlanCheck 'static'
        PlanCheck 'selftest'
        $vjson = "$rd/s34-gate-vitest.json"
        $vtxt = "$rd/s34-gate-ui-tests.txt"
        $ejson = "$rd/s34-gate-e2e.json"
        $result = [ordered]@{
            schema              = 's34-gate.v2'
            tested_commit       = (git rev-parse HEAD).Trim()
            vitest_json         = $vjson
            vitest_txt          = $vtxt
            e2e_json            = $ejson
            lockfile_sha256     = (Get-FileHash ui/package-lock.json -Algorithm SHA256).Hash
            mcp_lockfile_sha256 = (Get-FileHash mcp-server/package-lock.json -Algorithm SHA256).Hash
            uv_lock_sha256      = (Get-FileHash uv.lock -Algorithm SHA256).Hash
            node                = (node --version).Trim()
            identity_before     = (Get-Identity)
            started             = (Get-Date).ToString('o')
            stages              = @()
            pytest              = $null
            vitest              = $null
            e2e                 = $null
        }

        function Invoke-Stage([string]$Id, [string[]]$Argv) {
            $receipt = "$rd/s34-gate-$Id.txt"
            & rtk proxy @Argv *> $receipt
            $code = $LASTEXITCODE
            $script:result.stages += [ordered]@{ id = $Id; argv = ($Argv -join ' '); exit = $code; receipt = $receipt }
            Get-Content $receipt -Tail 15 | Write-Host
            return $code
        }

        # Must match AUDIT_SRC and its pattern in implementation-plan.md (plan_checks.py static).
        $auditSrc = @(
            'ui/src/renderer/src/components/ui/Tooltip.tsx',
            'ui/src/renderer/src/features/capture/ToolbarIconButton.tsx',
            'ui/src/renderer/src/features/capture/CaptureViewport.tsx',
            'ui/src/renderer/src/features/capture/CapturePage.tsx',
            'ui/src/renderer/src/features/capture/capture-toolbar.ts',
            'ui/src/renderer/src/components/layout/ConsolePanel.tsx',
            'ui/src/renderer/src/components/queue/BulkResultToast.tsx',
            'ui/src/renderer/src/components/queue/QueueCard.tsx',
            'ui/src/renderer/src/components/queue/QueueCardMenu.tsx',
            'ui/src/renderer/src/features/transcript/TranscriptPage.tsx',
            'ui/src/renderer/src/features/converter/ConvertPage.tsx')
        $auditPattern = 'TODO|FIXME|transition-all|bg-\[#|console\.log\(|@ts-ignore|@ts-expect-error|: any\b'
        $pytxt = "$rd/s34-gate-py-tests.txt"
        # The GATE stage order; plan_checks.py static and gate-check compare it with implementation-plan.md.
        $stages = @(
            @('ui-ci',            @('pwsh', '-NoProfile', '-Command', "npm --prefix ui ci; if (`$LASTEXITCODE -ne 0) { exit `$LASTEXITCODE }; node ui/node_modules/electron/install.js; if (`$LASTEXITCODE -ne 0) { exit `$LASTEXITCODE }; if (-not (Test-Path ui/node_modules/electron/path.txt)) { exit 3 }; exit 0")),
            @('mcp-ci',           @('npm', '--prefix', 'mcp-server', 'ci')),
            @('py-types',         @('uv', 'run', 'pyright', 'packages/')),
            @('py-lint',          @('uv', 'run', 'ruff', 'check', 'packages/', 'tests/')),
            @('ui-types',         @('npm', '--prefix', 'ui', 'run', 'typecheck')),
            @('ui-lint',          @('npm', '--prefix', 'ui', 'run', 'lint')),
            @('mcp-types',        @('npm', '--prefix', 'mcp-server', 'run', 'typecheck')),
            @('py-tests',         @('uv', 'run', 'pytest', 'tests/', '-x', '--tb=short', '-q')),
            @('ui-tests',         @('npm', '--prefix', 'ui', 'run', 'test', '--', '--reporter=default', '--reporter=json', "--outputFile.json=$vjson")),
            @('ui-build',         @('npm', '--prefix', 'ui', 'run', 'build')),
            @('ui-harness-build', @('pwsh', '-NoProfile', '-Command', "`$env:AVKIT_PRIMITIVE_HARNESS_BUILD='1'; npm --prefix ui run build -- --outDir '$((Resolve-Path ui).Path)/out-e2e'; exit `$LASTEXITCODE")),
            # The MCP suite asserts the built dist exists (AC-32.8, AC-38.8), so build first.
            @('mcp-build',        @('npm', '--prefix', 'mcp-server', 'run', 'build')),
            @('mcp-tests',        @('npm', '--prefix', 'mcp-server', 'run', 'test')),
            @('openapi',          @('uv', 'run', 'python', 'tools/export_openapi.py', '--check', 'openapi.committed.json')),
            @('state-render',     @('uv', 'run', 'python', 'tools/meu_status.py', 'render', '--check')),
            @('ui-electron',      @('npm', '--prefix', 'ui', 'run', 'test:e2e', '--', '--reporter=json', "--outputFile=$ejson")),
            @('source-audit',     (@('rg', '-n', '-e', $auditPattern) + $auditSrc))
        )
        $failed = $false
        foreach ($s in $stages) {
            $code = Invoke-Stage $s[0] $s[1]
            if ($s[0] -eq 'source-audit') {
                # rg exit 1 means zero hits (clean); 0 means hits; 2+ means an IO error.
                $clean = ($code -eq 1)
                $result.stages[-1].exit = $(if ($clean) { 0 } else { 1 })
                $result.stages[-1].note = "rg exit $code (1 = no hits)"
                if (-not $clean) { $failed = $true; break }
            } elseif ($s[0] -eq 'ui-tests') {
                # BASELINE_RED fails the run, so the stage's exit is the CASE_EVIDENCE verdict; raw_exit keeps Vitest's.
                & rtk proxy uv run python "$plan/plan_checks.py" vitest-ok --meu 81 --json $vjson --txt $vtxt --rc "$code" *> "$rd/s34-gate-ui-tests-verdict.txt"
                $verdict = $LASTEXITCODE
                Get-Content "$rd/s34-gate-ui-tests-verdict.txt" | Where-Object { $_ -notmatch 'VIRTUAL_ENV' } | Write-Host
                $result.stages[-1].raw_exit = $code
                $result.stages[-1].exit = $(if ($verdict -eq 0) { 0 } else { 1 })
                $result.stages[-1].note = "exit = plan_checks.py vitest-ok --meu 81 (receipt s34-gate-ui-tests-verdict.txt)"
                if ($verdict -ne 0) { $failed = $true; break }
            } elseif ($code -ne 0) { $failed = $true; break }
        }
        $ran = @($result.stages | ForEach-Object { $_.id })
        if ($ran -contains 'py-tests' -and (Test-Path $pytxt)) {
            $summary = (Get-Content $pytxt | Select-String -Pattern '(\d+) passed' | Select-Object -Last 1)
            $failedMatch = (Get-Content $pytxt | Select-String -Pattern '(\d+) failed' | Select-Object -Last 1)
            $result.pytest = [ordered]@{
                passed = $(if ($summary) { [int]$summary.Matches[0].Groups[1].Value } else { $null })
                failed = $(if ($failedMatch) { [int]$failedMatch.Matches[0].Groups[1].Value } else { 0 })
            }
        }
        if ($ran -contains 'ui-tests' -and (Test-Path $vjson)) {
            $v = Get-Content $vjson -Raw | ConvertFrom-Json
            $result.vitest = [ordered]@{ passed = $v.numPassedTests; failed = $v.numFailedTests; total = $v.numTotalTests }
        }
        if ($ran -contains 'ui-electron' -and (Test-Path $ejson)) {
            $e = Get-Content $ejson -Raw | ConvertFrom-Json
            $result.e2e = [ordered]@{ expected = $e.stats.expected; unexpected = $e.stats.unexpected; skipped = $e.stats.skipped; flaky = $e.stats.flaky }
        }
        if ($ran -contains 'py-tests' -and ($null -eq $result.pytest -or $null -eq $result.pytest.passed)) { Write-Host 'FAIL: py-tests ran but produced no pytest summary'; $failed = $true }
        if ($ran -contains 'ui-tests' -and $null -eq $result.vitest) { Write-Host 'FAIL: ui-tests ran but produced no Vitest JSON'; $failed = $true }
        if ($ran -contains 'ui-electron' -and $null -eq $result.e2e) { Write-Host 'FAIL: ui-electron ran but produced no Playwright JSON'; $failed = $true }
        $result.identity_after = (Get-Identity)
        # D-31: bind the result to this producer and to the exact raw reports gate-check will re-read.
        $result.check = 'gate'
        foreach ($k in 'vitest_json', 'vitest_txt', 'e2e_json') {
            $result["${k}_sha256"] = $(if (Test-Path $result[$k]) { (Get-FileHash $result[$k] -Algorithm SHA256).Hash } else { $null })
        }
        $result.finished = (Get-Date).ToString('o')
        $result | ConvertTo-Json -Depth 6 | Set-Content -Path $out -Encoding utf8
        Get-Content $out
        if ($failed) { Fail 'GATE failed; see the receipts named in gate-result.json' }
        'PASS GATE (run -Check gate-check next)'
        exit 0
    }
    'gate-check' {
        PlanCheck 'gate-check' @('--result', "$plan/gate-result.json")
        exit 0
    }
    'ssot-review' {
        Step 's34-meu-80-rfr' @('uv', 'run', 'python', 'tools/meu_status.py', 'update', 'MEU-80', 'ready_for_review', '--plan', $plan)
        Step 's34-meu-81-rfr' @('uv', 'run', 'python', 'tools/meu_status.py', 'update', 'MEU-81', 'ready_for_review', '--plan', $plan)
        Step 's34-rfr-render' @('uv', 'run', 'python', 'tools/meu_status.py', 'render')
        Step 's34-rfr-render-check' @('uv', 'run', 'python', 'tools/meu_status.py', 'render', '--check')
        PlanCheck 'ssot-review-state'
        exit 0
    }
    'scope' {
        PlanCheck 'scope' @('--baseline', (Get-Baseline))
        exit 0
    }
    'handoff-ac' {
        # A-10: the final full record must be bound to the state under review (output-evidence-policy.md).
        $state = Get-Identity
        foreach ($h in $handoffs) {
            $meu = $(if ($h -match 'MEU-(\d+)') { $Matches[1] } else { 'x' })
            Step "s34-handoff-ac-$meu" @('uv', 'run', 'python', 'tools/validate_closeout_artifacts.py', '--plan', "$plan/implementation-plan.md", '--handoff', $h, '--ac-coverage-only')
            Step "s34-handoff-evidence-$meu" @('uv', 'run', 'python', 'tools/durable_evidence.py', $h, '--require-full', '--expected-state', $state)
        }
        PlanCheck 'handoff-cases'
        'PASS handoff-ac'
        exit 0
    }
    'look-check' {
        PlanCheck 'look-check' @('--result', "$plan/gate-result.json")
        exit 0
    }
    'review-check' {
        PlanCheck 'review-check' @('--review', $execReview, '--loop-id', $execLoop)
        Step 's34-review-state' @('uv', 'run', 'python', 'tools/validate_closeout_artifacts.py', '--review', $execReview, '--review-state-only', '--expected-review-mode', 'execution', '--expected-target-plan', "$plan/implementation-plan.md", '--max-review-rounds', '6', '--output', "$rd/s34-review-state.json")
        Step 's34-review-approved' @('uv', 'run', 'python', 'tools/validate_closeout_artifacts.py', '--review', $execReview, '--review-state-receipt', "$rd/s34-review-state.json", '--approved-state-only', '--max-review-rounds', '6')
        'PASS review-check'
        exit 0
    }
    'reflection' {
        $refl = 'docs/execution/reflections/2026-10-14-capture-chrome-reflection.md'
        $base = @('uv', 'run', 'python', 'tools/validate_closeout_artifacts.py', '--reflection', $refl,
            '--reflection-template', 'docs/execution/reflections/TEMPLATE.md', '--reflection-schema', '.agent/schemas/reflection.v1.yaml',
            '--decision-source', "$plan/implementation-plan.md", '--decision-source', $handoffs[0], '--decision-source', $handoffs[1],
            '--decision-source', $grouping, '--decision-source', '.agent/context/known-issues.yaml')
        foreach ($iss in $issues) {
            Step "s34-reflection-$iss" ($base + @('--decision-issue', $iss))
        }
        'PASS reflection'
        exit 0
    }
    'post-review-state' {
        Step 's34-meu-80-approved' @('uv', 'run', 'python', 'tools/meu_status.py', 'update', 'MEU-80', 'approved', '--plan', $plan)
        Step 's34-meu-81-approved' @('uv', 'run', 'python', 'tools/meu_status.py', 'update', 'MEU-81', 'approved', '--plan', $plan)
        Step 's34-approved-render' @('uv', 'run', 'python', 'tools/meu_status.py', 'render')
        Step 's34-approved-render-check' @('uv', 'run', 'python', 'tools/meu_status.py', 'render', '--check')
        PlanCheck 'post-review'
        Step 's34-issues-render-check' @('uv', 'run', 'python', 'tools/issue_triage.py', 'render', '--check')
        Test-VitestOk 's34-post-doc-vitest' @('layout-canon.test.ts', 'queue-canon.test.ts', 'gui-actions-audit.test.ts')
        'PASS post-review-state'
        exit 0
    }
    default { throw "Unknown check: $Check" }
}
