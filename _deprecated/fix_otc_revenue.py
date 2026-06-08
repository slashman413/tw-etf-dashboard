#!/usr/bin/env python3
"""
Re-merge OTC revenue with correct field mapping (no new API call — re-fetches from TPEX).
Field mapping confirmed from sample:
  rev_now  = 營業收入-當月營收
  rev_yoy  = 營業收入-去年同月增減(%)   ← the YoY %
  rev_mom  = 營業收入-上月比較增減(%)
  rev_cum  = 累計營業收入-當月累計營收  (YTD cumulative NTD thousand)
"""
import json, ssl, urllib.request
from pathlib import Path
from datetime import datetime

_dirs = sorted([d for d in Path("reports").iterdir()
    if d.is_dir() and d.name[:4].isdigit() and (d / "grand_unified.json").exists()], reverse=True)
TODAY      = _dirs[0].name if _dirs else datetime.now().strftime("%Y-%m-%d")
REPORT_DIR = Path("reports") / TODAY

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode    = ssl.CERT_NONE

def sf(v):
    if v is None: return None
    s = str(v).replace(",","").strip()
    if not s or s == "-": return None
    try: return float(s)
    except: return None

print(f"[{datetime.now():%H:%M:%S}] === Fix OTC Revenue Field Mapping ===")

req = urllib.request.Request(
    "https://www.tpex.org.tw/openapi/v1/mopsfin_t187ap05_O",
    headers={"User-Agent": "Mozilla/5.0"})
with urllib.request.urlopen(req, context=CTX, timeout=30) as r:
    data = json.loads(r.read().decode("utf-8"))
print(f"  Got {len(data)} rows, period={data[0].get('資料年月')}")

fm = json.loads((REPORT_DIR / "full_market.json").read_text(encoding="utf-8"))
companies = fm["companies"]
otc_map   = {c["code"]: c for c in companies if c.get("market") == "OTC"}

updated = 0
for row in data:
    code = str(row.get("公司代號","")).strip()
    if not code or code not in otc_map:
        continue
    c = otc_map[code]
    rev_now = sf(row.get("營業收入-當月營收"))
    rev_yoy = sf(row.get("營業收入-去年同月增減(%)"))
    rev_mom = sf(row.get("營業收入-上月比較增減(%)"))
    rev_cum = sf(row.get("累計營業收入-當月累計營收"))

    if rev_now is not None: c["rev_now"] = rev_now
    if rev_yoy is not None: c["rev_yoy"] = round(rev_yoy, 2)
    if rev_mom is not None: c["rev_mom"] = round(rev_mom, 2)
    if rev_cum is not None: c["rev_cum"] = rev_cum
    updated += 1

# Update quick_score with rev_yoy bonus
rev_score_updated = 0
for c in [c for c in companies if c.get("market") == "OTC"]:
    ry = c.get("rev_yoy")
    if ry is None: continue
    score = c.get("quick_score", 0) or 0
    if ry > 10:
        c["quick_score"] = score + 2
        rev_score_updated += 1
    elif ry > 0:
        c["quick_score"] = score + 1
        rev_score_updated += 1

# Coverage stats
with_yoy = sum(1 for c in companies if c.get("market")=="OTC" and c.get("rev_yoy") is not None)
with_now = sum(1 for c in companies if c.get("market")=="OTC" and c.get("rev_now") is not None)
print(f"  Updated {updated} OTC | rev_yoy: {with_yoy}/887 | rev_now: {with_now}/887")
print(f"  quick_score boosted by rev_yoy: {rev_score_updated}")

# Top 10 OTC by YoY
top_yoy = sorted(
    [c for c in companies if c.get("market")=="OTC" and c.get("rev_yoy") is not None
     and (c.get("rev_now") or 0) > 50000],
    key=lambda x: -(x.get("rev_yoy") or 0))[:10]
print("\n  Top 10 OTC April revenue YoY (>5000萬):")
for c in top_yoy:
    code = c["code"]
    name = c.get("name","?")[:10]
    yoy  = c.get("rev_yoy",0)
    eps  = c.get("eps_q1")
    print(f"    {code} {name:<12} YoY={yoy:+.1f}% Q1-EPS={eps}")

fm["generated"] = datetime.now().strftime("%Y-%m-%d %H:%M")
(REPORT_DIR / "full_market.json").write_text(
    json.dumps(fm, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\n  ✅ Saved {REPORT_DIR}/full_market.json")
print(f"[{datetime.now():%H:%M:%S}] Done")
