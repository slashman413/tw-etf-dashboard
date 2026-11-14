#!/usr/bin/env python3
"""Push key report files to GitHub via Contents API."""
from twetf.paths import CONFIG_PATH, REPORTS_DIR
import requests, base64, json, os, sys, time
from pathlib import Path

# PAT comes from the environment (name set by config.json "github_pat_env"), never from source.
_cfg_path = CONFIG_PATH
_pat_env = json.loads(_cfg_path.read_text(encoding="utf-8")).get("github_pat_env", "GITHUB_PAT") if _cfg_path.exists() else "GITHUB_PAT"
PAT = os.environ.get(_pat_env)
if not PAT:
    sys.exit(f"Missing ${_pat_env}: export it (e.g. `set -a; . ./.env; set +a`) — never hardcode the PAT.")
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

today = sorted([d.name for d in REPORTS_DIR.iterdir() if d.is_dir() and d.name[:4].isdigit()])[-1]
rd = REPORTS_DIR / today
msg = f"data: {today} full report"

KEY_FILES = [
    "grand_unified.json",
    "price_momentum.json",
    "bwibbu_fresh.json",
    "etf_4q_report.json",
    "watchlist_alerts.json",
    "triple_reports.json",
    "dna_screen.json",
    "action_signal.json",
    "premarket_checklist.json",
    "sector_analysis.json",
]

print(f"Pushing {len(KEY_FILES)} report files for {today}...")
ok = 0
for fname in KEY_FILES:
    fpath = rd / fname
    if fpath.exists():
        if push_file(str(fpath), f"data/reports/{today}/{fname}", msg):
            ok += 1
    else:
        print(f"  SKIP (missing): {fname}")
    time.sleep(0.5)

print(f"\nDone: {ok}/{len(KEY_FILES)} files pushed")
