---
name: crawl-render-audit
description: Scans a target URL to identify client-side rendering roadblocks and missing explicit text signals that hurt AI discoverability.
---
# Crawl and Render Audit

## When to use
Invoked by the orchestrator to perform the technical extraction of page content.

## Inputs
A target website URL.

## Procedure
1. Execute the web scraping script.
2. Extract plain text and search for structured data.
3. Return identified roadblocks to the orchestrator.

## Output
Raw extraction metrics and identified rendering issues.