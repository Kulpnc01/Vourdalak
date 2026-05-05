$ProjectRoot = Get-Location
$VenvDir = Join-Path $ProjectRoot "vourdalak_v3_env"

if ($args -contains "--install") {
    Write-Host "==================================================" -ForegroundColor Cyan
    Write-Host "   VOURDALAK V3: SYSTEM INSTALLATION SEQUENCE     " -ForegroundColor Cyan
    Write-Host "==================================================" -ForegroundColor Cyan
    & (Join-Path $ProjectRoot "install.ps1")
    exit
}

if (-not (Test-Path $VenvDir)) {
    Write-Host "[!] Sandbox missing. Run 'v3 --install' first." -ForegroundColor Red
    exit
}

# Quick Environment Check
& "$VenvDir\Scripts\Activate.ps1"

if ($args.Count -eq 0) {
    Write-Host "[*] Launching Vourdalak V3 GUI..." -ForegroundColor Green
    python (Join-Path $ProjectRoot "interface\cli.py") --gui
} else {
    python (Join-Path $ProjectRoot "interface\cli.py") $args
}
