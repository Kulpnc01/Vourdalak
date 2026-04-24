import os
import sys
import json
import time
from playwright.sync_api import sync_playwright

def search_florida_doc_direct(first_name, last_name):
    print(f"[*] DIRECT EXECUTION: Florida DOC for {first_name} {last_name}")
    
    # Direct link to the 'Search All' databases page
    url = "https://pubapps.fdc.myflorida.com/offendersearch/Search.aspx"
    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        page = context.new_page()
        
        try:
            print("  > Navigating to Search portal...")
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            
            # Fill search form
            page.fill('#ctl00_ContentPlaceHolder1_txtLastName', last_name)
            page.fill('#ctl00_ContentPlaceHolder1_txtFirstName', first_name)
            
            # Click the Search All Corrections Radio
            try:
                page.click('#ctl00_ContentPlaceHolder1_radSearchType_2')
            except: pass

            # Click Search button
            page.click('#ctl00_ContentPlaceHolder1_btnSearch')
            page.wait_for_load_state("networkidle", timeout=60000)

            # Parse results
            rows = page.query_selector_all('table[id*="grdInmates"] tr')
            if rows:
                print(f"  [+] Found {len(rows)-1} potential matches.")
                for row in rows[1:]:
                    cols = row.query_selector_all('td')
                    if len(cols) >= 5:
                        res_name = cols[0].inner_text().strip()
                        dc_num = cols[1].inner_text().strip()
                        release_date = cols[4].inner_text().strip()
                        
                        results.append({
                            "platform": "Florida DOC",
                            "timestamp": 0,
                            "sender": "Public Records",
                            "content": f"Offender Record Found: {res_name} (DC#{dc_num})\nRelease: {release_date}",
                            "type": "criminal_record",
                            "metadata": {"dc_number": dc_num, "name": res_name, "release": release_date}
                        })
            else:
                print("  [-] No records found.")
                
        except Exception as e:
            print(f"  [ERROR] Direct Scraper Failure: {e}")
            page.screenshot(path="fdoc_direct_error.png")
        finally:
            browser.close()
            
    return results

if __name__ == "__main__":
    f_name = "Nicholas"
    l_name = "Kulpa"
    if len(sys.argv) > 1:
        if len(sys.argv) == 2:
            parts = sys.argv[1].split()
            f_name = parts[0]
            l_name = parts[-1] if len(parts) > 1 else ""
        else:
            f_name = sys.argv[1]
            l_name = sys.argv[2]
            
    hits = search_florida_doc_direct(f_name, l_name)
    print(json.dumps(hits, indent=2))
