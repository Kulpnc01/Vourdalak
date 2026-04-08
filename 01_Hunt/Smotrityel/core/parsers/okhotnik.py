import os
import re
from datetime import datetime

def parse(extract_dir):
    """
    Scans for Okhotnik tool logs and yields standardized behavioral events.
    """
    log_dir = os.path.join(extract_dir, "Logs")
    if not os.path.exists(log_dir):
        return

    for file in os.listdir(log_dir):
        path = os.path.join(log_dir, file)
        if not os.path.isfile(path): continue
        
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Split content into execution blocks if multiple exist
        executions = content.split('--- EXECUTION:')
        
        for block in executions:
            if not block.strip(): continue
            
            # Extract timestamp from block header if possible
            ts = datetime.now().timestamp() # Default fallback
            ts_match = re.search(r' (\d{4}-\d{2}-\d{2} \d+:\d+:\d+)', block)
            if ts_match:
                try:
                    ts = datetime.strptime(ts_match.group(1), '%Y-%m-%d %H:%M:%S').timestamp()
                except: pass

            # --- SHERLOCK PARSER ---
            if 'sherlock' in file.lower():
                hits = re.findall(r'\[\+\] (.*?): (https?://\S+)', block)
                for platform, url in hits:
                    yield {
                        "platform": f"Sherlock ({platform})",
                        "timestamp": ts,
                        "sender": "Okhotnik",
                        "content": f"Account discovered on {platform}: {url}",
                        "type": "discovery"
                    }

            # --- HOLEHE PARSER ---
            elif 'holehe' in file.lower():
                hits = re.findall(r'\[\+\] (.*?)\n', block)
                for platform in hits:
                    yield {
                        "platform": f"Holehe ({platform.strip()})",
                        "timestamp": ts,
                        "sender": "Okhotnik",
                        "content": f"Email is registered on {platform.strip()}",
                        "type": "discovery"
                    }

            # --- BLACKBIRD PARSER ---
            elif 'blackbird' in file.lower():
                # Blackbird lists hits after 'Enumerating accounts'
                if 'No accounts were found' not in block:
                    hits = re.findall(r'馃敶 (.*?): (https?://\S+)', block)
                    for platform, url in hits:
                        yield {
                            "platform": f"Blackbird ({platform})",
                            "timestamp": ts,
                            "sender": "Okhotnik",
                            "content": f"Account discovered: {url}",
                            "type": "discovery"
                        }

            # --- H8MAIL PARSER ---
            elif 'h8mail' in file.lower():
                if 'Not Compromised' in block:
                    yield {
                        "platform": "h8mail",
                        "timestamp": ts,
                        "sender": "Okhotnik",
                        "content": "Target email checked against breach databases: No compromises found.",
                        "type": "security_check"
                    }
                elif 'Compromised' in block:
                    yield {
                        "platform": "h8mail",
                        "timestamp": ts,
                        "sender": "Okhotnik",
                        "content": "CRITICAL: Target email found in data breaches.",
                        "type": "security_alert"
                    }

            # --- JUDYRECORDS PARSER ---
            elif 'judyrecords' in file.lower():
                hits = re.findall(r'Record Found: (.*?)\nLink: (https?://\S+)', block)
                for title, url in hits:
                    yield {
                        "platform": "Judyrecords",
                        "timestamp": ts,
                        "sender": "Okhotnik",
                        "content": f"Court Record discovered: {title}\nURL: {url}",
                        "type": "public_record"
                    }

            # --- COURT SCRAPER PARSER ---
            elif 'court_scraper' in file.lower():
                if 'Search initiated' in block:
                    yield {
                        "platform": "Court Records",
                        "timestamp": ts,
                        "sender": "Okhotnik",
                        "content": block.strip(),
                        "type": "public_record_search"
                    }

            # --- FLORIDA DOC PARSER ---
            elif 'florida_doc' in file.lower():
                hits = re.findall(r'Offender Record Found: (.*?)\nRace: (.*?), Sex: (.*?)\nRelease Date: (.*)', block)
                for name, race, sex, release in hits:
                    yield {
                        "platform": "Florida DOC",
                        "timestamp": ts,
                        "sender": "Okhotnik",
                        "content": f"Offender Record Found: {name}\nRace: {race}, Sex: {sex}\nRelease Date: {release}",
                        "type": "criminal_record"
                    }

            # --- ALACHUA CLERK PARSER ---
            elif 'alachua_clerk' in file.lower():
                hits = re.findall(r'Case Record Found: (.*)', block)
                for case_data in hits:
                    yield {
                        "platform": "Alachua Clerk",
                        "timestamp": ts,
                        "sender": "Okhotnik",
                        "content": f"Court Record discovered: {case_data.strip()}",
                        "type": "court_record"
                    }
