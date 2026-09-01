from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import json

def audit_json_ld(url):
    schemas_found = []
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            # 1. Use a 60-second timeout and wait for the network to settle 
            # so JavaScript has time to inject the Schema/FAQs
            page.goto(url, wait_until="networkidle", timeout=60000)
            
            # 2. Search the fully rendered DOM for JSON-LD blocks
            script_tags = page.locator('script[type="application/ld+json"]').all_inner_texts()
            
            for text in script_tags:
                try:
                    data = json.loads(text)
                    # Handle both single schema objects and arrays of schemas
                    if isinstance(data, list):
                        schemas_found.extend([item.get('@type') for item in data if '@type' in item])
                    elif '@type' in data:
                        schemas_found.append(data['@type'])
                except json.JSONDecodeError:
                    continue
                    
            browser.close()
            
    except PlaywrightTimeoutError:
         return {
            "id": "F-001-ERR",
            "title": "Schema Crawl Timeout",
            "severity": "medium",
            "evidence": f"Failed to load {url} in time to check for JSON-LD.",
            "suggested_action": {
                "summary": "Ensure the site does not have an infinite loading loop blocking crawlers.",
                "priority": "medium"
            }
        }
    except Exception as e:
         return {
            "id": "F-001-ERR",
            "title": "Schema Crawl Error",
            "severity": "medium",
            "evidence": f"Error during schema extraction: {str(e)}",
            "suggested_action": {
                "summary": "Check server configuration.",
                "priority": "medium"
            }
        }

    # 3. Dynamic Return Logic
    if schemas_found:
        # Clean up the list to remove duplicates
        unique_schemas = list(set([str(s) for s in schemas_found if s]))
        return {
            "id": "P-001",
            "title": "Structured Data Detected",
            "severity": "low",
            "evidence": f"Detected JavaScript-injected schemas after render: {', '.join(unique_schemas)}",
            "suggested_action": {
                "summary": "Maintain current JSON-LD data structure. Ensure FAQPage and Product schemas are included.",
                "priority": "low"
            }
        }
    else:
        return {
            "id": "F-001",
            "title": "No JSON-LD structured data found",
            "severity": "high",
            "evidence": f"Scanned {url} after full JavaScript render; 0 schema.org tags detected.",
            "suggested_action": {
                "summary": "Add Organization, FAQPage, or Product JSON-LD markup to explicitly define facts for AI crawlers.",
                "priority": "high"
            }
        }

if __name__ == "__main__":
    # Test it locally against Fello AI
    print(json.dumps(audit_json_ld("https://fello.ai"), indent=2))