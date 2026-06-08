"""
Web Crawler Agent
Model: claude-haiku-4-5 — fast and cheap for content summarization
"""

import anthropic
import requests
from bs4 import BeautifulSoup

MODEL = "claude-haiku-4-5"
_client = anthropic.Anthropic()


def crawl(url: str, extract_links: bool = True, max_chars: int = 8000) -> dict:
    """
    Fetch a URL, clean the HTML, and use Claude to summarize the content.

    Args:
        url:           The page to crawl.
        extract_links: Whether to collect hrefs from the page.
        max_chars:     Max raw text characters passed to Claude (keeps cost low).

    Returns:
        dict with keys: url, summary, links, raw_text, error (on failure)
    """
    headers = {"User-Agent": "Mozilla/5.0 (compatible; MultiAgent/1.0)"}

    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
    except requests.RequestException as e:
        return {"url": url, "error": str(e), "summary": None, "links": [], "raw_text": ""}

    soup = BeautifulSoup(response.text, "html.parser")

    for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
        tag.decompose()

    raw_text = soup.get_text(separator="\n", strip=True)[:max_chars]

    links = []
    if extract_links:
        links = [a["href"] for a in soup.find_all("a", href=True)][:30]

    msg = _client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=(
            "You are a web crawler assistant. Given a URL and its page content, "
            "extract and summarize: page title, main topic, key points (bullet list), "
            "and any important data or figures mentioned. Be concise."
        ),
        messages=[{"role": "user", "content": f"URL: {url}\n\nPage content:\n{raw_text}"}],
    )

    return {
        "url": url,
        "summary": msg.content[0].text,
        "links": links,
        "raw_text": raw_text,
        "error": None,
    }
