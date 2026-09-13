import re
from bs4 import BeautifulSoup

def clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()

def audit_category_signals(rendered_html: str) -> dict:
    if not rendered_html:
        return {
            "id": "C-003",
            "title": "Category Signal Explicitness",
            "status": "pending",
            "requires_agent_synthesis": True,
            "evidence": {"error": "No rendered HTML available"},
            "suggested_action": {
                "summary": "AGENT INSTRUCTION: Evaluate category signals from domain name.",
                "priority": "medium"
            }
        }

    soup = BeautifulSoup(rendered_html, "html.parser")

    title = clean_text(soup.title.string) if soup.title and soup.title.string else ""
    meta_tag = soup.find("meta", attrs={"name": re.compile(r"description", re.I)})
    meta_desc = clean_text(meta_tag.get("content", "")) if meta_tag else ""

    raw_headings = [clean_text(h.get_text(separator=" ", strip=True)) for h in soup.find_all(["h1", "h2"])]
    
    # Deduplicate while preserving document order
    seen_headings = set()
    unique_headings = []
    for h in raw_headings:
        if h and len(h) > 5 and h.lower() not in seen_headings:
            seen_headings.add(h.lower())
            unique_headings.append(h)

    return {
        "id": "C-003",
        "title": "Category Signal Explicitness",
        "status": "pending",
        "requires_agent_synthesis": True,
        "evidence": {
            "title": title,
            "meta_description": meta_desc,
            "headings": unique_headings[:6]
        },
        "suggested_action": {
            "summary": "AGENT INSTRUCTION: Read the extracted title, meta, and headings. If the site clearly states its category/product, overwrite status to 'pass'. If it relies on vague marketing fluff, overwrite status to 'finding' and assign a severity.",
            "priority": "medium"
        }
    }