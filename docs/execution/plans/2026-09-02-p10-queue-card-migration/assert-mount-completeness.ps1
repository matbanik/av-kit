<#
.SYNOPSIS
  MOUNT_COMPLETENESS_RULE gate for the p10-queue-card-migration project.

.DESCRIPTION
  Successor to docs/execution/plans/2026-08-28-p10-queue-card-foundations/
  assert-page-isolation.ps1, which asserted the INVERSE contract (no page may
  mount the queue primitives). That gate is retired, not deleted; this one
  asserts the eight clauses of MOUNT_COMPLETENESS_RULE:

    1. each migrated page imports AND renders QueueList
    2. the retired table component no longer exists and nothing references it
    3. no @tanstack/react-table import remains in ui/src AND the dependency is
       absent from BOTH ui/package.json and ui/package-lock.json
    4. MOUNT_GATE_CLAUSE_4, per (page, retired-id, HOME) triple:
         (a) the retired id is gone from that page's tree
         (b) that home's testid is in THAT page's rendered tree
         (c) a test in THAT page's E2E spec PERFORMS the interaction
         (d) that same test asserts an observable OUTCOME afterwards
       Reorder homes must additionally assert the REORDER_WIRE_CONTRACT body.
    5. every PRESERVED_TESTIDS and NEW_TESTIDS id is registered in test-ids.ts
    6. no legacy STATUS_COLORS map survives in the queue features
    7. EMPTY_STATE_CONTRACT per page, with (c)+(d) applied to its action ids
    8. E2E_ASSERTION_CENSUS_RULE

  Every failure is ACCUMULATED and printed; the script exits 1 once at the end.
  First-failure exit would hide sibling-home defects, which is the one class
  MOUNT_GATE_PHASE_SCOPES was written to catch.

  -Scope obligates homes exactly as MOUNT_GATE_PHASE_SCOPES states. Homes whose
  MEU has not shipped print under a `PENDING (MEU-xx)` heading and do not fail
  the run -- except at -Scope all, where a non-empty PENDING list IS a failure.

.PARAMETER Scope
  convert (MEU-45 gate) | downloader (MEU-46 gate) | all (MEU-47 / phase exit).

.PARAMETER SelfTest
  Build hermetic fixtures and prove the gate fires. Every clause has at least
  one negative fixture, including the sibling-home case from round 2 Finding F4.

.PARAMETER Root
  Repo root to verify. Defaults to the four-levels-up real repo. -SelfTest
  drives this at fixture trees.

.PARAMETER CensusBefore
  The before-census receipt clause 8 compares against. Defaults to
  C:/Temp/av-kit/e2e-assertion-census-before.txt (E2E_ASSERTION_CENSUS_RULE).

.PARAMETER Only
  Restrict the run to these clause numbers. Diagnostics aid only -- a scoped
  run is not a gate pass.

.NOTES
  DISCLOSED DEVIATIONS (each is a narrowing forced by ground truth; all are
  reported in the MEU-45 handoff rather than silently applied):

  D1  Clause 6 is scoped to the queue features (features/converter,
      features/downloader, components/queue) instead of all of ui/src.
      TranscriptPage and TTSPage keep their own STATUS_COLORS maps, which
      AC-43.2 and AC-21.18 pin and which no Phase 10 row schedules for removal.

  D2  Clause 7's per-page ABSENCE half cannot be decided by scanning the
      rendered tree: QueueList is shared, so the literal `queue-empty-dropzone`
      is reachable from both pages. It is decided at the page's own props
      instead -- the converter must pass onBrowse/onDropFiles and must not pass
      emptyState; the downloader must pass emptyState carrying the invite ids
      and must not pass onBrowse/onDropFiles. That is the actual switch
      QueueList branches on (QueueList.tsx `acceptsFiles`).

  D3  Clause 8's case floor uses E2E_STATIC_CASE_FLOOR, not E2E_BASELINE_COUNT.
      59 is a Playwright RUNTIME pass count; a static `test(` scan of the same
      commit yields 53. A static gate cannot reproduce 59, and comparing the
      two numbers would fail every run. The assertion-level floor -- the part
      E2E_ASSERTION_CENSUS_RULE calls binding -- is unchanged.

  D4  Clause 4(a) is evaluated against the page's reachable tree and its feature
      directory, not all of ui/src. The downloader's retired ids (`start-btn`,
      `up-btn`, ...) are generic and are still live controls on TranscriptPage
      and TTSPage, which Phase 10 does not touch. Repo-wide absence would
      demand migrating pages no build-plan row schedules. Out-of-scope files
      still holding the id are printed as an informational note.

  D5  -SelfTest Fixture B (a synthetic MEU-46/47 completion) is generated from
      the same HOME_SPEC table the gate reads. Its PASS therefore proves only
      self-consistency, never that a real MEU-46/47 would pass. It exists to
      give the -Scope all NEGATIVES a passing baseline to be mutated away from.
      Fixture A is the real tree and is the only non-synthetic positive.
#>
[CmdletBinding()]
param(
  [ValidateSet('convert', 'downloader', 'all')]
  [string]$Scope = 'all',
  [switch]$SelfTest,
  [string]$Root,
  [string]$CensusBefore,
  [int[]]$Only
)

$ErrorActionPreference = 'Stop'

# ---------------------------------------------------------------------------
# Quote plumbing. A PowerShell string literal cannot hold every quote form at
# once, so the character classes the regexes need are built from code points --
# the same trick assert-page-isolation.ps1 uses for its own scanners.
# ---------------------------------------------------------------------------
$SQ = [string][char]39   # '
$DQ = [string][char]34   # "
$BQ = [string][char]96   # `
$QC = '[' + $SQ + $DQ + $BQ + ']'
$IMPORT_RE = 'from\s+' + $QC + '(\.[^' + $SQ + $DQ + $BQ + ']+)' + $QC

# An OUTCOME is any matcher that inspects a value. Visibility/attachment
# matchers are deliberately excluded: clause 4(d) exists precisely to reject a
# control that renders (and is therefore visible) but is wired to nothing.
$OUTCOME_RE = '\.(toEqual|toStrictEqual|toHaveLength|toHaveCount|toHaveText|' +
  'toContainText|toHaveAccessibleName|toHaveValue|toBeFocused|toBeDisabled|' +
  'toBeEnabled|toHaveClass|toHaveAttribute|toBeGreaterThan|toBeTruthy|' +
  'toBeUndefined|toContain|toBe)\('

$PLAN_DIR = $PSScriptRoot
$SETS_PATH = Join-Path $PLAN_DIR 'named-sets.json'
if (-not (Test-Path -LiteralPath $SETS_PATH)) {
  Write-Host ('FATAL: named-sets.json not found at ' + $SETS_PATH)
  exit 2
}
$SETS = Get-Content -LiteralPath $SETS_PATH -Raw | ConvertFrom-Json

if ([string]::IsNullOrWhiteSpace($Root)) {
  $repoRoot = (Resolve-Path -LiteralPath (Join-Path $PLAN_DIR '../../../..')).Path
}
else {
  $repoRoot = (Resolve-Path -LiteralPath $Root).Path
}
if ([string]::IsNullOrWhiteSpace($CensusBefore)) {
  $CensusBefore = 'C:/Temp/av-kit/e2e-assertion-census-before.txt'
}

# ---------------------------------------------------------------------------
# Result accumulation
# ---------------------------------------------------------------------------
$script:Failures = New-Object System.Collections.Generic.List[string]
$script:PendingRows = New-Object System.Collections.Generic.List[string]
$script:Notes = New-Object System.Collections.Generic.List[string]
$script:Passes = 0

function Add-Failure {
  param([string]$Clause, [string]$Message)
  $script:Failures.Add('clause ' + $Clause + ': ' + $Message) | Out-Null
}

function Add-Pass {
  $script:Passes++
}

function Test-ClauseEnabled {
  param([int]$Number)
  if ($null -eq $Only -or $Only.Count -eq 0) { return $true }
  return ($Only -contains $Number)
}

# ---------------------------------------------------------------------------
# Filesystem helpers
# ---------------------------------------------------------------------------
function Get-Abs {
  param([string]$Rel)
  return (Join-Path $repoRoot $Rel)
}

function Read-Text {
  param([string]$Path)
  if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { return '' }
  return [System.IO.File]::ReadAllText($Path)
}

function Get-SourceFiles {
  param([string]$Dir)
  if (-not (Test-Path -LiteralPath $Dir -PathType Container)) { return @() }
  return @(Get-ChildItem -LiteralPath $Dir -Recurse -File |
    Where-Object { $_.Extension -eq '.ts' -or $_.Extension -eq '.tsx' })
}

function Get-Rel {
  param([string]$Path)
  $full = $Path
  if ($full.StartsWith($repoRoot)) { $full = $full.Substring($repoRoot.Length) }
  return $full.TrimStart([char]92, [char]47).Replace([char]92, [char]47)
}

<#
  Resolve a relative import specifier to a file on disk. Written with character
  codes rather than backslash literals: inside a single-quoted PowerShell string
  a backslash pair is two backslashes, which silently breaks path splitting.
#>
function Resolve-Spec {
  param([string]$FromFile, [string]$Spec)
  if (-not $Spec.StartsWith('.')) { return $null }
  $dir = Split-Path -Parent $FromFile
  $current = $dir
  foreach ($seg in $Spec.Split([char]47, [char]92)) {
    if ($seg -eq '' -or $seg -eq '.') { continue }
    if ($seg -eq '..') { $current = Split-Path -Parent $current; continue }
    $current = Join-Path $current $seg
  }
  $candidates = @(
    ($current + '.tsx'),
    ($current + '.ts'),
    (Join-Path $current 'index.tsx'),
    (Join-Path $current 'index.ts'),
    $current
  )
  foreach ($cand in $candidates) {
    if (Test-Path -LiteralPath $cand -PathType Leaf) {
      return (Resolve-Path -LiteralPath $cand).Path
    }
  }
  return $null
}

<#
  The page's RENDERED TREE: the page component plus the transitive closure of
  its relative imports. Clause 4(b) says "THAT page's rendered tree, not merely
  somewhere in ui/src", and this is what makes that distinction mechanical.
#>
function Get-ReachableTree {
  param([string]$Entry)
  $seen = @{}
  if (-not (Test-Path -LiteralPath $Entry -PathType Leaf)) { return $seen }
  $stack = New-Object System.Collections.Stack
  $stack.Push((Resolve-Path -LiteralPath $Entry).Path) | Out-Null
  while ($stack.Count -gt 0) {
    $file = $stack.Pop()
    if ($seen.ContainsKey($file)) { continue }
    $text = Read-Text $file
    $seen[$file] = $text
    foreach ($m in [regex]::Matches($text, $IMPORT_RE)) {
      $target = Resolve-Spec -FromFile $file -Spec $m.Groups[1].Value
      if ($null -ne $target -and -not $seen.ContainsKey($target)) {
        $stack.Push($target) | Out-Null
      }
    }
  }
  return $seen
}

function Test-InTree {
  param([hashtable]$Tree, [string]$Pattern)
  foreach ($text in $Tree.Values) {
    if ([regex]::IsMatch($text, $Pattern)) { return $true }
  }
  return $false
}

# ---------------------------------------------------------------------------
# E2E spec parsing
# ---------------------------------------------------------------------------
<#
  Split a Playwright spec into its test cases. Clause 4(c)+(d) are evaluated
  inside ONE case ("at least one test ... and that same test"), so the block is
  the unit; a click in one case and an assertion in another must not combine
  into a false pass.
#>
function Get-TestBlocks {
  param([string]$Path)
  $blocks = New-Object System.Collections.Generic.List[object]
  if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { return @() }
  $lines = (Read-Text $Path) -split "`r?`n"
  $current = $null
  $titleRe = '^\s*test(\.\w+)?\(\s*' + $QC + '([^' + $SQ + $DQ + $BQ + ']+)' + $QC
  foreach ($line in $lines) {
    $m = [regex]::Match($line, $titleRe)
    if ($m.Success) {
      $current = [pscustomobject]@{
        Title = $m.Groups[2].Value
        Lines = (New-Object System.Collections.Generic.List[string])
      }
      $blocks.Add($current) | Out-Null
    }
    if ($null -ne $current) { $current.Lines.Add($line) | Out-Null }
  }
  $out = @()
  foreach ($b in $blocks) {
    $out += [pscustomobject]@{ Title = $b.Title; Body = ($b.Lines -join "`n") }
  }
  return $out
}

<#
  Clause 4(c)+(d) for one home against one spec. Returns a result object rather
  than writing failures directly, so clause 7 can reuse the identical check for
  its own action ids ("a present-but-no-op Browse or invite button fails").
#>
function Test-PerformAndOutcome {
  param(
    [object[]]$Blocks,
    [string]$Perform,
    [string[]]$Require,
    [string]$Wire
  )
  $performedIn = $null
  $outcomeIn = $null
  $wireIn = $null
  foreach ($block in $Blocks) {
    $m = [regex]::Match($block.Body, $Perform)
    if (-not $m.Success) { continue }
    $ok = $true
    foreach ($needle in @($Require)) {
      if ([string]::IsNullOrEmpty($needle)) { continue }
      if (-not [regex]::IsMatch($block.Body, $needle)) { $ok = $false }
    }
    if (-not $ok) { continue }
    if ($null -eq $performedIn) { $performedIn = $block.Title }
    $tail = $block.Body.Substring($m.Index + $m.Length)
    if (-not [regex]::IsMatch($tail, $OUTCOME_RE)) { continue }
    if ($null -eq $outcomeIn) { $outcomeIn = $block.Title }
    if (-not [string]::IsNullOrEmpty($Wire)) {
      if (-not [regex]::IsMatch($block.Body, $Wire)) { continue }
      $wireIn = $block.Title
    }
    break
  }
  return [pscustomobject]@{
    Performed = ($null -ne $performedIn)
    Outcome   = ($null -ne $outcomeIn)
    Wired     = ($null -ne $wireIn)
    Where     = $outcomeIn
  }
}

# ---------------------------------------------------------------------------
# Page table
# ---------------------------------------------------------------------------
$PAGES = @(
  [pscustomobject]@{
    Key               = 'converter'
    Meu               = 'MEU-45'
    ScopeName         = 'convert'
    Page              = 'ui/src/renderer/src/features/converter/ConvertPage.tsx'
    FeatureDir        = 'ui/src/renderer/src/features/converter'
    RetiredTable      = 'ui/src/renderer/src/features/converter/ConvertQueueTable.tsx'
    RetiredSymbol     = 'ConvertQueueTable'
    Spec              = 'ui/tests/e2e/convert-queue.test.ts'
    EmptyOwnRequired  = @('onBrowse=', 'onDropFiles=')
    EmptyOwnForbidden = @('emptyState=', 'queue-empty-invite')
    EmptyContainers   = @('queue-empty-dropzone', 'queue-drop-strip')
    EmptyActions      = @('queue-empty-browse')
  },
  [pscustomobject]@{
    Key               = 'downloader'
    Meu               = 'MEU-46'
    ScopeName         = 'downloader'
    Page              = 'ui/src/renderer/src/features/downloader/DownloaderPage.tsx'
    FeatureDir        = 'ui/src/renderer/src/features/downloader'
    RetiredTable      = 'ui/src/renderer/src/features/downloader/DownloadQueueTable.tsx'
    RetiredSymbol     = 'DownloadQueueTable'
    Spec              = 'ui/tests/e2e/download-queue.test.ts'
    EmptyOwnRequired  = @('emptyState=', 'queue-empty-invite', 'queue-empty-invite-action')
    EmptyOwnForbidden = @('onBrowse=', 'onDropFiles=')
    EmptyContainers   = @('queue-empty-invite')
    EmptyActions      = @('queue-empty-invite-action')
  }
)

# ---------------------------------------------------------------------------
# HOME_SPEC -- keyed on the verbatim `home` strings of RETIRED_TOOLBAR_CONTROLS.
#
#   Tree        regexes that must appear in the page's reachable tree  (4b)
#   Perform     regex proving the interaction is performed             (4c)
#   Require     literals that must sit in the SAME test case
#   Wire        REORDER_WIRE_CONTRACT body marker, reorder homes only
#   TreeSample  source snippet that satisfies Tree      (fixture generation)
#   Sample      spec snippet that satisfies Perform+outcome(+Wire)
#
# TreeSample/Sample keep -SelfTest's Fixture B honest about WHAT it is: a
# generated tree, not an implementation (deviation D5).
# ---------------------------------------------------------------------------
$K = $QC   # kebab ids are matched quote-delimited so `move-top` does not match
           # inside `bulk-move-top`.

function New-Home {
  param(
    [string[]]$Tree,
    [string]$Perform,
    [string[]]$Require = @(),   # regexes, all of which must match the SAME case
    [string]$Wire = '',
    [string]$TreeSample = '',
    [string]$Sample = ''
  )
  return [pscustomobject]@{
    Tree = $Tree; Perform = $Perform; Require = $Require; Wire = $Wire
    TreeSample = $TreeSample; Sample = $Sample
  }
}

function New-ToolbarHome {
  param([string]$Id)
  return New-Home -Tree @([regex]::Escape($Id)) `
    -Perform ([regex]::Escape($Id) + '[^\n]{0,200}?\.click\(') `
    -TreeSample ('      <button data-testid="' + $Id + '">' + $Id + '</button>') `
    -Sample (@(
      ('  await page.getByTestId(' + $SQ + $Id + $SQ + ').click()'),
      '  expect(await seam.calls()).toHaveLength(1)'
    ) -join "`n")
}

function New-KebabHome {
  param([string]$Action, [string]$Wire = '')
  $sample = @(
    ('  const menu = await openKebab(page, ' + $SQ + 'job-1' + $SQ + ')'),
    ('  await menu.locator(' + $SQ + '[data-menu-action="' + $Action + '"]' + $SQ + ').click()'),
    '  const after = await seam.calls()',
    ('  expect(after[0].body).toEqual({ job_ids: [' + $SQ + 'job-1' + $SQ + '] })')
  ) -join "`n"
  return New-Home -Tree @('data-menu-action', ($K + [regex]::Escape($Action) + $K)) `
    -Perform ('data-menu-action="' + [regex]::Escape($Action) + '"[^\n]{0,200}?\.click\(') `
    -Require @('queue-card-kebab|openKebab\(') -Wire $Wire `
    -TreeSample ('      <button data-menu-action="' + $Action + '">' + $Action + '</button>') `
    -Sample $sample
}

function New-PrimaryHome {
  param([string]$Label, [string]$Path)
  $sample = @(
    ('  const action = rowOf(' + $SQ + 'job-1' + $SQ + ').getByTestId(' + $SQ + 'queue-card-primary-action' + $SQ + ')'),
    ('  await expect(action).toHaveText(' + $SQ + $Label + $SQ + ')'),
    '  await action.click()',
    ('  expect(await seam.callsTo(' + $SQ + $Path + $SQ + ', ' + $SQ + 'POST' + $SQ + ')).toHaveLength(1)')
  ) -join "`n"
  return New-Home -Tree @('queue-card-primary-action', ($K + [regex]::Escape($Label) + $K)) `
    -Perform ([regex]::Escape($Label) + '[\s\S]{0,400}?\.click\(') `
    -Require @('queue-card-primary-action') `
    -TreeSample ('      <button data-testid="queue-card-primary-action">' + $SQ + $Label + $SQ + '</button>') `
    -Sample $sample
}

function New-AltArrowHome {
  param([string]$Key)
  $sample = @(
    ('  const card = rowOf(' + $SQ + 'job-1' + $SQ + ')'),
    ('  await card.press(' + $SQ + 'Alt+' + $Key + $SQ + ')'),
    '  const moved = await seam.calls()',
    ('  expect(moved[0].body).toEqual({ job_ids: [' + $SQ + 'job-1' + $SQ + '] })')
  ) -join "`n"
  return New-Home -Tree @('altKey', [regex]::Escape($Key)) `
    -Perform ('Alt\+' + [regex]::Escape($Key)) -Wire 'job_ids' `
    -TreeSample ('      // altKey + ' + $Key + ' reorder shortcut') `
    -Sample $sample
}

$HOME_SPEC = @{}
$HOME_SPEC['queue-toolbar-start'] = New-ToolbarHome 'queue-toolbar-start'
$HOME_SPEC['queue-toolbar-pause (half of the pause-resume toggle)'] = New-ToolbarHome 'queue-toolbar-pause'
$HOME_SPEC['queue-toolbar-resume (half of the pause-resume toggle)'] = New-ToolbarHome 'queue-toolbar-resume'
$HOME_SPEC['queue-toolbar-overflow -> queue-toolbar-clear-all'] = New-Home `
  -Tree @('queue-toolbar-overflow', 'queue-toolbar-clear-all') `
  -Perform ('queue-toolbar-overflow[^\n]{0,200}?\.click\([\s\S]{0,600}?queue-toolbar-clear-all[^\n]{0,200}?\.click\(') `
  -TreeSample (@(
    '      <button data-testid="queue-toolbar-overflow">More</button>',
    '      <button data-testid="queue-toolbar-clear-all">Clear all</button>'
  ) -join "`n") `
  -Sample (@(
    ('  await page.getByTestId(' + $SQ + 'queue-toolbar-overflow' + $SQ + ').click()'),
    ('  await page.getByTestId(' + $SQ + 'queue-toolbar-clear-all' + $SQ + ').click()'),
    ('  await expect(page.getByTestId(' + $SQ + 'confirm-modal' + $SQ + ')).toHaveCount(1)')
  ) -join "`n")

$CANCEL_LABEL = $SETS.CANCEL_CONTROL_LABEL.value
$HOME_SPEC['in-flight card primary action CANCEL_CONTROL_LABEL'] = New-Home `
  -Tree @('queue-card-primary-action', ($K + [regex]::Escape($CANCEL_LABEL) + $K)) `
  -Perform ([regex]::Escape($CANCEL_LABEL) + '[\s\S]{0,400}?\.click\(') `
  -Require @('queue-card-primary-action') `
  -TreeSample ('      <button data-testid="queue-card-primary-action">' + $SQ + $CANCEL_LABEL + $SQ + '</button>') `
  -Sample (@(
    ('  const cancel = rowOf(' + $SQ + 'job-2' + $SQ + ').getByTestId(' + $SQ + 'queue-card-primary-action' + $SQ + ')'),
    ('  await expect(cancel).toHaveAccessibleName(' + $SQ + $CANCEL_LABEL + $SQ + ')'),
    '  await cancel.click()',
    '  expect(await seam.calls()).toHaveLength(1)'
  ) -join "`n")

$HOME_SPEC['card primary action Retry'] = New-PrimaryHome 'Retry' '/downloads/job-1/reset'
$HOME_SPEC['card primary action Open file on a Done row'] = New-PrimaryHome 'Open file' '/downloads/job-1/open'
$HOME_SPEC['kebab move-up'] = New-KebabHome 'move-up' 'job_ids'
$HOME_SPEC['kebab move-down'] = New-KebabHome 'move-down' 'job_ids'
$HOME_SPEC['kebab move-top'] = New-KebabHome 'move-top' 'job_ids'
$HOME_SPEC['kebab move-bottom'] = New-KebabHome 'move-bottom' 'job_ids'
$HOME_SPEC['kebab remove'] = New-KebabHome 'remove'
$HOME_SPEC['kebab open-file'] = New-KebabHome 'open-file'
$HOME_SPEC['kebab open-folder'] = New-KebabHome 'open-folder'
$HOME_SPEC['Alt+ArrowUp on a focused card'] = New-AltArrowHome 'ArrowUp'
$HOME_SPEC['Alt+ArrowDown on a focused card'] = New-AltArrowHome 'ArrowDown'
$HOME_SPEC['bulk-move-top'] = New-Home -Tree @('bulk-move-top') `
  -Perform 'bulk-move-top[^\n]{0,200}?\.click\(' -Wire 'job_ids' `
  -TreeSample '      <button data-testid="bulk-move-top">Move to top</button>' `
  -Sample (@(
    ('  await page.getByTestId(' + $SQ + 'bulk-move-top' + $SQ + ').click()'),
    '  const bulkTop = await seam.calls()',
    ('  expect(bulkTop[0].body).toEqual({ job_ids: [' + $SQ + 'job-1' + $SQ + '] })')
  ) -join "`n")
$HOME_SPEC['bulk-move-bottom'] = New-Home -Tree @('bulk-move-bottom') `
  -Perform 'bulk-move-bottom[^\n]{0,200}?\.click\(' -Wire 'job_ids' `
  -TreeSample '      <button data-testid="bulk-move-bottom">Move to bottom</button>' `
  -Sample (@(
    ('  await page.getByTestId(' + $SQ + 'bulk-move-bottom' + $SQ + ').click()'),
    '  const bulkBottom = await seam.calls()',
    ('  expect(bulkBottom[0].body).toEqual({ job_ids: [' + $SQ + 'job-1' + $SQ + '] })')
  ) -join "`n")
$HOME_SPEC['bulk-retry'] = New-Home -Tree @('bulk-retry') `
  -Perform 'bulk-retry[^\n]{0,200}?\.click\(' `
  -TreeSample '      <button data-testid="bulk-retry">Retry</button>' `
  -Sample (@(
    ('  await page.getByTestId(' + $SQ + 'bulk-retry' + $SQ + ').click()'),
    '  expect(await seam.calls()).toHaveLength(1)'
  ) -join "`n")
$HOME_SPEC['bulk-remove'] = New-Home -Tree @('bulk-remove') `
  -Perform 'bulk-remove[^\n]{0,200}?\.click\(' `
  -TreeSample '      <button data-testid="bulk-remove">Remove</button>' `
  -Sample (@(
    ('  await page.getByTestId(' + $SQ + 'bulk-remove' + $SQ + ').click()'),
    '  expect(await seam.calls()).toHaveLength(1)'
  ) -join "`n")

# ---------------------------------------------------------------------------
# Scope -> obligated MEUs (MOUNT_GATE_PHASE_SCOPES)
# ---------------------------------------------------------------------------
$OBLIGATED = switch ($Scope) {
  'convert' { @('MEU-45') }
  'downloader' { @('MEU-46') }
  'all' { @('MEU-45', 'MEU-46', 'MEU-47') }
}

function Test-Obligated {
  param([string]$Meu)
  return ($OBLIGATED -contains $Meu)
}

# ===========================================================================
# VERIFY
# ===========================================================================
function Invoke-Verify {
  $retired = $SETS.RETIRED_TOOLBAR_CONTROLS.value

  Write-Host ('MOUNT_COMPLETENESS_RULE gate  scope=' + $Scope)
  Write-Host ('  root:   ' + $repoRoot)
  Write-Host ('  sets:   ' + (Get-Rel $SETS_PATH))
  Write-Host ('  obligated MEUs: ' + ($OBLIGATED -join ', '))
  Write-Host ('-' * 74)

  $trees = @{}
  foreach ($page in $PAGES) {
    $trees[$page.Key] = Get-ReachableTree (Get-Abs $page.Page)
  }

  # -- clause 1: page imports AND renders QueueList -------------------------
  if (Test-ClauseEnabled 1) {
    foreach ($page in $PAGES) {
      if (-not (Test-Obligated $page.Meu)) {
        $script:PendingRows.Add(($page.Meu + '  clause 1  ' + $page.Key + ' mounts QueueList')) | Out-Null
        continue
      }
      $src = Read-Text (Get-Abs $page.Page)
      if ($src -eq '') {
        Add-Failure '1' ($page.Key + ': page not found at ' + $page.Page)
        continue
      }
      if (-not [regex]::IsMatch($src, 'import\s*\{[^}]*\bQueueList\b[^}]*\}\s*' + $IMPORT_RE)) {
        Add-Failure '1' ($page.Key + ': ' + $page.Page + ' does not import QueueList')
      }
      else { Add-Pass }
      if (-not [regex]::IsMatch($src, '<QueueList[\s/>]')) {
        Add-Failure '1' ($page.Key + ': ' + $page.Page + ' does not render <QueueList')
      }
      else { Add-Pass }
    }
  }

  # -- clause 2: retired table gone, nothing references it ------------------
  if (Test-ClauseEnabled 2) {
    foreach ($page in $PAGES) {
      if (-not (Test-Obligated $page.Meu)) {
        $script:PendingRows.Add(($page.Meu + '  clause 2  ' + $page.RetiredSymbol + ' deleted')) | Out-Null
        continue
      }
      if (Test-Path -LiteralPath (Get-Abs $page.RetiredTable) -PathType Leaf) {
        Add-Failure '2' ($page.RetiredTable + ' still exists')
      }
      else { Add-Pass }
      $referers = @()
      foreach ($file in (Get-SourceFiles (Get-Abs 'ui/src')) + (Get-SourceFiles (Get-Abs 'ui/tests/e2e'))) {
        if ((Read-Text $file.FullName) -match ('\b' + $page.RetiredSymbol + '\b')) {
          $referers += (Get-Rel $file.FullName)
        }
      }
      if ($referers.Count -gt 0) {
        Add-Failure '2' ($page.RetiredSymbol + ' still referenced by: ' + ($referers -join ', '))
      }
      else { Add-Pass }
    }
  }

  # -- clause 3: @tanstack/react-table gone from source AND both manifests --
  if (Test-ClauseEnabled 3) {
    if (-not (Test-Obligated 'MEU-46')) {
      $script:PendingRows.Add('MEU-46  clause 3  @tanstack/react-table removed') | Out-Null
    }
    else {
      $offenders = @()
      foreach ($file in (Get-SourceFiles (Get-Abs 'ui/src'))) {
        if ((Read-Text $file.FullName).Contains('@tanstack/react-table')) {
          $offenders += (Get-Rel $file.FullName)
        }
      }
      foreach ($manifest in @('ui/package.json', 'ui/package-lock.json')) {
        $text = Read-Text (Get-Abs $manifest)
        if ($text -eq '') {
          Add-Failure '3' ($manifest + ' not found -- clause 3 requires BOTH manifests')
          continue
        }
        if ($text.Contains('@tanstack/react-table')) { $offenders += $manifest }
      }
      if ($offenders.Count -gt 0) {
        Add-Failure '3' ('@tanstack/react-table survives in: ' + ($offenders -join ', '))
      }
      else { Add-Pass }
    }
  }

  # -- clause 4: MOUNT_GATE_CLAUSE_4, per (page, retired-id, HOME) ----------
  if (Test-ClauseEnabled 4) {
    foreach ($page in $PAGES) {
      $tree = $trees[$page.Key]
      $blocks = Get-TestBlocks (Get-Abs $page.Spec)
      $subMap = $retired.($page.Key)
      if ($null -eq $subMap) {
        Add-Failure '4' ('RETIRED_TOOLBAR_CONTROLS has no sub-map for ' + $page.Key)
        continue
      }
      foreach ($id in ($subMap.PSObject.Properties.Name | Sort-Object)) {

        # (a) -- once per retired id, gated on the PAGE's migration MEU.
        if (Test-Obligated $page.Meu) {
          $hits = @()
          foreach ($kv in $tree.GetEnumerator()) {
            if ($kv.Value.Contains($id)) { $hits += (Get-Rel $kv.Key) }
          }
          foreach ($file in (Get-SourceFiles (Get-Abs $page.FeatureDir))) {
            if ((Read-Text $file.FullName).Contains($id)) {
              $rel = Get-Rel $file.FullName
              if ($hits -notcontains $rel) { $hits += $rel }
            }
          }
          if ($hits.Count -gt 0) {
            Add-Failure '4(a)' ($page.Key + '/' + $id + ' still present in: ' + ($hits -join ', '))
          }
          else { Add-Pass }
          # Deviation D4: report, do not fail, on out-of-scope pages.
          $outside = @()
          foreach ($file in (Get-SourceFiles (Get-Abs 'ui/src'))) {
            $rel = Get-Rel $file.FullName
            if ($rel.StartsWith($page.FeatureDir)) { continue }
            if ($tree.ContainsKey($file.FullName)) { continue }
            if ((Read-Text $file.FullName).Contains($id)) { $outside += $rel }
          }
          if ($outside.Count -gt 0) {
            $script:Notes.Add(('4(a) D4  ' + $id + ' also lives outside ' + $page.Key +
              ' (out of Phase 10 scope): ' + ($outside -join ', '))) | Out-Null
          }
        }
        else {
          $script:PendingRows.Add(($page.Meu + '  clause 4(a)  ' + $page.Key + '/' + $id)) | Out-Null
        }

        # (b)(c)(d) -- per HOME.
        foreach ($hRow in $subMap.$id) {
          $label = $page.Key + '/' + $id + ' -> ' + $hRow.home
          if (-not (Test-Obligated $hRow.meu)) {
            $script:PendingRows.Add(($hRow.meu + '  clause 4(b-d)  ' + $label)) | Out-Null
            continue
          }
          $spec = $HOME_SPEC[$hRow.home]
          if ($null -eq $spec) {
            Add-Failure '4' ('no HOME_SPEC entry for home ' + $SQ + $hRow.home + $SQ +
              ' -- the gate cannot verify what it cannot describe')
            continue
          }
          $missing = @()
          foreach ($marker in $spec.Tree) {
            if (-not (Test-InTree $tree $marker)) { $missing += $marker }
          }
          if ($missing.Count -gt 0) {
            Add-Failure '4(b)' ($label + ': absent from the page tree (' + ($missing -join ' | ') + ')')
          }
          else { Add-Pass }

          $r = Test-PerformAndOutcome -Blocks $blocks -Perform $spec.Perform `
            -Require $spec.Require -Wire $spec.Wire
          if (-not $r.Performed) {
            Add-Failure '4(c)' ($label + ': no test in ' + $page.Spec + ' performs the interaction')
          }
          elseif (-not $r.Outcome) {
            Add-Failure '4(d)' ($label + ': performed but no outcome asserted afterwards in ' + $page.Spec)
          }
          elseif (-not [string]::IsNullOrEmpty($spec.Wire) -and -not $r.Wired) {
            Add-Failure '4(d)' ($label + ': REORDER_WIRE_CONTRACT body (' + $spec.Wire +
              ') not asserted in the same test')
          }
          else { Add-Pass }
        }
      }
    }
  }

  # -- clause 5: testid registration ---------------------------------------
  if (Test-ClauseEnabled 5) {
    $idsPath = Get-Abs 'ui/tests/e2e/test-ids.ts'
    $idsText = Read-Text $idsPath
    if ($idsText -eq '') {
      Add-Failure '5' 'ui/tests/e2e/test-ids.ts not found'
    }
    else {
      $unregistered = @()
      foreach ($id in @($SETS.PRESERVED_TESTIDS.value) + @($SETS.NEW_TESTIDS.value)) {
        if (-not $idsText.Contains($id)) { $unregistered += $id }
      }
      if ($unregistered.Count -gt 0) {
        Add-Failure '5' ('unregistered in test-ids.ts: ' + ($unregistered -join ', '))
      }
      else { Add-Pass }
    }
  }

  # -- clause 6: no legacy STATUS_COLORS in the queue features (D1) --------
  if (Test-ClauseEnabled 6) {
    $dirs = @()
    foreach ($page in $PAGES) {
      if (Test-Obligated $page.Meu) { $dirs += $page.FeatureDir }
      else { $script:PendingRows.Add(($page.Meu + '  clause 6  STATUS_COLORS gone from ' + $page.FeatureDir)) | Out-Null }
    }
    if ((Test-Obligated 'MEU-45')) { $dirs += 'ui/src/renderer/src/components/queue' }
    $offenders = @()
    foreach ($dir in $dirs) {
      foreach ($file in (Get-SourceFiles (Get-Abs $dir))) {
        if ([regex]::IsMatch((Read-Text $file.FullName), '\bSTATUS_COLORS\b')) {
          $offenders += (Get-Rel $file.FullName)
        }
      }
    }
    if ($offenders.Count -gt 0) {
      Add-Failure '6' ('legacy STATUS_COLORS map survives in: ' + ($offenders -join ', '))
    }
    elseif ($dirs.Count -gt 0) { Add-Pass }
  }

  # -- clause 7: EMPTY_STATE_CONTRACT, per page ----------------------------
  if (Test-ClauseEnabled 7) {
    foreach ($page in $PAGES) {
      if (-not (Test-Obligated $page.Meu)) {
        $script:PendingRows.Add(($page.Meu + '  clause 7  EMPTY_STATE_CONTRACT ' + $page.Key)) | Out-Null
        continue
      }
      $src = Read-Text (Get-Abs $page.Page)
      # D2: the branch QueueList takes is decided by the props the page passes.
      foreach ($needle in $page.EmptyOwnRequired) {
        if (-not $src.Contains($needle)) {
          Add-Failure '7' ($page.Key + ': ' + $page.Page + ' must pass ' + $needle +
            ' (EMPTY_STATE_CONTRACT)')
        }
        else { Add-Pass }
      }
      foreach ($needle in $page.EmptyOwnForbidden) {
        if ($src.Contains($needle)) {
          Add-Failure '7' ($page.Key + ': ' + $page.Page + ' must NOT carry ' + $needle +
            ' (EMPTY_STATE_CONTRACT is per page)')
        }
        else { Add-Pass }
      }
      $tree = $trees[$page.Key]
      $blocks = Get-TestBlocks (Get-Abs $page.Spec)
      foreach ($id in ($page.EmptyContainers + $page.EmptyActions)) {
        if (-not (Test-InTree $tree ([regex]::Escape($id)))) {
          Add-Failure '7' ($page.Key + ': ' + $id + ' absent from the page tree')
        }
        else { Add-Pass }
      }
      # Action ids take clause 4 (c)+(d) verbatim: a no-op Browse fails.
      foreach ($id in $page.EmptyActions) {
        $r = Test-PerformAndOutcome -Blocks $blocks `
          -Perform ([regex]::Escape($id) + '[^\n]{0,200}?\.click\(') -Require @()
        if (-not $r.Performed) {
          Add-Failure '7' ($page.Key + ': ' + $id + ' is never clicked in ' + $page.Spec +
            ' -- a present-but-no-op invitation fails the clause')
        }
        elseif (-not $r.Outcome) {
          Add-Failure '7' ($page.Key + ': ' + $id + ' is clicked but asserts no outcome in ' + $page.Spec)
        }
        else { Add-Pass }
      }
      # Container ids must at least live inside a case that interacts and asserts.
      foreach ($id in $page.EmptyContainers) {
        $covered = $false
        foreach ($block in $blocks) {
          if (-not $block.Body.Contains($id)) { continue }
          if (-not [regex]::IsMatch($block.Body, '\.(click|press)\(')) { continue }
          if (-not [regex]::IsMatch($block.Body, $OUTCOME_RE)) { continue }
          $covered = $true
          break
        }
        if (-not $covered) {
          Add-Failure '7' ($page.Key + ': ' + $id + ' has no interacting, outcome-asserting test in ' + $page.Spec)
        }
        else { Add-Pass }
      }
    }
  }

  # -- clause 8: E2E_ASSERTION_CENSUS_RULE ---------------------------------
  if (Test-ClauseEnabled 8) { Invoke-Clause8 }

  # -- report ---------------------------------------------------------------
  Write-Host ''
  if ($script:Notes.Count -gt 0) {
    Write-Host 'NOTES (informational, non-blocking)'
    foreach ($n in $script:Notes) { Write-Host ('  ' + $n) }
    Write-Host ''
  }
  Write-Host ('PENDING (' + $script:PendingRows.Count + ' obligations not yet owed at scope=' + $Scope + ')')
  if ($script:PendingRows.Count -eq 0) {
    Write-Host '  <none>'
  }
  else {
    foreach ($row in ($script:PendingRows | Sort-Object -Unique)) {
      $meu = ($row -split '\s+')[0]
      Write-Host ('  PENDING (' + $meu + ')  ' + $row.Substring($meu.Length).Trim())
    }
    if ($Scope -eq 'all') {
      Add-Failure 'phase' ('scope=all obligates every home; the PENDING list must be empty but holds ' +
        $script:PendingRows.Count + ' rows')
    }
  }

  Write-Host ''
  Write-Host ('checks passed: ' + $script:Passes)
  if ($script:Failures.Count -eq 0) {
    Write-Host ('GATE PASS  scope=' + $Scope)
    return 0
  }
  Write-Host ('FAILURES (' + $script:Failures.Count + ')')
  foreach ($f in $script:Failures) { Write-Host ('  FAIL ' + $f) }
  Write-Host ('GATE FAIL  scope=' + $Scope)
  return 1
}

# ---------------------------------------------------------------------------
# Clause 8 -- census comparison
# ---------------------------------------------------------------------------
function Read-Census {
  param([string]$Path)
  $page = $null
  $totals = 0
  $caps = @{}
  $retiredCov = @{}
  foreach ($line in ((Read-Text $Path) -split "`r?`n")) {
    $m = [regex]::Match($line, '^FILE .*\[page=(\w+)\]')
    if ($m.Success) {
      $page = $m.Groups[1].Value
      if (-not $caps.ContainsKey($page)) { $caps[$page] = @{} }
      if (-not $retiredCov.ContainsKey($page)) { $retiredCov[$page] = @{} }
      continue
    }
    $m = [regex]::Match($line, '^\s+capability page:(\S+).*?(\d+)\s*$')
    if ($m.Success -and $null -ne $page) {
      $id = $m.Groups[1].Value
      $caps[$page][$id] = [int]$caps[$page][$id] + [int]$m.Groups[2].Value
      continue
    }
    $m = [regex]::Match($line, '^\s{4}(\S+)\s+assertions=(\d+)\s+homes:')
    if ($m.Success -and $null -ne $page) {
      $retiredCov[$page][$m.Groups[1].Value] = [int]$m.Groups[2].Value
      continue
    }
    $m = [regex]::Match($line, '^TOTAL expect\(\) assertions in the two queue specs: (\d+)')
    if ($m.Success) { $totals = [int]$m.Groups[1].Value }
  }
  return [pscustomobject]@{ Total = $totals; Caps = $caps; Retired = $retiredCov }
}

function Invoke-Clause8 {
  $generator = Join-Path $PLAN_DIR 'e2e-assertion-census.py'
  if (-not (Test-Path -LiteralPath $generator -PathType Leaf)) {
    Add-Failure '8' ('census generator missing: ' + $generator)
    return
  }
  if (-not (Test-Path -LiteralPath $CensusBefore -PathType Leaf)) {
    Add-Failure '8' ('before-census receipt missing: ' + $CensusBefore +
      ' -- E2E_ASSERTION_CENSUS_RULE requires it be captured before the first rewrite')
    return
  }
  $afterPath = Join-Path ([System.IO.Path]::GetTempPath()) ('av-kit-census-after-' + [guid]::NewGuid().ToString('N') + '.txt')
  $env:PYTHONIOENCODING = 'utf-8'
  $null = & python $generator $afterPath $repoRoot 2>&1
  if ($LASTEXITCODE -ne 0) {
    Add-Failure '8' ('census generator failed (exit ' + $LASTEXITCODE + ') for root ' + $repoRoot)
    return
  }
  $before = Read-Census $CensusBefore
  $after = Read-Census $afterPath
  Remove-Item -LiteralPath $afterPath -Force -ErrorAction SilentlyContinue

  if ($after.Total -lt $before.Total) {
    Add-Failure '8' ('assertion count fell: ' + $before.Total + ' -> ' + $after.Total)
  }
  else { Add-Pass }

  # Static case floor (deviation D3).
  $floorSet = $SETS.E2E_STATIC_CASE_FLOOR
  if ($null -eq $floorSet) {
    Add-Failure '8' 'E2E_STATIC_CASE_FLOOR is not defined in named-sets.json'
  }
  else {
    $cases = 0
    $e2eDir = Get-Abs 'ui/tests/e2e'
    if (Test-Path -LiteralPath $e2eDir -PathType Container) {
      foreach ($file in (Get-ChildItem -LiteralPath $e2eDir -File -Filter '*.test.ts')) {
        $cases += [regex]::Matches((Read-Text $file.FullName), '(?m)^\s*test(\.\w+)?\(').Count
      }
    }
    if ($cases -lt [int]$floorSet.value) {
      Add-Failure '8' ('E2E test-case count ' + $cases + ' fell below E2E_STATIC_CASE_FLOOR ' + $floorSet.value)
    }
    else { Add-Pass }
  }

  $retiredMap = $SETS.RETIRED_TESTIDS.value
  foreach ($page in $PAGES) {
    $key = $page.Key
    if (-not $before.Caps.ContainsKey($key)) { continue }

    # Page-level capabilities may not be softened to zero. A retired id is
    # exempt only when its RETIRED_TESTIDS successor carries the assertions.
    foreach ($id in $before.Caps[$key].Keys) {
      if ([int]$before.Caps[$key][$id] -le 0) { continue }
      $afterCount = 0
      if ($after.Caps.ContainsKey($key) -and $after.Caps[$key].ContainsKey($id)) {
        $afterCount = [int]$after.Caps[$key][$id]
      }
      if ($afterCount -gt 0) { Add-Pass; continue }
      $successor = $retiredMap.$id
      if ($null -ne $successor -and $after.Caps.ContainsKey($key) -and
        $after.Caps[$key].ContainsKey($successor) -and [int]$after.Caps[$key][$successor] -gt 0) {
        $script:Notes.Add(('8  ' + $key + ' page capability ' + $id + ' moved to its RETIRED_TESTIDS successor ' +
            $successor)) | Out-Null
        Add-Pass
        continue
      }
      Add-Failure '8' ($key + ': page capability ' + $id + ' fell from ' +
        $before.Caps[$key][$id] + ' assertions to zero with no successor')
    }

    # A retired CONTROL falling to zero is expected once its page migrates --
    # the id text is gone by clause 4(a). It is acceptable ONLY when clause 4
    # actually proved every home for that id in this run; otherwise coverage
    # was simply dropped.
    if (-not $before.Retired.ContainsKey($key)) { continue }
    # The zero-assertion exemption is earned by clause 4 proving the homes, so this
    # check cannot run on a page whose migration MEU this scope has not obligated --
    # there, the retired controls are PENDING, not lost. -Scope all obligates both
    # pages, which is where a genuinely dropped control is caught.
    if (-not (Test-Obligated $page.Meu)) {
      $script:PendingRows.Add(($page.Meu + '  clause 8  retired-control census for ' + $key)) | Out-Null
      continue
    }
    $clause4Held = -not ($script:Failures | Where-Object { $_ -like ('*' + $key + '/*') })
    foreach ($id in $before.Retired[$key].Keys) {
      if ([int]$before.Retired[$key][$id] -le 0) { continue }
      $afterCount = 0
      if ($after.Retired.ContainsKey($key) -and $after.Retired[$key].ContainsKey($id)) {
        $afterCount = [int]$after.Retired[$key][$id]
      }
      if ($afterCount -gt 0) { Add-Pass; continue }
      if ($clause4Held) {
        Add-Pass
        continue
      }
      Add-Failure '8' ($key + ': retired control ' + $id + ' lost all ' +
        $before.Retired[$key][$id] + ' assertions and clause 4 did not prove its homes')
    }
  }
}

# ===========================================================================
# SELF-TEST
# ===========================================================================
function Copy-Fixture {
  param([string]$Destination)
  if (Test-Path -LiteralPath $Destination) {
    Remove-Item -LiteralPath $Destination -Recurse -Force
  }
  $realRoot = (Resolve-Path -LiteralPath (Join-Path $PLAN_DIR '../../../..')).Path
  New-Item -ItemType Directory -Path (Join-Path $Destination 'ui/tests') -Force | Out-Null
  Copy-Item -LiteralPath (Join-Path $realRoot 'ui/src') -Destination (Join-Path $Destination 'ui/src') -Recurse -Force
  Copy-Item -LiteralPath (Join-Path $realRoot 'ui/tests/e2e') -Destination (Join-Path $Destination 'ui/tests/e2e') -Recurse -Force
  foreach ($manifest in @('ui/package.json', 'ui/package-lock.json')) {
    $src = Join-Path $realRoot $manifest
    if (Test-Path -LiteralPath $src -PathType Leaf) {
      Copy-Item -LiteralPath $src -Destination (Join-Path $Destination $manifest) -Force
    }
  }
}

function Edit-Fixture {
  param([string]$Path, [scriptblock]$Transform)
  $text = [System.IO.File]::ReadAllText($Path)
  $text = & $Transform $text
  [System.IO.File]::WriteAllText($Path, $text)
}

<#
  Fixture B: Fixture A plus a SYNTHETIC MEU-46/47 completion generated from
  HOME_SPEC (deviation D5). Its PASS proves self-consistency only; it exists so
  the -Scope all negatives have a green baseline to be mutated away from.
#>
function New-FixtureB {
  param([string]$Root)
  $ui = Join-Path $Root 'ui/src/renderer/src'
  $dl = Join-Path $ui 'features/downloader'

  Remove-Item -LiteralPath (Join-Path $dl 'DownloadQueueTable.tsx') -Force -ErrorAction SilentlyContinue

  # The downloader's own STATUS_COLORS map dies with its table (clause 6).
  $controls = Join-Path $dl 'download-controls.ts'
  if (Test-Path -LiteralPath $controls -PathType Leaf) {
    Edit-Fixture $controls { param($t) $t.Replace('STATUS_COLORS', 'LEGACY_STATUS_PALETTE') }
  }

  # A page stub that mounts the shared package and honours the downloader half
  # of EMPTY_STATE_CONTRACT.
  $stub = @(
    '// SYNTHETIC MEU-46 downloader page (assert-mount-completeness.ps1 -SelfTest).',
    ('import { QueueList } from ' + $SQ + '../../components/queue/QueueList' + $SQ),
    ('import { QueueToolbar } from ' + $SQ + '../../components/queue/QueueToolbar' + $SQ),
    '',
    'export function DownloaderPage(): JSX.Element {',
    '  return (',
    '    <section data-testid="downloader-page">',
    '      <QueueToolbar label="Download queue actions" />',
    '      <QueueList',
    '        testId="queue-list"',
    '        rowTestId="queue-card"',
    '        emptyState={',
    '          <div data-testid="queue-empty-invite">',
    '            Paste a video link above to queue a download',
    '            <button data-testid="queue-empty-invite-action">Paste a link</button>',
    '          </div>',
    '        }',
    '      />',
    '    </section>',
    '  )',
    '}'
  ) -join "`n"
  [System.IO.File]::WriteAllText((Join-Path $dl 'DownloaderPage.tsx'), $stub + "`n")

  # MEU-47 bulk bar, reachable from BOTH pages via the shared list.
  $bulkTree = @()
  foreach ($hRow in @('bulk-move-top', 'bulk-move-bottom', 'bulk-retry', 'bulk-remove')) {
    $bulkTree += $HOME_SPEC[$hRow].TreeSample
  }
  $bulk = @(
    '// SYNTHETIC MEU-47 bulk bar (assert-mount-completeness.ps1 -SelfTest).',
    'export function BulkActionBar(): JSX.Element {',
    '  return (',
    '    <div data-testid="bulk-action-bar">'
  ) + $bulkTree + @(
    '    </div>',
    '  )',
    '}'
  )
  $queueDir = Join-Path $ui 'components/queue'
  [System.IO.File]::WriteAllText((Join-Path $queueDir 'BulkActionBar.tsx'), ($bulk -join "`n") + "`n")
  Edit-Fixture (Join-Path $queueDir 'QueueList.tsx') {
    param($t)
    return ('import { BulkActionBar } from ' + $SQ + './BulkActionBar' + $SQ + "`n" + $t)
  }

  # react-table leaves source and both manifests with the table it served.
  foreach ($manifest in @('ui/package.json', 'ui/package-lock.json')) {
    $path = Join-Path $Root $manifest
    if (Test-Path -LiteralPath $path -PathType Leaf) {
      Edit-Fixture $path { param($t) $t.Replace('@tanstack/react-table', '@removed/react-table') }
    }
  }

  # Synthetic downloader spec: every downloader home, both empty-state ids, and
  # every page capability the before-census recorded.
  $spec = New-SyntheticSpec -PageKey 'downloader'
  [System.IO.File]::WriteAllText((Join-Path $Root 'ui/tests/e2e/download-queue.test.ts'), $spec)

  # The converter owns MEU-47 homes too; append their cases to its real spec.
  $convertExtra = New-SyntheticCases -PageKey 'converter' -Meus @('MEU-47')
  $convertSpec = Join-Path $Root 'ui/tests/e2e/convert-queue.test.ts'
  [System.IO.File]::AppendAllText($convertSpec, "`n" + $convertExtra)
}

function New-SyntheticCases {
  param([string]$PageKey, [string[]]$Meus)
  $retired = $SETS.RETIRED_TOOLBAR_CONTROLS.value
  $subMap = $retired.$PageKey
  $emitted = @{}
  $out = @()
  foreach ($id in ($subMap.PSObject.Properties.Name | Sort-Object)) {
    foreach ($hRow in $subMap.$id) {
      if ($Meus -notcontains $hRow.meu) { continue }
      if ($emitted.ContainsKey($hRow.home)) { continue }
      $emitted[$hRow.home] = $true
      $spec = $HOME_SPEC[$hRow.home]
      if ($null -eq $spec) { continue }
      $out += ('test(' + $SQ + 'synthetic ' + $PageKey + ' home: ' + $hRow.home + $SQ + ', async () => {')
      $out += '  const seam = await mountSeam()'
      $out += ('  const rowOf = (id: string) => page.locator(' + $SQ + '[data-job-id]' + $SQ + ')')
      $out += ('  const openKebab = async (p: unknown, id: string) => page.getByTestId(' + $SQ + 'queue-card-kebab' + $SQ + ')')
      $out += $spec.Sample
      $out += '})'
      $out += ''
    }
  }
  return ($out -join "`n")
}

function New-SyntheticSpec {
  param([string]$PageKey)
  $page = $PAGES | Where-Object { $_.Key -eq $PageKey }
  $header = @(
    ('// SYNTHETIC ' + $PageKey + ' E2E spec (assert-mount-completeness.ps1 -SelfTest).'),
    '// Generated from HOME_SPEC -- see deviation D5 in the script header.',
    ('import { expect, test } from ' + $SQ + '@playwright/test' + $SQ),
    ''
  ) -join "`n"

  $caps = @(
    'downloader-page', 'url-input', 'add-btn', 'queue-list', 'queue-card',
    'queue-summary', 'processor-indicator', 'queue-toolbar'
  )
  $capLines = @('test(' + $SQ + 'synthetic ' + $PageKey + ' page capabilities' + $SQ + ', async () => {')
  foreach ($id in $caps) {
    $capLines += ('  await expect(page.getByTestId(' + $SQ + $id + $SQ + ')).toHaveCount(1)')
  }
  $capLines += '})'
  $capLines += ''

  # EMPTY_STATE_CONTRACT: the invite is interacted with and asserts an outcome.
  $emptyLines = @('test(' + $SQ + 'synthetic ' + $PageKey + ' empty-state contract' + $SQ + ', async () => {')
  foreach ($id in $page.EmptyContainers) {
    $emptyLines += ('  await expect(page.getByTestId(' + $SQ + $id + $SQ + ')).toHaveCount(1)')
  }
  foreach ($id in $page.EmptyActions) {
    $emptyLines += ('  await page.getByTestId(' + $SQ + $id + $SQ + ').click()')
    $emptyLines += ('  await expect(page.getByTestId(' + $SQ + 'url-input' + $SQ + ')).toBeFocused()')
  }
  $emptyLines += '})'
  $emptyLines += ''

  $cases = New-SyntheticCases -PageKey $PageKey -Meus @('MEU-46', 'MEU-47')
  return $header + ($capLines -join "`n") + "`n" + ($emptyLines -join "`n") + "`n" + $cases
}

function Invoke-Gate {
  param([string]$FixtureRoot, [string]$GateScope)
  $output = & pwsh -NoProfile -File $PSCommandPath -Scope $GateScope -Root $FixtureRoot `
    -CensusBefore $CensusBefore 2>&1 | Out-String
  return [pscustomobject]@{ Code = $LASTEXITCODE; Text = $output }
}

function Invoke-SelfTest {
  $fixtureRoot = 'C:/Temp/av-kit/mount-gate-fixtures'
  if (-not (Test-Path -LiteralPath $fixtureRoot)) {
    New-Item -ItemType Directory -Path $fixtureRoot -Force | Out-Null
  }
  $baseA = Join-Path $fixtureRoot 'A'
  $baseB = Join-Path $fixtureRoot 'B'
  Write-Host 'building fixture A (verbatim copy of the real tree)...'
  Copy-Fixture $baseA
  Write-Host 'building fixture B (A + synthetic MEU-46/47 completion, deviation D5)...'
  Copy-Fixture $baseB
  New-FixtureB $baseB

  $convertSpecA = 'ui/tests/e2e/convert-queue.test.ts'
  $downloadSpecA = 'ui/tests/e2e/download-queue.test.ts'
  $convertPageA = 'ui/src/renderer/src/features/converter/ConvertPage.tsx'

  $cases = @(
    @{ Name = 'positive-convert (fixture A, real tree)'; Base = 'A'; GateScope = 'convert'; Code = 0
      Expect = @('GATE PASS', 'PENDING (MEU-46)', 'PENDING (MEU-47)'); Mutate = { param($r) }
    },
    @{ Name = 'c1 page no longer renders QueueList'; Base = 'A'; GateScope = 'convert'; Code = 1
      Expect = @('clause 1'); Mutate = {
        param($r) Edit-Fixture (Join-Path $r $convertPageA) { param($t) $t.Replace('<QueueList', '<LegacyTable') }
      }
    },
    @{ Name = 'c2 retired table resurrected'; Base = 'A'; GateScope = 'convert'; Code = 1
      Expect = @('clause 2'); Mutate = {
        param($r)
        [System.IO.File]::WriteAllText(
          (Join-Path $r 'ui/src/renderer/src/features/converter/ConvertQueueTable.tsx'),
          ('export function ConvertQueueTable(): null { return null }' + "`n"))
      }
    },
    @{ Name = 'c3 react-table back in the manifest only'; Base = 'B'; GateScope = 'all'; Code = 1
      Expect = @('clause 3'); Mutate = {
        param($r) Edit-Fixture (Join-Path $r 'ui/package.json') {
          param($t) $t.Replace('"dependencies": {', '"dependencies": {' + "`n" + '    "@tanstack/react-table": "^8.21.0",')
        }
      }
    },
    @{ Name = 'c4a retired convert-up reintroduced'; Base = 'A'; GateScope = 'convert'; Code = 1
      Expect = @('clause 4(a)', 'convert-up'); Mutate = {
        param($r) Edit-Fixture (Join-Path $r $convertPageA) {
          param($t) $t + "`n" + '// resurrected: data-testid="convert-up"' + "`n"
        }
      }
    },
    @{ Name = 'c4b home testid missing from the tree'; Base = 'A'; GateScope = 'convert'; Code = 1
      Expect = @('clause 4(b)'); Mutate = {
        param($r) Edit-Fixture (Join-Path $r 'ui/src/renderer/src/components/queue/QueueToolbar.tsx') {
          param($t) $t.Replace('queue-toolbar-start', 'queue-toolbar-begin')
        }
      }
    },
    @{ Name = 'c4c home renders but is wired to nothing'; Base = 'A'; GateScope = 'convert'; Code = 1
      Expect = @('clause 4(c)'); Mutate = {
        param($r) Edit-Fixture (Join-Path $r $convertSpecA) { param($t) $t.Replace('.click()', '.count()') }
      }
    },
    @{ Name = 'c4d interaction performed but no outcome asserted'; Base = 'A'; GateScope = 'convert'; Code = 1
      Expect = @('clause 4(d)'); Mutate = {
        param($r) Edit-Fixture (Join-Path $r $convertSpecA) {
          param($t)
          foreach ($matcher in @('toEqual(', 'toHaveLength(', 'toHaveCount(', 'toHaveText(',
              'toHaveAccessibleName(', 'toBeDisabled(', 'toBe(', 'toBeUndefined(')) {
            $t = $t.Replace('.' + $matcher, '.toBeVisible(')
          }
          return $t
        }
      }
    },
    @{ Name = 'c4-sibling bulk-move-top dead while kebab move-top works'; Base = 'B'; GateScope = 'all'; Code = 1
      Expect = @('clause 4(c)', 'bulk-move-top')
      Also = @{ GateScope = 'convert'; Code = 0; Expect = @('GATE PASS', 'PENDING (MEU-47)') }
      Mutate = {
        param($r)
        foreach ($spec in @($convertSpecA, $downloadSpecA)) {
          Edit-Fixture (Join-Path $r $spec) {
            param($t)
            return [regex]::Replace($t, 'test\(' + $SQ + 'synthetic [^' + $SQ + ']*bulk-move-top' + $SQ +
              '[\s\S]*?\n\}\)\n', '')
          }
        }
      }
    },
    @{ Name = 'c5 new testid unregistered in test-ids.ts'; Base = 'A'; GateScope = 'convert'; Code = 1
      Expect = @('clause 5', 'bulk-move-top'); Mutate = {
        param($r) Edit-Fixture (Join-Path $r 'ui/tests/e2e/test-ids.ts') {
          param($t) $t.Replace('bulk-move-top', 'bulk-shift-top')
        }
      }
    },
    @{ Name = 'c6 legacy STATUS_COLORS map survives'; Base = 'A'; GateScope = 'convert'; Code = 1
      Expect = @('clause 6'); Mutate = {
        param($r) Edit-Fixture (Join-Path $r 'ui/src/renderer/src/features/converter/convert-controls.ts') {
          param($t) $t + "`n" + 'export const STATUS_COLORS = { Done: ' + $SQ + 'bg-accent' + $SQ + ' }' + "`n"
        }
      }
    },
    @{ Name = 'c7 empty-state Browse present but no-op'; Base = 'A'; GateScope = 'convert'; Code = 1
      Expect = @('clause 7', 'queue-empty-browse'); Mutate = {
        param($r) Edit-Fixture (Join-Path $r $convertSpecA) {
          param($t)
          return [regex]::Replace($t, '(?m)^.*queue-empty-browse' + $SQ + '\)\.click\(\).*$\r?\n', '')
        }
      }
    },
    @{ Name = 'c8 assertions softened out of the census'; Base = 'A'; GateScope = 'convert'; Code = 1
      Expect = @('clause 8'); Mutate = {
        param($r) Edit-Fixture (Join-Path $r $downloadSpecA) {
          param($t) $t.Replace('await expect(', 'await Promise.resolve(')
        }
      }
    },
    @{ Name = 'positive-all (fixture B, synthetic completion)'; Base = 'B'; GateScope = 'all'; Code = 0
      Expect = @('GATE PASS', '<none>'); Mutate = { param($r) }
    }
  )

  $failed = 0
  $index = 0
  foreach ($case in $cases) {
    $index++
    $caseRoot = Join-Path $fixtureRoot ('case-' + $index)
    if (Test-Path -LiteralPath $caseRoot) { Remove-Item -LiteralPath $caseRoot -Recurse -Force }
    $source = if ($case.Base -eq 'B') { $baseB } else { $baseA }
    Copy-Item -LiteralPath $source -Destination $caseRoot -Recurse -Force
    & $case.Mutate $caseRoot

    $runs = @(@{ GateScope = $case.GateScope; Code = $case.Code; Expect = $case.Expect })
    if ($null -ne $case.Also) { $runs += $case.Also }

    $ok = $true
    $why = @()
    foreach ($run in $runs) {
      $result = Invoke-Gate -FixtureRoot $caseRoot -GateScope $run.GateScope
      if ($result.Code -ne $run.Code) {
        $ok = $false
        $why += ('scope=' + $run.GateScope + ' exit ' + $result.Code + ' (expected ' + $run.Code + ')')
      }
      foreach ($needle in $run.Expect) {
        if ($result.Text.IndexOf($needle) -lt 0) {
          $ok = $false
          $why += ('scope=' + $run.GateScope + ' output missing ' + $SQ + $needle + $SQ)
        }
      }
      if (-not $ok) {
        $tail = ($result.Text -split "`r?`n" | Select-Object -Last 25) -join "`n"
        $why += ('--- tail ---' + "`n" + $tail)
      }
    }
    if ($ok) {
      Write-Host ('  PASS  ' + $case.Name)
      Remove-Item -LiteralPath $caseRoot -Recurse -Force -ErrorAction SilentlyContinue
    }
    else {
      $failed++
      Write-Host ('  FAIL  ' + $case.Name)
      foreach ($line in $why) { Write-Host ('        ' + $line) }
    }
  }

  Write-Host ''
  Write-Host ('self-test cases: ' + $cases.Count + '  failed: ' + $failed)
  if ($failed -eq 0) {
    Write-Host 'SELFTEST PASS'
    return 0
  }
  Write-Host 'SELFTEST FAIL'
  return 1
}

# ===========================================================================
if ($SelfTest) { exit (Invoke-SelfTest) }
exit (Invoke-Verify)
