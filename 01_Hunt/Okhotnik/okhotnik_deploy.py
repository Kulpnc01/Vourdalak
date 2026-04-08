import os
import sys
import subprocess
import platform
from pathlib import Path

def deploy_okhotnik():
    print("--- OKHOTNIK: DEPLOYMENT (ARM64 OPTIMIZED) ---")
    script_dir = Path(__file__).parent
    req_file = script_dir / "requirements.txt"
    
    # Core libraries required by standard OSINT toolchains
    # Using specific versions known for stability or latest
    core_reqs = [
        "requests", "instaloader", "holehe", "pandas", 
        "beautifulsoup4", "aiohttp", "colorama", "lxml",
        "duckduckgo-search"
    ,
        "h8mail", "ghunt"
    ]
    
    with open(req_file, "w") as f:
        f.write("\n".join(core_reqs))
    
    print(f"[*] Target Architecture: {platform.machine()}")
    print("[*] Installing/Upgrading dependencies...")
    
    try:
        # --prefer-binary: Critical for ARM64 to avoid failing on C++ builds if a wheel exists
        # --upgrade: Ensures we pull the latest versions
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "--upgrade", "--prefer-binary", "-r", str(req_file)
        ])
        print("[SUCCESS] Okhotnik environment is primed and latest.")
    except subprocess.CalledProcessError as e:
        print(f"\n[!] INSTALLATION WARNING: Code {e.returncode}")
        if platform.machine().lower() in ['arm64', 'aarch64']:
            print("  > ARM64 Detected. If 'aiohttp' or 'lxml' failed, ensure 'Visual C++ Build Tools' (Desktop development with C++) is installed.")
            print("  > You may also need to install dependencies individually to identify the blocker.")

if __name__ == "__main__":
    deploy_okhotnik()
