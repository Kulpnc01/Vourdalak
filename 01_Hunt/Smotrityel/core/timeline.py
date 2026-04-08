import os
import json
import ijson
import bisect
from datetime import datetime, timezone

def parse_iso_time(time_val):
    """Resilient parser for 2008-2026 timestamps including raw Unix and ISO."""
    if not time_val: return None
    if isinstance(time_val, (int, float)): return float(time_val)
    if str(time_val).isdigit(): return float(time_val)
    
    try:
        # Standardize for Google, FB, and Snapchat formats
        clean_str = str(time_val).replace(' UTC', '').replace('Z', '+00:00').replace(' ', 'T')
        return datetime.fromisoformat(clean_str).timestamp()
    except: return None

def build_index(storage_dir, temp_dir):
    timeline_data = []
    print(f" -> Executing deep-scan for Master Spatial Index...")

    search_dirs = [storage_dir, temp_dir]
    for d in search_dirs:
        if not os.path.exists(d): continue
        for root, _, files in os.walk(d):
            for file in files:
                path = os.path.join(root, file)
                
                # 1. FUZZY GOOGLE SEARCH (Handles Records, Location History, and Semantic)
                if file.endswith('.json') and any(x in file.lower() for x in ['location', 'history', 'records', 'timeline', 'semantic']):
                    print(f"   [SCAN] Processing Google/Spatial: {file}")
                    with open(path, 'rb') as f:
                        try:
                            # Try standard Google 'locations' array
                            for loc in ijson.items(f, 'locations.item'):
                                ts = parse_iso_time(loc.get('timestamp'))
                                if ts:
                                    lat = loc.get('latitudeE7', 0) / 1e7 if 'latitudeE7' in loc else loc.get('latitude', 0)
                                    lon = loc.get('longitudeE7', 0) / 1e7 if 'longitudeE7' in loc else loc.get('longitude', 0)
                                    timeline_data.append([ts, lat, lon, loc.get('accuracy', 25)])
                            
                            f.seek(0)
                            # Try Semantic Segments / timeline.json
                            for seg in ijson.items(f, 'semanticSegments.item'):
                                if 'timelinePath' in seg:
                                    for pt in seg['timelinePath']:
                                        ts = parse_iso_time(pt.get('time'))
                                        if ts and 'point' in pt:
                                            coords = pt['point'].replace('°','').replace(' ','')
                                            lat, lon = coords.split(',')
                                            timeline_data.append([ts, float(lat), float(lon), 15])
                        except: continue

                # 2. SOURCE-AGNOSTIC SOCIAL & SAMSUNG HARVESTER
                elif file.endswith('.json'):
                    with open(path, 'r', encoding='utf-8') as f:
                        try:
                            data = json.load(f)
                            
                            # A. Facebook Pattern
                            if isinstance(data, dict) and 'location_history' in data:
                                for entry in data['location_history']:
                                    ts, coord = entry.get('timestamp'), entry.get('coordinate', {})
                                    if ts and 'latitude' in coord:
                                        timeline_data.append([ts, coord['latitude'], coord['longitude'], 500])
                            
                            # B. Snapchat / Generic List Pattern
                            elif isinstance(data, list):
                                for entry in data:
                                    lat = entry.get('Latitude') or entry.get('lat')
                                    lon = entry.get('Longitude') or entry.get('lon')
                                    ts = parse_iso_time(entry.get('Time') or entry.get('timestamp'))
                                    if lat and ts:
                                        timeline_data.append([ts, float(lat), float(lon), 100])

                            # C. Samsung Exercise Pattern
                            elif isinstance(data, dict) and 'location_data' in data:
                                for pt in data['location_data']:
                                    timeline_data.append([pt['timestamp']/1000.0, pt['latitude'], pt['longitude'], 15])
                        except: continue

    timeline_data.sort(key=lambda x: x[0])
    
    # Verification Output
    if timeline_data:
        start_date = datetime.fromtimestamp(timeline_data[0][0], tz=timezone.utc).strftime('%Y-%m-%d')
        end_date = datetime.fromtimestamp(timeline_data[-1][0], tz=timezone.utc).strftime('%Y-%m-%d')
        print(f" [SUCCESS] Master Spatial Index spans: {start_date} to {end_date}")
        
    return timeline_data

def export_lean_records(timeline_data, output_dir):
    """Saves the Master Spatial Index for your permanent context."""
    path = os.path.join(output_dir, "Processed_Context")
    os.makedirs(path, exist_ok=True)
    with open(os.path.join(path, "master_spatial_index.jsonl"), 'w', encoding='utf-8') as f:
        for e in timeline_data:
            f.write(json.dumps({"ts": e[0], "lat": e[1], "lon": e[2], "acc": e[3]}) + '\n')

def get_closest_coordinate(timeline_data, target_unix_time, max_delta_seconds=86400):
    """Binary search for spatial anchoring."""
    if not timeline_data: return None
    timestamps = [row[0] for row in timeline_data]
    idx = bisect.bisect_left(timestamps, target_unix_time)
    if idx == 0: closest = timeline_data[0]
    elif idx == len(timeline_data): closest = timeline_data[-1]
    else:
        before, after = timeline_data[idx - 1], timeline_data[idx]
        closest = before if (target_unix_time - before[0]) < (after[0] - target_unix_time) else after
    if abs(closest[0] - target_unix_time) > max_delta_seconds: return None
    return closest