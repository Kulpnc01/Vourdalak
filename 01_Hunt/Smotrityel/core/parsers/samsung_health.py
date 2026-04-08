import os
import csv
from datetime import datetime, timezone

def parse(extract_dir):
    """
    Scans for Samsung Health CSVs (com.samsung.health.heart_rate, etc.)
    and yields standardized physiological tuples.
    """
    for root, _, files in os.walk(extract_dir):
        for file in files:
            # We target the core biometric CSVs
            if not file.endswith('.csv'): continue
            
            metric_type = None
            if 'heart_rate' in file: metric_type = 'heart_rate_bpm'
            elif 'step_count' in file: metric_type = 'step_count'
            elif 'oxygen_saturation' in file: metric_type = 'spo2'
            
            if not metric_type: continue

            file_path = os.path.join(root, file)
            with open(file_path, 'r', encoding='utf-8') as f:
                # Samsung CSVs often have metadata headers; we skip to the actual data
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        # Samsung uses 'start_time' or 'create_time' in UTC
                        raw_ts = row.get('start_time') or row.get('create_time')
                        if not raw_ts: continue
                        
                        dt = datetime.strptime(raw_ts, "%Y-%m-%d %H:%M:%S.%f").replace(tzinfo=timezone.utc)
                        val = float(row.get('heart_rate') or row.get('count') or row.get('spo2'))
                        
                        yield (dt.timestamp(), metric_type, val)
                    except (ValueError, TypeError, KeyError):
                        continue