import requests
from bs4 import BeautifulSoup
import json

def audit_freshness_signals(url):
    headers = {'User-Agent': 'Mozilla/5.0 (AI Readiness Auditor)'}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return {"error": str(e), "severity": "high"}

    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 1. Check backend HTTP Headers for 'Last-Modified'
    last_modified_header = response.headers.get('Last-Modified')
    
    # 2. Check frontend HTML for explicit timestamp metadata
    meta_modified = soup.find('meta', attrs={'property': 'article:modified_time'})
    time_tags = soup.find_all('time', attrs={'datetime': True})
    
    has_html_timestamp = bool(meta_modified) or len(time_tags) > 0
    
    # 3. Evaluate findings
    if not last_modified_header and not has_html_timestamp:
        return {
            "id": "F-004",
            "title": "Missing Fact Freshness Signals",
            "severity": "high",
            "evidence": f"Scanned {url}; no Last-Modified HTTP header, <time> tags, or article:modified_time meta tags detected.",
            "suggested_action": {
                "summary": "Inject explicit Last-Modified headers and HTML <time> tags so AI models know to overwrite obsolete cached facts (e.g., outdated logos or pricing).",
                "priority": "high"
            }
        }

    return {
        "status": "Passed",
        "evidence": f"Freshness signals found. HTTP Last-Modified: {bool(last_modified_header)}. HTML timestamps: {has_html_timestamp}."
    }

if __name__ == "__main__":
    # Using adobe.com to avoid the DNS resolution error
    test_url = "https://www.example.com"
    result = audit_freshness_signals(test_url)
    print(json.dumps(result, indent=2))