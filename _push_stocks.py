"""Push dashboard + updated stock reports to GitHub."""
import requests, base64, time, json
from pathlib import Path

PAT    = "GITHUB_PAT_PLACEHOLDER"
REPO   = "slashman413/tw-etf-dashboard"
BRANCH = "main"
HDRS   = {"Authorization": f"Bearer {PAT}", "Accept": "application/vnd.github.v3+json"}
API    = "https://api.github.com"

def sha(p):
    r = requests.get(f"{API}/repos/{REPO}/contents/{p}?ref={BRANCH}", headers=HDRS, timeout=15)
    return r.json().get("sha") if r.status_code == 200 else None

def push(local, remote, msg):
    b64 = base64.b64encode(Path(local).read_bytes()).decode()
    body = {"message": msg, "content": b64, "branch": BRANCH}
    s = sha(remote)
    if s: body["sha"] = s
    r = requests.put(f"{API}/repos/{REPO}/contents/{remote}", headers=HDRS, json=body, timeout=60)
    ok = r.status_code in (200, 201)
    if not ok:
        print(f"  FAIL {r.status_code}: {remote}")
    return ok

today = sorted([d.name for d in Path("reports").iterdir() if d.is_dir() and d.name[:4].isdigit()])[-1]
_gu = json.loads(Path(f"reports/{today}/grand_unified.json").read_text(encoding="utf-8"))
_triple = len(_gu.get("triple_confirmed", []))
_sbuy   = len(_gu.get("strong_buy", []))
msg = f"reports: {today} — TRIPLE={_triple} STRONG_BUY={_sbuy} stocks updated"

ok = 0
for local, remote in [
    ("dashboard.html", "dashboard.html"),
    (f"reports/{today}/technical_data.json", f"reports/{today}/technical_data.json"),
    (f"reports/{today}/FULL_REPORT.md", f"reports/{today}/FULL_REPORT.md"),
]:
    if Path(local).exists() and push(local, remote, msg):
        ok += 1
    time.sleep(0.3)

stocks = sorted(Path(f"reports/{today}/stocks").glob("*.json"))
print(f"Pushing {len(stocks)} stock reports...")
stock_ok = 0
for f in stocks:
    remote = f"reports/{today}/stocks/{f.name}"
    if push(str(f), remote, msg):
        stock_ok += 1
    time.sleep(0.3)

print(f"Done: {ok}/3 key files + {stock_ok}/{len(stocks)} stock reports pushed")
