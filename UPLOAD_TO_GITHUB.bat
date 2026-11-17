@echo off
setlocal
where git >nul 2>nul || (echo Install Git for Windows first.& pause & exit /b 1)
echo This uploads this folder to YOUR own empty GitHub repository.
set /p REPO=Paste your repository HTTPS URL: 
if "%REPO%"=="" exit /b 1
git init
git add .
git commit -m "Add Cloud Student Task Manager project"
git branch -M main
git remote add origin %REPO%
git push -u origin main
if errorlevel 1 echo Upload failed. Check repository URL and GitHub sign-in.
pause
