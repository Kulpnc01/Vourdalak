import os
import sys
import json
import subprocess
import shutil
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
                os.environ["HTTP_PROXY"] = "socks5://127.0.0.1:9050"
                os.environ["HTTPS_PROXY"] = "socks5://127.0.0.1:9050"
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

    def run_hunt(self, target=None, aliases=None, skip_sherlock=False, enabled_tools=None):
        print("--- OKHOTNIK CORE: ACQUISITION ---")
        if not target:
            target = input("[Target Name]: ").strip().replace(" ", "_")
        else:
            target = target.replace(" ", "_")
            
        if not target: return
        
        try:
            self.setup_proxy_env()
            
            target_dir = self.raw_dest / target
            log_dir = target_dir / "Logs"
            os.makedirs(log_dir, exist_ok=True)
            
            if aliases is None:
                aliases = input("[Enter Known Aliases/Data]: ")
                
            with open(target_dir / "User_Supplied.txt", "w") as f:
                f.write(f"Target: {target}\nData: {aliases}\nTimestamp: {datetime.now()}\n")
                
            print(f"\n[+] Initiating Toolchain for {target}...")
            current_env = os.environ.copy()
            current_env["PYTHONIOENCODING"] = "utf-8"
            
            for tool_name, rel_path in self.config["tools"].items():
                # Filter by enabled tools
                if enabled_tools is not None and tool_name not in enabled_tools:
                    print(f"  [SKIP] {tool_name} (Not selected).")
                    continue

                if tool_name == "sherlock" and skip_sherlock:
                    print(f"  [SKIP] {tool_name} (User requested skip).")
                    continue

                script_path = self.toolchain / rel_path
                is_global = False
                
                if not script_path.exists():
                    if shutil.which(rel_path):
                        is_global = True
                    else:
                        print(f"  [SKIP] {tool_name} missing from Toolchain and not in PATH.")
                        continue

                print(f"  > Running {tool_name}...")
                log_file = log_dir / f"{tool_name}.log"
                extra_args = self.get_tool_args(tool_name)
                
                cmd = [sys.executable]
                cwd = script_path.parent if not is_global else BASE_DIR
                
                if tool_name == "sherlock":
                    cmd += ["-m", "sherlock_project", aliases]
                    cwd = script_path.parent.parent
                elif tool_name == "maigret":
                    cmd += ["-m", "maigret", aliases]
                    cwd = script_path.parent.parent
                elif tool_name == "holehe":
                    cmd += ["-m", "holehe.core", aliases, "--only-used"]
                    cwd = script_path.parent.parent
                elif tool_name == "ghunt":
                    if "@" in aliases:
                        cmd = [sys.executable, "-m", "ghunt", "email", aliases]
                    else:
                        print(f"  [SKIP] {tool_name} requires an email.")
                        continue
                elif tool_name == "h8mail":
                    if "@" in aliases:
                        cmd = [sys.executable, "-m", "h8mail", "-t", aliases]
                    else:
                        print(f"  [SKIP] {tool_name} requires an email.")
                        continue
                elif tool_name == "phoneinfoga":
                    clean_alias = aliases.replace("-", "").replace(" ", "").replace("(", "").replace(")", "")
                    if clean_alias.isdigit() or (clean_alias.startswith("+") and clean_alias[1:].isdigit()):
                        cmd = [str(script_path), "scan", "-n", aliases]
                    else:
                        print(f"  [SKIP] {tool_name} requires a phone number.")
                        continue
                elif tool_name == "blackbird":
                    if "@" in aliases:
                        cmd = [sys.executable, str(script_path), "--email", aliases, "--json"]
                    else:
                        cmd = [sys.executable, str(script_path), "--username", aliases, "--json"]
                elif tool_name == "twscrape":
                    # Deep scraping for twitter
                    cmd = [sys.executable, "-m", "twscrape", "search", aliases]
                    cwd = script_path.parent.parent
                elif tool_name == "instaloader":
                    # Deep scraping for instagram
                    cmd = [sys.executable, "-m", "instaloader", "--no-videos", "--no-captions", aliases]
                    cwd = script_path.parent.parent
                elif tool_name == "judyrecords":
                    cmd = [sys.executable, str(script_path), aliases]
                elif tool_name == "court_scraper":
                    # This needs more specific target data, using 'alachua' as a default for FL test
                    cmd = [sys.executable, str(script_path), aliases, "alachua", "fl"]
                elif tool_name == "florida_doc":
                    cmd = [sys.executable, str(script_path), aliases]
                elif tool_name == "alachua_clerk":
                    cmd = [sys.executable, str(script_path), aliases]
                elif tool_name == "duval_clerk":
                    cmd = [sys.executable, str(script_path), aliases]
                else:
                    cmd = [str(script_path), aliases]
                
                cmd += extra_args
                
                with open(log_file, "a", encoding="utf-8") as lf:
                    lf.write(f"\n--- EXECUTION: {datetime.now()} ---\n")
                    lf.flush()
                    subprocess.run(cmd, stdout=lf, stderr=lf, cwd=cwd, env=current_env)
                    
            print(f"\n[SUCCESS] Hunt complete. Data staged at: {target_dir}")

        finally:
            if self.tor_proc:
                print("[*] SHUTTING DOWN ONION ROUTER...")
                self.tor_proc.terminate()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Okhotnik Core Hunter")
    parser.add_argument("target", nargs="?", help="Target identifier")
    parser.add_argument("aliases", nargs="?", help="Known aliases or data")
    parser.add_argument("--skip-sherlock", action="store_true", help="Skip Sherlock")
    parser.add_argument("--tools", help="Comma-separated tools")
    args = parser.parse_args()
    
    enabled = [t.strip() for t in args.tools.split(",")] if args.tools else None
    OkhotnikCore().run_hunt(args.target, args.aliases, args.skip_sherlock, enabled)
