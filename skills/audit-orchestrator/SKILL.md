---
name: audit-orchestrator
description: Entrypoint skill that orchestrates the brand AI-readiness audit. Triggers sub-skills and outputs the final JSON report of findings and suggested actions.
---
# Audit Orchestrator

## When to use
Use this as the primary entrypoint when an audit request is received for a target URL.

## Inputs
A single target website URL.

## Procedure
1. Trigger the crawl-render-audit skill for the given URL.
2. Compile the returned data into the required JSON audit report schema.
3. Emit the final report.

## Output
A JSON report containing site metadata, a severity summary, findings, and suggested actions.