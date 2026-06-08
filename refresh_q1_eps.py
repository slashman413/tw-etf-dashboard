#!/usr/bin/env python3
"""
Fetch t187ap14_L (all listed companies Q1 EPS), merge into quarterly_financials.json
and full_market.json. Then regenerate per-stock reports and rebuild dashboard.
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
H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

def fetch(url):
    req = urllib.request.Request(url, headers=H)
    with urllib.request.urlopen(req, context=CTX, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))

def sf(v):
    try: return float(str(v).replace(",","").strip()) if v not in (None,"","—","N/A") else None
    except: return None

print(f"[{datetime.now():%H:%M:%S}] === Q1 EPS Refresh (t187ap14_L) ===")
print(f"  Report dir: {REPORT_DIR}")
print(f"  Waiting {WAIT_SEC}s before TWSE call (rate limit)...")
time.sleep(WAIT_SEC)

# ── Fetch t187ap14_L: Q1 2026 EPS for all 1,079 listed companies ────────────
print(f"\n[{datetime.now():%H:%M:%S}] Fetching t187ap14_L...")
eps_data = fetch("https://openapi.twse.com.tw/v1/opendata/t187ap14_L")
print(f"  ✅ {len(eps_data)} companies")
if eps_data:
    yr = eps_data[0].get("年度","?"); qt = eps_data[0].get("季別","?")
    print(f"  Period: {yr}Q{qt}")
    print(f"  Sample: {eps_data[0]}")

# Build eps_map
eps_map = {}
for r in eps_data:
    code = str(r.get("公司代號","")).strip()
    if not code: continue
    eps_map[code] = {
        "code":    code,
        "name":    r.get("公司名稱",""),
        "year":    r.get("年度",""),
        "quarter": r.get("季別",""),
        "sector":  r.get("產業別",""),
        "eps":     sf(r.get("基本每股盈餘(元)") or r.get("基本每股盈餘（元）")),
    }

# ── Check 0050 coverage ──────────────────────────────────────────────────────
etfc = json.loads((REPORT_DIR / "etf_concentration.json").read_text(encoding="utf-8"))
w0050 = etfc.get("weights_0050", {})
now_covered = [c for c in w0050 if c in eps_map]
still_missing = [c for c in w0050 if c not in eps_map]
grand = json.loads((REPORT_DIR / "grand_unified.json").read_text(encoding="utf-8"))
gmap = {r["code"]: r for r in grand.get("all_ranked", [])}

print(f"\n  0050 coverage from t187ap14_L: {len(now_covered)}/{len(w0050)}")
if still_missing:
    print(f"  Still missing: {[(c, gmap.get(c,{}).get('name','?')) for c in still_missing]}")

print(f"\n  0050 Financial stocks Q1 2026 EPS:")
fin_list = ["2882","2881","2886","2891","2884","5880","2892","2887","2883","2801","2890","5876","2207"]
for code in fin_list:
    d = eps_map.get(code, {})
    eps = d.get("eps"); name = d.get("name") or gmap.get(code,{}).get("name","?")
    wt  = w0050.get(code, 0)
    print(f"    {code} {name:<10} EPS={str(eps or '—'):>7}  wt={wt:.2f}%")

# ── Merge into quarterly_financials.json ────────────────────────────────────
qf_path = REPORT_DIR / "quarterly_financials.json"
qf = json.loads(qf_path.read_text(encoding="utf-8"))
existing = {c["code"]: c for c in qf.get("companies", [])}

added = updated = 0
for code, d in eps_map.items():
    if code not in existing:
        existing[code] = d
        added += 1
    elif d.get("eps") is not None and existing[code].get("eps") is None:
        existing[code]["eps"] = d["eps"]
        existing[code].setdefault("name", d["name"])
        updated += 1

qf["companies"] = list(existing.values())
qf["total_companies"] = len(existing)
qf["generated"] = datetime.now().strftime("%Y-%m-%d %H:%M")
qf["eps_source_t187ap14_L"] = len(eps_map)
qf_path.write_text(json.dumps(qf, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\n  ✅ quarterly_financials.json: {len(existing)} companies (+{added} new, {updated} eps updated)")

# ── Merge into full_market.json ──────────────────────────────────────────────
fm_path = REPORT_DIR / "full_market.json"
fm = json.loads(fm_path.read_text(encoding="utf-8"))
enriched = 0
for c in fm.get("companies", []):
    code = c["code"]
    d = eps_map.get(code)
    if d and d.get("eps") is not None and c.get("eps_q1") is None:
        c["eps_q1"] = d["eps"]
        score = c.get("quick_score", 0) or 0
        if d["eps"] > 2:  score += 2
        elif d["eps"] > 0: score += 1
        c["quick_score"] = score
        enriched += 1

fm["generated"] = datetime.now().strftime("%Y-%m-%d %H:%M")
fm_path.write_text(json.dumps(fm, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"  ✅ full_market.json: {enriched} additional companies got eps_q1")

# ── Update grand_unified with EPS for missing stocks ─────────────────────────
updated_grand = 0
for r in grand.get("all_ranked", []):
    code = r["code"]
    d = eps_map.get(code)
    if d and d.get("eps") is not None and r.get("eps_q1") is None:
        r["eps_q1"] = d["eps"]
        updated_grand += 1

if updated_grand:
    grand["generated"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    (REPORT_DIR / "grand_unified.json").write_text(
        json.dumps(grand, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  ✅ grand_unified.json: {updated_grand} stocks got eps_q1")

# ── Full 0050 Q1 EPS summary ──────────────────────────────────────────────────
print(f"\n  ══ 0050 Component Q1 2026 EPS Summary ══")
print(f"  {'代號':<6} {'名稱':<12} {'EPS':>8} {'部門':>10} {'權重':>7}")
print("  " + "─"*54)
rows = []
for code, wt in sorted(w0050.items(), key=lambda x: -x[1]):
    d = eps_map.get(code, {})
    gr = gmap.get(code, {})
    name = d.get("name") or gr.get("name","?")
    eps  = d.get("eps")
    sec  = d.get("sector","")[:8]
    rows.append((code, name, eps, sec, wt))
    star = " ⭐" if (eps or 0) > 5 else ""
    eps_s = f"{eps:.2f}" if eps is not None else "—"
    print(f"  {code:<6} {name:<12} {eps_s:>8} {sec:>10} {wt:>6.2f}%{star}")

have_eps = [r for r in rows if r[2] is not None]
print(f"\n  Coverage: {len(have_eps)}/{len(rows)} stocks have Q1 EPS")
if have_eps:
    avg_eps = sum(r[2] for r in have_eps) / len(have_eps)
    top3 = sorted(have_eps, key=lambda x: -(x[2] or 0))[:3]
    print(f"  Avg EPS: {avg_eps:.2f}  Top 3: {[(r[0],r[1][:6],r[2]) for r in top3]}")

print(f"\n[{datetime.now():%H:%M:%S}] === Done. Run generate_stock_reports.py and build_dashboard.py next. ===")
