@echo off
SETLOCAL EnableDelayedExpansion
set PROJECT_ROOT=%~dp0
set VENV_DIR=%PROJECT_ROOT%vourdalak_v3_env

echo ==================================================
echo   VOURDALAK V3: SANDBOX INSTALLATION SEQUENCE
echo ==================================================

if not exist "%VENV_DIR%" (
    echo [*] Creating new virtual environment bubble...
    python -m venv "%VENV_DIR%"
) else (
    echo [*] Existing environment detected.
)

echo [*] Activating Sandbox and Syncing Dependencies...
call "%VENV_DIR%\Scripts\activate.bat"
python -m pip install --upgrade pip setuptools wheel --quiet
python -m pip install -r "%PROJECT_ROOT%requirements.txt" --quiet

echo [SUCCESS] Vourdalak V3 Environment is Primed.
pause
