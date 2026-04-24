@echo off
TITLE Vourdalak OSINT Orchestrator
SET VENV_PATH=%~dp0vourdalak_env\Scripts\python.exe

IF NOT EXIST "%VENV_PATH%" (
    echo [!] ERROR: Virtual environment not found at %VENV_PATH%
    echo [!] Please run 01_Hunt\hunt_deploy.py first.
    pause
    exit /b 1
)

echo [*] Starting Vourdalak GUI...
"%VENV_PATH%" "%~dp0vourdalak_gui.py"
pause
