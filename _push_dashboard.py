"""Push dashboard.html and dna_signals.json to GitHub."""
import requests, base64, time
from pathlib import Path

PAT = "GITHUB_PAT_PLACEHOLDER"
REPO = "slashman413/tw-etf-dashboard"
BRANCH = "main"
HEADERS = {"Authorization": f"Bearer {PAT}", "Accept": "application/vnd.github.v3+json"}
API = "https://api.github.com"

def get_sha(path):
    r = requests.get(f"{API}/repos/{REPO}/contents/{path}?ref={BRANCH}", headers=HEADERS, timeout=15)
    return r.json().get("sha") if r.status_code == 200 else None

def push_file(local_path, remote_path, message):
    content = Path(local_path).read_bytes()
    b64 = base64.b64encode(content).decode()
    sha = get_sha(remote_path)
    body = {"message": message, "content": b64, "branch": BRANCH}
    if sha:
        body["sha"] = sha
    r = requests.put(f"{API}/repos/{REPO}/contents/{remote_path}",
                     headers=HEADERS, json=body, timeout=90)
    status = "OK" if r.status_code in (200, 201) else f"FAIL {r.status_code}"
    print(f"  {status}: {remote_path} ({len(content)//1024} KB)")
    return r.status_code in (200, 201)

import json
today = sorted([d.name for d in Path("reports").iterdir() if d.is_dir() and d.name[:4].isdigit()])[-1]
_gu = json.loads(Path(f"reports/{today}/grand_unified.json").read_text(encoding="utf-8"))
_triple = len(_gu.get("triple_confirmed", []))
_sbuy   = len(_gu.get("strong_buy", []))
_dna = json.loads(Path(f"reports/{today}/dna_signals.json").read_text(encoding="utf-8"))
_5dna = sum(1 for s in _dna.get("all_signals", []) if (s.get("bull_signs") or 0) >= 5)
msg = f"dashboard: {today} — TRIPLE={_triple} STRONG={_sbuy} DNA5+={_5dna}"

push_file("dashboard.html", "dashboard.html", msg)
time.sleep(0.5)
push_file(f"reports/{today}/dna_signals.json", f"reports/{today}/dna_signals.json", msg)
