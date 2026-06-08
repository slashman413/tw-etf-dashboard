#!/usr/bin/env python3
"""Push README.md to GitHub repo root."""
import json, base64, ssl, urllib.request
from pathlib import Path

PAT    = "GITHUB_PAT_PLACEHOLDER"
REPO   = "slashman413/tw-etf-dashboard"
BRANCH = "main"
CTX = ssl.create_default_context(); CTX.check_hostname=False; CTX.verify_mode=ssl.CERT_NONE

def api(method, path, data=None):
    url = f"https://api.github.com/repos/{REPO}/{path}"
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, method=method,
        headers={"Authorization": f"token {PAT}",
                 "Accept": "application/vnd.github.v3+json",
                 "Content-Type": "application/json",
                 "User-Agent": "tw-etf-push/1.0"})
    with urllib.request.urlopen(req, context=CTX, timeout=60) as r:
        return json.loads(r.read().decode())

HERE = Path(__file__).parent
content = (HERE / "README.md").read_bytes()
encoded = base64.b64encode(content).decode()

# Check if README.md exists in repo
try:
    existing = api("GET", "contents/README.md")
    sha = existing.get("sha")
    print(f"Updating existing README.md (sha={sha[:8]})")
except:
    sha = None
    print("Creating new README.md")

data = {
    "message": "docs: add comprehensive project README",
    "content": encoded,
    "branch": BRANCH,
}
if sha:
    data["sha"] = sha

result = api("PUT", "contents/README.md", data)
print(f"Done! Commit: {result['commit']['sha'][:8]}")
print(f"https://github.com/{REPO}/blob/main/README.md")
