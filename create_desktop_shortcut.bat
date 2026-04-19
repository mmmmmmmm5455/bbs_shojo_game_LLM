@echo off
setlocal
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File ".\create_desktop_shortcut.ps1"
if errorlevel 1 (
  echo Failed to create desktop shortcut.
  pause
  exit /b 1
)
echo Done.
pause
endlocal
