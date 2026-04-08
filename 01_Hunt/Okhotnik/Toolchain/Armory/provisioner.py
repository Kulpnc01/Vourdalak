import os
import time
import uuid
import requests
import random
import string
from pathlib import Path

class BurnerProvisioner:
    def __init__(self):
        self.email_api = "https://api.mail.tm"
        self.armory_dir = Path(__file__).parent.absolute()
        
    def generate_random_string(self, length=10):
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

    # --- EMAIL PROVISIONING (mail.tm) ---
    def create_burner_email(self):
        """Creates a temporary email account and returns (address, password, token)."""
        print("[*] PROVISIONER: Requesting new burner email...")
        try:
            # 1. Get Domain
            domains = requests.get(f"{self.email_api}/domains").json()
            domain = domains['hydra:member'][0]['domain']
            
            # 2. Create Account
            address = f"{self.generate_random_string()}@{domain}"
            password = self.generate_random_string(12)
            
            payload = {"address": address, "password": password}
            requests.post(f"{self.email_api}/accounts", json=payload).json()
            
            # 3. Get Auth Token
            token_resp = requests.post(f"{self.email_api}/token", json=payload).json()
            token = token_resp['token']
            
            print(f" [+] PROVISIONED: {address}")
            return address, password, token
        except Exception as e:
            print(f" [!] Email Provisioning Failed: {e}")
            return None, None, None

    def wait_for_verification_code(self, token, timeout=300):
        """Polls the inbox for a verification code or link."""
        print("[*] PROVISIONER: Watching inbox for verification signal...")
        start_time = time.time()
        headers = {"Authorization": f"Bearer {token}"}
        
        while time.time() - start_time < timeout:
            try:
                resp = requests.get(f"{self.email_api}/messages", headers=headers).json()
                messages = resp.get('hydra:member', [])
                
                if messages:
                    # Get latest message
                    msg_id = messages[0]['id']
                    msg_full = requests.get(f"{self.email_api}/messages/{msg_id}", headers=headers).json()
                    body = msg_full.get('text', '')
                    
                    # Heuristic to find 6-digit codes
                    import re
                    code = re.search(r'\b\d{6}\b', body)
                    if code:
                        print(f" [+] SIGNAL ACQUIRED: Code {code.group(0)}")
                        return code.group(0)
                    
                    # Fallback: return the whole body for manual inspection
                    print(" [+] SIGNAL ACQUIRED: Content received (no numeric code found).")
                    return body
            except: pass
            time.sleep(5)
        
        print(" [!] TIMEOUT: No verification signal received.")
        return None

    # --- SMS PROVISIONING (Local Gateway / Android Bridge) ---
    def wait_for_local_sms(self, timeout=300):
        """
        Polls a local file for incoming SMS signals. 
        This is the landing zone for your Android phone bridge.
        """
        gateway_file = self.armory_dir / "sms_gateway.txt"
        print(f"[*] PROVISIONER: Watching Local SMS Gateway ({gateway_file.name})...")
        
        if not gateway_file.exists():
            with open(gateway_file, 'w') as f: f.write("") # Create empty

        start_time = time.time()
        # Keep track of initial content to only catch NEW messages
        initial_content = gateway_file.read_text()

        while time.time() - start_time < timeout:
            current_content = gateway_file.read_text()
            if current_content != initial_content:
                # New signal detected!
                new_data = current_content.replace(initial_content, "").strip()
                import re
                code = re.search(r'\b\d{4,8}\b', new_data)
                if code:
                    print(f" [+] SMS SIGNAL ACQUIRED: Code {code.group(0)}")
                    return code.group(0)
                else:
                    print(" [+] SMS SIGNAL ACQUIRED: Content received.")
                    return new_data
            time.sleep(2)
        
        print(" [!] TIMEOUT: No SMS signal detected in gateway.")
        return None

    def request_sms_number(self, api_key=None, service="generic"):
        """Bridge for both paid and local phone verification."""
        if not api_key:
            print(" [*] SMS MODE: Using Local Android Bridge. (Update sms_gateway.txt)")
            return "LOCAL_GATEWAY"
        # Paid logic...
        return "PENDING_API"

if __name__ == "__main__":
    p = BurnerProvisioner()
    email, pwd, token = p.create_burner_email()
    if email:
        print(f"Email: {email}\nPass: {pwd}")
        print("Waiting for verification (Ctrl+C to stop)...")
        content = p.wait_for_verification_code(token)
        if content:
            print(f"Message Content: {content}")
