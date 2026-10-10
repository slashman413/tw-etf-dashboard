"""
Web Crawler Agent
Prompt + model: config/llm.toml [tasks.web_summary]
"""

import requests
from bs4 import BeautifulSoup

from twetf import llm


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

    msg = llm.run("web_summary", url=url, raw_text=raw_text)

    return {
        "url": url,
        "summary": llm.text(msg),
        "links": links,
        "raw_text": raw_text,
        "error": None,
    }
