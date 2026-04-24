import os
import sys
import json
import time
from playwright.sync_api import sync_playwright

def search_alachua_clerk_hardened(first_name, last_name):
    print(f"[*] Hardened Search: Alachua County Clerk for {first_name} {last_name}")
    
    url_menu = "https://www.alachuaclerk.org/court_records/index.cfm?section=menu"
    url_search = "https://www.alachuaclerk.org/court_records/index.cfm?section=casehist"
    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        page = context.new_page()
        
        try:
            # Step 1: Initial Handshake (Captcha/Entry)
            print("  > Passing entry wall...")
            page.goto(url_menu, wait_until="networkidle")
            # The HAR showed a 'loginsubmit' button
            # We check if we need to click it
            btn = page.query_selector('input[name="loginsubmit"]')
            if btn:
                btn.click()
                page.wait_for_load_state("networkidle")

            # Step 2: The Search
            print(f"  > Submitting search query for {first_name} {last_name}...")

            # Navigate to Name Search section if not already there
            page.goto("https://www.alachuaclerk.org/court_records/index.cfm?section=name_search", wait_until="networkidle")

            # Fill Name Fields
            page.fill('input[name="LastName"]', last_name)
            page.fill('input[name="FirstName"]', first_name)

            # Click Submit
            page.click('input[name="namesubmit"]')
            page.wait_for_load_state("networkidle")
            # Step 3: Parsing Results
            content = page.content()
            if "No records found" in content:
                print("  [-] No records found.")
            else:
                # Look for the links we saw in the HTML: section=summary
                links = page.query_selector_all('a[href*="section=summary"]')
                print(f"  [+] Found {len(links)} potential case links.")
                
                for link in links:
                    case_text = link.inner_text().strip()
                    href = link.get_attribute('href')
                    if case_text:
                        results.append({
                            "platform": "Alachua Clerk",
                            "timestamp": 0,
                            "sender": "Public Records",
                            "content": f"Automated Case Discovery: {case_text}\nLink: https://www.alachuaclerk.org/court_records/{href}",
                            "type": "court_record",
                            "metadata": {"case_number": case_text, "url": href}
                        })
                        
        except Exception as e:
            print(f"  [ERROR] Hardened search failed: {e}")
            page.screenshot(path="alachua_hardened_error.png")
        finally:
            browser.close()
            
    return results

if __name__ == "__main__":
    f_name = "Nicholas"
    l_name = "Kulpa"
    if len(sys.argv) > 1:
        # Expecting either "First Last" as one arg or "First" "Last" as two
        if len(sys.argv) == 2:
            parts = sys.argv[1].split()
            f_name = parts[0]
            l_name = parts[-1] if len(parts) > 1 else ""
        else:
            f_name = sys.argv[1]
            l_name = sys.argv[2]
            
    hits = search_alachua_clerk_hardened(f_name, l_name)
    print(json.dumps(hits, indent=2))
