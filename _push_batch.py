"""Push a batch of updated report files to GitHub."""
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

today = sorted([d.name for d in Path("reports").iterdir() if d.is_dir() and d.name[:4].isdigit()])[-1]
msg = f"data: {today} full refresh batch — backtest/RS/screen/sectors/optimizer"

push_files = [
    "dashboard.html",
    f"reports/{today}/dna_backtest.json",
    f"reports/{today}/relative_strength.json",
    f"reports/{today}/dna_screen.json",
    f"reports/{today}/may_preview.json",
    f"reports/{today}/sector_rotation.json",
    f"reports/{today}/ai_chain.json",
    f"reports/{today}/portfolio_optimizer.json",
    f"reports/{today}/dividend_sustainability.json",
]

ok = 0
for f in push_files:
    if Path(f).exists():
        if push_file(f, f, msg):
            ok += 1
    else:
        print(f"  SKIP: {f}")
    time.sleep(0.4)

print(f"\nDone: {ok}/{len(push_files)} files pushed")
