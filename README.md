# Brand AI-Readiness Audit Marketplace

## Overview
This package is an Agent Skill Marketplace designed to audit target websites for AI discoverability and on-site engagement roadblocks. The system operates strictly read-only and emits a prioritized JSON audit report detailing technical findings and actionable recommendations.

## Architecture & Composition
The marketplace is orchestrated via the root `marketplace.json` manifest, designating a single entrypoint skill that coordinates specialized sub-skills[cite: 1]:

* **`audit-orchestrator` (Entrypoint):** Receives the audit request, triggers the sub-skill auditing routines, computes severity totals, and formats the output into the required JSON report schema[cite: 1].
* **`crawl-render-audit` (Sub-Skill):** Performs read-only technical inspections on the target URL[cite: 1], specifically auditing:
  * **Structured Data:** Scans the DOM for Schema.org / JSON-LD markup to verify explicit fact readability for AI engines[cite: 1].
  * **Client-Side Rendering Gaps:** Compares raw static HTML against rendered DOM text volume using Playwright to detect content hidden behind client-side JavaScript execution[cite: 1].
## Execution steps 
Install python dependencies:- 
pip install requests beautifulsoup4 playwright
playwright install chromium

Run audit:-
python skills/audit-orchestrator/scripts/run_audit.py
