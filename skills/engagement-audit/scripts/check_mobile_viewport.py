from bs4 import BeautifulSoup

def audit_mobile_viewport(static_html):
    if not static_html: return {"status": "error", "error": "Viewport: No static HTML."}
    soup = BeautifulSoup(static_html, 'html.parser')
    
    if soup.find('meta', attrs={'name': 'viewport'}):
        return {"id": "E-003", "title": "Mobile Viewport Configured", "status": "pass", "evidence": "Found valid <meta name=\"viewport\"> tag."}
        
    return {
        "id": "E-003", "title": "Missing Mobile Viewport", "status": "finding", "severity": "high", 
        "evidence": "No viewport meta tag found. AI platforms frequently refer traffic via mobile apps.", 
        "suggested_action": {"summary": "Add <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">.", "priority": "high"}
    }