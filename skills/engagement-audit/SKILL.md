---
name: engagement-audit
description: Audits a webpage for on-site bounce risks, focusing on structural orientation and context retention.
---
# Engagement Audit

## When to use
Invoked by the orchestrator to check if human visitors are likely to bounce due to poor page structure.

## Inputs
A target website URL.

## Procedure
1. Parse the static HTML.
2. Check for the presence of primary orientation headers (H1).
3. Return findings.

## Output
Raw extraction metrics and identified orientation issues formatted as JSON.