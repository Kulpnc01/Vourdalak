import os
import re
from bs4 import BeautifulSoup
from datetime import datetime

def parse(extract_dir):
    """
    Parses exported Florida County Clerk HTML result pages (Alachua, Duval, etc.)
    """
    for root, dirs, files in os.walk(extract_dir):
        for file in files:
            if file.endswith('.html') and any(x in file.lower() for x in ['alachua', 'duval', 'match', 'clerk']):
                path = os.path.join(root, file)
                
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    soup = BeautifulSoup(f.read(), 'html.parser')

                # --- ALACHUA/DUVAL TABLE PARSER ---
                case_links = soup.find_all('a', href=re.compile(r'section=summary|CaseDetails'))
                
                for link in case_links:
                    case_num = link.get_text().strip()
                    row = link.find_parent('tr')
                    if not row: continue
                    
                    cols = row.find_all('td')
                    # This is a generic column mapper, might need tuning per county
                    party_type = "Unknown"
                    status = "Unknown"
                    if len(cols) > 6:
                        party_type = cols[1].get_text().strip()
                        status = cols[6].get_text().strip()
                    
                    # Look for charge details in the next row
                    next_row = row.find_next_sibling('tr')
                    charge_info = ""
                    disp_date = None
                    if next_row:
                        charge_cols = next_row.find_all('td')
                        if len(charge_cols) > 6:
                            disp_date_str = charge_cols[2].get_text().strip()
                            charge_info = charge_cols[3].get_text().strip()
                            
                            if disp_date_str:
                                try:
                                    disp_date = datetime.strptime(disp_date_str, '%m/%d/%Y').timestamp()
                                except: pass

                    yield {
                        "platform": "Florida Clerk Portal",
                        "timestamp": disp_date or datetime.now().timestamp(),
                        "sender": "Public Records",
                        "content": f"Court Case Found: {case_num}\nParty: {party_type}\nStatus: {status}\nCharge: {charge_info}",
                        "type": "court_record",
                        "metadata": {
                            "case_number": case_num,
                            "status": status
                        }
                    }
