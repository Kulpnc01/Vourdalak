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
            if isinstance(data, dict) and not any(k in data for k in ['Received Saved Chat History', 'Sent Saved Chat History']):
                for thread_name, messages in data.items():
                    if not isinstance(messages, list): continue
                    for msg in messages:
                        content = msg.get('Content') or msg.get('Text') or ""
                        media_type = msg.get('Media Type', 'TEXT')
                        
                        if not content and media_type != 'TEXT':
                            content = f"[{media_type}]"
                        if not content: continue

                        try:
                            # New format: "2026-03-01 06:58:20 UTC"
                            clean_time = msg.get('Created', '').replace(' UTC', '')
                            dt = datetime.strptime(clean_time, '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc)
                            ts = dt.timestamp()
                            date_str = dt.strftime("%Y-%m-%d")
                        except (ValueError, AttributeError): continue

                        sender = msg.get('From', 'Unknown')

                        if date_str not in daily_chats:
                            daily_chats[date_str] = {"timestamp": ts, "messages": []}
                        daily_chats[date_str]['messages'].append({"ts": ts, "text": f"[{sender}]: {content}"})

            # Handle Old Format: Category-based
            else:
                categories = ['Received Saved Chat History', 'Sent Saved Chat History']
                for category in categories:
                    for msg in data.get(category, []):
                        content = msg.get('Text') or msg.get('Content') or ""
                        media_type = msg.get('Media Type', 'TEXT')
                        
                        if not content and media_type != 'TEXT':
                            content = f"[{media_type}]"
                        if not content: continue

                        try:
                            clean_time = msg.get('Created', '').replace(' UTC', '')
                            dt = datetime.strptime(clean_time, '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc)
                            ts = dt.timestamp()
                            date_str = dt.strftime("%Y-%m-%d")
                        except (ValueError, AttributeError): continue

                        sender = msg.get('From', 'Unknown')

                        if date_str not in daily_chats:
                            daily_chats[date_str] = {"timestamp": ts, "messages": []}
                        daily_chats[date_str]['messages'].append({"ts": ts, "text": f"[{sender}]: {content}"})

            for date_str in sorted(daily_chats.keys()):
                chat_data = daily_chats[date_str]
                chat_data['messages'].sort(key=lambda x: x['ts'])
                joined = "\n".join([m['text'] for m in chat_data['messages']])
                
                yield {
                    "platform": "Snapchat",
                    "timestamp": chat_data['timestamp'],
                    "sender": "Snapchat Thread",
                    "content": joined,
                    "type": "message"
                }