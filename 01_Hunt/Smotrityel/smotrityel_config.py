import json
import os
from pathlib import Path

def build_smotrityel_config():
    # 1. Anchor directly to where this script is saved (Smotrityel folder)
    smotrityel_dir = Path(__file__).parent.absolute()
    
    # 2. Walk backwards to find the roots
    base_hunt = smotrityel_dir.parent
    root = base_hunt.parent
    
    config = {
        "vourdalak_root": str(root),
        "smotrityel_root": str(smotrityel_dir),
        "input_raw": str(smotrityel_dir / "Raw" / "Hunt" / "Subject"),
        "supplied_input": str(base_hunt / "Input"),
        "processing_norm": str(smotrityel_dir / "Normalized" / "Subject"),
        "output_feed": str(root / "02_Feed" / "Subject"),
        "filter_settings": {
            "min_psych_score": 3.0,
            "vip_senders": ["VIP_Contact_1"],
            "safe_keywords": ["PROJECT_CODENAME"]
        }
    }
    
    # Pre-build critical pathways
    os.makedirs(smotrityel_dir / "Raw" / "Hunt" / "Subject", exist_ok=True)
    os.makedirs(base_hunt / "Input", exist_ok=True)
    os.makedirs(smotrityel_dir / "Normalized" / "Subject", exist_ok=True)
    os.makedirs(root / "02_Feed" / "Subject", exist_ok=True)
    
    # 3. Save the config EXACTLY next to this script
    config_file = smotrityel_dir / "smotrityel_config.json"
    with open(config_file, "w") as f:
        json.dump(config, f, indent=4)
        
    print(f"--- SMOTRITYEL CONFIGURATION ---")
    print(f"[+] Root dynamically resolved: {root}")
    print(f"[+] Config strictly saved to: {config_file}")

if __name__ == "__main__":
    build_smotrityel_config()
