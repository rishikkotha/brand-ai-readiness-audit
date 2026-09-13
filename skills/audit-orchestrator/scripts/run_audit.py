# skills/audit-orchestrator/scripts/run_audit.py
import sys
import os
import json
import argparse
import requests
import urllib.robotparser
from urllib.parse import urlparse
from datetime import datetime, timezone
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../crawl-render-audit/scripts')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../engagement-audit/scripts')))

from check_structured_data import audit_json_ld
from check_render_gap import audit_render_gap
from check_category_signals import audit_category_signals
from check_freshness import audit_freshness_signals
from check_orientation import audit_orientation
from check_context_retention import audit_context_retention
from check_hallucination_guardrails import audit_hallucination_guardrails
from check_mobile_viewport import audit_mobile_viewport
from check_cta_presence import audit_cta_presence
from check_corroboration import audit_corroboration

def can_fetch(url, user_agent="AI-Readiness-Auditor/1.0"):
    try:
        parsed = urlparse(url)
        rp = urllib.robotparser.RobotFileParser()
        rp.set_url(f"{parsed.scheme}://{parsed.netloc}/robots.txt")
        rp.read()
        return rp.can_fetch(user_agent, url)
    except Exception:
        return True

def fetch_payloads(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 (compatible; AI-Readiness-Auditor/1.0)"
    }
    static_html = ""
    rendered_html = ""
    response_headers = {}
    render_success = False
    
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        static_html, response_headers = resp.text, resp.headers
    except Exception:
        pass

    try:
        with sync_playwright() as p:
            is_render = os.environ.get('RENDER') == 'true'
            browser = p.chromium.launch(
                headless=True,
                args=['--disable-dev-shm-usage', '--no-sandbox', '--single-process', '--js-flags="--max-old-space-size=256"'] if is_render else []
            )
            try:
                page = browser.new_page()
                page.goto(url, wait_until="domcontentloaded", timeout=20000)
                try:
                    page.wait_for_load_state("networkidle", timeout=15000)
                except PlaywrightTimeoutError:
                    pass
                rendered_html = page.content()
                render_success = True
            finally:
                if 'page' in locals(): page.close()
                if 'browser' in locals(): browser.close()
    except Exception as e:
        print(f"\n[DEBUG] Playwright render failed: {str(e)}", file=sys.stderr)
        rendered_html = static_html
        render_success = False

    return static_html, rendered_html, response_headers, render_success

def run_orchestrator(url):
    report = {
        "site": url,
        "audited_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "summary": {"total_findings": 0, "critical": 0, "high": 0, "medium": 0, "low": 0},
        "findings": [],
        "passes": [],
        "proactive_suggestions": [],
        "pending_agent_synthesis": [],
        "errors": []
    }

    if not can_fetch(url):
        report["errors"].append({"status": "error", "error": f"Robots.txt blocked crawling for {url}"})
        return report

    static_html, rendered_html, response_headers, render_success = fetch_payloads(url)

    audits = [
        audit_json_ld(static_html, rendered_html),
        audit_render_gap(static_html, rendered_html, render_success=render_success),
        audit_category_signals(rendered_html),
        audit_freshness_signals(url, static_html, response_headers),
        audit_orientation(rendered_html),
        audit_context_retention(url, static_html),
        audit_hallucination_guardrails(static_html, url=url),
        audit_mobile_viewport(static_html),
        audit_cta_presence(rendered_html),
        audit_corroboration(url, static_html)
    ]
    
    for result in audits:
        if not isinstance(result, dict):
            continue
        status = result.get("status")
        
        if result.get("requires_agent_synthesis"):
            report["pending_agent_synthesis"].append(result)
        elif status == "finding":
            report["findings"].append(result)
            sev = result.get("severity", "low").lower()
            if sev in report["summary"]:
                report["summary"][sev] += 1
        elif status == "pass":
            report["passes"].append(result)
        elif status == "suggestion":
            report["proactive_suggestions"].append(result)
        elif status == "error" or "error" in result:
            report["errors"].append(result)

    report["summary"]["total_findings"] = len(report["findings"])
    return report

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("url", help="Target URL")
    args = parser.parse_args()
    print(json.dumps(run_orchestrator(args.url), indent=2))