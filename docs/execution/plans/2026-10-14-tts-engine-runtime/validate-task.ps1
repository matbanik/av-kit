# Validation runner for 2026-10-14-tts-engine-runtime (Session 32). It is the only runner: the driver OS is the
# target OS (implementation-plan.md §Harness), so there is no validate-task.sh. Run from the worktree root:
#   pwsh -NoProfile -File docs/execution/plans/2026-10-14-tts-engine-runtime/validate-task.ps1 -Check <id> [-Arg <value>]
# Every tool runs through `rtk proxy` with its raw receipt at C:/Temp/av-kit/s32-<id>*.txt (AGENTS §RTK).
# The parsers live in gate_lib.py. This file and gate_lib.py are in GATED_PATHS, so editing either reopens the gate.
# Adapted from Session 31's windows-gate runner (stage list, durations, preflight) and Session 30's
# validate-task.sh (Red/Green parsers, census, scope fences).
param(
    [Parameter(Mandatory = $true)][string]$Check,
    [string[]]$Arg = @()
)
$ErrorActionPreference = 'Stop'
# Native exit codes are read explicitly from $LASTEXITCODE; never let pwsh 7.4+ turn them into throws.
$PSNativeCommandUseErrorActionPreference = $false
$root = (git rev-parse --show-toplevel).Trim()
Set-Location $root
$rd = 'C:/Temp/av-kit'
New-Item -ItemType Directory -Force -Path $rd | Out-Null
$plan = 'docs/execution/plans/2026-10-14-tts-engine-runtime'
$lib = "$plan/gate_lib.py"
$planMd = "$plan/implementation-plan.md"
$taskMd = "$plan/task.md"
$baseSha = "$plan/baseline.sha"
$handoffs = '.agent/context/handoffs'
$env:PYTHONIOENCODING = 'utf-8'
Remove-Item Env:ELECTRON_RUN_AS_NODE -ErrorAction SilentlyContinue
Remove-Item Env:AVKIT_E2E_OUT_DIR -ErrorAction SilentlyContinue

# GATED_PATHS (implementation-plan.md §Single-statement contracts); plan_checks.py static asserts equality.
$gated = @('ui', 'packages', 'mcp-server', 'tests', 'tools', 'packaging', 'pyproject.toml', 'uv.lock',
    'openapi.committed.json', 'docs/build-plan', 'docs/proposals', '.agent/docs', '.agent/schemas', '.agent/roles',
    '.agent/templates', '.agent/skills', '.agent/workflows', '.agent/model-registry.local.json',
    '.agent/model-registry.local.yaml', 'docs/execution/plans/2026-10-14-tts-engine-runtime/validate-task.ps1',
    'docs/execution/plans/2026-10-14-tts-engine-runtime/gate_lib.py')
$productPaths = @('ui', 'packages', 'mcp-server', 'tests', 'tools', 'packaging', 'openapi.committed.json', 'uv.lock', 'pyproject.toml')

# Symbols a Red run may fail to import or call because the Green row creates them (Evidence-First rule 2).
$PY_SYMBOLS = @{
    '73' = 'VOICE_PACKS,tts_voice_packs,fetch_voice_pack,voice_packs,ONNX_REPO,ONNX_REVISION,ONNX_LOCAL_DIR,LEGACY_ONNX_DIR,is_legacy_onnx_path,variant_local_path'
    '74' = 'VoiceUnavailableReason,EspeakStatus,voice_availability,EspeakPort,EspeakCliAdapter,avkit_infra.tts.espeak,tts_espeak,MULTI_E2M,EN_E2M,ESPEAK_EN_FALLBACK,ESPEAK_VOICE'
    '72' = 'KokoroG2p,split_phonemes,avkit_infra.tts.g2p'
}
$TS_SYMBOLS = @{ '73' = 'useRefreshDependenciesOnSettle'; '74' = '' }
$PY73 = @('tests/unit/test_tts_voice_packs_service.py', 'tests/integration/test_tts_voice_packs.py',
    'tests/e2e/test_api_tts_runtime.py', 'tests/integration/test_tts_models.py', 'tests/integration/test_tts_assets.py')
$REG73 = @('tests/e2e/test_api_health_settings.py', 'tests/e2e/test_api_auth.py', 'tests/e2e/test_api_tts_models.py',
    'tests/e2e/test_api_openapi.py')
$UI73 = @('tests/unit/settings-tts-runtime.test.ts', 'tests/unit/settings-page.test.ts')
$MCP73 = @('tests/models-assets.test.ts', 'tests/tools-parity.test.ts')
$PY74 = @('tests/unit/test_tts_voice_availability.py', 'tests/unit/test_espeak_adapter.py',
    'tests/e2e/test_api_tts_runtime.py', 'tests/unit/test_tts_voice_fixture.py')
$UI74 = @('tests/unit/voice-combobox.test.tsx', 'tests/unit/settings-tts-runtime.test.ts', 'tests/unit/settings-page.test.ts')
$E2E74 = @('tests/e2e/tts-generate.test.ts')
$PY72 = @('tests/integration/test_tts_no_torch.py', 'tests/unit/test_tts_g2p.py', 'tests/integration/test_tts_models.py',
    'tests/integration/test_tts_assets.py', 'tests/unit/test_packaging_backend.py', 'tests/unit/test_packaging_installer.py')
$DOC_SUITES = @('tests/unit/layout-canon.test.ts', 'tests/unit/gui-actions-audit.test.ts')

function Fail([string]$Msg) { Write-Host "FAIL: $Msg"; exit 1 }

function Invoke-Run([string]$Id, [string[]]$Argv) {
    $receipt = "$rd/s32-$Id.txt"
    & rtk proxy @Argv *> $receipt
    $code = $LASTEXITCODE
    Get-Content $receipt -Tail 25 | Write-Host
    return $code
}

function Assert-Run([string]$Id, [string[]]$Argv) {
    $code = Invoke-Run $Id $Argv
    if ($code -ne 0) { Fail "$Id exited $code (receipt $rd/s32-$Id.txt)" }
}

function Invoke-Lib([string]$Id, [string[]]$LibArgs) {
    $receipt = "$rd/s32-$Id.txt"
    & rtk proxy uv run python $lib @LibArgs *> $receipt
    $code = $LASTEXITCODE
    Get-Content $receipt | Write-Host
    if ($code -ne 0) { Fail "gate_lib $($LibArgs[0]) exited $code (receipt $receipt)" }
}

function Get-WorktreeIdentity {
    # WORKTREE_IDENTITY: one implementation, gate_lib.py identity (byte-exact over git's own output).
    $lines = @(& rtk proxy uv run python $lib identity --paths @gated 2>$null)
    $id = $lines | Where-Object { $_ -match '^[0-9a-f]{64}$' } | Select-Object -Last 1
    if (-not $id) { Fail 'WORKTREE_IDENTITY could not be computed' }
    return $id
}

function Get-BaselineSha {
    if (-not (Test-Path $baseSha)) { Fail "$baseSha missing; run -Check baseline first (row 0)" }
    return (Get-Content $baseSha -Raw).Trim()
}

function Invoke-PyRed([string]$Meu, [string[]]$Files) {
    $xml = "$rd/s32-red-$Meu-pytest.xml"
    Remove-Item $xml -ErrorAction SilentlyContinue
    $code = Invoke-Run "red-$Meu-pytest" (@('uv', 'run', 'pytest') + $Files + @('-q', '--tb=short', '-p', 'no:cacheprovider', "--junitxml=$xml"))
    Invoke-Lib "red-$Meu-pytest-verdict" (@('pytest-red', '--meu', $Meu, '--junit', $xml, '--symbols', $PY_SYMBOLS[$Meu],
            '--plan', $planMd, '--rc', "$code", '--files') + $Files)
}

function Invoke-VitestRed([string]$Meu, [string]$Pkg, [string[]]$Files) {
    $json = "$rd/s32-red-$Meu-$Pkg-vitest.json"
    Remove-Item $json -ErrorAction SilentlyContinue
    $code = Invoke-Run "red-$Meu-$Pkg-vitest" (@('npm', '--prefix', $Pkg, 'run', 'test', '--') + $Files + @('--reporter=json', "--outputFile=$json"))
    Invoke-Lib "red-$Meu-$Pkg-vitest-verdict" (@('vitest-red', '--meu', $Meu, '--pkg', $Pkg, '--json', $json, '--plan', $planMd,
            "--symbols=$($TS_SYMBOLS[$Meu])", '--rc', "$code", '--files') + $Files)
}

function Invoke-PyOk([string]$Id, [string[]]$Files) {
    $code = Invoke-Run $Id (@('uv', 'run', 'pytest') + $Files + @('-q', '--tb=short', '-p', 'no:cacheprovider', '-rfE'))
    Invoke-Lib "$Id-verdict" @('pytest-ok', '--receipt', "$rd/s32-$Id.txt", '--baseline', "$rd/s32-baseline-pytest.txt", '--rc', "$code")
}

function Invoke-VitestOk([string]$Id, [string]$Pkg, [string[]]$Files, [string]$Baseline) {
    $json = "$rd/s32-$Id.json"
    Remove-Item $json -ErrorAction SilentlyContinue
    $code = Invoke-Run $Id (@('npm', '--prefix', $Pkg, 'run', 'test', '--') + $Files + @('--reporter=json', "--outputFile=$json"))
    Invoke-Lib "$Id-verdict" @('vitest-ok', '--json', $json, '--rc', "$code", "--baseline=$Baseline")
}

function Invoke-UiBuilds([string]$Prefix) {
    Assert-Run "$Prefix-ui-build" @('npm', '--prefix', 'ui', 'run', 'build')
    Assert-Run "$Prefix-ui-harness-build" @('pwsh', '-NoProfile', '-Command',
        "`$env:AVKIT_PRIMITIVE_HARNESS_BUILD='1'; npm --prefix ui run build -- --outDir '$((Resolve-Path ui).Path)/out-e2e'; exit `$LASTEXITCODE")
}

function Invoke-ElectronOk([string]$Id, [string[]]$Extra) {
    $json = "$rd/s32-$Id.json"
    Remove-Item $json -ErrorAction SilentlyContinue
    $code = Invoke-Run $Id (@('npm', '--prefix', 'ui', 'run', 'test:e2e', '--') + $Extra + @('--reporter=json', "--outputFile=$json"))
    Invoke-Lib "$Id-verdict" @('electron-ok', '--json', $json, '--rc', "$code", '--baseline', "$rd/s32-baseline-e2e.json")
}

function Invoke-OpenApiTwoStep([string]$Prefix) {
    # G8: --check first; regenerate only on drift, then --check again.
    $code = Invoke-Run "$Prefix-openapi-check" @('uv', 'run', 'python', 'tools/export_openapi.py', '--check', 'openapi.committed.json')
    if ($code -ne 0) {
        Assert-Run "$Prefix-openapi-write" @('uv', 'run', 'python', 'tools/export_openapi.py', '-o', 'openapi.committed.json')
        Assert-Run "$Prefix-openapi-recheck" @('uv', 'run', 'python', 'tools/export_openapi.py', '--check', 'openapi.committed.json')
    }
}

function Invoke-StaticSet([string]$Prefix, [string[]]$LintExtra) {
    Assert-Run "$Prefix-py-types" @('uv', 'run', 'pyright', 'packages/')
    Assert-Run "$Prefix-py-lint" (@('uv', 'run', 'ruff', 'check', 'packages/', 'tests/') + $LintExtra)
    Assert-Run "$Prefix-ui-types" @('npm', '--prefix', 'ui', 'run', 'typecheck')
    Assert-Run "$Prefix-ui-lint" @('npm', '--prefix', 'ui', 'run', 'lint')
    Assert-Run "$Prefix-mcp-types" @('npm', '--prefix', 'mcp-server', 'run', 'typecheck')
}

function Invoke-TaCheck([string]$Id) {
    Invoke-Lib $Id @('ta-check', '--baseline-sha', $baseSha, '--plan', $planMd)
}

function Unique([string[]]$Items) { return @($Items | Select-Object -Unique) }

switch ($Check) {
    'prereq' {
        $branch = (git branch --show-current).Trim()
        if ($branch -ne 'claude/s32-tts-engine-runtime') { Fail "branch $branch (want claude/s32-tts-engine-runtime)" }
        # Stop condition S1 fired after row 0 (walkthrough §Execution amendments): the branch now sits on c72fc44,
        # which carries Session 31, and COUNT_FLOORS were re-derived. A later Session 31 commit on main is still stale.
        $s31 = (git log --oneline c72fc44..main -- docs/execution/plans/2026-10-10-gui-polish-residuals | Out-String).Trim()
        if ($s31) { Fail "Stop condition S1: Session 31 changed on main after c72fc44:`n$s31" }
        foreach ($g in 'graphify-out', 'graphify-out-research') { if (Test-Path $g) { Fail "$g exists: re-run the Context Tool Decision" } }
        $wt = "$plan/walkthrough.md"
        if (-not (Test-Path $wt)) { Fail "$wt missing: record the execution authorization first" }
        $auth = ((Get-Content $wt -Raw) -split '(?m)^## ')
        $sect = $auth | Where-Object { $_ -like 'Execution authorization*' } | Select-Object -First 1
        if (-not $sect -or $sect -notmatch 'USER_EXPLICIT') { Fail 'walkthrough.md §Execution authorization does not record USER_EXPLICIT' }
        Invoke-Lib 'prereq-plan-review' @('review-check', '--file', "$handoffs/2026-10-14-tts-engine-runtime-plan-critical-review.md", '--mode', 'plan', '--cap', '3')
        Assert-Run 'prereq-uv-sync' @('uv', 'sync', '--all-packages', '--frozen')
        Assert-Run 'prereq-npm-ci' @('pwsh', '-NoProfile', '-Command', "npm --prefix ui ci; if (`$LASTEXITCODE -ne 0) { exit `$LASTEXITCODE }; node ui/node_modules/electron/install.js; if (`$LASTEXITCODE -ne 0) { exit `$LASTEXITCODE }; if (-not (Test-Path ui/node_modules/electron/path.txt)) { exit 3 }; exit 0")
        Assert-Run 'prereq-mcp-npm-ci' @('npm', '--prefix', 'mcp-server', 'ci')
        Assert-Run 'prereq-electron' @('ui/node_modules/electron/dist/electron.exe', '--version')
        Invoke-Lib 'prereq-meu-state' @('meu-state', '--want', 'MEU-73=pending', 'MEU-74=pending', 'MEU-72=pending',
            'MEU-24=approved', 'MEU-62=approved', 'MEU-64=approved')
        'PASS prereq'
    }
    'baseline' {
        $dirty = (git status --porcelain -- @productPaths | Out-String).Trim()
        if ($dirty) { Fail "product paths are not clean at baseline:`n$dirty" }
        (git rev-parse HEAD).Trim() | Set-Content -Path $baseSha -Encoding ascii -NoNewline
        # Baseline failures are recorded, never fixed here; every later Green check tolerates exactly these.
        $code = Invoke-Run 'baseline-pytest' @('uv', 'run', 'pytest', 'tests/', '-q', '--tb=short', '-p', 'no:cacheprovider', '-rfE')
        Invoke-Lib 'baseline-pytest-verdict' @('pytest-ok', '--receipt', "$rd/s32-baseline-pytest.txt", '--baseline', "$rd/s32-baseline-pytest.txt", '--rc', "$code")
        $vj = "$rd/s32-baseline-vitest.json"
        $code = Invoke-Run 'baseline-vitest' @('npm', '--prefix', 'ui', 'run', 'test', '--', '--reporter=json', "--outputFile=$vj")
        Invoke-Lib 'baseline-vitest-verdict' @('vitest-ok', '--json', $vj, '--rc', "$code", '--baseline', $vj)
        Assert-Run 'baseline-mcp-build' @('npm', '--prefix', 'mcp-server', 'run', 'build')
        $mj = "$rd/s32-baseline-mcp.json"
        $code = Invoke-Run 'baseline-mcp' @('npm', '--prefix', 'mcp-server', 'run', 'test', '--', '--reporter=json', "--outputFile=$mj")
        Invoke-Lib 'baseline-mcp-verdict' @('vitest-ok', '--json', $mj, '--rc', "$code", '--baseline', $mj)
        Invoke-UiBuilds 'baseline'
        $ej = "$rd/s32-baseline-e2e.json"
        $code = Invoke-Run 'baseline-e2e' @('npm', '--prefix', 'ui', 'run', 'test:e2e', '--', '--reporter=json', "--outputFile=$ej")
        Invoke-Lib 'baseline-e2e-verdict' @('electron-ok', '--json', $ej, '--rc', "$code", '--baseline', $ej)
        "PASS baseline @ $(Get-Content $baseSha -Raw)"
    }
    'census' {
        $patterns = @('FakeKPipeline', 'KPipeline', 'Kokoro-82M-ONNX', 'HF_FILE_MAP', 'tts_onnx_vocab', 'tts_spacy_model',
            'TtsAsset', 'DependencyHealth', 'TTS_ASSET_WIRES', 'required_tts_assets', 'activate_spacy_dir', 'sys.path',
            'VoiceOut', 'list_voices', 'tts-voices.json', 'load_single_voice', '_chunk_part', 'MAX_ONNX_INPUT_IDS',
            'voices/', '.pt', 'tts-asset-row', 'VoiceCombobox', 'aria-disabled', '/tts/voices', 'health/dependencies',
            'avkit-backend.spec', 'excludes', 'hiddenimports', 'extraResources', 'lang_code', 'espeak', 'phonemizer', 'misaki')
        $argv = @('rg', '-n', '-F') + ($patterns | ForEach-Object { @('-e', $_) }) + @('tests', 'ui/tests', 'mcp-server/tests')
        $code = Invoke-Run 'census' $argv
        if ($code -gt 1) { Fail "rg exited $code" }
        "PASS census: $((Get-Content "$rd/s32-census.txt").Count) hits in $rd/s32-census.txt; disposition each in walkthrough.md §Census"
    }
    'red-73' {
        Get-BaselineSha | Out-Null
        Invoke-PyRed '73' $PY73
        Invoke-VitestRed '73' 'ui' $UI73
        Invoke-VitestRed '73' 'mcp-server' @('tests/models-assets.test.ts')
        'PASS red-73'
    }
    'green-73' {
        Invoke-PyOk 'green-73-pytest' (Unique ($PY73 + $REG73))
        Invoke-VitestOk 'green-73-ui' 'ui' $UI73 ''
        Assert-Run 'green-73-mcp-build' @('npm', '--prefix', 'mcp-server', 'run', 'build')
        Invoke-VitestOk 'green-73-mcp' 'mcp-server' $MCP73 ''
        'PASS green-73'
    }
    'gate73' {
        Invoke-StaticSet 'gate73' @()
        Invoke-PyOk 'gate73-pytest' (Unique ($PY73 + $REG73))
        Invoke-VitestOk 'gate73-ui' 'ui' @() "$rd/s32-baseline-vitest.json"
        Assert-Run 'gate73-mcp-build' @('npm', '--prefix', 'mcp-server', 'run', 'build')
        Invoke-VitestOk 'gate73-mcp' 'mcp-server' @() "$rd/s32-baseline-mcp.json"
        Invoke-OpenApiTwoStep 'gate73'
        Invoke-TaCheck 'gate73-ta-check'
        'PASS gate73'
    }
    'red-74' {
        Get-BaselineSha | Out-Null
        Invoke-PyRed '74' $PY74
        Invoke-VitestRed '74' 'ui' $UI74
        Invoke-UiBuilds 'red-74'
        $json = "$rd/s32-red-74-e2e.json"
        Remove-Item $json -ErrorAction SilentlyContinue
        $code = Invoke-Run 'red-74-e2e' (@('npm', '--prefix', 'ui', 'run', 'test:e2e', '--') + $E2E74 + @('-g', 'AC-74.9', '--reporter=json', "--outputFile=$json"))
        Invoke-Lib 'red-74-e2e-verdict' @('electron-red', '--tag', 'AC-74.9', '--json', $json, '--rc', "$code")
        'PASS red-74'
    }
    'green-74' {
        Invoke-PyOk 'green-74-pytest' (Unique ($PY74 + $PY73 + $REG73))
        'PASS green-74'
    }
    'green-74-ui' {
        Invoke-VitestOk 'green-74-ui' 'ui' $UI74 ''
        Invoke-UiBuilds 'green-74'
        Invoke-ElectronOk 'green-74-e2e' $E2E74
        'PASS green-74-ui'
    }
    'gate74' {
        Invoke-StaticSet 'gate74' @()
        Invoke-PyOk 'gate74-pytest' (Unique ($PY74 + $PY73 + $REG73))
        Invoke-VitestOk 'gate74-ui' 'ui' @() "$rd/s32-baseline-vitest.json"
        Assert-Run 'gate74-mcp-build' @('npm', '--prefix', 'mcp-server', 'run', 'build')
        Invoke-VitestOk 'gate74-mcp' 'mcp-server' @() "$rd/s32-baseline-mcp.json"
        Invoke-UiBuilds 'gate74'
        Invoke-ElectronOk 'gate74-e2e' $E2E74
        # The new spec must be stable, not only green once (Session 30 electron_repeat).
        Invoke-ElectronOk 'gate74-e2e-repeat' ($E2E74 + @('-g', 'AC-74.9', '--repeat-each=20'))
        Invoke-OpenApiTwoStep 'gate74'
        Invoke-TaCheck 'gate74-ta-check'
        'PASS gate74'
    }
    'red-72' {
        Get-BaselineSha | Out-Null
        Invoke-PyRed '72' $PY72
        'PASS red-72'
    }
    'green-72' {
        Invoke-PyOk 'green-72-pytest' (Unique ($PY72 + $PY74 + $PY73 + $REG73))
        'PASS green-72'
    }
    'gate72' {
        Invoke-StaticSet 'gate72' @('tools/smoke_packaged_tts.py')
        Assert-Run 'gate72-uv-lock' @('uv', 'lock', '--check')
        Invoke-PyOk 'gate72-pytest' (Unique ($PY72 + $PY74 + $PY73 + $REG73))
        Invoke-VitestOk 'gate72-ui' 'ui' @() "$rd/s32-baseline-vitest.json"
        Invoke-OpenApiTwoStep 'gate72'
        Invoke-TaCheck 'gate72-ta-check'
        'PASS gate72'
    }
    'hub' {
        Invoke-Lib 'hub-verdict' @('hub')
        Assert-Run 'hub-render-check' @('uv', 'run', 'python', 'tools/meu_status.py', 'render', '--check')
        Invoke-VitestOk 'hub-doc-suites' 'ui' $DOC_SUITES ''
        'PASS hub'
    }
    'plan-static' {
        Assert-Run 'plan-static' @('uv', 'run', 'python', "$plan/plan_checks.py", 'static')
        Assert-Run 'plan-selftest' @('uv', 'run', 'python', "$plan/plan_checks.py", 'selftest')
        $env:RECEIPTS_DIR = $rd
        Assert-Run 'plan-lint-task' @('uv', 'run', 'python', 'tools/lint_task_contract.py', '--allowed-builder-classes',
            'avkit_builder,avkit_coordinator,avkit_verifier', '--task', $taskMd)
        'PASS plan-static'
    }
    'task-state' {
        Invoke-Lib 'task-state-verdict' @('task-state', '--task', $taskMd, '--rows', '0-13')
    }
    'ssot-review' {
        Invoke-Lib 'ssot-review-verdict' @('ssot', '--stage', 'review')
        Assert-Run 'ssot-review-render' @('uv', 'run', 'python', 'tools/meu_status.py', 'render', '--check')
        'PASS ssot-review'
    }
    'api-scope' {
        Get-BaselineSha | Out-Null
        Invoke-Lib 'api-scope-verdict' @('api-scope', '--baseline-sha', $baseSha, '--plan', $planMd)
        Assert-Run 'api-scope-openapi' @('uv', 'run', 'python', 'tools/export_openapi.py', '--check', 'openapi.committed.json')
        Invoke-TaCheck 'api-scope-ta-check'
        'PASS api-scope'
    }
    'ta-check' {
        Invoke-TaCheck 'ta-check'
    }
    'handoff-ac' {
        foreach ($m in 'MEU-73', 'MEU-74', 'MEU-72') {
            Assert-Run "handoff-ac-$m" @('uv', 'run', 'python', 'tools/validate_closeout_artifacts.py', '--plan', $planMd,
                '--handoff', "$handoffs/2026-10-14-tts-engine-runtime-$m-handoff.md", '--ac-coverage-only')
        }
        'PASS handoff-ac'
    }
    'windows-gate' {
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
            schema              = 's32-windows-gate.v1'
            identity            = (Get-WorktreeIdentity)
            head                = (git rev-parse HEAD).Trim()
            lockfile_sha256     = (Get-FileHash ui/package-lock.json -Algorithm SHA256).Hash
            mcp_lockfile_sha256 = (Get-FileHash mcp-server/package-lock.json -Algorithm SHA256).Hash
            uv_lock_sha256      = (Get-FileHash uv.lock -Algorithm SHA256).Hash
            electron            = ((npm --prefix ui ls electron --depth=0 2>$null) | Select-String 'electron@' | Out-String).Trim()
            node                = (node --version).Trim()
            preflight           = [ordered]@{ agentic_framework_head = $afHead; agent_registry_sha256 = $regHash; drift = $drift }
            started             = (Get-Date).ToString('o')
            stages              = @()
            pytest              = $null
            vitest              = $null
            e2e                 = $null
        }
        if ($drift) {
            $result.finished = (Get-Date).ToString('o')
            $result | ConvertTo-Json -Depth 6 | Set-Content -Path $out -Encoding utf8
            Fail 'PREFLIGHT drift: P:/agentic-framework HEAD or P:/.agent registry changed since the previous attempt; report before stage 1'
        }

        function Invoke-Stage([string]$Id, [string[]]$Argv) {
            $receipt = "$rd/s32-win-$Id.txt"
            $clock = [System.Diagnostics.Stopwatch]::StartNew()
            & rtk proxy @Argv *> $receipt
            $code = $LASTEXITCODE
            $clock.Stop()
            $script:result.stages += [ordered]@{ id = $Id; argv = ($Argv -join ' '); exit = $code; seconds = [math]::Round($clock.Elapsed.TotalSeconds, 1); receipt = $receipt }
            Get-Content $receipt -Tail 15 | Write-Host
            return $code
        }

        # The production sources this plan creates or rewrites (Files Modified); none may carry these markers.
        $auditSrc = @(
            'packages/infrastructure/src/avkit_infra/tts/g2p.py', 'packages/infrastructure/src/avkit_infra/tts/espeak.py',
            'packages/infrastructure/src/avkit_infra/tts/adapter.py', 'packages/infrastructure/src/avkit_infra/tts/assets.py',
            'packages/infrastructure/src/avkit_infra/model_manager/voice_packs.py', 'tools/smoke_packaged_tts.py',
            'ui/src/renderer/src/features/tts/VoiceCombobox.tsx', 'ui/src/renderer/src/features/tts/useTtsJob.ts',
            'ui/src/renderer/src/features/tts/tts-voices.ts', 'ui/src/renderer/src/features/tts/tts-assets.ts',
            'ui/src/renderer/src/features/settings/SettingsPage.tsx')
        $auditPattern = 'TODO|FIXME|transition-all|bg-\[#|console\.log\(|@ts-ignore|@ts-expect-error|: any\b|breakpoint\(\)|# type: ignore'
        $vjson = "$rd/s32-win-vitest.json"
        $ejson = "$rd/s32-win-e2e.json"
        $pytxt = "$rd/s32-win-py-tests.txt"
        $stages = @(
            # Session 27 A-5: Electron 42 has no postinstall; install its binary serially so Vitest workers never race it.
            @('npm-ci',           @('pwsh', '-NoProfile', '-Command', "npm --prefix ui ci; if (`$LASTEXITCODE -ne 0) { exit `$LASTEXITCODE }; node ui/node_modules/electron/install.js; if (`$LASTEXITCODE -ne 0) { exit `$LASTEXITCODE }; if (-not (Test-Path ui/node_modules/electron/path.txt)) { exit 3 }; exit 0")),
            @('mcp-npm-ci',       @('npm', '--prefix', 'mcp-server', 'ci')),
            @('py-types',         @('uv', 'run', 'pyright', 'packages/')),
            @('py-lint',          @('uv', 'run', 'ruff', 'check', 'packages/', 'tests/', 'tools/smoke_packaged_tts.py')),
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
        # A run must never report an earlier run's counts: start from no receipts.
        Get-ChildItem -Path $rd -Filter 's32-win-*' -ErrorAction SilentlyContinue | Remove-Item -Force
        $failed = $false
        foreach ($s in $stages) {
            $code = Invoke-Stage $s[0] $s[1]
            if ($s[0] -eq 'source-audit') {
                # rg exit 1 means zero hits (clean); 0 means hits; 2+ means an IO error (a missing file is one).
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
        # A tree edited while the gate ran is not the tree the gate tested.
        $result.identity_end = (Get-WorktreeIdentity)
        if ($result.identity_end -ne $result.identity) { Write-Host 'FAIL: WORKTREE_IDENTITY changed during the gate'; $failed = $true }
        $result.finished = (Get-Date).ToString('o')
        $result | ConvertTo-Json -Depth 6 | Set-Content -Path $out -Encoding utf8
        Get-Content $out
        if ($failed) { Fail 'WINDOWS_GATE failed; see the receipts named in the JSON' }
        'PASS WINDOWS_GATE'
    }
    'package-smoke' {
        # PACKAGE_SMOKE = ONLINE_PROVISION -> INSTALLER_STAGE -> OFFLINE_SMOKE (implementation-plan.md contracts).
        $out = Join-Path $plan 'package-smoke-result.json'
        $online = "$rd/s32-smoke-online.json"
        $offline = "$rd/s32-smoke-offline.json"
        $probe = "$rd/s32-mcp-probe.json"
        $runDir = 'C:/Temp/av-kit/s32-smoke-run'
        $models = 'C:/Temp/av-kit/s32-smoke-models'
        Remove-Item $online, $offline, $probe -ErrorAction SilentlyContinue
        $result = [ordered]@{
            schema    = 's32-package-smoke.v2'
            identity  = (Get-WorktreeIdentity)
            head      = (git rev-parse HEAD).Trim()
            started   = (Get-Date).ToString('o')
            online    = $null
            installer = $null
            offline   = $null
            mcp_probe = $null
        }
        function Save-Result { $script:result.finished = (Get-Date).ToString('o'); $script:result | ConvertTo-Json -Depth 6 | Set-Content -Path $out -Encoding utf8 }
        # (A) ONLINE_PROVISION: build without --stub-ok (the smoke refuses an exe under 1 MB), forbidden dirs, fill SMOKE_MODELS.
        $code = Invoke-Run 'package-smoke-online' @('uv', 'run', 'python', 'tools/smoke_packaged_tts.py', '--phase', 'online',
            '--models-dir', $models, '--out', $online)
        if (Test-Path $online) { $result.online = Get-Content $online -Raw | ConvertFrom-Json }
        if ($code -ne 0) { Save-Result; Fail "ONLINE_PROVISION exited $code (receipt $rd/s32-package-smoke-online.txt)" }
        # (B) INSTALLER_STAGE. The fetch runs when any FFmpeg file or its LICENSE.txt is missing (D-87).
        $ff = 'packaging/ffmpeg-win64'
        if (@('ffmpeg.exe', 'ffprobe.exe', 'LICENSE.txt' | Where-Object { -not (Test-Path (Join-Path $ff $_)) }).Count -gt 0) {
            Assert-Run 'package-smoke-ffmpeg' @('pwsh', '-NoProfile', '-File', 'tools/fetch_ffmpeg_windows.ps1')
        }
        Assert-Run 'package-smoke-mcp-build' @('npm', '--prefix', 'mcp-server', 'run', 'build')
        $buildReceipt = "$rd/s32-package-smoke-dist.txt"
        $distCode = Invoke-Run 'package-smoke-dist' @('npm', '--prefix', 'ui', 'run', 'dist')
        $nsisCode = $null
        if ($distCode -eq 0) {
            $nsisCode = Invoke-Run 'package-smoke-nsis' @('pwsh', '-NoProfile', '-File',
                'docs/execution/plans/2026-08-24-p7-distribution/assert-nsis-pack.ps1', '-BuildReceipt', $buildReceipt)
        }
        $res = 'ui/dist/win-unpacked/resources'
        $notices = Join-Path $res 'THIRD_PARTY_NOTICES.md'
        $noticesStaged = (Test-Path $notices) -and ((Get-Content $notices -Raw) -match 'FFmpeg') -and ((Get-Content $notices -Raw) -match 'GPL-3\.0')
        $lic = Join-Path $res 'ffmpeg/LICENSE.txt'
        $licStaged = (Test-Path $lic) -and ((Get-Item $lic).Length -gt 0)
        $result.installer = [ordered]@{ dist_exit = $distCode; nsis_assert_exit = $nsisCode; build_receipt = $buildReceipt
            notices_staged = $noticesStaged; ffmpeg_license_staged = $licStaged }
        if ($distCode -ne 0 -or $nsisCode -ne 0) { Save-Result; Fail "INSTALLER_STAGE dist $distCode nsis $nsisCode (Stop condition S6 if over the size cap)" }
        if (-not $noticesStaged -or -not $licStaged) { Save-Result; Fail "INSTALLER_STAGE notices_staged $noticesStaged ffmpeg_license_staged $licStaged" }
        # MCP_ENTRY_PROBE: recorded, not a pass condition.
        Invoke-Lib 'package-smoke-mcp-probe' @('mcp-probe', '--entry', "$res/mcp-server/index.js", '--out', $probe)
        $result.mcp_probe = Get-Content $probe -Raw | ConvertFrom-Json
        # (C) OFFLINE_SMOKE: the installer's own backend copy, outside the checkout, fresh process, proxies dead (D-88).
        Remove-Item $runDir -Recurse -Force -ErrorAction SilentlyContinue
        New-Item -ItemType Directory -Force -Path $runDir | Out-Null
        Copy-Item -Recurse -LiteralPath "$res/avkit-backend" -Destination "$runDir/avkit-backend"
        $code = Invoke-Run 'package-smoke-offline' @('uv', 'run', 'python', 'tools/smoke_packaged_tts.py', '--phase', 'offline',
            '--backend-dir', "$runDir/avkit-backend", '--models-dir', $models, '--out', $offline)
        if (Test-Path $offline) { $result.offline = Get-Content $offline -Raw | ConvertFrom-Json }
        $result.identity_end = (Get-WorktreeIdentity)
        Save-Result
        Get-Content $out
        if ($code -ne 0) { Fail "OFFLINE_SMOKE exited $code (receipt $rd/s32-package-smoke-offline.txt)" }
        if ($result.identity_end -ne $result.identity) { Fail 'WORKTREE_IDENTITY changed during package-smoke' }
        "PASS PACKAGE_SMOKE: ONLINE_PROVISION + INSTALLER_STAGE + OFFLINE_SMOKE (MCP probe: $($result.mcp_probe.result))"
    }
    'windows-gate-check' {
        # COUNT_FLOORS literals (S1 amendment); plan_checks.py static asserts they equal the plan's 800 / 137 / 655.
        Invoke-Lib 'windows-gate-check-verdict' (@('gate-check', '--floor-vitest', '800', '--floor-e2e', '137', '--floor-pytest', '655', '--gated') + $gated)
    }
    'review-check' {
        $mode = $(if ($Arg.Count -gt 0) { $Arg[0] } else { 'implementation' })
        $cap = $(if ($mode -eq 'plan') { '3' } else { '6' })
        Invoke-Lib "review-check-$mode" @('review-check', '--file', "$handoffs/2026-10-14-tts-engine-runtime-$mode-critical-review.md",
            '--mode', $mode, '--cap', $cap)
    }
    'reflection' {
        $argv = @('uv', 'run', 'python', 'tools/validate_closeout_artifacts.py',
            '--reflection', 'docs/execution/reflections/2026-10-14-tts-engine-runtime-reflection.md',
            '--reflection-template', 'docs/execution/reflections/TEMPLATE.md', '--reflection-schema', '.agent/schemas/reflection.v1.yaml',
            '--decision-source', $planMd, '--decision-source', '.agent/context/grouping/2026-10-09-triage-residuals-session-grouping.md')
        # Execution-time decisions are appended to the plan's decision_log, so the plan and grouping are the full set.
        Assert-Run 'reflection' $argv
        'PASS reflection'
    }
    'post-review-state' {
        Invoke-Lib 'post-review-verdict' @('ssot', '--stage', 'post-review')
        Assert-Run 'post-review-render' @('uv', 'run', 'python', 'tools/meu_status.py', 'render', '--check')
        Assert-Run 'post-review-issues' @('uv', 'run', 'python', 'tools/issue_triage.py', 'render', '--check')
        # The SSOT edits are outside GATED_PATHS; re-run the suites that read them.
        Invoke-VitestOk 'post-review-doc-suites' 'ui' $DOC_SUITES ''
        'PASS post-review-state'
    }
    default { Fail "unknown check: $Check" }
}
exit 0
