import json
from bs4 import BeautifulSoup

def extract_json_ld(html_content):
    if not html_content: 
        return []
        
    soup = BeautifulSoup(html_content, 'html.parser')
    schemas = []
    
    for script in soup.find_all('script', type='application/ld+json'):
        try: 
            schemas.append(json.loads(script.string))
        except (json.JSONDecodeError, TypeError): 
            pass
            
    return schemas

def audit_json_ld(static_html, rendered_html):
    if not static_html and not rendered_html:
        return {
            "status": "error", 
            "error": "No HTML payloads provided for JSON-LD check."
        }
        
    static_ld = extract_json_ld(static_html)
    rendered_ld = extract_json_ld(rendered_html)

    if not static_ld and not rendered_ld:
        return {
            "id": "C-001", 
            "title": "Missing Structured Data", 
            "status": "finding", 
            "severity": "high",
            "evidence": "No application/ld+json schema found in either static or rendered HTML.",
            "suggested_action": {
                "summary": "Implement JSON-LD structured data so AI crawlers can definitively understand entities.", 
                "priority": "high"
            }
        }
    
    if not static_ld and rendered_ld:
        return {
            "id": "C-001", 
            "title": "Client-Side Only Structured Data", 
            "status": "finding", 
            "severity": "medium",
            "evidence": "JSON-LD schema was only found after JavaScript rendering. Static crawlers will miss it.",
            "suggested_action": {
                "summary": "Move JSON-LD injection to the server (SSR) so it exists in the initial static HTML payload.", 
                "priority": "medium"
            }
        }

    return {
        "id": "C-001", 
        "title": "Static Structured Data Present", 
        "status": "pass", 
        "evidence": f"Found {len(static_ld)} JSON-LD schema(s) natively in the static payload."
    }