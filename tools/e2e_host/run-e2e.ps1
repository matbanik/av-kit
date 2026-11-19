$ErrorActionPreference = 'Continue'
$ProgressPreference = 'SilentlyContinue'
# avkit-remote-launcher
# run-e2e.ps1: the scheduled task's action, run in the signed-in session with no arguments. It
# runs the locked run's suite from runs\<id>\tree\ui and writes only under results\<id>\; DONE is
# written last, through DONE.tmp, so a poll never reads a partial one.

$RunIdPattern = '^r[0-9]{8}T[0-9]{6}Z-[0-9a-f]{7}$'
$root = $PSScriptRoot
$results = Join-Path $root 'results'
$stamp = [DateTime]::UtcNow.ToString('yyyyMMddTHHmmssZ')

function AvDone([string]$dir, [int]$code, [string]$note) {
    New-Item -ItemType Directory -Force -Path $dir | Out-Null
    if ($note) { Add-Content -LiteralPath (Join-Path $dir 'meta.txt') -Value $note -Encoding ASCII }
    Set-Content -LiteralPath (Join-Path $dir 'DONE.tmp') -Value $code -Encoding ASCII
    Move-Item -LiteralPath (Join-Path $dir 'DONE.tmp') -Destination (Join-Path $dir 'DONE') -Force
    ConvertTo-Json -InputObject ([ordered]@{ reason = 'finished'; exit = $code; note = $note }) -Depth 8 -Compress
    exit $code
}

function AvStale([string]$tree, [string]$commit) {
    # global-setup.ts:40-56 on this tree, plus both markers naming the commit.
    foreach ($m in @('.avkit-remote-tree', '.avkit-remote-build')) {
        $mp = Join-Path $tree $m
        if (-not (Test-Path -LiteralPath $mp)) { return ($m + ' is missing') }
        if (([string](Get-Content -LiteralPath $mp -Raw)).Trim() -cne $commit) { return ($m + ' does not name ' + $commit) }
    }
    $ui = Join-Path $tree 'ui'
    $main = Join-Path $ui 'out\main\index.js'
    $config = Join-Path $ui 'electron.vite.config.ts'
    $html = Join-Path $ui 'out-e2e\renderer\primitive-harness.html'
    $entry = Join-Path $ui 'src\renderer\src\primitive-harness.tsx'
    foreach ($f in @($main, $config, $html, $entry)) {
        if (-not (Test-Path -LiteralPath $f -PathType Leaf)) { return ($f + ' is missing') }
    }
    $built = (Get-Item -LiteralPath $main).LastWriteTimeUtc
    $cfg = (Get-Item -LiteralPath $config).LastWriteTimeUtc
    $newest = $null
    foreach ($f in @(Get-ChildItem -LiteralPath (Join-Path $ui 'src') -Recurse -File -Force)) {
        if ($null -eq $newest -or $f.LastWriteTimeUtc -gt $newest.LastWriteTimeUtc) { $newest = $f }
    }
    if ($newest -and $newest.LastWriteTimeUtc -gt $built) { return ('ui\out\main\index.js is older than ' + $newest.FullName) }
    if ($cfg -gt $built) { return 'ui\out\main\index.js is older than electron.vite.config.ts' }
    $htmlT = (Get-Item -LiteralPath $html).LastWriteTimeUtc
    if ((Get-Item -LiteralPath $entry).LastWriteTimeUtc -gt $htmlT -or $cfg -gt $htmlT) {
        return 'ui\out-e2e\renderer\primitive-harness.html is older than its entry or the config'
    }
    return ''
}

$lock = $null
$lockPath = Join-Path $root 'avkit-remote.lock'
if (Test-Path -LiteralPath $lockPath) {
    try { $lock = Get-Content -LiteralPath $lockPath -Raw -ErrorAction Stop | ConvertFrom-Json } catch { $lock = $null }
}
$runId = ''
if ($lock) { $runId = [string]$lock.run_id }
if (-not ($runId -cmatch $RunIdPattern)) {
    AvDone (Join-Path $results ('no-lock-' + $stamp)) 95 'refused: no lock names a run'
}
$commit = [string]$lock.commit
$res = Join-Path $results $runId
if (Test-Path -LiteralPath $res) {
    AvDone (Join-Path $results ('dup-' + $stamp)) 95 ('refused: results\' + $runId + ' already exists')
}
New-Item -ItemType Directory -Force -Path $res | Out-Null
$sid = (Get-Process -Id $PID).SessionId
$meta = Join-Path $res 'meta.txt'
$who = $env:USERDOMAIN + '\' + $env:USERNAME
$lines = @(('run_id=' + $runId), ('commit=' + $commit), ('user=' + $who), ('session=' + $sid), ('start=' + [DateTime]::UtcNow.ToString('o')))
Set-Content -LiteralPath $meta -Value $lines -Encoding ASCII

$rd = Join-Path $root ('runs\' + $runId)
$reqPath = Join-Path $rd 'request.json'
if (-not (Test-Path -LiteralPath $reqPath -PathType Leaf)) { AvDone $res 95 'refused: request-missing' }
$req = $null
try { $req = Get-Content -LiteralPath $reqPath -Raw -ErrorAction Stop | ConvertFrom-Json } catch { $req = $null }
if (-not $req) { AvDone $res 95 'refused: request-missing (unreadable)' }
if ([string]$req.commit -cne $commit) { AvDone $res 98 'refused: commit-mismatch (the request is another commit)' }
$tree = Join-Path $rd 'tree'
$tm = Join-Path $tree '.avkit-remote-tree'
if (-not (Test-Path -LiteralPath $tm) -or ([string](Get-Content -LiteralPath $tm -Raw)).Trim() -cne $commit) {
    AvDone $res 98 'refused: commit-mismatch (the tree is not this commit)'
}
$why = AvStale $tree $commit
if ($why) { AvDone $res 99 ('refused: build-stale: ' + $why) }
if ($sid -eq 0) { AvDone $res 96 'refused: no-desktop-session (session 0)' }
$state = ''
if (Get-Command quser.exe -ErrorAction SilentlyContinue) {
    foreach ($ln in @(quser.exe 2>$null)) {
        if ([string]$ln -match '^\s*>?(\S+)\s+(?:(\S+)\s+)?(\d+)\s+(\S+)') {
            if ([int]$Matches[3] -eq $sid) { $state = $Matches[4] }
        }
    }
}
if ($state -ne 'Active') { AvDone $res 96 ('refused: no-desktop-session (session ' + $sid + ' is ' + $state + ')') }
if (@(Get-Process -Name LogonUI -ErrorAction SilentlyContinue | Where-Object { $_.SessionId -eq $sid }).Count -gt 0) {
    AvDone $res 97 'refused: desktop-locked'
}

Remove-Item Env:ELECTRON_RUN_AS_NODE -ErrorAction SilentlyContinue
$nodeExe = [string]$req.node_exe
$env:Path = (Split-Path -Parent $nodeExe) + ';' + [string]$req.ffmpeg_bin + ';' + $env:Path
$diag = Join-Path $res 'diag'
New-Item -ItemType Directory -Force -Path $diag | Out-Null
$env:AVKIT_E2E_DIAG_DIR = $diag
$ui = Join-Path $tree 'ui'
$skip = @(@($req.skip) | Where-Object { $_ } | ForEach-Object { [string]$_ })
$specs = @(Get-ChildItem -LiteralPath (Join-Path $ui 'tests\e2e') -File | Where-Object { ($_.Name -like '*.test.ts' -or $_.Name -like '*.spec.ts') -and ($skip -notcontains $_.Name) } | ForEach-Object { $_.Name } | Sort-Object)
Set-Content -LiteralPath (Join-Path $res 'specs.txt') -Value $specs -Encoding ASCII
Add-Content -LiteralPath $meta -Value ('specs=' + $specs.Count + ' skip=' + ($skip -join ',')) -Encoding ASCII
$argv = @('scripts\playwright-with-outputfile.mjs') + $specs + @('--reporter=json', ('--outputFile=' + (Join-Path $res 'report.json')))
$p = Start-Process -FilePath $nodeExe -ArgumentList $argv -WorkingDirectory $ui -RedirectStandardOutput (Join-Path $res 'run.log') -RedirectStandardError (Join-Path $res 'run.err') -NoNewWindow -PassThru
$null = $p.Handle
Set-Content -LiteralPath (Join-Path $res 'pid.txt') -Value @([string]$p.Id, $p.StartTime.ToUniversalTime().ToString('o')) -Encoding ASCII
$p.WaitForExit()
$code = $p.ExitCode
Add-Content -LiteralPath $meta -Value ('exit=' + $code + ' end=' + [DateTime]::UtcNow.ToString('o')) -Encoding ASCII
AvDone $res $code ''
