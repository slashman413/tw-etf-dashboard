#!/usr/bin/env python3
"""Push reports folder to GitHub via Git Data API (batch tree commit)."""
import json, base64, ssl, urllib.request
from pathlib import Path

PAT    = "GITHUB_PAT_PLACEHOLDER"
REPO   = "slashman413/tw-etf-dashboard"
BRANCH = "main"
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE

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

# Get current branch HEAD
ref = api("GET", f"git/refs/heads/{BRANCH}")
base_sha = ref["object"]["sha"]
print(f"Base commit: {base_sha[:8]}")

commit_obj = api("GET", f"git/commits/{base_sha}")
base_tree = commit_obj["tree"]["sha"]
print(f"Base tree:   {base_tree[:8]}")

# Collect all report files
report_files = sorted([f for f in (HERE / "reports").rglob("*") if f.is_file()])
print(f"Files to upload: {len(report_files)}")

blobs = []
for i, fpath in enumerate(report_files):
    content = base64.b64encode(fpath.read_bytes()).decode()
    blob = api("POST", "git/blobs", {"content": content, "encoding": "base64"})
    rel = fpath.relative_to(HERE).as_posix()
    blobs.append({"path": rel, "mode": "100644", "type": "blob", "sha": blob["sha"]})
    if (i + 1) % 25 == 0:
        print(f"  Blobs: {i+1}/{len(report_files)}")

print("Creating tree...")
tree = api("POST", "git/trees", {"base_tree": base_tree, "tree": blobs})
tree_sha = tree["sha"]
print(f"Tree: {tree_sha[:8]}")

new_commit = api("POST", "git/commits", {
    "message": "backup: add reports folder (2026-06-05 to 2026-06-07)\n\n406 files, ~20MB — ETF component stock reports, financial analysis,\nDNA screening, grand unified rankings, sector data.",
    "tree": tree_sha,
    "parents": [base_sha],
})
commit_sha = new_commit["sha"]
print(f"Commit: {commit_sha[:8]}")

api("PATCH", f"git/refs/heads/{BRANCH}", {"sha": commit_sha})
print(f"\nDone! Reports backed up to github.com/{REPO}/tree/main/reports")
