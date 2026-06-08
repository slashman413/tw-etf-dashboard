#!/usr/bin/env python3
"""
Push dashboard.html to GitHub Pages via GitHub REST API.
Avoids git command network issues on Windows.
"""
import json, base64, ssl, urllib.request, urllib.error
from pathlib import Path

PAT  = "GITHUB_PAT_PLACEHOLDER"
REPO = "slashman413/tw-etf-dashboard"
BRANCH = "main"
FILES_TO_PUSH = ["dashboard.html", "series_map.json"]

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE

def api(method, path, data=None):
    url = f"https://api.github.com/repos/{REPO}/{path}"
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(
        url, data=body, method=method,
        headers={
            "Authorization": f"token {PAT}",
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json",
            "User-Agent": "tw-etf-push/1.0",
        }
    )
    try:
        with urllib.request.urlopen(req, context=CTX, timeout=60) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        raise RuntimeError(f"HTTP {e.code}: {body[:200]}")

HERE = Path(__file__).parent

for filename in FILES_TO_PUSH:
    fpath = HERE / filename
    if not fpath.exists():
        print(f"  ⚠️  {filename} not found, skipping")
        continue

    content = base64.b64encode(fpath.read_bytes()).decode()
    api_path = f"contents/{filename}"

    # Get current SHA if file exists
    sha = None
    try:
        existing = api("GET", api_path + f"?ref={BRANCH}")
        sha = existing.get("sha")
        print(f"  Found existing {filename} (sha={sha[:8]})")
    except Exception:
        print(f"  {filename} is new")

    # Push file
    payload = {
        "message": f"auto: update {filename} [{fpath.stat().st_size//1024} KB]",
        "content": content,
        "branch": BRANCH,
    }
    if sha:
        payload["sha"] = sha

    print(f"  Uploading {filename} ({fpath.stat().st_size//1024} KB)...", end=" ", flush=True)
    result = api("PUT", api_path, payload)
    commit_sha = result.get("commit", {}).get("sha", "?")[:8]
    print(f"✅ committed {commit_sha}")

print(f"\n  🌐 https://slashman413.github.io/tw-etf-dashboard/dashboard.html")
