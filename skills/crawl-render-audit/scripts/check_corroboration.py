# skills/crawl-render-audit/scripts/check_corroboration.py
import re
from urllib.parse import urlparse

def audit_corroboration(url: str, static_html: str) -> dict:
    """
    C-006: Entity Corroboration & Ambiguity Check.
    Extracts brand/entity candidate and routes to downstream agent synthesis.
    """
    extracted_name = None

    if static_html:
        # Check <title> tag
        title_match = re.search(r"<title[^>]*>(.*?)</title>", static_html, re.IGNORECASE | re.DOTALL)
        if title_match:
            raw_title = title_match.group(1).strip()
            # Extract primary brand segment (e.g., before |, -, or :)
            parts = re.split(r"[\s\-_|:]+", raw_title)
            if parts and len(parts[0]) > 1:
                extracted_name = parts[0].strip()

        if not extracted_name:
            h1_match = re.search(r"<h1[^>]*>(.*?)</h1>", static_html, re.IGNORECASE | re.DOTALL)
            if h1_match:
                clean_h1 = re.sub(r"<[^>]+>", "", h1_match.group(1)).strip()
                if clean_h1:
                    extracted_name = clean_h1

    parsed_domain = urlparse(url).netloc


    if not extracted_name:
        domain_parts = parsed_domain.replace("www.", "").split(".")
        extracted_name = domain_parts[0].capitalize() if domain_parts else "Unknown Entity"

    return {
        "id": "C-006",
        "title": "Entity Corroboration & Ambiguity Check",
        "status": "pending",
        "requires_agent_synthesis": True,
        "evidence": {
            "candidate_entity_name": extracted_name,
            "domain": parsed_domain,
        },
        "suggested_action": {
            "summary": (
                "AGENT INSTRUCTION: Search the web for the extracted entity name. "
                "Judge whether (a) independent sources consistently describe the same brand/product, "
                "and (b) the name is ambiguous with unrelated entities sharing it. "
                "If ambiguous with no on-page disambiguation (e.g., founding year, location, category), "
                "flag as a finding."
            ),
            "priority": "medium",
        },
    }