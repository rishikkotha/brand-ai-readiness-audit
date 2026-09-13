---
name: crawl-render-audit
description: Evaluates a website's machine-readability for AI crawlers — structured data, JS-render gaps, staleness signals, and factual clarity — by comparing static and rendered HTML payloads.
allowed-tools: Bash(python:*) Read
---
# Crawl & Render Audit

Evaluates the machine-readability and semantic clarity of a website by parsing both static and JS-rendered payloads.

**Checks Performed:**
* **Structured Data (`C-001`)**: Detects `application/ld+json` schema natively in static vs. rendered HTML.
* **Render Gap (`C-002`)**: Compares static vs. JS-rendered payload size to flag severe client-side dependencies.
* **Category Signals (`C-003`)**: Extracts Title, Meta, and Headings for agent-synthesized clarity scoring.
* **Freshness (`C-004`)**: Evaluates temporal relevance via `Last-Modified` headers, `article:modified_time` meta tags, and HTML `<time>` tags.
* **Hallucination Guardrails (`F-005`)**: Scans for rigid factual bounding structures like data tables or definition lists.
* **Cross-Source Corroboration (`C-006`)**: Analyzes entity-ambiguity risk via agent-delegated web searches (Appendix D).