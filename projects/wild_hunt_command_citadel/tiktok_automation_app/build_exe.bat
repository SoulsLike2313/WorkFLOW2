@echo off
cd /d %~dp0
powershell -ExecutionPolicy Bypass -File ".\build_exe.ps1" -Clean
pause
