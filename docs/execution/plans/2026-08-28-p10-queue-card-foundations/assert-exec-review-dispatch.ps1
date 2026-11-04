# Bind EXEC_REVIEW_FILE to one Invoke-CodexDispatch receipt (dispatch_id in frontmatter).
# Rejects reusable older changes_required receipts and self-authored approved files.
$ErrorActionPreference = 'Stop'
$setsPath = Join-Path $PSScriptRoot 'named-sets.json'
if (-not (Test-Path -LiteralPath $setsPath)) {
    Write-Error ('missing NAMED_SETS_FILE ' + $setsPath)
    exit 1
}
$sets = Get-Content -LiteralPath $setsPath -Raw | ConvertFrom-Json
$reviewPath = [string]$sets.EXEC_REVIEW_FILE
$agent = [string]$sets.REVIEWER_AGENT
$dispatchDir = [string]$sets.DISPATCH_DIR
$schema = [string]$sets.DISPATCH_STATUS_SCHEMA
$idField = [string]$sets.DISPATCH_ID_FIELD
$expectedMode = [string]$sets.EXEC_REVIEW_MODE
$expectedVerdict = [string]$sets.EXEC_REVIEW_APPROVED
if ([string]::IsNullOrWhiteSpace($reviewPath) -or [string]::IsNullOrWhiteSpace($agent) -or [string]::IsNullOrWhiteSpace($idField)) {
    Write-Error 'named-sets missing EXEC_REVIEW_FILE, REVIEWER_AGENT, or DISPATCH_ID_FIELD'
    exit 1
}
if (-not (Test-Path -LiteralPath $reviewPath)) {
    Write-Error ('missing EXEC_REVIEW_FILE ' + $reviewPath)
    exit 1
}

function Get-FrontmatterValue {
    param([string]$Frontmatter, [string]$Key)
    $pattern = '(?m)^' + [regex]::Escape($Key) + ':\s*"?([^"\r\n]+)"?\s*$'
    $m = [regex]::Match($Frontmatter, $pattern)
    if (-not $m.Success) { return $null }
    return $m.Groups[1].Value.Trim()
}

$reviewText = Get-Content -LiteralPath $reviewPath -Raw
if ($reviewText -notmatch '(?s)\A---\r?\n(?<fm>.*?)\r?\n---') {
    Write-Error 'EXEC_REVIEW_FILE missing YAML frontmatter'
    exit 1
}
$fm = $Matches['fm']
$liveAgent = Get-FrontmatterValue -Frontmatter $fm -Key 'agent'
$liveMode = Get-FrontmatterValue -Frontmatter $fm -Key 'review_mode'
$liveVerdict = Get-FrontmatterValue -Frontmatter $fm -Key 'verdict'
$liveFindings = Get-FrontmatterValue -Frontmatter $fm -Key 'findings_count'
$dispatchId = Get-FrontmatterValue -Frontmatter $fm -Key $idField
if ($liveAgent -ne $agent) {
    Write-Error ('frontmatter agent=' + $liveAgent + ' expected ' + $agent)
    exit 1
}
if ($liveMode -ne $expectedMode) {
    Write-Error ('frontmatter review_mode=' + $liveMode + ' expected ' + $expectedMode)
    exit 1
}
if ($liveVerdict -ne $expectedVerdict) {
    Write-Error ('frontmatter verdict=' + $liveVerdict + ' expected ' + $expectedVerdict)
    exit 1
}
if ($liveFindings -ne '0') {
    Write-Error ('frontmatter findings_count=' + $liveFindings + ' expected 0')
    exit 1
}
if ([string]::IsNullOrWhiteSpace($dispatchId)) {
    Write-Error ('frontmatter missing ' + $idField + ' (must equal Invoke-CodexDispatch -DispatchId)')
    exit 1
}

$statusPath = Join-Path $dispatchDir (Join-Path $dispatchId 'status.json')
if (-not (Test-Path -LiteralPath $statusPath)) {
    Write-Error ('missing status.json for ' + $idField + '=' + $dispatchId + ' at ' + $statusPath)
    exit 1
}
$st = Get-Content -LiteralPath $statusPath -Raw | ConvertFrom-Json
if ([string]$st.schema_version -ne $schema) {
    Write-Error ('status schema_version=' + $st.schema_version + ' expected ' + $schema)
    exit 1
}
if ([int]$st.exit_code -ne 0) {
    Write-Error ('dispatch exit_code=' + $st.exit_code + ' for ' + $dispatchId)
    exit 1
}
if ([string]$st.model -ne $agent) {
    Write-Error ('dispatch model=' + $st.model + ' expected ' + $agent)
    exit 1
}
if ([string]$st.dispatch_id -ne $dispatchId) {
    Write-Error ('status dispatch_id=' + $st.dispatch_id + ' != frontmatter ' + $dispatchId)
    exit 1
}

$promptPath = Join-Path $dispatchDir (Join-Path $dispatchId 'prompt_temp.txt')
if (-not (Test-Path -LiteralPath $promptPath)) {
    Write-Error ('missing prompt_temp.txt for ' + $dispatchId)
    exit 1
}
$prompt = (Get-Content -LiteralPath $promptPath -Raw).Replace('\', '/')
$reviewNorm = $reviewPath.Replace('\', '/')
$reviewName = [System.IO.Path]::GetFileName($reviewPath)
if (($prompt -notlike ('*' + $reviewNorm + '*')) -and ($prompt -notlike ('*' + $reviewName + '*'))) {
    Write-Error ('dispatch prompt does not name ' + $reviewPath)
    exit 1
}

$finalPath = [string]$st.output_paths.final_output
if ([string]::IsNullOrWhiteSpace($finalPath) -or -not (Test-Path -LiteralPath $finalPath)) {
    Write-Error ('missing dispatch final.md for ' + $dispatchId)
    exit 1
}
$final = Get-Content -LiteralPath $finalPath -Raw
$verdictMatch = [regex]::Match($final, '(?im)verdict:\s*`?(approved|changes_required)`?')
if (-not $verdictMatch.Success) {
    Write-Error ('dispatch final.md has no verdict token for ' + $dispatchId)
    exit 1
}
if ($verdictMatch.Groups[1].Value -ne $expectedVerdict) {
    Write-Error ('dispatch final.md verdict=' + $verdictMatch.Groups[1].Value + ' expected ' + $expectedVerdict + ' (a prior changes_required receipt cannot approve a self-authored file)')
    exit 1
}

'PASS: EXEC_REVIEW_DISPATCH agent=' + $agent + ' ' + $idField + '=' + $dispatchId
exit 0
