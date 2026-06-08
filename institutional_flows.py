#!/usr/bin/env python3
"""
Iteration 55: Institutional Net Buy/Sell Flows (法人買賣超)
Fetches TWSE T86 data for 2026-06-05 (Friday).
Shows foreign / trust fund / dealer net buy/sell per stock.
Waits 130s after API call per IP-ban constraint.
Generates: institutional_flows.json
"""
import json, ssl, urllib.request, time, sys
from pathlib import Path
from datetime import datetime

SKIP_WAIT = "--skip-wait" in sys.argv

TODAY = sorted([d.name for d in Path("reports").iterdir() if d.is_dir() and d.name[:4].isdigit()])[-1]
REPORT_DIR = Path("reports") / TODAY
# Derive DATA_DATE from latest price_momentum data_date (ROC format "1150608" → "20260608")
_mom_tmp = json.loads((REPORT_DIR / "price_momentum.json").read_text(encoding="utf-8"))
_roc_dd  = _mom_tmp.get("data_date", "")
if _roc_dd and len(_roc_dd) == 7 and _roc_dd[:3].isdigit():
    _yr = int(_roc_dd[:3]) + 1911
    DATA_DATE = f"{_yr}{_roc_dd[3:]}"
else:
    DATA_DATE = datetime.now().strftime("%Y%m%d")

# Stale-date guard: skip if existing data already covers DATA_DATE
_if_path = REPORT_DIR / "institutional_flows.json"
if _if_path.exists():
    try:
        _prev = json.loads(_if_path.read_text(encoding="utf-8"))
        if _prev.get("data_date") == DATA_DATE:
            print(f"institutional_flows already at {DATA_DATE} — skipping")
            sys.exit(0)
    except Exception:
        pass

grand   = json.loads((REPORT_DIR/"grand_unified.json").read_text(encoding="utf-8"))
comp    = json.loads((REPORT_DIR/"composite_data.json").read_text(encoding="utf-8"))
expd    = json.loads((REPORT_DIR/"expansion_stocks.json").read_text(encoding="utf-8"))
mom     = json.loads((REPORT_DIR/"price_momentum.json").read_text(encoding="utf-8"))

grand_map = {r["code"]: r for r in grand.get("all_ranked",[])}
name_map  = {**{s["code"]: s["name"] for s in comp}, **{s["code"]: s["name"] for s in expd}}
mom_map   = {m["code"]: m for m in mom.get("all_momentum",[])}

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode    = ssl.CERT_NONE

def fetch(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer":    "https://www.twse.com.tw/",
    })
    with urllib.request.urlopen(req, context=CTX, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))

def sf(v):
    if v is None: return None
    try: return float(str(v).replace(",","").strip())
    except: return None

# ── Fetch T86: 三大法人買賣超 ─────────────────────────────────────────────────
print(f"Fetching 法人買賣超 for {DATA_DATE}...")
url = f"https://www.twse.com.tw/rwd/zh/fund/T86?date={DATA_DATE}&selectType=ALL&response=json"
try:
    data = fetch(url)
    print(f"  Status: {data.get('stat','?')}")
    rows_raw = data.get("data", [])
    print(f"  Raw rows: {len(rows_raw)}")
except Exception as e:
    print(f"  ERROR: {e}")
    rows_raw = []

# If T86 returned no data, preserve existing file rather than overwriting with empty
if not rows_raw:
    print("  T86 returned no data — preserving existing institutional_flows.json")
    sys.exit(0)

_wait = 0 if SKIP_WAIT else 130
if _wait:
    print(f"Waiting {_wait}s before any next API call...")
    time.sleep(_wait)

# ── Parse T86 columns ─────────────────────────────────────────────────────────
# Expected columns: 證券代號, 證券名稱, 外陸資買進, 外陸資賣出, 外陸資淨買超,
#   投信買進, 投信賣出, 投信淨買超, 自營商買進, 自營商賣出, 自營商淨買超,
#   三大法人買賣超日數, 三大法人買賣超

results = []
for row in rows_raw:
    if len(row) < 12:
        continue
    code     = str(row[0]).strip()
    name_raw = str(row[1]).strip()

    # Parse numeric columns (remove commas, handle negative with parens)
    def pn(s):
        s = str(s).replace(",","").strip()
        if s.startswith("(") and s.endswith(")"):
            s = "-" + s[1:-1]
        try: return int(float(s))
        except: return 0

    foreign_buy  = pn(row[2])
    foreign_sell = pn(row[3])
    foreign_net  = pn(row[4])   # 外陸資淨買超 (shares)
    trust_buy    = pn(row[5])
    trust_sell   = pn(row[6])
    trust_net    = pn(row[7])   # 投信淨買超
    dealer_buy   = pn(row[8])
    dealer_sell  = pn(row[9])
    dealer_net   = pn(row[10])  # 自營商淨買超
    total_net    = pn(row[12]) if len(row) > 12 else (foreign_net + trust_net + dealer_net)

    # Skip stocks not in our universe
    g = grand_map.get(code, {})
    grand_s = g.get("grand", 0) or 0
    final   = g.get("final", "")
    name    = name_map.get(code, name_raw)
    mm      = mom_map.get(code, {})

    pct_ma  = sf(mm.get("pct_vs_ma"))
    close   = sf(mm.get("close"))

    # Classify institutional sentiment
    if total_net > 5000:    inst_signal = "大量買超"
    elif total_net > 1000:  inst_signal = "買超"
    elif total_net > 0:     inst_signal = "小幅買超"
    elif total_net > -1000: inst_signal = "小幅賣超"
    elif total_net > -5000: inst_signal = "賣超"
    else:                    inst_signal = "大量賣超"

    # Divergence: price down but institutions buying = bullish divergence
    divergence = None
    if total_net > 1000 and pct_ma is not None and pct_ma < -2:
        divergence = "價跌法買 (看漲背離)"
    elif total_net < -1000 and pct_ma is not None and pct_ma > 5:
        divergence = "價漲法賣 (看跌背離)"

    # Only keep stocks with meaningful institutional activity OR in our universe
    if code not in grand_map and abs(total_net) < 500:
        continue

    results.append({
        "code":         code,
        "name":         name.split(" ")[0] if name else name_raw,
        "grand":        round(grand_s, 1),
        "final":        final,
        "foreign_net":  foreign_net,
        "trust_net":    trust_net,
        "dealer_net":   dealer_net,
        "total_net":    total_net,
        "inst_signal":  inst_signal,
        "divergence":   divergence,
        "pct_vs_ma":    round(pct_ma, 1) if pct_ma is not None else None,
        "close":        close,
    })

# Sort by total net (most bought first)
results.sort(key=lambda x: -x["total_net"])

# ── Filter our universe stocks ────────────────────────────────────────────────
our_stocks = [r for r in results if r["code"] in grand_map]
our_stocks.sort(key=lambda x: -x["grand"])

# Key groups
heavy_buy   = [r for r in our_stocks if r["total_net"] > 1000]
heavy_sell  = [r for r in our_stocks if r["total_net"] < -1000]
divergence_bullish = [r for r in our_stocks if (r.get("divergence") or "").startswith("價跌法買")]
divergence_bearish = [r for r in our_stocks if (r.get("divergence") or "").startswith("價漲法賣")]

# TRIPLE stocks flow check
triple_flows = [r for r in our_stocks if "TRIPLE" in (r.get("final") or "")]

# ── Print ─────────────────────────────────────────────────────────────────────
print(f"\n{'INSTITUTIONAL FLOWS — {DATA_DATE}':=<65}")
print(f"  Total rows parsed: {len(results)}  |  Our universe: {len(our_stocks)}")

print(f"\n  TRIPLE持倉機構流向:")
for r in triple_flows:
    print(f"    {r['code']} {r['name']:<10} Grand={r['grand']:.1f}  "
          f"外資={r['foreign_net']:+,}  投信={r['trust_net']:+,}  合計={r['total_net']:+,}  [{r['inst_signal']}]")

print(f"\n  大量買超 (>1000張):")
for r in heavy_buy[:10]:
    print(f"    {r['code']} {r['name']:<10} {r['total_net']:+,}  Grand={r['grand']:.1f}  {r['inst_signal']}")

print(f"\n  大量賣超 (<-1000張):")
for r in heavy_sell[:5]:
    print(f"    {r['code']} {r['name']:<10} {r['total_net']:+,}  Grand={r['grand']:.1f}  {r['inst_signal']}")

if divergence_bullish:
    print(f"\n  看漲背離 (價跌法買):")
    for r in divergence_bullish:
        print(f"    {r['code']} {r['name']:<10} 法人={r['total_net']:+,}  vs MA={r['pct_vs_ma']:+.1f}%")

out = {
    "date":       TODAY,
    "data_date":  DATA_DATE,
    "generated":  datetime.now().strftime("%Y-%m-%d %H:%M"),
    "total_rows": len(results),
    "universe_count": len(our_stocks),
    "summary": {
        "heavy_buy_count":   len(heavy_buy),
        "heavy_sell_count":  len(heavy_sell),
        "bullish_divergence": len(divergence_bullish),
        "bearish_divergence": len(divergence_bearish),
    },
    "all_flows":      results,
    "universe_flows": our_stocks,
    "heavy_buy":      heavy_buy,
    "heavy_sell":     heavy_sell,
    "triple_flows":   triple_flows,
    "bullish_divergence": divergence_bullish,
}
(REPORT_DIR/"institutional_flows.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\n-- institutional_flows.json saved ({len(results)} stocks)")
