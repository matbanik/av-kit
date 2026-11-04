<#
.SYNOPSIS
  Correction blast-radius census for the plan-review correction passes (plan-corrections.md Step 5c).

.DESCRIPTION
  Two independent sweeps over BOTH plan files.

  1. LITERALS (`-Gate Literals`). For every literal, term, count, threshold or predicate that a
     correction pass changed, sweep the OLD value (to find sites the correction missed) and the NEW
     value (to confirm every site now agrees), plus the declared semantic variants that a
     fixed-string sweep cannot find on its own. Reporting only; it never fails the run, because a
     surviving old value may be a legitimate historical mention that the correction log dispositions.

  2. UNIVERSAL CLAIMS (`-Gate S6`). Round 4. The plan makes two universal claims about its own name
     inventory; this gate enforces them instead of restating them. It is fail-closed - a finding
     exits 1 - because round 3 found the round-2 version of both claims false on its face:
       (a) any line making a universal claim about NAMEs must carry a qualifier token, and
       (b) every SCREAMING_SNAKE token in either plan file must resolve to a `named-sets.json` key,
           to `INHERITED_NAMES.value`, or to `INHERITED_NAMES.non_set_token_list`.
     (b) is the check the round-2 self-review did by hand; it had already gone stale by round 3
     (three undeclared tokens), which is the whole argument for it being a script.

  Every sweep is unfiltered and written whole to its own receipt under -ReceiptDir. Nothing is
  truncated: the hit you did not expect is the entire point.

  `rg` exit codes: 0 = matched, 1 = no match, >1 = a real execution error. Only >1 aborts.
  For an OLD value, 1 is the good outcome. For a NEW value, 1 means the edit did not land.

.PARAMETER ReceiptDir
  Where the per-value receipts are written. Defaults to C:/Temp/av-kit/census.

.PARAMETER Gate
  `All` (default), `Literals`, or `S6`.

.PARAMETER SelfTest
  Prove the harness itself reports what it claims: a value planted in a fixture file is found, an
  absent value is reported absent, a regex metacharacter is matched literally, a leading-dash value
  is swept rather than parsed as an rg flag, an unqualified universal claim and an unresolved token
  are each reported, their qualified/resolved counterparts are not, and - case 10 - the REAL plan
  files against the REAL `named-sets.json` pass S6, so "the inventory claim is unsatisfiable" is a
  claim this script refutes on every run.
#>
[CmdletBinding()]
param(
    [string]$ReceiptDir = 'C:/Temp/av-kit/census',
    [ValidateSet('All', 'Literals', 'S6')][string]$Gate = 'All',
    [switch]$SelfTest
)

$ErrorActionPreference = 'Stop'

# The two plan files carry en dashes in AC ranges. Building the dash from its code point keeps this
# script pure ASCII, so it cannot be corrupted by an encoding-unaware editor or shell redirect.
$D = [string][char]0x2013

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '../../../..')).Path
$plan = Join-Path $PSScriptRoot 'implementation-plan.md'
$task = Join-Path $PSScriptRoot 'task.md'
$namesPath = Join-Path $PSScriptRoot 'named-sets.json'

# ---------------------------------------------------------------------------
# `superseded_by` marks an entry whose `new` value a LATER round replaced in turn (the
# C-chain: C4.new -> C8.old, C8.new -> C11.old). Its `new` is therefore expected to sweep
# to zero hits, which is not the "edit did not land" signal the report otherwise raises -
# it is reported separately, and an entry that declares a supersession which did NOT land
# (hits > 0) is the finding instead. Added round 6, when the chain reached three links.
# The census table. `old` is what the correction replaced (expected to be gone,
# or to survive only at sites this log dispositions); `new` is what replaced it
# (expected to be present). `variants` are the other phrasings the same value
# plausibly takes in these two files - declared by hand, because a fixed-string
# sweep cannot discover them.
#
# When a later round supersedes an earlier round's NEW value, the entry is
# rewritten rather than appended to: this table is a sweep of the CURRENT state,
# not a changelog. The changelog is the rolling review file.
# ---------------------------------------------------------------------------
$census = @(
    # ---- F1: single-flight reorder gate
    @{ f = 'F1'; slug = 'single-flight-rule'; old = ''; new = 'REORDER_SINGLE_FLIGHT_RULE'
        variants = @('createSingleFlight', 'reorder-single-flight.ts', 'reorder-single-flight.test.ts', 'tryAcquire', 'single-flight') }
    @{ f = 'F1'; slug = 'single-flight-acs'; old = ''; new = 'AC-49.31'
        variants = @('AC-49.32', 'AC-49.33', 'AC-49.34', 'AC-49.35') }
    @{ f = 'F1'; slug = 'single-flight-rows'; old = ''; new = '| 4a |'; variants = @('4a') }

    # ---- F2: move-to-index semantics
    @{ f = 'F2'; slug = 'move-to-index-after-removal'; old = 'after removal'; new = 'PRE-MOVE'
        variants = @('pre-move', 'FINAL index', 'final index', 'arrayMove') }

    # ---- F3: touch-action
    @{ f = 'F3'; slug = 'touch-action'; old = ''; new = 'DND_TOUCH_ACTION_RULE'
        variants = @('touch-none', "touchAction === 'none'", 'AC-49.36') }

    # ---- F4: E2E run command
    @{ f = 'F4'; slug = 'e2e-run-command'; old = 'npx --prefix ui playwright test'; new = 'npm --prefix ui run test:e2e'
        variants = @('E2E_RUN_COMMAND', 'playwright test') }

    # ---- F5: red-phase oracle
    @{ f = 'F5'; slug = 'red-phase-oracle'; old = ''; new = 'RED_PHASE_ORACLE'
        variants = @('assert-red-phase.ps1', 'RED_PHASE_REQUIRED_ACS', 'RED_PHASE_TEST_FILES', '| 3a |', '-Census') }

    # ---- F6: GUI element compliance
    @{ f = 'F6'; slug = 'feedback-tier'; old = ''; new = 'REORDER_FEEDBACK_TIER'
        variants = @('TESTING_LIBRARY_ADOPTION', 'GUI_ENFORCEMENT_FALLBACK') }

    # ---- F7: exact negative orders
    @{ f = 'F7'; slug = 'exact-order'; old = 'the order changed'; new = '[B,C,A,D]'
        variants = @('[A,B,C,D]', '[B,A,C,D]', '[A,D,B,C]') }

    # ---- F8: baseline and inheritance
    @{ f = 'F8'; slug = 'vitest-baseline'; old = '438'; new = '439'
        variants = @('VITEST_BASELINE_COUNT') }
    @{ f = 'F8'; slug = 'inheritance-meu'; old = 'MEU-56'; new = 'MEU-55'
        variants = @('inherit') }

    # ---- Self-review 1: oracle clause (e)
    @{ f = 'S1'; slug = 'required-ac-ids'; old = ''; new = '-RequiredAcIds'
        variants = @('clause (e)', 'RED_PHASE_REQUIRED_ACS') }

    # ---- Self-review 2: row 3a placeholder
    @{ f = 'S2'; slug = 'vitest-exit-placeholder'; old = '<the VITEST_EXIT from row 3>'; new = '$vitest'
        variants = @('VITEST_EXIT') }

    # ---- Self-review 3: shell expansion / plan gates
    @{ f = 'S3'; slug = 'shell-expansion'; old = 'pwsh -NoProfile -Command "$'; new = 'SHELL_EXPANSION_RULE'
        variants = @('PLAN_GATE_SCRIPT', 'assert-plan-gates.ps1') }
    @{ f = 'S3'; slug = 'plan-gate-names'; old = ''; new = '-Gate '
        variants = @('-Gate Deps', '-Gate E2eCensus', '-Gate BuildPlanAudit', '-Gate Unchecked', '-Gate ApiSkip', '-Gate Reflection') }
    @{ f = 'S3'; slug = 'fic-ac-check'; old = "-Pattern 'AC-49\.').Count"; new = 'assert-handoff-acs.ps1 -Only MEU-49'
        variants = @('HANDOFF_AC_CHECK') }
    @{ f = 'S3'; slug = 'red-selftest-cases'; old = '8 self-test cases'; new = '**14** self-test cases'
        superseded_by = 'R4-F1'
        variants = @('8 cases', '14 cases', 'now 14 cases') }

    # ---- S4: defect the round-2 census itself surfaced (Out of Scope contradicted the F8 fix)
    @{ f = 'S4'; slug = 'oos-tts-row'; old = 'Drag reorder on the Transcript and TTS queues'
        new = 'Drag reorder on the TTS queue'
        variants = @('Drag reorder on the Transcript queue', 'MEU-55, MEU-56', 'Those MEUs adopt') }
    @{ f = 'S4'; slug = 'queuelist-source'; old = 'meu-registry.md:149-150'
        new = 'p11-page-layout-session-grouping.md:134-136'
        variants = @('meu-registry.md:149', 'meu-registry.md:150', ':134-136') }
    @{ f = 'S4'; slug = 'tts-primitive'; old = 'adopts the shared progress primitive'
        new = 'inherits the shared `ProgressBar`'
        variants = @('shared progress primitive', 'inherits the shared ProgressBar') }
    @{ f = 'S4'; slug = 'selfreview-count'; old = 'Three further defects'; new = 'Four further defects'
        variants = @('three more defects', 'four self-review', 'three self-review') }

    # ---- S5: registering this script as CORRECTION_CENSUS
    @{ f = 'S5'; slug = 'census-name'; old = 'two plan-local scripts, both already'
        new = 'CORRECTION_CENSUS'
        variants = @('three plan-local scripts, all already', 'run-correction-census.ps1') }

    # ---- S6: NAMEs referenced by this plan but defined in an earlier Phase 10 project, and the
    # header sentence that used to claim - falsely - that there were no such names (R3-F7).
    @{ f = 'S6'; slug = 'inherited-names'; old = ''; new = 'INHERITED_NAMES'
        variants = @('COMMAND_MODULE_RULE', 'BULK_REORDER_ALGORITHM', 'FROZEN_GLOBS',
            'ELECTRON_RUN_AS_NODE', 'Six NAMEs are the exception') }
    @{ f = 'S6'; slug = 'universal-name-claim'
        old = 'every capitalised NAME below is defined there once.'
        new = 'defined there exactly once, **except** the names listed in `INHERITED_NAMES`'
        variants = @('every capitalised NAME', 'defined there once', 'are not named sets at all',
            'non_set_token_list', 'BUILD_PLAN', 'FAIL_TO_PASS') }

    # ======================= round 4: R3-F1 .. R3-F7 =======================

    # ---- R3-F1: preservation ACs must not be demanded to fail in the Red phase
    @{ f = 'R3-F1'; slug = 'preservation-acs'; old = ''; new = 'RED_PHASE_PRESERVATION_ACS'
        variants = @('unit (**preservation**)', 'preservation criteria', 'AC-49.11', 'AC-49.23',
            '24 required', '3 preservation') }

    # ---- R3-F2: the Red oracle vs. Vitest collection failures
    @{ f = 'R3-F2'; slug = 'uncollected-files'; old = ''; new = 'RED_PHASE_UNCOLLECTED_FILES'
        variants = @('VITEST_COLLECTION_FAILURE_SHAPE', 'vitest-shape-probe.json',
            'Cannot find module', '**(b2)**', '**(b3)**', 'numTotalTests') }
    @{ f = 'R3-F2'; slug = 'queue-dnd-test-file'; old = ''
        new = 'ui/tests/unit/queue-dnd.test.ts'
        variants = @('queue-dnd.test.ts', 'AC-49.16, AC-49.17', 'a **separate** file') }
    @{ f = 'R3-F2'; slug = 'red-file-count'; old = 'The six test files'
        new = 'The seven `RED_PHASE_TEST_FILES` entries'
        variants = @('six test files', 'seven test files', 'the six test files') }

    # ---- R3-F3: single-flight ownership, cross-queue independence, feedback parity
    @{ f = 'R3-F3'; slug = 'queue-scoped-single-flight'; old = ''; new = 'REORDER_QUEUE_KEYS'
        variants = @('acquireQueueReorder', 'use-queue-bulk.ts', 'moveSelected', 'module-level map') }
    @{ f = 'R3-F3'; slug = 'new-acs'; old = ''; new = 'AC-49.37'
        variants = @('AC-49.38', 'both completion orders', 'feedback parity') }

    # ---- R3-F4: two closeout rows whose "validation" printed instead of asserting
    @{ f = 'R3-F4'; slug = 'metrics-gate'
        old = 'pwsh -NoProfile -Command "Get-Content docs/execution/metrics.md -Tail 3"'
        new = '-Gate Metrics'
        variants = @('METRICS_ROW_MARKERS', '-Tail 3') }
    @{ f = 'R3-F4'; slug = 'commit-draft-gate'
        old = 'pwsh -NoProfile -Command "Get-Content C:/Temp/av-kit/commit-draft-p10-queue-card-dnd.txt"'
        new = '-Gate CommitDraft'
        variants = @('COMMIT_DRAFT_MARKERS', '-ReceiptPath', 'PHASE_EXIT_ASSERTIONS') }
    @{ f = 'R3-F4'; slug = 'gate-count'; superseded_by = 'C7'; old = '24 self-test cases across 6 gates'
        new = '**53** self-test cases across **8** gates'
        variants = @('53 cases across 8 gates', '6 gates', '8 gates') }

    # ---- R3-F5: every gate must be a predicate the unstarted tree FAILS
    @{ f = 'R3-F5'; slug = 'post-meu-floors'; old = ''; new = 'E2E_POST_MEU_STATIC_FLOOR'
        variants = @('E2E_POST_MEU_RUNTIME_FLOOR', 'E2E_STATIC_CASE_FLOOR', 'E2E_BASELINE_COUNT',
            'pre-MEU 67', '**73**', '**79**') }

    # ---- R3-F6: RTK on the second process, and the G37 source label
    @{ f = 'R3-F6'; slug = 'rtk-second-process'
        old = '$vitest=$LASTEXITCODE; pwsh -NoProfile -File'
        new = '$vitest=$LASTEXITCODE; rtk proxy pwsh -NoProfile -File'
        variants = @('rtk proxy npm --prefix ui run test:e2e', 'rtk proxy pwsh') }
    @{ f = 'R3-F6'; slug = 'g37-source'; old = ''; new = 'OQ-5'
        variants = @('Human-approved', 'Local Canon', 'no `@testing-library/*` dependency',
            'helpers/user-event.ts') }

    # ---- R3-F7 / counts restated in prose by the round-4 pass itself
    @{ f = 'C1'; slug = 'ac-count'; superseded_by = 'C5'; old = ('AC-49.1' + $D + '49.36'); new = ('AC-49.1' + $D + '49.38')
        variants = @('AC-49.36', 'AC-49.38', '**38**', '**36**') }
    @{ f = 'C2'; slug = 'named-set-key-count'; old = '72 to **84**'; new = 'to **94** in round 4'
        variants = @('72 to 84 keys', '84 keys', '94 keys') }
    @{ f = 'C3'; slug = 'plan-local-script-count'; old = 'the **five** plan-local'
        new = 'the **six** plan-local'
        variants = @('five `-SelfTest` receipts', 'six `-SelfTest` receipts', 'Six self-tested',
            'Five self-tested', 'five scripts and not six') }
    @{ f = 'C4'; slug = 'file-estimate'; old = '~17 files changed'; new = '~19 files changed'
        superseded_by = 'C8'; variants = @('files changed') }

    # ======================= round 5: R4-F1 .. R4-F5 =======================

    # ---- R4-F1: clause (e) demanded AC ids that an uncollected file can never report
    @{ f = 'R4-F1'; slug = 'ac-ownership'; old = ''; new = 'RED_PHASE_AC_OWNERSHIP'
        variants = @('Get-ClauseEIds', 'clause (e) scoped', 'proven by clause (b2)',
            'owned only by an expected-uncollected file') }
    @{ f = 'R4-F1'; slug = 'red-selftest-cases-r5'; old = 'now 14 cases'; new = 'now **17** cases'
        variants = @('14 self-test cases', '17 self-test cases', '**17** cases') }

    # ---- R4-F2: two round-4 ACs were never added to the required-red set
    @{ f = 'R4-F2'; slug = 'required-ac-count'; old = '24 required'; new = '**27** required'
        variants = @('27 required', 'RED_PHASE_REQUIRED_ACS', 'ownership union',
            'neither required nor preservation') }

    # ---- R4-F3: the held-gate feedback contradicted QueueCardMenu's own rule 1
    @{ f = 'R4-F3'; slug = 'present-not-all-four'
        old = 'the drag handle **and all four kebab reorder items** render `disabled`'
        new = 'every kebab reorder item that is present'
        variants = @('absent, never disabled', 'disabled?: boolean', 'QueueCardMenu.tsx',
            'structurally unavailable', 'useQueueReorderHeld') }

    # ---- R4-F4: the BUILD_PLAN `Next:` audit tested the whole file, not the pointer
    @{ f = 'R4-F4'; slug = 'next-pointer-segment'; old = ''; new = 'BUILD_PLAN_NEXT_POINTER'
        variants = @('Next: segment', 'segment_start', 'must_not_match', 'next-decoy') }

    # ---- R4-F5: G37 / OQ-5 resolved in-MEU rather than deferred (user direction 2026-09-04)
    @{ f = 'R4-F5'; slug = 'testing-library-adoption'; old = ''; new = 'TESTING_LIBRARY_PACKAGES'
        variants = @('TL_MIGRATION_FILES', 'userEvent.setup()', '@testing-library/react',
            '@testing-library/jest-dom', 'helpers/user-event.ts', 'AC-49.39') }
    @{ f = 'R4-F5'; slug = 'oq5-closed'; old = 'package-wide adoption is OQ-5'
        new = 'OQ-5 is closed'
        variants = @('OQ-5', 'satisfied **literally**', 'as all 54 existing unit files do',
            'No exception is claimed') }

    # ---- counts restated by the round-5 pass itself
    @{ f = 'C5'; slug = 'ac-count-r5'; old = ('AC-49.1' + $D + '49.38'); new = ('AC-49.1' + $D + '49.39')
        variants = @('AC-49.38', 'AC-49.39', '**39**', '**38**') }
    @{ f = 'C6'; slug = 'named-set-key-count-r5'; old = 'to **94** in round 4'
        new = '**98** in round 5'
        variants = @('94 keys', '98 in round 5', '**98**') }
    @{ f = 'C7'; slug = 'plan-gate-cases-r5'; old = 'now 53 cases across 8 gates'
        new = 'now **60** cases across 8 gates'; superseded_by = 'C10'
        variants = @('53 self-test cases', '60 self-test cases', '**60** cases') }
    @{ f = 'C8'; slug = 'file-estimate-r5'; old = '~19 files changed'; new = '~33 files changed'
        superseded_by = 'C11'
        variants = @('files changed', '3 runtime dependencies + 4 dev dependencies') }

    # ======================= round 6: R5-F1 .. R5-F3 =======================

    # ---- R5-F1: round 5 declared the hook in the one module row 4a forbids React in
    @{ f = 'R5-F1'; slug = 'held-hook-module'
        old = '(`useSyncExternalStore` over the module-level registry, `REORDER_SINGLE_FLIGHT_RULE`)'
        new = 'REORDER_HELD_HOOK'
        variants = @('use-queue-reorder-held.ts', '| 4b |', 'useQueueReorderHeld',
            'has no React import', 'React-free') }

    # ---- R5-F2: row 2 was gated on a check only row 2a, which depends on row 2, could satisfy
    @{ f = 'R5-F2'; slug = 'deps-packages-mode'
        old = '-Gate Deps *> C:/Temp/av-kit/meu49-deps.txt'
        new = '-Gate DepsPackages'
        variants = @('-Gate Deps', 'packages-mode-pre-migration', 'full-mode-pre-migration',
            'jest-dom/vitest') }
    @{ f = 'R5-F2'; slug = 'red-phase-after-migration'
        old = '| 2 | shared | `C:/Temp/av-kit/meu49-red-census.json`'
        new = '| 2a | shared | `C:/Temp/av-kit/meu49-red-census.json`'
        variants = @('| 2a |') }

    # ---- R5-F3: the migration gate could not see the migration it was gating
    @{ f = 'R5-F3'; slug = 'rtl-mount-half'
        old = 'every `TL_MIGRATION_FILES` entry imports `userEvent` from `@testing-library/user-event` and calls `userEvent.setup()`'
        new = 'TL_INTERACTION_FILES'
        variants = @('TL_MOUNT_ONLY_FILES', 'react-dom/client', 'createRoot', 'partition',
            'tl-old-style-retained', 'use-queue-selection.test.ts') }

    # ---- counts restated by the round-6 pass itself
    @{ f = 'C9'; slug = 'named-set-key-count-r6'; old = ''; new = '**101** in round 6'
        variants = @('98 in round 5', '101 keys') }
    @{ f = 'C10'; slug = 'plan-gate-cases-r6'; old = 'now **60** cases across 8 gates'
        new = 'now **69** cases'; superseded_by = 'C13'
        variants = @('60 self-test cases', '69 self-test cases', '**69**') }
    @{ f = 'C11'; slug = 'file-estimate-r6'; old = '~33 files changed'; new = '~34 files changed'
        variants = @('files changed', '3 new lib modules') }

    # ======================= round 7: R6-F1 =======================

    # ---- R6-F1: row 2's gate never read the file holding row 2's own AC-49.2 deliverable
    @{ f = 'R6-F1'; slug = 'dep-guard-check'
        old = 'and the rejected `@dnd-kit/react` / `react-virtual` in neither. **`DepsPackages`'
        new = 'DND_DEP_GUARD_CHECK'
        variants = @('dep-guard-still-broad', 'dep-guard-deleted', 'dep-guard-no-supersession',
            'dep-guard-comment-not-in-place', 'within 12 lines') }

    # ---- counts restated by the round-7 pass itself
    @{ f = 'C12'; slug = 'named-set-key-count-r7'; old = ''; new = '**102** in round 7'
        variants = @('101 in round 6') }
    @{ f = 'C13'; slug = 'plan-gate-cases-r7'; old = 'now **69** cases'; new = 'now **73** cases'
        variants = @('69 self-test cases', '73 self-test cases', '**73**') }
)

# ---------------------------------------------------------------------------
# S6 (a): universal claims about the NAME inventory must be qualified.
# Patterns are matched case-SENSITIVELY so that the capitalised token NAME is
# required; the quantifier itself is matched case-insensitively via (?i:...) so
# a sentence-initial "Every" is not a hole in the check.
# ---------------------------------------------------------------------------
$UniversalClaimPatterns = @(
    '(?i:every|each|all)\s+(?i:capitalised\s+|capitalized\s+)?NAMEs?\b'
    '(?i:every|all)\s+(?i:named\s+set)s?\b'
    '(?i:defined)\s+(?i:there\s+)?(?i:exactly\s+)?once\b'
)

$UniversalQualifierTokens = @(
    'except', 'unless', 'other than', 'apart from', 'excluding', 'INHERITED_NAMES'
)

# A SCREAMING_SNAKE token: at least one underscore, so JSON / UI / E2E / PUT and
# other ordinary capitalised prose are not swept in as false positives.
$TokenPattern = '\b[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+\b'

function Get-PlanText {
    param([Parameter(Mandatory = $true)][string]$Path)
    return (Get-Content -LiteralPath $Path -Raw -ErrorAction Stop)
}

function Test-UniversalClaims {
    <#
      Returns one finding string per line that makes a universal claim about NAMEs whose PARAGRAPH
      carries no qualifier token. The qualifier is looked for over the whole contiguous non-blank
      block rather than the matched line, because these files are hard-wrapped markdown: the claim
      and its "except ..." routinely land on different physical lines, and a per-line check would
      demand that a sentence be rewritten to satisfy the checker. A blank line ends the block, so a
      qualifier in a *different* paragraph does not launder an unqualified claim.
    #>
    param([Parameter(Mandatory = $true)][string[]]$Files)

    $findings = New-Object System.Collections.Generic.List[string]
    foreach ($file in $Files) {
        $lines = @(Get-Content -LiteralPath $file -ErrorAction Stop)

        # blockQualified[i] = does line i's paragraph contain a qualifier token?
        $blockQualified = New-Object 'bool[]' $lines.Count
        $i = 0
        while ($i -lt $lines.Count) {
            if ([string]::IsNullOrWhiteSpace([string]$lines[$i])) { $i++; continue }
            $start = $i
            while ($i -lt $lines.Count -and -not [string]::IsNullOrWhiteSpace([string]$lines[$i])) { $i++ }
            $block = ($lines[$start..($i - 1)] -join ' ')
            $q = $false
            foreach ($tok in $UniversalQualifierTokens) {
                if ($block -match [regex]::Escape($tok)) { $q = $true; break }
            }
            for ($j = $start; $j -lt $i; $j++) { $blockQualified[$j] = $q }
        }

        for ($k = 0; $k -lt $lines.Count; $k++) {
            $line = [string]$lines[$k]
            $matched = $null
            foreach ($p in $UniversalClaimPatterns) {
                if ($line -cmatch $p) { $matched = $p; break }
            }
            if ($null -eq $matched) { continue }
            if ($blockQualified[$k]) { continue }
            $findings.Add((Split-Path -Leaf $file) + ':' + ($k + 1) +
                ' - unqualified universal claim about NAMEs (matched /' + $matched +
                '/, no qualifier token in its paragraph): ' + $line.Trim())
        }
    }
    return $findings
}

function Get-AllowedTokens {
    <#
      The inventory a SCREAMING_SNAKE token may resolve against: this project's named-set keys,
      the names inherited from earlier Phase 10 projects, and the declared non-set tokens.
    #>
    param([Parameter(Mandatory = $true)][string]$NamesPath)

    $json = (Get-Content -LiteralPath $NamesPath -Raw -ErrorAction Stop) | ConvertFrom-Json -AsHashtable
    $allowed = New-Object System.Collections.Generic.HashSet[string]
    foreach ($k in @($json.Keys)) { [void]$allowed.Add([string]$k) }

    $inherited = $json['INHERITED_NAMES']
    if ($null -eq $inherited) {
        throw ('named-sets.json has no INHERITED_NAMES key: ' + $NamesPath)
    }
    foreach ($k in @($inherited['value'].Keys)) { [void]$allowed.Add([string]$k) }

    $nonSet = @($inherited['non_set_token_list'])
    if ($nonSet.Count -lt 1) {
        throw ('INHERITED_NAMES.non_set_token_list is missing or empty in ' + $NamesPath +
            ' - the allowlist has to be machine-readable, or this gate silently weakens to nothing')
    }
    foreach ($t in $nonSet) { [void]$allowed.Add([string]$t) }
    return $allowed
}

function Test-NameInventory {
    <#
      Returns one finding per SCREAMING_SNAKE token that resolves to nothing. This is the check the
      round-2 self-review performed by hand; by round 3 it had gone stale by three tokens.
    #>
    param(
        [Parameter(Mandatory = $true)][string[]]$Files,
        [Parameter(Mandatory = $true)][string]$NamesPath
    )

    $allowed = Get-AllowedTokens -NamesPath $NamesPath
    $findings = New-Object System.Collections.Generic.List[string]
    $seen = 0
    foreach ($file in $Files) {
        $lines = @(Get-Content -LiteralPath $file -ErrorAction Stop)
        for ($i = 0; $i -lt $lines.Count; $i++) {
            foreach ($m in ([regex]::Matches([string]$lines[$i], $TokenPattern))) {
                $seen++
                $tok = $m.Value
                if ($allowed.Contains($tok)) { continue }
                $findings.Add((Split-Path -Leaf $file) + ':' + ($i + 1) +
                    ' - `' + $tok + '` resolves to nothing: not a named-sets.json key, not in ' +
                    'INHERITED_NAMES.value, not in INHERITED_NAMES.non_set_token_list')
            }
        }
    }
    if ($seen -lt 1) {
        $findings.Add('no SCREAMING_SNAKE token was found in any plan file - the token scan is ' +
            'vacuous, so a passing result would prove nothing')
    }
    return $findings
}

function Invoke-Sweep {
    param(
        [Parameter(Mandatory = $true)][string]$Value,
        [Parameter(Mandatory = $true)][string]$Receipt
    )
    # -e is required: several swept values start with '-' and would otherwise be
    # parsed as rg flags (`-Census`, `-Gate `, `-RequiredAcIds`).
    rg -F -n --no-heading --with-filename -e $Value -- $plan $task *> $Receipt
    $rc = $LASTEXITCODE
    if ($rc -gt 1) {
        Write-Error ('rg failed (exit ' + $rc + ') sweeping "' + $Value + '" - receipt ' + $Receipt)
        exit $rc
    }
    $lines = @(Get-Content -LiteralPath $Receipt -ErrorAction SilentlyContinue | Where-Object { $_.Trim().Length -gt 0 })
    return [pscustomobject]@{ Exit = $rc; Hits = $lines.Count; Receipt = $Receipt; Lines = $lines }
}

if ($SelfTest) {
    $fixtureRoot = Join-Path ([System.IO.Path]::GetTempPath()) ('census-selftest-' + [guid]::NewGuid().ToString('N'))
    New-Item -ItemType Directory -Path $fixtureRoot -Force | Out-Null
    $problems = New-Object System.Collections.Generic.List[string]
    $realPlan = $plan
    $realTask = $task
    try {
        $plan = Join-Path $fixtureRoot 'implementation-plan.md'
        $task = Join-Path $fixtureRoot 'task.md'
        Set-Content -LiteralPath $plan -Value "planted VALUE_A here`nand a regex metachar AC-49.[0-9] literal`n" -Encoding utf8
        Set-Content -LiteralPath $task -Value "VALUE_A again in task`n" -Encoding utf8

        # 1
        $r = Invoke-Sweep -Value 'VALUE_A' -Receipt (Join-Path $fixtureRoot 'a.txt')
        if ($r.Exit -ne 0 -or $r.Hits -ne 2) { $problems.Add('1 planted value: expected exit 0 / 2 hits, got exit ' + $r.Exit + ' / ' + $r.Hits + ' hits') }

        # 2
        $r = Invoke-Sweep -Value 'VALUE_ABSENT' -Receipt (Join-Path $fixtureRoot 'b.txt')
        if ($r.Exit -ne 1 -or $r.Hits -ne 0) { $problems.Add('2 absent value: expected exit 1 / 0 hits, got exit ' + $r.Exit + ' / ' + $r.Hits + ' hits') }

        # 3 - -F must treat [0-9] literally, not as a character class
        $r = Invoke-Sweep -Value 'AC-49.[0-9]' -Receipt (Join-Path $fixtureRoot 'c.txt')
        if ($r.Exit -ne 0 -or $r.Hits -ne 1) { $problems.Add('3 literal metachar: expected exit 0 / 1 hit, got exit ' + $r.Exit + ' / ' + $r.Hits + ' hits') }

        # 4
        $r = Invoke-Sweep -Value 'AC-49.5' -Receipt (Join-Path $fixtureRoot 'd.txt')
        if ($r.Exit -ne 1) { $problems.Add('4 literal metachar: "AC-49.5" must NOT match "AC-49.[0-9]" under -F, but exit was ' + $r.Exit) }

        # 5 - a value beginning with '-' must be swept as a pattern, not parsed as an rg flag
        Add-Content -LiteralPath $plan -Value 'invoked with -Census here'
        $r = Invoke-Sweep -Value '-Census' -Receipt (Join-Path $fixtureRoot 'e.txt')
        if ($r.Exit -ne 0 -or $r.Hits -ne 1) { $problems.Add('5 leading-dash value: expected exit 0 / 1 hit, got exit ' + $r.Exit + ' / ' + $r.Hits + ' hits') }

        # ---- S6 (a): universal claims
        $claimFile = Join-Path $fixtureRoot 'claims.md'

        # 6 - an unqualified universal claim is reported, in each of its phrasings
        Set-Content -LiteralPath $claimFile -Encoding utf8 -Value @(
            'every capitalised NAME below is defined there once.'
            'All named sets live in one file.'
            'ordinary prose about every name of every user is not a NAME claim'
        )
        $f = @(Test-UniversalClaims -Files @($claimFile))
        if ($f.Count -ne 2) {
            $problems.Add('6 unqualified claims: expected 2 findings, got ' + $f.Count + ' -> ' + ($f -join ' | '))
        }

        # 7 - the same claims, qualified, are silent
        Set-Content -LiteralPath $claimFile -Encoding utf8 -Value @(
            'every capitalised NAME below is defined there exactly once, except the names in `INHERITED_NAMES`.'
            'All named sets live in one file, apart from the inherited ones.'
        )
        $f = @(Test-UniversalClaims -Files @($claimFile))
        if ($f.Count -ne 0) {
            $problems.Add('7 qualified claims: expected 0 findings, got ' + $f.Count + ' -> ' + ($f -join ' | '))
        }

        # 7b - the qualifier may sit on a later line of the SAME paragraph, but a blank line ends
        # the block: a qualifier in the next paragraph does not launder the claim.
        Set-Content -LiteralPath $claimFile -Encoding utf8 -Value @(
            'every capitalised NAME below is defined there exactly once'
            'in `named-sets.json`, except the inherited ones.'
            ''
            'every capitalised NAME below is defined there exactly once'
            ''
            'except the ones that are not.'
        )
        $f = @(Test-UniversalClaims -Files @($claimFile))
        if ($f.Count -ne 1 -or $f[0] -notmatch ':4 ') {
            $problems.Add('7b paragraph scope: expected exactly 1 finding on line 4, got ' + $f.Count + ' -> ' + ($f -join ' | '))
        }

        # ---- S6 (b): token inventory
        $namesFixture = Join-Path $fixtureRoot 'named-sets.json'
        Set-Content -LiteralPath $namesFixture -Encoding utf8 -Value @'
{
  "KNOWN_SET": { "value": "x" },
  "INHERITED_NAMES": {
    "value": { "INHERITED_SET": "elsewhere.json" },
    "non_set_token_list": ["NOT_A_SET"]
  }
}
'@
        $tokenFile = Join-Path $fixtureRoot 'tokens.md'

        # 8 - an unresolved token is reported once per occurrence
        Set-Content -LiteralPath $tokenFile -Encoding utf8 -Value @(
            'uses `KNOWN_SET` and `INHERITED_SET` and `NOT_A_SET`'
            'but `MYSTERY_TOKEN` resolves to nothing'
            'JSON UI E2E PUT are not tokens at all'
        )
        $f = @(Test-NameInventory -Files @($tokenFile) -NamesPath $namesFixture)
        if ($f.Count -ne 1 -or $f[0] -notmatch 'MYSTERY_TOKEN') {
            $problems.Add('8 unresolved token: expected 1 finding naming MYSTERY_TOKEN, got ' + $f.Count + ' -> ' + ($f -join ' | '))
        }

        # 9 - all three resolution routes are honoured, and an empty allowlist is fatal rather than vacuous
        Set-Content -LiteralPath $tokenFile -Encoding utf8 -Value @(
            'uses `KNOWN_SET`, `INHERITED_SET` and `NOT_A_SET` only'
        )
        $f = @(Test-NameInventory -Files @($tokenFile) -NamesPath $namesFixture)
        if ($f.Count -ne 0) {
            $problems.Add('9 resolved tokens: expected 0 findings, got ' + $f.Count + ' -> ' + ($f -join ' | '))
        }
        $emptyNames = Join-Path $fixtureRoot 'named-sets-empty.json'
        Set-Content -LiteralPath $emptyNames -Encoding utf8 -Value '{ "INHERITED_NAMES": { "value": {}, "non_set_token_list": [] } }'
        $threw = $false
        try { [void](Test-NameInventory -Files @($tokenFile) -NamesPath $emptyNames) } catch { $threw = $true }
        if (-not $threw) { $problems.Add('9 empty allowlist: an empty non_set_token_list must throw, not pass silently') }

        # 10 - the satisfiability proof: the REAL plan files against the REAL named-sets.json
        $f = @(Test-UniversalClaims -Files @($realPlan, $realTask))
        $f += @(Test-NameInventory -Files @($realPlan, $realTask) -NamesPath $namesPath)
        if ($f.Count -ne 0) {
            $problems.Add('10 real files must pass S6, got ' + $f.Count + ' finding(s) -> ' + ($f -join ' | '))
        }
    }
    finally {
        $plan = $realPlan
        $task = $realTask
        Remove-Item -LiteralPath $fixtureRoot -Recurse -Force -ErrorAction SilentlyContinue
    }
    if ($problems.Count -gt 0) {
        foreach ($p in $problems) { Write-Error $p -ErrorAction Continue }
        Write-Output 'FAIL: CORRECTION_CENSUS self-test'
        exit 1
    }
    Write-Output 'PASS: CORRECTION_CENSUS self-test (11 cases: 5 sweep, 3 universal-claim, 2 inventory, 1 real-file satisfiability)'
    exit 0
}

if (-not (Test-Path -LiteralPath $ReceiptDir)) { New-Item -ItemType Directory -Path $ReceiptDir -Force | Out-Null }

$s6Findings = New-Object System.Collections.Generic.List[string]
if ($Gate -eq 'All' -or $Gate -eq 'S6') {
    foreach ($x in @(Test-UniversalClaims -Files @($plan, $task))) { $s6Findings.Add($x) }
    foreach ($x in @(Test-NameInventory -Files @($plan, $task) -NamesPath $namesPath)) { $s6Findings.Add($x) }

    $s6Receipt = Join-Path $ReceiptDir 'census-s6-universal-claims.txt'
    $s6Out = New-Object System.Collections.Generic.List[string]
    $s6Out.Add('S6 UNIVERSAL-CLAIM AND NAME-INVENTORY SWEEP')
    $s6Out.Add('plan: ' + $plan)
    $s6Out.Add('task: ' + $task)
    $s6Out.Add('names: ' + $namesPath)
    $s6Out.Add('findings: ' + $s6Findings.Count)
    $s6Out.Add('')
    foreach ($x in $s6Findings) { $s6Out.Add($x) }
    if ($s6Findings.Count -eq 0) { $s6Out.Add('(none - every universal claim is qualified and every token resolves)') }
    Set-Content -LiteralPath $s6Receipt -Value $s6Out -Encoding utf8

    Write-Output ('S6: ' + $s6Findings.Count + ' finding(s)  receipt=' + $s6Receipt)
    foreach ($x in $s6Findings) { Write-Output ('  ' + $x) }
    Write-Output ''
}

if ($Gate -eq 'S6') {
    if ($s6Findings.Count -gt 0) { exit 1 }
    exit 0
}

$rows = New-Object System.Collections.Generic.List[object]
$valuesSwept = 0
$variantsSwept = 0

foreach ($entry in $census) {
    $slug = [string]$entry.slug

    if (-not [string]::IsNullOrEmpty([string]$entry.old)) {
        $valuesSwept++
        $r = Invoke-Sweep -Value ([string]$entry.old) -Receipt (Join-Path $ReceiptDir ('census-' + $slug + '-old.txt'))
        $rows.Add([pscustomobject]@{ Finding = $entry.f; Value = [string]$entry.old; Direction = 'old'; Exit = $r.Exit; Hits = $r.Hits; Receipt = $r.Receipt; Lines = $r.Lines })
    }

    $valuesSwept++
    $r = Invoke-Sweep -Value ([string]$entry.new) -Receipt (Join-Path $ReceiptDir ('census-' + $slug + '-new.txt'))
    $rows.Add([pscustomobject]@{ Finding = $entry.f; Value = [string]$entry.new; Direction = 'new'; Exit = $r.Exit; Hits = $r.Hits; Receipt = $r.Receipt; Lines = $r.Lines; SupersededBy = [string]$entry.superseded_by })

    $i = 0
    foreach ($v in @($entry.variants)) {
        $variantsSwept++
        $i++
        $r = Invoke-Sweep -Value ([string]$v) -Receipt (Join-Path $ReceiptDir ('census-' + $slug + '-variant' + $i + '.txt'))
        $rows.Add([pscustomobject]@{ Finding = $entry.f; Value = [string]$v; Direction = 'variant'; Exit = $r.Exit; Hits = $r.Hits; Receipt = $r.Receipt; Lines = $r.Lines })
    }
}

$totalHits = ($rows | Measure-Object -Property Hits -Sum).Sum

# The consolidated index. Every per-value receipt is on disk untruncated; this
# names them all so the reviewer can open any one of them.
$index = Join-Path $ReceiptDir 'census-index.txt'
$out = New-Object System.Collections.Generic.List[string]
$out.Add('CORRECTION BLAST-RADIUS CENSUS - 2026-09-03-p10-queue-card-dnd (rounds 1-7, current state)')
$out.Add('plan: ' + $plan)
$out.Add('task: ' + $task)
$out.Add('values swept: ' + $valuesSwept + '  variants swept: ' + $variantsSwept + '  total hits: ' + $totalHits)
$out.Add('S6 findings: ' + $s6Findings.Count)
$out.Add('')
foreach ($x in $s6Findings) { $out.Add('  [S6] ' + $x) }
if ($s6Findings.Count -gt 0) { $out.Add('') }
foreach ($row in $rows) {
    $out.Add(('[' + $row.Finding + '] ' + $row.Direction + ' "' + $row.Value + '"  exit=' + $row.Exit + '  hits=' + $row.Hits + '  receipt=' + $row.Receipt))
    foreach ($line in $row.Lines) { $out.Add('    ' + $line) }
    $out.Add('')
}
Set-Content -LiteralPath $index -Value $out -Encoding utf8

Write-Output ('CENSUS COMPLETE: ' + $valuesSwept + ' values, ' + $variantsSwept + ' variants, ' + $totalHits + ' hits')
Write-Output ('index: ' + $index)
Write-Output ''
Write-Output 'Zero-hit NEW values (the edit did not land where it was claimed):'
$missing = @($rows | Where-Object { $_.Direction -eq 'new' -and $_.Hits -eq 0 -and [string]::IsNullOrEmpty($_.SupersededBy) })
if ($missing.Count -eq 0) { Write-Output '  (none)' }
foreach ($m in $missing) { Write-Output ('  [' + $m.Finding + '] ' + $m.Value) }
Write-Output ''
Write-Output 'Superseded NEW values (a later round replaced them; zero hits is correct):'
$superseded = @($rows | Where-Object { $_.Direction -eq 'new' -and -not [string]::IsNullOrEmpty($_.SupersededBy) })
if ($superseded.Count -eq 0) { Write-Output '  (none)' }
foreach ($s in $superseded) {
    $state = if ($s.Hits -eq 0) { 'gone as expected' } else { 'STILL PRESENT - the superseding edit did not land' }
    Write-Output ('  [' + $s.Finding + ' -> ' + $s.SupersededBy + '] "' + $s.Value + '" - ' + $state)
}
Write-Output ''
Write-Output 'Surviving OLD values (each needs a disposition in the correction log):'
$stale = @($rows | Where-Object { $_.Direction -eq 'old' -and $_.Hits -gt 0 })
if ($stale.Count -eq 0) { Write-Output '  (none)' }
foreach ($s in $stale) {
    Write-Output ('  [' + $s.Finding + '] "' + $s.Value + '" - ' + $s.Hits + ' hits')
    foreach ($line in $s.Lines) { Write-Output ('      ' + $line) }
}
if ($s6Findings.Count -gt 0) { exit 1 }
exit 0
