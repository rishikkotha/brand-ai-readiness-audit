import re
from collections import Counter
import requests
from bs4 import BeautifulSoup
import json

def suggest_geo_keywords(url):
    headers = {'User-Agent': 'Mozilla/5.0 (AI Readiness Auditor)'}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return {"error": f"Keyword Extractor Failed: {str(e)}", "severity": "medium"}

    # Extract text from the page
    soup = BeautifulSoup(response.text, 'html.parser')
    text = soup.get_text(separator=' ').lower()

    # Clean text and split into words
    words = re.findall(r'\b[a-z]{3,}\b', text)

    # Standard English stopwords to ignore
    stop_words = {
        "the", "and", "for", "with", "that", "this", "you", "are", "from", "not",
        "have", "has", "will", "can", "but", "all", "your", "what", "how", "about",
        "which", "their", "they", "was", "were", "there", "out", "more", "when"
    }
    
    # Filter and count meaningful words
    meaningful_words = [w for w in words if w not in stop_words]
    word_counts = Counter(meaningful_words)
    
   # Extract the top 5 most common themes
    top_themes = [word for word, count in word_counts.most_common(5)]
    
    # Grab the #1 most common word to build the core keyword clusters
    main_theme = top_themes[0] if top_themes else "product"
    
    # Generate AI-intent keyword clusters based on the main theme
    suggested_clusters = [f"best {main_theme} options", f"top rated {main_theme}", f"{main_theme} features and pricing"]

    return {
        "id": "O-001",
        "title": "GEO Keyword Opportunities",
        "severity": "medium",
        "evidence": f"Page naturally emphasizes: {', '.join(top_themes)}. However, AI queries rely on explicit user-intent phrasing.",
        "suggested_action": {
            "summary": f"Inject these exact-match semantic phrases into your <h2> tags and FAQ sections so AI models match your page to user prompts: {', '.join(suggested_clusters)}.",
            "priority": "medium"
        }
    }

if __name__ == "__main__":
    print(json.dumps(suggest_geo_keywords("https://en.wikipedia.org/wiki/Running_shoe"), indent=2))