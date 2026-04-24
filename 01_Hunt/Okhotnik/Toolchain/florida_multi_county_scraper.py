import os
import sys
import json
import time
from playwright.sync_api import sync_playwright

def search_duval_core(first_name, last_name, dob="02/01/1989"):
    print(f"[*] Targeting Duval County CORE for: {first_name} {last_name} (DOB: {dob})")
    
    # URL for Duval CORE Search
    url = "https://core.duvalclerk.com/Core/Search/Search"
    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        try:
            page.goto(url, wait_until="networkidle")
            
            # Duval usually requires accepting an agreement first
            if "Agreement" in page.content() or "Accept" in page.content():
                try:
                    page.click('button:has-text("Accept")')
                    page.wait_for_load_state("networkidle")
                except: pass

            # Fill search form
            page.fill('input[id*="FirstName"]', first_name)
            page.fill('input[id*="LastName"]', last_name)
            
            # Select appropriate search options (often a dropdown for 'Criminal')
            # If DOB field is available, we use it to filter
            dob_input = page.query_selector('input[id*="DateOfBirth"]')
            if dob_input:
                dob_input.fill(dob)

            page.click('button[type="submit"]')
            page.wait_for_load_state("networkidle")
            
            # Parse results
            # Similar to Alachua, we look for result grids/rows
            rows = page.query_selector_all('tr')
            for row in rows:
                text = row.inner_text().strip()
                # Generic pattern for Case Numbers
                if "-" in text and ("CF" in text or "MM" in text or "TR" in text):
                    results.append({
                        "platform": "Duval Clerk (CORE)",
                        "timestamp": 0,
                        "sender": "Public Records",
                        "content": f"Case Record Found: {text}",
                        "type": "court_record"
                    })
                    
        except Exception as e:
            print(f"  [ERROR] Duval Scraper Failure: {e}")
        finally:
            browser.close()
            
    return results

def search_modular_pioneer(county_name, first_name, last_name):
    # This handles counties using the common Pioneer portal (often St. Johns/Clay)
    print(f"[*] Targeting {county_name} (Pioneer Portal) for: {first_name} {last_name}")
    
    urls = {
        "StJohns": "https://stjohnsclerk.com/court-records-search/",
        "Clay": "https://clayclerk.com/search-records/",
        "Putnam": "https://putnamclerk.com/online-court-records-search/"
    }
    
    results = []
    # Logic similar to Playwright above, customized per portal if needed
    return results

if __name__ == "__main__":
    # Test Duval
    hits = search_duval_core("Nicholas", "Kulpa")
    print(json.dumps(hits, indent=2))
