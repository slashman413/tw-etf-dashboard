"""
MOPS / TWSE Financial Report Scraper
Downloads quarterly/annual financial reports for Taiwan-listed companies.

Real endpoint (per TWSE observation):
  https://doc.twse.com.tw/server-java/t57sb01
    ?step=1&colorchg=1&seamon={quarter}&mtype=A&co_id={stock_code}&year={roc_year}

The site requires browser-like session handling — Playwright is the primary method.
A direct requests() attempt is made first as a fast-path.
"""

import io
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime

BASE_DOC   = "https://doc.twse.com.tw/server-java/t57sb01"
BASE_MOPS  = "https://mops.twse.com.tw"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8",
    "Referer": "https://mops.twse.com.tw/mops/",
}

# ROC year = Gregorian year − 1911
def _roc_year() -> int:
    return datetime.now().year - 1911

# Major Taiwan-listed companies (stock code → display name)
COMPANIES = {
    "2330": "台積電 TSMC",
    "2317": "鴻海 Foxconn",
    "2454": "聯發科 MediaTek",
    "2308": "台達電 Delta Electronics",
    "2412": "中華電信 Chunghwa Telecom",
    "2382": "廣達 Quanta Computer",
    "3008": "大立光 LARGAN Precision",
    "2881": "富邦金 Fubon Financial",
    "2882": "國泰金 Cathay Financial",
    "6505": "台塑化 Formosa Petrochemical",
}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _build_url(co_id: str, year: int, quarter: int = None) -> str:
    seamon = str(quarter) if quarter else ""
    return (f"{BASE_DOC}?step=1&colorchg=1&seamon={seamon}"
            f"&mtype=A&co_id={co_id}&year={year}")


def _parse_pdf_bytes(content: bytes) -> str:
    try:
        import pdfplumber
        pages = []
        with pdfplumber.open(io.BytesIO(content)) as pdf:
            for pg in pdf.pages:
                t = pg.extract_text()
                if t:
                    pages.append(t)
                for tbl in pg.extract_tables() or []:
                    for row in tbl:
                        pages.append(" | ".join(str(c or "").strip() for c in row))
        return "\n".join(pages)
    except ImportError:
        print("  [pdf] Install pdfplumber: pip install pdfplumber")
        return "[PDF parsing unavailable — install pdfplumber]"
    except Exception as e:
        return f"[PDF parse error: {e}]"


def _parse_html_bytes(content: bytes) -> tuple:
    """Returns (tables: list[list[list[str]]], text: str)."""
    soup = BeautifulSoup(content.decode("utf-8", errors="replace"), "html.parser")
    for tag in soup(["script", "style", "nav", "footer"]):
        tag.decompose()

    tables = []
    for tbl in soup.find_all("table"):
        rows = []
        for tr in tbl.find_all("tr"):
            cells = [td.get_text(separator=" ", strip=True) for td in tr.find_all(["th", "td"])]
            if any(cells):
                rows.append(cells)
        if len(rows) > 1:
            tables.append(rows)

    if tables:
        lines = []
        for i, rows in enumerate(tables, 1):
            lines.append(f"\n=== Table {i} ===")
            for row in rows:
                lines.append(" | ".join(row))
        text = "\n".join(lines)
    else:
        text = soup.get_text(separator="\n", strip=True)[:12000]

    return tables, text


def _is_blocked(content: bytes, ct: str) -> bool:
    if not content or len(content) < 200:
        return True
    if "pdf" in ct.lower():
        return False
    snippet = content[:500].decode("utf-8", errors="replace").lower()
    return ("page can not be accessed" in snippet or "security" in snippet)


# ── Fetch methods ─────────────────────────────────────────────────────────────

def _fetch_via_requests(url: str) -> tuple:
    """Returns (content_bytes, content_type, ok)."""
    session = requests.Session()
    session.headers.update(HEADERS)
    try:
        session.get(BASE_MOPS + "/mops/", timeout=10)
        time.sleep(0.6)
        r = session.get(url, timeout=25, allow_redirects=True)
        r.raise_for_status()
        ct = r.headers.get("Content-Type", "")
        ok = not _is_blocked(r.content, ct)
        return r.content, ct, ok
    except Exception as e:
        print(f"  [requests] {e}")
        return None, "", False


def _fetch_via_playwright(url: str, co_id: str) -> tuple:
    """Returns (content_bytes, content_type, ok)."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("\n  [playwright] Not installed.")
        print("  Run: pip install playwright && playwright install chromium\n")
        return None, "", False

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=HEADERS["User-Agent"],
            locale="zh-TW",
            accept_downloads=True,
        )
        page = context.new_page()
        pdf_bucket = {}

        def on_response(response):
            ct = response.headers.get("content-type", "")
            if "pdf" in ct and response.status == 200:
                try:
                    pdf_bucket["bytes"] = response.body()
                except Exception:
                    pass

        page.on("response", on_response)

        try:
            print(f"  [playwright] {url}")
            page.goto(BASE_MOPS + "/mops/", timeout=15000)
            time.sleep(0.8)
            page.goto(url, wait_until="networkidle", timeout=35000)
            time.sleep(2)

            # If a PDF was intercepted
            if pdf_bucket.get("bytes"):
                browser.close()
                return pdf_bucket["bytes"], "application/pdf", True

            # Look for PDF in iframes
            for frame in page.frames:
                if ".pdf" in frame.url or "pdf" in frame.url.lower():
                    cookies = {c["name"]: c["value"] for c in context.cookies()}
                    try:
                        r = requests.get(frame.url, headers=HEADERS,
                                         cookies=cookies, timeout=20)
                        if r.status_code == 200 and len(r.content) > 1000:
                            browser.close()
                            return r.content, "application/pdf", True
                    except Exception:
                        pass

            # Fall through: capture rendered HTML
            html = page.content().encode("utf-8")
            browser.close()
            ok = not _is_blocked(html, "text/html")
            return html, "text/html", ok

        except Exception as e:
            print(f"  [playwright] Error: {e}")
            try:
                html = page.content().encode("utf-8")
                browser.close()
                return html, "text/html", False
            except Exception:
                browser.close()
                return None, "", False


# ── Public API ────────────────────────────────────────────────────────────────

def fetch_company_report(co_id: str, year: int = None, quarter: int = None) -> dict:
    """
    Fetch a financial report for one Taiwan-listed company.

    Args:
        co_id:   Stock code string, e.g. '2330' for TSMC.
        year:    ROC year (e.g. 114 = 2025). Defaults to current year.
        quarter: 1–4 for quarterly. None or 0 for annual report.

    Returns:
        dict with keys: co_id, name, year, quarter, content_type, text, tables, error
    """
    year    = year or _roc_year()
    quarter = quarter or None
    name    = COMPANIES.get(co_id, co_id)
    label   = f"Q{quarter}" if quarter else "Annual"
    url     = _build_url(co_id, year, quarter)

    print(f"\n── {co_id} {name} | ROC {year} {label}")
    print(f"   {url}")

    content, ct, ok = _fetch_via_requests(url)

    if not ok:
        print("  Requests blocked. Switching to Playwright...")
        content, ct, ok = _fetch_via_playwright(url, co_id)

    if not content:
        return {
            "co_id": co_id, "name": name, "year": year, "quarter": quarter,
            "error": "Failed to fetch report via any method.",
            "text": "", "tables": [], "content_type": "",
        }

    if "pdf" in ct.lower():
        print("  Parsing PDF...")
        text   = _parse_pdf_bytes(content)
        tables = []
    else:
        tables, text = _parse_html_bytes(content)

    print(f"  ✓ {len(text):,} chars | {len(tables)} table(s) | {'PDF' if 'pdf' in ct.lower() else 'HTML'}")

    return {
        "co_id": co_id,
        "name": name,
        "year": year,
        "quarter": quarter,
        "content_type": ct,
        "text": text[:15000],
        "tables": tables,
        "error": None,
    }


def fetch_multiple(
    co_ids: list,
    year: int = None,
    quarter: int = None,
) -> list:
    """
    Fetch reports for a list of companies sequentially.
    (TWSE rate-limits; parallel requests get blocked.)
    """
    results = []
    for co_id in co_ids:
        results.append(fetch_company_report(co_id, year, quarter))
        time.sleep(1.2)
    return results
