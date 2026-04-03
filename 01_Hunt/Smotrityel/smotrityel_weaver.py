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
