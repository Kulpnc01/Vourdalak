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