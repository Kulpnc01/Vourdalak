# PROJECT ARCHITECTURE: Vourdalak2.0
```text
  01_Hunt/
    hunt_deploy.py
    Okhotnik/
      okhotnik_config.example.json
      okhotnik_config.py
      okhotnik_core.py
      okhotnik_deploy.py
      requirements.txt
      Toolchain/
        Armory/
          provisioner.py
          vault_manager.py
        Install/
          tool_installer.py
        Proxy/
          tor_manager.py
    Smotrityel/
      config.example.json
      core/
        __init__.py
        filter.py
        health.py
        parsers/
          __init__.py
          chatgpt.py
          copilot.py
          facebook.py
          gemini.py
          gmail.py
          okhotnik.py
          phone.py
          samsung_health.py
          snapchat.py
          whatsapp.py
        timeline.py
      smotrityel_config.example.json
      smotrityel_config.py
      smotrityel_core.py
      smotrityel_deploy.py
      smotrityel_reqs.txt
      smotrityel_weaver.py
      subject_profile.example.json
  AGENT_PROTOCOL.md
  core_flattener.py
  hunt.bat
  initialize_repo.bat
  panopticon.py
  README.md
  vourdalak.py
  vourdalak_gui.py
  Vourdalak_Logic_Map.md
```

## FILE: 01_Hunt\hunt_deploy.py
```py
import os
import sys
import subprocess
from pathlib import Path

class HuntDeployer:
    def __init__(self):
        # Anchor strictly to the 01_Hunt directory and define the Project Root
        self.hunt_dir = Path(__file__).parent.absolute()
        self.project_root = self.hunt_dir.parent
        self.venv_dir = self.project_root / "vourdalak_env"
        
        # This will hold the path to the isolated Python engine
        self.venv_python = None

        print("==================================================")
        print("  MODULE 01_HUNT: MASTER DEPLOYMENT SEQUENCE      ")
        print(f"  Project Root: {self.project_root}")
        print("==================================================\n")

    def setup_virtual_environment(self):
        print("[*] INITIALIZING: Virtual Environment Sandbox")
        
        # 1. Check if Venv already exists
        if not self.venv_dir.exists():
            print("  > Creating new venv bubble 'vourdalak_env'...")
            subprocess.run([sys.executable, "-m", "venv", str(self.venv_dir)], check=True)
        else:
            print("  > Existing 'vourdalak_env' detected.")

        # 2. Map the isolated Python executable based on OS
        if os.name == 'nt':
            # Windows
            self.venv_python = self.venv_dir / "Scripts" / "python.exe"
        else:
            # Linux / Android (Termux)
            self.venv_python = self.venv_dir / "bin" / "python"

        if not self.venv_python.exists():
            print(f"  [CRITICAL ERROR] Failed to locate venv Python at {self.venv_python}")
            sys.exit(1)

        # 3. Auto-upgrade build tools inside the bubble to prevent warnings
        print("  > Upgrading pip, setuptools, and wheel inside the sandbox...")
        subprocess.run(
            [str(self.venv_python), "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel", "--quiet"], 
            check=True
        )  
        print("[+] SUCCESS: Sandbox is active.\n")

    def run_python_script(self, rel_path_with_args, description):
        # Split args if present
        parts = str(rel_path_with_args).split(' ')
        rel_path = parts[0]
        args = parts[1:]
        
        script_path = self.hunt_dir / rel_path
        
        print(f"[*] EXECUTING: {description}")
        if not script_path.exists():
            print(f"  [CRITICAL ERROR] Target missing: {script_path}")
            print(f"  [!] HALTING DEPLOYMENT TO PREVENT CORRUPTION.")
            sys.exit(1)

        try:
            # We strictly use the venv_python engine here, NOT the global one
            cmd = [str(self.venv_python), str(script_path)] + args
            subprocess.run(
                cmd,
                cwd=script_path.parent, 
                check=True
            )
            print(f"[+] SUCCESS: {description} completed.\n")
        except subprocess.CalledProcessError as e:
            print(f"\n[CRITICAL ERROR] {description} failed with code {e.returncode}.")
            print(f"  [!] HALTING DEPLOYMENT.")
            sys.exit(1)

    def execute_sequence(self):
        # ---------------------------------------------------------
        # PHASE 0: Establish the Sandbox
        # ---------------------------------------------------------
        self.setup_virtual_environment()

        # ---------------------------------------------------------
        # THE DEPLOYMENT SEQUENCE (Running inside the Sandbox)
        # ---------------------------------------------------------
        
        # PHASE 1: Build the Maps (Configs)
        self.run_python_script("Okhotnik/okhotnik_config.py", "Okhotnik Configuration Map")
        self.run_python_script("Smotrityel/smotrityel_config.py", "Smotrityel Configuration Map")
        
        # PHASE 2: Prime the Environments (Dependencies)
        self.run_python_script("Okhotnik/okhotnik_deploy.py", "Okhotnik Core Dependencies")
        self.run_python_script("Smotrityel/smotrityel_deploy.py", "Smotrityel Normalization Dependencies")
        
        # PHASE 3: Arm the Hunters (Toolchain)
        self.run_python_script("Okhotnik/Toolchain/Install/tool_installer.py", "Okhotnik Toolchain & Requirements")

        # PHASE 4: Identity Obscuration (Tor Proxy)
        self.run_python_script("Okhotnik/Toolchain/Proxy/tor_manager.py --setup", "Portable Tor Engine Deployment")

        print("==================================================")
        print("  [SYSTEM GREEN] 01_HUNT INFRASTRUCTURE PRIMED    ")
        print("  Sandbox Active. Dependencies Isolated.          ")
        print("==================================================")
        print("To run hunts manually later, activate the environment first:")
        if os.name == 'nt':
            print("  Command: .\\vourdalak_env\\Scripts\\activate")
        else:
            print("  Command: source vourdalak_env/bin/activate")

if __name__ == "__main__":
    HuntDeployer().execute_sequence()

```

## FILE: 01_Hunt\Okhotnik\okhotnik_config.example.json
```json
{
    "vourdalak_root": "FULL_PATH_TO_VOURDALAK",
    "okhotnik_root": "FULL_PATH_TO_OKHOTNIK",
    "toolchain_root": "FULL_PATH_TO_TOOLCHAIN",
    "staging_root": "FULL_PATH_TO_STAGING",
    "smotrityel_raw": "FULL_PATH_TO_SMOTRITYEL_RAW",
    "proxy_settings": {
        "enabled": false,
        "http": "http://127.0.0.1:8080",
        "https": "http://127.0.0.1:8080",
        "use_tor": false
    },
    "tools": {
        "sherlock": "sherlock/sherlock.py",
        "maigret": "maigret/maigret.py",
        "blackbird": "blackbird/blackbird.py",
        "holehe": "holehe/holehe.py"
    }
}

```

## FILE: 01_Hunt\Okhotnik\okhotnik_config.py
```py
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
```

## FILE: 01_Hunt\Okhotnik\okhotnik_core.py
```py
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

```

## FILE: 01_Hunt\Okhotnik\okhotnik_deploy.py
```py
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

```

## FILE: 01_Hunt\Okhotnik\requirements.txt
```txt
requests
instaloader
holehe
pandas
beautifulsoup4
aiohttp
colorama
lxml
duckduckgo-search
```

## FILE: 01_Hunt\Okhotnik\Toolchain\Armory\provisioner.py
```py
import os
import time
import uuid
import requests
import random
import string
from pathlib import Path

class BurnerProvisioner:
    def __init__(self):
        self.email_api = "https://api.mail.tm"
        self.armory_dir = Path(__file__).parent.absolute()
        
    def generate_random_string(self, length=10):
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

    # --- EMAIL PROVISIONING (mail.tm) ---
    def create_burner_email(self):
        """Creates a temporary email account and returns (address, password, token)."""
        print("[*] PROVISIONER: Requesting new burner email...")
        try:
            # 1. Get Domain
            domains = requests.get(f"{self.email_api}/domains").json()
            domain = domains['hydra:member'][0]['domain']
            
            # 2. Create Account
            address = f"{self.generate_random_string()}@{domain}"
            password = self.generate_random_string(12)
            
            payload = {"address": address, "password": password}
            requests.post(f"{self.email_api}/accounts", json=payload).json()
            
            # 3. Get Auth Token
            token_resp = requests.post(f"{self.email_api}/token", json=payload).json()
            token = token_resp['token']
            
            print(f" [+] PROVISIONED: {address}")
            return address, password, token
        except Exception as e:
            print(f" [!] Email Provisioning Failed: {e}")
            return None, None, None

    def wait_for_verification_code(self, token, timeout=300):
        """Polls the inbox for a verification code or link."""
        print("[*] PROVISIONER: Watching inbox for verification signal...")
        start_time = time.time()
        headers = {"Authorization": f"Bearer {token}"}
        
        while time.time() - start_time < timeout:
            try:
                resp = requests.get(f"{self.email_api}/messages", headers=headers).json()
                messages = resp.get('hydra:member', [])
                
                if messages:
                    # Get latest message
                    msg_id = messages[0]['id']
                    msg_full = requests.get(f"{self.email_api}/messages/{msg_id}", headers=headers).json()
                    body = msg_full.get('text', '')
                    
                    # Heuristic to find 6-digit codes
                    import re
                    code = re.search(r'\b\d{6}\b', body)
                    if code:
                        print(f" [+] SIGNAL ACQUIRED: Code {code.group(0)}")
                        return code.group(0)
                    
                    # Fallback: return the whole body for manual inspection
                    print(" [+] SIGNAL ACQUIRED: Content received (no numeric code found).")
                    return body
            except: pass
            time.sleep(5)
        
        print(" [!] TIMEOUT: No verification signal received.")
        return None

    # --- SMS PROVISIONING (Local Gateway / Android Bridge) ---
    def wait_for_local_sms(self, timeout=300):
        """
        Polls a local file for incoming SMS signals. 
        This is the landing zone for your Android phone bridge.
        """
        gateway_file = self.armory_dir / "sms_gateway.txt"
        print(f"[*] PROVISIONER: Watching Local SMS Gateway ({gateway_file.name})...")
        
        if not gateway_file.exists():
            with open(gateway_file, 'w') as f: f.write("") # Create empty

        start_time = time.time()
        # Keep track of initial content to only catch NEW messages
        initial_content = gateway_file.read_text()

        while time.time() - start_time < timeout:
            current_content = gateway_file.read_text()
            if current_content != initial_content:
                # New signal detected!
                new_data = current_content.replace(initial_content, "").strip()
                import re
                code = re.search(r'\b\d{4,8}\b', new_data)
                if code:
                    print(f" [+] SMS SIGNAL ACQUIRED: Code {code.group(0)}")
                    return code.group(0)
                else:
                    print(" [+] SMS SIGNAL ACQUIRED: Content received.")
                    return new_data
            time.sleep(2)
        
        print(" [!] TIMEOUT: No SMS signal detected in gateway.")
        return None

    def request_sms_number(self, api_key=None, service="generic"):
        """Bridge for both paid and local phone verification."""
        if not api_key:
            print(" [*] SMS MODE: Using Local Android Bridge. (Update sms_gateway.txt)")
            return "LOCAL_GATEWAY"
        # Paid logic...
        return "PENDING_API"

if __name__ == "__main__":
    p = BurnerProvisioner()
    email, pwd, token = p.create_burner_email()
    if email:
        print(f"Email: {email}\nPass: {pwd}")
        print("Waiting for verification (Ctrl+C to stop)...")
        content = p.wait_for_verification_code(token)
        if content:
            print(f"Message Content: {content}")

```

## FILE: 01_Hunt\Okhotnik\Toolchain\Armory\vault_manager.py
```py
import os
import json
import time
from pathlib import Path

class ArmoryVault:
    def __init__(self):
        self.vault_dir = Path(__file__).parent.absolute()
        self.db_file = self.vault_dir / "armory_vault.json"
        self.sessions_dir = self.vault_dir / "Sessions"
        os.makedirs(self.sessions_dir, exist_ok=True)
        self.db = self._load_db()

    def _load_db(self):
        if self.db_file.exists():
            with open(self.db_file, 'r') as f:
                return json.load(f)
        return {"accounts": {}, "cookies": {}, "api_keys": {}}

    def save_db(self):
        with open(self.db_file, 'w') as f:
            json.dump(self.db, f, indent=4)

    def add_account(self, platform, username, password, session_data=None):
        if platform not in self.db["accounts"]:
            self.db["accounts"][platform] = []
        
        # Check for existing
        for acc in self.db["accounts"][platform]:
            if acc["user"] == username:
                acc["pass"] = password
                acc["session"] = session_data
                self.save_db()
                return

        self.db["accounts"][platform].append({
            "user": username,
            "pass": password,
            "session": session_data,
            "last_used": 0,
            "status": "active"
        })
        self.save_db()

    def get_next_available(self, platform, cooldown_seconds=3600):
        """Fetches the next available account that isn't in cooldown."""
        if platform not in self.db["accounts"]:
            return None

        # Sort by last_used to ensure even rotation
        accounts = sorted(self.db["accounts"][platform], key=lambda x: x["last_used"])
        now = time.time()

        for acc in accounts:
            if acc["status"] == "active" and (now - acc["last_used"]) > cooldown_seconds:
                acc["last_used"] = now
                self.save_db()
                return acc
        
        return None

    def mark_failed(self, platform, username):
        """Flags an account as compromised or banned."""
        if platform in self.db["accounts"]:
            for acc in self.db["accounts"][platform]:
                if acc["user"] == username:
                    acc["status"] = "banned"
                    self.save_db()
                    print(f" [!] FLAG: Account {username} marked as BANNED.")

if __name__ == "__main__":
    # CLI interface for adding accounts
    import sys
    vault = ArmoryVault()
    if len(sys.argv) > 4 and sys.argv[1] == "--add":
        # python vault_manager.py --add instagram myuser mypass
        vault.add_account(sys.argv[2], sys.argv[3], sys.argv[4])
        print(f"[+] Added {sys.argv[3]} to {sys.argv[2]} armory.")

```

## FILE: 01_Hunt\Okhotnik\Toolchain\Install\tool_installer.py
```py
import os
import sys
import json
import shutil
import subprocess
import platform
from pathlib import Path

class ToolchainInstaller:
    def __init__(self):
        # Anchor: 01_Hunt/Okhotnik/Toolchain/Install/tool_installer.py
        self.script_dir = Path(__file__).parent.absolute()
        
        # Navigate up exactly 2 levels to Okhotnik to find the config
        self.config_file = self.script_dir.parents[1] / "okhotnik_config.json"
        
        if not self.config_file.exists():
            print(f"[CRITICAL] Config missing at {self.config_file}")
            print("  > Run the hunt_deploy.py master script first.")
            sys.exit(1)
            
        with open(self.config_file, 'r') as f:
            self.config = json.load(f)

        self.production_dir = Path(self.config["toolchain_root"])
        self.staging_dir = Path(self.config["staging_root"])
        
        # The Engine: Inherently uses the venv Python if called by hunt_deploy.py
        self.python_exe = sys.executable

        # Master Armory of OSINT Tools
        self.repositories = {
            "sherlock": "https://github.com/sherlock-project/sherlock.git",
            "maigret": "https://github.com/soxoj/maigret.git",
            "blackbird": "https://github.com/p1ngul1n0/blackbird.git",
            "holehe": "https://github.com/megadose/holehe.git",
            "twscrape": "https://github.com/vladkens/twscrape.git",
            "instaloader": "https://github.com/Instaloader/instaloader.git"
        }

    def check_git(self):
        """Ensures Git is installed before attempting to pull repositories."""
        if not shutil.which("git"):
            print("[CRITICAL] Git is missing from system PATH.")
            sys.exit(1)

    def safe_cleanup(self, path: Path):
        """Forcefully cleans a directory, bypassing Windows file locks on .git folders."""
        if path.exists():
            try:
                import stat
                def on_rm_error(func, bad_path, exc_info):
                    os.chmod(bad_path, stat.S_IWRITE)
                    os.unlink(bad_path)
                shutil.rmtree(path, onerror=on_rm_error)
            except Exception: pass

    def deploy_tools(self):
        print("\n==================================================")
        print("  OKHOTNIK: TOOLCHAIN ARMORY DEPLOYMENT           ")
        print(f"  Arch: {platform.machine()} | Engine: {self.python_exe}")
        print("==================================================\n")
        
        os.makedirs(self.staging_dir, exist_ok=True)
        os.makedirs(self.production_dir, exist_ok=True)

        for name, url in self.repositories.items():
            final_path = self.production_dir / name
            
            if final_path.exists():
                print(f"[*] Updating {name.upper()}...")
                try:
                    subprocess.run(["git", "pull"], cwd=final_path, stdout=subprocess.DEVNULL, check=True)
                except Exception:
                    print(f"    [!] Git pull failed for {name}. Skipping update.")
            else:
                print(f"[*] Acquiring {name.upper()}...")
                staging_path = self.staging_dir / name
                self.safe_cleanup(staging_path)
                
                try:
                    subprocess.run(
                        ["git", "clone", "--depth", "1", url, str(staging_path)], 
                        stdout=subprocess.DEVNULL, check=True
                    )
                    shutil.move(str(staging_path), str(final_path))
                except Exception as e:
                    print(f"    [!] Failed to acquire {name}: {e}")
                    continue

            # Install/Update requirements for this tool
            req_file = final_path / "requirements.txt"
            if req_file.exists():
                print(f"  > Syncing dependencies for {name} (ARM64 Optimized)...")
                try:
                    subprocess.run(
                        [self.python_exe, "-m", "pip", "install", "--upgrade", "--prefer-binary", "-r", str(req_file), "--quiet"],
                        check=True
                    )
                except subprocess.CalledProcessError:
                    print(f"    [!] Dependency sync partial for {name}. Manual check may be needed.")

        print("\n[SUCCESS] Armory is current and optimized.")

    def run(self):
        self.check_git()
        self.deploy_tools()

if __name__ == "__main__":
    ToolchainInstaller().run()

```

## FILE: 01_Hunt\Okhotnik\Toolchain\Proxy\tor_manager.py
```py
import os
import sys
import subprocess
import tarfile
import time
import requests
import platform
from pathlib import Path

class TorManager:
    def __init__(self):
        self.base_dir = Path(__file__).parent.absolute()
        self.tor_dir = self.base_dir / "Tor"
        self.tor_exe = self.tor_dir / "tor" / "tor.exe" # Note: tar.gz extraction structure
        self.tar_path = self.base_dir / "tor_bundle.tar.gz"
        
        # Latest Stable 15.0.8 (Current as of 2026)
        # We use x86_64 for Surface Pro ARM64 emulation or native
        self.download_url = "https://dist.torproject.org/torbrowser/15.0.8/tor-expert-bundle-windows-x86_64-15.0.8.tar.gz"

    def setup(self):
        """Downloads and extracts Tor if not present."""
        if self.tor_exe.exists():
            print("[+] Tor Expert Bundle already present.")
            return True

        print(f"[*] Acquiring Portable Tor Engine (v15.0.8)...")
        try:
            r = requests.get(self.download_url, stream=True, timeout=30)
            r.raise_for_status()
            with open(self.tar_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print("  > Extracting .tar.gz bundle...")
            with tarfile.open(self.tar_path, 'r:gz') as tar:
                tar.extractall(path=self.tor_dir)
            
            os.remove(self.tar_path)
            
            # Verify extraction and fix path if needed
            # The tar usually contains a 'tor' folder
            if (self.tor_dir / "tor" / "tor.exe").exists():
                self.tor_exe = self.tor_dir / "tor" / "tor.exe"
                print("[SUCCESS] Tor engine deployed.")
                return True
            else:
                print(" [!] Warning: tor.exe not found in expected extraction path.")
                return False
                
        except Exception as e:
            print(f"[ERROR] Failed to setup Tor: {e}")
            if self.tar_path.exists(): os.remove(self.tar_path)
            return False

    def start(self):
        """Starts the Tor process in the background."""
        # Refresh exe path check
        if not (self.tor_dir / "tor" / "tor.exe").exists():
            print("[!] Tor binary missing. Run setup first.")
            return None

        actual_exe = self.tor_dir / "tor" / "tor.exe"
        print("[*] IGNITING ONION ROUTER: IP Obscuration Active...")
        
        try:
            data_dir = self.tor_dir / "Data"
            os.makedirs(data_dir, exist_ok=True)
            
            process = subprocess.Popen(
                [str(actual_exe), "--SocksPort", "9050", "--DataDirectory", str(data_dir)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            
            print("    > Bootstrapping circuit (approx 10s)...")
            time.sleep(10)
            return process
        except Exception as e:
            print(f"[!] Failed to start Tor: {e}")
            return None

if __name__ == "__main__":
    tm = TorManager()
    if "--setup" in sys.argv:
        tm.setup()
    elif "--start" in sys.argv:
        p = tm.start()
        if p:
            print("[+] Tor is running on SOCKS5://127.0.0.1:9050")
            input("Press Enter to stop Tor...")
            p.terminate()

```

## FILE: 01_Hunt\Smotrityel\config.example.json
```json
{
    "paths": {
        "input": "Input",
        "output": "output"
    },
    "filter_settings": {
        "min_psych_score": 3.0,
        "vip_senders": [
            "VIP_Contact_1"
        ],
        "safe_keywords": [
            "PROJECT_CODENAME"
        ]
    }
}
```

## FILE: 01_Hunt\Smotrityel\core\__init__.py
```py
"""
EgoWeaver 2.0 Core Engine
Exposes the spatial, physiological, and psychological processing units.
"""

# Import from timeline.py
from .timeline import build_index, get_closest_coordinate, export_lean_records

# Import from health.py 
# We alias this so it doesn't collide with the timeline version
from .health import build_health_index, get_closest_health_metrics, export_health_records 

# Import from filter.py
from .filter import evaluate_psych_signal
```

## FILE: 01_Hunt\Smotrityel\core\filter.py
```py
import json
import os
import re

def evaluate_psych_signal(content, sender, config, subject_identifiers=None):
    """
    Mult-stage behavioral filter.
    1. Aggressive Spam/Newsletter Rejector
    2. Business/Utility Logic (High Priority Records)
    3. Personal Psychological Density (Interaction Logic)
    """
    content_lower = content.lower()
    word_count = len(content_lower.split())
    
    # --- STAGE 1: THE JUNK GUILLOTINE ---
    # Common markers of automated marketing/newsletters
    junk_markers = [
        'unsubscribe', 'view in browser', 'manage preferences', 
        'privacy policy', 'all rights reserved', 'click here to',
        'sent to you because', 'opt out'
    ]
    
    # If it contains multiple junk markers, it's out
    junk_hits = sum(1 for m in junk_markers if m in content_lower)
    if junk_hits >= 2:
        return 0.0, False, "spam"

    # Stage 1b: Domain rejection (if possible to infer from sender)
    if any(x in sender.lower() for x in ['no-reply', 'noreply', 'notifications@', 'marketing']):
        # Still allow it if it's business high-signal (handled in Stage 2)
        pass
    
    # --- STAGE 2: BUSINESS/UTILITY PASS ---
    # High-signal keywords for life-records
    utility_keywords = [
        'receipt', 'confirmation', 'order', 'invoice', 'payment',
        'statement', 'account created', 'security alert', 'login',
        'tracking', 'shipped', 'delivered', 'appointment', 'reservation',
        'subscription', 'banking', 'transaction', 'transfer'
    ]
    
    is_utility = any(u in content_lower for u in utility_keywords)
    if is_utility and word_count > 5:
        # High score for utility records, they are forensics gold
        return 8.0, True, "utility"

    # --- STAGE 3: PERSONAL PSYCHOLOGICAL DENSITY ---
    # Noise floor
    if word_count < 4: return 0.0, False, "noise"

    score = 0.0
    
    # Introspection and Emotional Weight
    introspection = ['i', 'me', 'my', 'mine', 'myself']
    emotional = ['feel', 'think', 'want', 'hope', 'wish', 'believe', 'love', 'hate', 'miss', 'sorry']
    
    # Identity Bonus (Is the subject talking?)
    if subject_identifiers:
        for ident in subject_identifiers:
            if ident.lower() in sender.lower():
                score += 3.0 # Heavy weight for self-authored content
                break

    score += sum(1.5 for w in content_lower.split() if w in introspection)
    score += sum(2.0 for w in content_lower.split() if w in emotional)
    
    # Length Bonuses
    if word_count > 12: score += 1.0
    if word_count > 30: score += 2.0

    min_score = config.get("filter_settings", {}).get("min_psych_score", 3.0)
    
    # Final check
    is_valid = score >= min_score
    return score, is_valid, "personal"

```

## FILE: 01_Hunt\Smotrityel\core\health.py
```py
import os
import json
import bisect
import csv
from datetime import datetime, timezone

def parse_iso_time(time_str):
    if not time_str: return None
    try:
        # Standard ISO or Google format
        clean_str = time_str.split('.')[0].replace('Z', '').replace(' UTC', '')
        # Handle formats like 2024-03-15 10:00:00 or 2024-03-15T10:00:00
        clean_str = clean_str.replace('T', ' ')
        dt = datetime.strptime(clean_str, '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc)
        return dt.timestamp()
    except:
        try:
            # Fallback for short dates
            dt = datetime.strptime(time_str[:10], '%Y-%m-%d').replace(tzinfo=timezone.utc)
            return dt.timestamp()
        except: return None

def build_health_index(storage_dir, temp_dir):
    """
    Builds a searchable physiological index from Fitbit, Google, and Samsung data.
    Returns a sorted list of [timestamp, metric_name, value]
    """
    raw_data = []
    
    # 1. SCAN BOTH STORAGE AND TEMP
    targets = [d for d in [storage_dir, temp_dir] if os.path.exists(d)]
    
    for d in targets:
        for root, _, files in os.walk(d):
            for file in files:
                path = os.path.join(root, file)
                
                # --- 1. FITBIT & GOOGLE JSON ---
                if file.endswith('.json'):
                    try:
                        with open(path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        
                        entries = data if isinstance(data, list) else data.get('Data Points', [])
                        if not isinstance(entries, list): continue
                        
                        for entry in entries:
                            ts = parse_iso_time(entry.get('dateTime') or entry.get('time'))
                            if not ts: continue
                            
                            val = entry.get('value')
                            if isinstance(val, dict):
                                for k, v in val.items():
                                    try: raw_data.append([ts, k, float(v)])
                                    except: pass
                            else:
                                try: raw_data.append([ts, file.split('.')[0], float(val)])
                                except: pass
                    except: continue

                # --- 2. SAMSUNG CSV ---
                elif file.endswith('.csv') and 'com.samsung' in file:
                    try:
                        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                            # Samsung CSVs have a metadata line first
                            first_line = f.readline()
                            if ',' not in first_line: # Probably metadata
                                pass 
                            else:
                                # If the first line looks like a header, rewind
                                f.seek(0)
                                
                            reader = csv.DictReader(f)
                            for row in reader:
                                # Find time column (Samsung uses long names)
                                time_key = next((k for k in row.keys() if k.endswith('start_time') or k.endswith('create_time')), None)
                                ts = parse_iso_time(row.get(time_key))
                                if not ts: continue
                                
                                # Harvest every non-metadata column as a metric
                                for col, val in row.items():
                                    if not val: continue
                                    clean_col = col.split('.')[-1]
                                    if clean_col not in ['start_time', 'create_time', 'deviceuuid', 'pkg_name', 'update_time', 'datauuid', 'time_offset', 'client_data_id']:
                                        try:
                                            raw_data.append([ts, clean_col, float(val)])
                                        except:
                                            # Keep as string if not a number but has content
                                            raw_data.append([ts, clean_col, val])
                    except: continue
                    
                # --- 3. GENERIC CSV ---
                elif file.endswith('.csv'):
                    try:
                        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                            reader = csv.DictReader(f)
                            for row in reader:
                                ts = parse_iso_time(row.get('timestamp') or row.get('date') or row.get('time'))
                                if not ts: continue
                                for k, v in row.items():
                                    if k.lower() not in ['timestamp', 'date', 'time']:
                                        try: raw_data.append([ts, k, float(v)])
                                        except: pass
                    except: continue

    # Sort by timestamp for fast bisect searching
    raw_data.sort(key=lambda x: x[0])
    return raw_data

def get_closest_health_metrics(h_index, target_unix_time, max_delta_seconds=300):
    """
    Returns a dict of metrics active within the window of the target time.
    """
    if not h_index: return {}
    
    # Use bisect to find the range
    keys = [x[0] for x in h_index]
    idx = bisect.bisect_left(keys, target_unix_time)
    
    metrics_at_time = {}
    
    # Check a window around the index
    search_range = range(max(0, idx - 50), min(len(h_index), idx + 50))
    for i in search_range:
        ts, metric, value = h_index[i]
        if abs(ts - target_unix_time) <= max_delta_seconds:
            # Keep the closest reading for each metric type found
            if metric not in metrics_at_time:
                metrics_at_time[metric] = value
                
    return metrics_at_time

def export_health_records(h_index, output_dir):
    if not h_index: return
    out_path = os.path.join(output_dir, "Physiology_Index.json")
    os.makedirs(output_dir, exist_ok=True)
    
    # Group by metric for a cleaner export
    export_data = {}
    for ts, metric, val in h_index:
        if metric not in export_data: export_data[metric] = []
        export_data[metric].append({"ts": ts, "val": val})
        
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, indent=2)

```

## FILE: 01_Hunt\Smotrityel\core\parsers\__init__.py
```py
"""
EgoWeaver 2.0 Parsers Package (Vourdalak Integrated)
Registers all modular data adapters for the orchestrator.
"""

from . import facebook
from . import gmail
from . import snapchat
from . import phone
from . import gemini
from . import whatsapp
from . import chatgpt
from . import copilot
from . import samsung_health
from . import okhotnik

```

## FILE: 01_Hunt\Smotrityel\core\parsers\chatgpt.py
```py
import os
import json

def parse(extract_dir):
    """
    Scans for OpenAI's conversations.json export and yields standardized dictionaries.
    Flattens the complex node-based conversation tree into discrete chronological messages.
    Expected output: {"platform": str, "timestamp": float, "sender": str, "content": str, "type": str}
    """
    for root, _, files in os.walk(extract_dir):
        for file in files:
            # OpenAI exports all chat history in a single conversations.json file
            if file == 'conversations.json':
                file_path = os.path.join(root, file)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                except (json.JSONDecodeError, FileNotFoundError):
                    continue
                    
                for conversation in data:
                    # The mapping dictionary contains all the message nodes
                    mapping = conversation.get('mapping', {})
                    
                    for node_id, node in mapping.items():
                        message = node.get('message')
                        
                        # Some nodes are empty roots or system branches; skip them
                        if not message:
                            continue
                            
                        # Extract the author to distinguish your prompts from the AI's replies
                        author = message.get('author', {})
                        role = author.get('role')
                        
                        # We generally only want 'user' (you) or 'assistant' (ChatGPT)
                        if role not in ['user', 'assistant']:
                            continue
                            
                        # OpenAI uses standard Unix timestamps (float/int in seconds) natively
                        timestamp = message.get('create_time')
                        if not timestamp:
                            continue
                            
                        # Extract the actual text content
                        content_dict = message.get('content', {})
                        content_type = content_dict.get('content_type')
                        
                        # Ensure we are only pulling text (ignoring DALL-E image generation nodes or code execution outputs)
                        if content_type != 'text':
                            continue
                            
                        parts = content_dict.get('parts', [])
                        # Combine the parts (usually just one string, but can be multiple)
                        content = "".join([str(p) for p in parts if p]).strip()
                        
                        if not content:
                            continue
                            
                        yield {
                            "platform": "ChatGPT",
                            "timestamp": float(timestamp),
                            "sender": "Self" if role == 'user' else "ChatGPT", 
                            "content": content,
                            "type": "ai_interaction"
                        }
```

## FILE: 01_Hunt\Smotrityel\core\parsers\copilot.py
```py
import os
import json
from datetime import datetime, timezone

def parse(extract_dir):
    """
    Scans for Microsoft Copilot / Bing Chat activity in MS Privacy exports.
    Yields standardized dictionaries for the EgoWeaver pipeline.
    Expected output: {"platform": str, "timestamp": float, "sender": str, "content": str, "type": str}
    """
    for root, _, files in os.walk(extract_dir):
        for file in files:
            # Microsoft often bundles this inside 'Search' or 'Bing' export folders
            if file.endswith('.json') and any(keyword in root for keyword in ['Copilot', 'Bing', 'Search']):
                file_path = os.path.join(root, file)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                except (json.JSONDecodeError, FileNotFoundError):
                    continue
                    
                # MS Privacy exports usually nest data heavily. 
                # This flattens the structure to find the actual activity list.
                activities = []
                if isinstance(data, dict):
                    if 'ActivityTypes' in data:
                        for at in data['ActivityTypes']:
                            activities.extend(at.get('Activities', []))
                    elif 'Activities' in data:
                        activities.extend(data['Activities'])
                elif isinstance(data, list):
                    activities = data
                    
                for item in activities:
                    try:
                        # Microsoft typically uses 'DateTime' with standard ISO formatting
                        time_str = item.get('DateTime') or item.get('time')
                        if not time_str:
                            continue
                            
                        # Convert to standard Unix time
                        time_str = time_str.replace('Z', '+00:00')
                        dt = datetime.fromisoformat(time_str)
                        
                        # Microsoft changes its keys frequently; check all likely prompt locations
                        content = item.get('SearchTerms') or item.get('Prompt') or item.get('Text') or item.get('QueryText')
                        
                        if not content:
                            continue
                            
                        yield {
                            "platform": "Copilot",
                            "timestamp": dt.timestamp(),
                            "sender": "Self", 
                            "content": content.strip(),
                            "type": "ai_interaction"
                        }
                        
                    except (ValueError, AttributeError):
                        continue
```

## FILE: 01_Hunt\Smotrityel\core\parsers\facebook.py
```py
import os
import json
from datetime import datetime, timezone

def fix_text(text):
    if not text: return ""
    try:
        return text.encode('latin1').decode('utf-8', 'ignore')
    except (UnicodeEncodeError, UnicodeDecodeError):
        return text

def parse(extract_dir):
    for root, _, files in os.walk(extract_dir):
        for file in files:
            # FIX: Process ALL message files, not just message_1
            if file.startswith('message_') and file.endswith('.json') and ('inbox' in root or 'e2ee_cutover' in root):
                file_path = os.path.join(root, file)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                except (json.JSONDecodeError, FileNotFoundError):
                    continue

                participants = [fix_text(p.get('name', 'Unknown')) for p in data.get('participants', [])]
                thread_name = " and ".join(participants) if participants else "Unknown Thread"

                daily_chats = {}
                for msg in data.get('messages', []):
                    if 'content' not in msg:
                        continue
                        
                    ts = msg.get('timestamp_ms', 0) / 1000.0
                    date_str = datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d")
                    
                    sender = fix_text(msg.get('sender_name', 'Unknown'))
                    content = fix_text(msg.get('content', ''))
                    
                    if date_str not in daily_chats:
                        daily_chats[date_str] = {"timestamp": ts, "messages": []}
                    daily_chats[date_str]['messages'].append(f"[{sender}]: {content}")
                    
                for date_str, chat_data in daily_chats.items():
                    chat_data['messages'].reverse() 
                    joined_transcript = "\n".join(chat_data['messages'])
                    
                    yield {
                        "platform": "Facebook",
                        "timestamp": chat_data['timestamp'],
                        "sender": thread_name, 
                        "content": joined_transcript,
                        "type": "message"
                    }
```

## FILE: 01_Hunt\Smotrityel\core\parsers\gemini.py
```py
import os
import json
import re
from datetime import datetime, timezone

def clean_html(raw_html):
    """Fallback: Strips HTML tags if no plain text part exists."""
    cleanr = re.compile('<.*?>')
    # Replace common HTML entities
    text = re.sub(cleanr, '', raw_html)
    text = text.replace('&quot;', '"').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
    text = text.replace('&#39;', "'").replace('&nbsp;', ' ')
    return text.strip()

def parse_html_activity(file_path):
    """
    Parses Google Takeout's MyActivity.html for Gemini/Bard activity.
    """
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
        # Each activity is inside an outer-cell mdl-cell
        # We look for Gemini Apps specifically
        items = content.split('<div class="outer-cell')
        for item in items:
            if 'Gemini Apps' not in item: continue
            
            # Extract Prompted text
            # Format: <div ...>Prompted鑱絎hy can&#39;t 8 build a solid wheel<br>
            prompt_match = re.search(r'Prompted.*?鑱(.*?)<br>', item, re.DOTALL)
            if not prompt_match: continue
            prompt = clean_html(prompt_match.group(1))
            
            # Extract Date
            # Format: Mar 1, 2026, 2:08:28閳ョ枿M EST<br>
            # Note: 閳ョ枿M seems to be an encoding issue for PM
            date_match = re.search(r'<br>(.*?)閳.*?EST<br>', item)
            if not date_match: 
                # Try a more generic date match
                date_match = re.search(r'<br>([A-Z][a-z]{2} \d+, \d{4}, \d+:\d+:\d+.*?)<br>', item)
            
            if not date_match: continue
            date_str = date_match.group(1).strip()
            # Clean up the weird characters
            date_str = re.sub(r'閳.*', ' PM', date_str) if '閳' in date_str else date_str
            
            try:
                # Example: Mar 1, 2026, 2:08:28 PM
                dt = datetime.strptime(date_str, '%b %d, %l:%M:%S %p') # This is hard because of missing year or different formats
                # Actually, let's use a more flexible parser if possible, but we don't have many libs.
                # Let's try to extract year, month, day, time
                parts = re.search(r'([A-Z][a-z]{2}) (\d+), (\d{4}), (\d+:\d+:\d+)', date_str)
                if parts:
                    m, d, y, t = parts.groups()
                    dt_str = f"{m} {d} {y} {t}"
                    dt = datetime.strptime(dt_str, '%b %d %Y %H:%M:%S').replace(tzinfo=timezone.utc)
                    ts = dt.timestamp()
                else: continue
            except: continue
            
            # Extract Response
            # The response is usually in <p> tags after the date
            response_match = re.search(r'EST<br>(.*?)<div class="content-cell', item, re.DOTALL)
            if not response_match: continue
            response = clean_html(response_match.group(1))
            
            if prompt:
                yield {
                    "platform": "Gemini",
                    "timestamp": ts,
                    "sender": "Self",
                    "content": prompt,
                    "type": "ai_interaction"
                }
            if response:
                yield {
                    "platform": "Gemini",
                    "timestamp": ts + 1, # Offset response by 1s
                    "sender": "Gemini",
                    "content": response,
                    "type": "ai_interaction"
                }
    except Exception: pass

def parse(extract_dir):
    """
    Scans for Gemini (or Bard) My Activity exports (JSON or HTML).
    """
    for root, _, files in os.walk(extract_dir):
        for file in files:
            file_path = os.path.join(root, file)
            
            # --- 1. HTML HANDLING ---
            if file == 'MyActivity.html' and ('Gemini' in root or 'Bard' in root):
                yield from parse_html_activity(file_path)
                
            # --- 2. JSON HANDLING ---
            elif file == 'My Activity.json' and ('Gemini' in root or 'Bard' in root):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        
                    for entry in data:
                        # Standard Google Activity structure
                        title = entry.get('title', '')
                        if 'Prompted' not in title and 'Searched for' not in title: continue
                        
                        content = entry.get('titleValue', '') or title.replace('Prompted ', '')
                        timestamp = entry.get('time')
                        
                        try:
                            # 2024-03-15T10:00:00Z or similar
                            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                            ts = dt.timestamp()
                        except (ValueError, AttributeError):
                            continue
                            
                        yield {
                            "platform": "Gemini",
                            "timestamp": ts,
                            "sender": "Self", 
                            "content": content,
                            "type": "ai_interaction"
                        }
                        
                except (json.JSONDecodeError, FileNotFoundError):
                    continue

```

## FILE: 01_Hunt\Smotrityel\core\parsers\gmail.py
```py
import os
import mailbox
import re
from email.utils import parsedate_to_datetime
from datetime import datetime, timezone

def clean_html(raw_html):
    """Fallback: Strips HTML tags if no plain text part exists."""
    cleanr = re.compile('<.*?>')
    return re.sub(cleanr, '', raw_html).strip()

def get_text_body(msg):
    """Digs for plain text, falls back to stripped HTML."""
    text_content = ""
    html_content = ""
    
    if msg.is_multipart():
        for part in msg.walk():
            ctype = part.get_content_type()
            cdispo = str(part.get("Content-Disposition"))
            if "attachment" in cdispo: continue
            
            try:
                if ctype == "text/plain":
                    text_content += part.get_payload(decode=True).decode('utf-8', errors='ignore')
                elif ctype == "text/html":
                    html_content += part.get_payload(decode=True).decode('utf-8', errors='ignore')
            except Exception: continue
    else:
        try:
            if msg.get_content_type() == "text/plain":
                text_content = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
            elif msg.get_content_type() == "text/html":
                html_content = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
        except Exception: pass
        
    if text_content.strip(): return text_content.strip()
    if html_content.strip(): return clean_html(html_content)
    return ""

def parse_md_export(file_path):
    """
    Parses a combined .mbox.md file which contains emails separated by '---'.
    """
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
        # Split by the separator used in the file
        parts = content.split('\n---\n')
        for part in parts:
            if not part.strip(): continue
            
            # Extract Subject, From, Date using regex
            subject_match = re.search(r'### Subject: (.*)', part)
            from_match = re.search(r'\*\*From:\*\* (.*)', part)
            date_match = re.search(r'\*\*Date:\*\* (.*)', part)
            
            if not (subject_match and from_match and date_match): continue
            
            subject = subject_match.group(1).strip()
            sender = from_match.group(1).strip()
            date_str = date_match.group(1).strip()
            
            # The body is everything after the Date line
            body_start = date_match.end()
            body = part[body_start:].strip()
            
            try:
                # Try to parse the date
                # Example: Fri, 27 Feb 2026 20:24:21 +0000
                dt = parsedate_to_datetime(date_str)
                ts = dt.timestamp()
            except: continue
            
            yield {
                "platform": "Gmail",
                "timestamp": ts,
                "sender": sender,
                "content": f"Subject: {subject}\n\n{body}",
                "type": "message"
            }
    except Exception: pass

def parse(extract_dir):
    for root, _, files in os.walk(extract_dir):
        for file in files:
            file_path = os.path.join(root, file)
            
            if file.lower().endswith('.mbox.md'):
                yield from parse_md_export(file_path)
                
            elif file.lower().endswith('.mbox'):
                try:
                    mb = mailbox.mbox(file_path)
                    for message in mb:
                        date_str = message['date']
                        if not date_str: continue
                        
                        try:
                            ts = parsedate_to_datetime(date_str).timestamp()
                        except Exception: continue
                            
                        content = get_text_body(message)
                        if not content: continue
                            
                        yield {
                            "platform": "Gmail",
                            "timestamp": ts,
                            "sender": message['from'] or "Unknown Sender",
                            "content": content,
                            "type": "message"
                        }
                except Exception:
                    pass

```

## FILE: 01_Hunt\Smotrityel\core\parsers\okhotnik.py
```py
import os
import re
from datetime import datetime, timezone

def parse(extract_dir):
    """
    Parses Okhotnik OSINT logs (Sherlock, Maigret, etc.)
    Expected format: [+][*] Signal output from CLI tools.
    """
    for root, _, files in os.walk(extract_dir):
        for file in files:
            if file.endswith('.log') or 'User_Supplied' in file:
                file_path = os.path.join(root, file)
                
                try:
                    # Get file modification time as a fallback timestamp
                    mtime = os.path.getmtime(file_path)
                    
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                        
                    for line in lines:
                        line = line.strip()
                        if not line: continue
                        
                        # Sherlock/Maigret style: [+] Site: http://url.com
                        if line.startswith('[+]') or 'Found at' in line:
                            yield {
                                "platform": "OSINT",
                                "timestamp": mtime,
                                "sender": "Okhotnik",
                                "content": f"Signal Discovered: {line}",
                                "type": "system"
                            }
                        
                        # Generic Log Info: [*] Checking...
                        elif line.startswith('[*]'):
                            # High signal for behavioral timeline
                            yield {
                                "platform": "OSINT",
                                "timestamp": mtime,
                                "sender": "Okhotnik",
                                "content": f"Search Event: {line}",
                                "type": "system"
                            }
                            
                except Exception:
                    continue

```

## FILE: 01_Hunt\Smotrityel\core\parsers\phone.py
```py
import os
import csv
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

def parse_csv_time(time_val):
    if not time_val: return None
    time_val = time_val.strip()
    if time_val.replace('.', '', 1).isdigit():
        try:
            ts = float(time_val)
            if ts > 1e11: ts /= 1000
            return ts
        except: return None
    return None

def parse(extract_dir):
    """
    Scans for SMS/Call XML and CSV exports.
    Uses iterative parsing for massive XML files.
    """
    for root, _, files in os.walk(extract_dir):
        for file in files:
            file_path = os.path.join(root, file)
            
            # --- 1. XML HANDLING (SMS Backup & Restore) ---
            if file.endswith('.xml'):
                try:
                    # Use iterparse to handle massive files (e.g. 500MB+) without memory crash
                    context = ET.iterparse(file_path, events=('end',))
                    for event, elem in context:
                        if elem.tag == 'sms':
                            ts_str = elem.get('date')
                            if ts_str:
                                try:
                                    ts = float(ts_str) / 1000
                                    is_sent = elem.get('type') == '2'
                                    contact = elem.get('contact_name') or elem.get('address') or "Unknown"
                                    body = elem.get('body', '').strip()
                                    if body:
                                        yield {
                                            "platform": "SMS",
                                            "timestamp": ts,
                                            "sender": "Self" if is_sent else contact,
                                            "content": body,
                                            "type": "message"
                                        }
                                except: pass
                        
                        elif elem.tag == 'call':
                            ts_str = elem.get('date')
                            if ts_str:
                                try:
                                    ts = float(ts_str) / 1000
                                    call_type = elem.get('type') # 1=In, 2=Out, 3=Missed
                                    type_map = {"1": "Incoming Call", "2": "Outgoing Call", "3": "Missed Call", "5": "Rejected Call"}
                                    call_label = type_map.get(call_type, "Call")
                                    
                                    contact = elem.get('contact_name') or elem.get('number') or "Unknown"
                                    duration = elem.get('duration', '0')
                                    
                                    content = f"[{call_label}] with {contact} | Duration: {duration}s"
                                    
                                    yield {
                                        "platform": "Phone",
                                        "timestamp": ts,
                                        "sender": "System",
                                        "content": content,
                                        "type": "message"
                                    }
                                except: pass
                        
                        # Clear element from memory
                        elem.clear()
                except Exception:
                    continue

            # --- 2. CSV HANDLING ---
            elif file.endswith('.csv'):
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            # Try to find a message/body column
                            body = row.get('body') or row.get('message') or row.get('Content') or row.get('Text')
                            ts = parse_csv_time(row.get('date') or row.get('timestamp') or row.get('time'))
                            
                            if body and ts:
                                is_sent = str(row.get('type', '')).lower() in ['2', 'sent', 'outgoing']
                                contact = row.get('contact_name') or row.get('address') or row.get('sender') or "Unknown"
                                
                                yield {
                                    "platform": "SMS", 
                                    "timestamp": ts, 
                                    "sender": "Self" if is_sent else contact, 
                                    "content": body.strip(), 
                                    "type": "message"
                                }
                except Exception: continue

```

## FILE: 01_Hunt\Smotrityel\core\parsers\samsung_health.py
```py
import os
import csv
from datetime import datetime, timezone

def parse(extract_dir):
    """
    Scans for Samsung Health CSVs (com.samsung.health.heart_rate, etc.)
    and yields standardized physiological tuples.
    """
    for root, _, files in os.walk(extract_dir):
        for file in files:
            # We target the core biometric CSVs
            if not file.endswith('.csv'): continue
            
            metric_type = None
            if 'heart_rate' in file: metric_type = 'heart_rate_bpm'
            elif 'step_count' in file: metric_type = 'step_count'
            elif 'oxygen_saturation' in file: metric_type = 'spo2'
            
            if not metric_type: continue

            file_path = os.path.join(root, file)
            with open(file_path, 'r', encoding='utf-8') as f:
                # Samsung CSVs often have metadata headers; we skip to the actual data
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        # Samsung uses 'start_time' or 'create_time' in UTC
                        raw_ts = row.get('start_time') or row.get('create_time')
                        if not raw_ts: continue
                        
                        dt = datetime.strptime(raw_ts, "%Y-%m-%d %H:%M:%S.%f").replace(tzinfo=timezone.utc)
                        val = float(row.get('heart_rate') or row.get('count') or row.get('spo2'))
                        
                        yield (dt.timestamp(), metric_type, val)
                    except (ValueError, TypeError, KeyError):
                        continue
```

## FILE: 01_Hunt\Smotrityel\core\parsers\snapchat.py
```py
import os
import json
from datetime import datetime, timezone

def parse(extract_dir):
    """Hunts for chat_history.json recursively to avoid zip-folder nesting issues."""
    for root, _, files in os.walk(extract_dir):
        if 'chat_history.json' in files:
            file_path = os.path.join(root, 'chat_history.json')
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                continue

            daily_chats = {}

            # Handle New Format: Dictionary of usernames/threads
            if isinstance(data, dict) and not any(k in data for k in ['Received Saved Chat History', 'Sent Saved Chat History']):
                for thread_name, messages in data.items():
                    if not isinstance(messages, list): continue
                    for msg in messages:
                        content = msg.get('Content') or msg.get('Text') or ""
                        media_type = msg.get('Media Type', 'TEXT')
                        
                        if not content and media_type != 'TEXT':
                            content = f"[{media_type}]"
                        if not content: continue

                        try:
                            # New format: "2026-03-01 06:58:20 UTC"
                            clean_time = msg.get('Created', '').replace(' UTC', '')
                            dt = datetime.strptime(clean_time, '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc)
                            ts = dt.timestamp()
                            date_str = dt.strftime("%Y-%m-%d")
                        except (ValueError, AttributeError): continue

                        sender = msg.get('From', 'Unknown')

                        if date_str not in daily_chats:
                            daily_chats[date_str] = {"timestamp": ts, "messages": []}
                        daily_chats[date_str]['messages'].append({"ts": ts, "text": f"[{sender}]: {content}"})

            # Handle Old Format: Category-based
            else:
                categories = ['Received Saved Chat History', 'Sent Saved Chat History']
                for category in categories:
                    for msg in data.get(category, []):
                        content = msg.get('Text') or msg.get('Content') or ""
                        media_type = msg.get('Media Type', 'TEXT')
                        
                        if not content and media_type != 'TEXT':
                            content = f"[{media_type}]"
                        if not content: continue

                        try:
                            clean_time = msg.get('Created', '').replace(' UTC', '')
                            dt = datetime.strptime(clean_time, '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc)
                            ts = dt.timestamp()
                            date_str = dt.strftime("%Y-%m-%d")
                        except (ValueError, AttributeError): continue

                        sender = msg.get('From', 'Unknown')

                        if date_str not in daily_chats:
                            daily_chats[date_str] = {"timestamp": ts, "messages": []}
                        daily_chats[date_str]['messages'].append({"ts": ts, "text": f"[{sender}]: {content}"})

            for date_str in sorted(daily_chats.keys()):
                chat_data = daily_chats[date_str]
                chat_data['messages'].sort(key=lambda x: x['ts'])
                joined = "\n".join([m['text'] for m in chat_data['messages']])
                
                yield {
                    "platform": "Snapchat",
                    "timestamp": chat_data['timestamp'],
                    "sender": "Snapchat Thread",
                    "content": joined,
                    "type": "message"
                }
```

## FILE: 01_Hunt\Smotrityel\core\parsers\whatsapp.py
```py
import os
import re
from datetime import datetime, timezone

def parse(extract_dir):
    """
    Scans for WhatsApp .txt exports and yields standardized dictionaries.
    Handles both Android and iOS timestamp formatting, as well as multi-line messages.
    """
    # Android format: "12/31/23, 11:59 PM - Sender Name: Message"
    android_pattern = re.compile(r'^(\d{1,2}/\d{1,2}/\d{2,4}, \d{1,2}:\d{2}\s?[APM]{2}) - ([^:]+): (.*)$', re.IGNORECASE)
    
    # iOS format: "[12/31/23, 11:59:00 PM] Sender Name: Message"
    ios_pattern = re.compile(r'^\[(\d{1,2}/\d{1,2}/\d{2,4}, \d{1,2}:\d{2}:\d{2}\s?[APM]{2})\] ([^:]+): (.*)$', re.IGNORECASE)

    for root, _, files in os.walk(extract_dir):
        for file in files:
            # WhatsApp chat files usually contain 'WhatsApp' or start with '_chat'
            if file.endswith('.txt') and ('WhatsApp' in file or file.startswith('_chat')):
                file_path = os.path.join(root, file)

                with open(file_path, 'r', encoding='utf-8') as f:
                    current_msg = None

                    for line in f:
                        line = line.strip()
                        if not line:
                            continue

                        # Check which OS generated the export
                        match_android = android_pattern.match(line)
                        match_ios = ios_pattern.match(line)

                        if match_android or match_ios:
                            # If we have a fully built message waiting, yield it to EgoWeaver
                            if current_msg:
                                yield current_msg

                            # Explicit elif satisfies strict type linters in VS Code
                            if match_android:
                                date_str, sender, content = match_android.groups()
                                date_format = "%m/%d/%y, %I:%M %p"
                            elif match_ios:
                                date_str, sender, content = match_ios.groups()
                                date_format = "%m/%d/%y, %I:%M:%S %p"

                            try:
                                # Check if the year is 4 digits (e.g., '2023') instead of 2 digits ('23')
                                year_str = date_str.split(',')[0].split('/')[-1]
                                if len(year_str) == 4:
                                    date_format = date_format.replace('%y', '%Y')

                                # Convert to standard Unix time
                                dt = datetime.strptime(date_str, date_format).replace(tzinfo=timezone.utc)
                            except ValueError:
                                # If the date is completely malformed, skip it
                                current_msg = None
                                continue

                            # Start building the new message
                            current_msg = {
                                "platform": "WhatsApp",
                                "timestamp": dt.timestamp(),
                                "sender": sender.strip(),
                                "content": content.strip(),
                                "type": "message"
                            }
                        else:
                            # If the line doesn't start with a timestamp, it belongs to the previous message
                            if current_msg:
                                current_msg["content"] += f"\n{line}"

                    # Don't forget to yield the very last message in the file once the loop ends
                    if current_msg:
                        yield current_msg
```

## FILE: 01_Hunt\Smotrityel\core\timeline.py
```py
import os
import json
import ijson
import bisect
from datetime import datetime, timezone

def parse_iso_time(time_val):
    """Resilient parser for 2008-2026 timestamps including raw Unix and ISO."""
    if not time_val: return None
    if isinstance(time_val, (int, float)): return float(time_val)
    if str(time_val).isdigit(): return float(time_val)
    
    try:
        # Standardize for Google, FB, and Snapchat formats
        clean_str = str(time_val).replace(' UTC', '').replace('Z', '+00:00').replace(' ', 'T')
        return datetime.fromisoformat(clean_str).timestamp()
    except: return None

def build_index(storage_dir, temp_dir):
    timeline_data = []
    print(f" -> Executing deep-scan for Master Spatial Index...")

    search_dirs = [storage_dir, temp_dir]
    for d in search_dirs:
        if not os.path.exists(d): continue
        for root, _, files in os.walk(d):
            for file in files:
                path = os.path.join(root, file)
                
                # 1. FUZZY GOOGLE SEARCH (Handles Records, Location History, and Semantic)
                if file.endswith('.json') and any(x in file.lower() for x in ['location', 'history', 'records', 'timeline', 'semantic']):
                    print(f"   [SCAN] Processing Google/Spatial: {file}")
                    with open(path, 'rb') as f:
                        try:
                            # Try standard Google 'locations' array
                            for loc in ijson.items(f, 'locations.item'):
                                ts = parse_iso_time(loc.get('timestamp'))
                                if ts:
                                    lat = loc.get('latitudeE7', 0) / 1e7 if 'latitudeE7' in loc else loc.get('latitude', 0)
                                    lon = loc.get('longitudeE7', 0) / 1e7 if 'longitudeE7' in loc else loc.get('longitude', 0)
                                    timeline_data.append([ts, lat, lon, loc.get('accuracy', 25)])
                            
                            f.seek(0)
                            # Try Semantic Segments / timeline.json
                            for seg in ijson.items(f, 'semanticSegments.item'):
                                if 'timelinePath' in seg:
                                    for pt in seg['timelinePath']:
                                        ts = parse_iso_time(pt.get('time'))
                                        if ts and 'point' in pt:
                                            coords = pt['point'].replace('°','').replace(' ','')
                                            lat, lon = coords.split(',')
                                            timeline_data.append([ts, float(lat), float(lon), 15])
                        except: continue

                # 2. SOURCE-AGNOSTIC SOCIAL & SAMSUNG HARVESTER
                elif file.endswith('.json'):
                    with open(path, 'r', encoding='utf-8') as f:
                        try:
                            data = json.load(f)
                            
                            # A. Facebook Pattern
                            if isinstance(data, dict) and 'location_history' in data:
                                for entry in data['location_history']:
                                    ts, coord = entry.get('timestamp'), entry.get('coordinate', {})
                                    if ts and 'latitude' in coord:
                                        timeline_data.append([ts, coord['latitude'], coord['longitude'], 500])
                            
                            # B. Snapchat / Generic List Pattern
                            elif isinstance(data, list):
                                for entry in data:
                                    lat = entry.get('Latitude') or entry.get('lat')
                                    lon = entry.get('Longitude') or entry.get('lon')
                                    ts = parse_iso_time(entry.get('Time') or entry.get('timestamp'))
                                    if lat and ts:
                                        timeline_data.append([ts, float(lat), float(lon), 100])

                            # C. Samsung Exercise Pattern
                            elif isinstance(data, dict) and 'location_data' in data:
                                for pt in data['location_data']:
                                    timeline_data.append([pt['timestamp']/1000.0, pt['latitude'], pt['longitude'], 15])
                        except: continue

    timeline_data.sort(key=lambda x: x[0])
    
    # Verification Output
    if timeline_data:
        start_date = datetime.fromtimestamp(timeline_data[0][0], tz=timezone.utc).strftime('%Y-%m-%d')
        end_date = datetime.fromtimestamp(timeline_data[-1][0], tz=timezone.utc).strftime('%Y-%m-%d')
        print(f" [SUCCESS] Master Spatial Index spans: {start_date} to {end_date}")
        
    return timeline_data

def export_lean_records(timeline_data, output_dir):
    """Saves the Master Spatial Index for your permanent context."""
    path = os.path.join(output_dir, "Processed_Context")
    os.makedirs(path, exist_ok=True)
    with open(os.path.join(path, "master_spatial_index.jsonl"), 'w', encoding='utf-8') as f:
        for e in timeline_data:
            f.write(json.dumps({"ts": e[0], "lat": e[1], "lon": e[2], "acc": e[3]}) + '\n')

def get_closest_coordinate(timeline_data, target_unix_time, max_delta_seconds=86400):
    """Binary search for spatial anchoring."""
    if not timeline_data: return None
    timestamps = [row[0] for row in timeline_data]
    idx = bisect.bisect_left(timestamps, target_unix_time)
    if idx == 0: closest = timeline_data[0]
    elif idx == len(timeline_data): closest = timeline_data[-1]
    else:
        before, after = timeline_data[idx - 1], timeline_data[idx]
        closest = before if (target_unix_time - before[0]) < (after[0] - target_unix_time) else after
    if abs(closest[0] - target_unix_time) > max_delta_seconds: return None
    return closest
```

## FILE: 01_Hunt\Smotrityel\smotrityel_config.example.json
```json
{
    "vourdalak_root": "FULL_PATH_TO_VOURDALAK",
    "smotrityel_root": "FULL_PATH_TO_SMOTRITYEL",
    "input_raw": "FULL_PATH_TO_SMOTRITYEL_RAW",
    "supplied_input": "FULL_PATH_TO_01_HUNT_INPUT",
    "processing_norm": "FULL_PATH_TO_NORMALIZED",
    "output_feed": "FULL_PATH_TO_02_FEED",
    "filter_settings": {
        "min_psych_score": 3.0,
        "vip_senders": ["VIP_Contact_1"],
        "safe_keywords": ["PROJECT_CODENAME"]
    }
}

```

## FILE: 01_Hunt\Smotrityel\smotrityel_config.py
```py
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

```

## FILE: 01_Hunt\Smotrityel\smotrityel_core.py
```py
import os
import sys
import json
import shutil
import uuid
import zipfile
from datetime import datetime, timezone
from pathlib import Path

# Add core to path so imports work
sys.path.append(str(Path(__file__).parent))

from core import filter, health, timeline
from core.parsers import (
    facebook, gemini, gmail, phone, snapchat, whatsapp, chatgpt, copilot, okhotnik
)

class SmotrityelEngine:
    def __init__(self):
        self.smotrityel_dir = Path(__file__).parent.absolute()
        self.config_file = self.smotrityel_dir / "smotrityel_config.json"
        
        if not self.config_file.exists():
            print(f"[!] Config missing. Run smotrityel_config.py first.")
            sys.exit(1)
            
        with open(self.config_file, "r") as f:
            self.config = json.load(f)
            
        self.raw_src = Path(self.config["input_raw"])
        self.supplied_src = Path(self.config.get("supplied_input", str(self.smotrityel_dir.parent / "Input")))
        self.feed_dest = Path(self.config["output_feed"]).parent / "Compendium" # Standardized Vourdalak Feed
        
        # EgoWeaver specific settings from config
        self.filter_settings = self.config.get("filter_settings", {
            "min_psych_score": 3.0, 
            "vip_senders": [], 
            "safe_keywords": []
        })

    def get_behavioral_state(self, hr_val):
        if not hr_val: return "STABLE"
        try:
            hr = float(hr_val)
            if hr > 100: return "ELEVATED"
            if hr < 60: return "REPRESSED"
            return "BASELINE"
        except: return "UNKNOWN"

    def extract_if_needed(self, source_dir, extract_to):
        if not source_dir.exists(): return
        for item in source_dir.iterdir():
            if item.suffix == '.zip':
                target_extract = extract_to / item.stem
                if not target_extract.exists():
                    print(f" [ZIP] Unzipping supplied backup: {item.name}")
                    try:
                        with zipfile.ZipFile(item, 'r') as z:
                            z.extractall(target_extract)
                    except Exception as e:
                        print(f" [ERROR] Could not unzip {item.name}: {e}")

    def process_target(self, target_name):
        print(f"\n--- [SMOTRITYEL/EGOWEAVER] WEAVING: {target_name} ---")
        
        target_raw = self.raw_src / target_name
        target_supplied = self.supplied_src / target_name
        target_output = self.feed_dest / target_name
        os.makedirs(target_output, exist_ok=True)
        
        # Temp extract for supplied ZIPs inside target folder
        temp_extract = target_raw / "_temp_extract"
        os.makedirs(temp_extract, exist_ok=True)
        
        # Extract from both target_raw and target_supplied if they exist
        self.extract_if_needed(target_raw, temp_extract)
        self.extract_if_needed(target_supplied, temp_extract)

        # 1. Subject Profile (Local to Target)
        subject_file = target_raw / "subject_profile.json"
        if not subject_file.exists():
             subject_file = target_supplied / "subject_profile.json"

        if subject_file.exists():
            with open(subject_file, 'r', encoding='utf-8') as f:
                subject = json.load(f)
        else:
            subject = {
                "target_name": target_name,
                "identifiers": [target_name.lower(), target_name.replace('_', ' ')],
                "analysis_mode": "forensic"
            }

        # 2. Indexing
        # Scan raw, supplied, and temp_extract
        scan_dirs = [str(d) for d in [target_raw, target_supplied, temp_extract] if d.exists()]
        
        print(f" -> Phase 1: Context Indexing...")
        t_index = []
        h_index = []
        for d in scan_dirs:
            t_index.extend(timeline.build_index(d, d))
            h_index.extend(health.build_health_index(d, d))
        
        # Sort indices
        t_index.sort(key=lambda x: x[0])
        h_index.sort(key=lambda x: x[0])
        
        # 3. Weaving
        print(f" -> Phase 2: Weaving Multimodal Threads...")
        parsers = [
            (facebook.parse, "facebook"), (snapchat.parse, "snapchat"),
            (gmail.parse, "gmail"), (gemini.parse, "gemini"),
            (phone.parse, "phone"), (whatsapp.parse, "whatsapp"),
            (chatgpt.parse, "chatgpt"), (copilot.parse, "copilot"),
            (okhotnik.parse, "osint")
        ]
        
        total_processed = 0
        new_identifiers_found = False

        for parse_func, name in parsers:
            parser_count = 0
            for d in scan_dirs:
                for msg in parse_func(d):
                    # Filter Logic
                    score, is_val, category = filter.evaluate_psych_signal(
                        msg['content'], msg['sender'], {"filter_settings": self.filter_settings}, subject['identifiers']
                    )
                    if not is_val: continue
                    
                    # Discovery Logic
                    is_subject = any(ident.lower() in msg['sender'].lower() for ident in subject['identifiers'])
                    if is_subject and msg['sender'] not in subject['identifiers']:
                        subject['identifiers'].append(msg['sender'])
                        new_identifiers_found = True
                        print(f"   [DISCOVERY] New identity node: {msg['sender']}")

                    # Paths
                    platform_folder = target_output / msg['platform'].replace(" ", "_")
                    os.makedirs(platform_folder, exist_ok=True)

                    # Anchoring
                    f_coord = timeline.get_closest_coordinate(t_index, msg['timestamp'], max_delta_seconds=60)
                    f_phys = health.get_closest_health_metrics(h_index, msg['timestamp'], max_delta_seconds=60)
                    g_coord = timeline.get_closest_coordinate(t_index, msg['timestamp'], max_delta_seconds=3600)
                    
                    conf = 0.9 if (f_coord or f_phys) else (0.4 if g_coord else 0.0)
                    lat, lon, acc = (g_coord[1], g_coord[2], g_coord[3]) if g_coord else ("null", "null", "null")
                    if f_coord: lat, lon, acc = f_coord[1], f_coord[2], f_coord[3]

                    state = self.get_behavioral_state(f_phys.get('heart_rate') or f_phys.get('heart_rate.heart_rate'))
                    ts_str = datetime.fromtimestamp(msg['timestamp'], tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
                    safe_s = "".join(c for c in msg['sender'] if c.isalnum() or c in (' ', '_'))[:50].strip()
                    f_name = f"{msg['platform']}_{safe_s}_{int(msg['timestamp'])}_{uuid.uuid4().hex[:6]}.md"
                    
                    with open(platform_folder / f_name, 'w', encoding='utf-8') as f:
                        f.write(f"---\nplatform: {msg['platform']}\nsender: \"{msg['sender']}\"\ntimestamp: {ts_str}\nsubject_match: {is_subject}\npsych_score: {score:.2f}\ncategory: {category}\ncontext_confidence: {conf}\nbehavioral_state: {state}\nlocation:\n  lat: {lat}\n  lon: {lon}\n  accuracy: {acc}\n")
                        if h_index:
                            f.write("physiology:\n")
                            if f_phys:
                                for k, v in f_phys.items(): f.write(f"  {k}: {v}\n")
                            else: f.write("  data: null\n")
                        f.write(f"---\n\n[[{msg['sender']}]]\n\n{msg['content']}")
                    
                    parser_count += 1
                    total_processed += 1
            
            if parser_count > 0:
                print(f"   [PARSER] {name.upper()}: Created {parser_count} events.")

        # 4. Finalize
        if new_identifiers_found:
            save_path = target_raw / "subject_profile.json"
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(subject, f, indent=4)
        
        # Cleanup temp
        shutil.rmtree(temp_extract, ignore_errors=True)
        print(f"[SUCCESS] {target_name} normalized. Golden Record available at: {target_output}")

    def run_manager(self):
        print("--- SMOTRITYEL ENGINE: Multimodal Weaving ---")
        
        # Targets can come from Raw (Okhotnik) or Supplied Input
        targets = set()
        if self.raw_src.exists():
            targets.update([d.name for d in self.raw_src.iterdir() if d.is_dir()])
        if self.supplied_src.exists():
            targets.update([d.name for d in self.supplied_src.iterdir() if d.is_dir()])
            # Also check for individual ZIP files in supplied_src that might be named after targets
            for item in self.supplied_src.iterdir():
                if item.suffix == '.zip':
                    targets.add(item.stem)

        if not targets:
            print("  > No targets found in Smotrityel/Raw or 01_Hunt/Input.")
            return
            
        for target_name in sorted(list(targets)):
            self.process_target(target_name)

if __name__ == "__main__":
    SmotrityelEngine().run_manager()

```

## FILE: 01_Hunt\Smotrityel\smotrityel_deploy.py
```py
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

```

## FILE: 01_Hunt\Smotrityel\smotrityel_reqs.txt
```txt
requests
pandas
numpy
customtkinter
ijson
```

## FILE: 01_Hunt\Smotrityel\smotrityel_weaver.py
```py
import argparse
import json
import os
import shutil
import uuid
import zipfile
from datetime import datetime, timezone

from core import filter, health, timeline
from core.parsers import (
    facebook, gemini, gmail, phone, snapchat, whatsapp, chatgpt, copilot
)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(SCRIPT_DIR, "config.json")
SUBJECT_FILE = os.path.join(SCRIPT_DIR, "subject_profile.json")

def load_engine_config() -> dict:
    defaults = {
        "paths": {"input": "Input", "output": "output"},
        "filter_settings": {"min_psych_score": 3.0, "vip_senders": [], "safe_keywords": []}
    }
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                defaults.update(json.load(f))
        except: pass
    return defaults

def load_subject_profile() -> dict:
    defaults = {
        "target_name": "Subject_Alpha",
        "identifiers": ["subject@example.com", "subject_handle"],
        "analysis_mode": "forensic"
    }
    if os.path.exists(SUBJECT_FILE):
        try:
            with open(SUBJECT_FILE, 'r', encoding='utf-8') as f:
                defaults.update(json.load(f))
        except: pass
    else:
        # Save defaults if not exists
        with open(SUBJECT_FILE, 'w', encoding='utf-8') as f:
            json.dump(defaults, f, indent=4)
    return defaults

def update_subject_profile(profile: dict):
    with open(SUBJECT_FILE, 'w', encoding='utf-8') as f:
        json.dump(profile, f, indent=4)

def extract_archives(input_dir: str, temp_dir: str):
    print(f"--- Phase 0: Extraction ---")
    zip_count = 0
    if not os.path.exists(input_dir): return
    for item in os.listdir(input_dir):
        if item.endswith('.zip'):
            zip_count += 1
            print(f" [ZIP] Unzipping: {item}")
            try:
                with zipfile.ZipFile(os.path.join(input_dir, item), 'r') as z:
                    z.extractall(os.path.join(temp_dir, item.replace('.zip', '')))
            except Exception as e:
                print(f" [ERROR] Could not unzip {item}: {e}")
    if zip_count == 0:
        print(" [!] No .zip files found in Input folder.")

def get_behavioral_state(hr_val):
    """Placeholder for physiological state mapping."""
    if not hr_val: return "STABLE"
    try:
        hr = float(hr_val)
        if hr > 100: return "ELEVATED"
        if hr < 60: return "REPRESSED"
        return "BASELINE"
    except: return "UNKNOWN"

def main():
    config = load_engine_config()
    subject = load_subject_profile()
    
    args_input = config['paths'].get('input', 'Input')
    args_output = config['paths'].get('output', 'output')

    # Ensure folders exist
    for d in [args_input, args_output]:
        os.makedirs(d, exist_ok=True)
    for d in ['health', 'timeline']:
        os.makedirs(os.path.join(args_input, d), exist_ok=True)

    # 1. SETUP & EXTRACTION
    temp_dir = os.path.join(args_input, "_temp_extract")
    os.makedirs(temp_dir, exist_ok=True)
    extract_archives(args_input, temp_dir)

    # 2. INDICES
    print(f"\n--- Phase 1: Context Indexing ---")
    p_time = os.path.join(args_input, "timeline")
    p_health = os.path.join(args_input, "health")
    
    t_index = timeline.build_index(p_time, temp_dir)
    h_index = health.build_health_index(p_health, temp_dir)
    
    print(f" [DATA] Timeline Index: {len(t_index)} points loaded.")
    print(f" [DATA] Health Index: {len(h_index)} metrics loaded.")

    # 3. WEAVING
    print(f"\n--- Phase 2: Weaving Behavioral Context ---")
    parsers = [
        (facebook.parse, "facebook"), (snapchat.parse, "snapchat"),
        (gmail.parse, "gmail"), (gemini.parse, "gemini"),
        (phone.parse, "phone"), (whatsapp.parse, "whatsapp"),
        (chatgpt.parse, "chatgpt"), (copilot.parse, "copilot")
    ]
    
    total_processed = 0
    total_filtered = 0
    new_identifiers_found = False

    for parse_func, name in parsers:
        p_dir = os.path.join(args_input, name)
        targets = [d for d in [temp_dir, p_dir] if os.path.exists(d)]
        
        parser_count = 0
        for d in targets:
            for msg in parse_func(d):
                # Filter Logic
                score, is_val, category = filter.evaluate_psych_signal(
                    msg['content'], msg['sender'], config, subject['identifiers']
                )
                if not is_val:
                    total_filtered += 1
                    continue
                
                # Identity Discovery Logic
                is_subject = any(ident.lower() in msg['sender'].lower() for ident in subject['identifiers'])
                if is_subject and msg['sender'] not in subject['identifiers']:
                    subject['identifiers'].append(msg['sender'])
                    new_identifiers_found = True
                    print(f" [DISCOVERY] New identifier for {subject['target_name']}: {msg['sender']}")

                msg['psych_score'] = score
                platform_folder = os.path.join(args_output, msg['platform'].replace(" ", "_"))
                os.makedirs(platform_folder, exist_ok=True)

                # Context Lookup (Dual Layer)
                # Forensic Anchor (Strict 60s)
                f_coord = timeline.get_closest_coordinate(t_index, msg['timestamp'], max_delta_seconds=60)
                f_phys = health.get_closest_health_metrics(h_index, msg['timestamp'], max_delta_seconds=60)
                
                # General Context (Loose 1h)
                g_coord = timeline.get_closest_coordinate(t_index, msg['timestamp'], max_delta_seconds=3600)
                
                # Confidence Calculation
                # If we have a forensic match, confidence is high.
                conf = 0.0
                if f_coord or f_phys: conf = 0.9
                elif g_coord: conf = 0.4
                
                lat, lon, acc = (g_coord[1], g_coord[2], g_coord[3]) if g_coord else ("null", "null", "null")
                if f_coord: lat, lon, acc = f_coord[1], f_coord[2], f_coord[3]

                hr_val = f_phys.get('heart_rate') or f_phys.get('heart_rate.heart_rate')
                state = get_behavioral_state(hr_val)
                
                ts_str = datetime.fromtimestamp(msg['timestamp'], tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
                safe_s = "".join(c for c in msg['sender'] if c.isalnum() or c in (' ', '_'))[:50].strip()
                f_name = f"{msg['platform']}_{safe_s}_{int(msg['timestamp'])}_{uuid.uuid4().hex[:6]}.md"
                
                with open(os.path.join(platform_folder, f_name), 'w', encoding='utf-8') as f:
                    f.write("---\n")
                    f.write(f"platform: {msg['platform']}\n")
                    f.write(f"sender: \"{msg['sender']}\"\n")
                    f.write(f"timestamp: {ts_str}\n")
                    f.write(f"subject_match: {is_subject}\n")
                    f.write(f"psych_score: {msg['psych_score']:.2f}\n")
                    f.write(f"category: {category}\n")
                    f.write(f"context_confidence: {conf}\n")
                    f.write(f"behavioral_state: {state}\n")
                    f.write(f"location:\n  lat: {lat}\n  lon: {lon}\n  accuracy: {acc}\n")
                    
                    if h_index: # Only log physiology if health data exists for subject
                        f.write("physiology:\n")
                        if f_phys:
                            for k, v in f_phys.items(): f.write(f"  {k}: {v}\n")
                        else:
                            f.write("  data: null\n")
                    
                    f.write(f"---\n\n[[{msg['sender']}]]\n\n{msg['content']}")
                
                parser_count += 1
                total_processed += 1
        if parser_count > 0:
            print(f" [PARSER] {name.upper()}: Processed {parser_count} behavioral events.")

    # 4. EXPORT & CLEANUP
    if new_identifiers_found:
        update_subject_profile(subject)
        
    print(f"\n--- Phase 3: Finalizing ---")
    timeline.export_lean_records(t_index, args_output)
    health.export_health_records(h_index, args_output)
    
    shutil.rmtree(temp_dir, ignore_errors=True)
    print(f" [DONE] Processed: {total_processed} | Filtered: {total_filtered}")

if __name__ == "__main__":
    main()

```

## FILE: 01_Hunt\Smotrityel\subject_profile.example.json
```json
{
    "target_name": "Subject_Alpha",
    "identifiers": [
        "subject@example.com",
        "subject_handle",
        "+15550000000"
    ],
    "analysis_mode": "forensic"
}
```

## FILE: AGENT_PROTOCOL.md
```md
# Vourdalak Agent Protocol | Autonomous Operational Guide

This document defines the deterministic interface for an AI Orchestrator to control the Vourdalak pipeline.

## 1. System Topology & Discovery
The Agent must first parse the following JSON maps to understand the environment:
- **Okhotnik Config:** `01_Hunt/Okhotnik/okhotnik_config.json` (Proxy settings, tool paths)
- **Smotrityel Config:** `01_Hunt/Smotrityel/smotrityel_config.json` (Pathing, filter thresholds)
- **Vault Database:** `01_Hunt/Okhotnik/Toolchain/Armory/armory_vault.json` (Available identities)

## 2. Deterministic Workflows

### Phase A: Identity Provisioning
If the Agent requires a new identity for a specific platform:
1.  Execute `python 01_Hunt/Okhotnik/Toolchain/Armory/provisioner.py` to acquire a temporary email.
2.  Store new credentials using the Vault Manager:
    `python 01_Hunt/Okhotnik/Toolchain/Armory/vault_manager.py --add [platform] [user] [pass]`

### Phase B: Target Acquisition (The Hunt)
To initiate OSINT harvesting:
1.  Ensure proxy status is correct in `okhotnik_config.json`.
2.  Launch the Okhotnik Core:
    `python 01_Hunt/Okhotnik/okhotnik_core.py`
    - Input 1: `Target_Name` (Use underscores for spaces).
    - Input 2: `Aliases/Data` (Comma-separated strings).

### Phase C: Multimodal Weaving (Normalization)
To generate the behavioral dossier:
1.  Ensure raw data or backups are present in `01_Hunt/Smotrityel/Raw/Hunt/Subject/[Target_Name]` or `01_Hunt/Input/[Target_Name]`.
2.  Execute the Smotrityel Engine:
    `python 01_Hunt/Smotrityel/smotrityel_core.py`
3.  Monitor STDOUT for `[DISCOVERY]` tags to identify new subject handles found during weaving.

## 3. Data Schema (Consumption)
Normalized output is located at: `02_Feed/Compendium/[Target_Name]/`.
The Agent should parse files with `.md` extensions and read the YAML frontmatter for:
- `psych_score`: Heuristic psychological density (0.0 - 10.0).
- `behavioral_state`: Physiological inference (STABLE, ELEVATED, BASELINE).
- `context_confidence`: Temporal proximity score (0.0 - 1.0).

## 4. Operational Safety
- **Stealth:** Always verify `proxy_settings.enabled == true` before Phase B.
- **Throttling:** Do not execute consecutive hunts without checking account cooldowns in the Vault.
- **Resource Cleanup:** The engine handles `_temp_extract` cleanup; do not manually delete folders during processing.

---
*End of Protocol.*

```

## FILE: core_flattener.py
```py
import os
from pathlib import Path

def flatten_project(root_path, output_file, ignore_dirs=None, ignore_exts=None):
    if ignore_dirs is None:
        ignore_dirs = {'.git', '__pycache__', 'vourdalak_env', '01_Hunt/Input', '02_Feed', 'output', '03_Devour', 'sherlock', 'Vourdalak_3_3', 'Vourdalak_dead'}
    if ignore_exts is None:
        ignore_exts = {'.pyc', '.exe', '.zip', '.tar.gz', '.png', '.jpg', '.pdf', '.jsonl'}

    root = Path(root_path)
    print(f"[*] FLATTENING: {root.name} -> {output_file}")

    with open(output_file, 'w', encoding='utf-8') as out:
        # 1. Write Directory Tree Overview
        out.write(f"# PROJECT ARCHITECTURE: {root.name}\n")
        out.write("```text\n")
        for p in sorted(root.rglob('*')):
            # Check if path should be ignored
            rel_path = p.relative_to(root)
            if any(id_dir in str(rel_path) for id_dir in ignore_dirs): continue
            
            depth = len(p.parts) - len(root.parts)
            indent = "  " * depth
            out.write(f"{indent}{p.name}{'/' if p.is_dir() else ''}\n")
        out.write("```\n\n")

        # 2. Write File Contents
        for p in sorted(root.rglob('*')):
            if p.is_dir(): continue
            
            rel_path = p.relative_to(root)
            
            # Skip ignores
            if any(id_dir in str(rel_path) for id_dir in ignore_dirs): continue
            if p.suffix.lower() in ignore_exts: continue
            if p.name == output_file: continue

            print(f"  > Adding: {rel_path}")
            out.write(f"## FILE: {rel_path}\n")
            out.write(f"```{p.suffix.replace('.', '')}\n")
            try:
                with open(p, 'r', encoding='utf-8', errors='ignore') as f:
                    out.write(f.read())
            except Exception as e:
                out.write(f"ERROR READING FILE: {e}")
            out.write("\n```\n\n")

    print(f"[SUCCESS] Flattened map saved to: {output_file}")

if __name__ == "__main__":
    # Flatten Vourdalak 2.0
    flatten_project('C:/HDT/Vourdalak2.0', 'Vourdalak_Logic_Map.md')
    
    # Flatten EgoWeaver 2.0
    flatten_project('C:/HDT/EgoWeaver2.0', 'EgoWeaver_Logic_Map.md')

```

## FILE: hunt.bat
```bat
@echo off
python "C:\Users\kulpn\Documents\Vourdalak\sherlock\sherlock_project\sherlock.py" %*
```

## FILE: initialize_repo.bat
```bat
@echo off
SET REPO_URL=https://github.com/Kulpnc01/Vourdalak.git
echo ==================================================
echo   VOURDALAK 2.0: GIT INITIALIZATION TOOL
echo ==================================================
echo.

:: Initialize Repository
echo [*] Initializing Git...
git init

:: Link to Remote
echo [*] Linking to GitHub: %REPO_URL%
git remote add origin %REPO_URL%

:: Stage Files
echo [*] Staging finalized logic and documentation...
git add .

:: Commit
echo [*] Performing initial commit...
git commit -m "chore: initial release of Vourdalak v3.3 - Integrated Behavioral Engine"

:: Change branch to main
echo [*] Setting branch to main...
git branch -M main

echo.
echo ==================================================
echo   SUCCESS: REPOSITORY INITIALIZED LOCALLY
echo ==================================================
echo.
echo To complete the backup, run: 
echo   git push -u origin main
echo.
pause

```

## FILE: panopticon.py
```py
import os
import json
import uuid
import sys
from datetime import datetime
from openai import AzureOpenAI

# --- CONFIGURATION ---
API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "YOUR_API_KEY_HERE")
ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "YOUR_ENDPOINT_HERE")
DB_FILE = "panopticon_vectors.json"

# --- THE PANOPTICON "FULL STACK" PROMPT ---
# Sourced directly from PDF Pages 3-13 (DCMF & Dark Tetrad)
SYSTEM_PROMPT = """
You are the PANOPTICON AI, a forensic psychometrics engine. 
Your mandate is to generate a 25-Dimensional Character Vector based on the HiTOP and AMPD frameworks.

### I. DIMENSIONAL CHARACTER MAPPING (Score 0.0 - 1.0)
Analyze the text for these specific High-Fidelity facets:

DOMAIN 1: NEGATIVE AFFECTIVITY (Internalizing)
- Anxiousness: Nervousness, hedging language ("maybe"), recursive worrying.
- Emotional Lability: Polarity shifts, "text bombing", punctuation ("!!!").
- Hostility: Vengeful affect, "hostile attribution bias".
- Separation Insecurity: "Double texting", abandonment fears.
- Submissiveness: Apologetic ("sorry"), passive voice.

DOMAIN 2: ANTAGONISM (Externalizing)
- Callousness: Lack of remorse, dehumanizing language.
- Deceitfulness: Inconsistencies, fewer "I" pronouns (distancing).
- Grandiosity: Status seeking, "I" ownership of success, condescension.
- Manipulativeness: Gaslighting, conditional affection ("If you loved me...").

DOMAIN 3: DISINHIBITION
- Impulsivity: Urgency ("now"), typos, rapid-fire syntax.
- Irresponsibility: Blame shifting, victim stance.
- Risk Taking: Thrill-seeking verbal output.

### II. DARK TETRAD DETECTION (Adversarial Architecture)
Flag specific tactical signatures:
- "Duping Delight": Smirking/Joy in deception.
- "Future Faking": Promises of future value to extract current resources.
- "DARVO": Deny, Attack, Reverse Victim & Offender.
- "Virtuous Victimhood": Using victim status for moral immunity.

### III. BEHAVIORAL ENGINEERING (Intervention)
Based on the profile, select the optimal Counter-Measure:
- For High Narcissism/Sadism: "GRAY ROCK" (Remove emotional valence, monosyllabic).
- For High Machiavellianism: "PAPER TRAIL" (Extreme transparency, immutable rules).
- For High Volatility: "DRI" (Differential Reinforcement of Incompatible behavior).

### OUTPUT FORMAT (Strict JSON Schema)
{
  "target_identity": "String",
  "dcmf_vector": {
    "anxiousness": 0.0, "emotional_lability": 0.0, "hostility": 0.0, 
    "callousness": 0.0, "grandiosity": 0.0, "manipulativeness": 0.0,
    "impulsivity": 0.0, "risk_taking": 0.0
  },
  "dark_tetrad_flags": ["List of detected tactics or 'None'"],
  "cybernetic_phenotype": {
    "volatility": "High/Low", 
    "withdrawal": "High/Low" 
  },
  "intervention_protocol": {
    "strategy": "NAME OF STRATEGY (e.g., Gray Rock)",
    "rationale": "Why this works based on the vector.",
    "script_example": "A specific sentence the user should say."
  }
}
"""

def load_vectors():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r') as f: return json.load(f)
        except: return []
    return []

def save_vector(profile):
    db = load_vectors()
    # Create the "Full Stack" record [Page 14 Schema]
    record = {
        "user_id": str(uuid.uuid4()),
        "timestamp": datetime.utcnow().isoformat(),
        "dcmf_vector": profile.get("dcmf_vector", {}),
        "dark_tetrad_scores": profile.get("dark_tetrad_flags", []),
        "intervention_trigger": profile.get("intervention_protocol", {}).get("strategy", "MONITOR"),
        "full_profile": profile
    }
    db.append(record)
    with open(DB_FILE, 'w') as f:
        json.dump(db, f, indent=2)
    return "VECTOR_STORED"

def analyze_target(text_input, target_name):
    print(f"\n[*] INITIATING PANOPTICON VECTOR ANALYSIS for '{target_name}'...")
    
    client = AzureOpenAI(
        api_key=API_KEY, 
        api_version="2024-02-15-preview", 
        azure_endpoint=ENDPOINT
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"TARGET: {target_name}\n\nDATA:\n{text_input[:25000]}"}
            ],
            response_format={"type": "json_object"},
            temperature=0.0
        )
        
        profile = json.loads(response.choices[0].message.content)
        save_vector(profile)

        # --- THE REPORT ---
        print("\n" + "="*60)
        print(f"PANOPTICON TARGET: {target_name.upper()}")
        print("-" * 60)
        
        vec = profile.get("dcmf_vector", {})
        print(f"[!] DOMAIN: ANTAGONISM")
        print(f"    Grandiosity:      {vec.get('grandiosity', 0):.2f}")
        print(f"    Manipulativeness: {vec.get('manipulativeness', 0):.2f}")
        print(f"    Callousness:      {vec.get('callousness', 0):.2f}")
        
        print(f"\n[!] DOMAIN: NEGATIVE AFFECTIVITY")
        print(f"    Emotional Lability: {vec.get('emotional_lability', 0):.2f}")
        print(f"    Hostility:          {vec.get('hostility', 0):.2f}")

        print("-" * 60)
        print("DETECTED ADVERSARIAL ARCHITECTURES:")
        for flag in profile.get("dark_tetrad_flags", []):
            print(f"  [X] {flag}")

        print("-" * 60)
        protocol = profile.get("intervention_protocol", {})
        print(f"RECOMMENDED INTERVENTION: {protocol.get('strategy', 'N/A').upper()}")
        print(f"RATIONALE: {protocol.get('rationale', 'N/A')}")
        print(f"SCRIPT:    \"{protocol.get('script_example', 'N/A')}\"")
        print("="*60 + "\n")

    except Exception as e:
        print(f"[!] SYSTEM FAILURE: {e}")

# --- INGESTION INTERFACE ---
if __name__ == "__main__":
    print("\nPROJECT PANOPTICON // BEHAVIORAL ENGINEERING INTERFACE")
    target = input("Enter Target Name: ")
    print("Paste Intelligence (Text/Logs) - Press Ctrl+Z then Enter to finish:")
    lines = []
    try:
        while True:
            line = input()
            lines.append(line)
    except EOFError:
        pass
    text = "\n".join(lines)
    
    if len(text) > 50:
        analyze_target(text, target)
    else:
        print("[!] Insufficient Biomass.")
```

## FILE: README.md
```md
# Project Vourdalak | Behavioral Context & OSINT Orchestrator

Vourdalak is a modular intelligence architecture designed to automate the collection, normalization, and psychological profiling of digital subjects. It integrates high-fidelity OSINT harvesting (**Okhotnik**) with multimodal behavioral weaving (**Smotrityel/EgoWeaver**).

## Architecture

### 01_Hunt: Acquisition & Normalization
*   **Okhotnik (The Hunter):** Orchestrates a toolchain of OSINT scanners (Sherlock, Maigret, etc.) to harvest digital footprints.
*   **Smotrityel (The Watcher):** Ingests raw OSINT and User Backups (social, messaging, health). Weaves these threads into a "Golden Record" with enriched spatial and physiological context.
*   **EgoWeaver Core:** The behavioral engine powering the normalization phase, providing forensic anchoring and psychological scoring.

### 02_Feed: Intelligence Output
*   Standardized Markdown dossiers with YAML frontmatter containing behavioral states, physiological telemetry, and spatial coordinates.

---

## Installation Sequence (Windows ARM64 / PS7 Optimized)

1.  **Clone & Deploy:**
    ```powershell
    python 01_Hunt/hunt_deploy.py
    ```
    *This automatically creates the `vourdalak_env` sandbox, installs dependencies, and acquires the toolchain (Sherlock, Tor, etc.).*

2.  **Activate Sandbox:**
    ```powershell
    .\vourdalak_env\Scripts\activate
    ```

## Operational Interfaces

### GUI Mode (Human Control)
Launch the visual command center for point-and-click orchestration:
```powershell
python vourdalak_gui.py
```

### CLI Mode (Power User / AI)
Refer to `AGENT_PROTOCOL.md` for deterministic command schemas and autonomous workflows.

---

## Capabilities & Stealth
- **Portable Tor Circuit:** Automated IP obscuration via integrated Onion Routing.
- **Armory Vault:** Credential rotation and cooldown management for "Burner" accounts.
- **Multimodal Anchoring:** Synchronizes heart rate and location data with messaging events for deep behavioral profiling.

*Disclaimer: This tool is for authorized security research and digital twin construction only.*

```

## FILE: vourdalak.py
```py
import os
import json
import uuid
import sys
import time
from datetime import datetime
from openai import AzureOpenAI
from pypdf import PdfReader

# --- CRITICAL PATCH FOR DUCKDUCKGO ---
try:
    from duckduckgo_search import DDGS
except ImportError:
    try:
        from ddgs import DDGS
    except ImportError:
        print("[!] CRITICAL ERROR: 'duckduckgo-search' library not found.")
        sys.exit()

# --- CONFIGURATION ---
API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "YOUR_API_KEY_HERE")
ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "YOUR_ENDPOINT_HERE")

# Load Okhotnik Config for Proxy Settings
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "01_Hunt", "Okhotnik", "okhotnik_config.json")
PROXY = None
if os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH, 'r') as f:
        _cfg = json.load(f)
        _ps = _cfg.get("proxy_settings", {})
        if _ps.get("enabled"):
            PROXY = _ps.get("http")

# --- THE PANOPTICON SYSTEM PROMPT (SBM v4.0) ---
PANOPTICON_PROMPT = """
You are the "Vourdalak," a specialized behavioral intelligence engine operating under Project Panopticon protocols (SBM v4.0).
Your mission is to analyze the provided OSINT Intelligence Report and generate a high-fidelity psychological dossier.

### ANALYSIS FRAMEWORK (SBM v4.0)
You must deconstruct the subject into three nodes:

1. THE DRIVE CORE (Primary Motivation)
   - Identify the dominant engine: POWER (Control), AFFILIATION (Belonging), or ACHIEVEMENT (Competence).

2. COGNITIVE CIRCUITRY (Processing Style)
   - Complexity: Gestalt (Big Picture) vs. Granular (Details).
   - Rigidity: Reaction to Cognitive Dissonance.

3. THE SOCIAL CHASSIS (Interaction Style)
   - Authority Orientation: Submissive, Cooperative, or Adversarial.
   - Status Battery: Internal vs. External validation.

### OUTPUT FORMAT (JSON ONLY)
{
  "target_identity": "String",
  "sbm_profile": {
    "drive_core": "String",
    "cognitive_circuitry": "String",
    "social_chassis": "String"
  },
  "deyoung_scorecard": {
    "volatility": 0.0, "withdrawal": 0.0, "compassion": 0.0, "politeness": 0.0,
    "industriousness": 0.0, "orderliness": 0.0, "enthusiasm": 0.0,
    "assertiveness": 0.0, "intellect": 0.0, "openness": 0.0
  },
  "tactical_recommendation": "Actionable SBM advice based on their Drive Core."
}
"""

def save_soul(profile, target_id):
    filename = "souls.json"
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            try:
                db = json.load(f)
            except:
                db = []
    else:
        db = []

    record = {
        "id": str(uuid.uuid4()),
        "target_id": target_id,
        "timestamp": datetime.utcnow().isoformat(),
        "soul_fragment": profile
    }
    db.append(record)

    with open(filename, 'w') as f:
        json.dump(db, f, indent=2)

# --- PANOPTICON ACQUISITION PROTOCOL ---
def perform_sector_scan(query, sector_name):
    print(f"[*] Scanning {sector_name} Sector: '{query}'...")
    sector_data = ""
    try:
        # Pass proxy to DDGS if enabled
        with DDGS(proxy=PROXY) as ddgs:
            results = ddgs.text(query, max_results=5)
            if results:
                for r in results:
                    sector_data += f"[{sector_name.upper()}] Source: {r['title']} | Content: {r['body']}\n"
            else:
                print(f"    [!] No signals found in {sector_name}.")
    except Exception as e:
        print(f"    [!] Scan Error: {e}")
    return sector_data

def hunt_prey(target_name):
    print(f"\n[*] INITIATING PANOPTICON ACQUISITION PROTOCOL for: '{target_name}'")
    if PROXY: print(f"[*] IDENTITY MASKED: Via Proxy {PROXY}")
    print("=" * 60)
    
    aggregated_intel = f"PANOPTICON TARGET REPORT: {target_name}\nDATE: {datetime.utcnow().isoformat()}\n\n"

    # 1. DIGITAL IDENTITY BRANCH (Handles & Presence)
    query_digital = f'"{target_name}" site:twitter.com OR site:linkedin.com OR site:instagram.com OR site:facebook.com'
    aggregated_intel += perform_sector_scan(query_digital, "Digital_Identity")
    time.sleep(1) # Evasion pause

    # 2. PHYSICAL/ENVIRONMENTAL BRANCH (Location & Affiliation)
    query_physical = f'"{target_name}" location OR residence OR hometown OR "lived in"'
    aggregated_intel += perform_sector_scan(query_physical, "Physical_Environment")
    time.sleep(1)

    # 3. PSYCHOLOGICAL BASELINE (Verbal Output for SBM Analysis)
    query_psych = f'"{target_name}" interview OR podcast OR transcript OR "written by"'
    aggregated_intel += perform_sector_scan(query_psych, "Psych_Baseline")
    
    print("=" * 60)
    print(f"[*] ACQUISITION COMPLETE. Constructing Dossier...")
    return aggregated_intel

def vourdalak_feed(text_input, target_name):
    if not text_input or len(text_input) < 100:
        print("[!] ERROR: Intelligence yield too low. Target is a ghost.")
        return

    print(f"[*] ENGAGING SBM ENGINE ({len(text_input)} bytes of intel)...")
    
    try:
        client = AzureOpenAI(api_key=API_KEY, api_version="2024-02-15-preview", azure_endpoint=ENDPOINT)
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": PANOPTICON_PROMPT},
                {"role": "user", "content": text_input[:30000]} 
            ],
            response_format={"type": "json_object"},
            temperature=0.0
        )

        profile = json.loads(response.choices[0].message.content)
        profile["status"] = "SOUL_CONSUMED"
        save_soul(profile, target_name)
        
        print("\n" + "="*60)
        print(f"TARGET ACQUIRED: {profile.get('target_identity', target_name).upper()}")
        print("-" * 60)
        print(f"DRIVE CORE:       {profile['sbm_profile']['drive_core']}")
        print(f"COGNITIVE STYLE:  {profile['sbm_profile']['cognitive_circuitry']}")
        print(f"SOCIAL CHASSIS:   {profile['sbm_profile']['social_chassis']}")
        print("-" * 60)
        print(f"TACTICAL ADVICE:  {profile.get('tactical_recommendation', 'N/A')}")
        print("="*60 + "\n")
        print("[*] Full SBM Dossier encrypted and saved to 'souls.json'.")

    except Exception as e:
        print(f"\n[!] SYSTEM FAILURE: {str(e)}")

# --- INTERFACE ---
if __name__ == "__main__":
    print("\nPANOPTICON PROTOCOL // AUTOMATED HUNTER KILLER")
    print("------------------------------------------------")
    
    target = input("ENTER TARGET IDENTIFIER: ")
    if target:
        # Mode 2 is now the default "Hunt"
        intel_dossier = hunt_prey(target)
        if intel_dossier:
            vourdalak_feed(intel_dossier, target)

```

## FILE: vourdalak_gui.py
```py
import os
import sys
import json
import threading
import subprocess
import customtkinter as ctk
from tkinter import filedialog, messagebox
from pathlib import Path

# Add paths for internal module imports
sys.path.append(str(Path(__file__).parent / "01_Hunt" / "Okhotnik"))
sys.path.append(str(Path(__file__).parent / "01_Hunt" / "Okhotnik" / "Toolchain" / "Armory"))
sys.path.append(str(Path(__file__).parent / "01_Hunt" / "Okhotnik" / "Toolchain" / "Proxy"))

class VourdalakGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Vourdalak | Behavioral Context & OSINT Orchestrator")
        self.geometry("1100x750")
        ctk.set_appearance_mode("dark")
        
        self.root_dir = Path(__file__).parent.absolute()
        self.okhotnik_cfg_path = self.root_dir / "01_Hunt" / "Okhotnik" / "okhotnik_config.json"
        self.smotrityel_cfg_path = self.root_dir / "01_Hunt" / "Smotrityel" / "smotrityel_config.json"
        
        self.load_configs()

        # --- Layout ---
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        self.logo = ctk.CTkLabel(self.sidebar, text="VOURDALAK", font=ctk.CTkFont(size=24, weight="bold"))
        self.logo.pack(pady=20)

        self.btn_hunt = ctk.CTkButton(self.sidebar, text="Hunt Console", command=lambda: self.show_frame("hunt"))
        self.btn_hunt.pack(pady=10, padx=20)

        self.btn_vault = ctk.CTkButton(self.sidebar, text="Armory Vault", command=lambda: self.show_frame("vault"))
        self.btn_vault.pack(pady=10, padx=20)

        self.btn_network = ctk.CTkButton(self.sidebar, text="Network Hub", command=lambda: self.show_frame("network"))
        self.btn_network.pack(pady=10, padx=20)

        # Main Content Area
        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        
        self.frames = {}
        self.setup_hunt_frame()
        self.setup_vault_frame()
        self.setup_network_frame()

        self.show_frame("hunt")

    def load_configs(self):
        try:
            with open(self.okhotnik_cfg_path, 'r') as f: self.ok_cfg = json.load(f)
            with open(self.smotrityel_cfg_path, 'r') as f: self.sm_cfg = json.load(f)
        except:
            messagebox.showerror("Error", "Configs not found. Run hunt_deploy.py first.")
            sys.exit()

    def show_frame(self, name):
        for f in self.frames.values(): f.pack_forget()
        self.frames[name].pack(fill="both", expand=True)

    # --- FRAME: HUNT CONSOLE ---
    def setup_hunt_frame(self):
        f = ctk.CTkFrame(self.container, fg_color="transparent")
        self.frames["hunt"] = f
        
        ctk.CTkLabel(f, text="OPERATIONAL CONSOLE", font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w")
        
        input_group = ctk.CTkFrame(f)
        input_group.pack(fill="x", pady=10)
        
        self.target_input = ctk.CTkEntry(input_group, placeholder_text="Target Name (e.g. John_Doe)", width=300)
        self.target_input.pack(side="left", padx=10, pady=10)
        
        self.alias_input = ctk.CTkEntry(input_group, placeholder_text="Known Aliases / Emails", width=400)
        self.alias_input.pack(side="left", padx=10, pady=10)

        ctrl_group = ctk.CTkFrame(f)
        ctrl_group.pack(fill="x", pady=5)
        
        self.btn_start_hunt = ctk.CTkButton(ctrl_group, text="INITIATE HUNT", fg_color="#e74c3c", hover_color="#c0392b", command=self.run_hunt_thread)
        self.btn_start_hunt.pack(side="left", padx=10, pady=10)
        
        self.btn_start_weave = ctk.CTkButton(ctrl_group, text="START WEAVING", fg_color="#2ecc71", hover_color="#27ae60", command=self.run_weave_thread)
        self.btn_start_weave.pack(side="left", padx=10, pady=10)

        self.log_output = ctk.CTkTextbox(f, height=400)
        self.log_output.pack(fill="both", expand=True, pady=10)

    # --- FRAME: ARMORY VAULT ---
    def setup_vault_frame(self):
        f = ctk.CTkFrame(self.container, fg_color="transparent")
        self.frames["vault"] = f
        ctk.CTkLabel(f, text="CREDENTIAL ARMORY", font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w")
        
        # Simple management view
        self.vault_display = ctk.CTkTextbox(f, height=300)
        self.vault_display.pack(fill="both", expand=True, pady=10)
        self.refresh_vault_display()
        
        add_group = ctk.CTkFrame(f)
        add_group.pack(fill="x", pady=10)
        
        self.acc_platform = ctk.CTkOptionMenu(add_group, values=["instagram", "twitter", "facebook", "gmail"])
        self.acc_platform.pack(side="left", padx=5)
        
        self.acc_user = ctk.CTkEntry(add_group, placeholder_text="Username")
        self.acc_user.pack(side="left", padx=5)
        
        self.acc_pass = ctk.CTkEntry(add_group, placeholder_text="Password", show="*")
        self.acc_pass.pack(side="left", padx=5)
        
        ctk.CTkButton(add_group, text="Add Account", command=self.add_vault_acc).pack(side="left", padx=5)

    # --- FRAME: NETWORK HUB ---
    def setup_network_frame(self):
        f = ctk.CTkFrame(self.container, fg_color="transparent")
        self.frames["network"] = f
        ctk.CTkLabel(f, text="NETWORK TOPOLOGY", font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w")
        
        self.tor_switch = ctk.CTkSwitch(f, text="ENABLE TOR IP OBSCURATION", command=self.toggle_tor)
        if self.ok_cfg.get("proxy_settings", {}).get("use_tor"): self.tor_switch.select()
        self.tor_switch.pack(pady=20, anchor="w")
        
        ctk.CTkLabel(f, text="Custom Proxy (HTTP/HTTPS):").pack(anchor="w")
        self.proxy_addr = ctk.CTkEntry(f, width=400)
        self.proxy_addr.insert(0, self.ok_cfg.get("proxy_settings", {}).get("http", ""))
        self.proxy_addr.pack(pady=5, anchor="w")
        
        ctk.CTkButton(f, text="Save Network Settings", command=self.save_network).pack(pady=10, anchor="w")

    # --- LOGIC ---
    def toggle_tor(self):
        enabled = self.tor_switch.get()
        self.ok_cfg["proxy_settings"]["enabled"] = bool(enabled)
        self.ok_cfg["proxy_settings"]["use_tor"] = bool(enabled)
        
    def save_network(self):
        addr = self.proxy_addr.get()
        self.ok_cfg["proxy_settings"]["http"] = addr
        self.ok_cfg["proxy_settings"]["https"] = addr
        with open(self.okhotnik_cfg_path, 'w') as f: json.dump(self.ok_cfg, f, indent=4)
        messagebox.showinfo("Success", "Network settings updated.")

    def refresh_vault_display(self):
        vault_path = self.root_dir / "01_Hunt" / "Okhotnik" / "Toolchain" / "Armory" / "armory_vault.json"
        if vault_path.exists():
            with open(vault_path, 'r') as f:
                data = json.load(f)
                self.vault_display.delete("1.0", "end")
                self.vault_display.insert("end", json.dumps(data, indent=4))

    def add_vault_acc(self):
        p, u, pw = self.acc_platform.get(), self.acc_user.get(), self.acc_pass.get()
        if p and u and pw:
            cmd = [sys.executable, str(self.root_dir / "01_Hunt" / "Okhotnik" / "Toolchain" / "Armory" / "vault_manager.py"), "--add", p, u, pw]
            subprocess.run(cmd)
            self.refresh_vault_display()
            self.acc_user.delete(0, "end"); self.acc_pass.delete(0, "end")

    def log(self, msg):
        self.log_output.insert("end", f"{msg}\n")
        self.log_output.see("end")

    def run_hunt_thread(self):
        target = self.target_input.get()
        aliases = self.alias_input.get()
        if not target: return
        self.btn_start_hunt.configure(state="disabled")
        threading.Thread(target=self.execute_hunt, args=(target, aliases), daemon=True).start()

    def execute_hunt(self, target, aliases):
        self.log(f"[*] INITIATING HUNT: {target}...")
        # Since okhotnik_core uses input(), we need to simulate it or refactor. 
        # For now, we call it via subprocess and pipe strings if needed, 
        # but a cleaner way is to refactor okhotnik_core to accept args.
        # I'll implement a 'non-interactive' mode in the core shortly.
        self.log("[!] Note: Subprocess redirection active.")
        # Mock execution for GUI preview
        proc = subprocess.Popen(
            [sys.executable, "01_Hunt/Okhotnik/okhotnik_core.py"],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, cwd=str(self.root_dir)
        )
        # Feed target and aliases to the process
        proc.stdin.write(f"{target}\n{aliases}\n")
        proc.stdin.flush()
        
        for line in iter(proc.stdout.readline, ""):
            self.log(line.strip())
        
        proc.wait()
        self.btn_start_hunt.configure(state="normal")
        self.log("[+] HUNT SEQUENCE TERMINATED.")

    def run_weave_thread(self):
        self.btn_start_weave.configure(state="disabled")
        threading.Thread(target=self.execute_weave, daemon=True).start()

    def execute_weave(self):
        self.log("[*] STARTING MULTIMODAL WEAVER...")
        proc = subprocess.Popen(
            [sys.executable, "01_Hunt/Smotrityel/smotrityel_core.py"],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, cwd=str(self.root_dir)
        )
        for line in iter(proc.stdout.readline, ""):
            self.log(line.strip())
        proc.wait()
        self.btn_start_weave.configure(state="normal")
        self.log("[+] WEAVING COMPLETE.")

if __name__ == "__main__":
    app = VourdalakGUI()
    app.mainloop()

```

