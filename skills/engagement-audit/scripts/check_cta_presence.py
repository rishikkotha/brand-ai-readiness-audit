import re
from bs4 import BeautifulSoup

CONVERSION_VERBS = re.compile(
    r"\b(get started|start free|free trial|book a demo|request demo|schedule (a )?demo|"
    r"schedule (a )?call|try for free|sign up|join (now|waitlist)|talk to sales|"
    r"buy now|contact sales|get a quote|create account|get felix|get fello|start now)\b",
    re.I
)

STRICT_CTA_CLASSES = re.compile(
    r"\b(cta|primary-cta|hero-cta|btn-cta|conversion-btn|conversion)\b",
    re.I
)

NAV_EXCLUSIONS = {
    "close", "cancel", "dismiss", "x", "pricing", "blog", "careers", "about",
    "about us", "features", "resources", "docs", "documentation", "login",
    "log in", "customer stories", "case studies", "terms", "privacy policy"
}

def clean_and_dedupe_label(text: str) -> str:
    cleaned = re.sub(r"\s+", " ", text or "").strip()
    words = cleaned.split()
    
    # Deduplicate duplicated responsive spans (e.g. "Sign in Sign in" -> "Sign in")
    if len(words) >= 2 and len(words) % 2 == 0:
        mid = len(words) // 2
        if [w.lower() for w in words[:mid]] == [w.lower() for w in words[mid:]]:
            cleaned = " ".join(words[:mid])
            
    return cleaned

def audit_cta_presence(rendered_html: str) -> dict:
    if not rendered_html:
        return {
            "id": "E-004",
            "title": "AI Referral Conversion Handoff (CTAs)",
            "status": "finding",
            "severity": "high",
            "evidence": {"found_ctas": [], "count": 0},
            "suggested_action": {
                "summary": "No rendered DOM available to evaluate AI referral conversion targets.",
                "priority": "high"
            }
        }

    soup = BeautifulSoup(rendered_html, "html.parser")
    candidate_elements = soup.find_all(["a", "button", "input"])
    
    detected_ctas = []
    seen_labels = set()

    for el in candidate_elements:
        if el.name == "input" and el.get("type") in ("button", "submit", "reset"):
            raw_text = el.get("value", "")
        else:
            # Use space separator so nested tags don't concatenate into 'Sign inSign in'
            raw_text = el.get_text(separator=" ", strip=True)

        label = clean_and_dedupe_label(raw_text)
        label_lower = label.lower()

        if len(label) < 2 or len(label) > 50:
            continue

        if label_lower in NAV_EXCLUSIONS or label_lower.startswith("why "):
            continue

        classes = " ".join(el.get("class", [])) if el.get("class") else ""
        has_conversion_verb = bool(CONVERSION_VERBS.search(label))
        has_strict_cta_class = bool(STRICT_CTA_CLASSES.search(classes))

        if has_conversion_verb or has_strict_cta_class:
            if label_lower not in seen_labels:
                seen_labels.add(label_lower)
                detected_ctas.append(label)

    count = len(detected_ctas)

    if count > 0:
        sample_str = ", ".join([f"'{c}'" for c in detected_ctas[:3]])
        return {
            "id": "E-004",
            "title": "AI Referral Conversion Handoff (CTAs)",
            "status": "pass",
            "evidence": f"Found {count} distinct conversion target(s) for AI-referred users (e.g., {sample_str})."
        }

    return {
        "id": "E-004",
        "title": "AI Referral Conversion Handoff (CTAs)",
        "status": "finding",
        "severity": "medium",
        "evidence": {"found_ctas": [], "count": 0},
        "suggested_action": {
            "summary": "No primary conversion targets detected. AI assistants referring traffic lack unambiguous landing destinations for users.",
            "priority": "medium"
        }
    }