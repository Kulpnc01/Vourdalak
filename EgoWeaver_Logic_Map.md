# PROJECT ARCHITECTURE: EgoWeaver2.0
```text
  .vscode/
    settings.json
  config.example.json
  core/
    __init__.py
    filter.py
    health.py
    parsers/
      __init__.py
      chatgpt.py
      copilot.py
      facebook.py
      gemini.py
      gmail.py
      phone.py
      samsung_health.py
      snapchat.py
      whatsapp.py
    timeline.py
  egoweaver.py
  gui_launcher.py
  Input/
    health/
    timeline/
  README.md
  requirements.txt
  run_eagoweaver.bat
  subject_profile.example.json
```

## FILE: .vscode\settings.json
```json
{
    "python-envs.defaultEnvManager": "ms-python.python:system",
    "python.defaultInterpreterPath": "C:\\HDT\\Nikolai\\venv\\Scripts\\python.exe"
}
```

## FILE: config.example.json
```json
{
    "paths": {
        "input": "Input",
        "output": "output"
    },
    "filter_settings": {
        "min_psych_score": 3.0,
        "vip_senders": [
            "VIP_Contact_1"
        ],
        "safe_keywords": [
            "PROJECT_CODENAME"
        ]
    }
}
```

## FILE: core\__init__.py
```py
"""
EgoWeaver 2.0 Core Engine
Exposes the spatial, physiological, and psychological processing units.
"""

# Import from timeline.py
from .timeline import build_index, get_closest_coordinate, export_lean_records

# Import from health.py 
# We alias this so it doesn't collide with the timeline version
from .health import build_health_index, get_closest_health_metrics, export_health_records 

# Import from filter.py
from .filter import evaluate_psych_signal
```

## FILE: core\filter.py
```py
import json
import os
import re

def evaluate_psych_signal(content, sender, config, subject_identifiers=None):
    """
    Mult-stage behavioral filter.
    1. Aggressive Spam/Newsletter Rejector
    2. Business/Utility Logic (High Priority Records)
    3. Personal Psychological Density (Interaction Logic)
    """
    content_lower = content.lower()
    word_count = len(content_lower.split())
    
    # --- STAGE 1: THE JUNK GUILLOTINE ---
    # Common markers of automated marketing/newsletters
    junk_markers = [
        'unsubscribe', 'view in browser', 'manage preferences', 
        'privacy policy', 'all rights reserved', 'click here to',
        'sent to you because', 'opt out'
    ]
    
    # If it contains multiple junk markers, it's out
    junk_hits = sum(1 for m in junk_markers if m in content_lower)
    if junk_hits >= 2:
        return 0.0, False, "spam"

    # Stage 1b: Domain rejection (if possible to infer from sender)
    if any(x in sender.lower() for x in ['no-reply', 'noreply', 'notifications@', 'marketing']):
        # Still allow it if it's business high-signal (handled in Stage 2)
        pass
    
    # --- STAGE 2: BUSINESS/UTILITY PASS ---
    # High-signal keywords for life-records
    utility_keywords = [
        'receipt', 'confirmation', 'order', 'invoice', 'payment',
        'statement', 'account created', 'security alert', 'login',
        'tracking', 'shipped', 'delivered', 'appointment', 'reservation',
        'subscription', 'banking', 'transaction', 'transfer'
    ]
    
    is_utility = any(u in content_lower for u in utility_keywords)
    if is_utility and word_count > 5:
        # High score for utility records, they are forensics gold
        return 8.0, True, "utility"

    # --- STAGE 3: PERSONAL PSYCHOLOGICAL DENSITY ---
    # Noise floor
    if word_count < 4: return 0.0, False, "noise"

    score = 0.0
    
    # Introspection and Emotional Weight
    introspection = ['i', 'me', 'my', 'mine', 'myself']
    emotional = ['feel', 'think', 'want', 'hope', 'wish', 'believe', 'love', 'hate', 'miss', 'sorry']
    
    # Identity Bonus (Is the subject talking?)
    if subject_identifiers:
        for ident in subject_identifiers:
            if ident.lower() in sender.lower():
                score += 3.0 # Heavy weight for self-authored content
                break

    score += sum(1.5 for w in content_lower.split() if w in introspection)
    score += sum(2.0 for w in content_lower.split() if w in emotional)
    
    # Length Bonuses
    if word_count > 12: score += 1.0
    if word_count > 30: score += 2.0

    min_score = config.get("filter_settings", {}).get("min_psych_score", 3.0)
    
    # Final check
    is_valid = score >= min_score
    return score, is_valid, "personal"

```

## FILE: core\health.py
```py
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
                metrics_at_time[metric] = value
                
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

```

## FILE: core\parsers\__init__.py
```py
"""
EgoWeaver 2.0 Parsers Package
Registers all modular data adapters for the orchestrator.
"""

from . import facebook
from . import gmail
from . import snapchat
from . import phone
from . import gemini
from . import whatsapp
from . import chatgpt
from . import copilot
from . import samsung_health
```

## FILE: core\parsers\chatgpt.py
```py
import os
import json

def parse(extract_dir):
    """
    Scans for OpenAI's conversations.json export and yields standardized dictionaries.
    Flattens the complex node-based conversation tree into discrete chronological messages.
    Expected output: {"platform": str, "timestamp": float, "sender": str, "content": str, "type": str}
    """
    for root, _, files in os.walk(extract_dir):
        for file in files:
            # OpenAI exports all chat history in a single conversations.json file
            if file == 'conversations.json':
                file_path = os.path.join(root, file)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                except (json.JSONDecodeError, FileNotFoundError):
                    continue
                    
                for conversation in data:
                    # The mapping dictionary contains all the message nodes
                    mapping = conversation.get('mapping', {})
                    
                    for node_id, node in mapping.items():
                        message = node.get('message')
                        
                        # Some nodes are empty roots or system branches; skip them
                        if not message:
                            continue
                            
                        # Extract the author to distinguish your prompts from the AI's replies
                        author = message.get('author', {})
                        role = author.get('role')
                        
                        # We generally only want 'user' (you) or 'assistant' (ChatGPT)
                        if role not in ['user', 'assistant']:
                            continue
                            
                        # OpenAI uses standard Unix timestamps (float/int in seconds) natively
                        timestamp = message.get('create_time')
                        if not timestamp:
                            continue
                            
                        # Extract the actual text content
                        content_dict = message.get('content', {})
                        content_type = content_dict.get('content_type')
                        
                        # Ensure we are only pulling text (ignoring DALL-E image generation nodes or code execution outputs)
                        if content_type != 'text':
                            continue
                            
                        parts = content_dict.get('parts', [])
                        # Combine the parts (usually just one string, but can be multiple)
                        content = "".join([str(p) for p in parts if p]).strip()
                        
                        if not content:
                            continue
                            
                        yield {
                            "platform": "ChatGPT",
                            "timestamp": float(timestamp),
                            "sender": "Self" if role == 'user' else "ChatGPT", 
                            "content": content,
                            "type": "ai_interaction"
                        }
```

## FILE: core\parsers\copilot.py
```py
import os
import json
from datetime import datetime, timezone

def parse(extract_dir):
    """
    Scans for Microsoft Copilot / Bing Chat activity in MS Privacy exports.
    Yields standardized dictionaries for the EgoWeaver pipeline.
    Expected output: {"platform": str, "timestamp": float, "sender": str, "content": str, "type": str}
    """
    for root, _, files in os.walk(extract_dir):
        for file in files:
            # Microsoft often bundles this inside 'Search' or 'Bing' export folders
            if file.endswith('.json') and any(keyword in root for keyword in ['Copilot', 'Bing', 'Search']):
                file_path = os.path.join(root, file)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                except (json.JSONDecodeError, FileNotFoundError):
                    continue
                    
                # MS Privacy exports usually nest data heavily. 
                # This flattens the structure to find the actual activity list.
                activities = []
                if isinstance(data, dict):
                    if 'ActivityTypes' in data:
                        for at in data['ActivityTypes']:
                            activities.extend(at.get('Activities', []))
                    elif 'Activities' in data:
                        activities.extend(data['Activities'])
                elif isinstance(data, list):
                    activities = data
                    
                for item in activities:
                    try:
                        # Microsoft typically uses 'DateTime' with standard ISO formatting
                        time_str = item.get('DateTime') or item.get('time')
                        if not time_str:
                            continue
                            
                        # Convert to standard Unix time
                        time_str = time_str.replace('Z', '+00:00')
                        dt = datetime.fromisoformat(time_str)
                        
                        # Microsoft changes its keys frequently; check all likely prompt locations
                        content = item.get('SearchTerms') or item.get('Prompt') or item.get('Text') or item.get('QueryText')
                        
                        if not content:
                            continue
                            
                        yield {
                            "platform": "Copilot",
                            "timestamp": dt.timestamp(),
                            "sender": "Self", 
                            "content": content.strip(),
                            "type": "ai_interaction"
                        }
                        
                    except (ValueError, AttributeError):
                        continue
```

## FILE: core\parsers\facebook.py
```py
import os
import json
from datetime import datetime, timezone

def fix_text(text):
    if not text: return ""
    try:
        return text.encode('latin1').decode('utf-8', 'ignore')
    except (UnicodeEncodeError, UnicodeDecodeError):
        return text

def parse(extract_dir):
    for root, _, files in os.walk(extract_dir):
        for file in files:
            # FIX: Process ALL message files, not just message_1
            if file.startswith('message_') and file.endswith('.json') and ('inbox' in root or 'e2ee_cutover' in root):
                file_path = os.path.join(root, file)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                except (json.JSONDecodeError, FileNotFoundError):
                    continue

                participants = [fix_text(p.get('name', 'Unknown')) for p in data.get('participants', [])]
                thread_name = " and ".join(participants) if participants else "Unknown Thread"

                daily_chats = {}
                for msg in data.get('messages', []):
                    if 'content' not in msg:
                        continue
                        
                    ts = msg.get('timestamp_ms', 0) / 1000.0
                    date_str = datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d")
                    
                    sender = fix_text(msg.get('sender_name', 'Unknown'))
                    content = fix_text(msg.get('content', ''))
                    
                    if date_str not in daily_chats:
                        daily_chats[date_str] = {"timestamp": ts, "messages": []}
                    daily_chats[date_str]['messages'].append(f"[{sender}]: {content}")
                    
                for date_str, chat_data in daily_chats.items():
                    chat_data['messages'].reverse() 
                    joined_transcript = "\n".join(chat_data['messages'])
                    
                    yield {
                        "platform": "Facebook",
                        "timestamp": chat_data['timestamp'],
                        "sender": thread_name, 
                        "content": joined_transcript,
                        "type": "message"
                    }
```

## FILE: core\parsers\gemini.py
```py
import os
import json
import re
from datetime import datetime, timezone

def clean_html(raw_html):
    """Fallback: Strips HTML tags if no plain text part exists."""
    cleanr = re.compile('<.*?>')
    # Replace common HTML entities
    text = re.sub(cleanr, '', raw_html)
    text = text.replace('&quot;', '"').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
    text = text.replace('&#39;', "'").replace('&nbsp;', ' ')
    return text.strip()

def parse_html_activity(file_path):
    """
    Parses Google Takeout's MyActivity.html for Gemini/Bard activity.
    """
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
        # Each activity is inside an outer-cell mdl-cell
        # We look for Gemini Apps specifically
        items = content.split('<div class="outer-cell')
        for item in items:
            if 'Gemini Apps' not in item: continue
            
            # Extract Prompted text
            # Format: <div ...>Prompted鑱絎hy can&#39;t 8 build a solid wheel<br>
            prompt_match = re.search(r'Prompted.*?鑱(.*?)<br>', item, re.DOTALL)
            if not prompt_match: continue
            prompt = clean_html(prompt_match.group(1))
            
            # Extract Date
            # Format: Mar 1, 2026, 2:08:28閳ョ枿M EST<br>
            # Note: 閳ョ枿M seems to be an encoding issue for PM
            date_match = re.search(r'<br>(.*?)閳.*?EST<br>', item)
            if not date_match: 
                # Try a more generic date match
                date_match = re.search(r'<br>([A-Z][a-z]{2} \d+, \d{4}, \d+:\d+:\d+.*?)<br>', item)
            
            if not date_match: continue
            date_str = date_match.group(1).strip()
            # Clean up the weird characters
            date_str = re.sub(r'閳.*', ' PM', date_str) if '閳' in date_str else date_str
            
            try:
                # Example: Mar 1, 2026, 2:08:28 PM
                dt = datetime.strptime(date_str, '%b %d, %l:%M:%S %p') # This is hard because of missing year or different formats
                # Actually, let's use a more flexible parser if possible, but we don't have many libs.
                # Let's try to extract year, month, day, time
                parts = re.search(r'([A-Z][a-z]{2}) (\d+), (\d{4}), (\d+:\d+:\d+)', date_str)
                if parts:
                    m, d, y, t = parts.groups()
                    dt_str = f"{m} {d} {y} {t}"
                    dt = datetime.strptime(dt_str, '%b %d %Y %H:%M:%S').replace(tzinfo=timezone.utc)
                    ts = dt.timestamp()
                else: continue
            except: continue
            
            # Extract Response
            # The response is usually in <p> tags after the date
            response_match = re.search(r'EST<br>(.*?)<div class="content-cell', item, re.DOTALL)
            if not response_match: continue
            response = clean_html(response_match.group(1))
            
            if prompt:
                yield {
                    "platform": "Gemini",
                    "timestamp": ts,
                    "sender": "Self",
                    "content": prompt,
                    "type": "ai_interaction"
                }
            if response:
                yield {
                    "platform": "Gemini",
                    "timestamp": ts + 1, # Offset response by 1s
                    "sender": "Gemini",
                    "content": response,
                    "type": "ai_interaction"
                }
    except Exception: pass

def parse(extract_dir):
    """
    Scans for Gemini (or Bard) My Activity exports (JSON or HTML).
    """
    for root, _, files in os.walk(extract_dir):
        for file in files:
            file_path = os.path.join(root, file)
            
            # --- 1. HTML HANDLING ---
            if file == 'MyActivity.html' and ('Gemini' in root or 'Bard' in root):
                yield from parse_html_activity(file_path)
                
            # --- 2. JSON HANDLING ---
            elif file == 'My Activity.json' and ('Gemini' in root or 'Bard' in root):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        
                    for entry in data:
                        # Standard Google Activity structure
                        title = entry.get('title', '')
                        if 'Prompted' not in title and 'Searched for' not in title: continue
                        
                        content = entry.get('titleValue', '') or title.replace('Prompted ', '')
                        timestamp = entry.get('time')
                        
                        try:
                            # 2024-03-15T10:00:00Z or similar
                            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                            ts = dt.timestamp()
                        except (ValueError, AttributeError):
                            continue
                            
                        yield {
                            "platform": "Gemini",
                            "timestamp": ts,
                            "sender": "Self", 
                            "content": content,
                            "type": "ai_interaction"
                        }
                        
                except (json.JSONDecodeError, FileNotFoundError):
                    continue

```

## FILE: core\parsers\gmail.py
```py
import os
import mailbox
import re
from email.utils import parsedate_to_datetime
from datetime import datetime, timezone

def clean_html(raw_html):
    """Fallback: Strips HTML tags if no plain text part exists."""
    cleanr = re.compile('<.*?>')
    return re.sub(cleanr, '', raw_html).strip()

def get_text_body(msg):
    """Digs for plain text, falls back to stripped HTML."""
    text_content = ""
    html_content = ""
    
    if msg.is_multipart():
        for part in msg.walk():
            ctype = part.get_content_type()
            cdispo = str(part.get("Content-Disposition"))
            if "attachment" in cdispo: continue
            
            try:
                if ctype == "text/plain":
                    text_content += part.get_payload(decode=True).decode('utf-8', errors='ignore')
                elif ctype == "text/html":
                    html_content += part.get_payload(decode=True).decode('utf-8', errors='ignore')
            except Exception: continue
    else:
        try:
            if msg.get_content_type() == "text/plain":
                text_content = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
            elif msg.get_content_type() == "text/html":
                html_content = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
        except Exception: pass
        
    if text_content.strip(): return text_content.strip()
    if html_content.strip(): return clean_html(html_content)
    return ""

def parse_md_export(file_path):
    """
    Parses a combined .mbox.md file which contains emails separated by '---'.
    """
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
        # Split by the separator used in the file
        parts = content.split('\n---\n')
        for part in parts:
            if not part.strip(): continue
            
            # Extract Subject, From, Date using regex
            subject_match = re.search(r'### Subject: (.*)', part)
            from_match = re.search(r'\*\*From:\*\* (.*)', part)
            date_match = re.search(r'\*\*Date:\*\* (.*)', part)
            
            if not (subject_match and from_match and date_match): continue
            
            subject = subject_match.group(1).strip()
            sender = from_match.group(1).strip()
            date_str = date_match.group(1).strip()
            
            # The body is everything after the Date line
            body_start = date_match.end()
            body = part[body_start:].strip()
            
            try:
                # Try to parse the date
                # Example: Fri, 27 Feb 2026 20:24:21 +0000
                dt = parsedate_to_datetime(date_str)
                ts = dt.timestamp()
            except: continue
            
            yield {
                "platform": "Gmail",
                "timestamp": ts,
                "sender": sender,
                "content": f"Subject: {subject}\n\n{body}",
                "type": "message"
            }
    except Exception: pass

def parse(extract_dir):
    for root, _, files in os.walk(extract_dir):
        for file in files:
            file_path = os.path.join(root, file)
            
            if file.lower().endswith('.mbox.md'):
                yield from parse_md_export(file_path)
                
            elif file.lower().endswith('.mbox'):
                try:
                    mb = mailbox.mbox(file_path)
                    for message in mb:
                        date_str = message['date']
                        if not date_str: continue
                        
                        try:
                            ts = parsedate_to_datetime(date_str).timestamp()
                        except Exception: continue
                            
                        content = get_text_body(message)
                        if not content: continue
                            
                        yield {
                            "platform": "Gmail",
                            "timestamp": ts,
                            "sender": message['from'] or "Unknown Sender",
                            "content": content,
                            "type": "message"
                        }
                except Exception:
                    pass

```

## FILE: core\parsers\phone.py
```py
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

```

## FILE: core\parsers\samsung_health.py
```py
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
```

## FILE: core\parsers\snapchat.py
```py
import os
import json
from datetime import datetime, timezone

def parse(extract_dir):
    """Hunts for chat_history.json recursively to avoid zip-folder nesting issues."""
    for root, _, files in os.walk(extract_dir):
        if 'chat_history.json' in files:
            file_path = os.path.join(root, 'chat_history.json')
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                continue

            daily_chats = {}

            # Handle New Format: Dictionary of usernames/threads
            old_categories = ['Received Saved Chat History', 'Sent Saved Chat History']
            is_new_format = isinstance(data, dict) and not any(k in data for k in old_categories)

            if is_new_format:
                for thread_name, messages in data.items():
                    if not isinstance(messages, list): continue
                    for msg in messages:
                        content = msg.get('Content') or msg.get('Text') or ""
                        media_type = msg.get('Media Type', 'TEXT')
                        if not content and media_type != 'TEXT': content = f"[{media_type}]"
                        if not content: continue

                        try:
                            clean_time = msg.get('Created', '').replace(' UTC', '')
                            dt = datetime.strptime(clean_time, '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc)
                            ts = dt.timestamp()
                            date_str = dt.strftime("%Y-%m-%d")
                        except: continue

                        sender = msg.get('From', thread_name)
                        if date_str not in daily_chats:
                            daily_chats[date_str] = {"messages": []}
                        daily_chats[date_str]['messages'].append({
                            "ts": ts, 
                            "sender_raw": sender, 
                            "text_only": content
                        })

            # Handle Old Format: Category-based
            else:
                for category in old_categories:
                    for msg in data.get(category, []):
                        content = msg.get('Text') or msg.get('Content') or ""
                        media_type = msg.get('Media Type', 'TEXT')
                        if not content and media_type != 'TEXT': content = f"[{media_type}]"
                        if not content: continue

                        try:
                            clean_time = msg.get('Created', '').replace(' UTC', '')
                            dt = datetime.strptime(clean_time, '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc)
                            ts = dt.timestamp()
                            date_str = dt.strftime("%Y-%m-%d")
                        except: continue

                        sender = msg.get('From', 'Unknown')
                        if date_str not in daily_chats:
                            daily_chats[date_str] = {"messages": []}
                        daily_chats[date_str]['messages'].append({
                            "ts": ts, 
                            "sender_raw": sender, 
                            "text_only": content
                        })

            # Yield individual messages for better anchoring and discovery
            for date_str in sorted(daily_chats.keys()):
                for msg_item in daily_chats[date_str]['messages']:
                    yield {
                        "platform": "Snapchat",
                        "timestamp": msg_item['ts'],
                        "sender": msg_item['sender_raw'],
                        "content": msg_item['text_only'],
                        "type": "message"
                    }

```

## FILE: core\parsers\whatsapp.py
```py
import os
import re
from datetime import datetime, timezone

def parse(extract_dir):
    """
    Scans for WhatsApp .txt exports and yields standardized dictionaries.
    Handles both Android and iOS timestamp formatting, as well as multi-line messages.
    """
    # Android format: "12/31/23, 11:59 PM - Sender Name: Message"
    android_pattern = re.compile(r'^(\d{1,2}/\d{1,2}/\d{2,4}, \d{1,2}:\d{2}\s?[APM]{2}) - ([^:]+): (.*)$', re.IGNORECASE)
    
    # iOS format: "[12/31/23, 11:59:00 PM] Sender Name: Message"
    ios_pattern = re.compile(r'^\[(\d{1,2}/\d{1,2}/\d{2,4}, \d{1,2}:\d{2}:\d{2}\s?[APM]{2})\] ([^:]+): (.*)$', re.IGNORECASE)

    for root, _, files in os.walk(extract_dir):
        for file in files:
            # WhatsApp chat files usually contain 'WhatsApp' or start with '_chat'
            if file.endswith('.txt') and ('WhatsApp' in file or file.startswith('_chat')):
                file_path = os.path.join(root, file)

                with open(file_path, 'r', encoding='utf-8') as f:
                    current_msg = None

                    for line in f:
                        line = line.strip()
                        if not line:
                            continue

                        # Check which OS generated the export
                        match_android = android_pattern.match(line)
                        match_ios = ios_pattern.match(line)

                        if match_android or match_ios:
                            # If we have a fully built message waiting, yield it to EgoWeaver
                            if current_msg:
                                yield current_msg

                            # Explicit elif satisfies strict type linters in VS Code
                            if match_android:
                                date_str, sender, content = match_android.groups()
                                date_format = "%m/%d/%y, %I:%M %p"
                            elif match_ios:
                                date_str, sender, content = match_ios.groups()
                                date_format = "%m/%d/%y, %I:%M:%S %p"

                            try:
                                # Check if the year is 4 digits (e.g., '2023') instead of 2 digits ('23')
                                year_str = date_str.split(',')[0].split('/')[-1]
                                if len(year_str) == 4:
                                    date_format = date_format.replace('%y', '%Y')

                                # Convert to standard Unix time
                                dt = datetime.strptime(date_str, date_format).replace(tzinfo=timezone.utc)
                            except ValueError:
                                # If the date is completely malformed, skip it
                                current_msg = None
                                continue

                            # Start building the new message
                            current_msg = {
                                "platform": "WhatsApp",
                                "timestamp": dt.timestamp(),
                                "sender": sender.strip(),
                                "content": content.strip(),
                                "type": "message"
                            }
                        else:
                            # If the line doesn't start with a timestamp, it belongs to the previous message
                            if current_msg:
                                current_msg["content"] += f"\n{line}"

                    # Don't forget to yield the very last message in the file once the loop ends
                    if current_msg:
                        yield current_msg
```

## FILE: core\timeline.py
```py
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
```

## FILE: egoweaver.py
```py
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
    
    t_index = timeline.build_index(args_input, temp_dir)
    h_index = health.build_health_index(args_input, temp_dir)
    
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
        # We now scan the entire Input dir recursively for each parser
        targets = [temp_dir, args_input]
        
        parser_count = 0
        for d in targets:
            if not os.path.exists(d): continue
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
                
                # If they ARE a subject but the specific handle isn't in our list yet, learn it.
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
    print(f"\n--- Phase 3: Finalizing & Exporting Master Context ---")
    
    # Generate Master Record for the current Subject
    master_record = {
        "subject_profile": subject,
        "spatial_history": [
            {"ts": e[0], "lat": e[1], "lon": e[2], "acc": e[3]} for e in t_index
        ],
        "physiology_telemetry": [
            {"ts": e[0], "metric": e[1], "val": e[2]} for e in h_index
        ],
        "last_weaving_event": datetime.now(timezone.utc).isoformat()
    }
    
    # Save directly into the root output folder for easy retrieval
    with open(os.path.join(args_output, "subject_master_record.json"), 'w', encoding='utf-8') as f:
        json.dump(master_record, f, indent=4)

    if new_identifiers_found:
        update_subject_profile(subject)
        
    timeline.export_lean_records(t_index, args_output)
    health.export_health_records(h_index, args_output)
    
    shutil.rmtree(temp_dir, ignore_errors=True)
    print(f" [DONE] Processed: {total_processed} | Filtered: {total_filtered}")

if __name__ == "__main__":
    main()

```

## FILE: gui_launcher.py
```py
import sys
import threading
import json
import os
import customtkinter as ctk
from tkinter import filedialog, messagebox
import egoweaver

class EgoWeaverGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("EgoWeaver | Behavioral Context Engine")
        self.geometry("900x650")
        ctk.set_appearance_mode("dark")
        
        # --- State Variables ---
        self.config = egoweaver.load_engine_config()
        self.input_path = ctk.StringVar(value=self.config['paths'].get('input', 'Input'))
        self.output_path = ctk.StringVar(value=self.config['paths'].get('output', 'output'))

        # --- Layout ---
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Sidebar ---
        self.sidebar = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        self.logo = ctk.CTkLabel(self.sidebar, text="EgoWeaver", font=ctk.CTkFont(size=22, weight="bold"))
        self.logo.grid(row=0, column=0, padx=20, pady=20)

        # VIP Editor Section
        self.vip_label = ctk.CTkLabel(self.sidebar, text="VIP Senders (Safe List):", font=ctk.CTkFont(weight="bold"))
        self.vip_label.grid(row=1, column=0, padx=20, pady=(10, 0))
        
        self.vip_listbox = ctk.CTkTextbox(self.sidebar, height=150, width=200)
        self.vip_listbox.grid(row=2, column=0, padx=20, pady=10)
        self.vip_listbox.insert("1.0", "\n".join(self.config['filter_settings'].get('vip_senders', [])))

        self.score_label = ctk.CTkLabel(self.sidebar, text=f"Min Psych Score: {round(self.config['filter_settings']['min_psych_score'], 1)}")
        self.score_label.grid(row=3, column=0, padx=20, pady=(10, 0))
        
        self.score_slider = ctk.CTkSlider(self.sidebar, from_=0, to=10, command=self.update_score_label)
        self.score_slider.set(self.config['filter_settings']['min_psych_score'])
        self.score_slider.grid(row=4, column=0, padx=20, pady=10)

        # --- Main View ---
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        # Path Selection
        self.path_frame = ctk.CTkFrame(self.main_frame)
        self.path_frame.pack(fill="x", pady=10)

        self.in_label = ctk.CTkLabel(self.path_frame, textvariable=self.input_path, wraplength=400)
        self.in_label.pack(side="left", padx=10, pady=10)
        
        self.btn_in = ctk.CTkButton(self.path_frame, text="Browse Input", width=120, command=self.browse_input)
        self.btn_in.pack(side="right", padx=10)

        self.out_frame = ctk.CTkFrame(self.main_frame)
        self.out_frame.pack(fill="x", pady=10)
        
        self.out_label = ctk.CTkLabel(self.out_frame, textvariable=self.output_path)
        self.out_label.pack(side="left", padx=10, pady=10)

        self.btn_out = ctk.CTkButton(self.out_frame, text="Set Output", width=120, command=self.browse_output)
        self.btn_out.pack(side="right", padx=10)

        # Logs
        self.log_box = ctk.CTkTextbox(self.main_frame, height=300)
        self.log_box.pack(fill="both", expand=True, pady=10)

        self.start_btn = ctk.CTkButton(self.main_frame, text="START WEAVING", height=50, fg_color="#2ecc71", hover_color="#27ae60", font=ctk.CTkFont(weight="bold"), command=self.start_thread)
        self.start_btn.pack(fill="x", pady=10)

        sys.stdout = self # Redirect print()

    def update_score_label(self, val):
        self.score_label.configure(text=f"Min Psych Score: {round(val, 1)}")

    def browse_input(self):
        path = filedialog.askdirectory(title="Select folder containing .zip archives or stashed folders")
        if path: self.input_path.set(path)

    def browse_output(self):
        path = filedialog.askdirectory(title="Select where to save MD records")
        if path: self.output_path.set(path)

    def write(self, text):
        self.log_box.insert("end", text)
        self.log_box.see("end")

    def flush(self): pass

    def start_thread(self):
        if self.input_path.get() == "Not Selected":
            messagebox.showwarning("Selection Required", "Please select an input directory first.")
            return
        self.start_btn.configure(state="disabled")
        threading.Thread(target=self.run_weave, daemon=True).start()

    def run_weave(self):
        try:
            # Sync GUI settings to actual config object
            vips = self.vip_listbox.get("1.0", "end-1c").split('\n')
            self.config['filter_settings']['vip_senders'] = [v.strip() for v in vips if v.strip()]
            self.config['filter_settings']['min_psych_score'] = self.score_slider.get()
            self.config['paths']['input'] = self.input_path.get()
            self.config['paths']['output'] = self.output_path.get()
            
            # Save updated config back to file
            with open(egoweaver.CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4)
            
            print(f"\n[GUI] Config Saved. Starting EgoWeaver core...")
            egoweaver.main()
        except Exception as e:
            print(f"\n[CRITICAL ERROR] {e}")
        finally:
            self.start_btn.configure(state="normal")

if __name__ == "__main__":
    app = EgoWeaverGUI()
    app.mainloop()

```

## FILE: README.md
```md
# EgoWeaver 2.0: Behavioral Context Engine

EgoWeaver is a multimodal data orchestration and analysis engine designed to reconstruct digital identity and behavioral context from disparate data exports. By weaving together messaging transcripts, spatial history, and physiological telemetry, EgoWeaver creates a high-fidelity narrative of a subject's digital life.

## Core Capabilities

- **Multimodal Weaving:** Synchronizes data from Facebook, Gmail, Snapchat, WhatsApp, Phone/SMS, Gemini (AI), and more.
- **Contextual Anchoring:** Automatically attaches the closest known GPS coordinates and biometric data (Heart Rate, Steps) to every event.
- **Dual-Layer Forensic Schema:** Output records distinguish between "Forensic Anchors" (tight 60s window) and "General Context" (loose 1h window), providing a `context_confidence` score for each event.
- **Behavioral State Mapping:** Infers physiological states (e.g., ELEVATED, BASELINE) based on biometric deviations at the moment of interaction.
- **Identity Discovery:** Automatically "learns" new handles, emails, and identifiers for a subject during processing, updating the target profile recursively.
- **Psychological Density Filtering:** Uses heuristic scoring to separate high-signal personal and business records from automated noise and spam.

## Target Use Cases

1. **Digital Twin Construction:** Build long-term RAG (Retrieval-Augmented Generation) memory for personalized AI agents using a user's own historical data.
2. **Forensic Behavioral Analysis:** Analyze a target subject's emotional and physical state during specific interactions for behavioral prediction and profile reading.

## Setup & Usage

### 1. Requirements
- Python 3.10+
- Dependencies: `pip install -r requirements.txt`

### 2. Configuration
- Copy `config.example.json` to `config.json` and set your preferred input/output paths.
- Copy `subject_profile.example.json` to `subject_profile.json` and populate the `identifiers` list with known emails or handles of the target subject.

### 3. Execution
- **GUI Mode:** Run `python gui_launcher.py` for a visual control panel.
- **CLI Mode:** Run `python egoweaver.py` (ensure `config.json` is set).

## Data Schema
Each event is exported as a Markdown file with a rich YAML frontmatter:

```yaml
---
platform: Gmail
sender: "Subject_Alpha"
timestamp: 2026-03-01 14:20:05
subject_match: true
psych_score: 8.50
category: personal
context_confidence: 0.9
behavioral_state: ELEVATED
location:
  lat: 40.7128
  lon: -74.0060
  accuracy: 15
physiology:
  heart_rate: 112.0
---
[[Subject_Alpha]]
Content of the message or interaction...
```

## Security & Privacy
EgoWeaver is designed for local execution. No data is sent to external servers during the weaving process. Users are responsible for ensuring they have the legal right to process the data exports provided to the engine.

---
*Developed for Deep Behavioral Analysis and Identity Reconstruction.*

```

## FILE: requirements.txt
```txt
# EgoWeaver 2.0 Dependencies
customtkinter==5.2.2
ijson==3.2.3

# Standard library modules (no install required):
# argparse, json, os, shutil, uuid, zipfile, datetime, mailbox, re, email, xml, csv, bisect, threading

```

## FILE: run_eagoweaver.bat
```bat
@echo off
set "PYTHON_EXE=C:\HDT\Nikolai\venv\Scripts\python.exe"
title EgoWeaver 2.0 Engine
echo [SYSTEM] Initiating Weaving Process...
:: Ensure we are in the script directory
cd /d "%~dp0"
"%PYTHON_EXE%" egoweaver.py
echo.
echo [SYSTEM] Process Complete. Check the 'output' folder for your context records.
pause
```

## FILE: subject_profile.example.json
```json
{
    "target_name": "Subject_Alpha",
    "identifiers": [
        "subject@example.com",
        "subject_handle",
        "+15550000000"
    ],
    "analysis_mode": "forensic"
}
```

