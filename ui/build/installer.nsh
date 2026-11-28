!macro customCheckAppRunning
  ; APP_RUNNING_CHECK (MEU-174, D-1554): this replaces the stock running-app check in the installer
  ; and the uninstaller. It stops only the processes whose executable is inside this install folder
  ; (the stock check also matches a sibling folder that starts with the same name). find exits 0
  ; when none runs and 1 when one does; stop exits 0 when none is left after 10 s and 3 when one is;
  ; any exception exits 2. Every non-zero result refuses before any file changes.
  Push $9
  System::Call 'kernel32::GetCurrentProcessId() i .r9'
  nsExec::ExecToLog `"$SYSDIR\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -NonInteractive -ExecutionPolicy Bypass -Command "$$m = 'find'; try { $$d = [IO.Path]::GetFullPath('$INSTDIR').TrimEnd('\') + '\'; $$s = { @(Get-CimInstance -ClassName Win32_Process | Where-Object { $$_.ExecutablePath -and $$_.ExecutablePath.StartsWith($$d, [StringComparison]::OrdinalIgnoreCase) -and $$_.ProcessId -ne $9 }) }; $$p = @(& $$s); if ($$m -eq 'find') { if ($$p.Count) { exit 1 }; exit 0 }; foreach ($$x in $$p) { Stop-Process -Id $$x.ProcessId -Force -ErrorAction SilentlyContinue }; $$t = [DateTime]::UtcNow.AddSeconds(10); while (@(& $$s).Count -and [DateTime]::UtcNow -lt $$t) { Start-Sleep -Milliseconds 250 }; if (@(& $$s).Count) { exit 3 }; exit 0 } catch { exit 2 }"`
  Pop $R0
  ${if} $R0 == 1
    ${ifNot} ${isUpdated}
      MessageBox MB_OKCANCEL|MB_ICONEXCLAMATION "$(appRunning)" /SD IDOK IDOK +2
      Quit
    ${endIf}
    nsExec::ExecToLog `"$SYSDIR\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -NonInteractive -ExecutionPolicy Bypass -Command "$$m = 'stop'; try { $$d = [IO.Path]::GetFullPath('$INSTDIR').TrimEnd('\') + '\'; $$s = { @(Get-CimInstance -ClassName Win32_Process | Where-Object { $$_.ExecutablePath -and $$_.ExecutablePath.StartsWith($$d, [StringComparison]::OrdinalIgnoreCase) -and $$_.ProcessId -ne $9 }) }; $$p = @(& $$s); if ($$m -eq 'find') { if ($$p.Count) { exit 1 }; exit 0 }; foreach ($$x in $$p) { Stop-Process -Id $$x.ProcessId -Force -ErrorAction SilentlyContinue }; $$t = [DateTime]::UtcNow.AddSeconds(10); while (@(& $$s).Count -and [DateTime]::UtcNow -lt $$t) { Start-Sleep -Milliseconds 250 }; if (@(& $$s).Count) { exit 3 }; exit 0 } catch { exit 2 }"`
    Pop $R0
  ${endIf}
  ; nsExec pushes "error" when PowerShell cannot start; LogicLib's != compares integers and would
  ; read that as 0, so any result that is not a number becomes 2 first.
  Push $R1
  IntOp $R1 $R0 + 0
  ${if} $R1 S!= $R0
    StrCpy $R0 2
  ${endIf}
  Pop $R1
  ${if} $R0 != 0
    MessageBox MB_OK|MB_ICONEXCLAMATION "$(appCannotBeClosed)" /SD IDOK
    SetErrorLevel 2
    Quit
  ${endIf}
  Pop $9
!macroend

!macro customUnInstall
  ; An update runs this macro too: the sign-in entry and the updater cache stay unless it is a
  ; real uninstall (UNINSTALL_CACHE_RECURSIVE, MEU-174).
  ${ifNot} ${isUpdated}
    DeleteRegValue HKCU "Software\Microsoft\Windows\CurrentVersion\Run" "com.avkit.app"
    DeleteRegValue HKCU "Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run" "com.avkit.app"
    ${if} $installMode == "all"
      SetShellVarContext current
    ${endif}
    Delete "$LOCALAPPDATA\${APP_INSTALLER_STORE_FILE}"
    RMDir /r "$LOCALAPPDATA\av-kit-ui-updater"
    ${if} $installMode == "all"
      SetShellVarContext all
    ${endif}
  ${endIf}
!macroend
