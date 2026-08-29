import requests
from bs4 import BeautifulSoup
import json

def audit_json_ld(url):
    # 1. Fetch the website content (Read-only, respects live site)
    headers = {'User-Agent': 'Mozilla/5.0 (AI Readiness Auditor)'}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return {"error": str(e), "severity": "high"}

    # 2. Parse the HTML using BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 3. Search for structured data tags
    json_ld_scripts = soup.find_all('script', type='application/ld+json')
    
    # 4. Evaluate findings against the required report schema
    if not json_ld_scripts:
        return {
            "id": "F-001",
            "title": "No JSON-LD structured data found",
            "severity": "high",
            "evidence": f"Scanned {url}; 0 schema.org tags detected.",
            "suggested_action": {
                "summary": "Add Organization or Product JSON-LD markup to explicitly define facts for AI crawlers.",
                "priority": "high"
            }
        }
    
    return {
        "status": "Passed", 
        "evidence": f"Found {len(json_ld_scripts)} JSON-LD tags."
    }

if __name__ == "__main__":
    # Test the function with a sample URL
    test_url = "https://example.com"
    result = audit_json_ld(test_url)
    print(json.dumps(result, indent=2))