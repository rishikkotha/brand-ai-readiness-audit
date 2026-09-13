import requests
from bs4 import BeautifulSoup

def audit_context_retention(url, static_html=None):
    headers = {"User-Agent": "Mozilla/5.0 (compatible; AI-Readiness-Auditor/1.0)"}
    param_url = url + ("&" if "?" in url else "?") + "intent=ai_referral"
    
    try:
        # 1. Use the pre-fetched static_html if provided, otherwise fetch it manually
        if static_html:
            html_base = static_html
        else:
            r1 = requests.get(url, headers=headers, timeout=10)
            html_base = r1.text
            
        # 2. We always must fetch the parameterized URL to test for dynamic DOM changes
        r2 = requests.get(param_url, headers=headers, timeout=10)
        html_param = r2.text
        
        s1 = BeautifulSoup(html_base, 'html.parser')
        s2 = BeautifulSoup(html_param, 'html.parser')
        
        h1_1 = s1.find('h1').text.strip() if s1.find('h1') else ""
        h1_2 = s2.find('h1').text.strip() if s2.find('h1') else ""
        
        if h1_1 and (h1_1 != h1_2):
            return {
                "id": "E-002", "title": "Dynamic Context Retention Active", "status": "pass", 
                "evidence": "Detected DOM (H1) changes when URL parameters are present."
            }
            
        return {
            "id": "E-002", "title": "Static Context Retention", "status": "suggestion",
            "evidence": "DOM (H1 tags) did not change when a synthetic ?intent= parameter was appended. (Informational)",
            "suggested_action": {"summary": "Consider configuring landing pages to dynamically parse AI-driven URL parameters to reflect user intent.", "priority": "low"}
        }
    except Exception as e:
        return {"status": "error", "error": f"Context Retention Check Failed: {str(e)}"}