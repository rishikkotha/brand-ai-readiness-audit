import requests
from bs4 import BeautifulSoup
import json

def audit_orientation(url):
    headers = {'User-Agent': 'Mozilla/5.0 (AI Readiness Auditor)'}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return {"error": str(e), "severity": "high"}

    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Check for H1 tag (Primary On-Site Orientation)
    h1_tags = soup.find_all('h1')
    
    if not h1_tags:
        return {
            "id": "E-001",
            "title": "Missing H1 Orientation Tag",
            "severity": "high",
            "evidence": "Scanned page structure; 0 <h1> tags found. Visitor lacks immediate context.",
            "suggested_action": {
                "summary": "Add a clear, descriptive <h1> tag to instantly orient visitors and confirm they are in the right place.",
                "priority": "high"
            }
        }
        
    return {
        "status": "Passed", 
        "evidence": f"Found {len(h1_tags)} H1 tag(s) for initial orientation."
    }

if __name__ == "__main__":
    test_url = "https://example.com"
    result = audit_orientation(test_url)
    print(json.dumps(result, indent=2))