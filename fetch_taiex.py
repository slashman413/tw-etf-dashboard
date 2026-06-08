"""Fetch TAIEX daily OHLC for last 3 months and compute N2 pivot."""
import requests, json, time, sys
from datetime import datetime, timedelta
from pathlib import Path

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
WAIT = 132  # seconds between API calls per crawl constraint

# CLI flags
SKIP_WAIT  = "--skip-wait" in sys.argv
MONTHS_ARG = next((int(a.split("=")[1]) for a in sys.argv if a.startswith("--months=")), 3)

def fetch_taiex_month(year_ad, month):
    date_str = f"{year_ad}{month:02d}01"
    url = f"https://www.twse.com.tw/rwd/zh/TAIEX/MI_5MINS_HIST?date={date_str}&response=json"
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        d = r.json()
        if d.get("stat") == "OK" and d.get("data"):
            rows = []
            for row in d["data"]:
                try:
                    parts = row[0].strip().split("/")
                    y, m, day = int(parts[0]) + 1911, int(parts[1]), int(parts[2])
                    rows.append({
                        "date": f"{y}-{m:02d}-{day:02d}",
                        "open": float(row[1].replace(",", "")),
                        "high": float(row[2].replace(",", "")),
                        "low":  float(row[3].replace(",", "")),
                        "close": float(row[4].replace(",", ""))
                    })
                except Exception:
                    continue
            return rows
    except Exception as e:
        print(f"  Error fetching {year_ad}/{month}: {e}")
    return []

def main():
    today = datetime.now()
    results = []

    # Seed with existing history so N2 stays accurate even on --months=1
    existing_path = Path("taiex_ohlc.json")
    if existing_path.exists():
        try:
            existing = json.loads(existing_path.read_text(encoding="utf-8"))
            results.extend(existing.get("history", []))
            print(f"  Loaded {len(results)} existing days from taiex_ohlc.json")
        except Exception:
            pass

    # Fetch N months (default 3, or --months=N)
    n_months = MONTHS_ARG
    for i in range(n_months):
        dt = today.replace(day=1) - timedelta(days=30 * i)
        print(f"  Fetching TAIEX {dt.year}/{dt.month:02d}...")
        rows = fetch_taiex_month(dt.year, dt.month)
        results.extend(rows)
        if i < n_months - 1:
            if SKIP_WAIT and i == 0:
                pass  # skip first inter-call wait when called from pipeline
            else:
                print(f"  Waiting {WAIT}s...")
                time.sleep(WAIT)

    # Sort and deduplicate
    seen = set()
    final = []
    for row in sorted(results, key=lambda x: x["date"]):
        if row["date"] not in seen:
            seen.add(row["date"])
            final.append(row)

    if not final:
        print("  No TAIEX data fetched!")
        return None

    # N2 = (2-month high + 2-month low) / 2 using last 44 trading days
    recent = final[-44:] if len(final) >= 44 else final
    highs = [r["high"] for r in recent]
    lows  = [r["low"]  for r in recent]

    n2_high = max(highs)
    n2_low  = min(lows)
    n2      = (n2_high + n2_low) / 2
    standby = n2 - 100

    current = final[-1]
    close   = current["close"]
    trend   = "多頭" if close > n2 else "空頭"
    in_zone = standby <= close <= n2

    print(f"  TAIEX current: {close:,.2f}")
    print(f"  N2 pivot: {n2:,.2f} (High {n2_high:,.2f} / Low {n2_low:,.2f})")
    print(f"  Trend: {trend} | Standby zone: {standby:,.2f}–{n2:,.2f} | In zone: {in_zone}")

    output = {
        "generated": today.strftime("%Y-%m-%d %H:%M"),
        "current": current,
        "n2": round(n2, 2),
        "n2_high": round(n2_high, 2),
        "n2_low":  round(n2_low,  2),
        "standby": round(standby, 2),
        "trend":   trend,
        "in_standby": in_zone,
        "days_used": len(recent),
        "history": final[-60:]  # last 60 days for chart
    }

    Path("taiex_ohlc.json").write_text(
        json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"  Saved taiex_ohlc.json ({len(final)} days)")
    return output

if __name__ == "__main__":
    main()
