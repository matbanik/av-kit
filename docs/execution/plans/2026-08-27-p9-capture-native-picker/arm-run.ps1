# RUN_ARM - clears a run's artifact and stamps the moment it was cleared, so a consumer gate
# can prove the artifact it reads was produced AFTER arming rather than being a stale green
# receipt from an earlier run (round-5 finding R4-3-R5).
#
# Round-11 trim: the nonce / SHA-256 / call-stack-owner protocol that used to live here is
# deleted. It defended against an operator hand-authoring a passing receipt - a threat model
# that never applied, since anyone who can type a receipt can also edit these scripts. What
# survives is the one property a script CAN establish: this artifact is newer than this stamp.
param(
    [Parameter(Mandatory = $true)][string]$Name,
    [switch]$SelfTest
)
$ErrorActionPreference = 'Stop'
$setsPath = Join-Path $PSScriptRoot 'named-sets.json'
if (-not (Test-Path -LiteralPath $setsPath)) { Write-Error ('missing NAMED_SETS_FILE ' + $setsPath); exit 1 }
$sets = Get-Content -LiteralPath $setsPath -Raw | ConvertFrom-Json
. (Join-Path $PSScriptRoot 'lib-disposition.ps1')

$entry = $sets.RUN_STAMPS.$Name
if ($null -eq $entry) { Write-Error ('unknown run name "' + $Name + '" - not in RUN_STAMPS'); exit 1 }
$artifact = [string]$entry.artifact
$stamp = [string]$entry.stamp

if ($SelfTest) {
    $tmp = Join-Path ([System.IO.Path]::GetTempPath()) ('arm-selftest-' + [guid]::NewGuid().ToString('N'))
    New-Item -ItemType Directory -Path $tmp | Out-Null
    try {
        $a = Join-Path $tmp 'artifact.json'; $s = Join-Path $tmp 'stamp.txt'
        # A1 a missing stamp is never fresh - an unarmed step cannot claim this run produced it.
        'x' | Set-Content -LiteralPath $a
        if ($null -eq (Test-ArtifactFresh -Artifact $a -Stamp (Join-Path $tmp 'nope.txt'))) {
            Write-Error 'SELFTEST A1 an unarmed run was accepted'; exit 1
        }
        # A2 an artifact older than the stamp is a stale receipt from an earlier run.
        'stamp' | Set-Content -LiteralPath $s
        (Get-Item -LiteralPath $a).LastWriteTimeUtc = (Get-Item -LiteralPath $s).LastWriteTimeUtc.AddSeconds(-30)
        if ($null -eq (Test-ArtifactFresh -Artifact $a -Stamp $s)) {
            Write-Error 'SELFTEST A2 a stale artifact was accepted as this run''s output'; exit 1
        }
        # A3 a deleted artifact is not silently treated as clean.
        Remove-Item -LiteralPath $a -Force
        if ($null -eq (Test-ArtifactFresh -Artifact $a -Stamp $s)) {
            Write-Error 'SELFTEST A3 a missing artifact was accepted'; exit 1
        }
        # A4 positive control: an artifact written after arming passes, so the gate is not
        # merely refusing everything.
        'x' | Set-Content -LiteralPath $a
        (Get-Item -LiteralPath $a).LastWriteTimeUtc = (Get-Item -LiteralPath $s).LastWriteTimeUtc.AddSeconds(5)
        $ok = Test-ArtifactFresh -Artifact $a -Stamp $s
        if ($null -ne $ok) { Write-Error ('SELFTEST A4 a fresh artifact was rejected: ' + $ok); exit 1 }
        'PASS: RUN_ARM self-test (A1 unarmed, A2 stale, A3 missing, A4 fresh)'
        exit 0
    } finally { Remove-Item -LiteralPath $tmp -Recurse -Force -ErrorAction SilentlyContinue }
}

foreach ($p in @($artifact, $stamp)) {
    $dir = Split-Path -Parent $p
    if ($dir -and -not (Test-Path -LiteralPath $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
}
if (Test-Path -LiteralPath $artifact) { Remove-Item -LiteralPath $artifact -Force }
('ARMED=' + $Name + ' AT=' + (Get-Date).ToUniversalTime().ToString('o')) | Set-Content -LiteralPath $stamp -Encoding utf8
'PASS: RUN_ARM ' + $Name + ' (cleared ' + $artifact + ', stamped ' + $stamp + ')'
exit 0
