@echo off
cd /d "%~dp0"
echo Updating project...
git add .
git commit -m "Update: Added Battery Selection Features"
git push origin main
echo.
echo Process Completed!
pause
