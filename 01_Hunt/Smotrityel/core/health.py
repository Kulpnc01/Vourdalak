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
                metrics_at_time[metric] = {"value": value, "timestamp": ts}
                
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
