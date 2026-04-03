import os
import re
from datetime import datetime, timezone

def parse(extract_dir):
    """
    Parses Okhotnik OSINT logs (Sherlock, Maigret, etc.)
    Expected format: [+][*] Signal output from CLI tools.
    """
    for root, _, files in os.walk(extract_dir):
        for file in files:
            if file.endswith('.log') or 'User_Supplied' in file:
                file_path = os.path.join(root, file)
                
                try:
                    # Get file modification time as a fallback timestamp
                    mtime = os.path.getmtime(file_path)
                    
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                        
                    for line in lines:
                        line = line.strip()
                        if not line: continue
                        
                        # Sherlock/Maigret style: [+] Site: http://url.com
                        if line.startswith('[+]') or 'Found at' in line:
                            yield {
                                "platform": "OSINT",
                                "timestamp": mtime,
                                "sender": "Okhotnik",
                                "content": f"Signal Discovered: {line}",
                                "type": "system"
                            }
                        
                        # Generic Log Info: [*] Checking...
                        elif line.startswith('[*]'):
                            # High signal for behavioral timeline
                            yield {
                                "platform": "OSINT",
                                "timestamp": mtime,
                                "sender": "Okhotnik",
                                "content": f"Search Event: {line}",
                                "type": "system"
                            }
                            
                except Exception:
                    continue
