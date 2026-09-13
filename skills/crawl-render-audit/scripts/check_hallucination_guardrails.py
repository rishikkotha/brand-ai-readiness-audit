# skills/engagement-audit/scripts/check_hallucination_guardrails.py
import re
import json

def audit_hallucination_guardrails(static_html: str, url: str = None) -> dict:
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

    plain_text = re.sub(r"<[^>]+>", " ", static_html or "")
    plain_text = re.sub(r"\s+", " ", plain_text).strip()

    spec_like_matches = re.findall(
        r"\$\d[\d,]*(?:\.\d+)?|\d+(?:\.\d+)?\s?(?:%|GB|TB|MB|Mbps|Gbps|kg|lb|oz|in|cm|mm|ms|fps|hrs?|hours?)\b",
        plain_text,
        re.I
    )

    return {
        "id": "F-005",
        "title": "Tabular Fact Disambiguation",
        "status": "pending",
        "requires_agent_synthesis": True,
        "evidence": {
            "has_tables": False,
            "has_dl": False,
            "json_ld_mitigation": False,
            "spec_like_fact_count": len(spec_like_matches),
            "spec_like_fact_sample": spec_like_matches[:8]
        },
        "suggested_action": {
            "summary": (
                "AGENT INSTRUCTION: No <table>, <dl>, or recognized JSON-LD entity schema was found. "
                "Read spec_like_fact_sample and the page's evident purpose. If the page states few or no "
                "specific numeric/spec facts (e.g. a marketing homepage with no pricing, dimensions, or "
                "quantitative claims), overwrite status to 'pass' — there is nothing here that needs "
                "disambiguation. If it states several such facts in plain prose with no structured "
                "containment (e.g. a pricing or specs page), overwrite status to 'finding' and assign a "
                "severity based on how many facts are at risk of extraction errors."
            ),
            "priority": "medium"
        }
    }