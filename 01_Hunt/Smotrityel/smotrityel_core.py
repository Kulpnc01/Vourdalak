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

    def process_target(self, target_id):
        print(f"\n--- [SMOTRITYEL/EGOWEAVER] WEAVING: {target_id} ---")
        
        # New structure: Profiles/$Target/Raw
        target_profile_dir = self.raw_src / target_id
        target_raw = target_profile_dir / "Raw"
        target_supplied = self.supplied_src / target_id # Fallback for legacy/manual input
        target_output = self.feed_dest / target_id
        os.makedirs(target_output, exist_ok=True)
        
        # Temp extract for supplied ZIPs inside target folder
        temp_extract = target_raw / "_temp_extract"
        os.makedirs(temp_extract, exist_ok=True)
        
        # Extract from both target_raw and target_supplied if they exist
        self.extract_if_needed(target_raw, temp_extract)
        self.extract_if_needed(target_supplied, temp_extract)

        # 1. Subject Profile (Check for both .json formats)
        profile_file = target_profile_dir / f"{target_id}.json"
        if not profile_file.exists():
             profile_file = target_raw / "subject_profile.json"

        if profile_file.exists():
            with open(profile_file, 'r', encoding='utf-8') as f:
                profile_data = json.load(f)
                # Normalize identifiers for EgoWeaver filter
                identifiers = profile_data.get('name_variations', []) + profile_data.get('aliases', []) + profile_data.get('identifiers', [])
                subject = {
                    "target_name": target_id,
                    "identifiers": identifiers,
                    "analysis_mode": "forensic"
                }
        else:
            subject = {
                "target_name": target_id,
                "identifiers": [target_id.lower(), target_id.replace('_', ' ')],
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
