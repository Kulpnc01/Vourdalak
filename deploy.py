import os
import sys
import subprocess
from pathlib import Path

class HuntDeployer:
    def __init__(self):
        # Anchor strictly to the 01_Hunt directory and define the Project Root
        self.project_root = Path(__file__).parent.absolute()
        # self.project_root already defined
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
        
        script_path = self.project_root / rel_path
        
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
        self.run_python_script("01_Hunt/Okhotnik/okhotnik_config.py", "Okhotnik Configuration Map")
        self.run_python_script("01_Hunt/Smotrityel/smotrityel_config.py", "Smotrityel Configuration Map")
        
        # PHASE 2: Prime the Environments (Dependencies)
        self.run_python_script("01_Hunt/Okhotnik/okhotnik_deploy.py", "Okhotnik Core Dependencies")
        self.run_python_script("01_Hunt/Smotrityel/smotrityel_deploy.py", "Smotrityel Normalization Dependencies")
        self.run_python_script("02_Feed/feed_deploy.py", "Feed Analysis Dependencies")
        
        # PHASE 3: Arm the Hunters (Toolchain)
        self.run_python_script("01_Hunt/Okhotnik/Toolchain/Install/tool_installer.py", "Okhotnik Toolchain & Requirements")

        # PHASE 4: Identity Obscuration (Tor Proxy)
        self.run_python_script("01_Hunt/Okhotnik/Toolchain/Proxy/tor_manager.py --setup", "Portable Tor Engine Deployment")

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
