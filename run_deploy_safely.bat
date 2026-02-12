@echo off
cd /d "%~dp0"
echo Moving to the correct directory...
echo Current Directory: %CD%
echo.
echo Running deploy.bat...
call deploy.bat
pause
