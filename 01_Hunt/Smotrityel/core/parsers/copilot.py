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