import argparse
import json
import os
import sys
import subprocess
import shutil
import uuid
import zipfile
from datetime import datetime, timezone

from core import filter, health, timeline, db
from core.parsers import (
    facebook, gemini, gmail, phone, snapchat, whatsapp, chatgpt, copilot, okhotnik, florida_clerk_html, discovery_pdf
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
    media_output = os.path.join(args_output, "media")

    # 0. INIT DATABASE
    db_path = os.path.join(args_output, "behavioral_context.db")
    os.makedirs(args_output, exist_ok=True)
    os.makedirs(media_output, exist_ok=True)
    engine_db = db.DatabaseManager(db_path)

    # Ensure folders exist
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
    
    # Save raw indices to DB for persistence
    for e in t_index: engine_db.save_spatial(e[0], e[1], e[2], e[3])
    for e in h_index: engine_db.save_biometric(e[0], e[1], e[2])

    print(f" [DATA] Timeline Index: {len(t_index)} points loaded.")
    print(f" [DATA] Health Index: {len(h_index)} metrics loaded.")

    # 3. WEAVING
    print(f"\n--- Phase 2: Weaving Behavioral Context ---")
    parsers = [
        (facebook.parse, "facebook"), (snapchat.parse, "snapchat"),
        (gmail.parse, "gmail"), (gemini.parse, "gemini"),
        (phone.parse, "phone"), (whatsapp.parse, "whatsapp"),
        (chatgpt.parse, "chatgpt"), (copilot.parse, "copilot"),
        (okhotnik.parse, "okhotnik"), (florida_clerk_html.parse, "clerk_html"),
        (discovery_pdf.parse, "discovery_docs")
    ]
    
    total_processed = 0
    total_filtered = 0
    new_identifiers_found = False

    for parse_func, name in parsers:
        if name in ["okhotnik", "clerk_html", "discovery_docs"]:
            targets = [args_input]
        else:
            p_dir = os.path.join(args_input, name)
            targets = [d for d in [temp_dir, p_dir] if os.path.exists(d)]
        
        parser_count = 0
        for d in targets:
            for msg in parse_func(d):
                event_id = str(uuid.uuid4())
                
                # Context Lookup (Forensic Anchor)
                f_coord = timeline.get_closest_coordinate(t_index, msg['timestamp'], max_delta_seconds=60)
                f_phys = health.get_closest_health_metrics(h_index, msg['timestamp'], max_delta_seconds=60)
                g_coord = timeline.get_closest_coordinate(t_index, msg['timestamp'], max_delta_seconds=3600)
                
                lat, lon = (f_coord[1], f_coord[2]) if f_coord else ((g_coord[1], g_coord[2]) if g_coord else (None, None))
                
                spatial_delta = None
                if f_coord: spatial_delta = abs(f_coord[0] - msg['timestamp'])
                elif g_coord: spatial_delta = abs(g_coord[0] - msg['timestamp'])

                hr_data = f_phys.get('heart_rate') or f_phys.get('heart_rate.heart_rate')
                hr_val = None
                biometric_delta = None
                if hr_data and isinstance(hr_data, dict):
                    hr_val = hr_data.get('value')
                    biometric_delta = abs(hr_data.get('timestamp') - msg['timestamp'])
                elif hr_data: # Fallback
                    hr_val = hr_data

                state = get_behavioral_state(hr_val)

                # Filter Logic
                score, is_val, category = filter.evaluate_psych_signal(
                    msg['content'], msg['sender'], config, subject['identifiers']
                )
                
                # UNIFIED SAVE (Even if filtered from Markdown, save to DB)
                engine_db.save_event({
                    "id": event_id,
                    "timestamp": msg['timestamp'],
                    "platform": msg['platform'],
                    "sender": msg['sender'],
                    "content": msg['content'],
                    "type": msg.get('type', 'event'),
                    "psych_score": score,
                    "category": category,
                    "lat": lat,
                    "lon": lon,
                    "spatial_delta": spatial_delta,
                    "heart_rate": hr_val,
                    "biometric_delta": biometric_delta
                })

                # Media Extraction Logic
                for m in msg.get('media', []):
                    found_path = None
                    m_uri = m['uri'].replace('/', os.sep).replace('\\', os.sep)
                    
                    for root, dirs, files in os.walk(temp_dir):
                        test_path = os.path.join(root, m_uri)
                        if os.path.exists(test_path):
                            found_path = test_path
                            break
                    
                    if found_path:
                        m_id = str(uuid.uuid4())
                        ext = os.path.splitext(found_path)[1]
                        new_file_name = f"{m_id}{ext}"
                        new_path = os.path.join(media_output, new_file_name)
                        try:
                            shutil.copy2(found_path, new_path)
                            engine_db.save_media({
                                "id": m_id,
                                "event_id": event_id,
                                "timestamp": m['timestamp'],
                                "file_path": os.path.join("media", new_file_name),
                                "original_path": found_path,
                                "metadata": m.get('metadata', {})
                            })
                        except: pass

                if not is_val:
                    total_filtered += 1
                    continue
                
                # Identity Discovery
                is_subject = any(ident.lower() in msg['sender'].lower() for ident in subject['identifiers'])
                if is_subject and msg['sender'] not in subject['identifiers']:
                    subject['identifiers'].append(msg['sender'])
                    new_identifiers_found = True
                    print(f" [DISCOVERY] New identifier for {subject['target_name']}: {msg['sender']}")

                import re
                msg['psych_score'] = score
                safe_platform = re.sub(r'[\\/*?:"<>|]', "", msg['platform']).replace(" ", "_")
                platform_folder = os.path.join(args_output, safe_platform)
                os.makedirs(platform_folder, exist_ok=True)

                # Markdown Export
                ts_str = datetime.fromtimestamp(msg['timestamp'], tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
                safe_s = "".join(c for c in msg['sender'] if c.isalnum() or c in (' ', '_'))[:50].strip()
                safe_platform_file = re.sub(r'[\\/*?:"<>|]', "_", msg['platform'])
                f_name = f"{safe_platform_file}_{safe_s}_{int(msg['timestamp'])}_{uuid.uuid4().hex[:6]}.md"
                
                with open(os.path.join(platform_folder, f_name), 'w', encoding='utf-8') as f:
                    f.write("---\n")
                    f.write(f"id: {event_id}\n")
                    f.write(f"platform: {msg['platform']}\n")
                    f.write(f"sender: \"{msg['sender']}\"\n")
                    f.write(f"timestamp: {ts_str}\n")
                    f.write(f"psych_score: {msg['psych_score']:.2f}\n")
                    f.write(f"behavioral_state: {state}\n")
                    f.write(f"location: {{lat: {lat}, lon: {lon}}}\n")
                    
                    if msg.get('media'):
                        f.write("media:\n")
                        for m in msg['media']: f.write(f"  - {m['uri']}\n")
                    
                    f.write(f"---\n\n{msg['content']}")
                
                parser_count += 1
                total_processed += 1
        if parser_count > 0:
            print(f" [PARSER] {name.upper()}: Processed {parser_count} behavioral events.")

    # 4. EXPORT & CLEANUP
    if new_identifiers_found: update_subject_profile(subject)
    engine_db.close()
    
    print(f"\n--- Phase 3: Finalizing ---")
    timeline.export_lean_records(t_index, args_output)
    health.export_health_records(h_index, args_output)
    shutil.rmtree(temp_dir, ignore_errors=True)

    print(f"\n--- Phase 4: Media Analysis ---")
    media_processor_path = os.path.join(os.path.dirname(os.path.dirname(SCRIPT_DIR)), "02_Feed", "media_processor.py")
    if os.path.exists(media_processor_path):
        print(f" [MEDIA] Launching Media Processor from {media_processor_path}...")
        subprocess.run([sys.executable, media_processor_path])
    else:
        print(f" [MEDIA] Media processor not found at {media_processor_path}")

    print(f" [DONE] Database saved. Processed: {total_processed} | Filtered: {total_filtered}")

if __name__ == "__main__":
    main()
