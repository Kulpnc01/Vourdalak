@echo off
setlocal
set PROJECT_ROOT=%~dp0
cd /d "%PROJECT_ROOT%"

:: Check if virtual environment exists
if exist "vourdalak_env\Scripts\python.exe" (
    set PYTHON_EXE="%PROJECT_ROOT%vourdalak_env\Scripts\python.exe"
) else (
    set PYTHON_EXE=python
)

if "%~1"=="" (
    echo [*] Starting Vourdalak Panopticon...
    %PYTHON_EXE% vourdalak.py
) else (
    echo [*] Starting Okhotnik Hunt for: %*
    %PYTHON_EXE% 01_Hunt\Okhotnik\okhotnik_core.py %*
)
pause
