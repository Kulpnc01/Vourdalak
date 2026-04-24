import os
import re
from bs4 import BeautifulSoup
from datetime import datetime

def parse(extract_dir):
    """
    Parses exported Alachua County Clerk HTML result pages.
    """
    # Look for the saved match files or any .html files in the subject directory
    for root, dirs, files in os.walk(extract_dir):
        for file in files:
            if file.endswith('.html') and ('alachua' in file.lower() or 'match' in file.lower()):
                path = os.path.join(root, file)
                
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    soup = BeautifulSoup(f.read(), 'html.parser')

                # Identify search criteria for context
                criteria_text = ""
                criteria_div = soup.find(string=re.compile(r'Search Criteria:'))
                if criteria_div:
                    criteria_table = criteria_div.find_next('table')
                    if criteria_table:
                        criteria_text = criteria_table.get_text(separator=' ').strip()

                # Find the results table
                # The table contains case numbers in <a> tags
                case_links = soup.find_all('a', href=re.compile(r'section=summary'))
                
                for link in case_links:
                    case_num = link.get_text().strip()
                    row = link.find_parent('tr')
                    if not row: continue
                    
                    cols = row.find_all('td')
                    party_type = cols[1].get_text().strip() if len(cols) > 1 else "Unknown"
                    status = cols[6].get_text().strip() if len(cols) > 6 else "Unknown"
                    
                    # Look for charge details in the next row
                    # (The HTML structure uses multiple <tr> for one case)
                    next_row = row.find_next_sibling('tr')
                    charge_info = ""
                    disp_date = None
                    if next_row:
                        charge_cols = next_row.find_all('td')
                        if len(charge_cols) > 6:
                            disp_date_str = charge_cols[2].get_text().strip()
                            charge_info = charge_cols[3].get_text().strip()
                            disposition = charge_cols[6].get_text().strip()
                            
                            if disp_date_str:
                                try:
                                    disp_date = datetime.strptime(disp_date_str, '%m/%d/%Y').timestamp()
                                except: pass

                    yield {
                        "platform": "Alachua Clerk",
                        "timestamp": disp_date or datetime.now().timestamp(),
                        "sender": "Public Records",
                        "content": f"Court Case Found: {case_num}\nParty: {party_type}\nStatus: {status}\nCharge: {charge_info}\nDisposition: {disposition if 'disposition' in locals() else 'N/A'}",
                        "type": "court_record",
                        "metadata": {
                            "case_number": case_num,
                            "status": status,
                            "disposition_date": disp_date_str if 'disp_date_str' in locals() else None
                        }
                    }
