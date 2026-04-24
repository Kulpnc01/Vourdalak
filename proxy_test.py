import requests
import sys
import os
from pathlib import Path

# Add paths for TorManager
sys.path.append(str(Path(__file__).parent / "01_Hunt" / "Okhotnik" / "Toolchain" / "Proxy"))

try:
    from tor_manager import TorManager
except ImportError:
    print("[!] Failed to import TorManager")
    sys.exit(1)

def get_ip():
    try:
        response = requests.get('https://api.ipify.org', timeout=10)
        return response.text
    except Exception as e:
        return f"Error: {e}"

print(f"[*] Current Public IP: {get_ip()}")

tm = TorManager()
print("[*] Starting Tor...")
p = tm.start()

if p:
    try:
        proxies = {
            'http': 'socks5h://127.0.0.1:9050',
            'https': 'socks5h://127.0.0.1:9050'
        }
        print(f"[*] Tor Public IP: {requests.get('https://api.ipify.org', proxies=proxies, timeout=30).text}")
    except Exception as e:
        print(f"[!] Tor test failed: {e}")
    finally:
        print("[*] Stopping Tor...")
        p.terminate()
else:
    print("[!] Could not start Tor.")
