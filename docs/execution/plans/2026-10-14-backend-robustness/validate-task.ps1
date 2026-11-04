# Validation checks for 2026-10-14-backend-robustness (Session 33). Driver-run, local (plan D-8).
# Run from the worktree root P:/av-kit-wt/backend-robustness, one check per task.md row:
#   pwsh -NoProfile -File docs/execution/plans/2026-10-14-backend-robustness/validate-task.ps1 -Check <name>
# Every tool runs through `rtk proxy` into C:/Temp/av-kit/s33-* receipts and reports; exec_checks.py
# (stdlib) reads them and decides. Nothing here commits, pushes or requires a clean tree: evidence is bound
# to the working tree by GATE_FINGERPRINT and AUDIT_FINGERPRINT (implementation-plan.md §Single-statement
# contracts). Adapted from Session 30 (audit) and Session 31 (windows-gate).
param(
    [Parameter(Mandatory = $true)][string]$Check,
    [string]$Target = '',
    [string]$Mode = '',
    [int]$Cap = 0
)
$ErrorActionPreference = 'Stop'
# Native exit codes are read explicitly from $LASTEXITCODE; never let pwsh 7.4+ turn them into throws.
$PSNativeCommandUseErrorActionPreference = $false
$rd = 'C:/Temp/av-kit'
New-Item -ItemType Directory -Force -Path $rd | Out-Null
$plan = 'docs/execution/plans/2026-10-14-backend-robustness'
$ec = "$plan/exec_checks.py"
# A-1 (2026-10-15): the base moved to c72fc44 (the Session 31 merge); Mat accepted it as the planning head.
$planningHead = 'c72fc4436da8534ef613264620b83c3e84e97631'
Remove-Item Env:ELECTRON_RUN_AS_NODE -ErrorAction SilentlyContinue
Remove-Item Env:AVKIT_E2E_OUT_DIR -ErrorAction SilentlyContinue
# An activated venv from another checkout (P:/av-kit/.venv) must not leak into `uv run`.
Remove-Item Env:VIRTUAL_ENV -ErrorAction SilentlyContinue
if (-not (Test-Path $ec) -or ((git rev-parse --show-toplevel).Trim() -ne ((Resolve-Path .).Path -replace '\\', '/'))) {
    Write-Error 'run from the worktree root'
    exit 1
}

# GATED_PATHS (the whole tree minus GATE_EXCLUDED) lives only in exec_checks.py; plan_checks.py static asserts it
# equals the plan. The fingerprint verbs apply it; this script holds no copy.

# Per-MEU test sets (the AC table's files) and the TEST_AMENDMENTS / FIXTURE_REPAIRS files each Green re-runs.
$PY76 = @('tests/e2e/test_api_error_surface.py', 'tests/unit/test_console_level.py', 'tests/integration/test_youtube_adapter.py')
$UI76 = @('tests/unit/api-fetch.test.ts')
$MCP76 = @('tests/audit/census-signature.test.ts')
$TA76 = @('tests/unit/test_domain.py')
$PY78 = @('tests/unit/test_ffmpeg_resolver.py', 'tests/integration/test_youtube_adapter.py', 'tests/integration/test_api_wiring.py', 'tests/e2e/test_api_ffmpeg_resolution.py')
$UI78 = @('tests/unit/settings-deps-refresh.test.ts')
$E2E78 = @('tests/e2e/settings.test.ts')
$TA78 = @('tests/unit/test_domain.py', 'tests/integration/test_filesystem_media.py')
$PY77 = @('tests/unit/test_tts_async.py', 'tests/integration/test_tts_assets.py')
$MCP77 = @('tests/tts.test.ts', 'tests/audit/tts-cancel-step.test.ts')
$E2E77 = @('tests/e2e/tts-generate.test.ts')
$TA77 = @('tests/unit/test_domain.py', 'tests/integration/test_sqlite_uow.py', 'tests/unit/test_services.py')

# Source audit (G32/G33 and code-quality bans) per MEU: the MEU's product Files Modified rows.
# plan_checks.py static asserts each list equals exec_checks.product_files() for that MEU.
$SRC76 = @('mcp-server/scripts/audit/census.ts', 'packages/api/src/avkit_api/errors.py', 'packages/api/src/avkit_api/main.py',
    'packages/core/src/avkit_core/domain/errors.py', 'packages/core/src/avkit_core/services/health.py',
    'packages/infrastructure/src/avkit_infra/youtube/adapter.py', 'ui/src/renderer/src/lib/api.ts')
$SRC78 = @('packages/api/src/avkit_api/routes/health.py', 'packages/api/src/avkit_api/schemas/health.py', 'packages/api/src/avkit_api/wiring.py',
    'packages/core/src/avkit_core/domain/conversion.py', 'packages/core/src/avkit_core/domain/health.py', 'packages/core/src/avkit_core/ports/media.py',
    'packages/core/src/avkit_core/services/health.py', 'packages/infrastructure/src/avkit_infra/media/adapter.py',
    'packages/infrastructure/src/avkit_infra/youtube/adapter.py', 'ui/src/renderer/src/features/settings/SettingsPage.tsx',
    'ui/src/renderer/src/features/settings/useSettingsPage.ts')
$SRC77 = @('mcp-server/scripts/audit/fixtures.ts', 'mcp-server/scripts/audit/plan.ts', 'mcp-server/src/index.ts', 'mcp-server/src/toolsets/tts.ts',
    'packages/api/src/avkit_api/main.py', 'packages/api/src/avkit_api/routes/tts.py', 'packages/api/src/avkit_api/wiring.py',
    'packages/core/src/avkit_core/ports/storage.py', 'packages/core/src/avkit_core/services/tts.py',
    'packages/infrastructure/src/avkit_infra/database/repositories.py', 'packages/infrastructure/src/avkit_infra/tts/adapter.py')
$auditPattern = 'TODO|FIXME|transition-all|bg-\[#|console\.log\(|@ts-ignore|@ts-expect-error|: any\b'

function Run([string]$Id, [string[]]$Argv) {
    # One tool call through rtk proxy into its own receipt; returns the exit code.
    $receipt = "$rd/s33-$Id.txt"
    & rtk proxy @Argv *> $receipt
    $code = $LASTEXITCODE
    Write-Host "[$Id] exit $code -> $receipt"
    Get-Content $receipt -Tail 12 | Write-Host
    return $code
}

function Ev([string]$Id, [string[]]$Argv) {
    # exec_checks.py verdict (PASS ... / FAIL: ...); returns its exit code.
    return (Run $Id (@('uv', 'run', 'python', $ec) + $Argv))
}

function Fresh([string]$Path) {
    # A check never reads an earlier run's report.
    Remove-Item $Path -Force -ErrorAction SilentlyContinue
    return $Path
}

function Tier([string]$Kind, [string]$Tier, [string]$Meu, [string]$Id, [string[]]$Files, [string]$Grep = '', [string[]]$Extra = @()) {
    # Run one tier's files and evaluate it: red|green (with --meu) or suite. Returns 0 on PASS.
    switch ($Tier) {
        'pytest' {
            $report = Fresh "$rd/s33-$Id.xml"
            $code = Run $Id (@('uv', 'run', 'pytest') + $Files + $Extra + @('-q', '--tb=short', '-p', 'no:cacheprovider', "--junitxml=$report"))
        }
        'vitest' {
            $report = Fresh "$rd/s33-$Id.json"
            $code = Run $Id (@('npm', '--prefix', 'ui', 'run', 'test', '--') + $Files + @('--reporter=json', "--outputFile=$report"))
        }
        'mcp' {
            # The MCP suite asserts the built dist (AC-32.8), so every MCP run builds first.
            if ((Run "$Id-build" @('npm', '--prefix', 'mcp-server', 'run', 'build')) -ne 0) { return 1 }
            $report = Fresh "$rd/s33-$Id.json"
            $code = Run $Id (@('npm', '--prefix', 'mcp-server', 'run', 'test', '--') + $Files + @('--reporter=json', "--outputFile=$report"))
        }
        'electron' {
            # Electron specs run the built renderer: rebuild after every renderer edit (reflection 2026-09-20 KEEP).
            if ((Run "$Id-build" @('npm', '--prefix', 'ui', 'run', 'build')) -ne 0) { return 1 }
            $report = Fresh "$rd/s33-$Id.json"
            $grepArgs = $(if ($Grep -ne '') { @('-g', $Grep) } else { @() })
            $code = Run $Id (@('npm', '--prefix', 'ui', 'run', 'test:e2e', '--') + $Files + $grepArgs + $Extra + @('--reporter=json', "--outputFile=$report"))
        }
    }
    $meuArgs = $(if ($Meu -ne '') { @('--meu', $Meu) } else { @() })
    return (Ev "$Id-eval" (@($Kind, '--tier', $Tier) + $meuArgs + @('--report', $report, '--exit', "$code")))
}

function SourceAudit([string]$Id, [string[]]$Files) {
    # rg exit 1 means zero hits (clean); 0 means hits; 2+ means an IO error.
    $code = Run $Id (@('rg', '-n', '-e', $auditPattern) + $Files)
    if ($code -eq 1) { return 0 }
    Write-Host "FAIL source audit (rg exit $code)"
    return 1
}

function TargetedGate([string]$Meu, [string[]]$Src) {
    # PROFILE D6 targeted gate for one MEU; returns the number of failed stages.
    $bad = 0
    foreach ($s in @(
            @("gate$Meu-py-types", @('uv', 'run', 'pyright', 'packages/')),
            @("gate$Meu-py-lint", @('uv', 'run', 'ruff', 'check', 'packages/', 'tests/')),
            @("gate$Meu-ui-types", @('npm', '--prefix', 'ui', 'run', 'typecheck')),
            @("gate$Meu-ui-lint", @('npm', '--prefix', 'ui', 'run', 'lint')),
            @("gate$Meu-mcp-types", @('npm', '--prefix', 'mcp-server', 'run', 'typecheck')),
            @("gate$Meu-openapi", @('uv', 'run', 'python', 'tools/export_openapi.py', '--check', 'openapi.committed.json')))) {
        if ((Run $s[0] $s[1]) -ne 0) { $bad++ }
    }
    if ((Tier 'suite' 'pytest' '' "gate$Meu-pytest" @('tests/')) -ne 0) { $bad++ }
    if ((Tier 'suite' 'vitest' '' "gate$Meu-vitest" @()) -ne 0) { $bad++ }
    if ((Tier 'suite' 'mcp' '' "gate$Meu-mcp" @()) -ne 0) { $bad++ }
    if ((SourceAudit "gate$Meu-source-audit" $Src) -ne 0) { $bad++ }
    return $bad
}

function Finish([int]$Bad, [string]$Name) {
    if ($Bad -ne 0) { Write-Host "FAIL $Name ($Bad failed step(s); see the receipts above)"; exit 1 }
    Write-Host "PASS $Name"
    exit 0
}

if ($Check -eq 'prereq') {
    $bad = 0
    # Context-tool gate re-check (create-plan §5f): still not_applicable.
    foreach ($d in @('graphify-out', 'graphify-out-research')) { if (Test-Path $d) { Write-Host "FAIL: $d appeared; re-run the context-tool decision"; $bad++ } }
    # A-2 (2026-10-15): headroom on PATH needs a recorded execution-phase decision, not a refusal.
    if ((Get-Command headroom -ErrorAction SilentlyContinue) -and -not (Select-String -Path "$plan/task.md" -Pattern '^\s*phase: execution\s*$' -Quiet)) { Write-Host 'FAIL: headroom is on PATH and task.md records no execution-phase context-tool decision'; $bad++ }
    if ((Ev 'prereq-meu' @('meu-state', '--expect', 'pending')) -ne 0) { $bad++ }
    if ((Ev 'prereq-plan-review' @('review-check', '--target', '.agent/context/handoffs/2026-10-14-backend-robustness-plan-critical-review.md', '--mode', 'plan', '--cap', '6')) -ne 0) { $bad++ }  # A-3 (2026-10-15): cap 6 on Mat's instruction
    if ((Ev 'prereq-auth' @('prereq-auth')) -ne 0) { $bad++ }
    if (-not (Test-Path 'P:/agentic-framework/.git') -or -not (Test-Path 'P:/.agent/model-registry.json')) { Write-Host 'FAIL: P:/agentic-framework or P:/.agent/model-registry.json is not readable'; $bad++ }
    if ($bad -ne 0) { Finish $bad 'prereq' }
    # Installs (Session 27 A-5: Electron's binary is installed serially, then path.txt proves it).
    foreach ($s in @(
            @('prereq-uv-sync', @('uv', 'sync', '--frozen', '--all-packages')),
            @('prereq-ui-ci', @('npm', '--prefix', 'ui', 'ci')),
            @('prereq-electron', @('node', 'ui/node_modules/electron/install.js')),
            @('prereq-mcp-ci', @('npm', '--prefix', 'mcp-server', 'ci')))) {
        if ((Run $s[0] $s[1]) -ne 0) { Finish 1 'prereq' }
    }
    if (-not (Test-Path 'ui/node_modules/electron/path.txt')) { Write-Host 'FAIL: Electron binary not installed (path.txt)'; Finish 1 'prereq' }
    # baseline.sha is written once, at the first prereq run, and never moved.
    if (-not (Test-Path "$plan/baseline.sha")) { (git rev-parse HEAD).Trim() | Set-Content -Path "$plan/baseline.sha" -Encoding ascii }
    Write-Host "baseline.sha $(Get-Content "$plan/baseline.sha")"
    # S4 and D-10: nothing merged since planning touched a Files Modified path; record the P:/av-kit overlap.
    if ((Ev 'prereq-overlap' @('overlap', '--planning-head', $planningHead, '--out', "$rd/s33-overlap.txt")) -ne 0) { Finish 1 'prereq' }
    Get-Content "$rd/s33-overlap.txt" | Write-Host
    # COUNT_FLOORS: the MCP suite count before any edit (kept from the first measurement).
    if ((Run 'prereq-mcp-build' @('npm', '--prefix', 'mcp-server', 'run', 'build')) -ne 0) { Finish 1 'prereq' }
    $mj = Fresh "$rd/s33-prereq-mcp.json"
    $code = Run 'prereq-mcp' @('npm', '--prefix', 'mcp-server', 'run', 'test', '--', '--reporter=json', "--outputFile=$mj")
    if ((Ev 'prereq-counts' @('baseline-counts', '--report', $mj, '--exit', "$code")) -ne 0) { $bad++ }
    Finish $bad 'prereq'
}

if ($Check -eq 'census') {
    # Every pinned expectation this design changes (TEST_AMENDMENTS, FIXTURE_REPAIRS); row 1 dispositions each hit.
    $patterns = @('DOMAIN_ERROR_TYPE_NAMES', 'MEDIA_PORT_METHODS', 'TTS_REPO_METHODS', '_probed', 'configured_path',
        'is re-raised', 'pytest\.raises\(ValidationError\)', 'status_code == 500', '"Done"', 'MASKED_500',
        'generate is one job', 'tts_text', 'DependencyHealth\(', 'AppServices\(', 'list_by_status',
        'ffmpeg_binaries', 'CONSOLE_FIELDS', '_ffmpeg_path', 'internal_error')
    $argv = @('rg', '-n')
    foreach ($p in $patterns) { $argv += @('-e', $p) }
    $code = Run 'census' ($argv + @('tests', 'ui/tests', 'mcp-server/tests'))
    if ($code -gt 1) { Finish 1 'census' }
    Write-Host "census: $((Get-Content "$rd/s33-census.txt" | Measure-Object -Line).Lines) hit line(s) in $rd/s33-census.txt; disposition each in walkthrough.md §Census"
    Finish 0 'census'
}

if ($Check -eq 'red76') {
    if ((Ev 'red76-guard' @('red-guard', '--meu', '76')) -ne 0) { Finish 1 'red76' }
    $bad = 0
    if ((Tier 'red' 'pytest' '76' 'red76-py' $PY76) -ne 0) { $bad++ }
    if ((Tier 'red' 'vitest' '76' 'red76-ui' $UI76) -ne 0) { $bad++ }
    if ((Tier 'red' 'mcp' '76' 'red76-mcp' $MCP76) -ne 0) { $bad++ }
    Finish $bad 'red76 (RED_RULE)'
}

if ($Check -eq 'green76') {
    $bad = 0
    if ((Tier 'green' 'pytest' '76' 'green76-py' ($PY76 + $TA76)) -ne 0) { $bad++ }
    if ((Tier 'green' 'vitest' '76' 'green76-ui' $UI76) -ne 0) { $bad++ }
    if ((Tier 'green' 'mcp' '76' 'green76-mcp' $MCP76) -ne 0) { $bad++ }
    Finish $bad 'green76'
}

if ($Check -eq 'gate76') {
    $bad = TargetedGate '76' $SRC76
    if ($bad -eq 0 -and (Ev 'gate76-snapshot' @('snapshot', '--out', "$rd/s33-gate76-product.json")) -ne 0) { $bad++ }
    Finish $bad 'gate76'
}

if ($Check -eq 'red78') {
    if ((Ev 'red78-guard' @('red-guard', '--meu', '78', '--snapshot', "$rd/s33-gate76-product.json")) -ne 0) { Finish 1 'red78' }
    $bad = 0
    if ((Tier 'red' 'pytest' '78' 'red78-py' $PY78) -ne 0) { $bad++ }
    if ((Tier 'red' 'vitest' '78' 'red78-ui' $UI78) -ne 0) { $bad++ }
    if ((Tier 'red' 'electron' '78' 'red78-e2e' $E2E78 'AC-78.9') -ne 0) { $bad++ }
    Finish $bad 'red78 (RED_RULE)'
}

if ($Check -eq 'green78') {
    $bad = 0
    if ((Tier 'green' 'pytest' '78' 'green78-py' ($PY78 + $TA78)) -ne 0) { $bad++ }
    if ((Tier 'green' 'vitest' '78' 'green78-ui' $UI78) -ne 0) { $bad++ }
    if ((Tier 'green' 'electron' '78' 'green78-e2e' $E2E78 'AC-78.9') -ne 0) { $bad++ }
    if ((Run 'green78-openapi' @('uv', 'run', 'python', 'tools/export_openapi.py', '--check', 'openapi.committed.json')) -ne 0) { $bad++ }
    Finish $bad 'green78'
}

if ($Check -eq 'gate78') {
    $bad = TargetedGate '78' $SRC78
    if ((Tier 'suite' 'electron' '' 'gate78-e2e' $E2E78 '' @('--repeat-each=5')) -ne 0) { $bad++ }
    if ($bad -eq 0 -and (Ev 'gate78-snapshot' @('snapshot', '--out', "$rd/s33-gate78-product.json")) -ne 0) { $bad++ }
    Finish $bad 'gate78'
}

if ($Check -eq 'red77') {
    if ((Ev 'red77-guard' @('red-guard', '--meu', '77', '--snapshot', "$rd/s33-gate78-product.json")) -ne 0) { Finish 1 'red77' }
    $bad = 0
    if ((Tier 'red' 'pytest' '77' 'red77-py' $PY77) -ne 0) { $bad++ }
    if ((Tier 'red' 'mcp' '77' 'red77-mcp' $MCP77) -ne 0) { $bad++ }
    # AC-77.14 is a pin (RED_RULE item 5): it must pass in this run.
    if ((Tier 'red' 'electron' '77' 'red77-e2e' $E2E77 'AC-77.14') -ne 0) { $bad++ }
    Finish $bad 'red77 (RED_RULE)'
}

if ($Check -eq 'green77-svc') {
    $bad = 0
    if ((Tier 'green' 'pytest' '77' 'green77-svc-py' ($PY77 + $TA77)) -ne 0) { $bad++ }
    if ((Run 'green77-svc-openapi' @('uv', 'run', 'python', 'tools/export_openapi.py', '--check', 'openapi.committed.json')) -ne 0) { $bad++ }
    Finish $bad 'green77-svc'
}

if ($Check -eq 'green77') {
    $bad = 0
    if ((Tier 'green' 'mcp' '77' 'green77-mcp' $MCP77) -ne 0) { $bad++ }
    if ((Tier 'green' 'electron' '77' 'green77-e2e' $E2E77 'AC-77.14') -ne 0) { $bad++ }
    if ((Tier 'green' 'pytest' '77' 'green77-py' ($PY77 + $TA77)) -ne 0) { $bad++ }
    Finish $bad 'green77'
}

if ($Check -eq 'gate77') {
    $bad = TargetedGate '77' $SRC77
    if ((Tier 'suite' 'electron' '' 'gate77-e2e' $E2E77 '' @('--repeat-each=5')) -ne 0) { $bad++ }
    # Five consecutive runs of the threaded tests, all of which must pass (worker races).
    foreach ($n in 1..5) { if ((Tier 'suite' 'pytest' '' "gate77-async-$n" @('tests/unit/test_tts_async.py')) -ne 0) { $bad++ } }
    Finish $bad 'gate77'
}

if ($Check -eq 'hub') {
    $bad = 0
    if ((Ev 'hub-strings' @('hub')) -ne 0) { $bad++ }
    if ((Run 'hub-render' @('uv', 'run', 'python', 'tools/meu_status.py', 'render', '--check')) -ne 0) { $bad++ }
    # The doc-reading suites (they parse docs/build-plan).
    if ((Tier 'suite' 'vitest' '' 'hub-ui-docs' @('tests/unit/layout-canon.test.ts', 'tests/unit/queue-canon.test.ts', 'tests/unit/gui-actions-audit.test.ts')) -ne 0) { $bad++ }
    if ((Tier 'suite' 'mcp' '' 'hub-mcp-docs' @('tests/audit/docs.test.ts')) -ne 0) { $bad++ }
    Finish $bad 'hub'
}

if ($Check -eq 'task-state') {
    Finish (Ev 'h1-rows-eval' @('task-state')) 'task-state'
}

if ($Check -eq 'audit') {
    # H1-2: the authoritative /mcp-audit with --update-baseline (BASELINE_UPDATE_RULE), then baseline_carry.py and
    # AUDIT_EXPECT. AUDIT_COMPARISON: every attempt compares against the pre-session baseline (baseline.sha), so the
    # tts.cancel delta is FIXED on a rerun too. AUDIT_FINGERPRINT is measured before the prep and after the carry and
    # must not move. On any failure the start-of-check baseline is restored and this attempt's plan-folder evidence
    # is deleted (S5). The baseline is never edited by hand.
    $repo = (Resolve-Path .).Path
    $baselineRel = '.agent/skills/mcp-tool-audit/resources/baseline-snapshot.json'
    $baseline = Join-Path $repo $baselineRel
    $report = Join-Path $repo '.agent/context/MCP/mcp-tool-audit-report.md'
    $out = "$rd/s33-audit"
    $prior = "$rd/s33-baseline-prior.json"
    $presession = "$rd/s33-baseline-presession.json"
    $fpBefore = "$rd/s33-audit-fingerprint-before.txt"
    $fpAfter = "$rd/s33-audit-fingerprint-after.txt"
    $evidence = @((Join-Path $plan 'mcp-audit-summary.json'), (Join-Path $plan 'audit-fingerprint.json'))
    function AuditFail([string]$Why) {
        Copy-Item $prior $baseline -Force
        $evidence | ForEach-Object { Remove-Item $_ -Force -ErrorAction SilentlyContinue }
        Write-Host "FAIL $Why; the start-of-check baseline was restored and this attempt's evidence deleted. Keep $out and $report for the Decision Brief (S5)"
        exit 1
    }
    # A-11 (2026-10-15): skip the row's own receipt, which the task row's redirect holds open.
    Get-ChildItem -Path $rd -Filter 's33-audit*' -ErrorAction SilentlyContinue | Where-Object Name -ne 's33-audit-run.txt' | Remove-Item -Recurse -Force
    $evidence | ForEach-Object { Remove-Item $_ -Force -ErrorAction SilentlyContinue }
    Copy-Item $baseline $prior -Force
    if ((Ev 'audit-fp-before' @('fingerprint', '--out', $fpBefore, '--exclude', $baselineRel)) -ne 0) { AuditFail 'AUDIT_FINGERPRINT (before)' }
    foreach ($s in @(
            @('audit-uv-sync', @('uv', 'sync', '--frozen', '--all-packages')),
            @('audit-mcp-ci', @('npm', '--prefix', 'mcp-server', 'ci')),
            @('audit-mcp-build', @('npm', '--prefix', 'mcp-server', 'run', 'build')))) {
        if ((Run $s[0] $s[1]) -ne 0) { AuditFail "audit prep $($s[0])" }
    }
    # AUDIT_COMPARISON: the comparison file is the pre-session baseline, byte for byte from baseline.sha.
    $sha = (Get-Content "$plan/baseline.sha").Trim()
    $git = Start-Process -FilePath 'git' -ArgumentList @('show', "${sha}:$baselineRel") -NoNewWindow -Wait -PassThru `
        -RedirectStandardOutput $presession -RedirectStandardError "$rd/s33-audit-presession-err.txt"
    if ($git.ExitCode -ne 0) { AuditFail "git show ${sha}:$baselineRel" }
    Copy-Item $presession $baseline -Force
    $code = Run 'audit-runner' @('npm', '--prefix', 'mcp-server', 'run', 'audit', '--', '--mode', 'authoritative', '--baseline', $baseline,
        '--report', $report, '--update-baseline', '--out', $out, '--agent', 'local-windows-gate')
    # AUDIT_EXPECT needs exit 0 (1 = findings, 2 baseline refused, 3 isolation, 4 runner).
    if ($code -ne 0) { AuditFail "audit exit $code" }
    if ((Run 'audit-carry' @('uv', 'run', 'python', "$plan/baseline_carry.py", '--prior', $presession, '--baseline', $baseline)) -ne 0) { AuditFail 'baseline_carry refused' }
    if ((Ev 'audit-expect' @('audit-check', '--summary', "$out/mcp-audit-summary.json")) -ne 0) { AuditFail 'AUDIT_EXPECT' }
    if ((Ev 'audit-fp-after' @('fingerprint', '--out', $fpAfter, '--exclude', $baselineRel)) -ne 0) { AuditFail 'AUDIT_FINGERPRINT (after)' }
    if ((Ev 'audit-fp' @('audit-fp', '--before', $fpBefore, '--after', $fpAfter, '--out', "$plan/audit-fingerprint.json")) -ne 0) { AuditFail 'AUDIT_FINGERPRINT moved during the audit' }
    Copy-Item "$out/mcp-audit-summary.json" (Join-Path $plan 'mcp-audit-summary.json') -Force
    Finish 0 'audit (AUDIT_EXPECT; AUDIT_FINGERPRINT before == after, recorded)'
}

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
    $fpBefore = "$rd/s33-win-fingerprint-before.txt"
    $fpAfter = "$rd/s33-win-fingerprint-after.txt"
    # A run must never report an earlier run's counts: start from no receipts.
    Get-ChildItem -Path $rd -Filter 's33-win-*' -ErrorAction SilentlyContinue | Remove-Item -Force
    if ((Ev 'win-fp-before' @('fingerprint', '--out', $fpBefore)) -ne 0) { Finish 1 'windows-gate (fingerprint)' }
    $result = [ordered]@{
        schema              = 's33-windows-gate.v1'
        head                = (git rev-parse HEAD).Trim()
        baseline_sha        = (Get-Content "$plan/baseline.sha").Trim()
        fingerprint_before  = (Get-Content $fpBefore).Trim()
        fingerprint_after   = $null
        lockfile_sha256     = (Get-FileHash ui/package-lock.json -Algorithm SHA256).Hash
        mcp_lockfile_sha256 = (Get-FileHash mcp-server/package-lock.json -Algorithm SHA256).Hash
        uv_lock_sha256      = (Get-FileHash uv.lock -Algorithm SHA256).Hash
        electron            = ((npm --prefix ui ls electron --depth=0 2>$null) | Select-String 'electron@' | Out-String).Trim()
        node                = (node --version).Trim()
        preflight           = [ordered]@{ agentic_framework_head = $afHead; agent_registry_sha256 = $regHash; drift = $drift }
        # COUNT_FLOORS: seeds at 655 (Session 30 gate of record); then carries the first counted attempt's total.
        pytest_floor        = $(if ($null -ne $prev -and $null -ne $prev.pytest_floor) { $prev.pytest_floor } elseif ($null -ne $prev -and $null -ne $prev.pytest -and $null -ne $prev.pytest.passed) { $prev.pytest.passed } else { 655 })
        started             = (Get-Date).ToString('o')
        stages              = @()
        pytest              = $null
        vitest              = $null
        e2e                 = $null
        mcp                 = $null
    }
    if ($drift) {
        $result.finished = (Get-Date).ToString('o')
        $result | ConvertTo-Json -Depth 6 | Set-Content -Path $out -Encoding utf8
        Write-Host 'FAIL PREFLIGHT drift: P:/agentic-framework HEAD or P:/.agent registry changed since the previous attempt; report before stage 1 (S6)'
        exit 1
    }

    function Invoke-Stage([string]$Id, [string[]]$Argv) {
        $receipt = "$rd/s33-win-$Id.txt"
        $clock = [System.Diagnostics.Stopwatch]::StartNew()
        & rtk proxy @Argv *> $receipt
        $code = $LASTEXITCODE
        $clock.Stop()
        $script:result.stages += [ordered]@{ id = $Id; argv = ($Argv -join ' '); exit = $code; seconds = [math]::Round($clock.Elapsed.TotalSeconds, 1); receipt = $receipt }
        Get-Content $receipt -Tail 15 | Write-Host
        return $code
    }

    $auditSrc = @($SRC76 + $SRC78 + $SRC77 | Sort-Object -Unique)
    $vjson = "$rd/s33-win-vitest.json"
    $ejson = "$rd/s33-win-e2e.json"
    $mjson = "$rd/s33-win-mcp.json"
    $pytxt = "$rd/s33-win-py-tests.txt"
    # WINDOWS_GATE stage order (Session 30/31); plan_checks.py static asserts it equals exec_checks.STAGES.
    $stages = @(
        # Session 27 A-5: Electron 42 has no postinstall; its binary downloads on the first require. Install it
        # here, serially, so parallel Vitest workers never race the extraction.
        @('npm-ci', @('pwsh', '-NoProfile', '-Command', "npm --prefix ui ci; if (`$LASTEXITCODE -ne 0) { exit `$LASTEXITCODE }; node ui/node_modules/electron/install.js; if (`$LASTEXITCODE -ne 0) { exit `$LASTEXITCODE }; if (-not (Test-Path ui/node_modules/electron/path.txt)) { exit 3 }; exit 0")),
        @('mcp-npm-ci', @('npm', '--prefix', 'mcp-server', 'ci')),
        @('py-types', @('uv', 'run', 'pyright', 'packages/')),
        @('py-lint', @('uv', 'run', 'ruff', 'check', 'packages/', 'tests/')),
        @('ui-types', @('npm', '--prefix', 'ui', 'run', 'typecheck')),
        @('ui-lint', @('npm', '--prefix', 'ui', 'run', 'lint')),
        @('mcp-types', @('npm', '--prefix', 'mcp-server', 'run', 'typecheck')),
        @('py-tests', @('uv', 'run', 'pytest', 'tests/', '-x', '--tb=short', '-q')),
        @('ui-tests', @('npm', '--prefix', 'ui', 'run', 'test', '--', '--reporter=json', "--outputFile=$vjson")),
        @('ui-build', @('npm', '--prefix', 'ui', 'run', 'build')),
        @('ui-harness-build', @('pwsh', '-NoProfile', '-Command', "`$env:AVKIT_PRIMITIVE_HARNESS_BUILD='1'; npm --prefix ui run build -- --outDir '$((Resolve-Path ui).Path)/out-e2e'; exit `$LASTEXITCODE")),
        # The MCP suite asserts the built dist exists (AC-32.8, AC-38.8), so build first.
        @('mcp-build', @('npm', '--prefix', 'mcp-server', 'run', 'build')),
        @('mcp-tests', @('npm', '--prefix', 'mcp-server', 'run', 'test', '--', '--reporter=json', "--outputFile=$mjson")),
        @('openapi', @('uv', 'run', 'python', 'tools/export_openapi.py', '--check', 'openapi.committed.json')),
        @('state-render', @('uv', 'run', 'python', 'tools/meu_status.py', 'render', '--check')),
        @('ui-electron', @('npm', '--prefix', 'ui', 'run', 'test:e2e', '--', '--reporter=json', "--outputFile=$ejson")),
        @('source-audit', (@('rg', '-n', '-e', $auditPattern) + $auditSrc))
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
    if ($ran -contains 'mcp-tests' -and (Test-Path $mjson)) {
        $m = Get-Content $mjson -Raw | ConvertFrom-Json
        $result.mcp = [ordered]@{ passed = $m.numPassedTests; failed = $m.numFailedTests; total = $m.numTotalTests }
    }
    if ($ran -contains 'ui-electron' -and (Test-Path $ejson)) {
        $e = Get-Content $ejson -Raw | ConvertFrom-Json
        $result.e2e = [ordered]@{ expected = $e.stats.expected; unexpected = $e.stats.unexpected; skipped = $e.stats.skipped; flaky = $e.stats.flaky }
    }
    if ($ran -contains 'py-tests' -and ($null -eq $result.pytest -or $null -eq $result.pytest.passed)) { Write-Host 'FAIL: py-tests ran but produced no pytest summary'; $failed = $true }
    if ($ran -contains 'ui-tests' -and $null -eq $result.vitest) { Write-Host 'FAIL: ui-tests ran but produced no Vitest JSON'; $failed = $true }
    if ($ran -contains 'mcp-tests' -and $null -eq $result.mcp) { Write-Host 'FAIL: mcp-tests ran but produced no Vitest JSON'; $failed = $true }
    if ($ran -contains 'ui-electron' -and $null -eq $result.e2e) { Write-Host 'FAIL: ui-electron ran but produced no Playwright JSON'; $failed = $true }
    # GATE_FINGERPRINT after the last stage: the stages must not have changed a gated file.
    if ((Ev 'win-fp-after' @('fingerprint', '--out', $fpAfter)) -ne 0) { $failed = $true } else { $result.fingerprint_after = (Get-Content $fpAfter).Trim() }
    if ($result.fingerprint_after -ne $result.fingerprint_before) { Write-Host 'FAIL: GATE_FINGERPRINT changed during the run'; $failed = $true }
    $result.finished = (Get-Date).ToString('o')
    $result | ConvertTo-Json -Depth 6 | Set-Content -Path $out -Encoding utf8
    Get-Content $out | Write-Host
    if ($failed) { Write-Host 'FAIL WINDOWS_GATE; see the receipts named in the JSON'; exit 1 }
    Finish 0 'WINDOWS_GATE'
}

if ($Check -eq 'gate-check') {
    Finish (Ev 'gate-check-eval' @('gate-check')) 'gate-check (stages, COUNT_FLOORS, GATE_FINGERPRINT, AUDIT_FINGERPRINT, AUDIT_EXPECT)'
}

if ($Check -eq 'ssot-review') {
    $bad = 0
    foreach ($m in @('MEU-76', 'MEU-78', 'MEU-77')) {
        if ((Run "h1-ssot-$m" @('uv', 'run', 'python', 'tools/meu_status.py', 'update', $m, 'ready_for_review', '--plan', $plan)) -ne 0) { $bad++ }
    }
    if ((Run 'h1-ssot-render' @('uv', 'run', 'python', 'tools/meu_status.py', 'render')) -ne 0) { $bad++ }
    if ((Run 'h1-ssot-render-check' @('uv', 'run', 'python', 'tools/meu_status.py', 'render', '--check')) -ne 0) { $bad++ }
    if ((Ev 'h1-ssot-eval' @('ssot-review')) -ne 0) { $bad++ }
    Finish $bad 'ssot-review'
}

if ($Check -eq 'api-scope') {
    $bad = 0
    if ((Run 'api-scope-openapi' @('uv', 'run', 'python', 'tools/export_openapi.py', '--check', 'openapi.committed.json')) -ne 0) { $bad++ }
    if ((Ev 'api-scope-eval' @('api-scope')) -ne 0) { $bad++ }
    Finish $bad 'api-scope (PRODUCT_SCOPE, OPENAPI_DIFF, TEST_AMENDMENTS markers)'
}

if ($Check -eq 'handoff-ac') {
    # The closeout tool's AC_ID is \bAC-(\d+)\b, so it proves each handoff names AC-76, AC-77 and AC-78;
    # exec_checks handoff-ac proves each handoff names every full AC id of its own MEU.
    $bad = 0
    foreach ($m in @('76', '78', '77')) {
        if ((Run "handoff-ac-$m" @('uv', 'run', 'python', 'tools/validate_closeout_artifacts.py', '--plan', "$plan/implementation-plan.md",
                    '--handoff', ".agent/context/handoffs/2026-10-14-backend-robustness-MEU-$m-handoff.md", '--ac-coverage-only')) -ne 0) { $bad++ }
    }
    if ((Ev 'handoff-ac-eval' @('handoff-ac')) -ne 0) { $bad++ }
    Finish $bad 'handoff-ac'
}

if ($Check -eq 'review-check') {
    if ($Target -eq '' -or $Mode -notin @('plan', 'execution') -or $Cap -lt 1) { Write-Host 'FAIL: review-check needs -Target, -Mode plan|execution and -Cap'; exit 1 }
    Finish (Ev "review-check-$Mode" @('review-check', '--target', $Target, '--mode', $Mode, '--cap', "$Cap")) 'review-check'
}

if ($Check -eq 'post-review-state') {
    $bad = 0
    foreach ($m in @('MEU-76', 'MEU-78', 'MEU-77')) {
        if ((Run "post-review-$m" @('uv', 'run', 'python', 'tools/meu_status.py', 'update', $m, 'approved', '--plan', $plan)) -ne 0) { $bad++ }
    }
    if ((Run 'post-review-render' @('uv', 'run', 'python', 'tools/meu_status.py', 'render')) -ne 0) { $bad++ }
    if ((Run 'post-review-render-check' @('uv', 'run', 'python', 'tools/meu_status.py', 'render', '--check')) -ne 0) { $bad++ }
    if ((Run 'post-review-issues' @('uv', 'run', 'python', 'tools/issue_triage.py', 'render', '--check')) -ne 0) { $bad++ }
    if ((Ev 'post-review-eval' @('post-review-state')) -ne 0) { $bad++ }
    # Every suite that reads a GATE_EXCLUDED file again: those files changed after the gate (GATED_PATHS rule).
    if ((Tier 'suite' 'vitest' '' 'post-review-ui-docs' @('tests/unit/layout-canon.test.ts', 'tests/unit/queue-canon.test.ts', 'tests/unit/gui-actions-audit.test.ts')) -ne 0) { $bad++ }
    if ((Tier 'suite' 'mcp' '' 'post-review-mcp-docs' @('tests/audit/docs.test.ts')) -ne 0) { $bad++ }
    # test_framework_adoption copies the manifest's files, current-focus.md among them.
    if ((Tier 'suite' 'pytest' '' 'post-review-py-docs' @('tests/tooling/test_framework_adoption.py')) -ne 0) { $bad++ }
    Finish $bad 'post-review-state'
}

throw "Unknown check: $Check"
