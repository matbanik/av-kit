# Non-vacuous AC-60.12 census: named test() block must contain E2E_BODY_TOKENS.
# E2E_TESTIDS must be registered in ui/tests/e2e/test-ids.ts (not "anywhere in the spec").
$ErrorActionPreference = 'Stop'
$setsPath = Join-Path $PSScriptRoot 'named-sets.json'
$sets = Get-Content -LiteralPath $setsPath -Raw | ConvertFrom-Json
$spec = [string]$sets.E2E_SPEC
$idsFile = 'ui/tests/e2e/test-ids.ts'
if (-not (Test-Path -LiteralPath $spec)) {
    Write-Error ('missing E2E_SPEC ' + $spec)
    exit 1
}
if (-not (Test-Path -LiteralPath $idsFile)) {
    Write-Error ('missing test-ids.ts ' + $idsFile)
    exit 1
}
$text = Get-Content -LiteralPath $spec -Raw
$idsText = Get-Content -LiteralPath $idsFile -Raw
$decl = [string]$sets.E2E_TEST_DECL

function Get-NamedTestBlock {
    param([string]$Source, [string]$Decl, [string]$Case)
    $lines = $Source -split "`r?`n"
    $start = -1
    for ($i = 0; $i -lt $lines.Length; $i++) {
        if ($lines[$i].Contains($Decl) -and $lines[$i].Contains($Case)) {
            $start = $i
            break
        }
    }
    if ($start -lt 0) { return $null }
    $buf = New-Object System.Text.StringBuilder
    $depth = 0
    $seen = $false
    for ($i = $start; $i -lt $lines.Length; $i++) {
        $line = $lines[$i]
        [void]$buf.AppendLine($line)
        foreach ($ch in $line.ToCharArray()) {
            if ($ch -eq '{') { $depth++; $seen = $true }
            elseif ($ch -eq '}') { $depth-- }
        }
        if ($seen -and $depth -le 0) { break }
    }
    return $buf.ToString()
}

foreach ($case in @($sets.E2E_REQUIRED_CASES)) {
    $block = Get-NamedTestBlock -Source $text -Decl $decl -Case ([string]$case)
    if ([string]::IsNullOrWhiteSpace($block)) {
        Write-Error ('E2E_SPEC missing test( declaration whose title contains ' + $case)
        exit 1
    }
    foreach ($tok in @($sets.E2E_BODY_TOKENS)) {
        $needle = [string]$tok
        if ($block.IndexOf($needle, [StringComparison]::Ordinal) -lt 0) {
            Write-Error ('E2E named block for ' + $case + ' missing body token ' + $needle)
            exit 1
        }
    }
}

foreach ($id in @($sets.E2E_TESTIDS)) {
    $token = [string]$id
    if ($idsText.IndexOf($token, [StringComparison]::Ordinal) -lt 0) {
        Write-Error ('E2E testid unregistered in test-ids.ts: ' + $token)
        exit 1
    }
}
'PASS: E2E census'
exit 0
