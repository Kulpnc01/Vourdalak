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