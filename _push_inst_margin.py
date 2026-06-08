"""Push institutional flows + margin data refresh batch."""
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

def push_file(local, remote, msg):
    content = Path(local).read_bytes()
    b64 = base64.b64encode(content).decode()
    sha = get_sha(remote)
    body = {"message": msg, "content": b64, "branch": BRANCH}
    if sha: body["sha"] = sha
    r = requests.put(f"{API}/repos/{REPO}/contents/{remote}", headers=HEADERS, json=body, timeout=90)
    status = "OK" if r.status_code in (200, 201) else f"FAIL {r.status_code}"
    print(f"  {status}: {remote} ({len(content)//1024}KB)")
    return r.status_code in (200, 201)

today = sorted([d.name for d in Path("reports").iterdir() if d.is_dir() and d.name[:4].isdigit()])[-1]
msg = f"data: {today} institutional T86 + margin MI_MARGN refresh"

files = [
    "dashboard.html",
    f"reports/{today}/institutional_flows.json",
    f"reports/{today}/margin_data.json",
    f"reports/{today}/action_signal.json",
    f"reports/{today}/smart_money_confluence.json",
    f"reports/{today}/conviction_data.json",
    f"reports/{today}/conviction_matrix.json",
]
ok = 0
for f in files:
    if Path(f).exists():
        if push_file(f, f, msg):
            ok += 1
    else:
        print(f"  SKIP: {f}")
    time.sleep(0.4)
print(f"\nDone: {ok}/{len(files)} pushed")
