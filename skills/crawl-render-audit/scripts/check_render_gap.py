import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import json

def audit_render_gap(url):
    # 1. Static Fetch (How a basic AI bot sees the site)
    headers = {'User-Agent': 'Mozilla/5.0 (AI Readiness Auditor)'}
    try:
        static_resp = requests.get(url, headers=headers, timeout=10)
        static_soup = BeautifulSoup(static_resp.text, 'html.parser')
        static_text = len(static_soup.get_text(strip=True))
    except Exception as e:
        return {"error": str(e)}

    # 2. Dynamic Fetch (How a full browser sees the site)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=15000)
            dynamic_text = len(page.evaluate("document.body.innerText"))
        except Exception as e:
            browser.close()
            return {"error": str(e)}
        browser.close()

    # 3. Calculate the gap
    difference = dynamic_text - static_text
    
    # 4. Evaluate findings
    if difference > 500:  # Arbitrary threshold for missing text
        return {
            "id": "F-002",
            "title": "Severe Client-Side Rendering Dependency",
            "severity": "critical",
            "evidence": f"Static text: {static_text} chars. Rendered text: {dynamic_text} chars. Core content is hidden from basic crawlers.",
            "suggested_action": {
                "summary": "Implement Server-Side Rendering (SSR) or static site generation so core text is present in the initial HTML payload.",
                "priority": "critical"
            }
        }
        
    return {
        "status": "Passed", 
        "evidence": "Minimal text gap between static HTML and rendered DOM."
    }

if __name__ == "__main__":
    test_url = "https://example.com"
    result = audit_render_gap(test_url)
    print(json.dumps(result, indent=2))