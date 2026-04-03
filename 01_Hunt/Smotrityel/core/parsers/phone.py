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
