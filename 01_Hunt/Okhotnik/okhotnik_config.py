import json
import os
from pathlib import Path

def build_config():
    # 1. Anchor directly to where this script is saved
    okhotnik_dir = Path(__file__).parent.absolute()
    
    # 2. Walk backwards to dynamically find the other folders
    base_hunt = okhotnik_dir.parent
    root = base_hunt.parent
    
    config = {
        "vourdalak_root": str(root),
        "okhotnik_root": str(okhotnik_dir),
        "toolchain_root": str(okhotnik_dir / "Toolchain"),
        "staging_root": str(okhotnik_dir / "Toolchain" / "Install"),
        "smotrityel_raw": str(base_hunt / "Smotrityel" / "Raw" / "Hunt" / "Subject"),
        "tools": {
            "sherlock": "sherlock/sherlock.py",
            "maigret": "maigret/maigret.py",
            "blackbird": "blackbird/blackbird.py",
            "holehe": "holehe/holehe.py"
        }
    }
    
    # Pre-build critical pathways to prevent runtime errors
    os.makedirs(okhotnik_dir / "Toolchain" / "Install", exist_ok=True)
    os.makedirs(base_hunt / "Smotrityel" / "Raw" / "Hunt" / "Subject", exist_ok=True)
    
    # 3. Save the config EXACTLY next to this script
    config_file = okhotnik_dir / "okhotnik_config.json"
    with open(config_file, "w") as f:
        json.dump(config, f, indent=4)
        
    print(f"--- OKHOTNIK CONFIGURATION ---")
    print(f"[+] Root dynamically resolved: {root}")
    print(f"[+] Config strictly saved to: {config_file}")

if __name__ == "__main__":
    build_config()