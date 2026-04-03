import os
import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path

# Path injections for Armory and Proxy
BASE_DIR = Path(__file__).parent
sys.path.append(str(BASE_DIR / "Toolchain" / "Proxy"))
sys.path.append(str(BASE_DIR / "Toolchain" / "Armory"))

try:
    from tor_manager import TorManager
except ImportError: TorManager = None

try:
    from vault_manager import ArmoryVault
except ImportError: ArmoryVault = None

class OkhotnikCore:
    def __init__(self):
        self.config_file = BASE_DIR / "okhotnik_config.json"
        
        if not self.config_file.exists():
            print("[CRITICAL] Missing config. Run okhotnik_config.py first.")
            sys.exit(1)
            
        with open(self.config_file, "r") as f:
            self.config = json.load(f)
            
        self.toolchain = Path(self.config["toolchain_root"])
        self.raw_dest = Path(self.config["smotrityel_raw"])
        self.proxy = self.config.get("proxy_settings", {"enabled": False})
        self.vault = ArmoryVault() if ArmoryVault else None
        self.tor_proc = None

    def setup_proxy_env(self):
        if self.proxy.get("enabled"):
            if self.proxy.get("use_tor") and TorManager:
                tm = TorManager()
                self.tor_proc = tm.start()
                os.environ["HTTP_PROXY"] = "socks5h://127.0.0.1:9050"
                os.environ["HTTPS_PROXY"] = "socks5h://127.0.0.1:9050"
            else:
                os.environ["HTTP_PROXY"] = self.proxy.get("http", "")
                os.environ["HTTPS_PROXY"] = self.proxy.get("https", "")
            os.environ["PYTHONHTTPSVERIFY"] = "0" 
        else:
            os.environ.pop("HTTP_PROXY", None)
            os.environ.pop("HTTPS_PROXY", None)

    def get_tool_args(self, tool_name):
        """Fetches dynamic arguments like credentials for specific tools."""
        if not self.vault: return []
        
        if tool_name == "instaloader":
            acc = self.vault.get_next_available("instagram")
            if acc:
                print(f" [*] ARMORY: Injecting session for {acc['user']}")
                return ["--login", acc["user"], "--password", acc["pass"]]
        
        elif tool_name == "maigret":
            # Maigret can use a global cookie file if added to Armory
            cookie_path = BASE_DIR / "Toolchain" / "Armory" / "maigret_cookies.txt"
            if cookie_path.exists():
                return ["--cookie-file", str(cookie_path)]
                
        return []

    def run_hunt(self):
        print("--- OKHOTNIK CORE: ACQUISITION ---")
        target = input("[Target Name]: ").strip().replace(" ", "_")
        if not target: return
        
        try:
            self.setup_proxy_env()
            
            target_dir = self.raw_dest / target
            log_dir = target_dir / "Logs"
            os.makedirs(log_dir, exist_ok=True)
            
            manual_data = input("[Enter Known Aliases/Data]: ")
            with open(target_dir / "User_Supplied.txt", "w") as f:
                f.write(f"Target: {target}\nData: {manual_data}\nTimestamp: {datetime.now()}\n")
                
            print(f"\n[+] Initiating Toolchain for {target}...")
            current_env = os.environ.copy()
            
            for tool_name, rel_path in self.config["tools"].items():
                script_path = self.toolchain / rel_path
                
                if script_path.exists():
                    print(f"  > Running {tool_name}...")
                    log_file = log_dir / f"{tool_name}.log"
                    
                    # Fetch extra args (credentials)
                    extra_args = self.get_tool_args(tool_name)
                    
                    with open(log_file, "a", encoding="utf-8") as lf:
                        lf.write(f"\n--- EXECUTION: {datetime.now()} ---\n")
                        subprocess.run(
                            [sys.executable, str(script_path), manual_data] + extra_args,
                            stdout=lf, stderr=lf, cwd=script_path.parent,
                            env=current_env
                        )
                else:
                    print(f"  [SKIP] {tool_name} missing from Toolchain.")
                    
            print(f"\n[SUCCESS] Hunt complete. Data staged at: {target_dir}")

        finally:
            if self.tor_proc:
                print("[*] SHUTTING DOWN ONION ROUTER...")
                self.tor_proc.terminate()

if __name__ == "__main__":
    OkhotnikCore().run_hunt()
