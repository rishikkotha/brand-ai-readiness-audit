# skills/engagement-audit/scripts/check_hallucination_guardrails.py
import re
import json
from urllib.parse import urlparse

def audit_hallucination_guardrails(static_html: str, url: str = None) -> dict:
    # 1. Check for physical HTML tables or definition lists
    has_tables = "<table" in (static_html or "").lower()
    has_dl = "<dl" in (static_html or "").lower()
    
    if has_tables or has_dl:
        return {
            "id": "F-005",
            "title": "Tabular Fact Disambiguation",
            "status": "pass",
            "evidence": {"has_tables": has_tables, "has_dl": has_dl}
        }

    # 2. Schema mitigation: Check if structured facts exist in JSON-LD
    if static_html:
        json_ld_matches = re.findall(
            r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
            static_html,
            re.I | re.DOTALL
        )
        for block in json_ld_matches:
            try:
                data = json.loads(block.strip())
                types = []
                if isinstance(data, dict):
                    types.append(data.get("@type", ""))
                    if "@graph" in data and isinstance(data["@graph"], list):
                        types.extend([item.get("@type", "") for item in data["@graph"] if isinstance(item, dict)])
                elif isinstance(data, list):
                    types.extend([item.get("@type", "") for item in data if isinstance(item, dict)])

                recognized_schemas = {"product", "organization", "corporation", "faqpage", "dataset", "itemlist"}
                matched = [t for t in types if isinstance(t, str) and t.lower() in recognized_schemas]
                
                if matched:
                    return {
                        "id": "F-005",
                        "title": "Tabular Fact Disambiguation",
                        "status": "pass",
                        "evidence": {
                            "has_tables": False,
                            "has_dl": False,
                            "json_ld_mitigation": True,
                            "matched_types": matched
                        }
                    }
            except Exception:
                pass

    # 3. Fail-safe Homepage bypass (URL must be explicitly provided and non-empty)
    if url and isinstance(url, str) and url.strip():
        parsed_path = urlparse(url).path
        if parsed_path in ("", "/"):
            return {
                "id": "F-005",
                "title": "Tabular Fact Disambiguation",
                "status": "pass",
                "evidence": {
                    "has_tables": False,
                    "has_dl": False,
                    "context": "Homepage detected without tabular specs; structured catalog cards assumed."
                }
            }

    # 4. Flag deep specification/product pages lacking structured facts
    return {
        "id": "F-005",
        "title": "Tabular Fact Disambiguation",
        "status": "finding",
        "severity": "low",
        "evidence": {"has_tables": False, "has_dl": False},
        "suggested_action": {
            "summary": "Key specifications lack tabular containment (<table>, <dl>) or explicit JSON-LD entity schemas. Unstructured key-value pairs risk extraction hallucinations.",
            "priority": "low"
        }
    }