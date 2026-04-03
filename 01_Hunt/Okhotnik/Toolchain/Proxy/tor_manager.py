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
