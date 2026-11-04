<#
.SYNOPSIS
  PLAN_GATE_SCRIPT - the eight task.md validation gates that cannot be expressed
  as a variable-free one-liner.

.DESCRIPTION
  Eight task rows (2, 9, 11, H1-1, H1-4, H2-2, H2-3, H2-5) previously carried
  their validation either as an inline `pwsh -NoProfile -Command "$var=..."`
  payload or as adjacent text. Neither is a gate. The inline form is not even
  executable: the OUTER shell expands `$var` inside the double-quoted argument
  before the inner pwsh ever parses it, so the child receives `=@(Select-String
  ...)` and dies with `The term '=@' is not recognized` - identical under a
  PowerShell and a bash outer shell, and non-zero for the wrong reason. The
  adjacent-text form (`Get-Content <file> -Tail 3`) prints whatever is there and
  exits 0 even when the file is absent or empty.

  This script is the single home for those eight gates. Each is selected with
  -Gate and is written as a fail-closed predicate over files, with every literal
  (package names and ranges, floors, AC-to-file maps, marker lists, file paths)
  read from named-sets.json rather than restated here.

  ROUND-4 HARDENING (R3-F4/R3-F5). Round 3 found that five of the six then-
  existing gates were already satisfied by the UNSTARTED tree, so passing them
  proved nothing about the MEU:

    - Deps substring-matched a package NAME anywhere in the file text, so a
      mention in a comment or an unrelated transitive entry satisfied it, and no
      version range was ever checked. It now parses both manifests as JSON.
    - E2eCensus asserted the PRE-MEU static floor, one testid registration and
      the absence of `dragTo(` - all three true before a line is written. It now
      requires each E2E_REQUIRED_CASES AC id inside a `test(` title in its NAMED
      file, and the POST-MEU floor.
    - BuildPlanAudit grepped only the two GENERATED status files, so deleting a
      sentence by hand passed while .agent/context/meu-status.yaml - the source
      those files are rendered from - still said `pending`. It now asserts the
      YAML, the phase row, and the Next pointer.
    - Unchecked scanned the whole of task.md including its OWN row and every
      later closeout row, which are legitimately open while it runs, so it could
      never pass. It is now scoped above its own row, rejects `[/]` as well as
      `[ ]`, and evidence-gates `[B]`.
    - ApiSkip merged git's stderr into its porcelain output with `2>&1`, so a
      single git warning line was read as a modified file. Streams are now
      separated and each porcelain line is validated against the v1 shape.

  Two gates are new: Metrics (H2-3) and CommitDraft (H2-5), replacing bare
  `Get-Content` receipts.

  ABSENT_VALIDATOR_RULE: no repo-level equivalent exists for any of these eight
  checks; this plan-local script is the check.

.PARAMETER Gate
  Which gate to run:

    Deps            row 2    - every DND_PACKAGES entry declared in ui/package.json
                               `dependencies` at its REGISTERED range and resolved in
                               ui/package-lock.json with a concrete matching version;
                               `@dnd-kit/react` and `react-virtual` absent.
    E2eCensus       row 9    - every E2E_REQUIRED_CASES AC id inside a `test(` title in
                               its NAMED spec; static `test(` count at or above
                               E2E_POST_MEU_STATIC_FLOOR; DND_TESTIDS registered;
                               `dragTo(` nowhere (E2E_DRAG_DRIVER).
    BuildPlanAudit  row 11   - PHASE_EXIT_ASSERTIONS landed in the status YAML and both
                               generated files, phase row Completed, Next -> Phase 11.
    Unchecked       H1-1     - every task.md row ABOVE the H1-1 row is `[x]` or a valid,
                               evidence-carrying `[B]`.
    ApiSkip         H1-4     - packages/api/ untouched (stdout-only porcelain), and when
                               -ReceiptPath is given the pytest receipt is clean.
    Reflection      H2-2     - every REFLECTION_MARKERS pattern appears in REFLECTION_FILE.
    Metrics         H2-3     - METRICS_FILE has a METRICS_SLUG row carrying every
                               METRICS_ROW_MARKERS entry.
    CommitDraft     H2-5     - the COMMIT_DRAFT_MARKERS draft exists, is non-empty, has a
                               short conventional subject, carries every required marker
                               and no forbidden trailer. It does NOT commit.

.PARAMETER ReceiptPath
  ApiSkip only: an optional pytest receipt under VALIDATION_RECEIPT_DIR to scan
  for a non-zero failure/error count.

.PARAMETER SelfTest
  Prove each gate PASSES on a synthetic well-formed fixture and FAILS on each of
  its defect shapes, including the five round-3 "passes on the unstarted tree"
  shapes. Writes fixtures under the system temp directory. Run this before
  trusting any gate - most legitimately fail against today's tree (the work is
  not done yet), so a live run cannot distinguish "gate works" from "gate always
  fails".
#>
[CmdletBinding()]
param(
    [ValidateSet('Deps', 'DepsPackages', 'E2eCensus', 'BuildPlanAudit', 'Unchecked', 'ApiSkip', 'Reflection', 'Metrics', 'CommitDraft')]
    [string]$Gate,
    [string]$ReceiptPath,
    [switch]$SelfTest
)

$ErrorActionPreference = 'Stop'

$setsPath = Join-Path $PSScriptRoot 'named-sets.json'
if (-not (Test-Path -LiteralPath $setsPath)) {
    Write-Error ('missing NAMED_SETS_FILE ' + $setsPath)
    exit 1
}
$sets = Get-Content -LiteralPath $setsPath -Raw | ConvertFrom-Json

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '../../../..')).Path
$planRel = 'docs/execution/plans/2026-09-03-p10-queue-card-dnd'

# DND_PACKAGES is stated as name@range. Split on the LAST '@' so scoped names
# (@dnd-kit/core) survive; both halves are load-bearing - the name proves the
# dependency is present, the range proves it is the researched one.
$dndPackages = @()
foreach ($entry in @($sets.DND_PACKAGES.value)) {
    $s = [string]$entry
    $idx = $s.LastIndexOf('@')
    if ($idx -lt 1) { continue }
    $dndPackages += [pscustomobject]@{ Name = $s.Substring(0, $idx); Range = $s.Substring($idx + 1) }
}
$dndNames = @($dndPackages | ForEach-Object { $_.Name })

# TESTING_LIBRARY_PACKAGES are DEV dependencies (round-5 R4-F5). They are parsed
# and gated separately from DND_PACKAGES so a package can never drift into the
# wrong section unnoticed: a runtime dep in devDependencies and a dev dep in
# dependencies are both named failures.
$tlPackages = @()
foreach ($s in @($sets.TESTING_LIBRARY_PACKAGES.value)) {
    $idx = ([string]$s).LastIndexOf('@')
    if ($idx -lt 1) { continue }
    $tlPackages += [pscustomobject]@{ Name = $s.Substring(0, $idx); Range = $s.Substring($idx + 1) }
}
if ($tlPackages.Count -lt 1) {
    Write-Error 'TESTING_LIBRARY_PACKAGES is missing or empty in named-sets.json'
    exit 1
}
$tlMigrationFiles = @($sets.TL_MIGRATION_FILES.value)
# The user-event obligation binds to the INTERACTION subset only (round-6 R5-F3):
# demanding userEvent.setup() in a file that simulates nothing would be satisfied by
# a no-op call, which is the shape of false pass this gate exists to reject.
$tlInteractionFiles = @($sets.TL_INTERACTION_FILES.value)
$tlMountOnlyFiles = @($sets.TL_MOUNT_ONLY_FILES.value)
# AC-49.2 in executable form (round-7, R6-F1). Every field is a literal substring;
# the gate never builds a regex out of them, so the guard cannot be satisfied by a
# lookalike that merely mentions react-virtual somewhere.
$depGuard = $sets.DND_DEP_GUARD_CHECK.value
$nextPointer = $sets.BUILD_PLAN_NEXT_POINTER.value

$postMeuStaticFloor = [int]$sets.E2E_POST_MEU_STATIC_FLOOR.value
$testIds = @($sets.DND_TESTIDS.value)
$reflectionMarkers = @($sets.REFLECTION_MARKERS.value)
$reflectionFile = [string]$sets.REFLECTION_FILE.value
$metricsFile = [string]$sets.METRICS_FILE.value
$metricsSlug = [string]$sets.METRICS_SLUG.value
$metricsMarkers = @($sets.METRICS_ROW_MARKERS.value)
$receiptDir = [string]$sets.VALIDATION_RECEIPT_DIR.value

$e2eRequired = @{}
foreach ($prop in $sets.E2E_REQUIRED_CASES.value.PSObject.Properties) {
    $e2eRequired[[string]$prop.Name] = [string]$prop.Value
}

$phaseExit = $sets.PHASE_EXIT_ASSERTIONS.value
$commitDraft = $sets.COMMIT_DRAFT_MARKERS.value

function Get-Text {
    param([Parameter(Mandatory = $true)][string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) { return $null }
    return (Get-Content -LiteralPath $Path -Raw)
}

function Get-Json {
    param([Parameter(Mandatory = $true)][string]$Path)
    $text = Get-Text $Path
    if ($null -eq $text) { return $null }
    # -AsHashtable is REQUIRED, not a style choice: a lockfileVersion 2+ manifest
    # keys its own root package as the empty string (`packages[""]`), and
    # ConvertFrom-Json refuses an empty property name in object mode with
    # "The provided JSON includes a property whose name is an empty string".
    # Without this the gate would silently report "ui/package-lock.json is
    # missing or is not valid JSON" against a perfectly good lockfile.
    try { return ($text | ConvertFrom-Json -AsHashtable) } catch { return $null }
}

function Get-Prop {
    param($Object, [string]$Name)
    if ($null -eq $Object) { return $null }
    if ($Object -is [System.Collections.IDictionary]) {
        if (-not $Object.Contains($Name)) { return $null }
        return $Object[$Name]
    }
    $p = $Object.PSObject.Properties[$Name]
    if ($null -eq $p) { return $null }
    return $p.Value
}

function Get-PropNames {
    param($Object)
    if ($null -eq $Object) { return @() }
    if ($Object -is [System.Collections.IDictionary]) { return @($Object.Keys) }
    return @($Object.PSObject.Properties.Name)
}

# ---------------------------------------------------------------- row 2

# TL_INTERACTION_FILES and TL_MOUNT_ONLY_FILES must PARTITION TL_MIGRATION_FILES:
# no overlap, no stranger, no unclassified file. Without this, the exempt bucket
# is a hole - moving a file into TL_MOUNT_ONLY_FILES silently removes its
# user-event obligation, and moving one out of TL_MIGRATION_FILES removes every
# obligation at once. Taken as parameters rather than read from the closure so the
# self-test can feed it drifted sets without a checked-out tree.
function Test-TlPartition {
    param($Migration, $Interaction, $MountOnly)

    $problems = New-Object System.Collections.Generic.List[string]
    $mig = @($Migration | ForEach-Object { [string]$_ })
    $int = @($Interaction | ForEach-Object { [string]$_ })
    $mo = @($MountOnly | ForEach-Object { [string]$_ })

    foreach ($f in $int) {
        if ($mo -contains $f) {
            $problems.Add('TL partition: ' + $f + ' is in BOTH TL_INTERACTION_FILES and TL_MOUNT_ONLY_FILES - a file either owes the user-event obligation or is exempt from it')
        }
        if ($mig -notcontains $f) {
            $problems.Add('TL partition: TL_INTERACTION_FILES names ' + $f + ', which is not in TL_MIGRATION_FILES')
        }
    }
    foreach ($f in $mo) {
        if ($mig -notcontains $f) {
            $problems.Add('TL partition: TL_MOUNT_ONLY_FILES names ' + $f + ', which is not in TL_MIGRATION_FILES')
        }
    }
    foreach ($f in $mig) {
        if (($int -notcontains $f) -and ($mo -notcontains $f)) {
            $problems.Add('TL partition: ' + $f + ' is in TL_MIGRATION_FILES but in neither TL_INTERACTION_FILES nor TL_MOUNT_ONLY_FILES - every migrated file must declare whether it simulates interaction')
        }
    }
    return $problems
}

# The canonical row-2 result. Every fixture that writes the guard file appends this,
# so the good tree and the boundary tree model what row 2 actually delivers rather
# than a file that merely satisfies the RTL predicates (round-7, R6-F1). A LITERAL
# here-string: nothing in it may be expanded.
$depGuardBlock = @'

  it('AC-49.2 no virtualization dependency', () => {
    // MEU-49 supersession (DND_DEP_GUARD_SUPERSESSION), citing
    // docs/build-plan/10-queue-card-ui.md:254-256: that section schedules dnd-kit as
    // this MEU's own dependency, so the half of this guard that forbade it has expired.
    // The virtualization half stays armed - :47 still forbids a virtualization package.
    expect(names.filter((name) => /react-virtual/.test(name))).toEqual([])
  })
'@

function Add-DepGuard {
    param([Parameter(Mandatory = $true)][string]$Rel, [Parameter(Mandatory = $true)][string]$Content)
    if ([string]$Rel -eq [string]$depGuard.file) { return $Content + $depGuardBlock }
    return $Content
}

# AC-49.2 / DND_DEP_GUARD_CHECK. Row 2 narrows the live dependency guard from
# /dnd-kit|react-virtual/ to /react-virtual/ and leaves an in-place supersession
# comment. Until it does, installing DND_PACKAGES makes a PRE-EXISTING test fail for a
# reason unrelated to MEU-49 - and round 6's Packages mode never read the file, so it
# reported green on a tree where row 2's own named deliverable was absent (R6-F1).
function Test-DepGuard {
    param([Parameter(Mandatory = $true)][string]$Root)

    $problems = New-Object System.Collections.Generic.List[string]
    $rel = [string]$depGuard.file
    $text = Get-Text (Join-Path $Root $rel)
    if ($null -eq $text) {
        $problems.Add($rel + ' is missing - DND_DEP_GUARD_SUPERSESSION cannot be verified (AC-49.2)')
        return $problems
    }

    if ($text.Contains([string]$depGuard.retired)) {
        $problems.Add($rel + ' still asserts the broad ' + [string]$depGuard.retired + ' dependency guard - AC-49.2 narrows it to ' + [string]$depGuard.narrowed + ', and until it does, the three DND_PACKAGES this row installs fail a pre-existing test for a reason that has nothing to do with MEU-49')
        return $problems
    }

    $lines = $text -split "`r?`n"
    $at = -1
    for ($i = 0; $i -lt $lines.Count; $i++) {
        if ($lines[$i].Contains([string]$depGuard.narrowed)) { $at = $i; break }
    }
    if ($at -lt 0) {
        $problems.Add($rel + ' does not narrow the dependency guard to ' + [string]$depGuard.narrowed + ' - DELETING the assertion is test-weakening (G36_RULE), not supersession; AC-49.2 requires the virtualization half to stay armed')
        return $problems
    }
    if (-not $text.Contains([string]$depGuard.armed)) {
        $problems.Add($rel + ' narrows the guard but no ' + [string]$depGuard.armed + ' assertion remains - the virtualization half must stay ARMED (AC-49.2)')
    }

    # "In place" is executable: the comment must sit within comment_window lines of the
    # assertion it supersedes, which is the MEU-45 precedent's own shape (6 lines).
    $window = [int]$depGuard.comment_window
    $lo = [Math]::Max(0, $at - $window)
    $hi = [Math]::Min($lines.Count - 1, $at + $window)
    $hasMarker = $false
    $hasCite = $false
    for ($i = $lo; $i -le $hi; $i++) {
        $trimmed = $lines[$i].TrimStart()
        if (-not ($trimmed.StartsWith('//') -or $trimmed.StartsWith('*') -or $trimmed.StartsWith('/*'))) { continue }
        if ($trimmed.Contains([string]$depGuard.marker)) { $hasMarker = $true }
        if ($trimmed.Contains([string]$depGuard.citation)) { $hasCite = $true }
    }
    if (-not $hasMarker) {
        $problems.Add($rel + ' has no in-place ' + [string]$depGuard.marker + ' supersession comment within ' + $window + ' lines of the narrowed guard - a narrowed assertion with no stated reason is indistinguishable from test-weakening (AC-49.2, G36_RULE)')
    }
    if (-not $hasCite) {
        $problems.Add($rel + ' supersession comment does not cite ' + [string]$depGuard.citation + ' within ' + $window + ' lines of the narrowed guard - the citation is what makes it spec supersession rather than an opinion (AC-49.2)')
    }
    return $problems
}

function Test-Deps {
    param(
        [Parameter(Mandatory = $true)][string]$Root,
        # `Packages` is task row 2's gate (manifests, lockfile, rejected packages,
        # jest-dom wiring). `Full` adds the row-2a adoption half. Round-6 (R5-F2).
        [ValidateSet('Packages', 'Full')][string]$Mode = 'Full'
    )

    $problems = New-Object System.Collections.Generic.List[string]

    $pkg = Get-Json (Join-Path $Root 'ui/package.json')
    if ($null -eq $pkg) {
        $problems.Add('ui/package.json is missing or is not valid JSON')
    }
    else {
        $deps = Get-Prop $pkg 'dependencies'
        $devDeps = Get-Prop $pkg 'devDependencies'
        foreach ($p in $dndPackages) {
            $declared = Get-Prop $deps $p.Name
            if ($null -eq $declared) {
                if ($null -ne (Get-Prop $devDeps $p.Name)) {
                    $problems.Add('ui/package.json declares ' + $p.Name + ' in devDependencies - it is a RUNTIME dependency of the renderer and must be in dependencies')
                }
                else {
                    $problems.Add('ui/package.json dependencies does not declare ' + $p.Name)
                }
                continue
            }
            if ([string]$declared -ne $p.Range) {
                $problems.Add('ui/package.json declares ' + $p.Name + ' at "' + $declared + '" but DND_PACKAGES registers "' + $p.Range + '"')
            }
        }
        # TESTING_LIBRARY_PACKAGES: devDependencies, exact registered range, and a
        # named failure if one is parked in `dependencies` instead (round-5 R4-F5).
        foreach ($p in $tlPackages) {
            $declared = Get-Prop $devDeps $p.Name
            if ($null -eq $declared) {
                if ($null -ne (Get-Prop $deps $p.Name)) {
                    $problems.Add('ui/package.json declares ' + $p.Name + ' in dependencies - it is a TEST-ONLY dependency and must be in devDependencies')
                }
                else {
                    $problems.Add('ui/package.json devDependencies does not declare ' + $p.Name + ' - TESTING_LIBRARY_ADOPTION requires it (G37_RULE, AC-49.39)')
                }
                continue
            }
            if ([string]$declared -ne $p.Range) {
                $problems.Add('ui/package.json declares ' + $p.Name + ' at "' + $declared + '" but TESTING_LIBRARY_PACKAGES registers "' + $p.Range + '"')
            }
        }

        foreach ($forbidden in @('@dnd-kit/react', 'react-virtual')) {
            foreach ($section in @('dependencies', 'devDependencies', 'optionalDependencies', 'peerDependencies')) {
                $bag = Get-Prop $pkg $section
                if ($null -eq $bag) { continue }
                foreach ($name in (Get-PropNames $bag)) {
                    if ($name -like ('*' + $forbidden + '*')) {
                        $problems.Add('ui/package.json ' + $section + ' declares the rejected dependency ' + $name)
                    }
                }
            }
        }
    }

    $lock = Get-Json (Join-Path $Root 'ui/package-lock.json')
    if ($null -eq $lock) {
        $problems.Add('ui/package-lock.json is missing or is not valid JSON')
    }
    else {
        $packages = Get-Prop $lock 'packages'
        if ($null -eq $packages) {
            $problems.Add('ui/package-lock.json has no `packages` map - lockfileVersion 2+ is required to verify resolution')
        }
        else {
            foreach ($p in (@($dndPackages) + @($tlPackages))) {
                $entry = Get-Prop $packages ('node_modules/' + $p.Name)
                if ($null -eq $entry) {
                    $problems.Add('ui/package-lock.json does not resolve node_modules/' + $p.Name + ' - the dependency is declared but not installed')
                    continue
                }
                $version = [string](Get-Prop $entry 'version')
                if ([string]::IsNullOrWhiteSpace($version)) {
                    $problems.Add('ui/package-lock.json entry for ' + $p.Name + ' has no concrete version')
                    continue
                }
                # The registered range is `^MAJOR.MINOR.PATCH`; a caret range can only
                # resolve within the same major, so a major mismatch is a real defect
                # rather than a stale pin.
                $wantMajor = ($p.Range -replace '^[\^~>=<\s]*', '') -split '\.' | Select-Object -First 1
                $gotMajor = ($version -split '\.') | Select-Object -First 1
                if ($wantMajor -ne $gotMajor) {
                    $problems.Add('ui/package-lock.json resolved ' + $p.Name + ' to ' + $version + ', outside the registered range ' + $p.Range)
                }
            }
        }
    }

    # AC-49.2: the matchers the migrated assertions read (toBeDisabled,
    # toBeInTheDocument) only exist once '@testing-library/jest-dom/vitest' is
    # imported from a setup file. Row 2 installs the package AND wires it; either
    # location is executable, so either satisfies the check.
    $jestDomWired = $false
    foreach ($rel in @('ui/vitest.config.ts', 'ui/tests/unit/setup.ts')) {
        $text = Get-Text (Join-Path $Root $rel)
        if ($null -ne $text -and $text.Contains('@testing-library/jest-dom/vitest')) {
            $jestDomWired = $true
        }
    }
    if (-not $jestDomWired) {
        $problems.Add('neither ui/vitest.config.ts nor ui/tests/unit/setup.ts imports @testing-library/jest-dom/vitest - the jest-dom matchers are installed but never registered, so every migrated assertion that uses one throws (AC-49.2)')
    }

    # AC-49.2 runs in BOTH modes: the narrowed dependency guard is row 2's own named
    # deliverable, so a Packages-mode green with the broad guard still in place is a
    # false pass on the very row being gated (round-7, R6-F1).
    foreach ($p in (Test-DepGuard -Root $Root)) { $problems.Add($p) }

    # Everything below is the row-2a ADOPTION half. Row 2 must be able to close
    # before row 2a runs, so -Mode Packages stops here (round-6, R5-F2).
    if ($Mode -ne 'Full') { return $problems }

    foreach ($p in (Test-TlPartition -Migration $tlMigrationFiles -Interaction $tlInteractionFiles -MountOnly $tlMountOnlyFiles)) { $problems.Add($p) }

    # AC-49.39 (round-5 R4-F5). Installing the packages is not the deliverable;
    # REPLACING the shim is. Without these three checks, adding the devDependencies
    # and changing nothing else passes every other gate in this file, and the suite
    # ships with two userEvent surfaces - the exact fork TESTING_LIBRARY_ADOPTION
    # exists to prevent.
    $shim = Join-Path $Root 'ui/tests/unit/helpers/user-event.ts'
    if (Test-Path -LiteralPath $shim) {
        $problems.Add('ui/tests/unit/helpers/user-event.ts still exists - TESTING_LIBRARY_ADOPTION deletes it outright rather than keeping a re-export (AC-49.39)')
    }
    $uiRoot = Join-Path $Root 'ui'
    if (Test-Path -LiteralPath $uiRoot) {
        $importers = @(Get-ChildItem -LiteralPath $uiRoot -Recurse -File -Include '*.ts', '*.tsx' -ErrorAction SilentlyContinue |
            Where-Object { $_.FullName -notmatch '[\\/]node_modules[\\/]' } |
            Select-String -Pattern 'helpers/user-event' -SimpleMatch)
        foreach ($hit in $importers) {
            $rel = $hit.Path.Substring($Root.Length).TrimStart([char]0x5C, [char]0x2F) -replace '\\', '/'
            $problems.Add('still imports the deleted shim at ' + $rel + ':' + $hit.LineNumber + ' (AC-49.39)')
        }
    }
    $interactionSet = @{}
    foreach ($rel in $tlInteractionFiles) { $interactionSet[[string]$rel] = $true }

    foreach ($rel in $tlMigrationFiles) {
        $full = Join-Path $Root $rel
        if (-not (Test-Path -LiteralPath $full)) {
            $problems.Add('TL_MIGRATION_FILES entry is missing: ' + $rel)
            continue
        }
        $text = Get-Content -LiteralPath $full -Raw
        if ($null -eq $text) { $text = '' }

        # ---- MOUNT half, required of ALL 14 (round-6, R5-F3). The round-5 gate
        #      checked only the user-event half, so a file that kept its hand-rolled
        #      createRoot mount and gained one no-op userEvent.setup() satisfied both
        #      this gate and the exactly-439 count while delivering no migration.
        #      TESTING_LIBRARY_ADOPTION clauses (a)-(e).
        if (-not $text.Contains('@testing-library/react')) {
            $problems.Add($rel + ' does not import @testing-library/react - clause (a): row 2a recodes the MOUNT, not just the click helper (AC-49.39)')
        }
        if ($text -notmatch '\brender\s*\(') {
            $problems.Add($rel + ' never calls render( - clause (b): the hand-rolled mount block was not replaced (AC-49.39)')
        }
        if ($text -notmatch '\bscreen\s*\.') {
            $problems.Add($rel + ' never queries through screen - clause (c) (AC-49.39)')
        }
        # ---- the RETIRED surface must be GONE, not merely joined by a new one
        if ($text.Contains('react-dom/client')) {
            $problems.Add($rel + ' still imports react-dom/client - clause (d): the retired manual-mount surface survived alongside the new one (AC-49.39)')
        }
        if ($text.Contains('createRoot')) {
            $problems.Add($rel + ' still calls createRoot - clause (d): render() replaces it rather than sitting next to it (AC-49.39)')
        }
        # `act` from RTL is fine and is sometimes the right escape hatch; `act` from
        # react is the manual-mount idiom this row retires. `createElement` is NOT
        # checked at all: these are .test.ts files with no JSX, so
        # render(createElement(C, props)) is the idiomatic RTL form in this suite.
        if ($text -match "import\s*\{[^}]*\bact\b[^}]*\}\s*from\s*'react'") {
            $problems.Add($rel + " still imports act from 'react' - clause (e): userEvent v14 and RTL handle act themselves, and a manual wrapper is the double-wrap warning (AC-49.39)")
        }

        # ---- INTERACTION half, required only of TL_INTERACTION_FILES. The one
        #      TL_MOUNT_ONLY_FILES entry simulates nothing, and forcing a setup() call
        #      into it would manufacture the dead ceremony this gate rejects elsewhere.
        if ($interactionSet.ContainsKey([string]$rel)) {
            if (-not $text.Contains('@testing-library/user-event')) {
                $problems.Add($rel + ' does not import @testing-library/user-event - clause (f): it simulates interaction, so it owes the user-event surface (G37_RULE, AC-49.39)')
            }
            if (-not $text.Contains('userEvent.setup()')) {
                $problems.Add($rel + ' never calls userEvent.setup() - clause (g): G37_RULE requires the v14 setup form, not the deprecated direct-call API')
            }
        }
    }

    return $problems
}

# ---------------------------------------------------------------- row 9

function Test-E2eCensus {
    param([Parameter(Mandatory = $true)][string]$Root)

    $problems = New-Object System.Collections.Generic.List[string]
    $specs = @(Get-ChildItem -Path (Join-Path $Root 'ui/tests/e2e') -Filter '*.test.ts' -ErrorAction SilentlyContinue)
    if ($specs.Count -lt 1) {
        $problems.Add('no ui/tests/e2e/*.test.ts specs found')
        return $problems
    }

    $paths = @($specs | ForEach-Object { $_.FullName })
    $cases = @(Select-String -LiteralPath $paths -Pattern '^\s*test\(')
    if ($cases.Count -lt $postMeuStaticFloor) {
        $problems.Add('static E2E case count ' + $cases.Count + ' is below E2E_POST_MEU_STATIC_FLOOR ' + $postMeuStaticFloor + ' - the MEU-49 cases were not all written')
    }

    # Each integration AC must be a case in the file that OWNS it. A count floor
    # alone cannot tell a completed MEU from an untouched tree.
    foreach ($id in @($e2eRequired.Keys)) {
        $rel = [string]$e2eRequired[$id]
        $full = Join-Path $Root $rel
        if (-not (Test-Path -LiteralPath $full)) {
            $problems.Add('E2E_REQUIRED_CASES names a spec that does not exist: ' + $rel)
            continue
        }
        $hits = @(Select-String -LiteralPath $full -Pattern ('^\s*test\(.*' + [regex]::Escape($id)))
        if ($hits.Count -lt 1) {
            $problems.Add('no `test(` title in ' + $rel + ' carries ' + $id)
        }
    }

    # Comments are exempt. E2E_DRAG_DRIVER is a rule about what the specs CALL,
    # and the specs are required to explain why they hand-drive the pointer - an
    # explanation that has to name the API it rejects. Flagging the prose would
    # make documenting the rule a violation of it. Comments are blanked rather
    # than filtered line-by-line so a `/* ... */` block whose continuation lines
    # carry no leading `*` is covered too; blanking preserves the newlines, so
    # every reported line number still points at the real line.
    $commentPattern = '/\*[\s\S]*?\*/|//[^\r\n]*'
    $blankOut = [System.Text.RegularExpressions.MatchEvaluator] {
        param($m)
        [regex]::Replace($m.Value, '[^\r\n]', ' ')
    }
    foreach ($specPath in $paths) {
        $specText = Get-Content -LiteralPath $specPath -Raw
        if ([string]::IsNullOrEmpty($specText)) { continue }
        $code = [regex]::Replace($specText, $commentPattern, $blankOut)
        $specLines = $code -split "`r?`n"
        for ($i = 0; $i -lt $specLines.Count; $i++) {
            if ($specLines[$i] -match 'dragTo\(') {
                $problems.Add('E2E_DRAG_DRIVER violation - locator.dragTo() at ' +
                    (Split-Path -Leaf $specPath) + ':' + ($i + 1))
            }
        }
    }
    $registry = Get-Text (Join-Path $Root 'ui/tests/e2e/test-ids.ts')
    if ($null -eq $registry) {
        $problems.Add('missing ui/tests/e2e/test-ids.ts')
    }
    else {
        foreach ($id in $testIds) {
            if ($registry -notmatch [regex]::Escape($id)) {
                $problems.Add('DND_TESTIDS id not registered in test-ids.ts: ' + $id)
            }
        }
    }

    return $problems
}

# ---------------------------------------------------------------- row 11

function Test-BuildPlanAudit {
    param([Parameter(Mandatory = $true)][string]$Root)

    $problems = New-Object System.Collections.Generic.List[string]
    $stale = [string]$phaseExit.stale_prose_pattern
    $meuId = [string]$phaseExit.meu_id

    # (1) The SOURCE of truth. meu-registry.md and the BUILD_PLAN status table are
    # rendered from this file, so asserting only the rendered output can pass while
    # the YAML still says pending.
    $statusRel = [string]$phaseExit.status_file
    $statusFull = Join-Path $Root $statusRel
    $statusLines = @()
    if (-not (Test-Path -LiteralPath $statusFull)) {
        $problems.Add('missing ' + $statusRel)
    }
    else {
        $statusLines = @(Get-Content -LiteralPath $statusFull)
        $anchor = -1
        for ($i = 0; $i -lt $statusLines.Count; $i++) {
            if ($statusLines[$i] -match ('^\s*-?\s*id:\s*' + [regex]::Escape($meuId) + '\s*$')) { $anchor = $i; break }
        }
        if ($anchor -lt 0) {
            $problems.Add($statusRel + ' has no `id: ' + $meuId + '` entry - the audit target vanished')
        }
        else {
            $statusPattern = [string]$phaseExit.status_field_pattern
            $found = $false
            for ($i = $anchor; $i -lt [Math]::Min($statusLines.Count, $anchor + 60); $i++) {
                if ($i -gt $anchor -and $statusLines[$i] -match '^\s*-\s+row_key:') { break }
                if ($statusLines[$i] -match $statusPattern) { $found = $true; break }
            }
            if (-not $found) {
                $problems.Add($statusRel + ' does not record ' + $meuId + ' as complete - PHASE_EXIT_UPDATES was not applied to the SOURCE, only possibly to the generated files')
            }
        }
    }

    # (2) No stale prose survives anywhere, including in the YAML's free-text notes.
    foreach ($rel in @($phaseExit.stale_prose_files)) {
        $full = Join-Path $Root ([string]$rel)
        $text = Get-Text $full
        if ($null -eq $text) { $problems.Add('missing ' + $rel); continue }
        if ($text -notmatch [regex]::Escape($meuId)) {
            $problems.Add($rel + ' no longer mentions ' + $meuId + ' at all - the audit target vanished')
            continue
        }
        foreach ($hit in @(Select-String -LiteralPath $full -Pattern $stale)) {
            $problems.Add('PHASE_EXIT_UPDATES not applied - stale prose at ' + $rel + ':' + $hit.LineNumber + ' -> ' + $hit.Line.Trim())
        }
    }

    # (3) The phase row and the Next pointer. MEU-49 is the Phase 10 EXIT MEU, so
    # the phase must read Completed and the pointer must advance.
    $nextRel = [string]$phaseExit.next_pointer_file
    $nextFull = Join-Path $Root $nextRel
    $nextText = Get-Text $nextFull
    if ($null -eq $nextText) {
        $problems.Add('missing ' + $nextRel)
    }
    else {
        if ($nextText -notmatch ([string]$phaseExit.phase_row_pattern)) {
            $problems.Add($nextRel + ' Phase 10 status row does not read Completed - MEU-49 is the phase exit MEU')
        }
        # (Round-5 R4-F4.) The pointer is a SENTENCE inside a long paragraph line,
        # not a line of its own. Applying -notmatch to the whole file tested adjacent
        # text, not the deliverable: 'Phase 11' occurs four times and 'MEU-50' twice
        # in docs/BUILD_PLAN.md for unrelated reasons, so the audit passed while the
        # pointer still read `p10-queue-card-dnd (MEU-49)`. Extract the segment first,
        # then assert BOTH directions on it - it must name the successor AND must no
        # longer name this MEU.
        $startTok = [string]$nextPointer.segment_start
        $endTok = [string]$nextPointer.segment_end
        $startIdx = $nextText.IndexOf($startTok)
        if ($startIdx -lt 0) {
            $problems.Add($nextRel + ' has no "' + $startTok + '" pointer segment at all - BUILD_PLAN_NEXT_POINTER cannot be evaluated')
        }
        else {
            $rest = $nextText.Substring($startIdx)
            $lineEnd = $rest.IndexOf("`n")
            if ($lineEnd -ge 0) { $rest = $rest.Substring(0, $lineEnd) }
            $endIdx = $rest.IndexOf($endTok, $startTok.Length)
            $segment = if ($endIdx -ge 0) { $rest.Substring(0, $endIdx + 1) } else { $rest }

            foreach ($pat in @($nextPointer.must_match)) {
                if ($segment -notmatch [regex]::Escape([string]$pat)) {
                    $problems.Add($nextRel + ' Next: segment does not point forward to ' + $pat + ' -> ' + $segment.Trim())
                }
            }
            foreach ($pat in @($nextPointer.must_not_match)) {
                if ($segment -match [regex]::Escape([string]$pat)) {
                    $problems.Add($nextRel + ' Next: segment still names ' + $pat + ' - PHASE_EXIT_UPDATES was not applied to the pointer -> ' + $segment.Trim())
                }
            }
        }
    }

    return $problems
}

# ---------------------------------------------------------------- H1-1

function Test-Unchecked {
    param(
        [Parameter(Mandatory = $true)][string]$Root,
        [string]$BeforeRow = 'H1-1'
    )

    $problems = New-Object System.Collections.Generic.List[string]
    $full = Join-Path $Root ($planRel + '/task.md')
    if (-not (Test-Path -LiteralPath $full)) {
        $problems.Add('missing ' + $planRel + '/task.md')
        return $problems
    }

    $lines = @(Get-Content -LiteralPath $full)

    # H1-1 runs BEFORE the closeout rows, so its own row and every later row are
    # legitimately still open. Scanning them makes the gate unpassable, which is
    # indistinguishable from a gate that always fails.
    $limit = -1
    for ($i = 0; $i -lt $lines.Count; $i++) {
        if ($lines[$i] -match ('^\|\s*' + [regex]::Escape($BeforeRow) + '\s*\|')) { $limit = $i; break }
    }
    if ($limit -lt 0) {
        $problems.Add('task.md has no `| ' + $BeforeRow + ' |` row - the scan boundary vanished, so the gate cannot be scoped')
        return $problems
    }

    $scanned = 0
    for ($i = 0; $i -lt $limit; $i++) {
        $line = $lines[$i]
        if ($line -notmatch '`\[(x| |/|B)\]`') { continue }
        $scanned++
        if ($line -match '`\[ \]`') {
            $problems.Add('task.md:' + ($i + 1) + ' is still unchecked -> ' + $line.Substring(0, [Math]::Min(90, $line.Length)))
        }
        elseif ($line -match '`\[/\]`') {
            $problems.Add('task.md:' + ($i + 1) + ' is still in progress `[/]` -> ' + $line.Substring(0, [Math]::Min(90, $line.Length)))
        }
        elseif ($line -match '`\[B\]`') {
            # AGENTS.md: a valid [B] carries a reproduced error receipt or a named
            # follow-up. A bare [B] is a subjective deferral and is forbidden.
            if (($line -notmatch [regex]::Escape($receiptDir)) -and ($line -notmatch '(?i)follow-up')) {
                $problems.Add('task.md:' + ($i + 1) + ' is `[B]` with no ' + $receiptDir + ' receipt path and no named follow-up - not a valid block')
            }
        }
    }

    if ($scanned -lt 1) {
        $problems.Add('no status cells found above the ' + $BeforeRow + ' row - the gate would pass vacuously')
    }

    return $problems
}

# ---------------------------------------------------------------- H1-4

function Test-ApiUntouched {
    param(
        [AllowEmptyCollection()][string[]]$PorcelainLines = @(),
        [AllowEmptyCollection()][string[]]$Diagnostics = @(),
        [string]$Receipt
    )

    $problems = New-Object System.Collections.Generic.List[string]

    # Round 3 read `git status --porcelain -- packages/api 2>&1`, which merges git's
    # DIAGNOSTICS into the porcelain array; a single warning line then reads as a
    # modified file. Streams are separated at the call site, and each surviving line
    # is validated against the porcelain v1 shape `XY <path>` before being believed.
    foreach ($line in $PorcelainLines) {
        if ([string]::IsNullOrWhiteSpace($line)) { continue }
        if ($line -notmatch '^[ MADRCU?!]{2} .+$') {
            $problems.Add('unparseable git output on stdout (not porcelain v1): ' + $line.Trim())
            continue
        }
        $problems.Add('packages/api/ IS modified - ' + $line.Trim() + ' - the skip basis is false; run tools/export_openapi.py')
    }

    foreach ($line in $Diagnostics) {
        if ([string]::IsNullOrWhiteSpace($line)) { continue }
        Write-Verbose ('git diagnostic (not a modification): ' + $line.Trim())
    }

    if (-not [string]::IsNullOrWhiteSpace($Receipt)) {
        $text = Get-Text $Receipt
        if ($null -eq $text) {
            $problems.Add('missing pytest receipt ' + $Receipt)
        }
        else {
            # `0 failed` and `no errors` must not trip the gate; a non-zero count must.
            foreach ($m in ([regex]'(?im)\b([1-9][0-9]*)\s+(failed|errors?)\b').Matches($text)) {
                $problems.Add('pytest receipt records ' + $m.Value)
            }
            foreach ($m in ([regex]'(?m)^(FAILED|ERROR)\b.*$').Matches($text)) {
                $problems.Add('pytest receipt line: ' + $m.Value.Trim())
            }
        }
    }

    return $problems
}

# ---------------------------------------------------------------- H2-2

function Test-Reflection {
    param([Parameter(Mandatory = $true)][string]$Root)

    $problems = New-Object System.Collections.Generic.List[string]
    if ($reflectionMarkers.Count -lt 1) {
        $problems.Add('REFLECTION_MARKERS is empty in named-sets.json - the gate would pass vacuously')
        return $problems
    }

    $full = Join-Path $Root $reflectionFile
    $text = Get-Text $full
    if ($null -eq $text) {
        $problems.Add('missing REFLECTION_FILE ' + $reflectionFile)
        return $problems
    }

    foreach ($marker in $reflectionMarkers) {
        if ($text -notmatch [regex]::Escape($marker)) {
            $problems.Add('REFLECTION_FILE is missing the marker ' + $marker)
        }
    }

    return $problems
}

# ---------------------------------------------------------------- H2-3

function Test-Metrics {
    param([Parameter(Mandatory = $true)][string]$Root)

    $problems = New-Object System.Collections.Generic.List[string]
    if ($metricsMarkers.Count -lt 1) {
        $problems.Add('METRICS_ROW_MARKERS is empty in named-sets.json - the gate would pass vacuously')
        return $problems
    }

    $full = Join-Path $Root $metricsFile
    if (-not (Test-Path -LiteralPath $full)) {
        $problems.Add('missing METRICS_FILE ' + $metricsFile)
        return $problems
    }

    $rows = @(Get-Content -LiteralPath $full | Where-Object {
            ($_ -match '^\|') -and ($_ -match ('\|\s*' + [regex]::Escape($metricsSlug) + '\s*\|'))
        })
    if ($rows.Count -lt 1) {
        $problems.Add($metricsFile + ' has no table row for METRICS_SLUG ' + $metricsSlug)
        return $problems
    }
    if ($rows.Count -gt 1) {
        $problems.Add($metricsFile + ' has ' + $rows.Count + ' rows for ' + $metricsSlug + ' - the session appended a duplicate')
    }

    $row = [string]$rows[0]
    foreach ($marker in $metricsMarkers) {
        if ($row -notmatch [regex]::Escape($marker)) {
            $problems.Add('the ' + $metricsSlug + ' metrics row is missing ' + $marker)
        }
    }

    return $problems
}

# ---------------------------------------------------------------- H2-5

function Test-CommitDraft {
    param([string]$Path)

    $problems = New-Object System.Collections.Generic.List[string]
    if ([string]::IsNullOrWhiteSpace($Path)) { $Path = [string]$commitDraft.path }

    $text = Get-Text $Path
    if ($null -eq $text) {
        $problems.Add('missing commit draft ' + $Path)
        return $problems
    }
    if ([string]::IsNullOrWhiteSpace($text)) {
        $problems.Add('commit draft ' + $Path + ' is empty - `Get-Content` on it exits 0 and proves nothing')
        return $problems
    }

    foreach ($marker in @($commitDraft.required)) {
        if ($text -notmatch [regex]::Escape([string]$marker)) {
            $problems.Add('commit draft is missing the required marker ' + $marker)
        }
    }
    foreach ($marker in @($commitDraft.forbidden)) {
        if ($text -match [regex]::Escape([string]$marker)) {
            $problems.Add('commit draft carries the forbidden trailer ' + $marker)
        }
    }

    $subject = @($text -split "`r?`n" | Where-Object { -not [string]::IsNullOrWhiteSpace($_) } | Select-Object -First 1)
    $max = [int]$commitDraft.max_subject_chars
    if ($subject.Count -lt 1) {
        $problems.Add('commit draft has no subject line')
    }
    elseif (([string]$subject[0]).Trim().Length -gt $max) {
        $problems.Add('commit draft subject is ' + ([string]$subject[0]).Trim().Length + ' chars, over the ' + $max + '-char limit')
    }

    return $problems
}

# ---------------------------------------------------------------- self-test

function New-File {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][AllowEmptyString()][string]$Content
    )
    $dir = Split-Path -Parent $Path
    if (-not (Test-Path -LiteralPath $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
    Set-Content -LiteralPath $Path -Value $Content -Encoding utf8
}

function New-GoodTree {
    param([Parameter(Mandatory = $true)][string]$Root)

    # --- manifests, built as real JSON so the parsing gate is exercised
    $deps = [ordered]@{}
    $devDeps = [ordered]@{ vitest = '^3.0.0' }
    $lockPackages = [ordered]@{}
    foreach ($p in $dndPackages) {
        $deps[$p.Name] = $p.Range
        $concrete = ($p.Range -replace '^[\^~>=<\s]*', '')
        $lockPackages['node_modules/' + $p.Name] = [ordered]@{ version = $concrete }
    }
    # TESTING_LIBRARY_PACKAGES belong in devDependencies (round-5 R4-F5). Building
    # the good tree from the SAME registered sets the gate reads means a package
    # added to named-sets.json is automatically demanded here too - the fixture can
    # never quietly fall behind the rule it is supposed to satisfy.
    foreach ($p in $tlPackages) {
        $devDeps[$p.Name] = $p.Range
        $concrete = ($p.Range -replace '^[\^~>=<\s]*', '')
        $lockPackages['node_modules/' + $p.Name] = [ordered]@{ version = $concrete; dev = $true }
    }
    $lockPackages[''] = [ordered]@{ name = 'av-kit-ui'; version = '0.1.0'; dependencies = $deps; devDependencies = $devDeps }
    New-File (Join-Path $Root 'ui/package.json') (
        ([ordered]@{ name = 'av-kit-ui'; dependencies = $deps; devDependencies = $devDeps } | ConvertTo-Json -Depth 8))
    New-File (Join-Path $Root 'ui/package-lock.json') (
        ([ordered]@{ lockfileVersion = 3; packages = $lockPackages } | ConvertTo-Json -Depth 8))

    # --- jest-dom matchers wired from a setup file (AC-49.2)
    New-File (Join-Path $Root 'ui/vitest.config.ts') @"
export default { test: { setupFiles: ['./tests/unit/setup.ts', '@testing-library/jest-dom/vitest'] } }
"@

    # --- the migrated unit files: canonical surface, no shim anywhere under ui/.
    #     Built from the SAME registered sets Test-Deps reads, and split the same way:
    #     an interaction file carries the user-event surface, the mount-only file
    #     deliberately does NOT - so the good tree proves the exemption is real rather
    #     than proving a uniform rule the gate no longer states (round-6, R5-F3).
    $mountOnlySet = @{}
    foreach ($rel in $tlMountOnlyFiles) { $mountOnlySet[[string]$rel] = $true }
    foreach ($rel in $tlMigrationFiles) {
        if ($mountOnlySet.ContainsKey([string]$rel)) {
            $mountBody = @"
import { render, screen } from '@testing-library/react'
import { createElement } from 'react'

it('mounts without simulating anything', () => {
  render(createElement('div'))
  expect(screen.getByRole('button')).toBeTruthy()
})
"@
            # Add-DepGuard is a no-op for every file except the ONE the guard lives in,
            # so the good tree satisfies AC-49.2 without the rule being restated here
            # (round-7, R6-F1).
            New-File (Join-Path $Root $rel) (Add-DepGuard -Rel $rel -Content $mountBody)
            continue
        }
        $migratedBody = @"
import { render, screen } from '@testing-library/react'
import { createElement } from 'react'
import userEvent from '@testing-library/user-event'

it('migrated case', async () => {
  const user = userEvent.setup()
  render(createElement('div'))
  await user.click(screen.getByRole('button'))
})
"@
        New-File (Join-Path $Root $rel) (Add-DepGuard -Rel $rel -Content $migratedBody)
    }

    # --- e2e tree: the required AC cases in their named files, plus filler to the floor
    $ids = ($testIds | ForEach-Object { "  " + ($_ -replace '-', '_') + ": '" + $_ + "'," }) -join "`n"
    New-File (Join-Path $Root 'ui/tests/e2e/test-ids.ts') ("export const TEST_IDS = {`n" + $ids + "`n} as const`n")

    $byFile = @{}
    foreach ($id in @($e2eRequired.Keys)) {
        $rel = [string]$e2eRequired[$id]
        if (-not $byFile.ContainsKey($rel)) { $byFile[$rel] = New-Object System.Collections.Generic.List[string] }
        $byFile[$rel].Add("test('" + $id + " drag reorder', async ({ page }) => { await page.mouse.down() })")
    }
    $written = 0
    foreach ($rel in @($byFile.Keys)) {
        New-File (Join-Path $Root $rel) (($byFile[$rel].ToArray()) -join "`n")
        $written += $byFile[$rel].Count
    }
    $filler = $postMeuStaticFloor - $written
    if ($filler -lt 0) { $filler = 0 }
    $fillerText = (1..([Math]::Max(1, $filler)) | ForEach-Object { "test('filler case $_', async ({ page }) => { await page.mouse.up() })" }) -join "`n"
    if ($filler -gt 0) { New-File (Join-Path $Root 'ui/tests/e2e/filler.test.ts') $fillerText }

    # --- phase-exit state: the SOURCE yaml plus both generated files
    New-File (Join-Path $Root ([string]$phaseExit.status_file)) @"
version: 1
phases:
- id: '10'
  name: Queue card UI
  note: MEU-41-47 bound. MEU-49 delivered in session 22.
meus:
- row_key: MEU-49
  id: MEU-49
  slug: gui-queue-dnd
  status: approved
- row_key: MEU-50
  id: MEU-50
  status: pending
"@
    New-File (Join-Path $Root 'docs/BUILD_PLAN.md') @"
# Build plan

| 10 | Queue card UI | Completed (MEU-41-47, MEU-49 bound to p10-queue-card-dnd.) | 2026-09-03 |

Next: Phase 11 sessions 23-26, starting with MEU-50. MEU-49 shipped in session 22.
"@
    New-File (Join-Path $Root '.agent/context/meu-registry.md') "| MEU-49 | gui-queue-dnd | complete |`n"

    # --- task.md: closed rows above H1-1, open rows at and after it
    New-File (Join-Path $Root ($planRel + '/task.md')) @"
| # | task | owner | deliverable | validation | deps | status |
|---|---|---|---|---|---|---|
| 1 | do a thing | coder | d | v | - | ``[x]`` |
| 2 | do another | coder | d | v | 1 | ``[x]`` |
| **H1** | **divider** | | | | | |
| H1-1 | re-read task.md | coder | d | v | 2 | ``[ ]`` |
| H1-2 | later row | coder | d | v | H1-1 | ``[ ]`` |
"@

    $markers = ($reflectionMarkers | ForEach-Object { '## ' + $_ }) -join "`n"
    New-File (Join-Path $Root $reflectionFile) $markers

    $metricsRow = '| 2026-09-03 | ' + $metricsSlug + ' | MEU-49 drag reorder. 460 vitest; Playwright 79. No commit. |'
    New-File (Join-Path $Root $metricsFile) ("# Execution metrics`n`n| Date | Project | Notes |`n|---|---|---|`n" + $metricsRow + "`n")
}

function New-GoodCommitDraft {
    param([Parameter(Mandatory = $true)][string]$Path)
    New-File $Path @"
feat(ui): add dnd-kit pointer drag reorder to the shared queue

Implements MEU-49 (gui-queue-dnd): drag handle, keyboard sensor and ARIA
announcements inside QueueList, with the kebab menu and Alt+Arrow retained
as equal reorder paths and a queue-scoped single-flight gate.
"@
}

if ($SelfTest) {
    $fixtureRoot = Join-Path ([System.IO.Path]::GetTempPath()) ('plan-gates-selftest-' + [guid]::NewGuid().ToString('N'))
    $failures = New-Object System.Collections.Generic.List[string]
    $cases = 0

    function Assert-Pass {
        param([string]$Label, [System.Collections.Generic.List[string]]$Result)
        $script:cases++
        if ($Result.Count -ne 0) {
            $script:failures.Add($Label + ' should PASS but reported: ' + ($Result -join '; '))
        }
    }
    function Assert-Fail {
        param([string]$Label, [System.Collections.Generic.List[string]]$Result, [string]$Expect)
        $script:cases++
        if ($Result.Count -eq 0) {
            $script:failures.Add($Label + ' should FAIL but passed')
        }
        elseif ($Expect -and -not (@($Result) -match $Expect)) {
            $script:failures.Add($Label + ' failed for the wrong reason: ' + ($Result -join '; '))
        }
    }

    try {
        # ---- every gate must PASS on a well-formed tree
        $good = Join-Path $fixtureRoot 'good'
        New-GoodTree -Root $good
        $goodDraft = Join-Path $fixtureRoot 'commit-good.txt'
        New-GoodCommitDraft -Path $goodDraft
        Assert-Pass 'Deps/good'           (Test-Deps -Root $good)
        Assert-Pass 'E2eCensus/good'      (Test-E2eCensus -Root $good)
        Assert-Pass 'BuildPlanAudit/good' (Test-BuildPlanAudit -Root $good)
        Assert-Pass 'Unchecked/good'      (Test-Unchecked -Root $good)
        Assert-Pass 'Reflection/good'     (Test-Reflection -Root $good)
        Assert-Pass 'Metrics/good'        (Test-Metrics -Root $good)
        Assert-Pass 'CommitDraft/good'    (Test-CommitDraft -Path $goodDraft)
        Assert-Pass 'ApiSkip/good'        (Test-ApiUntouched -PorcelainLines @())

        # ---- Deps: declared but never resolved in the lockfile
        $d1 = Join-Path $fixtureRoot 'deps-lock'
        New-GoodTree -Root $d1
        New-File (Join-Path $d1 'ui/package-lock.json') "{ `"lockfileVersion`": 3, `"packages`": {} }"
        Assert-Fail 'Deps/lockfile-unresolved' (Test-Deps -Root $d1) 'does not resolve node_modules/'

        # ---- Deps (R3-F4): a bare NAME mention must NOT satisfy the gate. This is the
        #      round-3 defect: the old substring match passed on any occurrence anywhere.
        $d1b = Join-Path $fixtureRoot 'deps-mention-only'
        New-GoodTree -Root $d1b
        $mention = '{ "lockfileVersion": 3, "comment": "' + ($dndNames -join ' ') + '", "packages": {} }'
        New-File (Join-Path $d1b 'ui/package-lock.json') $mention
        Assert-Fail 'Deps/name-mention-is-not-resolution' (Test-Deps -Root $d1b) 'does not resolve node_modules/'

        # ---- Deps: wrong version range in the manifest
        $d1c = Join-Path $fixtureRoot 'deps-range'
        New-GoodTree -Root $d1c
        # -AsHashtable throughout: these fixtures carry the same empty-string root key
        # a real lockfile does, and object-mode ConvertFrom-Json cannot represent it.
        $pkgObj = Get-Content -LiteralPath (Join-Path $d1c 'ui/package.json') -Raw | ConvertFrom-Json -AsHashtable
        $pkgObj['dependencies'][$dndPackages[0].Name] = '^0.0.1'
        New-File (Join-Path $d1c 'ui/package.json') ($pkgObj | ConvertTo-Json -Depth 8)
        Assert-Fail 'Deps/wrong-range' (Test-Deps -Root $d1c) 'but DND_PACKAGES registers'

        # ---- Deps: right name, wrong resolved major
        $d1d = Join-Path $fixtureRoot 'deps-major'
        New-GoodTree -Root $d1d
        $lockObj = Get-Content -LiteralPath (Join-Path $d1d 'ui/package-lock.json') -Raw | ConvertFrom-Json -AsHashtable
        $lockObj['packages'][('node_modules/' + $dndPackages[0].Name)]['version'] = '99.0.0'
        New-File (Join-Path $d1d 'ui/package-lock.json') ($lockObj | ConvertTo-Json -Depth 8)
        Assert-Fail 'Deps/wrong-major' (Test-Deps -Root $d1d) 'outside the registered range'

        # ---- Deps: runtime dependency parked in devDependencies
        $d1e = Join-Path $fixtureRoot 'deps-dev'
        New-GoodTree -Root $d1e
        $pkgObj2 = Get-Content -LiteralPath (Join-Path $d1e 'ui/package.json') -Raw | ConvertFrom-Json -AsHashtable
        $moved = $dndPackages[0].Name
        $pkgObj2['dependencies'].Remove($moved)
        $pkgObj2['devDependencies'][$moved] = $dndPackages[0].Range
        New-File (Join-Path $d1e 'ui/package.json') ($pkgObj2 | ConvertTo-Json -Depth 8)
        Assert-Fail 'Deps/dev-dependency' (Test-Deps -Root $d1e) 'in devDependencies'

        # ---- Deps: the rejected @dnd-kit/react line crept in
        $d2 = Join-Path $fixtureRoot 'deps-rejected'
        New-GoodTree -Root $d2
        $pkgObj3 = Get-Content -LiteralPath (Join-Path $d2 'ui/package.json') -Raw | ConvertFrom-Json -AsHashtable
        $pkgObj3['dependencies']['@dnd-kit/react'] = '^0.5.0'
        New-File (Join-Path $d2 'ui/package.json') ($pkgObj3 | ConvertTo-Json -Depth 8)
        Assert-Fail 'Deps/rejected-package' (Test-Deps -Root $d2) 'rejected dependency @dnd-kit/react'

        # ---- Deps (R4-F5): a TESTING_LIBRARY_PACKAGES entry was never installed
        $d3 = Join-Path $fixtureRoot 'deps-tl-missing'
        New-GoodTree -Root $d3
        $pkgObj4 = Get-Content -LiteralPath (Join-Path $d3 'ui/package.json') -Raw | ConvertFrom-Json -AsHashtable
        $pkgObj4['devDependencies'].Remove($tlPackages[0].Name)
        New-File (Join-Path $d3 'ui/package.json') ($pkgObj4 | ConvertTo-Json -Depth 8)
        Assert-Fail 'Deps/tl-missing' (Test-Deps -Root $d3) 'devDependencies does not declare'

        # ---- Deps (R4-F5): a TEST-ONLY package parked in `dependencies`. The
        #      mirror image of Deps/dev-dependency: both sections are wrong in one
        #      direction each, so neither check can be satisfied by the other's fix.
        $d4 = Join-Path $fixtureRoot 'deps-tl-runtime'
        New-GoodTree -Root $d4
        $pkgObj5 = Get-Content -LiteralPath (Join-Path $d4 'ui/package.json') -Raw | ConvertFrom-Json -AsHashtable
        $movedTl = $tlPackages[0].Name
        $pkgObj5['devDependencies'].Remove($movedTl)
        $pkgObj5['dependencies'][$movedTl] = $tlPackages[0].Range
        New-File (Join-Path $d4 'ui/package.json') ($pkgObj5 | ConvertTo-Json -Depth 8)
        Assert-Fail 'Deps/tl-wrong-section' (Test-Deps -Root $d4) 'TEST-ONLY'

        # ---- Deps (AC-49.39): the packages were installed but the shim was KEPT.
        #      This is the failure mode the whole row exists to prevent - a suite
        #      with two userEvent surfaces passes every other gate in this file.
        $d5 = Join-Path $fixtureRoot 'deps-shim-kept'
        New-GoodTree -Root $d5
        New-File (Join-Path $d5 'ui/tests/unit/helpers/user-event.ts') "export default {}`n"
        Assert-Fail 'Deps/shim-still-exists' (Test-Deps -Root $d5) 'still exists'

        # ---- Deps (AC-49.39): shim deleted, but a caller still imports the path.
        #      Deleted separately from the file itself so this fixture proves the
        #      IMPORT scan, not the existence check, is what fires.
        $d6 = Join-Path $fixtureRoot 'deps-shim-importer'
        New-GoodTree -Root $d6
        New-File (Join-Path $d6 'ui/tests/unit/leftover.test.ts') "import { userEvent } from './helpers/user-event'`n"
        Assert-Fail 'Deps/shim-importer' (Test-Deps -Root $d6) 'still imports the deleted shim'

        # ---- Deps (AC-49.39): an interaction file was recoded onto the RTL mount but
        #      never picked up the user-event surface. Everything ELSE about the file is
        #      valid, so the assertion can only be satisfied by clause (f) - round 5's
        #      version of this fixture also dropped the RTL import, which meant it passed
        #      for a reason it was not testing (R5-F3 called it a lookalike).
        $d7 = Join-Path $fixtureRoot 'deps-tl-partial'
        New-GoodTree -Root $d7
        New-File (Join-Path $d7 ([string]$tlInteractionFiles[0])) @"
import { render, screen } from '@testing-library/react'
it('no interaction surface', () => { render(null); screen.getByRole('button') })
"@
        Assert-Fail 'Deps/tl-partial-migration' (Test-Deps -Root $d7) 'does not import @testing-library/user-event'

        # ---- Deps (AC-49.39): imported, but called in the deprecated direct form
        $d8 = Join-Path $fixtureRoot 'deps-tl-nosetup'
        New-GoodTree -Root $d8
        New-File (Join-Path $d8 ([string]$tlInteractionFiles[0])) @"
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
it('old form', async () => { render(null); await userEvent.click(screen.getByRole('button')) })
"@
        Assert-Fail 'Deps/tl-no-setup' (Test-Deps -Root $d8) 'never calls userEvent.setup'

        # ---- Deps (round-6, R5-F3): THE false pass. Every round-5 predicate is
        #      satisfied - RTL import, render, screen, user-event import, setup() call -
        #      and the file still mounts through createRoot. Round 5's gate passed this
        #      tree, and so did its exactly-439 count, because nothing was actually
        #      migrated. It must now fail on the retired surface, not on a missing one.
        $d9 = Join-Path $fixtureRoot 'deps-tl-old-style-retained'
        New-GoodTree -Root $d9
        New-File (Join-Path $d9 ([string]$tlInteractionFiles[0])) @"
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { createRoot } from 'react-dom/client'
import { act, createElement } from 'react'

it('looks migrated, is not', async () => {
  const user = userEvent.setup()
  const root = createRoot(document.body)
  act(() => root.render(createElement('div')))
  render(null)
  await user.click(screen.getByRole('button'))
})
"@
        Assert-Fail 'Deps/tl-old-style-retained' (Test-Deps -Root $d9) 'still imports react-dom/client'

        # ---- Deps (round-6, R5-F3): the mirror - the user-event half is perfect and the
        #      RTL MOUNT half is absent, which is what "migrated the click helper only"
        #      looks like on a file that never had a hand-rolled mount to leave behind.
        $d10 = Join-Path $fixtureRoot 'deps-tl-no-rtl'
        New-GoodTree -Root $d10
        New-File (Join-Path $d10 ([string]$tlInteractionFiles[0])) @"
import userEvent from '@testing-library/user-event'
it('user-event only', async () => { const user = userEvent.setup(); await user.click(document.body) })
"@
        Assert-Fail 'Deps/tl-no-rtl-import' (Test-Deps -Root $d10) 'does not import @testing-library/react'

        # ---- Deps (round-6, R5-F3): the registered exemption is REAL. The mount-only
        #      file carries no user-event surface at all and the full gate still passes.
        #      Without this case the exemption could rot into a no-op that nobody notices
        #      because every fixture happens to include user-event anyway.
        $d11 = Join-Path $fixtureRoot 'deps-tl-mount-only'
        New-GoodTree -Root $d11
        New-File (Join-Path $d11 ([string]$tlMountOnlyFiles[0])) @"
import { render, screen } from '@testing-library/react'
it('mount only', () => { render(null); screen.getByRole('button') })
"@
        Assert-Pass 'Deps/tl-mount-only-exempt' (Test-Deps -Root $d11)

        # ---- Deps (round-6, R5-F2): row 2's boundary is REACHABLE. This is the tree at
        #      the moment row 2 closes - packages installed, jest-dom wired, and NOTHING
        #      of row 2a done yet: the shim is present and every migration file is still
        #      on the old surface. -Mode Packages must PASS (row 2 can close) and -Mode
        #      Full must FAIL (row 2a is genuinely still owed). Round 5 had only the one
        #      gate, so this tree failed row 2's own validation and the task could not be
        #      executed as written.
        $d12 = Join-Path $fixtureRoot 'deps-pre-migration'
        New-GoodTree -Root $d12
        New-File (Join-Path $d12 'ui/tests/unit/helpers/user-event.ts') "export default {}`n"
        foreach ($rel in $tlMigrationFiles) {
            $preBody = @"
import { createRoot } from 'react-dom/client'
import { act, createElement } from 'react'
import { userEvent } from './helpers/user-event'
it('pre-migration', async () => { const root = createRoot(document.body); act(() => root.render(createElement('div'))) })
"@
            # The narrowed guard IS part of this tree: row 2 delivers it, and row 2a - the
            # only row this fixture leaves undone - does not. Round 6 wrote generic
            # pre-migration lines over the guard file and still asserted a Packages-mode
            # PASS, which is precisely the false pass R6-F1 reproduced.
            New-File (Join-Path $d12 ([string]$rel)) (Add-DepGuard -Rel $rel -Content $preBody)
        }
        Assert-Pass 'Deps/packages-mode-pre-migration' (Test-Deps -Root $d12 -Mode Packages)
        Assert-Fail 'Deps/full-mode-pre-migration' (Test-Deps -Root $d12 -Mode Full) 'still exists'

        # ---- Deps (round-7, R6-F1): the four shapes of a MISSING AC-49.2. All four are
        #      PACKAGES-mode failures, because row 2 owns the guard change - round 6 asserted
        #      the row-2 gate and never read the file, so all four passed it.
        $guardBase = @"
import { render, screen } from '@testing-library/react'
import { createElement } from 'react'
import userEvent from '@testing-library/user-event'

it('migrated case', async () => {
  const user = userEvent.setup()
  render(createElement('div'))
  await user.click(screen.getByRole('button'))
})
"@

        # (i) nobody touched the guard. This is the tree that exists the moment the three
        #     DND_PACKAGES land, and in it the whole unit suite fails on a pre-existing
        #     assertion that has nothing to do with MEU-49.
        $d14 = Join-Path $fixtureRoot 'deps-guard-broad'
        New-GoodTree -Root $d14
        New-File (Join-Path $d14 ([string]$depGuard.file)) ($guardBase + @"

  it('AC-49.2 no virtualization dependency', () => {
    // MEU-49 supersession, docs/build-plan/10-queue-card-ui.md:254-256
    expect(names.filter((name) => /dnd-kit|react-virtual/.test(name))).toEqual([])
  })
"@)
        Assert-Fail 'Deps/dep-guard-still-broad' (Test-Deps -Root $d14 -Mode Packages) 'still asserts the broad'

        # (ii) the assertion was DELETED rather than narrowed - the G36_RULE violation the
        #      DND_DEP_GUARD_SUPERSESSION note names explicitly. It removes the broad regex,
        #      so case (i)'s check cannot catch it.
        $d15 = Join-Path $fixtureRoot 'deps-guard-deleted'
        New-GoodTree -Root $d15
        New-File (Join-Path $d15 ([string]$depGuard.file)) $guardBase
        Assert-Fail 'Deps/dep-guard-deleted' (Test-Deps -Root $d15 -Mode Packages) 'does not narrow the dependency guard'

        # (iii) narrowed correctly, no supersession comment. A narrowed assertion with no
        #       stated reason is indistinguishable from quietly weakening the test.
        $d16 = Join-Path $fixtureRoot 'deps-guard-nocomment'
        New-GoodTree -Root $d16
        New-File (Join-Path $d16 ([string]$depGuard.file)) ($guardBase + @"

  it('AC-49.2 no virtualization dependency', () => {
    expect(names.filter((name) => /react-virtual/.test(name))).toEqual([])
  })
"@)
        Assert-Fail 'Deps/dep-guard-no-supersession' (Test-Deps -Root $d16 -Mode Packages) 'has no in-place'

        # (iv) the comment exists but sits at the top of the file, far from what it
        #      supersedes. This is what makes "in-place" executable rather than decorative:
        #      DND_DEP_GUARD_SUPERSESSION cites the MEU-45 precedent, whose comment sits six
        #      lines from its assertion. Without this case the window is never exercised.
        $d17 = Join-Path $fixtureRoot 'deps-guard-comment-far'
        New-GoodTree -Root $d17
        $guardFiller = (1..30 | ForEach-Object { "// unrelated line $_" }) -join "`n"
        New-File (Join-Path $d17 ([string]$depGuard.file)) (
            "// MEU-49 supersession, docs/build-plan/10-queue-card-ui.md:254-256`n" +
            $guardFiller + "`n" + $guardBase + @"

  it('AC-49.2 no virtualization dependency', () => {
    expect(names.filter((name) => /react-virtual/.test(name))).toEqual([])
  })
"@)
        Assert-Fail 'Deps/dep-guard-comment-not-in-place' (Test-Deps -Root $d17 -Mode Packages) 'within 12 lines'

        # ---- Deps (AC-49.2): the four packages are installed and jest-dom is never
        #      registered, so toBeDisabled() throws in every migrated assertion. This is
        #      a PACKAGES-mode failure because row 2 owns the wiring.
        $d13 = Join-Path $fixtureRoot 'deps-no-jestdom'
        New-GoodTree -Root $d13
        New-File (Join-Path $d13 'ui/vitest.config.ts') "export default { test: { setupFiles: ['./tests/unit/setup.ts'] } }`n"
        Assert-Fail 'Deps/no-jestdom-setup' (Test-Deps -Root $d13 -Mode Packages) 'jest-dom/vitest'

        # ---- Deps (round-6, R5-F3): the partition itself. Fed synthetic sets so the
        #      check is proved without a tree - a file classified in neither bucket
        #      silently loses its user-event obligation, and one in both is ambiguous.
        Assert-Fail 'Deps/tl-partition-gap' (Test-TlPartition -Migration @('a.ts', 'b.ts') -Interaction @('a.ts') -MountOnly @()) 'in neither'
        Assert-Fail 'Deps/tl-partition-overlap' (Test-TlPartition -Migration @('a.ts') -Interaction @('a.ts') -MountOnly @('a.ts')) 'in BOTH'
        Assert-Pass 'Deps/tl-partition-real' (Test-TlPartition -Migration $tlMigrationFiles -Interaction $tlInteractionFiles -MountOnly $tlMountOnlyFiles)

        # ---- E2eCensus: one case below the POST-MEU floor
        $e1 = Join-Path $fixtureRoot 'e2e-short'
        New-GoodTree -Root $e1
        Remove-Item -LiteralPath (Join-Path $e1 'ui/tests/e2e/filler.test.ts') -Force -ErrorAction SilentlyContinue
        Assert-Fail 'E2eCensus/below-floor' (Test-E2eCensus -Root $e1) 'below E2E_POST_MEU_STATIC_FLOOR'

        # ---- E2eCensus (R3-F5): the count floor is met but a required AC case is absent.
        #      This is exactly the unstarted-tree shape the round-3 gate passed.
        $e1b = Join-Path $fixtureRoot 'e2e-no-ac'
        New-GoodTree -Root $e1b
        $missingId = @($e2eRequired.Keys)[0]
        $missingRel = [string]$e2eRequired[$missingId]
        $kept = @(Get-Content -LiteralPath (Join-Path $e1b $missingRel) | Where-Object { $_ -notmatch [regex]::Escape($missingId) })
        New-File (Join-Path $e1b $missingRel) (($kept + @("test('unrelated case', async ({ page }) => { await page.mouse.up() })")) -join "`n")
        Assert-Fail 'E2eCensus/required-ac-absent' (Test-E2eCensus -Root $e1b) ('carries ' + [regex]::Escape($missingId))

        # ---- E2eCensus: the AC exists, but in the WRONG spec file
        $e1c = Join-Path $fixtureRoot 'e2e-wrong-file'
        New-GoodTree -Root $e1c
        New-File (Join-Path $e1c $missingRel) (($kept) -join "`n")
        Add-Content -LiteralPath (Join-Path $e1c 'ui/tests/e2e/filler.test.ts') -Value ("test('" + $missingId + " in the wrong file', async ({ page }) => {})")
        Assert-Fail 'E2eCensus/required-ac-wrong-file' (Test-E2eCensus -Root $e1c) ('carries ' + [regex]::Escape($missingId))

        # ---- E2eCensus: dragTo() used
        $e2 = Join-Path $fixtureRoot 'e2e-dragto'
        New-GoodTree -Root $e2
        Add-Content -LiteralPath (Join-Path $e2 'ui/tests/e2e/filler.test.ts') -Value "await handle.dragTo(target)"
        Assert-Fail 'E2eCensus/dragTo' (Test-E2eCensus -Root $e2) 'E2E_DRAG_DRIVER violation'

        # ---- E2eCensus: testid never registered
        $e3 = Join-Path $fixtureRoot 'e2e-testid'
        New-GoodTree -Root $e3
        New-File (Join-Path $e3 'ui/tests/e2e/test-ids.ts') "export const TEST_IDS = {} as const`n"
        Assert-Fail 'E2eCensus/testid-missing' (Test-E2eCensus -Root $e3) 'not registered in test-ids\.ts'

        # ---- BuildPlanAudit: stale prose left behind
        $b1 = Join-Path $fixtureRoot 'buildplan-stale'
        New-GoodTree -Root $b1
        New-File (Join-Path $b1 'docs/BUILD_PLAN.md') @"
# Build plan

| 10 | Queue card UI | Completed | 2026-09-03 |

Next: Phase 11 / MEU-50. Phase 10: MEU-49 remains.
"@
        Assert-Fail 'BuildPlanAudit/stale' (Test-BuildPlanAudit -Root $b1) 'stale prose'

        # ---- BuildPlanAudit (R3-F4): the two GENERATED files were hand-cleaned but the
        #      SOURCE yaml still says pending. The round-3 gate passed on exactly this.
        $b1b = Join-Path $fixtureRoot 'buildplan-source-stale'
        New-GoodTree -Root $b1b
        $yaml = Get-Content -LiteralPath (Join-Path $b1b ([string]$phaseExit.status_file)) -Raw
        New-File (Join-Path $b1b ([string]$phaseExit.status_file)) ($yaml -replace 'status: approved', 'status: pending')
        Assert-Fail 'BuildPlanAudit/source-not-updated' (Test-BuildPlanAudit -Root $b1b) 'does not record MEU-49 as complete'

        # ---- BuildPlanAudit: the Next pointer never advanced
        $b1c = Join-Path $fixtureRoot 'buildplan-next'
        New-GoodTree -Root $b1c
        New-File (Join-Path $b1c 'docs/BUILD_PLAN.md') @"
# Build plan

| 10 | Queue card UI | Completed | 2026-09-03 |

Next: nothing scheduled. MEU-49 shipped in session 22.
"@
        Assert-Fail 'BuildPlanAudit/next-pointer' (Test-BuildPlanAudit -Root $b1c) 'does not point forward to'

        # ---- BuildPlanAudit (R4-F4): the exact round-4 defect. The BODY of the file
        #      carries `Phase 11` and `MEU-50` for unrelated reasons (a grouping line,
        #      a phase table row) while the `Next:` pointer itself is still stale. The
        #      whole-file -notmatch predicate passed on precisely this shape; only the
        #      segment-scoped check can see it.
        $b1e = Join-Path $fixtureRoot 'buildplan-next-decoy'
        New-GoodTree -Root $b1e
        New-File (Join-Path $b1e 'docs/BUILD_PLAN.md') @"
# Build plan

| 10 | Queue card UI | Completed | 2026-09-03 |
| 11 | Page layout | Planned (MEU-50 first) | 2026-09-10 |

Phase 11 grouping: MEU-50, MEU-55. Next: ``p10-queue-card-dnd (MEU-49)``, then Phase 11 sessions 23-26.
"@
        Assert-Fail 'BuildPlanAudit/next-decoy' (Test-BuildPlanAudit -Root $b1e) 'Next: segment still names'

        # ---- BuildPlanAudit: the phase row still reads In Progress
        $b1d = Join-Path $fixtureRoot 'buildplan-phase-row'
        New-GoodTree -Root $b1d
        New-File (Join-Path $b1d 'docs/BUILD_PLAN.md') @"
# Build plan

| 10 | Queue card UI | In Progress | 2026-09-03 |

Next: Phase 11 sessions 23-26, starting with MEU-50. MEU-49 shipped in session 22.
"@
        Assert-Fail 'BuildPlanAudit/phase-row' (Test-BuildPlanAudit -Root $b1d) 'does not read Completed'

        # ---- BuildPlanAudit: the MEU vanished from the registry
        $b2 = Join-Path $fixtureRoot 'buildplan-gone'
        New-GoodTree -Root $b2
        New-File (Join-Path $b2 '.agent/context/meu-registry.md') "| MEU-48 | done |`n"
        Assert-Fail 'BuildPlanAudit/absent' (Test-BuildPlanAudit -Root $b2) 'no longer mentions MEU-49'

        # ---- Unchecked: an implementation row left open
        $u1 = Join-Path $fixtureRoot 'task-open'
        New-GoodTree -Root $u1
        $t = Get-Content -LiteralPath (Join-Path $u1 ($planRel + '/task.md')) -Raw
        New-File (Join-Path $u1 ($planRel + '/task.md')) ($t -replace '\| 2 \| do another \| coder \| d \| v \| 1 \| `\[x\]` \|', '| 2 | do another | coder | d | v | 1 | `[ ]` |')
        Assert-Fail 'Unchecked/open-row' (Test-Unchecked -Root $u1) 'is still unchecked'

        # ---- Unchecked: an in-progress row is not done either
        $u2 = Join-Path $fixtureRoot 'task-inprogress'
        New-GoodTree -Root $u2
        $t2 = Get-Content -LiteralPath (Join-Path $u2 ($planRel + '/task.md')) -Raw
        New-File (Join-Path $u2 ($planRel + '/task.md')) ($t2 -replace '\| 2 \| do another \| coder \| d \| v \| 1 \| `\[x\]` \|', '| 2 | do another | coder | d | v | 1 | `[/]` |')
        Assert-Fail 'Unchecked/in-progress-row' (Test-Unchecked -Root $u2) 'is still in progress'

        # ---- Unchecked: a bare [B] with no receipt and no follow-up is not a valid block
        $u3 = Join-Path $fixtureRoot 'task-bare-block'
        New-GoodTree -Root $u3
        $t3 = Get-Content -LiteralPath (Join-Path $u3 ($planRel + '/task.md')) -Raw
        New-File (Join-Path $u3 ($planRel + '/task.md')) ($t3 -replace '\| 2 \| do another \| coder \| d \| v \| 1 \| `\[x\]` \|', '| 2 | do another | coder | d | v | 1 | `[B]` |')
        Assert-Fail 'Unchecked/bare-block' (Test-Unchecked -Root $u3) 'not a valid block'

        # ---- Unchecked: an evidence-carrying [B] IS acceptable
        $u4 = Join-Path $fixtureRoot 'task-good-block'
        New-GoodTree -Root $u4
        $t4 = Get-Content -LiteralPath (Join-Path $u4 ($planRel + '/task.md')) -Raw
        New-File (Join-Path $u4 ($planRel + '/task.md')) ($t4 -replace '\| 2 \| do another \| coder \| d \| v \| 1 \| `\[x\]` \|', ('| 2 | do another | coder | d | v | 1 | `[B]` ' + $receiptDir + 'e2e.txt |'))
        Assert-Pass 'Unchecked/evidence-block' (Test-Unchecked -Root $u4)

        # ---- Unchecked (R3-F4): H1-1's own row and the later closeout rows are open by
        #      construction in every fixture above; if the gate scanned them, the /good
        #      case could never pass. Prove the boundary exists rather than assuming it.
        $cases++
        $boundaryProbe = Test-Unchecked -Root $good -BeforeRow 'H1-2'
        if (-not (@($boundaryProbe) -match 'is still unchecked')) {
            $failures.Add('Unchecked/boundary: moving the scan boundary past H1-1 did not surface H1-1 as unchecked - the scoping is not actually doing anything')
        }

        # ---- Unchecked: a task.md with no H1-1 row at all is fail-closed
        $u5 = Join-Path $fixtureRoot 'task-no-anchor'
        New-GoodTree -Root $u5
        New-File (Join-Path $u5 ($planRel + '/task.md')) "| 1 | a | coder | d | v | - | ``[x]`` |`n"
        Assert-Fail 'Unchecked/missing-anchor' (Test-Unchecked -Root $u5) 'scan boundary vanished'

        # ---- ApiSkip: a modified api file
        Assert-Fail 'ApiSkip/modified' (Test-ApiUntouched -PorcelainLines @(' M packages/api/routes.py')) 'IS modified'

        # ---- ApiSkip (R3-F4): a git DIAGNOSTIC must not read as a modification. This is
        #      the `2>&1` stream-merge defect: the warning arrives on stderr, is now
        #      passed separately, and the gate stays green.
        Assert-Pass 'ApiSkip/diagnostic-on-stderr' (Test-ApiUntouched -PorcelainLines @() -Diagnostics @('warning: could not open directory: Permission denied'))

        # ---- ApiSkip: a non-porcelain line on STDOUT is reported as unparseable, not
        #      silently swallowed and not misread as a modification.
        Assert-Fail 'ApiSkip/unparseable-stdout' (Test-ApiUntouched -PorcelainLines @('warning: leaked onto stdout')) 'unparseable git output'

        # ---- ApiSkip: a clean receipt must not trip on "0 failed"
        $r0 = Join-Path $fixtureRoot 'pytest-clean.txt'
        New-File $r0 "=== 214 passed, 0 failed in 12.03s ===`n"
        Assert-Pass 'ApiSkip/clean-receipt' (Test-ApiUntouched -PorcelainLines @() -Receipt $r0)

        # ---- ApiSkip: a dirty receipt must trip
        $r1 = Join-Path $fixtureRoot 'pytest-dirty.txt'
        New-File $r1 "FAILED tests/test_reorder.py::test_permutation`n=== 3 failed, 211 passed ===`n"
        Assert-Fail 'ApiSkip/dirty-receipt' (Test-ApiUntouched -PorcelainLines @() -Receipt $r1) 'pytest receipt'

        # ---- ApiSkip: a receipt that does not exist is a failure, not a pass
        Assert-Fail 'ApiSkip/missing-receipt' (Test-ApiUntouched -PorcelainLines @() -Receipt (Join-Path $fixtureRoot 'nope.txt')) 'missing pytest receipt'

        # ---- Reflection: one marker missing
        $f1 = Join-Path $fixtureRoot 'reflection-partial'
        New-GoodTree -Root $f1
        $partial = (($reflectionMarkers | Select-Object -SkipLast 1) | ForEach-Object { '## ' + $_ }) -join "`n"
        New-File (Join-Path $f1 $reflectionFile) $partial
        Assert-Fail 'Reflection/partial' (Test-Reflection -Root $f1) 'missing the marker'

        # ---- Reflection: the file does not exist at all
        $f2 = Join-Path $fixtureRoot 'reflection-absent'
        New-GoodTree -Root $f2
        Remove-Item -LiteralPath (Join-Path $f2 $reflectionFile) -Force
        Assert-Fail 'Reflection/absent' (Test-Reflection -Root $f2) 'missing REFLECTION_FILE'

        # ---- Metrics: the row was never appended
        $m1 = Join-Path $fixtureRoot 'metrics-absent'
        New-GoodTree -Root $m1
        New-File (Join-Path $m1 $metricsFile) "# Execution metrics`n`n| Date | Project | Notes |`n|---|---|---|`n"
        Assert-Fail 'Metrics/row-absent' (Test-Metrics -Root $m1) 'has no table row for METRICS_SLUG'

        # ---- Metrics: the row exists but is a stub
        $m2 = Join-Path $fixtureRoot 'metrics-stub'
        New-GoodTree -Root $m2
        New-File (Join-Path $m2 $metricsFile) ("# Execution metrics`n`n| Date | Project | Notes |`n|---|---|---|`n| 2026-09-03 | " + $metricsSlug + " | TBD |`n")
        Assert-Fail 'Metrics/stub-row' (Test-Metrics -Root $m2) 'metrics row is missing'

        # ---- Metrics: a duplicated row is a defect too
        $m3 = Join-Path $fixtureRoot 'metrics-dupe'
        New-GoodTree -Root $m3
        $mrow = '| 2026-09-03 | ' + $metricsSlug + ' | MEU-49 drag reorder. 460 vitest; Playwright 79. No commit. |'
        New-File (Join-Path $m3 $metricsFile) ("# Execution metrics`n`n| Date | Project | Notes |`n|---|---|---|`n" + $mrow + "`n" + $mrow + "`n")
        Assert-Fail 'Metrics/duplicate-row' (Test-Metrics -Root $m3) 'appended a duplicate'

        # ---- CommitDraft: absent
        Assert-Fail 'CommitDraft/absent' (Test-CommitDraft -Path (Join-Path $fixtureRoot 'no-such-draft.txt')) 'missing commit draft'

        # ---- CommitDraft: empty (the exact shape a bare Get-Content receipt passes)
        $c1 = Join-Path $fixtureRoot 'commit-empty.txt'
        New-File $c1 "   `n"
        Assert-Fail 'CommitDraft/empty' (Test-CommitDraft -Path $c1) 'is empty'

        # ---- CommitDraft: an AI attribution trailer crept in
        $c2 = Join-Path $fixtureRoot 'commit-trailer.txt'
        New-GoodCommitDraft -Path $c2
        Add-Content -LiteralPath $c2 -Value "`nCo-Authored-By: someone <noreply@example.com>"
        Assert-Fail 'CommitDraft/trailer' (Test-CommitDraft -Path $c2) 'forbidden trailer'

        # ---- CommitDraft: a required marker missing
        $c3 = Join-Path $fixtureRoot 'commit-nomeu.txt'
        New-File $c3 "feat(ui): add drag reorder`n`nNo MEU id anywhere in the body.`n"
        Assert-Fail 'CommitDraft/missing-marker' (Test-CommitDraft -Path $c3) 'required marker MEU-49'

        # ---- CommitDraft: an over-long subject
        $c4 = Join-Path $fixtureRoot 'commit-long.txt'
        New-File $c4 ("feat(ui): " + ('x' * 90) + " MEU-49`n")
        Assert-Fail 'CommitDraft/long-subject' (Test-CommitDraft -Path $c4) 'over the'

        # ---- the named sets the gates depend on must not be empty
        $cases++
        if ($dndPackages.Count -lt 1) { $failures.Add('DND_PACKAGES is empty or unparseable - Deps would pass vacuously') }
        $cases++
        if ($testIds.Count -lt 1) { $failures.Add('DND_TESTIDS is empty - the testid clause would pass vacuously') }
        $cases++
        if ($e2eRequired.Count -lt 1) { $failures.Add('E2E_REQUIRED_CASES is empty - E2eCensus would fall back to a bare count') }
        $cases++
        if ($postMeuStaticFloor -le [int]$sets.E2E_STATIC_CASE_FLOOR.value) {
            $failures.Add('E2E_POST_MEU_STATIC_FLOOR ' + $postMeuStaticFloor + ' is not above the PRE-MEU E2E_STATIC_CASE_FLOOR - the post-MEU floor would be satisfied by the unstarted tree')
        }
        $cases++
        if ($reflectionMarkers.Count -lt 1) { $failures.Add('REFLECTION_MARKERS is empty - Reflection would pass vacuously') }
        $cases++
        if ($metricsMarkers.Count -lt 1) { $failures.Add('METRICS_ROW_MARKERS is empty - Metrics would pass vacuously') }
        $cases++
        if (@($commitDraft.required).Count -lt 1 -or @($commitDraft.forbidden).Count -lt 1) {
            $failures.Add('COMMIT_DRAFT_MARKERS has an empty required or forbidden list - CommitDraft would pass vacuously')
        }
    }
    finally {
        Remove-Item -LiteralPath $fixtureRoot -Recurse -Force -ErrorAction SilentlyContinue
    }

    if ($failures.Count -gt 0) {
        foreach ($f in $failures) { Write-Error $f -ErrorAction Continue }
        Write-Output ('FAIL: PLAN_GATE_SCRIPT self-test (' + $failures.Count + ' of ' + $cases + ' cases)')
        exit 1
    }
    Write-Output ('PASS: PLAN_GATE_SCRIPT self-test (' + $cases + ' cases across 8 gates)')
    exit 0
}

if ([string]::IsNullOrWhiteSpace($Gate)) {
    Write-Error '-Gate is required (Deps | DepsPackages | E2eCensus | BuildPlanAudit | Unchecked | ApiSkip | Reflection | Metrics | CommitDraft), or use -SelfTest'
    exit 1
}

switch ($Gate) {
    # Row 2 runs -Gate DepsPackages, row 2a runs -Gate Deps. Round-6 (R5-F2): one
    # gate covering both rows made row 2's declared boundary unreachable, because
    # row 2a - which depends on row 2 - produces half of what it checked.
    'Deps' { $result = Test-Deps -Root $repoRoot -Mode Full }
    'DepsPackages' { $result = Test-Deps -Root $repoRoot -Mode Packages }
    'E2eCensus' { $result = Test-E2eCensus -Root $repoRoot }
    'BuildPlanAudit' { $result = Test-BuildPlanAudit -Root $repoRoot }
    'Unchecked' { $result = Test-Unchecked -Root $repoRoot }
    'Reflection' { $result = Test-Reflection -Root $repoRoot }
    'Metrics' { $result = Test-Metrics -Root $repoRoot }
    'CommitDraft' { $result = Test-CommitDraft -Path $ReceiptPath }
    'ApiSkip' {
        # Streams are separated: git's DIAGNOSTICS (warnings, config notices) go to a
        # temp file and are never mistaken for porcelain records. `2>&1` here was the
        # round-3 defect that reported two fictitious API modifications.
        $errFile = Join-Path ([System.IO.Path]::GetTempPath()) ('git-status-err-' + [guid]::NewGuid().ToString('N') + '.txt')
        Push-Location -LiteralPath $repoRoot
        try {
            $porcelain = @(& git status --porcelain -- packages/api 2> $errFile)
            $gitCode = $LASTEXITCODE
        }
        finally { Pop-Location }
        $diagnostics = @()
        if (Test-Path -LiteralPath $errFile) {
            $diagnostics = @(Get-Content -LiteralPath $errFile -ErrorAction SilentlyContinue)
            Remove-Item -LiteralPath $errFile -Force -ErrorAction SilentlyContinue
        }
        if ($gitCode -ne 0) {
            Write-Error ('git status failed (exit ' + $gitCode + '): ' + (($porcelain + $diagnostics) -join ' | '))
            exit 1
        }
        $result = Test-ApiUntouched -PorcelainLines $porcelain -Diagnostics $diagnostics -Receipt $ReceiptPath
    }
}

if ($result.Count -gt 0) {
    foreach ($f in $result) { Write-Error $f -ErrorAction Continue }
    Write-Output ('FAIL: PLAN_GATE_SCRIPT ' + $Gate + ' (' + $result.Count + ' problems)')
    exit 1
}

Write-Output ('PASS: PLAN_GATE_SCRIPT ' + $Gate)
exit 0
