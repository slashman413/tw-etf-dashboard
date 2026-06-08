#!/usr/bin/env python3
"""
Dashboard HTTP server + Yahoo Finance chart proxy.
Replaces: python -m http.server 8765

Serves static files from current directory AND proxies Yahoo Finance OHLCV
data server-side to avoid browser CORS restrictions.

Proxy endpoint: GET /api/yahoo_chart?code=2330
Returns: raw Yahoo Finance v8 JSON (chart data)
"""
import json, ssl, sys, urllib.request
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from pathlib import Path
import os

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8765

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE

YAHOO_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://finance.yahoo.com/",
    "Origin": "https://finance.yahoo.com",
}

class DashboardHandler(SimpleHTTPRequestHandler):

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/yahoo_chart":
            self._serve_yahoo(parsed)
        else:
            super().do_GET()

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors_headers()
        self.end_headers()

    def _serve_yahoo(self, parsed):
        qs  = parse_qs(parsed.query)
        code = qs.get("code", [""])[0].upper().strip()
        if not code or not all(c.isalnum() or c in "-." for c in code):
            self._json_error(400, "invalid code")
            return

        symbol = code + ".TW"
        url = (
            f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
            f"?range=3y&interval=1d&includePrePost=false"
        )
        try:
            req = urllib.request.Request(url, headers=YAHOO_HEADERS)
            with urllib.request.urlopen(req, context=CTX, timeout=20) as r:
                data = r.read()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self._cors_headers()
            self.end_headers()
            self.wfile.write(data)
            print(f"[proxy] ✅ {symbol} → {len(data)} bytes")
        except urllib.error.HTTPError as e:
            body = e.read()
            print(f"[proxy] ❌ {symbol} HTTP {e.code}: {body[:120]}")
            self._json_error(e.code, f"Yahoo returned {e.code}")
        except Exception as e:
            print(f"[proxy] ❌ {symbol} error: {e}")
            self._json_error(502, str(e))

    def _cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _json_error(self, code, msg):
        body = json.dumps({"error": msg}).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self._cors_headers()
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        pass  # suppress default per-request logs; proxy prints its own

if __name__ == "__main__":
    os.chdir(Path(__file__).parent)
    httpd = HTTPServer(("", PORT), DashboardHandler)
    print(f"Dashboard server: http://localhost:{PORT}/dashboard.html")
    print(f"Yahoo proxy:      http://localhost:{PORT}/api/yahoo_chart?code=2330")
    httpd.serve_forever()
