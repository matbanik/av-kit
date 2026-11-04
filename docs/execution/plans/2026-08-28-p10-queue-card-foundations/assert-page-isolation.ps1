# RETIRED (MEU-45, AC-45.14) - DO NOT RUN AGAINST A MIGRATED TREE.
#
# Successor: docs/execution/plans/2026-09-02-p10-queue-card-migration/assert-mount-completeness.ps1
# (MOUNT_GATE_SCRIPT). This gate proves the OPPOSITE property of its successor: it asserts that
# the shared queue surface is wired to NO page, which was true only for the MEU-43/44 foundations
# sessions. From MEU-45 onward the pages deliberately mount that surface, so a verify run here
# fails by design and its failure carries no information. The file is kept, not deleted, because
# it is the sole executable record of PAGE_ISOLATION_RULE and of the foundations baseline it
# captured; run assert-mount-completeness.ps1 instead.

# Sole executable owner of PAGE_ISOLATION_RULE. Proves session 19 wires nothing to a page.
#
# This tree is NOT a git work tree, so "no delta" cannot be proven with `git diff`.
# Instead task row 1 runs -Capture BEFORE any edit to record a content baseline, and every
# later gate runs the default verify mode against it. Verify is delta-bound (R1-F2):
#   1. every FROZEN file is byte-identical, and no frozen file was added or deleted
#   2. the two CARVE_OUT files admit ONLY the shared-import edit: added lines must be
#      lib/queue imports, removed lines must belong to the local formatFileSize block,
#      and the data-testid multiset must be unchanged
#   3. nothing outside the new surface itself may reference the new surface, which closes
#      barrel/re-export reachability because a barrel is itself a referencing file
#   4. E2E test identities (not just a count) are unchanged
#   5. every PRESERVED_TESTIDS id is still registered
param(
    [switch]$Capture,
    [switch]$SelfTest,
    # -Root/-Baseline exist ONLY so -SelfTest can re-invoke this same script against a
    # synthetic fixture repo. Normal gate runs pass neither and operate on the real tree.
    [string]$Root,
    [string]$Baseline,
    # -Only filters -SelfTest to one case and keeps its fixture on disk (debugging aid).
    [string]$Only
)
$ErrorActionPreference = 'Stop'
$setsPath = Join-Path $PSScriptRoot 'named-sets.json'
if (-not (Test-Path -LiteralPath $setsPath)) {
    Write-Error ('missing NAMED_SETS_FILE ' + $setsPath)
    exit 1
}
$sets = Get-Content -LiteralPath $setsPath -Raw | ConvertFrom-Json
$baselinePath = if ($Baseline) { $Baseline } else { [string]$sets.PAGE_BASELINE }
$carveOut = @($sets.CARVE_OUT_FILES)
$repoRoot = if ($Root) {
    (Resolve-Path -LiteralPath $Root).Path
} else {
    (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '../../../..')).Path
}

function Get-Rel {
    param([string]$FullPath)
    $p = $FullPath.Replace('\', '/')
    $root = $repoRoot.Replace('\', '/').TrimEnd('/') + '/'
    if ($p.StartsWith($root, [StringComparison]::OrdinalIgnoreCase)) {
        return $p.Substring($root.Length)
    }
    return $p
}

# Every file the session promises not to touch, minus the two declared carve-outs.
# PowerShell has no globstar: 'a/**/*.tsx' with -Recurse silently matches nothing, and a bare
# leaf path with -Recurse degrades into "find this filename anywhere below the parent" (which
# sweeps in node_modules). Both were live defects. Resolve each glob explicitly instead.
function Get-FrozenFiles {
    $out = New-Object System.Collections.Generic.List[string]
    foreach ($glob in @($sets.FROZEN_GLOBS)) {
        $items = @()
        if ($glob -match '^(.*?)/\*\*/(.+)$') {
            # recursive form: <dir>/**/<leafPattern>
            $dir = Join-Path $repoRoot $Matches[1]
            $leaf = $Matches[2]
            if (Test-Path -LiteralPath $dir) {
                $items = @(Get-ChildItem -LiteralPath $dir -Recurse -File -Filter $leaf -ErrorAction Stop)
            } else {
                Write-Error ("FROZEN_GLOBS dir does not exist: " + $Matches[1]); exit 1
            }
        } elseif ($glob -match '[\*\?]') {
            # single-level wildcard
            $items = @(Get-ChildItem -Path (Join-Path $repoRoot $glob) -File -ErrorAction SilentlyContinue)
        } else {
            # literal file - never -Recurse
            $lit = Join-Path $repoRoot $glob
            if (-not (Test-Path -LiteralPath $lit -PathType Leaf)) {
                Write-Error ("FROZEN_GLOBS file does not exist: " + $glob); exit 1
            }
            $items = @(Get-Item -LiteralPath $lit)
        }
        if ($items.Count -eq 0) {
            Write-Error ("FROZEN_GLOBS pattern matched zero files (frozen set must never be empty): " + $glob)
            exit 1
        }
        foreach ($i in $items) {
            $rel = Get-Rel $i.FullName
            if ($rel -match '(^|/)(node_modules|dist|out|build)/') { continue }
            if ($carveOut -contains $rel) { continue }
            if (-not $out.Contains($rel)) { $out.Add($rel) }
        }
    }
    return @($out | Sort-Object)
}

function Get-Sha {
    param([string]$Rel)
    $full = Join-Path $repoRoot $Rel
    return (Get-FileHash -LiteralPath $full -Algorithm SHA256).Hash
}

function Get-Lines {
    param([string]$Rel)
    $full = Join-Path $repoRoot $Rel
    return @(Get-Content -LiteralPath $full)
}

function Get-TestIds {
    param([string[]]$Lines)
    $ids = New-Object System.Collections.Generic.List[string]
    foreach ($l in $Lines) {
        foreach ($m in [regex]::Matches($l, "data-testid\s*=\s*[`"'{]?\s*[`"']?([A-Za-z0-9_.:-]+)")) {
            $ids.Add($m.Groups[1].Value)
        }
    }
    return @($ids | Sort-Object)
}

# The contiguous local definition block for the duplicated helper, so "removed lines" can be
# checked against an exact allowed set instead of a fuzzy heuristic.
function Get-RemovableBlock {
    param([string[]]$Lines)
    $symbol = [string]$sets.CARVE_OUT_REMOVABLE_SYMBOL
    $start = -1
    for ($i = 0; $i -lt $Lines.Count; $i++) {
        if ($Lines[$i] -match ('(function|const)\s+' + [regex]::Escape($symbol) + '\b')) { $start = $i; break }
    }
    if ($start -lt 0) { return @() }
    $depth = 0
    $seen = $false
    for ($j = $start; $j -lt $Lines.Count; $j++) {
        $depth += ([regex]::Matches($Lines[$j], '\{')).Count
        $depth -= ([regex]::Matches($Lines[$j], '\}')).Count
        if (([regex]::Matches($Lines[$j], '\{')).Count -gt 0) { $seen = $true }
        if ($seen -and $depth -le 0) {
            return @($Lines[$start..$j])
        }
    }
    return @()
}

function Get-E2eTitles {
    $titles = New-Object System.Collections.Generic.List[string]
    foreach ($glob in @($sets.E2E_GLOBS)) {
        $specs = @(Get-ChildItem -Path (Join-Path $repoRoot ([string]$sets.E2E_DIR)) -Filter $glob -File -ErrorAction SilentlyContinue)
        foreach ($s in $specs) {
            $rel = Get-Rel $s.FullName
            foreach ($line in @(Get-Content -LiteralPath $s.FullName)) {
                $m = [regex]::Match($line, "^\s*test\(\s*(['`"``])(.+?)\1")
                if ($m.Success) {
                    $titles.Add($rel + ' :: ' + $m.Groups[2].Value)
                }
            }
        }
    }
    return @($titles | Sort-Object)
}

# ---------------------------------------------------------------------------
# -SelfTest: prove the NEGATIVE direction hermetically (R1-F2).
#
# A gate that only ever reports PASS on an unchanged tree proves nothing -- the reviewer's
# finding was precisely that the previous oracle "can pass a materially migrated queue".
# So build a synthetic fixture repo under SELFTEST_DIR, capture a baseline from it, apply
# ONE mutation per case, and assert this same script rejects it with the expected reason.
# Nothing outside SELFTEST_DIR is read or written; the real tree is never mutated.
# ---------------------------------------------------------------------------
if ($SelfTest) {
    $sandbox = [string]$sets.SELFTEST_DIR
    $fx = Join-Path $sandbox 'repo'
    $bl = Join-Path $sandbox 'baseline.json'
    $log = Join-Path $sandbox 'child.out.txt'
    $errLog = Join-Path $sandbox 'child.err.txt'

    function Write-Fx {
        param([string]$Rel, [string[]]$Lines)
        $full = Join-Path $fx $Rel
        New-Item -ItemType Directory -Force -Path (Split-Path -Parent $full) | Out-Null
        Set-Content -LiteralPath $full -Value $Lines -Encoding UTF8
    }

    function New-Fixture {
        if (Test-Path -LiteralPath $fx) { Remove-Item -LiteralPath $fx -Recurse -Force }
        New-Item -ItemType Directory -Force -Path $fx | Out-Null

        # frozen page entrypoints
        foreach ($pair in @(@('converter', 'ConvertPage'), @('downloader', 'DownloaderPage'))) {
            Write-Fx ('ui/src/renderer/src/features/' + $pair[0] + '/' + $pair[1] + '.tsx') @(
                "import { useState } from 'react'",
                ('export function ' + $pair[1] + '() {'),
                '  const [n] = useState(0)',
                '  return <div>{n}</div>',
                '}'
            )
        }
        Write-Fx 'ui/src/renderer/src/router.tsx' @('export const routes = []')
        Write-Fx 'ui/src/renderer/src/main.tsx' @('export const main = 1')
        Write-Fx 'mcp-server/src/index.ts' @('export const server = 1')
        Write-Fx 'ui/package.json' @('{ "name": "ui", "dependencies": {} }')
        Write-Fx 'ui/package-lock.json' @('{ "lockfileVersion": 3 }')

        # the two carve-out queue tables: each owns a local formatFileSize block
        foreach ($pair in @(@('converter', 'ConvertQueueTable'), @('downloader', 'DownloadQueueTable'))) {
            Write-Fx ('ui/src/renderer/src/features/' + $pair[0] + '/' + $pair[1] + '.tsx') @(
                "import { useState } from 'react'",
                '',
                'function formatFileSize(bytes: number): string {',
                "  if (bytes < 1024) { return bytes + ' B' }",
                "  return (bytes / 1024).toFixed(1) + ' KB'",
                '}',
                '',
                ('export function ' + $pair[1] + '() {'),
                '  return (',
                '    <table data-testid="queue-table">',
                '      <tbody data-testid="queue-row" />',
                '    </table>',
                '  )',
                '}'
            )
        }

        # the new (session-19) surface plus one exempt sibling, and one clean scanned file
        Write-Fx 'ui/src/renderer/src/components/queue/QueueCard.tsx' @('export function QueueCard() { return null }')
        Write-Fx 'ui/src/renderer/src/lib/queue/format.ts' @('export function formatFileSize(b: number) { return String(b) }')
        Write-Fx 'ui/src/renderer/src/components/ui/Button.tsx' @('export function Button() { return null }')
        # a legal neighbour import of a PRE-EXISTING components/ui module: must stay legal,
        # otherwise the rule would forbid ordinary shared-component use.
        Write-Fx 'ui/src/renderer/src/components/help/HelpCard.tsx' @(
            "import { Button } from '../ui/Button'",
            'export function HelpCard() { return <Button /> }'
        )
        Write-Fx 'ui/src/renderer/src/lib/api.ts' @('export const api = 1')

        # E2E specs: exactly E2E_BASELINE_COUNT titles so the real count check applies
        $e2e = New-Object System.Collections.Generic.List[string]
        $e2e.Add("import { test } from '@playwright/test'")
        for ($i = 1; $i -le [int]$sets.E2E_BASELINE_COUNT; $i++) {
            $e2e.Add("test('selftest case " + $i + "', async () => {})")
        }
        Write-Fx (([string]$sets.E2E_DIR) + '/app.test.ts') @($e2e)

        $reg = New-Object System.Collections.Generic.List[string]
        $reg.Add('export const TEST_IDS = [')
        foreach ($id in @($sets.PRESERVED_TESTIDS)) { $reg.Add("  '" + $id + "',") }
        $reg.Add('] as const')
        Write-Fx ([string]$sets.TESTID_REGISTRY) @($reg)
    }

    function Invoke-Iso {
        param([switch]$Cap)
        $a = @('-NoProfile', '-File', $PSCommandPath, '-Root', $fx, '-Baseline', $bl)
        if ($Cap) { $a += '-Capture' }
        # P0: every child stream lands in a file under the sandbox, never on this terminal.
        $p = Start-Process -FilePath 'pwsh' -ArgumentList $a -Wait -PassThru -NoNewWindow `
            -RedirectStandardOutput $log -RedirectStandardError $errLog
        $out = ''
        foreach ($f in @($log, $errLog)) {
            if (Test-Path -LiteralPath $f) { $out += ((Get-Content -LiteralPath $f -Raw) + "`n") }
        }
        return @{ code = $p.ExitCode; out = $out }
    }

    function Edit-Line {
        param([string]$Rel, [string]$Match, [string]$Replacement)
        $full = Join-Path $fx $Rel
        $lines = @(Get-Content -LiteralPath $full)
        $done = $false
        for ($i = 0; $i -lt $lines.Count; $i++) {
            if (-not $done -and $lines[$i] -match [regex]::Escape($Match)) {
                if ($Replacement -eq '') { $lines[$i] = '__DELETE__' } else { $lines[$i] = $Replacement }
                $done = $true
            }
        }
        if (-not $done) { throw ('selftest fixture drift: no line matching "' + $Match + '" in ' + $Rel) }
        Set-Content -LiteralPath $full -Value @($lines | Where-Object { $_ -ne '__DELETE__' }) -Encoding UTF8
    }

    $CARVE = 'ui/src/renderer/src/features/converter/ConvertQueueTable.tsx'
    $PAGE = 'ui/src/renderer/src/features/converter/ConvertPage.tsx'

    # expect = '' means the mutation is LEGAL and the gate must still pass.
    $cases = @(
        @{ name = 'clean-baseline'; expect = ''; mut = { } },
        @{ name = 'frozen-page-modified'; expect = 'frozen file modified'
            mut = { Add-Content -LiteralPath (Join-Path $fx $PAGE) -Value '// migrated to QueueCard' } },
        @{ name = 'frozen-page-added'; expect = 'new file appeared inside the frozen surface'
            mut = { Write-Fx 'ui/src/renderer/src/features/converter/ConvertPageV2.tsx' @('export const x = 1') } },
        @{ name = 'frozen-page-deleted'; expect = 'frozen file deleted'
            mut = { Remove-Item -LiteralPath (Join-Path $fx 'ui/src/renderer/src/features/downloader/DownloaderPage.tsx') } },
        @{ name = 'mcp-source-modified'; expect = 'frozen file modified'
            mut = { Add-Content -LiteralPath (Join-Path $fx 'mcp-server/src/index.ts') -Value '// new tool' } },
        @{ name = 'dependency-manifest-modified'; expect = 'frozen file modified'
            mut = { Set-Content -LiteralPath (Join-Path $fx 'ui/package.json') -Value '{ "name": "ui", "dependencies": { "dnd-kit": "^6" } }' -Encoding UTF8 } },
        @{ name = 'carveout-legal-shared-import'; expect = ''
            mut = {
                $full = Join-Path $fx $CARVE
                $lines = @(Get-Content -LiteralPath $full)
                $keep = New-Object System.Collections.Generic.List[string]
                $keep.Add($lines[0])
                $keep.Add("import { formatFileSize } from '../../lib/queue/format'")
                for ($i = 6; $i -lt $lines.Count; $i++) { $keep.Add($lines[$i]) }
                Set-Content -LiteralPath $full -Value @($keep) -Encoding UTF8
            } },
        @{ name = 'carveout-illegal-add'; expect = 'added a non-import line'
            mut = { Edit-Line $CARVE '<tbody' '      <QueueCard status="Done" />' } },
        @{ name = 'carveout-illegal-remove'; expect = 'removed a line outside'
            mut = { Edit-Line $CARVE '<tbody' '' } },
        @{ name = 'carveout-testid-renamed'; expect = '(added a non-import line|changed its data-testid set)'
            mut = { Edit-Line $CARVE 'queue-row' '      <tbody data-testid="queue-row-v2" />' } },
        @{ name = 'carveout-file-deleted'; expect = 'carve-out file deleted'
            mut = { Remove-Item -LiteralPath (Join-Path $fx $CARVE) } },
        # Rule 2 is strictly tighter than rule 3 on the carve-outs (only a lib/queue/format import
        # may be ADDED at all), so it legitimately fires first; either rejection proves the doorway
        # is narrow rather than a blanket new-surface exemption.
        @{ name = 'carveout-reaches-other-new-surface'; expect = '(added a non-import line|removed a line outside|referenced outside its own directory)'
            mut = { Edit-Line $CARVE "import { useState } from 'react'" "import { QueueCard } from '../../components/queue/QueueCard'" } },
        @{ name = 'reachability-direct-import'; expect = 'referenced outside its own directory'
            mut = { Write-Fx 'ui/src/renderer/src/hooks/useQueue.ts' @(
                    "import { QueueCard } from '../components/queue/QueueCard'",
                    'export const useQueue = () => QueueCard') } },
        @{ name = 'reachability-barrel-reexport'; expect = 'referenced outside its own directory'
            mut = { Write-Fx 'ui/src/renderer/src/components/index.ts' @("export * from './queue/QueueCard'") } },
        @{ name = 'reachability-alias-import'; expect = 'referenced outside its own directory'
            mut = { Write-Fx 'ui/src/renderer/src/hooks/useFmt.ts' @("import { formatFileSize } from '@/lib/queue/format'") } },
        @{ name = 'e2e-title-renamed-at-constant-count'; expect = 'E2E identity changed'
            mut = { Edit-Line (([string]$sets.E2E_DIR) + '/app.test.ts') "test('selftest case 7'" "test('renamed case', async () => {})" } },
        @{ name = 'e2e-test-added'; expect = 'E2E identity changed'
            mut = { Add-Content -LiteralPath (Join-Path $fx (([string]$sets.E2E_DIR) + '/app.test.ts')) -Value "test('extra case', async () => {})" } },
        @{ name = 'preserved-testid-dropped'; expect = 'lost preserved testid'
            mut = { Edit-Line ([string]$sets.TESTID_REGISTRY) ("'" + @($sets.PRESERVED_TESTIDS)[2] + "',") '' } },
        @{ name = 'baseline-missing'; expect = 'missing PAGE_BASELINE'
            mut = { Remove-Item -LiteralPath $bl } }
    )

    New-Item -ItemType Directory -Force -Path $sandbox | Out-Null
    $failures = New-Object System.Collections.Generic.List[string]
    if ($Only) { $cases = @($cases | Where-Object { $_.name -eq $Only }) }
    if ($cases.Count -eq 0) { Write-Error ('no selftest case named ' + $Only); exit 1 }
    foreach ($case in $cases) {
        New-Fixture
        $cap = Invoke-Iso -Cap
        if ($cap.code -ne 0) {
            $failures.Add($case.name + ': fixture baseline capture failed -> ' + $cap.out.Trim())
            continue
        }
        & $case.mut
        $r = Invoke-Iso
        if ($case.expect -eq '') {
            if ($r.code -ne 0) {
                $failures.Add($case.name + ': expected PASS, got exit ' + $r.code + ' -> ' + $r.out.Trim())
            }
        } elseif ($r.code -eq 0) {
            $failures.Add($case.name + ': MUTATION NOT DETECTED (gate returned PASS)')
        } elseif ($r.out -notmatch $case.expect) {
            $failures.Add($case.name + ': detected but wrong reason; wanted /' + $case.expect + '/ got -> ' + $r.out.Trim())
        }
    }
    if (-not $Only -and (Test-Path -LiteralPath $fx)) { Remove-Item -LiteralPath $fx -Recurse -Force }
    if ($failures.Count -gt 0) {
        foreach ($f in $failures) { Write-Error $f }
        Write-Error ('FAIL: PAGE_ISOLATION selftest ' + $failures.Count + '/' + $cases.Count + ' cases wrong')
        exit 1
    }
    'PASS: PAGE_ISOLATION selftest ' + $cases.Count + ' cases'
    exit 0
}

# ---------------------------------------------------------------------------
if ($Capture) {
    $frozen = [ordered]@{}
    foreach ($rel in Get-FrozenFiles) { $frozen[$rel] = Get-Sha $rel }
    $carve = [ordered]@{}
    foreach ($rel in $carveOut) {
        $full = Join-Path $repoRoot $rel
        if (-not (Test-Path -LiteralPath $full)) {
            Write-Error ('missing CARVE_OUT_FILES entry ' + $rel)
            exit 1
        }
        $lines = Get-Lines $rel
        $removable = Get-RemovableBlock $lines
        if ($removable.Count -lt 1) {
            Write-Error ('carve-out file has no ' + $sets.CARVE_OUT_REMOVABLE_SYMBOL + ' block: ' + $rel)
            exit 1
        }
        $carve[$rel] = [ordered]@{
            lines     = @($lines)
            removable = @($removable)
            testids   = @(Get-TestIds $lines)
        }
    }
    $titles = Get-E2eTitles
    if ($titles.Count -lt 1) {
        Write-Error ('no E2E test titles found under ' + $sets.E2E_DIR)
        exit 1
    }
    $payload = [ordered]@{
        frozen    = $frozen
        carveout  = $carve
        e2eTitles = @($titles)
    }
    New-Item -ItemType Directory -Force -Path (Split-Path -Parent $baselinePath) | Out-Null
    $payload | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath $baselinePath -Encoding UTF8
    'PASS: PAGE_ISOLATION baseline captured frozen=' + $frozen.Count + ' carveout=' + $carve.Count + ' e2e=' + $titles.Count
    exit 0
}

# ---------------------------------------------------------------------------
if (-not (Test-Path -LiteralPath $baselinePath)) {
    Write-Error ('missing PAGE_BASELINE ' + $baselinePath + ' — task row 1 must run this script with -Capture before any edit')
    exit 1
}
$base = Get-Content -LiteralPath $baselinePath -Raw | ConvertFrom-Json

# 1. Frozen surface is byte-identical, with no additions or deletions.
$baseFrozen = @{}
foreach ($p in $base.frozen.PSObject.Properties) { $baseFrozen[$p.Name] = [string]$p.Value }
$nowFrozen = @(Get-FrozenFiles)
foreach ($rel in $nowFrozen) {
    if (-not $baseFrozen.ContainsKey($rel)) {
        Write-Error ('new file appeared inside the frozen surface: ' + $rel)
        exit 1
    }
    if ((Get-Sha $rel) -ne $baseFrozen[$rel]) {
        Write-Error ('frozen file modified: ' + $rel)
        exit 1
    }
}
foreach ($rel in $baseFrozen.Keys) {
    if ($nowFrozen -notcontains $rel) {
        Write-Error ('frozen file deleted: ' + $rel)
        exit 1
    }
}

# 2. The two carve-out files admit only the shared-import edit.
$allowedImport = [string]$sets.CARVE_OUT_ALLOWED_IMPORT
foreach ($rel in $carveOut) {
    $full = Join-Path $repoRoot $rel
    if (-not (Test-Path -LiteralPath $full)) {
        Write-Error ('carve-out file deleted: ' + $rel)
        exit 1
    }
    $entry = $base.carveout.$rel
    if ($null -eq $entry) {
        Write-Error ('PAGE_BASELINE has no carve-out record for ' + $rel)
        exit 1
    }
    $baseLines = @($entry.lines)
    $nowLines = Get-Lines $rel
    $removable = @($entry.removable)

    $added = @(Compare-Object -ReferenceObject $baseLines -DifferenceObject $nowLines |
        Where-Object { $_.SideIndicator -eq '=>' } | ForEach-Object { [string]$_.InputObject })
    $removed = @(Compare-Object -ReferenceObject $baseLines -DifferenceObject $nowLines |
        Where-Object { $_.SideIndicator -eq '<=' } | ForEach-Object { [string]$_.InputObject })

    foreach ($line in $added) {
        $t = $line.Trim()
        if ($t -eq '') { continue }
        if ($t -notmatch '^import\b' -or $t -notmatch [regex]::Escape($allowedImport)) {
            Write-Error ('carve-out ' + $rel + ' added a non-import line: ' + $t)
            exit 1
        }
    }
    foreach ($line in $removed) {
        if ($line.Trim() -eq '') { continue }
        if ($removable -notcontains $line) {
            Write-Error ('carve-out ' + $rel + ' removed a line outside the ' + $sets.CARVE_OUT_REMOVABLE_SYMBOL + ' block: ' + $line.Trim())
            exit 1
        }
    }
    $baseIds = @($entry.testids)
    $nowIds = @(Get-TestIds $nowLines)
    $idDiff = @(Compare-Object -ReferenceObject $baseIds -DifferenceObject $nowIds)
    if ($idDiff.Count -gt 0) {
        Write-Error ('carve-out ' + $rel + ' changed its data-testid set')
        exit 1
    }
}

# 3. Nothing outside the new surface may reference the new surface. Import specifiers are
#    RESOLVED (not substring-matched) because this repo imports relatively: a barrel at
#    components/index.ts re-exporting './queue/QueueCard' contains no 'components/queue/'
#    substring, so raw text matching could not see the very re-export bypass this closes.
$newSurface = @($sets.NEW_SURFACE_MODULES)
$exempt = @($sets.NEW_SURFACE_EXEMPT)
$scanRootRel = ([string]$sets.REACHABILITY_SCAN_ROOT).TrimEnd('/')
$carveAllowed = $scanRootRel + '/' + ([string]$sets.CARVE_OUT_ALLOWED_IMPORT)
$scanRoot = Join-Path $repoRoot $scanRootRel

# './a/../b/c' -> 'a/b/c', relative to the importing file's directory.
function Resolve-Spec {
    param([string]$FromRel, [string]$Spec)
    if ($Spec.StartsWith('@/')) { return $scanRootRel + '/' + $Spec.Substring(2) }
    if (-not $Spec.StartsWith('.')) { return $null }
    $parts = New-Object System.Collections.Generic.List[string]
    # NB: a two-character '\\' in a PowerShell single-quoted string is TWO backslashes, so
    # .Replace() against it is a silent no-op on Windows paths -- it dropped every parent
    # segment and made this whole rule vacuous. Split on both separators by char code.
    foreach ($p in (Split-Path -Parent $FromRel).Split([char[]]@([char]92, [char]47))) {
        if ($p -ne '') { $parts.Add($p) }
    }
    foreach ($p in $Spec.Split('/')) {
        if ($p -eq '' -or $p -eq '.') { continue }
        if ($p -eq '..') {
            if ($parts.Count -gt 0) { $parts.RemoveAt($parts.Count - 1) }
        } else {
            $parts.Add($p)
        }
    }
    return ($parts -join '/')
}

# NEW_SURFACE_MODULES entries ending in '/' are directories; the rest name a module,
# with or without extension. Matching the suffix (not the exempt directory) is what
# keeps pre-existing neighbours such as components/ui/Button legal.
function Test-HitsNewSurface {
    param([string]$Resolved)
    if ($null -eq $Resolved) { return $null }
    $prefix = $scanRootRel + '/'
    if (-not $Resolved.StartsWith($prefix, [StringComparison]::OrdinalIgnoreCase)) { return $null }
    $suffix = $Resolved.Substring($prefix.Length)
    foreach ($needle in $newSurface) {
        if ($needle.EndsWith('/')) {
            if ($suffix.StartsWith($needle, [StringComparison]::OrdinalIgnoreCase)) { return $needle }
        } elseif ($suffix -eq $needle -or $suffix.StartsWith($needle + '.', [StringComparison]::OrdinalIgnoreCase)) {
            return $needle
        }
    }
    return $null
}

# Quote class built from char codes: a literal single/double/backtick set cannot be written
# inline in either PowerShell string form without an escape that changes the regex.
$qc = [string][char]39 + [string][char]34 + [string][char]96
$specRe = '(?:\bfrom|\bimport|\brequire)\s*\(?\s*[' + $qc + ']([^' + $qc + ']+)[' + $qc + ']'
$scanned = @(Get-ChildItem -Path $scanRoot -Recurse -File -Include '*.ts', '*.tsx' -ErrorAction SilentlyContinue)
$checked = 0
foreach ($f in $scanned) {
    $rel = Get-Rel $f.FullName
    if ($rel -match '(^|/)(node_modules|dist|out|build)/') { continue }
    $isExempt = $false
    foreach ($e in $exempt) {
        if ($rel -eq $e -or $rel.StartsWith(($e.TrimEnd('/') + '/'), [StringComparison]::OrdinalIgnoreCase)) {
            $isExempt = $true
            break
        }
    }
    if ($isExempt) { continue }
    $checked++
    $text = Get-Content -LiteralPath $f.FullName -Raw
    # static import, re-export, bare side-effect import, and dynamic import() alike
    foreach ($m in [regex]::Matches($text, $specRe)) {
        $spec = $m.Groups[1].Value
        $resolved = Resolve-Spec $rel $spec
        $hit = Test-HitsNewSurface $resolved
        if ($null -eq $hit) { continue }
        # The carve-out files are the single sanctioned doorway into the new surface, and only
        # for CARVE_OUT_ALLOWED_IMPORT -- any other new-surface reference from them still fails.
        if (($carveOut -contains $rel) -and
            ($resolved -eq $carveAllowed -or $resolved.StartsWith($carveAllowed + '.', [StringComparison]::OrdinalIgnoreCase))) {
            continue
        }
        Write-Error ('session-19 surface referenced outside its own directory: ' + $rel + ' -> ' + $spec + ' (' + $hit + ')')
        exit 1
    }
}

# 4. E2E identities unchanged, and the count still matches the declared baseline.
$baseTitles = @($base.e2eTitles)
$nowTitles = @(Get-E2eTitles)
$titleDiff = @(Compare-Object -ReferenceObject $baseTitles -DifferenceObject $nowTitles)
if ($titleDiff.Count -gt 0) {
    foreach ($d in $titleDiff) {
        Write-Error ('E2E identity changed (' + $d.SideIndicator + '): ' + $d.InputObject)
    }
    exit 1
}
$expected = [int]$sets.E2E_BASELINE_COUNT
if ($nowTitles.Count -ne $expected) {
    Write-Error ('E2E test count ' + $nowTitles.Count + ' != E2E_BASELINE_COUNT ' + $expected)
    exit 1
}

# 5. Every preserved testid is still registered.
$registry = Join-Path $repoRoot ([string]$sets.TESTID_REGISTRY)
if (-not (Test-Path -LiteralPath $registry)) {
    Write-Error ('missing TESTID_REGISTRY ' + $sets.TESTID_REGISTRY)
    exit 1
}
$registryText = Get-Content -LiteralPath $registry -Raw
foreach ($id in @($sets.PRESERVED_TESTIDS)) {
    if ($registryText -notlike ('*' + $id + '*')) {
        Write-Error ('lost preserved testid ' + $id)
        exit 1
    }
}

'PASS: PAGE_ISOLATION frozen=' + $nowFrozen.Count + ' carveout=' + $carveOut.Count + ' scanned=' + $checked + ' e2e=' + $nowTitles.Count + ' preserved=' + @($sets.PRESERVED_TESTIDS).Count
exit 0
