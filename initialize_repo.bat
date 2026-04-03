@echo off
SET REPO_URL=https://github.com/Kulpnc01/Vourdalak.git
echo ==================================================
echo   VOURDALAK 2.0: GIT INITIALIZATION TOOL
echo ==================================================
echo.

:: Initialize Repository
echo [*] Initializing Git...
git init

:: Link to Remote
echo [*] Linking to GitHub: %REPO_URL%
git remote add origin %REPO_URL%

:: Stage Files
echo [*] Staging finalized logic and documentation...
git add .

:: Commit
echo [*] Performing initial commit...
git commit -m "chore: initial release of Vourdalak v3.3 - Integrated Behavioral Engine"

:: Change branch to main
echo [*] Setting branch to main...
git branch -M main

echo.
echo ==================================================
echo   SUCCESS: REPOSITORY INITIALIZED LOCALLY
echo ==================================================
echo.
echo To complete the backup, run: 
echo   git push -u origin main
echo.
pause
