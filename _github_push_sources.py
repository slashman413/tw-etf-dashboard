#!/usr/bin/env python3
"""Push multiple source files to GitHub via REST API."""
import json, base64, ssl, urllib.request, urllib.error
from pathlib import Path

PAT    = "GITHUB_PAT_PLACEHOLDER"
REPO   = "slashman413/tw-etf-dashboard"
BRANCH = "main"

FILES = [
    "generate_stock_reports.py",
    "etf_4q_report.py",
    "fetch_financial_sector.py",
    "refresh_q1_eps.py",
    "_github_push.py",
    "_github_push_sources.py",
    "etf_4q_report.py",
]

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE
HERE = Path(__file__).parent

def api(method, path, data=None):
    url = f"https://api.github.com/repos/{REPO}/{path}"
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(
        url, data=body, method=method,
        headers={"Authorization": f"token {PAT}", "Accept": "application/vnd.github.v3+json",
                 "Content-Type": "application/json", "User-Agent": "tw-etf-push/1.0"}
    )
    try:
        with urllib.request.urlopen(req, context=CTX, timeout=30) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"HTTP {e.code}: {e.read().decode()[:200]}")

pushed = 0
for filename in FILES:
    fpath = HERE / filename
    if not fpath.exists():
        print(f"  skip: {filename}")
        continue
    content = base64.b64encode(fpath.read_bytes()).decode()
    sha = None
    try:
        existing = api("GET", f"contents/{filename}?ref={BRANCH}")
        sha = existing.get("sha")
    except Exception:
        pass
    payload = {"message": f"auto: {filename}", "content": content, "branch": BRANCH}
    if sha:
        payload["sha"] = sha
    try:
        api("PUT", f"contents/{filename}", payload)
        print(f"  ✅ {filename}")
        pushed += 1
    except Exception as e:
        print(f"  ❌ {filename}: {e}")

print(f"\n  Pushed {pushed}/{len(FILES)} files")
