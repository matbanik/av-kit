$ErrorActionPreference = 'Continue'
$ProgressPreference = 'SilentlyContinue'
# Read-only probe of the second E2E host (Session 96 plan, rows 0, 5 and 6).
# host-probe-run.py sends one first line that sets $root, $busyUsers, $ffbin, $taskPath and
# $taskName from the local config, so no host detail is written in this tracked file.
# It reads process, task, session and file facts only. It starts, stops, installs,
# registers and writes nothing, and it reads nothing under the users folder.
$all = @(Get-Process -IncludeUserName -ErrorAction SilentlyContinue)
$named = @($all | Where-Object { $_.UserName })
'processes=' + $all.Count + ' with_username=' + $named.Count
'users=' + ((($named | Select-Object -ExpandProperty UserName -Unique) | ForEach-Object { ($_ -split '\\')[-1] }) -join ',')
$bu = @($busyUsers -split ',' | Where-Object { $_ })
$busy = @($named | Where-Object { $bu -contains (($_.UserName -split '\\')[-1]) -and $_.ProcessName -match '^(node|electron|python|pytest|vitest)$' })
'busy_user_test_processes=' + $busy.Count + ' names=' + (($busy | Select-Object -ExpandProperty ProcessName -Unique) -join ',')
'busy_users_missing=' + (($bu | Where-Object { -not (Get-LocalUser -Name $_ -ErrorAction SilentlyContinue) }) -join ',')
'runner_processes=' + @(Get-Process -Name 'Runner.Listener', 'Runner.Worker' -ErrorAction SilentlyContinue).Count
$id = [Security.Principal.WindowsIdentity]::GetCurrent()
$pr = New-Object Security.Principal.WindowsPrincipal($id)
'ssh_elevated=' + $pr.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator) + ' ssh_session=' + (Get-Process -Id $PID).SessionId
$ex = @(Get-CimInstance Win32_Process -Filter "Name='explorer.exe'" -ErrorAction SilentlyContinue)
'explorer=' + (($ex | ForEach-Object { $o = Invoke-CimMethod -InputObject $_ -MethodName GetOwner; [string]$_.SessionId + ':' + $o.User }) -join ',')
'logonui=' + ((Get-Process LogonUI -ErrorAction SilentlyContinue | Select-Object -ExpandProperty SessionId) -join ',')
$t = Get-ScheduledTask -TaskPath $taskPath -TaskName $taskName -ErrorAction SilentlyContinue
'task=' + [bool]$t + ' state=' + $t.State + ' user=' + $t.Principal.UserId + ' logon=' + $t.Principal.LogonType + ' runlevel=' + $t.Principal.RunLevel
'task_action=' + $t.Actions[0].Execute + ' ' + $t.Actions[0].Arguments
'task_limit=' + $t.Settings.ExecutionTimeLimit + ' multiple=' + $t.Settings.MultipleInstances
'lock=' + (Test-Path "$root\avkit-remote.lock") + ' tree_marker=' + [bool](Get-ChildItem "$root\runs\*\tree\.avkit-remote-tree" -Force -ErrorAction SilentlyContinue) + ' bin=' + (Test-Path "$root\bin")
'runs=' + (Test-Path "$root\runs") + ' results_r=' + @(Get-ChildItem "$root\results" -Directory -Filter 'r*' -ErrorAction SilentlyContinue).Count + ' hand_copies=' + @(Get-ChildItem "$root\run-e2e.hand-*.ps1" -ErrorAction SilentlyContinue).Count
$l = Get-Item "$root\run-e2e.ps1" -ErrorAction SilentlyContinue
'launcher=' + [bool]$l + ' sha256=' + (Get-FileHash "$root\run-e2e.ps1" -Algorithm SHA256 -ErrorAction SilentlyContinue).Hash + ' tracked_marker=' + [bool](Select-String -Path "$root\run-e2e.ps1" -Pattern '^# avkit-remote-launcher' -Quiet -ErrorAction SilentlyContinue)
'node=' + (Test-Path 'C:\Program Files\nodejs\node.exe') + ' ver=' + $(if (Test-Path 'C:\Program Files\nodejs\node.exe') { & 'C:\Program Files\nodejs\node.exe' -v })
'uv=' + [bool](Get-Command uv -ErrorAction SilentlyContinue) + ' git=' + [bool](Get-Command git -ErrorAction SilentlyContinue)
'vcruntime140_1=' + (Test-Path 'C:\Windows\System32\vcruntime140_1.dll') + ' msvcp140=' + (Test-Path 'C:\Windows\System32\msvcp140.dll')
'ffmpeg=' + (Test-Path "$ffbin\ffmpeg.exe") + ' ffprobe=' + (Test-Path "$ffbin\ffprobe.exe")
'dotnet=' + [bool](Get-Command dotnet -ErrorAction SilentlyContinue)
'psver=' + $PSVersionTable.PSVersion + ' tz=' + (Get-TimeZone).Id + ' utc_offset_h=' + (Get-TimeZone).GetUtcOffset((Get-Date)).TotalHours + ' now=' + (Get-Date -Format o)
'free_gb=' + [math]::Round((Get-PSDrive C).Free / 1GB, 1)
'sessions=' + ((quser 2>$null | Select-Object -Skip 1 | ForEach-Object { ($_.Trim() -replace '\s{2,}', '|') }) -join ';')
'ssh_shell=' + (Get-ItemProperty 'HKLM:\SOFTWARE\OpenSSH' -Name DefaultShell -ErrorAction SilentlyContinue).DefaultShell
'cpu_load=' + (Get-CimInstance Win32_Processor | Measure-Object -Property LoadPercentage -Average).Average
