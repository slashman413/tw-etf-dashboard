#!/usr/bin/env python3
"""Push all Python source files to GitHub repo under src/ folder via Git Data API."""
import json, base64, ssl, re, urllib.request
from pathlib import Path

PAT    = "GITHUB_PAT_PLACEHOLDER"
REPO   = "slashman413/tw-etf-dashboard"
BRANCH = "main"
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE

# Pattern to sanitize embedded secrets before pushing to public repo
_SECRET_PATTERNS = [
    (r'ghp_[A-Za-z0-9]{36}', 'ghp_REDACTED'),
    (r'(?i)(pat\s*=\s*["\'])([^"\']{10,})(["\'])', r'\1REDACTED\3'),
]

def sanitize(text):
    for pat, repl in _SECRET_PATTERNS:
        text = re.sub(pat, repl, text)
    return text

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

# Collect all .py files
py_files = sorted([
    f for f in HERE.rglob("*.py")
    if '.git' not in f.parts and '__pycache__' not in f.parts
])
print(f"Python files to upload: {len(py_files)}")

# Get current branch HEAD
ref = api("GET", f"git/refs/heads/{BRANCH}")
base_sha = ref["object"]["sha"]
print(f"Base commit: {base_sha[:8]}")

commit_obj = api("GET", f"git/commits/{base_sha}")
base_tree = commit_obj["tree"]["sha"]
print(f"Base tree:   {base_tree[:8]}")

blobs = []
for i, fpath in enumerate(py_files):
    try:
        text = fpath.read_text(encoding='utf-8', errors='replace')
    except Exception as e:
        print(f"  Skip {fpath.name}: {e}")
        continue
    clean = sanitize(text)
    content = base64.b64encode(clean.encode('utf-8')).decode()
    blob = api("POST", "git/blobs", {"content": content, "encoding": "base64"})
    # Place under src/ preserving relative structure from HERE
    rel = fpath.relative_to(HERE).as_posix()
    github_path = f"src/{rel}"
    blobs.append({"path": github_path, "mode": "100644", "type": "blob", "sha": blob["sha"]})
    if (i + 1) % 20 == 0 or i == 0:
        print(f"  Blobs: {i+1}/{len(py_files)}")

print(f"  Blobs: {len(py_files)}/{len(py_files)}")
print("Creating tree...")
tree = api("POST", "git/trees", {"base_tree": base_tree, "tree": blobs})
tree_sha = tree["sha"]
print(f"Tree: {tree_sha[:8]}")

new_commit = api("POST", "git/commits", {
    "message": f"src: add Python source files ({len(blobs)} files)\n\nOrganize all Python analysis/dashboard scripts under src/",
    "tree": tree_sha,
    "parents": [base_sha],
})
commit_sha = new_commit["sha"]
print(f"Commit: {commit_sha[:8]}")

api("PATCH", f"git/refs/heads/{BRANCH}", {"sha": commit_sha})
print(f"\nDone! Source backed up to github.com/{REPO}/tree/main/src")
