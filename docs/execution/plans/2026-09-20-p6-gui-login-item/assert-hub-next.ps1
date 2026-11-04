# Bind BUILD_PLAN hub Next + prior plan slashes + this MEU plan folder. Names from named-sets.json.
# Next: lives in a narrative paragraph; require exactly one Next: whose remainder starts with HUB_NEXT_AFTER.
$ErrorActionPreference = 'Stop'
$setsPath = Join-Path $PSScriptRoot 'named-sets.json'
$sets = Get-Content -LiteralPath $setsPath -Raw | ConvertFrom-Json
$hubPath = 'docs/BUILD_PLAN.md'
$yamlPath = '.agent/context/meu-status.yaml'
if (-not (Test-Path -LiteralPath $hubPath)) {
    Write-Error ('missing ' + $hubPath)
    exit 1
}
if (-not (Test-Path -LiteralPath $yamlPath)) {
    Write-Error ('missing ' + $yamlPath)
    exit 1
}
$hub = Get-Content -LiteralPath $hubPath -Raw
$yaml = Get-Content -LiteralPath $yamlPath -Raw
$wantNext = [string]$sets.HUB_NEXT_AFTER
$nextHits = @([regex]::Matches($hub, 'Next:'))
if ($nextHits.Count -ne 1) {
    Write-Error ('HUB_NEXT_FIELD count=' + $nextHits.Count + ' expected 1')
    exit 1
}
$idx = $hub.IndexOf('Next:', [StringComparison]::Ordinal)
$after = $hub.Substring($idx + 5).TrimStart()
$lineRest = (($after -split "`r?`n")[0]).Trim()
if (-not $lineRest.StartsWith($wantNext, [StringComparison]::Ordinal)) {
    Write-Error ('HUB_NEXT_AFTER mismatch start=[' + $lineRest + '] want prefix [' + $wantNext + ']')
    exit 1
}
foreach ($p in @($sets.PRIOR_PLAN_SLASHES)) {
    $needle = [string]$p
    if ($yaml.IndexOf($needle, [StringComparison]::Ordinal) -lt 0) {
        Write-Error ('PRIOR_PLAN_SLASHES missing from meu-status.yaml: ' + $needle)
        exit 1
    }
}
$planBind = [string]$sets.PLAN_FOLDER
if ($yaml.IndexOf($planBind, [StringComparison]::Ordinal) -lt 0) {
    Write-Error ('MEU plan binding missing from meu-status.yaml: ' + $planBind)
    exit 1
}
if ($hub.IndexOf('MEU-61', [StringComparison]::Ordinal) -lt 0) {
    Write-Error 'BUILD_PLAN.md missing MEU-61'
    exit 1
}
'PASS: hub Next + prior plans + MEU-61 bind'
exit 0
