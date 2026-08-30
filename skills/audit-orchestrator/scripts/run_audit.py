import sys
import os
import json
from datetime import datetime, timezone

# Map the system paths to both sub-skill folders
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../crawl-render-audit/scripts')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../engagement-audit/scripts')))

# Import all six field inspectors
from check_structured_data import audit_json_ld
from check_render_gap import audit_render_gap
from check_category_signals import audit_category_signals
from check_freshness import audit_freshness_signals
from check_orientation import audit_orientation
from check_context_retention import audit_context_retention

def run_orchestrator(url):
    findings = []
    
    # 1. Trigger Discoverability Checks
    audits = [
        audit_json_ld(url),
        audit_render_gap(url),
        audit_category_signals(url),
        audit_freshness_signals(url),
        audit_orientation(url),
        audit_context_retention(url)
    ]
    
    # 2. Filter for actual issues (ignore "Passed" checks)
    for result in audits:
        if "id" in result or "error" in result:
            findings.append(result)

    # 3. Calculate Severity Totals
    severity_counts = {"critical": 0, "high": 0, "medium": 0}
    for finding in findings:
        sev = finding.get("severity", "medium")
        if sev in severity_counts:
            severity_counts[sev] += 1

    # 4. Inject Proactive Recommendations
    proactive_actions = [
        {
            "summary": "Even if orientation tags exist, ensure dynamic user context from AI referrals is explicitly retained on the landing page to minimize bounce risk.",
            "priority": "medium"
        }
    ]

    # 5. Assemble Final Schema
    report = {
        "site": url,
        "audited_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "summary": {
            "total_findings": len(findings),
            "critical": severity_counts["critical"],
            "high": severity_counts["high"],
            "medium": severity_counts["medium"]
        },
        "findings": findings,
        "proactive_suggestions": proactive_actions
    }
    
    return report

if __name__ == "__main__":
    target_url = "https://example.com"
    final_report = run_orchestrator(target_url)
    print(json.dumps(final_report, indent=2))