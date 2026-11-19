# Session 95 (eval-describe-raw-bytes) row 1: reproduce both old describe redirects (AC-8, D-1206).
#
# Run it as its own process so the driver's console settings play no part:
#   pwsh -NoProfile -File docs/execution/plans/2026-11-18-eval-describe-raw-bytes/edr-old.ps1
#
# It records the shell first (edr-old-env.txt), then runs, in this same process, from mcp-server:
#   E-1 form   (Session 64 row E-1): rtk proxy npx tsx HARNESS ROOT describe *> edr-old-e1.txt
#   step-3 form (eval-run.md:24, as Session 92 row 5 ran it): npx tsx ... > edr-old-step3.txt 2>&1
# It never overwrites a receipt or reuses a root (exit 2). Exit 0 when both children exit 0, else
# 1. Whether each receipt holds mojibake is edr-check.py old's call, not this script's.

$ErrorActionPreference = 'Continue'
$D = 'C:/Temp/av-kit/eval-describe-raw-bytes'
$Base = 'C:/Temp/av-kit/s64/eval'
$Harness = '../docs/execution/plans/2026-11-11-capture-export-copy/eval-harness.ts'
$EnvFile = "$D/edr-old-env.txt"
$E1 = "$D/edr-old-e1.txt"
$Step3 = "$D/edr-old-step3.txt"

foreach ($p in @($EnvFile, $E1, $Step3, "$Base/s95-old", "$Base/s95-old3")) {
    if (Test-Path -LiteralPath $p) {
        Write-Output "usage: $p exists; a receipt or root is never reused"
        exit 2
    }
}
Remove-Item Env:ELECTRON_RUN_AS_NODE -ErrorAction SilentlyContinue

$lines = @(
    "psversion $($PSVersionTable.PSVersion.ToString())",
    "psedition $($PSVersionTable.PSEdition)",
    "console-output-codepage $([Console]::OutputEncoding.CodePage)",
    "output-encoding $($OutputEncoding.WebName)"
)
[IO.File]::WriteAllText($EnvFile, (($lines -join "`n") + "`n"), [Text.UTF8Encoding]::new($false))

Push-Location 'P:\av-kit\mcp-server'
try {
    rtk proxy npx tsx $Harness "$Base/s95-old/root" describe *> $E1
    $e1Exit = $LASTEXITCODE
    npx tsx $Harness "$Base/s95-old3/root" describe > $Step3 2>&1
    $step3Exit = $LASTEXITCODE
}
finally {
    Pop-Location
}

$tail = "e1-exit $e1Exit`nstep3-exit $step3Exit`n"
[IO.File]::AppendAllText($EnvFile, $tail, [Text.UTF8Encoding]::new($false))
Get-Content -LiteralPath $EnvFile
if ($e1Exit -ne 0 -or $step3Exit -ne 0) {
    Write-Output 'edr-old: a harness run exited non-zero; see the receipts'
    exit 1
}
Write-Output 'edr-old: both forms ran'
exit 0
