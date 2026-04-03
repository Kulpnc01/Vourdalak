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
