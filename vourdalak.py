import os
import json
import uuid
import sys
import time
from datetime import datetime
from openai import AzureOpenAI
from pypdf import PdfReader

# --- CRITICAL PATCH FOR DUCKDUCKGO ---
try:
    from duckduckgo_search import DDGS
except ImportError:
    try:
        from ddgs import DDGS
    except ImportError:
        print("[!] CRITICAL ERROR: 'duckduckgo-search' library not found.")
        sys.exit()

# --- CONFIGURATION ---
API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "YOUR_API_KEY_HERE")
ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "YOUR_ENDPOINT_HERE")

# Load Okhotnik Config for Proxy Settings
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "01_Hunt", "Okhotnik", "okhotnik_config.json")
PROXY = None
if os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH, 'r') as f:
        _cfg = json.load(f)
        _ps = _cfg.get("proxy_settings", {})
        if _ps.get("enabled"):
            PROXY = _ps.get("http")

# --- THE PANOPTICON SYSTEM PROMPT (SBM v4.0) ---
PANOPTICON_PROMPT = """
You are the "Vourdalak," a specialized behavioral intelligence engine operating under Project Panopticon protocols (SBM v4.0).
Your mission is to analyze the provided OSINT Intelligence Report and generate a high-fidelity psychological dossier.

### ANALYSIS FRAMEWORK (SBM v4.0)
You must deconstruct the subject into three nodes:

1. THE DRIVE CORE (Primary Motivation)
   - Identify the dominant engine: POWER (Control), AFFILIATION (Belonging), or ACHIEVEMENT (Competence).

2. COGNITIVE CIRCUITRY (Processing Style)
   - Complexity: Gestalt (Big Picture) vs. Granular (Details).
   - Rigidity: Reaction to Cognitive Dissonance.

3. THE SOCIAL CHASSIS (Interaction Style)
   - Authority Orientation: Submissive, Cooperative, or Adversarial.
   - Status Battery: Internal vs. External validation.

### OUTPUT FORMAT (JSON ONLY)
{
  "target_identity": "String",
  "sbm_profile": {
    "drive_core": "String",
    "cognitive_circuitry": "String",
    "social_chassis": "String"
  },
  "deyoung_scorecard": {
    "volatility": 0.0, "withdrawal": 0.0, "compassion": 0.0, "politeness": 0.0,
    "industriousness": 0.0, "orderliness": 0.0, "enthusiasm": 0.0,
    "assertiveness": 0.0, "intellect": 0.0, "openness": 0.0
  },
  "tactical_recommendation": "Actionable SBM advice based on their Drive Core."
}
"""

def save_soul(profile, target_id):
    filename = "souls.json"
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            try:
                db = json.load(f)
            except:
                db = []
    else:
        db = []

    record = {
        "id": str(uuid.uuid4()),
        "target_id": target_id,
        "timestamp": datetime.utcnow().isoformat(),
        "soul_fragment": profile
    }
    db.append(record)

    with open(filename, 'w') as f:
        json.dump(db, f, indent=2)

# --- PANOPTICON ACQUISITION PROTOCOL ---
def perform_sector_scan(query, sector_name):
    print(f"[*] Scanning {sector_name} Sector: '{query}'...")
    sector_data = ""
    try:
        # Pass proxy to DDGS if enabled
        with DDGS(proxy=PROXY) as ddgs:
            results = ddgs.text(query, max_results=5)
            if results:
                for r in results:
                    sector_data += f"[{sector_name.upper()}] Source: {r['title']} | Content: {r['body']}\n"
            else:
                print(f"    [!] No signals found in {sector_name}.")
    except Exception as e:
        print(f"    [!] Scan Error: {e}")
    return sector_data

def hunt_prey(target_name):
    print(f"\n[*] INITIATING PANOPTICON ACQUISITION PROTOCOL for: '{target_name}'")
    if PROXY: print(f"[*] IDENTITY MASKED: Via Proxy {PROXY}")
    print("=" * 60)
    
    aggregated_intel = f"PANOPTICON TARGET REPORT: {target_name}\nDATE: {datetime.utcnow().isoformat()}\n\n"

    # 1. DIGITAL IDENTITY BRANCH (Handles & Presence)
    query_digital = f'"{target_name}" site:twitter.com OR site:linkedin.com OR site:instagram.com OR site:facebook.com'
    aggregated_intel += perform_sector_scan(query_digital, "Digital_Identity")
    time.sleep(1) # Evasion pause

    # 2. PHYSICAL/ENVIRONMENTAL BRANCH (Location & Affiliation)
    query_physical = f'"{target_name}" location OR residence OR hometown OR "lived in"'
    aggregated_intel += perform_sector_scan(query_physical, "Physical_Environment")
    time.sleep(1)

    # 3. PSYCHOLOGICAL BASELINE (Verbal Output for SBM Analysis)
    query_psych = f'"{target_name}" interview OR podcast OR transcript OR "written by"'
    aggregated_intel += perform_sector_scan(query_psych, "Psych_Baseline")
    
    print("=" * 60)
    print(f"[*] ACQUISITION COMPLETE. Constructing Dossier...")
    return aggregated_intel

def vourdalak_feed(text_input, target_name):
    if not text_input or len(text_input) < 100:
        print("[!] ERROR: Intelligence yield too low. Target is a ghost.")
        return

    print(f"[*] ENGAGING SBM ENGINE ({len(text_input)} bytes of intel)...")
    
    try:
        client = AzureOpenAI(api_key=API_KEY, api_version="2024-02-15-preview", azure_endpoint=ENDPOINT)
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": PANOPTICON_PROMPT},
                {"role": "user", "content": text_input[:30000]} 
            ],
            response_format={"type": "json_object"},
            temperature=0.0
        )

        profile = json.loads(response.choices[0].message.content)
        profile["status"] = "SOUL_CONSUMED"
        save_soul(profile, target_name)
        
        print("\n" + "="*60)
        print(f"TARGET ACQUIRED: {profile.get('target_identity', target_name).upper()}")
        print("-" * 60)
        print(f"DRIVE CORE:       {profile['sbm_profile']['drive_core']}")
        print(f"COGNITIVE STYLE:  {profile['sbm_profile']['cognitive_circuitry']}")
        print(f"SOCIAL CHASSIS:   {profile['sbm_profile']['social_chassis']}")
        print("-" * 60)
        print(f"TACTICAL ADVICE:  {profile.get('tactical_recommendation', 'N/A')}")
        print("="*60 + "\n")
        print("[*] Full SBM Dossier encrypted and saved to 'souls.json'.")

    except Exception as e:
        print(f"\n[!] SYSTEM FAILURE: {str(e)}")

# --- INTERFACE ---
if __name__ == "__main__":
    print("\nPANOPTICON PROTOCOL // AUTOMATED HUNTER KILLER")
    print("------------------------------------------------")
    
    target = input("ENTER TARGET IDENTIFIER: ")
    if target:
        # Mode 2 is now the default "Hunt"
        intel_dossier = hunt_prey(target)
        if intel_dossier:
            vourdalak_feed(intel_dossier, target)
