@echo off
echo Initializing Git repository...
git init
git add .
git commit -m "Initial commit: Solar Calculator App"
git branch -M main
echo Adding remote origin...
git remote add origin https://github.com/Ali-2003-ux/Solar-Calculator-Babil.git
echo Pushing to GitHub...
git push -u origin main
pause
