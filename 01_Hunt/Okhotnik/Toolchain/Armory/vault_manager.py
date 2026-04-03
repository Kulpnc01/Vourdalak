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
