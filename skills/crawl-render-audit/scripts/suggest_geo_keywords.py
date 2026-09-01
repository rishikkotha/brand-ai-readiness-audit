import re
from collections import Counter
import requests
from bs4 import BeautifulSoup
import json

def suggest_geo_keywords(url):
    headers = {'User-Agent': 'Mozilla/5.0 (AI Readiness Auditor)'}
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return {"error": f"Keyword Extractor Failed: {str(e)}", "severity": "medium"}

    soup = BeautifulSoup(response.text, 'html.parser')

    # STEP 1: ANALYZE THE WEBSITE'S CONTEXT (Title & Meta)
    title_tag = soup.title.string.strip() if soup.title else "Unknown Site"
    meta_desc_tag = soup.find('meta', attrs={'name': 'description'})
    meta_desc = meta_desc_tag['content'].strip() if meta_desc_tag else "No description provided."

    # STEP 2: EXTRACT CORE THEMES FROM MAIN CONTENT
    main_content = soup.find('main') or soup.find('body')
    if main_content:
        # Destroy marketing fluff and navigation before reading
        for element in main_content.find_all(['nav', 'footer', 'header', 'button', 'script', 'style']):
            element.decompose()
        text = main_content.get_text(separator=' ').lower()
    else:
        text = soup.get_text(separator=' ').lower()

    # Find words 4 letters or longer
    words = re.findall(r'\b[a-z]{4,}\b', text)

    # Aggressive filter for SaaS fluff and standard English
    stop_words = {
        "this", "that", "with", "from", "your", "what", "about", "which", "their", 
        "they", "there", "more", "when", "call", "ready", "email", "buyer", "market", 
        "book", "demo", "contact", "click", "start", "free", "platform", "solution", 
        "software", "team", "sales", "help", "time", "work", "make"
    }
    
    meaningful_words = [w for w in words if w not in stop_words]
    word_counts = Counter(meaningful_words)
    
    # Grab the top 2 distinct themes
    top_themes = [word for word, count in word_counts.most_common(2)]
    
    # Fallbacks in case the site is completely empty
    primary_theme = top_themes[0] if len(top_themes) > 0 else "product"
    secondary_theme = top_themes[1] if len(top_themes) > 1 else "industry"

    # STEP 3: SYNTHESIZE THE ANALYSIS
    analysis_summary = f"Site Context Detected: Title indicates '{title_tag[:60]}...'. Primary text focuses on '{primary_theme}' and '{secondary_theme}'."

    # STEP 4: GENERATE CONVERSATIONAL GEO KEYWORDS
    # AI models match user questions to FAQ answers, not just random keywords.
    geo_suggestions = [
        f"best {primary_theme}",
        f"{primary_theme} {secondary_theme}",
        f"top {secondary_theme} tools",
        f"{primary_theme} features"
    ]

    return {
        "id": "O-001",
        "title": "GEO Keyword Opportunities",
        "severity": "medium",
        "evidence": analysis_summary,
        "suggested_action": {
            "summary": f"Inject these exact-match semantic keywords into your <h2> tags, product descriptions, and metadata to improve AI discoverability: {', '.join(geo_suggestions)}",
            "priority": "medium"
        }
    }

if __name__ == "__main__":
    print(json.dumps(suggest_geo_keywords("https://fello.ai"), indent=2))