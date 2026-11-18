# Session 74 host-load wait (implementation-plan.md §Verification Plan 1.4 and §Session gate;
# Session 81 RULE-2 with this session's 50 % bar; S15). Samples Win32_Processor.LoadPercentage
# five times, 2 s apart (each sample is the mean over the processors). While the mean is above
# 50 % it waits, taking a new five-sample mean every 30 s, for up to 20 minutes. It prints every
# mean and the value it ran at. Exit 0 when the load is at or below 50 %; exit 1 (S15) when it
# is still above 50 % after 20 minutes. Rows 0, 3, 7 and 8 and the gate's host-load step call it.
$ErrorActionPreference = 'Stop'
$bar = 50
$limitSeconds = 20 * 60

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
        Write-Output ("host-load: S15: still {0} % after {1} s, above the {2} % bar" -f $load, [int]$clock.Elapsed.TotalSeconds, $bar)
        exit 1
    }
    Write-Output ("host-load {0} % is above {1} %; waiting 30 s ({2} s so far)" -f $load, $bar, [int]$clock.Elapsed.TotalSeconds)
    Start-Sleep -Seconds 30
    $out = Get-LoadMean
    $load = $out[-1]
    $out | Select-Object -SkipLast 1
}
Write-Output ("host-load: ran at {0} % (bar {1} %, waited {2} s)" -f $load, $bar, [int]$clock.Elapsed.TotalSeconds)
exit 0
