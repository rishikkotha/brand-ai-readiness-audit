# Brand AI-Readiness Audit Marketplace

## Overview
This Agent Skill Marketplace acts as an automated health inspector for Generative Engine Optimization (GEO). It audits websites to detect technical roadblocks that prevent AI assistants (like ChatGPT, Gemini, or Claude) from discovering, trusting, and citing the brand, as well as on-site engagement flaws that cause human visitors to bounce.

The system operates entirely read-only, mapping directly to the Round 2 Hackathon Failure Modes: **Visibility**, **Staleness**, and **Engagement**.

## Architecture & Composition
The marketplace is orchestrated via the root `marketplace.json` manifest, designating a single entrypoint that coordinates specialized sub-skills:

* **`audit-orchestrator` (Entrypoint):** Central controller. Fetches payloads once, routes schema data (`finding`, `pass`, `suggestion`), and enforces the agent-synthesis protocol for LLM reasoning.
* **`crawl-render-audit` (Sub-Skill):** Evaluates machine-readability (JSON-LD, Render Gaps, Freshness, Semantic Categories) and cross-source entity corroboration.
* **`engagement-audit` (Sub-Skill):** Evaluates on-site user experience (Mobile Viewport, CTA presence, H1 orientation, Context Retention).

## Key Features & Audit Checks

### 1. Off-Site Discoverability (`crawl-render-audit`)
* **Machine Readability (Render Gap):** Uses Playwright to compare static HTML against dynamic DOM renders, ensuring core facts aren't trapped behind client-side JavaScript.
* **Structured Data:** Scans for Schema.org / JSON-LD markup to ensure explicit fact readability.
* **Category Omission & GEO Keywords:** Analyzes structural semantics for agent-synthesized clarity scoring and generates conversational search intents.
* **Fact Staleness:** Checks backend HTTP headers (`Last-Modified`) and frontend HTML (`<time>`) and meta tags to ensure AI models flush cached, outdated facts.
* **Cross-Source Corroboration:** Analyzes entity-ambiguity risk via agent-delegated web searches (Appendix D).

### 2. On-Site Engagement (`engagement-audit`)
* **Context Retention:** Tests if the DOM changes dynamically when synthetic intent parameters are appended to the URL.
* **Structural Orientation:** Verifies the presence of primary orientation headers (`<h1>`) so incoming visitors immediately know they are in the right place.
* **Mobile Viewport:** Verifies the presence of mobile-responsive `<meta name="viewport">` configurations.
* **CTA Presence:** Scans the rendered DOM for clear, recognizable conversion elements using lexical matching and structural CSS fallbacks.

## Installation

Ensure you have Python 3.9+ installed.

```bash
pip install -r requirements.txt
playwright install chromium

**Usage**
Run the orchestrator against any target URL:
```bash
python skills/audit-orchestrator/scripts/run_audit.py [http://127.0.0.1:8901/index.html](http://127.0.0.1:8901/index.html)