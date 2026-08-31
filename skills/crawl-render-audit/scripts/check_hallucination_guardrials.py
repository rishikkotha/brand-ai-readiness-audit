import requests
from bs4 import BeautifulSoup
import json

def audit_hallucination_guardrails(url):
    """
    Audits the page for strict structured constraints (tables) and explicit 
    negative constraints to prevent LLMs from hallucinating missing features.
    """
    headers = {'User-Agent': 'Mozilla/5.0 (AI Readiness Auditor)'}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return {"error": str(e), "severity": "high"}

    soup = BeautifulSoup(response.text, 'html.parser')
    page_text = soup.get_text().lower()

    # 1. Check for tabular specification data (Machine-readable constraints)
    has_tables = len(soup.find_all('table')) > 0

    # 2. Check for explicit negative constraints
    negative_phrases = [
        "does not include", 
        "not compatible with", 
        "excludes", 
        "what this is not",
        "not supported"
    ]
    has_negative_constraints = any(phrase in page_text for phrase in negative_phrases)

    # If the page lacks both strict tables and negative boundaries, it's vulnerable to LLM hallucination
    if not has_tables and not has_negative_constraints:
        return {
            "id": "F-005",
            "title": "Vulnerable to AI Feature Hallucination",
            "severity": "medium",
            "evidence": f"Scanned {url}; found 0 strict data tables and 0 explicit negative constraints ('does not include', etc.).",
            "suggested_action": {
                "summary": "Publish a strict 'Technical Specifications' matrix and an explicit 'What this is NOT' section to establish definitive negative constraints and prevent LLM hallucination.",
                "priority": "medium"
            }
        }

    return {
        "status": "Passed",
        "evidence": f"Guardrails found. Tabular data present: {has_tables}. Negative constraints present: {has_negative_constraints}."
    }

if __name__ == "__main__":
    test_url = "https://example.com"
    result = audit_hallucination_guardrails(test_url)
    print(json.dumps(result, indent=2))