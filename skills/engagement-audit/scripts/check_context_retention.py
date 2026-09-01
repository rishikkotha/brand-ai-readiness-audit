import sys
from playwright.sync_api import sync_playwright
import json

def audit_context_retention(base_url):
    # Simulate an AI appending a specific search intent to the URL
    intent_keyword = "special-ai-offer"
    test_url = f"{base_url}?intent={intent_keyword}"
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            # Navigate to the URL with the intent parameter
            page.goto(test_url, wait_until="domcontentloaded", timeout=45000)
            
            # Extract all visible text on the rendered page
            page_text = page.evaluate("document.body.innerText").lower()
            browser.close()
            
            # Check if the page actually used the context we passed in the URL
            if intent_keyword not in page_text:
                return {
                    "id": "E-002",
                    "title": "Context Retention Failure (Bounce Risk)",
                    "severity": "critical",
                    "evidence": f"Passed parameter '?intent={intent_keyword}' to {base_url}. The page ignored it and rendered a generic layout.",
                    "suggested_action": {
                        "summary": "Configure landing pages to dynamically parse URL parameters (e.g., ?intent=...) and update H1s or banners to reflect the user's specific AI search context.",
                        "priority": "critical"
                    }
                }
            
            return {
                "status": "Passed",
                "evidence": f"Page successfully parsed and displayed the dynamic URL context: '{intent_keyword}'."
            }
            
    except Exception as e:
        return {"error": str(e), "severity": "high"}

if __name__ == "__main__":
    test_url = "https://example.com"
    result = audit_context_retention(test_url)
    print(json.dumps(result, indent=2))