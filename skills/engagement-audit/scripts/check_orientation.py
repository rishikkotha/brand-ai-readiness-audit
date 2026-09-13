from bs4 import BeautifulSoup

def audit_orientation(rendered_html):
    if not rendered_html:
        return {"status": "error", "error": "Orientation Check: No rendered HTML provided."}
    
    soup = BeautifulSoup(rendered_html, "html.parser")
    h1_tags = soup.find_all("h1")

    if not h1_tags:
        return {
            "id": "E-001",
            "title": "Missing Primary Orientation (H1)",
            "status": "finding",
            "severity": "high",
            "evidence": "Scanned fully rendered DOM; found 0 <h1> tags.",
            "suggested_action": {
                "summary": "Add a descriptive <h1> tag to instantly orient users arriving from AI referrals.",
                "priority": "high"
            }
        }
        
    return {
        "id": "E-001",
        "title": "Primary Orientation (H1) Present",
        "status": "pass",
        "evidence": f"Found {len(h1_tags)} <h1> tag(s)."
    }