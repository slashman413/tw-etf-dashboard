#!/usr/bin/env python3
"""
Full market crawl: fetch BWIBBU_ALL (all TWSE listed companies),
OTC TPEX data, merge with revenue data, produce full_market.json.
Rate limit: ≥130s between each TWSE/TPEX endpoint call.
"""
import json, ssl, time, urllib.request
from pathlib import Path
from datetime import datetime

TODAY      = datetime.now().strftime("%Y-%m-%d")
REPORT_DIR = Path("reports") / TODAY
REPORT_DIR.mkdir(parents=True, exist_ok=True)

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode   = ssl.CERT_NONE

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

def fetch_json(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, context=CTX, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))

def sf(v):
    if v is None: return None
    try: return float(str(v).replace(",","").strip())
    except: return None

print(f"[{datetime.now():%H:%M:%S}] === Full Market Crawl ===")
print(f"  Report dir: {REPORT_DIR}")

# ── Step 1: BWIBBU_ALL (all listed companies P/E, P/B, yield) ──────────────
print(f"\n[{datetime.now():%H:%M:%S}] Fetching BWIBBU_ALL...")
bwibbu_all = []
try:
    data = fetch_json("https://openapi.twse.com.tw/v1/exchangeReport/BWIBBU_ALL")
    bwibbu_all = data
    print(f"  ✅ BWIBBU_ALL: {len(data)} records  date={data[0].get('Date','?') if data else '?'}")
except Exception as e:
    print(f"  ❌ BWIBBU_ALL error: {e}")

print(f"\n[{datetime.now():%H:%M:%S}] Waiting 132s before next API call...")
time.sleep(132)

# ── Step 2: TWSE stock list (STOCK_DAY_ALL for latest prices) ───────────────
print(f"\n[{datetime.now():%H:%M:%S}] Fetching STOCK_DAY_ALL (latest prices)...")
stock_prices = []
try:
    data = fetch_json("https://openapi.twse.com.tw/v1/exchangeReport/STOCK_DAY_ALL")
    stock_prices = data
    print(f"  ✅ STOCK_DAY_ALL: {len(data)} records")
except Exception as e:
    print(f"  ❌ STOCK_DAY_ALL error: {e}")

print(f"\n[{datetime.now():%H:%M:%S}] Waiting 132s before next API call...")
time.sleep(132)

# ── Step 3: OTC company list from TPEX ──────────────────────────────────────
print(f"\n[{datetime.now():%H:%M:%S}] Fetching OTC (上櫃) PE/PB data from TPEX...")
otc_data = []
try:
    data = fetch_json("https://www.tpex.org.tw/openapi/v1/tpex_mainboard_peratio_analysis")
    otc_data = data
    print(f"  ✅ TPEX OTC: {len(data)} records")
except Exception as e:
    print(f"  ❌ TPEX OTC error: {e}")

print(f"\n[{datetime.now():%H:%M:%S}] Waiting 132s before next API call...")
time.sleep(132)

# ── Step 4: OTC daily prices ────────────────────────────────────────────────
print(f"\n[{datetime.now():%H:%M:%S}] Fetching OTC daily stock data...")
otc_prices = []
try:
    data = fetch_json("https://www.tpex.org.tw/openapi/v1/tpex_mainboard_daily_close_quotes")
    otc_prices = data
    print(f"  ✅ TPEX prices: {len(data)} records")
except Exception as e:
    print(f"  ❌ TPEX prices error: {e}")

# ── Step 5: Merge with revenue data ─────────────────────────────────────────
print(f"\n[{datetime.now():%H:%M:%S}] Merging data...")

rev_path = REPORT_DIR / "may_revenue_raw.json"
rev_map = {}
if rev_path.exists():
    rev_raw = json.loads(rev_path.read_text(encoding="utf-8"))
    for r in rev_raw.get("raw", []):
        code = r.get("公司代號","").strip()
        if code:
            yoy = sf(r.get("營業收入-去年同月增減(%)"))
            cum = sf(r.get("累計營業收入-前期比較增減(%)"))
            mom = sf(r.get("營業收入-上月比較增減(%)"))
            rev = sf(r.get("營業收入-當月營收"))
            rev_map[code] = {
                "sector":  r.get("產業別",""),
                "rev_yoy": yoy,
                "rev_cum": cum,
                "rev_mom": mom,
                "rev_now": rev,
                "name_tw": r.get("公司名稱",""),
            }
    print(f"  Revenue data: {len(rev_map)} companies")

# Build price map
price_map = {}
for r in stock_prices:
    code = r.get("Code","").strip()
    if code:
        price_map[code] = {
            "price":  sf(r.get("ClosingPrice") or r.get("closing_price")),
            "change": sf(r.get("Change") or r.get("change")),
            "volume": sf(r.get("TradeVolume") or r.get("trade_volume")),
            "name":   r.get("Name",""),
        }
for r in otc_prices:
    code = r.get("SecuritiesCompanyCode","") or r.get("Code","")
    code = str(code).strip()
    if code:
        price_map[code] = {
            "price":  sf(r.get("Close") or r.get("ClosingPrice")),
            "change": sf(r.get("Change")),
            "volume": sf(r.get("TradeVolume")),
            "name":   r.get("CompanyName","") or r.get("Name",""),
            "market": "OTC",
        }

# Build PE/PB map (listed)
pe_map = {}
for r in bwibbu_all:
    code = r.get("Code","").strip()
    if code:
        pe_map[code] = {
            "pe":    sf(r.get("PEratio")),
            "pb":    sf(r.get("PBratio")),
            "yield": sf(r.get("DividendYield")),
            "name":  r.get("Name",""),
            "market":"TSE",
        }
# OTC PE data
for r in otc_data:
    code = (r.get("SecuritiesCompanyCode","") or r.get("Code","")).strip()
    if code:
        pe_map[code] = {
            "pe":    sf(r.get("PriceEarningRatio") or r.get("PE")),
            "pb":    sf(r.get("PriceBookRatio") or r.get("PB")),
            "yield": sf(r.get("DividendYield")),
            "name":  r.get("CompanyName","") or r.get("Name",""),
            "market":"OTC",
        }

# ── Combine all companies ────────────────────────────────────────────────────
all_codes = set(pe_map.keys()) | set(rev_map.keys())
companies = []
for code in sorted(all_codes):
    if not code or not code.isdigit(): continue
    pe_d  = pe_map.get(code, {})
    rev_d = rev_map.get(code, {})
    pr_d  = price_map.get(code, {})
    name  = pe_d.get("name") or rev_d.get("name_tw") or pr_d.get("name") or ""
    companies.append({
        "code":     code,
        "name":     name,
        "market":   pe_d.get("market","TSE"),
        "sector":   rev_d.get("sector",""),
        "price":    pr_d.get("price"),
        "change":   pr_d.get("change"),
        "volume":   pr_d.get("volume"),
        "pe":       pe_d.get("pe"),
        "pb":       pe_d.get("pb"),
        "yield":    pe_d.get("yield"),
        "rev_yoy":  rev_d.get("rev_yoy"),
        "rev_cum":  rev_d.get("rev_cum"),
        "rev_mom":  rev_d.get("rev_mom"),
        "rev_now":  rev_d.get("rev_now"),
    })

# Score each company (simple)
for c in companies:
    score = 0
    if (c["rev_yoy"] or 0) > 10:  score += 2
    if (c["rev_yoy"] or 0) > 0:   score += 1
    if (c["pe"] or 999) < 15:     score += 2
    if (c["pe"] or 999) < 25:     score += 1
    if (c["pb"] or 999) < 1.5:    score += 1
    if (c["yield"] or 0) > 4:     score += 2
    if (c["yield"] or 0) > 2:     score += 1
    c["quick_score"] = score

companies.sort(key=lambda x: -(x["quick_score"] or 0))

# Sector stats
from collections import defaultdict
sector_counts = defaultdict(int)
sector_yoys   = defaultdict(list)
for c in companies:
    s = c.get("sector","")
    if s:
        sector_counts[s] += 1
        if c["rev_yoy"] is not None:
            sector_yoys[s].append(c["rev_yoy"])

sector_summary = []
import statistics
for s, cnt in sorted(sector_counts.items(), key=lambda x:-x[1]):
    yoys = sector_yoys.get(s,[])
    sector_summary.append({
        "sector": s,
        "count":  cnt,
        "median_yoy": round(statistics.median(yoys),1) if yoys else None,
    })

out = {
    "generated":     datetime.now().strftime("%Y-%m-%d %H:%M"),
    "total_listed":  sum(1 for c in companies if c["market"]=="TSE"),
    "total_otc":     sum(1 for c in companies if c["market"]=="OTC"),
    "total":         len(companies),
    "sector_summary": sector_summary,
    "companies":     companies,
}

out_path = REPORT_DIR / "full_market.json"
out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\n  ✅ Saved: {out_path}")
print(f"  Total companies: {len(companies)}  (TSE: {out['total_listed']}, OTC: {out['total_otc']})")
print(f"  Sectors: {len(sector_summary)}")
print(f"\n[{datetime.now():%H:%M:%S}] === Done ===")
