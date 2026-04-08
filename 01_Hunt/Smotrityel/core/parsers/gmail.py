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
