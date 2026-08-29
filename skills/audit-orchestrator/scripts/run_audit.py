import sys
import os
import json
from datetime import datetime, timezone

# Add the sub-skill scripts folder to the system path so we can trigger them
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../crawl-render-audit/scripts')))

from check_structured_data import audit_json_ld
from check_render_gap import audit_render_gap

def run_orchestrator(url):
    findings = []
    
    # 1. Trigger the sub-skills
    ld_result = audit_json_ld(url)
    if "id" in ld_result:  # It's a recorded problem, not just a "Passed" status
        findings.append(ld_result)
        
    render_result = audit_render_gap(url)
    if "id" in render_result:
        findings.append(render_result)

    # 2. Calculate summary counts for the final report
    severity_counts = {"critical": 0, "high": 0, "medium": 0}
    for finding in findings:
        sev = finding.get("severity", "medium")
        if sev in severity_counts:
            severity_counts[sev] += 1

    # 3. Assemble the final required audit report schema
    report = {
        "site": url,
        "audited_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "summary": {
            "total_findings": len(findings),
            "critical": severity_counts["critical"],
            "high": severity_counts["high"],
            "medium": severity_counts["medium"]
        },
        "findings": findings
    }
    
    return report

if __name__ == "__main__":
    target_url = "https://example.com"
    final_report = run_orchestrator(target_url)
    print(json.dumps(final_report, indent=2))