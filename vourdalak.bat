@echo off
SETLOCAL EnableDelayedExpansion
set PROJECT_ROOT=%~dp0
set VENV_DIR=%PROJECT_ROOT%vourdalak_v3_env

echo ==================================================
echo   VOURDALAK V3: RECURSIVE INTELLIGENCE ENGINE
echo ==================================================

if not exist "%VENV_DIR%" (
    echo [!] Sandbox missing. Running Installation...
    call "%PROJECT_ROOT%install.bat"
)

:: Auto-sync dependencies on every launch
call "%VENV_DIR%\Scripts\activate.bat"
echo [*] Checking Environment Integrity...
python -m pip install -r "%PROJECT_ROOT%requirements.txt" --quiet

echo [*] Launching Master Interface...
python "%PROJECT_ROOT%interface\cli.py" %*

deactivate
