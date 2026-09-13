# skills/crawl-render-audit/scripts/check_render_gap.py
import re

def audit_render_gap(static_html: str, rendered_html: str, render_success: bool = True) -> dict:
    if not render_success:
        return {
            "id": "C-002",
            "title": "Render Gap Analysis",
            "status": "finding",
            "severity": "medium",
            "evidence": {
                "render_status": "blocked_or_failed",
                "details": "Headless browser rendering failed (WAF, anti-bot challenge, or protocol error). Cannot calculate dynamic render gap."
            },
            "suggested_action": {
                "summary": "Dynamic rendering was blocked or failed during headless crawl. AI agents and search bots relying on browser execution may fail to index client-side content.",
                "priority": "medium"
            }
        }

    # Normal render-gap comparison when rendering succeeded
    static_text = re.sub(r"<[^>]+>", " ", static_html or "").split()
    rendered_text = re.sub(r"<[^>]+>", " ", rendered_html or "").split()
    
    len_static = len(static_text)
    len_rendered = len(rendered_text)

    if len_rendered == 0:
        return {
            "id": "C-002",
            "title": "Render Gap Analysis",
            "status": "pass",
            "evidence": {"details": "No rendered content to evaluate."}
        }

    gap = max(0.0, (len_rendered - len_static) / len_rendered)

    if gap > 0.35:
        return {
            "id": "C-002",
            "title": "Render Gap Analysis",
            "status": "finding",
            "severity": "high",
            "evidence": {"static_word_count": len_static, "rendered_word_count": len_rendered, "render_gap_pct": round(gap * 100, 1)},
            "suggested_action": {
                "summary": f"Substantial client-side render gap detected ({round(gap * 100, 1)}%). Move critical product and brand content to static SSR.",
                "priority": "high"
            }
        }

    return {
        "id": "C-002",
        "title": "Render Gap Analysis",
        "status": "pass",
        "evidence": {"static_word_count": len_static, "rendered_word_count": len_rendered, "render_gap_pct": round(gap * 100, 1)}
    }