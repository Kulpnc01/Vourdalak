import os
import sys
import subprocess
import platform
from pathlib import Path

def deploy_smotrityel():
    print("--- SMOTRITYEL: DEPLOYMENT (EGOWEAVER 2.0 + ARM64) ---")
    script_dir = Path(__file__).parent
    req_file = script_dir / "smotrityel_reqs.txt"
    
    # Core libraries + EgoWeaver 2.0 Requirements
    core_reqs = [
        "requests", 
        "pandas", 
        "numpy",
        "customtkinter",
        "ijson"
    ]
    
    with open(req_file, "w") as f:
        f.write("\n".join(core_reqs))
    
    print(f"[*] Target Architecture: {platform.machine()}")
    print("[*] Installing/Upgrading dependencies...")
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "--upgrade", "--prefer-binary", "-r", str(req_file)
        ])
        print("[SUCCESS] Smotrityel (EgoWeaver) environment is primed.")
    except subprocess.CalledProcessError as e:
        print(f"\n[!] INSTALLATION WARNING: Code {e.returncode}")
        if platform.machine().lower() in ['arm64', 'aarch64']:
            print("  > ARM64 Detected. Note: 'numpy' and 'pandas' usually have wheels, but if they fail, ensure build tools are active.")

if __name__ == "__main__":
    deploy_smotrityel()
