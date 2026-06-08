#!/usr/bin/env python3
"""Delete src/agents/ folder from GitHub repo (old scaffolding, duplicated by root scripts)."""
import json, ssl, urllib.request

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

# Get current HEAD
ref = api("GET", f"git/refs/heads/{BRANCH}")
base_sha = ref["object"]["sha"]
commit_obj = api("GET", f"git/commits/{base_sha}")
base_tree_sha = commit_obj["tree"]["sha"]
print(f"Base commit: {base_sha[:8]} | Base tree: {base_tree_sha[:8]}")

# Get the full tree recursively to find all src/agents/ files
tree_data = api("GET", f"git/trees/{base_tree_sha}?recursive=1")
agents_files = [item["path"] for item in tree_data["tree"]
                if item["path"].startswith("src/agents/") and item["type"] == "blob"]
print(f"Files to delete: {agents_files}")

if not agents_files:
    print("Nothing to delete.")
    exit(0)

# Create new tree with sha=null for each file to delete
deletions = [{"path": p, "mode": "100644", "type": "blob", "sha": None}
             for p in agents_files]

new_tree = api("POST", "git/trees", {"base_tree": base_tree_sha, "tree": deletions})
print(f"New tree: {new_tree['sha'][:8]}")

new_commit = api("POST", "git/commits", {
    "message": "cleanup: remove src/agents/ (old scaffolding, superseded by root scripts)",
    "tree": new_tree["sha"],
    "parents": [base_sha],
})
print(f"New commit: {new_commit['sha'][:8]}")

api("PATCH", f"git/refs/heads/{BRANCH}", {"sha": new_commit["sha"]})
print(f"Done! Deleted {len(agents_files)} files from src/agents/")
