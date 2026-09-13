from bs4 import BeautifulSoup

def audit_freshness_signals(url, static_html, response_headers):
    if not static_html:
        return {"status": "error", "error": "Freshness Check: No static HTML provided."}

    soup = BeautifulSoup(static_html, 'html.parser')
    is_article = bool(soup.find('article')) or ('blog' in url.lower()) or ('article' in url.lower())
    severity = "high" if is_article else "low"

    signals = []
    
    if response_headers and response_headers.get('Last-Modified'):
        signals.append("HTTP Last-Modified header")
        
    meta_tags = soup.find_all('meta', property=lambda x: x in ['article:modified_time', 'article:published_time'])
    if meta_tags:
        signals.append("article:modified_time meta tag")
        
    time_tags = soup.find_all('time')
    if time_tags:
        signals.append("<time> HTML tag")

    if signals:
        return {
            "id": "C-004",
            "title": "Temporal Freshness Signals Active",
            "status": "pass",
            "evidence": f"Detected freshness signals: {', '.join(signals)}."
        }

    return {
        "id": "C-004",
        "title": "Missing Freshness Signals",
        "status": "finding",
        "severity": severity,
        "evidence": "No Last-Modified header, article meta tags, or <time> elements detected.",
        "suggested_action": {
            "summary": "Add <time> tags or Last-Modified headers for AI indexing.",
            "priority": severity
        }
    }