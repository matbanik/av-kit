$ErrorActionPreference = 'Continue'
$ProgressPreference = 'SilentlyContinue'
# host-release.ps1 -RunId: removes the lock only when it names this run.
$Allowed = @('runid')
# Staged by tools/e2e_remote.py into <root>\bin\<set>\ beside host.json. Prints one JSON object
# on its last stdout line; exit 0 is ok, 1 a refusal with its reason, 2 usage. It never stops a
# process and never changes the scheduled task.

$RunIdPattern = '^r[0-9]{8}T[0-9]{6}Z-[0-9a-f]{7}$'
$CommitPattern = '^[0-9a-f]{40}$'

function AvOut($o, [int]$code) {
    ConvertTo-Json -InputObject $o -Depth 8 -Compress
    exit $code
}

function AvRefuse([string]$reason, [string]$detail, [int]$code) {
    AvOut ([ordered]@{ reason = $reason; detail = $detail }) $code
}

$avArgs = @{}
$i = 0
while ($i -lt $args.Count) {
    $name = [string]$args[$i]
    if (-not $name.StartsWith('-') -or ($i + 1) -ge $args.Count) {
        AvRefuse 'usage' ('unexpected argument ' + $name) 2
    }
    $avArgs[$name.Substring(1).ToLower()] = [string]$args[$i + 1]
    $i += 2
}
foreach ($k in @($avArgs.Keys)) {
    if ($Allowed -notcontains $k) { AvRefuse 'usage' ('unknown parameter -' + $k) 2 }
}

function AvArg([string]$name, [string]$pattern) {
    $v = [string]$avArgs[$name.ToLower()]
    if (-not ($v -cmatch $pattern)) { AvRefuse 'usage' ('-' + $name + ' must match ' + $pattern) 2 }
    return $v
}

function AvHostJson {
    $h = $null
    try {
        $h = Get-Content -LiteralPath (Join-Path $PSScriptRoot 'host.json') -Raw -ErrorAction Stop | ConvertFrom-Json
    } catch {
        $h = $null
    }
    if (-not $h -or -not $h.root) { AvRefuse 'prerequisite-missing' 'host.json beside the script is missing or unreadable' 1 }
    return $h
}

function AvHash([string]$path) {
    # .NET rather than the hash cmdlet, so a module path inherited from PowerShell 7 cannot matter.
    $sha = [Security.Cryptography.SHA256]::Create()
    $fs = [IO.File]::OpenRead($path)
    try { $h = $sha.ComputeHash($fs) } finally { $fs.Close(); $sha.Dispose() }
    return ([BitConverter]::ToString($h)).Replace('-', '').ToLower()
}

function AvReadLock([string]$path) {
    if (-not (Test-Path -LiteralPath $path)) { return $null }
    $l = $null
    try { $l = Get-Content -LiteralPath $path -Raw -ErrorAction Stop | ConvertFrom-Json } catch { $l = $null }
    if (-not $l) { return [ordered]@{ run_id = 'unreadable'; commit = ''; set = ''; created_utc = '' } }
    return $l
}

$runId = AvArg 'RunId' $RunIdPattern
$hj = AvHostJson
$lockPath = Join-Path ([string]$hj.root) 'avkit-remote.lock'
$lock = AvReadLock $lockPath
if (-not $lock) { AvOut ([ordered]@{ reason = 'ok'; released = 'none' }) 0 }
$holder = [string]$lock.run_id
if ($holder -cne $runId) { AvRefuse 'lock-mismatch' ('holder=' + $holder) 1 }
Remove-Item -LiteralPath $lockPath -Force
if (Test-Path -LiteralPath $lockPath) { AvRefuse 'lock-mismatch' ('the lock of ' + $runId + ' could not be removed') 1 }
AvOut ([ordered]@{ reason = 'ok'; released = $runId }) 0
