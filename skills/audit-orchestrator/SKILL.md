---
name: audit-orchestrator
description: Entrypoint orchestrator that runs website discoverability and engagement audits, fetches content once, and coordinates LLM reasoning for checks a script alone can't judge. Use when auditing a website URL for AI-discoverability and engagement problems.
allowed-tools: Bash(python:*) Read
---
# Brand AI-Readiness Auditor (Orchestrator)

This is the primary entrypoint for the AI Readiness Audit marketplace. It executes a suite of Python scripts to evaluate a brand's off-site AI discoverability and on-site user engagement.

**Invocation:**
Run: `python skills/audit-orchestrator/scripts/run_audit.py <target_url>`

**CRITICAL AGENT PROTOCOL (Action Required):**
The orchestrator outputs a JSON report. You MUST review the `pending_agent_synthesis` array in this output. For every item in that array:
1. Read the `evidence` and the specific `suggested_action.summary` instructions.
2. Use your native reasoning to evaluate the evidence as requested (e.g., executing a web search or analyzing text semantics).
3. Overwrite the `status` (to 'pass', 'finding', or 'suggestion') and update the `severity` or `evidence` based on your analysis.
4. Move the synthesized item into the appropriate array (`findings`, `passes`, or `proactive_suggestions`).
5. Present the final, fully resolved JSON report to the user. Do NOT present unresolved `pending_agent_synthesis` items.