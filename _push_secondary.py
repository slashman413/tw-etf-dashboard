"""Push secondary analysis files batch to GitHub."""
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
msg = f"data: {today} secondary analysis batch"

secondary = [
    "earnings_quality.json", "peer_comparison.json", "q2_eps_forecast.json",
    "smart_money_confluence.json", "sector_analysis.json", "scenario_analysis.json",
    "margin_of_safety.json", "dna_trigger_calc.json", "monday_plan.json",
    "conviction_matrix.json", "catalyst_calendar.json", "dividend_income.json",
    "position_sizing.json",
]

ok = 0
print(f"Pushing dashboard + {len(secondary)} secondary files for {today}...")
if push_file("dashboard.html", "dashboard.html", msg):
    ok += 1
time.sleep(0.4)

for fname in secondary:
    fpath = Path("reports") / today / fname
    if fpath.exists():
        if push_file(str(fpath), f"reports/{today}/{fname}", msg):
            ok += 1
    else:
        print(f"  SKIP: {fname}")
    time.sleep(0.4)

print(f"\nDone: {ok}/{1 + len(secondary)} files pushed")
