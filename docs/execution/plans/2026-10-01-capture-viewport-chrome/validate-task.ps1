# WINDOWS_GATE for 2026-10-01-capture-viewport-chrome (Session 29). Human-run by Mat;
# see human-gate-decision.md A-1 and local-requests.md §GATE (the CAPTURE_LOOK checklist follows it by hand).
# Run from P:/av-kit on the pushed commit under review:
#   git pull origin claude/bold-edison-b91w56
#   pwsh -NoProfile -File docs/execution/plans/2026-10-01-capture-viewport-chrome/validate-task.ps1 -Check windows-gate
# windows-gate runs the full PROFILE D6 set (Python, UI, MCP, OpenAPI, state render, real Electron)
# in the same stage order as validate-task.sh windows-gate-check, through `rtk proxy`, and stops at
# the first failure (later stages are not_run). It writes its result JSON next to this script.
# Then commit and push only that file:
#   git add docs/execution/plans/2026-10-01-capture-viewport-chrome/windows-gate-result.json
#   git commit -m "docs(execution): record Session 29 Windows gate (attempt N)"
#   git push origin claude/bold-edison-b91w56
param([Parameter(Mandatory = $true)][string]$Check)
$ErrorActionPreference = 'Stop'
# Native exit codes are read explicitly from $LASTEXITCODE; never let pwsh 7.4+ turn them into throws.
$PSNativeCommandUseErrorActionPreference = $false
$rd = 'C:/Temp/av-kit'
New-Item -ItemType Directory -Force -Path $rd | Out-Null
$plan = 'docs/execution/plans/2026-10-01-capture-viewport-chrome'
$resultFiles = 'windows-gate-result\.json'

function Get-CleanTree {
    # A leftover result file from an earlier run is not a dirty tree.
    return [string]::IsNullOrWhiteSpace((git status --porcelain | Where-Object { $_ -notmatch $resultFiles } | Out-String))
}
Remove-Item Env:ELECTRON_RUN_AS_NODE -ErrorAction SilentlyContinue
Remove-Item Env:AVKIT_E2E_OUT_DIR -ErrorAction SilentlyContinue

if ($Check -eq 'windows-gate') {
    $out = Join-Path $plan 'windows-gate-result.json'
    # External-input preflight (cloud-local §3.2): record, and on attempt >= 2 compare with the previous run.
    $afHead = (git -C P:/agentic-framework rev-parse HEAD 2>$null | Out-String).Trim()
    $regHash = $(if (Test-Path 'P:/.agent/model-registry.json') { (Get-FileHash 'P:/.agent/model-registry.json' -Algorithm SHA256).Hash } else { '' })
    $prev = $(if (Test-Path $out) { Get-Content $out -Raw | ConvertFrom-Json } else { $null })
    $drift = $false
    if ($null -ne $prev -and $null -ne $prev.preflight) {
        $drift = ($prev.preflight.agentic_framework_head -ne $afHead) -or ($prev.preflight.agent_registry_sha256 -ne $regHash)
    }
    $result = [ordered]@{
        schema              = 's29-windows-gate.v1'
        tested_commit       = (git rev-parse HEAD).Trim()
        clean_tree          = (Get-CleanTree)
        lockfile_sha256     = (Get-FileHash ui/package-lock.json -Algorithm SHA256).Hash
        mcp_lockfile_sha256 = (Get-FileHash mcp-server/package-lock.json -Algorithm SHA256).Hash
        uv_lock_sha256      = (Get-FileHash uv.lock -Algorithm SHA256).Hash
        electron            = ((npm --prefix ui ls electron --depth=0 2>$null) | Select-String 'electron@' | Out-String).Trim()
        node                = (node --version).Trim()
        preflight           = [ordered]@{ agentic_framework_head = $afHead; agent_registry_sha256 = $regHash; drift = $drift }
        # Carry the first counted attempt's pytest total forward (COUNT_FLOORS), never a later partial run's.
        pytest_floor        = $(if ($null -ne $prev -and $null -ne $prev.pytest_floor) { $prev.pytest_floor } elseif ($null -ne $prev -and $null -ne $prev.pytest -and $null -ne $prev.pytest.passed) { $prev.pytest.passed } else { $null })
        started             = (Get-Date).ToString('o')
        stages              = @()
        pytest              = $null
        vitest              = $null
        e2e                 = $null
    }
    if ($drift) {
        $result.finished = (Get-Date).ToString('o')
        $result | ConvertTo-Json -Depth 6 | Set-Content -Path $out -Encoding utf8
        Write-Error "PREFLIGHT drift: P:/agentic-framework HEAD or P:/.agent registry changed since the previous attempt; report before stage 1"
        exit 1
    }

    function Invoke-Stage([string]$Id, [string[]]$Argv) {
        $receipt = "$rd/s29-win-$Id.txt"
        & rtk proxy @Argv *> $receipt
        $code = $LASTEXITCODE
        $script:result.stages += [ordered]@{ id = $Id; argv = ($Argv -join ' '); exit = $code; receipt = $receipt }
        Get-Content $receipt -Tail 15 | Write-Host
        return $code
    }

    # Must match AUDIT_SRC and PREFIX_AUDIT in validate-task.sh.
    $auditSrc = @(
        'ui/src/renderer/src/features/capture/CaptureViewport.tsx', 'ui/src/renderer/src/features/capture/CapturePage.tsx',
        'ui/src/renderer/src/features/capture/capture-toolbar.ts', 'ui/src/renderer/src/features/capture/capture-zoom.ts',
        'ui/src/renderer/src/features/capture/capture-fit-map.ts', 'ui/src/renderer/src/features/capture/capture-help-content.ts',
        'ui/src/renderer/src/components/ui/Disclosure.tsx')
    $auditPattern = 'TODO|FIXME|transition-all|bg-\[#|console\.log\(|@ts-ignore|@ts-expect-error|: any\b'
    $vjson = "$rd/s29-win-vitest.json"
    $ejson = "$rd/s29-win-e2e.json"
    $pytxt = "$rd/s29-win-py-tests.txt"
    $stages = @(
        # Session 27 A-5: Electron 42 has no postinstall; its binary downloads on the first require. Install it
        # here, serially (the same install.js index.js would spawn; idempotent, checksum-pinned), so
        # parallel Vitest workers never race the extraction (attempt 5: os error 183).
        @('npm-ci',           @('pwsh', '-NoProfile', '-Command', "npm --prefix ui ci; if (`$LASTEXITCODE -ne 0) { exit `$LASTEXITCODE }; node ui/node_modules/electron/install.js; if (`$LASTEXITCODE -ne 0) { exit `$LASTEXITCODE }; if (-not (Test-Path ui/node_modules/electron/path.txt)) { exit 3 }; exit 0")),
        @('mcp-npm-ci',       @('npm', '--prefix', 'mcp-server', 'ci')),
        @('py-types',         @('uv', 'run', 'pyright', 'packages/')),
        @('py-lint',          @('uv', 'run', 'ruff', 'check', 'packages/', 'tests/')),
        @('ui-types',         @('npm', '--prefix', 'ui', 'run', 'typecheck')),
        @('ui-lint',          @('npm', '--prefix', 'ui', 'run', 'lint')),
        @('mcp-types',        @('npm', '--prefix', 'mcp-server', 'run', 'typecheck')),
        @('py-tests',         @('uv', 'run', 'pytest', 'tests/', '-x', '--tb=short', '-q')),
        @('ui-tests',         @('npm', '--prefix', 'ui', 'run', 'test', '--', '--reporter=json', "--outputFile=$vjson")),
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
    # A run must never report an earlier run's counts: start from no receipts and read each
    # count only when the stage that writes it ran in this run.
    Get-ChildItem -Path $rd -Filter 's29-win-*' -ErrorAction SilentlyContinue | Remove-Item -Force
    $failed = $false
    foreach ($s in $stages) {
        $code = Invoke-Stage $s[0] $s[1]
        if ($s[0] -eq 'source-audit') {
            # rg exit 1 means zero hits (clean); 0 means hits; 2+ means an IO error.
            $clean = ($code -eq 1)
            $result.stages[-1].exit = $(if ($clean) { 0 } else { 1 })
            $result.stages[-1].note = "rg exit $code (1 = no hits)"
            if (-not $clean) { $failed = $true; break }
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
    $result.finished = (Get-Date).ToString('o')
    $result | ConvertTo-Json -Depth 6 | Set-Content -Path $out -Encoding utf8
    Get-Content $out
    if ($failed) { Write-Error 'WINDOWS_GATE failed; see the receipts named in the JSON'; exit 1 }
    'PASS WINDOWS_GATE'
    exit 0
}

throw "Unknown check: $Check"
