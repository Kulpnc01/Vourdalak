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
        "profiles_root": str(base_hunt / "Smotrityel" / "Profiles"),
        "smotrityel_raw": str(base_hunt / "Smotrityel" / "Profiles"),
        "proxy_settings": {
            "enabled": False,
            "http": "http://127.0.0.1:8080",
            "https": "http://127.0.0.1:8080",
            "use_tor": False
        },
        "tools": {
            "sherlock": "sherlock/sherlock_project/sherlock.py",
            "maigret": "maigret/maigret/maigret.py",
            "blackbird": "blackbird/blackbird.py",
            "holehe": "holehe/holehe/core.py",
            "instaloader": "instaloader/instaloader/instaloader.py",
            "twscrape": "twscrape/twscrape/main.py",
            "phoneinfoga": "phoneinfoga/phoneinfoga.exe",
            "judyrecords": "judyrecords_scraper.py",
            "court_scraper": "court_scraper_launcher.py",
            "florida_doc": "florida_doc_scraper.py",
            "alachua_clerk": "alachua_clerk_scraper.py",
            "multi_county": "florida_multi_county_scraper.py"
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
