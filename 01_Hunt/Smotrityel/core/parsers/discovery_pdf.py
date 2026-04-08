import os
import re
from datetime import datetime

def parse(extract_dir):
    """
    Parses user-provided Discovery PDFs or their text equivalents.
    """
    # Specifically looking for the Discovery.pdf or any text/md file containing legal data
    # For now, we will look for files in the subject's directory
    for root, dirs, files in os.walk(extract_dir):
        for file in files:
            if 'discovery' in file.lower() or 'taxes' in file.lower():
                path = os.path.join(root, file)
                
                # Resilient reading (PDFs might be already extracted to text/md in some pipelines)
                content = ""
                if file.endswith('.md') or file.endswith('.txt'):
                    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                
                if not content: continue

                # 1. Look for Alachua County Case Number
                case_matches = re.findall(r'Case Number:\s*([\d-]+-\w+-\d+-\w+)', content)
                for case_num in case_matches:
                    yield {
                        "platform": "Legal Discovery",
                        "timestamp": datetime.now().timestamp(), # Case is current
                        "sender": "State Attorney",
                        "content": f"Active Case discovered in documents: {case_num}",
                        "type": "criminal_record",
                        "metadata": {"case_number": case_num}
                    }

                # 2. Look for Scoresheet/Prior Record entries
                # Pattern: 2 / 810.02(3)(b) / 7 / BURGLARY OF A DWELLING ('15) / 1 X 14 = 14
                prior_matches = re.findall(r'/ (.*?) \(\'(\d{2})\'\) /', content)
                for desc, year_short in prior_matches:
                    year = 2000 + int(year_short) if int(year_short) < 50 else 1900 + int(year_short)
                    yield {
                        "platform": "Legal Discovery (Priors)",
                        "timestamp": datetime(year, 1, 1).timestamp(),
                        "sender": "Public Records",
                        "content": f"Prior Conviction: {desc.strip()} (Year: {year})",
                        "type": "criminal_record",
                        "metadata": {"description": desc.strip(), "year": year}
                    }
