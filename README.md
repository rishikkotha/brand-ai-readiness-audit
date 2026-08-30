# Brand AI-Readiness Audit Marketplace

## Overview
This Agent Skill Marketplace acts as an automated health inspector for Generative Engine Optimization (GEO). It audits websites to detect technical roadblocks that prevent AI assistants (like ChatGPT, Gemini, or Claude) from discovering, trusting, and citing the brand, as well as on-site engagement flaws that cause human visitors to bounce.

The system operates entirely read-only, mapping directly to the Round 2 Hackathon Failure Modes: **Visibility**, **Staleness**, and **Engagement**.

## Architecture & Composition
The marketplace is orchestrated via the root `marketplace.json` manifest, designating a single entrypoint that coordinates specialized sub-skills:

* **`audit-orchestrator` (Entrypoint):** Receives the audit request, sequentially triggers all discoverability and engagement sub-skills, computes severity totals, and formats a unified JSON report with proactive recommendations.
* **`crawl-render-audit` (Sub-Skill):** Performs off-site discoverability inspections.
* **`engagement-audit` (Sub-Skill):** Evaluates on-site user retention and structural orientation.

## Key Features & Audit Checks

### 1. Off-Site Discoverability (`crawl-render-audit`)
* **Machine Readability (Render Gap):** Uses Playwright to compare static HTML against dynamic DOM renders, ensuring core facts aren't trapped behind client-side JavaScript.
* **Structured Data:** Scans for Schema.org / JSON-LD markup to ensure explicit fact readability.
* **Category Omission:** Analyzes `<title>`, `<h1>`, and metadata for semantic category signals so the brand ranks for broad AI queries (e.g., "best running shoes").
* **Fact Staleness:** Checks backend HTTP headers (`Last-Modified`) and frontend HTML (`<time>`) to ensure AI models flush cached, outdated facts (like old logos or prices).

### 2. On-Site Engagement (`engagement-audit`)
* **Context Retention:** Dynamically injects AI-simulated search intent parameters (e.g., `?intent=...`) into the URL to test if the landing page adapts, preventing bounce risks.
* **Structural Orientation:** Verifies the presence of primary orientation headers (`<h1>`) so incoming visitors immediately know they are in the right place.

## Installation & Setup
Ensure you have Python 3.8+ installed.

1. **Install standard dependencies:**
   ```bash
   pip install requests beautifulsoup4 playwright