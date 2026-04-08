import os
import sys
import json
import requests
from bs4 import BeautifulSoup

def search_judyrecords(query):
    print(f"[*] Searching Judyrecords for: {query}")
    # Judyrecords search uses a simple query param
    url = f"https://www.judyrecords.com/search?q={query.replace(' ', '+')}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        results = []
        
        # Identify search result blocks (this is a heuristic, real sites change)
        for card in soup.find_all('div', class_='card-body'):
            title = card.find('h5')
            if title:
                link = card.find('a', href=True)
                summary = card.find('p')
                results.append({
                    "platform": "Judyrecords",
                    "timestamp": 0, # Usually found in summary, needs regex
                    "sender": "Public Records",
                    "content": f"Record Found: {title.get_text().strip()}\nLink: https://www.judyrecords.com{link['href']}\nSummary: {summary.get_text().strip() if summary else 'No summary'}",
                    "type": "court_record"
                })
        
        return results
    except Exception as e:
        print(f"[ERROR] Judyrecords search failed: {e}")
        return []

if __name__ == "__main__":
    query = sys.argv[1] if len(sys.argv) > 1 else "Nicholas Kulpa"
    hits = search_judyrecords(query)
    print(json.dumps(hits, indent=2))
