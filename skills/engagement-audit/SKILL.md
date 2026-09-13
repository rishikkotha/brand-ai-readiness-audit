---
name: engagement-audit
description: Evaluates on-site engagement signals for visitors arriving from AI assistants — orientation, mobile-readiness, CTA clarity, and context retention.
allowed-tools: Bash(python:*) Read
---
# Engagement Audit

Evaluates on-site user experience signals for AI referrals by parsing fully JS-rendered HTML via headless Chromium. 

**Checks Performed:**
* **Primary Orientation (`E-001`)**: Confirms the presence of a descriptive `<h1>` tag in the rendered DOM to immediately orient arriving users.
* **Context Retention (`E-002`)**: Tests if the DOM changes dynamically when synthetic intent parameters are appended to the URL.
* **Mobile Viewport (`E-003`)**: Verifies the presence of mobile-responsive `<meta name="viewport">` configurations.
* **CTA Presence (`E-004`)**: Scans the rendered DOM for clear, recognizable conversion elements using lexical matching and structural CSS fallbacks.