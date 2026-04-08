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
                    ts = msg.get('timestamp_ms', 0) / 1000.0
                    date_str = datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d")
                    sender = fix_text(msg.get('sender_name', 'Unknown'))

                    # Capture Media
                    media_list = []
                    for m_type in ['photos', 'videos', 'audio_files', 'files']:
                        if m_type in msg:
                            for item in msg[m_type]:
                                uri = item.get('uri')
                                if uri:
                                    media_list.append({
                                        "uri": uri,
                                        "type": m_type,
                                        "timestamp": ts,
                                        "metadata": item
                                    })

                    if 'content' in msg:
                        content = fix_text(msg.get('content', ''))
                        if date_str not in daily_chats:
                            daily_chats[date_str] = {"timestamp": ts, "messages": [], "media": []}
                        daily_chats[date_str]['messages'].append(f"[{sender}]: {content}")
                        daily_chats[date_str]['media'].extend(media_list)
                    elif media_list:
                        # Media-only message
                        if date_str not in daily_chats:
                            daily_chats[date_str] = {"timestamp": ts, "messages": [], "media": []}
                        daily_chats[date_str]['media'].extend(media_list)

                for date_str, chat_data in daily_chats.items():
                    chat_data['messages'].reverse() 
                    joined_transcript = "\n".join(chat_data['messages'])

                    yield {
                        "platform": "Facebook",
                        "timestamp": chat_data['timestamp'],
                        "sender": thread_name, 
                        "content": joined_transcript,
                        "type": "message",
                        "media": chat_data['media']
                    }