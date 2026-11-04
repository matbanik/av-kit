# Sole executable owner of the task-row completeness gate.
#
# Round-1 finding F1: the original gate was vacuous (matched no rows).
# Round-3 finding N1: requiring ZERO open rows deadlocks - the row that RUNS this gate
#   (H1-1) and every row after it are necessarily still open at the moment it runs.
# Round-4 finding R4-1: status was the single boolean "the line contains `[ ]`", so a
#   `[/]` (In progress - a state the task.md legend documents), a missing status cell, a
#   malformed cell, or any unknown marker counted as CLOSED. The gate now parses the
#   status cell POSITIVELY and fails closed: only exactly `[x]` or `[B]` is complete.
#
# Contract: the gate proves PREDECESSOR COMPLETENESS, not global completeness.
#   -Through <rowId>  every row STRICTLY BEFORE <rowId> in document order must be closed
#                     (exactly `[x]` or `[B]`); the boundary row itself and all rows after
#                     it may be open. -Through is MANDATORY in live mode.
#
# Status parsing rules (fail-closed):
#   * The status cell is the LAST cell of the row, not "somewhere on the line". Row 7a's
#     prose legitimately contains an inline `[B]`, so a whole-line scan is ambiguous by
#     construction.
#   * That cell must hold EXACTLY ONE status-shaped token and nothing else. Zero tokens
#     (missing status), two or more tokens (ambiguous/duplicate), or trailing prose all
#     make the row INVALID.
#   * closed = `[x]` | `[B]`   open = `[ ]` | `[/]`   anything else = INVALID.
#   * An INVALID row fails the gate wherever it appears in the table - a malformed status
#     is never silently treated as complete.
#
# Round-7 finding R7-2 (static-binding half): a row whose evidence must come from a named
#   producer has to SAY SO in its own cells. Row 9's binding to run-live-smoke.ps1 was purely
#   dynamic - the smoke gate checks a receipt's provenance, but nothing stopped task.md from
#   telling a coder to run `npm --prefix ui run dev` directly, in which case no receipt is ever
#   produced and the row's own text is the thing that misleads. TASK_ROW_REQUIRED_TOKENS maps
#   row id -> tokens that must appear in that row; a listed row that is ABSENT is a failure,
#   never a skip (the standing vacuity rule for every named set in this plan).
#
# Round-8 finding R8-3: that check searched the WHOLE markdown row. Row 9 names its producer in
#   its Task prose as well as its Validation command, so replacing only the Validation cell with
#   `npm --prefix ui run dev, then type the receipt` still passed - the gate proved the row
#   MENTIONS the producer, never that it RUNS it. TASK_ROW_REQUIRED_TOKENS is now scoped by
#   COLUMN (row id -> column name -> tokens); the column is resolved from the table's own header,
#   and the token must appear in an EXECUTABLE segment of that cell - a segment whose head, after
#   stripping VALIDATION_ALLOWED_PREFIXES, is not a SCRIPT_HOLLOW_HEADS head - and, since round-9
#   finding R9-3, in which the token occupies an INVOCATION POSITION (command head, after `&`, or
#   the value of a TASK_ROW_INVOCATION_PARAMS parameter) rather than sitting anywhere inside such a
#   segment: `pwsh -NoProfile -Command { Write-Output <producer> }` has a real head and runs
#   nothing. Naming the producer
#   in a comment, an `echo`, or a neighbouring cell is not running it.
#
# -SelfTest is the mandatory negative oracle: it proves the predicate is not vacuous, that
#   an open predecessor fails while an open successor does not, that `[/]`, unknown,
#   missing, and duplicate statuses are all rejected rather than counted as closed, and that
#   a row which drops its producer token fails.
param([switch]$SelfTest, [string]$Through)
$ErrorActionPreference = 'Stop'
$setsPath = Join-Path $PSScriptRoot 'named-sets.json'
if (-not (Test-Path -LiteralPath $setsPath)) { Write-Error ('missing NAMED_SETS_FILE ' + $setsPath); exit 1 }
$sets = Get-Content -LiteralPath $setsPath -Raw | ConvertFrom-Json
$taskPath = [string]$sets.TASK_FILE

# A task row starts with '|', then a row id (numeric, H1-*, or H2-*), then '|'.
$RowIdPattern = '^\|\s*(?<id>[0-9]+[a-z]?|H[12]-[0-9]+[a-z]?)\s*\|'
# Any backticked bracket token, used to COUNT candidate status markers in the status cell.
$StatusTokenPattern = '`\[[^\]]*\]`'
# The only accepted status cell contents: exactly one marker, nothing else.
$StatusCellPattern = '^`\[(?<s>[ xB/])\]`$'
$ClosedMarkers = @('x', 'B')

# Returns 'closed' | 'open' | 'invalid' plus the reason on invalid.
function Get-RowStatus {
    param([string]$Line)
    $t = $Line.TrimEnd()
    if (-not $t.EndsWith('|')) {
        return [pscustomobject]@{ status = 'invalid'; marker = ''; detail = 'row does not end with a table cell delimiter "|"' }
    }
    # Splitting on '|' is safe for the LAST cell: pipes inside earlier cells (the validation
    # commands contain them) only add cells before it, never after the trailing delimiter.
    $parts = $t.Split('|')
    if ($parts.Count -lt 3) {
        return [pscustomobject]@{ status = 'invalid'; marker = ''; detail = 'row has no parsable cells' }
    }
    $cell = $parts[$parts.Count - 2].Trim()
    $tokens = @([regex]::Matches($cell, $StatusTokenPattern))
    if ($tokens.Count -lt 1) {
        return [pscustomobject]@{ status = 'invalid'; marker = ''; detail = 'status cell "' + $cell + '" holds no status marker' }
    }
    if ($tokens.Count -gt 1) {
        return [pscustomobject]@{ status = 'invalid'; marker = ''; detail = 'status cell "' + $cell + '" holds ' + $tokens.Count + ' status markers - ambiguous' }
    }
    $m = [regex]::Match($cell, $StatusCellPattern)
    if (-not $m.Success) {
        return [pscustomobject]@{ status = 'invalid'; marker = $tokens[0].Value; detail = 'status cell "' + $cell + '" is not exactly one of `[ ]` `[/]` `[x]` `[B]`' }
    }
    $s = $m.Groups['s'].Value
    if ($ClosedMarkers -contains $s) {
        return [pscustomobject]@{ status = 'closed'; marker = $s; detail = '' }
    }
    return [pscustomobject]@{ status = 'open'; marker = $s; detail = '' }
}

# Splits a markdown table row into cells. A naive Split('|') is wrong for this table: the
# Validation commands contain pipes (`Get-Content ... | Select-Object -Last 15`) and the Task
# prose contains escaped ones (`{e2e-capture\|live-smoke}`). Backtick code spans are opaque and
# `\|` is a literal, so only a bare pipe outside a code span starts a new cell. Round-4's status
# parsing avoided this by reading only the LAST cell, which is why nothing could address a cell
# by NAME until now (round-8 finding R8-3).
function Split-TableCells {
    param([string]$Line)
    $cells = New-Object System.Collections.ArrayList
    $sb = New-Object System.Text.StringBuilder
    $inCode = $false
    for ($i = 0; $i -lt $Line.Length; $i++) {
        $ch = $Line[$i]
        if ($ch -eq '\' -and ($i + 1) -lt $Line.Length -and $Line[$i + 1] -eq '|') {
            [void]$sb.Append('|'); $i++; continue
        }
        if ($ch -eq '`') { $inCode = -not $inCode; [void]$sb.Append($ch); continue }
        if ($ch -eq '|' -and -not $inCode) { [void]$cells.Add($sb.ToString()); $sb = New-Object System.Text.StringBuilder; continue }
        [void]$sb.Append($ch)
    }
    [void]$cells.Add($sb.ToString())
    return @($cells.ToArray() | ForEach-Object { ([string]$_).Trim() })
}

function Get-TaskRows {
    param([string]$Path)
    $lines = @(Get-Content -LiteralPath $Path)
    $out = New-Object System.Collections.ArrayList
    # The header in force for the rows that follow it: the row immediately above a markdown
    # alignment row. Carried onto each parsed row so a column can be addressed by NAME.
    $header = @()
    for ($n = 0; $n -lt $lines.Count; $n++) {
        $line = [string]$lines[$n]
        if ($line.TrimStart().StartsWith('|') -and ($n + 1) -lt $lines.Count -and $lines[$n + 1] -match '^\|[\s\-:|]+\|\s*$') {
            $header = @(Split-TableCells -Line $line)
            continue
        }
        $m = [regex]::Match($line, $RowIdPattern)
        if (-not $m.Success) { continue }
        $st = Get-RowStatus -Line $line
        [void]$out.Add([pscustomobject]@{
            id     = $m.Groups['id'].Value
            line   = $n + 1
            status = $st.status
            marker = $st.marker
            detail = $st.detail
            text   = $line
            cells  = @(Split-TableCells -Line $line)
            header = $header
        })
    }
    # No comma-wrap: the callers use @(...), which would otherwise collect a single nested array.
    $out.ToArray()
}

# True when $Segment would actually START the token's process rather than describe it.
function Test-ExecutableSegment {
    param([string]$Segment, [string[]]$AllowedPrefixes, [string[]]$HollowHeads)
    $t = ([string]$Segment).Trim().Trim('`').Trim()
    # Strip wrappers that delegate to a real head (`rtk proxy pwsh ...` runs pwsh).
    $stripped = $true
    while ($stripped) {
        $stripped = $false
        foreach ($pre in @($AllowedPrefixes)) {
            $p = [string]$pre
            if ($p.Length -gt 0 -and $t.StartsWith($p, [System.StringComparison]::OrdinalIgnoreCase)) {
                $t = $t.Substring($p.Length).TrimStart(); $stripped = $true
            }
        }
    }
    if ([string]::IsNullOrWhiteSpace($t)) { return $false }
    $head = ([regex]::Split($t, '\s+'))[0]
    foreach ($h in @($HollowHeads)) {
        if ([string]::Equals($head, [string]$h, [System.StringComparison]::OrdinalIgnoreCase)) { return $false }
    }
    return $true
}

# One argument, reduced to the bare path a shell would resolve: quotes, backticks, a leading `./`
# and Windows separators all removed, so `'./docs/x.ps1'` and `docs\x.ps1` compare equal.
function Get-BareArg {
    param([string]$Arg)
    $a = ([string]$Arg).Trim().Trim('`').Trim('"').Trim("'").Trim()
    $a = $a -replace '\\', '/'
    while ($a.StartsWith('./')) { $a = $a.Substring(2) }
    return $a
}

# True when $Segment would actually INVOKE $Token, not merely mention it somewhere inside a
# segment whose HEAD happens to be executable. Round-9 finding R9-3: Test-ExecutableSegment
# answers "is this segment's head a real command?", and the binding check treated that as
# "therefore the token ran". It does not follow - `rtk proxy pwsh -NoProfile -Command { Write-Output
# <producer> }` has a real head, prints a path, runs nothing, and scored ERROR_COUNT=0. T12d closed
# the `echo` HEAD; it never closed inert ARGUMENTS to other heads. A token counts as invoked in
# exactly three positions: it is the command head, it follows the call operator `&`, or it is the
# value of a declared TASK_ROW_INVOCATION_PARAMS parameter (`-File <producer>`). The rule is
# applied uniformly, brace bodies included: mutation testing showed a blank-the-scriptblock pass was
# not load-bearing here (the position rule alone rejects `-Command { Write-Output <producer> }`)
# while it WOULD have falsely rejected `-Command { & <producer> }`, which genuinely runs it. Position
# is the property; nesting is not (T12f rejected, T12j accepted).
#
# Round-10 finding R10-3: those positions were computed by SPLITTING ON WHITESPACE, so they were
# offsets in a string rather than positions in a language. Three shapes scored as invocations while
# running nothing: a token inside a block comment (`{ <# & <producer> #> Write-Output noop }`), a
# token after a terminal statement (`{ exit 0; & <producer> }`), and a token behind the stop-parsing
# token (`--% & <producer>`, which PowerShell hands to the child as literal text). The segment is
# now PARSED and invocation is read off the command AST: a token counts when it is a command's own
# name - which still covers `& <producer>`, because the call operator yields a CommandAst whose
# first element is the operand - or when it is the argument of a declared TASK_ROW_INVOCATION_PARAMS
# parameter, and only when the command that would run it is REACHABLE. Comments and `--%` payloads
# produce no CommandAst, so they stop counting for free. `exit 0;` is closed at cell level by a
# different rule and it is worth being exact about which: Test-RowTokens splits the cell on `;`, and
# the tail segment (`& <producer> }`) is then refused for not PARSING - an unparseable cell cannot be
# shown to run anything. The reachability walk covers the general case the split cannot see - a
# terminal statement and the invocation inside one parseable segment - which T12n exercises directly,
# because a single-line table cell can only reach that shape across a newline.

# A command preceded by a terminal statement in any enclosing block never runs, whatever position
# it occupies. Ascends the AST rather than the text, so nesting depth does not matter.
function Test-AstReachable {
    param($Node)
    $terminals = @('ExitStatementAst', 'ReturnStatementAst', 'ThrowStatementAst', 'BreakStatementAst', 'ContinueStatementAst')
    $n = $Node
    while ($null -ne $n -and $null -ne $n.Parent) {
        $p = $n.Parent
        $stmts = $null
        if ($p -is [System.Management.Automation.Language.StatementBlockAst]) { $stmts = @($p.Statements) }
        elseif ($p -is [System.Management.Automation.Language.NamedBlockAst]) { $stmts = @($p.Statements) }
        if ($null -ne $stmts) {
            foreach ($s in $stmts) {
                if ($s.Extent.StartOffset -ge $n.Extent.StartOffset) { break }
                if ($terminals -contains $s.GetType().Name) { return $false }
            }
        }
        $n = $p
    }
    return $true
}

function Test-InvokesToken {
    param(
        [string]$Segment, [string]$Token,
        [string[]]$AllowedPrefixes, [string[]]$HollowHeads, [string[]]$InvocationParams
    )
    if (-not (Test-ExecutableSegment -Segment $Segment -AllowedPrefixes $AllowedPrefixes -HollowHeads $HollowHeads)) {
        return $false
    }
    $t = ([string]$Segment).Trim().Trim('`').Trim()
    $stripped = $true
    while ($stripped) {
        $stripped = $false
        foreach ($pre in @($AllowedPrefixes)) {
            $p = [string]$pre
            if ($p.Length -gt 0 -and $t.StartsWith($p, [System.StringComparison]::OrdinalIgnoreCase)) {
                $t = $t.Substring($p.Length).TrimStart(); $stripped = $true
            }
        }
    }
    $want = Get-BareArg -Arg $Token
    if ([string]::IsNullOrWhiteSpace($want)) { return $false }
    $isTok = {
        param([string]$Arg)
        $a = Get-BareArg -Arg $Arg
        if ([string]::Equals($a, $want, [System.StringComparison]::OrdinalIgnoreCase)) { return $true }
        return $a.EndsWith('/' + $want, [System.StringComparison]::OrdinalIgnoreCase)
    }
    $errs = $null
    $ast = $null
    try { $ast = [System.Management.Automation.Language.Parser]::ParseInput($t, [ref]$null, [ref]$errs) } catch { return $false }
    if ($null -eq $ast -or @($errs).Count -gt 0) { return $false }
    $cmds = @($ast.FindAll({ param($n) $n -is [System.Management.Automation.Language.CommandAst] }, $true))
    foreach ($c in $cmds) {
        $els = @($c.CommandElements)
        if ($els.Count -lt 1) { continue }
        # Head position. `& <producer>` lands here too: the call operator produces a CommandAst
        # whose first element IS the operand, which is why T12h's idiomatic shape still passes.
        $hit = (& $isTok ([string]$els[0].Extent.Text))
        for ($i = 0; (-not $hit) -and $i -lt $els.Count; $i++) {
            if ($els[$i] -isnot [System.Management.Automation.Language.CommandParameterAst]) { continue }
            $pname = '-' + [string]$els[$i].ParameterName
            $argText = ''
            if ($null -ne $els[$i].Argument) { $argText = [string]$els[$i].Argument.Extent.Text }
            elseif ($i + 1 -lt $els.Count) { $argText = [string]$els[$i + 1].Extent.Text }
            if ([string]::IsNullOrWhiteSpace($argText)) { continue }
            foreach ($ip in @($InvocationParams)) {
                if ([string]::Equals($pname, [string]$ip, [System.StringComparison]::OrdinalIgnoreCase) -and (& $isTok $argText)) { $hit = $true }
            }
        }
        if ($hit -and (Test-AstReachable -Node $c)) { return $true }
    }
    return $false
}

# Every row listed in TASK_ROW_REQUIRED_TOKENS must carry each of its tokens inside an EXECUTABLE
# segment of the NAMED COLUMN (round-8 finding R8-3 - a whole-row search proved only that the row
# mentions its producer, which row 9's Task prose does independently of what it tells anyone to
# run). Returns the (possibly empty) list of binding errors.
function Test-RowTokens {
    param(
        $Rows, $Required, [string[]]$AllowedPrefixes = @(), [string[]]$HollowHeads = @(),
        [string[]]$InvocationParams = @()
    )
    $errors = @()
    # Fail closed (round-9 finding R9-3): with no declared invocation positions, every position in
    # a segment would count as one and this whole check would be a substring search again.
    if (@($InvocationParams).Count -lt 1) {
        return @('TASK_ROW_INVOCATION_PARAMS is empty - with no declared invocation position, an inert argument would count as running the producer')
    }
    foreach ($p in $Required.PSObject.Properties) {
        $id = [string]$p.Name
        $row = @($Rows | Where-Object { $_.id -eq $id })
        if ($row.Count -lt 1) {
            $errors += ('row "' + $id + '" is listed in TASK_ROW_REQUIRED_TOKENS but no such row exists in the table - a renamed or deleted row silently drops its producer binding')
            continue
        }
        foreach ($colProp in $p.Value.PSObject.Properties) {
            $col = [string]$colProp.Name
            $r = $row[0]
            $ci = -1
            for ($i = 0; $i -lt @($r.header).Count; $i++) {
                if ([string]::Equals([string]$r.header[$i], $col, [System.StringComparison]::OrdinalIgnoreCase)) { $ci = $i; break }
            }
            if ($ci -lt 0) {
                $errors += ('row ' + $id + ' has no "' + $col + '" column in the table header (' + (@($r.header) -join ' / ') + ') - the producer binding cannot be scoped to the cell that is actually executed')
                continue
            }
            if ($ci -ge @($r.cells).Count) {
                $errors += ('row ' + $id + ' has no cell under "' + $col + '" - the row is short of the header it is parsed against')
                continue
            }
            $cell = [string]$r.cells[$ci]
            foreach ($tok in @($colProp.Value)) {
                $t = [string]$tok
                $named = @()
                foreach ($seg in [regex]::Split($cell, ';')) {
                    if (([string]$seg).IndexOf($t, [System.StringComparison]::OrdinalIgnoreCase) -ge 0) { $named += [string]$seg }
                }
                if ($named.Count -lt 1) {
                    $errors += ('row ' + $id + ' does not name "' + $t + '" in its ' + $col + ' cell - the row must bind STATICALLY to the producer that generates its evidence, in the cell that is actually EXECUTED; naming it in neighbouring prose is not running it')
                    continue
                }
                $runs = @($named | Where-Object { Test-InvokesToken -Segment $_ -Token $t -AllowedPrefixes $AllowedPrefixes -HollowHeads $HollowHeads -InvocationParams $InvocationParams })
                if ($runs.Count -lt 1) {
                    $errors += ('row ' + $id + ' names "' + $t + '" in its ' + $col + ' cell but no segment INVOKES it ("' + $named[0].Trim() + '") - it sits in a non-executable segment or as an inert argument. A producer counts as run only where it is the command head, follows the call operator "&", or is the value of ' + (@($InvocationParams) -join ' / ') + '; printing its name, or handing it to another command as data, is not running it')
                }
            }
        }
    }
    return @($errors)
}

# Returns: rows / boundaryIndex (-1 when absent) / required (rows before boundary) /
#          openRequired / invalidAll (malformed status anywhere in the table)
function Measure-Predecessors {
    param([string]$Path, [string]$Boundary)
    $rows = @(Get-TaskRows -Path $Path)
    $idx = -1
    for ($i = 0; $i -lt $rows.Count; $i++) {
        if ($rows[$i].id -eq $Boundary) { $idx = $i; break }
    }
    $required = @()
    if ($idx -ge 0 -and $idx -gt 0) { $required = @($rows[0..($idx - 1)]) }
    $openRequired = @($required | Where-Object { $_.status -eq 'open' })
    $invalidAll = @($rows | Where-Object { $_.status -eq 'invalid' })
    [pscustomobject]@{
        rows          = $rows.Count
        boundaryIndex = $idx
        required      = $required.Count
        openRequired  = $openRequired.Count
        invalidAll    = $invalidAll.Count
        openLines     = @($openRequired)
        invalidLines  = @($invalidAll)
        all           = $rows
    }
}

if ($SelfTest) {
    $tmp = Join-Path ([System.IO.Path]::GetTempPath()) ('task-rows-selftest-' + [guid]::NewGuid().ToString('N'))
    New-Item -ItemType Directory -Path $tmp | Out-Null
    try {
        # T1 - predicate totality: every real row-id FORM must match, and the legend row must not.
        $forms = Join-Path $tmp 'forms.md'
        @(
            '| # | Task | Status |',
            '|---|---|---|',
            '| 1 | do a thing | `[x]` |',
            '| 4a | suffixed row id | `[x]` |',
            '| **H1 - implementation closeout** | | |',
            '| H1-1 | closeout | `[x]` |',
            '| H2-5 | commit draft | `[B]` |',
            '| `[ ]` | Not started |'
        ) | Set-Content -LiteralPath $forms
        $t1 = @(Get-TaskRows -Path $forms)
        if ($t1.Count -ne 4) { Write-Error ('SELFTEST T1 rows=' + $t1.Count + ' expected 4 (predicate misses a row-id form, e.g. the 4a suffix, or the legend/divider leaked in)'); exit 1 }
        if (@($t1 | Where-Object { $_.status -ne 'closed' }).Count -ne 0) { Write-Error 'SELFTEST T1 expected 4 closed rows in an all-closed table'; exit 1 }

        # Shared fixture for T2-T4: one open PREDECESSOR, plus open boundary and successor rows.
        $mixed = Join-Path $tmp 'mixed.md'
        @(
            '| # | Task | Status |',
            '|---|---|---|',
            '| 1 | done | `[x]` |',
            '| 2 | still open PREDECESSOR | `[ ]` |',
            '| H1-1 | run this gate | `[ ]` |',
            '| H1-2 | later row | `[ ]` |'
        ) | Set-Content -LiteralPath $mixed

        # T2 - an open row BEFORE the boundary must be detected (gate would false-pass otherwise).
        $t2 = Measure-Predecessors -Path $mixed -Boundary 'H1-1'
        if ($t2.boundaryIndex -lt 0) { Write-Error 'SELFTEST T2 boundary H1-1 not located'; exit 1 }
        if ($t2.required -ne 2) { Write-Error ('SELFTEST T2 required=' + $t2.required + ' expected 2'); exit 1 }
        if ($t2.openRequired -ne 1) { Write-Error ('SELFTEST T2 openRequired=' + $t2.openRequired + ' expected 1 (open predecessor slips through)'); exit 1 }

        # T3 - an open row AT or AFTER the boundary must NOT block (the N1 deadlock regression).
        $ok = Join-Path $tmp 'ok.md'
        @(
            '| # | Task | Status |',
            '|---|---|---|',
            '| 1 | done | `[x]` |',
            '| 2 | done | `[B]` |',
            '| H1-1 | run this gate (open by construction) | `[ ]` |',
            '| H1-2 | later row (open by construction) | `[ ]` |'
        ) | Set-Content -LiteralPath $ok
        $t3 = Measure-Predecessors -Path $ok -Boundary 'H1-1'
        if ($t3.openRequired -ne 0) { Write-Error ('SELFTEST T3 openRequired=' + $t3.openRequired + ' expected 0 (gate deadlocks on its own row)'); exit 1 }
        if ($t3.required -lt 1) { Write-Error 'SELFTEST T3 required<1 (gate would be vacuous)'; exit 1 }
        if ($t3.invalidAll -ne 0) { Write-Error ('SELFTEST T3 invalidAll=' + $t3.invalidAll + ' expected 0 on a well-formed table'); exit 1 }

        # T4 - an unknown boundary id must be an error, never a silent pass over zero rows.
        $t4 = Measure-Predecessors -Path $ok -Boundary 'H9-9'
        if ($t4.boundaryIndex -ne -1) { Write-Error 'SELFTEST T4 expected boundaryIndex -1 for an unknown row id'; exit 1 }

        # T5 - a boundary that is the FIRST row leaves an empty required set: must be rejected as vacuous.
        $t5 = Measure-Predecessors -Path $ok -Boundary '1'
        if ($t5.required -ne 0) { Write-Error ('SELFTEST T5 required=' + $t5.required + ' expected 0'); exit 1 }

        # ---- R4-1 status-parsing oracles: each of these USED to count as closed. ----

        # T6 - `[/]` (In progress, documented in the task.md legend) is NOT complete.
        $t6r = Get-RowStatus -Line '| 2 | half done | `[/]` |'
        if ($t6r.status -ne 'open') { Write-Error ('SELFTEST T6 `[/]` parsed as ' + $t6r.status + ' - an in-progress predecessor would close the gate'); exit 1 }
        $inprog = Join-Path $tmp 'inprogress.md'
        @(
            '| # | Task | Status |',
            '|---|---|---|',
            '| 1 | done | `[x]` |',
            '| 2 | IN PROGRESS predecessor | `[/]` |',
            '| H1-1 | run this gate | `[ ]` |'
        ) | Set-Content -LiteralPath $inprog
        $t6 = Measure-Predecessors -Path $inprog -Boundary 'H1-1'
        if ($t6.openRequired -ne 1) { Write-Error ('SELFTEST T6 openRequired=' + $t6.openRequired + ' expected 1 (an in-progress row must block)'); exit 1 }

        # T7 - an unknown marker is INVALID, never closed.
        $t7 = Get-RowStatus -Line '| 2 | mystery | `[?]` |'
        if ($t7.status -ne 'invalid') { Write-Error ('SELFTEST T7 unknown status `[?]` parsed as ' + $t7.status); exit 1 }
        $t7b = Get-RowStatus -Line '| 2 | mystery | `[done]` |'
        if ($t7b.status -ne 'invalid') { Write-Error ('SELFTEST T7b unknown status `[done]` parsed as ' + $t7b.status); exit 1 }

        # T8 - a missing/empty status cell is INVALID, never closed.
        $t8 = Get-RowStatus -Line '| 2 | no status column at all | |'
        if ($t8.status -ne 'invalid') { Write-Error ('SELFTEST T8 missing status parsed as ' + $t8.status); exit 1 }
        $t8b = Get-RowStatus -Line '| 2 | truncated row'
        if ($t8b.status -ne 'invalid') { Write-Error ('SELFTEST T8b unterminated row parsed as ' + $t8b.status); exit 1 }

        # T9 - two markers in the status cell are ambiguous, so INVALID (not "the good one wins").
        $t9 = Get-RowStatus -Line '| 2 | ambiguous | `[x]` `[ ]` |'
        if ($t9.status -ne 'invalid') { Write-Error ('SELFTEST T9 duplicate status markers parsed as ' + $t9.status); exit 1 }
        $t9b = Get-RowStatus -Line '| 2 | decorated | `[x]` (see note) |'
        if ($t9b.status -ne 'invalid') { Write-Error ('SELFTEST T9b decorated status cell parsed as ' + $t9b.status); exit 1 }

        # T10 - a REAL-table shape: row 7a's prose carries an inline `[B]` while the status cell
        #       is open. The inline mention must not close the row (whole-line scanning would).
        $t10 = Get-RowStatus -Line '| 7a | run E2E; `[B]` only per the evidence-gated rule below | tester | cmd | 7 | shared | out | - | `[ ]` |'
        if ($t10.status -ne 'open') { Write-Error ('SELFTEST T10 inline `[B]` in prose parsed as ' + $t10.status + ' - status must come from the status CELL'); exit 1 }

        # T12 (round-7 finding R7-2) - the producer binding is STATIC. A row that merely says
        #      "run the dev server" passes every status check while quietly authorising the
        #      hand-run this plan's whole evidence chain exists to forbid.
        $req = [pscustomobject]@{ '9' = [pscustomobject]@{ 'Validation' = @('docs/execution/plans/2026-08-27-p9-capture-native-picker/run-live-smoke.ps1') } }
        $oraclePrefixes = @('rtk proxy ', 'npx ')
        $oracleHollow = @('echo', 'rem', '#', 'type')
        $oracleInvoke = @($sets.TASK_ROW_INVOCATION_PARAMS)
        $bound = @(Get-TaskRows -Path (
            $(  $f = Join-Path $tmp 'bound.md'
                @(
                    '| # | Task | Validation | Status |',
                    '|---|---|---|---|',
                    '| 9 | live smoke | pwsh -File docs/execution/plans/2026-08-27-p9-capture-native-picker/run-live-smoke.ps1 | `[ ]` |'
                ) | Set-Content -LiteralPath $f
                $f)))
        $t12ok = @(Test-RowTokens -Rows $bound -Required $req -AllowedPrefixes $oraclePrefixes -HollowHeads $oracleHollow -InvocationParams $oracleInvoke)
        if ($t12ok.Count -ne 0) {
            Write-Error ('SELFTEST T12 a row that DOES run its producer was rejected: ' + ($t12ok -join ' | ')); exit 1
        }
        $unbound = @(Get-TaskRows -Path (
            $(  $f = Join-Path $tmp 'unbound.md'
                @(
                    '| # | Task | Validation | Status |',
                    '|---|---|---|---|',
                    '| 9 | live smoke | npm --prefix ui run dev, then eyeball the picker | `[ ]` |'
                ) | Set-Content -LiteralPath $f
                $f)))
        $t12 = @(Test-RowTokens -Rows $unbound -Required $req -AllowedPrefixes $oraclePrefixes -HollowHeads $oracleHollow -InvocationParams $oracleInvoke)
        if ($t12.Count -ne 1) { Write-Error ('SELFTEST T12 a row that runs the command by hand was accepted (' + $t12.Count + ' errors)'); exit 1 }
        if ($t12[0] -notmatch 'does not name') { Write-Error ('SELFTEST T12 rejected for the WRONG reason: ' + $t12[0]); exit 1 }
        # T12b - deleting or renaming the row must FAIL, not vacuously pass.
        $t12b = @(Test-RowTokens -Rows @($unbound | Where-Object { $_.id -ne '9' }) -Required $req -AllowedPrefixes $oraclePrefixes -HollowHeads $oracleHollow -InvocationParams $oracleInvoke)
        if ($t12b.Count -ne 1) { Write-Error 'SELFTEST T12b a missing row passed the binding check vacuously'; exit 1 }
        if ($t12b[0] -notmatch 'no such row exists') { Write-Error ('SELFTEST T12b rejected for the WRONG reason: ' + $t12b[0]); exit 1 }

        # T12c (round-8 finding R8-3) - THE reviewer's bypass, verbatim in shape. The Task cell
        #       keeps the producer path (row 9's real prose does), while the Validation cell is
        #       swapped for a hand-run. A whole-row search passes this; a column-scoped one must
        #       not, because the Validation cell is the only cell anybody executes.
        $prose = @(Get-TaskRows -Path (
            $(  $f = Join-Path $tmp 'prose.md'
                @(
                    '| # | Task | Validation | Status |',
                    '|---|---|---|---|',
                    '| 9 | produce the smoke through docs/execution/plans/2026-08-27-p9-capture-native-picker/run-live-smoke.ps1 | npm --prefix ui run dev, then type the receipt | `[ ]` |'
                ) | Set-Content -LiteralPath $f
                $f)))
        if ($prose[0].text.IndexOf('run-live-smoke.ps1') -lt 0) {
            Write-Error 'SELFTEST T12c fixture is wrong - the whole-row search this oracle exists to defeat would not have passed it'; exit 1
        }
        $t12c = @(Test-RowTokens -Rows $prose -Required $req -AllowedPrefixes $oraclePrefixes -HollowHeads $oracleHollow -InvocationParams $oracleInvoke)
        if ($t12c.Count -ne 1) { Write-Error ('SELFTEST T12c a row naming its producer only in PROSE while running the command by hand was accepted (' + $t12c.Count + ' errors)'); exit 1 }
        if ($t12c[0] -notmatch 'Validation cell') { Write-Error ('SELFTEST T12c rejected for the WRONG reason: ' + $t12c[0]); exit 1 }

        # T12d - the token IS in the Validation cell, but only in a segment that prints its name.
        #       Presence in the right cell is not execution.
        $echoed = @(Get-TaskRows -Path (
            $(  $f = Join-Path $tmp 'echoed.md'
                @(
                    '| # | Task | Validation | Status |',
                    '|---|---|---|---|',
                    '| 9 | live smoke | echo docs/execution/plans/2026-08-27-p9-capture-native-picker/run-live-smoke.ps1 | `[ ]` |'
                ) | Set-Content -LiteralPath $f
                $f)))
        $t12d = @(Test-RowTokens -Rows $echoed -Required $req -AllowedPrefixes $oraclePrefixes -HollowHeads $oracleHollow -InvocationParams $oracleInvoke)
        if ($t12d.Count -ne 1) { Write-Error ('SELFTEST T12d an echoed producer was accepted as an invocation (' + $t12d.Count + ' errors)'); exit 1 }
        if ($t12d[0] -notmatch 'non-executable segment') { Write-Error ('SELFTEST T12d rejected for the WRONG reason: ' + $t12d[0]); exit 1 }

        # T12e - the cell splitter must survive the real table's pipes. A Validation cell whose
        #       command contains `| Select-Object` is one cell, not two; if it split there, the
        #       column index would shift and every binding above would be checked against the
        #       wrong cell - failing open on the next row that happens to contain the token.
        $piped = @(Get-TaskRows -Path (
            $(  $f = Join-Path $tmp 'piped.md'
                @(
                    '| # | Task | Validation | Status |',
                    '|---|---|---|---|',
                    '| 9 | live smoke | `pwsh -File docs/execution/plans/2026-08-27-p9-capture-native-picker/run-live-smoke.ps1; Get-Content out.txt | Select-Object -Last 5` | `[ ]` |'
                ) | Set-Content -LiteralPath $f
                $f)))
        if (@($piped[0].cells).Count -ne @($piped[0].header).Count) {
            Write-Error ('SELFTEST T12e a pipe inside a code span split the row into ' + @($piped[0].cells).Count + ' cells against a ' + @($piped[0].header).Count + '-cell header'); exit 1
        }
        $t12e = @(Test-RowTokens -Rows $piped -Required $req -AllowedPrefixes $oraclePrefixes -HollowHeads $oracleHollow -InvocationParams $oracleInvoke)
        if ($t12e.Count -ne 0) { Write-Error ('SELFTEST T12e a valid piped Validation cell was rejected: ' + ($t12e -join ' | ')); exit 1 }

        # T12f (round-9 finding R9-3) - THE round-9 bypass, verbatim: the token is in the right
        #       cell, in a segment whose head is a real executable, and the row still runs nothing
        #       but a print. `-Command { Write-Output ... }` scored ERROR_COUNT=0 before this.
        $inert = @(Get-TaskRows -Path (
            $(  $f = Join-Path $tmp 'inert.md'
                @(
                    '| # | Task | Validation | Status |',
                    '|---|---|---|---|',
                    '| 9 | live smoke | rtk proxy pwsh -NoProfile -Command { Write-Output docs/execution/plans/2026-08-27-p9-capture-native-picker/run-live-smoke.ps1 } | `[ ]` |'
                ) | Set-Content -LiteralPath $f
                $f)))
        $t12f = @(Test-RowTokens -Rows $inert -Required $req -AllowedPrefixes $oraclePrefixes -HollowHeads $oracleHollow -InvocationParams $oracleInvoke)
        if ($t12f.Count -ne 1) { Write-Error ('SELFTEST T12f a producer PRINTED from inside a scriptblock was accepted as an invocation (' + $t12f.Count + ' errors)'); exit 1 }
        if ($t12f[0] -notmatch 'no segment INVOKES it') { Write-Error ('SELFTEST T12f rejected for the WRONG reason: ' + $t12f[0]); exit 1 }

        # T12g - the same defect without a scriptblock: the producer is an inert ARGUMENT to a
        #       head that runs some OTHER script. Position, not presence, is the property.
        $arg = @(Get-TaskRows -Path (
            $(  $f = Join-Path $tmp 'arg.md'
                @(
                    '| # | Task | Validation | Status |',
                    '|---|---|---|---|',
                    '| 9 | live smoke | rtk proxy pwsh -NoProfile -File docs/execution/plans/2026-08-27-p9-capture-native-picker/assert-smoke-disposition.ps1 -Note docs/execution/plans/2026-08-27-p9-capture-native-picker/run-live-smoke.ps1 | `[ ]` |'
                ) | Set-Content -LiteralPath $f
                $f)))
        $t12g = @(Test-RowTokens -Rows $arg -Required $req -AllowedPrefixes $oraclePrefixes -HollowHeads $oracleHollow -InvocationParams $oracleInvoke)
        if ($t12g.Count -ne 1) { Write-Error ('SELFTEST T12g a producer passed as an inert argument to another script was accepted (' + $t12g.Count + ' errors)'); exit 1 }
        if ($t12g[0] -notmatch 'no segment INVOKES it') { Write-Error ('SELFTEST T12g rejected for the WRONG reason: ' + $t12g[0]); exit 1 }

        # T12h (positive) - a rule that only tightens can reject honest rows. The two other
        #       legitimate invocation shapes must still pass: the call operator, and the producer
        #       as the command head itself.
        foreach ($shape in @(
            '& docs/execution/plans/2026-08-27-p9-capture-native-picker/run-live-smoke.ps1 *> C:/Temp/av-kit/run-live-smoke.txt',
            'docs/execution/plans/2026-08-27-p9-capture-native-picker/run-live-smoke.ps1 *> C:/Temp/av-kit/run-live-smoke.txt'
        )) {
            $okRow = @(Get-TaskRows -Path (
                $(  $f = Join-Path $tmp 'shape.md'
                    @(
                        '| # | Task | Validation | Status |',
                        '|---|---|---|---|',
                        ('| 9 | live smoke | ' + $shape + ' | `[ ]` |')
                    ) | Set-Content -LiteralPath $f
                    $f)))
            $t12h = @(Test-RowTokens -Rows $okRow -Required $req -AllowedPrefixes $oraclePrefixes -HollowHeads $oracleHollow -InvocationParams $oracleInvoke)
            if ($t12h.Count -ne 0) { Write-Error ('SELFTEST T12h an honest invocation shape was rejected ("' + $shape + '"): ' + ($t12h -join ' | ')); exit 1 }
        }

        # T12j (positive) - the counterpart to T12f, and the reason this gate does NOT blank
        #       scriptblock bodies: the same `-Command { ... }` head that PRINTS a path (rejected
        #       above) genuinely RUNS it one operator later. A rule that rejected both would be
        #       measuring nesting instead of position, and would push honest rows out of the table.
        $nested = @(Get-TaskRows -Path (
            $(  $f = Join-Path $tmp 'nested.md'
                @(
                    '| # | Task | Validation | Status |',
                    '|---|---|---|---|',
                    '| 9 | live smoke | rtk proxy pwsh -NoProfile -Command { & docs/execution/plans/2026-08-27-p9-capture-native-picker/run-live-smoke.ps1 } | `[ ]` |'
                ) | Set-Content -LiteralPath $f
                $f)))
        $t12j = @(Test-RowTokens -Rows $nested -Required $req -AllowedPrefixes $oraclePrefixes -HollowHeads $oracleHollow -InvocationParams $oracleInvoke)
        if ($t12j.Count -ne 0) { Write-Error ('SELFTEST T12j a real invocation inside a -Command scriptblock was rejected: ' + ($t12j -join ' | ')); exit 1 }

        # T12k/T12l/T12m (round-10 finding R10-3) - THE REVIEWER'S THREE PROBES, verbatim in shape.
        #       Each puts the producer in a whitespace position the old scan read as an invocation
        #       while the shell runs nothing: inside a block comment, after a terminal statement,
        #       and behind the stop-parsing token. All three must now be rejected for the same
        #       reason a printed path is - the cell does not invoke the producer. (Which RULE
        #       rejects each is asserted separately: mutation testing showed T12l is refused by the
        #       `;` split plus the parse requirement, before reachability is consulted, so the walk
        #       gets its own probe in T12n rather than borrowing this one's PASS.)
        $prod = 'docs/execution/plans/2026-08-27-p9-capture-native-picker/run-live-smoke.ps1'
        foreach ($probe in @(
            @{ id = 'T12k'; what = 'a producer named only inside a block comment';
               cell = 'rtk proxy pwsh -NoProfile -Command { <# & ' + $prod + ' #> Write-Output noop }' },
            @{ id = 'T12l'; what = 'a producer placed after a terminal statement';
               cell = 'rtk proxy pwsh -NoProfile -Command { exit 0; & ' + $prod + ' }' },
            @{ id = 'T12m'; what = 'a producer behind the stop-parsing token';
               cell = 'rtk proxy pwsh -NoProfile --% & ' + $prod }
        )) {
            $fakeRow = @(Get-TaskRows -Path (
                $(  $f = Join-Path $tmp 'fake-position.md'
                    @(
                        '| # | Task | Validation | Status |',
                        '|---|---|---|---|',
                        ('| 9 | live smoke | ' + [string]$probe.cell + ' | `[ ]` |')
                    ) | Set-Content -LiteralPath $f
                    $f)))
            $fk = @(Test-RowTokens -Rows $fakeRow -Required $req -AllowedPrefixes $oraclePrefixes -HollowHeads $oracleHollow -InvocationParams $oracleInvoke)
            if ($fk.Count -ne 1) { Write-Error ('SELFTEST ' + [string]$probe.id + ' ' + [string]$probe.what + ' was accepted as an invocation (' + $fk.Count + ' errors)'); exit 1 }
            if ($fk[0] -notmatch 'no segment INVOKES it') { Write-Error ('SELFTEST ' + [string]$probe.id + ' rejected for the WRONG reason: ' + $fk[0]); exit 1 }
        }

        # T12n - the reachability rule itself, exercised where it is actually load-bearing and
        #       called directly because no single-line CELL can reach it (see T12l above). A
        #       terminal statement and the invocation inside ONE parseable segment: the shell runs
        #       nothing, and only the AST walk can say so.
        $reach = "rtk proxy pwsh -NoProfile -Command { exit 0`n & " + $prod + " }"
        if (Test-InvokesToken -Segment $reach -Token $prod -AllowedPrefixes $oraclePrefixes -HollowHeads $oracleHollow -InvocationParams $oracleInvoke) {
            Write-Error 'SELFTEST T12n a command placed after a terminal statement in the same parseable segment counted as an invocation'; exit 1
        }
        $reachOk = "rtk proxy pwsh -NoProfile -Command { Write-Output start`n & " + $prod + " }"
        if (-not (Test-InvokesToken -Segment $reachOk -Token $prod -AllowedPrefixes $oraclePrefixes -HollowHeads $oracleHollow -InvocationParams $oracleInvoke)) {
            Write-Error 'SELFTEST T12n positive control: a REACHABLE invocation in the same shape was rejected - the walk is refusing on nesting, not on position'; exit 1
        }

        # T12i - and the position list itself must fail closed, or T12f/T12g pass vacuously.
        $t12i = @(Test-RowTokens -Rows $bound -Required $req -AllowedPrefixes $oraclePrefixes -HollowHeads $oracleHollow -InvocationParams @())
        if ($t12i.Count -lt 1) { Write-Error 'SELFTEST T12i an empty TASK_ROW_INVOCATION_PARAMS was treated as "any position counts"'; exit 1 }
        if ($t12i[0] -notmatch 'TASK_ROW_INVOCATION_PARAMS is empty') { Write-Error ('SELFTEST T12i rejected for the WRONG reason: ' + $t12i[0]); exit 1 }

        # T11 - an invalid row anywhere in the table must surface, even when it is a successor.
        $bad = Join-Path $tmp 'bad.md'
        @(
            '| # | Task | Status |',
            '|---|---|---|',
            '| 1 | done | `[x]` |',
            '| H1-1 | run this gate | `[ ]` |',
            '| H1-2 | malformed successor | `[?]` |'
        ) | Set-Content -LiteralPath $bad
        $t11 = Measure-Predecessors -Path $bad -Boundary 'H1-1'
        if ($t11.invalidAll -ne 1) { Write-Error ('SELFTEST T11 invalidAll=' + $t11.invalidAll + ' expected 1 (a malformed status must fail the table)'); exit 1 }

        'PASS: TASK_ROW_GATE self-test (T1 4 row-id forms; T2 open predecessor caught; T3 open boundary/successor allowed; T4 unknown boundary rejected; T5 empty predecessor set rejected; T6 `[/]` blocks; T7 unknown marker invalid; T8 missing status invalid; T9 duplicate/decorated status invalid; T10 inline prose marker ignored; T11 malformed successor fails; T12/T12b producer-token binding enforced, missing row not vacuous; T12c producer named only in Task prose while Validation hand-runs the command rejected, T12d echoed producer rejected, T12e piped Validation cell parsed as one cell; T12f/T12g a producer printed from a scriptblock or passed as an inert argument rejected, T12h the call-operator and bare-head invocation shapes still accepted, T12j a real invocation inside the same scriptblock head still accepted, T12i an empty invocation-position set fails closed; T12k/T12l/T12m a producer in a comment, after `exit 0;`, or behind `--%` is not an invocation, T12n a post-terminal command in one parseable segment rejected by the reachability walk while the reachable shape still passes)'
        exit 0
    } finally {
        Remove-Item -LiteralPath $tmp -Recurse -Force -ErrorAction SilentlyContinue
    }
}

if ([string]::IsNullOrWhiteSpace($Through)) {
    Write-Error 'TASK_ROW_GATE requires -Through <rowId>: the gate proves every row BEFORE <rowId> is closed'
    exit 1
}
if (-not (Test-Path -LiteralPath $taskPath)) { Write-Error ('missing TASK_FILE ' + $taskPath); exit 1 }
$r = Measure-Predecessors -Path $taskPath -Boundary $Through
if ($r.rows -lt 1) {
    Write-Error ('TASK_ROW_GATE vacuous: row predicate matched 0 rows in ' + $taskPath)
    exit 1
}
if ($r.invalidAll -ne 0) {
    $r.invalidLines | ForEach-Object { 'INVALID row ' + $_.id + ' (line ' + $_.line + '): ' + $_.detail }
    Write-Error ('TASK_ROW_GATE ' + $r.invalidAll + ' row(s) carry a malformed status cell - status must be exactly `[ ]`, `[/]`, `[x]`, or `[B]`')
    exit 1
}
# The static producer binding is checked on every live run, independent of -Through: a row
# can lose its producer token long before that row's turn comes.
$rowTokens = $sets.TASK_ROW_REQUIRED_TOKENS
if ($null -eq $rowTokens -or @($rowTokens.PSObject.Properties).Count -lt 1) {
    Write-Error 'TASK_ROW_GATE vacuous: TASK_ROW_REQUIRED_TOKENS is empty - the producer-binding check would pass trivially'
    exit 1
}
$invokeParams = @($sets.TASK_ROW_INVOCATION_PARAMS)
if ($invokeParams.Count -lt 1) {
    Write-Error 'TASK_ROW_GATE vacuous: TASK_ROW_INVOCATION_PARAMS is empty - an inert argument would count as running the producer'
    exit 1
}
$bindErrors = @(Test-RowTokens -Rows $r.all -Required $rowTokens -AllowedPrefixes @($sets.VALIDATION_ALLOWED_PREFIXES) -HollowHeads @($sets.SCRIPT_HOLLOW_HEADS) -InvocationParams $invokeParams)
if ($bindErrors.Count -ne 0) {
    $bindErrors | ForEach-Object { 'UNBOUND ' + $_ }
    Write-Error ('TASK_ROW_GATE ' + $bindErrors.Count + ' row(s) do not name the producer that generates their evidence')
    exit 1
}
if ($r.boundaryIndex -lt 0) {
    Write-Error ('TASK_ROW_GATE boundary row id "' + $Through + '" not found in ' + $taskPath)
    exit 1
}
if ($r.required -lt 1) {
    Write-Error ('TASK_ROW_GATE vacuous: boundary "' + $Through + '" has 0 predecessor rows')
    exit 1
}
if ($r.openRequired -ne 0) {
    $r.openLines | ForEach-Object { $_.text }
    Write-Error ('TASK_ROW_GATE ' + $r.openRequired + ' of ' + $r.required + ' rows before "' + $Through + '" still open (`[ ]` or `[/]`)')
    exit 1
}
'PASS: TASK_ROW_GATE ' + $r.required + ' of ' + $r.rows + ' rows closed (`[x]`/`[B]`) through "' + $Through + '"; ' + @($rowTokens.PSObject.Properties).Count + ' producer binding(s) statically named'
exit 0
