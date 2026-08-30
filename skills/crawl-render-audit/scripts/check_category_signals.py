import requests
from bs4 import BeautifulSoup
import json

def audit_category_signals(url, target_category_keywords=None):
    """
    Audits whether the page contains explicit category-level semantic signals
    in <title>, <meta description>, <h1>, and JSON-LD markup to prevent AI omission.
    """
    if target_category_keywords is None:
        # Default common category descriptor tokens if none provided
        target_category_keywords = ["product", "shop", "collection", "service", "pricing", "guide", "reviews"]

    headers = {'User-Agent': 'Mozilla/5.0 (AI Readiness Auditor)'}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return {"error": str(e), "severity": "high"}

    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 1. Extract high-priority semantic zones
    title_text = soup.title.string.lower() if soup.title and soup.title.string else ""
    meta_desc = ""
    meta_tag = soup.find('meta', attrs={'name': 'description'}) or soup.find('meta', attrs={'property': 'og:description'})
    if meta_tag and meta_tag.get('content'):
        meta_desc = meta_tag['content'].lower()
    
    h1_text = " ".join([h.get_text().lower() for h in soup.find_all('h1')])
    
    # 2. Check for explicit JSON-LD entity definitions
    json_ld_scripts = soup.find_all('script', type='application/ld+json')
    has_category_schema = False
    for script in json_ld_scripts:
        try:
            data = json.loads(script.string)
            # Check for standard e-commerce / service entity types
            types = ["Product", "ItemList", "CollectionPage", "OfferCatalog", "Organization", "LocalBusiness"]
            if any(t in str(data) for t in types):
                has_category_schema = True
                break
        except Exception:
            continue

    # 3. Analyze semantic coverage
    found_keywords = [kw for kw in target_category_keywords if kw in title_text or kw in meta_desc or kw in h1_text]
    
    if not has_category_schema and len(found_keywords) == 0:
        return {
            "id": "F-003",
            "title": "Category-Level Semantic Omission",
            "severity": "high",
            "evidence": f"Scanned {url}; missing explicit Category/Product Schema and semantic keywords in <title>, <h1>, and <meta description>.",
            "suggested_action": {
                "summary": "Incorporate explicit category entity terms into primary HTML headings and deploy Product/ItemList Schema.org markup to be surfaced in category-level AI queries.",
                "priority": "high"
            }
        }

    return {
        "status": "Passed",
        "evidence": f"Found valid entity Schema: {has_category_schema}, matched category descriptors: {len(found_keywords)}."
    }

if __name__ == "__main__":
    test_url = "https://example.com"
    result = audit_category_signals(test_url)
    print(json.dumps(result, indent=2))