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
                # Use socks5h to ensure DNS is resolved through Tor
                os.environ["HTTP_PROXY"] = "socks5h://127.0.0.1:9050"
                os.environ["HTTPS_PROXY"] = "socks5h://127.0.0.1:9050"
                print("[*] DNS Redirection: Active (socks5h)")
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

    def generate_name_variations(self, full_name):
        """Generates comprehensive permutations of a target's name."""
        parts = full_name.split()
        if not parts: return {"social": [], "legal": []}
        
        first = parts[0]
        last = parts[-1] if len(parts) > 1 else ""
        middle_parts = parts[1:-1] if len(parts) > 2 else []
        middle = " ".join(middle_parts)
        m_initial = middle[0] if middle else ""

        social_vars = {full_name}
        legal_vars = {full_name}
        
        if last:
            # --- FORMAL & LEGAL ---
            # First Last
            legal_vars.add(f"{first} {last}")
            if middle:
                # First Middle Last
                legal_vars.add(f"{first} {middle} {last}")
                # First M. Last
                social_vars.add(f"{first} {m_initial}. {last}")
                
                # Middle as First (Legal & Social)
                for m_name in middle_parts:
                    legal_vars.add(f"{m_name} {last}")
            
            # --- INITIALS (Social Only) ---
            f_initial = first[0]
            social_vars.add(f"{f_initial}. {last}")
            if m_initial:
                social_vars.add(f"{f_initial}. {m_initial}. {last}")

            # --- NICKNAMES (Legal & Social) ---
            nicknames = {
                "matthew": ["matt", "matty"],
                "charles": ["charlie", "chuck"],
                "nicholas": ["nick", "nikolai", "nicolai"],
                "william": ["bill", "will", "billy"],
                "robert": ["bob", "rob"],
                "james": ["jim", "jamie"],
                "christopher": ["chris", "topher"]
            }
            
            f_lower = first.lower()
            if f_lower in nicknames:
                for nick in nicknames[f_lower]:
                    n_title = nick.capitalize()
                    legal_vars.add(f"{n_title} {last}")
            
            # Nicknames for Middle Name as First
            for m_name in middle_parts:
                m_lower = m_name.lower()
                if m_lower in nicknames:
                    for nick in nicknames[m_lower]:
                        legal_vars.add(f"{nick.capitalize()} {last}")

        social_vars.update(legal_vars)
        return {
            "social": sorted(list(social_vars)),
            "legal": sorted(list(legal_vars))
        }

    def run_hunt(self, target=None, aliases=None, skip_sherlock=False, enabled_tools=None):
        print("--- OKHOTNIK CORE: ACQUISITION ---")
        if not target:
            target_full = input("[Full Target Name]: ").strip()
        else:
            target_full = target

        if not target_full: return
        
        target_id = target_full.replace(" ", "_")
        parts = target_full.split()
        
        try:
            self.setup_proxy_env()
            
            profiles_root = Path(self.config.get("profiles_root", str(BASE_DIR.parent / "Smotrityel" / "Profiles")))
            target_profile_dir = profiles_root / target_id
            target_raw_dir = target_profile_dir / "Raw"
            target_log_dir = target_profile_dir / "Logs"
            
            os.makedirs(target_raw_dir, exist_ok=True)
            os.makedirs(target_log_dir, exist_ok=True)
            
            # 2. Manage Granular Profile JSON
            profile_file = target_profile_dir / f"{target_id}.json"
            vars_dict = self.generate_name_variations(target_full)
            
            if profile_file.exists():
                with open(profile_file, 'r', encoding='utf-8') as f:
                    profile_data = json.load(f)
                profile_data["identity"]["name_variations"] = vars_dict # Update variations
            else:
                profile_data = {
                    "identity": {
                        "full_name": target_full,
                        "first_name": parts[0],
                        "middle_name": " ".join(parts[1:-1]) if len(parts) > 2 else "",
                        "last_name": parts[-1] if len(parts) > 1 else "",
                        "name_variations": vars_dict
                    },
                    "aliases": {
                        "usernames": [],
                        "emails": [],
                        "phones": [],
                        "addresses": []
                    },
                    "metadata": {
                        "target_id": target_id,
                        "created_at": datetime.now().isoformat()
                    }
                }

            if aliases:
                raw_nodes = [a.strip() for a in aliases.split(",") if a.strip()]
                for node in raw_nodes:
                    if "@" in node:
                        if node not in profile_data["aliases"]["emails"]:
                            profile_data["aliases"]["emails"].append(node)
                    elif any(c.isdigit() for c in node) and len([c for c in node if c.isdigit()]) >= 7:
                        if node not in profile_data["aliases"]["phones"]:
                            profile_data["aliases"]["phones"].append(node)
                    else:
                        if node not in profile_data["aliases"]["usernames"]:
                            profile_data["aliases"]["usernames"].append(node)
            
            with open(profile_file, 'w', encoding='utf-8') as f:
                json.dump(profile_data, f, indent=4)

            print(f"\n[+] Profile Anchored: {target_id}")
            
            # Collate all searchable strings for social engines
            search_list = sorted(list(set(vars_dict["social"] + profile_data["aliases"]["usernames"] + profile_data["aliases"]["emails"])))
            legal_list = vars_dict["legal"]
            
            print(f"[*] Social Search Nodes: {len(search_list)}")
            print(f"[*] Legal Search Nodes: {len(legal_list)}")
            
            current_env = os.environ.copy()
            current_env["PYTHONIOENCODING"] = "utf-8"
            
            legal_tool_names = ["judyrecords", "court_scraper", "florida_doc", "alachua_clerk", "multi_county"]

            for tool_name, rel_path in self.config["tools"].items():
                if enabled_tools is not None and tool_name not in enabled_tools:
                    continue

                script_path = self.toolchain / rel_path
                if not script_path.exists() and not shutil.which(rel_path):
                    continue

                print(f"  > Running {tool_name}...")
                log_file = target_log_dir / f"{tool_name}.log"
                extra_args = self.get_tool_args(tool_name)
                
                cmd_base = [sys.executable]
                cwd = script_path.parent
                
                # Multi-target tools (Sherlock / Maigret)
                if tool_name in ["sherlock", "maigret"]:
                    targets = search_list if tool_name == "maigret" else profile_data["aliases"]["usernames"]
                    if not targets: continue
                    cmd = cmd_base + ["-m", tool_name if tool_name == "maigret" else "sherlock_project"] + targets + extra_args
                    cwd = script_path.parents[1]
                    with open(log_file, "a", encoding="utf-8") as lf:
                        lf.write(f"\n--- EXECUTION: {datetime.now()} ---\n")
                        subprocess.run(cmd, stdout=lf, stderr=lf, cwd=cwd, env=current_env)
                
                # Specialized Target tools
                else:
                    active_nodes = []
                    if tool_name in legal_tool_names: active_nodes = legal_list
                    elif tool_name in ["holehe", "ghunt"]: active_nodes = profile_data["aliases"]["emails"]
                    elif tool_name == "phoneinfoga": active_nodes = profile_data["aliases"]["phones"]
                    else: active_nodes = search_list

                    for node in active_nodes:
                        # CREATE A NEW COPY of cmd_base for every node
                        cmd = list(cmd_base) 
                        if tool_name == "holehe": cmd += ["-m", "holehe.core", node, "--only-used"]
                        elif tool_name == "blackbird":
                            flag = "--email" if "@" in node else "--username"
                            cmd += [str(script_path), flag, node, "--json"]
                        elif tool_name in ["florida_doc", "alachua_clerk"]:
                            n_parts = node.split()
                            f_part = n_parts[0]
                            l_part = n_parts[-1] if len(n_parts) > 1 else ""
                            cmd += [str(script_path), f_part, l_part]
                        else: cmd += [str(script_path), node]
                        
                        cmd += extra_args
                        with open(log_file, "a", encoding="utf-8") as lf:
                            lf.write(f"\n--- NODE: {node} | {datetime.now()} ---\n")
                            subprocess.run(cmd, stdout=lf, stderr=lf, cwd=cwd, env=current_env)
                    
            print(f"\n[SUCCESS] Hunt complete. Data staged at: {target_raw_dir}")

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
