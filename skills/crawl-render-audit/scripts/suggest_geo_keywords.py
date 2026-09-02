import os
import re
import json
from collections import Counter
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
# Playwright for JavaScript-rendered websites
from playwright.sync_api import (
    sync_playwright,
    TimeoutError as PlaywrightTimeoutError
)

STOP_WORDS = {
    "this", "that", "with", "from", "your", "what", "about",
    "which", "their", "they", "there", "more", "when", "where",
    "will", "would", "could", "should", "have", "has", "been",
    "were", "these", "those", "than", "then", "them",
    "into", "over", "under", "through", "using", "used",
    "only", "very", "just", "also", "some", "such", "each",
    "other", "many", "most", "much", "here", "ours", "our",
    "you", "who", "how", "why", "can", "get", "getting",
    "make", "made", "making", "take", "taking", "give", "given",
    "home", "about", "contact", "login", "signup", "sign",
    "register", "pricing", "careers", "blog", "learn", "read",
    "click", "start", "demo", "free", "today", "now",
    "platform", "solution", "solutions", "software", "service",
    "services", "product", "products", "business", "businesses",
    "company", "companies", "team", "teams", "customers",
    "customer", "users", "user", "people", "world", "future",
    "powerful", "simple", "easy", "better", "leading",
    "innovative", "modern", "seamless", "trusted", "designed",
    "built", "experience", "experiences", "help", "helps"
}


GENERIC_WORDS = {
    "things", "everything", "something", "anything",
    "experience", "solution", "solutions", "platform",
    "software", "service", "services", "product", "products",
    "business", "businesses", "company", "companies",
    "customers", "customer", "users", "user", "people",
    "powerful", "simple", "easy", "better", "great",
    "future", "world", "modern", "leading", "innovative",
    "seamless", "trusted", "quality", "best"
}


def clean_text(text):
    """Normalize text for analysis."""

    text = text.lower()
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def tokenize(text):
    """Extract meaningful alphabetic tokens."""

    return re.findall(
        r"\b[a-z]{3,}\b",
        text.lower()
    )

def extract_candidate_phrases(text):
    """
    Extract single words, bigrams and trigrams.

    Multi-word phrases are preferred because they are more
    likely to represent actual concepts than isolated words.
    """

    words = tokenize(text)

    filtered_words = [
        word
        for word in words
        if word not in STOP_WORDS
        and word not in GENERIC_WORDS
        and len(word) >= 3
    ]

    bigrams = []

    for i in range(len(filtered_words) - 1):

        first = filtered_words[i]
        second = filtered_words[i + 1]

        phrase = f"{first} {second}"

        if (
            first not in STOP_WORDS
            and second not in STOP_WORDS
            and len(phrase) >= 8
        ):
            bigrams.append(phrase)

    trigrams = []

    for i in range(len(filtered_words) - 2):

        first = filtered_words[i]
        second = filtered_words[i + 1]
        third = filtered_words[i + 2]

        phrase = f"{first} {second} {third}"

        if (
            first not in STOP_WORDS
            and second not in STOP_WORDS
            and third not in STOP_WORDS
        ):
            trigrams.append(phrase)

    return filtered_words, bigrams, trigrams



def score_candidates(words, bigrams, trigrams):
    """
    Score candidate concepts using frequency and phrase length.
    """

    word_counts = Counter(words)
    bigram_counts = Counter(bigrams)
    trigram_counts = Counter(trigrams)

    scores = {}

    for word, count in word_counts.items():

        if count < 2:
            continue

        scores[word] = scores.get(word, 0) + count

    for phrase, count in bigram_counts.items():

        if count < 1:
            continue

        scores[phrase] = (
            scores.get(phrase, 0)
            + count * 4
        )

    for phrase, count in trigram_counts.items():

        if count < 1:
            continue

        scores[phrase] = (
            scores.get(phrase, 0)
            + count * 6
        )

    ranked = sorted(
        scores.items(),
        key=lambda item: item[1],
        reverse=True
    )

    return ranked



def extract_heading_candidates(headings):
    """
    Headings receive higher semantic importance because they
    generally describe the main topics of a page.
    """

    heading_text = " ".join(headings)

    words, bigrams, trigrams = (
        extract_candidate_phrases(heading_text)
    )

    candidates = []

    word_counts = Counter(words)
    bigram_counts = Counter(bigrams)
    trigram_counts = Counter(trigrams)

    for phrase, count in trigram_counts.items():
        candidates.append(
            (phrase, count * 10)
        )

    for phrase, count in bigram_counts.items():
        candidates.append(
            (phrase, count * 8)
        )

    for word, count in word_counts.items():
        candidates.append(
            (word, count * 5)
        )

    return sorted(
        candidates,
        key=lambda item: item[1],
        reverse=True
    )



def is_valid_phrase(phrase):
    """
    Reject phrases that are unlikely to represent useful
    website concepts.
    """

    words = phrase.split()

    if len(phrase) < 4:
        return False

    if len(words) > 4:
        return False

    if not all(
        re.fullmatch(r"[a-z]+", word)
        for word in words
    ):
        return False

    if (
        len(words) == 1
        and words[0] in GENERIC_WORDS
    ):
        return False

    generic_count = sum(
        1
        for word in words
        if word in GENERIC_WORDS
    )

    if generic_count >= len(words):
        return False

    return True


def remove_redundant_candidates(
    candidates,
    limit=10
):
    """
    Remove duplicate and overly similar concepts.
    """

    selected = []

    for candidate in candidates:

        phrase = candidate.strip()

        if not is_valid_phrase(phrase):
            continue

        if phrase in selected:
            continue

        phrase_words = set(
            phrase.split()
        )

        redundant = False

        for existing in selected:

            existing_words = set(
                existing.split()
            )

            if (
                phrase_words.issubset(existing_words)
                and len(existing_words)
                > len(phrase_words)
            ):
                redundant = True
                break

        if redundant:
            continue

        selected.append(phrase)

        if len(selected) >= limit:
            break

    return selected


def extract_page_context(soup):
    """
    Extract high-value semantic page signals.
    """

    title = ""

    if soup.title and soup.title.string:
        title = soup.title.string.strip()

    meta_description = ""

    meta_tag = soup.find(
        "meta",
        attrs={"name": "description"}
    )

    if meta_tag:
        meta_description = meta_tag.get(
            "content",
            ""
        ).strip()

    headings = []

    for tag in soup.find_all(
        ["h1", "h2", "h3"]
    ):

        heading = tag.get_text(
            " ",
            strip=True
        )

        if heading:
            headings.append(heading)

    return {
        "title": title,
        "meta_description": meta_description,
        "headings": headings
    }



def extract_main_content(soup):
    """
    Extract useful page content while removing navigation,
    scripts and other irrelevant elements.
    """

    main = soup.find("main")

    if main is None:
        main = soup.find("body")

    if main is None:
        return ""

    for element in main.find_all([
        "nav",
        "footer",
        "header",
        "script",
        "style",
        "noscript",
        "svg",
        "button",
        "form"
    ]):
        element.decompose()

    return main.get_text(
        separator=" ",
        strip=True
    )



def detect_core_topics(
    context,
    body_text
):
    """
    Determine strong concepts using multiple semantic
    signals rather than raw word frequency alone.

    Signal priority:

        Title
        ↓
        Meta description
        ↓
        Headings
        ↓
        Main content
    """

    title = context["title"]
    meta = context["meta_description"]
    headings = context["headings"]


    (
        title_words,
        title_bigrams,
        title_trigrams
    ) = extract_candidate_phrases(title)


    (
        meta_words,
        meta_bigrams,
        meta_trigrams
    ) = extract_candidate_phrases(meta)


    heading_ranked = extract_heading_candidates(
        headings
    )


    (
        body_words,
        body_bigrams,
        body_trigrams
    ) = extract_candidate_phrases(body_text)

    body_ranked = score_candidates(
        body_words,
        body_bigrams,
        body_trigrams
    )


    weighted = Counter()

    for phrase in (
        title_trigrams
        + title_bigrams
        + title_words
    ):

        if is_valid_phrase(phrase):
            weighted[phrase] += 15

    for phrase in (
        meta_trigrams
        + meta_bigrams
        + meta_words
    ):

        if is_valid_phrase(phrase):
            weighted[phrase] += 10

    for phrase, score in heading_ranked:

        if is_valid_phrase(phrase):
            weighted[phrase] += score

    for phrase, score in body_ranked:

        if is_valid_phrase(phrase):
            weighted[phrase] += score

    ranked = sorted(
        weighted.items(),
        key=lambda item: item[1],
        reverse=True
    )

    return remove_redundant_candidates(
        [phrase for phrase, score in ranked],
        limit=10
    )



def generate_geo_opportunities(
    core_topics
):
    """
    Generate natural-language search intents.

    These are search opportunities, NOT instructions to
    insert exact-match keywords into the website.
    """

    if not core_topics:
        return []

    primary = core_topics[0]

    secondary = (
        core_topics[1]
        if len(core_topics) > 1
        else None
    )

    opportunities = []


    opportunities.append({
        "intent": "Discovery",
        "query": f"best {primary}",
        "reason": (
            "Targets users looking for leading options "
            "within the detected category or topic."
        )
    })


    opportunities.append({
        "intent": "Comparison",
        "query": f"{primary} alternatives",
        "reason": (
            "Targets users comparing competing solutions "
            "or different approaches."
        )
    })


    opportunities.append({
        "intent": "Features",
        "query": f"{primary} features",
        "reason": (
            "Targets users researching capabilities and "
            "functionality."
        )
    })

    opportunities.append({
        "intent": "Evaluation",
        "query": f"how to choose {primary}",
        "reason": (
            "Targets users evaluating options before "
            "making a decision."
        )
    })


    if secondary:

        opportunities.append({
            "intent": "Use case",
            "query": f"{primary} for {secondary}",
            "reason": (
                "Connects the primary topic with another "
                "relevant concept detected on the site."
            )
        })


    opportunities.append({
        "intent": "Problem solving",
        "query": f"how does {primary} work",
        "reason": (
            "Targets informational users trying to "
            "understand the category."
        )
    })


    opportunities.append({
        "intent": "FAQ",
        "query": f"what is {primary}",
        "reason": (
            "Creates an opportunity for the website to "
            "provide a concise definition of the topic."
        )
    })

    return opportunities


def validate_opportunities(
    opportunities
):
    """
    Remove obviously poor or repetitive suggestions.
    """

    validated = []
    seen = set()

    for item in opportunities:

        query = item["query"].strip().lower()

        if not query:
            continue

        if query in seen:
            continue

        if len(query.split()) < 3:
            continue

        words = query.split()

        if len(words) != len(set(words)):
            continue

        seen.add(query)

        validated.append(item)

    return validated



def suggest_geo_keywords(url):

    html_content = ""

    try:
        with sync_playwright() as p:
            # Check if running on Render's cloud environment
            is_render = os.environ.get('RENDER') == 'true'
            
            if is_render:
                # Aggressive memory limits to prevent 512MB RAM exhaustion
                browser = p.chromium.launch(
                    headless=True,
                    args=[
                        '--disable-dev-shm-usage', 
                        '--no-sandbox',             
                        '--disable-setuid-sandbox',
                        '--disable-gpu',            
                        '--single-process',         
                        '--js-flags="--max-old-space-size=256"' 
                    ]
                )
            else:
                # Standard setup for local Windows development
                browser = p.chromium.launch(headless=True)
                
            page = browser.new_page()
            page.goto(url, wait_until="networkidle", timeout=30000)
            html_content = page.content()
            
            # The 'with' context manager will automatically close 
            # the browser and release memory here.
            
    except PlaywrightTimeoutError:
        return {
            "error": f"Keyword Extractor Failed: Timeout waiting for {url} to fully render JavaScript.",
            "severity": "medium"
        }
    except Exception as e:
        return {
            "error": f"Keyword Extractor Failed: {str(e)}",
            "severity": "medium"
        }

    if not html_content:

        return {
            "error": (
                "Keyword Extractor Failed: "
                "No HTML content was returned."
            ),
            "severity": "medium"
        }

    soup = BeautifulSoup(
        html_content,
        "html.parser"
    )


    context = extract_page_context(
        soup
    )


    body_text = extract_main_content(
        soup
    )

    body_text = clean_text(
        body_text
    )


    core_topics = detect_core_topics(
        context,
        body_text
    )


    opportunities = generate_geo_opportunities(
        core_topics
    )

    opportunities = validate_opportunities(
        opportunities
    )


    warnings = []

    if not context["title"]:

        warnings.append(
            "The website does not have a detectable title."
        )

    if not context["headings"]:

        warnings.append(
            "No H1/H2/H3 headings were detected."
        )

    if len(body_text.split()) < 50:

        warnings.append(
            "Very little main-page text was available "
            "for semantic analysis."
        )

    if not core_topics:

        warnings.append(
            "Unable to detect strong semantic topics "
            "from the available content."
        )


    parsed_url = urlparse(
        url
    )

    analysis_summary = {

        "url": url,

        "domain": parsed_url.netloc,

        "title": (
            context["title"][:150]
        ),

        "meta_description": (
            context["meta_description"][:300]
        ),

        "detected_headings": (
            context["headings"][:10]
        ),

        "core_topics": core_topics,

        "method": (
            "Weighted semantic extraction using "
            "rendered title, meta description, "
            "headings and main content."
        )
    }


    return {

        "id": "O-001",

        "title": (
            "GEO Search Intent Opportunities"
        ),

        "severity": "medium",

        "evidence": analysis_summary,

        "geo_opportunities": opportunities,

        "suggested_action": {

            "summary": (
                "Improve the website's content so it "
                "clearly answers the identified user "
                "intents. Do not insert these queries "
                "unnaturally or use them as exact-match "
                "keyword stuffing."
            ),

            "recommended_content": [

                "Clear category or product explanation",

                "Feature and capability descriptions",

                "Relevant use-case pages",

                "Comparison or alternatives content "
                "where appropriate",

                "FAQ content answering genuine user "
                "questions",

                "Concise definitions of important concepts"
            ],

            "priority": "medium"
        },

        "quality_warnings": warnings
    }



if __name__ == "__main__":

    # Use any website here for local testing.
    test_url = "https://fello.ai"

    result = suggest_geo_keywords(
        test_url
    )

    print(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False
        )
    )