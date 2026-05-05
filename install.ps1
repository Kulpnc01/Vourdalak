$ProjectRoot = Get-Location
$VenvDir = Join-Path $ProjectRoot "vourdalak_v3_env"

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "   VOURDALAK V3: POWERSHELL ARM64 INSTALLER       " -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan

if (-not (Test-Path $VenvDir)) {
    Write-Host "[*] Creating native virtual environment bubble..."
    python -m venv $VenvDir
} else {
    Write-Host "[*] Existing environment detected."
}

Write-Host "[*] Activating Sandbox and Syncing Dependencies..."
& "$VenvDir\Scripts\Activate.ps1"

python -m pip install --upgrade pip setuptools wheel --quiet
Write-Host "[*] Installing modular toolchain from source..." -ForegroundColor Cyan
python -m pip install --upgrade -r (Join-Path $ProjectRoot "requirements.txt") --quiet

Write-Host "[SUCCESS] Vourdalak V3 Sandbox is Primed for ARM64." -ForegroundColor Green
Read-Host "Press Enter to exit"
