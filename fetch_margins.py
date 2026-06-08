#!/usr/bin/env python3
"""
Fetch t187ap17_L (Q1 2026 profitability ratios for 1,049 companies)
and merge gross/op/net margins into quarterly_financials.json + full_market.json.
"""
import json, ssl, time, urllib.request
from pathlib import Path
from datetime import datetime

_dirs = sorted([d for d in Path("reports").iterdir() if d.is_dir() and d.name[:4].isdigit() and (d / "grand_unified.json").exists()], reverse=True)
TODAY      = _dirs[0].name if _dirs else datetime.now().strftime("%Y-%m-%d")
REPORT_DIR = Path("reports") / TODAY
WAIT_SEC   = 132

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode    = ssl.CERT_NONE
H = {"User-Agent": "Mozilla/5.0"}

def fetch(url):
    req = urllib.request.Request(url, headers=H)
    with urllib.request.urlopen(req, context=CTX, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))

def sf(v):
    try: return float(str(v).replace(",","").strip()) if v not in (None,"","—") else None
    except: return None

print(f"[{datetime.now():%H:%M:%S}] === Fetch t187ap17_L Margin Ratios ===")
print(f"  Waiting {WAIT_SEC}s (rate limit)...")
time.sleep(WAIT_SEC)

print(f"\n[{datetime.now():%H:%M:%S}] Fetching t187ap17_L...")
data = fetch("https://openapi.twse.com.tw/v1/opendata/t187ap17_L")
print(f"  ✅ {len(data)} companies")
if data:
    yr = data[0].get("年度","?"); qt = data[0].get("季別","?")
    print(f"  Period: {yr}Q{qt}")
    print(f"  Fields: {list(data[0].keys())}")

# Build margin map
margin_map = {}
for r in data:
    code = str(r.get("公司代號","")).strip()
    if not code: continue
    margin_map[code] = {
        "code":         code,
        "name":         r.get("公司名稱",""),
        "year":         r.get("年度",""),
        "quarter":      r.get("季別",""),
        "revenue_m":    sf(r.get("營業收入(百萬元)")),
        "gross_margin": sf(r.get("毛利率(%)(營業毛利)/(營業收入)")),
        "op_margin":    sf(r.get("營業利益率(%)(營業利益)/(營業收入)")),
        "pretax_margin":sf(r.get("稅前純益率(%)(稅前純益)/(營業收入)")),
        "net_margin":   sf(r.get("稅後純益率(%)(稅後純益)/(營業收入)")),
    }

# Check 0050 financial holding coverage (the ones missing from t187ap06_L_ci)
fin_codes = ["2882","2881","2886","2891","2884","5880","2892","2887","2883","2801","2890","5876"]
print(f"\n  Financial holdings margin coverage:")
for code in fin_codes:
    d = margin_map.get(code,{})
    name = d.get("name","?")[:8]
    gm = d.get("gross_margin"); om = d.get("op_margin"); nm = d.get("net_margin")
    print(f"    {code} {name}: gm={gm}% op={om}% net={nm}%")

# ── Merge into quarterly_financials.json ────────────────────────────────────
qf_path = REPORT_DIR / "quarterly_financials.json"
qf = json.loads(qf_path.read_text(encoding="utf-8"))
qf_map = {c["code"]: c for c in qf.get("companies",[])}
updated = added = 0
for code, md in margin_map.items():
    if code in qf_map:
        # Only fill missing margins
        c = qf_map[code]
        if c.get("gross_margin") is None and md.get("gross_margin") is not None:
            c["gross_margin"] = md["gross_margin"]; updated += 1
        if c.get("op_margin") is None and md.get("op_margin") is not None:
            c["op_margin"] = md["op_margin"]
        if c.get("net_margin") is None and md.get("net_margin") is not None:
            c["net_margin"] = md["net_margin"]
    else:
        qf_map[code] = md; added += 1

qf["companies"] = list(qf_map.values())
qf["total_companies"] = len(qf_map)
qf["generated"] = datetime.now().strftime("%Y-%m-%d %H:%M")
qf["margin_source"] = f"t187ap17_L: {len(margin_map)} companies"
qf_path.write_text(json.dumps(qf, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\n  ✅ quarterly_financials.json: {len(qf_map)} cos (+{added} new, {updated} margins updated)")

# ── Merge into full_market.json ──────────────────────────────────────────────
fm_path = REPORT_DIR / "full_market.json"
fm = json.loads(fm_path.read_text(encoding="utf-8"))
fm_updated = 0
for c in fm.get("companies",[]):
    md = margin_map.get(c["code"])
    if md:
        changed = False
        if c.get("gross_margin") is None and md.get("gross_margin") is not None:
            c["gross_margin"] = md["gross_margin"]; changed = True
        if c.get("op_margin") is None and md.get("op_margin") is not None:
            c["op_margin"] = md["op_margin"]; changed = True
        if c.get("net_margin") is None and md.get("net_margin") is not None:
            c["net_margin"] = md["net_margin"]; changed = True
        if changed: fm_updated += 1

fm["generated"] = datetime.now().strftime("%Y-%m-%d %H:%M")
fm_path.write_text(json.dumps(fm, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"  ✅ full_market.json: {fm_updated} companies got margin data")

# ── Print top/bottom margins for insight ────────────────────────────────────
by_net = sorted([m for m in margin_map.values() if m.get("net_margin") is not None], key=lambda x: -(x["net_margin"] or 0))
print(f"\n  Top 10 Net Margin (Q1 2026):")
print(f"  {'代號':<6} {'名稱':<10} {'Net%':>8} {'Op%':>8} {'Gross%':>8}")
for m in by_net[:10]:
    print(f"  {m['code']:<6} {m['name']:<10} {str(m['net_margin'])+'%':>8} {str(m['op_margin'])+'%':>8} {str(m['gross_margin'])+'%':>8}")

print(f"\n  Bottom 5 Net Margin:")
for m in by_net[-5:]:
    print(f"  {m['code']:<6} {m['name']:<10} {str(m['net_margin'])+'%':>8}")

print(f"\n[{datetime.now():%H:%M:%S}] === Done ===")
