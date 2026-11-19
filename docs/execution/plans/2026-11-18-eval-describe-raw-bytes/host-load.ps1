# Session 92 host-load wait (task row 0; implementation-plan.md §Session gate "Host load"). The
# shape of 2026-11-17-tts-fp16-guard-ship/host-load.ps1 with this plan's limit: it takes five
# Win32_Processor.LoadPercentage samples, 2 s apart (each sample is the mean over the
# processors), and averages them. While the mean is above 50 % it waits, taking a new
# five-sample mean every 30 s, for up to 10 minutes. It prints every mean, and its last line is
# `host-load: <n> %`. Exit 0 when the load is at or below 50 %; exit 1 when it is still above
# 50 % after 10 minutes. Rows 0, 1, 3, 6 and 7 and the gate's host-load step call it.
$ErrorActionPreference = 'Stop'
$bar = 50
$limitSeconds = 10 * 60

function Get-LoadMean {
    $samples = @()
    for ($i = 0; $i -lt 5; $i++) {
        if ($i -gt 0) { Start-Sleep -Seconds 2 }
        $avg = (Get-CimInstance Win32_Processor | Measure-Object -Property LoadPercentage -Average).Average
        $samples += [math]::Round([double]$avg, 1)
    }
    $mean = [math]::Round((($samples | Measure-Object -Average).Average), 1)
    Write-Output ("host-load samples: [{0}] mean={1}" -f ($samples -join ', '), $mean)
    return $mean
}

$clock = [System.Diagnostics.Stopwatch]::StartNew()
$out = Get-LoadMean
$load = $out[-1]
$out | Select-Object -SkipLast 1
while ($load -gt $bar) {
    if ($clock.Elapsed.TotalSeconds -ge $limitSeconds) {
        Write-Output ("host-load: still above the {0} % bar after {1} s" -f $bar, [int]$clock.Elapsed.TotalSeconds)
        Write-Output ("host-load: {0} %" -f $load)
        exit 1
    }
    Write-Output ("host-load {0} % is above {1} %; waiting 30 s ({2} s so far)" -f $load, $bar, [int]$clock.Elapsed.TotalSeconds)
    Start-Sleep -Seconds 30
    $out = Get-LoadMean
    $load = $out[-1]
    $out | Select-Object -SkipLast 1
}
Write-Output ("host-load: waited {0} s (bar {1} %)" -f [int]$clock.Elapsed.TotalSeconds, $bar)
Write-Output ("host-load: {0} %" -f $load)
exit 0
