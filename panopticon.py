import os
import json
import uuid
import sys
from datetime import datetime
from openai import AzureOpenAI

# --- CONFIGURATION ---
API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "YOUR_API_KEY_HERE")
ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "YOUR_ENDPOINT_HERE")
DB_FILE = "panopticon_vectors.json"

# --- THE PANOPTICON "FULL STACK" PROMPT ---
# Sourced directly from PDF Pages 3-13 (DCMF & Dark Tetrad)
SYSTEM_PROMPT = """
You are the PANOPTICON AI, a forensic psychometrics engine. 
Your mandate is to generate a 25-Dimensional Character Vector based on the HiTOP and AMPD frameworks.

### I. DIMENSIONAL CHARACTER MAPPING (Score 0.0 - 1.0)
Analyze the text for these specific High-Fidelity facets:

DOMAIN 1: NEGATIVE AFFECTIVITY (Internalizing)
- Anxiousness: Nervousness, hedging language ("maybe"), recursive worrying.
- Emotional Lability: Polarity shifts, "text bombing", punctuation ("!!!").
- Hostility: Vengeful affect, "hostile attribution bias".
- Separation Insecurity: "Double texting", abandonment fears.
- Submissiveness: Apologetic ("sorry"), passive voice.

DOMAIN 2: ANTAGONISM (Externalizing)
- Callousness: Lack of remorse, dehumanizing language.
- Deceitfulness: Inconsistencies, fewer "I" pronouns (distancing).
- Grandiosity: Status seeking, "I" ownership of success, condescension.
- Manipulativeness: Gaslighting, conditional affection ("If you loved me...").

DOMAIN 3: DISINHIBITION
- Impulsivity: Urgency ("now"), typos, rapid-fire syntax.
- Irresponsibility: Blame shifting, victim stance.
- Risk Taking: Thrill-seeking verbal output.

### II. DARK TETRAD DETECTION (Adversarial Architecture)
Flag specific tactical signatures:
- "Duping Delight": Smirking/Joy in deception.
- "Future Faking": Promises of future value to extract current resources.
- "DARVO": Deny, Attack, Reverse Victim & Offender.
- "Virtuous Victimhood": Using victim status for moral immunity.

### III. BEHAVIORAL ENGINEERING (Intervention)
Based on the profile, select the optimal Counter-Measure:
- For High Narcissism/Sadism: "GRAY ROCK" (Remove emotional valence, monosyllabic).
- For High Machiavellianism: "PAPER TRAIL" (Extreme transparency, immutable rules).
- For High Volatility: "DRI" (Differential Reinforcement of Incompatible behavior).

### OUTPUT FORMAT (Strict JSON Schema)
{
  "target_identity": "String",
  "dcmf_vector": {
    "anxiousness": 0.0, "emotional_lability": 0.0, "hostility": 0.0, 
    "callousness": 0.0, "grandiosity": 0.0, "manipulativeness": 0.0,
    "impulsivity": 0.0, "risk_taking": 0.0
  },
  "dark_tetrad_flags": ["List of detected tactics or 'None'"],
  "cybernetic_phenotype": {
    "volatility": "High/Low", 
    "withdrawal": "High/Low" 
  },
  "intervention_protocol": {
    "strategy": "NAME OF STRATEGY (e.g., Gray Rock)",
    "rationale": "Why this works based on the vector.",
    "script_example": "A specific sentence the user should say."
  }
}
"""

def load_vectors():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r') as f: return json.load(f)
        except: return []
    return []

def save_vector(profile):
    db = load_vectors()
    # Create the "Full Stack" record [Page 14 Schema]
    record = {
        "user_id": str(uuid.uuid4()),
        "timestamp": datetime.utcnow().isoformat(),
        "dcmf_vector": profile.get("dcmf_vector", {}),
        "dark_tetrad_scores": profile.get("dark_tetrad_flags", []),
        "intervention_trigger": profile.get("intervention_protocol", {}).get("strategy", "MONITOR"),
        "full_profile": profile
    }
    db.append(record)
    with open(DB_FILE, 'w') as f:
        json.dump(db, f, indent=2)
    return "VECTOR_STORED"

def analyze_target(text_input, target_name):
    print(f"\n[*] INITIATING PANOPTICON VECTOR ANALYSIS for '{target_name}'...")
    
    client = AzureOpenAI(
        api_key=API_KEY, 
        api_version="2024-02-15-preview", 
        azure_endpoint=ENDPOINT
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"TARGET: {target_name}\n\nDATA:\n{text_input[:25000]}"}
            ],
            response_format={"type": "json_object"},
            temperature=0.0
        )
        
        profile = json.loads(response.choices[0].message.content)
        save_vector(profile)

        # --- THE REPORT ---
        print("\n" + "="*60)
        print(f"PANOPTICON TARGET: {target_name.upper()}")
        print("-" * 60)
        
        vec = profile.get("dcmf_vector", {})
        print(f"[!] DOMAIN: ANTAGONISM")
        print(f"    Grandiosity:      {vec.get('grandiosity', 0):.2f}")
        print(f"    Manipulativeness: {vec.get('manipulativeness', 0):.2f}")
        print(f"    Callousness:      {vec.get('callousness', 0):.2f}")
        
        print(f"\n[!] DOMAIN: NEGATIVE AFFECTIVITY")
        print(f"    Emotional Lability: {vec.get('emotional_lability', 0):.2f}")
        print(f"    Hostility:          {vec.get('hostility', 0):.2f}")

        print("-" * 60)
        print("DETECTED ADVERSARIAL ARCHITECTURES:")
        for flag in profile.get("dark_tetrad_flags", []):
            print(f"  [X] {flag}")

        print("-" * 60)
        protocol = profile.get("intervention_protocol", {})
        print(f"RECOMMENDED INTERVENTION: {protocol.get('strategy', 'N/A').upper()}")
        print(f"RATIONALE: {protocol.get('rationale', 'N/A')}")
        print(f"SCRIPT:    \"{protocol.get('script_example', 'N/A')}\"")
        print("="*60 + "\n")

    except Exception as e:
        print(f"[!] SYSTEM FAILURE: {e}")

# --- INGESTION INTERFACE ---
if __name__ == "__main__":
    print("\nPROJECT PANOPTICON // BEHAVIORAL ENGINEERING INTERFACE")
    target = input("Enter Target Name: ")
    print("Paste Intelligence (Text/Logs) - Press Ctrl+Z then Enter to finish:")
    lines = []
    try:
        while True:
            line = input()
            lines.append(line)
    except EOFError:
        pass
    text = "\n".join(lines)
    
    if len(text) > 50:
        analyze_target(text, target)
    else:
        print("[!] Insufficient Biomass.")