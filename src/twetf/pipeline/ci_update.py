#!/usr/bin/env python3
"""
Daily dashboard refresh — the job GitHub Actions runs (Mon–Fri 16:00 Taiwan).

    python run.py ci_update                 # fetch live TWSE data, patch dashboard.html + series_map.json
    python run.py ci_update --dry-run       # same, but write nothing
    python run.py ci_update --valuation     # force the BWIBBU valuation refresh (default: Mon/Thu)

Updates MOMENTUM, MOVERS, MAREFRESH, DNASIGNALS, GRANDDATA (+ BWIBBU2 on valuation
days) and appends today's prices to series_map.json for indicator history.

Layers: fetch (slashman_finance) → indicators (twetf.analyzers.indicators) →
patch (twetf.renderers.dashboard_consts) → write. Nothing here is Actions-specific;
the workflow is a one-line call to this module.
"""
import argparse
import json
import sys
from datetime import date, datetime
from pathlib import Path

from slashman_finance import ad_to_roc, bwibbu_all, stock_day_all

from twetf.analyzers.indicators import append_today
from twetf.paths import DASHBOARD, SERIES_MAP
from twetf.renderers import dashboard_consts as dc

# Refresh the BWIBBU valuation block on these weekdays (Mon, Thu → ~2×/week).
VALUATION_DAYS = {0, 3}


def fetch_prices(today):
    """(data_date_roc, {code: {close, open, high, low, volume}}); {} on a non-trading day."""
    data_date, prices = stock_day_all(today)
    return data_date or ad_to_roc(today), prices


def fetch_valuation():
    """(data_date_roc, {code: {pe, div, pb}}) or (None, {}) on failure."""
    try:
        return bwibbu_all()
    except Exception as e:
        print(f"  BWIBBU_ALL fetch failed: {e}")
        return None, {}


def refresh(html, series_map, prices, data_date, *, today, stamp, valuation=None):
    """Pure core: returns the patched html. Mutates series_map in place."""
    if series_map:
        n = append_today(series_map, prices, today)
        print(f"  Appended today's prices to {n} series")
    # MOMENTUM first — MOVERS is derived from it
    html = dc.patch_momentum(html, prices, data_date, today, stamp)
    html = dc.patch_movers(html)
    html = dc.patch_marefresh(html, series_map, prices, data_date, today, stamp)
    html = dc.patch_dnasignals(html, series_map, prices, data_date, today, stamp)
    html = dc.patch_granddata(html, series_map, prices, data_date, today, stamp)
    if valuation is not None:
        val_date, live = valuation
        html = dc.patch_valuation(html, val_date, live, stamp)
    else:
        print("  VALUATION: skipped (not a scheduled valuation day)")
    return html


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0].strip())
    ap.add_argument("--dashboard", type=Path, default=DASHBOARD)
    ap.add_argument("--series-map", type=Path, default=SERIES_MAP)
    ap.add_argument("--dry-run", action="store_true", help="compute everything, write nothing")
    ap.add_argument("--valuation", action="store_true", help="force the BWIBBU valuation refresh")
    args = ap.parse_args(argv)

    today_d = date.today()
    today = today_d.strftime("%Y-%m-%d")
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    print(f"[{stamp}] Comprehensive CI update starting...")

    data_date, prices = fetch_prices(today_d)
    if not prices:
        print("No price data — non-trading day, skipping.")
        return 0
    print(f"  {len(prices)} stocks fetched, data_date={data_date}")

    series_map = {}
    if args.series_map.exists():
        print("  Loading series_map.json...")
        series_map = json.loads(args.series_map.read_text(encoding="utf-8"))

    print("  Loading dashboard.html...")
    html = args.dashboard.read_text(encoding="utf-8")
    valuation = fetch_valuation() if (args.valuation or today_d.weekday() in VALUATION_DAYS) else None
    html = refresh(html, series_map, prices, data_date, today=today, stamp=stamp, valuation=valuation)

    if args.dry_run:
        print("  --dry-run: nothing written")
    else:
        if series_map:
            args.series_map.write_text(json.dumps(series_map, ensure_ascii=False, separators=(",", ":")),
                                       encoding="utf-8")
            print("  series_map.json saved")
        args.dashboard.write_text(html, encoding="utf-8")
        print(f"  dashboard.html saved ({len(html)//1024} KB)")
    print(f"[{datetime.now():%Y-%m-%d %H:%M}] Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
