from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup

def audit_category_signals(url):
    # 1. Parse URL to determine page typology (broad storefront vs. specific category)
    parsed_url = urlparse(url)
    is_homepage = parsed_url.path in ['', '/']

    # 2. Scrape the page for semantic signals (Title and H1)
    has_category_keywords = False
    headers = {'User-Agent': 'Mozilla/5.0 (AI Readiness Auditor)'}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.title.string.lower() if soup.title else ""
            h1_tags = [h1.get_text().lower() for h1 in soup.find_all('h1')]
            
            # Placeholder for your specific keyword matching logic.
            # Assuming it evaluates to False if explicit product terms are missing.
            page_text = title + " ".join(h1_tags)
            if "product" in page_text or "shoes" in page_text: # Example condition
                has_category_keywords = True
                
    except Exception as e:
        return {
            "id": "F-003-ERR",
            "title": "Category Audit Failed",
            "severity": "medium",
            "evidence": f"Failed to fetch page data: {str(e)}",
            "suggested_action": {
                "summary": "Ensure URL is accessible to crawling bots.",
                "priority": "medium"
            }
        }

    # 3. Apply Context-Aware Routing Logic
    if not has_category_keywords:
        if is_homepage:
            # The Adaptive Warning for Homepages
            return {
                "id": "F-003-A",
                "title": "Homepage Semantic Ambiguity",
                "severity": "medium", 
                "evidence": f"URL {url} is a root homepage missing explicit product keywords.",
                "suggested_action": {
                    "summary": "Context Rule: If this is a multi-category marketplace, broad thematic messaging is acceptable. If this is a single-category brand, you must inject your core product type into the H1 for AI discoverability.",
                    "priority": "medium"
                }
            }
        else:
            # The Strict Error for specific product pages
            return {
                "id": "F-003",
                "title": "Category-Level Semantic Omission",
                "severity": "high",
                "evidence": "Missing critical explicit category terms in <title> and <h1>.",
                "suggested_action": {
                    "summary": "Incorporate explicit category entity terms into primary HTML headings.",
                    "priority": "high"
                }
            }
    
    # 4. Pass Condition
    return {
        "id": "P-003",
        "title": "Category Semantics Passed",
        "severity": "low",
        "evidence": "Explicit category keywords found in primary HTML elements.",
        "suggested_action": {
            "summary": "Maintain current semantic HTML structure.",
            "priority": "low"
        }
    }

if __name__ == "__main__":
    import json
    # Quick local test for a homepage
    print(json.dumps(audit_category_signals("https://www.myntra.com/"), indent=2))